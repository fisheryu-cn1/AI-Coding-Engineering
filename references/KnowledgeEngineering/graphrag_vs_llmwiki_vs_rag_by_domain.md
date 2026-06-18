# 软件工程与金融业务领域：GraphRAG vs LLM Wiki vs 传统 RAG 场景化决策指南

> 基于知识边界理论、查询复杂度分析和领域实践经验的综合决策框架
> 报告日期：2026年5月

---

## 一、核心决策框架

### 1.1 三维决策模型

两个领域的技术选型取决于三个核心维度的交集：

```
                    知识规模
              小 ◄─────────────► 大
                │                    │
        ┌───────┴────────────────────┴───────┐
        │   LLM Wiki (Karpathy)   │ GraphRAG │
        │   · 精确读取              │ · 关系推理 │
 高结构化│   · 低延迟                │ · 多源整合 │
     ▲  │   · 人类可维护            │ · 可扩展   │
     │  ├─────────────────────────┼───────────┤
     │  │  混合架构 (Wiki + RAG)   │ 混合架构   │
     │  │  · 架构知识用 Wiki        │  (最优)    │
     │  │  · 代码搜索用 RAG         │ · 向量召回 │
 低结构化│  · 关系查询用 Graph       │ + 图遍历   │
        │                          │ + LLM生成  │
        └──────────────────────────┴───────────┘
```

### 1.2 查询分类学（两领域通用）

根据 RAG vs GraphRAG: A Systematic Evaluation (2026) 的研究成果，将查询分为两大类：

| 查询类型 | 特征 | 推荐方案 |
|---------|------|---------|
| **事实型查询 (Fact-Based)** | 答案可直接从单一来源获取，无需多步推理 | 传统 RAG 或 LLM Wiki |
| **推理型查询 (Reasoning-Based)** | 需要跨多个来源交叉引用、逻辑推断、多步推理 | **GraphRAG** |

关键发现：*RAG 在单跳和细节导向问题上表现更好，而 GraphRAG 在多跳和推理密集型查询上表现更优。*

---

## 二、软件工程领域分析

### 2.1 领域知识结构特征

软件工程领域的知识结构具有显著的**多层次关系型**特征：

```
知识层次结构：
  架构层：微服务关系、模块边界、接口契约、设计模式
    ↓
  代码层：类继承、函数调用、依赖导入、API 签名
    ↓
  文档层：API 文档、README、RFC、架构决策记录(ADR)
    ↓
  运维层：部署配置、监控指标、日志模式、故障历史
```

| 特征 | 描述 | 对技术选型的影响 |
|------|------|-----------------|
| **强关系性** | 代码间的调用、继承、依赖关系是显式且类型化的 | 天然适合图结构表示 |
| **规模跨度大** | 从个人项目(< 100文件)到超大规模 monorepo(> 10万文件) | 小项目用 Wiki，大项目需 RAG/GraphRAG |
| **动态演化** | 代码持续变更，依赖关系频繁变化 | 需要增量更新能力 |
| **双重语义** | 代码有语法结构(AST)和语义含义 | AST 天然是图，语义适合向量 |
| **人类可维护性** | 文档需要开发者持续维护 | LLM Wiki 的人类可读性是优势 |

### 2.2 软件工程：适合 GraphRAG 的场景

#### 场景 A：代码依赖分析与架构理解

**典型问题**：
- "如果我修改这个接口，会影响哪些服务和模块？"
- "从用户请求到数据库写入的完整调用链是什么？"
- "找出所有直接和间接依赖于 X 库的文件"
- "哪些模块形成了循环依赖？"

**为什么需要 GraphRAG**：

> "In large-scale software systems, dependencies between modules are commonly represented as networks where nodes correspond to software components and edges represent dependency relationships... Graph-based representations enable developers to visualize complex software structures more clearly and identify relationships that may not be evident from source code alone."
> —— Software Dependency Analysis Using Graph Learning (2026)

