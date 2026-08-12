# 论文摘要：Wikidata SPARQL 引擎评测（GraphDB / Fuseki / Neptune / RDFox / Stardog / QLever）

> **原论文标题**：Evaluation of a Representative Selection of SPARQL Query Engines using Wikidata
> **完整 PDF 文件名**：`lam2023_sparql_engines_wikidata_eswc.pdf`
> 作者 / 年份：An Ngoc Lam, Brian Elvesæter, Francisco Martin-Recuerda（SINTEF AS, Oslo），2023，ESWC 2023
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 在 **Wikidata 全量（16.3B triples）** 上做 RDF triplestore 选型（替代不再维护的 Blazegraph）。
- 比较 **import / load / export / query performance** 四个维度。
- 评估 6 个系统：GraphDB EE / Jena Fuseki / Amazon Neptune / RDFox / Stardog / QLever。
- 用 **SP2 Bench**（125M–1B triples）做合成基准对比，把结果置于历史评测语境中。

> 锚点：Abstract；§1 Introduction；§3 Evaluation Setup；§4 Results；§5 Conclusion。

## 2. 主要观点与方案

### 2.1 候选选型逻辑

- 6 系统代表多样性：商业 vs 开源（Jena Fuseki、QLever）；云原生（Neptune 基于 Blazegraph）；内存型（RDFox）；持久型（其余）。
- 全部支持 SPARQL 1.1，提供 SPARQL endpoint。
- 选 QLever / Jena Fuseki 是因为 Wikimedia Foundation 正在评估它们替代 Blazegraph。

### 2.2 数据集

- SP2 Bench：125M / 250M / 500M / 1B triples（19 类 / 64 obj prop / 21 data prop）。
- Wikidata full version：latest-all.nt.gz（2021-11-19 下载），**16.3B triples / 1.78B subjects / 42.92K predicates / 2.93B objects / 1.2K classes / 17.1K obj prop / 27K data prop**。

### 2.3 查询集

- SP2 Bench：14 SELECT + 3 ASK。
- Wikidata：356 条用户查询 → 剔除 proprietary extensions / SPARQL 1.1 不合规 → **328 queries**。

### 2.4 SPARQL feature coverage（Table 2）

- SP2 Bench：distinct 35.29% / filter 58.82% / optional 17.65% / PropPath 0 / 时间/数值/字符串函数 0%。
- Wikidata：distinct 33.14% / groupby 29.11% / PropPath 35.73% / SetFnc 27.67% / StringFnc 9.8% 等更丰富。

### 2.5 关键发现

- 大多数系统能在超时前完成 328 条 Wikidata 用户查询中几乎全部。
- 但 **import / export** Wikidata 全量耗时对工业 / 学术项目仍偏长。
- 改进服务架构（去中心化 / 微服务）必须同时考虑 import/export 优化。

> 锚点：§3 Evaluation Setup；§4 Results；§5 Conclusion。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 候选数 | 6（GraphDB / Jena Fuseki / Neptune / RDFox / Stardog / QLever） | Abstract |
| 替代 Blazegraph 背景 | Wikimedia Foundation 评估中 | §1 |
| Wikidata 规模 | 16.3B triples / 1.78B subjects / 42.92K predicates | Table 1 |
| Wikidata 查询数 | 356 用户查询 → 328 合规查询 | §3 |
| SP2 Bench | 4 规模（125M / 250M / 500M / 1B triples） | §3 |
| 查询执行 | 大多数系统在超时前完成几乎全部 Wikidata 查询 | Abstract，§4 |
| 导入导出 | 时间偏长，是工业/学术瓶颈 | Abstract，§4 |
| 复用 | 脚本 / 数据 / 结果均开源 | §1 |

> 锚点：Abstract；§3 Evaluation Setup；§4 Results；Table 1 / Table 2。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 会议 | ESWC 2023（Extended Semantic Web Conference） |
| 单位 | SINTEF AS（Oslo, Norway） |
| 数据 | Wikidata latest-all.nt.gz（2021-11-19）；SP2 Bench 125M/250M/500M/1B |
| 候选 | GraphDB EE 9.10.0、Jena Fuseki 4.4.0（TDB2）、Amazon Neptune 1.0.5.1、RDFox 5.4、QLever、Stardog 7.8.0 |
| 关联方法 | LUBM、UOBM、BSBM、SP2 Bench、Bowlognabench、WatDiv、LDBC-SNB、TrainBench、OWL2Bench；DBPSB、FishMark、BioBenchmark、FEASIBLE、WGPB、WDBench |
| 替代背景 | Blazegraph（不再维护） |

> 锚点：§2 Related Work；§3 Evaluation Setup；References。

## 5. 一句话索引（给 Agent 用）

> 6 个主流 RDF triplestore × Wikidata 16.3B 全量 × 328 条真实用户查询——查询性能普遍过关，但 **import/export 是工业落地瓶颈**；Neptune / QLever / Fuseki 是 Wikimedia 替代 Blazegraph 的候选——给"大规模公共 KG Agent 检索层"一份基于 SP2 Bench 合成对比的真实查询评测基线。