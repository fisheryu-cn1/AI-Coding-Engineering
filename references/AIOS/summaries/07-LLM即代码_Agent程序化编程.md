# 论文摘要：LLM-as-Code（Agentic Programming — 程序掌控控制流）

> **原论文标题**：LLM-as-Code: Agentic Programming for Agent Harness
> **完整 PDF 文件名**：`07-Qi-LLM-as-Code.pdf`
> 作者 / 年份 / 出版：Junjia Qi, Zichuan Fu, Jingtong Gao, Wenlin Zhang, Hanyu Yan, Xian Wu, Xiangyu Zhao（City University of Hong Kong / Tencent Jarvis Lab），2026，KDD 2026 Workshop on Agentic SE（AgenticSE），arXiv:2606.15874v2
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **长时、多步、可靠** 的 AI 编程 / 通用 Agent harness 时：本文论证"LLM-as-Orchestrator"范式有结构性失败，主张"LLM-as-Code"。
- 解决 **token 爆炸（context overflow）**、**控制流幻觉（control-flow hallucination）**、**完成不可靠（unreliable completion）** 三类典型 Agent 失效。
- 当需要让 Agent 同时满足：① 灵活的 LLM 推理；② 可靠的循环 / 分支 / 顺序执行；③ 单元测试级别的可断言性。
- 设计 **多 Agent 协作**（每个 Agent 是一个普通函数）时的范式选择。
- 给 Agent 写 **自编程演化**（self-programmed evolution）的工程范式。

> 锚点：Abstract；§1 Introduction；§2 Why LLM Orchestrator Fails；§3 Agentic Programming；§4 Conclusion。

## 2. 主要观点与方案

### 2.1 核心论断（§1）

- "Token 爆炸、控制流幻觉、完成不可靠不是实现 bug，而是 **把确定性工作交给概率系统的架构后果**"。
- 范式主张：LLM **不应** 是 Orchestrator，而应是 **被调用的组件**——程序掌控控制流，LLM 在需要推理的节点被 invoke。

### 2.2 LLM-as-Orchestrator 失败的三个层级（§2）

- **§2.1 确定性 vs 概率性工作流**：把 looping、branching、sequencing、variable binding、error handling 这些确定性步骤交给概率系统，是 **类别错误**——a for loop 跑 n 次靠语言运行时保证，LLM 决定的"做几次"则随时间衰减。
- **§2.2 不可保证的合规性**：每个控制决策都是采样结果，无原生机制遵守"提交前跑测试"这类硬规则；规则越多越难全守。
- **§2.3 上下文溢出**：
  - 硬限制：窗口不够时必须截断或摘要，丢失早期根因假设。
  - 软成本：长上下文中推理质量下降（多步任务准确率衰减），吞吐下降（每步 token + 延迟增加）。

### 2.3 Agentic Programming 的四要素（§3）

- **§3.1 代码驱动的工作流**：Agent 工作流用普通代码写，运行时不依赖模型遵从规则。LLM 仅在需要时调用——其判断可递归触发更多 LLM 调用（call-site decorator）。
- **§3.2 DAG 结构化上下文**：上下文不再是对话日志，而是 **调用图（DAG）**——一个 call 看见整个祖先链，每个 frame 仅保留已返回子节点的摘要。任意时刻上下文长度 = O(depth)，不是 O(steps)。
- **§3.3 多 Agent 协作**：Agent 是普通函数，多 Agent 是 **并发函数调用**——每个子 Agent 在自己的 call 里推理，结果通过 typed return value 合并。失败局部化、可重试、可路由到更强模型。
- **§3.4 自编程演化**：Agent 可生成并精炼其他 Agent 函数，但生成是 LLM 调用，**结果以代码形式提交**（通过 caller 测试后才接受），从此如同普通保证步骤运行。

### 2.4 案例：GUI Agent（§3 末，Table 1）

- OSWorld 基准上：最强 baseline Holo3-35B-A3B 80.4%、OpenAPA Gemini-3.1-pro 78.3%、Claude Sonnet 4.6 72.1%（均 100 步）。
- LLM-as-Code + Claude Sonnet 4.6：**86.8%（仅 15 步）**——步数节省 + 准确率提升。

> 锚点：§1 Introduction; §2.1 Deterministic vs Probabilistic Workflow; §2.2 Unguaranteed Compliance; §2.3 Context Overflow; §3.1 Code-driven agent workflow; §3.2 DAG-structured context; §3.3 Multi-agent collaboration; §3.4 Self-programmed evolution; Figure 1 LLM-as-Orchestrator vs LLM-as-Code; Figure 2 DAG 上下文追踪; Table 1 OSWorld 结果。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| OSWorld 整体成功率（GUI Agent） | **86.8%（15 步）** vs 最强 baseline 80.4%（100 步） | §3, Table 1 |
| 步数节省 | 100 → 15（约 6.7×） | Table 1 |
| Holo3-35B-A3B baseline | 80.4%（100 步） | Table 1 |
| OpenAPA w/ Gemini-3.1-pro | 78.3%（100 步） | Table 1 |
| Claude Sonnet 4.6 baseline | 72.1%（100 步） | Table 1 |
| 评测基准 | OSWorld（public leaderboard，访问 2026-06-02） | Table 1 脚注 |
| 编程范式收益 | 上下文 O(steps) → O(depth)；失败局部化；可单元测试；可逐步迁移 | §3.2-3.4 |
| 适用范围限制 | 完全开放式（无 stage model）的 brainstorm / research 仍适合 LLM-driven 编排 | §3.4 |

> 锚点：§3.3 Code-review agent 案例; §3.4 Self-programmed evolution; Table 1 OSWorld; Appendix C call-site decorator; Appendix E 完整对比。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2606.15874 |
| 会议 | KDD 2026 Workshop on Agentic Software Engineering (AgenticSE) |
| 引用框架 | AutoGen、OpenHands、MetaGPT、ReAct、Toolformer、DSPy |
| 案例系统 | OSWorld（GUI agent 评测）；本研究基于 Claude Sonnet 4.6 |
| 关联设计模式 | 与 08-Zheng-ActPlane（OS 级策略强制执行）、02-AIOS（OS 级调度）、10-Ben_Sghaier（harness 演化）共同构成"Agent Harness 设计"系列参考 |
| 引用文献 | [10][11] Same Task More Tokens / Lost in the Middle（验证上下文衰减）；[12] Can LLMs Follow Simple Rules?（验证规则遵从）；[5] MetaGPT（多 agent 代码组织） |

> 锚点：Abstract; §3.4 末段（OSWorld 案例）；References（DSPy [9]、Lost in the Middle [11]、Can LLMs Follow Simple Rules [12] 等）。

## 5. 一句话索引（给 Agent 用）

> 本文是 Agent Harness 范式批评 + 重建的代表：**主张程序而非 LLM 掌控控制流（Agentic Programming），LLM 仅在被调用时推理**——同时给出 DAG 化上下文（O(steps)→O(depth)）、多 Agent 即并行函数调用、自编程演化（改进提交为代码）三件工程工具；OSWorld 上 86.8% / 15 步 vs baseline 80.4% / 100 步是说服力最强的实证。与 08-ActPlane 互补：本文负责"控制流在程序"，08 负责"策略在内核执行"。