代码依赖图天然是**有向图**（A imports B），需要图遍历才能回答多跳问题。传统 RAG 无法回答 "A 调用 B，B 调用 C，C 修改了什么" 这类链式查询。

**推荐方案**：Code-Graph-RAG 或类似工具（Graph-Code），将 AST + 依赖关系构建为知识图谱。

---

#### 场景 B：跨模块/跨服务影响分析

**典型问题**：
- "这个 API 变更会影响哪些客户端？"
- "哪些数据库表被哪些服务读写？"
- "如果服务 X 宕机，哪些用户流程会受影响？"

**为什么需要 GraphRAG**：

这类查询需要在**代码-服务-数据**三层之间进行多跳推理。例如：
```
API Endpoint → Service Method → Database Table → Consumer Service → Frontend Page
```

每条边代表不同类型的关系（调用、读写、依赖），传统 RAG 的向量相似度无法捕捉这种类型化的路径。

---

#### 场景 C：代码知识图谱辅助开发（大型代码库）

**典型问题**：
- "这个函数的实现遵循了什么设计模式？"
- "类似功能的代码在其他模块中是如何实现的？"
- "找出所有使用了观察者模式的组件"

**为什么需要 GraphRAG**：

> "Graph-Code is designed to be versatile... It combines a semantic and structural understanding of code, giving you a global architectural view rather than just a local snippet analysis."
> —— GraphRAG for Devs: Graph-Code Demo (2025)

大型代码库中，理解一个组件需要同时掌握其**结构关系**（依赖图）和**语义关系**（相似功能），GraphRAG 的混合检索（向量召回 + 图遍历）是最佳方案。

---

### 2.3 软件工程：适合 LLM Wiki 的场景

#### 场景 D：编码规范和架构决策文档

**典型问题**：
- "我们团队的 API 命名规范是什么？"
- "为什么选择了 Redis 而不是 Memcached？"
- "新模块应该放在哪个目录下？"
- "认证流程的架构决策是什么？"

**为什么适合 LLM Wiki**：

> "LLMs are good at reading structured text. A well-written markdown page about your authentication module — how it works, what to watch out for, recent changes — is exactly the kind of material modern LLMs handle well. They don't need embeddings to understand it."
> —— LLM Wiki vs RAG for Codebase Memory (MindStudio, 2026)

架构决策记录（ADR）和编码规范的特点：
- **规模可控**：通常几十到几百页文档
- **高度结构化**：Markdown 层级天然携带语义
- **需要人类维护**：架构决策需要人参与讨论和记录
- **精确性要求高**：规范需要逐字准确，不能模糊
- **变更低频**：架构决策相对稳定，不需要频繁重索引

**推荐方案**：Karpathy 的 LLM Wiki 方法——结构化 Markdown + 索引文件。

---

#### 场景 E：小型项目/个人项目的代码理解

**典型问题**：
- "这个项目的技术栈和目录结构是什么？"
- "如何运行和部署这个项目？"
- "这个模块的主要功能是什么？"

**为什么适合 LLM Wiki**：

> "Start with LLM wiki: personal research workflows, stable knowledge corpora under 150 pages, solo practitioners, zero-infrastructure constraints"
> —— LLM Wiki vs RAG Knowledge Base (Atlan, 2026)

小型项目的特点：
- 全部代码和文档可放入 LLM 上下文窗口
- 不需要复杂检索
- 零基础设施要求

---

#### 场景 F：API 文档和快速参考

**典型问题**：
- "这个 API 的参数和返回值是什么？"
- "如何调用用户认证接口？"
- "错误码 403 代表什么？"

**为什么适合 LLM Wiki**：

API 文档是**结构化、边界明确、精确性要求高**的知识。LLM Wiki 的确定性读取确保答案 100% 来自文档原文，而不会被相似但不相关的 API 文档干扰。

---

### 2.4 软件工程：适合传统 RAG 的场景

#### 场景 G：代码语义搜索（大规模代码库）

