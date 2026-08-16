# GraphIt-KB (kbapp)

> M1–M6 已完成：解析分类 → 检索摘要 → MCP → 知识图谱 → Web 可视化。本地运行的个人知识库应用。

把 `references/` 资料自动分类、索引、章节级结构化，并支持检索 / 上下文组装 / 关联阅读 / 图遍历 / 只读 Web 可视化。本仓库是 GraphIt-KB 的代码实验实现，对应设计文档在 `design/kb-app/`（01–17）。

## 状态

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M1 地基 | CLI、config、SQLite 八表、fingerprint、写锁、任务队列 | ✅ 完成 |
| M2 解析+分类 | 五格式解析、结构感知分块 + FTS5、关键词降级分类、LLM client | ✅ 完成 |
| M3 检索+摘要 | 混合检索（FTS + 图路 + RRF）+ 自动摘要 + `kb search` | ✅ 完成 |
| M4 MCP | stdio MCP + 四只读工具（`kb_search`/`kb_show`/`kb_read`/`kb_assemble_context`） | ✅ 完成 |
| M5 图谱 | LadybugDB 单后端 + GraphStore 协议 + 结构同步/实体抽取 + `kb related`/`kb compare` | ✅ 完成 |
| M6 可视化 | `kb serve viz` 只读四页（检索/文档/图谱/状态）+ G6 v5 vendored | ✅ 完成 |
| M7 自动扩充(P2) | 评分插件 + arXiv/网页收集 + Inbox | 待办 |

## 设计依据

`design/kb-app/` 下 01–17 号文档（功能需求 → 技术选型 → 概要/详细设计 → 各里程碑补充设计与代码评审报告）。里程碑演进与实现决策见 `docs/milestone-log.md`；架构见 `docs/architecture.md`、`docs/diagrams/`。

## 目录

| 路径 | 作用 |
|---|---|
| `src/kbapp/` | Python 包，src-layout |
| `src/kbapp/cli/` | Typer 命令层（init / index / search / related / compare / topics / serve / config / status / maintenance / collect） |
| `src/kbapp/core/` | config / paths / registry / fingerprint / lock / task / files |
| `src/kbapp/parse/` | 五格式解析 + manifest 绑定 + 结构感知分块 |
| `src/kbapp/pipeline/` | 串行 runner + 阶段（parse → chunk → classify → index → extract → summarize → tombstone） |
| `src/kbapp/llm/` | LiteLLM client（可选 extra，两级重试 + fallback） |
| `src/kbapp/retrieve/` | 混合检索 / resolve / 上下文组装 / 图语义（graph_search） |
| `src/kbapp/graph/` | GraphStore 协议 + LadybugStore（单后端）+ Schema + 结构同步/实体抽取/图查询/reset |
| `src/kbapp/web/` | FastAPI 只读服务（server + api）+ 四页静态前端（index/document/graph/status） |
| `tests/` | pytest，unit + integration（310 项） |
| `docs/` | 架构、数据模型、里程碑日志、图、用户指南 |

## 快速开始

```bash
# 安装依赖（uv 已就绪）
cd code/kb-app
uv sync                                            # 基础依赖
uv sync --extra parse --extra dev                  # 加解析器 + dev 工具
uv sync --extra llm --extra graph-ladybug --extra mcp --extra viz   # LLM + 图谱 + MCP + Web

# 运行测试
uv run pytest -v                         # 全部测试（310 passed + 2 skipped）
uv run pytest -m 'not integration' -v    # 仅单元

# 端到端流程
export KB_DATA=$(mktemp -d)
uv run kb --data-dir "$KB_DATA" init                # 幂等初始化数据目录
uv run kb --data-dir "$KB_DATA" index scan          # 扫描 corpus_roots 入队
uv run kb --data-dir "$KB_DATA" index run           # 串行执行 parse→chunk→classify→index→extract→summarize
uv run kb --data-dir "$KB_DATA" index reindex --full # 全量重建（清 FTS + 清 graph/ + 重入队）
uv run kb --data-dir "$KB_DATA" status              # 查看 files/topics/tasks
uv run kb --data-dir "$KB_DATA" search "context engineering"   # 检索
uv run kb --data-dir "$KB_DATA" related Method:rag --hops 2     # 图遍历邻域
uv run kb --data-dir "$KB_DATA" compare "RAG" --docs D0001,D0002  # 图语义对照
uv run kb --data-dir "$KB_DATA" topics              # 主题清单
uv run kb --data-dir "$KB_DATA" serve mcp           # 启动 MCP stdio 服务
uv run kb --data-dir "$KB_DATA" serve viz --port 8371  # 启动只读 Web（127.0.0.1）
```

> LLM 需配置 `llm.provider/model/api_base/api_key_env`（config.yaml 或 `kb config set`）；缺失时分类走纯规则降级、抽取/摘要跳过。

## 数据目录布局（默认 `~/.graphit-kb/`）

```
graphit-kb/
├── config.yaml
├── sources.yaml
├── registry.sqlite
├── graph/                  # LadybugDB 图库（衍生数据，可 reindex --full 重建）
├── vectors/                # P1 向量检索启用
├── cache/extracted/        # 解析缓存（<sha256>.json）
├── auto_summaries/         # 自动摘要（L1–L3）
├── inbox/                  # M7 起
├── reports/
└── scoring_modules/        # P1 起启用
```

## 注意

- 不要把数据目录放到网络盘（NFS / SMB），SQLite WAL 在网络盘上有损。
- `kb` CLI 默认从环境变量 `GRAPHIT_KB_DATA_DIR` 或 `--data-dir` 读取数据目录。
- 本仓库 `references/` `research/` `design/` 严格只读（GraphIt 设计依据 NFR-3）。
- **平台**：写锁 `core/lock.py` 依赖 `os.kill(pid, 0)` 做持锁进程探测，仅在
  Linux / macOS（POSIX）上验证。Windows 上 PID 语义不同，写锁不可用
  （stale 锁仅靠 1h mtime 兜底回收）；其余功能在 Windows 上经测试验证。
