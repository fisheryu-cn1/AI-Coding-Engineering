---
title: "Large Language Model-Based Agents for Software Engineering: A Survey"
source_pdf: "02-Liu-Survey_Agents_for_SE_v2.pdf"
arxiv_id: "2409.02977"
arxiv_version: "v2"
authors:
  - "Junwei Liu"
  - "Kaixin Wang"
  - "Yixuan Chen"
  - "Xin Peng"
  - "Zhenpeng Chen"
  - "Lingming Zhang"
  - "Yiling Lou"
year: 2024
venue: "ACM TOSEM"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：面向软件工程的 LLM 智能体综述（任务 × 组件矩阵）

## 1. 适用场景

- 当你要**为某个 SE 生命周期任务（需求工程/代码生成/静态检查/测试/调试/IT 运维/端到端开发或维护）调研现有 LLM agent 系统、代表性工作与已知失败模式**时，读这篇可一次拿到 124 篇论文的分类地图与取舍结论。
- 当你要**设计 agent 架构**——决定 planner 单/多、单/多轮、单/多路径，memory 的时长/归属/格式/读写策略，工具（检索/静态分析/动态分析/测试/版本控制）接入方式，多 agent 拓扑与人机协作阶段——时，读 §5 的组件分类学（taxonomy）逐维对照。
- 当你要**评估 agent 系统或构建基准**（SWE-bench 系列演化、项目级开发基准、resolve rate/成本等指标缺陷）时，读 §4.7.4/§4.8.8/§6 获取基准谱系、指标清单与改进方向。
- 当你需要**引用一组可溯源的量化对比**（如 SpecGen vs 传统工具、AutoCodeRover 加 SBFL 前后、Flows 人类计划片段增益）支撑自己的论证时，查 §3 效果表所列原文数据。

> 锚点：Abstract; §1 INTRODUCTION; §3 SURVEY METHODOLOGY; §4 ANALYSIS FROM SE PERSPECTIVES; §5 ANALYSIS FROM AGENT PERSPECTIVE; §6 RESEARCH OPPORTUNITIES。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 INTRODUCTION; §2 BACKGROUND AND PRELIMINARY）

- 核心论点：standalone LLM 只擅长单一 SE 任务；LLM-based agent 通过 planning、memory、perception、action 四组件（§2.1 Basic Framework of LLM-based Agents）感知并利用外部资源与工具，再叠加多 agent 协作与人机协作，才能胜任端到端真实 SE 任务（§2.2 Advanced LLM-based Agent Systems）。
- 与既有 LLM4SE 综述的差异：覆盖更宽任务（含端到端开发/维护），并从 agent 架构视角建立 memory/planning/action、多 agent 协作与人机交互的分类学；区别于 He et al. 的 MAS-for-SE 愿景论文，本综述覆盖单 agent 与多 agent 的既有系统（§2.4 Related Surveys）。
- 双视角组织：SE 视角按软件生命周期任务分节（§4），agent 视角按组件与协作机制分节（§5），最后给出研究机会（§6）。

### 2.2 方法学（§3 SURVEY METHODOLOGY）

- 范围界定：只收"以 LLM 为核心大脑且能迭代与环境交互"的系统，排除单 LLM 线性流水线；定位为 comprehensive survey 而非 SLR，不做额外实验（§3.1 Survey Scope；Table 1 纳入/排除标准含"少于 2 页""灰色文献"等 7 条排除项）。
- 三步收集：关键词检索（最终关键词 `(agent|llm|language model) AND (api|bug|code|…|vulnerab)` 共 19 个 SE 词），2024-07-01 在 DBLP 上执行 57 次搜索得 10,362 命中、人工筛得 67 篇（§3.2.1 Keyword Searching）；前向+后向滚雪球 +41 篇（§3.2.2 Snowballing）；向 321 位作者征集反馈、收 36 份有效回复、新纳入 16 篇（§3.2.3 Author Feedback Collection）。
- 共 124 篇；约 75% 为同行评审出版物，其余为 arXiv 预印本（§3.3 Statistics of Collected Papers）。

### 2.3 SE 视角一：单任务章节（§4.1–§4.6）