**典型问题**：
- "找到处理用户支付的代码"
- "哪些代码实现了重试逻辑？"
- "查找使用了特定算法的实现"

**为什么适合传统 RAG**：

> "RAG continues to perform better on single-hop and detail-oriented questions, whereas GraphRAG outperforms on multi-hop and reasoning-intensive queries."
> —— RAG vs GraphRAG: A Systematic Evaluation (2026)

代码语义搜索的特点：
- **单跳查询**：找到匹配的代码片段即可
- **语义模糊性**：开发者可能用不同词汇描述相同功能
- **规模巨大**：大型代码库需要向量索引来快速召回

**推荐方案**：混合架构——传统 RAG 做语义召回，GraphRAG 做依赖推理。

---

#### 场景 H：错误日志和故障排查知识库

**典型问题**：
- "这个错误信息是什么意思？"
- "之前遇到过类似的故障是怎么解决的？"

**为什么适合传统 RAG**：

故障排查记录通常是**非结构化文本**（日志片段、排查步骤、解决方案），相似度匹配（"类似的错误信息"）比图遍历更有效。

---

### 2.5 软件工程领域决策矩阵

| 场景 | 知识特征 | 查询类型 | 推荐方案 | 理由 |
|------|---------|---------|---------|------|
| 代码依赖分析 | 关系密集、有向图 | 多跳推理 | **GraphRAG** | AST 和依赖关系天然是图 |
| 架构影响分析 | 跨层关系、多源 | 路径遍历 | **GraphRAG** | 需要跨服务/模块/数据的多跳推理 |
| 编码规范查询 | 结构化、边界明确 | 精确查找 | **LLM Wiki** | 规模小、需人类维护、精确性高 |
| 架构决策记录 | 结构化、低频变更 | 事实检索 | **LLM Wiki** | ADR 适合 Markdown 结构化表示 |
| 小型项目理解 | 规模小 | 综合问答 | **LLM Wiki** | 全量可放入上下文窗口 |
| 大规模代码语义搜索 | 规模大、语义模糊 | 单跳相似 | **传统 RAG** | 向量相似度适合语义匹配 |
| API 快速参考 | 结构化、精确 | 精确查找 | **LLM Wiki** | 确定性读取避免干扰 |
| 故障排查知识库 | 非结构化文本 | 相似匹配 | **传统 RAG** | 日志和排查记录适合相似度匹配 |
| 设计模式发现 | 关系+语义混合 | 推理+相似 | **混合架构** | 向量召回 + 图遍历结合 |

---

## 三、金融业务领域分析

### 3.1 领域知识结构特征

金融业务的知识结构具有显著的**网络化、合规驱动、高风险**特征：

```
金融业务知识网络：
  实体层：客户、账户、交易、公司、监管主体
    ↓
  关系层：交易对手、担保关系、所有权链、资金流向
    ↓
  规则层：监管法规（Basel III/IV, MiFID II, AML/KYC）
    ↓
  证据层：审计线索、调查报告、可疑活动报告(SAR)
```

| 特征 | 描述 | 对技术选型的影响 |
|------|------|-----------------|
| **极高关系密度** | 金融实体间的关系是业务核心（交易、担保、控股） | 图结构几乎是必需 |
| **监管合规要求** | 需要完整的审计线索和可追溯性 | GraphRAG 的可解释性是关键优势 |
| **对抗性环境** | 欺诈者故意隐藏关系、制造噪声 | 需要图遍历发现隐藏模式 |
| **多源异构数据** | 核心银行、KYC、交易、公开市场数据 | 需要统一的知识图谱整合 |
| **高风险低容错** | 错误决策可能导致巨额损失 | 精确性和可审计性优先于效率 |
| **知识动态更新** | 交易实时发生，关系持续变化 | 需要增量图更新能力 |

### 3.2 金融业务：适合 GraphRAG 的场景

#### 场景 A：反洗钱（AML）与欺诈检测

