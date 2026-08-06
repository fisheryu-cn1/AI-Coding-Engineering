# 本体论工程落地应用资料库 · 阅读索引

> 收集整理日期：2026-08-07
> 定位：从"基础理论 → 存储/推理引擎 → LLM 整合 → 行业实践"四个层次，整理本体论（Ontology）实际工程落地的技术方案、论文与非论文实践案例，面向有工程背景、需要选型或落地本体/知识图谱系统的读者。

---

## 一、目录结构与文档地图

```
engineering-practice/
├── README.md                          ← 本索引
├── 01-OWL-DL与HermiT推理机.md           理论与推理层
├── 02-Apache-Jena-TDB2存储引擎.md       存储层（开源）
├── 03-GraphDB企业级语义图数据库.md      存储层（商业）
├── 04-GraphRAG与本体整合.md             LLM 整合层
├── 05-金融行业本体应用实践.md           行业实践 · 金融
├── 06-企业经营决策本体应用实践.md       行业实践 · 企业经营决策
└── papers/                            20 篇已存档的开放获取论文 PDF
```

### 各文档摘要与适用场景

| 文档 | 核心内容 | 什么时候读 |
|------|---------|-----------|
| **01 OWL-DL 与 HermiT** | OWL 语言谱系（Lite/DL/Full）、SROIQ(D) 描述逻辑基础、OWL 2 EL/QL/RL 三 profile 选型；HermiT hypertableau 演算原理、与 Pellet/FaCT++/ELK/Openllet/Konclude 的对比评测；OWL API/Maven 集成代码、Protégé 使用、大本体推理调优与局限 | 需要理解"为什么推理"及推理机选型；评估是否需要 OWL 全量推理 |
| **02 Jena TDB2** | Jena 技术栈（ARQ/Fuseki/TDB）分层；TDB1→TDB2 演进；B+ 树索引排列、MVCC 事务模型；Fuseki 部署、批量加载、备份、JVM 调优、HA 方案（RDF Delta）与局限；WDBench 等基准数据；与 OWL 推理器的集成模式 | 选型开源 RDF 存储；搭建自托管 SPARQL 服务 |
| **03 GraphDB (Ontotext)** | TRREE 前向链物化推理、OWL-Horst/OWL2-RL ruleset 与自定义规则、sameAs 优化；Free/SE/EE 许可与 Raft 集群；加载调优、SPARQL 优化、Connectors；与 Stardog/Neptune/Virtuoso/TDB2 的公开评测对比；BBC、AstraZeneca 等案例 | 评估商业 triplestore；需要内置推理 + 企业级 HA 的托管方案 |
| **04 GraphRAG 与本体整合** | MS GraphRAG 原论文（arXiv:2404.16130）索引管线与查询模式；LightRAG/HippoRAG/KAG 等变体对比；本体/schema 约束抽取、OWL 与 GraphRAG 结合的四条集成路线、幻觉控制量化证据（OG-RAG、KAG）；成本、增量更新、生产部署清单 | 做 RAG 项目需要结构化知识支撑；评估"图+LLM"技术路线 |
| **05 金融行业实践** | FIBO 结构/治理/部署与采用案例；AML/KYC 实体解析（HSBC×Quantexa、意大利央行）、信用风险（蚂蚁 TuGraph）、监管合规（BCBS 239、Suade FIRE）、投研 KG（Bloomberg bbKG、LSEG PermID、GS/JPMC）；12 个案例汇总表（含可信度）；金融本体治理与数仓整合五模式 | 金融行业落地参考；合规/风控场景的架构借鉴 |
| **06 企业经营决策实践** | Palantir Foundry Ontology 三层架构（语义/动力/安全）与公开案例；EKG 方法论（EKGF 成熟度模型）、Gartner 决策智能定位；Salesforce/SAP 语义层动向；西门子/博世/阿斯利康数字化转型案例；DI 与本体关系四层次 | 企业级"语义层+决策"架构设计；理解 Palantir 模式与 EKG 方法论 |

---

## 二、papers/ 已存档论文清单（20 篇）

按主题分组，文件名与所属文档对应：

**推理与理论基础（配合 01）**
- `MotikShearerHorrocks2009_HypertableauReasoning_JAIR.pdf` — HermiT 的 hypertableau 演算长文（JAIR 2009）
- `GlimmEtAl2014_HermiT_OWL2Reasoner_JAR.pdf` — HermiT 系统描述（JAR 2014）

