# review-pi 工作区（场景一：代码评审 agent @ pi）

> 建立日期：2026-08-17（P2 装配，装配流程 v1 首次执行）
> 定位：本目录是可运行的装配工件集合（pi 约定目录结构），在本目录内启动 pi 即加载 skill/模板/扩展。
> 上游文档：画像卡（`../01-场景一画像-代码评审agent.md`）、装配流程 v1（`../../装配流程v1.md`）、装配实录（`../02-装配实录.md`）。

## 目录结构

```
review-pi/
├── .pi/
│   ├── skills/code-review/SKILL.md     # L2 评审规范 skill（SOP+维度+意见卡模板+红线）
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

## 已知校准项（v0 风险登记）

1. **review-guard.ts 的事件负载字段名**为按调研材料推断（toolCall/name/arguments 多候选读取），首次运行需对照所装 pi 版本 `docs/extensions.md` 校准；未找到阻止 API 时降级为告警（不静默失败）。
2. skill 的意见卡以 Markdown 落盘 `reviews/`——评分器为关键词启发式（v0），语义召回需人工复核或后续引入 judge（按可观测清单 §5 的 judge 信度协议）。
3. 评估案例锚定"修复提交的父状态"，重现方法见 `evals/README.md`。

## 组件登记（迁移参照，D1-S5）

| 工件 | 层/档位 | DSH 等价形态 | 接入成本预估 |
|---|---|---|---|
| code-review skill | L2 / F-通用 | `.agents/skills/code-review/SKILL.md` | 近零（目录约定相同） |
| review-commit 模板 | L2 / F-通用 | 配置/插件注入 | 低 |
| review-guard 扩展 | L1+L5 / F-绑定 | ctx.tools 作用域 + ctx.fs provider / fs 事件 | 中（接缝模型不同，语义可平移） |
| 评分器 | L5 / F-通用（纯 python） | 生态插件或脚本 | 近零 |
| cases.jsonl | L5 数据 / F-通用 | 同 | 零 |