**典型问题**：
- "账户 A 和账户 B 之间是否存在隐藏的关联交易？"
- "找出所有与 X 有共同设备/地址/受益人的账户"
- "这笔资金的完整流向路径是什么？经过了哪些中间账户？"
- "这个交易网络是否呈现分层（layering）特征？"

**为什么强烈需要 GraphRAG**：

> "Fraud rings rarely leave a clean trail in a single dataset. They share devices, addresses, beneficial owners, or transaction patterns across accounts that look unrelated at the surface. Graph traversal surfaces these hidden connections by following relationships multiple hops deep, something vector search cannot do."
> —— GraphRAG for Banking and Finance (Datavid, 2026)

AML 场景的核心是**多跳关系发现**：

```
账户A → 转账 → 账户B → 转账 → 账户C → 提现 → 实体D
  ↓          ↓
共享设备    共享地址    共同受益人
```

传统 RAG 的向量相似度完全无法回答 "经过 3 个以上中间节点的资金流向" 这类问题——这是典型的图遍历任务。

**关键要求**：
- **可审计性**：每个可疑发现必须能追溯到具体的交易路径和证据链
- **实时性**：新交易进入后，图需要增量更新以反映最新关系
- **误报控制**：GraphRAG 通过关系上下文帮助分析师快速理解警报背景，降低误报调查成本

**推荐方案**：Neo4j/TigerGraph + GraphRAG，结合 GNN 进行模式识别。

---

#### 场景 B：信用风险与担保网络分析

**典型问题**：
- "如果 X 公司违约，哪些借款人会受到连带影响？"
- "找出所有通过担保链间接关联的客户"
- "评估这个客户群的集中度风险"
- "某个关键供应商倒闭后，哪些贷款组合会暴露？"

**为什么强烈需要 GraphRAG**：

> "From borrower-only features → to ecosystem risk (suppliers, guarantors, regional exposures). Early warning via contagion paths (if a key supplier fails, who is structurally exposed?)."
> —— GraphRAG for Banking: BFSI Use Cases (Finextra, 2025)

信用风险的本质是**网络传染（contagion）**分析——单一节点的风险通过担保、交易、所有权等关系在网络中传播。这需要：

1. **路径遍历**：从违约实体出发，沿担保链找到所有受影响的节点
2. **社区发现**：识别高度互联的客户群（集中度风险）
3. **影响度量**：计算每个节点的网络中心性（系统性重要程度）

这些都是图算法的核心能力，传统 RAG 完全无法支持。

---

#### 场景 C：合规监管与法规追踪

**典型问题**：
- "MiFID II 和 Basel III 对风险管理的要求有什么重叠和差异？"
- "EU AI Act 中'高风险系统'的定义适用于我们的哪些产品？"
- "新发布的 AML 规定要求我们修改哪些内部流程？"
- "哪些法规条款之间存在冲突？"

**为什么强烈需要 GraphRAG**：

> "Traditional RAG relies on vector embeddings and semantic similarity... it fails in three critical areas: (1) Chunking Destroys Contextual Relationships, (2) Semantic Similarity is Not Semantic Equivalence, (3) The Gap Analysis Problem."
> —— Why GraphRAG Beats Traditional RAG for Regulatory Compliance (2026)

法规合规场景的核心挑战：

| 挑战 | 传统 RAG 的问题 | GraphRAG 的解决方案 |
|------|----------------|-------------------|
| 法规间的交叉引用 | 分块切断了条款间的引用链 | 图边显式保留"引用"关系 |
| 语义等价但法律效力不同 | "必须"和"建议"在向量空间中相近 | 节点属性区分 mandatory vs recommended |
| 法规空白分析（Gap Analysis） | 向量检索只能找到"存在"的内容 | 图遍历可发现"缺失"的要求 |
| 多法规对比 | 无法系统性对比两个法规框架 | 通过 Canonical ID 对齐相同概念 |

