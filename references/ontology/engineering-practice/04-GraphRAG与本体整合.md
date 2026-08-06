# 04 GraphRAG 及其与本体的整合

> 专题定位：本体论工程落地应用资料库 · 工程实践系列第 04 篇
> 读者对象：有工程背景、评估或实施 GraphRAG 类系统的架构师与开发者
> 调研时间：2026-08；所有关键事实均标注编号引用，见文末「参考来源」；无法核实的信息明确标注「待核实」。

---

## 0. 概述与定位

GraphRAG 不是单一系统，而是一类「以图结构为检索与组织中介的 RAG」方法族。狭义的 GraphRAG 特指 Microsoft Research 2024 年 4 月发表的论文 *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*（arXiv:2404.16130）及其开源实现 `microsoft/graphrag` [1][2]；广义的 GraphRAG 则涵盖 Neo4j、LlamaIndex、LangChain、LightRAG、HippoRAG、KAG 等一系列「LLM 抽取实体/关系 → 构图 → 图增强检索」的实现路线 [8][10][12][14]。

其核心动因是传统向量 RAG 的两个失效模式 [1]：

1. **全局性问题（global sensemaking）**：如「这批 500 篇报道的主题有哪些？」——答案不存在于任何单一文本块，向量 top-k 检索天然无法回答；
2. **多跳推理**：答案需要沿实体关系链跨文档组合，扁平 chunk 丢失结构性连接。

对本体工程而言，GraphRAG 的交汇点在于：**GraphRAG 产出的图本质上是「无 schema 的开放信息抽取图」（property-graph 风格，节点/边类型为自由文本），而本体/领域 schema 正是约束、规范和提升这张图质量的最直接手段**。用本体约束抽取（限定实体类型、关系类型、属性结构）可以显著降低抽取噪声、改善实体对齐、抑制幻觉，并打通与既有企业知识图谱（OWL/RDF）的互操作——OG-RAG、KAG 等工作已经把这条路走通并给出了量化收益 [14][15]。

一句话选型定位：**GraphRAG 解决「向量 RAG 检索不到」的问题；本体解决「GraphRAG 抽取不准、不可治理」的问题**。两者是互补而非竞争关系。

---

## 1. GraphRAG 基础理论

### 1.1 问题定义：查询聚焦摘要（QFS）

原始论文将目标任务形式化为语料级的 **Query-Focused Summarization（QFS）**：给定查询 q 和整个文档语料 D，生成一份面向 q 的摘要性回答 [1]。这与传统 RAG 的「检索片段 → 拼接回答」范式不同——QFS 的难点在于答案需要**跨整个语料聚合**，检索必须发生在比 chunk 更高的抽象层级上。论文明确指出：基线 RAG 擅长答案明确包含在少数文本区域中的问题，但在需要理解数据集整体结构的问题上失败 [1]。

### 1.2 索引管线（Indexing Pipeline）

`microsoft/graphrag` 的索引管线将原始文档处理为一个「文本单元 → 实体/关系图 → 层级社区 → 社区报告」的多层结构 [1][2]：

1. **文本分块（TextUnits）**：源文档被切成固定大小的 TextUnit。论文实验使用 600 token 块、100 token 重叠（开源实现早期版本默认 chunk size 300，**默认配置随版本变化，以 `settings.yaml` 为准**）[1][23]。
2. **实体与关系抽取（Graph Extraction）**：对每个 TextUnit 调用 LLM，抽取（实体名, 类型, 描述）与（源实体, 目标实体, 关系描述, 权重）元组。论文采用多轮「**gleaning**」策略——同一 chunk 反复提示 LLM「是否还有遗漏」，以提升召回；gleaning 轮次可配置（`max_gleanings`），是成本与召回的直接杠杆 [1]。
3. **实体摘要与图实例化**：对每个实体/关系的描述文本做 LLM 摘要，合并同名同类型节点；图建模为同质无向加权图，边权为关系实例的归一化频次 [1]。
4. **社区检测（Leiden）**：用 **Leiden 算法**（Traag, Waltman & van Eck 2019，*From Louvain to Leiden*，Scientific Reports）做**层级式**社区划分：低层社区对应少量紧耦合实体，高层社区跨越图的大片区域，形成多粒度索引 [1][7]。Leiden 相对 Louvain 保证社区内部连通，是论文明确选用的原因 [1]。
5. **社区报告（Community Reports / Summaries）**：对每个社区、每个层级，LLM 预生成一份「报告」式摘要，并生成 embedding。这一步是 GraphRAG 区别于普通「图 + 向量」混合检索的关键——**摘要被预计算并缓存，查询期直接复用** [1]。

管线产物以 Parquet 表形式落盘（entities、relationships、communities、community_reports、text_units 等），血缘链路为 Document → TextUnit → entity/relation → community report [2][23]。

几个容易忽略但对工程影响很大的机制细节：

- **Gleaning 是召回的主杠杆**。LLM 单遍抽取的实体召回有限，论文的做法是在同一 chunk 上循环追问「是否遗漏」，直到达到 `max_gleanings` 上限或无新增。每多一轮，LLM 调用近似线性增加——这是「索引 token 放大 26–85×」的首要来源，也是调参时成本/质量权衡的第一旋钮 [1][24]。
- **描述文本摘要化**。同一实体在多个 chunk 中反复出现时，各次抽取的描述会被合并后再由 LLM 压缩为单一摘要。这引入了第二重 LLM 生成内容（第一重是抽取本身），意味着图中的「实体描述」并非原文，引用溯源必须回到 TextUnit 层 [1][23]。
- **协变量（Covariates / Claims）**。管线支持可选的 claim 抽取（形如「实体 A 在时间 T 对实体 B 做了 X」的结构化断言），用于回答「关于 X 的正面/负面说法有哪些」类问题；默认关闭，开启后索引成本进一步上升且需要定制 prompt [23]。
- **层级社区 = 多分辨率索引**。Leiden 递归地把大社区切分为子社区，形成树状层级。查询时选哪一层是一个显式的成本/粒度旋钮：高层级报告少而概括（token 省、覆盖广、细节少），低层级报告多而具体（token 贵、细节全）。论文证明中低层级在全面性不输的前提下 token 效率优于全语料直送 LLM 的基线 [1]。
- **embedding 的双重角色**。实体描述、社区报告、原始 TextUnit 均生成 embedding；local search 用实体 embedding 找查询相关实体，global search（动态社区选择开启时）用报告 embedding 做预筛 [5][23]。

