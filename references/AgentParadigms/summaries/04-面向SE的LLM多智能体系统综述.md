---
title: "LLM-Based Multi-Agent Systems for Software Engineering: Literature Review, Vision, and the Road Ahead"
source_pdf: "04-He-Multi_Agents_for_SE_Review_v4.pdf"
arxiv_id: "2404.04834"
arxiv_version: "v4"
authors:
  - "Junda He"
  - "Christoph Treude"
  - "David Lo"
year: 2024
venue: "ACM TOSEM 34(5), 2025"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：面向 SE 的 LLM 多智能体系统综述（He/Treude/Lo）

## 1. 适用场景

- 当你要为 **SDLC 某一阶段（需求工程、代码生成、质量保障、维护或端到端开发）选型现成 LMA 框架**、比较其角色分工与协作机制时，读 §3.1–§3.5 的逐阶段框架清单（Elicitron、MARE、PairCoder、ChatDev、MetaGPT、AgileCoder、SWE-Search 等 71 篇一手研究的归纳）。
- 当你要**设计一个多智能体编码/测试/修复系统**、需要常见角色模板（Orchestrator/Programmer/Reviewer/Tester/Information Retriever）与编排平台设计维度（协调模型、通信机制、CPDE vs DPDE）时，读 §2.3 与 §3.2。
- 当你要**评估当前 LMA 系统的真实能力边界**、决定把多复杂的任务交给它（快速原型 vs 逻辑密集功能）时，读 §4 两个 ChatDev 案例的量化结果。
- 当你要**规划 LMA 研究方向或写研究计划**（角色扮演增强、面向 agent 的提示语言、人机任务分配、协同基准、规模化、隐私）时，读 §5 的两阶段研究议程与 8 个研究问题。
- 当你需要在论文中**引用 LMA-for-SE 的标准定义**（LLM-based agent 六元组、LMA 系统的两大组成）时，读 §2 PRELIMINARY。

> 锚点：§1 INTRODUCTION; §2 PRELIMINARY; §3 LITERATURE REVIEW; §4 CASE STUDY; §5 RESEARCH AGENDA。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 INTRODUCTION）

- 单个 LLM-based agent 难以覆盖跨领域的真实问题；LMA（LLM-based Multi-Agent）系统通过多专长 agent 的辩论、交叉审查与协同获得三重收益：自主问题求解、鲁棒性与容错（对抗 hallucination）、对复杂系统的可扩展性（§1）。
- 论文三大贡献：71 篇一手研究的系统综述、两个案例研究、两阶段结构化研究议程，服务于 Software Engineering 2.0 愿景（§1）。

### 2.2 概念基础：从 autonomous agent 到 LMA 系统（§2 PRELIMINARY）

- §2.1 给出 autonomous agent 五属性：Autonomy、Perception、Intelligence and Goal-Driven、Social Ability、Learning Capabilities。
- §2.2 用六元组 ⟨L, O, M, P, A, R⟩ 形式化 LLM-based agent：LLM 认知核（ChatGPT/Claude/Gemini 类）、Objective、Memory、Perception、Action、Rethink（行动后的反思）。
- §2.3 定义 LMA = 编排平台 + LLM-based agents：§2.3.1 编排平台规定协调模型（合作/竞争/层级/混合）、通信机制（集中/分散/层级；交换代码片段、commit message、bug 报告、漏洞报告等）与规划学习风格（CPDE 集中规划分散执行 / DPDE 分散规划分散执行）；§2.3.2 agent 档案可预定义或由 LLM 动态生成、可同构或异构，交互可建模为图 G(V,E)。

### 2.3 综述方法（§3 LITERATURE REVIEW）

- 在 DBLP（750 万+ 篇出版物、1,800 种期刊、6,700 个学术会议）上按 [agent words] AND [SE words] 对四个 SDLC 阶段分别检索（执行日 2024-11-14）；三阶段筛选含 8 条排除标准（短文、重复、非 LMA、ChatGPT 发布（2022-11）之前、无实验结果等），得 41 篇；再双向雪球至不动点补 30 篇，合计 71 篇一手研究（§3）。

### 2.4 SDLC 各阶段的 LMA 应用图景（§3.1–§3.5）

