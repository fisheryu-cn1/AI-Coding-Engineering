# GraphIt-KB 里程碑日志（M1 → 落地映射）

> 把设计评审与方案决策 → 代码位置的映射集中记录；后续里程碑追加新行。
> 评审依据：`design/kb-app/07-详细设计评审报告.md`。

## M1 地基（2026-08-13）

| 评审修订 | 决策 | 落地点 | 验证 |
|---|---|---|---|
| S3 | Document 节点级 `valid_from/valid_to`；Section 不带 | SQLite `files.status` + `status` 索引（软删在 graph 节点层 M5 才落地） | `tests/unit/test_registry.py::test_initialize_creates_all_expected_tables` |
| S4 | Document 节点含 `summary/summary_model/summary_generated_at` | SQLite `files.summary_source`、`files.summary_path`、`files.summary_stale`（M1 仅列） | 同上 |
| S7 | 原子写锁：O_EXCL + PID 探测 + mtime 兜底 | `core/lock.py:acquire_write_lock()` | `tests/unit/test_lock.py::test_stale_pid_is_reclaimed` / `test_stale_mtime_is_reclaimed` / `test_corrupt_lock_file_is_reclaimed` |
| S8 | LadybugDB 不支持二级索引（仅约束图库） | SQLite 侧为 WHERE/反查列建索引；设计清单 8 条之外另建 4 条（`idx_files_arxiv_id`/`idx_tasks_kind`/`idx_collect_arxiv`/`idx_llm_usage_doc`，用途见 data-model.md），已回写 05 §2.1 补注 | `test_no_secondary_indexes_on_files_non_pk_columns` |
| R3 | `tasks.kind` 枚举含 `tombstone` | `core/task.py:TASK_KINDS` 元组 + `Literal` 类型；DDL 是 TEXT 由应用层校验 | `tests/unit/test_task.py::test_enqueue_supports_tombstone_kind` |
| 07 §6 | `tasks.run_after` 用于退避重试 | `core/task.py:backoff_seconds()` (30s→1m→5m) + `mark_failed(retryable)` 写 `run_after` | `test_backoff_schedule_matches_design` / `test_mark_failed_retryable_resets_to_pending_with_run_after` |
| 07 §7.2 | 崩溃恢复：`running` 且 `started_at` 超时 → `pending` | `core/task.py:reset_stale_running()`，阈值 30 分钟 | `test_reset_stale_running_recovers_crashed_tasks` |
| 07 §9 | 新增 `llm_usage` 表 | `core/registry.py:_DDL_STATEMENTS` 中 `TABLE_LLM_USAGE` | `test_llm_usage_table_present` |
| 07 §10.3 | `files.summary_stale` + `files.pages` | DDL 列；M1 仅 schema，M2 起填值（09 §5 manifest 绑定 + stale 检测） | `test_files_table_has_summary_stale_and_pages` |
| 02 §2 D8 | FTS5 `tokenize='trigram'` | `_DDL_STATEMENTS` 中 `TABLE_FTS_CHUNKS` 创建语句 | `test_fts_chunks_uses_trigram_tokenizer` |
| 03 §6 | SQLite WAL 模式 | `Registry.connect()` 设 `journal_mode=WAL` | `test_wal_mode_enabled` |
| 05 §9（M1 补入） | CLI 退出码约定 0/1/2（成功/校验失败/锁冲突或 IO）为 M1 实现时补充，已回写 05 §9 | `cli/config.py:set_cmd` 三路 raise typer.Exit | `test_config_set_lock_held_exits_2` / `test_config_set_missing_key_exits_with_code_1` |
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
| `kb init`（初始化数据目录 / 下载模型 / 落默认 `config.yaml`） | M2 | 04 §2.1 / 05 §8 明确要求；M1 暂由写路径按需建目录 + 首次 `kb config set` 落盘 `config.yaml` 兜底（第二轮起 `resolve_data_dir` 已不再隐式建目录），未提供独立 init 入口；bge-m3 下载引导部分随 M3 Embedding 落地 |

## M1 验收清单

- [x] `uv run pytest` 86 项全绿（CLI smoke + 6 个单元测试文件）
- [x] `kb --help` / `kb config show` / `kb config set` / `kb config get` / `kb config diff` / `kb status` 端到端可跑
- [x] 写锁、崩溃锁回收、互斥（`acquire_write_lock` 双调用第二把返回 None）
- [x] SQLite 五表 + FTS5 + 索引齐全；WAL + FK 开启
- [x] 任务状态机 + 退避 + 崩溃恢复（含 max_attempts 耗尽进 failed）
- [x] 评审修订 S3/S4/S7/S8/R3/§6/§7.2/§9/§10.3 全部有代码 / 测试 / 文档落点

