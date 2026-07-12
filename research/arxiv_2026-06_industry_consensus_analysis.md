# 2026 年 6–7 月 arXiv 论文趋势分析：AI 编程 Agent、代码图谱、上下文工程与 GraphRAG

> 基于 10 篇 2026 年 6–7 月 arXiv 论文全文提取与归纳  
> 分析范围：AI 编程 Agent / Agent Harness、代码图谱与多模态仓库理解、长程上下文工程、GraphRAG / 知识工程  
> 报告日期：2026-07-12

---

## 一、分析对象与方法

### 1.1 论文清单（10 篇）

| 编号 | 论文 | 第一作者/团队 | 主题归类 | arXiv ID |
|------|------|---------------|----------|----------|
| 1 | LLM-as-Code: Agentic Programming for Agent Harness | Junjia Qi, CityU + Tencent Jarvis Lab | Agent 架构 / 控制流 | 2606.15874 |
| 2 | ActPlane: Programmable OS-Level Policy Enforcement for Agent Harnesses | Yusheng Zheng, UCSC/VT/HKUST/eunomia-bpf/Alibaba | Agent 安全 / 策略执行 | 2606.25189 |
| 3 | LLM Agents Can See Code Repositories | Dongjian Ma, SJTU (Xiaodong Gu 团队) | 多模态代码图谱 / 仓库理解 | 2606.14061 |
| 4 | TICoder: A Repository-Level Code Generation Framework with Test-Driven Planning and Implementation-Aware Reuse | Siyu Nan, WHU | 仓库级代码生成 / RAG / 复用 | 2606.08135 |
| 5 | SWE-Explore: Benchmarking How Coding Agents Explore Repositories | Shaoqiu Zhang, SJTU (Xiaodong Gu 团队) | 仓库探索 / 定位 / 评测 | 2606.07297 |
| 6 | RepoRescue: An Empirical Study of LLM Agents on Whole-Repository Compatibility Rescue | Zhihao Lin, BUAA + SMU (David Lo) | 兼容性救援 / 实证研究 | 2607.01213 |
| 7 | TokenMizer: Graph-Structured Session Memory for Long-Horizon LLM Context Management | Shweta Mishra | 长程上下文 / 会话图谱 | 2606.06337 |
| 8 | Organize then Retrieve: Hierarchical Memory Navigation for Efficient Agents (HORMA) | Hao-Lun Hsu, Duke + Snowflake AI Research | 长程上下文 / 层次记忆 | 2606.11680 |
| 9 | LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via a Proprioceptive Dashboard (VISTA) | Binyan Xu, CUHK + Tencent Lightspeed | 长程上下文 / 自管理上下文 | 2606.30005 |
| 10 | Core-based Hierarchies for Efficient GraphRAG | Jakir Hossain, University at Buffalo (Ahmet Erdem Sarıyüce) | GraphRAG / 知识图谱层次化 | 2603.05207v2 |

### 1.2 分析方法

- 使用 `pdftotext` 提取全部 PDF 正文，合并为约 152 KB 的文本语料。
- 按主题归类后，从 **问题定义、核心论点、方法创新、实验结论、对本项目的启示** 五个维度进行归纳。
- 重点识别跨论文的 **共识（consensus）** 与 **分歧（controversy）**，以判断领域演进方向。

---

## 二、核心共识（Industry Consensus）

### 共识 1：LLM 不应是编排器，控制流应当外化为可确定执行的程序

**代表论文**：LLM-as-Code（Qi et al., 2606.15874）

该论文提出了一个强烈的架构性主张：当前主流 Agent 框架（ReAct、AutoGen、OpenHands、MetaGPT）把 LLM 放在 orchestrator 位置，导致三个结构性病症：

1. **Token explosion**：每一步历史都重新喂入，上下文随步数线性增长。
2. **Control-flow hallucination**：LLM 自己决定循环、分支、终止，无法保证执行路径。
3. **Unreliable completion**：采样决策的误差会在长程任务中复合。

作者认为这些不是实现 bug，而是 **把确定性控制流委托给概率模型** 的类别错误（category error）。解决方案是 **Agentic Programming / LLM-as-Code**：程序控制所有控制流，LLM 仅作为可调用的自适应组件；执行历史变成调用树的 DAG，每个调用的上下文长度由调用深度决定，而非步数累积。

