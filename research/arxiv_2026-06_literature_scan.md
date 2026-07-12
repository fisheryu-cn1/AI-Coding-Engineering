# arXiv 近期论文检索与评估报告（2026-06-01 以来）

> 基于 `references/README.md` 中的研究领域，检索 arXiv 上 2026-06-01 以来与 AI 编程、上下文工程、知识工程、代码图谱、本体工程相关的预印本，并从作者背景、引用情况、内容相关性三个维度评估是否值得收集和阅读。

---

## 1. 检索策略

1. **主题锚定**：以 `references/README.md` 中 7 个主题目录（AIOS、CodeGraph、ContextEngineering、KnowledgeEngineering、Ontology、PetriNets、llm_app_diagrams）为关键词骨架。
2. **时间范围**：2026-06-01 至 2026-07-12（当前日期）。
3. **检索方式**：
   - 使用 arXiv 公开搜索页面 + 网络检索（`site:arxiv.org` + 主题关键词 + `June 2026`）。
   - 通过 OpenAlex API 校验论文元数据（标题、作者、发表日期、citation count）。
   - 由于 arXiv 官方 API 近期 rate limit 极严，部分摘要通过 `FetchURL` 直接读取 arXiv 摘要页获取。
4. **筛选原则**：只保留 2026-06-01 之后首次提交（或 v2 显著更新）的论文；与项目研究主线（AI 编程 Agent、代码图谱、上下文/记忆管理、GraphRAG/KG）有直接方法论关联的优先纳入。

---

## 2. 整体结论（TL;DR）

- **共发现 13 篇值得关注的论文**，分布在：
  - Agentic 编程 / AIOS 治理（3 篇）
  - 代码图谱与仓库级代码生成（4 篇）
  - 上下文工程 / Agent 记忆（3 篇）
  - GraphRAG / 知识图谱构建（3 篇）
- **引用情况**：所有论文均为 2026-04 至 2026-07 的极新预印本，OpenAlex 显示 `cited_by_count = 0`，符合时间预期，因此**引用不能作为否定依据**。
- **推荐优先级**：
  - **必读（High）**：4 篇，与项目核心方向高度契合，作者团队可靠。
  - **选读（Medium）**：6 篇，方向相关但偏垂直或实证，可作为专题补充。
  - **暂不建议（Low）**：3 篇，领域相关但距项目当前主线较远或质量信号一般。

---

## 3. 推荐必读论文（High Priority）

### 3.1 LLM-as-Code: Agentic Programming for Agent Harness

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.15874 |
| **提交日期** | 2026-06-14 |
| **作者** | Junjia Qi, Zichuan Fu, Jingtong Gao, Wei Zhang, Hanyu Yan, Xian Wu, Xiangyu Zhao |
| **机构** | 待进一步确认（OpenAlex 未收录机构） |
| **引用** | 0 |
| **相关主题** | AIOS / Agentic Coding / Context Engineering |

**核心观点**：提出 *Agentic Programming* 范式——把循环、分支、序列等确定性控制流从 LLM 中剥离，交还给程序；LLM 仅作为“LLM-as-Code”的可调用组件，负责推理/生成。通过执行历史的调用树构建 DAG 上下文，每个调用的上下文长度由调用深度而非步数决定。

**与项目相关性**：极高。项目中的 `AIOS/` 与 `ContextEngineering/` 正是研究“AI 编程 Agent 的上下文控制与执行架构”。该文对“LLM 编排器导致 token 爆炸和控制流幻觉”的批判，与项目关注的上下文工程、Agent 可预测性直接相关。

**评估**：概念框架清晰，提出的范式转换对设计 Agent 操作系统或 harness 有启发。尽管作者机构未明，但论文定位与项目设计文档《AI代码生成上下文控制_设计分析框架.md》《Claude-Code-context-management.md》高度契合。**建议优先收集并精读。**

---

### 3.2 ActPlane: Programmable OS-Level Policy Enforcement for Agent Harnesses

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.25189 |
| **提交日期** | 2026-06-23 |
| **作者** | Yusheng Zheng, Tianyuan Wu, Quanzhi Fu, Tong Yu, Wenan Mao, Wei Wang, Dan Williams, Andi Quinn |
| **机构** | 待确认 |
| **引用** | 0 |
| **相关主题** | AIOS / Agent 安全 / 系统策略 |

