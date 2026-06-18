# 本体论、图数据库与知识图谱：关联性资料综述

> 基于7篇论文和3篇网络文章的阅读整理
> 生成日期：2026-05-02

---

## 一、已下载论文

| 编号 | 标题 | 来源 | 年份 | 文件 |
|------|------|------|------|------|
| 01 | LLM-empowered Knowledge Graph Construction: A Survey | arXiv | 2025 | `01-LLM-KG-Construction-Survey.pdf` |
| 02 | OntoKG: Ontology-Oriented Knowledge Graph Construction | arXiv | 2026 | `02-OntoKG.pdf` |
| 03 | IRS: Information Retrieval System for Cyber Threat Intelligence (含KG部分) | arXiv | 2025 | `03-IRS-KG-Cyber.pdf` |
| 04 | Integration Strategy and Tool between Formal Ontology and Graph Database Technology | MDPI Electronics | 2021 | `04-Ontology-GraphDB-Integration.pdf` (HTML提取) |
| 05 | NatureKG: Ontology and Knowledge Graph for Nature Finance | Frontiers | 2025 | `05-NatureKG.pdf` |

---

## 二、网络博客中文解读摘要

### 摘要1：知识图谱——从数据到智慧 (HaskoningDHV, 2025)

**来源**：https://www.haskoning.com/en/newsroom/blogs/2025/from-data-to-wisdom

**核心观点**：

本文从数据管理咨询公司的视角，将知识图谱定位为"数据→信息→知识→智慧"金字塔的上层建筑。

**关键论点**：

1. **本体是图的语义层**：属性图数据库（如Neo4j）提供了灵活的存储，但缺乏统一的语义解释。本体（Ontology）作为"图的词汇表"，定义了存在什么类型的实体、它们如何关联、什么属性是合法的。没有本体的图存储的是"事实"；有了本体的图存储的是"带有意义的事实"。

2. **OWL本体在属性图中的角色**：OWL的类层次结构、属性约束和推理能力，可以叠加在属性图之上，解决Neo4j等图数据库"schema-free"导致的互操作性问题。

3. **知识图谱的构建流程**：
   - 阶段1：定义本体（类和关系的模式）
   - 阶段2：将结构化/非结构化数据映射到本体
   - 阶段3：加载到图数据库
   - 阶段4：利用推理和查询进行知识发现

**评价**：这是一篇面向企业高管的科普文章，没有技术深度，但清晰地传达了"本体是知识图谱的骨架"这一核心观念。

---

### 摘要2：Context Graph vs Knowledge Graph (TrustGraph, 2026)

**来源**：https://trustgraph.ai/guides/key-concepts/context-graph-vs-knowledge-graph/

**核心观点**：

本文提出了 **Context Graph** 概念，将其定义为 Knowledge Graph 的增强版本：

```
Context Graph = Knowledge Graph + Ontological Grounding + AI-Optimized Retrieval
```

**关键论点**：

1. **本体作为语义地基**："本体定义图的语义词汇表——存在什么类型的实体、它们如何关联、什么属性是有效的。没有本体支撑，图存储的是事实；有了本体，图存储的是带有意义的事实。"

2. **OWL本体的工程价值**：
   - 每个实体都有来自本体类层次结构的类型
   - 每条关系都有来自本体属性定义的谓词
   - 推理器可以自动检测数据中的矛盾

3. **AI优化的检索层**：传统KG查询需要知道具体的节点和边；Context Graph增加了语义检索能力，允许基于概念相似度而非精确匹配的查询。

4. **对LLM时代的重要性**：LLM需要结构化schema来减少幻觉，本体提供了"语义契约"，使LLM的输出可验证。

**评价**：来自AI基础设施公司TrustGraph的技术博客，有明显的商业推广色彩。"Context Graph"术语可能是该公司的营销概念，但"本体作为LLM的语义契约"这一观点有价值。

---

### 摘要3：RDF vs OWL：有何区别？ (Atlan, 2026)

**来源**：https://atlan.com/know/rdf-vs-owl/

**核心观点**：

