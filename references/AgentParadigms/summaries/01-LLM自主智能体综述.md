---
title: "A Survey on Large Language Model based Autonomous Agents"
source_pdf: "01-Wang-Survey_LLM_Autonomous_Agents_v7.pdf"
arxiv_id: "2308.11432"
arxiv_version: "v7"
authors:
  - "Lei Wang"
  - "Chen Ma"
  - "Xueyang Feng"
  - "Zeyu Zhang"
  - "Hao Yang"
  - "Jingsen Zhang"
year: 2023
venue: "Frontiers of Computer Science"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：LLM 自主智能体综述（Wang 四模块框架）

## 1. 适用场景

- 要**从零构建单个 LLM agent**、需要一张"部件选型清单"时读这篇：按 Profiling/Memory/Planning/Action 四槽位做需求分析（简单任务无需上齐四模块），再到各小节找代表实现与原始文献入口。
- 为自建 agent 框架设计**记忆子系统**（结构/格式/操作三级分类 + "新近性—相关性—重要性"加权读取公式）或**规划子系统**（有无反馈二分、单/多路径推理、外部规划器）时，用作二级分类与方案对照表。
- 决定 agent **能力获取路线**（微调三类数据集 vs 提示工程 vs 机制工程）并评估各自适用边界（开源/闭源模型、上下文窗口限制）时。
- 为 agent 项目**选型评测方案**时：主观（人工标注/图灵测试/LLM-as-judge）与客观（指标/协议/基准三层）给出完整清单与 29 个评估工作的对照表。
- 想**快速摸清 2021–2023 年 LLM agent 研究全景**（应用领域分布、开源库生态、六大开放挑战）时作总览入口。

> 锚点：§1 Introduction; §2 LLM-based Autonomous Agent Construction; §3 LLM-based Autonomous Agent Application; §4 LLM-based Autonomous Agent Evaluation; §6 Challenges。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- 传统 agent 基于"简单启发式策略 + 孤立受限环境"训练，与人类从广泛环境学习的过程差距大，难以在开放域做出类人决策；LLM 以海量网络知识 + 大参数量展现出类人智能潜力，催生"以 LLM 为中央控制器构建自主 agent"的研究浪潮（Fig 1 给出 2021-01 至 2023-08 累计论文增长曲线，含 General/Tool/Simulation/Embodied/Game/Web/Assistant Agent 七类着色）。
- 相比强化学习，LLM agent 具备更全面的内在世界知识（无需领域数据训练即可行动）、自然语言人机接口（更灵活、可解释）。
- 综述沿三条主线组织：**构建（§2）→ 应用（§3）→ 评估（§4）**，最后给出挑战（§6）；作者自比：架构设计≈定义网络结构，能力获取≈学习网络参数。

### 2.2 统一架构：四模块框架（§2.1 Agent Architecture Design）