**核心观点**：Agent harness 需要在 LLM 旁边执行“运行测试后再提交”这类策略，但现有工具调用护栏或 OS 沙箱都存在语义鸿沟。ActPlane 让 Agent 声明策略，并在 OS 内核层用 eBPF 强制执行，提供语义反馈与隔离，开销仅 1.9%–8.4%。

**与项目相关性**：高。项目的 `AIOS/` 关注“LLM as OS、Agentic Coding 趋势”，而 Agent 的安全与策略执行是 AI OS 的关键基础设施。该文提供了从策略意图到内核执行的完整工程路径。

**评估**：工程导向强，eBPF + 信息流控制 DSL 的实现对构建可信 AI 编程环境有参考价值。**建议收集，重点阅读其策略模型与实现架构。**

---

### 3.3 LLM Agents Can See Code Repositories

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.14061 |
| **提交日期** | 2026-06-12 |
| **作者** | Dongjian Ma, Silin Chen, Yufei Yang, Yuling Shi, Yanfu Yan, **Xiaodong Gu** |
| **机构** | 上海交通大学软件学院（Xiaodong Gu 团队） |
| **引用** | 0 |
| **相关主题** | CodeGraph / AI Software Engineering / 多模态 |

**核心观点**：首次系统研究“视觉化的代码仓库表示”对 LLM coding agent 的作用。纯视觉会显著降低准确率并增加 token 成本；但将仓库结构图作为文本之外的补充模态，可在保持或提升 issue 解决率的同时降低最多 26% 的输入 token。

**与项目相关性**：极高。项目的 `CodeGraph/` 目录专门收集“代码属性图、RepoGraph、代码-文本-代码规范”等资料。该文探索了代码图谱的**视觉呈现**对 Agent 的影响，与“代码图谱如何服务 AI 编程”直接相关。

**评估**：作者 Xiaodong Gu 是 LLM4SE 领域知名学者（上海交大教授，多篇 ICSE/ASE/FSE CCF-A 论文）。实验设计严谨（SWE-bench Verified），结论对代码图谱可视化与多模态交互有实践指导意义。**强烈推荐收集并精读。**

---

### 3.4 TokenMizer: Graph-Structured Session Memory for Long-Horizon LLM Context Management

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.06337 |
| **提交日期** | 2026-06-04 |
| **作者** | Shweta Mishra |
| **机构** | 待确认 |
| **引用** | 0 |
| **相关主题** | ContextEngineering / Agent 记忆 / 知识图谱 |

**核心观点**：把 LLM 会话历史建模为带类型的知识图谱（14 种节点、7 种边），通过三阶段检查点和 8 层压缩管线生成紧凑的 resume block（平均 78 token，比基线小 2 倍），在决策召回率上提升 9–17 个百分点。

**与项目相关性**：极高。项目的 `ContextEngineering/` 是核心研究方向之一，且《上下文工程_核心参考资料清单.md》专门汇总上下文工程文献。TokenMizer 的“图结构会话记忆”直接回应了“长会话上下文如何保留结构化决策信息”的问题。

**评估**：单作者论文，机构信息不明，但系统开源、实验覆盖 5 个领域，方法论与项目关注的“上下文工程”高度一致。**建议优先收集，作为上下文工程专题的补充案例。**

---

## 4. 推荐选读论文（Medium Priority）

### 4.1 TICoder: A Repository-Level Code Generation Framework with Test-Driven Planning and Implementation-Aware Reuse

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.08135 |
| **提交日期** | 2026-06-06 |
| **作者** | Siyu Nan, Yaling Luo, Jian Wang, Neng Zhang, Bing Li |
| **引用** | 0 |
| **相关主题** | CodeGraph / 仓库级代码生成 |

**核心观点**：提出测试驱动的迭代规划机制，以及结合功能相似性与实现相似性的双视角代码复用策略。在仓库级代码生成基准上平均提升 11.52%。

**与项目相关性**：高。与代码图谱、RAG for code、仓库级上下文管理均相关。

**评估**：方法完整，但与现有大量 Repo-level code generation 工作（RepoGraph、RepoHyper、GraphCoder 等）存在重叠。可作为专题补充阅读。**建议收集摘要与实验结论。**

