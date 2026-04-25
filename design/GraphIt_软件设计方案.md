# GraphIt 软件设计方案

## 一、项目概述

### 1.1 项目定位

GraphIt 是一个基于大模型语义理解的知识图谱构建与混合检索系统。核心能力是将多种类型的信息源（API文档网页、软件详细设计文档、代码仓库等）自动整理为结构化知识图谱，存储到轻量化图数据库，并对关键信息构建向量索引，最终为大模型提供"向量检索定位关键节点 + 图检索获取关联上下文"的混合检索能力。

### 1.2 核心价值

传统RAG依赖向量相似度检索，存在三大局限：信息碎片化导致多跳推理困难、语义相似不等于语义相关、缺乏全局视角。GraphIt通过知识图谱的结构化连接能力弥补这些缺陷，同时保留向量检索的语义模糊匹配优势，实现"结构化关系 + 语义相似"双驱动的智能检索。

### 1.3 设计原则

- **轻量化优先**：零外部服务依赖即可运行，支持嵌入式部署
- **增量可演化**：知识图谱支持增量更新，无需全量重建
- **文档类型感知**：针对不同文档类型采用差异化抽取策略
- **检索可解释**：检索路径可追溯，结果可审计

---

## 二、功能设计

### 2.1 功能模块总览