## M1 补充设计登记（设计文档外的实现决策）

> M1 开发中补充、01–07 设计文档未覆盖的决策。契约级变更（CLI 退出码、`kb init` 惰性化、设计外索引、`schema_version` 元表、`config_audit.source` 扩展）已回写 05 §2.1/§8/§9；其余记录于此。

| 决策 | 内容 | 落地点 |
|---|---|---|
| 锁接口形状 | `acquire_write_lock(wait=False)` 在持锁时返回 `None`（而非设计伪代码的 `raise LockHeld`），由 CLI 映射退出码 2；`wait=True` 超时仍抛 `LockHeld` | `core/lock.py:acquire_write_lock()` |
| 锁 stale 阈值 | mtime 兜底阈值取 1 小时（`DEFAULT_STALE_AFTER_SECONDS=3600`；设计未定值） | `core/lock.py:31` |
| 损坏锁文件加固 | 锁文件无合法 PID 时按 stale 回收（设计外加固） | `core/lock.py:_is_lock_held()` |
| 恢复工具 API | `force_release()` / `lock_holder()`（设计未要求，供恢复与诊断） | `core/lock.py:140-157` |
| `TerminalError` | 异常分层：不可重试失败立即终态（设计仅定义 `RetryableError`） | `core/task.py:82-86` |
| attempts 计数时点 | 在 `mark_running` 时 +1（设计伪代码在失败时 +1；净行为等价）。第二轮起默认 `max_attempts=4`（由 3 改为 4），退避 30s→60s→300s 三档全部可达后终态 | `core/task.py:mark_running()` |
| CLI 值类型转换 | `_coerce_scalar`：按现有值类型把 CLI 字符串转 bool/int/float（`true/yes/1/on` 等映射表） | `core/config.py:_coerce_scalar()` |
| Config 松散结构 | `Config.raw: dict` + 点路径访问，不设强类型子结构（schema 演进不升版） | `core/config.py:Config` |
| config_audit 值编码 | 非标量以 `repr()` 存储（设计未定编码；M2+ 如需机器消费可改 JSON） | `core/registry.py:_encode()` |
| diff 哨兵 | 键缺失以 `"<missing>"` 标记（与真实 `None` 值的显示区分待改进，见 08 评审 P2-1） | `core/config.py:_walk_diff()` |
| mtime 精度 | 指纹用 `st_mtime_ns` 纳秒精度，避免秒级回写/克隆造成的假命中 | `core/fingerprint.py:mtime_ns()` |
| 只读命令副作用 | ~~`resolve_data_dir` 隐式 `mkdir`~~ **已修（第二轮）**：改为纯路径解析，只读命令零副作用；目录创建收敛到写路径（`ensure_dirs()` / 锁获取 / registry 连接） | `cli/_common.py:resolve_data_dir()` |
| extras 前置铺排 | pyproject 预声明 embed/vector/graph-*/mcp 五组 optional extras（M1 代码未使用；`fastmcp` 项违规待移除，见 08 评审 P1-1） | `pyproject.toml:19-25` |
| 异常层级 | `ConfigError(ValueError)`、`UnknownTaskKindError(TaskError, ValueError)` 多继承，便于 CLI 统一捕获 | `core/config.py` / `core/task.py` |

## M2 解析 + 分类（2026-08-13）

> 依据：`design/kb-app/09-M2补充设计.md`（M2 权威设计）。落地解析（五格式）、结构感知分块 + FTS5 填充、关键词降级分类、LiteLLM client（可选）、`kb init`、`kb index scan/run/reindex/add/set-topic`。

### M2 决策落地点（09 §0）