### 1.3 查询模式：Global / Local / DRIFT / Basic

- **Global Search（全局搜索）**：面向 QFS。采用 map-reduce：将社区报告按层级/相关性分批送入 LLM 并行生成中间答案（map），再汇总为最终回答（reduce）。层级越低细节越多、token 开销越大；层级越高覆盖面越广 [1]。
- **Local Search（局部搜索）**：面向「关于实体 X」的实体中心问题。从查询中识别实体 → 在图中取邻居（关系、社区报告、原始 TextUnit、协变量 claim）→ 按混合 token 预算组装上下文。回答带实体级溯源 [2][23]。
- **DRIFT Search**（Dynamic Reasoning and Inference with Flexible Traversal）：2024 年下半年加入开源实现的第三种模式，结合 global 的全局覆盖与 local 的局部细节，做迭代式「引子—下钻」搜索；Neo4j 官方博客给出了与 LlamaIndex 组合的复现教程 [13]。社区经验指出 DRIFT 需要显式的深度/分支/调用预算控制，否则调用量会失控 [23]。
- **Basic Search**：纯向量搜索基线，用于对照 [2]。

四种模式的工程画像对比：

| 模式 | 上下文核心构件 | LLM 调用形态 | 典型延迟 | 适用问题 |
|---|---|---|---|---|
| Basic | top-k TextUnit | 单次生成 | 亚秒 | 事实型 lookup |
| Local | 实体 + 邻居关系 + 报告 + 原文块（混合 token 预算） | 单次生成 | 百毫秒–秒级 | 「关于实体 X」类问题 |
| Global | 某层级社区报告集合 | map-reduce（多次并行 + 汇总） | 秒级–数十秒 | 全语料综合/主题类问题 |
| DRIFT | 全局引子 + 迭代下钻的局部上下文 | 多轮迭代 | 秒级–数十秒（需预算封顶） | 探索型、深浅混合问题 |

Local search 的上下文组装是固定的优先级预算分配：先放入识别出的实体描述，再按相关性依次填充关系、协变量、社区报告与原始 TextUnit，直到 token 预算耗尽——各来源的预算配比可配置，是把「图结构」翻译成「LLM 上下文」的关键环节 [23]。

### 1.4 论文评测结果

论文在两个真实语料上评测：播客转写语料与新闻文章语料，各自构建约百万 token 级图索引，用 LLM 评估器做 head-to-head 对比（comprehensiveness 全面性、diversity 多样性、empowerment 赋能感三个指标）[1]。结论要点：

- GraphRAG（全局搜索）相对基线 RAG 在全面性与多样性上取得约 **70%–80% 的胜率**（LLM 评估，head-to-head）[1]；
- 在中低社区层级下，GraphRAG 的 token 效率优于「全语料直接送 LLM」的朴素全局摘要基线——**社区报告起到了有损但高效的语料压缩作用** [1]；
- 代价全部前置在索引期：论文量级上，对约 100 万源 token 的语料，索引消耗约 **2600 万–8500 万 LLM token**（约 26–85 倍 token 放大）[24 转引，原始数字见 1]。

对工程读者的关键推论：**GraphRAG 的收益集中在「全局/综合类问题」，其成本集中在「一次性索引构建」**。查询类型以事实型 lookup 为主的系统不应引入 GraphRAG 全管线。

---

## 2. 主要变体与实现

### 2.1 microsoft/graphrag（参考实现）

- 仓库：`github.com/microsoft/graphrag`，定位为「数据管线与转换套件」，README 明确声明「代码为演示性质，非官方支持产品」，并显著警告「**GraphRAG indexing can be an expensive operation**」[2]。
- 使用形态：CLI（`graphrag init` → 编辑 `settings.yaml`（LLM/embedding/分块/抽取配置）→ `graphrag index` → `graphrag query --method global|local|drift`）+ Python API [2][18]。
- **Prompt Tuning 是官方强推步骤**：开箱 prompt 面向通用语料，官方文档提供自动模板化工具，根据语料自动生成领域化的抽取 prompt（含 domain、persona、entity types 定制）——这是本体/schema 知识注入的第一入口（见 §3.1）[2][3]。
- 版本治理：仓库维护 `breaking-changes.md`，次版本升级需 `graphrag init --force` 刷新配置格式，主版本升级提供迁移 notebook 以免重建索引 [2]。
- 生态配套：GraphRAG Visualizer、Azure Solution Accelerator（**已归档，且不支持增量索引** [21]）。

### 2.2 Neo4j / LlamaIndex / LangChain 的 GraphRAG 实现

这三个生态解决的是「把 GraphRAG 思路落到生产级图数据库与主流 LLM 编排框架」的问题：

- **Neo4j 官方 `neo4j-graphrag` Python 包**（原 `neo4j-genai`，已弃用并更名）：提供两类能力——
  - KG Builder Pipeline：`SimpleKGPipeline` 把「chunking → LLM 抽取 → 实体解析（内置 spaCy 语义匹配 / rapidfuzz 模糊匹配 resolver）→ 写库」做成可组合组件；**`SchemaBuilder` 支持从文本自动归纳 schema 或用户显式定义节点标签、关系类型、属性**，这是 Neo4j 侧注入本体约束的官方机制 [12]；
  - Retrievers：`VectorRetriever`、`VectorCypherRetriever`（向量命中后沿 Cypher 遍历）、`HybridRetriever`（向量 + 全文）、`Text2CypherRetriever`（自然语言转 Cypher）。环境要求 Neo4j ≥ 5.18.1（Aura ≥ 5.18.0）[12]。
- **LlamaIndex `PropertyGraphIndex`**：内置多种 KG 抽取器（SchemaLLMPathExtractor 用**用户给定 schema** 抽取，DynamicLLMPathExtractor 自由抽取），存储后端可接 Neo4j/Nebula 等；检索器支持向量 + 图路径混合 [16][25]。
- **LangChain `LLMGraphTransformer`**：`langchain_experimental` 中的文档转图组件，**`allowed_nodes` / `allowed_relationships` 参数直接限定抽取的实体类型与关系类型白名单**，输出写入 Neo4j 等图库；定位轻量，适合快速原型，不负责社区检测与分层摘要 [16][17]。

