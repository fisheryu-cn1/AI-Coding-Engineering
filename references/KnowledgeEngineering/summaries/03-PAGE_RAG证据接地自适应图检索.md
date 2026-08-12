# 论文摘要：PAGE-RAG（投影感知 + 自适应路由 + 证据边界回答）

> **原论文标题**：PAGE-RAG: Evidence-Grounded Adaptive Graph Retrieval for Long-Document Question Answering
> **完整 PDF 文件名**：`03-Chen-PAGE_RAG_v1.pdf`
> 作者 / 年份：Xingyu Chen, Junxiu An, Jun Guo, Li Wang（Chengdu University of Information Technology / Beihang University），2026，arXiv:2607.19301
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **长文档 / 整书级 QA 的 GraphRAG 系统** 时：当现有方案对查询类型"一刀切"，或自动抽取的图不能替代原文。
- 评估 **图谱检索 vs 段落检索的边界条件** 时：本文论证"图是有损的语义骨架、不能取代原文"，并强制保留**文本兜底（textual retrieval floor）**。
- 设计 **可拒绝 / 可 abstain 的 RAG 系统** 时：当需要把"证据是否充足"做成显式的 answer-or-refuse 决策，而不是 prompt-level 软指令。
- 在 **多查询类型（local / relational / multi-hop / global）混跑** 的系统里做"按查询分派的路由"——本文给出 query profile (`α`, `β`, `γ`, `η`) 与检索算子组合 (`ρ(q)`)。
- 处理 **闭域敏感语料（医疗、法律、企档）** 时的访问边界设计基础。

> 锚点：摘要；§1 Introduction；§2 Related Work；§A Projection-aware Hybrid Repository Construction。

## 2. 主要观点与方案

### 2.1 投影感知视角：图是有损骨架，文本兜底不可关闭

- 自动抽取的图谱对原文本来说是 **lossy projection**——能组织实体/关系/事件/社区/路径，但丢失原子事实、修饰语、本地细节。
- 因此 GraphRAG 系统应同时保留：
  - 文本证据库 `T(D)`：可引用、可审计的事实底座；
  - 受控的图骨架 `G(D)`：`Σ(zj, T(D), P)`，受 profile 约束（叙事/概念/论证）和 source-evidence 约束；
  - **证据绑定 `b: V ∪ Eg → 2^T(D)`**——任何图节点 / 边都映射回支持它的文本证据；
- **始终开启的文本检索底座**原则：只在文本证据不够时才激活图算子。
- 图谱构造中加入 governed 子流程：evidence binding、schema/domain-range 校验、因果保护、confidence routing、保守的实体对齐。

> 锚点：§A Projection-Aware Hybrid Repository Construction；§1 Introduction 的 "projection-aware" 假设；Figure 1 左半部分。

### 2.2 文档 profiling 控制构造与检索

- 对每篇文档产出 profile `pi = (τi, δi, µi, σi, κi)`：
  - `τi` 文体（小说/论文/报告/混合）；
  - `δi` 领域或主题分布；
  - `µi` 主导话语模式（叙事 / 概念 / 论证）；
  - `σi` 内部结构（章/段/节）；
  - `κi` 边界（章节顺序、时间线、可见 scope）。
- Profile 不直接是答案证据，而是 **构造与检索的控制信号**：
  - 叙事文本保留章序、事件跨度、人物提及；
  - 概念 / 论证文本保留定义、命题、论证链、主题段；
  - 跨文档全局感知语料需要交叉主题与摘要结构。
- 抽取函数 `zj = Aµi(xj, pi)`——同一文本在不同 discourse mode 下抽出不同知识单元（叙事强调角色/事件/位置/因果，论证强调 claim/premise/evidence）。

> 锚点：§A "document profile" 子节；Equation 1–4。

### 2.3 Query-adaptive Retrieval Routing（核心机制）

- 对查询 `q` 估计 query profile `u = (α, β, γ, η)`：
  - `α` scope：local / relational / global；
  - `β` 是否需要多跳 / 路径；
  - `γ` 是否需要主题合成 / 社区摘要；
  - `η` 边界敏感性（是否可能超出可见 scope）。