| 决策 | 裁决 | 落地点 | 验证 |
|---|---|---|---|
| 1 分类倒挂 | 关键词粗排（§7），embedding 质心推迟 M3 | `pipeline/classify.py:score_topics/decide_topic/decide_doc_type` | `tests/unit/test_classify.py`（13 项） |
| 2 topics 表 | 补 `topics` 表 DDL（§8） | `core/registry.py:TABLE_TOPICS` + `upsert_topic/seed_topics/adjust_topic_doc_count` | `test_registry.py::test_initialize_creates_all_expected_tables` |
| 3 LLM client | `llm/litellm_client.py` 两级重试（§9） | `llm/litellm_client.py:LLM.complete` + `get_llm_or_none` | `test_llm_client.py`（7 项） |
| 4 doc_id | 全局顺序号 `D%04d`（§2），永不复用 | `core/registry.py:next_doc_id` + `core/files.py:decide_action` | `test_files.py::test_next_doc_id_never_reuses` |
| 5 分块 + FTS | M2 分块并填 `fts_chunks`（§6） | `parse/chunk.py:chunk_document` + `pipeline/stages.py:stage_chunk` | `test_chunk.py`（5 项） |
| 6 Runner 串行 | 前台同步单写循环（§10） | `pipeline/runner.py:run_pending_tasks` | `test_runner.py`（4 项） |

### M2 关键落地点（09 §2–§12）

| 设计 | 落地点 | 验证 |
|---|---|---|
| §2 doc_id 五情形决策表 | `core/files.py:decide_action/apply_*` | `test_files.py`（14 项） |
| §3 扫描规则（白名单六扩展、忽略隐藏/summaries/符号链接、遵循 .gitignore） | `cli/index.py:_iter_candidates` | `test_index_e2e.py::test_scan_idempotent_second_pass` |
| §5 summaries manifest 绑定 | `parse/manifest.py:parse_summary/bind_summaries_to_corpus` + `cli/index.py:_stamp_manifest` | `test_manifest.py`（6 项） |
| §6 分块幂等（先删后插） | `pipeline/stages.py:stage_chunk`（`delete_chunks_by_doc` → `insert_chunk`） | `test_runner.py::test_runner_drains_queue_and_writes_chunks` |
| §7.1 关键词计分（标题×3 + 正文×1） | `pipeline/classify.py:score_topics` | `test_classify.py::test_score_topics_weights_title_hits_3x` |
| §7.3 doc_type 优先级规则 | `pipeline/classify.py:decide_doc_type` | `test_classify.py::test_decide_doc_type_*` |
| §9 两级重试 + 记账 | `llm/litellm_client.py` + `registry.py:record_llm_usage` | `test_llm_client.py`（7 项） |
| §10 Ctrl-C 回退 pending 退出码 130 | `pipeline/runner.py`（`KeyboardInterrupt` → `mark_failed(retryable)`）+ `cli/index.py:run_cmd` | 手动验证（信号不可单元测） |
| §11 `kb init` 幂等 | `cli/init.py:init_cmd` | `test_init.py`（3 项） |
| §12 `kb index add` 登记不拷贝 | `cli/index.py:add_cmd` | `test_index_e2e.py::test_add_external_file` |
| §12 `kb index set-topic` 改判即时生效 | `pipeline/stages.py:set_topic` + `cli/index.py:set_topic_cmd` | `test_index_e2e.py::test_set_topic_updates_doc_count` |

## M2 验收清单

- [x] `uv run pytest` 全绿（174 项：155 unit + 19 integration）；`ruff check` 与 `ruff format --check` 全过
- [ ] 解析器：五格式各 3+ fixtures，PDF 覆盖快路径/降级/扁平三分支（05 §10.1）——**部分达成**：txt/md/html/docx 有单测（`test_parse.py` 9 项），PDF 无自动化 fixture（`test_parse_pdf.py` 未落地，`pdf_fast.py` 三分支未纳入门禁）
- [x] 幂等重放：同一文档跑两次结果一致（`test_runner.py`）；移动零重抽取（`test_files.py::test_decide_action_moved_zero_re_extract` + scan 级 `test_index_e2e.py::test_move_preserves_doc_id`）；duplicate 不入队不入 FTS（`test_files.py::test_apply_new_or_duplicate_marks_duplicate`）
- [x] 分块：超长章节切分 + overlap 正确（`test_chunk.py::test_long_section_is_split_with_overlap`）；重解析后 `fts_chunks` 无旧块残留（先删后插）
- [x] 降级分类：关键词命中/不命中/比值不足三分支（`test_classify.py`）；`needs_confirm` 进 `kb status`（`cli/main.py:status_cmd`）；`set-topic` 改判即时生效
- [x] LLM client：第一级 4 轮退避（delay 序列 1s→2s→4s）、第二级 1 次切换（一主一备）、4xx 直通 fallback、全败抛 `LLMUnavailable`（继承 `RetryableError`，runner 可直接退避）（`test_llm_client.py`，mock 不依赖真实 API）
- [x] `kb init` 幂等（跑两遍无副作用、不覆盖既有 config）
- [ ] NFR-4：30 页 PDF 单篇端到端 < 2 分钟——未纳入自动化门禁，需手工计时验证
- [x] 文档：`docs/milestone-log.md` 新增 M2 节（含"M2 补充设计登记"）

