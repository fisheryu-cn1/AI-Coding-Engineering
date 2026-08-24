# AgentParadigms 主题论文摘要索引

> 主题：Agent 设计范式——综述框架、经典范式原始论文、多智能体协作、失败模式与 benchmark 边界
> 文件数：30（2026-08-21 增补黑板×2 + 主动推理×2，见 manifest 增补节）
> 生成日期：2026-08-17（同日完成全文精读，摘要均为精读级 summary_version 3.0）；2026-08-24 增补 27/28（黑板架构谱系，summary_version 1.0）

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-LLM自主智能体综述.md](01-LLM自主智能体综述.md) | A Survey on Large Language Model based Autonomous Agents | Wang 四模块框架（Profiling/Memory/Planning/Action） |
| 02 | [02-面向软件工程的LLM智能体综述.md](02-面向软件工程的LLM智能体综述.md) | Large Language Model-Based Agents for Software Engineering: A Survey | SE 任务 × agent 组件矩阵（TOSEM） |
| 03 | [03-Agentic软件工程支柱与路线图.md](03-Agentic软件工程支柱与路线图.md) | Agentic Software Engineering: Foundational Pillars and a Research Roadmap | 四支柱 + agency/autonomy 自治分级 L0–L5 |
| 04 | [04-面向SE的LLM多智能体系统综述.md](04-面向SE的LLM多智能体系统综述.md) | LLM-Based Multi-Agent Systems for Software Engineering | SE 场景 MAS 成熟度地图（TOSEM 2025） |
| 05 | [05-ReAct推理行动协同.md](05-ReAct推理行动协同.md) | ReAct: Synergizing Reasoning and Acting in Language Models | 推理-行动循环（范式默认基线，ICLR 2023 Oral） |
| 06 | [06-Reflexion语言化反思.md](06-Reflexion语言化反思.md) | Reflexion: Language Agents with Verbal Reinforcement Learning | 语言化反思外循环（NeurIPS 2023） |
| 07 | [07-思维树ToT审慎搜索.md](07-思维树ToT审慎搜索.md) | Tree of Thoughts: Deliberate Problem Solving with Large Language Models | 推理时树状搜索（NeurIPS 2023） |
| 08 | [08-计划与求解提示范式.md](08-计划与求解提示范式.md) | Plan-and-Solve Prompting | 静态计划 + 顺序执行（ACL 2023） |
| 09 | [09-LLM编译器并行任务图.md](09-LLM编译器并行任务图.md) | An LLM Compiler for Parallel Function Calling | 任务 DAG 并行派发（ICML 2024） |
| 10 | [10-生成式智能体小镇.md](10-生成式智能体小镇.md) | Generative Agents: Interactive Simulacra of Human Behavior | 记忆流 + 反思 + 规划认知架构（UIST 2023） |
| 11 | [11-CAMEL角色扮演协作.md](11-CAMEL角色扮演协作.md) | CAMEL: Communicative Agents for "Mind" Exploration | 角色扮演对话（NeurIPS 2023） |
| 12 | [12-MetaGPT多智能体装配线.md](12-MetaGPT多智能体装配线.md) | MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework | SOP 装配线 + 中间产物契约（ICLR 2024） |
| 13 | [13-AutoGen可编程会话.md](13-AutoGen可编程会话.md) | AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation | 可编程会话协议（v0.2 原点） |
| 14 | [14-AgentScope消息中心平台.md](14-AgentScope消息中心平台.md) | AgentScope: A Flexible yet Robust Multi-Agent Platform | 消息中心式多 agent 平台（v1 论文） |
| 15 | [15-MAST多智能体失败分类.md](15-MAST多智能体失败分类.md) | Why Do Multi-Agent LLM Systems Fail? | MAST 失败分类法（FC1 41.77%） |
| 16 | [16-更多智能体采样投票.md](16-更多智能体采样投票.md) | More Agents Is All You Need | 采样投票规模化（best-of-N 基线，TMLR） |
| 17 | [17-单智能体还是多智能体.md](17-单智能体还是多智能体.md) | Single-agent or Multi-agent Systems? Why Not Both? | SAS↔MAS 级联（ASE 2025） |
| 18 | [18-Agent框架代码任务实证.md](18-Agent框架代码任务实证.md) | A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric SE Tasks | 7 框架实测（SAS 持续优于 MAS） |
| 19 | [19-收益递减错觉长程执行.md](19-收益递减错觉长程执行.md) | The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs | 长程执行与 self-conditioning（ICLR 2026） |
| 20 | [20-METR长任务时间地平线.md](20-METR长任务时间地平线.md) | Measuring AI Ability to Complete Long Software Tasks | 50% 时间地平线（每 7 个月翻番） |
| 21 | [21-SWE基准错觉与记忆污染.md](21-SWE基准错觉与记忆污染.md) | The SWE-Bench Illusion | 基准记忆污染探测 |
| 22 | [22-SWE基准多模态.md](22-SWE基准多模态.md) | SWE-bench Multimodal | 视觉域迁移崩塌（最佳仅 ~12%） |
| 23 | [23-TAU基准工具策略.md](23-TAU基准工具策略.md) | τ-bench | 工具-代理-用户交互 + pass^k（ICLR 2025） |
| 24 | [24-TAU2双控协调基准.md](24-TAU2双控协调基准.md) | τ²-bench | 双控环境：协调独立于推理 |
| 25 | [25-GAIA通用助手基准.md](25-GAIA通用助手基准.md) | GAIA: A Benchmark for General AI Assistants | 通用助手基准（人类 92% vs GPT-4 15%） |
| 26 | [26-OSWorld计算机环境基准.md](26-OSWorld计算机环境基准.md) | OSWorld | 真实计算机 GUI 环境（人类 72% vs 模型 12%） |
| 27 | [27-黑板架构高级多智能体.md](27-黑板架构高级多智能体.md) | Exploring Advanced LLM Multi-Agent Systems Based on Blackboard Architecture | 黑板 MAS 首个 LLM 实现（黑板取代 memory + 动态调度） |
| 28 | [28-黑板多智能体信息发现.md](28-黑板多智能体信息发现.md) | LLM-based Multi-Agent Blackboard System for Information Discovery in Data Science | 黑板广播 + 自愿应答（数据发现，vs 主从式 +13%~57%） |
| 29 | [29-缺失的奖励经验时代的主动推理.md](29-缺失的奖励经验时代的主动推理.md) | The Missing Reward: Active Inference in the Era of Experience | 以内在自由能最小化取代外部 reward 的概念论文（有公式伪代码、无实验） |
| 30 | [30-神经语言模型的自由能与主动推理.md](30-神经语言模型的自由能与主动推理.md) | Free Energy Principle and Active Inference in Neural Language Models (short) | FEP×NLM 接口的概念定义（被动生成 vs 主动行动的边界，CEUR 短文） |

