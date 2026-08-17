---
title: "Large Language Models as Software Components: A Taxonomy for LLM-Integrated Applications"
source_pdf: "01-Weber-LLMs_as_Software_Components_v1.pdf"
arxiv_id: "2406.10300"
arxiv_version: "v1"
authors:
  - "Irene Weber"
year: 2024
venue: "arXiv (MSR 2025)"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：LLM 作为软件构件——集成应用架构分类学

## 1. 适用场景

- 当你要**设计或评审把 LLM 当软件组件嵌入产品的系统**（copilot、智能助手、LLM 驱动的控制/规划等），需要一套现成的架构描述维度与统一术语时，读这篇。
- 当你的应用里有**多个 LLM 调用点**（planner / parser / generator / explainer 等），需要按 "LLM component" 逐个拆解、再组合成整体架构描述时，读这篇。
- 当你要做**跨产品/跨文献的 LLM 集成方式横向比较**，或系统枚举 prompt 组装、输出格式与消费方式、技能选型等设计选项空间时，读这篇。
- 当你研究 **prompt 作为软件资产的管理、LLM 应用的测试/监控、LMaaS vs 本地部署**等工程挑战，需要一手实证观察（含 ExcelCopilot 反推架构、Honeycomb 工程博客经验）时，读这篇。

> 锚点：Abstract; §1 Introduction; §4.2 Sample of LLM-integrated applications; §6 Discussion; §7 Conclusion。

## 2. 主要观点与方案

### 2.1 研究问题与定位（Abstract; §1 Introduction; §2.2 Definitions）

- 与主流两条研究线相区分：SE 研究多把 LLM 当**开发工具**（LLM for SE），agent 研究把 LLM 当**自主 agent**；本文取第三视角——LLM 作为**软件构件**（software component）嵌入系统，而 LLM-integrated application engineering 是术语/概念/方法尚待建立的新兴学科。
- 核心定义（§2.2）：**LLM invocation**＝一次"输入-处理-输出"序列；**LLM-integrated application**＝由软件生成 prompt 并处理其输出的系统；**LLM component**＝完成特定任务（构造 prompt + 处理输出）的软件构件。一个应用可含多个 LLM component，**应用 = 其 LLM component 的组合**——这是理解其架构的关键分解方式。

### 2.2 分类学构建方法（§4 Methods; §4.1 Development）

- 遵循 Nickerson 等人的分类学开发指南与 Design Science Research 方法；最初从会话助手标准架构（"chatbots with tools"）推导失败，改以经典三层架构为基础，经 **5 轮主要精化循环**（empirical-to-conceptual 与 conceptual-to-empirical 交替），直到用**全新评估样本**检验时维度与特征保持稳定才宣告完成。
- 可视化（§4.1）：评估过形态学箱（morphological boxes）但占地过大、难以把多组件应用作为整体一览，故改用 **feature vector** 表示——特征值取单字母码、每个 LLM component 一行、同应用的组件分组排列成表。
- 样本筛选标准（§4.1）：面向真实使用而非纯研究原型；架构（尤其 LLM 集成）描述足够细致；覆盖多样架构；聚焦工业/技术域（刻意避开法律/医学/营销/HR/教育等已被充分讨论的领域）。

### 2.3 样本：11 个应用、21 个 LLM 组件（§4.2; Table 1）

- **开发集 6 应用 11 组件**：Honeycomb（QueryAssistant：自然语言→查询语言）；LowCode（Planning 把粗任务设计成可视化流程图再转写回自然语言 prompt + Executing 多轮对话执行）；MyCrunchGpt（DesignAssistant / SettingsEditor / DomainExpert，翼型设计专家系统，LLM 作智能参数解析器）；MatrixProduction（Manager 生成排产计划 + Operator 为自动化模块编程，用 Industry 4.0 Asset Administration Shell 自动生成 few-shot prompt）；WorkplaceRobot（以 Python 编码任务形式做机器人任务规划，执行无成功反馈）；AutoDroid（TaskExecutor 按动态 GUI 状态迭代规划手机操作，不可逆操作需用户确认；两个 MemoryGenerator 离线解析 UI Transition Graph 构建知识库）。
- **评估集 5 应用 10 组件**：ProgPrompt（ActionPlanning 生成带 assert 前置检查的 Python 机器人脚本 + ScenarioFeedback 在仿真中判定断言 True/False）；FactoryAssistants（FAQ 域知识直接进 prompt 的产线排障顾问）；SgpTod（DstPrompter 做 NLU 填充 belief state 并输出 SQL + PolicyPrompter 同时兼做 DM 与 NLG）；TruckPlatoon（算法控制环的测量值→自然语言性能报告）；ExcelCopilot（从录屏与开发者报告**反推**出 intent detection–skill routing 架构：ActionExecutor\* / Advisor / IntentDetector / Explainer；多步命令常被拒绝，提示其缺少规划组件）。

