# 论文摘要：从 RAG 到多智能体系统（LLM 开发范式综述）

> **原论文标题**：From RAG to Multi-Agent Systems: A Survey of Modern Approaches in LLM Development
> **完整 PDF 文件名**：`from_rag_to_multi_agent_systems.pdf`
> 作者 / 年份：Gustavo de Aquino e Aquino, Nádila da Silva de Azevedo, Leandro Youiti Silva Okimoto, Leonardo Yuto Suzuki Camelo, Hendrio Luis de Souza Bragança, Rubens Fernandes, Andre Printes, Fábio Cardoso, Raimundo Gomes, Israel Gondres Torné（State University of Amazonas, Brazil），2025，Preprints.org doi:10.20944/preprints202502.0406.v1
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计或评估 **LLM 应用架构选择** 时：当面对"naive RAG vs Graph-based RAG"或"single-agent vs multi-agent"的决策，需要 trade-off 概览。
- 设计 **RAG 流水线** 时：需要明确 chunking / indexing / sparse+dense retrieval / reranking 等各环节的选项与现代实践。
- 评估 **多智能体系统（MAS）相对单智能体的优势** 时：本文给出并行处理、专业分工、可扩展性、对幻觉与故障的容错等系统化对照。
- 选型 **LangGraph / LangChain / AutoGen / OpenAI / Anthropic / AWS Bedrock** 等框架并设计有状态多智能体应用时。
- 为团队 / 学生 / 工业用户做"架构选型指南"型讲义或决策文档时：本文自我定位为"strategic guide"。

> 锚点：摘要；§1 Introduction；§8 Open Challenges and Future Directions。

## 2. 主要观点与方案

### 2.1 综述定位与覆盖面

- 本文是"LLM 应用开发综述"，区别于仅覆盖训练策略或预训练方法的现有综述：聚焦 **架构与管道层面的实际选择**。
- 覆盖面（图 1 给出 survey overview）：
  1. §2 LLM 基础——演化（统计方法 → seq2seq → RNN → Transformer → LLM）、架构、训练-推理管道、限制；
  2. §3 Prompt Engineering——zero/one/few-shot、CoT、ToT、自一致性、安全漏洞；
  3. §4 Naive RAG——稀疏/稠密检索、搜索 / chunking / indexing、文本生成、重排、prompt engineering、限制；
  4. §5 Graph-Based RAG——RDF / 属性图、混合方法、索引 / 查询 / 推理、对比、限制；
  5. §6 Agents——定义、single-agent vs multi-agent、用例；
  6. §7 框架与 LLM 服务（LangChain、LangGraph、AutoGen、OpenAI、Anthropic、AWS Bedrock）；
  7. §8 Open Challenges & Final Remarks。

> 锚点：§1；Figure 1（Survey Overview）；§2–8 各节标题。

### 2.2 LLM 演化路径与基础架构

- **四代演进**（图 2）：
  1. Statistical（N-gram、POS 标注）—— 固定窗口、数据稀疏；
  2. Sequence-to-Sequence + RNN/LSTM/GRU —— 编码-解码、门控、Word2Vec/GloVe；
  3. Transformer —— 自注意力、并行化、长程依赖、模块化（BERT/GPT/T5）；
  4. LLM —— 规模 + 涌现（few-shot / zero-shot / 多任务）。
- Transformer 三大优势：并行化、长程依赖直连、模块化设计；缺点是序列长度上 O(n²) 注意力代价——驱动后续 Long-context / RAG 路线。
- LLM 训练-推理管道：pre-train → instruction tuning / SFT / RLHF → 推理；瓶颈是**固定 context window + 静态知识**——这正是 RAG 与 agents 的动机。

> 锚点：§2 Fundamentals of LLMs；§2.1 Historical Context；Figure 2 (Evolution of NLP Architectures)。

### 2.3 Prompt Engineering 的关键技巧

- **Zero/One/Few-shot**：通过 in-context example 数控制泛化与开销；
- **Chain-of-Thought（CoT）**：把多步推理外化为中间步骤文本，提升算术 / 逻辑任务表现；
- **Self-Consistency**：多条 CoT 链 + 多数投票，提升稳健性；
- **Tree-of-Thoughts（ToT）**：把"思维路径"扩展为可探索的树结构，支持回溯与分支评估；
- **Prompt 注入 / 安全漏洞**：把 prompt 工程视为可攻击面；需要做权限边界与内容过滤。

> 锚点：§3 Prompt Engineering；§3.x 各项关键技术；§6 中也指出 prompt 工程是 LLM 行为校准的核心。

### 2.4 Naive RAG 流水线