```
┌─────────────────────────────────────────────────────────────────┐
│                         GraphIt 系统架构                          │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  数据接入层   │  知识构建层   │  存储索引层   │    检索服务层      │
│              │              │              │                   │
│ · 网页抓取   │ · 文档解析   │ · 图数据库   │ · 向量语义检索     │
│ · 文件上传   │ · 智能分块   │ · 向量索引   │ · 图结构遍历       │
│ · API规范    │ · 实体抽取   │ · 元数据管理 │ · 混合检索编排     │
│ · 代码仓库   │ · 关系抽取   │ · 版本管理   │ · 上下文组装       │
│ · 增量更新   │ · Schema管理 │ · 增量同步   │ · LLM生成         │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

### 2.2 数据接入层

| 数据源类型 | 接入方式 | 典型场景 |
|-----------|---------|---------|
| API文档网页 | URL抓取 + HTML正文提取 | Swagger UI页面、REST API参考文档 |
| OpenAPI规范 | JSON/YAML直接解析 | swagger.json、openapi.yaml |
| 软件设计文档 | 文件上传 | PDF、DOCX、Markdown详细设计文档 |
| 代码仓库 | Git Clone + AST解析 | 源码中的函数、类、依赖关系 |
| 通用文本 | 文件上传/粘贴 | Confluence导出、技术博客、会议纪要 |

**增量更新机制**：维护数据源指纹（文档哈希/版本号）检测变更；文件系统Watch或Git Hook触发更新；变更时仅重新抽取受影响部分局部更新图谱；使用"墓碑"标记处理删除。

### 2.3 知识构建层

#### 2.3.1 文档解析与预处理

| 文档类型 | 解析工具 | 输出格式 | 关键能力 |
|---------|---------|---------|---------|
| 网页HTML | Trafilatura 2.0 | Markdown | F1=0.958，保留标题结构 |
| JS渲染页面 | Playwright + Trafilatura | Markdown | 无头浏览器渲染后提取 |
| PDF/DOCX | Docling v2.91 | Markdown/JSON | 保留文档层级、表格OCR、公式识别 |
| OpenAPI规范 | openapi-core | 结构化JSON | 直接解析，无需LLM |
| 源代码 | tree-sitter | AST | 增量解析，多语言支持 |

#### 2.3.2 智能分块策略

KG构建对分块有特殊要求：粒度更细（句子级）、结构保留更重要（标题层级映射为KG层级）、语义连贯性要求更高。采用**分层混合分块**：第一阶段按Markdown标题层级分割保留文档逻辑结构；第二阶段超出预设大小时句子级分割（最大2048字符，重叠200字符）；为每个块附加标题路径和文档元数据消解代词引用。

#### 2.3.3 实体与关系抽取

采用**混合Schema策略**——根据文档类型选择固定或开放Schema：

| 文档类型 | Schema策略 | 原因 |
|---------|-----------|------|
| API文档 | 固定Schema | 端点/参数/响应/错误码结构明确 |
| 设计文档 | 半固定Schema | 组件/模块/接口有固定类型，数据流关系可开放 |
| 代码 | 固定Schema | 类/函数/依赖/调用关系结构化程度高 |
| 通用文本 | 开放Schema | 内容多样，实体/关系类型不可预知 |

**API文档专用Schema**：
```
(:Endpoint)-[:HAS_PARAMETER]->(:Parameter)
(:Endpoint)-[:RETURNS]->(:Response)
(:Endpoint)-[:RAISES]->(:ErrorCode)
(:Endpoint)-[:CALLS]->(:Endpoint)
(:Parameter)-[:REFERENCES]->(:Schema)
(:Schema)-[:CONTAINS]->(:Field)
```

**设计文档专用Schema**：
```
(:Component)-[:CONTAINS]->(:Module)
(:Module)-[:EXPOSES]->(:Interface)
(:Component)-[:DEPENDS_ON]->(:Component)
(:Interface)-[:HAS_METHOD]->(:Method)
(:DataFlow)-[:FROM]->(:Component)
(:DataFlow)-[:TO]->(:Component)
```

**代码专用Schema**：
```
(:Module)-[:CONTAINS]->(:Class)
(:Module)-[:CONTAINS]->(:Function)
(:Class)-[:INHERITS_FROM]->(:Class)
(:Function)-[:CALLS]->(:Function)
(:Function)-[:HAS_ARGUMENT]->(:Argument)
(:Module)-[:DEPENDS_ON]->(:Module)
```

**抽取方法**：结构化数据源（OpenAPI规范）直接解析零LLM调用；半结构化文档（设计文档）LLM + 预定义Schema引导；非结构化文本（通用文档）LLM开放抽取 + EDC后置规范化（Extract-Define-Canonicalize）。

#### 2.3.4 实体消歧与规范化

同一实体的不同表述归并（如"用户服务"与"UserService"）；EntityRelationNormalizer去重标准化；为节点添加来源文档、位置信息等元数据支持回溯验证。

### 2.4 存储索引层

**图数据库**存储实体节点、关系边及属性，支持多跳遍历查询。**向量索引**为关键实体节点和文档块构建嵌入：实体节点嵌入名称+关键属性描述，文档块嵌入块文本内容，关系边嵌入关系描述（可选）。**双索引同步**通过实体ID建立映射，确保向量检索命中节点可在图中定位、图遍历获取节点可查询向量表示、增量更新时双索引同步维护。

### 2.5 检索服务层

#### 2.5.1 混合检索流水线

```
用户查询 → ①查询理解改写(LLM提取关键实体/意图)
         → ②双路并行检索
              ├── 向量语义检索(LanceDB Top-K候选节点)
              └── 图结构检索(Neo4j多跳遍历关联上下文)
         → ③结果融合排序(合并去重，按相关性评分)
         → ④上下文组装(结构化Prompt，控制Token预算)
         → ⑤LLM生成(基于组装上下文生成回答)
