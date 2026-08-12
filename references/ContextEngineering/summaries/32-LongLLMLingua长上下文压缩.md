# 论文摘要：LongLLMLingua 长上下文场景的提示压缩

> **原论文标题**：LongLLMLingua: Prompt Compression for Long Context Scenarios
> **完整 PDF 文件名**：`32-Long-LLMLingua.pdf`
> 作者 / 年份：Huiqiang Jiang et al. (Microsoft Research)，2024
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 长上下文场景下（10k+ tokens）的多文档 QA、多跳 QA、代码补全、摘要、ICL 等任务。
- 需要同时应对长上下文的三大挑战：高算力/成本、信息噪声导致性能下降、lost-in-the-middle 位置偏差。
- 检索增强生成 (RAG) 中需要对召回的多文档做 question-aware 压缩，平衡检索召回与压缩比。
- 通用黑盒 LLM（GPT-3.5、LongChat 等）在自然问题/LongBench/ZeroSCROLLS/MuSiQue/LooGLE 上的高效推理。

## 主要观点与方案

LongLLMLingua 在 LLMLingua 骨架上针对长上下文提出四个组件（Figure 2, §4）：

1. **Question-Aware Coarse-Grained Compression（§4.1）**：文档级重要性 r_k = -(1/N_c) Σ log p(x_i^{que,restrict} | x_k^{doc})（Eq.(2)），即在 question + restrict prompt（"We can get the answer to this question in the given documents"）条件下对每个文档算 PPL；Figure 3a 显示 r_k 在不同保留文档数下 Recall@1 超过 BM25、OpenAI-Embedding、Voyageai、SBERT、Gzip、Cohere-Rerank、Jina 等。
2. **Contrastive Perplexity Fine-Grained Compression（§4.1）**：token 级重要性 s_i = ppl(x_i|x_{<i}) - ppl(x_i|x^{que}, x_{<i})（Eq.(3)），等价于条件 pointwise mutual information（Eq.(8)）；Figure 3b 表明对比 PPL 能把 ground-truth 文档的 token 凸显出来，避免朴素 PPL 被无关高 PPL token 噪声淹没。
3. **Document Reordering（§4.2）**：按 r_k 升序重排文档，让关键文档出现在 prompt 两端以缓解 lost-in-the-middle 问题（Eq.(4)）。
4. **Dynamic Compression Ratio（§4.3）**：粗筛分数指导细粒压缩预算，τ_k^{doc} = max(min((1 - 2I(r_k)/K') δτ + τ^{doc}, 1), 0)（Eq.(5)），越相关的文档保留越多 token。
5. **Subsequence Recovery（§4.4）**：把 LLM 输出中能在压缩 prompt 中找到的最长子串回填为原文最长公共最短子串（Algorithm 1），恢复被截断的实体名称/数字。

实现细节（§5）：GPT-3.5-Turbo-0613 / LongChat-13B-16k 作为 target LLM，LLaMA-2-7B-Chat 作为 M_s，segment size=200, δτ=0.3。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| NaturalQuestions, GPT-3.5, 2x constraint | 1st 77.2, 5th 72.9, 10th 70.8, 15th 70.5, 20th 70.6；Reorder 76.2（vs 原始 75.7） | Table 1 |
| NaturalQuestions, GPT-3.5, 4x constraint | 1st 75.0, 5th 71.8, 10th 71.2；Reorder 75.5 | Table 1 |
| LongBench 3k tokens, GPT-3.5 | AVG 48.8（vs Original 44.0, BM25 40.6, OpenAI 41.7, LLMLingua 37.4） | Table 2 |
| LongBench 2k tokens, GPT-3.5 | AVG 48.3（vs Original 44.0, BM25 23.6, LongLLMLingua-rk 46.3） | Table 2 |
| MuSiQue F1 | 51.2 at 2x（vs Original 45.8, BM25 28.5, LLMLingua 40.1） | Table 7 |
| LooGLE long dependency QA | AVG 32.1 at 10x（vs Original 22.6, BM25 19.2, LLMLingua 17.3） | Table 8 |
| ZeroSCROLLS 2k, GPT-3.5 | AVG 32.7（vs Original 32.5, BM25 20.1, LLMLingua 27.2） | Table 6 |
| 端到端 latency 加速 | 1.4x (2x), 2.0x (4x), 2.6x (10k token prompt, 2x-6x ratio) | Table 1 latency |
| 成本下降 (per 1k samples) | Multi-doc QA ↓71.7%, LongBench ↓90.5%, ZeroSCROLLS ↓89.5%, MuSiQue ↓52.6%, LooGLE ↓94.0% | Table 9 |
| 计算量 | 比 LLMLingua 翻倍（question-aware 需要重算），但通过缓存 question 可缓解 | Limitation |

关键消融（Table 3, NaturalQuestions 2x）：w/o Question-aware Coarse → 42.1 (-35)；w/o Question-aware Fine → 75.8；w/o Dynamic Compression → 74.4；w/o Subsequence Recovery → 76.7；w/ Document Reordering 全位置均衡到 76.2。

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2310.06839v2 |
| 代码 | https://aka.ms/LongLLMLingua |
| 数据集 | NaturalQuestions Multi-doc QA (Liu et al., 2024), LongBench (Bai et al., 2023), ZeroSCROLLS (Shaham et al., 2023), MuSiQue (Trivedi et al., 2022), LooGLE (Li et al., 2023b) |
| 度量 | Accuracy/F1, EM, 类别得分；EM/NLL 等 |
| 关键依赖 | GPT-3.5-Turbo-0613, LongChat-13B-16k, LLaMA-2-7B-Chat, tiktoken |
| 相关工作 | LLMLingua (Jiang et al., 2023a), Selective-Context (Li et al., 2023c), LLMLingua-2 (Pan et al., 2024) |
