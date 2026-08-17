---
title: "Bidirectional Empowerment of Metamorphic Testing and Large Language Models: A Systematic Survey"
source_pdf: "04-Zheng-MT_LLM_Survey_v1.pdf"
arxiv_id: "2605.13898"
arxiv_version: "v1"
authors:
  - "Zheng Zheng"
  - "Zenghui Zhou"
  - "Yinwang Xu"
  - "Daixu Ren"
  - "Tsong Yueh Chen"
year: 2026
venue: "arXiv"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：蜕变测试 × LLM 双向赋能系统综述

## 1. 适用场景

- 当你要为"输出无唯一正确答案"的 LLM 任务（生成、问答、代码、摘要、对话、Agent 规划）**选择不依赖标注 oracle 的验证/评测手段**，并需要论证蜕变测试（MT）的适用边界时，读这篇的 §2.1–§2.2 与 §4。
- 当你要**系统梳理 MT×LLM 交叉领域的文献地图**——无论是"用 MT 测 LLM"（幻觉/公平性/鲁棒性/代码可靠性/RAG/对话/Agent）还是"用 LLM 自动化 MT"（MR 发现、输入变换、可执行测试、agentic 闭环）——需要一份带分类法和 93 篇初级研究索引的综述时。
- 当你要**为自己的系统设计蜕变关系（MR）**并想复用已有模式（语义一致性、人口统计扰动、对话级变换、end-state 等价、逻辑规则推导等）时，§4.2 按质量属性整理的 MR 策略清单可直接对照选型。
- 当你在搭建 LLM 评测体系时需要**规避数据泄漏/基准污染、处理非确定性、控制测试成本**，§6 的六类挑战与对策（防泄漏协议、统计化 MT、组合式 MT、成本感知、标准化）可当作设计 checklist。
- 当你需要引用证据说明"LLM 生成 MR 可行但有假阳性风险"或"知识蒸馏学生模型行为保真度存疑"等论点时，§5.1 与 §4.1.4 提供了带具体数字的实证出处。

> 锚点：§1 Introduction; §3.4 Proposed Taxonomy; §4 MT for LLMs; §5 LLMs for MT; §6 Challenges & Future Directions。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- LLM 的生成式、概率性、开放式输出使经典 oracle problem 在 LLM 场景下格外严重：答案不唯一、失败模式（幻觉、偏见、对抗脆弱性、非确定行为）难以用静态基准或精确匹配断言捕捉，人工标注不可扩展（§1）。
- MT 检查多次相关执行间的**必要关系**而非单输出对错，天然适配 LLM；反向地，LLM 的语义理解/推理/代码生成能力又能自动化 MT 中最耗人力的环节（MR 识别、输入变换、可执行测试实现）。作者将其概括为**双向赋能（bidirectional empowerment）**并形成闭环生态：MT 增强 LLM 可信性，LLM 增强 MT 可扩展性（§1、§2.3）。
- 文献趋势：2020–2026 累计发表量在 ChatGPT（2022 底）发布后出现拐点，2024 后两方向均快速增长（§1、Fig. 2）。
- 三个研究问题：RQ1 MT 如何验证/确认/评估/理解 LLM（§4）；RQ2 LLM 如何自动化 MT 生命周期（§5）；RQ3 闭环生态的开放挑战（§6）（§3）。

### 2.2 背景与核心概念（§2 Background and Core Concepts）

- **MT 形式化（§2.1）**：MR 是 SUT 函数 f 在 n≥2 个输入及其输出上的必要关系 R ⊆ Xⁿ×Yⁿ；输入分 source inputs 与由其构造的 follow-up inputs，二者构成 Metamorphic Group（MG）——MT 的基本执行单元。MT 流程四阶段：Source Test Generation → Input Transformation → Execution → Relation Checking；优势是无需人工核对即可海量产生测试。
- **LLM 质量保障难点（§2.2）**：非确定性（同 prompt 不同输出，甚至贪心解码下仍受实现/硬件影响）、开放性与 oracle 稀缺、幻觉与事实不可靠、对表层扰动敏感、需求隐式欠规约——五点合起来使 LLM 成为典型的 oracle 缺失系统。
- **双向协同（§2.3）**：MT for LLMs（验证一致性/对齐外部事实/系统评估/理解内部机制）+ LLMs for MT（MR 发现、变换合成、测试实现、agentic 闭环）。

