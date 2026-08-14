"""Unit tests for :mod:`kbapp.core.files` (doc_id decision table; 09 §2)."""

from __future__ import annotations

from pathlib import Path

from kbapp.core.files import (
    ACTION_DUPLICATE,
    ACTION_MODIFIED,
    ACTION_MOVED,
    ACTION_NEW,
    ACTION_UNCHANGED,
    ScanAction,
    apply_deleted,
    apply_modified,
    apply_moved,
    apply_new_or_duplicate,
    decide_action,
    detect_deleted,
)
from kbapp.core.registry import (
    FileRow,
    get_file,
    list_files,
    next_doc_id,
)


def _row(
    *,
    doc_id: str = "D0001",
    path: str = "/x.md",
    sha256: str = "abc",
    status: str = "active",
    summary_source: str = "none",
    summary_path: str | None = None,
    summary_stale: int = 0,
    topic: str | None = None,
) -> FileRow:
    """Minimal FileRow for decision-table tests."""
    return FileRow(
        doc_id=doc_id,
        path=path,
        sha256=sha256,
        mtime=0,
        topic=topic,
        doc_type=None,
        corpus="references",
        extract_status="pending",
        status=status,
        arxiv_id=None,
        version=None,
        authors=None,
        published=None,
        pages=None,
        title=None,
        summary_source=summary_source,
        summary_path=summary_path,
        summary_stale=summary_stale,
        updated_at="2026-08-13T00:00:00Z",
    )


def test_decide_action_new_when_no_match(tmp_path: Path) -> None:
    p = tmp_path / "n.md"
    p.write_text("new")
    a = decide_action(path=p, sha256="h1", mtime=0, by_path=None, by_sha=None)
    assert a.kind == ACTION_NEW
    assert a.doc_id is None


def test_decide_action_unchanged_when_same_sha(tmp_path: Path) -> None:
    p = tmp_path / "u.md"
    p.write_text("u")
    row = _row(path=str(p), sha256="h1")
    a = decide_action(path=p, sha256="h1", mtime=0, by_path=row, by_sha=row)
    assert a.kind == ACTION_UNCHANGED
    assert a.doc_id == "D0001"


def test_decide_action_modified_keeps_doc_id(tmp_path: Path) -> None:
    p = tmp_path / "m.md"
    p.write_text("m")
    row = _row(path=str(p), sha256="old")
    a = decide_action(path=p, sha256="new", mtime=0, by_path=row, by_sha=None)
    assert a.kind == ACTION_MODIFIED
    assert a.doc_id == "D0001"
    assert a.note.startswith("old_sha=")


def test_decide_action_moved_zero_re_extract(tmp_path: Path) -> None:
    old = tmp_path / "old.md"  # does NOT exist
    new = tmp_path / "new.md"
    new.write_text("n")
    row = _row(path=str(old), sha256="h1")
    a = decide_action(path=new, sha256="h1", mtime=0, by_path=None, by_sha=row)
    assert a.kind == ACTION_MOVED
    assert a.doc_id == "D0001"


def test_decide_action_duplicate_when_both_present(tmp_path: Path) -> None:
    a_path = tmp_path / "a.md"
    a_path.write_text("a")
    b_path = tmp_path / "b.md"
    b_path.write_text("b")
    row = _row(path=str(a_path), sha256="h1")
    a = decide_action(path=b_path, sha256="h1", mtime=0, by_path=None, by_sha=row)
    assert a.kind == ACTION_DUPLICATE
    assert a.doc_id is None  # caller allocates


def test_detect_deleted_skips_present_paths() -> None:
    rows = [
        _row(doc_id="D0001", path="/gone.md"),
        _row(doc_id="D0002", path="/present.md"),
    ]
    gone = detect_deleted(on_disk_paths={"/present.md"}, registered_rows=rows)
    assert [r.doc_id for r in gone] == ["D0001"]