- 需求工程（§3.1 Requirements Engineering）：Elicitron 以模拟用户 agent 群做需求引导；MARE 用 stakeholder/collector/modeler/checker/documenter 五种 agent、九种动作覆盖引导-建模-验证-规格；Sami 等用 product owner/developer/QA/manager 四 agent 生成、评估与排序用户故事。
- 代码生成（§3.2 Code Generation）：归纳出五类通用角色——Orchestrator（PairCoder 的 Navigator-Driver、SoA 的 Mother-Child 层级、CODES 的 RepoSketcher/FileSketcher/SketchFiller）、Programmer、Reviewer、Tester（无预定义测试时自生成含边界用例的测试）、Information Retriever（Agent4PLC、MapCoder 的检索 agent；CodexGraph 经图数据库查询）；Agent Forest 不做角色分工，改用采样-投票选共识最高的候选。
- 质量保障（§3.3 Software Quality Assurance）：测试——Fuzz4All（多语言模糊测试，蒸馏 agent + 生成 agent）、AXNav（自然语言驱动的 iOS 无障碍测试）、WhiteFox（编译器优化测试）及渗透/UAT/GUI 测试；漏洞检测——GPTLens（多审计员 + critic 排序过滤）、MuCoLD（tester/developer 讨论达共识）、Widyasari 等（多 LLM 交叉验证）；缺陷检测——ICAA（Report Agent + False Positive Pruner + 代码-意图一致性检查）；故障定位——RCAgent（云环境根因）、AgentFL（Comprehension/Navigation/Confirmation 三阶段）。
- 维护（§3.4 Software Maintenance）：调试普遍遵循复现-定位-修复-验证流水线（MASAI、MarsCode、AutoSD、FixAgent、MASTER 的 Code Quizzer-Learner-Teacher、AutoCodeOver 的谱定位 + AST 表示、SpecRover 的意图规约、DEI 的元策略重排、SWE-Search 的 MCTS、RepoUnderstander 的全仓知识图谱）；ACFIX 从 344,000+ 份智能合约挖 RBAC 模式指导修复；代码审查——Rasheed 等四 agent 系统、CodeAgent（带 QA-Checker 监工）；测试用例维护——Lemner 等两种架构预测需维护的测试。
- 端到端开发（§3.5 End-to-end Software Development）：多数沿用 Waterfall（MetaGPT：PM→Architect→Engineer→QA）；AgileCoder/AgileGen 走敏捷冲刺（AgileGen 用 Gherkin 写可测需求并融入人机协作）；ToP 与 MegaAgent 动态生成过程实例与角色任务；Co-Learning 与 IER 复用历史项目经验；FlowGen、Self-Collaboration 因实验只做代码段生成，不计入真端到端。

### 2.5 案例研究：ChatDev 实测（§4 CASE STUDY）

- 设置（§4）：ChatDev（designing/coding/testing 三阶段；CEO、CTO、programmer、reviewer、tester 角色），底座 GPT-3.5-turbo，temperature 0.2。
- Snake（§4.1 Snake Game）：第 1 次失败、第 2 次成功且满足 prompt 全部要求，并生成含依赖与分步运行说明的手册；平均 76 秒、$0.019/次。
- Tetris（§4.2 Tetris Game）：前 9 次尝试均无法产出可玩版本，第 10 次满足大部分要求，但始终缺少"消除整行"核心功能；平均 70 秒、$0.020/次。
- 结论（§4.2 Summary of Findings）：LMA 适合中等复杂度任务与快速原型；复杂逻辑推理与抽象仍是短板。

### 2.6 两阶段研究议程（§5 RESEARCH AGENDA）