## M2 补充设计登记（设计文档外的实现决策）

> M2 开发中补充、01–09 设计文档未覆盖的决策。契约级变更已回写 09 §14；其余记录于此。

| 决策 | 内容 | 落地点 |
|---|---|---|
| DOCX 轻量解析 | 09 §1 原依赖 Docling；实现改用 `python-docx`（按段落，不做版面分析），避免重依赖 | `pyproject.toml` parse extra |
| 分块物理存储 | 09 §6 只定义 FTS 填充；实现将带偏移/page_range 的完整 chunk 对象存 `cache/extracted/<sha256>.json`，`fts_chunks` 只存可检索文本；M2 未建独立 `chunks` 表 | `parse/chunk.py:write_cache_payload` |
| duplicate 落库形态 | duplicate 也分配新 doc_id 并落 `files` 行（status='duplicate'），仅不入队/不入 FTS | `core/files.py:apply_new_or_duplicate` |
| deleted 墓碑 | `apply_deleted` 仅置 `status='deleted'`，**保留** path/sha256/mtime 与身份字段（09 §2"M5 图软删衔接"；修 P0-2 双删 UNIQUE 崩溃）；`detect_deleted` 跳过已墓碑行，`decide_action` 遇墓碑路径复用该行复活 | `core/files.py:apply_deleted/detect_deleted/decide_action` |
| 非 parse 任务 | runner 以 `next_task(kind='parse')` 只取 parse 任务，非 parse（summarize/extract 等 M3+）保持 pending 不被吞 | `pipeline/runner.py:run_pending_tasks` + `core/task.py:next_task` |
| LLM 兜底 doc_type | `llm/litellm_client.py` 已落地；`stage_classify` 在 doc_type 规则⑤落空（other）且 LLM 可用时走 `llm_arbitrate_doc_type`，失败静默回退 'other'（09 §7.3/§7.4） | `pipeline/classify.py:llm_arbitrate_doc_type` + `stages.py:stage_classify` |
| PDF 三级判定塌缩 | 09 §4 原"快路径/Docling 降级/扫描版 no_text"三级在 M2 塌缩为两级（快路径 / 无文本 no_text）：无 Docling 降级路径、无 `pdf_layout.py`；coverage<0.85 仅记 warning（`structure` 仍按标题数判 tree/flat） | `parse/pdf_fast.py`（模块 docstring 已注明） |
| parse config 接线 | `parse_path(path, cfg=...)` 把 `parse.page_char_norm/pdf_fast_min_coverage/pdf_fast_min_headers` 传给 PDF 快路径（`parse.ocr_enabled` 为 M3 占位，M2 无 OCR 路径故不消费） | `parse/registry.py:_pdf_kwargs` |
| summary stale 与 mismatch | `apply_modified` 在源 PDF 变化且 `summary_source='curated'` 时置 `summary_stale=1`；scan 收集未命中 manifest 的 summary 报 `SUMMARY_MANIFEST_MISMATCH` 并写 `reports/manifest_mismatch_*.json`（09 §5 / 06 §4.4） | `core/files.py:apply_modified` + `cli/index.py:_load_manifest_bindings/_write_manifest_mismatch_report` |
| Ctrl-C 立即重排队 | `mark_failed(immediate=True)` 重置为 `run_after=NULL` 的 pending（非 30s 退避），重启 runner 立即续跑（09 §10） | `core/task.py:mark_failed` + `pipeline/runner.py` |
| `kb init` diff + `--force` | 已存在 config 时打印相对默认值的 diff；`--force` 为显式重写入口（已回写 09 §11） | `cli/init.py:_print_config_diff` |
| `files.pages/title` 落库 + cache 指标 | `stage_parse` 写 `pages`（page_count）与 `title`（首标题，flat 回退文件名）；cache payload 增 `page_count/header_count/coverage` 三键，缓存命中不再恒 None | `pipeline/stages.py` + `parse/chunk.py:write_cache_payload` |
| manifest 搜索范围 | `_load_manifest_bindings` 仅沿各文件「所在 corpus 根子树」的祖先目录找 `summaries/`，不再越出 corpus | `cli/index.py:_load_manifest_bindings` |
| config 容器写入 | `_coerce_scalar` 对 list/dict 键用 YAML 解析 CLI 字符串，`llm.fallback`/`classify.topic_keywords` 经 `kb config set` 可写 | `core/config.py:_coerce_scalar` |
| 连接管理 | `stages.py` 全部 `connect()` 内联调用改为 `read_only()`/`transaction()` 上下文，删除 `stage_parse` 的 no-op 死调用 | `pipeline/stages.py` |
| litellm cost map | 模块加载时 `setdefault("LITELLM_LOCAL_MODEL_COST_MAP","True")`，离线启动不再拉取远端 cost map 报超时噪音 | `llm/litellm_client.py` |
| status 聚合展示 | `kb status` 新增 files 分状态、extract_status、topics、needs_confirm、FTS 数 | `cli/main.py:status_cmd` |

