"""LiteLLM-backed LLM client with two-level retry + fallback (09 §9).

Design contract (also see module docstring):

- ``LLM.complete(messages, json_mode=False, max_tokens=1024) -> str``
- Two-level ladder:

  - L1: per-provider exponential backoff. Default 4 attempts; delay sequence
    ``1s, 2s, 4s`` (4 attempts sleep only 3 times — the last attempt
    exhausts without sleeping). Configurable via ``llm.retry.{max_attempts,
    base_delay_seconds, backoff_factor, max_delay_seconds}``; capped at
    ``max_delay_seconds`` so the schedule stays bounded.
  - L2: switch to the next entry in ``llm.fallback`` and restart L1. We
    stop after ``llm.fallback_max_switches=1`` further providers (one
    primary + one backup). Each backup provider still runs its own 4
    attempts.

- 4xx-ish errors (``AuthenticationError``, ``PermissionDeniedError``,
  ``NotFoundError``, ``BadRequestError``, ``ContentPolicyViolationError``)
  are *not* retried — they indicate a config / request problem that will
  repeat, so we jump straight to L2.
- 5xx / 429 / ``Timeout`` / ``APIConnectionError`` / ``InternalServerError``
  / ``ServiceUnavailableError`` are retried within L1.
- After L2 exhausts (no provider succeeded), raise :class:`LLMUnavailable`
  so the runner can decide whether to backoff (typical) or mark terminal.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from kbapp.core.task import RetryableError

# `kbapp.llm` is optional (parse extra); the tests / classifier handle a
# missing litellm by routing to pure-rule mode (09 §7.4).

_logger = logging.getLogger(__name__)

_THINK_RE = None  # 惰性编译，见 _clean_content
_FENCE_RE = None


def _clean_content(text: str) -> str:
    """清洗模型输出：剥 ``<think>…</think>`` 块与 ```json 围栏。

    - MiniMax-M3 等推理模型把 think 块混进 content（只剥闭合块；未闭合
      即 max_tokens 截断，保留原文由调用方解析失败走降级）。
    - json_mode 下部分模型仍套 ```json … ``` 围栏（MiniMax 实测），剥掉
      再交 ``json.loads``。
    """
    global _THINK_RE, _FENCE_RE
    if _THINK_RE is None:
        import re

        _THINK_RE = re.compile(r"^\s*<think>.*?</think>\s*", re.DOTALL)
        _FENCE_RE = re.compile(r"^\s*```[A-Za-z]*\s*\n(?P<body>.*?)\n?\s*```\s*$", re.DOTALL)
    text = _THINK_RE.sub("", text)
    m = _FENCE_RE.match(text)
    if m:
        text = m.group("body")
    return text


# Force litellm's bundled cost map so it skips the remote model-cost fetch at
# import time. Offline this fetch otherwise emits a timeout warning on every
# CLI command (P3-9). ``setdefault`` keeps a user's explicit override intact.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class LLMError(Exception):
    """Base for all LLM client failures."""


class LLMUnavailable(LLMError, RetryableError):
    """Raised when no provider succeeds (final failure).

    Subclasses :class:`~kbapp.core.task.RetryableError` so the runner's
    ``except RetryableError`` branch catches it directly and puts the task
    back to ``pending`` with the standard 30s→1m→5m backoff (09 §9 / M1 §07).
    """


class LLMClientError(LLMError):
    """Parameter / config error — not retryable, not worth backing off.

    The runner treats this as terminal (``mark_failed(terminal=True)``).
    """


# ---------------------------------------------------------------------------
# Retry outcome (used by tests / metrics)
# ---------------------------------------------------------------------------


@dataclass
class RetryOutcome:
    """Summary of one ``LLM.complete`` call for log / metrics.

    Fields mirror 09 §9: which provider succeeded (or ``None`` on total
    failure), how many attempts we made in total, and the wall-clock time
    spent across both levels.
    """

    provider: str | None = None
    attempts: int = 0
    fallback_switches: int = 0
    elapsed_seconds: float = 0.0
    error: str | None = None


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------


def get_llm_or_none(cfg: Any) -> LLM | None:
    """Return an :class:`LLM` if litellm + a usable API key are present.

    ``None`` means the caller should take the pure-rule fallback path
    (09 §7.4).
    """
    try:
        import litellm  # noqa: F401  (presence check)
    except ImportError:
        return None

    api_key_env = (
        cfg.get("llm.api_key_env") if hasattr(cfg, "get") else None
    ) or "DEEPSEEK_API_KEY"
    # M2 treats an unset API key as "missing" — no network calls attempted.
    if not os.environ.get(api_key_env):
        return None

    return LLM(cfg)


# ---------------------------------------------------------------------------
# The client
# ---------------------------------------------------------------------------


@dataclass
class _ProviderSpec:
    """One provider slot — primary or fallback."""

    provider: str
    model: str
    api_base: str | None = None
    json_mode: bool = True
    api_key_env: str = "DEEPSEEK_API_KEY"


@dataclass
class LLM:
    """LiteLLM wrapper with two-level retry (09 §9)."""

    cfg: Any  # Config-like (duck-typed; supports dotted get)
    # Internal: collected after each call for tests / metrics.
    last_outcome: RetryOutcome | None = None

    # -- public ---------------------------------------------------------

    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        json_mode: bool = False,
        max_tokens: int = 1024,
        purpose: str = "classify",
        doc_id: str | None = None,
    ) -> str:
        """Run ``messages`` through the retry ladder.

        Returns the assistant text on success. Raises
        :class:`LLMUnavailable` after both levels exhaust; raises
        :class:`LLMClientError` for unrecoverable parameter problems.
        """
        providers = self._providers(json_mode=json_mode)
        if not providers:
            raise LLMUnavailable("未配置 LLM provider（缺 api_key 或 litellm 未装）")

        retry_cfg = self._retry_config()
        max_attempts = int(retry_cfg["max_attempts"])
        base_delay = float(retry_cfg["base_delay_seconds"])
        factor = float(retry_cfg["backoff_factor"])
        max_delay = float(retry_cfg["max_delay_seconds"])
        max_switches = int(self.cfg.get("llm.fallback_max_switches", 1))

        started = time.monotonic()
        outcome = RetryOutcome()
        last_err: Exception | None = None

        for switch_idx, spec in enumerate(providers):
            if switch_idx > max_switches:
                break
            if switch_idx > 0:
                outcome.fallback_switches += 1
                _logger.info(
                    "LLM fallback 切换到 %s/%s（第 %d 次）",
                    spec.provider,
                    spec.model,
                    switch_idx,
                )
            for attempt in range(1, max_attempts + 1):
                outcome.attempts += 1
                try:
                    text, tokens = self._call_once(
                        spec,
                        messages,
                        json_mode=json_mode,
                        max_tokens=max_tokens,
                    )
                except _Retryable as e:
                    last_err = e
                    if attempt >= max_attempts:
                        _logger.warning(
                            "LLM %s/%s 第 %d 轮耗尽：%s",
                            spec.provider,
                            spec.model,
                            attempt,
                            e,
                        )
                        break
                    delay = self._backoff_delay(attempt, base_delay, factor, max_delay)
                    _logger.info(
                        "LLM %s/%s 第 %d 轮失败，%.1fs 后重试：%s",
                        spec.provider,
                        spec.model,
                        attempt,
                        delay,
                        e,
                    )
                    time.sleep(delay)
                    continue
                except _Terminal as e:
                    # 4xx-class — don't retry this provider; jump to next.
                    last_err = e
                    _logger.warning(
                        "LLM %s/%s 配置/参数错误直通 fallback：%s",
                        spec.provider,
                        spec.model,
                        e,
                    )
                    break
                except _Fatal as e:
                    # Catch-all config (import error etc.) — never retry.
                    raise LLMClientError(str(e)) from e

                # Success.
                outcome.provider = f"{spec.provider}/{spec.model}"
                outcome.elapsed_seconds = time.monotonic() - started
                self.last_outcome = outcome
                self._record_usage(
                    spec=spec,
                    purpose=purpose,
                    input_tokens=tokens[0],
                    output_tokens=tokens[1],
                    doc_id=doc_id,
                )
                return text

        # Both levels exhausted.
        outcome.elapsed_seconds = time.monotonic() - started
        outcome.error = str(last_err) if last_err else "no_provider_succeeded"
        self.last_outcome = outcome
        raise LLMUnavailable(outcome.error)

    # -- internals -------------------------------------------------------

    def _providers(self, *, json_mode: bool) -> list[_ProviderSpec]:
        """Build the [primary, fallback1, fallback2, …] chain.

        Honours ``llm.fallback`` from config; missing list → just primary.
        """
        primary = _ProviderSpec(
            provider=self.cfg.get("llm.provider"),
            model=self.cfg.get("llm.model"),
            api_base=self.cfg.get("llm.api_base"),
            json_mode=bool(self.cfg.get("llm.json_mode", True)),
            api_key_env=self.cfg.get("llm.api_key_env", "DEEPSEEK_API_KEY"),
        )
        chain: list[_ProviderSpec] = [primary]
        for entry in self.cfg.get("llm.fallback", []) or []:
            chain.append(
                _ProviderSpec(
                    provider=entry.get("provider"),
                    model=entry.get("model"),
                    api_base=entry.get("api_base"),
                    json_mode=bool(entry.get("json_mode", True)),
                    api_key_env=entry.get("api_key_env", primary.api_key_env),
                )
            )
        # Force the caller's json_mode for the whole chain (primary set the
        # default but it must follow the live arg).
        for spec in chain:
            spec.json_mode = json_mode
        return chain

    def _retry_config(self) -> dict[str, Any]:
        raw = self.cfg.get("llm.retry", {}) or {}
        return {
            "max_attempts": int(raw.get("max_attempts", 4)),
            "base_delay_seconds": float(raw.get("base_delay_seconds", 1)),
            "backoff_factor": float(raw.get("backoff_factor", 2)),
            "max_delay_seconds": float(raw.get("max_delay_seconds", 30)),
        }

    def _backoff_delay(
        self,
        attempt: int,
        base: float,
        factor: float,
        cap: float,
    ) -> float:
        """``base * factor^(attempt-1)`` capped at ``cap`` seconds."""
        delay = base * (factor ** max(0, attempt - 1))
        return min(cap, delay)

    def _call_once(
        self,
        spec: _ProviderSpec,
        messages: list[dict[str, Any]],
        *,
        json_mode: bool,
        max_tokens: int,
    ) -> tuple[str, tuple[int, int]]:
        """Single ``litellm.completion`` call; classify the outcome.

        Returns ``(text, (input_tokens, output_tokens))`` on success.
        Raises ``_Retryable`` / ``_Terminal`` / ``_Fatal`` to communicate
        the error type to the ladder.
        """
        try:
            import litellm  # local import — only when actually called
        except ImportError as e:
            raise _Fatal(f"litellm 未安装：{e}") from e

        api_key = os.environ.get(spec.api_key_env)
        if not api_key:
            raise _Fatal(f"环境变量 {spec.api_key_env} 未设置")

        kwargs: dict[str, Any] = {
            "model": f"{spec.provider}/{spec.model}",
            "messages": messages,
            "max_tokens": max_tokens,
            "timeout": 60,
            "num_retries": 0,  # ★ disable litellm's own retries (we own ladder)
        }
        if spec.api_base:
            kwargs["api_base"] = spec.api_base
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            resp = litellm.completion(**kwargs)
        except _LITELLM_TERMINAL_EXCEPTIONS as e:  # 4xx-class
            raise _Terminal(str(e)) from e
        except _LITELLM_RETRYABLE_EXCEPTIONS as e:  # 5xx/429/net/timeout
            raise _Retryable(str(e)) from e
        except Exception as e:  # unknown — treat as retryable so user sees it
            # but with the original exception type for diagnostic clarity
            raise _Retryable(f"unexpected: {e}") from e

        try:
            text = resp.choices[0].message.content or ""
        except (AttributeError, IndexError, KeyError) as e:
            raise _Fatal(f"响应结构异常：{e}") from e
        text = _clean_content(text)
        usage = getattr(resp, "usage", None)
        in_tok = int(getattr(usage, "prompt_tokens", 0) or 0)
        out_tok = int(getattr(usage, "completion_tokens", 0) or 0)
        return text, (in_tok, out_tok)

    def _record_usage(
        self,
        *,
        spec: _ProviderSpec,
        purpose: str,
        input_tokens: int,
        output_tokens: int,
        doc_id: str | None,
    ) -> None:
        """Append a row to ``llm_usage``. Failures here are logged, not raised."""
        try:
            from kbapp.core.registry import (
                LLM_PURPOSES,
                record_llm_usage,
            )
        except ImportError:
            return

        if purpose not in LLM_PURPOSES:
            # 未知 purpose 是编程错误，显式报错而非静默回退 classify（11 §7，避免审计断链被掩盖）。
            raise ValueError(f"未知 purpose：{purpose!r}（允许：{LLM_PURPOSES}）")
        try:
            data_dir = self.cfg.data_dir
        except AttributeError:
            return
        try:
            from kbapp.core.registry import Registry

            db = data_dir / "registry.sqlite"
            reg = Registry(db)
            with reg.transaction() as conn:
                record_llm_usage(
                    conn,
                    model=f"{spec.provider}/{spec.model}",
                    purpose=purpose,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=None,  # M2: price source TBD (09 §9)
                    doc_id=doc_id,
                )
        except Exception as e:  # pragma: no cover - audit must not block
            _logger.warning("llm_usage 记账失败：%s", e)


# ---------------------------------------------------------------------------
# Internal exception markers + litellm-class mapping
# ---------------------------------------------------------------------------


class _Retryable(Exception):
    """Marker for retryable errors (private)."""


class _Terminal(Exception):
    """Marker for 4xx-class errors that should jump to L2 (private)."""


class _Fatal(Exception):
    """Marker for unrecoverable config errors (private)."""


def _load_litellm_classes() -> (
    tuple[type[BaseException], ...],
    tuple[type[BaseException], ...],
):
    """Build the (retryable, terminal) exception tuples for litellm.

    Returns empty tuples if litellm is not installed — the caller will
    fall back to a generic-classification heuristic on the raised object.
    """
    retryable: list[type[BaseException]] = []
    terminal: list[type[BaseException]] = []
    try:
        import litellm
        from litellm.exceptions import (
            APIConnectionError,
            AuthenticationError,
            BadRequestError,
            ContentPolicyViolationError,
            InternalServerError,
            NotFoundError,
            PermissionDeniedError,
            RateLimitError,
            ServiceUnavailableError,
            Timeout,
        )
    except ImportError:
        return (), ()

    retryable.extend(
        [
            Timeout,
            APIConnectionError,
            InternalServerError,
            ServiceUnavailableError,
            RateLimitError,
        ]
    )
    terminal.extend(
        [
            AuthenticationError,
            PermissionDeniedError,
            NotFoundError,
            BadRequestError,
            ContentPolicyViolationError,
        ]
    )
    # ``litellm`` also re-exports several of these at top level.
    for cls in (RateLimitError, Timeout, APIConnectionError):
        if hasattr(litellm, cls.__name__):
            retryable.append(getattr(litellm, cls.__name__))
    return tuple(retryable), tuple(terminal)


_LITELLM_RETRYABLE_EXCEPTIONS, _LITELLM_TERMINAL_EXCEPTIONS = _load_litellm_classes()


__all__ = [
    "LLM",
    "LLMClientError",
    "LLMUnavailable",
    "RetryOutcome",
    "get_llm_or_none",
]