```

#### 2.5.2 检索模式

| 模式 | 适用场景 | 工作方式 |
|------|---------|---------|
| 向量优先 | 模糊语义查询（"如何处理认证失败"） | 向量检索Top-K → 图扩展1-2跳 |
| 图优先 | 精确实体查询（"UserService的createUser参数"） | 实体定位 → 图遍历获取完整上下文 |
| 混合模式 | 复杂推理（"哪些服务依赖了已废弃的API"） | 双路并行 → 结果融合排序 |
| 全局模式 | 宏观分析（"系统整体架构概览"） | 社区检测摘要 → LLM综合 |

---

## 三、技术选型

### 3.1 选型总览

| 层次 | 选型 | 备选 | 选型理由 |
|------|------|------|---------|
| 开发语言 | Python 3.10+ | — | AI/ML生态最成熟 |
| 网页解析 | Trafilatura 2.0 | readability-lxml + Playwright | F1=0.958最高，Markdown输出保留结构 |
| PDF/DOCX解析 | Docling v2.91 | Marker/PyMuPDF | 58.5k星，保留文档层级，表格OCR |
| OpenAPI解析 | openapi-core | prance | 支持v3.0/v3.1/v3.2最全面 |
| 代码解析 | tree-sitter | CodeGraph | 轻量增量解析，多语言，易嵌入 |
| 分块 | MarkdownHeaderTextSplitter + SentenceSplitter | HybridChunker | 结构感知+句子级粒度 |
| 实体关系抽取 | LLM + Schema引导 | OneKE/EDC框架 | 灵活可控，固定/开放Schema切换 |
| Embedding | BAAI/bge-m3 | text-embedding-3-large | 多语言好，开源可本地 |
| 图数据库 | Neo4j Community | FalkorDBLite/Apache AGE | Cypher生态最成熟，社区版免费 |
| 向量数据库 | LanceDB | ChromaDB | 嵌入式零服务器，三合一搜索 |
| LLM | OpenAI/DeepSeek/Ollama | — | API和本地模型灵活切换 |
| 检索编排 | 自定义Python流水线 | LangChain/LlamaIndex | 精细控制，避免框架黑盒 |

### 3.2 图数据库选型对比

| 维度 | Neo4j Community | FalkorDBLite | Apache AGE | CogDB |
|------|----------------|-------------|------------|-------|
| 部署 | Docker/JAR | pip install | PG扩展 | pip install |
| 查询语言 | Cypher | OpenCypher | openCypher+SQL | Torque(Python链式) |
| 向量支持 | 需插件 | 内置HNSW | 需pgvector | 内置SIMD |
| 社区成熟度 | 最成熟 | 新兴 | Apache顶级 | 早期(356星) |
| 许可证 | GPL 3.0 | SSPL | Apache 2.0 | 开源 |

选择Neo4j Community：Cypher是图查询事实标准，生态工具最丰富（Bloom可视化、LLM Graph Builder等），社区资源充分。社区版Slotted运行时对中小规模图谱够用，未来可平滑升级企业版或迁移FalkorDB。

### 3.3 向量数据库选型对比

| 维度 | LanceDB | ChromaDB | Qdrant | FAISS |
|------|---------|----------|--------|-------|
| 部署 | 嵌入式 | 嵌入式 | Docker/云 | 嵌入式库 |
| 混合搜索 | 向量+全文+SQL | 基础元数据过滤 | 高级过滤无损耗 | 无 |
| Stars | 10.1k | ~16k | ~22k | — |
| 多模态 | 文本/图像/视频 | 文本 | 文本 | 文本 |
| 自动版本控制 | 有 | 无 | 无 | 无 |

选择LanceDB：嵌入式零服务器与轻量化定位契合；三合一搜索（向量+全文+SQL）最灵活；微软GraphRAG默认使用验证充分；Rust内核高性能；自动版本控制便于增量更新。

### 3.4 GraphRAG框架选型对比

| 维度 | Microsoft GraphRAG | LightRAG | 自建流水线 |
|------|-------------------|----------|-----------|
| Stars | ~30k | 34.2k | — |
| 索引构建成本 | 高 | 低 | 可控 |
| 增量更新 | 不支持 | 支持 | 支持 |
| Schema灵活性 | 低 | 中 | 高 |
| 文档类型适配 | 通用 | 通用 | 可按类型定制 |

选择自建+借鉴LightRAG：GraphIt需针对不同文档类型差异化抽取，现有框架通用流程无法满足。自建可精细控制每个环节，同时借鉴LightRAG双层检索架构和增量更新算法。

---

## 四、系统架构设计

### 4.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      API / SDK / CLI / WebUI                  │
├──────────────────────────────────────────────────────────────┤
│                      检索服务层 (Retrieval)                    │
│  QueryParser → HybridRetriever → ContextAssembler → LLM     │
│                    ↙            ↘                             │
│         VectorRetriever    GraphRetriever                    │
├──────────────────────────────────────────────────────────────┤
│                      存储索引层 (Storage)                      │
│  Neo4j Community ◄──双索引映射──► LanceDB                    │
│  (实体节点/关系边/属性/社区摘要)  (实体嵌入/块嵌入/全文/元数据) │
├──────────────────────────────────────────────────────────────┤
│                      知识构建层 (Construction)                 │
│  DocParser → SmartChunker → Extractor → Normalizer           │
│  SchemaManager → IndexBuilder                                 │
├──────────────────────────────────────────────────────────────┤
│                      数据接入层 (Ingestion)                    │
│  WebIngestor │ FileIngestor │ APIIngestor │ CodeIngestor     │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 核心数据模型

**通用节点属性**：id(UUID), name, type, description, source_doc, source_location, created_at, updated_at, valid_from, valid_to(可选), embedding_id

**通用边属性**：type, weight, description, source_doc, created_at

**文档-实体关联**：
```
(:Document)-[:CONTAINS_CHUNK]->(:Chunk)
(:Chunk)-[:MENTIONS_ENTITY]->(:Entity)
(:Document)-[:HAS_METADATA]->(:DocMetadata)
```

这种双层结构（词汇图+实体图）确保原始文档片段可通过向量检索召回，实体关系可通过图遍历获取，两者通过Chunk-Entity关联桥接。

### 4.3 关键流程

**知识图谱构建流程**：数据源接入 → 文档解析(按类型选解析器) → 智能分块(标题层级→句子级) → Schema选择(按文档类型) → 实体抽取(LLM+Schema引导) → 关系抽取(LLM+依赖解析) → 消歧规范化 → 图写入(Neo4j) → 向量索引构建(LanceDB) → 双索引同步验证

**混合检索示例**：查询"UserService的createUser方法调用了哪些外部服务？" → QueryParser提取关键实体["UserService","createUser"]，识别GRAPH_FIRST模式 → GraphRetriever执行Cypher多跳遍历 → VectorRetriever补充相关文档片段 → ContextAssembler合并去重排序附加来源 → LLM生成结构化回答

---

## 五、接口设计

### 5.1 REST API

```
POST   /api/v1/ingest/web          # 接入网页URL
POST   /api/v1/ingest/file         # 上传文件
POST   /api/v1/ingest/openapi      # 接入OpenAPI规范
POST   /api/v1/ingest/code         # 接入代码仓库
GET    /api/v1/ingest/{task_id}    # 查询接入任务状态