三者分工（综合社区对比 [16]）：LangChain 组件最轻、适合验证想法；LlamaIndex 在「抽取器—索引—检索器」链路上抽象最全；Neo4j 官方包在实体解析、schema 治理与生产图库集成上最强。微软 GraphRAG 则是唯一自带「社区层级 + 预计算报告 + 全局 map-reduce 查询」完整语义的实现。

### 2.3 LightRAG

- 出处：港大 HKUDS 团队，*LightRAG: Simple and Fast Retrieval-Augmented Generation*，arXiv:2410.05779（2024-10），后发表于 EMNLP 2025 Findings [8]；代码库 `HKUDS/LightRAG` [9]。
- 原理：LLM 抽取实体/关系构建图索引，**双层检索范式（dual-level retrieval）**——low-level 检索聚焦具体实体及其属性细节，high-level 检索聚焦抽象主题与多实体聚合；图结构同时用于**索引增强**（实体关键词与向量双通道召回）与**关联扩展**（沿图取一跳上下文）。
- 工程卖点（论文与社区实测 [8][18]）：索引与查询 token 开销远低于微软 GraphRAG（社区实测 500 页语料索引约 $0.5、约 3 分钟，对比微软 GraphRAG 的 $50–200/约 45 分钟 [18]）；**原生支持增量更新**（新文档直接并入图索引）；查询延迟接近向量 RAG。
- 代价：无社区层级与预计算全局报告，真正的「全语料主题综合」能力弱于微软 GraphRAG 全局搜索 [8][18]。

### 2.4 HippoRAG / HippoRAG 2

- 出处：俄亥俄州立大学 + 斯坦福，*HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models*，arXiv:2405.14831，NeurIPS 2024 [10]；后续工作 HippoRAG 2（*From RAG to Memory*，arXiv:2502.14802，2025-02）[11]。
- 原理：模拟人类长期记忆的海马体索引理论——LLM 扮演「新皮层」用 OpenIE 把段落抽成 KG 三元组（「人工海马体」开放知识图谱），稠密编码器扮演「旁海马区」负责同义关联建边；检索时对查询抽取命名实体、链接到图，跑 **Personalized PageRank（PPR）** 做上下文相关的段落打分。
- 结果：多跳 QA 上相对当时 SOTA RAG 提升最高约 20%；单步检索达到或超过 IRCoT 式迭代检索的效果，而成本低 10–30 倍 [10]。
- 定位：偏「记忆框架」而非企业问答管线；社区报告指出其实体中心抽取在长上下文上会丢失语境，且 PPR 随图规模增长，增量更新成本需评估 [11 转引]。

### 2.5 横向对比与选型速查

| 维度 | 微软 GraphRAG | LightRAG | Neo4j graphrag 包 | LlamaIndex PropertyGraphIndex | HippoRAG |
|---|---|---|---|---|---|
| 核心抽象 | 实体图 + Leiden 社区 + 预计算报告 | 实体图 + 双层关键词/向量检索 | 生产图库上的 KG + 多检索器 | 属性图索引 + 可插拔抽取器 | OpenIE 图 + PPR 记忆检索 |
| 全局综合查询 | 强（社区报告 map-reduce）[1] | 中（high-level 检索）[8] | 需自建 | 需自建 | 弱 |
| 多跳查询 | 中 | 中-强 | 强（Cypher 遍历） | 中 | 强（+20%）[10] |
| 索引成本 | 极高（26–85× token 放大）[1][24] | 低（≈向量 RAG 量级）[18] | 中（按文档 LLM 调用） | 中 | 低-中 |
| 增量更新 | 支持（v0.4.0+ `graphrag update`）[20] | 原生支持 [8] | 图库天然支持 upsert | 支持 | 受限 [11] |
| Schema/本体约束 | 仅 prompt 级（entity types）[3] | 弱 | 强（SchemaBuilder）[12] | 强（SchemaLLMPathExtractor）[16] | 无 |
| 生产成熟度 | 参考实现，自运维 | 活跃开源 | 厂商官方维护 | 框架组件 | 研究原型 |

组合使用的常见模式（工程实践中大量出现）：用 LangChain/LlamaIndex 的抽取组件负责「文档 → 图」的 ingestion，落库到 Neo4j；用 Neo4j 官方包的 retriever 负责查询期；当语料需要全局综合能力时，再单独跑一份微软 GraphRAG（或 AWS 统一框架）做社区摘要索引，两套索引按问题路由 [16][27]。三者并非互斥选项，而是可拼装在不同层级的组件。

### 2.6 其他值得关注的变体（速览）

- **LazyGraphRAG**（微软，2024-11）：不是独立产品而是 GraphRAG 的低成本模式——社区摘要推迟到查询期按需生成，索引成本降至完整 GraphRAG 的 0.1%，详见 §4.1 [6]。
- **Dynamic Community Selection**（微软，2024-11）：全局搜索的查询期优化，先用轻量模型对社区报告按查询相关性打分筛选，只对入选报告做 map-reduce，token 降幅约 77–79%（精确值待核实，见 §9）[5][19]。
- **RAPTOR**（Stanford，ICLR 2024）：不做实体图，而是对 chunk 递归聚类并摘要成树状索引，思想与社区摘要有亲缘性，常作为 GraphRAG 的对照基线出现 [10][15 引用链]。
- **GraphRAG-Bench**：针对 GraphRAG 类方法的独立评测基准，多家厂商（如 FalkorDB）用它给出可复现的成本/吞吐数据，选型时可作为横向对照 [30]。
- **AWS unified-kg-rag-on-aws**：把 GraphRAG 社区摘要与 LightRAG 双层检索统一到一套摄取/检索/评估底座上，支持按查询切换策略与增量索引，代表「变体融合」的工程化方向 [27]。

---

## 3. 本体在 GraphRAG 中的角色

这是本篇的核心议题。本体/领域 schema 对 GraphRAG 的价值体现在三个层面：**抽取约束、索引融合、质量与幻觉控制**。

### 3.1 用本体/Schema 约束实体与关系抽取

「schema-free 开放抽取」是微软 GraphRAG 的默认形态：实体类型、关系描述都是 LLM 自由生成的文本，类型体系随语料漂移，同义实体靠后处理合并。把本体知识注入抽取阶段的成熟做法有：

