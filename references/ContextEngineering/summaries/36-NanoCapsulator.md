# 论文摘要：Nano-Capsulator 自然语言形式的提示压缩

> **原论文标题**：Nano-Capsulator: NL-Formatted Prompt Compression with Reward
> **完整 PDF 文件名**：`36-Nano-Capsulator.pdf`
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 需要在多个不同 LLM（Vicuna-13B、PaLM、Claude2、GPT-3.5）间共享压缩 prompt 的场景（natural language 形式保证 transferability）。
- Soft prompt 压缩因绑定特定 LLM 的权重而难以在 API 模型上复用的痛点。
- few-shot CoT 与阅读理解 (passage) 类型的 prompt 压缩。
- 训练开销敏感、需要在 LoRA + 单卡 48GB 上完成训练的场景。

## 主要观点与方案

Nano-Capsulator 把 soft prompt 压缩的两大限制（无法迁移 API LLM、难以精确控制长度）转化为自然语言生成问题，通过 (1) 语义保留 loss + (2) 长度受限的奖励函数联合训练（§3, Algorithm 1）。

1. **NL-formatted Prompt Compression（§3.1.1, Eq.(1)）**：用同一个 compressor F(·|θ_C) 同时执行两项任务：复制 (T_Rep) 与摘要 (T_Summ)。通过让 F 复制输入 K 得到 embedding e_K，再让其摘要生成 capsule C 得到 e_C，最小化 MSE 距离 L_Comp = E_C[D_dist(e_K || e_C)]，迫使生成的 capsule 在隐藏空间保留原语义。
2. **Prompt Utility Preservation（§3.1.2, Eq.(2)）**：定义 reward R_cap = E_Q[ I(G*(Φ(C_i)⊕Q_i) || G*(K_i⊕Q_i)) ]，其中 Φ(·) 是截断机制：超过长度阈值的 capsule 直接截短再算分，从而对超长 capsule 强制低分；I 可为 MSE embedding distance、accuracy 或 GPT4Eval 等。
3. **总目标（§3.1.3, Eq.(3)）**：L_Nano = L_Comp(·|θ_C) × R_cap(·|θ*)，θ* 是冻结的 G* 参数；用 LoRA 微调 Vicuna-7B 作为 compressor，单次前向即可得 capsule prompt。

实现细节（§4.1-4.2）：few-shot CoT 任务用 CSQA + GSM8K；阅读理解用 MultiRC + TriviaQA-Long（≤2k tokens）；训练 2x NVIDIA A40 48GB，Adam lr=5e-6，gradient clipping=0.8。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 压缩率 | 81.4% (CSQA), 81.25% (TriviaQA-Long), 74.71% (MultiRC), 69.3% (GSM8K) | Table 1 |
| CSQA Acc (Claude2) | 74.6（vs Manual 76.6, Zero-shot 69.4） | Table 1 |
| CSQA Acc (Vicuna-13B) | 58.8（vs Manual 60.4） | Table 1 |
| CSQA Acc (PaLM) | 75.5（vs Manual 73.7，**超过 Manual**） | Table 1 |
| GSM8K Acc (Claude2) | 84.9（vs Manual 85.6） | Table 1 |
| MultiRC Acc (Vicuna-13B) | 57.1（vs Original 57.3，几乎无损失） | Table 1 |
| TriviaQA-Long Acc (Claude2) | 90.1（vs Original 95.0） | Table 1 |
| API 成本节省 (Claude2) | CSQA -77.9%, GSM8K -63.9%, MultiRC -71.6%, TriviaQA-Long -80.1% | Table 2 |
| API 成本节省 (PaLM) | -77.9% / -63.9% / -71.6% / -80.1% (同趋势) | Table 5 |
| 推理 latency 加速 | 2.1x-4.5x；OPT-2.7B 在 batch=16 不再 OOM | Figure 8, 9 |
| Cross-LLM transferability | 在 Vicuna-13B / PaLM / Claude2 / GPT-3.5 间直接迁移 | Figure 3, Table 1 |
| 数据迁移 (MultiRC→BoolQ) | Vicuna-13B/Claude2 仅微小 accuracy 下降 | Figure 3 |
| Capsule 长度影响 | 150-250 tokens 区间最佳；过长引入噪声 | Figure 6 |
| vs AutoCompressors (GSM8K) | 19.7 vs 3.79 Acc（capsule 显著更好） | Table 4 |

消融（Figure 5）：w/o Reward 时 Claude2 TriviaQA 准确率显著下降；Figure 7：Capsule 优于 Selective-Context 与 Random Drop。

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2402.18700v1 |
| 训练硬件 | 2x NVIDIA A40 48GB, Adam lr=5e-6 |
| 模型 | Vicuna-7B (compressor base), Vicuna-13B/PaLM/Claude2/GPT-3.5 (evaluation) |
| 数据集 | CSQA, GSM8K, MultiRC, TriviaQA-Long (LongBench), BoolQ (cross-domain test) |
| 度量 | Accuracy (exact match), API cost $ |
| 关键依赖 | LoRA (PEFT), HuggingFace |
| 相关工作 | LLMLingua 系列, Gist Tokens, Selective-Context, Compressive Transformer, HyperTuning, AutoCompressors |