## M3 检索 + 摘要（2026-08-14）

> 依据：`design/kb-app/11-M3补充设计.md`（M3 权威设计，v5 四轮评审修订）。M3 按**无向量 MVP 变体**实施：FTS5 全文路 + SQLite 结构导航图路两路加权 RRF + 可选 LLM 查询扩展/重排；自动摘要子特性（`summarize` 任务 + `$summary` 伪 chunk 进 FTS）；检索六命令顶层化。LanceDB/bge-m3/质心分类保留为 P1 目标态，不进 M3 依赖。

### M3 决策落地点（11 §0）

| 决策 | 裁决 | 落地点 | 验证 |
|---|---|---|---|
| 1 向量 P1 | 保留目标态，M3 不实施 | `config.py` `embedding.backend='none'`（新装默认）；`--mode vector` 显式报错 | `test_search_e2e.py::test_search_vector_mode_errors` |
| 2 两路召回 | FTS + 结构导航，section 粒度加权 RRF | `retrieve/hybrid.py`（`_fts_chunk_hits`/`_graph_chunk_hits`/`_rrf`） | `test_hybrid.py`（10 项） |
| 3 图路 SQLite | 结构关系导航（非节点图存储） | `retrieve/hybrid.py:_graph_chunk_hits` | `test_search_graph_mode_returns_structural_list` |
| 4 分类维持 M2 | 关键词 + LLM 兜底 | `pipeline/classify.py`（不变） | `test_classify.py` |
| 5 依赖不新增 | 无 LanceDB/bge-m3 | `pyproject.toml` 不变 | — |
| 7 摘要生成 | `summarize` 任务 + 四段式 L1–L3 | `pipeline/stages.py:stage_summarize` | `test_runner.py::test_stage_summarize_*` |
| 8 命令顶层化 | 六命令提升顶层，旧 `kb search` 子组移除 | `cli/search.py` + `cli/main.py` | `test_search_e2e.py` |

### M3 关键落地点（11 §2–§7）

| 设计 | 落地点 | 验证 |
|---|---|---|
| §2.1 图路语义 + norm 碰撞并集 | `retrieve/query_understanding.py:norm/match_topics` + `hybrid.py` | `test_query_understanding.py`（12 项） |
| §2.2 FTS + 短查询兜底 + 章节聚合 | `retrieve/hybrid.py:_fts_chunk_hits/_aggregate_sections`（CJK LIKE / ASCII synonyms 扩展，禁用裸 LIKE） | `test_hybrid.py::test_search_short_ascii_*` |
| §2.3 查询扩展 + 离线 synonyms | `retrieve/query_understanding.py:llm_expand_query/merged_synonyms`（`BUILTIN_SYNONYMS` + config 合并） | `test_query_understanding.py` |
| §2.4 LLM 重排 | `retrieve/hybrid.py:_rerank`（失败静默回退 RRF 原序） | `test_hybrid.py::test_rerank_*` |
| §2.6 检索模式语义表 | `cli/search.py:search_cmd`（hybrid/graph/topic-global/vector） | `test_search_e2e.py` |
| §3 自动摘要 | `stage_summarize`（curated 跳过 / stale-curated 临时摘要保 provenance / `$summary` 伪 chunk） | `test_runner.py::test_stage_summarize_*` |
| §5 embedding 档迁移 | `cli/search.py:_warn_embedding_backend` + config `embedding.backend='none'` | `test_search_e2e.py::test_search_vector_mode_errors` |
| §7 purpose 枚举扩 | `registry.py:LLM_PURPOSES` 增 `query_expand/rerank`；`litellm_client` 移除未知 purpose 静默回退 | `test_llm_client.py` |

