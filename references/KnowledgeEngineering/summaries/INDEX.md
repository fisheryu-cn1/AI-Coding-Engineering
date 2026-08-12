# KnowledgeEngineering 主题论文摘要索引

> 主题：GraphRAG、知识图谱问答、多智能体系统
> 文件数：4
> 生成日期：2026-08-12

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-基于核心的层次化GraphRAG.md](01-基于核心的层次化GraphRAG.md) | Core-based Hierarchies for Efficient GraphRAG | 基于核心的层次化 GraphRAG |
| 02 | [02-RAGU多步GraphRAG引擎.md](02-RAGU多步GraphRAG引擎.md) | RAGU: A Multi-Step GraphRAG Engine with a Compact Domain-Adapted LLM | 多步 GraphRAG 引擎 + 紧凑领域 LLM |
| 03 | [03-PAGE_RAG证据接地自适应图检索.md](03-PAGE_RAG证据接地自适应图检索.md) | PAGE-RAG: Evidence-Grounded Adaptive Graph Retrieval for Long-Document QA | 证据接地自适应图检索 |
| 04 | [04-从RAG到多智能体系统.md](04-从RAG到多智能体系统.md) | From RAG to Multi-Agent Systems: A Survey of Modern Approaches in LLM Development | RAG → MAS 综述 |

## 推荐先读

- **理解 GraphRAG 整体思路**：04（综述）→ 01（层次化）→ 02（多步）
- **评估方案选择**：01 vs 03（层次化 vs 证据接地自适应）

## 与 GraphIt-KB 的相关性

- 论文 04（综述）是 GraphIt-KB 的设计参照集——其 RAG→MAS 演进路径与 GraphIt-KB 的 P1 实体图谱 + 关联分析路径平行。
- 论文 01–03 提供"图谱检索的多种实现"，可作为 GraphIt-KB FR-3.1 "图路检索"在 P1 阶段的具体实现参考。