### 2.3 综述方法与分类法（§3 Methodology and Taxonomy）

- **检索（§3.1）**：遵循 Kitchenham 系统综述指南；5 个库（ACM DL、IEEE Xplore、SpringerLink、ScienceDirect、arXiv）+ Google Scholar 补充（每查询看相关性前 250 条）；Boolean 检索式 = 8 个 MT 同义词 AND 12 个 LLM 同义词；仅检索 Title/Abstract/Keywords 元数据（排除顺带提及者），再用向后/向前滚雪球补召回；检索截至 2026-04-30，入选研究跨 2019-01 至 2026-04。
- **筛选（§3.2）**：元数据初筛后 135 篇进入详细评估 → 76 篇直接满足纳入/排除标准 → 滚雪球增补 17 篇 → **最终 93 篇初级研究**。纳入要求：显式采用 MT/定义或使用 MR、以 LLM 或 LLM 系统为 SUT 或用 LLM 支撑 MT、英文。
- **抽取与编码（§3.3）**：抽取书目信息、MT/LLM 角色、MR 类型、变换策略、输出检查机制、模型/数据集/指标/局限等字段；多标签编码，一作者编码 + 至少一作者交叉核对，分歧讨论至共识。
- **分类法（§3.4）**：两方向树。MT for LLMs 下分功能视角（Verify/Validate/Assess/Understand）与应用视角（幻觉、公平性、鲁棒性、代码生成与修复、复杂系统-Agent 与对话）；LLMs for MT 下分三个自动化阶段（MR 自动发现、输入变换与测试实现、agentic 闭环测试）。计数非互斥：MT for LLMs 共 70 篇（功能 43 / 应用 63），LLMs for MT 共 34 篇——MT 作为保障技术的探索远多于 LLM 作为 MT 自动化机制的探索。

### 2.4 MT for LLMs：功能视角（§4.1 Functional Perspectives）

- **Verify——内部一致性与逻辑正确性（§4.1.1）**：语义不变式验证（CheckList 的 Invariance/Directional Expectation 行为测试矩阵；LLMORPH 用 36 个 MR + LLM 变换做全自动验证；Curtò & Zarzà 对数学/物理推理链做结构/冗长/上下文变换并逐步算语义相似度，揭示聚合精度与逐步推理保真的分离）；逻辑与时序一致性（Drowzee-Temporal 用 metric temporal logic + 逻辑编程合成时间约束问答对）；代码与 Text-to-SQL（Chan 等对称 MR 验证 prompt 语义保持时代码等价；SQLhd 两阶段 MT 无需 ground-truth SQL 即可查出 schema 链接幻觉与比较范围/极值错误）；RAG 检索机制（MeTMaP 用词级/句级 MR 构造三元组揭露虚假向量匹配；CHIME 在 bug 报告理解中在线验证并修复 ChatGPT 回答）。
- **Validate——对齐现实真值与用户期望（§4.1.2）**：事实对齐与幻觉确认（SelfCheckGPT 多采样一致性；MetaQA 同义/反义 MR；DrHall 多路投票主动诱发不一致并纠正；Drowzee 从知识库抽事实三元组 + 否定/对称/传递规则生成 MR）；RAG 证据对齐（MetaRAG 将答案拆原子 factoid、同义反义变体对照检索上下文打幻觉分）；对话 Agent（Sensei 用户模拟器 + DSL 检查多轮 MR；CQ2A 上下文驱动问题生成）；置信度评估（PCS 用主动/被动语态变换、双重否定等 MR 聚合标签一致性估计零样本分类置信度，无需内部 logits）；代码对齐（MRSQLGen 用蜕变 prompting 对比原/变换 SQL 执行结果；Metamorphic prompt testing 用 prompt 复述生成多程序变体交叉验证；Metamon 把文档当规约验证程序行为；CID 的 Enquirer-Challenger-Decider 架构）；法律合规（税法更新转可执行工件 + 税务性质派生 MR 验证合法性）。
- **Assess——系统评估与基准化（§4.1.3）**：通用库（PromptOps 可视化数据流工具；METAL 形式化 MR 模板覆盖鲁棒性/公平性/非确定性/效率并配攻击成功率 + 语义相似度指标；LLMORPH 执行超 50 万个 MG）；多模态（MTEE 文本+视觉蕴含统一 MT 并解释失败；VRPTEST 视觉指代 prompt 变换评测大多模态模型）；代码与数学（Turbulence 的 question neighborhoods；Sarker 等数学公式语法鲁棒性 + 公式化简缓解）；复杂系统（Mortar 多轮对话级变换（轮次打乱/删减/重复）且不依赖 LLM-as-judge；ReliabilityBench 三维可靠性面（一致性/鲁棒性/容错）+ 基于 end-state 等价的 action MR；NoD-DGMT 在 AI2-THOR 评 embodied agent 决策最优性而非仅任务成功）；垂域（中国工业 8 场景本地 LLM 评估；ICD 编码临床常见错误的参数化 MR；60 个多模态 LLM × 30 套 ISTQB 认证考试的软件测试知识评估）。
- **Understand——揭示内部机制与失败模式（§4.1.4）**：压缩模型保真（MetaCompress 发现蒸馏学生模型在对抗攻击下性能降幅可比教师**高达 285%**；MORPH 把 MR 鲁棒性加入多多目标蒸馏，产出比 SOTA 基线**鲁棒 47%** 的压缩模型）；失败边界与数据记忆（Hyun 等多目标搜索选出 silver bullet 变换；MT-LAPR 揭示 LLM 鲁棒性与代码可读性强正相关，并用 MT 动态生成的无泄漏数据集揭露训练记忆造成的虚高；De Koning 等发现变换下性能退化与低 NLL 相关，可区分真实修复能力与基准污染）。