- 五类可组合算子 `O = {Ot, On, Op, Oc, Or}`：
  - `Ot` 文本检索（BM25 或 dense）；
  - `On` graph-neighborhood（实体周围的局部子图）；
  - `Op` semantic-path（连接多个查询节点）；
  - `Oc` community-summary（全局主题）；
  - `Or` rerank（候选证据精选）。
- **多选而非互斥**：`ρ(q) = Π(u, O)` 把多个算子组合成一个 plan；常见 plan 是 `Ot + On + Or`。
- **证据预算 `B = (Bt, Bn, Bp, Bc)`** 按算子类型分配 token / 通路额度——避免对每个查询都做完整图遍历。
- 关键结论："vector-only 漏跨段关系 / graph-only 漏原文细节 / global-only 引入大量无关上下文"——所以**按查询证据需要做组合**。

> 锚点：§B Query-adaptive Retrieval Routing；Equation 5–8；Figure 1 中部（Routing policy / Evidence budget）。

### 2.4 Evidence-bounded Generation（核心机制）

- 阈值函数 `s(q, E) ∈ {0, 1}`：基于检索到的 bounded evidence set `E` 判定证据是否充足。
- 决策规则：
  - `s = 1` 输出有引用的答案 `a`；
  - `s = 0` 输出拒绝符号 `⊥`——**abstain 视为正确动作而非生成失败**。
- 与 prompt-only grounded generation 的区别：把"证据边界"从软约束升级为硬决策。未来可挂权限分层与敏感信息治理。
- 拒绝机制的双重作用：(1) 维持 evidence-boundary reliability；(2) 为私有 RAG 的访问边界管理提供前置基础（permission tier / sensitive-info control）。

> 锚点：§C Evidence-Bounded Generation；Equation 9–10；§D Ablation "No Evidence Constraint" 项。

### 2.5 混合仓库的完整公式

- 形式化：
  - `R(D) = (T(D), G(D), P, b)`；
  - `T(D) = {(xj, ej, mj)}` 文本证据（三元组 = 文本块、可引用 id、profile 派生的 metadata）；
  - `G(D) = (V, Eg, C, S)` 图骨架；
  - 证据绑定 `b` 提供可审计的"图→文"回链。

> 锚点：§A；Figure 1 完整图。

### 2.6 评估协议：边界—质量—效率三维

- **数据集**：
  - Simulacra and Simulation（Baudrillard 概念/论证书）：94 answerable + 12 unanswerable；
  - One Hundred Years of Solitude（Márquez 叙事小说）：88 + 12；
  - UltraDomain-Mix（公开全局感知基准，61 docs / 619K tokens / 125 题）。
- **基线**：
  - BDR-RAG（BM25+dense+rerank 的强力无图对照）；
  - LightRAG（graph-vector 轻量 GraphRAG）；
  - Microsoft GraphRAG（社区摘要 + map-reduce）。
- **指标**：
  - Strict Accuracy / Lenient Accuracy；
  - Correct Refusal on unanswerable；
  - Median Latency、Query Tokens/Question、Build Tokens；
  - **BBS（Boundary-Balanced Score）**：`2·Acc_lenient·Ref / (Acc_lenient + Ref)`——把 accuracy 和 refusal 的调和均值作为质量信号；
  - UltraDomain-Mix 四维 pairwise：comprehensiveness / diversity / empowerment / directness。