- **需求工程（§4.1 Requirements Engineering）**：两条策略——多 agent 角色扮演协作（Elicitron 以多 persona 用户 agent 采访挖掘潜在需求；Arora et al. 四阶段流水线；MARE 用 stakeholder/collector/modeler/checker/documenter 团队，§4.1.1）vs 工具增强单 agent（SpecGen 结合 OpenJML 迭代精化 JML 规约并对失败规约做变异再验证，§4.1.2）；比较结论：多 agent 覆盖面广但协同质量保证是难点，单 agent 借工具反馈质量更高但可扩展性受限（§4.1.3）。挑战：生成需求含糊/不相关、人机交互被"角色替换"弱化、无需求演化支持（§4.1.4）。
- **代码生成（§4.2 Code Generation）**：总体是"plan–generate–refine"范式（Fig. 6）。规划侧分 prompt engineering（zero-shot/few-shot CoT 数量相当，静态单例而非按相似度动态选例）与 agentic 策略（CodePlan 自适应仓库级计划、LATS 用 MCTS 模拟生成树、MapCoder 多计划带置信度排序；Flows 实验显示双 planner 不优于单 planner，§4.2.1）；计划表示含自然语言、伪代码、中间代码、代码骨架。精化侧按反馈来源分四类（§4.2.2）：模型反馈（peer-reflection 如 AutoGen 的 SafeGuard 审查 Writer、AgentForest/DyLAN 用 BLEU 聚合选优；self-reflection 如 Self-Debugging 橡皮鸭解释）、工具反馈（执行/静态检查/检索，如 ToolCoder 在线+本地文档检索）、人类反馈（ClarifyGPT 主动识别歧义并提问）、混合反馈（现仅见工具+模型组合，INTERVENOR 师-生解释错误，LDB 按控制流分块收集断点处中间运行状态、优于只看最终输出的 Self-Debugging）。失败成因（§4.2.3）：协作失序（CAMEL 陷入"thank you"死循环）、低质量测试误导自纠（Self-Refine 失败案例中 33% 源于错误定位、61% 源于不当修复建议）、错误反馈级联、长上下文推理退化（AutoGen/InterCode）。挑战（§4.2.4）：高质量测试难获得、迭代开销大、外部工具可靠性无保证。
- **静态检查（§4.3 Static Code Checking）**：漏洞/缺陷检测三路线（§4.3.1）——多 agent 共检（Mao et al. developer+tester 讨论、GPTLens 两阶段 auditor+critic、iAudit 微调 Detector+Reasoner 后 Ranker-Critic 辩论）、工具执行增知（ART 检索任务示范、LLM4Vuln 检索漏洞报告与知识库、PropertyGPT 生成形式验证属性）、与传统静态分析结合（LLift 建在 UBITect 上判 Linux UBI、E&V 伪代码执行+Clang 取上下文、IRIS 用 CodeQL 提 source/sink、LLM4DFA 用 tree-sitter+Z3 做数据流验证）。代码评审（§4.3.2）分过程型（CodeAgent 类瀑布四阶段六角色、ICAA 意图一致性、CORE Proposer+Ranker）与目标型（Rasheed et al. 四个专职 agent）。挑战（§4.3.3）：与传统工具集成浅（多止于过滤误报）、需强推理模型（GPT-4 级）、误报缺自动核验。
- **测试（§4.4 Testing）**：单测三大方向（§4.4.1）——修编译/执行错误（ChatTester/TestPilot/ChatUniTest/AgentCoder/AutoDev，差异在 prompt 上下文构造）、提覆盖率（CoverUp 用 SlipCover 找未覆盖段、TELPA 借 Pynguin/CodaMosa 打难覆盖分支、AutoDev 在 HumanEval 达 99.3% 覆盖）、强化缺陷检测（MuTAP 以存活变异体为反馈、Mokav 生成差异暴露测试）。系统测试按被测对象（§4.4.2）：内核 KernelGPT 生成 syscall 规约交 Syzkaller、编译器 WhiteFox 双 agent 与 LLM4CBI、移动端 GPTDroid/DroidAgent/AXNav/InputBlaster/VisionDroid（唯一多模态 LLM）/AdbGPT/XUAT-Copilot、Web RESTSpecIT 推断 RESTful 规范、通用 Fuzz4All/PentestGPT/Fang et al.（15 个 one-day 漏洞利用基准）。挑战（§4.4.3）：类/项目级上下文增强难、与传统测试工具松耦合、目标过窄缺多维协同。
- **调试（§4.5 Debugging）**：故障定位（§4.5.1）AgentFL 四 agent（测试/源码审查员+架构师+测试工程师）三阶段（理解-导航-确认），AutoFL 单 agent 四个工具调用做根因解释。程序修复（§4.5.2）ChatRepair/CigaR（失败重启机制）/RepairAgent（状态机中间件）/AutoSD（模拟科学调试）/ACFix（智能合约访问控制）/FlakyDoctor（修 flaky test）/SRepair（双 agent）。统一调试（§4.5.3）FixAgent 四角色互为反馈、LDB 分块运行时分析。失败成因（§4.5.4）：项目上下文理解不足（AutoFL 大量轮次耗在理解自定义类/测试框架）、多步工作流不连贯（AutoSD 断点未命中却归咎测试）、上下文溢出/工具不兼容调用。挑战（§4.5.5）：仅靠失败测试判正确性、工具集成开销与结果不一致、多 agent 复杂度（AutoSD 生成 patch 约为 standalone LLM 的 5 倍耗时）、plausible patch 语义等价仍需人工。
- **IT 运维（§4.6 IT Operations）**：三种协作诊断策略——RCAgent 自一致性+嵌入投票（§4.6.1）、mABC 区块链启发投票的 Agent Chain（§4.6.2）、D-Bot 树搜索+多数投票（§4.6.3）；挑战（§4.6.4）是多维度监控调度、迭代探索开销、根因分析之外任务未开发。