---

### 4.2 SWE-Explore: Benchmarking How Coding Agents Explore Repositories

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.07297 |
| **提交日期** | 2026-06-05 |
| **作者** | Shaoqiu Zhang, Yuhang Wang, Jialiang Liang, Yuling Shi, Wenhao Zeng, Maoquan Wang, Shilin He, Ningyuan Xu, Siyu Ye, Kai Cai, **Xiaodong Gu** |
| **机构** | 上海交通大学（Xiaodong Gu 团队） |
| **引用** | 0 |
| **相关主题** | CodeGraph / Agent 评估 / 仓库探索 |

**核心观点**：构建专门评估 coding agent“仓库探索能力”的基准，覆盖 848 个 issue、10 种语言、203 个仓库，从覆盖率、排序、上下文效率三个维度评估。

**与项目相关性**：中高。代码图谱的最终价值之一是支撑 Agent 的仓库探索；该基准可作为评价代码图谱辅助效果的参考。

**评估**：Xiaodong Gu 团队出品，实验规模大。如果项目需要设计自己的 Agent 评估体系，值得参考。**建议选读。**

---

### 4.3 Organize then Retrieve: Hierarchical Memory Navigation for Efficient Agents (HORMA)

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.11680 |
| **提交日期** | 2026-06-10 |
| **作者** | Hao-Lun Hsu, Nikki Lijing Kuang, Boyi Liu, Zhewei Yao, Yuxiong He |
| **引用** | 0 |
| **相关主题** | ContextEngineering / Agent 记忆 |

**核心观点**：将经验组织成类文件系统的层级结构，通过 RL 训练的轻量 Agent 在层级中导航检索，长对话任务最多只用 22.17% 的 token。

**与项目相关性**：中。上下文工程方向相关，但主要面向通用 long-horizon agent，而非 specifically coding agent。

**评估**：方法有新意，但作者机构与代码/软件工程关联度不明。**建议泛读，作为上下文压缩与记忆管理的对比材料。**

---

### 4.4 LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via a Proprioceptive Dashboard (VISTA)

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.30005 |
| **提交日期** | 2026-06-29 |
| **作者** | Binyan Xu, Haitao Li, Kehuan Zhang |
| **引用** | 0 |
| **相关主题** | ContextEngineering / Agent 记忆 |

**核心观点**：LLM 对自身上下文“看不见、管不了”。VISTA 通过暴露每个上下文块的 token 用量、新鲜度、访问历史等运行时仪表盘，让模型自行管理上下文，在 LOCA-Bench 上将 Gemini-3-Flash 从 22.7% 提升到 50.7%。

**与项目相关性**：中高。上下文工程的核心问题之一正是“让模型/Agent 感知并管理上下文”。

**评估**：训练无关、模型无关的接口设计思路与项目追求的“上下文控制”理念一致。**建议选读，重点看其 dashboard 抽象。**

---

### 4.5 RepoRescue: An Empirical Study of LLM Agents on Whole-Repository Compatibility Rescue

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2607.01213 |
| **提交日期** | 2026-07-01 |
| **作者** | Zhihao Lin, Mingyi Zhou, Zhensu Sun, Yizhuo Yang, Renyu Yang, **David Lo**, Li Li |
| **机构** | 新加坡管理大学（David Lo 团队）等 |
| **引用** | 0 |
| **相关主题** | AIOS / Agentic Coding / 软件维护 |

**核心观点**：研究 LLM Agent 对“老旧仓库在新环境下兼容性修复”的能力，构建 193 个 Python + 122 个 Java 仓库的 RepoRescue 基准，比较 Claude Code、Kimi、GPT-5.2/Codex 等系统。

**与项目相关性**：中。属于 Agentic coding 的实证研究，但聚焦于兼容性救援而非代码图谱/上下文架构。

**评估**：David Lo 是软件工程领域资深教授（SMU）， empirical study 质量有保障。若项目关注 Agent 在真实维护任务中的表现，可参考。**建议选读，收集基准与方法。**

---

