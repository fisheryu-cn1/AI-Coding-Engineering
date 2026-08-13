"""SQLite 注册库 (设计 05 §2.1).

五张表 + FTS5，吸收评审修订 07 全部关键修改：

- **files** —— ``pages``（FR-1.5，05 §2.1）+ ``summary_stale``（06 §2.6，
  PDF 变更后策展摘要被标记 stale）+ ``extract_status ∈
  {pending, ok, flat, no_text, failed}`` + ``corpus ∈
  {references, research, design, inbox, external}``
- **tasks** —— ``run_after``（07 §7.2 退避）+ ``kind`` 枚举含 ``tombstone``
  （R3）+ WAL 状态机
- **inbox** —— arxiv_id 唯一索引（去重）+ ``scoring_module`` /
  ``scoring_version`` / ``scoring_notes``（FR-6.7 评分可追溯）
- **collect_log** —— 每次收集运行的台账（FR-6.4）
- **config_audit** —— 配置变更审计（kb config set / set 写此表）
- **llm_usage** —— LLM token 与费用记账（07 §9 报告）

**FTS5** 用 ``tokenize='trigram'``（02 §2 D8）：中英兼顾。

S8（LadybugDB 无属性二级索引）仅约束图库，SQLite 这边合理建索引，但
我们仍然 *不为非主键建索引* —— 当前规模下 PK + WHERE 已经够用。
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

#: Schema version, used to detect incompatible on-disk DBs and force a
#: rebuild if needed (M2 之后会演化为真正的迁移器；M1 仅记录。
SCHEMA_VERSION = 1

#: Five main tables (设计 05 §2.1)
TABLE_FILES = "files"
TABLE_TASKS = "tasks"
TABLE_INBOX = "inbox"
TABLE_COLLECT_LOG = "collect_log"
TABLE_CONFIG_AUDIT = "config_audit"
TABLE_LLM_USAGE = "llm_usage"

#: FTS5 virtual table (设计 05 §2.1)
TABLE_FTS_CHUNKS = "fts_chunks"

ALL_TABLES: tuple[str, ...] = (
    TABLE_FILES,
    TABLE_TASKS,
    TABLE_INBOX,
    TABLE_COLLECT_LOG,
    TABLE_CONFIG_AUDIT,
    TABLE_LLM_USAGE,
    TABLE_FTS_CHUNKS,
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class RegistryError(RuntimeError):
    """Raised for any registry-level problem (corrupt DB, migration needed, …)."""


# ---------------------------------------------------------------------------
# Registry class
# ---------------------------------------------------------------------------


@dataclass
class Registry:
    """Thin SQLite wrapper.

    The connection is opened in *WAL* mode for concurrent reads (设计 03 §6)；
    writes are serialized by :func:`kbapp.core.lock.acquire_write_lock` in
    the CLI layer.
    """

    db_path: Path

    # -- lifecycle --------------------------------------------------------

    def connect(self) -> sqlite3.Connection:
        """Open a connection with sane defaults (WAL, FK, Row factory)."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            str(self.db_path),
            isolation_level=None,  # autocommit; explicit BEGIN elsewhere
            timeout=30.0,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def initialize(self, conn: sqlite3.Connection | None = None) -> None:
        """Create tables and indexes if missing."""
        own = conn is None
        if own:
            conn = self.connect()
        try:
            self._apply_ddl(conn)
        finally:
            if own:
                conn.close()

    def schema_version(self, conn: sqlite3.Connection | None = None) -> int:
        """Return the on-disk schema version; 0 if no DB / no marker table."""
        own = conn is None
        if own:
            conn = self.connect()
        try:
            row = conn.execute(
                "SELECT version FROM schema_version WHERE id = 1"
            ).fetchone()
        except sqlite3.OperationalError:
            return 0
        finally:
            if own:
                conn.close()
        return int(row["version"]) if row else 0

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Context manager that wraps a write transaction.

        On exception the txn is rolled back; otherwise committed.
        """
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.execute("COMMIT")
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.OperationalError:
                pass
            raise
        finally:
            conn.close()

    # -- DDL --------------------------------------------------------------

    def _apply_ddl(self, conn: sqlite3.Connection) -> None:
        for stmt in _DDL_STATEMENTS:
            conn.execute(stmt)
        # Record schema version
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_version ("
            "  id INTEGER PRIMARY KEY CHECK (id = 1),"
            "  version INTEGER NOT NULL,"
            "  set_at TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "INSERT OR REPLACE INTO schema_version (id, version, set_at) "
            "VALUES (1, ?, ?)",
            (SCHEMA_VERSION, _now_iso()),
        )

    # -- helpers used by tests / introspection -----------------------------

    def list_tables(self, conn: sqlite3.Connection | None = None) -> list[str]:
        own = conn is None
        if own:
            conn = self.connect()
        try:
            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
                "AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        finally:
            if own:
                conn.close()
        return [r["name"] for r in rows]

    def has_column(
        self,
        table: str,
        column: str,
        conn: sqlite3.Connection | None = None,
    ) -> bool:
        own = conn is None
        if own:
            conn = self.connect()
        try:
            rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        finally:
            if own:
                conn.close()
        return any(r["name"] == column for r in rows)


# ---------------------------------------------------------------------------
# DDL statements (设计 05 §2.1; 吸收 07 S3/S4/R3/§6/§9)
# ---------------------------------------------------------------------------

_DDL_STATEMENTS: tuple[str, ...] = (
    # ----- files (FR-1.5, FR-4.1, 07 §10.3) ----------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_FILES} (
      doc_id         TEXT PRIMARY KEY,
      path           TEXT NOT NULL UNIQUE,
      sha256         TEXT NOT NULL,
      mtime          INTEGER NOT NULL,
      topic          TEXT,
      doc_type       TEXT,
      corpus         TEXT NOT NULL,
      extract_status TEXT NOT NULL DEFAULT 'pending',
      status         TEXT NOT NULL DEFAULT 'new',
      arxiv_id       TEXT,
      version        TEXT,
      authors        TEXT,
      published      TEXT,
      pages          INTEGER,
      title          TEXT,
      summary_source TEXT NOT NULL DEFAULT 'none',
      summary_path   TEXT,
      summary_stale  INTEGER NOT NULL DEFAULT 0,
      updated_at     TEXT NOT NULL
    )
    """,
    f"CREATE INDEX IF NOT EXISTS idx_files_topic ON {TABLE_FILES}(topic)",
    f"CREATE INDEX IF NOT EXISTS idx_files_status ON {TABLE_FILES}(status)",
    f"CREATE INDEX IF NOT EXISTS idx_files_sha256 ON {TABLE_FILES}(sha256)",
    f"CREATE INDEX IF NOT EXISTS idx_files_arxiv_id ON {TABLE_FILES}(arxiv_id)",
    # ----- tasks (R3 tombstone + 07 §7.2 run_after) ---------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_TASKS} (
      id           TEXT PRIMARY KEY,
      kind         TEXT NOT NULL,
      payload      TEXT NOT NULL,
      status       TEXT NOT NULL DEFAULT 'pending',
      attempts     INTEGER NOT NULL DEFAULT 0,
      max_attempts INTEGER NOT NULL DEFAULT 3,
      run_after    TEXT,
      error        TEXT,
      created_at   TEXT NOT NULL,
      started_at   TEXT,
      finished_at  TEXT
    )
    """,
    f"CREATE INDEX IF NOT EXISTS idx_tasks_status ON {TABLE_TASKS}(status, created_at)",
    f"CREATE INDEX IF NOT EXISTS idx_tasks_kind ON {TABLE_TASKS}(kind)",
    # ----- inbox (FR-6.3, FR-6.7) --------------------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_INBOX} (
      id              TEXT PRIMARY KEY,
      source          TEXT NOT NULL,
      url             TEXT,
      title           TEXT NOT NULL,
      arxiv_id        TEXT,
      sha256          TEXT,
      relevance_score REAL,
      verdict         TEXT NOT NULL DEFAULT 'pending',
      scoring_module  TEXT NOT NULL DEFAULT 'default',
      scoring_version TEXT,
      scoring_notes   TEXT,
      suggested_topic TEXT,
      created_at      TEXT NOT NULL
    )
    """,
    f"CREATE INDEX IF NOT EXISTS idx_inbox_verdict ON {TABLE_INBOX}(verdict, relevance_score DESC)",
    f"CREATE UNIQUE INDEX IF NOT EXISTS idx_inbox_arxiv ON {TABLE_INBOX}(arxiv_id) "
    "WHERE arxiv_id IS NOT NULL",
    # ----- collect_log (FR-6.4) ----------------------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_COLLECT_LOG} (
      id          TEXT PRIMARY KEY,
      source      TEXT NOT NULL,
      query       TEXT,
      title       TEXT,
      arxiv_id    TEXT,
      sha256      TEXT,
      score       REAL,
      disposition TEXT NOT NULL,
      run_id      TEXT NOT NULL,
      created_at  TEXT NOT NULL
    )
    """,
    f"CREATE INDEX IF NOT EXISTS idx_collect_run ON {TABLE_COLLECT_LOG}(run_id)",
    f"CREATE INDEX IF NOT EXISTS idx_collect_arxiv ON {TABLE_COLLECT_LOG}(arxiv_id)",
    # ----- config_audit (kb config set) ----------------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_CONFIG_AUDIT} (
      id        INTEGER PRIMARY KEY AUTOINCREMENT,
      ts        TEXT NOT NULL,
      key       TEXT NOT NULL,
      old_value TEXT,
      new_value TEXT,
      source    TEXT NOT NULL
    )
    """,
    f"CREATE INDEX IF NOT EXISTS idx_config_audit_key ON {TABLE_CONFIG_AUDIT}(key, ts)",
    # ----- llm_usage (07 §9) -------------------------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_LLM_USAGE} (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      ts            TEXT NOT NULL,
      model         TEXT NOT NULL,
      purpose       TEXT NOT NULL,
      input_tokens  INTEGER NOT NULL DEFAULT 0,
      output_tokens INTEGER NOT NULL DEFAULT 0,
      cost          REAL,
      doc_id        TEXT
    )
    """,
    f"CREATE INDEX IF NOT EXISTS idx_llm_usage_ts ON {TABLE_LLM_USAGE}(ts)",
    f"CREATE INDEX IF NOT EXISTS idx_llm_usage_doc ON {TABLE_LLM_USAGE}(doc_id)",
    # ----- fts_chunks (02 §2 D8 trigram) -------------------------------
    f"""
    CREATE VIRTUAL TABLE IF NOT EXISTS {TABLE_FTS_CHUNKS} USING fts5(
      chunk_id UNINDEXED,
      doc_id   UNINDEXED,
      section_path,
      title,
      text,
      tokenize='trigram'
    )
    """,
)


# ---------------------------------------------------------------------------
# Helpers (not full DAOs yet — those come in M2 once the call sites exist)
# ---------------------------------------------------------------------------


def config_audit(
    conn: sqlite3.Connection,
    *,
    key: str,
    old_value: Any,
    new_value: Any,
    source: str,
) -> None:
    """Insert a row into ``config_audit``. Used by ``kb config set``.

    ``source`` should be one of ``{'cli', 'file_edit', 'auto'}``.
    """
    conn.execute(
        f"INSERT INTO {TABLE_CONFIG_AUDIT} (ts, key, old_value, new_value, source) "
        f"VALUES (?, ?, ?, ?, ?)",
        (_now_iso(), key, _encode(old_value), _encode(new_value), source),
    )


def _now_iso() -> str:
    from datetime import datetime
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return repr(value)


__all__ = [
    "ALL_TABLES",
    "Registry",
    "RegistryError",
    "SCHEMA_VERSION",
    "TABLE_COLLECT_LOG",
    "TABLE_CONFIG_AUDIT",
    "TABLE_FILES",
    "TABLE_FTS_CHUNKS",
    "TABLE_INBOX",
    "TABLE_LLM_USAGE",
    "TABLE_TASKS",
    "config_audit",
]