### 2.4 SE 视角二：端到端两章（§4.7–§4.8）

- **端到端开发（§4.7 End-to-end Software Development）**：过程模型（§4.7.1）以瀑布为主流但各阶段内嵌迭代；敏捷含 TDD 与 Scrum（省略 Daily Scrum，可由 memory 机制替代），函数级基准实验显示 Scrum 最优最稳、TDD 次之。角色（§4.7.2）分 manager/需求/设计/开发/QA/部署/助手七类，创建方式分预定义与任务自适应（AutoAgents、AgentVerse、Talebirad et al. 可动态派生角色）。协作（§4.7.3）：整体流水线全用垂直架构（leader 分派-汇总），部分阶段引入水平协作（ChatDev 双 agent 对话、CTC 多团队并行淘汰）；通信协议分直接对话与结构化文档/图表（MetaGPT 共享信息池，避免多轮对话失真）。评估（§4.7.4）：8 篇仍用 HumanEval/MBPP 函数级基准，5 个项目级基准 SRDD/CAASD/SoftwareDev/SketchEval/ProjectDev 复杂度仍有限（多数项目输入 ≤60 词）；指标含执行验证（Pass Rate/Pass@K）、相似度（SketchBLEU）、成本（时长/token/费用/#sprints）、人工修订与代码规模。挑战（§4.7.5）：线性瀑布缺真正迭代演化、基本只支持 Python/简单 Web、缺标准化基准与指标。
- **端到端维护（§4.8 End-to-end Software Maintenance）**：通用流水线为 issue 定位→patch 生成→patch 验证三必备阶段 + 预处理（LingmaAgent 知识图谱、Agentless 目录树、MASAI 测试模板）、issue 复现（MASAI 两阶段模板示范）、任务分解、patch 排序等可选阶段（§4.8.1–§4.8.7）。定位四策略（§4.8.3）：检索型（MAGIS BM25 Top-K）、导航型（SWE-agent/MASAI 自主导航 vs AutoCodeRover/SpecRover 上下文引导 vs Agentless 层级定位）、频谱型（AutoCodeRover 用开发者测试 SBFL；CodeR 用自生成复现测试+BM25 融合，发现 SBFL 单独用时低于与 BM25 结合，归因于测试质量差异）、模拟型（LingmaAgent 用 MCTS 在仓库知识图谱上排序路径）。验证与排序（§4.8.6–§4.8.7）：代码评审、静态检查、动态检查（复现/回归测试）、多 patch 排序（MASAI ranker、Agentless 归一化+多数投票、SpecRover 选择 agent、DEIBase 集成多专家+LLM 评审委员会）。基准演化（§4.8.8）：Defects4J（357 bug、5 项目、92.41% patch 只改单文件）与真实用户报 issue 场景差距大 → SWE-bench（2,294 issue/12 个 Python 仓库）→ Lite/LiteS/Verified 子集与 SWE-bench-java-verified 转移构建。性能观察：完全自主定位的 SWE-agent 在 SWE-bench Lite 上表现最差；采用动态验证+patch 排序的 Agentless/MASAI/SpecRover/DEIBase 位居前列；用传统故障定位管线的 Agentless 反超多数 agentic 方案，对复杂 agent 设计的有效性评估提出更高要求。挑战（§4.8.9）：issue 描述非结构化/多模态、复现机制不可靠、patch 正确性判定歧义。

