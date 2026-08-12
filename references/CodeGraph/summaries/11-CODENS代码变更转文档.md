# 论文摘要：CODENS（把代码变更转成可查询的"活的"文档）

> **原论文标题**：CODENS: Transforming Code Changes into Living, Accessible, and Queryable Documentation
> **完整 PDF 文件名**：`11-Kelious-CODENS_v1.pdf`
> 作者 / 年份 / 出版：Abdelhak Kelious, Chyrine Tahri, Eliot Bardet；CAPSENS（Paris）；arXiv:2607.18356v1，2026-07-20；ACM DocEng '26
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 维护**长期演化代码库的"活文档"**：把 PR 历史累积成可查询的"项目记忆"。
- 为**框架化代码库**（Rails 风格的 MVC、约定的目录结构）建立**类型化软件知识图谱**。
- 把代码变更、文档、图检索三件事合在一起（typed software KG），供 Agent 引导的多跳问答。
- **Neo4j + LLM 抽取属性** 的端到端管道参考实现。
- 在生产代码库上做"文档导向"QA：技术细节 vs. 业务解释 vs. 端到端用户流。

> 锚点：摘要；§1 Introduction；§2 Tool Architecture；§3 Evaluation Results；§4 Conclusion。

## 2. 主要观点与方案

### 2.1 核心论点

- 旧系统的设计知识散落在源码、PR、code review、非正式讨论里，文档很快就过时。
- 把 **PR 历史** 当作"过去的知识"输入，按时序重放，**逐步构建并持续维护**一个类型化软件知识图谱。
- 知识图谱要同时支持**结构化查询**（graph traversal）和**语义检索**（embedding），并允许 Agent 在两者间自主调度。
- 关键设计：每个 PR 处理时**先注入节点已有状态**（state injection），让 LLM 增量更新而不是重写——避免早期知识丢失。
- 三种检索模式：**Standard 向量**、**Multi-hop 多跳**、**Agent-guided traversal（ReAct + 5 个工具）**。

### 2.2 方法

- **初始化**：扫描仓库，按目录约定把源文件分类为 17 种组件（Controller / Model / View / Service / Policy / Job / Spec 等），生成仅含结构元数据的 skeleton node。
- **增量图构建**（每个 PR 五步）：
  1. Diff 提取（GitHub API，仅保留与已有节点对应的文件）。
  2. State injection：注入当前节点状态 + 已有属性（purpose / behavioral_flow / business_logic / invoked_models / relations / provenance）。
  3. LLM 分析（GPT-4）：输入 patch + schema + state + 合并指令，输出 JSON 属性变化。
  4. Node 合并：标量叙事字段（behavioral_flow / purpose）替换并归档旧版本；列表字段（invoked_models / relationships）合并保持唯一性；provenance 记录首/末/全部 PR 列表。
  5. Edge 提取：schema-driven（从 enriched 节点读关系字段）+ cue-based（regex 模板）。
- **存储**：Neo4j；节点文本以 `behavioral_flow` 为优先，sentence-transformers (`all-mpnet-base-v2`) 嵌入。
- **检索模式**：
  - **Standard**：top-k 向量相似节点拼成上下文给 LLM。
  - **Multi-hop**：从 top-k 种子出发沿边扩展，按相似度过滤。
  - **Agent**：ReAct + 5 个图工具（GET_NODE / GET_NEIGHBORS / GET_RELATIONS / CYPHER / ANSWER）。
- **评估指标**：人类打分（relevance / completeness / document relevance）、RAG 指标（context precision / faithfulness / answer relevancy）、运维指标（延迟、token、cost、CO2）。

> 锚点：§2.1 Initialization；§2.2 Incremental Graph Construction；§2.3 Knowledge Base；§2.4 Multi-Mode RAG Querying；§2.5 Execution Metrics；Table 1（Agent 工具）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 评估项目 | 1 个生产 Ruby on Rails 应用（>1,700 源文件，数百 PR） | §2 |
| 知识图规模 | 1,739 skeleton nodes；622 unique edges；11 种关系类型 | §2.1/2.2 |
| 评估问题数 | 11 个文档导向问题（Q1–Q11） | Table 2 |
| 人类打分 | relevance 4.09/5、completeness 4.45/5、document relevance 4.91/5 | Table 2 |
| 自动指标 | context precision / faithfulness 全 1.00；answer relevancy 均值 0.94 | Table 2 |
| 质量短板（定性） | 答案"过于技术、过于逐行引用"——合成度与文档化表达不足 | Table 3 |
| 检索模式 | Agent 模式最强也最贵 | §3 |
| 配套指标 | 每次查询报告时长、模型、节点数、token、cost、CO2 | §2.5 |

> 锚点：Table 2 / Table 3；§3。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2607.18356v1；ACM DocEng '26，2026-07-20 |
| 图存储 | Neo4j |
| 嵌入 | sentence-transformers `all-mpnet-base-v2` |
| LLM | GPT-4（抽取）；Agent 模式可用 ReAct |
| 概念邻居 | Code–Text–Code（见 `05-`，中性文本规约）、RepoGraph（见 `03-`，行级图谱）、Agent-BOM（见 `06-`，安全审计） |
| 框架风格 | Ruby on Rails MVC 约定；可推广到 Django / Spring / Express 等 |

> 锚点：References。

## 5. 一句话索引（给 Agent 用）

> 维护老旧/快速迭代代码库的"活文档"时，**别只生成一次摘要**——按时序重放 PR、注入节点已有状态、增量合并属性，把代码变更**累积成 typed software KG**（Neo4j + GPT-4 schema-driven 抽取 + 622 边/11 种关系），再开放 5 个图工具供 ReAct Agent 多跳检索——context precision / faithfulness 接近 1.0，answer relevancy 0.94，主要短板是"答得太技术、太逐行"。