### M3 验收清单

- [x] `uv run pytest` 全绿（**219 项**：195 unit + 24 integration）；`ruff check` / `ruff format --check` 全过
- [x] 检索六命令顶层化；旧 `kb search query` 移除（`cli/main.py`）
- [x] 检索 e2e：英文短语、2 字符缩写（synonyms 扩展 + 无裸 LIKE 假阳性）、topic 硬过滤、topic 稀疏退化
- [x] RRF section 粒度 + `w_fts=1.0/w_graph=0.5` 加权 + `--topic` 硬过滤
- [x] 摘要管线：curated 跳过、auto 生成+落盘+`summary_source='auto'`、`$summary` 伪 chunk 进 FTS、stale-curated 保 provenance、幂等重放、LLM 缺席 skip+检索回退（`test_runner.py` 6 项 stage_summarize 用例）
- [x] embedding 档校验：非 none 档警告 + `--mode vector` 显式报错
- [x] 召回抽检（§10-7）：`fixtures/recall_queries.yaml` 20 条标注 + `scripts/recall_sweep.py`；真实语料实测**在线档 80.0%/70.0% 两测（压线波动）、离线档 65.0%**——未稳定越过 80% 门槛，misses 归因与裁决选项见 12 报告"DoD 测试执行与闭环"节
- [x] NFR-4 计时（§10-8/9）：31 页 PDF 不含摘要 16.2s / 含摘要 20.1s（门槛 2min）；检索纯查询 p50=13ms（门槛 3s）
- [x] milestone-log 新增 M3 节（含补充设计登记）

### M3 补充设计登记（设计文档外的实现决策）

