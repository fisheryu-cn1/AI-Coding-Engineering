# 论文摘要：NatureKG（自然金融本体 + 知识图谱 + Text2Cypher 应用）

> **原论文标题**：NatureKG: an ontology and knowledge graph for nature finance with a Text2Cypher application
> **完整 PDF 文件名**：`05-NatureKG.pdf`
> 作者 / 年份：Neetu Kushwaha, Alok Singh, Hassan Aftab Sheikh（Smith School of Enterprise and the Environment, University of Oxford; NatureMind AI; Norwich University of the Arts），2025，Frontiers in Artificial Intelligence 8:1693843，DOI 10.3389/frai.2025.1693843
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **领域（自然/ESG/可持续金融）KG + LLM 接入** 系统时，需要把行业标准（ENCORE、SBTN）落到本体上。
- 构建 **Text-to-GraphQuery（Cypher/SPARQL）** 微调数据集与基线评估时——本文给出 paraphrase / cypher-level / generalization 三种 split。
- 评估 **小模型（Phi-3 / LLaMA-3.1-8B / Mistral-7B）fine-tune** 在低资源、领域专用图查询上的可用性。
- 选型 **Neo4j + LLM** 做可持续金融决策支持时的基线方案。

> 锚点：摘要（Abstract）；§1 Introduction；§2 Methods；§2.2 KG creation；§3 Text2Cypher 实验。

## 2. 主要观点与方案

### 2.1 问题定位

- 自然金融（nature finance）需要量化生态系统对金融系统的依赖与风险；现有金融体系缺乏结构化工具。
- 大语言模型在通用问答上很强，但在"高专业、低数据"领域（自然金融）存在数据稀缺、适配成本高、幻觉三大问题。
- 文本→图查询（Cypher）是图原生 SQL 替代方案；但 zero-/few-shot 表现仍受限。

### 2.2 贡献点

- ① 提出面向 **自然金融** 的本体（Actions、Drivers of Nature Loss、Value Chains、Evidence、Sources），基于 ENCORE + SBTN + 同行评议文献。
- ② 实例化为 NatureKG（Neo4j，320 节点 / 540 关系），覆盖"建成环境（built environment）"领域，专家 + LLM 协同生成 Evidence。
- ③ 构建 Text2Cypher 数据集，fine-tune Phi-3 / LLaMA-3.1-8B / Mistral-7B；证明小模型可在低资源领域下做"自然语言 → Cypher"。

### 2.3 端到端管线

- 阶段 1：本体设计（核心类 + 关系）。
- 阶段 2：实例化 KG（专家审核 + LLM 辅助摘要）。
- 阶段 3：构造 Text2Cypher 训练/评测数据。
- 阶段 4：fine-tune 开源 LLM，并在三种 split 策略下评估。

### 2.4 三种 split 策略

- **paraphrase split**：同义改写。
- **cypher-level split**：Cypher 结构层。
- **schema generalization split**：schema 泛化（最严苛）。

### 2.5 评测指标

- BLEU、Exact Match、Execution Accuracy、Macro F1。

> 锚点：§2 Methods；§2.2.1 Data sources；§2.2.2 Knowledge graph creation；§3 Text2Cypher fine-tuning & evaluation。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 本体核心类 | Actions、DriversOfNatureLoss、ValueChain、Evidence、Sources | §2.1 |
| KG 规模 | 320 节点 / 540 关系（Neo4j 实例） | 摘要，§2.2.2 |
| 数据源 | ENCORE（13 environmental pressures）、SBTN、学术 + 灰色文献 | §2.2.1 |
| 模型 | Phi-3 / LLaMA-3.1-8B / Mistral-7B（fine-tune） | 摘要，§3 |
| Phi-3 最高 | Execution Accuracy 0.21，Macro F1 0.56（paraphrase + schema generalization） | 摘要 |
| LLaMA-3.1-8B | 均衡表现 | 摘要 |
| Mistral-7B | 大多数指标落后 | 摘要 |
| 结论 | 小模型 fine-tune 在低资源、专用领域图查询可行 | 摘要 Discussion |

> 锚点：Abstract；§2.2.1 Data sources；§2.2.2 KG creation；§3 Results；Table 1。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 期刊 | Frontiers in Artificial Intelligence（Open Access） |
| DOI | 10.3389/frai.2025.1693843 |
| 单位 | University of Oxford Smith School of Enterprise and the Environment; NatureMind AI; Norwich University of the Arts |
| 框架标准 | ENCORE（Natural Capital Finance Alliance）、SBTN（Science Based Targets Network）、TNFD（Taskforce on Nature-related Financial Disclosures） |
| 数据库 | Neo4j（图数据库） |
| 模型 | Phi-3（Microsoft）、LLaMA-3.1-8B（Meta）、Mistral-7B（Mistral AI） |
| 关联方法 | OntoSustain（Zhou & Perzylo 2023）、BloombergGPT（Wu 2023）、GPT4Graph（Guo 2023）、Neo4j Labs fine-tuned Codestral / LLaMA（Bratanic 2024） |

> 锚点：§1 Introduction；§2 Methods；References。

## 5. 一句话索引（给 Agent 用）

> 把行业标准（ENCORE / SBTN）落到本体、用专家 + LLM 协同实例化为 Neo4j KG，再用小模型（Phi-3 / LLaMA / Mistral）fine-tune 出"自然语言 → Cypher"——给"Agent 在 ESG / 自然金融领域查询结构化知识"一个完整可复用的低资源模板。