**跨论文呼应**：
- ActPlane 进一步强化：即使 LLM 被调用，**策略（policy）** 也必须在 OS 内核层被确定性地编译和执行，而不是依赖模型遵循自然语言指令。
- RepoRescue 的实证也发现：当运行时禁止编辑测试时，Kimi 仍能在 41.5% 的仓库上完成兼容性救援，说明 **确定性约束可以显著提升 Agent 行为的可靠性**。

> **对本项目的启示**：我们在设计 AI 编程 Agent 时，应把“规划、循环、分支、验证、提交”等控制流写成显式程序或状态机，而不是全部交给 LLM 采样；LLM 只负责需要推理/生成的节点。

---

### 共识 2：Agent 的“策略/规则”不能仅靠提示词遵守，必须下沉到可执行的系统层

**代表论文**：ActPlane（Zheng et al., 2606.25189）

ActPlane 对 64 个包含 CLAUDE.md / AGENTS.md 的热门项目进行了语句级实证分析，发现：

- **64% 的语句是行为策略（policy）**，而非描述性上下文；
- **83% 的策略涉及系统级动作**（文件、网络、进程）；
- **74% 的策略依赖任务上下文**，无法静态预定义；
- **81% 的项目包含跨事件策略**（如“提交前必须先跑测试”）。

现有工具层拦截（tool-call guardrails）无法覆盖间接执行路径（如 Agent 写的脚本内部调用 git commit），OS 沙盒只能返回不透明错误（EPERM）。ActPlane 的解决方案是：

- 让最接近任务的 Agent 根据上下文生成 **具体策略 DSL**；
- 通过 eBPF 在 OS 内核层执行信息流控制（IFC）；
- 提供语义化反馈（如“blocked: commit without tests; run npm test first”）。

> **对本项目的启示**：AGENTS.md / CLAUDE.md 中的规则需要一条从“自然语言意图 → 具体 DSL → 内核/运行时执行”的桥接路径。未来的 Agent Harness 必须内置可编程策略引擎，而不是把规则仅作为 prompt 的一部分。

---

### 共识 3：代码仓库不应只被看作文本序列，结构化/视觉化表示是下一代 Agent 的必需品

**代表论文**：LLM Agents Can See Code Repositories（Ma et al., 2606.14061）

这是第一个系统性研究 MLLM 在仓库级任务上的工作。核心发现：

- **纯视觉输入不足以替代文本**：vision-only 模式在所有模型上显著降低准确率（Doubao 从 51% 降到 16.9%），且 token 成本反而暴涨（Doubao +268%）。
- **文本 + 可视化结构图作为补充模态** 能同时降低成本并维持/提升效果：
  - GPT-5-mini：输入 token -25%，成本 -26%，Pass@1 +0.4%；
  - Kimi K2.5：Pass@1 从 68.8% 提升到 70.6%，成本 -3%。
- **图（Graph）布局在三种可视化策略中效率最优**（-25% input tokens, -26% cost）。
- **视觉工具在故障定位（fault localization）阶段最有效**。

该研究把仓库建模为异构图 `G = (V, E, A, R)`，节点类型包括文件、类、函数，边类型包括 contains、imports、inherits、invokes，并用 Graphviz 渲染子图作为视觉输入。

**跨论文呼应**：
- SWE-Explore 也强调：现有 end-to-end 评测把“探索、定位、修复”混为一谈，掩盖了 Agent 在 **仓库探索** 阶段的真实能力。
- TICoder 使用 AST 构建多关系依赖图，并通过结构感知检索提升仓库级代码生成。

> **对本项目的启示**：代码图谱不仅是检索增强的辅助，而是 Agent 感知仓库的核心界面。应把 AST/依赖图/调用图可视化，作为文本之外的第二模态，并在探索与定位阶段优先使用。

---

### 共识 4：长程上下文管理正在从“压缩/截断文本”转向“结构化状态 + 可导航记忆”

这是本次检索中最密集的共识，三篇论文从不同角度 converged：

#### 4.1 会话历史应被建模为带类型的知识图谱

**代表论文**：TokenMizer（Mishra, 2606.06337）

TokenMizer 把会话历史维护为一个 **typed knowledge graph**，包含：