| 决策 | 内容 | 落地点 |
|---|---|---|
| 预算近似 | token 预算用 ~4 字符/token 近似（MVP 不做真实 tokenizer） | `retrieve/assembler.py:_CHARS_PER_TOKEN` |
| `$summary` 伪 chunk | 摘要经 `chunk_id='<doc_id>#summary'`、`section_path='$summary'` 进 `fts_chunks`，不建新表 | `pipeline/stages.py:stage_summarize` |
| BUILTIN_SYNONYMS | 内置缩写/同义表为代码级常量，config `search.synonyms` 查询期合并（用户覆盖） | `retrieve/query_understanding.py` |
| 图路退化 | 无主题词命中 → 图路**空列表**；仅 topic 稀疏（NULL 占比 ≥ 50%）才退化为 corpus/doc_type 导航（受 max_docs/max_sections 截断，P1-1 修正） | `retrieve/hybrid.py:_graph_chunk_hits` |
| compare 组装 | `compare` 的 LLM 对比表复用 purpose=`extract`（11 §7 未为 compare 单列枚举）；LLM 不可用/失败回退并排摘要 | `retrieve/assembler.py:compare_documents` + `cli/search.py:compare_cmd` |
| 扩展词合成语义 | LLM 扩展词**并集增召回**（独立 OR 组 MATCH，与原查询结果并集留最高分），不进原查询 AND 组——11 §2.3 未定义合成方式，AND 混入会致 FTS 零命中（DoD 实测修复 D-4） | `retrieve/hybrid.py:_fts_chunk_hits/_fts_rows` |
| 推理模型预算 | `query_expansion_max_tokens` / `search.rerank.max_tokens` 默认 1024（推理模型 think 计入 completion 预算，128/256 会被吃光，DoD 实测修复 D-3） | `core/config.py` + `query_understanding.py` / `hybrid.py:_rerank` |
| LLM 输出清洗 | `_clean_content` 剥 `<think>` 闭合块 + ```json 围栏（MiniMax-M3 实测混入 content；截断未闭合不剥） | `llm/litellm_client.py` |
| PDF 页码归属 | 页码取枚举序号（1-based，与 TOC 同基），不用 `metadata.page`（部分 pymupdf4llm 版本为 None，曾致 80 篇零 chunk，DoD 实测修复 D-1） | `parse/pdf_fast.py` |
| data_dir 寻址 | `Config.data_dir` 优先 `GRAPHIT_KB_DATA_DIR` 环境变量，保证 llm_usage 记账落实际数据目录（D-5） | `core/config.py:Config.data_dir` |

### M3 关闭（2026-08-14）

P1×6 修复 + DoD 执行闭环（12 报告"DoD 测试执行与闭环"节）：219 项测试全绿、ruff 全过、NFR-4 双口径与检索延迟实测达标、召回抽检在线档 70–80% 区间波动。DoD-7 裁决：按基线关闭 M3，排序质量三项改进（文档标识进 FTS / 精确命中保护 / LIKE 路分档）**并入 M4**，连续两轮 ≥80% 复测门槛随之转移（13 §3/§6.6）。**M3 正式关闭。**

## M4 基础 MCP 子集 + 排序改进（2026-08-14，MVP 收口）

> 依据：`design/kb-app/13-M4补充设计.md`（M4 权威设计，v2 一轮评审修订）。M4 收窄为 **stdio MCP + 四只读工具**（`kb_search`/`kb_show`/`kb_read`/`kb_assemble_context`）+ 结构化错误码子集 + 排序质量三项改进（DoD-7 裁决回收）。**M4 DoD 全绿即 MVP 达成**（13 §7）。

### M4 决策落地点（13 §0）

| 决策 | 裁决 | 落地点 | 验证 |
|---|---|---|---|
| 1 收窄范围 | stdio MCP + 四只读工具；完整工具集留 P1 | `mcp_server.py`（4 `@mcp.tool`） | `test_mcp.py::test_mcp_handshake_and_four_tools` |
| 2 工具命名 | `kb_show`/`kb_read`（对齐 CLI，05 §6 回写） | `mcp_server.py` | `test_mcp.py` |
| 3 命令形态 | `kb serve mcp`（M1 占位替换） | `cli/serve.py:mcp_cmd` | `test_mcp.py` |
| 4 SDK | `mcp>=1.29,<2`（实测 1.29.0），`mcp` extra | `pyproject.toml` + `uv.lock` | DoD-4（未装显式报错） |
| 5 并发 | MCP 只读、不取写锁；SQLite busy 归 `INTERNAL` | `mcp_server.py`（只读打开） | — |
| 6 排序改进 | R-1/R-2/R-3 确定性改进 | `hybrid.py` + `stages.py` | `test_hybrid.py`/`test_runner.py` |
| 7 上下文组装 | `assemble_for_task` 确定性路径（不触发 LLM） | `assembler.py:assemble_for_task` | `test_assembler.py` |
| 8 复合 title 契约 | title 列存复合、展示/匹配出口剥离 stem | `hybrid.py:section_title` + `_sections_for_doc`/`section_tree` | `test_hybrid.py`/`test_assembler.py`/`test_mcp.py` |

### M4 关键落地点（13 §2–§4）

| 设计 | 落地点 | 验证 |
|---|---|---|
| §2 MCP 四工具 + 错误结构 | `mcp_server.py`（薄封装 `retrieve`，`{error:{code,message,suggestion}}`）；错误码子集 `DOC_NOT_FOUND`（含歧义候选）/`SECTION_NOT_FOUND`/`MODE_NOT_READY`/`INTERNAL` | `test_mcp.py`（5 项） |
| §2.1 `resolve_doc` 提升 | `retrieve/resolve.py`（doc_id 精确 → path 精确 → 后缀/title 子串须唯一；歧义回候选） | `test_resolve.py`（6 项） |
| §3 R-1 文档标识进 FTS | `stage_chunk` 写 `{stem} \| {章节标题}`；`section_title`（`split(TITLE_SEP,1)[-1]`）剥离 | `test_runner.py::test_stage_chunk_writes_composite_title` + `test_hybrid.py` |
| §3 R-2 精确命中保护 | `_fts_chunk_hits` 原查询路得分 ×`search.exact_boost`（默认 1.3）再与扩展路 max 并集；无扩展词不 boost | `test_hybrid.py::test_exact_boost_protects_original_query` |
| §3 R-3 LIKE 分档 | 纯 LIKE 路 `title LIKE` 1.0 / `text LIKE` 0.5，按 (score, doc_id, section) 确定性排序 | `test_hybrid.py::test_like_ranking_title_above_text` |
| §4 `assemble_for_task` | 检索（无 llm）→ 去重 → 摘要/首节装配 → 预算截断；`used=len(context_block)//4`；`sources` 只含实际纳入文档 | `test_assembler.py`（4 项） |

### M4 验收清单（13 §6 DoD）