1. **Prompt 级类型约束（轻量）**：
   - 微软 GraphRAG 的 Prompt Tuning 允许在抽取 prompt 中固定 `entity_types`（如 PERSON/ORGANIZATION/GEO/EVENT…）并注入领域 persona 与少量示例 [3]；
   - LangChain `LLMGraphTransformer` 的 `allowed_nodes`/`allowed_relationships` 白名单 [17]；
   - 适用场景：无既有本体、只想收敛类型体系。局限：约束停留在提示词层，LLM 仍可能越界，需要输出校验兜底。
2. **Schema 对象级约束（中量）**：
   - Neo4j `SchemaBuilder`：显式定义节点标签、关系模式（源标签-关系-目标标签三元组）与属性类型，抽取器据此生成结构化输出，并可驱动后续实体解析 [12]；
   - LlamaIndex `SchemaLLMPathExtractor`：以用户给定 schema 的「可能路径」限定抽取空间 [16]；
   - KAG 的「LLM 友好知识表示」把 SPG schema 与自然语言格式对齐，抽取即受强 schema 约束 [14]。
3. **本体驱动抽取（重量）**：
   - OG-RAG：以**领域本体**为基础，把文档表示为「超图」——每条超边是一簇被本体概念 grounding 的事实；检索时用优化算法选出覆盖查询概念的最小超边集合，构造精确上下文 [15]；
   - KAG：在 OpenSPG 语义增强框架上做「知识对齐」——抽取的实体/关系通过语义推理对齐到 schema 定义的概念与规则，跨来源消歧 [14]；
   - 近期预印本 UniAI-GraphRAG（arXiv:2603.25152，2026-03，**未经同行评审，结论待核实**）进一步把「本体引导抽取 + 多维聚类 + 图/语义双通道检索」做成端到端管线，直接对标 schema-free 抽取的社区检测质量缺陷 [26]。

实践结论：**约束强度与工程成本正相关，与噪声负相关**。prompt 级约束适合探索期；进入专业领域（医疗、法律、金融、政务）且存在既有本体时，schema 对象级乃至本体驱动抽取是质量分水岭 [14][15]。

一个 prompt 级约束的最小示例（微软 GraphRAG `settings.yaml` 片段，示意性质，具体键名随版本变化以官方文档为准 [3]）：

```yaml
extract_graph:
  model_id: default_chat_model
  prompt: "prompts/extract_graph.txt"   # Prompt Tuning 自动生成的领域化模板
  entity_types: [person, organization, location, event, product, regulation]
  max_gleanings: 1
```

LangChain 侧的等价物是构造期白名单：

```python
from langchain_experimental.graph_transformers import LLMGraphTransformer
transformer = LLMGraphTransformer(
    llm=llm,
    allowed_nodes=["Person", "Organization", "Product", "Regulation"],
    allowed_relationships=["EMPLOYED_BY", "PRODUCES", "REGULATED_BY"],
)
```

注意两类约束的共同短板：**它们约束「类型」但不约束「取值」**。LLM 仍可能把不在本体实例集内的实体抽取出来（open-world 抽取），或与既有本体中的规范实体对不上（需实体链接）。这正是第 3 档「本体驱动抽取」用 grounding/对齐步骤解决的问题 [14][15]。

### 3.2 OWL 本体 / RDF 知识图谱与 GraphRAG 索引的结合

微软 GraphRAG 的图是内存/Parquet 中的 property graph，与语义网技术栈（RDF/OWL/SPARQL/SHACL）无原生互操作。桥接路线按集成深度分：

- **路线 A：图库共存，双索引并行**。GraphRAG 图与既有 RDF 本体库各自索引，查询期按问题类型路由或结果融合。实现成本最低，语义一致性靠实体链接维持。AWS 的 `awslabs/unified-kg-rag-on-aws` 框架示范了「一套摄取/缓存/混合检索底座 + GraphRAG 社区摘要与 LightRAG 双层检索双策略按查询切换」的并行架构 [27]。
- **路线 B：本体作为 GraphRAG 抽取的 schema 源**（§3.1 第 2/3 档）。本体概念体系先约束抽取，产出的实例图自然携带本体语义；实例图可按本体映射导出为 RDF，与既有 KG 合并。KAG 的 mutual indexing（KG 节点与原文 chunk 互索引）是该路线的完整实现 [14]。
- **路线 C：RDF 原生 GraphRAG**。检索直接发生在 RDF 图上，用 SPARQL property path 做多跳遍历，OWL 2 推理 + SHACL 校验提供逻辑一致性保障，PROV-O 提供溯源。厂商 ArcaQ 的实践报告宣称该路线可将幻觉风险压到接近零（**厂商博客，无可复现评测数据，结论待核实**）[28]。该路线对本体工程成熟度要求最高。
- **路线 D：超图/本体 grounding 索引**。OG-RAG 不做 chunk 向量索引，而是把文档组织成本体 grounding 的事实超边集合，检索即集合优化问题——本体既是索引结构又是检索语义 [15]。

选型建议：已有受治理的 OWL/SHACL 本体与 SPARQL 基础设施的组织，优先路线 B（渐进、收益确定）；本体资产薄弱、以非结构化文档为主的组织，路线 A 起步、用 prompt 级约束过渡。

### 3.3 对抽取质量与幻觉控制的影响（评测数据）

本体约束对质量的影响已有量化证据，注意各数据的口径与来源可信度：

- **OG-RAG**（arXiv:2412.15235，论文自报）：相对基线方法，正确事实召回 **+55%**、回答正确性 **+40%**、事实归因速度 **+30%**、基于事实的推理准确率 **+27%**，在 4 个不同 LLM 上验证 [15]。论文未与微软 GraphRAG 直接对比，口径为「vs 基线 RAG」。
- **KAG**（arXiv:2409.13731，论文自报）：多跳 QA 基准上，相对强 RAG 基线的相对 F1 提升 **19.6%（2WikiMultiHopQA）** 与 **33.5%（HotpotQA）**；强调其收益来自「schema 约束构建 + 逻辑形式引导的混合推理」的组合 [14]。
- **GraphRAG-Vet**（MDPI *Computers* 2026，期刊论文，样本规模有限）：在牛病精准诊断场景用领域本体（疾病-症状-药物）构建可验证的神经符号检索，报告核心疾病诊断准确率 100%（**垂直小样本场景，勿外推**）[29]。
- **反方证据**：社区工程报告指出，schema-free 的 LLM 抽取器会漏抽 30%–40% 的实体或产生错误关系 [19 转引]；GraphRAG-Bench 等独立评测显示 LLM 抽取存在系统性偏差 [24]。这正是本体约束要消除的噪声来源。
- 机制层面：本体通过 (a) 收敛类型空间降低抽取方差、(b) 提供实体解析的锚点（IRI/规范名）、(c) 使 SHACL/规则校验成为可能（抽取结果可机器验证）、(d) 为回答提供概念级溯源链，四条路径共同压低幻觉 [14][15][28]。

