# GraphIt-KB 数据模型（M2 SQLite 注册库）

> 适用范围：`code/kb-app/src/kbapp/core/registry.py` 的 DDL。
> 八张主表 + FTS5 + `schema_version` 元表，吸收评审修订 S3/S4/R3、§6/§9 与 M2 补充设计 09 §2/§8。

## 设计依据

- `design/kb-app/03-技术概要设计.md` §2（存储布局）、§6（WAL）
- `design/kb-app/05-详细设计方案.md` §2.1（DDL 定义）
- `design/kb-app/07-详细设计评审报告.md` S3、S4、R3、§6、§9
- `design/kb-app/09-M2补充设计.md` §2（doc_id）、§8（topics 表）
- `design/kb-app/02-技术选型方案.md` §2 D8（中文检索 tokenize='trigram'）

## 总览

| 表 | 用途 | 关键列 |
|---|---|---|
| `files` | 已索引文档元数据 | `sha256`, `mtime`, `summary_stale`, `pages`, `extract_status`, `status` |
| `tasks` | 任务队列 | `kind`, `run_after`, `attempts`/`max_attempts` |
| `inbox` | 自动收集的待审素材 | `arxiv_id` (unique when not null), `scoring_module`, `verdict` |
| `collect_log` | 收集运行台账 | `run_id`, `disposition` |
| `config_audit` | 配置变更审计 | `key`, `old_value`, `new_value`, `source` |
| `llm_usage` | LLM token 与费用记账 | `model`, `purpose`, `input_tokens`, `output_tokens`, `cost` |
| `topics` | 主题清单 + 质心预留 | `name`, `doc_count`, `centroid` (M2 恒 NULL) |
| `id_counters` | doc_id 全局顺序号 | `name`, `value` |
| `fts_chunks` | FTS5 倒排索引（trigram） | `chunk_id`, `doc_id`, `text` |
| `schema_version` | 单行元表 | `version` |

`ALL_TABLES = (TABLE_FILES, TABLE_TASKS, TABLE_INBOX, TABLE_COLLECT_LOG, TABLE_CONFIG_AUDIT, TABLE_LLM_USAGE, TABLE_TOPICS, TABLE_ID_COUNTERS, TABLE_FTS_CHUNKS)`。

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

**doc_id 与 status（09 §2）**：`doc_id` 由 `id_counters` 分配，格式 `D%04d`，**永不复用**。`status` 枚举（应用层校验，DDL 为 TEXT）：

| status | 含义 | 谁写入 |
|---|---|---|
| `new` | 新扫描/修改待解析 | scan（new/modified） |
| `active` | 解析 + 分类成功 | `stage_classify` |
| `needs_confirm` | 分类不确定或解析失败 | `stage_classify` / `stage_parse` |
| `duplicate` | sha256 重复（不入队、不入 FTS） | scan（duplicate） |
| `deleted` | 墓碑（源文件消失） | scan（deleted） |

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

**值编码**：`old_value`/`new_value` 为 TEXT，统一以 `json.dumps(ensure_ascii=False)` 编码（字符串带 JSON 引号，全部取值可机器解析；`None` 存 SQL NULL）。`source` 允许 `{cli, file_edit, auto}`，已对齐 05 §2.1。

## `llm_usage` 表（07 §9）

```sql
CREATE TABLE IF NOT EXISTS llm_usage (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  ts            TEXT NOT NULL,
  model         TEXT NOT NULL,
  purpose       TEXT NOT NULL,     -- {classify, summarize, extract, arbitrate, embed}（对齐 05 §2.1）
  input_tokens  INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  cost          REAL,
  doc_id        TEXT
)
```

M2 起每次 LLM 调用写入（`record_llm_usage`）；`cost` 在 M2 恒 NULL（价格表来源未定，09 §9/§14.9）。M2 分类走纯规则降级，故实际只在安装了 `llm` extra 且调用 LLM 时才产生行；`kb maintenance report` 用于月度费用汇总。

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
- **M2 已落地**（09 §6）：`stage_chunk` 分块后即写入 `fts_chunks`（`chunk_id = "<doc_id>#c%03d"`）；重解析按 `doc_id` 先删后插保证幂等。
- **分块存储双写**：可检索文本存 `fts_chunks.text`；带字符偏移 / `page_range` 的完整 chunk 对象存 `cache/extracted/<sha256>.json`（05 §2.4）。M2 未建独立的物理 `chunks` 表——向量 embedding（M3）将读 `fts_chunks` 或缓存 JSON。

## `schema_version` 表

单行元表，标记当前 DDL 版本。M1 记录 v1；**M2 记录 v2**（新增 `topics` / `id_counters`，09 §8/§2）。M3 起会演化为真正的迁移器（v2 → v3 ...）。

## `topics` 表（M2 新增，09 §8）

```sql
CREATE TABLE IF NOT EXISTS topics (
  name        TEXT PRIMARY KEY,
  description TEXT,
  centroid    BLOB,                  -- M3: bge-m3 质心（float32 序列化）；M2 恒 NULL
  doc_count   INTEGER NOT NULL DEFAULT 0,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
)
```

`kb init` 从 `config.core_topics` 播种（`seed_topics` 幂等）；`files.topic` 应用层引用 `topics.name`（不加外键，允许临时主题）。`doc_count` 由流水线 `stage_classify` / `set_topic` 维护。M2 分类为关键词粗排（09 §7），质心列 M3 才填。

## `id_counters` 表（M2 新增，09 §2）

```sql
CREATE TABLE IF NOT EXISTS id_counters (
  name  TEXT PRIMARY KEY,
  value INTEGER NOT NULL
)
```

`doc_id` 全局顺序号计数器。`next_doc_id()` 在扫描事务内自增并返回 `D%04d`；单写锁 + 事务保证唯一，`doc_id` 永不复用。M2 仅使用 `name='doc_id'` 这一行，但表结构通用（M3+ 可复用于其它顺序号）。

## 不在 M2 范围

- `docs`、`sections`、`entities`、`relations` 等图谱节点 —— M5 LadybugDB 落地（不在 SQLite）。
- 独立物理 `chunks` 表 —— M3 向量检索评估；M2 分块直接写入 `fts_chunks` + 缓存 JSON。
- `users` / `permissions` —— 单用户本地工具，不需要。

## 已知约束

1. SQLite WAL 在网络盘（NFS / SMB）下不稳定；`README.md` 提示用户放在本地文件系统。
2. 同一进程多连接默认串行化（`isolation_level=None` 强制 autocommit，事务显式 begin）；不同进程并发写会被 SQLite 内部 mutex 串行化。
3. 大文档（>10MB 文本）不存 SQLite；只存元数据 + FTS5 chunks 索引，原文走 `cache/extracted/<sha256>.json`。