### 2.4 分类学本体：5 元维度 × 13 维度（§5; Table 2; §5.2.1–§5.2.5）

- **Invocation（§5.2.1）**：Interaction（App 应用自动调用，用户不直接对话 / Command 用户单条自然语言命令 / Dialog 多轮对话）；Frequency（Single 单次调用即得结果 / Iterative 反复调用）。
- **Function（§5.2.2）**：源自经典三层架构——UI（none / Input / Output / Both，LLM 是否实现界面功能）；Logic（cAlculate 输出仅作数据处理 vs Control 输出驱动应用控制流，二者互斥）；Data（none / Read / Write / Both，是否读写持久数据）。
- **Prompt（§5.2.3）**：统一术语将 prompt 拆为 **Instruction（开发期定义、全生命周期静态）/ State（每次调用动态生成的情境部分：对话史、知识库摘录、环境描述）/ Task（本次调用要解决的任务）** 三部分，可任意顺序、可缺省；各部分来源取值 none / User / LLM / Program；另设 Prompt Check（调用前是否有检查/修改机制，同四种来源）。Instruction 恒为 Program、无区分度，仅为完整性保留。Table 3 对照了 10 篇文献中 prompt 部件命名的混乱现状。
- **Skills（§5.2.4）**：非互斥六特征 reWrite（改写/转换）/ Create（生成新内容）/ conVerse（目的性对话）/ Inform（依赖训练所得知识）/ Reason（推理）/ Plan（规划）；Plan 隐含 Reason（只标 Plan 不再标 Reason）；所有组件必备的"理解"能力因无区分度不单列。
- **Output（§5.2.5）**：Format（FreeText / Item / Code / Structure，非互斥）；Revision（none / User / LLM / Program，指校验修正而非仅解析转换）；Consumer（User / LLM / Program / Engine，互斥，指**最终**消费者而非中间解析器）。
- 互斥性策略（§5.1）：技术集成相关维度强制互斥、每个组件取**主导特征**；Skills 与 Output Format 允许多特征并存（Table 2）。

### 2.5 评估（§5.3 Evaluation）

- 按六项公认质量准则评估：comprehensiveness（覆盖全部实例，含构建时未见的评估集）；robustness（**全部示例实例的分类结果彼此唯一**）；conciseness（部分让步：为展示设计空间保留无人占用的特征，如 Data 的 Write/Both、Prompt Check 与 Output Revision 的 LLM 特征）；mutual exclusiveness（有意对 Skills/Format 放宽）；explanatory power（元维度分层 + 逐特征配真实示例）；extensibility（扁平结构易于增补维度）。
- 承认 feature vector 表示的代价：需对照图例、互斥维度的未选用特征不可见（设计空间未完全展开）。

### 2.6 讨论与关键洞察（§6 Discussion; §6.1 Applicability and ease of use; §6.2 Usefulness）

- 提出 **overloaded LLM component** 概念（类比函数重载，如 SgpTod PolicyPrompter 一次输出同时产生类别动作与聊天回复）；三种处理方式（放宽互斥/仅标 overloaded/按主导用途归类）中本文采用第三种。
- 关键洞察：分析 LLM-integrated application 应**从识别并逐个描述其 LLM component 开始**，而非把应用当整体分析；组件间 prompt chaining（一组件输出进另一组件 prompt）在 Prompt 维度的 LLM 特征中体现——同为 LLM 生成，AutoDroid TaskExecutor 与 LowCode Executing 体现在 State（预备阶段批量生成），MatrixProduction Operator 体现在 Task（临近使用即时生成）。
- 作为**分析透镜**可快速聚焦 LLM 集成本身、抽象掉领域细节；为跨领域研究者与从业者提供统一描述框架，便于比较与共享开发知识。