### 2.5 Agent 视角：四组件、多 agent 与人机协作（§5）

- **Planning（§5.1.1 Planning）**：四个维度——单/多 planner（单 planner 开销小但易幻觉；多 planner 互纠但增 token 与时延）、单/多轮（多轮 ReAct 式按环境反馈调整计划，但轨迹累积可能超出上下文）、单/多路径（多路径赋予试错能力但成本高）、计划表示（自然语言/半结构化如 JSON 与代码骨架/图如 PentestGPT 任务树与 LATS 搜索树）。挑战：计划幻觉（操作不存在的方法/循环步骤）、复杂任务可靠性不足（CoCoST 显示单函数复杂度升高时规划贡献显著下降；Flows 显示给一小段人类计划片段可使竞赛编程从 26.9%→74.5%、47.5%→80.8%）、缺乏对规划本身的细粒度评估。
- **Memory（§5.1.2 Memory）**：四维分类——时长（短期：对话记录/Action-Observation-Critique/中间输出；长期：轨迹蒸馏摘要与捷径抽取、选择性存储关键数据，Reflexion 滑窗上限 3 条防超 prompt 窗口）、归属（专有 vs 共享，共享似黑板系统，MetaGPT 共享消息池）、格式（自然语言/编程语言/结构化消息/键值对/嵌入/树/图像，VisionDroid 存截图）、操作（写入：蒸馏+淘汰，Co-Learning 按信息量阈值过滤、按使用频率淘汰；读取：reflection/retrieval/subscription，过滤准则 recency/relevance/similarity，DroidAgent 取 20 条最近任务摘要+5 条最相似知识）。挑战：信息抽象级别权衡、上下文匹配时机、缺独立模块级评估。
- **Perception（§5.1.3 Perception）**：文本输入为主（自然语言指令+代码上下文，仓库级任务靠导航补全）；视觉输入集中在 GUI 测试（XUAT-Copilot 用 SegLink++/ConvNeXts、AXNav 用 Screen Recognition、VisionDroid 用多模态 LLM），view hierarchy 冗余干扰决策，纯截图又有遮挡/简洁问题，现有工作均视觉+文本并用。
- **Action（§5.1.4 Action）**：工具分类学——搜索（Web 搜索 DuckDuckGo/SerpAPI vs 本地知识库：BM25 稀疏、稠密嵌入、关键词匹配、模型生成式检索如 MapCoder）、文件操作、GUI 操作、静态分析（AST tree-sitter/ANTLR、CFG、调用图、数据流图、代码依赖图、补全 token 语言服务器 Jedi/EclipseJDTLS、质量检查 GCC/Black/OClint/Frama-C/Slither 等）、动态分析（插桩方法调用轨迹、断点取运行时值、覆盖率 SlipCover/Pynguin/Gcov）、测试工具（PyTest/JUnit 验证、Pynguin 生成、MutPy 变异）、故障定位工具（GZoltar）、版本控制。工具开销控制实践：ToolCoder 限搜索延迟 0.6 秒、SWE-agent 限检索结果 50 条、LingmaAgent 限 600 次搜索迭代且最长 300 秒。
- **Foundation LLM（§5.1.5 Foundation LLMs）**：agent 不绑定特定 LLM，但对基座有五类要求——指令遵循/规划/多轮对话、工具使用能力、开源可微调（ToolCoder/ToolGen）、长上下文（CodeS 指出 200K token 对仓库级任务仍可能不足）、强多步推理（端到端维护 agent 全部依赖 GPT-4/GPT-4o/Claude-3.5-Sonnet 级闭源模型）；基座差距无法被架构完全弥补（Self-Refine 在 GPT 系表现好，在 Vicuna-13B 上常输出格式错误/重复/幻觉）。
- **多 agent 系统（§5.2 Multi-agent System）**：59.7% 的 SE agent 为多 agent。角色分类学（§5.2.1）：manager（任务分解/决策/团队组织）、需求分析、设计、开发、QA（评审员/测试员/调试员）、部署、助手；50 个单 agent 工作中仅 12 个用角色扮演 prompt 且形式简单。协作拓扑（§5.2.2）：分层、循环（生成-验证双角色回路）、星型（中心调度，AutoDev 的 Round-Robin/Token-Based/Priority-Based 调度）、树型（SoA 母-子 agent 派生）、网状（3DGen 基于 AutoGen 群聊）；规模化瓶颈及对策——限制派生数量（AutoAgents/AgentVerse 实际至多 4 个、SoA 树深限 2）或任务规模（MAGIS 按 SWE-bench 平均 1.7 个待改文件派生开发者）；MacNet 显示在 MMLU/HumanEval 等流行基准上性能会饱和、与拓扑无关。信息流（§5.2.3）：单向传递（解耦、最常用）与双向聊天（共享对话史）；ChatDev 混合两式。真实应用（§5.2.4）：MultiDevin（1 管理者+最多 10 worker 并行开发合并 PR）、Amazon Bedrock、CrewAI、Swarm、AgentScope。
- **人机协作（§5.3 Human-Agent Collaboration）**：人类介入四阶段——规划（low-code LLM 修改工作流；Flows 人类简短 oracle 计划优于 AI 反馈方案）、需求（ClarifyGPT 澄清歧义、AISD 修订用例）、开发（CodeS Extended 三层草图逐层可编辑、ART 修正子步输出）、评估（AISD/Prompt Sapper 人工验收测试）。讨论：现有人机协作为 agent 中心的固定阶段触发，human-driven workflow 是开放问题。

