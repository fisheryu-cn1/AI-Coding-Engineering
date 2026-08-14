"""Unit tests for :mod:`kbapp.core.registry`.

Validates:
- All seven tables (five main + schema_version + FTS5) are created
- Indexes exist
- The :data:`07`评审修订 are encoded (summary_stale, pages, run_after,
  tombstone kind support, llm_usage table)
- FTS5 uses trigram tokenizer
- WAL mode is enabled
- Transaction context manager commits/rolls back correctly
"""

from __future__ import annotations

import collections
import sqlite3

import pytest

from kbapp.core.registry import (
    ALL_TABLES,
    SCHEMA_VERSION,
    TABLE_COLLECT_LOG,
    TABLE_CONFIG_AUDIT,
    TABLE_FILES,
    TABLE_FTS_CHUNKS,
    TABLE_INBOX,
    TABLE_LLM_USAGE,
    TABLE_TASKS,
    Registry,
    config_audit,
)


def test_initialize_creates_all_expected_tables(registry: Registry) -> None:
    tables = set(registry.list_tables())
    assert TABLE_FILES in tables
    assert TABLE_TASKS in tables
    assert TABLE_INBOX in tables
    assert TABLE_COLLECT_LOG in tables
    assert TABLE_CONFIG_AUDIT in tables
    assert TABLE_LLM_USAGE in tables
    # FTS5 virtual tables appear in sqlite_master as 'table'
    assert TABLE_FTS_CHUNKS in tables
    # Schema version tracker is present
    assert "schema_version" in tables


def test_schema_version_recorded(registry: Registry) -> None:
    assert registry.schema_version() == SCHEMA_VERSION


def test_files_table_has_summary_stale_and_pages() -> None:
    """评审修订: files 必须包含 summary_stale 与 pages 字段。"""
    # We need a temp DB to introspect columns without shared state
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.sqlite"
        r = Registry(db)
        r.initialize()
        with r.connect() as conn:
            cols = {
                row["name"] for row in conn.execute(f"PRAGMA table_info({TABLE_FILES})").fetchall()
            }
            assert "summary_stale" in cols
            assert "pages" in cols


def test_tasks_table_supports_tombstone_kind() -> None:
    """The kind column is TEXT (no DB-level enum) — ``tombstone`` is a valid value."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.sqlite"
        r = Registry(db)
        r.initialize()
        with r.connect() as conn:
            conn.execute(
                f"INSERT INTO {TABLE_TASKS} (id, kind, payload, created_at) "
                f"VALUES (?, 'tombstone', '{{}}', '2026-08-13T00:00:00Z')",
                ("t1",),
            )
            row = conn.execute(f"SELECT kind FROM {TABLE_TASKS} WHERE id = 't1'").fetchone()
            assert row["kind"] == "tombstone"


def test_tasks_table_has_run_after_column() -> None:
    """评审修订: tasks.run_after 用于退避重试。"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.sqlite"
        r = Registry(db)
        r.initialize()
        with r.connect() as conn:
            cols = {
                row["name"] for row in conn.execute(f"PRAGMA table_info({TABLE_TASKS})").fetchall()
            }
            assert "run_after" in cols


def test_llm_usage_table_present() -> None:
    """评审修订: 新增 llm_usage 表。"""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "r.sqlite"
        r = Registry(db)
        r.initialize()
        with r.connect() as conn:
            cols = {
                row["name"]
                for row in conn.execute(f"PRAGMA table_info({TABLE_LLM_USAGE})").fetchall()
            }
            for col in ("model", "purpose", "input_tokens", "output_tokens", "cost"):
                assert col in cols


def test_fts_chunks_uses_trigram_tokenizer(registry: Registry) -> None:
    """设计 02 §2 D8: 中文检索用 trigram。"""
    with registry.connect() as conn:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (TABLE_FTS_CHUNKS,),
        ).fetchall()
        sql = rows[0]["sql"]
        assert "tokenize='trigram'" in sql


def test_wal_mode_enabled(registry: Registry) -> None:
    with registry.connect() as conn:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode.lower() == "wal"


def test_foreign_keys_enabled(registry: Registry) -> None:
    with registry.connect() as conn:
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1


