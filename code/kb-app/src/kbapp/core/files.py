"""Document registry domain logic — the doc_id decision table (09 §2).

The scan loop asks ``decide_action()`` for every candidate file on disk and
applies the returned :class:`ScanAction`. The five cases match the table in
the M2 supplementary design (09 §2):

| case       | path match | sha256 match      | result                 |
|------------|------------|-------------------|------------------------|
| new        | none       | none              | allocate next doc_id   |
| modified   | yes        | changed           | keep doc_id, re-parse  |
| moved      | no         | yes, old path gone| keep doc_id, update path |
| duplicate  | yes        | yes, unchanged    | new id, status=duplicate (no parse, no FTS) |
| deleted    | (path gone)| no move match     | status=deleted (tombstone; M5 graph soft-delete) |

The scan loop is single-writer (M2 串行 runner, 09 §10) so the four-corner
comparison does not require extra locking; the doc_id counter is atomic via
the registry transaction.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from kbapp.core.registry import (
    FileRow,
    next_doc_id,
    upsert_file,
)

#: Outcome kinds — see module docstring table.
ACTION_NEW = "new"
ACTION_MODIFIED = "modified"
ACTION_MOVED = "moved"
ACTION_DUPLICATE = "duplicate"
ACTION_DELETED = "deleted"
ACTION_UNCHANGED = "unchanged"  # internal: skip (no DB write)


@dataclass
class ScanAction:
    """Result of comparing one on-disk file to the registry."""

    kind: str
    doc_id: str | None
    path: str
    sha256: str
    mtime: int
    note: str = ""


# ---------------------------------------------------------------------------
# Decision table (the single place where 09 §2 lives in code)
# ---------------------------------------------------------------------------


def decide_action(
    *,
    path: Path,
    sha256: str,
    mtime: int,
    by_path: FileRow | None,
    by_sha: FileRow | None,
) -> ScanAction:
    """Return the :class:`ScanAction` for one candidate.

    ``by_path`` is the row matching ``path`` (if any); ``by_sha`` is the row
    matching ``sha256`` (if any). Both may be ``None``.
    """
    p = str(path)

    if by_path is not None and by_path.status == "deleted":
        # A tombstone (status='deleted') sits at this path: the file was
        # deleted in a prior scan and has since reappeared. Revive the row
        # in place (keep its doc_id, re-parse) rather than allocating a new
        # doc_id that would collide on ``files.path`` UNIQUE.
        return ScanAction(
            ACTION_MODIFIED,
            by_path.doc_id,
            p,
            sha256,
            mtime,
            note=f"revive_tombstone old_sha={by_path.sha256[:8]}",
        )

    if by_path is not None and by_path.sha256 == sha256:
        # path & content match → nothing to do
        return ScanAction(ACTION_UNCHANGED, by_path.doc_id, p, sha256, mtime)

    if by_path is not None and by_path.sha256 != sha256:
        # path matched but content changed → modified, keep doc_id
        return ScanAction(
            ACTION_MODIFIED,
            by_path.doc_id,
            p,
            sha256,
            mtime,
            note=f"old_sha={by_path.sha256[:8]}",
        )

    if by_sha is not None:
        # content seen before. If the previous path is gone from disk, treat
        # as a move (zero re-extract). Otherwise the file exists at two
        # places → duplicate (gets a new doc_id, no parse/FTS).
        if not Path(by_sha.path).exists():
            return ScanAction(
                ACTION_MOVED,
                by_sha.doc_id,
                p,
                sha256,
                mtime,
                note=f"from={by_sha.path}",
            )
        return ScanAction(
            ACTION_DUPLICATE,
            None,  # doc_id will be allocated by caller
            p,
            sha256,
            mtime,
            note=f"also_at={by_sha.path}",
        )

    # No path match, no content match → new file.
    return ScanAction(ACTION_NEW, None, p, sha256, mtime)


def detect_deleted(
    *,
    on_disk_paths: set[str],
    registered_rows: list[FileRow],
) -> list[FileRow]:
    """Find registered rows whose path no longer exists.

    Rows already tombstoned (``status='deleted'``) are skipped — they keep
    their original path (see :func:`apply_deleted`), so re-flagging them
    every scan would be pure noise and would double-report deletions.
    """
    return [r for r in registered_rows if r.path not in on_disk_paths and r.status != "deleted"]


# ---------------------------------------------------------------------------
# Apply — turn a ScanAction into DB writes
# ---------------------------------------------------------------------------


def apply_new_or_duplicate(
    conn: sqlite3.Connection,
    *,
    action: ScanAction,
    corpus: str,
    is_duplicate: bool,
) -> str:
    """Allocate a doc_id and insert a ``files`` row. Returns the new doc_id.

    ``is_duplicate=True`` sets ``status='duplicate'`` and skips parse/enqueue
    (caller's responsibility — this helper only persists).
    """
    if action.doc_id is None:
        action = ScanAction(
            action.kind,
            next_doc_id(conn),
            action.path,
            action.sha256,
            action.mtime,
            action.note,
        )
    upsert_file(
        conn,
        doc_id=action.doc_id,
        path=action.path,
        sha256=action.sha256,
        mtime=action.mtime,
        corpus=corpus,
        extract_status="pending",
        status="duplicate" if is_duplicate else "new",
    )
    return action.doc_id


def apply_modified(conn: sqlite3.Connection, action: ScanAction, *, corpus: str) -> None:
    """Update an existing doc_id's path/sha256/mtime; reset status='new'.

    Preserves identity fields (topic / doc_type / curated-summary binding)
    so a re-parse doesn't drop the manifest link. If the source file changed
    under a curated summary, mark ``summary_stale=1`` (09 §5).
    """
    assert action.doc_id is not None
    row = next(iter(_row_lookup(conn, action.doc_id)), None)
    stale = 1 if (row is not None and row.summary_source == "curated") else 0
    upsert_file(
        conn,
        doc_id=action.doc_id,
        path=action.path,
        sha256=action.sha256,
        mtime=action.mtime,
        corpus=corpus,
        extract_status="pending",
        status="new",  # triggers re-parse in the runner
        topic=row.topic if row else None,
        doc_type=row.doc_type if row else None,
        arxiv_id=row.arxiv_id if row else None,
        version=row.version if row else None,
        authors=row.authors if row else None,
        published=row.published if row else None,
        pages=row.pages if row else None,
        title=row.title if row else None,
        summary_source=row.summary_source if row else "none",
        summary_path=row.summary_path if row else None,
        summary_stale=stale,
    )


def apply_moved(conn: sqlite3.Connection, action: ScanAction) -> None:
    """Update only the path (content & mtime also refreshed). No status reset."""
    assert action.doc_id is not None
    row = next(iter(_row_lookup(conn, action.doc_id)))
    upsert_file(
        conn,
        doc_id=action.doc_id,
        path=action.path,
        sha256=action.sha256,
        mtime=action.mtime,
        corpus=row.corpus,
        extract_status=row.extract_status,
        status=row.status,
        topic=row.topic,
        doc_type=row.doc_type,
        arxiv_id=row.arxiv_id,
        version=row.version,
        authors=row.authors,
        published=row.published,
        pages=row.pages,
        title=row.title,
        summary_source=row.summary_source,
        summary_path=row.summary_path,
        summary_stale=row.summary_stale,
    )


def apply_deleted(conn: sqlite3.Connection, doc_id: str) -> None:
    """Mark a row as deleted (tombstone).

    09 §2: the tombstone sets only ``status='deleted'``. The path/sha256/mtime
    and identity fields are **preserved** so M5 graph soft-delete can still
    locate the row, and so a later re-add at the same path revives the row
    instead of colliding on the ``files.path`` UNIQUE constraint (P0-2).
    """
    row = next(iter(_row_lookup(conn, doc_id)), None)
    if row is None:
        return
    upsert_file(
        conn,
        doc_id=doc_id,
        path=row.path,
        sha256=row.sha256,
        mtime=row.mtime,
        corpus=row.corpus,
        extract_status="failed",
        status="deleted",
        topic=row.topic,
        doc_type=row.doc_type,
        arxiv_id=row.arxiv_id,
        version=row.version,
        authors=row.authors,
        published=row.published,
        pages=row.pages,
        title=row.title,
        summary_source=row.summary_source,
        summary_path=row.summary_path,
        summary_stale=row.summary_stale,
    )


def _row_lookup(conn: sqlite3.Connection, doc_id: str) -> list[FileRow]:
    """Tiny helper: load a single row by doc_id."""
    from kbapp.core.registry import get_file  # local import to avoid cycle

    row = get_file(conn, doc_id)
    return [row] if row is not None else []


__all__ = [
    "ACTION_DELETED",
    "ACTION_DUPLICATE",
    "ACTION_MODIFIED",
    "ACTION_MOVED",
    "ACTION_NEW",
    "ACTION_UNCHANGED",
    "ScanAction",
    "apply_deleted",
    "apply_modified",
    "apply_moved",
    "apply_new_or_duplicate",
    "decide_action",
    "detect_deleted",
]