### 2.6 挑战、未来方向与威胁效度（§6; §7; §8）

- 七大研究方向（§6 RESEARCH OPPORTUNITIES）：(1) 评估——细粒度指标（错误类：错误动作比/平均调试迭代/回溯率；进度类：各阶段完成率）+可信属性（鲁棒/安全/公平）+成本（仅 46.7% 论文显式考虑效率）；基准需更真实（SWE-bench 有描述含糊问题，77.8% 任务有经验工程师 1 小时内可完成）。(2) 人机协作扩展到架构设计/测试生成/代码评审/端到端维护及界面机制。(3) 感知模态（仅 VisionDroid 用多模态 LLM；语音/手势未开发）。(4) 覆盖更多 SE 任务（设计、验证、特性维护缺 agent）。(5) 训练 software-oriented LLM（利用设计/架构/开发者讨论/历史变更/运行时数据）。(6) 将 SE 专业知识融入 agent 构建（工具集成、过程模型约束工作流——Agentless 与 OpenAI 均证实简单传统管线可胜过复杂自主 agent；用 SE 质量保障技术构建可信 agent）。优先级：标准化基准与指标最高，software-oriented LLM 是长期方向。
- LLM agent vs standalone LLM（§7.1）：agent 在方法级（HumanEval）、竞赛级（LiveCodeBench）、仓库级（CodeAgentBench）代码生成上 pass@1 一致更高，并在 IT 运维、端到端开发/维护等环境依赖任务上填补 standalone LLM 的空白。
- 威胁效度（§7.2 Threats to Validity）：人工筛选主观性；部分策略证据薄弱——RE 多 agent 策略 3 篇中 2 篇未同行评审、知识增强漏洞检测 4 篇仅 1 篇已发表、单测覆盖率迭代 3 篇仅 1 篇已发表、视觉输入 3 篇仅 1 篇已发表、结构化消息记忆仅 MetaGPT 已发表、图像记忆仅未发表的 VisionDroid。
- 结论（§8 CONCLUSION）：对 124 篇文献完成 SE + agent 双视角系统综述并指出开放挑战与方向。