### 3.4 边界认知：GraphRAG 的图 ≠ 本体知识图谱

落地时必须向干系人讲清的概念边界：

- **GraphRAG 图是「文档的统计性投影」**：节点/边来自 LLM 对文本的开放抽取，边权是共现频次的归一化，无语义约束、无逻辑公理、无推理能力。它回答「语料里说了什么」，不回答「领域内什么是真的」 [1]。
- **本体知识图谱是「领域的规范性模型」**：概念体系经治理、可推理、可校验（OWL 推理、SHACL 约束），回答「领域内什么成立」。
- 因此「GraphRAG 图 + 本体」的正确关系是**本体管语义与治理、GraphRAG 管文档覆盖与检索效率**：本体提供 schema、规范实体与校验规则；GraphRAG 管线提供从非结构化文本批量填充实例、并把实例链回原文证据的机制。把 GraphRAG 产出的图当作受治理 KG 直接对外服务，是常见的认知错误——它缺少实体消歧、schema 一致性与 provenance 治理 [14][23][28]。
- 反向也成立：既有本体 KG 通常缺乏对海量非结构化文档的覆盖，GraphRAG 管线恰好补这一短板。KAG 的「mutual indexing」（KG 节点与原文 chunk 双向互索引）就是把两者缝合成一个检索单元的参考设计 [14]。

---

## 4. 工程落地

### 4.1 成本与延迟

成本结构（以微软 GraphRAG 为例，数据均注明出处）：

| 项目 | 数据 | 来源 |
|---|---|---|
| 索引 token 放大 | 每 100 万源 token 消耗 2600 万–8500 万 LLM token（26–85×） | 论文量级，转引自 [24] |
| 单文档索引成本 | 约 32,000 词的书记引 $4–7（GPT-4o 时代定价）；38,371 token 文档实测约 $0.34 | 社区实测汇总 [24] |
| 大规模语料案例 | 微软 8,400 小时播客语料：470,000 实体，3.4 亿输入 + 4,700 万输出 token，约合 $12,400（GPT-4 定价） | 博客转引微软官方博客 [22] |
| token 构成 | 实体/关系抽取约占索引 token 的 58%，其余为 gleaning 与社区报告 | 工程分析 [19] |
| 轻量实现对照 | gpt-4o-mini 下约 17,600 token/文档，1,000 文档约 17.6M token / ~$5.50，吞吐约 10 小时（单 worker） | FalkorDB GraphRAG-Bench 外推 [30] |
| 查询期成本 | Global search map-reduce 每次查询多次 LLM 调用；LazyGraphRAG 报告查询成本比全量全局搜索低 700 倍以上 | 微软官方博客 [6] |

降本手段（按有效性排序，均有出处）：

1. **LazyGraphRAG**（微软，2024-11-25 官方博客）：把社区摘要从索引期推迟到查询期，索引成本降至完整 GraphRAG 的 **0.1%**（与向量 RAG 同量级），同预算查询质量超过向量 RAG 与 GraphRAG；代价是查询延迟上升（社区实测 +2–8 秒）与全局综合能力略降 [6][19]。
2. **Dynamic Community Selection**（微软，2024-11 官方博客）：全局搜索时先用轻量模型筛掉无关社区报告，再对选中报告做 map-reduce，报告 token 用量下降约 **77–79%** 而质量基本持平（精确数字两个二手来源略有出入，**待核实**，以官方博客为准）[5][19]。
3. **抽取模型降级**：用 mini 级模型做抽取（成本降一个数量级），仅保留大模型做社区报告与回答生成；社区报告抽取质量保持约 82%（单一博客来源，**待核实**）[22]。
4. **经典 NLP 预处理 + 选择性建图**：对低价值语料只做向量索引，对高价值子集建图 [22]。
5. **换实现**：索引成本敏感场景直接选 LightRAG（500 页 ≈ $0.5/3 分钟 [18]）。

延迟画像：Local search 为「实体命中 + 邻域组装」，与混合检索同量级（百毫秒到秒级）；Global search 为 map-reduce，秒级到数十秒，随社区报告数量线性增长；DRIFT 为迭代搜索，必须配置深度/分支/调用预算 [19][23]。

### 4.2 索引构建管线与配置要点

微软 GraphRAG 最小可行流程 [2][3]：

```bash
pip install graphrag
graphrag init --root ./my-project        # 生成 settings.yaml 与 prompts/
# 编辑 settings.yaml：LLM/embedding API key、模型、chunks.size/overlap、max_gleanings、entity types
graphrag index --root ./my-project       # 全量索引（昂贵，先小样本试跑）
graphrag query --root ./my-project --method global "这批数据的主要主题是什么？"
graphrag query --root ./my-project --method local  "X 和 Y 是什么关系？"
```

关键配置与调优点：

- **chunk size / overlap**：论文用 600/100；块越小抽取越细但调用次数（成本）越高，块越大召回越依赖 gleaning [1][23]。
- **max_gleanings**：每增加一轮 gleaning，抽取召回上升、成本近似线性上升；社区经验从 1 起步逐步加 [1]。
- **entity types / prompt tuning**：上线前必做自动 prompt 调优，固定领域类型体系（§3.1）[3]。
- **社区层级（max_cluster_size / hierarchy level）**：global search 的层级选择直接决定 token 开销与回答粒度；需观测各层级社区规模分布与稳定性 [23]。
- **claim extraction（协变量）**：默认关闭，开启后成本显著上升且需要定制 prompt，按需启用 [23]。
- **并发与失败恢复**：抽取是 LLM 调用密集型，需配置并发上限与重试；建议记录索引期的 token/成本/失败清单（manifest）[23][30]。
- **升级注意**：跨次版本升级先 `graphrag init --force` 刷新配置；跨主版本用迁移 notebook 避免重建索引 [2]。