> 锚点：§D.1 Setup；Table 1（书级 QA）；Table 2（UltraDomain-Mix）；§E Ablation。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| **Simulacra & Simulation（book）** | PAGE-RAG strict 72.3 / lenient **92.6** / Refusal 12/12 / latency 14.9s / QTok 4,213 | Table 1 |
| **One Hundred Years of Solitude（book）** | strict 60.2 / lenient **87.5**（最高）/ Refusal 12/12 / latency 16.3s / QTok 7,052 | Table 1 |
| **vs LightRAG（book）** | PAGE-RAG 同样 12/12 refusal；latency 仅 14.9–16.3s（LightRAG 47.3–48.4s）；QTok 4.2–7.0k（LightRAG 9.2–15.3k） | Table 1 |
| **vs MS GraphRAG（book）** | MS 在 strict 上较弱（52.1 / 48.9）、refusal 11/9；但 ultra-wide 摘要型任务上 BTok 高得多（Simulacra 1.30M vs PAGE-RAG 842K；Solitude 4.41M vs 1.85M） | Table 1 |
| **vs BDR-RAG（book）** | BDR refusal 5/12 和 3/12——强力但无法 abstention；PAGE-RAG 同时保留高 accuracy 和 abstention | Table 1 |
| **UltraDomain-Mix vs MS GraphRAG** | 四维 pairwise 39/21/65, 36/26/63, 40/29/56, 27/75/23——MS 在质量维度胜出，但 **QTok 1,956 vs 136,509（~70× 差），latency 13.4s vs 38.7s** | Table 2 |
| **UltraDomain-Mix vs LightRAG** | PAGE-RAG 全面大幅胜出（如 directness 76/45/4） | Table 2 |
| **UltraDomain-Mix vs BDR-RAG** | comprehensiveness/diversity 接近（49/41/35, 51/37/37）；directness 23/75/27（偏弱） | Table 2 |
| **Ablation — Full PAGE-RAG** | Lenient Acc 90.1 / Refusal 24/24 / **BBS 94.8** | Table 3 |
| **Ablation — No Floor（去掉文本底座）** | Lenient Acc **58.2**（断崖）/ Refusal 24/24 / BBS 73.6——证明图不能替代原文 | Table 3 |
| **Ablation — No Evidence Constraint** | Lenient Acc 95.1（虚高）但 **Refusal 4/24** / BBS 28.4——揭示 accuracy 与 boundary 不可互换 | Table 3 |
| **Ablation — Raw Graph** | Lenient 86.3 / Refusal 24/24 / BBS 92.6；治理后 entity 4,300→1,919，community 1,024→194，孤立 entity 763→175，真实 path 使用 3→39 | Table 3 注释 |
| **Ablation — No Structural Guidance** | Lenient 87.9；routed path-using 子集 94.1→89.7——结构证据在路由命中时收益更大 | Table 3 |

> 锚点：§E Main Results；§F Ablation Study；Table 1–3；Figure 2（empirical quality–efficiency frontier）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2607.19301 |
| 代码 | https://github.com/CXY0112/PAGE-RAG |
| 数据集 | Simulacra and Simulation（Baudrillard 1994）；One Hundred Years of Solitude（Márquez 2018）；UltraDomain-Mix（Tao et al. ACL Findings 2026） |
| 基线系统 | DPR（Karpukhin et al. 2020）；BEIR（Thakur et al. 2021）；LightRAG（Guo et al. EMNLP Findings 2025）；Microsoft GraphRAG（Edge et al. 2024）；HippoRAG / HippoRAG 2（Gutiérrez et al.）；KAG（Liang et al. WWW 2025）；RAPTOR（Sarthi et al. ICLR 2024）；PathRAG（Chen et al. AAAI 2026）；A*Net（Zhu et al. NeurIPS 2023） |
| 关联方法 | RAG（Lewis et al. 2020）；PAL（Gao et al. ICML 2023）；Logic-LM（Pan et al. EMNLP Findings 2023）；神经符号综述（Hitzler et al. 2022） |
| 关联问题 | 七大 RAG 失败模式（Barnett et al. 2024）；Lost in the middle（Liu et al. TACL 2024）；知识冲突（Xu et al. EMNLP 2024） |

> 锚点：§1 Introduction；§2 Related Work；§A–C 方法；References。

## 5. 一句话索引（给 Agent 用）

> 长文档 GraphRAG 的核心反直觉：**图是有损骨架，不能替代原文**，所以正确范式是"常驻文本检索底座 + 受治理的图谱 + 按 query profile 自适应组合（Ot/On/Op/Oc/Or）+ 证据预算 + 把 abstain 升级为 answer-or-refuse 的硬决策"——本文用 BBS 指标同时监督 accuracy 和 refusal，去掉 evidence constraint 时 lenient accuracy 虚高但 refusal 从 24/24 崩到 4/24，这是把"是否回答"做成 first-class 优化目标的最直接证据。