- 14 种节点类型（TASK、FILE、ERROR、DECISION、GOAL、ENVIRONMENT 等）；
- 7 种边类型（DEPENDS_ON、RELATED_TO、IMPLEMENTS、FIXES、BLOCKS、PART_OF、SUPERSEDES）；
- 8 状态生命周期（含 SUPERSEDED、INVALIDATED、ARCHIVED 等修订状态）；
- 双时态有效性区间（bitemporal validity），支持时间旅行查询；
- 决策转换记录（DecisionTransition）：保留“为什么从 PostgreSQL 切换到 SQLite”。

在上下文边界处，它用 token-budgeted 的图序列化替代原始对话记录，实验显示：

- 任务召回率与 plain summary 持平（75.6%）；
- 决策召回率更高（85.0% vs. 70.0%）；
- 文件召回率 100%（vs. 91.7%）。

#### 4.2 记忆应被组织为层次化文件系统，并通过导航式 Agent 检索

**代表论文**：HORMA（Hsu et al., 2606.11680）

HORMA 把记忆构建与检索解耦：

- **记忆构建**：将原始轨迹组织成文件系统式的层次笔记，摘要与原始轨迹通过 provenance 链接；
- **检索**：训练一个轻量级 RL Agent，使用 `ls/cd/grep/cat/select/done` 等 Bash 工具在记忆树中导航，选择最小且充分的上下文。

在 LoCoMo 和 LongMemEval 上，HORMA 仅用 baseline **1.24%–22.17%** 的 token，同时保持或提升性能。

#### 4.3 上下文管理需要让 Agent 感知自身上下文状态

**代表论文**：VISTA（Xu et al., 2606.30005）

VISTA 提出 **context proprioception（本体感知）**： frontier LLM 无法从 prompt 中感知“每个块多大、多旧、被访问多少次、剩余预算多少”，因此无法做出合理的 keep/archive 决策。VISTA 通过 dashboard 暴露：

- 每块的 token 成本、recency、访问历史；
- 剩余预算；
- 可归档为外部 payload（无损）并通过 handle 恢复。

实验：在 LOCA-Bench 上，Gemini-3-Flash 从 22.7% 提升到 50.7%；BrowseComp-Plus 达到 58.0%；且该层无需训练、可跨模型迁移。

**跨论文呼应**：
- LLM-as-Code 的 DAG 上下文本质上也把历史从 flat transcript 变成结构化调用图。
- ActPlane 的策略状态也需要跨操作持久化。

> **对本项目的启示**：我们正在研究的“上下文工程”不应停留在 prompt 压缩，而应升级为 **会话状态图 + 层次记忆 + 本体感知 dashboard** 的体系化设计。

---

### 共识 5：评测正在从 end-to-end pass/fail 分解为细粒度能力评测

**代表论文**：SWE-Explore（Zhang et al., 2606.07297）

SWE-Explore 指出 SWE-bench 把“探索、定位、修复、验证”压缩为一个二值指标，掩盖了失败根因。它把 **repository exploration** 单独抽出来评测：给定 issue 和仓库，Agent 返回排序的代码区域列表，与成功轨迹实际访问的代码行对齐。核心发现：

- 现代方法在 **文件级定位** 已较强；
- **行级覆盖（line-level coverage）** 和 **高效排序（efficient ranking）** 才是区分 SOTA 探索者的关键维度。

**跨论文呼应**：
- RepoRescue 也引入了 source-only audit、runtime-blocked regime、scenario validation 等多维度评估。
- TICoder 把测试用例引入 planning 阶段，说明行为验证需要前置到中间步骤。

> **对本项目的启示**：如果我们构建代码 Agent 评测，应设计 **探索质量、定位精度、策略合规、上下文效率** 等细粒度指标，而非只看最终 patch 是否通过测试。

---

### 共识 6：GraphRAG 的层次化社区发现需要更稳定、可解释、可控的拓扑方法

**代表论文**：Core-based Hierarchies for Efficient GraphRAG（Hossain & Sarıyüce, 2603.05207v2）

该论文证明：在稀疏知识图上，基于模块度（modularity）的 Leiden 算法存在 **指数级数量的近似最优划分**，导致社区结构不稳定、不可复现。作者提出用 **k-core decomposition** 替代 Leiden：

- 确定性、线性时间、密度感知的层次结构；
- 适合稀疏知识图（平均度为常数、多数节点低度）；
- 配合 token-budget-aware 采样，降低 LLM 成本。

