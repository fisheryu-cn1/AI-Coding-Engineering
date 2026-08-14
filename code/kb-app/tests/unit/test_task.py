"""Unit tests for :mod:`kbapp.core.task`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from kbapp.core.registry import Registry
from kbapp.core.task import (
    TASK_KINDS,
    Task,
    TaskError,
    UnknownTaskKindError,
    backoff,
    backoff_seconds,
    count_tasks,
    enqueue_task,
    list_tasks,
    mark_done,
    mark_failed,
    mark_running,
    new_task_id,
    next_task,
    reset_stale_running,
)


def test_backoff_schedule_matches_design() -> None:
    """设计 07 §7.2: 30s → 1m → 5m (capped)."""
    assert backoff_seconds(1) == 30
    assert backoff_seconds(2) == 60
    assert backoff_seconds(3) == 300
    # Beyond the cap, the schedule stays at 300s
    assert backoff_seconds(7) == 300
    assert backoff(1) == timedelta(seconds=30)


def test_backoff_for_nonpositive_attempt() -> None:
    assert backoff_seconds(0) == 0
    assert backoff_seconds(-3) == 0


def test_new_task_id_is_unique() -> None:
    a = new_task_id()
    b = new_task_id()
    assert a != b
    # ULIDs are 26 characters in Crockal Base32
    assert len(a) == 26
    assert len(b) == 26


def test_new_task_id_is_sortable_across_time() -> None:
    """A ULID generated later must lexically sort after an earlier one."""
    import time as _time

    a = new_task_id()
    _time.sleep(0.01)  # ~10ms — enough for the timestamp prefix to advance
    b = new_task_id()
    assert a < b


def test_enqueue_returns_id_and_increments_count(registry: Registry) -> None:
    tid = enqueue_task(registry, "parse", {"doc_id": "x"})
    assert isinstance(tid, str) and len(tid) > 0
    assert count_tasks(registry, status="pending") == 1


def test_enqueue_rejects_unknown_kind(registry: Registry) -> None:
    with pytest.raises(UnknownTaskKindError):
        enqueue_task(registry, "frobnicate", {})


def test_enqueue_supports_tombstone_kind(registry: Registry) -> None:
    """R3: ``tombstone`` 是合法任务类型。"""
    assert "tombstone" in TASK_KINDS
    tid = enqueue_task(registry, "tombstone", {"doc_id": "y"})
    assert tid


def test_next_task_returns_oldest_pending(registry: Registry) -> None:
    enqueue_task(registry, "parse", {"a": 1})
    enqueue_task(registry, "classify", {"b": 2})
    t = next_task(registry)
    assert t is not None
    assert t.kind == "parse"


def test_next_task_skips_future_run_after(registry: Registry) -> None:
    """A task whose ``run_after`` is in the future must not be picked up."""
    future = (datetime.now(UTC) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    enqueue_task(registry, "parse", {}, run_after=future)
    assert next_task(registry) is None


def test_next_task_skips_failed_and_done(registry: Registry) -> None:
    enqueue_task(registry, "parse", {})
    enqueue_task(registry, "classify", {})

    t1 = next_task(registry)
    assert t1 is not None
    mark_running(registry, t1.id)
    mark_done(registry, t1.id)

    t2 = next_task(registry)
    assert t2 is not None
    mark_running(registry, t2.id)
    mark_failed(registry, t2.id, error="boom", terminal=True)

    # Both should be skipped now
    assert next_task(registry) is None


def test_mark_running_only_from_pending(registry: Registry) -> None:
    tid = enqueue_task(registry, "parse", {})
    mark_running(registry, tid)
    # Second call must fail because status is no longer pending
    with pytest.raises(TaskError):
        mark_running(registry, tid)


def test_mark_running_unknown_task_raises(registry: Registry) -> None:
    with pytest.raises(TaskError):
        mark_running(registry, "no-such-task")


def test_mark_failed_retryable_resets_to_pending_with_run_after(
    registry: Registry,
) -> None:
    tid = enqueue_task(registry, "parse", {})
    mark_running(registry, tid)
    mark_failed(registry, tid, error="transient", terminal=False)

    rows = list_tasks(registry, status="pending")
    assert len(rows) == 1
    assert rows[0].id == tid
    assert rows[0].run_after is not None
    # Attempts counter should have been incremented to 1
    assert rows[0].attempts == 1


def test_mark_failed_immediate_requeues_without_run_after(registry: Registry) -> None:
    """``immediate=True`` requeues without backoff (09 §10 Ctrl-C；P3-1)."""
    tid = enqueue_task(registry, "parse", {})
    mark_running(registry, tid)
    mark_failed(registry, tid, error="Ctrl-C", immediate=True)

    rows = list_tasks(registry, status="pending")
    assert len(rows) == 1
    assert rows[0].id == tid
    assert rows[0].run_after is None


def test_mark_failed_terminal_goes_to_failed(registry: Registry) -> None:
    tid = enqueue_task(registry, "parse", {})
    mark_running(registry, tid)
    mark_failed(registry, tid, error="bad input", terminal=True)
    rows = list_tasks(registry, status="failed")
    assert len(rows) == 1
    assert rows[0].error == "bad input"


def test_mark_failed_exhausts_retries_and_lands_in_failed(
    registry: Registry,
) -> None:
    tid = enqueue_task(registry, "parse", {}, max_attempts=2)
    # First round → pending (retryable)
    mark_running(registry, tid)
    mark_failed(registry, tid, error="transient 1")
    # Second round → failed (attempts == max_attempts)
    mark_running(registry, tid)
    mark_failed(registry, tid, error="transient 2")
    assert count_tasks(registry, status="failed") == 1
    assert count_tasks(registry, status="pending") == 0


def test_reset_stale_running_recovers_crashed_tasks(registry: Registry) -> None:
    tid = enqueue_task(registry, "parse", {})
    mark_running(registry, tid)
    # Backdate started_at so it looks stale
    with registry.connect() as conn:
        old = (datetime.now(UTC) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn.execute("UPDATE tasks SET started_at = ? WHERE id = ?", (old, tid))

    n = reset_stale_running(registry)
    assert n == 1
    # Task is back to pending
    assert count_tasks(registry, status="pending") == 1


def test_reset_stale_running_no_op_when_fresh(registry: Registry) -> None:
    tid = enqueue_task(registry, "parse", {})
    mark_running(registry, tid)
    n = reset_stale_running(registry)
    assert n == 0
    # Task still running
    assert count_tasks(registry, status="running") == 1


def test_payload_roundtrip(registry: Registry) -> None:
    """JSON-encoding preserves Chinese text + nested dicts."""
    payload = {"doc_id": "references/AIOS/02", "title": "AIOS 中文", "n": 3}
    enqueue_task(registry, "parse", payload)
    t = next_task(registry)
    assert t is not None
    assert t.payload == payload


def test_task_dataclass_from_row_fields_match_schema() -> None:
    """Sanity: the dataclass fields cover the columns we use."""
    expected = {
        "id",
        "kind",
        "payload",
        "status",
        "attempts",
        "max_attempts",
        "run_after",
        "error",
        "created_at",
        "started_at",
        "finished_at",
    }
    assert set(Task.__dataclass_fields__) == expected
