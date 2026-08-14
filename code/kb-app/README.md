# GraphIt-KB (kbapp)

> M2 解析 + 分类里程碑 — 五格式解析、结构感知分块 + FTS5、关键词降级分类、LiteLLM client、`kb init` / `kb index scan|run`

本地运行的个人知识库应用，把 `references/` 资料自动分类、索引、章节级结构化并支持检索 / 上下文组装 / 关联阅读 / 自动扩充。本仓库是 GraphIt-KB 的代码实验实现，对应设计文档在 `design/kb-app/`。

## 状态

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M1 地基 | CLI、config、SQLite 八表、fingerprint、写锁、任务队列 | ✅ 完成 |
| **M2 解析+分类** | 五格式解析、结构感知分块 + FTS5、关键词降级分类、LLM client、`kb init` | ✅ 当前 |
| M3 检索 | FTS5 trigram + LanceDB + 上下文组装 + `kb search` | 下一里程碑 |
| M4 MCP | FastMCP（mcp v1）工具集 | 待 M3 |
| M5 图谱(P1) | GraphStore 适配层 + 实体抽取 | 待 M4 |
| M6 可视化(P1) | FastAPI 只读 + G6 v5 | 待 M5 |
| M7 自动扩充(P2) | 评分插件 + arXiv/网页收集 + Inbox | 待 M6 |

## 设计依据

`design/kb-app/` 下九份文档（01–09）。本代码必须编码 07 评审报告里的全部 S1–S8 / R1–R4 关键修订与 09 M2 补充设计（详见 `docs/milestone-log.md`）。

## 目录

| 路径 | 作用 |
|---|---|
| `src/kbapp/` | Python 包，src-layout |
| `src/kbapp/cli/` | Typer 命令层（薄） |
| `src/kbapp/core/` | config / paths / registry / fingerprint / lock / task / files |
| `src/kbapp/parse/` | 五格式解析 + manifest 绑定 + 结构感知分块 |
| `src/kbapp/pipeline/` | runner + 三阶段（parse → chunk → classify） |
| `src/kbapp/llm/` | LiteLLM client（可选 extra，两级重试） |
| `tests/` | pytest，unit + integration |
| `docs/` | 架构、数据模型、里程碑日志 |

## 快速开始

```bash
# 安装依赖（uv 已就绪）
cd code/kb-app
uv sync                                  # 基础依赖
uv sync --extra parse --extra dev        # 加解析器 + dev 工具
uv sync --extra llm                      # 可选：LiteLLM client（缺省时分类走纯规则降级）

# 运行测试
uv run pytest -v                         # 全部测试（154 项）
uv run pytest -m 'not integration' -v    # 仅单元

# 端到端流程
export KB_DATA=$(mktemp -d)
uv run kb --data-dir "$KB_DATA" init                # 幂等初始化数据目录
uv run kb --data-dir "$KB_DATA" config show         # 查看默认配置
uv run kb --data-dir "$KB_DATA" index scan          # 扫描 corpus_roots 入队
uv run kb --data-dir "$KB_DATA" index run           # 串行执行 parse → chunk → classify
uv run kb --data-dir "$KB_DATA" status              # 查看 files/topics/needs_confirm
uv run kb --data-dir "$KB_DATA" index set-topic D0001 ContextEngineering  # 改判
```

## 数据目录布局（默认 `~/.graphit-kb/`）

```
graphit-kb/
├── config.yaml
├── sources.yaml
├── scoring_modules/        # P1 起启用
├── registry.sqlite
├── graph/
├── vectors/
├── cache/extracted/        # M2 起
├── inbox/                  # M7 起
└── reports/
```

## 注意

- 不要把数据目录放到网络盘（NFS / SMB），SQLite WAL 在网络盘上有损。
- `kb` CLI 默认从环境变量 `GRAPHIT_KB_DATA_DIR` 或 `--data-dir` 读取数据目录。
- 本仓库 `references/` `research/` `design/` 严格只读（GraphIt 设计依据 NFR-3）。
- **平台**：写锁 `core/lock.py` 依赖 `os.kill(pid, 0)` 做持锁进程探测，仅在
  Linux / macOS（POSIX）上验证。Windows 上 PID 语义不同，写锁不可用；
  仅读命令（`kb config get` / `kb status` / `kb search query`）应仍可运行
  但未做端到端验证。