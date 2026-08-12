# 论文摘要：跨语言 Token 套利用于代码 Agent 上下文窗口

> **原论文标题**：Cross-Lingual Token Arbitrage for Code Agent Context Windows
> **完整 PDF 文件名**：`40-Cross-Lingual-Token-Arbitrage.pdf`
> 摘要类型：Agent 设计参考 + 内容索引

## 适用场景

- 多语言代码助手场景（English, Turkish, Chinese, Arabic 等）下优化代码 agent (Cursor) 的提示 token 预算。
- 闭源 API 模型 (gpt-3.5-turbo, gpt-4o, gemini-2.5-flash-lite) 的成本优化。
- 通过用低 token 成本的源语言重写高 token 成本语言的输入来"套利" tokenizer。
- 工业级代码 agent 系统的输入预处理网关（TypeScript gateway）。

## 主要观点与方案

论文 (arXiv:2606.03618v2, Mehmet Utku Çolak, Istanbul Technical University, Jul 2026) 提出 Cross-Lingual Token Arbitrage 框架，利用不同语言在 cl100k_base tokenizer 上的 token 成本差异，把高成本语言的 prompt 转写为低成本英语再喂给目标 LLM。

1. **架构（§3.1）**：TypeScript gateway + 本地 Llama 3.2 (3B) via Ollama 作为 rewrite 服务。
2. **Cross-Lingual Token Arbitrage（§3.2）**：实测 token 成本系数——English 1.0, Turkish 2.16, Chinese 2.41, Arabic 3.00。把高成本语言 prompt rewrite 为 English 后再送 LLM，可显著降低总 token 数。
3. **Bi-Block / Tri-Block Schema（§3.3）**：输入格式拆为 [CONTEXT] + [TASK]（Bi-Block）或再加 [CONSTRAINTS]（Tri-Block），便于 rewrite 模块针对性处理。
4. **Regex-validated rewrite-with-fallback（§3.4）**：正则校验 rewrite 结果；若超过 5% token-budget 阈值则 fallback 到原 prompt，保证重写不会过度膨胀或破坏语义。
5. **OMH Benchmark（§4.1）**：构造 OMH-Wrapped (0.96x) 与 OMH-Polyglot (mean 2.05x) 评估套件。

## 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| Prompt token 减少 | 34-47% | §4 |
| Total token 减少 | 8.3-18.8% | §4 |
| vs LLMLingua-2 | 严格 Pareto 支配 | §4 |
| 测试模型 | gpt-3.5-turbo, gpt-4o, gemini-2.5-flash-lite | §4 |
| 评估套件 | OMH-Wrapped (0.96x 平均), OMH-Polyglot (2.05x 平均 token 扩展) | §4.1 |
| Rewrite 服务 | Llama 3.2 3B via Ollama | §3.1 |

## 参考项目/资源

| 资源 | 说明 |
|---|---|
| 论文 | arXiv:2606.03618v2, Jul 2026 |
| 代码 | github.com/utkucolak/cursor-prompt-optimizer |
| 模型 | Llama 3.2 3B (rewrite), gpt-3.5-turbo / gpt-4o / gemini-2.5-flash-lite (target) |
| 度量 | prompt tokens, total tokens, accuracy on OMH benchmark |
| 关键依赖 | TypeScript gateway, Ollama, cl100k_base tokenizer |
| 相关工作 | LLMLingua-2, LongLLMLingua, Style-Compress, Cross-lingual transfer, Token cost optimization |