实验在 earnings transcripts、news、podcasts 等真实数据上，使用 3 个 LLM 生成答案、5 个独立 LLM judge 进行头对头评估，结果显示该方法在 **comprehensiveness** 和 **diversity** 上稳定提升，同时降低 token 使用。

> **对本项目的启示**：如果我们把 API 文档、代码依赖、知识库构建为 GraphRAG，应优先考虑 k-core 等拓扑稳定的层次化方法，而不是直接套用 Leiden/Louvain。

---

## 三、热点方向（Hot Directions）

### 方向 1：Agentic Programming / LLM-as-Code 范式

- 将控制流从 LLM 中剥离，写入确定性程序；
- LLM 仅作为函数/节点被调用；
- 执行历史是 DAG/调用树，上下文随深度而非步数增长。

**与本项目关系**：AI 编程 Agent 的“规划-执行-验证-提交”流程非常适合用该范式重新设计。

---

### 方向 2：可编程、可执行、内核级 Agent 策略引擎

- 从 AGENTS.md / CLAUDE.md 自动提取策略；
- 生成具体 DSL；
- 在 OS/运行时层用 eBPF/IFC 强制执行；
- 提供语义反馈而非 EPERM 式 opaque denial。

**与本项目关系**：我们项目中的“规则/约束/最佳实践”需要一条从文本到执行的闭环。

---

### 方向 3：多模态仓库理解（Vision + Graph + Text）

- 用 AST/静态分析构建多关系依赖图；
- 将子图渲染为图像，与文本代码共同输入 MLLM；
- 视觉辅助在探索和定位阶段最有效；
- 图布局优于嵌套/表格布局。

**与本项目关系**：代码图谱的可视化应成为 Agent 交互界面的一部分。

---

### 方向 4：长程上下文工程的三层架构

| 层级 | 代表工作 | 核心能力 |
|------|----------|----------|
| 会话状态图 | TokenMizer | 类型化节点/边、生命周期、决策转换、时间旅行 |
| 层次记忆导航 | HORMA | 文件系统式记忆、RL 导航 Agent、最小充分上下文 |
| 本体感知 dashboard | VISTA | per-block 元数据、无损归档/恢复、跨模型迁移 |

未来 Agent 的上下文系统很可能是这三者的融合。

---

### 方向 5：细粒度、轨迹驱动的仓库探索评测

- 从成功 Agent 轨迹中提取行级 ground truth；
- 评测覆盖、排序、上下文效率；
- 与下游修复能力做相关性验证。

**与本项目关系**：可用于评估我们代码 Agent 的“上下文检索/定位”模块。

---

### 方向 6：稳定拓扑驱动的 GraphRAG 索引

- 用 k-core / 其他确定性拓扑分解替代模块度聚类；
- 构建可解释、可复现的层次社区；
- token-budget-aware 采样降低生成成本。

**与本项目关系**：API 文档知识图谱、代码依赖图谱均可采用此类索引策略。

---

## 四、值得关注的分歧与开放问题

### 分歧 1：LLM 是否应保留一定的控制流能力？

- LLM-as-Code 持强硬立场：LLM 不应是 orchestrator。
- 但 HORMA、VISTA 仍让 LLM/轻量 Agent 参与记忆管理与上下文决策。
- **开放问题**：在高度不确定的探索性任务中，完全外化控制流是否会牺牲灵活性？如何平衡 determinism 与 adaptivity？

### 分歧 2：视觉模态在代码理解中的角色

- SeeRepo 证明 vision-only 不够，但 text+vision 有效。
- 仍有争议：视觉收益主要来自“空间布局”还是“迫使 Agent 减少无效文本读取”？
- **开放问题**：视觉表示的标准化（Graphviz、Mermaid、自定义渲染）与模型无关性。

### 分歧 3：记忆构建是否应被显式优化？

- HORMA 把记忆构建视为 skill evolution，用对比学习持续优化。
- TokenMizer 采用确定性启发式，默认不做 LLM 调用。
- VISTA 完全不做训练，只暴露元数据。
- **开放问题**：什么情况下需要学习/优化记忆构建，什么情况下应保持确定性与低成本？

### 分歧 4：GraphRAG 中“社区”的定义

- 传统 GraphRAG 用模块度社区；
- Core-based GraphRAG 用 k-core 层次；
- 两者对“全局 sensemaking”的定义不同：前者强调主题聚类，后者强调连接密度与关系 richness。
- **开放问题**：在代码/API 文档场景中，哪种结构更符合人类开发者的认知？