def test_initialize_is_idempotent(registry: Registry) -> None:
    """Calling initialize() twice must not raise or duplicate tables/indexes."""
    registry.initialize()
    registry.initialize()
    tables = registry.list_tables()
    counts = collections.Counter(tables)
    # No duplicates
    for t in ALL_TABLES:
        assert counts[t] == 1


def test_transaction_commits(registry: Registry) -> None:
    with registry.transaction() as conn:
        conn.execute(
            f"INSERT INTO {TABLE_CONFIG_AUDIT} (ts, key, old_value, new_value, source) "
            f"VALUES ('2026-08-13T00:00:00Z', 'x', 'old', 'new', 'cli')"
        )
    with registry.connect() as conn:
        n = conn.execute(f"SELECT COUNT(*) AS n FROM {TABLE_CONFIG_AUDIT}").fetchone()["n"]
        assert n == 1


def test_transaction_rolls_back_on_exception(registry: Registry) -> None:
    with pytest.raises(RuntimeError):
        with registry.transaction() as conn:
            conn.execute(
                f"INSERT INTO {TABLE_CONFIG_AUDIT} (ts, key, old_value, new_value, source) "
                f"VALUES ('2026-08-13T00:00:00Z', 'x', 'old', 'new', 'cli')"
            )
            raise RuntimeError("boom")
    with registry.connect() as conn:
        n = conn.execute(f"SELECT COUNT(*) AS n FROM {TABLE_CONFIG_AUDIT}").fetchone()["n"]
        assert n == 0


def test_config_audit_helper_writes_a_row(registry: Registry) -> None:
    with registry.transaction() as conn:
        config_audit(
            conn,
            key="scoring.thresholds.accept",
            old_value=0.70,
            new_value=0.65,
            source="cli",
        )
    with registry.connect() as conn:
        row = conn.execute(
            f"SELECT * FROM {TABLE_CONFIG_AUDIT} WHERE key = ? ORDER BY id DESC LIMIT 1",
            ("scoring.thresholds.accept",),
        ).fetchone()
        assert row["source"] == "cli"
        assert row["old_value"] == "0.7"
        assert row["new_value"] == "0.65"


def test_no_secondary_indexes_on_files_non_pk_columns(registry: Registry) -> None:
    """We *do* add some column indexes for SQLite (S8 only constrains the
    graph DB); this test documents the current intentional set."""
    with registry.connect() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = ?",
            (TABLE_FILES,),
        ).fetchall()
        idx = {r["name"] for r in rows}
    # Sanity: at least the documented ones exist
    assert "idx_files_topic" in idx
    assert "idx_files_status" in idx
    assert "idx_files_sha256" in idx


def test_inbox_arxiv_id_unique_when_present(registry: Registry) -> None:
    """Partial unique index on inbox.arxiv_id (NULLs not enforced)."""
    # First row commits successfully
    with registry.transaction() as conn:
        conn.execute(
            f"INSERT INTO {TABLE_INBOX} (id, source, title, arxiv_id, created_at) "
            f"VALUES ('a1', 'arxiv', 'paper one', '2607.00001', '2026-08-13T00:00:00Z')"
        )
    # Second row with same arxiv_id violates the partial unique index
    with pytest.raises(sqlite3.IntegrityError):
        with registry.transaction() as conn:
            conn.execute(
                f"INSERT INTO {TABLE_INBOX} (id, source, title, arxiv_id, created_at) "
                f"VALUES ('a2', 'arxiv', 'paper one dup', '2607.00001', '2026-08-13T00:00:01Z')"
            )


def test_inbox_arxiv_id_null_allowed(registry: Registry) -> None:
    """NULL arxiv_id values must not be constrained (partial index)."""
    with registry.transaction() as conn:
        conn.execute(
            f"INSERT INTO {TABLE_INBOX} (id, source, title, arxiv_id, created_at) "
            f"VALUES ('n1', 'manual', 'note one', NULL, '2026-08-13T00:00:00Z')"
        )
        conn.execute(
            f"INSERT INTO {TABLE_INBOX} (id, source, title, arxiv_id, created_at) "
            f"VALUES ('n2', 'manual', 'note two', NULL, '2026-08-13T00:00:01Z')"
        )
