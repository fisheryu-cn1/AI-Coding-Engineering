# GraphIt-KB 架构（M1 地基）

> 适用范围：`code/kb-app/` 仓库根。本文档描述当前落地的包结构、各模块职责、与设计文档的映射关系；后续里程碑在"未来锚点"小节追加。

## 设计依据

- `design/kb-app/03-技术概要设计.md` §2（存储布局）、§6（WAL）、§8.2.1–3（评分）
- `design/kb-app/05-详细设计方案.md` §1（包结构）、§2（DDL）、§4.0（runner）、§6（MCP）、§7（锁与任务）、§11（防踩坑）
- `design/kb-app/06-摘要构建与命名规范.md` §4.5（双格式解析）
- `design/kb-app/07-详细设计评审报告.md` S1–S8 + R1–R4

## 包结构

```
src/kbapp/
├── __init__.py            # re-export __version__
├── __version__.py         # "0.1.0"
├── py.typed               # PEP 561 标记
├── cli/                   # Typer 入口层
│   ├── _common.py         # DataDirOpt / YesOpt / resolve_data_dir
│   ├── main.py            # 顶级 `kb` 应用 + `status` 子命令
│   ├── config.py          # `kb config {show,get,set,diff}` (M1 完整实现)
│   ├── index.py           # `kb index ...` 占位
│   ├── search.py          # `kb search ...` 占位
│   ├── collect.py         # `kb collect ...` 占位
│   ├── maint.py           # `kb maintenance ...` 占位
│   └── serve.py           # `kb serve ...` 占位
└── core/                  # 业务无关的基础设施
    ├── paths.py           # 数据目录布局 (DataPaths frozen dataclass)
    ├── config.py          # Config dataclass + load/dump/原子写/点路径 get-set
    ├── fingerprint.py     # SHA-256 + mtime_ns
    ├── lock.py            # 原子写锁（O_EXCL + PID 探测 + mtime 兜底）
    ├── registry.py        # SQLite 访问层 + DDL（五表 + FTS5）
    └── task.py            # 任务状态机 + 退避 + 崩溃恢复
```

**src-layout 原则**：`src/kbapp/` 强制安装后才可 `import kbapp`；CI 测试在隔离环境跑，避免本地 `python -c` 误用未打包源码。

## 模块职责

| 模块 | 职责 | 对应设计 |
|---|---|---|
| `core/paths` | 数据目录布局；所有相对路径常量；`ensure_dirs()` 不创建文件 | 03 §2 |
| `core/config` | YAML 配置加载/原子写/默认值合并；点路径 get-set；与默认值 diff | 05 §2.5 |
| `core/fingerprint` | SHA-256 流式计算；mtime 纳秒；为增量更新提供主键 | 03 §3.1 |
| `core/lock` | 进程间写互斥；崩溃残留自动回收（PID 探测 + mtime 兜底） | 05 §7，S7 修复 |
| `core/registry` | SQLite 连接封装（WAL + FK + Row 工厂）；DDL；事务上下文；FTS5 (trigram) | 05 §2.1，07 S3/S4/R3/§9 |
| `core/task` | 任务状态机 pending→running→{done, failed}；退避 30s→1m→5m；崩溃恢复 | 05 §4.0，07 §7.2 |
| `cli/main` | 顶级 Typer 应用 + 全局 `--data-dir`；`status` 展示任务统计 | 05 §9 |
| `cli/config` | `kb config ...`：读 / 写 / 审计 / diff | 05 §9，07 §6 |

## 数据流（M1 范围）

```
用户 ── kb config set k v ──► acquire_write_lock ──► load_config
                                                       │
                                                       ▼
                                              set_value (类型校验)
                                                       │
                                                       ▼
                                       dump_config (tmp + rename)
                                                       │
                                                       ▼
                                       config_audit (SQLite 写一行)
                                                       │
                                                       ▼
                                          release_write_lock
```

`kb status`：

```
用户 ── kb status ──► reset_stale_running ──► count_tasks (按状态聚合) ──► Rich Table
```

## 设计决策的可追溯性

每个评审修订（S1–S8 / R1–R4）在代码中的落地点见 `docs/milestone-log.md`。

## 未来锚点

| 里程碑 | 拟新增 / 替换 |
|---|---|
| M2 解析+分类 | `core/parse/{pdf,html,md,docx,txt}.py`；`cli/index.py` 占位替换为 `kb index scan/run/reindex/add`；`core/parse/cache.py` 写入 `cache/extracted/<sha256>.json` |
| M3 检索 | `core/retrieve/{bm25,vector,hybrid}.py`；LanceDB 集成（`[vector]` extra）；`cli/search.py` 占位替换 |
| M4 MCP | `core/mcp/server.py`（FastMCP）；`cli/serve.py` 启动 stdio / HTTP；`[mcp]` extra |
| M5 图谱 | `core/graph/{ladybug,kuzu}.py`（LadybugDB 优先，Kuzu 降级）；`[graph-ladybug]` / `[graph-kuzu]` extra；`stage_extract` / `stage_relate` |
| M6 Web UI | `cli/serve.py` 加 FastAPI 子命令；移植 `design/kb-app/prototype/*.html` |
| M7 自动扩充 | `cli/collect.py` 占位替换为 `kb collect run / kb inbox list/accept/reject`；评分插件加载 |
| M8 评测 | `core/scoring/` 插件协议；`cli/maint.py` 加 `kb maintenance eval` |

## 不在 M1 范围（明确边界）

- 任何解析器（PDF/HTML/MD/DOCX/TXT）
- 任何 LLM/Embedding 调用
- LadybugDB / LanceDB / FastMCP 接入
- Web UI / FastAPI
- arXiv 收集器 / Inbox / 评分插件
- 实体抽取 / 关联阅读

`stage_*` 流水线（M5+）只在 M5 落地；M1 仅预留任务 kind 枚举（`parse/classify/summarize/extract/index/collect/tombstone`）。