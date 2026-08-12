# 论文摘要：GraphRAG（从局部到全局的查询聚焦摘要）

> **原论文标题**：From Local to Global: A GraphRAG Approach to Query-Focused Summarization
> **完整 PDF 文件名**：`GraphRAG_From-Local-to-Global_arXiv2404.16130.pdf`
> 作者 / 年份：Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson（Microsoft Research / Microsoft Strategic Missions and Technologies / Microsoft Office of the CTO），2024，arXiv:2404.16130
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **全局 sensemaking QA 系统**——回答 "What are the main themes in the dataset?" 这类覆盖整个语料的查询。
- 解决 **传统 vector RAG** 在大规模语料上无法回答全局问题（comprehensiveness / diversity 不足）。
- 构建 **基于 KG 的 RAG 索引**：entity KG + community detection + 自底向上 community summary。
- 实现 **map-reduce** 风格的 query 时处理：map（社区摘要→部分答案）+ reduce（聚合为最终答案）。
- 用 **LLM-as-a-judge** 做无 ground-truth 的 sensemaking 评测。

> 锚点：Abstract；§1 Introduction；§2 Background；§3 Method；§4 Evaluation；§5 Discussion。

## 2. 主要观点与方案

### 2.1 核心论点

- 传统 RAG（vector RAG）擅长"局部证据检索"，但对"全局摘要/主题识别"类查询无能为力。
- GraphRAG：用 LLM 构造图索引（entities + relations + covariates）→ Leiden 社区检测 → 层次化 community summary → map-reduce 回答。
- 在 1M token 量级数据集的 sensemaking QA 上，GraphRAG 显著优于 vector RAG（comprehensiveness + diversity）。

### 2.2 索引阶段（Indexing Time）

- Text chunks → Entities & Relationships → Knowledge Graph → Community Detection（Leiden）→ Community Summaries（自底向上）。

### 2.3 查询阶段（Query Time）

- Community Summaries → Community Answers（map，partial responses）→ Global Answer（reduce）。

### 2.4 评测方法

- LLM-as-a-judge 自适应基准：一个 LLM 生成多样化 sensemaking 问题，另一个 LLM 作为评委对比两个 RAG 系统的答案。
- 评测标准：comprehensiveness + diversity。
- 用 GPT-4 作 LLM，GraphRAG 强于 vector RAG。

### 2.5 与已有方法的区别

- 与"高级 RAG（hierarchical index summary）"相似，但用 KG 而非纯文本摘要 + 用社区检测做主题划分。
- 不像 subgraph-RAG 直接把子图喂给 prompt；GraphRAG 用图的结构特性（modularity / community）做层次化摘要。

### 2.6 集成生态

- 开源：https://github.com/microsoft/graphrag
- 库扩展：LangChain、LlamaIndex、NebulaGraph、Neo4j。

> 锚点：§1 Introduction；§2 Background；§3 Method；§4 Evaluation；Figure 1。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 适用规模 | 1M token 量级语料 | Abstract |
| 提升 | substantial improvements vs vector RAG（comprehensiveness + diversity） | Abstract |
| LLM | GPT-4 | Abstract |
| 索引管线 | Text chunks → Entities → KG → Leiden communities → Community summaries | §3，Figure 1 |
| 查询管线 | Map（per-community partial answers）+ Reduce（final global answer） | §3 |
| 评测 | LLM-as-a-judge（adaptive benchmarking + personas） | §2.3，§4 |
| 基准 | 相对 vector RAG 全局 sensemaking 问题显著更优 | Abstract |
| 开源 | github.com/microsoft/graphrag | Abstract |
| 集成 | LangChain / LlamaIndex / NebulaGraph / Neo4j | Abstract |

> 锚点：Abstract；§3 Method；§4 Evaluation；Figure 1。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2404.16130 |
| 代码 | https://github.com/microsoft/graphrag |
| 库扩展 | LangChain、LlamaIndex、NebulaGraph、Neo4j |
| 单位 | Microsoft Research / Microsoft Strategic Missions and Technologies / Microsoft Office of the CTO |
| 模型 | GPT-4（LLM-as-a-judge 与 GraphRAG 主体） |
| 关联方法 | Vector RAG、Hierarchical indexing summary（Kim 2023, Sarthi 2024）、Leiden / Louvain 社区检测、HotPotQA、MultiHop-RAG、MT-Bench、Adaptive benchmarking、Persona generation |

> 锚点：§1 Introduction；§2 Background；§3 Method；§4 Evaluation；References。

## 5. 一句话索引（给 Agent 用）

> 当用户问的不是"具体某条事实"而是"整个语料的主题/趋势"时，**用 GraphRAG**：LLM 建实体 KG → Leiden 社区检测 → 自底向上 community summary → 查询时 map-reduce 生成全局答案——给"全局 sensemaking Agent"一套实证显著的工程模板（vs vector RAG 在 1M token 量级提升 comprehensiveness + diversity）。