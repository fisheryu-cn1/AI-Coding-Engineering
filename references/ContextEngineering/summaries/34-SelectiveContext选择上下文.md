# 论文摘要：Selective Context 基于自信息的内容过滤

> **原论文标题**：Selective Context: Self-Information Based Content Filtering
> **完整 PDF 文件名**：`34-Selective-Context.pdf`
> 作者 / 年份：Yucheng Li et al.，2023
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 通过丢弃低信息量片段提升 LLM 固定上下文窗口的利用率（arxiv 论文、新闻、对话）。
- 摘要、QA、对话与原文重建任务中需要在保留语义的同时大幅压缩输入。
- 黑盒 LLM (ChatGPT/GPT-3.5-turbo、Curie) 上快速部署，无需训练任何模型。
- 适合作为 baseline 与对照方法，分析 PPL/信息熵类压缩在极端压缩比下的极限。

## 主要观点与方案

Selective Context 论证 "LLM 不需要全部上下文也能正确回答"，提出基于 self-information 的词法单元过滤方法（§3）：

1. **Self-Information 计算（§3.1, Eq.(8)）**：用 base LM (Curie, GPT-2, OPT, LLaMA) 给每个 token x_i 计算 I(x_i) = -log2 P(x_i | x_0, ..., x_{i-1})。low PPL → low self-information → 对总体熵增贡献小（Shannon 1948）。
2. **Lexical Unit Merge（§3.2, Eq.(9)）**：利用 self-information 的可加性（Eq.(4-7)），把 token 级 I(x_i) 聚合为 phrase/sentence 级 I(u) = Σ I(x_i)。用 Spacy 做 noun-chunk 合并，sentence tokenizer 做 sentence 切分。
3. **Selective Retention（§3.3, Eq.(10-11)）**：不用固定阈值或 top-k，改用 percentile-based filtering：先按 I(u) 降序排序，再取 p-th percentile I_p（Eq.(10)），保留 I(u_i) ≥ I_p 的单元。Figure 2 给出一个 phrase 级 p=50 的可视化例子，剩下 57.2% tokens。

数据集（§4.1）：BBC News, ShareGPT, Arxiv 2023 三类语料；任务包括 Original Context Reconstruction、Summarisation、QA、Conversation；指标用 BLEU/METEOR/ROUGE/BERTScore。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| Summarisation (avg) | 0.275 BLEU / 0.570 ROUGE-1 / 0.911 BERTScore-F1（原始） | Table 2 |
| SC-0.2 (20% 删) | 0.251/0.563/0.909，BERTScore 几乎无下降 | Table 2 |
| SC-0.35 (35% 删) | Summ 0.212/0.533/0.903，QA 0.337/0.578/0.921 | Table 2 |
| SC-0.5 (50% 删) | QA ROUGE-1 0.487/BERTScore 0.907；Summ 0.170/0.500/0.896 | Table 2 |
| SC-0.65 (65% 删) | Summ BLEU 0.114，QA BLEU 0.157（显著下降） | Table 2 |
| SC-0.8 (80% 删) | 整体接近 random baseline | Table 2 |
| vs Random baseline | SC-0.35 时 0.3 BLEU / 0.55+ ROUGE-1，Random 仅 0.25 BLEU | Figure 3 |
| Conversation 任务 | reduction 0.2-0.8 下 BERTScore 仅从 0.877→0.832 缓慢下降 | Figure 4 |
| 数据源对比 | Arxiv optimal reduction 在 0.35-0.5；News 可达 0.5-0.65；Conversation 0.8 仍可工作 | Figure 5 |
| 重建任务 ROUGE-1 | 0.65 @ 0.2-0.35 删，0.59 @ 0.5 删 | §5.2 |

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2304.12102v1 |
| 代码 | https://github.com/liyucheng09/Selective_Context |
| 数据集 | BBC News (2023/03), Arxiv (2023/03), ShareGPT (post-ChatGPT release) |
| 度量 | BLEU, METEOR, ROUGE, BERTScore |
| 关键依赖 | GPT-3.5-turbo (ChatGPT), Curie (OpenAI API), Spacy noun-chunk, sentence tokenizer |
| 关键设置 | temperature=0.7；phrase-level filtering（sentence-level/token-level 留作未来工作） |
| 相关工作 | LLMLingua, LLMLingua-2, LongLLMLingua, Nano-Capsulator, Gist Tokens |