本文从数据编目平台Atlan的视角，对比RDF和OWL的技术定位。

**关键论点**：

1. **RDF是数据模型，OWL是本体语言**：
   - RDF提供三元组（主体-谓词-客体）的通用数据表示
   - OWL在RDF之上增加了逻辑约束和推理能力

2. **OWL的核心能力**：
   - **类层次结构**：子类关系自动继承
   - **属性约束**：定义域、值域、传递性、对称性
   - **自动推理**：从显式声明推导隐含知识
   - **一致性检查**：检测数据矛盾

3. **两者的关系**：
   - OWL基于RDF（OWL是RDF的扩展）
   - RDF可以独立使用，OWL必须基于RDF
   - OWL提供"语义层"，RDF提供"数据层"

4. **选择建议**：
   - 仅需数据交换和链接 → RDF
   - 需要推理、验证和复杂查询 → OWL

**评价**：简洁明了的技术对比文章，适合作为入门参考。

---

### 摘要4：形式化本体与图数据库的整合策略 (MDPI, 2021)

**来源**：https://www.mdpi.com/2079-9292/10/21/2616 (Ferilli)

**核心观点**：

这是一篇**具有开创性**的学术论文，首次从"数据库中心"视角（而非传统的"本体中心"视角）出发，提出将形式化本体与属性图数据库（LPG）整合的技术方案。

**关键论点**：

1. **两大视角的互补性**：
   - **知识库（KB）视角**：关注高层次推理（AI/KR领域）
   - **数据库（DB）视角**：关注高效存储、管理和检索
   - 两者传统上各自发展，但"AI解决方案的普及"使整合变得迫切

2. **RDF图 vs LPG的关键差异**（论文详细对比）：

| 特性 | RDF图 | LPG（属性图） |
|------|-------|--------------|
| 节点 | 原子性的（URI） | 可携带属性信息 |
| 关系实例 | 无法区分同一对实体间的多次关系 | 有唯一标识符 |
| 关系属性 | 需要reification（重化） | 可直接附加 |
| 多值属性 | 天然支持 | 用数组实现 |
| 可读性 | 差 | 好（节点数量可减少一个数量级） |
| 查询效率 | 遍历/分析效率低 | 针对浏览优化 |

3. **GBS（GraphBRAIN Schema）中间格式**：
   - 论文提出的XML格式，用于表达图数据库schema
   - 可映射到标准OWL本体（用于推理）
   - 可映射到Neo4j图数据库（用于存储和查询）
   - **独特贡献**：允许多个schema/ontology同时应用于同一张图

4. **从数据库到本体的映射策略**：
   - GBS实体 → OWL类（Class）
   - GBS关系 → OWL对象属性（Object Property）
   - GBS属性 → OWL数据属性（Datatype Property）
   - 特殊处理：关系属性在OWL中需reification（将关系转为类）

5. **"数据库中心"视角的创新**：
   - 传统文献（SciGraph、G2GML、OWL2LPG等）都是"OWL-centric"——将OWL本体映射到图DB
   - 本文反向操作：以LPG为起点，叠加OWL能力
   - 理由："数据库技术比本体技术更成熟、应用更广泛"

**评价**：本文是本体-图数据库整合领域的奠基性论文，技术深度高，提出的GBS格式和双向映射策略具有实际工程价值。缺点是作者的自研工具GraphBRAIN没有成为行业标准，Neo4j后来推出的Neosemantics插件部分实现了类似功能。

---

## 三、简要综述：本体论、图数据库与知识图谱的三角关系

### 3.1 三者的定位

```
                    ┌─────────────┐
                    │  知识图谱   │  ← 最终产品（数据+语义）
                    │ (KG)        │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼────┐ ┌────▼─────┐
        │   本体论   │ │ 图数据库│ │   数据   │
        │(Ontology) │ │(GraphDB)│ │(Instances)│
        │   语义层   │ │ 存储层  │ │  实例层   │
        └───────────┘ └─────────┘ └──────────┘
```