### 4.6 Core-based Hierarchies for Efficient GraphRAG

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2603.05207v2 |
| **提交日期（v2）** | 2026-06-02 |
| **作者** | Md Jakir Hossain, **Ahmet Erdem Sarıyüce** |
| **机构** | University at Buffalo |
| **引用** | 0 |
| **相关主题** | KnowledgeEngineering / GraphRAG |

**核心观点**：证明 GraphRAG 中 Leiden 社区检测在稀疏 KG 上存在指数级近优划分，导致不可复现；提出用 k-core 分解替代，得到确定性、密度感知的层级结构，并降低 token 成本。

**与项目相关性**：中。项目的 `KnowledgeEngineering/` 收集 GraphRAG 报告，k-core 层级对大规模知识图谱的全局感知任务有参考价值。

**评估**：Ahmet Erdem Sarıyüce 是图挖掘领域知名学者（University at Buffalo），在 k-core、中心性计算方面有深厚积累。论文偏算法/系统效率，若项目涉及 GraphRAG 的工程实现，**建议选读。**

---

## 5. 暂不建议优先阅读的论文（Low Priority）

### 5.1 ProjAgent: Procedural Similarity Retrieval for Repository-Level Code Generation

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2607.08691 |
| **提交日期** | 2026-07-09 |
| **作者** | Qihong Chen, Aaron Imani, **Iftekhar Ahmed** |
| **机构** | UC Irvine |
| **引用** | 0 |
| **相关主题** | CodeGraph / 仓库级代码生成 |

**核心观点**：提出“过程相似性”作为仓库级代码生成的检索信号，把目标函数分解为推理步骤并检索相似过程行为。

**评估**：Iftekhar Ahmed 是 UC Irvine 软件工程助理教授，研究方向可靠。但论文主要贡献是检索维度创新，与项目当前聚焦的“代码图谱构建、上下文控制、GraphRAG”相比，关系稍远。**可作为代码生成专题的后续补充，当前不建议优先收集。**

---

### 5.2 All Relations Lead to Rome: Automated Knowledge Graph Creation and Question Generation

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2606.22645 |
| **提交日期** | 2026-06-21 |
| **作者** | Matthijs Jansen op de Haar, Tobias Stähle, Lorenzo Gatti |
| **机构** | University of Twente（学生会议论文） |
| **引用** | 0 |
| **相关主题** | Ontology / KG 构建 |

**核心观点**：提出 ARLtR 框架，联合构建知识图谱、嵌入和面向事实的问答对，并以罗马帝国历史为实例发布数据集。

**评估**：概念框架与本体工程相关，但实例领域（罗马史）与 AI 编程/软件工程无关，且为学生会议（Twente Student Conference）。**暂不推荐优先收集。**

---

### 5.3 Beyond Predefined Schemas: TRACE-KG for Context-Enriched Knowledge Graph Generation

| 字段 | 内容 |
|------|------|
| **arXiv ID** | 2604.03496v2 |
| **提交日期（v2）** | 2026-06-15 |
| **作者** | Mohammad Sadeq Abolhasani, Yang Ba, Yixuan He, Rong Pan |
| **引用** | 0 |
| **相关主题** | Ontology / KG 构建 |

**核心观点**：在不依赖预定义本体的情况下，联合构建上下文丰富的知识图谱和诱导模式，保留对源证据的可追溯性。

**评估**：本体/KG 自动化构建方向相关，但论文未聚焦软件工程或代码领域，且方法上与现有 LLM-based KG 构建工作（AutoSchemaKG、LLM-empowered KG construction survey）重叠。**建议仅泛读摘要，作为本体工程的背景补充。**

---

## 6. 按项目目录的映射表

| 项目目录 | 高度相关论文 | 选读论文 |
|----------|-------------|----------|
| `AIOS/` | LLM-as-Code, ActPlane | RepoRescue |
| `CodeGraph/` | LLM Agents Can See Code Repositories | TICoder, SWE-Explore, ProjAgent |
| `ContextEngineering/` | TokenMizer | HORMA, VISTA |
| `KnowledgeEngineering/` | — | Core-based Hierarchies for Efficient GraphRAG |
| `Ontology/` | — | TRACE-KG, All Relations Lead to Rome |
| `PetriNets/` | — | 本次检索未发现 6 月以后直接相关论文 |

---

## 7. 收集建议与下一步行动

### 7.1 立即收集并精读（4 篇）

