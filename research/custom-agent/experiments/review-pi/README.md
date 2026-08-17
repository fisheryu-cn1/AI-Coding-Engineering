# review-pi 工作区（场景一：代码评审 agent @ pi）

> 建立日期：2026-08-17（P2 装配，装配流程 v1 首次执行）
> 定位：本目录是可运行的装配工件集合（pi 约定目录结构），在本目录内启动 pi 即加载 skill/模板/扩展。
> 上游文档：画像卡（`../01-场景一画像-代码评审agent.md`）、装配流程 v1（`../../装配流程v1.md`）、装配实录（`../02-装配实录.md`）。

## 目录结构

```
review-pi/
├── .pi/
│   ├── skills/code-review/
│   │   ├── SKILL.md                    # L2 评审规范 skill（SOP+维度+红线；相对引用 assets，自包含可分发）
│   │   └── assets/
│   │       ├── review-rules.md         # RR-1~7 规则摘录（自包含，含检查方法与反例信号）
│   │       └── opinion-card-template.md# 意见卡模板 + 分级口径
│   ├── prompts/review-commit.md        # L2 提示模板（{{commit}} 变量）
│   └── extensions/review-guard.ts      # L1/L5 守卫：工具白名单外的写路径阻止（v0，需按 pi 版本校准）
├── evals/
│   ├── cases.jsonl                     # 评估标注集（从 5 份评审报告 × git 历史构造）
│   └── README.md                       # schema 与构造方法
├── scripts/
│   └── score_review.py                 # 召回评分器（启发式 v0）
├── reviews/                            # 意见卡输出目录（守卫允许的唯一写位置；运行后生成）
└── README.md                           # 本文件
```

## 运行方法

前置：宿主仓库（被评审对象）= 本仓库根目录；已安装 pi（`d:/users/yu/documents/coding/pi` 的 coding-agent，只读引用）。

```bash
cd <本仓库根>/research/custom-agent/experiments/review-pi
# pi 从 cwd 向上发现 .pi/ 资源；--fork 或直接会话均可
pi
# 会话内：
> /prompt review-commit {{commit}}   # 或直接粘贴模板内容并填入目标 commit
```

无交互批跑（评估）：`pi -p "<review-commit 模板内容，填入 commit>"`（print 模式，stdin 可管道）；每案例跑 3 次取 pass^k 一致性（画像卡 §5 口径）。

评分：`python scripts/score_review.py --reviews reviews/ --cases evals/cases.jsonl [--commit <hash>]`

## 已知校准项与运行状态（2026-08-18 暂停点更新）

1. **review-guard.ts 已按 pi 0.84.2 实版校准**（2026-08-17 第 2 场）：阻断用返回值 `{ block: true, reason }`，事件字段 `event.toolName` / `event.input`；实测拦截生效（意见卡之外的写路径被拒并回传理由）。
2. **运行必带 `-a`**（--approve）：`-p` 非交互模式无信任决策时会静默忽略 `.pi/` 资源（skill 与守卫全不加载）；工作区信任已写入 `~/.pi/agent/trust.json`，交互模式可直接用。
3. **已验证的运行记录**：run1–run3（锚点 f62f287，禁读修复提交）——19/21/23 条意见，P0 均命中 R-1；run2/run3 为 skill v2（RR-4 机械化 + RR-8）。轨迹报告见 `traces/`。
4. 评分器 `score_review.py` 为启发式（上界口径），语义召回需人工复核（当前语义明确命中 6/11，待核 R-8/R-10/R-12）；跨 run 一致性用 `compare_runs.py`；pass^k 只能同 skill 版本内计算。
5. 评估案例锚定"修复提交的父状态"，重现方法见 `evals/README.md`；F/N 系列案例须用各自锚点（6e1abeb / e7c9aa9）补跑，勿与 f62f287 混算。

## 组件登记（迁移参照，D1-S5）

| 工件 | 层/档位 | DSH 等价形态 | 接入成本预估 |
|---|---|---|---|
| code-review skill（含 assets/ 规则与模板，自包含） | L2 / F-通用 | `.agents/skills/code-review/` 整目录同构（assets 约定相同） | 近零（目录约定相同） |
| review-commit 模板 | L2 / F-通用 | 配置/插件注入 | 低 |
| review-guard 扩展 | L1+L5 / F-绑定 | ctx.tools 作用域 + ctx.fs provider / fs 事件 | 中（接缝模型不同，语义可平移） |
| 评分器 | L5 / F-通用（纯 python） | 生态插件或脚本 | 近零 |
| cases.jsonl | L5 数据 / F-通用 | 同 | 零 |