- [x] DoD-1 stdio 握手 e2e：`tools/list` 恰含四工具 + `kb_search` 全通（真实 MCP client 会话）
- [x] DoD-2 契约：`kb_search.hits[].title` 复合 / `kb_show.sections[].title` 剥离 / `$summary` 哨兵 / 路径片段解析 / 退化 note
- [x] DoD-3 错误结构：`DOC_NOT_FOUND`（歧义带候选）/`SECTION_NOT_FOUND`/`MODE_NOT_READY`（vector + 非法 mode）
- [x] DoD-4 未装 mcp extra：`kb serve mcp` 显式报错 `uv sync --extra mcp`
- [x] DoD-5 R-1/R-2/R-3 单测齐备（R-2 provenance 断言、R-1 复合写/剥离双向）
- [ ] DoD-5 补充：R-1 实机验证 `context rot` 命中 D0032（需真实语料，待实测）
- [ ] DoD-6 召回抽检：在线档**连续两轮 success@10 ≥ 80%**（需真实语料 + LLM，待实测）
- [ ] DoD-7 NFR-4：`kb_assemble_context`（确定性路径）在线档 < 10s（需真实语料，待实测）
- [x] DoD-8 门禁：`uv run pytest` **242 项**全绿 + `ruff check .`/`ruff format --check .` 全过（含 `scripts/`，14 报告 P1-1 修复后）。环境口径（14 §10 复核）：POSIX/新 SQLite 下 242 passed；原生 Windows + Python 3.12 下 **240 passed + 2 skipped**（2 项 POSIX-only 锁测试 win32 skipif）；解释器须 ≥ SQLite 3.39 系（见下表 .python-version 行）
- [x] DoD-9 文档：milestone-log M4 节 + §8 回写清单执行（03/04/05）

### M4 补充设计登记（设计文档外的实现决策）

| 决策 | 内容 | 落地点 |
|---|---|---|
| `section_title` 用 `split` 非 `partition` | 13 §3 伪代码写 `title.partition(" \| ")[-1]`，但无分隔符时 `partition` 返回 `(原串,"","")`、`[-1]` 取到空串——实测测试即翻车；改用 `split(TITLE_SEP,1)[-1]`（无分隔符返回原串，幂等安全） | `retrieve/hybrid.py:section_title` |
| `used` 口径 | 13 §4 伪代码 `used=len(context_block)//4`；实现早期误用"块长和"（少算 `\n\n` 连接符，`used` 与 `len(context_block)` 差 1）——修正为 `len(context_block)//4` | `retrieve/assembler.py:assemble_for_task` |
| R-2 无扩展不 boost | `exact_boost` 仅在 `extra_terms` 非空时施加（无扩展时直接返回原 `rows`），满足 13 §3 回归约束"不得改变无扩展词时既有相对序" | `retrieve/hybrid.py:_fts_chunk_hits` |
| `search.exact_boost` DEFAULTS | 补入 `core/config.py` DEFAULTS["search"]（默认 1.3，`kb config set` 可改） | `core/config.py` |
| mcp 只读状态懒加载 | 进程内缓存 `(Registry, Config)`（`Registry.read_only()` 每次开新连接、WAL 下可并发读；config 改动需重启进程生效） | `mcp_server.py:_state` |
| e2e 测试跑法 | MCP e2e 用 `asyncio.run` + `stdio_client` 子进程（`python -m kbapp.cli.main serve mcp`，`GRAPHIT_KB_DATA_DIR` 注入），不依赖 pytest-asyncio | `tests/integration/test_mcp.py` |
| `.python-version` 3.11→3.12 | 14 §10 复核 N-2：Python 3.11.0 捆绑 SQLite 3.38.4，FTS5 虚表非 ASCII LIKE 静默空集（CJK 短查询零命中）；3.12.13/SQLite 3.50.4 修复。requires-python `>=3.11,<3.13` 不变 | `.python-version` |
| Windows 测试兼容 | 14 §10 复核 N-3：test_registry 4 项补 `conn.close()`（sqlite3 with 只提交不关闭，Windows 临时目录清理必败）；test_lock 2 项加 win32 skipif（lock 模块声明 POSIX-only，Windows 下 stale 锁仅靠 1h mtime 兜底回收） | `tests/unit/test_registry.py` / `test_lock.py` |

## 后续里程碑锚点

参见 [`architecture.md`](architecture.md) "未来锚点" 一节。