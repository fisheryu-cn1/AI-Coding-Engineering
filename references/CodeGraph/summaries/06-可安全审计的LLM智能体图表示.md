# 论文摘要：Agent-BOM（用统一图表示对 LLM 智能体做安全审计）

> **原论文标题**：Towards Security-Auditable LLM Agents: A Unified Graph Representation
> **完整 PDF 文件名**：`Towards Security-Auditable LLM Agents-Graph Presentation.pdf`
> 作者 / 年份 / 出版：Chaofan Li, Lyuye Zhang, Jintao Zhai, Siyue Feng, Xichun Yang, Huahao Wang, Shihan Dou, Yu Ji, Yutao Hu, Yueming Wu, Yang Liu, Deqing Zou；华中科技大学 / 南洋理工大学 / 复旦大学 / 重庆邮电大学 / 东华大学；arXiv:2605.06812v1，2026-05
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- **LLM Agent 安全审计与根因分析**：当 Agent 通过工具调用、状态化记忆、多 Agent 协作执行任务，底层物理事件与高层意图之间存在语义鸿沟时。
- 把 SBOM / AIBOM / 日志 / 通用溯源图这些**碎片化证据**统一为可查询的图结构。
- **路径级图查询审计**：把每条安全规则抽象为"审计入口 → 后向追溯 → 前向追溯 → 裁决条件"的 4 元组。
- 与 OWASP Agentic Top 10（ASI01–ASI10）一一对应的**可实例化审计规则**。
- 在真实 Agent 运行环境（OpenClaw V2026.2.6）部署审计插件并复核 4 类复合攻击场景时。

> 锚点：摘要；§I Introduction；§II Motivation；§III Agent-BOM；§IV Auditing Paradigm；§V Evaluation。

## 2. 主要观点与方案

### 2.1 核心论点

- **碎片化证据不能审计 Agent**：SBOM 只看静态材料；日志只记录事件；通用溯源图无法覆盖 Agent 原生语义阶段（Goal/Context/Reasoning/Decision）。
- **Agent-BOM = 层次化属性有向图**，把静态能力层与动态语义层用语义边连接。
- **每条安全规则都是路径级图查询**：`R = (审计入口, 后向追踪, 前向追踪, 裁决条件)`。
- **跨层绑定边**解释"为什么选中该工具/代码"，把语义意图与物理动作缝合。

### 2.2 方法

- **静态能力层**：模型、提示、工具、技能、长期记忆、代码、Agent。
- **动态语义层**：外部输入、目标、上下文、推理、决策、动作、观察、输出。
- **语义边**：结构依赖、运行时演化、跨层行为-能力绑定、跨 Agent 传播。
- **安全属性**：来源、完整性、权限、授权、确认状态、影响证据。
- **审计范式**：① 入口定位（Where）→ ② 后向追踪（Why）→ ③ 前向追踪（How）→ ④ 裁决条件（What）。
- **实例化**：用 OWASP Agentic Top 10 实例化 10 条路径级规则。
- **实现**：在 OpenClaw V2026.2.6 中部署插件，基础模型 GPT-5。
- **4 个复合攻击场景**：
  1. 跨会话记忆中毒 + 工具误用
  2. 能力供应链劫持 + 意外代码执行
  3. 多 Agent 生态系统劫持
  4. 特权与信任滥用

> 锚点：§III Agent-BOM；§IV Auditing Paradigm；§V Evaluation；图 1 / Table I / Table II。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 覆盖 Q1–Q6（6 大审计问题） | 全部直接支持（✓） | Table II |
| 与传统 SBOM/AIBOM/Logging/Tracing 对比 | 在 4W 维度上均显著超越（Limited/Partial → High） | Table I / Table II |
| 实例化 OWASP Agentic Top 10 规则 | 10 条路径级规则 | §IV |
| 部署环境 | OpenClaw V2026.2.6 + GPT-5 | §V |
| 复合攻击场景验证 | 4 个隐蔽攻击链（跨会话记忆、能力供应链、多 Agent 生态、特权滥用）均能完整重建 | §V |
| 关键能力 | 持久性污染追踪、跨 Agent 传播追踪、跨层因果解释、影响证据 | §V |

> 锚点：§V Evaluation；Table I；Table II。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2605.06812v1，2026-05 |
| 风险框架 | OWASP Agentic Top 10（ASI01–ASI10） |
| 部署环境 | OpenClaw（V2026.2.6） |
| 概念邻居 | CPG（见 `02-`）、Code Property Graph、Supply-Chain SBOM（如 SPDX、CycloneDX） |
| 配套研究 | Code–Text–Code（见 `05-`）的"语义漂移 / 可追溯"思想 |

> 锚点：References。

## 5. 一句话索引（给 Agent 用）

> 想审计 LLM Agent 时，**别只盯日志或 SBOM**：用 **Agent-BOM 层次化属性图**同时建模静态能力 + 动态语义状态 + 安全属性，把每条 OWASP Agentic 风险表达为 `(入口, 后向, 前向, 裁决)` 4 元组路径查询——这是"把碎片证据缝成可追溯因果链"的最强框架。
