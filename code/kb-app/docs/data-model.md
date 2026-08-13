# GraphIt-KB 数据模型（M1 SQLite 注册库）

> 适用范围：`code/kb-app/src/kbapp/core/registry.py` 的 DDL。
> 五张主表 + FTS5 + `schema_version` 元表，吸收评审修订 S3/S4/R3 与 §6/§9。

## 设计依据

- `design/kb-app/03-技术概要设计.md` §2（存储布局）、§6（WAL）
- `design/kb-app/05-详细设计方案.md` §2.1（DDL 定义）
- `design/kb-app/07-详细设计评审报告.md` S3、S4、R3、§6、§9
- `design/kb-app/02-需求文档.md` §2 D8（中文检索 tokenize='trigram'）

## 总览

| 表 | 用途 | 关键列 |
|---|---|---|
| `files` | 已索引文档元数据 | `sha256`, `mtime`, `summary_stale`, `pages`, `extract_status` |
| `tasks` | 任务队列 | `kind`, `run_after`, `attempts`/`max_attempts` |
| `inbox` | 自动收集的待审素材 | `arxiv_id` (unique when not null), `scoring_module`, `verdict` |
| `collect_log` | 收集运行台账 | `run_id`, `disposition` |
| `config_audit` | 配置变更审计 | `key`, `old_value`, `new_value`, `source` |
| `llm_usage` | LLM token 与费用记账 | `model`, `purpose`, `input_tokens`, `output_tokens`, `cost` |
| `fts_chunks` | FTS5 倒排索引（trigram） | `chunk_id`, `doc_id`, `text` |
| `schema_version` | 单行元表 | `version` |

`ALL_TABLES = (TABLE_FILES, TABLE_TASKS, TABLE_INBOX, TABLE_COLLECT_LOG, TABLE_CONFIG_AUDIT, TABLE_LLM_USAGE, TABLE_FTS_CHUNKS)`。

## 连接与 PRAGMA

```python
conn = sqlite3.connect(str(self.db_path), isolation_level=None, timeout=30.0, ...)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")
conn.execute("PRAGMA synchronous=NORMAL")
```

- **WAL** —— 并发读不阻塞写；多进程友好（设计 03 §6）。
- **foreign_keys=ON** —— 默认关闭，DDL 全部加 `_id` 关联时强制打开。
- **synchronous=NORMAL** —— WAL 下的安全/性能折中（崩溃丢最近一页 commit）。
- **isolation_level=None** —— 自动提交；显式 `BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK` 在 `Registry.transaction()` 上下文管理器中。

## `files` 表（评审修订 §10.3）

```sql
CREATE TABLE IF NOT EXISTS files (
  doc_id         TEXT PRIMARY KEY,
  path           TEXT NOT NULL UNIQUE,
  sha256         TEXT NOT NULL,
  mtime          INTEGER NOT NULL,
  topic          TEXT,
  doc_type       TEXT,
  corpus         TEXT NOT NULL,             -- {references, research, design, inbox, external}
  extract_status TEXT NOT NULL DEFAULT 'pending',  -- {pending, ok, flat, no_text, failed}
  status         TEXT NOT NULL DEFAULT 'new',
  arxiv_id       TEXT,
  version        TEXT,
  authors        TEXT,
  published      TEXT,
  pages          INTEGER,                   -- 07 §10.3: PDF 页数
  title          TEXT,
  summary_source TEXT NOT NULL DEFAULT 'none',
  summary_path   TEXT,
  summary_stale  INTEGER NOT NULL DEFAULT 0,-- 07 §10.3: 摘要是否过期
  updated_at     TEXT NOT NULL
)
```

**索引**：

| 索引 | 列 | 用途 |
|---|---|---|
| `idx_files_topic` | `topic` | 按主题过滤 |
| `idx_files_status` | `status` | 增量扫描（status='new'） |
| `idx_files_sha256` | `sha256` | 内容去重 |
| `idx_files_arxiv_id` | `arxiv_id` | 反查 arXiv 来源 |

**评审修订 S8 注释**：LadybugDB 不支持二级索引，所以图谱那边不建额外索引；SQLite 这边加索引（仅 PK + WHERE 走过的列）。

## `tasks` 表（R3 + §7.2）