### 4.3 增量更新

- 微软 GraphRAG：**v0.4.0 起提供 `graphrag update --root <workspace>` 增量索引**——向 input 目录新增文件后运行该命令，仅处理新增输入并合并进既有索引；官方讨论区确认该用法，同时存在多次增量合并边界情形的未解决问题（Discussion #1453），生产上应做合并后校验 [20]。
- Azure GraphRAG Solution Accelerator **已归档且不支持增量索引**，生产部署应基于开源包自建 [21]。
- LightRAG 原生支持增量插入（新文档直接并入图与向量索引），是高频更新语料的更省事选择 [8]。
- Neo4j 路线：图库天然支持 upsert，增量问题退化为「新增文档的抽取管线调度」，无全量重建问题 [12]。
- 注意：**任何增量策略都绕不开社区报告的陈旧化**——新增文档改变社区结构时，受影响社区的报告需重算；LazyGraphRAG 把摘要推迟到查询期，天然规避了该问题 [6]。

### 4.4 生产部署经验与常见坑

综合官方文档与多份实践报告 [2][19][23][30]，生产化清单：

- **成本门禁**：索引是全量 LLM 调用，先对 5–10 篇代表性文档试跑，实测 token 放大系数后再外推全量预算 [2][30]。
- **问题路由**：不是每个查询都走 GraphRAG。按问题类型路由（事实型 → basic/local；综合型 → global；探索型 → DRIFT），AWS 统一框架的 `auto` 策略即按查询分析自动选路 [23][27]。
- **社区报告忠实性**：社区摘要是 LLM 生成的有损压缩，**必须抽样评估其对源证据的忠实性**，关键场景回答需附源 TextUnit 引用 [23]。
- **实体解析**：默认仅按「名称+类型」合并节点，跨文档指代（如缩写、别名）需额外的领域实体解析步骤，否则图碎裂、社区失真 [23]。
- **ACL/多租户**：不同权限来源的文档不要混入同一份社区报告，否则摘要将越权信息泄露给低权限查询；按权限域分区建索引 [23]。
- **评估**：按查询模式分别做质量/延迟/成本消融（global/local/DRIFT 的成本结构完全不同），用 RAGAS 或自建评测集；AWS 框架内置了评估 CLI 可参考 [23][27]。
- **可观测性**：记录索引 token/成本/失败 manifest、查询模式分布、map-reduce 调用数 [23]。
- **何时不要用**：查询以事实 lookup 为主、语料频繁变动且预算有限、或延迟要求 <1s 的场景，向量 RAG 或 LightRAG 更合适 [18][19][24]。

### 4.5 评测方法与质量保障

GraphRAG 系统的评测比向量 RAG 多两层不确定性（抽取质量、社区报告忠实性），建议分层评测：

1. **抽取层**：抽样人工标注实体/关系抽取的 precision/recall；对比开/关 schema 约束、不同 gleaning 轮次的差异。社区报告指出 schema-free 抽取漏抽率可达 30–40%，这层不量化就无法归因后续质量问题 [19][24]。
2. **社区报告层**：抽样评估报告对源 TextUnit 的忠实性（faithfulness），尤其检查报告是否引入原文不存在的断言——全局搜索回答的错误大多可追溯到这一层 [23]。
3. **回答层**：
   - 对全局综合类问题，沿用论文的 LLM-as-judge head-to-head（comprehensiveness/diversity/empowerment），与向量 RAG 基线对比胜率 [1]；
   - 对事实/多跳类问题，用有标准答案的评测集（HotpotQA、2WikiMultiHopQA、或领域自建集）跑 F1/EM；KAG、HippoRAG 的提升数据均出自此类基准 [10][14]；
   - 工程指标：按查询模式分别统计 p50/p95 延迟、单次查询 LLM 调用数与 token 成本 [23][27]。
4. **消融纪律**：global/local/DRIFT 的成本结构完全不同，任何「质量提升」结论都必须绑定查询模式与成本口径，否则无法复现与比较 [23]。

### 4.6 部署拓扑与集成模式

生产环境的三种典型拓扑：

- **单体式（PoC/内部工具）**：微软 GraphRAG CLI + 本地 Parquet/LanceDB 存储，单进程完成索引与查询。适合验证与低频内部使用，无高可用 [2]。
- **服务化（团队级）**：索引管线离线批跑（可定时/事件触发增量），查询侧以 API 服务承载；图与向量落生产存储（Neo4j/Neptune + OpenSearch 组合是云上的常见选择），配合缓存与并发限流。AWS 统一框架是这一拓扑的现成参考 [12][27]。
- **平台化（企业级）**：多租户分区索引（按权限域隔离社区报告）、统一问题路由网关（basic/local/global/DRIFT 分流）、索引成本与查询成本的全链路计量、与既有本体 KG 的双索引融合。此层级本质上是把 §4.4 的检查清单产品化 [23][27]。

从既有向量 RAG 迁移的稳妥路径是**并行运行 + 灰度切流**：保持向量 RAG 在线，旁路构建 GraphRAG 索引，先切 10% 流量做 A/B，观测延迟（p50/p95/p99）、单查询 token 成本、回答质量与幻觉率，达标后再决策 [32]。

---

## 5. 行业实践案例

- **微软内部播客语料（方法发源地）**：8,400 小时播客转写，470,000 实体、百万级关系，索引消耗 3.4 亿输入 token（约 $12,400，GPT-4 定价）；证明了管线在真实大规模非结构化语料上的可行性，也成为「索引成本门槛」讨论的标准案例 [22]。
- **蚂蚁集团 KAG（OpenSPG）**：已在**政务（E-Government）**与**医疗健康（E-Health，基于支付宝健康管家场景）**落地。E-Health 侧构建了 180 万+ 实体、40 万+ 术语集、500 万+ 关系的高质量知识图谱，配 700+ 条指标计算 DSL 规则，支撑医学指标解读、医保政策问答、医院/医生查询等专业问答；采用**强约束 schema** 做知识构建 [14]。
- **AWS 统一 KG-RAG 框架**（`awslabs/unified-kg-rag-on-aws`）：AWS 官方实验室的开源参考架构，在 Bedrock + Neptune + OpenSearch 上统一 GraphRAG 社区摘要与 LightRAG 双层检索两条路线，支持增量索引（DynamoDB 状态跟踪）、多语言与内置评估，适合作为云原生生产化起点 [27]。
- **Neo4j + LlamaIndex 的 DRIFT 复现**：Neo4j 官方向开发者给出的 DRIFT search 实现教程（2025-11），示范在自有图库上复刻微软全局+局部混合搜索，适合已有 Neo4j 资产的团队 [13]。
- **垂直领域本体落地**：GraphRAG-Vet 将牛病领域本体（疾病-症状-药物）与图检索结合用于精准诊断问答 [29]；水利设施安全知识图谱工作用 LLM 抽取 + 领域约束机制抑制幻觉（MDPI *Water* 2026）[31]。均为「领域本体 + 图检索」在垂直场景的落地样本。