> "When the ingestion engine identifies 'Risk Management System' in the EU Act and 'Risk Management Framework' in the Singaporean guide, it assigns them the same canonical ID: risk_management_standard... the EU node has an attribute is_mandatory: true, while the Singapore node says is_mandatory: false. This is a structural conflict that a vector database would simply gloss over."
> —— GraphRAG for Regulatory Compliance

---

#### 场景 D：投资研究与市场情报

**典型问题**：
- "如果 X 公司下调业绩指引，哪些供应商和债权人最受影响？"
- "这家公司的高管与哪些其他公司有董事会关联？"
- "行业内的竞争格局和合作关系是怎样的？"

**为什么需要 GraphRAG**：

> "Analysts ask: 'If Company X misses guidance, which suppliers and lenders are most exposed?' GraphRAG returns impact paths with sources."
> —— BFSI GraphRAG Use Cases (Finextra, 2025)

投资研究需要**产业链图谱**（公司-产品-供应商-客户-竞争者）和**人物关系图谱**（高管-董事会-关联交易），这些都是典型的多跳图查询。

---

#### 场景 E：客户 360 度视图

**典型问题**：
- "这个客户在所有业务线的完整敞口是多少？"
- "客户的关联企业有哪些未结清贷款？"
- "推荐哪些适合这个客户的产品？"

**为什么需要 GraphRAG**：

客户数据分散在核心银行、KYC、交易、CRM 等多个系统中。GraphRAG 将这些孤岛数据统一为**客户关系图谱**：

```
客户 → 持有 → 账户 → 发生 → 交易 → 涉及 → 商户
  ↓        ↓
关联企业   担保 → 贷款
  ↓
政治敏感人物(PEP) → 风险标记
```

> "Relationship managers at commercial and private banks rely on a full picture of each client across accounts, products, transactions, and service interactions. GraphRAG maps those relationships into a queryable graph and lets an LLM produce account briefings, cross-sell recommendations, and retention-risk flags tied to specific data."
> —— GraphRAG for Banking (Datavid, 2026)

---

### 3.3 金融业务：适合 LLM Wiki 的场景

#### 场景 F：内部合规操作手册

**典型问题**：
- "可疑活动报告的提交流程是什么？"
- "新客户尽职调查需要收集哪些文件？"
- "内部控制测试的年度时间表是什么？"

**为什么适合 LLM Wiki**：

合规操作手册的特点：
- **规模可控**：通常几十到几百页
- **结构固定**：流程步骤、职责分工、时间节点
- **精确性要求极高**：流程不能模糊或近似
- **需要人工维护**：流程变更需要合规部门审批
- **低频更新**：除非法规变化，否则流程相对稳定

> "A well-organized markdown wiki covering 20–50 documents doesn't need semantic search. You already know what's in it."
> —— LLM Wiki vs RAG: A Decision Framework

---

#### 场景 G：金融产品说明和定价表

**典型问题**：
- "这个产品的手续费率是多少？"
- "定期存款的提前支取规则是什么？"
- "这个基金的风险等级和投资范围是什么？"

**为什么适合 LLM Wiki**：

产品说明和定价表是**精确、结构化、边界明确**的知识，需要 100% 准确的回答，不容许近似。LLM Wiki 的确定性读取确保答案来自文档原文。

---

### 3.4 金融业务：适合传统 RAG 的场景

#### 场景 H：金融新闻和市场评论分析

**典型问题**：
- "最近关于 X 公司的新闻有哪些？"
- "分析师对这支股票的观点是什么？"
- "这个行业的最新趋势是什么？"

**为什么适合传统 RAG**：

新闻和评论是**非结构化、语义相似性驱动**的内容。查询通常是 "找到类似主题的内容"，而非 "找到特定的关系路径"。向量相似度在这里是最自然的匹配方式。

> "RAG is stronger for factual/detail-oriented QA... RAG performs better on inference-style queries and summarization tasks, where detailed information is directly retrievable."
> —— RAG vs GraphRAG: A Systematic Evaluation (2026)

