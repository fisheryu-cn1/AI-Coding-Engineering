"""Pipeline runner (M2; 09 §10; M5 graph pipeline).

Serial, foreground, single-writer execution loop. The CLI's
``kb index run`` command calls :func:`run_pending_tasks` after taking
the write lock; the runner picks tasks one at a time and runs the M2
three-stage sequence (parse → chunk → classify), then enqueues the
``index`` stage task (15 §4.1), the ``extract`` task (15 §4.2), and
processes runtime ``tombstone`` tasks (15 §4.1).

Ctrl-C during a stage:

1. The runner catches :class:`KeyboardInterrupt`.
2. The in-flight task is moved back to ``pending`` **immediately executable**
   (no backoff) via :func:`mark_failed(immediate=True)` — 09 §10「立即可执行
   的 pending」。
3. The runner exits with code 130 (POSIX convention).

Crash recovery is delegated to :func:`reset_stale_running` (called by
the runner once at start so a previous crashed ``kb index run`` doesn't
leave tasks stuck in ``running``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from kbapp.core.config import Config
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry
from kbapp.core.task import (
    RetryableError,
    TerminalError,
    _now_iso,
    enqueue_task,
    mark_failed,
    mark_running,
    next_task,
    reset_stale_running,
)
from kbapp.pipeline.graph_stages import (
    stage_extract_graph,
    stage_index_graph,
    stage_tombstone_graph,
)
from kbapp.pipeline.stages import (
    set_topic,
    stage_chunk,
    stage_classify,
    stage_parse,
    stage_summarize,
)

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PipelineCtx
# ---------------------------------------------------------------------------


@dataclass
class PipelineCtx:
    """Shared dependencies passed through the runner."""

    cfg: Config
    paths: DataPaths
    registry: Registry
    llm: Any = None  # optional LLM client (None → pure-rule classification)
    max_tasks: int | None = None  # None = drain the queue


# ---------------------------------------------------------------------------
# RunReport
# ---------------------------------------------------------------------------


@dataclass
class RunReport:
    """Summary of a :func:`run_pending_tasks` invocation."""

    tasks_done: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    crashed: bool = False
    metrics: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

#: 串行 runner 消费的 task kinds（M3 增 summarize；M5 增 index/extract/tombstone）。
_RUNNER_KINDS: tuple[str, ...] = ("parse", "summarize", "index", "extract", "tombstone")


def run_pending_tasks(ctx: PipelineCtx) -> RunReport:
    """Drive the queue to drain; return a :class:`RunReport`.

    The runner is **single-writer** by design (09 §10): the CLI takes the
    global write lock before calling this function so we don't need our
    own serialization here.
    """
    report = RunReport()
    # Recover any tasks left ``running`` by a previous crash.
    reset_stale_running(ctx.registry)

    while True:
        if ctx.max_tasks is not None and report.tasks_done + report.tasks_failed >= ctx.max_tasks:
            break
        task = next_task(ctx.registry, kind=_RUNNER_KINDS)
        if task is None:
            break

        doc_id = (task.payload or {}).get("doc_id") if task.payload else None
        if not doc_id:
            mark_failed(
                ctx.registry,
                task.id,
                "missing doc_id in payload",
                terminal=True,
            )
            report.tasks_failed += 1
            continue

        try:
            mark_running(ctx.registry, task.id)
        except Exception as e:
            _logger.warning("mark_running 失败：%s", e)
            report.tasks_failed += 1
            continue

        try:
            _run_one(doc_id, ctx, task_kind=task.kind)
        except KeyboardInterrupt:
            report.crashed = True
            try:
                mark_failed(
                    ctx.registry,
                    task.id,
                    "Ctrl-C: re-queue immediately",
                    terminal=False,
                    immediate=True,
                )
            except Exception:
                pass
            raise
        except RetryableError as e:
            try:
                mark_failed(ctx.registry, task.id, str(e), terminal=False)
            except Exception:
                pass
            report.tasks_failed += 1
            _logger.info("任务 %s 失败（可重试）：%s", task.id, e)
            continue
        except TerminalError as e:
            try:
                mark_failed(ctx.registry, task.id, str(e), terminal=True)
            except Exception:
                pass
            report.tasks_failed += 1
            _logger.warning("任务 %s 失败（终态）：%s", task.id, e)
            continue
        except Exception as e:
            # Unknown stage failure → treat as terminal; safer to surface
            # than to keep retrying indefinitely.
            try:
                mark_failed(ctx.registry, task.id, f"unexpected: {e}", terminal=True)
            except Exception:
                pass
            report.tasks_failed += 1
            _logger.exception("任务 %s 异常：%s", task.id, e)
            continue

        try:
            with ctx.registry.transaction() as conn:
                conn.execute(
                    "UPDATE tasks SET status = 'done', finished_at = ?, error = NULL WHERE id = ?",
                    (_now_iso(), task.id),
                )
            report.tasks_done += 1
        except Exception as e:
            _logger.warning("mark_done 失败：%s", e)

    return report


def _run_one(doc_id: str, ctx: PipelineCtx, *, task_kind: str = "parse") -> None:
    """Dispatch by kind (15 §4.1)。"""
    if task_kind == "summarize":
        stage_summarize(doc_id, ctx)
        return
    if task_kind == "index":
        stage_index_graph(doc_id, ctx)
        # index 任务成功后按 is_core 门控入队 extract（15 §4.1）
        from kbapp.core.registry import get_file
        from kbapp.graph.extract import is_core_doc

        with ctx.registry.read_only() as conn:
            row = get_file(conn, doc_id)
        if row is not None and is_core_doc(
            ctx.cfg,
            topic=row.topic,
            doc_type=row.doc_type,
            doc_id=doc_id,
        ):
            enqueue_task(ctx.registry, kind="extract", payload={"doc_id": doc_id})
        return
    if task_kind == "extract":
        stage_extract_graph(doc_id, ctx)
        return
    if task_kind == "tombstone":
        stage_tombstone_graph(doc_id, ctx)
        return
    # parse → parse/chunk/classify → enqueue index（15 §4.1）
    parse_result = stage_parse(doc_id, ctx)
    if parse_result.status == "skip":
        return
    chunk_result = stage_chunk(doc_id, ctx)
    if chunk_result.status == "skip":
        return
    classify_result = stage_classify(doc_id, ctx)
    if classify_result.status == "skip":
        return
    # 入队 index 任务（runner 串行消费，extract 入队在 index 成功后按 is_core 门控）
    enqueue_task(ctx.registry, kind="index", payload={"doc_id": doc_id})


__all__ = [
    "PipelineCtx",
    "RunReport",
    "run_pending_tasks",
    "set_topic",
]