### 2.5 MT for LLMs：应用视角（§4.2 Application Perspective）

- **事实幻觉检测（§4.2.1）**：主路线是语义一致性 MR（同义改写/多路推理下事实应稳定）；DrHall 设计 6 个基础 + 3 个复合 MR（思维链、多语投票、外部知识增强）主动诱发不一致；结构化生成上 MRSQLGen 查"可执行但偏离用户意图"的 SQL 幻觉；RAG 上 MetaRAG 做 reference-free 黑盒检测；DomainProbe 让 LLM 解释主题关键词、词-解释对不一致即标记不可信。**核心局限**：对"一致性幻觉"（各语言变体下自信重复同一错误）会产生假阴性。
- **公平性与偏见（§4.2.2）**：框架类（Meta-Fair = MUSE 生成 + GENIE 执行 + GUARD-ME 的 LLM 裁判；GenFair 用等价类划分/变异/边界值生成多样且交叉性输入；CAFFE 形式化公平测试用例组件；Reeq 借"反思平衡"哲学方法做伦理一致性测试与缓解）；MR 优先化可提升检错率并缩短首失败时间（Giramata 等）；交叉偏见（tone 分析比情感分析更敏感）；检测之外还可用于缓解——用 MR 生成偏见样本微调可显著提升偏见韧性（Salimian 等）；RAG 中检索组件自身可放大偏见——微小人口统计变化可破坏**多达 1/3 的 MR**（Oliveira 等）；延伸到 ICD 编码、Text-to-Image（地域名实体替换）。
- **鲁棒性与一致性（§4.2.3）**：PromptOps 9 类扰动（错字注入、同义替换、时态上下文插入、共指改写等），在 BoolQ 上发现 GPT-4o/Gemini-2.0-Flash 在部分设置下答案翻转**超 30%**；METAL 的等价/差异模板；LLMORPH 36 个 MR 的自动测试；ISTQB 考题变换区分概念理解与题面记忆；VRPTEST 视觉指代敏感性；ICD 临床注错模拟；代码模型方面系统综述（Asgari 等）确认 MT 已成深度代码模型稳定性评测的主导范式，但集中在 Java/Python/C-C++；Turbulence 揭示 question neighborhood 内的泛化缺口；MeTMaP 查 RAG 虚假向量匹配；KonTest 用知识图谱构造等价查询揭露世界知识不一致。
- **代码生成与修复（§4.2.4）**：APR 与缺陷检测（MT-LAPR 在 token/语句/块三级定义 9 个 MR；CodeCocoon 用 LLM 同义生成造缺陷变体抗泄漏；De Koning 等在 Defects4J 与 GitBug-Java 上用变换下性能退化诊断记忆驱动成功）；**警示**：许多公开的"语义保持"变换实际改变了语义，复用需谨慎（Hort 等）；补全与生成（CCTEST 程序结构一致变换修复补全输出；SQLhd 与 MRSQLGen 的 Text-to-SQL；CodeMetaAgent 把 MR 作为主动语义算子嵌入综合管线）；理解与摘要（Metamon 对比文档意图与代码行为；Khatib 等注入行为变更检查摘要是否随之更新，在 9,482 个文档-测试对上达 precision 0.72 / recall 0.48）；安全与保真（CHTs 检测代码变换中的有害内容生成；MetaCompress 评蒸馏保真）。
- **复杂系统：Agent 与对话（§4.2.5）**：多轮对话（Mortar 对话级变换；Sensei 会话档案驱动的用户模拟器；CQ2A 上下文覆盖问题生成；MTF 开源框架验证含虚拟伴侣 Agent 的 LLM 服务）；自主 Agent（ReliabilityBench 的 action MR 以**终态等价**而非文本相似判定；NoD-DGMT 以更低成本轨迹检出非最优决策；AgentAssay 用 PASS/FAIL/INCONCLUSIVE 三值概率语义 + 行为指纹应对非确定性；ASSURE 测 AI 浏览器扩展的安全边界 MR）；领域多 Agent 系统（TEMPLEs 教学评估的多人格评审 + MT 验证 Agent；AutoMT 从 Gherkin 交通规则抽 MR 的三 Agent 架构；SYNEDRION 税务软件的 MetamorphicAgent 生成高阶 MR 检查多纳税人档位变化率）。