- 经典管道：query → 检索（sparse BM25 / dense embedding / hybrid）→ 重排（cross-encoder / LLM rerank）→ prompt 组装 → LLM 回答。
- **关键设计选择**：
  - **Chunking**：固定大小 / 重叠 / 语义切分（embedding similarity）——影响检索召回粒度；
  - **Embedding 模型**：bge / OpenAI / E5 / Cohere 等；决定语义空间；
  - **Indexing**：HNSW / IVF / Flat 等 ANN 索引；
  - **Reranking**：cross-encoder 模型、LLM reranker；
  - **Prompt 组装**：把检索到的 chunks 嵌入 system 或 user prompt。
- **已知限制**：
  1. 难以处理 **跨文档实体关系与多跳问题**；
  2. 仅适合从少量连续段落直接得出答案的任务；
  3. 当答案需要整体语料的"主题感知"时表现差。

> 锚点：§4 Naive RAG；§4 Limitations and Challenges。

### 2.5 Graph-Based RAG 范式

- 用知识图谱组织语料：实体、关系、属性、语义路径、社区；
- **两种 KG 形式**：
  - **RDF Graphs**（Resource Description Framework）——语义 web 标准；
  - **Property Graphs**（Neo4j / NebulaGraph 风格）——更接近工业实践；
- **混合方法**：向量检索 + 图遍历；多跳 / 路径推理；社区级 map-reduce 摘要；
- **Graph RAG pipeline**（图 1 / §5 详述）：
  1. KG 抽取（LLM 或规则）；
  2. 索引（节点 + 边 + 文本证据指针）；
  3. 查询：局部实体邻域 / 全局社区摘要 / 路径推理 / 向量近似；
  4. 综合回答：把图检索的证据与 query 组合送 LLM。
- **GraphRAG 的优势**：跨段关系显式化、多跳可追溯、合成主题感知任务上的覆盖更高；
- **限制**：构造 / 查询成本高、社区摘要 map-reduce 时代价显著、自动抽取图存在噪声与不完整。
- 注：本文 §5 提供高层的图 vs 向量 / Graph RAG vs naive RAG 的定性对比（综述性质，不深入做 head-to-head）。

> 锚点：§5 Graph-Based RAG；§5.1 Introduction to Knowledge Graphs；§5.x RDF / Property Graphs / Hybrid / Comparison / Limitations。

### 2.6 Agents：single-agent vs multi-agent

- **定义**：agent 是能在环境中感知、推理、行动并具备一定自主性的 LLM 系统。
- **Single-Agent**：单一 LLM + 工具调用（检索、代码执行、API）。优点：实现简单、调试直接、可控；缺点：难以并行、能力受限于单个上下文 / 工具集。
- **Multi-Agent**：
  - 任务分解到多个 specialist（planner / retriever / coder / critic / verifier）；
  - 支持并行处理与协作工作流（debate、role-play、hierarchical supervisor）；
  - 通过多视角降低幻觉、通过分工提升可扩展性、通过错误隔离提升鲁棒性；
- **关键设计模式**：
  - **Role specialization**：每个 agent 单独 prompt + 单独工具集；
  - **Message passing / shared memory**：共享短期上下文与持久记忆；
  - **Orchestration**：supervisor / DAG / blackboard；
  - **Error isolation**：单 agent 失败不影响整体。
- **用例**：复杂研究任务（multi-source synthesis）、代码生成 + 自检、长期规划任务、对抗式鲁棒性增强。

> 锚点：§6 Agents in LLM Development；§6.x Definitions / Single-Agent / Multi-Agent / Use Cases。

### 2.7 框架与 LLM 服务（生态地图）

- **应用框架**：
  - **LangChain**：生态最广的 LLM orchestration 库；
  - **LangGraph**：在 LangChain 上扩展为有状态多智能体（stateful multi-agent）；
  - **AutoGen**：微软主导的多智能体对话框架，强调 role-based conversation；
  - **LlamaIndex**：偏 RAG 索引 / 数据 connectors；
- **LLM 服务商**：
  - **OpenAI**（GPT-4 类 API）；
  - **Anthropic**（Claude 系列 API）；
  - **AWS Bedrock**（托管多模型 + 企业级部署）；
- 综述强调：**LangGraph 让"有状态的多智能体"成为第一类公民**，并提供 cycle / branch / human-in-the-loop 等图原语。

> 锚点：§7 Frameworks for LLM Applications；Figure 1 末段。

### 2.8 开放挑战（Open Challenges）

- **架构决策 trade-off**：什么时候用 single-agent / multi-agent；什么时候 GraphRAG 比 naive RAG 更好；
- **成本与可扩展性**：多智能体 LLM 调用数随复杂度线性上升；
- **评测**：RAG / GraphRAG / 多智能体系统都缺乏统一 ground truth 与稳定评测协议（与论文 01、02 中观察一致）；
- **可观测性 / 安全 / 隐私**：multi-agent 系统增加 prompt injection 攻击面，agent 间消息也需要 audit；
- **错误隔离与回滚**：失败 agent 的重试 / 替换 / 跳过策略；
- **跨语言 / 跨域泛化**：现有综述与基准多以英文为主。
- **未来方向**：与 OS/工具/企业系统的深度耦合、统一评测标准、agent 网关与权限模型。

