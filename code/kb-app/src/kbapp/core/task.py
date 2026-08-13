"""Task state machine + retry queue (设计 05 §4.0 + 07 §7.2).

任务状态机::

    pending → running → done
             ↘ failed (attempts < max 则退避回 pending)

设计要点：
- ``kind`` 枚举包括 R3 增补的 ``tombstone``（M5 起真正使用）
- 退避策略 30s → 1m → 5m 指数（设计 07 §7.2）
- 崩溃恢复：启动时把 ``running`` 且 ``started_at`` 超时的任务重置为
  ``pending``（设计 07 §7.2）
- ``RetryableError`` 触发退避；其他异常立即终态（terminal）
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import ulid

from kbapp.core.registry import Registry

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: 任务种类 (设计 05 §4.0, R3)
TASK_KIND = Literal[
    "parse",
    "classify",
    "summarize",
    "extract",
    "index",
    "collect",
    "tombstone",
]
TASK_KINDS: tuple[str, ...] = (
    "parse",
    "classify",
    "summarize",
    "extract",
    "index",
    "collect",
    "tombstone",
)

#: 任务状态 (设计 05 §4.0)
TASK_STATUS = Literal["pending", "running", "done", "failed"]
TASK_STATUSES: tuple[str, ...] = ("pending", "running", "done", "failed")

#: Default retry budget.
DEFAULT_MAX_ATTEMPTS = 3

#: Backoff schedule (设计 07 §7.2: 30s → 1m → 5m …)
_BACKOFF_SCHEDULE_SECONDS: tuple[int, ...] = (30, 60, 300)

#: Default staleness threshold for crash-recovery (07 §7.2).
DEFAULT_STALE_AFTER = timedelta(minutes=30)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TaskError(Exception):
    """Base for task-related errors."""


class RetryableError(TaskError):
    """Stage raised this when the failure is worth retrying.

    Raises trigger ``backoff(attempt)`` for ``run_after``.
    """


class TerminalError(TaskError):
    """Stage raised this when the failure is not worth retrying.

    Immediately moves to ``status='failed'``.
    """


class UnknownTaskKindError(TaskError, ValueError):
    def __init__(self, kind: str) -> None:
        super().__init__(f"未知任务种类：{kind!r}（允许：{TASK_KINDS}）")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def backoff_seconds(attempt: int) -> int:
    """Return the delay (seconds) for the *n*-th retry (1-based).

    Schedule: 30s, 60s, 300s, then cap at 300s. ``attempt <= 0`` returns 0
    (immediate).
    """
    if attempt <= 0:
        return 0
    idx = min(attempt - 1, len(_BACKOFF_SCHEDULE_SECONDS) - 1)
    return _BACKOFF_SCHEDULE_SECONDS[idx]


def backoff(attempt: int) -> timedelta:
    """Same as :func:`backoff_seconds` but returns a ``timedelta``."""
    return timedelta(seconds=backoff_seconds(attempt))


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    # Accept trailing 'Z' as UTC
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def new_task_id() -> str:
    """Generate a ULID for use as ``tasks.id`` (sortable + unique).

    Uses :func:`ulid.new` (the public factory) rather than instantiating the
    :class:`ulid.ULID` class directly; the latter requires an explicit byte
    buffer in ulid-py ≥ 2.0.
    """
    return str(ulid.new())


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class Task:
    """In-memory representation of a row in ``tasks``."""

    id: str
    kind: str
    payload: dict[str, Any]
    status: str = "pending"
    attempts: int = 0
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    run_after: str | None = None
    error: str | None = None
    created_at: str = field(default_factory=_now_iso)
    started_at: str | None = None
    finished_at: str | None = None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Task:
        return cls(
            id=row["id"],
            kind=row["kind"],
            payload=json.loads(row["payload"]) if row["payload"] else {},
            status=row["status"],
            attempts=row["attempts"],
            max_attempts=row["max_attempts"],
            run_after=row["run_after"],
            error=row["error"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
        )


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------


def enqueue_task(
    registry: Registry,
    kind: str,
    payload: dict[str, Any] | None = None,
    *,
    task_id: str | None = None,
    run_after: str | None = None,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> str:
    """Enqueue a new pending task; return the task id (generated if not given).

    Validates ``kind`` against :data:`TASK_KINDS`. JSON-encodes ``payload``.
    """
    if kind not in TASK_KINDS:
        raise UnknownTaskKindError(kind)
    tid = task_id or new_task_id()
    with registry.transaction() as conn:
        conn.execute(
            "INSERT INTO tasks (id, kind, payload, status, attempts, "
            "max_attempts, run_after, created_at) "
            "VALUES (?, ?, ?, 'pending', 0, ?, ?, ?)",
            (
                tid,
                kind,
                json.dumps(payload or {}, ensure_ascii=False),
                max_attempts,
                run_after,
                _now_iso(),
            ),
        )
    return tid


def next_task(registry: Registry) -> Task | None:
    """Return the next pending task whose ``run_after`` is in the past.

    FIFO by ``created_at`` (which is monotonic via ULID prefix).
    Returns ``None`` when nothing is runnable.
    """
    now = _now_iso()
    with registry.transaction() as conn:
        row = conn.execute(
            "SELECT * FROM tasks "
            "WHERE status = 'pending' AND (run_after IS NULL OR run_after <= ?) "
            "ORDER BY created_at ASC LIMIT 1",
            (now,),
        ).fetchone()
    return Task.from_row(row) if row else None


def mark_running(registry: Registry, task_id: str) -> None:
    """Transition ``pending`` → ``running``; bump ``attempts`` and set ``started_at``.

    If the task is not in ``pending`` state, raises :class:`TaskError`.
    """
    with registry.transaction() as conn:
        cur = conn.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if row is None:
            raise TaskError(f"任务不存在：{task_id}")
        if row["status"] != "pending":
            raise TaskError(
                f"任务 {task_id} 状态为 {row['status']!r}，无法切到 running"
            )
        conn.execute(
            "UPDATE tasks SET status = 'running', attempts = attempts + 1, "
            "started_at = ?, error = NULL WHERE id = ?",
            (_now_iso(), task_id),
        )


def mark_done(registry: Registry, task_id: str) -> None:
    """Transition ``running`` → ``done``."""
    with registry.transaction() as conn:
        conn.execute(
            "UPDATE tasks SET status = 'done', finished_at = ?, error = NULL "
            "WHERE id = ?",
            (_now_iso(), task_id),
        )


def mark_failed(
    registry: Registry,
    task_id: str,
    error: str,
    *,
    terminal: bool = False,
) -> None:
    """Transition ``running`` → ``pending`` (with ``run_after``) or ``failed``.

    If ``attempts < max_attempts`` and not ``terminal``, the task returns to
    ``pending`` with ``run_after = now + backoff(attempts)``; otherwise it
    becomes ``failed``.
    """
    with registry.transaction() as conn:
        row = conn.execute(
            "SELECT attempts, max_attempts FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise TaskError(f"任务不存在：{task_id}")

        attempts = row["attempts"]
        max_attempts = row["max_attempts"]
        if not terminal and attempts < max_attempts:
            delay = backoff_seconds(attempts)
            run_after = (
                datetime.now(UTC) + timedelta(seconds=delay)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            conn.execute(
                "UPDATE tasks SET status = 'pending', run_after = ?, "
                "error = ?, started_at = NULL WHERE id = ?",
                (run_after, error, task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET status = 'failed', finished_at = ?, "
                "error = ? WHERE id = ?",
                (_now_iso(), error, task_id),
            )


def reset_stale_running(
    registry: Registry,
    *,
    stale_after: timedelta = DEFAULT_STALE_AFTER,
) -> int:
    """Crash-recovery: reset ``running`` tasks whose ``started_at`` is too old.

    Returns the number of tasks reset (typically 0 in normal operation;
    >0 after a crash). Safe to call repeatedly.
    """
    threshold = (datetime.now(UTC) - stale_after).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    with registry.transaction() as conn:
        cur = conn.execute(
            "UPDATE tasks SET status = 'pending', started_at = NULL, "
            "run_after = ? "
            "WHERE status = 'running' AND started_at IS NOT NULL "
            "AND started_at < ?",
            (_now_iso(), threshold),
        )
        return cur.rowcount


def count_tasks(
    registry: Registry, *, status: str | None = None
) -> int:
    """Return the number of tasks, optionally filtered by ``status``."""
    with registry.transaction() as conn:
        if status is None:
            row = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM tasks WHERE status = ?", (status,)
            ).fetchone()
    return int(row["n"])


def list_tasks(
    registry: Registry, *, status: str | None = None, limit: int = 50
) -> list[Task]:
    """Return recent tasks, optionally filtered by ``status``."""
    with registry.transaction() as conn:
        if status is None:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = ? "
                "ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
    return [Task.from_row(r) for r in rows]


__all__ = [
    "DEFAULT_MAX_ATTEMPTS",
    "DEFAULT_STALE_AFTER",
    "RetryableError",
    "TASK_KINDS",
    "TASK_KIND",
    "TASK_STATUSES",
    "TASK_STATUS",
    "Task",
    "TaskError",
    "TerminalError",
    "UnknownTaskKindError",
    "backoff",
    "backoff_seconds",
    "count_tasks",
    "enqueue_task",
    "list_tasks",
    "mark_done",
    "mark_failed",
    "mark_running",
    "new_task_id",
    "next_task",
    "reset_stale_running",
]
