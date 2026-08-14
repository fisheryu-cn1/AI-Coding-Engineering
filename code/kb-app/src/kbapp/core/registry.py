"""SQLite 注册库 (设计 05 §2.1).

七张主表 + FTS5 + ``schema_version`` 元表，吸收评审修订 07 全部关键修改
以及 M2 补充设计 09：

- **files** —— ``pages``（FR-1.5，05 §2.1）+ ``summary_stale``（06 §2.6，
  PDF 变更后策展摘要被标记 stale）+ ``extract_status ∈
  {pending, ok, flat, no_text, failed}`` + ``corpus ∈
  {references, research, design, inbox, external}`` + ``status ∈
  {new, active, needs_confirm, duplicate, deleted}``（09 §2）
- **tasks** —— ``run_after``（07 §7.2 退避）+ ``kind`` 枚举含 ``tombstone``
  （R3）+ WAL 状态机
- **inbox** —— arxiv_id 唯一索引（去重）+ ``scoring_module`` /
  ``scoring_version`` / ``scoring_notes``（FR-6.7 评分可追溯）
- **collect_log** —— 每次收集运行的台账（FR-6.4）
- **config_audit** —— 配置变更审计（kb config set / set 写此表）
- **llm_usage** —— LLM token 与费用记账（07 §9 报告）
- **topics** —— 主题清单 + 质心预留（09 §8）
- **id_counters** —— doc_id 全局顺序号（09 §2）

**FTS5** 用 ``tokenize='trigram'``（02 §2 D8）：中英兼顾；M2 解析+分块
后即时填入（09 §6）。

S8（LadybugDB 无属性二级索引）仅约束图库；SQLite 侧为 WHERE/反查列建索引
——设计清单 8 条之外另有 4 条（``idx_files_arxiv_id`` / ``idx_tasks_kind`` /
``idx_collect_arxiv`` / ``idx_llm_usage_doc``，用途见 docs/data-model.md），
但不盲目为所有列建索引。
"""

from __future__ import annotations

import json
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
#: rebuild if needed (M3 起演化为真正的迁移器)。
#: v1 = M1 五表 + FTS5；v2 = M2 新增 topics / id_counters（09 §8、§2）。
SCHEMA_VERSION = 2