---

#### 场景 I：客户咨询的 FAQ 回答

**典型问题**：
- "如何开通网上银行？"
- "转账限额是多少？"
- "如何修改绑定手机号？"

**为什么适合传统 RAG**：

FAQ 类型的查询是**单跳、事实型**问题，答案通常存在于单一文档中。传统 RAG 的轻量级架构和快速响应更适合客服场景。

**注意**：如果涉及 "根据客户资料推荐产品" 或 "评估客户风险等级"，则需要升级到 GraphRAG。

---

### 3.5 金融业务领域决策矩阵

| 场景 | 知识特征 | 查询类型 | 推荐方案 | 关键理由 |
|------|---------|---------|---------|---------|
| 反洗钱/欺诈检测 | 交易网络、隐藏关系 | 多跳路径发现 | **GraphRAG** | 向量搜索无法做多跳关系遍历 |
| 信用风险/担保网络 | 网络传染、集中度 | 连通性分析 | **GraphRAG** | 需要社区发现 + 影响传播算法 |
| 合规监管/法规追踪 | 法规交叉引用、层级 | 多文档对比+Gap分析 | **GraphRAG** | 需要显式保留条款引用关系 |
| 投资研究/市场情报 | 产业链、人物关系 | 影响路径分析 | **GraphRAG** | 产业链图谱天然是图 |
| 客户 360 视图 | 多源异构、关系密集 | 关系整合 | **GraphRAG** | 需要整合核心银行+KYC+CRM+交易 |
| 内部合规操作手册 | 结构化、流程固定 | 精确查找 | **LLM Wiki** | 规模可控、精确性要求极高 |
| 产品说明/定价表 | 精确、边界明确 | 确定性读取 | **LLM Wiki** | 需要 100% 准确的原文 |
| 金融新闻分析 | 非结构化、语义驱动 | 相似性匹配 | **传统 RAG** | 向量相似度适合主题匹配 |
| FAQ/客服问答 | 单一文档、事实型 | 单跳查找 | **传统 RAG** | 轻量级、低延迟 |
| 审计报告生成 | 结构化+关系混合 | 聚合+路径 | **混合架构** | GraphRAG 做数据整合 + LLM Wiki 做模板 |

---

## 四、跨领域共性规律

### 4.1 "什么时候用什么"的普适决策树

```
开始
  │
  ├─ 知识规模 < 上下文窗口 且 结构固定?
  │   └─ YES → LLM Wiki (Karpathy 方法)
  │   └─ NO → 继续
  │
  ├─ 查询是否需要多跳关系推理?
  │   ├─ YES → GraphRAG
  │   └─ NO → 继续
  │
  ├─ 查询是否需要跨文档聚合/比较/Gap分析?
  │   ├─ YES → GraphRAG
  │   └─ NO → 继续
  │
  ├─ 知识是高度结构化且精确性要求极高?
  │   ├─ YES → LLM Wiki
  │   └─ NO → 继续
  │
  ├─ 查询是单跳事实型或语义相似型?
  │   ├─ YES → 传统 RAG
  │   └─ NO → 混合架构
  │
  └─ 默认 → 混合架构 (传统 RAG + GraphRAG + LLM Wiki)
```

### 4.2 关键风险提醒：GraphRAG 可能"帮倒忙"

根据 Zero-RAG (2025) 和知识过滤研究，在两个领域都需要注意：

> "Adding the redundant knowledge to the LLM instead degrades its performance by about 20 points... the redundant knowledge may distract the LLM and hinder it from utilizing corresponding knowledge."
> —— Zero-RAG: Towards Retrieval-Augmented Generation with Zero Redundant Knowledge (2025)