GET    /api/v1/graph/stats         # 图谱统计
GET    /api/v1/graph/schema        # 获取Schema
PUT    /api/v1/graph/schema        # 更新Schema
GET    /api/v1/graph/entities      # 实体列表
DELETE /api/v1/graph/source/{id}   # 删除数据源及关联知识

POST   /api/v1/retrieve            # 混合检索
POST   /api/v1/retrieve/vector     # 纯向量检索
POST   /api/v1/retrieve/graph      # 纯图检索
POST   /api/v1/query               # 端到端问答

POST   /api/v1/update/check        # 检测变更
POST   /api/v1/update/execute      # 执行增量更新
```

### 5.2 Python SDK

```python
from graphit import GraphIt

git = GraphIt(graph_db="neo4j://localhost:7687", vector_db="./data/vectors", llm="deepseek-chat")

# 数据接入
await git.ingest_web("https://api.example.com/docs")
await git.ingest_file("./design-doc.pdf")
await git.ingest_openapi("./swagger.json")
await git.ingest_code("./src/")

# 检索与问答
results = await git.retrieve("UserService调用了哪些外部服务？", mode="hybrid", max_hops=2)
answer = await git.query("系统中有哪些服务依赖了已废弃的认证API？")
```

---

## 六、部署方案

### 6.1 开发环境（零外部依赖模式）

```bash
pip install graphit
docker run -d -p 7474:7474 -p 7687:7687 neo4j:5-community
# LanceDB自动创建本地文件，无需额外部署
```

### 6.2 生产环境

```yaml
services:
  graphit-api:
    image: graphit:latest
    ports: ["8000:8000"]
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - LANCEDB_DIR=/data/vectors
      - LLM_PROVIDER=deepseek
    depends_on: [neo4j]
  neo4j:
    image: neo4j:5-community
    ports: ["7474:7474", "7687:7687"]
    volumes: ["neo4j-data:/data"]
