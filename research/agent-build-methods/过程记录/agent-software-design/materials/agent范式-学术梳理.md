# Agent 设计范式学术梳理

> 调研日期：2026-08-16
> 用途：为"从软件工程基本原理重新审视 Agent 软件设计方法"研究提供理论框架素材。
> 说明：所有 arXiv ID 均经检索核实；标注"约"的数字来自厂商自报或第三方榜单，口径不完全可比；个别未能直接核验处已显式注明。

---

## 一、综述类文献：架构分类框架

### 1.1 Wang et al., "A Survey on Large Language Model based Autonomous Agents"

- 出处：Lei Wang et al.（中国人民大学），2023-08 首版（持续更新至 2025-03 v7），正式发表于 *Frontiers of Computer Science* (2024)。[arXiv:2308.11432](https://arxiv.org/abs/2308.11432)
- **核心主张**：提出统一的 LLM 自主 agent 架构框架，含四个模块——**Profiling（角色画像）、Memory（记忆）、Planning（规划）、Action（行动）**。综述按"构建—应用—评估"三条主线组织文献。
- **证据类型**：综述归纳。各模块给出二级分类法：记忆按结构（统一短时 vs. 短长时混合）、格式、操作（读/写/反思，读取按"新近性—相关性—重要性"加权）分类；规划按"无反馈规划（单路径 CoT、多路径 ToT/GoT/RAP、外部规划器）vs. 有反馈规划（环境/人类/模型反馈）"分类；行动按目标、产生方式、空间（外部工具 vs. LLM 内部知识）、影响四维分类。
- **适用条件与边界**：框架是对 2021–2023 年工作的事后归纳，不声称普适；明确指出纯短时记忆受限于上下文窗口，实际系统普遍需要混合记忆结构；对具身 agent 与多 agent 协作覆盖较弱。
- **选型启示**：单 agent 设计的"部件选型清单"——先按四槽位做需求分析，再在模块内选型；简单任务不必上齐四模块，无反馈单路径规划 + 纯内部知识行动即可覆盖大量场景。

### 1.2 Liu et al., "Large Language Model-Based Agents for Software Engineering: A Survey"

- 出处：Junwei Liu et al.（复旦大学、UIUC 等），2024-09 首版（v2 更新至 2025-12，含 124 篇文献），TOSEM 接收。[arXiv:2409.02977](https://arxiv.org/abs/2409.02977)；文献列表：https://github.com/FudanSELab/Agent4SE-Paper-List
- **核心主张**：双视角梳理——SE 视角按软件生命周期任务组织（需求工程、代码生成、静态检查、测试、调试、端到端开发/维护）；Agent 视角将 agent 分解为 **planning、memory、perception、action** 四组件，并覆盖多 agent 系统（角色、协作机制、信息流）与人机协作模式。核心论点：单 LLM 只擅长单一任务，agent 化才使其胜任端到端真实 SE 任务。
- **证据类型**：系统性综述归纳，方法学规范（DBLP 初筛 10,362 命中 + 滚雪球 + 向 321 位作者征集反馈；约 75% 为同行评审出版物；明确纳入/排除标准）。各任务附代表性系统对比表（如代码生成按反馈来源分为模型/工具/人类/混合四类）。
- **适用条件与边界**：自述为 comprehensive survey 而非 SLR，不做实验复现；文献截止 2024-09（v1）；指出 RE 生成物含糊、多 agent 协作质量保证仍是开放挑战、工具增强单 agent 方案质量高但可扩展性受限。
- **选型启示**：支持按"任务类型 × agent 组件"矩阵做设计决策；对比结论可直接指导取舍——如双 planner 不优于单 planner、最常见的有效反馈组合是工具+模型混合反馈。

### 1.3 Hassan et al., "Agentic Software Engineering: Foundational Pillars and a Research Roadmap"

- 出处：Ahmed E. Hassan et al.（Queen's University 等），2025-09 首版（v3: 2026-06）。[arXiv:2509.06216](https://arxiv.org/abs/2509.06216)
- **核心主张**：提出"结构化 agentic 软件工程（SASE）"愿景：SE 3.0 时代存在 **SE for Humans 与 SE for Agents 的二元性**，需重构四大支柱 **Actors、Processes、Tools、Artifacts**；人类任 Agent Coach，在 ACE（编排环境）/AEE（执行环境）中与 agent 协作；交互由结构化、版本化工件承载（BriefingScript / MentorScript / MRP 等）。另提出类比 SAE 自动驾驶的 SE 自动化分级：L0 手工 → L1 补全 → L2 任务级 agentic（SE 2.0）→ L3 目标级 agentic（SE 3.0）→ L4/L5 自治；分类本质是 **agency（执行给定计划）与 autonomy（自行制定计划）两轴**，据此区分 Workflow Agents 与 Autonomous Agents。
- **证据类型**：观点性论述（vision/roadmap）+ 二手实证引用（如 SWE-Bench 上 29.6% 的"plausible"修复经复测存在回归；GPT-4 补丁真实解决率经人工审计从 12.47% 降至 3.97%；AIDev 数据集收录 93 万余个 agent 撰写的 PR）。无自实现验证。
- **适用条件与边界**：自述为"概念脚手架"而非确定性方案；L4/L5 尚不存在；证据主要来自编码类 agent，对其他 SE 活动外推需谨慎。
- **选型启示**：提供选型坐标系——先判任务所需自治级别（L2 用补全即可，L3 才需 agentic 系统），再按 agency/autonomy 两轴选 workflow agent 还是 autonomous agent；强烈支持"人机接口与可审计工件作为一等公民"。

### 1.4（补充）He et al., "LLM-Based Multi-Agent Systems for Software Engineering: Literature Review, Vision, and the Road Ahead"

- 出处：Junda He, Christoph Treude, David Lo，2024-04 首版，已刊 ACM TOSEM 34(5), 2025。[arXiv:2404.04834](https://arxiv.org/abs/2404.04834)
- **核心主张**：系统综述 LLM 多智能体系统在 SDLC 各阶段的应用图景，附两个案例研究，愿景为 Software Engineering 2.0。
- **证据类型**：综述归纳 + 演示性案例（非受控对比）。
- **选型启示**：提供 SE 场景下 MAS 的"成熟度地图"——按 SDLC 阶段判断哪些环节 MAS 已较成熟、哪些是空白，而非整体押注。

**综述层小结**：三层抽象可作文献综述骨架——组件架构层（Wang 的四模块）、领域应用层（Liu 的任务×组件矩阵）、工程过程与组织层（Hassan 的四支柱与自治分级）。引用时注意证据强度差异：前两篇为规范方法学的文献归纳，第三篇为观点性愿景。

---

## 二、经典范式原始论文：核心主张与适用条件

### 2.1 ReAct —— 单循环"推理-行动"范式

- Yao et al.（Princeton / Google Brain），2022-10 首版，ICLR 2023 (Oral)。[arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- **核心主张**：推理与行动应协同——LLM 交替生成 Thought 与 Action，形成 Thought-Action-Observation 循环；推理用于归纳、追踪、更新计划并处理异常，动作用于与外部环境交互获取信息。
- **证据类型**：中等规模实验（HotpotQA、Fever、ALFWorld、WebShop），仅 1–2 个上下文示例、未微调。ALFWorld 成功率绝对值提升 34%，WebShop 提升 10%。
- **适用条件与边界**：收益依赖可靠外部反馈源；纯封闭推理任务上相对 CoT 优势不明显（HotpotQA 上 ReAct 与 CoT 组合最佳）；错误动作沿轨迹累积；轨迹可解释性以 token 成本为代价。
- **选型启示**：需要外部工具/环境交互且要求轨迹可解释时的默认基线；无外部交互需求的任务用纯 CoT 更省成本。

### 2.2 Reflexion —— 语言化反思外循环

- Shinn et al.（Northeastern / MIT 等），2023-03，NeurIPS 2023。[arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- **核心主张**：不更新权重，将任务反馈转化为语言"反思"文本存入情景记忆，下次尝试时注入上下文，实现"语言强化学习"。框架由 Actor、Evaluator、Self-Reflection 模型与情景记忆组成。
- **证据类型**：中等规模实验（ALFWorld、HumanEval/MBPP、HotpotQA）+ 消融（反馈信号类型、融入方式）。HumanEval 达 91% pass@1，超 GPT-4 基线 80%。
- **适用条件与边界**：前提是**可重复尝试且有明确反馈信号**（单元测试、环境成功判定）；模型无法正确自评时反思会退化或误导；多次重试带来显著推理成本。
- **选型启示**：具备可验证成败信号且允许迭代的任务（编程、交互式环境）应在 ReAct 内循环上叠加"评估→反思→重试"外循环；选型关键先回答"反馈信号从哪来、是否可靠"。

### 2.3 Tree of Thoughts —— 推理时树状搜索

- Yao et al.（Princeton / Google DeepMind），2023-05，NeurIPS 2023。[arXiv:2305.10601](https://arxiv.org/abs/2305.10601)
- **核心主张**：将 CoT 推广为树结构——生成多个候选思维分支，模型自评状态价值，结合 BFS/DFS 做前瞻与回溯的全局决策（类 System 2 审慎求解）。
- **证据类型**：小规模任务特化实验（24 点游戏、创意写作、迷你填字，GPT-4）。24 点上 CoT 仅 4% 成功率，ToT 达 74%。
- **适用条件与边界**：适用于解空间可分解且中间状态可自评的组合搜索/规划任务；线性推理链任务收益有限；token 消耗随分支数与深度成倍增长（约 5–10 倍），且需任务特化的 prompt 与搜索参数调试。
- **选型启示**：先做任务分型——只有"组合搜索/规划型 + 可自评中间状态"才值得树状探索的成本；工程上应将 thought 生成、状态评估、搜索策略解耦并预估 token 预算。

### 2.4 Plan-and-Solve 与 plan-and-execute 类

- Plan-and-Solve：Lei Wang et al.（新加坡管理大学），2023-05，ACL 2023。[arXiv:2305.04091](https://arxiv.org/abs/2305.04091)
- **核心主张**：先生成将任务分解为子任务的计划，再按计划逐步执行；PS+ 加入更详细指令减少计算错误。针对 Zero-shot-CoT 的三类错误（计算、漏步、语义误解）。
- **证据类型**：中等规模基准实验（10 个算术/常识/符号推理数据集，GPT-3）；PS+ 稳定超过 Zero-shot-CoT，数学推理上接近 8-shot CoT。
- **适用条件与边界**：计划一次性静态生成，执行中遇意外无法自适应——这正是后续 plan-and-execute 加入 replanner 的动因；不提供工具调用、记忆或多轮交互；对更强模型的边际收益未验证。
- **选型启示**：任务结构清晰、可预先分解、执行中少有意外时，"静态计划 + 顺序执行"比 ReAct 式逐步反应更省 token 且更少漏步；环境不确定时必须升级为带重规划的架构。
- **延伸参照**：LLMCompiler（Kim et al., ICML 2024，[arXiv:2312.04511](https://arxiv.org/abs/2312.04511)）将计划工程化为任务 DAG + 并行派发 + 重规划，适用于多工具调用且子任务部分独立的场景；BabyAGI 无正式论文，仅宜作工程案例引用。

### 2.5 Generative Agents —— 认知架构式 agent

- Park et al.（Stanford / Google Research），2023-04，UIST 2023。[arXiv:2304.03442](https://arxiv.org/abs/2304.03442)
- **核心主张**：记忆流 + 反思 + 规划三件套——自然语言记忆流完整存储经历；周期性将记忆合成为高层抽象；递归分解日程生成计划；检索按新近度/重要性/相关性加权。
- **证据类型**：小规模案例研究 + 人类评估 + 消融（25 个 agent 在沙盒小镇运行两天；消融证明三组件各自对行为可信度有显著贡献）。评估维度是"可信度"而非任务正确率。
- **适用条件与边界**：面向行为模拟/角色扮演目标，无证据支持直接迁移到任务型 agent；成本高昂（数千美元量级 API 费用/两天模拟）；长时程运行出现记忆错位与幻觉式行为传播。
- **选型启示**：需求是长时程连续性（人物一致性、多日程行为）时，"记忆流 + 加权检索 + 周期反思"是消融可验证的必要架构；任务短、无状态时这套复杂度不划算——**架构复杂度应与任务的时间跨度与状态性匹配**。

**范式层小结**：ReAct 解决"与外部世界交互"，Reflexion 解决"从失败中迭代"，ToT 解决"推理时审慎搜索"，Plan-and-Solve 解决"先分解后执行"。共同证据模式是中小规模、任务特化实验，依赖反馈/自评信号质量，以推理成本换能力。选型应沿三问逐步判别：是否需要外部交互？是否有可验证反馈可重试？是否需要组合搜索？范式差异本质是**控制流结构（反应式循环 vs 静态计划 vs DAG 计划）与状态管理策略（无记忆 vs 上下文窗口 vs 记忆流+反思）两个正交维度的组合选择**。

---

## 三、多智能体协作范式原始论文

### 3.1 CAMEL —— 角色扮演对话

- Li et al.，2023-03，NeurIPS 2023。[arXiv:2303.17760](https://arxiv.org/abs/2303.17760)
- **核心机制**：inception prompting 驱动两个 LLM agent（助手/用户角色）在极少人类干预下自主协作；目标是可扩展地生成会话数据、研究"智能体社会"。
- **证据类型**：中小规模系统性实验 + 案例研究（四类领域生成角色扮演会话，人工 + GPT-4 评估），探索性而非严格基准对比。
- **适用条件与边界**：论文自述角色翻转、指令重复、flake replies、无限对话等失效模式，需终止条件与 critic 约束；更适合探索/数据生成而非高正确性工程交付。
- **选型启示**：多智能体价值的第一来源是**角色化系统提示词设计**而非复杂编排框架；必须有显式终止机制。

### 3.2 MetaGPT —— SOP 装配线

- Hong et al.，2023-08（更新至 v7 2024-11；ICLR 2024 接收为间接核实）。[arXiv:2308.00352](https://arxiv.org/abs/2308.00352)
- **核心机制**：将人类 SOP 编码进提示序列，以装配线范式分配角色（产品经理、架构师、工程师、QA），用结构化中间产物（文档、接口规约）作为 agent 间契约，校验中间产物以减少级联幻觉。
- **证据类型**：基准实验（代码生成任务与自建 SoftwareDev 评测），方案连贯性与可执行率高于聊天式多智能体系统。
- **适用条件与边界**：有效性建立在"已有成熟人类 SOP 可编码"的前提上；开放任务下固定流水线僵化；实验集中于 SE 域；串行多环节成本高、延迟大。
- **选型启示**：流程确定性高 → SOP 流水线；"中间产物可校验"是抑制幻觉级联的关键机制。

### 3.3 AutoGen —— 可编程会话协议

- Wu et al.（Microsoft Research），2023-08。[arXiv:2308.08155](https://arxiv.org/abs/2308.08155)
- **核心机制**：所有 agent 均为"可定制、可对话"的 conversable agent，通过会话完成任务；混合 LLM、人类输入与工具，用自然语言与代码共同编程会话模式，支撑双人对话到动态群聊的多样拓扑。
- **证据类型**：多应用场景实证展示（A1–A6 六个应用），框架论文而非单基准大规模对照。
- **适用条件与边界**：通用使能层，不提供正确性保证；收益取决于开发者对会话模式的设计；任务可单 agent 完成时多会话反引入开销。
- **选型启示**："会话即协议"抽象可作为默认底盘——先用 conversable agent 原语原型化，任务有固定流程再上 SOP（MetaGPT 式），纯探索对话用角色扮演（CAMEL 式）。

**多智能体层小结**：三种范式原语分别对应经典软件工程关切——团队角色分工（CAMEL）、过程模型制度化（MetaGPT）、通信中间件（AutoGen）。证据均偏框架/案例性质；选型按"任务流程确定性"：确定性高用 SOP 流水线，探索性用角色扮演，不确定时先用通用会话框架原型化。

---

## 四、失败模式与边界研究

### 4.1 MAST 分类法 —— Cemri et al., "Why Do Multi-Agent LLM Systems Fail?"

- UC Berkeley，2025-03（v3 2025-10）。[arXiv:2503.13657](https://arxiv.org/abs/2503.13657)，全文见 `references/AgentParadigms/15`
- **核心主张**：首个基于实证扎根分析的多智能体系统失败分类法 MAST，14 种失败模式归 3 大类（**v3 口径，2026-08-17 全文精读核实**；v1 曾报 41.77/36.94/21.30，引用旧文时注意区分）：
  - **FC1 系统设计问题（44.2%）**：不遵守任务规范（11.8%）、不遵守角色规范（1.50%）、步骤重复（15.7%，单模式最高）、对话历史丢失（2.80%）、无法识别终止条件（12.4%）；
  - **FC2 智能体间失调（32.3%）**：对话重置（2.20%）、不寻求澄清（6.80%）、任务跑偏（7.40%）、信息隐瞒（0.85%）、忽略他 agent 输入（1.90%）、推理-行动不匹配（13.2%）；
  - **FC3 任务验证不足（23.5%）**：过早终止（6.20%）、缺失/不完整验证（8.20%）、错误验证（9.10%）。
- **证据类型**：Grounded Theory 分析 150 条专家轨迹（平均每条超 15000 行，6 名专家标注 Cohen's Kappa 0.88），再用 o1-based LLM-as-a-Judge（accuracy 94%、Kappa 0.77）扩展标注 7 个主流 MAS 框架（MetaGPT、ChatDev、HyperAgent、AppWorld、AG2、Magentic-One、OpenManus）共 1642 条轨迹；附 ChatDev 干预实验（改角色规范 +9.4%、改拓扑 +15.6pp 但完成率仍低）。
- **适用条件与边界**：不声称覆盖全部失败模式；轨迹来自 GPT-4o/Claude-3 时代开源框架，对更强基座模型适用性需再验证；FC2 的本质被论证为"theory of mind 塌缩"，通信标准化（MCP/A2A）不足以解决。
- **选型启示**：多智能体失败大头是**组织设计问题而非基座模型能力不足**（援引高可靠性组织理论）：(1) 上 MAS 前先写清任务/角色/终止规范，FC1+FC3 近七成失败可用工程手段拦截；(2) 战术性修补（prompt/拓扑）不够，需结构级设计（多级验证、独立验证器——仅末段低层检查如"能否编译"不够）；(3) MAST 可直接用作失败诊断 checklist。

### 4.2 Single-agent vs Multi-agent 实证对比

**More Agents Is All You Need**（Li et al., Tencent AI Lab，2024-02，[arXiv:2402.05120](https://arxiv.org/abs/2402.05120)，全文见 `references/AgentParadigms/16`；2026-08-17 精读核实）：sampling-and-voting 下增加实例化 agent 数（ensemble size）即可在所有任务×模型上单调提升（GSM8K +12%~+24%、MMLU +5%~+11%、HumanEval +4%~+9%），且与 CoT-SC/Debate 等方法正交可叠加；暴力集成小模型可反超大模型（Llama2-13B×40 在 GSM8K 0.59 > Llama2-70B 单次 0.54）。本质是集成/自洽性方法（无角色分工、无通信拓扑），只适用于可投票任务。⚠️ 早期转述中的"COVER/CONF 维度模型"为误记，论文实际按任务难度三维（固有关联难度/推理步数/先验概率）分析增益。选型含义："多采样+投票"应作为任何 MAS 方案的 baseline。

**Single-agent or Multi-agent Systems? Why Not Both?**（Gao et al.，2025-05，[arXiv:2505.18286](https://arxiv.org/abs/2505.18286)，全文见 `references/AgentParadigms/17`；2026-08-17 精读核实）：15 数据集/7 任务/9 框架实测——**MAS 相对 SAS 的准确率优势随基座变强从 9%–16% 缩到 0.8%–3.0%，而 prefill token 仍贵 4–220×**（decode 2–12×）；失败归因为节点/边/路径三类缺陷，用 agent 自报置信度（1–10）定位升级点；SAS-MAS Routing/Cascade 混合后准确率最高 +12%（DS1000 62.9→71.2）、成本较逐请求 MAS 最多降 20%、总体最高省 88.1%。选型含义：反对"默认多智能体"——强模型优先 SAS，MAS 作为疑难请求的升级路径。

**A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric Software Engineering Tasks**（Yin, Gao et al.，2025-11，[arXiv:2511.00872](https://arxiv.org/abs/2511.00872)，全文见 `references/AgentParadigms/18`；2026-08-17 全文精读核实）：实测对象为 **AgentOrchestra、OWL、SE-Agent、Trae、GPTswarm、OpenHands、SWE-Agent** 7 框架 × 软件开发（SRDD 1200）/漏洞检测（LLM-SmartAudit 115）/程序修复（SWE-bench Lite 300），统一 DeepSeek-v3.1 后端。结论细化（并非笼统的"SAS 全面胜"）：软件开发 SAS 综合质量最佳（OpenHands 0.47 vs 均值 0.36）但分层 MAS（AgentOrchestra 0.86）完整性单项最高；漏洞检测七框架接近（均值约 66%，最高 GPTswarm 77%）；程序修复单 agent 的 SE-Agent（迭代 3）54% 最高、12 仓库全胜，而 3 个 MAS 因缺 Patch 工具仅 3–10%。机制归因：多 agent 的 planning 阶段 token 占 65.8%–94.2%、交互开销+上下文溢出+幻觉传播。选型含义：SE 任务默认单 agent，但**完整性优先的生成类任务分层 MAS 有单项优势**；MAS 框架必须配备 diff/patch 类工具与自监控，否则"修正次数少"实为错误检测缺失。

### 4.3 Long-horizon 任务可靠性

**The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs**（Sinha et al.，2025-09，ICLR 2026 接收，[arXiv:2509.09677](https://arxiv.org/abs/2509.09677)）：短任务基准上微小的单步准确率提升会复合成可完成任务长度的指数级增长；长程失败根源是**执行错误**而非推理能力缺失；发现 **self-conditioning 效应**——上下文中出现自己先前的错误会让模型更容易继续犯错，该效应不随模型规模消失，但 thinking 能显著缓解。证据类型：受控合成实验 + 前沿模型单轮长任务测试。选型含义：长程 agent 需要**外部化状态与检查点验证**（不要让模型在可能含错的上下文中无限滚动）；把长任务切成可验证的短段；thinking 预算对长程执行有实质帮助。

**Measuring AI Ability to Complete Long Tasks**（Kwa et al., METR，2025-03，v4 2026-07，[arXiv:2503.14499](https://arxiv.org/abs/2503.14499)，全文见 `references/AgentParadigms/20`；2026-08-17 精读核实）：提出 **50% 任务完成时间地平线**指标（logistic 回归拟合成功率-时长曲线）；v4 实测 **每 207 天翻番**（95% CI 166–240 天），GPT-2 约 2 秒 → o3 约 **110 分钟**并完成多个 >4 小时任务；**80% 地平线翻番速度相近但绝对值短 4–6 倍**——偶尔做成难任务 ≠ 可靠完成中等任务。增长主要由可靠性与自我纠错驱动（o1 失败的一半是"过早放弃"，GPT-4 则多为重复失败动作）。边界：受控环境比真实任务"干净"；SWE-bench Verified 上同方法翻番仅约 70 天，系标注时间低估易任务所致。选型含义：用"时间地平线"做能力预算锚点——超出可靠自主窗口的长任务必须引入人类检查点或结构化验证；生产选型建议按 80% 口径打 4–6 倍折扣。

**边界研究小结**：当前 agent 系统的失败更多是组织与工程问题而非单体智能问题。MAS 逾六成失败源于规范缺失与验证缺位；随基座模型增强，多智能体相对单智能体的收益收窄而协调开销确定存在；单步准确率的微小改进复合放大，但 self-conditioning 错误累积是长程执行的内生风险。综合选型原则：**默认"强单智能体 + 外部化状态 + 分段验证"，多智能体仅用于有明确分工收益的环节并配独立验证器，长任务按时间地平线设人类检查点**。

---

## 五、Agent Benchmark 揭示的能力边界

### 5.1 SWE-bench 系列

**SWE-bench**（Jimenez et al.，2023-10，ICLR 2024，[arXiv:2310.06770](https://arxiv.org/abs/2310.06770)）：12 个 Python 仓库的真实 GitHub issue + PR 共 2,294 任务，需直接编辑代码并通过 PR 附带测试。发布时最强模型 Claude 2 仅解决 1.96%。选型含义：证明"一次性生成补丁"在真实 SE 任务上完全失效，**agentic 循环（定位—编辑—运行测试—迭代）是必要条件而非可选项**。

**SWE-bench Verified**（OpenAI 官方博客，2024-08，[链接](https://openai.com/index/introducing-swe-bench-verified/)，非 arXiv 论文）：原版系统性低估模型能力；93 名开发者人工审查筛出 500 题，成为事实标准。选型含义：评估结论高度依赖评测集质量，引用解决率须注明 Verified 口径。

**解决率演进**：从 1.96%（2023，Claude 2）→ 约 49%（2024-10，Claude 3.5 Sonnet，Verified，约）→ 约 77%（2025，Claude Sonnet 4.5 厂商自报，约）→ 约 95–97%（2026 第三方榜单，口径不一，约）。含义：(1) benchmark 寿命短，"某范式不行"的旧结论可能过期；(2) 剩余未解决任务集中于长程、模糊需求、大型跨仓库修改，恰是真实工程核心难点（参见 "The SWE-Bench Illusion"，[arXiv:2506.12286](https://arxiv.org/abs/2506.12286)）。

**SWE-bench Multimodal**（Yang, Jimenez et al.，2024-10，[arXiv:2410.03859](https://arxiv.org/abs/2410.03859)）：17 个 JS 前端库 617 个含图像任务；SWE-bench 上表现最好的系统迁移后性能大幅崩塌（最佳系统仅 12%）。选型含义：scaffold 的语言/域无关性本身就是能力边界；针对单一 benchmark 调优的流水线不可迁移。

### 5.2 τ-bench / τ²-bench

**τ-bench**（Yao, Shinn, Razavi, Narasimhan，Sierra，2024-06，ICLR 2025，[arXiv:2406.12045](https://arxiv.org/abs/2406.12045)）：评测 agent 与 LLM 模拟用户的多轮交互 + 工具调用 + 政策遵循，以数据库终态比对判成败；提出 **pass^k** 指标（k 次独立试验全部成功的比例）。关键发现：gpt-4o 单轮成功率 <50%，retail 域 pass^8 <25%；Claude 3.5 Sonnet retail pass@1 约 69.2% 但 pass^4 降至 46.2%（约，榜单转引）。因 pass^k ≈ p^k，可靠性随 k 指数衰减。选型含义：生产选型必须看 pass^k 而非 pass@1；"平均能行"不等于"每次能行"，需确定性护栏（规则引擎、状态校验、幂等工具）。

**τ²-bench**（Barres et al.，Sierra，2025-06，[arXiv:2506.07982](https://arxiv.org/abs/2506.07982)）：将环境建模为 Dec-POMDP——用户也持有工具可对共享世界操作，agent 必须"引导用户行动"。核心发现：从 no-user 切换到 dual-control 设置时性能显著下降，**协调与沟通是独立于推理的能力短板**。选型含义：人机协作场景需显式设计"指导人类行动"的交互协议；评估时将推理错误与沟通/协调错误分别归因。

### 5.3 其他边界 benchmark（择要）

**GAIA**（Mialon et al.，2023-11，ICLR 2024，[arXiv:2311.12983](https://arxiv.org/abs/2311.12983)）：466 个对人类简单但需组合推理、多模态、网页浏览、工具使用的问题。发布时人类 92%，带插件 GPT-4 仅 15%——"人类容易 ≠ 机器容易"。选型含义：通用助手能力高度依赖工具链完备性；工具生态应与模型选择同级对待。

**OSWorld**（Xie et al.，2024-04，NeurIPS 2024 D&B，[arXiv:2404.07972](https://arxiv.org/abs/2404.07972)）：真实计算机环境 369 个跨应用任务。发布时人类 72.36%，最佳模型仅 12.24%，瓶颈在 GUI grounding。选型含义：能用 API 就不用 GUI 自动化；必须 GUI 时需专门 grounding 模块与执行校验。

**Benchmark 层小结**：三个结构性事实——(1) 边界移动极快，选型依据须按最新一代模型重新校准；(2) 单次能力与可靠性是两条独立边界（pass^k 腰斩现象），生产级设计须用确定性机制补足采样不一致；(3) scaffold 与工具生态是能力边界的一部分，"语言/域无关架构 + 结构化工具 + 可靠性工程"应置于模型选择之上。

---

## 六、综合：对"范式选型"的决策框架提炼

1. **任务分型先行**：是否需要外部交互（→ ReAct 基线）？是否有可验证反馈可重试（→ 叠加 Reflexion 外循环）？是否是组合搜索型且有可自评中间状态（→ 才考虑 ToT）？任务可否预先静态分解（→ plan-and-execute，动态环境必须 replan）？
2. **架构复杂度与任务时间跨度/状态性匹配**：短且无状态 → 简单循环；长时程连续性 → 记忆流 + 加权检索 + 反思（Generative Agents 的消融证据）。
3. **多智能体是例外而非常态**：先写清任务/角色/终止规范（MAST v3：FC1 系统设计占 44.2%），配独立验证器（FC3 占 23.5%）；以"单 agent + best-of-N"为 baseline 对比；强基座模型时代优先 SAS（MAS 优势已缩至 0.8%–3.0% 而 prefill 贵 4–220×），MAS 作为级联升级路径、完整性优先的生成任务可用分层 MAS；流程确定性高时 SOP 装配线优于自由对话。
4. **可靠性工程独立于能力工程**：pass^k 与 self-conditioning 研究表明，生产可用性来自外部化状态、分段验证、确定性护栏与人类检查点，而非单纯换更强模型或更复杂范式。
5. **评估口径自觉**：区分 benchmark 质量噪声与真实能力（SWE-bench → Verified 的教训）；引用数字注明口径；按最新模型代际重新校准旧结论。