| 组件 | 角色 | 核心能力 |
|------|------|---------|
| **本体论（Ontology）** | 语义层 / Schema | 定义类、属性、约束；支持推理和一致性检查 |
| **图数据库（Graph DB）** | 存储层 / Engine | 高效的节点-边存储和遍历查询 |
| **知识图谱（KG）** | 产品层 / Integration | 本体 + 数据实例的有机结合 |

### 3.2 核心矛盾：互补但不兼容

**RDF/OWL 与 属性图（LPG）的根本差异**是所有讨论的基础：

| 维度 | RDF/OWL | 属性图（LPG） |
|------|---------|--------------|
| **数据模型** | 三元组（S-P-O） | 节点+边+属性 |
| **Schema** | 严格的模式定义 | 通常schema-free |
| **推理** | 原生支持（OWL推理器） | 不支持 |
| **查询语言** | SPARQL | Cypher/Gremlin |
| **扩展性** | 标准化但灵活度低 | 灵活但缺乏语义一致性 |
| **关系属性** | 需reification | 原生支持 |
| **工业应用** | 学术/语义网为主 | 工业界广泛采用（Neo4j） |

> 关键结论：**工业界选择了属性图（LPG），学术界拥有OWL推理能力，两者的整合是核心挑战。**

### 3.3 两条整合路径

| 路径 | 方向 | 代表工作 | 特点 |
|------|------|---------|------|
| **OWL-centric** | OWL → LPG | SciGraph、OWL2LPG、G2GML | 将本体映射到图DB，保留OWL语义 |
| **DB-centric** | LPG → OWL | Ferilli (MDPI 2021) | 以图DB为中心，叠加OWL推理能力 |

**Ferilli的创新**：不是"把OWL塞进Neo4j"，而是"让Neo4j的数据能被OWL推理器使用"——通过GBS中间格式，schema和data分离，允许多个schema应用于同一张图。

### 3.4 LLM时代的新变化

2025-2026年的最新趋势（来自OntoKG、LLM-KG Survey等论文）：

1. **本体成为LLM的"护栏"**：LLM生成知识时，本体提供schema约束，减少幻觉
2. **Intrinsic-Relational Routing**：属性分类为"内在属性"（intrinsic，映射为节点属性）或"关系属性"（relational，映射为图边），这是本体工程在KG构建中的新方法论
3. **Schema作为一等资源**：不再事后补schema，而是先定义本体再填充数据
4. **多智能体KG构建**：不同Agent负责本体设计、数据抽取、知识融合、质量验证

### 3.5 选择指南

| 场景 | 推荐方案 |
|------|---------|
| 仅需数据链接和交换 | RDF + Triplestore |
| 需要推理和一致性检查 | OWL + 推理器（HermiT/Pellet） |
| 大规模图遍历和分析 | 属性图（Neo4j/Amazon Neptune） |
| 既需效率又需推理 | **整合方案**：Neo4j + Neosemantics + OWL推理器 |
| LLM驱动的KG构建 | 本体先行（OntoKG模式）+ 属性图存储 |

### 3.6 关键参考文献速查

| 文献 | 核心贡献 | 适用读者 |
|------|---------|---------|
| Ferilli (MDPI 2021) | GBS中间格式，DB-centric整合策略 | 工程师/架构师 |
| Hogan et al. (ACM Surveys 2021) | 知识图谱标杆综述 | 研究者 |
| OntoKG (arXiv 2026) | Intrinsic-Relational Routing，本体导向KG构建 | 前沿研究者 |
| LLM-KG Survey (2025) | LLM时代KG构建全景 | 综述入门 |
| TrustGraph Blog (2026) | Context Graph概念，本体作为LLM语义契约 | 工业界从业者 |

---

## 四、文件清单

```
papers/ontology/
├── 01-LLM-KG-Construction-Survey.pdf     (0.89 MB)
├── 02-OntoKG.pdf                         (0.80 MB)
├── 03-IRS-KG-Cyber.pdf                   (0.55 MB)
├── 05-NatureKG.pdf                       (1.08 MB)
└── ontology-kg-graphdb-survey.md        (本文件)
```

---

*整理日期：2026-05-02*