```

### 6.3 资源估算

| 规模 | 文档数 | 实体节点 | 关系边 | Neo4j内存 | LanceDB磁盘 | LLM成本 |
|------|--------|---------|--------|----------|------------|---------|
| 小型 | 10-50 | 1k-5k | 2k-10k | 2GB | <100MB | $1-5 |
| 中型 | 50-500 | 5k-50k | 10k-100k | 4-8GB | 100MB-1GB | $5-50 |
| 大型 | 500+ | 50k+ | 100k+ | 16GB+ | 1GB+ | $50+ |

---

## 七、风险与应对

| 风险 | 应对策略 |
|------|---------|
| LLM抽取质量不稳定 | Schema约束 + 多模型投票 + 置信度过滤 + 人工抽检 |
| LLM调用成本高 | 结构化数据直接解析(零LLM) + 批量API + 小模型微调 + 缓存复用 |
| 知识图谱噪声 | 规则引擎逻辑校验 + 墓碑删除 + 人工审核接口 |
| 增量更新一致性 | 事务性写入 + 定期一致性校验 + 失败回滚 |
| 图数据库性能 | 索引优化 + 查询超时保护 + 社区检测预计算 |

---

## 八、演进路线

**Phase 1 — MVP（4周）**：文件上传接入(PDF/Markdown) → 基础LLM抽取(开放Schema) → Neo4j+LanceDB存储 → 向量检索+单跳图遍历 → 基础REST API

**Phase 2 — 增强（4周）**：网页和OpenAPI规范接入 → 按文档类型差异化Schema → 增量更新机制 → 混合检索编排 → Python SDK

**Phase 3 — 生产化（4周）**：代码仓库接入(tree-sitter) → 社区检测与全局摘要 → 查询理解改写优化 → Web UI → Docker部署 → 性能调优监控

**Phase 4 — 智能化（持续）**：自动Schema学习 → 知识缺口自动发现与补全 → 多模态文档支持(图表/公式) → Agent化自主检索推理 → 图向量一体化数据库迁移评估

---

## 九、参考资源

1. [LightRAG - Simple and Fast Retrieval-Augmented Generation (GitHub 34.2k)](https://github.com/HKUDS/LightRAG)
2. [Microsoft GraphRAG (GitHub ~30k)](https://github.com/microsoft/graphrag)
3. [Docling - IBM Document Processing Library (GitHub 58.5k)](https://github.com/docling-project/docling)
4. [LanceDB - Embedded Vector Database (GitHub 10.1k)](https://github.com/lancedb/lancedb)
5. [OneKE - Schema-Guided LLM Knowledge Extraction (WWW 2025)](https://github.com/zjunlp/OneKE)
6. [EDC Framework - Extract Define Canonicalize (EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.548/)
7. [Efficient KG Construction and Retrieval (SAP, CIKM 2025)](https://arxiv.org/html/2507.03226v2)
8. [HybridRAG Benchmark (arXiv:2507.03608)](https://arxiv.org/abs/2507.03608)
9. [HybridRAG and Why Combine Vector with KG (Memgraph)](https://memgraph.com/blog/why-hybridrag)
10. [Trafilatura vs Readability vs Newspaper4k Comparison](https://www.contextractor.com/trafilatura-vs-readability-vs-newspaper/)
11. [Neo4j Alternatives in 2026 (ArcadeDB)](https://arcadedb.com/blog/neo4j-alternatives-in-2026-a-fair-look-at-the-open-source-options/)
12. [Vector Database Comparison 2025 (sysdebug)](https://sysdebug.com/posts/vector-database-comparison-guide-2025/)
13. [CodeGraph - Build Queryable KGs from Code (FalkorDB)](https://www.falkordb.com/blog/code-graph/)
14. [NebulaGraph GraphRAG Progress and Practice](https://www.nebula-graph.com.cn/posts/NebulaGraph-GraphRAG-RAG)
15. [GraphRAG开源生态全景 (腾讯云)](https://cloud.tencent.com/developer/article/2639682)
16. [KAG - Knowledge Augmented Generation (OpenSPG)](https://github.com/OpenSPG/KAG)
17. [FalkorDBLite - Embedded Python Graph Database](https://www.falkordb.com/blog/falkordblite-embedded-python-graph-database/)
18. [CogDB - Embedded Graph Database for Python](https://cogdb.io/)
19. [OOPS - Automated OpenAPI Generation via LLMs](https://arxiv.org/html/2601.12735)
20. [IncRML - Incremental KG Construction](https://www.semantic-web-journal.net/content/incrml-incremental-knowledge-graph-construction-heterogeneous-data-sources)
