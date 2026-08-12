# 论文摘要：OntoKG（本体导向的知识图谱构建与内在-关系路由）

> **原论文标题**：OntoKG: Ontology-Oriented Knowledge Graph Construction with Intrinsic-Relational Routing
> **完整 PDF 文件名**：`02-OntoKG.pdf`
> 作者 / 年份：Yitao Li, Zhanlin Liu, Anuranjan Pandey, Muni Srikanth（ProRata.ai），2026，arXiv:2604.02618
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **企业级知识图谱 schema** 时——需要把"实体属性"与"图边关系"明确分离，分别落到表/图两种存储后端。
- 构建 **Wikidata 规模开放 KG** 时——需要数据清洗 + 迭代 schema 精化 + LLM agent 协同的端到端流程。
- 评估 **实体消歧 / NER benchmark** 时——把基于本体的分类器作为 NER 标注的外部审计器。
- 设计 **LLM-guided extraction**——把 schema 用作 prompt 的"类型词表"，让 LLM 抽取时遵循 schema 约束。
- 借力 **Agent 工具（grounding tools）**——用 LMDB / SPARQL / DuckDB 验证 LLM 输出的 QID/PID 真伪，从源头抑制幻觉。

> 锚点：摘要（Abstract）；§1 Introduction；§3 Methodology；§4 Wikidata Case Study；§5 Applications。

## 2. 主要观点与方案

### 2.1 核心机制（intrinsic-relational routing，本征-关系路由）

- 将每个 property 分类为 **intrinsic**（节点属性，例如 birth date → 节点字段）或 **relational**（图边，例如 employer → 边），分别路由到 8 个 category、94 个 module（56 intrinsic + 38 relational）。
- **理论锚点**：Guizzardi 的 UFO（rigid sortals vs roles/mixins）、Ranganathan 的 faceted classification、Kiczales 的 cross-cutting concerns。
- **schema 是声明性的 YAML**，与构建管线解耦——可独立被下游任务消费。

### 2.2 迭代精化算法（Algorithm 1）

- 起点为种子 schema S0；每轮识别 unclassified E∅ 与 no-module E¬m 两类失败集合，调用三个 oracle：
  - 类别 oracle δc（未分类类型 → 类别 gate）
  - 模块 oracle δm（gate 同步到 module indicator）
  - 精化 oracle（合并 / 拆分 / 创建模块）
- 终止条件：分类率 rc ≥ θc（约 0.9）、模块分配率 rm ≥ θm（约 0.9）。

### 2.3 Agentic Oracle（LLM 决策代理）

- 由 Claude Opus 4.6 驱动；配备五个 grounding 工具以抑制幻觉：
  - `query_lmdb`（LMDB label 验证）
  - `query_p31`（实时 SPARQL 查询样本实体）
  - `tag_validator`（YAML 语法、QID/PID 格式、gate-module 同步）
  - `analyze_category_p31`（每类覆盖统计）
  - `find_unclassified_hubs`（高引用未分类枢纽）

### 2.4 Wikidata 案例

- 数据：January 2026 dump（~100M entities），100 GB JSON。
- 数据清洗：4 级优先级（structural / source signature / curation score / ratio-based safety net） → 34.6M core。
- Schema 三个来源：Schema.org + YAGO 4.5 + Wikidata EntitySchema → 8 个类别。
- 性能：Rust 分类器 ~110k 实体/秒；完整 34.6M 处理 ~5 分钟；导出 ~11 分钟。

### 2.5 五类下游应用

- 本体结构分析 + 主题子图提取（governance / biomedical / cultural 三大集群）。
- Benchmark 标注审计（AIDA-YAGO / CleanCoNLL 5,429 共享实体三轮一致率）。
- 实体消歧（BLINK controlled-candidate 子集比 YAGO 4.5 高 2.4 个 macro 点）。
- 领域定制（module 分解）。
- LLM 引导抽取（schema → prompt 类型词表）。

> 锚点：§3 Methodology；§4 Wikidata Case Study；§4.3 Agentic Oracle；§5 Applications。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 分类覆盖率 rc | 93.3%（32.3M / 34.6M core） | §4.2 |
| 模块分配率 rm | 98.0%（已分类中无模块率从 15.8% → 2.0%） | §4.2 |
| Schema 规模 | 8 类别 / 94 模块（56 intrinsic + 38 relational） | §4.2，图 2 |
| Property graph | 34.0M nodes（32.3M + 1.7M stub）+ 61.2M edges / 38 关系类型 | §4.4 |
| 导出大小 | 9.1 GB CSV / 1.7 GB gzipped | §4.4 |
| 实体消歧（BLINK） | 比 YAGO 4.5 macro +2.4 points（controlled-candidate 子集） | §5.3，摘要 |
| 三方一致（AIDA / CleanCoNLL / OntoKG） | 4,840 全一致 / 5,429 | §5.2，Table 2 |
| 跨类别关系模块 | 18 个跨度 ≥ 3（如 religion 跨 7、military 跨 6） | §4.2，图 2 |

> 锚点：§4.2 Schema Instantiation and Refinement；§4.4 Classified Result；§5.2 Benchmark Annotation Auditing；§5.3 Entity Disambiguation；Figure 2 / Figure 3 / Table 1 / Table 2。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2604.02618 |
| 代码 / schema | https://github.com/Prorata-ai/OntoKG（声明性 YAML schema + Rust + Python 实现） |
| 数据 | Wikidata January 2026 dump（约 100M entities，34.6M core） |
| 模型 | Claude Opus 4.6（agentic LLM workflow） |
| 工具栈 | LMDB（label 验证）、DuckDB（覆盖分析）、Wikidata SPARQL endpoint（实时 P31 查询）、Neo4j（property graph 导入） |
| 关联方法 | YAGO 4.5（schema.org 类型词表）、Schema.org、DBpedia、NECKAr、Wikidata Toolkit、HDT、UFO |

> 锚点：§4.1 Data Cleaning；§4.3 Agentic Oracle；§5 Applications。

## 5. 一句话索引（给 Agent 用）

> 把 Wikidata 100M 实体组织成 34M 节点 / 61M 边的 typed property graph 的端到端模板：intrinsic/relational 二分路由 → 迭代 schema 精化（Algorithm 1）→ LLM agent + grounding tools 协同——既能拿到一份可复用的声明性 schema，又能反哺实体消歧、领域定制和 LLM 引导抽取。