---

## 五、对本项目的具体建议

### 5.1 架构层面：采用 Agentic Programming 范式

- 将“需求解析 → 代码探索 → 修改规划 → 编辑执行 → 测试验证 → 提交”定义为状态机或工作流图；
- LLM 仅作为各节点的推理/生成调用；
- 控制流由程序保证，避免控制流幻觉。

### 5.2 上下文层面：构建三层上下文系统

1. **会话状态图**：记录任务、决策、文件、错误、环境等节点及关系，支持决策 supersede/invalidate。
2. **层次记忆/索引**：将代码仓库、历史会话、最佳实践组织为可导航的层次结构。
3. **本体感知 dashboard**：让 Agent 感知当前上下文预算、各块大小/年龄/访问频率，支持无损归档。

### 5.3 代码理解层面：引入多模态图谱

- 用 AST/静态分析构建代码依赖图；
- 提供 Graphviz 渲染的视觉子图作为 Agent 输入；
- 在探索和定位阶段优先使用视觉化结构图。

### 5.4 策略层面：将规则从 prompt 下沉到可执行层

- 将项目规则（如“修改 API 必须同步文档”）表示为可执行策略；
- 在 Agent Harness 或运行时层面强制执行；
- 对违规给出语义化反馈。

### 5.5 评测层面：设计细粒度指标

- 行级定位覆盖率、排序质量、上下文 token 效率；
- 策略合规率；
- 决策稳定性（是否重复已废弃决策）；
- source-only / runtime-blocked / scenario validation 等多维度验证。

### 5.6 知识工程层面：探索 k-core 等稳定拓扑方法

- 在 API 文档知识图谱、代码依赖图谱中比较 Leiden 与 k-core 的社区稳定性；
- 设计 token-budget-aware 的摘要/采样策略。

---

## 六、结论

2026 年 6–7 月的这 10 篇论文共同指向一个趋势：**AI 编程 Agent 正在从“让 LLM 自己决定一切”的 ReAct 范式，转向“程序控制确定性结构、LLM 负责概率性推理”的 Agentic Programming 范式**。与此同时，上下文工程、代码图谱、策略执行、GraphRAG 等子领域都在向 **结构化、可解释、可执行、可评测** 的方向收敛。

对本项目而言，最核心的机会是：

1. 把“控制流外化 + LLM-as-Code”作为 Agent 架构底座；
2. 把“代码图谱 + 视觉化 + 文本”作为仓库理解界面；
3. 把“会话状态图 + 层次记忆 + 本体感知”作为上下文工程框架；
4. 把“可执行策略引擎”作为合规与安全的保障；
5. 把“细粒度轨迹驱动评测”作为迭代依据。

这些方向与我们正在研究的“AI 代码生成上下文控制、API 文档知识图谱、软件详设提取为图谱”高度契合，建议作为下一阶段的重点探索方向。

---

## 附录：引用与原文关键句摘录

### LLM-as-Code
> "The only construction that guarantees a loop executes n times is to write the loop."  
> "These pathologies persist across models, frameworks, and prompting strategies because they originate in the architecture rather than the implementation."

### ActPlane
> "64% of statements are policies, 83% involve system actions, and 74% depend on context that cannot be pre-defined statically."  
> "Tool-call guardrails miss indirect system actions... OS sandboxes control resource access instead of actions."

### SeeRepo
> "Vision-only interaction significantly degrades resolution accuracy... Integrating SeeRepo as a supplementary modality significantly reduces token cost while maintaining or improving resolution accuracy."  
> "Visualization is most effective when invoked at the fault localization stage."

### TokenMizer
> "Session history is a structured knowledge artifact and should be stored as one."  
> "What survives a context boundary is then not 'whatever text was recent or similar' but the session's actual state."

### HORMA
> "Explicitly decoupling memory management and retrieval yields a more efficient, interpretable, and scalable mechanism for working memory."  
> "HORMA uses only 3.07%–22.17% of baseline token usage on long conversation tasks."

### VISTA
> "Frontier language models are proprioceptively blind to their own context."  
> "Lossless recovery is necessary under budget pressure."

### Core-based GraphRAG
> "On sparse knowledge graphs... the number of near-optimal modularity partitions is exponential in the graph size."  
> "k-core decomposition yields a deterministic, density-aware hierarchy in linear time."

---

*报告结束*
