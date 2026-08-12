# 论文摘要：Gist Tokens 用 gist token 学习压缩提示

> **原论文标题**：Learning to Compress Prompts with Gist Tokens
> **完整 PDF 文件名**：`35-Gist-Tokens.pdf`
> 作者 / 年份：Jesse Mu et al. (Stanford)，2023
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 重复使用的 instruction / system prompt 高效缓存（如 ChatGPT 的 system message）。
- 想要在不重训每个任务的前提下用 prompt-tuning 思想压缩 KV cache 与指令前缀。
- decoder-only (LLaMA-7B) 与 encoder-decoder (FLAN-T5-XXL) Transformer LM 上的通用方法。
- 大规模 API 服务中需要把 KV cache 缩小一个数量级（26x）以降低存储与传输成本。

## 主要观点与方案

提出 gisting：将 prompt 压缩成一组 gist token 上的 KV activations，可在推理时缓存并零样本泛化到未见指令（§2）。形式上学习分布 p_G(y | G(t), x)，其中 G(t) 是 prompt t 的 gist 化 Transformer prefix。

**核心实现（§3, Figure 2）：用注意掩码本身代替额外训练目标**

1. 在 vocab 中加一个 gist token g，构造序列 (t, g_1, ..., g_k, x)。
2. 修改 attention mask：让 g 之后的 token（包括输入 x 和输出 y）不能 attend 到 g 之前的 prompt t，但可以 attend 到 g。迫使模型把 t 的信息压入 gist prefix 的 activations。
3. 对 decoder-only（如 LLaMA）：把因果 mask 左下三角的 gist 之前区域置零（图 2a）。
4. 对 encoder-decoder（如 T5）：encoder 中 t/x 互相屏蔽（保证 gist 不依赖于 x），decoder cross-attention 屏蔽 prompt t，仅保留对 gist 与 x 的访问（图 2b）。

理论视角（§2.1）：等价于 meta context distillation（Eq.(2)）— 把多种任务的 pLM(y|t,x) 蒸馏到一个 gist-augmented p_G(y|G(t), x)，由 LM 自身充当 HyperNetwork。

训练数据集 Alpaca+（§4.1）：Self-Instruct + Stanford Alpaca 合成数据，130k 样本，104k unique tasks；3 个验证集 (Seen/Unseen/Human-252)。对比基线：Positive Control (无 mask 改动)、Negative Control (无 t)、TF-IDF 关键词离散压缩。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 压缩比 | 1 gist token → 20x (Seen), 16x (Unseen), 26x (Human)；10 tokens → 2-5x | Table 1, Figure 3 |
| LLaMA-7B Seen | 99.2% ROUGE-L / 92.4% ChatGPT win (vs Pos Control 100%) | Table 1 |
| LLaMA-7B Unseen | 91.0% ROUGE-L / 98.8% ChatGPT win | Table 1 |
| LLaMA-7B Human OOD | 75.4% ROUGE-L / 84.9% ChatGPT win | Table 1 |
| FLAN-T5-XXL Seen | 93.2% / 103.9% ChatGPT win | Table 1 |
| FLAN-T5-XXL Human | 80.9% / 63.2% | Table 1 |
| Human Eval vs Pos (LLaMA) | 52.3% (95% CI 46.1-58.4) Gist win | Table 2 |
| Human Eval vs Pos (FLAN-T5) | 40.6% (95% CI 34.6-46.8) Gist win | Table 2 |
| Cohen κ (Human-Human vs Human-ChatGPT) | 0.24/0.29 (LLaMA), 0.33/0.29 (FLAN-T5) — ChatGPT ≈ 1 个标注员 | Table 2 |
| TF-IDF baseline | 8.6-30.5% ChatGPT win，几乎与 Neg Control 一致 | Table 1 |
| FLOPs 节省 (LLaMA) | 40% (vs No Caching)，vs Instruction Caching 仅 0.11% | Table 3 |
| Wall time (LLaMA) | 6.8% / 1.0% 减少；FLAN-T5 4.2% | Table 3 |
| KV cache 容量提升 | 26x more prompts 可缓存 (LLaMA-7B 每个 token 1.05MB) | §6 |

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2304.08467v3, NeurIPS 2023 |
| 代码 & checkpoints | https://github.com/jayelm/gisting |
| 模型 | LLaMA-7B (decoder), FLAN-T5-XXL (encoder-decoder) |
| 数据 | Alpaca+ (Self-Instruct + Stanford Alpaca, 130k 样本), Human split 252 |
| 度量 | ROUGE-L, ChatGPT win rate, Human win rate, Cohen κ |
| 训练硬件 | 4x A100-SXM4-80GB；LLaMA-7B ~7h, FLAN-T5-XXL ~25h |
| 关键依赖 | PyTorch 2.0, Hugging Face Transformers, DeepSpeed ZeRO-3 |
| 相关工作 | Prefix-tuning (Li & Liang, 2021), HyperTuning (Phang et al., 2022), Compressive Transformer (Rae et al., 2020), context distillation (Snell et al., 2022) |
