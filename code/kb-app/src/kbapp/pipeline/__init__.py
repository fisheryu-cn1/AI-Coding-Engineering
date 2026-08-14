"""Pipeline stages + runner (M2; 设计 05 §4.0 + 09 §10).

The M2 runner is single-writer, synchronous, and runs in the foreground
(09 §10). One task per document (``kind='parse'``); the runner invokes
three stages in sequence:

1. :func:`stage_parse` — parse the source file, write cache payload.
2. :func:`stage_chunk` — split sections into FTS5 chunks.
3. :func:`stage_classify` — keyword topic scoring + doc_type decision.

Every stage is **idempotent**: re-running produces the same DB state
(doc_id, chunk_id primary keys; ``delete-then-insert`` for FTS rows).

Ctrl-C handling: see :mod:`kbapp.pipeline.runner`. A :class:`KeyboardInterrupt`
during stage execution marks the current task ``pending`` with retryable
backoff so the next ``kb index run`` picks it up unchanged (09 §10).
"""

from __future__ import annotations

from kbapp.pipeline.classify import (
    DOC_TYPES,
    TopicScore,
    decide_doc_type,
    decide_topic,
    score_topics,
)
from kbapp.pipeline.runner import (
    PipelineCtx,
    RunReport,
    run_pending_tasks,
)
from kbapp.pipeline.stages import (
    StageResult,
    set_topic,
    stage_chunk,
    stage_classify,
    stage_parse,
)

__all__ = [
    "DOC_TYPES",
    "PipelineCtx",
    "RunReport",
    "StageResult",
    "TopicScore",
    "decide_doc_type",
    "decide_topic",
    "run_pending_tasks",
    "score_topics",
    "set_topic",
    "stage_chunk",
    "stage_classify",
    "stage_parse",
]
