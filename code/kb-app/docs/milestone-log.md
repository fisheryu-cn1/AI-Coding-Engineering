# GraphIt-KB 里程碑日志（M1 → 落地映射）

> 把设计评审与方案决策 → 代码位置的映射集中记录；后续里程碑追加新行。
> 评审依据：`design/kb-app/07-详细设计评审报告.md`。

## M1 地基（2026-08-13）

| 评审修订 | 决策 | 落地点 | 验证 |
|---|---|---|---|
| S3 | Document 节点级 `valid_from/valid_to`；Section 不带 | SQLite `files.status` + `status` 索引（软删在 graph 节点层 M5 才落地） | `tests/unit/test_registry.py::test_initialize_creates_all_expected_tables` |
| S4 | Document 节点含 `summary/summary_model/summary_generated_at` | SQLite `files.summary_source`、`files.summary_path`、`files.summary_stale`（M1 仅列） | 同上 |
| S7 | 原子写锁：O_EXCL + PID 探测 + mtime 兜底 | `core/lock.py:acquire_write_lock()` | `tests/unit/test_lock.py::test_stale_pid_is_reclaimed` / `test_stale_mtime_is_reclaimed` / `test_corrupt_lock_file_is_reclaimed` |
| S8 | LadybugDB 不支持二级索引（仅约束图库） | SQLite 这边合理建索引（topic/status/sha256/arxiv_id），但不为非 WHERE 列建索引 | `test_no_secondary_indexes_on_files_non_pk_columns` |
| R3 | `tasks.kind` 枚举含 `tombstone` | `core/task.py:TASK_KINDS` 元组 + `Literal` 类型；DDL 是 TEXT 由应用层校验 | `tests/unit/test_task.py::test_enqueue_supports_tombstone_kind` |
| 07 §6 | `tasks.run_after` 用于退避重试 | `core/task.py:backoff_seconds()` (30s→1m→5m) + `mark_failed(retryable)` 写 `run_after` | `test_backoff_schedule_matches_design` / `test_mark_failed_retryable_resets_to_pending_with_run_after` |
| 07 §7.2 | 崩溃恢复：`running` 且 `started_at` 超时 → `pending` | `core/task.py:reset_stale_running()`，阈值 30 分钟 | `test_reset_stale_running_recovers_crashed_tasks` |
| 07 §9 | 新增 `llm_usage` 表 | `core/registry.py:_DDL_STATEMENTS` 中 `TABLE_LLM_USAGE` | `test_llm_usage_table_present` |
| 07 §10.3 | `files.summary_stale` + `files.pages` | DDL 列；M1 仅 schema，M3 起填值 | `test_files_table_has_summary_stale_and_pages` |
| 02 §2 D8 | FTS5 `tokenize='trigram'` | `_DDL_STATEMENTS` 中 `TABLE_FTS_CHUNKS` 创建语句 | `test_fts_chunks_uses_trigram_tokenizer` |
| 03 §6 | SQLite WAL 模式 | `Registry.connect()` 设 `journal_mode=WAL` | `test_wal_mode_enabled` |
| 05 §9 | CLI 退出码：0/1/2 (成功/校验/锁) | `cli/config.py:set_cmd` 三路 raise typer.Exit | `test_config_set_lock_held_exits_2` / `test_config_set_missing_key_exits_with_code_1` |
| 05 §2.5 | Config 点路径 + 原子写 + 与默认值 diff | `core/config.py:get_value` / `set_value` / `dump_config` / `diff_defaults` | `tests/unit/test_config.py`（20 个测试） |

## M1 不实施（明确推迟）

| 设计要点 | 推迟到 | 原因 |
|---|---|---|
| 实体抽取 / Section 树 | M5 | LadybugDB 图谱先于解析+分类落地 |
| 解析器（PDF/HTML/MD/DOCX/TXT） | M2 | 单里程碑聚焦，避免范围蔓延 |
| Embedding / 向量检索 | M3 | 需要先有 `chunks` 表（M2 提供） |
| MCP server | M4 | 需要检索/图谱接口稳定 |
| Web UI | M6 | 需先有稳定的服务层（M3+M5） |
| 评分插件 | M7 | 依赖收集器 + Inbox 工作流 |

## M1 验收清单

- [x] `uv run pytest` 86 项全绿（CLI smoke + 6 个单元测试文件）
- [x] `kb --help` / `kb config show` / `kb config set` / `kb config get` / `kb config diff` / `kb status` 端到端可跑
- [x] 写锁、崩溃锁回收、互斥（`acquire_write_lock` 双调用第二把返回 None）
- [x] SQLite 五表 + FTS5 + 索引齐全；WAL + FK 开启
- [x] 任务状态机 + 退避 + 崩溃恢复（含 max_attempts 耗尽进 failed）
- [x] 评审修订 S3/S4/S7/S8/R3/§6/§7.2/§9/§10.3 全部有代码 / 测试 / 文档落点

## 后续里程碑锚点

参见 [`architecture.md`](architecture.md) "未来锚点" 一节。