```sql
CREATE TABLE IF NOT EXISTS tasks (
  id           TEXT PRIMARY KEY,            -- ULID（时间序）
  kind         TEXT NOT NULL,               -- parse/classify/summarize/extract/index/collect/tombstone
  payload      TEXT NOT NULL,               -- JSON 编码
  status       TEXT NOT NULL DEFAULT 'pending',  -- {pending, running, done, failed}
  attempts     INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3,
  run_after    TEXT,                        -- §7.2: 退避后的可执行时刻
  error        TEXT,
  created_at   TEXT NOT NULL,
  started_at   TEXT,
  finished_at  TEXT
)
```

**索引**：

| 索引 | 列 | 用途 |
|---|---|---|
| `idx_tasks_status` | `(status, created_at)` | FIFO 取任务（`next_task` 排序） |
| `idx_tasks_kind` | `kind` | 统计 / 过滤某类任务 |

**R3**：`kind` 是 `TEXT`，由应用层校验；`"tombstone"` 是合法值（M5+ 实体删除任务用）。
**§7.2**：`run_after` 用于 `mark_failed(retryable)` 退避后回到 pending 时记录下次可执行时刻。

## `inbox` 表（FR-6.3 + FR-6.7）

```sql
CREATE TABLE IF NOT EXISTS inbox (
  id              TEXT PRIMARY KEY,
  source          TEXT NOT NULL,
  url             TEXT,
  title           TEXT NOT NULL,
  arxiv_id        TEXT,
  sha256          TEXT,
  relevance_score REAL,
  verdict         TEXT NOT NULL DEFAULT 'pending',  -- {pending, accepted, rejected}
  scoring_module  TEXT NOT NULL DEFAULT 'default',  -- FR-6.7: 评分可追溯
  scoring_version TEXT,
  scoring_notes   TEXT,
  suggested_topic TEXT,
  created_at      TEXT NOT NULL
)
```

**索引**：

| 索引 | 列 | 用途 |
|---|---|---|
| `idx_inbox_verdict` | `(verdict, relevance_score DESC)` | 审核排序 |
| `idx_inbox_arxiv` (UNIQUE, partial) | `arxiv_id WHERE arxiv_id IS NOT NULL` | arXiv 去重（NULL 不约束） |

## `collect_log` 表（FR-6.4）

每次 `kb collect run` 写一行；`run_id` 把同一批次的素材关联起来，便于复盘。

## `config_audit` 表（kb config set）

```sql
CREATE TABLE IF NOT EXISTS config_audit (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ts        TEXT NOT NULL,
  key       TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT,
  source    TEXT NOT NULL          -- {cli, file_edit, auto}
)
```

`kb config set` 写入；`kb config diff` 读取用户当前值与默认值。

## `llm_usage` 表（07 §9）

```sql
CREATE TABLE IF NOT EXISTS llm_usage (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  ts            TEXT NOT NULL,
  model         TEXT NOT NULL,
  purpose       TEXT NOT NULL,     -- {classify, summarize, extract}
  input_tokens  INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  cost          REAL,
  doc_id        TEXT
)
```

M3+ 起每次 LLM 调用写入；`kb maintenance report` 用于月度费用汇总。

## `fts_chunks` 表（FTS5 + trigram）

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks USING fts5(
  chunk_id UNINDEXED,
  doc_id   UNINDEXED,
  section_path,
  title,
  text,
  tokenize='trigram'
)
```

- `tokenize='trigram'`（02 §2 D8）—— 中英兼顾；3 字符滑动窗口生成倒排项。
- `chunk_id` / `doc_id` 不入倒排，仅用于回查。
- M2+ 解析后填入；M1 表结构存在但内容为空。

## `schema_version` 表

单行元表，标记当前 DDL 版本。M1 仅记录（v1）；M3 起会演化为真正的迁移器（v2 / v3 ...）。

## 不在 M1 范围

- `docs`、`sections`、`entities`、`relations` 等图谱节点 —— M5 LadybugDB 落地（不在 SQLite）。
- `topics` 表 —— M2 主题分类落地；M1 只在 `files.topic` 留字符串。
- `users` / `permissions` —— 单用户本地工具，不需要。

## 已知约束

1. SQLite WAL 在网络盘（NFS / SMB）下不稳定；`README.md` 提示用户放在本地文件系统。
2. 同一进程多连接默认串行化（`isolation_level=None` 强制 autocommit，事务显式 begin）；不同进程并发写会被 SQLite 内部 mutex 串行化。
3. 大文档（>10MB 文本）不存 SQLite；只存元数据 + FTS5 chunks 索引，原文走 `cache/extracted/<sha256>.json`。