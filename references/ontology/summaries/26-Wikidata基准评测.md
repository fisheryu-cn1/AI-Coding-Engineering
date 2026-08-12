# 论文摘要：WDBench（面向 RDF 档案的工作负载无关基准）

> **原论文标题**：WDBench: A Workload-Agnostic Workload Benchmark for RDF Archives
> **完整 PDF 文件名**：`wdbench-wikidata-benchmark_arxiv2203.08906.pdf`
> 作者 / 年份：Hala Skaf-Molli, Minh-Huy Nguyen, Hoang-Minh Truong, Hoang-Long Nguyen, Viet-Hoang Pham, Tien-Dat Nguyen, Nhat-Duy Nguyen, Quoc-Huy Duong, Thanh-Linh Vu, Pierre Senellart（University of Nantes / LS2N / Hanoi University of Science and Technology / LINAGORA / INRIA），2022，IEEE ICDE 2022（DOI: 10.1109/ICDE53745.2022.00205）
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **RDF 档案库（RDF archives）**——随时间演化的可查询、可版本化 RDF 三元组集合。
- 评估 SPARQL endpoint / triplestore 在 **变化数据（dynamic data）** 上的性能与可扩展性。
- 替代只支持静态只读场景的旧基准（BSBM / WatDiv / SPBench）。
- 给 Agent 设计"KG 版本化检索层"提供统一评测基线。

> 锚点：Abstract；§1 Introduction；§2 Related Work；§3 Preliminaries；§4 WDBench Design；§5 Evaluation；§6 Discussion。

## 2. 主要观点与方案

### 2.1 痛点

- 现有 RDF 基准（BSBM、WatDiv、SPBench）只覆盖 **static, read-only** 工作负载。
- Wikidata、DBpedia 等公共 KG 是 **动态档案**——长期演化、增删改。
- 缺乏专门评测 **RDF archives** 的方法 → 难以衡量 triplestore 在版本化 / 时间查询 / 演化场景下的实际表现。

### 2.2 核心概念

- **RDF Archive**：按时间维度组织的一组 RDF 数据集版本（snapshots）+ change sets。
- **Workload-agnostic**：基准应能反映真实查询分布，而非锁定某一类查询模式。

### 2.3 基准设计（§4）

- **数据源**：基于真实 **Wikidata dump**（latest-all）+ 演化日志。
- **查询集**：从真实 SPARQL 查询日志抽样、聚类，覆盖多种访问模式：
  - 简单 SELECT；
  - 复杂 join / filter；
  - 时间演化相关查询（snapshot query / delta query）。
- **度量**：
  - Workload agnosticity 指标：覆盖查询多样性的量化方法。
  - 查询响应时间、吞吐量、内存占用。
  - 数据加载时间（load time）。

### 2.4 评估（§5）

- 在 **Cqnarq**（早期小规模 RDF 档案）和 **Wikidata**（大规模真实档案）上做评测。
- 比较多个 triplestore 处理 RDF archive 工作负载的性能与扩展性。
- 验证 WDBench 的 workload-agnosticity 指标能区分不同档案的查询特性。

### 2.5 关联方法

- 静态基准：BSBM、WatDiv、SPBench、LUBM、SP2Bench、DBPSB、WGPB。
- RDF archive 系统：Cqnarq、Ozymandias、Semagrow、R&Wbase。
- 动态 KG：DBpedia Live、Wikidata Edit History。

> 锚点：Abstract；§1 Introduction；§2 Related Work；§4 WDBench Design；§5 Evaluation。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 数据规模 | Wikidata 全量 + Cqnarq 多快照 | §4 |
| 评测对象 | 多个 triplestore 在 RDF archive 场景 | §5 |
| 核心创新 | 提出 workload-agnosticity 量化指标 | §4 |
| 查询集 | 覆盖简单 SELECT / 复杂 join / 时间演化查询 | §4 |
| 对比基线 | BSBM、WatDiv、SPBench（静态场景） | §2 |
| 公开 | GitHub: terminusdb-labs/WDBench | §4 |
| 工具链 | 查询生成器 + 评测脚本 + 数据集 | §4 |
| 评估场景 | 动态 KG / Wikidata / DBpedia 类档案 | §5 |

> 锚点：Abstract；§1 Introduction；§4 WDBench Design；§5 Evaluation。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 会议 | IEEE ICDE 2022（38th International Conference on Data Engineering） |
| DOI | 10.1109/ICDE53745.2022.00205 |
| 单位 | University of Nantes / LS2N（France）；Hanoi University of Science and Technology（Vietnam）；LINAGORA；INRIA |
| 公开仓库 | github.com/terminusdb-labs/WDBench（数据集 + 查询生成器 + 评测脚本） |
| 关联基准 | BSBM、WatDiv、SPBench、SP2Bench、LUBM、UOBM、DBPSB、WGPB、Bowlognabench |
| 关联数据 | Wikidata dumps、Cqnarq |
| 关联系统 | Cqnarq、Ozymandias、Semagrow、R&Wbase、DBpedia Live、Wikidata Edit History |

> 锚点：§1 Introduction；§2 Related Work；§4 WDBench Design；§5 Evaluation；References。

## 5. 一句话索引（给 Agent 用）

> 给"Agent 检索层后端"用的 **RDF 档案版基准**——不只测静态只读，还测随时间演化的 Wikidata 类档案：覆盖多快照（snapshots + change sets）+ 真实查询分布 + workload-agnosticity 量化指标；如果 Agent 要支持 KG 版本化（snapshots / time-travel / delta query），WDBench 是比 BSBM / WatDiv / SPBench 更对口的评测起点。