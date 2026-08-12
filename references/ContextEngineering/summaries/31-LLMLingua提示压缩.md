# 论文摘要：LLMLingua 粗到细的提示压缩

> **原论文标题**：LLMLingua: Coarse-to-Fine Prompt Compression
> **完整 PDF 文件名**：`31-LLMLingua.pdf`
> 作者 / 年份：Huiqiang Jiang et al. (Microsoft Research)，2023
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 通过压缩提示词在保留语义的前提下加速黑盒 LLM 推理（GPT-3.5、Claude 等 API-only 模型）。
- 处理长上下文 CoT 提示、ICL 多示例与多文档场景，减少输入 token 数与推理成本。
- 需要在没有对黑盒 LLM 做 fine-tune 的前提下，把提示从几千 token 压到几百 token，同时保持任务表现。
- 自然语言普遍存在冗余（Shannon 1951），需要在不重训模型的情况下利用这种冗余降本。

## 主要观点与方案

LLMLingua 把提示压缩形式化为最小化 KL 散度 min_{x̃,τ} KL(P(ỹ|x̃), P(y|x))（§3, Eq.(1)），针对 Selective-Context 忽视 token 条件依赖和小模型分布与目标 LLM 分布不一致两个问题，提出三模块 coarse-to-fine 框架（§4, Figure 1）：

1. **Budget Controller（预算控制器，§4.1）**：对 instruction / demonstrations / question 分别设定不同压缩率；先在 demonstration 级别按 PPL 降序贪心保留高信息量样本（Algorithm 1），再把剩余预算按 Eq.(3) 分配给 instruction 与 question。在高压缩比下用句子/示例级过滤替代 token 级过滤，避免语义碎片。
2. **Iterative Token-level Prompt Compression（ITPC, §4.2）**：将粗筛后的 prompt 切成 segment，按 Eq.(5) 用前面已压缩段作为条件估计后续 token 的条件 PPL；动态阈值 γ_j 由 Eq.(6) 给出，按 Eq.(7) 保留 PPL > γ_j 的 token，缓解朴素 PPL 法的条件独立性假设。
3. **Distribution Alignment（分布对齐，§4.3）**：用 LLM 在 Alpaca 上生成的回答 instruction-tune 小模型 Ms（Eq.(8)），让 Ms 的 token 级 perplexity 分布更接近目标黑盒 LLM。

实现上使用 GPT2-Alpaca 或 Alpaca-7B 作为小模型 M_s（granular control coefficient k=2，τ_ins=0.85, τ_que=0.9, segment size=100，§5.1）。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| GSM8K Exact Match | 79.08 (1-shot, 5x), 77.41 (half-shot, 14x), 77.33 (quarter-shot, 20x) | Table 2 |
| BBH EM | 70.11 (1-shot, 3x), 61.60 (half-shot, 5x), 56.85 (quarter-shot, 7x) | Table 2 |
| ShareGPT BLEU/Rouge1 | 19.55/40.81 (3x), 27.36/48.87 (1.9x) | Table 1 |
| Arxiv-March23 BLEU/Rouge1 | 13.45/44.36 (9x), 23.15/54.21 (4x) | Table 1 |
| 端到端 latency 加速 | 1.7x (2x), 3.3x (5x), 5.7x (10x) | Table 6, GSM8K on V100 |
| 成本节省 | GSM8K $5.2→$0.5，BBH $12.8→$4.8，ShareGPT $0.7→$0.3，Arxiv $1.3→$0.2 (per benchmark) | Table 7 |
| 跨 LLM 迁移 (Claude-v1.3) | GSM8K 83.51 EM at 5x, 82.61 EM at 14x | Table 4 |
| 用小模型 GPT2-Alpaca | GSM8K 77.02 EM at 5x, 76.42 EM at 14x | Table 5 |
| 上限 | 20x 压缩比下 GSM8K 仅下降 1.5 点 | §6 |

关键消融（Table 3, GSM8K 1-shot）：去掉 ITPC EM 降到 72.93；去掉 Budget Controller 降到 73.62；w/o Distribution Alignment 78.62；w/o Dynamic Compression Ratio 77.26。

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2310.05736v2, EMNLP 2023 |
| 代码 | https://aka.ms/LLMLingua |
| 评估数据集 | GSM8K (Cobbe et al., 2021), BBH (Suzgun et al., 2022), ShareGPT (2023), Arxiv-March23 (Li, 2023) |
| 度量 | Exact Match (GSM8K/BBH)、BLEU/ROUGE/BERTScore (ShareGPT/Arxiv) |
| 关键依赖 | tiktoken, GPT-3.5-Turbo-0301, Claude-v1.3, GPT2-Alpaca, Alpaca-7B |
| 相关工作 | Selective-Context (Li, 2023), LLMLingua-2 (Pan et al., 2024), LongLLMLingua (Jiang et al., 2023b) |
