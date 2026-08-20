# 评审工作包 V1.0（AI 代码评审 · 人在回路）

> 版本：V1.0（2026-08-20 发布）——本研究"先形成可用交付版本"的第一个正式交付。
> 本目录是**快照打包**：各组件的修订源头在研究仓库内（见 §6 源头声明），后续版本以源头为准重新打包。

## 1. 内容清单

| 组件 | 位置 | 版本 | 作用 |
|---|---|---|---|
| 评审方法总纲 | `评审工作方法总纲-V1.md` | V1.0 | **先用这个**：六环节流程、人工介入点、多轮策略、错判复核清单、停止条件 |
| 评审 skill | `skill-code-review/`（SKILL.md + assets 四件 + CHANGELOG） | 规则 v5 / 模板 v5 / 指南 v1.2 | 评审与复审的执行载体（规则集、意见卡模板、类型判定指南、规则修订工作单） |
| 提示模板 | `templates/review-*.md` | 2026-08-20 | 评审 / A 复核应答 / B 复审三阶段的任务提示（含隔离纪律全套） |
| 守卫扩展 | `templates/review-guard.ts` | pi 0.84.2 校准版 | 限制评审代理只写 reviews/ 目录（pi 扩展） |
| 决策模板 | `templates/待确认问题卡-模板.md` | v2 | 人工裁决介入点的记录工件（内联摘录规范） |
| 规约模板 | `templates/规约-验证对-模板与实例.md` | v1 | 给任何 LLM 知识资产配"考题"的方法模板 |
| 评估工具 | `tools/score_review.py` | v2 | 评分配对分组三子命令（score / pair / groups） |

## 2. 快速开始（pi 框架）

```bash
# ① 把 skill 与模板放入目标仓库（或你的工作区）
cp -r skill-code-review  <目标仓库>/.pi/skills/code-review
cp templates/review-*.md <目标仓库>/.pi/prompts/
cp templates/review-guard.ts <目标仓库>/.pi/extensions/
# ② 启动（项目信任按 pi 约定；-nc 防上下文文件注入，评估场景必带）
cd <目标仓库> && pi -a -nc
# ③ 会话内用 /prompt review-commit 或直接粘贴模板内容（填入目标 commit）
```

**其他智能体工具**（无 pi）：skill 的 assets 均为自足 Markdown——把 `review-rules.md`、`opinion-card-template.md`、`issue-type-guide.md` 的内容作为评审提示注入任何模型即可；提示模板同理（剥离 pi 特有措辞后通用）。

## 3. 最小起步流程（首次使用者）

1. 读《评审工作方法总纲》§0–§3（半小时）；
2. 在目标仓库跑**一轮裸模型基线**（不装 skill，普通评审提示）——总纲 §6：先知道裸模型在本项目的盲区，再决定规则预算投向；
3. 装载 skill 跑评审（隔离纪律照 `templates/review-commit.md` 第 5–7 条）；
4. 高方差任务加轮次并行，按总纲 §2 归并；
5. 人工只裁总纲 §3 的三类介入点；
6. 修复后用 `templates/review-recheck.md` 跑独立复审，按项目惯例出修复报告。

## 4. 效果证据与边界声明（诚实条款）

- **正面**：留出项目（规则从未接触）三锚点目标缺陷全部命中，且信息盲复跑确认不依赖答案渗漏；带规则指引两轮 ≈ 裸模型三轮覆盖（35 主题口径 22/35）；产出结构化可审计、定级可回溯；
- **边界**：通用工程缺陷（超时/重试/异常处理）裸模型即稳定发现，规则近乎零增量——**价值在领域契约与口径类缺陷**；单轮评审是缺陷空间采样（单轮召回 31–46%），多轮归并是必要组成而非可选优化；
- 全部证据出自两个真实项目（其一为生产在用系统）与 7+12 次评审运行，明细见研究仓库记录。

## 5. 跨框架迁移注记

skill 与模板均为纯 Markdown（框架无关）；pi 特有件两处：守卫扩展（Event API，语义可平移到其他扩展体系）与提示模板的 `/prompt` 引用（可改为直接注入）。DSH 等价形态与逐组件接入成本详见研究仓库 `custom-agent/experiments/review-pi/README.md` 组件登记表。

## 6. 源头声明与修订

| 组件 | 修订源头 |
|---|---|
| skill 及全部模板 | `research/custom-agent/experiments/review-pi/.pi/…`（CHANGELOG 记版本） |
| 方法总纲 | `research/custom-agent/评审工作方法总纲-V1.md` |
| 规约-验证对 | `research/agent-software-design/experiments/03-…md` |
| 评估工具 | `research/custom-agent/experiments/review-pi/scripts/score_review.py` |

修订流程：改源头 → 源头 CHANGELOG 登记 → 重新打包（本目录整体替换）并更新本 README 版本号。

## 7. V1.0 发布说明

首次可用版本。范围：单仓代码评审全流程（多轮评审→归并→人工决策→修复→复审→合并收口）。已知未含（列入后续）：框架级读保护扩展（eval-hygiene）、LLM 裁判自动化（含校准）、阶段-模型成本分层配置、多仓/多语种适配验证。