### 2.7 局限、实践挑战与未来工作（§7 Conclusion）

- 局限：评估由分类学开发者本人执行（与近期同类工作一致，用新样本评估可部分强化效度）；样本用于枚举设计选项而非定量分析，个别实例（ExcelCopilot）信息不全需推测性解读。
- 实践挑战：prompt 需作为软件资产管理；**LLM 调用成本使常规大规模自动化测试不可行**；prompt 微小变化导致输出差异（非确定性）与自动处理要求格式严格遵从之间存在张力；LMaaS 的隐私 / 可靠性 / 可用性 / 成本 / 时延问题（Table 4：样本以 GPT-3.5 系为主；Honeycomb 因 GPT-4 太慢弃用；CODEX 表现更好但访问受限）。
- 未来工作：prompt 更细粒度部件拆分以便比较实验；用真实项目数据补充 format-following / instruction-following 的合成基准结果；研究 LLM 特性与任务的匹配（如意图检测的最优模型规模）；扩展应用级维度与语言模型特征维度；作为培训材料的设计选项框架。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 分类学规模 | 13 个维度、5 个元维度（Invocation / Function / Prompt / Skills / Output） | §5; Table 2 |
| 样本规模 | 开发集 6 应用 11 个 LLM 组件 + 评估集 5 应用 10 个 LLM 组件（合计 11 应用 21 组件） | §4.1 Development; Table 1 |
| 构建收敛 | 5 轮主要精化循环后，维度与特征在新样本上保持稳定 | §4.1 Development |
| 稳健性 | 全部示例实例获得唯一分类（无两个组件特征向量相同） | §5.3 Evaluation; Figure 1 |
| 互斥性设计 | 13 维中 11 维强制互斥，仅 Skills 与 Output Format 允许多特征并存 | Table 2; §5.3 Evaluation |
| 样本特征分布 | Interaction：App=8 / Command=9 / Dialog=4；Frequency：Single=16 / Iterative=5（21 组件合计） | Figure 2 |
| Prompt 结构 | 3 个部件（Instruction / State / Task）× 4 种来源（none / User / LLM / Program）；Instruction 恒为 Program | §5.2.3; Table 3 |
| Skills 维度 | 6 个非互斥特征：reWrite / Create / conVerse / Inform / Reason / Plan（Plan 隐含 Reason） | §5.2.4 |
| 可视化效果 | feature vector 表示比形态学箱 / 雷达图更紧凑，多组件应用可整体一览 | §4.1 Development; §7 Conclusion |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2406.10300（v1，2024-06-13，cs.SE） |
| 样本系统·代码 | LowCodeLLM: https://github.com/chenfei-wu/TaskMatrix/tree/main/LowCodeLLM；AutoDroid: https://github.com/MobileLLM/AutoDroid |
| 样本系统·论文 | Low-code LLM (arXiv:2304.08103)；AutoDroid (arXiv:2308.15272)；SGP-TOD (arXiv:2305.09067)；ProgPrompt (ICRA 2023)；MyCrunchGpt (J. Mach. Learn. Model. Comput. 2023)；MatrixProduction (IEEE ETFA 2023)；TruckPlatoon (Sensors 2023) |
| 工程一手经验 | Honeycomb 两篇工程博客（Phillip Carter，2023）；Parnin et al. "Building Your Own Product Copilot" (arXiv:2312.14231)；Microsoft Copilot in Excel 官方概述/录屏 |
| 关联本地摘要 | 本目录 02（Promptware 工程）、08（DbC 协议层）；`research/agent-software-design/materials/软件工程原理与LLM系统.md` §3.1 差异表 |

## 5. 一句话索引（给 Agent 用）

> 把 LLM 当"软件构件"嵌入应用时读这篇：Weber 分析 11 个真实应用（Honeycomb / AutoDroid / ExcelCopilot 等）拆解出的 21 个 LLM component，归纳出 5 元维度 × 13 维分类学（Invocation / Function / Prompt / Skills / Output，含 Instruction-State-Task 的 prompt 三部件拆分与 reWrite-Create-conVerse-Inform-Reason-Plan 六技能），并用 feature vector 紧凑可视化；全部样本获得唯一分类。核心结论：LLM-integrated 应用必须按 LLM component 逐个拆解才能看清架构——LLM 构件的调用方式、prompt 来源、输出消费与修订均可在此框架下系统描述与比较。