| 风险场景 | 描述 | 缓解措施 |
|---------|------|---------|
| 通用知识查询 | 问 LLM 已掌握的常识（如"什么是 REST API"） | 使用 Mastery-Score 评估，避免不必要的检索 |
| 冗余检索干扰 | 检索到与 LLM 内部知识冲突的过时信息 | 知识过滤机制，时间戳加权 |
| 工具过度使用 | LLM 倾向于过度调用外部检索（Knowledge Epistemic Illusion） | 查询路由，简单问题直接走 LLM |
| 噪声放大 | 图构建中的错误关系在多跳推理中被放大 | 关系置信度阈值、实体消歧 |

### 4.3 最优实践：混合架构

> "The most powerful hybrid arises when the 'wiki' is not a markdown folder but a governed data catalog - curated, certified, access-controlled metadata about every data asset in the enterprise."
> —— LLM Wiki vs RAG Knowledge Base (Atlan, 2026)

| 架构层 | 功能 | 软件工程示例 | 金融业务示例 |
|--------|------|-------------|-------------|
| **LLM Wiki 层** | 编码规范、架构决策、操作手册 | ADR、代码规范、部署流程 | 合规手册、操作流程、定价表 |
| **传统 RAG 层** | 语义搜索、非结构化内容 | 代码语义搜索、文档检索 | 新闻分析、研究报告、FAQ |
| **GraphRAG 层** | 关系推理、多跳查询 | 依赖分析、影响分析 | AML、信用风险、合规追踪 |
| **路由层** | 查询分类和动态分发 | 查询复杂度评估 | EA-GraphRAG / Zero-RAG 路由 |

---

## 五、实施建议

### 5.1 软件工程领域实施路线图

| 阶段 | 行动 | 预期收益 |
|------|------|---------|
| **Phase 1 (0-2周)** | 用 LLM Wiki 整理编码规范和 ADR | 立即提升 Agent 的架构理解能力 |
| **Phase 2 (2-6周)** | 传统 RAG 接入代码库做语义搜索 | 支持大规模代码库的语义查询 |
| **Phase 3 (6-12周)** | 构建代码知识图谱（AST + 依赖） | 支持依赖分析和影响分析 |
| **Phase 4 (12周+)** | 部署查询路由器，动态选择最优方案 | 根据查询类型自动选择最佳方案 |

### 5.2 金融业务领域实施路线图

| 阶段 | 行动 | 预期收益 |
|------|------|---------|
| **Phase 1 (0-4周)** | 用 LLM Wiki 整理操作手册和合规流程 | 确保基础合规知识的精确性 |
| **Phase 2 (4-12周)** | 构建客户/交易知识图谱 | 支持 AML 和风险分析 |
| **Phase 3 (12-20周)** | GraphRAG 整合法规图谱 | 支持多法规对比和 Gap 分析 |
| **Phase 4 (20周+)** | 部署混合架构 + 查询路由 | 全场景覆盖，动态优化 |

---

## 六、关键参考文献

| 来源 | 核心贡献 |
|------|---------|
| RAG vs. GraphRAG: A Systematic Evaluation (2026) | 明确 RAG 适合事实型查询、GraphRAG 适合推理型查询 |
| Zero-RAG (2025) | 冗余检索使性能下降约 20%，提出 Mastery-Score 路由 |
| GraphRAG for Banking and Finance (Datavid, 2026) | 金融业务四大场景（AML、合规、风险、客户）的 ROI 分析 |
| LLM Wiki vs RAG for Codebase Memory (MindStudio, 2026) | 代码库场景下 LLM Wiki 与 RAG 的详细对比 |
| GraphRAG for Regulatory Compliance (2026) | 法规合规场景下 GraphRAG 的三大优势 |
| BFSI Use Cases Where Graphs Disrupt (Finextra, 2025) | 金融图神经网络和 GraphRAG 的开放世界复杂性分析 |
| Software Dependency Analysis Using Graph Learning (2026) | 软件依赖分析的图学习方法论 |
| GraphRAG for Devs: Graph-Code Demo (2025) | 代码图谱的构建和应用实践 |
