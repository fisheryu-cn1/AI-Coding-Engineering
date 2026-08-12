# 论文摘要：Agent Harness Evolution（harness 演化对 Agent 质量的影响）

> **原论文标题**：Don't Blame the Large Language Model: How Agent Harness Evolution Shapes Coding Agent Quality
> **完整 PDF 文件名**：`10-Ben_Sghaier-Agent_Harness_Evolution_v2.pdf`
> 作者 / 年份 / 出版：Oussama Ben Sghaier, Hao Li, Bram Adams, Ahmed E. Hassan（Queen's University, Canada），2026，ACM TOSEM（arXiv:2607.03691v2）
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 评估 **"模型升级 vs harness 升级哪个更影响 Agent 质量"** 时：本文是首个"固定模型、变 harness"的纵向控制研究。
- 给 Agent 团队做 **CI/CD 质量门禁** 设计时：本文提出"Agentic Quality Assurance"概念，揭示常规 CI/CD 无法捕捉非功能性质量回归。
- 决策 **何时应锁定 harness 版本**、何时可以滚动升级时。
- 给 Agent 框架做 **架构级回归风险热力图**（哪些组件变更最容易引发质量下降）。
- 评估 **企业为何普遍把质量回归归咎于模型而非 harness** 这一现象。

> 锚点：Abstract；§1 Introduction；§2 Background（2.1 Coding Agents, 2.2 Agent Harness）；§3 RQ0–RQ3；§6 Discussion。

## 2. 主要观点与方案

### 2.1 研究问题（§1）

- "Harness 持续演化 → Agent 质量持续提升"是普遍假设，但缺乏隔离 harness 贡献的纵向工作。
- 4 个 RQ：
  - RQ0：5 个主流 harness 的规模 / 演化特征；
  - RQ1：固定模型下，35 个 sequential release 的质量演化；
  - RQ2：哪些 release-level 模式与质量波动相关；
  - RQ3：哪些架构组件对变更更敏感。

### 2.2 现状观察：Hyper-churn（RQ0）

- 5 个 harness 平均：**1.5–18 releases/week，2.8–34 commits/day，PR 中位 review <4 小时**。
- 对比 VSCode / GitHubCLI：仅 **0.6–0.8 releases/week**，开发强度远不及 harness。
- 数月内 issue 累积数千条，关单率跟不上 → backlogs 膨胀。
- **30% commit 是 bug-fix**——反映"边开发新功能边修旧功能"的反应式循环。
- 命名为 **"hyper-churn"**：远超传统 OSS 的发布强度。

### 2.3 实验设置（§4）

- 选定 **Qwen Code CLI** 作为 deep-dive 对象（fork 自 Gemini CLI，支持自定义本地 LLM 端点 → 可固定模型）。
- 35 个 sequential release × 50 个 stratified SWE-bench Verified task，固定 LLM。
- 指标：resolve rate、token consumption、tool call count、latency。
- 引用论坛 / issue tracker 实证（Cursor version regression、Claude Code token spike、Codex quality cliff 等）。

### 2.4 关键发现（RQ1）

- **无统计显著的 resolve rate 提升**——尽管代码体量持续增长，35 个 release 的任务通过率几乎不变。
- **早期版本有时反而优于后期版本**。
- **Token 消耗与 tool call 数翻倍**（部分 release），质量未对应提升。
- 揭示"开发活动 ↔ Agent 效果"脱钩。

### 2.5 Release-level 模式（RQ2）

- **Feature-heavy releases** 与更高 resolve rate 相关（ρ=0.438），代价是 token / tool call 增加。
- **Fix-heavy releases** 与更高 token 消耗相关，但不改善 resolve rate。
- **大 PR / 合并 PR** 与更低 token 消耗相关（合并优于细碎 PR）。
- **代码删除** 与成本下降相关。

### 2.6 架构级风险（RQ3）

- 高风险组件 = **LLM Provider 层 + Context Management**——直接决定信息如何传给模型。
- 低风险组件 = **Extensibility + Security**——变更通常是 neutral 或 safe。
- 项目 CI/CD 全部通过，却仍出现质量回归——证明现行 CI/CD 无法捕捉"非功能性"质量回归。

### 2.7 概念：Agentic Quality Assurance

- 自动化质量回归测试，评估 token / tool call / 非功能性指标，而不仅是 patch 功能正确性。
- 建议研究者：报告时控制 harness 版本，不只报 LLM。

> 锚点：§1 Introduction（4 个 RQ）; §3 Study Design; §4 RQ0 Findings; §5 RQ1-RQ3 Findings; §6 Discussion（Agentic QA）; §7 Implications。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 35 个 Qwen Code release × 50 SWE-bench Verified 任务 | **无统计显著的 resolve rate 提升** | RQ1, §5 |
| Token 消耗（部分 release） | **翻倍**（无对应质量提升） | RQ1, §5 |
| Tool call 计数 | 部分 release 翻倍 | RQ1, §5 |
| Harness 演化强度 | **1.5–18 releases/week, 2.8–34 commits/day**（hyper-churn） | RQ0, §4 |
| 对比 VSCode / GitHubCLI | 0.6–0.8 releases/week | RQ0 |
| Bug-fix commit 占比 | ~30% | RQ0 |
| Feature-heavy release vs resolve rate | ρ = 0.438（正相关） | RQ2 |
| PR size vs token consumption | 负相关 | RQ2 |
| 高风险组件 | LLM Provider + Context Management | RQ3 |
| 现行 CI/CD 对 agentic 回归检出率 | 0（全部通过） | §6 |
| 实证参考 | 456,000+ PRs by 5 leading agents across 61,000+ repos over 6 months（背景数据） | §2.1 |

> 锚点：§4 RQ0 Hyper-churn; §5 RQ1 (no improvement, double tokens); §5 RQ2 (patterns); §5 RQ3 (LLM Provider / Context 高风险); §6 Discussion (Agentic QA)。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2607.03691 |
| 期刊 | ACM Transactions on Software Engineering and Methodology（TOSEM） |
| 实证对象 | Qwen Code CLI（35 releases），对比 Codex、OpenHands、Gemini、OpenCode |
| 评测模型 | 固定 LLM（与 harness 解耦） |
| 评测基准 | SWE-bench Verified（50 stratified tasks） |
| 关联项目 | 与论文 09-RepoRescue（Agent 评测）、论文 11-ICAE-Bench（vibe coding）、论文 04-Anthropic-Trends（行业趋势）形成互补 |
| 公开案例 | Cursor version regression forum、Claude Code token issue #16856、Codex #8272 等（§1 脚注） |

> 锚点：Abstract; §1 Introduction; §3 Study Setup; §4-§5 Findings; §6 Discussion; References (含 456K PR 数据)。

## 5. 一句话索引（给 Agent 用）

> 当需要给团队解释"为什么 harness 升级后 Agent 反而变差、但大家普遍怪模型"时，本文是直接证据：**固定模型，35 release × 50 SWE-bench task，无显著 resolve rate 提升 + token/tool call 翻倍**——并把"现行 CI/CD 检不出 harness 质量回归"命名为 **Agentic Quality Assurance** 缺口。RQ3 还指出高风险组件是 **LLM Provider + Context Management**，对 harness 内部架构 review 优先级排序有直接指导意义。