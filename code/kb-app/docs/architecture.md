# GraphIt-KB 架构（M2 解析 + 分类）

> 适用范围：`code/kb-app/` 仓库根。本文档描述当前落地的包结构、各模块职责、与设计文档的映射关系；M1 内容（config / registry / 锁 / 任务队列）保留原样，M2 新增解析 / 分块 / 降级分类 / LLM client / `kb init`。

## 设计依据

- `design/kb-app/03-技术概要设计.md` §2（存储布局）、§4（解析三级判定）、§6（WAL）、§8.2.1–3（评分）
- `design/kb-app/05-详细设计方案.md` §1（包结构）、§2（DDL）、§3（解析）、§4.0（runner）、§7（锁与任务）、§9（CLI）
- `design/kb-app/06-摘要构建与命名规范.md` §4.5（双格式解析）
- `design/kb-app/07-详细设计评审报告.md` S1–S8 + R1–R4
- `design/kb-app/09-M2补充设计.md`（M2 权威设计：doc_id、扫描规则、分块、降级分类、LLM client、runner）

## 包结构

```
src/kbapp/
├── __init__.py            # re-export __version__
├── __version__.py         # "0.1.0"
├── py.typed               # PEP 561 标记
├── cli/                   # Typer 入口层
│   ├── _common.py         # resolve_data_dir（纯路径解析，零副作用）
│   ├── main.py            # 顶级 `kb` 应用 + `status` 子命令
│   ├── init.py            # `kb init`（M2：幂等初始化数据目录）
│   ├── config.py          # `kb config {show,get,set,diff}`
│   ├── index.py           # `kb index {scan,run,reindex,add,set-topic}`（M2）
│   ├── search.py          # `kb search ...` 占位（M3）
│   ├── collect.py         # `kb collect ...` 占位（M7）
│   ├── maint.py           # `kb maintenance ...` 占位（M8）
│   └── serve.py           # `kb serve ...` 占位（M4/M6）
├── core/                  # 业务无关的基础设施
│   ├── paths.py           # 数据目录布局 (DataPaths frozen dataclass)
│   ├── config.py          # Config + load/dump/原子写/点路径 get-set + 默认 schema
│   ├── fingerprint.py     # SHA-256 + mtime_ns
│   ├── lock.py            # 原子写锁（O_EXCL + PID 探测 + mtime 兜底）
│   ├── registry.py        # SQLite 访问层 + DDL（八表 + FTS5 + schema_version）
│   ├── files.py           # doc_id 决策表（09 §2 五情形）
│   └── task.py            # 任务状态机 + 退避 + 崩溃恢复
├── parse/                 # M2：文档解析
│   ├── base.py            # ParseResult / Section / ExtractMeta / Parser 协议
│   ├── registry.py        # 扩展名 → 解析器分发（白名单六格式）
│   ├── txt.py             # 纯文本 → flat
│   ├── md.py              # markdown-it-py → tree（标题树）
│   ├── html.py            # Trafilatura → tree（失败降 flat）
│   ├── docx.py            # python-docx → flat（按段落）
│   ├── pdf_fast.py        # pymupdf4llm 快路径 + 三级判定
│   ├── manifest.py        # summaries/*.md frontmatter/blockquote 绑定（09 §5）
│   └── chunk.py           # 结构感知分块 + cache 写入（09 §6）
├── pipeline/              # M2：流水线编排
│   ├── runner.py          # 串行单写 runner（09 §10）
│   ├── stages.py          # stage_parse / stage_chunk / stage_classify
│   └── classify.py        # 关键词粗排 + doc_type 规则（09 §7）
└── llm/                   # M2：LLM client（可选 extra）
    └── litellm_client.py  # LiteLLM 封装 + 两级重试（09 §9）
```

**src-layout 原则**：`src/kbapp/` 强制安装后才可 `import kbapp`；CI 测试在隔离环境跑，避免本地 `python -c` 误用未打包源码。

## 模块职责