- **Profiling 画像模块（§2.1.1）**：确定 agent 角色，写入 prompt 影响行为。画像内容三维：人口统计信息、性格（心理学）信息、社会关系信息，按应用场景取舍（如认知过程研究重心理学信息）。三种生成策略：① Handcrafting 手工指定（Generative Agent、MetaGPT、ChatDev、PTLLM 用 IPIP-NEO/BBI 人格量表）——灵活但大规模时费力；② LLM-generation（RecAgent 以少量种子画像让 ChatGPT 批量生成）——省力但控制精度差；③ Dataset alignment 真实数据集对齐（以 ANES 人口学背景画像 GPT-3 并与真人结果对照）——最贴近真实人群。作者 Remark：三者可组合（如用真实数据画像现存角色 + 手工指定未来新兴角色以预测社会发展）。
- **Memory 记忆模块（§2.1.2）**：三个正交视角。① 结构：Unified Memory（仅短时记忆，即上下文窗口内 prompt，如 RLP、SayPlan、CALYPSO、DEPS）实现简单但受窗口限制；Hybrid Memory（短时 + 长时外置向量库，如 Generative Agent、AgentSims、GITM、Reflexion、SCM、SimplyRetrieve、MemorySandbox）利于长程推理与经验积累；作者注："仅长时记忆"在文献中几乎不存在，因 agent 处于连续动态环境、相邻动作强相关。② 格式：自然语言（Reflexion、Voyager）、Embeddings（MemoryBank 双塔稠密检索）、数据库（ChatDB 用 SQL 增删改记忆）、结构化列表（GITM 层级树、RET-LLM 三元组）；格式可混用（GITM 键为 embedding、值为自然语言）。③ 操作：Memory Reading 以 `m* = argmax(α·s_rec + β·s_rel + γ·s_imp)` 加权新近性/相关性/重要性（Generative Agent 取 α=β=γ=1.0，GITM/Voyager 等仅取相关性）；Memory Writing 处理重复（GITM 同一子目标的 N=5 条成功序列凝练为一条方案）与溢出（RET-LLM FIFO 覆写、ChatDB 按指令删除）；Memory Reflection 生成高层洞察（Generative Agent 由 3 个关键问题检索记忆再生成 5 条洞察，可层级化；ExpeL 对比成败轨迹归纳经验）。
- **Planning 规划模块（§2.1.3）**：按有无反馈二分。**无反馈**：① 单路径推理（CoT、Zero-shot-CoT"think step by step"、RePrompting 前置条件检查、ReWOO 计划与观察解耦、HuggingGPT 子目标分解、SWIFTSAGE 双过程理论）；② 多路径推理（CoT-SC 投票、ToT 树状思考 + BFS/DFS、RecMind 自激励、GoT 图结构、AoT 算法示例、RAP 用 MCTS 世界模型）；③ 外部规划器（LLM+P 与 LLM-DP 转 PDDL 后调规划器、CO-LLM 高层计划 + 低层启发式执行器）。**有反馈**：① 环境反馈（ReAct 的 thought-act-observation 三元组、Voyager 的执行进度/报错/自验证、SayPlan 场景图仿真校验、DEPS 的失败原因解释、LLMPlanner 接地重规划、Inner Monologue 的三种反馈）；② 人类反馈（Inner Monologue 主动向人索取场景描述，可与环境反馈组合，对齐人类价值并缓解幻觉）；③ 模型反馈（Self-Refine 输出-反馈-精炼迭代、SelfCheck 分步自查、InterAct 辅助模型当 checker/sorter、ChatCoT 评估模块、Reflexion 用 LLM 生成详细语言反馈而非标量）。Remark：无反馈实现简单、适合少步推理；有反馈设计更讲究但能处理长程复杂任务。
- **Action 行动模块（§2.1.4）**：四维分类——① 目标：任务完成 / 通信（ChatDev 多 agent 对话、Inner Monologue 人机交互）/ 环境探索（Voyager 试错探索新技能）；② 产生方式：记忆回想触发（Generative Agent 检索记忆流、GITM 查询过往成功经验）vs 计划跟随（DEPS、GITM 按 sub-goal 顺序执行）；③ 空间：外部工具（API：HuggingGPT/WebGPT/Gorilla/ToolFormer/API-Bank/ToolLLaMA/RestGPT/TaskMatrix.AI；数据库与知识库：ChatDB/MRKL/OpenAGI；外部模型：ViperGPT 生成代码执行、ChemCrow 17 个专家模型、MM-REACT 多模态）vs LLM 内部知识（规划能力/对话能力/常识理解能力）；④ 影响：改变环境（GITM/Voyager 采集资源）、改变内部状态（更新记忆/计划）、触发新行动（Voyager 集齐资源触发建造）。

### 2.3 能力获取（§2.2 Agent Capability Acquisition）

- 架构是"硬件"，还需"软件"（任务特定技能）。Fig 4 概括范式迁移：机器学习时代=参数学习 → LLM 时代=参数学习 + 提示工程 → agent 时代=再加机制工程。
- **有微调**（仅适用开源 LLM）：① 人工标注数据集（CoH 将人类偏好转为自然语言比较信息、RET-LLM 三元组-自然语言对、WebShop 1.18M 商品 + 13 名工人行为数据、EduChat 教育场景）；② LLM 生成数据集（ToolBench 收集 RapidAPI Hub 16,464 个 API/49 类让 ChatGPT 生成指令后微调 LLaMA、社交沙盒 agent 交互数据）；③ 真实世界数据集（MIND2WEB 从 137 个真实网站/31 领域收集 2,000+ 开放式任务、SQL-PaLM 用 Spider/BIRD 微调 PaLM-2）。
- **无微调**（开源闭源皆可）：① 提示工程（CoT/CoT-SC/ToT 少样例推理、RLP 心智状态提示、Retroformer 失败反思写入 prompt 并用 RL 迭代）；② 机制工程：试错（RAH 预测-对比-修正、DEPS 失败解释、RoCo 计划验证不通过则带反馈重启对话、PREFER 详细反馈）；众包（多 agent 辩论直到共识）；经验积累（GITM 成功动作入库、Voyager 技能库、AppAgent 自主探索 + 人类演示构建知识库、MemPrompt 用户自然语言反馈入库）；自我驱动演化（LMA3 自设目标 + 奖励反馈、SALLMMS、CLMTWA 师生模型心智理论、NLSOM 动态调整角色任务）。
- Remark（§2.2）：微调可注入大量任务知识但仅限开源模型；无微调受上下文窗口限制、提示与机制设计空间过大难以寻优。Table 1 将 31 个代表模型按六列标记对齐到本分类法。

