# 论文摘要：LLM-Empowered Knowledge Graph Construction: A Survey（LLM 赋能的知识图谱构建综述）

> **原论文标题**：LLM-Empowered Knowledge Graph Construction: A Survey
> **完整 PDF 文件名**：`01-LLM-KG-Construction-Survey.pdf`
> 作者 / 年份：Haonan Bian（Xidian University），2025，arXiv:2510.20345，ICAIS 2025
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **LLM × KG** 系统时，需要建立对"三层管线（本体工程 / 知识抽取 / 知识融合）"的全局视图。
- 评估 **schema-based vs schema-free** 抽取范式（静态 schema、动态 schema、CoT 抽取、OIE）的取舍。
- 设计 **Agent 动态知识记忆**——KG 作为可演化、可被推理的外部记忆时，本体构建思路如何迁移。
- 选型 **多 Agent KG 构建框架**（KARMA、Graphusion、AutoSchemaKG、EDC）时用作决策依据。

> 锚点：摘要（Abstract）；§1 Introduction；§3 LLM-Enhanced Ontology Construction；§4 LLM-Driven Knowledge Extraction；§5 LLM-Powered Knowledge Fusion。

## 2. 主要观点与方案

### 2.1 核心论点（从"LLM for OE"到"OE for LLM"）

- KG 构建传统由三段组成：**本体工程（OE）→ 知识抽取（KE）→ 知识融合（KF）**；传统方法瓶颈为可扩展性差、专家依赖重、流水线碎片化与误差累积。
- LLM 通过三个机制改造 KG 构建：① 生成式知识建模；② 语义统一；③ 指令驱动编排（prompt-based orchestration）。
- 范式演进：top-down（LLM 作为本体建模助手，需求驱动）→ bottom-up（KG 作为 LLM 外部记忆 / RAG 底座）。

### 2.2 三层方法学分类

- **§3 本体工程**：
  - 3.1.1 CQ 驱动：Ontogenia、Ontology Design Patterns、CQbyCQ（自然语言需求 → OWL）。
  - 3.1.2 NL 驱动：LLMs4OL、NeOn-GPT、LLMs4Life、LKD-KGC（开放文本 → 本体）。
  - 3.2 自底向上：GraphRAG / OntoRAG（实例 → schema），EDC（Extract-Define-Canonicalize），AdaKGC（schema drift），AutoSchemaKG（schema-based + schema-free 统一）。
- **§4 知识抽取**：schema-based（Kommineni、KARMA、ODKE+）vs schema-free（Nie 2024、AutoRE、ChatIE、KGGEN、OIE-EDC）。
- **§5 知识融合**：schema-level（Kommineni、LKD-KGC、EDC canonicalize）→ instance-level（KGGEN、LLM-Align、EntGPT、RAG-based fusion、COMEM）→ 混合框架（KARMA、ODKE+、Graphusion）。

### 2.3 未来方向

- KG-based reasoning for LLMs（KG-RAR、随机游走推理）。
- Dynamic knowledge memory for agentic systems（A-MEM、Zep / TKG）。
- Multimodal KG（VaLiK、KG-MRI）。
- KGs 作为认知中间层（CogER、PKG-LLM），超越 RAG 的工具化定位。

> 锚点：§3 LLM-Enhanced Ontology Construction；§4 LLM-Driven Knowledge Extraction；§5 LLM-Powered Knowledge Fusion；§6 Future Applications。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 范式分类 | 三层（OE / KE / KF）× 两视角（schema-based / schema-free） | §1；图 1 Taxonomy |
| 代表框架 | Ontogenia、CQbyCQ、NeOn-GPT、LLMs4OL、GraphRAG、OntoRAG、EDC、AdaKGC、AutoSchemaKG、KARMA、ODKE+、Graphusion、KGGEN、LLM-Align、EntGPT、COMEM | §3–§5 |
| 评测发现 | GPT-4 输出可达"初级人类建模员"水平（Lippolis 2025b） | §3.1.2 |
| 演进方向 | 静态 schema → 动态 schema；模块化 → 生成式统一；符号刚性 → 语义自适应 | §7 Conclusion |
| 关键未来工作 | A-MEM（互联 notes）、Zep（TKG）、VaLiK（VLM→KG）、CogER（认知推荐） | §6.1–§6.4 |

> 锚点：§3.1.2 Natural Language-Based Ontology Construction；§4.2 Schema-Free Methods；§5.3 Comprehensive and Hybrid Frameworks；§6 Future Applications；§7 Conclusion。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2510.20345 |
| 会议 | ICAIS 2025（International Conference on Artificial Intelligence and Systems） |
| 关键工作 | Ontogenia（Lippolis 2025a）、CQbyCQ（Saeedizade & Blomqvist 2024）、NeOn-GPT（Fathallah 2025）、LLMs4OL（Giglou 2023）、EDC（Zhang & Soh 2024）、AutoSchemaKG（Bai 2025）、KARMA（Lu & Wang 2025）、Graphusion（Yang 2024）、AdaKGC（Ye 2023）、A-MEM（Xu 2025）、Zep（Rasmussen 2025） |
| 关联背景 | METHONTOLOGY、NeOn、Protégé、Ontology Design Patterns（ODP）、schema.org、UMLS |

> 锚点：§2 Preliminaries；§6 Future Applications；References。

## 5. 一句话索引（给 Agent 用）

> 选型 LLM × KG 系统的总览文档——把"本体工程 / 知识抽取 / 知识融合"三层在 LLM 时代的 schema-based 与 schema-free 两条路径，以及为 Agent 动态记忆服务的自底向上路线（GraphRAG、EDC、AutoSchemaKG）一次看清。