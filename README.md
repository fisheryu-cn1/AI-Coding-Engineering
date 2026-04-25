# GraphIt · AI Coding Engineering Knowledge Base

> A curated knowledge base for engineering practices around **AI-assisted code generation**, focusing on context management, knowledge graph construction from technical documents, and dynamic information retrieval for coding agents.

---

## 📌 What is this?

This repository documents the research, design frameworks, and engineering explorations behind **GraphIt** — a knowledge-graph-driven context management system for AI coding agents.

The core thesis: *Traditional RAG (Retrieval-Augmented Generation) is insufficient for large-scale software engineering tasks because it lacks structural reasoning capabilities. By converting API documentation, framework guides, and software design documents into structured knowledge graphs, we can provide coding agents with precise, traceable, and dynamically retrievable context.*

All content is research-oriented and written in **Chinese**, sourced from real-world engineering analysis of platforms like WeChat Mini Programs and Next.js.

---

## 📁 Repository Structure

```
GraphIt/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── research/                          # Deep-dive research reports
│   ├── AI代码生成工具大型项目生成能力深度研究报告.md
│   ├── 知识图谱管理Agent上下文_深度研究报告.md
│   ├── API信息提供策略_补充研究报告.md
│   └── API与框架文档自动化知识图谱提取_研究报告.md
│
├── design/                            # Design frameworks & technical schemes
│   ├── GraphIt_软件设计方案.md          # Project overview & system architecture
│   ├── AI代码生成上下文控制_设计分析框架.md
│   ├── API文档知识图谱构建专题设计.md
│   ├── Wiki与图数据库混合架构策略笔记.md
│   └── 软件详设提取为图谱的方案.md
│
└── references/                        # Curated reference materials
    └── 上下文工程_核心参考资料清单.md
```

---

## 🔬 Key Research Themes

### 1. Context Management for AI Coding Agents
How to feed the "right amount" of context to LLMs during code generation:
- **Hierarchical context compression** (TREEFRAG, SWE-Pruner)
- **Dynamic retrieval** vs. static pre-loading
- **Information-gap hypothesis**: RAG is most valuable when context is *partially* missing

### 2. Knowledge Graph Construction from Technical Documents
Automated pipelines to convert unstructured technical docs into queryable knowledge graphs:
- **Hybrid extraction**: Rule-based structural extraction + LLM semantic enrichment
- **Schema design**: Distinct schemas for API docs (`API`, `Parameter`, `Platform`) and framework docs (`FileConvention`, `Directive`, `ConfigOption`)
- **LLMGraphTransformer** (LangChain) + Neo4j for graph storage

### 3. API Card Management & Grounding
A three-layer information provision strategy:
- **L1+L2 (Inline Cards)**: API name + signature + one-line description + key parameters (~50-100 tokens)
- **L3+L4 (On-Demand Pull)**: Detailed params, examples, error codes fetched via `get_api_detail(uri)`
- **Grounding**: Every graph entity traces back to its original document location (URL, CSS selector, source text)

### 4. Document-to-Graph Mapping
- **WeChat Mini Program APIs**: 4-level hierarchy (namespace → category → subcategory → API), table-structured parameters
- **Next.js Framework Docs**: Hybrid knowledge (tutorials + conventions + API reference), file-system conventions as "implicit APIs"

---

## 📖 Reading Guide

| If you want to understand... | Read this |
|------------------------------|-----------|
| The overall project vision and architecture | `design/GraphIt_软件设计方案.md` |
| How to control context for AI code generation | `design/AI代码生成上下文控制_设计分析框架.md` |
| How knowledge graphs can manage agent context | `research/知识图谱管理Agent上下文_深度研究报告.md` |
| Whether to provide full API docs or just summaries | `research/API信息提供策略_补充研究报告.md` |
| How to automatically extract API/framework docs into KGs | `research/API与框架文档自动化知识图谱提取_研究报告.md` |
| OpenAPI-to-KG mapping and extraction strategies | `design/API文档知识图谱构建专题设计.md` |
| How to convert software design docs into graphs | `design/软件详设提取为图谱的方案.md` |
| Hybrid Wiki + Graph DB architecture | `design/Wiki与图数据库混合架构策略笔记.md` |
| Core papers and tools in the field | `references/上下文工程_核心参考资料清单.md` |

---

## 🛠 Technologies & Tools Referenced

- **Graph Databases**: Neo4j, Neo4jVector
- **LLM Frameworks**: LangChain (`LLMGraphTransformer`), LangGraph
- **Document Parsing**: BeautifulSoup, Trafilatura, markitdown, crawl4ai
- **Embedding Models**: text-embedding-3-small, bge-large
- **LLMs**: GPT-4o, Claude 3.5 Sonnet, Qwen2.5, DeepSeek-V3

---

## 📜 License

This repository is licensed under the [MIT License](LICENSE).

All research reports and design documents are original work created for engineering analysis purposes. Citations to external papers and documentation are clearly attributed within each document.

---

## 🤝 Contributing

This is primarily a personal research knowledge base. However, if you find errors, have suggestions, or want to discuss the ideas, feel free to open an issue or reach out.

---

*Last updated: April 2026*