---

## 6. 选型建议（决策速查）

1. 问题主要是「某实体相关的事实」→ **向量 RAG + 图遍历**（Neo4j 包 / LlamaIndex PGI）即可，不必上社区摘要管线。
2. 需要「全语料主题综合/态势感知」且语料稳定 → **微软 GraphRAG 全局搜索**，预算敏感则用 **LazyGraphRAG** 或 **Dynamic Community Selection** 降本 [5][6]。
3. 语料高频更新 / 预算紧 / 延迟敏感 → **LightRAG** [8]。
4. 多跳推理为主、偏研究或记忆场景 → **HippoRAG 2** [11]。
5. 专业领域（医/法/金/政务）且存在或愿建本体 → **本体约束抽取起步**（Neo4j SchemaBuilder / LangChain 白名单），成熟后演进到 **KAG / OG-RAG 式本体驱动索引** [12][14][15][17]。
6. 已有受治理 OWL/RDF 资产 → 双索引并行（路线 A）或本体作为抽取 schema（路线 B），不建议推倒重来 [27]。

---

## 7. 关键论文与资料清单

本地下载（`papers/` 子目录，均验证为合法 PDF）：

| 文件 | 论文 | arXiv / 出处 |
|---|---|---|
| `GraphRAG_From-Local-to-Global_arXiv2404.16130.pdf` | From Local to Global: A Graph RAG Approach to Query-Focused Summarization (Edge et al., Microsoft Research, 2024-04) | https://arxiv.org/abs/2404.16130 |
| `LightRAG_Simple-and-Fast-RAG_arXiv2410.05779.pdf` | LightRAG: Simple and Fast Retrieval-Augmented Generation (Guo et al., HKUDS, 2024-10) | https://arxiv.org/abs/2410.05779 |
| `HippoRAG_NeurIPS2024_arXiv2405.14831.pdf` | HippoRAG: Neurobiologically Inspired Long-Term Memory for LLMs (Gutiérrez et al., NeurIPS 2024) | https://arxiv.org/abs/2405.14831 |
| `KAG_OpenSPG_arXiv2409.13731.pdf` | KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation (Liang et al., Ant Group, 2024-09) | https://arxiv.org/abs/2409.13731 |
| `OG-RAG_Ontology-Grounded-RAG_arXiv2412.15235.pdf` | OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for LLMs (Sharma, Kumar & Li, 2024-12) | https://arxiv.org/abs/2412.15235 |

未下载但关键的文献与代码：

- HippoRAG 2 / *From RAG to Memory: Non-Parametric Continual Learning for LLMs*，https://arxiv.org/abs/2502.14802 [11]
- Traag, Waltman & van Eck, *From Louvain to Leiden: guaranteeing well-connected communities*, Scientific Reports 9, 5233 (2019)，https://doi.org/10.1038/s41598-019-41695-z [7]
- UniAI-GraphRAG（2026 预印本，待同行评审），https://arxiv.org/abs/2603.25152 [26]
- 代码库：`microsoft/graphrag` https://github.com/microsoft/graphrag [2]；`HKUDS/LightRAG` https://github.com/HKUDS/LightRAG [9]；`OSU-NLP-Group/HippoRAG` [10]；`OpenSPG/KAG` https://github.com/OpenSPG/KAG [14]；`neo4j/neo4j-graphrag-python` [12]

---

## 8. 参考来源

编号与正文引用一致；可信度标注：★★★ 一手（论文/官方文档/官方代码库），★★ 厂商博客或官方支持渠道，★ 社区/个人技术博客（需交叉验证）。