### 2.6 LLMs for MT：自动化测试生命周期（§5 LLMs for MT）

- **MR 自动发现（§5.1）**：从非形式文档/需求到形式规约（Tsigkanos 等从科学软件手册发现 I/O 变量；Shin 等让 LLM 把需求译为自然语言 MR 再转 DSL——SMRL；税务法条经 few-shot ICL 转逻辑化蜕变规约）；从既有测试与源码挖掘（MR-Scout 从开源测试断言中提炼隐式 MR 合成参数化可复用 MR；MR-Coupler 用签名/调用/状态耦合找方法对再让 LLM 推 MR 并生成具体测试；AR 领域把"MR 适用性判定"作为子问题，多 Agent 辩论提升稳定性）；实证规模（Luu 等 ChatGPT 为 9 个系统生成 MR 的经验研究——能提出正确 MR 但大量候选含糊/无据/错误，需专家校验；Zhang 等在 37 个系统上评估 GPT-3.5/GPT-4——能产出大量合法正确 MR 甚至人遗漏的额外 MR，但仍有不可忽视的"貌似有理实则有错"候选）；约束生成的改进（SVPrompt-MR 自验证提示策略在热工安全程序上**覆盖全部 44 条专家 MR 并新发现 24 条**；CARLA 混合框架把预定义 MR 模式嵌入 prompt 缩小搜索空间）。
- **输入变换与测试实现（§5.2）**：从样例/规约合成可执行变换代码（MR-Adopt 把输入关系推导当 programming by example，从单个种子对合成泛化 Java 变换函数并用数据流分析精化，**恢复开源项目中 >72% 不完整 MR** 的可执行变换；MR-Coupler 端到端生成完整蜕变测试工件；Shin 等把文本 MR 经 few-shot 译为可执行 DSL）；把 LLM 本身当语义变换引擎（LLMORPH 区分函数级简单变换与 LLM 级复杂变换，用 Hermes-2 few-shot 实现风格/方言改写；StaAgent 用 LLM 生成保持行为但含死存储/不可达分支的 Java 变异体测静态分析器）；可复用模式库与跨域扩展（MTF 的多语言输入/输出模式库；CodeMetaAgent 的逻辑反转/过程分解算子；DILLEMA 扩到视觉 MT（字幕 + 扩散模型生成保持类别的图像）；OBsmith 生成 JavaScript 程序 sketch 测混淆器；QTRAN 两阶段（RAG 翻译方言 + 微调 LLM 施变换）把 MT 扩到 MySQL→PostgreSQL 等 SQL 方言；Hazott 等桥接几何性质与 C++ 固件调用）。
- **Agentic 与闭环测试（§5.3）**：闭环工作流（Cañizares 等的 evaluator-fixer 管线 + Gotten MT 框架，在数据中心/自动驾驶/自动机三域生成语义有效 MR 并用推理型 LLM 达**>99% follow-up 正确率**；Sudheerbabu 等在线生成反馈环优化变换超参）；多 Agent 编排（AutoMT 的 M-Agent/T-Agent/F-Agent 三角色；SYNEDRION 的 MetamorphicAgent 持续生成高阶蜕变反例驱动 coder 迭代；StaAgent 分种子生成/代码验证/变异生成/分析器评估四个 Agent）；**MR 作为自纠正的语义算子**（CodeMetaAgent 借 MR 变换探索多条推理路径、分析解的一致性并在无外部 ground truth 下自我纠错；OBsmith 把失败分析反馈为新 sketch 综合知识）；伦理对齐（TEMPLEs 迭代多 Agent 教学评估；Reeq 用外部 LLM 批评者驱动反思均衡直至一致）。

