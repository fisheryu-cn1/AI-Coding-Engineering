"""LLM client (M2; 设计 05 §3.4 + 09 §9).

Public API:

- :class:`LLM` — :func:`complete` for chat-style calls (json mode optional).
- :class:`LLMUnavailable` — raised on permanent failure (runner退避 via
  ``RetryableError``); raised immediately on mis-config (no API key, etc.).
- :class:`LLMClientError` — parameter/config error; the runner marks the
  task terminal (no retry).

The client uses a **two-level retry ladder** (09 §9):

1. **In-call exponential backoff** (``max_attempts=4``,
   ``base_delay=1s``, ``factor=2``, ``max_delay=30s``).
2. **Fallback chain switch** at most ``fallback_max_switches=1`` times
   (one primary + one backup). Each switch restarts the in-call ladder.

``litellm.completion`` is called with ``num_retries=0`` to disable
litellm's own retries; we own the retry semantics end-to-end so they're
testable.

If litellm is not installed or no API key is configured, ``complete()``
raises :class:`LLMUnavailable` immediately so callers (the classifier) can
fall back to pure-rule mode (09 §7.4).
"""

from __future__ import annotations

from kbapp.llm.litellm_client import (
    LLM,
    LLMClientError,
    LLMUnavailable,
    RetryOutcome,
    get_llm_or_none,
)

__all__ = [
    "LLM",
    "LLMClientError",
    "LLMUnavailable",
    "RetryOutcome",
    "get_llm_or_none",
]