1. **2606.15874** — LLM-as-Code（Agentic 编程范式）
2. **2606.25189** — ActPlane（Agent 策略与 OS 级执行）
3. **2606.14061** — LLM Agents Can See Code Repositories（代码图谱可视化）
4. **2606.06337** — TokenMizer（图结构会话记忆）

**理由**：均直接命中项目核心研究线，且前两者面向 Agent 架构，后两者分别面向代码图谱与上下文工程，可形成“架构—表示—记忆”的互补阅读组合。

### 7.2 纳入专题补充包（6 篇）

5. **2606.08135** — TICoder
6. **2606.07297** — SWE-Explore
7. **2606.11680** — HORMA
8. **2606.30005** — VISTA
9. **2607.01213** — RepoRescue
10. **2603.05207v2** — Core-based Hierarchies for Efficient GraphRAG

### 7.3 暂不收集（3 篇）

11. **2607.08691** — ProjAgent
12. **2606.22645** — All Relations Lead to Rome
13. **2604.03496v2** — TRACE-KG

---

## 8. 数据说明与局限

- **引用数**：所有候选论文在 OpenAlex 中 `cited_by_count = 0`，因发表时间不足 2 个月，符合预期；无法据此判断长期影响力。
- **作者机构**：部分近期 arXiv 预印本的机构信息尚未被 OpenAlex 收录，已通过 arXiv 摘要页和公开网页交叉验证了核心作者的背景。
- **检索覆盖**：arXiv 官方 API 近期 rate limit 极严，未能做大规模批量检索；本报告基于主题关键词 + 网络检索 + 手动验证，可能遗漏少量相关论文。建议后续使用 arXiv 的 RSS/announcement feed 或 Valyu arxiv-search skill 做持续监控。
- **Petri 网**：本次检索未发现 2026-06-01 之后与 Petri 网和 AI 编程/代码图谱直接交叉的新论文。

---

## 9. 原始检索记录（供复核）

| arXiv ID | 标题 | 提交日期 | 作者数 | 引用 | 推荐等级 |
|----------|------|----------|--------|------|----------|
| 2606.15874 | LLM-as-Code: Agentic Programming for Agent Harness | 2026-06-14 | 7 | 0 | **High** |
| 2606.25189 | ActPlane: Programmable OS-Level Policy Enforcement for Agent Harnesses | 2026-06-23 | 9 | 0 | **High** |
| 2606.14061 | LLM Agents Can See Code Repositories | 2026-06-12 | 6 | 0 | **High** |
| 2606.06337 | TokenMizer: Graph-Structured Session Memory for Long-Horizon LLM Context Management | 2026-06-04 | 1 | 0 | **High** |
| 2606.08135 | TICoder: A Repository-Level Code Generation Framework with Test-Driven Planning and Implementation-Aware Reuse | 2026-06-06 | 5 | 0 | Medium |
| 2606.07297 | SWE-Explore: Benchmarking How Coding Agents Explore Repositories | 2026-06-05 | 11 | 0 | Medium |
| 2606.11680 | Organize then Retrieve: Hierarchical Memory Navigation for Efficient Agents | 2026-06-10 | 5 | 0 | Medium |
| 2606.30005 | LLM Agents Are Latent Context Managers: Eliciting Self-Managed Context via a Proprioceptive Dashboard | 2026-06-29 | 3 | 0 | Medium |
| 2607.01213 | RepoRescue: An Empirical Study of LLM Agents on Whole-Repository Compatibility Rescue | 2026-07-01 | 7 | 0 | Medium |
| 2603.05207v2 | Core-based Hierarchies for Efficient GraphRAG | 2026-06-02 (v2) | 2 | 0 | Medium |
| 2607.08691 | ProjAgent: Procedural Similarity Retrieval for Repository-Level Code Generation | 2026-07-09 | 3 | 0 | Low |
| 2606.22645 | All Relations Lead to Rome: Automated Knowledge Graph Creation and Question Generation | 2026-06-21 | 3 | 0 | Low |
| 2604.03496v2 | Beyond Predefined Schemas: TRACE-KG for Context-Enriched Knowledge Graph Generation | 2026-06-15 (v2) | 4 | 0 | Low |

---

*报告生成时间：2026-07-12*