### 2.4 应用全景（§3 LLM-based Autonomous Agent Application）

- **社会科学（§3.1）**：心理学（模拟实验对齐人类结果、发现 ChatGPT/GPT-4 存在"hyper-accuracy distortion"过于完美估计、120 条 Reddit 帖子的心理支持分析发现兼具帮助与有害内容风险）；政治与经济（意识形态检测、投票模式预测、经济行为模拟）；社会模拟（Social Simulacra、Generative Agents、AgentSims、SocialAI School、S3、CGMI 课堂模拟）；法学（Blind Judgement 多法官模拟 + 投票、ChatLaw 检索增强缓解幻觉）；科研助理。
- **自然科学（§3.2）**：文献与数据管理（ChatMOF 金属有机框架预测、ChemCrow 化学数据库验证）；实验助理（Boiko et al. 自动设计/规划/执行实验、ChemCrow 17 个工具含安全风险提示）；自然科学教育（Math Agents、CodeX 解大学数学题、CodeHelp、EduChat、FreeText 开放题自动评阅）。
- **工程（§3.3）**：CS 与软件工程（ChatDev 多角色对话走完软件开发全周期、MetaGPT 角色抽象、Self-collaboration 虚拟专家团队、LLIFT 静态分析辅助、ChatEDA、PentestGPT、D-Bot 用 ToT 思路做数据库异常诊断）；工业自动化（GPT4IA 数字孪生、IELLM 油气行业案例）；机器人与具身 AI（SayCan 551 个技能/7 技能族/17 物体、TidyBot、TaPA、DECKARD、RoCo）；开源库生态（LangChain、XLang、AutoGPT、WorkGPT、GPT-Engineer、DemoGPT、AGiXT、AgentVerse、GPT Researcher、BMTools）。Remark 警示两类风险：幻觉导致错误结论/实验失败/安全事故；恶意滥用（如研制化学武器）需人类对齐等安全措施。

### 2.5 评估策略（§4 LLM-based Autonomous Agent Evaluation）

- **主观评估（§4.1）**：人工标注（Generative Agent 请标注员答 25 个问题覆盖 5 个能力维度）与图灵测试（Argyle et al. 党派文本让人猜人/机）。缺陷：成本高、低效、人群偏差 → 趋势是 LLM 代理评估（ChemCrow 用 GPT 评任务完成与过程正确性、ChatEval 多 agent 辩论式评审）。
- **客观评估（§4.2）**：① 指标三类——任务成功（success rate、reward/score、coverage、accuracy/error rate）、人类相似度（coherent/fluent/对话相似度/人类接受率）、效率（开发成本、训练效率）；② 协议四种——真实世界仿真、社会评估、多任务评估、软件测试（测试覆盖率/缺陷检出率）；③ 基准——ALFWorld/IGLU/Minecraft/Tachikuma/AgentBench（首个跨多环境系统评估 LLM 作为 agent）/SocKET（58 任务 5 类社会信息）/AgentSims/ToolBench（16,464 RESTful API）/WebShop（1.18M 真实商品）/Mobile-Env/WebArena/GentBench/RocoBench（6 任务）/EmotionBench（400+ 情境 8 类负面情绪）/PEB（13 个渗透测试靶机）/ClemBench（5 个对话游戏）/E2E。Table 3 将 29 个评估工作对齐到该分类法；作者主张主客观结合。

### 2.6 相关综述定位与挑战（§5 Related Surveys; §6 Challenges）