1. ★★★ Edge, D., Trinh, H., Cheng, N., et al. *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. arXiv:2404.16130, 2024. https://arxiv.org/abs/2404.16130 （论文，一手）
2. ★★★ microsoft/graphrag GitHub 仓库（README、breaking-changes、Prompt Tuning 指引）. https://github.com/microsoft/graphrag （官方代码库）
3. ★★★ GraphRAG 官方文档（prompt tuning、indexing/query 配置）. https://microsoft.github.io/graphrag （官方文档）
4. ★★ Microsoft Research Blog: *GraphRAG: Unlocking LLM discovery on narrative private data*, 2024-02. https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/
5. ★★ Microsoft Research Blog: *GraphRAG: Improving Global Search via Dynamic Community Selection*, 2024-11. https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/
6. ★★ Microsoft Research Blog: *LazyGraphRAG: Setting a new standard for quality and cost*, 2024-11-25. https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
7. ★★★ Traag, V., Waltman, L., van Eck, N. *From Louvain to Leiden: guaranteeing well-connected communities*. Scientific Reports 9, 5233 (2019). https://doi.org/10.1038/s41598-019-41695-z （论文，一手）
8. ★★★ Guo, Z., et al. *LightRAG: Simple and Fast Retrieval-Augmented Generation*. arXiv:2410.05779；EMNLP 2025 Findings 版 https://aclanthology.org/2025.findings-emnlp.568.pdf （论文，一手）
9. ★★★ HKUDS/LightRAG 代码库. https://github.com/HKUDS/LightRAG （官方代码库）
10. ★★★ Gutiérrez, B. J., Shu, Y., Gu, Y., Yasunaga, M., Su, Y. *HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models*. arXiv:2405.14831；NeurIPS 2024. https://arxiv.org/abs/2405.14831 （论文，一手）
11. ★★★ Gutiérrez, B. J., et al. *From RAG to Memory: Non-Parametric Continual Learning for Large Language Models*. arXiv:2502.14802, 2025. https://arxiv.org/abs/2502.14802 （论文，一手）
12. ★★★ Neo4j GraphRAG Python 包官方文档. https://neo4j.com/docs/neo4j-graphrag-python/current/ （厂商官方文档）
13. ★★ Neo4j 开发者博客：*Implementing DRIFT search with Neo4j and LlamaIndex*, 2025-11. https://neo4j.com/blog/developer/drift-search-with-neo4j-and-llamaindex/
14. ★★★ Liang, L., et al. *KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation*. arXiv:2409.13731；代码库 https://github.com/OpenSPG/KAG （论文 + 官方代码库）
15. ★★★ Sharma, K., Kumar, P., Li, Y. *OG-RAG: Ontology-Grounded Retrieval-Augmented Generation for Large Language Models*. arXiv:2412.15235, 2024. https://arxiv.org/abs/2412.15235 （论文，一手）
16. ★ Atlan 对比文章：*Neo4j GraphRAG vs. LlamaIndex vs. LangChain*, 2026-08. https://atlan.com/know/ai-agent/knowledge-graph/neo4j-graphrag-vs-llamaindex-vs-langchain/ （社区对比，二手）
17. ★★★ LangChain 官方文档：How to construct knowledge graphs（LLMGraphTransformer 的 allowed_nodes/allowed_relationships）. https://python.langchain.com/docs/how_to/graph_constructing/ （官方文档）
18. ★ tianpan.co：*GraphRAG in Production: When Vector Search Hits Its Ceiling*, 2026-04. https://tianpan.co/blog/2026-04-09-graphrag-production-when-vector-search-hits-ceiling （技术博客，成本数据为其实测）
19. ★ tianpan.co：*GraphRAG vs. Vector RAG: When Knowledge Graphs Beat Embeddings*, 2026-04. https://tianpan.co/blog/2026-04-17-graphrag-vs-vector-rag-knowledge-graphs （技术博客）
20. ★★ microsoft/graphrag Discussion #1365 / #1453（增量更新用法与已知边界问题）. https://github.com/microsoft/graphrag/discussions/1365 （官方社区）
21. ★★ Microsoft Learn Q&A：GraphRAG Solution Accelerator 已归档且不支持增量索引. https://learn.microsoft.com/en-us/answers/questions/5578950/ （官方支持渠道）
22. ★ Ash Ganda 博客：*GraphRAG: Unlocking LLM Discovery on Narrative Private Data*（播客语料索引成本，原始数字出自微软官方博客 [4]）. https://ashganda.com/blog/graphrag-unlocking-lln-discovery-on-narrative-private-data/ （博客转引）
23. ★ ruah 博客：*Microsoft GraphRAG 解剖：Local·Global·DRIFT Search*（生产检查清单），2026-07. https://blog.ruahverce.com/posts/32-microsoft-graphrag-local-global-search/ （社区实践笔记）
24. ★ Best AI Web：*Indexing Cost, Token Blowup, and the Hard Engineering Limits of GraphRAG at Scale*, 2026-05. https://www.bestaiweb.ai/indexing-cost-token-blowup-and-the-hard-engineering-limits-of-graphrag-at-scale/ （博客汇总，含 token 放大系数转引）
25. ★★★ LlamaIndex 官方文档：PropertyGraphIndex 指南. https://docs.llamaindex.ai/en/stable/module_guides/indexing/lpg_index_guide/ （官方文档）
26. ★ UniAI-GraphRAG（本体引导抽取的 GraphRAG 变体，2026-03 预印本，**未经同行评审**）. https://arxiv.org/abs/2603.25152 （预印本）
27. ★★ AWS 官方实验室：awslabs/unified-kg-rag-on-aws. https://github.com/awslabs/unified-kg-rag-on-aws （厂商官方代码库）
28. ★ ArcaQ 博客：*GraphRAG: Beyond Simple Vector Search — RDF Knowledge Graphs to Eliminate Hallucinations*, 2026-02. https://www.arcaq.com/en/blog/graphrag-beyond-vector-search.html （厂商营销博客，结论待核实）
29. ★★ *GraphRAG-Vet: A Knowledge Graph-Augmented Large Language Model for Precision Bovine Disease Diagnosis*. MDPI Computers 15(4):203, 2026. https://www.mdpi.com/2073-431X/15/4/203 （期刊论文，小样本）
30. ★★ FalkorDB 博客：*GraphRAG SDK 1.0: Production-Grade GraphRAG*（GraphRAG-Bench 成本/吞吐外推数据）, 2026-04. https://www.falkordb.com/blog/graphrag-sdk-knowledge-graph/ （厂商博客，数据可复现性中等）
31. ★★ *Research on the Construction and Application of a Water Conservancy Facility Safety Knowledge Graph Based on Large Language Models*. MDPI Water 18(7):840, 2026. https://www.mdpi.com/2073-4441/18/7/840 （期刊论文）
32. ★ IoT Digital Twin PLM 博客：*GraphRAG Architecture Patterns: Building Knowledge-Graph-Enhanced Retrieval for Enterprise LLM Applications*（并行运行 + 灰度切流的迁移模式）, 2026-04. https://iotdigitaltwinplm.com/graphrag-knowledge-graph-retrieval-augmented-generation-architecture/ （技术博客）

---

## 9. 待核实与存疑信息点

- **Dynamic Community Selection 的 token 降幅精确数字**：二手来源分别称 77% 与 79% [19][24]，以微软官方博客 [5] 原文为准（本次调研未能抓取该博客正文）。
- **「GPT-3.5 级小模型抽取保持 82% 质量」**：仅见于单一博客 [22]，无原始评测出处，谨慎引用。
- **ArcaQ「RDF GraphRAG 幻觉归零」**：厂商营销表述，无第三方评测，仅作路线参考 [28]。
- **UniAI-GraphRAG 的性能主张**：2026-03 预印本，未经同行评审 [26]。
- **GraphRAG-Vet 的 100% 诊断准确率**：垂直小样本场景，不可外推到通用结论 [29]。
- **微软 graphrag 包的最新稳定版本号与默认 chunk 配置**：随版本演进变化（0.4.x 时代默认 chunk 300；论文实验 600），以当前 `settings.yaml` 模板与 `breaking-changes.md` 为准 [2]。
- **播客语料 $12,400 成本**：数字按撰文时 GPT-4 API 定价折算，非微软官方公布值 [22]。