## 推荐先读

- **综述三件套**：01 → 02 → 03（组件框架 → SE 任务矩阵 → 工程过程支柱）
- **范式谱系**：05（ReAct 循环）→ 06（反思外循环）→ 08（静态计划）→ 09（DAG 并行）→ 07（树搜索）
- **多智能体**：11 → 12 → 13（三原语）→ 15（失败分类）→ 16 → 17 → 18（SAS/MAS 收敛链）
- **黑板替代路线**：27（黑板=共享内存 + 控制单元调度）→ 28（黑板=广播信道 + 全员自主）——两者互为谱系对照
- **主动推理路线**：29（EFE 目标函数与控制回路骨架）→ 30（FEP×NLM 概念边界）——工程成熟度评估见摘要：有公式、无系统、无实验
- **可靠性**：19（self-conditioning）→ 20（时间地平线）→ 23（pass^k）

## 与 GraphIt-KB 的相关性

- 本主题是 `research/agent-software-design/` 理论框架 v0.2 的文献底座（三层骨架/两维范式/MAST 证据链/benchmark 边界），GraphIt-KB 检索层可借此回答 agent 设计类问题。
- 15（MAST）与 19（self-conditioning）直接支撑"验证组件与分段检查点是必备件"的架构判断；20/23 提供评估口径（时间地平线、pass^k），可借鉴为 GraphIt-KB 评分模块的可靠性指标设计。
- 27/28（黑板谱系）支撑 `research/agent-software-design/materials/harness与冯诺依曼架构类别关系.md` 的"黑板折中派"论证——共享结构化状态对象对"传话游戏"（上下文碎片化）的解法，与本研究"文档传递式协同"的独立收敛互证。
- 深度精读版梳理见 `research/agent-software-design/materials/agent范式-学术梳理.md`。