- Phase 1 增强个体 agent 能力（§5.1）：RQ1 哪些 SE 角色适合 LLM-based agent 扮演、如何增强；RQ2 如何设计有效、灵活、稳健的提示语言。§5.1.1 给出三步路线——识别与排序关键角色（市场分析/利益相关者参与/价值增量建模）→ 对照角色要求评估 agent 能力（能力映射/情境化性能评估/差距分析/专家迭代）→ 定向增强（专用语料微调（PEFT）、定制提示库、持续学习与再训练）；动机是 ChatGPT 等通用模型缺 SE 细分专长（如漏洞检测/修复被证实不足）。§5.1.2 主张以 Agent-Oriented Programming（AOP）乃至 Multi-Agent-Oriented Programming（MAOP）为基础，设计把 LLM 当第一受众的提示语言，权衡表达力与学习成本，并考虑跨模型/版本迁移。
- Phase 2 优化 agent 协同（§5.2，RQ3–RQ8 对应六个子节）：§5.2.1 人机协作——角色特定介入准则与界面、预测最优人机配比；§5.2.2 协同评估——现有基准只考孤立解题，应评估协作设计、任务委派与协调、冲突识别与协商、组件集成与同行评审、主动澄清五类能力，并度量协作过程（沟通效率、歧义消解、冲突管理）；§5.2.3 规模化——层级任务分解、摘要化通信防过载、共享黑板/集中知识库保一致性、决策层级与共识算法防拖慢；§5.2.4 借鉴工业原则——Value Stream Mapping、Design Thinking、MBSE、DDD、BDD、Team Topologies 尚未被利用；§5.2.5 动态适配——按需增删/复制 agent、动态重定义角色、内存与算力再分配、学习型终止条件；§5.2.6 隐私与部分信息——跨组织细粒度访问控制（扩展 RBAC/ABAC）、Differential Privacy/SMPC/Federated Learning/Homomorphic Encryption、GDPR/CCPA 合规与 privacy-by-design、区块链/分布式账本记录 agent 交易。

### 2.7 讨论、效度威胁与结论（§6 DISCUSSION; §7 CONCLUSION AND FUTURE WORK）

- §6.1 与 Mixture of Experts（MoE）对比：MoE 参数总量大、门控训练贵，且专家间无交互通信；LMA 显式模拟真实协作流、可整合编译器/静态分析/测试等外部反馈并支持持续 human-in-the-loop，作者认为更适合 SE 的多面挑战。
- §6.2 Threat to Validity：主要威胁是文献检索可能漏收；以 DBLP 广覆盖（含 preprint）+ 双向雪球缓解。
- §7 结论与未来工作：近期做 SE 专用数据集/预训练任务与提示策略；中期优化人机任务分配与大规模编排方法；长期解决 LMA 内数据隐私与访问控制。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 纳入综述的一手研究 | 71 篇 = DBLP 关键词检索 41 篇 + 双向雪球 30 篇（检索日 2024-11-14） | §3 LITERATURE REVIEW |
| 检索库规模 | DBLP：750 万+ 篇出版物、1,800 种期刊、6,700 个学术会议 | §3 LITERATURE REVIEW |
| Snake 案例成功率（中等复杂度） | 第 2 次尝试即满足 prompt 全部要求，另附完整运行手册 | §4.1 Snake Game |
| Snake 案例成本 | 平均 76 秒、$0.019 每次尝试 | §4.1 Snake Game |
| Tetris 案例成功率（较高复杂度，vs Snake 对比） | 第 10 次尝试才可玩，且仍缺"消除整行"核心功能 | §4.2 Tetris Game |
| Tetris 案例成本 | 平均 70 秒、$0.020 每次尝试 | §4.2 Tetris Game |
| 案例实现配置 | ChatDev + GPT-3.5-turbo，temperature 0.2 | §4 CASE STUDY |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2404.04834 |
| 案例框架 | ChatDev：§4 实验所用的开源多智能体软件开发框架（GPT-3.5-turbo 驱动） |
| 综述内代表性系统 | MARE、Elicitron、PairCoder、INTERVENOR、GPTLens、AgentFL、MASAI、AutoCodeOver、SpecRover、ACFIX、DEI、SWE-Search、MetaGPT、AgileCoder、MegaAgent、Co-Learning/IER 等，出处分布于 §3.1–§3.5 |
| 检索数据源 | DBLP（https://dblp.org）；检索式、纳入/排除标准与雪球流程均在 §3 LITERATURE REVIEW |

## 5. 一句话索引（给 Agent 用）

> He/Treude/Lo（TOSEM，arXiv:2404.04834v4）系统综述 71 篇一手研究：LMA（LLM 多智能体）= 编排平台 + 多专长 agent，应用覆盖需求工程、代码生成（Orchestrator/Programmer/Reviewer/Tester/Information Retriever 五类角色）、质量保障、维护与端到端开发（Waterfall/Agile/动态过程）；ChatDev + GPT-3.5-turbo（temperature 0.2）案例：Snake 第 2 次尝试即达标（76 秒、$0.019/次），Tetris 第 10 次才可玩且缺消行功能（70 秒、$0.020/次）；研究议程两阶段——增强个体 agent 能力（SE 角色扮演、AOP 式提示语言）与优化协同（人机协作、协作基准、规模化、工业原则、动态适配、隐私）。
