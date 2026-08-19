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
│   │       ├── opinion-card-template.md# 意见卡模板 v5 + 分级口径 + 格式契约
│   │       ├── issue-type-guide.md     # 问题类型判定指南（判定程序 + 已核定样例）
│   │       └── rule-revision-worksheet.md # 规则修订工作单（新案例→规则变更受控流程）
│   ├── prompts/
│   │   ├── review-commit.md            # 评审提示模板（{{commit}} 变量）
│   │   ├── review-respond.md           # A 复核应答模板（接受/部分/驳回+反证）
│   │   └── review-recheck.md           # B 复审模板（四档结论 + 驳回独立复核 + 回归检查）
│   └── extensions/review-guard.ts      # L1/L5 守卫：reviews/ 外写路径阻止（已按 pi 0.84.2 校准）
├── evals/
│   ├── cases.jsonl                     # 评估标注集（从 5 份评审报告 × git 历史构造）
│   ├── README.md                       # schema 与构造方法
│   └── 待确认问题卡-模板.md             # B1 流程工件（三触发点/人工四况归类/误检原因分析）
├── scripts/
│   └── score_review.py                 # 评估工具 v2（score / pair / groups；原 compare_runs.py 已并入）
├── reviews/                            # 意见卡/应答卡/复审卡输出目录（守卫允许的唯一写位置）
├── A-B评审闭环工作流.md                 # 闭环 SOP（五步/入口出口判则/模型路由/待确认流程）
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

评分：`python scripts/score_review.py score --reviews reviews/ --cases evals/cases.jsonl [--commit <标识>] [--anchor <hash>] [--json out.json]`
配对：`python scripts/score_review.py pair reviews/A.md reviews/B.md [...]`（pass^k 近似；自动配对为高精度子集，未配对清单供人工核验）

## 已知校准项与运行状态（2026-08-18 第 6 场后更新）

1. **review-guard.ts 已按 pi 0.84.2 实版校准**：阻断用返回值 `{ block: true, reason }`，事件字段 `event.toolName` / `event.input`；实测拦截生效。
2. **运行必带 `-a`**（项目信任）；信任已写入 `~/.pi/agent/trust.json`。
3. **运行记录（11 runs + 闭环首跑）**：run1–3（f62f287 × v1/v2）、run4（6e1abeb × v3）、run5（e7c9aa9 × v3）、run6（f62f287 × v4，**污染 run**——召回数字不可引用）、run7/run8（f62f287 × v4 **清洁双 run**——8 核心主题双 100%）、run9（f62f287 × skill v5，语义 7/11）、run10（`../review-control/` **无 skill 对照**，语义 3/11、原始格式不符契约经适配器评分）、闭环首跑（run9 → 应答卡 run9-respond → 历史修复 3ffebf0 → 复审卡 3ffebf0-recheck：已修复 5/部分 1/未修复 12/新发现 4——**复审发现历史修复未完全落地**，挂起待确认）。历史意见卡在 `reviews/archive/`。
4. **评估运行清洁规程**（第 5 场起强制）：运行前 `mv reviews/*.md reviews/archive/`；指令双禁（锚点后提交 + research/evals/reviews/scripts 目录）；pass^k 只在同 skill 版本内算。
5. **评估工具 v2（2026-08-19 第 8 场）**：`score_review.py` 双子命令——`score`（口径A 启发式上界 / 口径B 签名[文件键重合] / 错误排除检测[仅签名未命中时报] / B1 待语义核定工作清单）与 `pair`（意见配对：签名=规则∪文件末两段键，重叠系数≥0.5 且标题共享具体标识符——精确率优先，错配会无声污染 pass^k）。原 `compare_runs.py` 已删除（签名 v1 伪影根治）。已知容错：合并式"溯源 + 证据"字段（run7 偏差，已登记模板 v4 契约）。
6. 评估案例锚定"修复提交的父状态"（`evals/README.md`，含语义核定表与新发现复核）；F/N 系列用各自锚点，勿混。
7. **A-B 评审闭环工件（2026-08-19 第 9 场）**：`A-B评审闭环工作流.md`（五步：评审 → A 复核应答 → 修复 → B 复审 → 收口；含入口/出口判据、模型路由、待确认问题流程）+ 提示模板 `review-respond.md` / `review-recheck.md` + `evals/待确认问题卡-模板.md`。闭环首跑随批次 4 对照实验或独立安排；评分器 `groups` 子命令输出按文件分组核验清单，为语义配对（大模型判定 → 人工终审）提供确定性基底（实录 §8.5）。

## 组件登记（迁移参照，D1-S5）

| 工件 | 层/档位 | DSH 等价形态 | 接入成本预估 |
|---|---|---|---|
| code-review skill（含 assets/ 规则与模板，自包含） | L2 / F-通用 | `.agents/skills/code-review/` 整目录同构（assets 约定相同） | 近零（目录约定相同） |
| review-commit 模板 | L2 / F-通用 | 配置/插件注入 | 低 |
| review-guard 扩展 | L1+L5 / F-绑定 | ctx.tools 作用域 + ctx.fs provider / fs 事件 | 中（接缝模型不同，语义可平移） |
| 评分器 | L5 / F-通用（纯 python） | 生态插件或脚本 | 近零 |
| A-B 评审闭环（工作流文档 + respond/recheck 提示模板 + 待确认问题卡） | L2 流程 / F-通用 | 提示注入 + 流程文档（无框架绑定） | 低（提示模板需按目标框架提示机制接入） |
| cases.jsonl | L5 数据 / F-通用 | 同 | 零 |