### 2.7 挑战与未来方向（§6 Challenges & Future Directions）

- **MR 的有效性与可信性（§6.1）**：LLM 开放任务下 MR 定义远难于传统数值软件——太弱漏报、太强误报；LLM 生成 MR 使传统"自动化瓶颈"部分转为"**有效性瓶颈**"。建议：人在环校验、基于约束的 MR 检查、多模型交叉验证、MR 置信度估计；并发展"何为好 MR"的理论（有效性/必要性/判别力/语义稳定性/覆盖/变换多样性/成本）与 MR 质量基准。
- **数据泄漏与基准污染（§6.2）**：源输入或 follow-up 过接近记忆样本时 MT 也会失效；同族模型互测会共享归纳偏置。对策：从抽象 schema 动态生成 MG 的防泄漏基准、变换多样性控制、基准来源分析、跨模型族评测、持续刷新。
- **非确定性与可复现性（§6.3）**：MR 违例可能是缺陷也可能是随机波动；现有研究多依赖一次性执行。倡议**统计化 MT**：同 MG 重复执行、分布级比较、违例显著性检验、跨温度/prompt/检索配置的鲁棒性剖面、记录模型版本与解码参数的可复现协议。
- **扩展到复杂 LLM 系统（§6.4）**：现有研究多针对单轮 prompt；真实系统是 RAG/工具调用/工作流/记忆/多 Agent 的复合体，失败源于组件交互。方向：面向工作流-轨迹-记忆-环境变迁的状态感知 MR、把系统级 MR 分解到检索/推理/工具/记忆/执行的组合式 MT、交互级覆盖指标、运行时在线 MT、涌现群体行为测试；Agent 的正确性单元应是终态/成本/安全约束/轨迹一致性而非表层文本相似。
- **成本、效率与工业可用性（§6.5）**：前沿模型多次调用 + 重复执行 + 人工复核使大规模部署昂贵。策略：识别高检错回报的 MR 类、MG 优先化、小本地模型替换专有模型、缓存/批处理/近似语义检查、面向开发者与审计者的可行动报告；还需可复用工具链、基准仓库与平台集成。
- **标准化分类法、数据集与指标（§6.6）**：术语、MR 定义、指标、失败概念不一致，模型版本/解码设置等报告维度不统一，阻碍复现。呼吁共享分类法、经验证的 MR 公共仓库（含假设与适用任务元数据）、实验报告标准、MR 质量/检错/假阳率/成本/复现指标、跨文本-代码-多模态-RAG-工具-Agent 的共享基准套件。

### 2.8 结论（§7 Conclusion）

