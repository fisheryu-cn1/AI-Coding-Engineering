# 论文摘要：OwlPath（面向 LLM 缺陷修复的无损知识压缩）

> **原论文标题**：OwlPath: Lossless Knowledge Compression for LLM Bug Repair
> **完整 PDF 文件名**：`06-Zhang-OwlPath_v1.pdf`
> 作者 / 年份：Bo Zhang, Ren Pan, Huan Chen, Xiang Song（Shunfeng Technology / 顺丰科技），2026，arXiv:2607.27249
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **代码 Agent 的检索层**——当 bug 描述与目标符号没有字面重叠时，依赖结构依赖（图）而非字符串匹配。
- 把 **tree-sitter 提取的代码图**（CodeGraph SQLite）升级为可推理的 **OWL2 本体**，并用 SPARQL 1.1 property path 做传递闭包查询。
- 在 **SWE-bench / SWE-bench Pro / SWE-bench Lite** 上做端到端 bug 修复评测。
- 提供给 Agent 一个 **3KB 的 SKM（Software Knowledge Map）摘要**，压缩首次搜索空间。

> 锚点：摘要（Abstract）；§1 Introduction；§2 Related Work；§3 Method；§4 End-to-End Evaluation。

## 2. 主要观点与方案

### 2.1 核心论点（lossless knowledge compression）

- LLM 软件工程 Agent 受限于 ~100K token 上下文窗口；代码库通常百万行级别。
- 字符串/嵌入检索无法解决结构性查询：子类链、传递调用者、接口实现层级。
- OwlPath = OWL2 本体层 + SPARQL property path + OWL-SKM advisory 层。

### 2.2 OWL2 ontology projection（无损映射）

- 把 CodeGraph（SQLite）单遍 SQL pass 投影到 OWL2：
  - 每个节点 → `owl:NamedIndividual`（qualified_name / filePath / kind / line）。
  - `extends` → `rdfs:subClassOf`，声明 `owl:TransitiveProperty`。
  - `implements` → `:implements`，transitive。
  - `calls` → `:calls`，transitive + `owl:inverseOf`。
  - `contains` / `references` / `imports` 按语义标注。
- **无损保证**：每个源 tuple → 一个 OWL 公理；SPO 单射 → 不丢失结构信息。

### 2.3 Transitive-closure 检索引擎

- 用 rdflib（无 JVM 依赖）实现 SPARQL 1.1 property path（`:extends+`、`:calls+`、`:implements+`）。
- 首次查询一次性物化闭包 → 内存中 `(s, o)` 集合 → 后续查询 O(1) 摊销。
- 对比 SQL recursive CTE O(n^k)，k≥3 时差距跨数量级。

### 2.4 OWL-SKM advisory 层（3KB 摘要）

- Layer 1：Module Map（顶层包 + 文件数 + 符号数；按 `log(symbols)*0.5 + log(files)*0.3 + log(symbolsperfile)*0.2` 打分）。
- Layer 2：Issue Map（从 issue text 与 test patch 抽取 camelCase / snake_case / UPPERCASE 标识符 → codegraph explore 收集候选符号）。
- 首次 `owlpath search` 前一次性推送 3KB 摘要，引导 Agent 直接命中正确模块。

### 2.5 复杂度与集成

- 端到端：T_extract = O(n log n)（tree-sitter）+ T_project = O(n + m) + T_closure = O(n + m) 一次性 → O(1) 摊销每次查询。
- 1.4M 符号仓库单线程 4.7 分钟完成 extract-and-project。

> 锚点：§3 Method；§3.1 OWL2 projection；§3.2 Transitive-closure engine；§3.3 OWL-SKM；§3.4 Complexity analysis。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 18 matched SWE-bench Pro | OwlPath 严格通过 68.4% (13/19) vs CodeGraph 66.7% (12/18) | §4.1 |
| Token 消耗 | 1,416K vs 1,989K（-28.8%） | §4.1 |
| Wall-clock | 648s vs 1,071s（-39.5%） | §4.1 |
| SWE-bench Lite（9 实例） | 78% 正确率 vs 67%，省时 21.1% | 摘要 |
| 离线检索（67 实例） | recall 0.464 vs 0.226（+2.06×），hit rate 88.1% vs 59.7% | 摘要，§4.2 |
| 37 题结构检索 | recall@all 4.4% → 28.8%；transitive caller / interface 69–80% | 摘要，§4.2 |
| 仓库规模 | 1.4M 符号，4.7 分钟离线构建 | §3.4 |
| 支持语言 | Python / JavaScript / TypeScript / Go（tree-sitter 解析） | 摘要，§3 |

> 锚点：§4 End-to-End Evaluation；§4.1 SWE-bench Pro；§4.2 Offline retrieval；Table 1 / Figure 1。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2607.27249 |
| 代码图基座 | CodeGraph（GitHub 500K+ stars） |
| 解析器 | tree-sitter（多语言 AST） |
| OWL 库 | rdflib（Python，SPARQL 1.1 property path，无 JVM 依赖） |
| 评测 | SWE-bench Pro（Scale AI 公开 split 731 instances）、SWE-bench Lite |
| Agent 基线 | Hermes（同 agent、同 prompt 模板、同 tool-use budget、leak-proof git sealing） |
| 关联标准 | W3C OWL2（Motik et al. 2012） |

> 锚点：§1 Introduction；§2 Related Work；§3 Method；§4 Evaluation。

## 5. 一句话索引（给 Agent 用）

> 把代码图从 SQLite 升级到 OWL2 本体、SPARQL property path 一把抓多跳结构依赖、再加一份 3KB SKM 摘要引导首次搜索——比纯字符串 / CodeGraph 检索省 28.8% token 与 39.5% 时钟、recall 翻倍，是 LLM Bug Repair Agent 的"无损结构检索层"模板。