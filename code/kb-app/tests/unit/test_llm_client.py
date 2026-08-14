"""Unit tests for the LLM client (09 §9 two-level retry + fallback).

Mock ``litellm.completion`` so no real network calls happen.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from kbapp.llm.litellm_client import (
    LLM,
    LLMClientError,
    LLMUnavailable,
    get_llm_or_none,
)


# The LLM client checks this env var before patching; set it via fixture.
@pytest.fixture(autouse=True)
def _fake_api_key():
    os.environ["DEEPSEEK_API_KEY"] = "test-key-not-real"
    yield
    # Don't pop — other tests may need it.


class _Usage:
    def __init__(self, prompt_tokens: int = 10, completion_tokens: int = 20) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _Resp:
    def __init__(self, content: str) -> None:
        self.choices = [MagicMock(message=MagicMock(content=content))]
        self.usage = _Usage()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def test_get_llm_or_none_returns_none_when_no_api_key(tmp_path: Path) -> None:
    from kbapp.core.config import Config

    cfg = Config.defaults()
    # Ensure the API key env var is unset.
    os.environ.pop("DEEPSEEK_API_KEY", None)
    assert get_llm_or_none(cfg) is None


def test_get_llm_or_none_returns_llm_when_key_present(tmp_path: Path) -> None:
    from kbapp.core.config import Config

    cfg = Config.defaults()
    os.environ["DEEPSEEK_API_KEY"] = "fake-key"
    try:
        llm = get_llm_or_none(cfg)
        assert isinstance(llm, LLM)
    finally:
        os.environ.pop("DEEPSEEK_API_KEY", None)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_complete_returns_assistant_text_on_success() -> None:
    cfg = _make_cfg()
    llm = LLM(cfg)
    with patch("litellm.completion", return_value=_Resp("ok")) as m:
        text = llm.complete([{"role": "user", "content": "hi"}])
    assert text == "ok"
    assert m.call_args.kwargs["num_retries"] == 0  # litellm's own retries disabled


def test_complete_strips_inline_think_block() -> None:
    """MiniMax-M3 等推理模型把 ``<think>…</think>`` 混进 content（M3 DoD 复核回归）。"""
    cfg = _make_cfg()
    llm = LLM(cfg)
    dirty = '<think>user wants JSON</think>\n\n{"a": 1}'
    with patch("litellm.completion", return_value=_Resp(dirty)):
        text = llm.complete([{"role": "user", "content": "hi"}], json_mode=True)
    assert text == '{"a": 1}'


def test_complete_keeps_unterminated_think_block() -> None:
    """未闭合 think（max_tokens 截断）不剥，交由调用方解析失败走降级。"""
    cfg = _make_cfg()
    llm = LLM(cfg)
    dirty = "<think>truncated reasoning…"
    with patch("litellm.completion", return_value=_Resp(dirty)):
        text = llm.complete([{"role": "user", "content": "hi"}])
    assert text == dirty


def test_complete_strips_json_fence() -> None:
    """json_mode 下模型仍套 ```json 围栏（MiniMax 实测），剥掉再交 json.loads。"""
    cfg = _make_cfg()
    llm = LLM(cfg)
    dirty = '\n\n```json\n{\n  "a": 1\n}\n```'
    with patch("litellm.completion", return_value=_Resp(dirty)):
        text = llm.complete([{"role": "user", "content": "hi"}], json_mode=True)
    import json

    assert json.loads(text) == {"a": 1}


# ---------------------------------------------------------------------------
# L1 retry: 5xx → 4 attempts
# ---------------------------------------------------------------------------


def test_retryable_error_triggers_4_attempts_with_backoff() -> None:
    cfg = _make_cfg()
    llm = LLM(cfg)
    with (
        patch("litellm.completion", side_effect=_retryable_exc()) as m,
        patch("time.sleep") as sleep,
    ):
        with pytest.raises(LLMUnavailable):
            llm.complete([{"role": "user", "content": "x"}])
    # 4 attempts on primary, then exhausted (no fallback configured → LLMUnavailable).
    assert m.call_count == 4
    # Backoff delays are bounded (≤ 30s).
    delays = [c.args[0] for c in sleep.call_args_list]
    assert all(d <= 30 for d in delays)
    # attempts log is exposed via last_outcome
    assert llm.last_outcome.attempts == 4


# ---------------------------------------------------------------------------
# L2 fallback: terminal → switch to backup
# ---------------------------------------------------------------------------


def test_terminal_error_jumps_to_fallback_immediately() -> None:
    cfg = _make_cfg(fallback=[{"provider": "openai", "model": "gpt-4o-mini"}])
    llm = LLM(cfg)
    with patch("litellm.completion", side_effect=_terminal_exc()) as m:
        with pytest.raises(LLMUnavailable):
            llm.complete([{"role": "user", "content": "x"}])
    # Terminal (4xx-class) jumps straight to the next provider — 1 call each.
    assert m.call_count == 2  # primary + 1 fallback


def test_fallback_max_switches_caps_to_one_backup() -> None:
    """One primary + at most 1 backup = 2 providers, 8 attempts total."""
    cfg = _make_cfg(
        fallback=[
            {"provider": "openai", "model": "gpt-4o-mini"},
            {"provider": "anthropic", "model": "claude-haiku"},
        ]
    )
    llm = LLM(cfg)
    with patch("litellm.completion", side_effect=_retryable_exc()):
        with pytest.raises(LLMUnavailable):
            llm.complete([{"role": "user", "content": "x"}])
    # 4 primary + 4 fallback1 = 8 (fallback2 is past the cap)
    assert llm.last_outcome.attempts == 8


# ---------------------------------------------------------------------------
# Default degradation (no providers)
# ---------------------------------------------------------------------------


def test_no_providers_raises_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the API key env var is empty, primary is rejected as ``_Fatal``.

    The runner translates ``LLMUnavailable`` to a retryable error; the
    LLM client itself raises ``LLMUnavailable`` after exhausting the ladder.
    """
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    cfg = _make_cfg()
    llm = LLM(cfg)
    with pytest.raises((LLMUnavailable, LLMClientError)):
        llm.complete([{"role": "user", "content": "x"}])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cfg(*, fallback: list[dict[str, Any]] | None = None) -> Any:
    """Minimal Config stand-in (duck-typed; supports .get).

    ``spec=["get"]`` keeps the duck-type surface exact: ``.get`` resolves,
    while ``.data_dir`` raises ``AttributeError``. That matters because
    ``LLM._record_usage`` guards on ``except AttributeError`` to skip audit
    logging when no data dir is configured — a bare ``MagicMock()`` would
    auto-create ``.data_dir`` and leak a stray ``registry.sqlite``.
    """
    cfg = MagicMock(spec=["get"])
    cfg.get.side_effect = lambda key, default=None: _cfg_lookup(key, default, fallback)
    return cfg


def _cfg_lookup(key: str, default: Any, fallback: list | None) -> Any:
    data = {
        "llm.provider": "deepseek",
        "llm.model": "deepseek-chat",
        "llm.api_base": None,
        "llm.api_key_env": "DEEPSEEK_API_KEY",
        "llm.json_mode": True,
        "llm.fallback": fallback or [],
        "llm.retry": {
            "max_attempts": 4,
            "base_delay_seconds": 0.01,  # tiny so tests stay fast
            "backoff_factor": 2,
            "max_delay_seconds": 0.05,
        },
        "llm.fallback_max_switches": 1,
    }
    return data.get(key, default)


def _retryable_exc():
    """Factory: each call raises a retryable-looking exception."""
    from litellm.exceptions import InternalServerError

    def _raise(*a: Any, **kw: Any) -> None:
        raise InternalServerError("boom", llm_provider="deepseek", model="x")

    return _raise


def _terminal_exc():
    """Factory: each call raises a terminal (4xx-class) exception."""
    from litellm.exceptions import AuthenticationError

    def _raise(*a: Any, **kw: Any) -> None:
        raise AuthenticationError("nope", llm_provider="deepseek", model="x")

    return _raise