#: Tables introduced across milestones (设计 05 §2.1; 09 §8/§2).
TABLE_FILES = "files"
TABLE_TASKS = "tasks"
TABLE_INBOX = "inbox"
TABLE_COLLECT_LOG = "collect_log"
TABLE_CONFIG_AUDIT = "config_audit"
TABLE_LLM_USAGE = "llm_usage"
TABLE_TOPICS = "topics"  # 09 §8: M2 新增
TABLE_ID_COUNTERS = "id_counters"  # 09 §2: M2 新增（doc_id 顺序号）

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
    TABLE_TOPICS,
    TABLE_ID_COUNTERS,
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
            row = conn.execute("SELECT version FROM schema_version WHERE id = 1").fetchone()
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

    @contextmanager
    def read_only(self) -> Iterator[sqlite3.Connection]:
        """Context manager for read-only queries.

        Opens an autocommit connection (no ``BEGIN``) so it does **not**
        take the SQLite write mutex. Use this for ``count_*`` /
        ``list_*`` / ``SELECT``-only flows to keep them concurrent with
        the write lock.
        """
        conn = self.connect()
        try:
            yield conn
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
            "INSERT OR REPLACE INTO schema_version (id, version, set_at) VALUES (1, ?, ?)",
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
    # ----- topics (09 §8) ---------------------------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_TOPICS} (
      name        TEXT PRIMARY KEY,
      description TEXT,
      centroid    BLOB,                  -- M3: bge-m3 质心；M2 恒 NULL
      doc_count   INTEGER NOT NULL DEFAULT 0,
      created_at  TEXT NOT NULL,
      updated_at  TEXT NOT NULL
    )
    """,
    # ----- id_counters (09 §2) ----------------------------------------
    f"""
    CREATE TABLE IF NOT EXISTS {TABLE_ID_COUNTERS} (
      name  TEXT PRIMARY KEY,
      value INTEGER NOT NULL
    )
    """,
)


# ---------------------------------------------------------------------------
# Row dataclasses (lightweight, no behavior — just typed access for DAOs)
# ---------------------------------------------------------------------------


@dataclass
class FileRow:
    """In-memory representation of a row in ``files``."""

    doc_id: str
    path: str
    sha256: str
    mtime: int
    topic: str | None
    doc_type: str | None
    corpus: str
    extract_status: str
    status: str
    arxiv_id: str | None
    version: str | None
    authors: str | None
    published: str | None
    pages: int | None
    title: str | None
    summary_source: str
    summary_path: str | None
    summary_stale: int
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> FileRow:
        return cls(
            doc_id=row["doc_id"],
            path=row["path"],
            sha256=row["sha256"],
            mtime=row["mtime"],
            topic=row["topic"],
            doc_type=row["doc_type"],
            corpus=row["corpus"],
            extract_status=row["extract_status"],
            status=row["status"],
            arxiv_id=row["arxiv_id"],
            version=row["version"],
            authors=row["authors"],
            published=row["published"],
            pages=row["pages"],
            title=row["title"],
            summary_source=row["summary_source"],
            summary_path=row["summary_path"],
            summary_stale=row["summary_stale"],
            updated_at=row["updated_at"],
        )


@dataclass
class TopicRow:
    """In-memory representation of a row in ``topics``."""

    name: str
    description: str | None
    centroid: bytes | None
    doc_count: int
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> TopicRow:
        return cls(
            name=row["name"],
            description=row["description"],
            centroid=row["centroid"],
            doc_count=row["doc_count"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# ---------------------------------------------------------------------------
# files DAO (设计 05 §2.1; 09 §2 doc_id / status 枚举)
# ---------------------------------------------------------------------------

#: Sentinel for :func:`update_file_fields`: write a SQL NULL (clear the column).
#: Unlike ``None`` (which means "leave untouched"), passing ``CLEAR`` for a
#: nullable column emits ``col = NULL``. Used by ``stage_classify`` (topic
#: reset on needs_confirm) and ``set_topic`` (clear-topic override).
CLEAR = object()

#: Allowed values for ``files.status`` (应用层校验，DDL 为 TEXT；09 §2).
FILES_STATUSES: tuple[str, ...] = ("new", "active", "needs_confirm", "duplicate", "deleted")
#: Allowed values for ``files.extract_status`` (03 §4 P1; M2 起落地).
EXTRACT_STATUSES: tuple[str, ...] = ("pending", "ok", "flat", "no_text", "failed")
#: Allowed values for ``files.corpus`` (设计 05 §2.1).
CORPORA: tuple[str, ...] = ("references", "research", "design", "inbox", "external")


def upsert_file(
    conn: sqlite3.Connection,
    *,
    doc_id: str,
    path: str,
    sha256: str,
    mtime: int,
    corpus: str,
    extract_status: str = "pending",
    status: str = "new",
    topic: str | None = None,
    doc_type: str | None = None,
    arxiv_id: str | None = None,
    version: str | None = None,
    authors: str | None = None,
    published: str | None = None,
    pages: int | None = None,
    title: str | None = None,
    summary_source: str = "none",
    summary_path: str | None = None,
    summary_stale: int = 0,
) -> None:
    """Insert or replace a row in ``files`` by ``doc_id``.

    Idempotent: re-running with the same ``doc_id`` overwrites fields.
    ``updated_at`` is always bumped.
    """
    if corpus not in CORPORA:
        raise ValueError(f"未知 corpus：{corpus!r}（允许：{CORPORA}）")
    if extract_status not in EXTRACT_STATUSES:
        raise ValueError(f"未知 extract_status：{extract_status!r}")
    if status not in FILES_STATUSES:
        raise ValueError(f"未知 status：{status!r}")
    conn.execute(
        f"""
        INSERT INTO {TABLE_FILES} (
            doc_id, path, sha256, mtime, topic, doc_type, corpus,
            extract_status, status, arxiv_id, version, authors, published,
            pages, title, summary_source, summary_path, summary_stale, updated_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        ON CONFLICT(doc_id) DO UPDATE SET
            path           = excluded.path,
            sha256         = excluded.sha256,
            mtime          = excluded.mtime,
            topic          = COALESCE(excluded.topic, {TABLE_FILES}.topic),
            doc_type       = COALESCE(excluded.doc_type, {TABLE_FILES}.doc_type),
            corpus         = excluded.corpus,
            extract_status = excluded.extract_status,
            status         = excluded.status,
            arxiv_id       = COALESCE(excluded.arxiv_id, {TABLE_FILES}.arxiv_id),
            version        = COALESCE(excluded.version, {TABLE_FILES}.version),
            authors        = COALESCE(excluded.authors, {TABLE_FILES}.authors),
            published      = COALESCE(excluded.published, {TABLE_FILES}.published),
            pages          = COALESCE(excluded.pages, {TABLE_FILES}.pages),
            title          = COALESCE(excluded.title, {TABLE_FILES}.title),
            summary_source = excluded.summary_source,
            summary_path   = COALESCE(excluded.summary_path, {TABLE_FILES}.summary_path),
            summary_stale  = excluded.summary_stale,
            updated_at     = excluded.updated_at
        """,
        (
            doc_id,
            path,
            sha256,
            mtime,
            topic,
            doc_type,
            corpus,
            extract_status,
            status,
            arxiv_id,
            version,
            authors,
            published,
            pages,
            title,
            summary_source,
            summary_path,
            summary_stale,
            _now_iso(),
        ),
    )


def get_file(conn: sqlite3.Connection, doc_id: str) -> FileRow | None:
    row = conn.execute(f"SELECT * FROM {TABLE_FILES} WHERE doc_id = ?", (doc_id,)).fetchone()
    return FileRow.from_row(row) if row else None


def get_file_by_path(conn: sqlite3.Connection, path: str) -> FileRow | None:
    row = conn.execute(f"SELECT * FROM {TABLE_FILES} WHERE path = ?", (path,)).fetchone()
    return FileRow.from_row(row) if row else None


def get_file_by_sha256(conn: sqlite3.Connection, sha256: str) -> FileRow | None:
    """Return one file matching ``sha256`` (used by scan to detect moves/dupes).

    When multiple rows share a sha256 (rare, e.g. manual re-import), returns
    the most recently updated.
    """
    rows = conn.execute(
        f"SELECT * FROM {TABLE_FILES} WHERE sha256 = ? ORDER BY updated_at DESC LIMIT 1", (sha256,)
    ).fetchall()
    return FileRow.from_row(rows[0]) if rows else None


def list_files(
    conn: sqlite3.Connection,
    *,
    corpus: str | None = None,
    status: str | None = None,
    topic: str | None = None,
    limit: int = 1000,
) -> list[FileRow]:
    sql = f"SELECT * FROM {TABLE_FILES}"
    clauses: list[str] = []
    params: list[Any] = []
    if corpus is not None:
        clauses.append("corpus = ?")
        params.append(corpus)
    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    if topic is not None:
        clauses.append("topic = ?")
        params.append(topic)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY doc_id ASC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [FileRow.from_row(r) for r in rows]


def update_file_fields(
    conn: sqlite3.Connection,
    doc_id: str,
    *,
    status: str | None = None,
    extract_status: str | None = None,
    topic: str | None = None,
    doc_type: str | None = None,
    title: str | None = None,
    pages: int | None = None,
    summary_source: str | None = None,
    summary_path: str | None = None,
    summary_stale: int | None = None,
) -> None:
    """Update a subset of ``files`` columns by ``doc_id``.

    Pass ``None`` (or omit) for fields that should not be touched. To clear
    a nullable column (topic / doc_type / title / pages / summary_path) to
    SQL NULL, pass :data:`CLEAR`.
    """
    sets: list[str] = []
    params: list[Any] = []
    if status is not None:
        sets.append("status = ?")
        params.append(status)
    if extract_status is not None:
        sets.append("extract_status = ?")
        params.append(extract_status)
    for column, value in (
        ("topic", topic),
        ("doc_type", doc_type),
        ("title", title),
        ("pages", pages),
        ("summary_path", summary_path),
    ):
        if value is CLEAR:
            sets.append(f"{column} = NULL")
        elif value is not None:
            sets.append(f"{column} = ?")
            params.append(value)
    if summary_source is not None:
        sets.append("summary_source = ?")
        params.append(summary_source)
    if summary_stale is not None:
        sets.append("summary_stale = ?")
        params.append(summary_stale)
    if not sets:
        return
    sets.append("updated_at = ?")
    params.append(_now_iso())
    params.append(doc_id)
    conn.execute(
        f"UPDATE {TABLE_FILES} SET {', '.join(sets)} WHERE doc_id = ?",
        params,
    )


def count_files_by_status(conn: sqlite3.Connection) -> dict[str, int]:
    """Return ``{status_value: count}`` across all rows."""
    rows = conn.execute(
        f"SELECT status, COUNT(*) AS n FROM {TABLE_FILES} GROUP BY status"
    ).fetchall()
    return {r["status"]: r["n"] for r in rows}


def count_files_by_extract_status(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        f"SELECT extract_status, COUNT(*) AS n FROM {TABLE_FILES} GROUP BY extract_status"
    ).fetchall()
    return {r["extract_status"]: r["n"] for r in rows}


def list_files_needing_confirm(conn: sqlite3.Connection, *, limit: int = 100) -> list[FileRow]:
    rows = conn.execute(
        f"SELECT * FROM {TABLE_FILES} WHERE status = 'needs_confirm' "
        f"ORDER BY updated_at ASC LIMIT ?",
        (limit,),
    ).fetchall()
    return [FileRow.from_row(r) for r in rows]


# ---------------------------------------------------------------------------
# topics DAO (09 §8)
# ---------------------------------------------------------------------------


def upsert_topic(
    conn: sqlite3.Connection,
    *,
    name: str,
    description: str | None = None,
) -> None:
    """Insert a topic row; idempotent (re-running updates description only)."""
    now = _now_iso()
    conn.execute(
        f"""
        INSERT INTO {TABLE_TOPICS} (name, description, doc_count, created_at, updated_at)
        VALUES (?, ?, 0, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            description = COALESCE(excluded.description, {TABLE_TOPICS}.description),
            updated_at  = excluded.updated_at
        """,
        (name, description, now, now),
    )


def seed_topics(conn: sqlite3.Connection, names: list[str]) -> int:
    """Idempotent: insert topics for ``names`` if missing. Returns insert count."""
    inserted = 0
    for name in names:
        cur = conn.execute(f"SELECT 1 FROM {TABLE_TOPICS} WHERE name = ?", (name,)).fetchone()
        if cur is None:
            upsert_topic(conn, name=name)
            inserted += 1
    return inserted


def list_topics(conn: sqlite3.Connection) -> list[TopicRow]:
    rows = conn.execute(f"SELECT * FROM {TABLE_TOPICS} ORDER BY name ASC").fetchall()
    return [TopicRow.from_row(r) for r in rows]


def get_topic(conn: sqlite3.Connection, name: str) -> TopicRow | None:
    row = conn.execute(f"SELECT * FROM {TABLE_TOPICS} WHERE name = ?", (name,)).fetchone()
    return TopicRow.from_row(row) if row else None


def adjust_topic_doc_count(conn: sqlite3.Connection, name: str, delta: int) -> None:
    """Bump ``doc_count`` by ``delta`` (may be negative). No-op if topic absent."""
    conn.execute(
        f"UPDATE {TABLE_TOPICS} SET doc_count = MAX(0, doc_count + ?), "
        f"updated_at = ? WHERE name = ?",
        (delta, _now_iso(), name),
    )


# ---------------------------------------------------------------------------
# id_counters DAO (09 §2 doc_id 全局顺序号)
# ---------------------------------------------------------------------------

#: Counter name used by the scan loop (09 §2).
COUNTER_DOC_ID = "doc_id"


def next_doc_id(conn: sqlite3.Connection) -> str:
    """Atomically increment the doc_id counter and return ``D%04d``.

    Must be called inside a write transaction (caller's responsibility).
    On a fresh registry the counter row is inserted via the trigger-like
    SELECT-then-INSERT/REPLACE pattern; the surrounding transaction ensures
    unique allocation even under contention.
    """
    row = conn.execute(
        f"SELECT value FROM {TABLE_ID_COUNTERS} WHERE name = ?",
        (COUNTER_DOC_ID,),
    ).fetchone()
    if row is None:
        conn.execute(
            f"INSERT INTO {TABLE_ID_COUNTERS} (name, value) VALUES (?, 1)",
            (COUNTER_DOC_ID,),
        )
        n = 1
    else:
        n = row["value"] + 1
        conn.execute(
            f"UPDATE {TABLE_ID_COUNTERS} SET value = ? WHERE name = ?",
            (n, COUNTER_DOC_ID),
        )
    return f"D{n:04d}"


# ---------------------------------------------------------------------------
# fts_chunks DAO (02 §2 D8 trigram; 09 §6 M2 即填)
# ---------------------------------------------------------------------------


def delete_chunks_by_doc(conn: sqlite3.Connection, doc_id: str) -> int:
    """Remove all FTS rows for ``doc_id``. Returns count deleted."""
    cur = conn.execute(f"DELETE FROM {TABLE_FTS_CHUNKS} WHERE doc_id = ?", (doc_id,))
    return cur.rowcount


def insert_chunk(
    conn: sqlite3.Connection,
    *,
    chunk_id: str,
    doc_id: str,
    section_path: str,
    title: str,
    text: str,
) -> None:
    """Insert a single FTS row. Duplicate ``chunk_id`` silently coalesces."""
    conn.execute(
        f"INSERT INTO {TABLE_FTS_CHUNKS} (chunk_id, doc_id, section_path, title, text) "
        f"VALUES (?, ?, ?, ?, ?)",
        (chunk_id, doc_id, section_path, title, text),
    )


def count_chunks(conn: sqlite3.Connection) -> int:
    row = conn.execute(f"SELECT COUNT(*) AS n FROM {TABLE_FTS_CHUNKS}").fetchone()
    return int(row["n"])


def count_chunks_by_doc(conn: sqlite3.Connection, doc_id: str) -> int:
    row = conn.execute(
        f"SELECT COUNT(*) AS n FROM {TABLE_FTS_CHUNKS} WHERE doc_id = ?",
        (doc_id,),
    ).fetchone()
    return int(row["n"])


# ---------------------------------------------------------------------------
# llm_usage DAO (07 §9; M2 起写入)
# ---------------------------------------------------------------------------

#: Allowed purposes (设计 05 §2.1; M2 实际只用 `classify`；M3 扩 `query_expand`/`rerank`，11 §7).
LLM_PURPOSES: tuple[str, ...] = (
    "classify",
    "summarize",
    "extract",
    "arbitrate",
    "embed",
    "query_expand",
    "rerank",
)


def record_llm_usage(
    conn: sqlite3.Connection,
    *,
    model: str,
    purpose: str,
    input_tokens: int,
    output_tokens: int,
    cost: float | None = None,
    doc_id: str | None = None,
) -> None:
    """Append to ``llm_usage``. ``cost`` is NULL in M2 (09 §9 / §14.9)."""
    if purpose not in LLM_PURPOSES:
        raise ValueError(f"未知 purpose：{purpose!r}（允许：{LLM_PURPOSES}）")
    conn.execute(
        f"INSERT INTO {TABLE_LLM_USAGE} "
        f"(ts, model, purpose, input_tokens, output_tokens, cost, doc_id) "
        f"VALUES (?, ?, ?, ?, ?, ?, ?)",
        (_now_iso(), model, purpose, int(input_tokens), int(output_tokens), cost, doc_id),
    )


# ---------------------------------------------------------------------------
# config_audit (kb config set)
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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    from datetime import datetime

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _encode(value: Any) -> str | None:
    """Encode a config value for storage in ``config_audit``.

    - ``None`` is stored as SQL NULL (via Python ``None``).
    - Scalars (``str`` / ``int`` / ``float`` / ``bool``) round-trip via
      ``json.dumps`` to keep the representation stable and machine-readable.
    - ``list`` / ``dict`` are JSON-serialized (UTF-8, no ASCII escapes) so
      downstream tooling can deserialize without depending on Python
      ``repr`` quirks.
    """
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


__all__ = [
    "ALL_TABLES",
    "CLEAR",
    "COUNTER_DOC_ID",
    "CORPORA",
    "EXTRACT_STATUSES",
    "FILES_STATUSES",
    "FileRow",
    "LLM_PURPOSES",
    "Registry",
    "RegistryError",
    "SCHEMA_VERSION",
    "TABLE_COLLECT_LOG",
    "TABLE_CONFIG_AUDIT",
    "TABLE_FILES",
    "TABLE_FTS_CHUNKS",
    "TABLE_ID_COUNTERS",
    "TABLE_INBOX",
    "TABLE_LLM_USAGE",
    "TABLE_TASKS",
    "TABLE_TOPICS",
    "TopicRow",
    "adjust_topic_doc_count",
    "config_audit",
    "count_chunks",
    "count_chunks_by_doc",
    "count_files_by_extract_status",
    "count_files_by_status",
    "delete_chunks_by_doc",
    "get_file",
    "get_file_by_path",
    "get_file_by_sha256",
    "get_topic",
    "insert_chunk",
    "list_files",
    "list_files_needing_confirm",
    "list_topics",
    "next_doc_id",
    "record_llm_usage",
    "seed_topics",
    "update_file_fields",
    "upsert_file",
    "upsert_topic",
]