**存储与评测（配合 02/03）**
- `rdf-stores-sparql-engines-survey_arxiv2102.13027.pdf` — RDF 存储与 SPARQL 引擎综述（ACM CSUR）
- `wdbench-wikidata-benchmark_arxiv2203.08906.pdf` — WDBench 真实 Wikidata 负载多引擎对比
- `atemezing2018_commercial_rdf_stores_posb.pdf` — 商业 RDF 存储生产数据评测（QuWeDa 2018）
- `lam2023_sparql_engines_wikidata_eswc.pdf` — Wikidata 全量六引擎评测（ESWC 2023）

**GraphRAG（配合 04）**
- `GraphRAG_From-Local-to-Global_arXiv2404.16130.pdf` — MS GraphRAG 原始论文
- `LightRAG_Simple-and-Fast-RAG_arXiv2410.05779.pdf`、`HippoRAG_NeurIPS2024_arXiv2405.14831.pdf`
- `KAG_OpenSPG_arXiv2409.13731.pdf` — 蚂蚁 KAG：知识增强生成的专业领域方案
- `OG-RAG_Ontology-Grounded-RAG_arXiv2412.15235.pdf` — 本体接地的 RAG

**金融（配合 05）**
- `bellomarini_rule-based-aml_ceur2020.pdf` — 意大利央行规则推理 AML
- `aml-bitcoin-gcn_2019.pdf` — Elliptic 数据集 GCN 反洗钱
- `findkg_2024.pdf`、`finreflectkg_2025.pdf` — 金融动态/反思型 KG（ICAIF 2024/2025）

**企业经营决策（配合 06）**
- `06d-EnterpriseKG-Survey-ScitePress2017.pdf` — 企业知识图谱框架综述
- `06b-Zhou-Bosch-OntologyReshaping-ESWC2022.pdf`、`06e-ExecutableKG-Bosch-ISWC2022.pdf` — 博世本体重塑/可执行 KG
- `06a-AstraZeneca-BIKG-NSCLC-JTranslMed2024.pdf` — 阿斯利康生物医学 KG 应用
- `06c-SupplyChain-KG-LLM-arXiv2408.07705.pdf` — 供应链 KG + LLM

---

## 三、推荐阅读路径

- **技术选型决策**：03（商业 vs 开源格局）→ 02（开源自托管细节）→ 01（是否需要 OWL 推理）→ 各文档末尾的"选型建议"节
- **从零搭建语义栈**：01 §2（理论最小集）→ 02 §5（部署）→ 02 §7 / 01 §5（推理集成）→ 04 §3（如需接 LLM）
- **金融行业落地**：05 全文 → 02/03（存储选型）→ 01（合规推理场景）
- **企业决策/语义层架构**：06 全文 → 03（底层引擎）→ 04（AI 化延伸）
- **LLM + KG 前沿**：04 全文 → 06 §5（企业语义层动向）→ 上级目录 `ontology-kg-graphdb-survey.md`（既有综述）

## 四、与上级目录既有资料的关系

- `../ontology-kg-graphdb-survey.md`：本体-图数据库-知识图谱三角关系的理论综述（RDF vs LPG、OWL-centric vs DB-centric 整合路径），可作为本资料库的先导阅读。
- `../palantir-lightweight-analysis-report.md`：Palantir 本体模式的既有分析，与 06 文档 §3 互补。
- `../01~07-*.pdf`：LLM 驱动的 KG 构建与本体扩展（OntoKG、OwlPath、OntoExtend 等），与 04 文档的"LLM×本体"主题互补。

## 五、使用注意（重要）

1. **可信度分级**：各文档案例与数据均标注来源类型与可信度。厂商口径的 ROI/性能数字（Quantexa、Palantir、GraphDB 等）无第三方审计，引用时请保留该限定。
2. **存疑清单**：每篇文档末尾有"存疑与待核实"节（如 HermiT 与 OWL API 5.5.x 兼容性、TDB2 四元索引确切排列、GraphDB 最新定价、Palantir 定价等），使用前请查阅。
3. **时效性**：软件版本（Jena 6.2、GraphDB 11.4、graphrag 包等）与商业信息（Ontotext 已并入 Graphwise、EDM Council 更名 EDM Association）以 2026-08 调研时点为准。
4. 全部 20 篇 PDF 均来自开放获取渠道（arXiv/CEUR/期刊 OA），已验证文件完整性。