def test_apply_new_or_duplicate_inserts_new_row(registry, tmp_path: Path) -> None:
    p = tmp_path / "fresh.md"
    p.write_text("x")
    action = ScanAction(ACTION_NEW, None, str(p), "h", 0)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn, action=action, corpus="references", is_duplicate=False
        )
    assert doc_id == "D0001"
    row = get_file(registry.connect(), doc_id)
    assert row is not None
    assert row.status == "new"
    assert row.corpus == "references"


def test_apply_new_or_duplicate_marks_duplicate(registry, tmp_path: Path) -> None:
    p = tmp_path / "dup.md"
    p.write_text("x")
    action = ScanAction(ACTION_DUPLICATE, None, str(p), "h", 0)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(conn, action=action, corpus="research", is_duplicate=True)
    row = get_file(registry.connect(), doc_id)
    assert row is not None
    assert row.status == "duplicate"


def test_apply_modified_resets_status_to_new(registry, tmp_path: Path) -> None:
    p = tmp_path / "m.md"
    p.write_text("x")
    # Insert prior row first
    with registry.transaction() as conn:
        existing = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), "old_sha", 0),
            corpus="references",
            is_duplicate=False,
        )
    action = ScanAction(ACTION_MODIFIED, existing, str(p), "new_sha", 0)
    with registry.transaction() as conn:
        apply_modified(conn, action, corpus="references")
    row = get_file(registry.connect(), existing)
    assert row.sha256 == "new_sha"
    assert row.status == "new"


def test_apply_modified_preserves_curated_binding(registry, tmp_path: Path) -> None:
    p = tmp_path / "m.md"
    p.write_text("x")
    with registry.transaction() as conn:
        existing = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), "old_sha", 0),
            corpus="references",
            is_duplicate=False,
        )
        from kbapp.core.registry import update_file_fields

        update_file_fields(
            conn,
            existing,
            summary_source="curated",
            summary_path="/summaries/foo.md",
        )
    action = ScanAction(ACTION_MODIFIED, existing, str(p), "new_sha", 0)
    with registry.transaction() as conn:
        apply_modified(conn, action, corpus="references")
    row = get_file(registry.connect(), existing)
    # Curated binding is preserved across a re-parse (P1-1).
    assert row.summary_source == "curated"
    assert row.summary_path == "/summaries/foo.md"


def test_apply_modified_marks_curated_summary_stale(registry, tmp_path: Path) -> None:
    """Source PDF changed under a curated summary → summary_stale=1 (09 §5)."""
    p = tmp_path / "m.md"
    p.write_text("x")
    with registry.transaction() as conn:
        existing = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), "old_sha", 0),
            corpus="references",
            is_duplicate=False,
        )
        from kbapp.core.registry import update_file_fields

        update_file_fields(conn, existing, summary_source="curated")
    action = ScanAction(ACTION_MODIFIED, existing, str(p), "new_sha", 0)
    with registry.transaction() as conn:
        apply_modified(conn, action, corpus="references")
    row = get_file(registry.connect(), existing)
    assert row.summary_stale == 1


def test_apply_moved_preserves_topic_and_status(registry, tmp_path: Path) -> None:
    p_old = tmp_path / "old.md"
    p_new = tmp_path / "new.md"
    p_old.write_text("x")  # create first so upsert_file's UNIQUE(path) doesn't trip
    p_new.write_text("x")
    # Insert prior row at p_old, set topic + active
    with registry.transaction() as conn:
        old_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p_old), "h", 0),
            corpus="references",
            is_duplicate=False,
        )
    with registry.transaction() as conn:
        from kbapp.core.registry import adjust_topic_doc_count, update_file_fields, upsert_topic

        upsert_topic(conn, name="ContextEngineering")
        adjust_topic_doc_count(conn, "ContextEngineering", 1)
        update_file_fields(conn, old_id, topic="ContextEngineering", status="active")
    # Apply move (old path gone)
    p_old.unlink()
    action = ScanAction(ACTION_MOVED, old_id, str(p_new), "h", 0)
    with registry.transaction() as conn:
        apply_moved(conn, action)
    row = get_file(registry.connect(), old_id)
    assert row.path == str(p_new)
    assert row.topic == "ContextEngineering"
    assert row.status == "active"