- MT 缓解 oracle 问题、以关系式行为验证适配开放式概率系统；LLM 反向提升 MT 的自动化/可扩展性/可及性（MR 发现、变换、实现、agentic 工作流）——LLM 既是被测对象也是测试生命周期的智能助手。领域仍处形成期：需更严格的 MR 校验与排序、混合 oracle（符号规则 + 检索证据 + 统计分析 + 模型判断）、防污染基准、重复执行与分布感知协议、组合式 MT，以及实用工具链、公共 MR 仓库与共享评测标准，才能从原型走向成熟科学与工业实践（§7）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 综述规模 | 93 篇初级研究（135 篇详评 → 76 篇入选 + 17 篇滚雪球） | §3.2 Study Selection Criteria |
| 方向分布（非互斥） | MT for LLMs 70 篇 vs LLMs for MT 34 篇 | §3.4 Proposed Taxonomy |
| MT for LLMs 内部视角 | 功能视角 43 篇 / 应用视角 63 篇 | §3.4 Proposed Taxonomy |
| 检索窗口 | 截至 2026-04-30，入选研究跨 2019-01 至 2026-04 | §3.1 Search Strategy and Data Sources |
| 蒸馏学生模型行为保真缺口（MetaCompress） | 对抗攻击下学生模型性能降幅比教师高达 285% | §4.1.4 Understand |
| MR 引导蒸馏（MORPH） vs SOTA 基线 | 压缩模型鲁棒性提升 47% | §4.1.4 Understand |
| 变换函数自动恢复（MR-Adopt） | 开源项目不完整 MR 中 >72% 恢复出可执行变换 | §5.2 Input Transformation & Test Implementation |
| LLM 生成 MR 覆盖（SVPrompt-MR） | 覆盖全部 44 条专家 MR，另新发现 24 条 | §5.1 Automated MR Discovery |
| follow-up 正确率（Cañizares 等，推理型 LLM） | >99%（数据中心/自动驾驶/自动机三域） | §5.3 Agentic & Closed-Loop Testing |
| 商用 LLM 鲁棒性（PromptOps，BoolQ） | GPT-4o/Gemini-2.0-Flash 部分设置下答案翻转超 30% | §4.2.3 Robustness & Consistency |
| RAG 公平性（Oliveira 等） | 微小人口统计变化可破坏多达 1/3 的 MR | §4.2.2 Fairness & Bias Evaluation |
| 代码摘要 MT（Khatib 等） | 9,482 个文档-测试对上 precision 0.72 / recall 0.48 | §4.2.4 Code Generation & Repair |
| ISTQB 知识评估（Haq & Cabot） | 60 个多模态 LLM × 30 套 ISTQB 认证考试 | §4.1.3 Assess |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2605.13898 |
| 本目录关联 | 05（Cho 等 MR 关系库，191 MR / 24 任务）；06（LLMORPH 工具，本综述 §4.1.1/§4.2.3/§5.2 多处引用其 36 MR、>50 万 MG） |
| 综述内代表工具（MT for LLMs） | CheckList；METAL；LLMORPH；PromptOps；Drowzee / Drowzee-Temporal；MetaRAG；DrHall；MetaQA；Mortar；ReliabilityBench；NoD-DGMT；MTEE；VRPTEST；Turbulence；MT-LAPR；SQLhd；MRSQLGen；CCTEST；MeTMaP；CHIME；Sensei；CQ2A；AgentAssay；ASSURE（§4） |
| 综述内代表工具（LLMs for MT） | MR-Scout；MR-Adopt；MR-Coupler；SVPrompt-MR；StaAgent；CodeMetaAgent；OBsmith；QTRAN；AutoMT；SYNEDRION；DILLEMA；MTF；Gotten MT workflow（§5） |
| 方法论依据 | Kitchenham 系统综述指南；Chen 等 1998 MT 原始论文；Chen 等 2018 / Segura 等 2016 / Li 等 2025 MT 综述（§2、§3） |

## 5. 一句话索引（给 Agent 用）

> MT×LLM 双向赋能系统综述（arXiv 2605.13898）：系统综述 93 篇初级研究，分两方向——MT for LLMs（70 篇：Verify/Validate/Assess/Understand 四功能 × 幻觉/公平/鲁棒性/代码/RAG/对话/Agent 五类应用）与 LLMs for MT（34 篇：MR 发现、输入变换、agentic 闭环）。代表数字：MR-Adopt 恢复 >72% 不完整 MR；SVPrompt-MR 覆盖 44/44 专家 MR 并新增 24 条；蒸馏学生模型对抗降幅达 285%，MORPH 鲁棒性 +47%；PromptOps 下 GPT-4o 答案翻转可超 30%。核心警告：LLM 生成 MR 把自动化瓶颈转为有效性瓶颈，需防泄漏、统计化与标准化。