> 锚点：§4.2 Code Generation; §4.8 End-to-end Software Maintenance; §5.1 Agent Framework; §5.2 Multi-agent System; §6 RESEARCH OPPORTUNITIES; §7 DISCUSSION。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 收录论文总数 | 124 篇（关键词 67 + 滚雪球 41 + 作者反馈 16） | §3.3 |
| 关键词检索规模 | 57 次 DBLP 搜索，10,362 命中（2024-07-01） | §3.2.1 |
| SpecGen 规约生成 vs 基线 | 较纯 LLM 方法 +15.84%，较 Houdini +47.01%，较 Daikon +53.76% | §4.1.2 |
| GPTLens 智能合约漏洞检测率 | 76.9%（13 个真实智能合约） | §4.3.1 |
| AutoDev 单测覆盖率 | 99.3%（HumanEval 数据集，与人工测试覆盖率相当） | §4.4.1 |
| ChatRepair 正确修复率 | 162/337（Defects4J）、80/80（QuixBugs） | §4.5.2 |
| RepairAgent 修复数 | Defects4J 上修 164 bug，其中 39 个为既有技术未修 | §4.5.2 |
| AutoCodeRover 引入 SBFL 前后 | issue 解决率 17.00% → 20.33%（SWE-bench Lite，开发者测试为测试套件） | §4.8.3 |
| SWE-bench 基准规模 | 2,294 个真实 GitHub issue，12 个 Python 仓库；SWE-bench-java-verified 为 91 issue/6 Java 项目，最佳解决率 9.89%（9/91，SWE-agent + DeepSeek-Coder） | §4.8.8 |
| Flows 人类计划片段增益 | 竞赛编程 novel problems：26.9%→74.5%、47.5%→80.8% | §5.1.1 |
| 多 agent 系统占比 | 59.7%（现有 SE agent 中） | §5.2 |
| 显式考虑效率（时间/token/成本）的论文占比 | 46.7% | §6 |
| Self-Refine 失败归因 | 33% 案例反馈定位错错误位置，61% 案例给出不当修复 | §4.2.3 |
| 自然语言反馈每轮增益 | 绝对性能 +2–17%（每增加一轮 NL 反馈，各模型均受益） | §4.2.2 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2409.02977（v2，TOSEM 综述） |
| 文献列表仓库 | https://github.com/FudanSELab/Agent4SE-Paper-List（124 篇论文持续维护列表） |
| 基准（论文内盘点） | SWE-bench 系（§4.8.8，含 Lite/LiteS/Verified/java-verified）、SRDD/CAASD/SoftwareDev/SketchEval/ProjectDev（§4.7.4 Table 12）、Defects4J/HumanEval/MBPP |
| 代表性系统（§4–§5 各表） | MetaGPT、ChatDev、Agentless、SWE-agent、MASAI、AutoCodeRover、CodeR、SpecRover、DEIBase、LingmaAgent；AgentFL/AutoFL；ChatRepair/RepairAgent/FixAgent/LDB；CoverUp/TELPA/MuTAP；KernelGPT/WhiteFox/Fuzz4All/PentestGPT；GPTLens/IRIS/LLift；RCAgent/mABC/D-Bot 等 |
| 关联综述 | 本目录 04 号（MAS for SE）、SEforLLM/03（LLM→Agent for SE） |

## 5. 一句话索引（给 Agent 用）

> 复旦/NTU/UIUC 的 TOSEM 综述（arXiv:2409.02977v2）以"SE 任务（需求/生成/静态检查/测试/调试/运维/端到端开发与维护）× agent 组件（planning/memory/perception/action）"双视角梳理 124 篇 agent for SE 文献（59.7% 为多 agent）。关键结论：单 LLM 须 agent 化才能胜任端到端任务；双 planner 不优于单 planner；工具+模型混合反馈最常见有效；SWE-bench Lite 上动态验证+patch 排序者（Agentless/MASAI/SpecRover/DEIBase）居前、全自主 SWE-agent 最差，简单传统管线反超复杂 agent——SE 领域知识约束工作流有价值。