- §5：既有综述覆盖 LLM 背景/下游应用/人类对齐/推理/ALM/评估等，但此前**没有专门针对 LLM-based Agents 的综述**；本文汇编 100 篇相关工作。
- §6 六大挑战：① 角色扮演能力（网络语料稀缺角色与新角色难模拟、缺乏自我意识；解法=收集真人数据微调或定制 prompt/架构，但保住常见角色性能是新难题）；② 广义人类对齐（模拟场景需诚实刻画含负面价值的多样人类，与统一对齐矛盾；方向是按用途"realign"）；③ Prompt 鲁棒性（模块间 prompt 相互影响、跨 LLM 不通用；统一鲁棒 prompt 框架未解）；④ 幻觉（代码生成场景已观察到，可借人机交互纠错反馈缓解）；⑤ 知识边界（LLM 知道太多，模拟普通用户时会用到用户不应知道的信息，需约束）；⑥ 效率（自回归推理慢，agent 每个动作要多次查询 LLM）。
- §7 结论：沿构建/应用/评估三方面建立分类法连接既有研究，挑战部分指引未来方向。

> 锚点：§2.1.1 Profiling Module; §2.1.2 Memory Module; §2.1.3 Planning Module; §2.1.4 Action Module; §2.2 Agent Capability Acquisition; §3.1 Social Science; §3.2 Natural Science; §3.3 Engineering; §4.1 Subjective Evaluation; §4.2 Objective Evaluation; §5 Related Surveys; §6.1–§6.6; §7 Conclusion。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 综述覆盖文献量 | 100 篇 LLM-based Agent 相关工作（构建/应用/评估三线） | §5 Related Surveys |
| 统一架构模块数 | 4 模块（Profiling/Memory/Planning/Action），Table 1 将 31 个代表模型对齐到分类法 | §2.1 Agent Architecture Design; Table 1 |
| 记忆读取统一公式 | m\*=argmax(α·s_rec+β·s_rel+γ·s_imp)；Generative Agent 取 α=β=γ=1.0，GITM/Voyager 等仅用相关性 | §2.1.2 Memory Module |
| 能力获取分类 | 有微调（人工标注/LLM 生成/真实数据三类）+ 无微调（提示工程/机制工程），Fig 4 概括三时代范式迁移 | §2.2 Agent Capability Acquisition |
| 评估体系 | 2 类主观策略 + 3 类指标/4 类协议/约 19 个基准；Table 3 对齐 29 个评估工作 | §4.1; §4.2; Table 3 |
| 引用的代表性基准规模 | ToolBench 16,464 个 API/49 类；MIND2WEB 2,000+ 任务/137 网站/31 领域；WebShop 1.18M 商品；SocKET 58 任务/5 类；EmotionBench 400+ 情境/8 类负面情绪；PEB 13 靶机 | §2.2; §4.2 Objective Evaluation |
| 应用领域覆盖 | 社会科学 5 方向、自然科学 3 方向、工程 3 方向 + 约 11 个开源库（Table 2） | §3; Table 2 |
| 提出的开放挑战 | 6 项：角色扮演/广义对齐/prompt 鲁棒性/幻觉/知识边界/效率 | §6.1–§6.6 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2308.11432 |
| 期刊版 | Frontiers of Computer Science, 2025（doi:10.1007/s11704-024-40231-1） |
| 论文资源库 | https://github.com/Paitesanshi/LLM-Agent-Survey（综述配套论文列表） |
| 综述内开源库示例 | LangChain、AutoGPT、AgentVerse、BMTools、XLang、GPT-Engineer、DemoGPT、AGiXT、GPT Researcher 等（§3.3 Engineering 列出，均非本文产出） |
| 关联综述 | 本文与同目录 02（Agent for SE 综述）、10（Generative Agents）、11（CAMEL）、12（MetaGPT）等被引工作互为上下文 |

## 5. 一句话索引（给 Agent 用）

> 需要单 agent 构成的权威分类骨架时读这篇：Wang 综述（FCS 2025，覆盖 100 篇工作）把 LLM 自主 agent 统一为 **Profiling/Memory/Planning/Action 四模块**——画像分手工/LLM 生成/数据集对齐三策略；记忆按结构-格式-操作分类（读取按新近性-相关性-重要性加权）；规划分无反馈（CoT/ToT/外部规划器）vs 有反馈（环境/人类/模型）；行动按目标-产生-空间-影响四维。能力获取分微调与提示/机制工程两路；应用覆盖社科/自然科学/工程三域；评估分主观与客观（指标/协议/基准，含 AgentBench、ToolBench 16,464 API）；并提出角色扮演、广义对齐、prompt 鲁棒性等 6 项挑战。覆盖止于 2021–2023，具身与多 agent 协作涉及较浅。
