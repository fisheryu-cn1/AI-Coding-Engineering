# 论文摘要：LLMLingua-2 通过 token 分类做任务无关的提示压缩

> **原论文标题**：LLMLingua-2: Task-Agnostic Prompt Compression via Token Classification
> **完整 PDF 文件名**：`33-LLMLingua-2.pdf`
> 作者 / 年份：Huiqiang Jiang et al. (Microsoft Research)，2024
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 任务无关 (task-agnostic) 的通用 prompt 压缩，部署一次即可在多种下游任务与不同目标 LLM 上复用。
- RAG 中相同文档被多个 query 复用的场景，避免 task-aware 压缩对每个 query 重算的代价。
- 黑盒 LLM 场景下需要低延迟压缩器（XLM-RoBERTa / mBERT 而非 7B LLaMA）。
- 中英多语言、跨域 (LongBench/ZeroSCROLLS/GSM8K/BBH) 的泛化压缩。

## 主要观点与方案

LLMLingua-2 指出 task-agnostic 方法的两个关键问题（§1）：(1) 信息熵并非最优压缩指标 (ii) 因果 LM 仅单向 context。提出把 prompt 压缩重构为 token 分类问题，用 Transformer Encoder + Linear Head 进行双向保真压缩。

整体流程（Figure 1）：

1. **Data Distillation（§3.1, Figure 2）**：用 GPT-4-32k 在 MeetingBank 上做"只删词不加词"chunk-wise (≤512 tokens) 压缩；用 5 条 hard 指令约束 GPT-4 只能删除、不能重排/改写/缩写/新增（Figure 9）。Figure 3 显示不同 sentence 压缩率分布异质 (1x-20x)。
2. **Data Annotation（§3.2, Algorithm 1）**：用双向滑动窗口 + lemmatization + fuzzy match 把 GPT-4 压缩结果回标到原 token，处理三种障碍：Ambiguity、Variation、Reordering（Figure 5）。
3. **Quality Control（§3.3）**：定义 VR（Variation Rate, Eq.(1)）剔除 top 5% 幻觉样本，定义 AG（Alignment Gap = HR-MR, Eq.(2-4)）剔除 top 10% 错标注样本。
4. **Token Classification Model（§4.1, Eq.(5-7)）**：用 xlm-roberta-large (LLMLingua-2, 355M) 或 multilingual-BERT (LLMLingua-2-small, 110M) 作为 encoder，softmax 线性层预测每个词的 p(preserve)；用 cross-entropy 训练。
5. **Compression Strategy（§4.2）**：先按目标压缩比算出 Ñ = τN token 数，对所有 token 取 p_i 排序，保留 top-Ñ（保持原顺序）。可即插即用到 LLMLingua 的 budget controller 中（Appendix K）。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| MeetingBank QA EM | 86.92 (3.1x)，比 LLMLingua 67.52 高 +19.4，比 Selective-Context 66.28 高 +20.6 | Table 1 |
| MeetingBank Summ ROUGE-1 | 48.64 (3.1x)，比 LLMLingua 37.98 高 +10.7 | Table 1 |
| LongBench 3k-tokens AVG | 42.4 (vs LLMLingua 37.4, Selective-Context 32.0, Original 44.0) | Table 2 |
| LongBench 2k-tokens AVG | 39.1 (vs LLMLingua 34.6, Selective-Context 24.8, Original 44.0) | Table 2 |
| ZeroSCROLLS 2k AVG | 33.4（vs LLMLingua 27.2, Selective-Context 19.4, Original 34.7） | Table 2 |
| GSM8K EM | 79.08 (1-shot 5x), 77.79 (half-shot 14x)（vs Original 78.85） | Table 3 |
| BBH EM | 70.02 (1-shot 3x), 61.94 (half-shot 5x)（vs Original 70.07） | Table 3 |
| Mistral-7B MeetingBank QA | 76.22 EM @ 3x（vs Original 66.95, LLMLingua 50.45） | Table 4 |
| 端到端 latency 加速 | 1.6x (2x), 2.1x (3x), 2.9x (5x)（vs Original 14.9s → 5.2s @ 5x） | Table 5 |
| GPU 显存 | 2.1GB（vs LLMLingua 16.6GB, Selective-Context 26.5GB，~8x 减少） | Appendix I |
| 压缩延迟 | 0.4-0.5s（vs LLMLingua 1.5-2.9s, Selective-Context 15.5-15.9s） | Table 5 |
| LongBench-Zh 中文 AVG | 38.1 (vs LLMLingua 28.6, Original 42.5) | Table 10 |
| 用 TriviaQA 50k 扩增训练 | LLMLingua-2‡ AVG 39.5 | Table 6 |

消融（Table 7）：w/o Chunk-wise → 21x 压缩比 VR=6.0, F1=27.9（vs Chunk-wise 2.6x VR=2.2 F1=36.7）；Instruction1 (5% tokens) VR=13.7 F1=19.1。

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2403.12968v2 |
| 代码 | https://aka.ms/LLMLingua-2 |
| 数据集 | MeetingBank (Hu et al., 2023), LongBench, ZeroSCROLLS, GSM8K, BBH, TriviaQA-wiki |
| 评估 LLM | GPT-3.5-Turbo-0613, Mistral-7B-v0.1 |
| 训练硬件 | 训练 XLM-RoBERTa-large ~23h, multilingual-BERT ~16h |
| 度量 | Exact Match, BLEU, ROUGE-1/2/L, BERTScore |
| 关键依赖 | Huggingface Transformers, PyTorch 2.0.1, CUDA-11.7 |
| 相关工作 | LLMLingua, Selective-Context, LongLLMLingua, 500xCompressor, AutoCompressor |