| 模块 | 职责 | 对应设计 |
|---|---|---|
| `core/paths` | 数据目录布局；所有相对路径常量；`ensure_dirs()` 不创建文件 | 03 §2 |
| `core/config` | YAML 配置加载/原子写/默认值合并；点路径 get-set；与默认值 diff | 05 §2.5 |
| `core/fingerprint` | SHA-256 流式计算；mtime 纳秒；为增量更新提供主键 | 03 §3.1 |
| `core/lock` | 进程间写互斥；崩溃残留自动回收（PID 探测 + mtime 兜底） | 05 §7，S7 修复 |
| `core/registry` | SQLite 连接封装（WAL + FK + Row 工厂）；DDL；事务上下文；FTS5 (trigram)；topics / id_counters DAO | 05 §2.1，07 S3/S4/R3/§9，09 §2/§8 |
| `core/files` | doc_id 决策表（new/modified/moved/duplicate/deleted）+ 落库 apply | 09 §2 |
| `core/task` | 任务状态机 pending→running→{done, failed}；退避 30s→1m→5m；崩溃恢复 | 05 §4.0，07 §7.2 |
| `parse/*` | 五格式解析（tree/flat 结构）、扩展名分发、summaries 绑定、结构感知分块 | 05 §3.2，09 §3/§4/§5/§6 |
| `pipeline/runner` | 串行单写执行循环；parse→chunk→classify 三阶段；Ctrl-C 回退 | 09 §10 |
| `pipeline/stages` | 阶段函数（幂等）；写 registry + cache；`set_topic` 改判 | 09 §6/§7/§10 |
| `pipeline/classify` | 关键词主题粗排（标题×3 + 正文×1）+ doc_type 优先级规则 | 09 §7 |
| `llm/litellm_client` | `LLM.complete`；两级重试（调用内退避 4 轮 + fallback 切换 1 次）；记账 | 05 §3.4，09 §9 |
| `cli/main` | 顶级 Typer 应用 + 全局 `--data-dir`；`status` 展示 files/topics/needs_confirm/FTS | 05 §9 |
| `cli/init` | 幂等初始化：建目录、写默认 config、初始化 registry、播种 topics | 09 §11 |
| `cli/index` | `scan` / `run` / `reindex` / `add` / `set-topic` | 09 §3/§10/§12/§7.2 |
| `cli/config` | `kb config ...`：读 / 写 / 审计 / diff | 05 §9，07 §6 |

## 数据流（M2 范围）

`kb init`：

```
kb init ──► ensure_dirs ──► 写默认 config.yaml + sources.yaml 模板
                              └─► registry.initialize (SCHEMA_VERSION=2)
                                    └─► seed_topics (config.core_topics)
```

`kb index scan`：

```
scan ──► 遍历 corpus_roots（白名单六扩展、跳过隐藏/summaries/符号链接、遵循 .gitignore）
           └─► fingerprint ──► decide_action（09 §2 决策表）
                 └─► apply_*（upsert files + 分配/保留 doc_id）
                       └─► manifest 绑定（summaries/*.md → summary_source/summary_path）
                             └─► 入队 parse 任务（new/modified 才入队；duplicate/moved 不入队）
```

`kb index run`：

```
run ──► acquire_write_lock ──► reset_stale_running
         └─► 循环 next_task → mark_running → stage_parse → stage_chunk → stage_classify
                                                                          → mark_done
         （串行；Ctrl-C 回退 pending 退出码 130）
```

`kb status`：

```
status ──► reset_stale_running ──► files 分状态 + extract_status + topics + needs_confirm + FTS 数
```

## 设计决策的可追溯性

每个评审修订（S1–S8 / R1–R4）与 M2 决策（09 §0）在代码中的落地点见 `docs/milestone-log.md`。

## 补充设计决策

M1 开发中补充的决策集中登记于 `docs/milestone-log.md` "M1 补充设计登记"；M2 的决策在 09 §14 已回写设计文档，其余登记于 "M2 补充设计登记"。与本仓库模块契约直接相关的两条：

- `cli/_common.resolve_data_dir` 为纯路径解析，只读命令零副作用；数据目录创建收敛到写路径（`ensure_dirs()` / 锁获取 / registry 连接）；
- `core/config.Config` 采用松散 `raw: dict` + 点路径访问，不设强类型子结构，schema 演进不升版。

## 未来锚点

| 里程碑 | 拟新增 / 替换 |
|---|---|
| M3 检索 | `core/retrieve/{bm25,vector,hybrid}.py`；LanceDB 集成（`[vector]` extra）；`cli/search.py` 占位替换为 `kb search query`；embedding 质心分类（05 §4.2）恢复 |
| M4 MCP | `core/mcp/server.py`（FastMCP）；`cli/serve.py` 启动 stdio / HTTP；`[mcp]` extra |
| M5 图谱 | `core/graph/{ladybug,kuzu}.py`（LadybugDB 优先，Kuzu 降级）；`[graph-ladybug]` / `[graph-kuzu]` extra；`stage_extract` / `stage_relate` |
| M6 Web UI | `cli/serve.py` 加 FastAPI 子命令；移植 `design/kb-app/prototype/*.html` |
| M7 自动扩充 | `cli/collect.py` 占位替换为 `kb collect run / kb inbox list/accept/reject`；评分插件加载 |
| M8 评测 | `core/scoring/` 插件协议；`cli/maint.py` 加 `kb maintenance eval` |

## 不在 M2 范围（明确边界）

- Embedding / 向量检索（LanceDB / bge-m3 下载引导）
- `kb search` CLI（M2 已具备 SQL 级 FTS 检索能力，但检索命令 M3 落地）
- LLM 兜底分类（`llm_arbitrate` 不调用；`llm/litellm_client.py` 已落地但未接入分类）
- LadybugDB / MCP server / Web UI / FastAPI
- arXiv 收集器 / Inbox / 评分插件
- 实体抽取 / 关联阅读 / 章节树（图谱节点层，M5）
