# GraphIt-KB (kbapp)

> M1 地基里程碑 — CLI 骨架 + config + SQLite 注册库 + 写锁 + 任务队列

本地运行的个人知识库应用，把 `references/` 资料自动分类、索引、章节级结构化并支持检索 / 上下文组装 / 关联阅读 / 自动扩充。本仓库是 GraphIt-KB 的代码实验实现，对应设计文档在 `design/kb-app/`。

## 状态

| 里程碑 | 内容 | 状态 |
|---|---|---|
| **M1 地基** | CLI、config、SQLite 五表、fingerprint、写锁、任务队列 | ✅ 当前 |
| M2 解析+分类 | 五格式解析、缓存、P2 分类、章节树 | 下一里程碑 |
| M3 检索 | FTS5 trigram + LanceDB + 上下文组装 | 待 M2 |
| M4 MCP | FastMCP（mcp v1）工具集 | 待 M3 |
| M5 图谱(P1) | GraphStore 适配层 + 实体抽取 | 待 M4 |
| M6 可视化(P1) | FastAPI 只读 + G6 v5 | 待 M5 |
| M7 自动扩充(P2) | 评分插件 + arXiv/网页收集 + Inbox | 待 M6 |

## 设计依据

`design/kb-app/` 下七份文档（01–07）。本代码必须编码 07 评审报告里的全部 S1–S8 / R1–R4 关键修订（详见 `docs/milestone-log.md`）。

## 目录

| 路径 | 作用 |
|---|---|
| `src/kbapp/` | Python 包，src-layout |
| `src/kbapp/cli/` | Typer 命令层（薄） |
| `src/kbapp/core/` | config / paths / registry / fingerprint / lock / task |
| `tests/` | pytest，unit + integration |
| `docs/` | 架构、数据模型、里程碑日志 |

## 快速开始

```bash
# 安装依赖（uv 已就绪）
cd code/kb-app
uv sync                                  # 创建 venv + 安装
uv sync --extra dev                      # 加 dev 工具（pytest / ruff / mypy）

# 运行测试
uv run pytest -v                         # 全部测试
uv run pytest -m 'not integration' -v    # 仅单元

# CLI 冒烟
uv run kb --help                         # 列出子命令
uv run kb --data-dir /tmp/test-kb config show
uv run kb --data-dir /tmp/test-kb config set scoring.thresholds.accept 0.65 --yes
uv run kb --data-dir /tmp/test-kb config get scoring.thresholds.accept
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