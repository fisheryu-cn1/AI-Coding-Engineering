# 论文摘要：MRCoder（Map–Reduce 仓库级代码上下文选择）

> **原论文标题**：MRCoder: An Efficient Context Selecting Approach for Repository-Level Code Generation
> **完整 PDF 文件名**：`25-Wang-MRCoder_v1.pdf`
> 作者 / 年份 / 出版：Peiding Wang, Li Zhang, Fang Liu（Beihang University），2018（arXiv 公开 2026-07-29；arXiv:2607.26805v1），ACM Manuscript Submitted
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 给**仓库级代码生成**（repo-level code generation）做"检索后 / 生成前"的上下文选择：在保留必要证据的同时把噪声块切掉。
- 当现有 RAG 方案存在"Top-K 越大噪声越多"现象、需要同时优化质量与效率时（Pass@1 先升后降曲线，Figure 1）。
- 在 CoderEval、DevEval 类 benchmark 上把 **LLM 推理成本**当一等约束对待——同时报告 tokens 与 wall-clock。
- 想用"小型 LLM 起草 + 大 LLM 还原"的**draft-based 加速**机制但担心一致性损失时。
- 作为**对比基线**评估其他方法（RepoFormer / CodeFilter / LongCodeZip / ReSum / RL-Coder / RepoCoder / GraphCoder / DietCode / SlimCode）。

> 锚点：Abstract；§1 Introduction（Figure 1 Motivation）；§2 Related Work。

## 2. 主要观点与方案

### 2.1 核心主张（"检索之后还想砍一刀"）

- Repo-level 代码生成的当前主流是 RAG 检索 Top-K 个相关 snippet 直接喂给 LLM；Top-K 一旦大，噪声块会拉低 Pass@1、抬高 token 与时延（Issue 1 & 2）。
- 现有方案在「轻量决策 token」（RepoFormer / CodeFilter）和「多轮 perplexity 选择」（LongCodeZip）之间两极分化：要么没真正滤掉噪声，要么选择阶段耗时太高。
- MRCoder 用 Map–Reduce 范式把**"判别是否有用"**这一任务外包给一个轻量 LLM 起草代码，再用一个**Structure-Aware Draft-Guided Selection** 选片段。

### 2.2 方法结构（§3, Figure 2）

- **任务形式化**：F = LLM(Q, {C_1, ..., C_K})；目标是选择有效 context 的子集送到 LLM。
- **预处理**：用 tree-sitter 把仓库切成 functions/classes 作为 context 单元；对标准答案 Jaccard > 0.9 的 context 过滤避免泄漏。
- **Map Phase**：
  - 把 Top-K 检索结果切成 size-M（M=2）的若干 group；
  - 小 LLM draft model 并行给每个 group 生成一份 draft code D_i；
  - **SADGS = API Call Matching + Logic Similarity** 两个信号：把 draft 中出现过的 API 调用映射回各 candidate context，再加 CodeBERT 计算的语义/逻辑相似度做 cross-reference，得到每个 candidate 的"有效度分数"。
- **Reduce Phase**：
  - 把 Map Phase 筛出的有效 context 聚合喂给目标大 LLM 生成 final code；
  - 把 draft D_i 当作**并行 verifiable speculation** 用于解码加速（每个 forward 验证 n 个 token，加速比 ≈ n）。
- **与现有方法关系**：
  - vs RepoFormer / CodeFilter：不是简单的"是否要这一块"，而是真正比对了草稿与候选的语义/逻辑关系；
  - vs LongCodeZip：不需要对每个候选跑独立 perplexity forward，依靠 draft 的"自然信号"近似评估，质量更好 / 时延更低。

> 锚点：§3.1 Task Definition；§3.2 Overview；§3.3 Map Phase；§3.3.1 Context partition & draft generation；§3.3.2 SADGS；§3.4 Reduce Phase + parallel verification。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| Pass@1 vs RAG | 最高相对 +52.7% | Abstract |
| Pass@1 vs LongCodeZip (SOTA baseline) | 最高相对 +31.3% | Abstract |
| Token 节省 | 30%–50% reduction vs RAG | Abstract |
| 推理时间减少 | 最高 -52.1% vs RAG / -47.6% vs RepoFormer | Abstract |
| 稳定性 | 在不同 Top-K 设置下都稳定优于 baselines（不出现 Top-K 大就垮） | Fig. 1; 实验部分 |
| 实际 benchmark | CoderEval、DevEval | §4 Experiments |
| Backbone 模型 | Qwen2.5-Coder + DeepSeek-Coder 双家族 | Abstract |

> 锚点：Abstract；§4 Experiments；Figure 1（Motivating Example）；Figure 2（Pipeline）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 代码 / 数据 | https://github.com/zhu-zhu-ding/MRCoder |
| 评测基准 | CoderEval；DevEval |
| 主要对比方法 | RAG；RepoCoder；RL-Coder；GraphCoder；RepoFormer；CodeFilter；LongCodeZip；ReSum；DietCode；SlimCode；AutoCompressor |
| 解析工具 | tree-sitter |
| LLM backbone | Qwen2.5-Coder；DeepSeek-Coder |
| 嵌入模型 | CodeBERT（语义 / 逻辑相似度） |
| 主题分类 | Software（Repository-Level Code Generation）；Context Selection；Efficient Inference；LLM；MapReduce |

> 锚点：§2 Related Work；§4 Experiments；参考文献列表。

## 5. 一句话索引（给 Agent 用）

> 做仓库级代码生成的检索后处理时，**别再直接把 Top-K 全部送进 LLM**：用 Map–Reduce 让一个小 LLM 对每个 context 分组起草一份 draft（D_i），再以 API call matching + 逻辑相似度（SADGS）选有效块，让大 LLM 只吃筛过的证据——在 CoderEval / DevEval 上同时拿 +31.3% Pass@1 vs LongCodeZip 与 30–50% token 省 / 最高 -52% 时延。