> 锚点：§8 Open Challenges and Future Directions。

## 3. 关键 trade-off / 比较表（综述给出）

> 注：本文为综述，§4–§6 表格多为定性比较 + 引用文献列举；下面摘出文中明确给出的对照与代表性数字。

| 维度 | Naive RAG | Graph-Based RAG | Single-Agent | Multi-Agent |
|---|---|---|---|---|
| 适用任务 | 局部事实查找、连续段落问答 | 跨段关系、多跳、全局主题合成 | 简单、单线流程 | 复杂、可分解、可并行任务 |
| 优势 | 易部署、低成本、文档级索引 | 关系显式化、社区/路径推理 | 实现简单、可控、易调试 | 分工、并行、可扩展、故障隔离 |
| 限制 | 难处理跨段 / 多跳 / 全局主题 | 构造 / 查询成本高、自动抽取噪声 | 上下文压力大、能力封顶 | 协调复杂、调用成本高、调试难 |
| 工程关键词 | BM25 / dense / rerank | KG（实体-关系）、社区摘要、路径遍历 | tools / function calling | role / message-passing / supervisor |
| 锚点 | §4 | §5 | §6.2 | §6.3 |

| 框架 / 服务 | 角色 | 关键特性 | 锚点 |
|---|---|---|---|
| **LangChain** | LLM orchestration | 生态最广，链式 prompt + 工具 | §7 |
| **LangGraph** | 多智能体框架 | 有状态图、cycle / branch / human-in-the-loop | §7 |
| **AutoGen** | 多智能体对话框架 | role-based conversation、可自定义 critic | §7 |
| **LlamaIndex** | RAG 索引库 | 数据 connectors、index 与 query 抽象 | §7 |
| **OpenAI** | LLM 服务 | GPT-4 系列 API | §7 |
| **Anthropic** | LLM 服务 | Claude 系列 API | §7 |
| **AWS Bedrock** | LLM 服务 | 托管多模型 + 企业部署 | §7 |

| 关键演化节点 | 内容 | 锚点 |
|---|---|---|
| N-gram / POS 标注 | 统计方法、有限上下文、数据稀疏 | §2.1.1 |
| seq2seq + Attention | 编码-解码、固定瓶颈被 attention 缓解 | §2.1.2 |
| Transformer（2017） | 自注意力、并行化、长程依赖、模块化 | §2.1.3 |
| LLM 时代 | 规模 + 涌现（few-shot、zero-shot、多任务） | §2.1.3 |
| RAG | 缓解固定知识截止 & context 限制 | §4 |
| GraphRAG | 解决跨文档关系与全局感知 | §5 |
| Agents / Multi-Agent | 复杂任务分解 + 并行 + 协作 | §6 |

> 锚点：§2–§7 各节；Table 1–3 风格由综述合并而成。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 preprint | https://doi.org/10.20944/preprints202502.0406.v1 |
| 发表平台 | Preprints.org（多学科预印本平台，未 peer-review） |
| 综述涉及的核心技术 | N-gram、Word2Vec、GloVe、LSTM/GRU、seq2seq、Bahdanau attention、Transformer、GPT、BERT、T5、ELMo、CoT、Self-Consistency、ToT、BM25、DPR、ColBERT、BGE、Cross-encoder rerank、LangChain、LangGraph、LlamaIndex、AutoGen |
| 关联阅读 | RAG 原论文（Lewis et al. 2020）；GraphRAG（Edge et al. 2024）；HippoRAG（Gutiérrez et al. NeurIPS 2024）；LightRAG（Guo et al. EMNLP Findings 2025）；Multi-Agent Survey / Wooldridge (2009) 多智能体系统经典教材 |
| 评测资源 | BEIR、MultiHop-RAG、Knowledge Graph QA benchmarks 等被多次引用 |

> 锚点：References §（论文最后）；§7 Frameworks；§8 Open Challenges。

## 5. 一句话索引（给 Agent 用）

> 选择 LLM 应用架构时，先按任务形态切：**事实查找 + 段落问答 → naive RAG（BM25/dense + rerank）；跨段关系 / 多跳 / 全局主题 → Graph-based RAG（KG + 社区/路径）；复杂可分解 / 需要并行 / 需要协作 → multi-agent（LangGraph / AutoGen）**——LangGraph 把有状态多智能体做成图原语是当下最直接的工程入口；本文作为一份"战略指南型综述"的价值在于把三个层级（LLM → Prompt → RAG/GraphRAG → Agents）的 trade-off 串成一张可对照的决策地图。