def test_apply_deleted_marks_tombstone(registry, tmp_path: Path) -> None:
    p = tmp_path / "doomed.md"
    p.write_text("x")
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), "h", 0),
            corpus="references",
            is_duplicate=False,
        )
    with registry.transaction() as conn:
        apply_deleted(conn, doc_id)
    row = get_file(registry.connect(), doc_id)
    assert row.status == "deleted"
    # 09 §2: tombstone preserves path/sha256 for M5 graph soft-delete (P0-2).
    assert row.path == str(p)
    assert row.sha256 == "h"


def test_apply_deleted_twice_does_not_collide(registry, tmp_path: Path) -> None:
    """Two tombstones in the same transaction must not trip UNIQUE(path)."""
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"
    a.write_text("a")
    b.write_text("b")
    with registry.transaction() as conn:
        da = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(a), "ha", 0),
            corpus="references",
            is_duplicate=False,
        )
        db = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(b), "hb", 0),
            corpus="references",
            is_duplicate=False,
        )
    with registry.transaction() as conn:
        apply_deleted(conn, da)
        apply_deleted(conn, db)  # previously raised UNIQUE constraint (P0-2)
    rows = {r.doc_id: r for r in list_files(registry.connect())}
    assert rows[da].status == "deleted"
    assert rows[db].status == "deleted"


def test_detect_deleted_skips_already_deleted() -> None:
    rows = [
        _row(doc_id="D0001", path="/gone.md", status="deleted"),
        _row(doc_id="D0002", path="/present.md"),
        _row(doc_id="D0003", path="/also_gone.md", status="active"),
    ]
    gone = detect_deleted(on_disk_paths={"/present.md"}, registered_rows=rows)
    assert [r.doc_id for r in gone] == ["D0003"]


def test_decide_action_revives_tombstone(tmp_path: Path) -> None:
    """A recreated file at a tombstoned path revives the row (P0-2 edge)."""
    p = tmp_path / "revived.md"
    p.write_text("v")
    tombstone = _row(path=str(p), sha256="old", status="deleted")
    a = decide_action(path=p, sha256="new", mtime=0, by_path=tombstone, by_sha=None)
    assert a.kind == ACTION_MODIFIED
    assert a.doc_id == "D0001"
    assert "revive_tombstone" in a.note


def test_next_doc_id_increments(registry) -> None:
    with registry.transaction() as conn:
        d1 = next_doc_id(conn)
        d2 = next_doc_id(conn)
    assert d1 == "D0001"
    assert d2 == "D0002"


def test_next_doc_id_never_reuses(registry) -> None:
    """doc_id 永不复用（09 §2）。"""
    with registry.transaction() as conn:
        first = next_doc_id(conn)
        # Simulate deleted row still holding the doc_id
        cur = conn.execute("SELECT 1")
        cur.fetchone()  # noop
    # Even if the rows table is wiped, counter is in id_counters
    with registry.transaction() as conn:
        # Re-fetch counter; should never go back to D0001
        cur = conn.execute("SELECT value FROM id_counters WHERE name = 'doc_id'").fetchone()
        assert cur["value"] >= 1
    with registry.transaction() as conn:
        second = next_doc_id(conn)
    assert second != first
    assert int(second[1:]) > int(first[1:])


def test_list_files_filter_by_corpus(registry) -> None:
    with registry.transaction() as conn:
        apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, "/a.md", "h1", 0),
            corpus="references",
            is_duplicate=False,
        )
        apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, "/b.md", "h2", 0),
            corpus="design",
            is_duplicate=False,
        )
    with registry.read_only() as conn:
        ref_rows = list_files(conn, corpus="references")
        all_rows = list_files(conn)
    assert len(ref_rows) == 1 and ref_rows[0].path == "/a.md"
    assert len(all_rows) == 2
