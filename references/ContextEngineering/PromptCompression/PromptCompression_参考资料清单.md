# Prompt 压缩（Prompt Compression）参考资料清单

> 本文档汇总 LLM 提示词压缩方向的核心论文、工业方案、工具箱与综述，按主题分组标注优先级，对应 `../` 上下文工程主目录的 **G 组**。
>
> 适配场景：**本地小模型前置处理、削减无效 Token、完善提示词完整性**。
>
> 最后更新：2026-08-11

---

## 一、必读核心论文（优先级最高）

### 1.1 微软 LLMLingua 系列（工业落地首选）

| 资料 | 作者/来源 | 年份 | 核心贡献 | arXiv ID | 本地 PDF | 优先级 |
|------|----------|------|---------|----------|----------|--------|
| **LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models** | Huiqiang Jiang 等（Microsoft） | EMNLP-2023 | 初代标杆：预算控制器 + 迭代式 token 级压缩 + 分布对齐；最高 **20× 压缩比**且性能几乎无损。 | 2310.05736 | [`31-LLMLingua.pdf`](31-LLMLingua.pdf) | ⭐⭐⭐⭐⭐ |
| **LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios** | Huiqiang Jiang 等（Microsoft） | ACL-2024 | 面向 RAG 长上下文：**问题感知粗到细压缩** + 文档重排序对抗 "lost in the middle" + 子序列恢复。NaturalQuestions **+21.4%**（4× 减 token）；LooGLE **94% 成本降低**；10K tokens 2×–6× 压缩加速 **1.4×–2.6×**。 | 2310.06839 | [`32-Long-LLMLingua.pdf`](32-Long-LLMLingua.pdf) | ⭐⭐⭐⭐⭐ |
| **LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression** | Zhuoshi Pan 等（清华 + Microsoft） | ACL-2024 Findings | **GPT-4 蒸馏 token 分类器** + Transformer 双向编码（XLM-RoBERTa/mBERT）；任务无关，跨 LLM 泛化；**比初代快 3×–6×**，端到端加速 **1.6×–2.9×**（压缩比 2×–5×）。你重点需要。 | 2403.12968 | [`33-LLMLingua-2.pdf`](33-LLMLingua-2.pdf) | ⭐⭐⭐⭐⭐ |

> 项目仓库：<https://github.com/microsoft/LLMLingua>；项目主页：<https://llmlingua.com>

### 1.2 抽取式压缩基础范式

| 资料 | 作者/来源 | 年份 | 核心贡献 | arXiv ID | 本地 PDF | 优先级 |
|------|----------|------|---------|----------|----------|--------|
| **Selective Context** | Yucheng Li 等（Surrey） | EMNLP-2023 | 「本地小模型对输入文本打分筛选关键片段」的最早确立者；基于**自信息（self-information）**量化词/短语/句子的信息量，按百分位过滤；BBC / Arxiv / ShareGPT 上验证。 | 2304.12102 | [`34-Selective-Context.pdf`](34-Selective-Context.pdf) | ⭐⭐⭐⭐ |
| **Learning to Compress Prompts with Gist Tokens** | Jesse Mu 等（Stanford） | NeurIPS-2023 | **软提示压缩开山之作**；通过修改 attention mask 让模型在指令微调过程中同时学会压缩 prompt 为 gist tokens；**26× 压缩比，40% FLOPs 降低，4.2% 墙钟加速**；LLaMA-7B 与 FLAN-T5-XXL 双验证。 | 2304.08467 | [`35-Gist-Tokens.pdf`](35-Gist-Tokens.pdf) | ⭐⭐⭐⭐ |

> GitHub：<https://github.com/jxmorris12/gist-tokens>

---

## 二、生成式改写与小模型优化 Prompt

| 资料 | 作者/来源 | 年份 | 核心贡献 | arXiv ID | 本地 PDF | 优先级 |
|------|----------|------|---------|----------|----------|--------|
| **Nano-Capsulator: Paraphrase-based Prompt Compression** | Yu-Neng Chuang 等（Rice + Samsung） | 2024 | **自然语言格式 Capsule Prompt**：与软提示不同，可跨 LLM 迁移；针对 API-only LLM；用语义保持 loss + 长度约束 reward 优化。**81.4% 长度压缩，4.5× 推理加速，80.1% 预算节省**。 | 2402.18700 | [`36-Nano-Capsulator.pdf`](36-Nano-Capsulator.pdf) | ⭐⭐⭐⭐ |
| **Small Language Model Helps Resolve Semantic Ambiguity of LLM Prompt** | Zhenzhen Huang 等（UESTC + Kyung Hee） | 2026-04 | **DisambiguSLM**：SLM 在推理前显式识别语义风险点、多视角一致性检查、解决冲突，以逻辑结构化方式重组；不修改 LLM 内部机制；**推理性能 +2.5pp，$0.02/任务**成本。 | 2604.23263 | [`37-SLM-Ambiguity.pdf`](37-SLM-Ambiguity.pdf) | ⭐⭐⭐⭐ |
| **Style-Compress: An LLM-Based Prompt Compression Framework Considering Task-Specific Styles** | Xiao Pu 等（UCSB + Tsinghua + PKU） | 2024 | **任务自适应风格压缩**；通过风格变化（抽取/抽象/位置/可读性/格式感知）+ 上下文学习，让小模型零训练适配新任务；**10 样本适应后即与原 prompt 持平或更好**（压缩比 0.25 / 0.5）。 | 2410.14042 | [`38-Style-Compress.pdf`](38-Style-Compress.pdf) | ⭐⭐⭐⭐ |
| **Telegraph English: Semantic Prompt Compression via Structured Symbolic Rewriting** | Mikhail L. Arbuzov 等 | 2026-05 | **符号化结构化改写协议**：把自然语言 prompt 拆解为精简原子事实条目 + 符号化结构，降低大模型理解偏差、减少幻觉；与 LLMLingua-2 的 fixed-ratio 删 token 路线正交。 | 2605.04426 | [`41-Telegraph-English.pdf`](41-Telegraph-English.pdf) | ⭐⭐⭐⭐ |

---

## 三、多级级联与超长上下文压缩

| 资料 | 作者/来源 | 年份 | 核心贡献 | arXiv ID | 本地 PDF | 优先级 |
|------|----------|------|---------|----------|----------|--------|
| **Context Cascade Compression (C3)** | Fanfan Liu, Haibo Qiu | 2025-11 | **多级 SLM 流水线**：小 LLM 把长文本压缩为 32–64 个 latent tokens，大 LLM 解码。**20× 压缩比 98% 精度**，40× 仍 93%，**显著超越 DeepSeek-OCR**（97%@10×）。纯文本管线，简化部署。 | 2511.15244 | [`39-Context-Cascade-C3.pdf`](39-Context-Cascade-C3.pdf) | ⭐⭐⭐⭐ |
| **Cross-Lingual Token Arbitrage: Optimizing Code Agent Context Windows via Local LLM Preprocessing** | Mehmet Utku Çolak（Istanbul Technical University） | 2026-06 | **生产级边缘预处理中间件**：本地 Llama 3.2 (3B) via Ollama 做三项操作——跨语言翻译到便宜 token 空间、结构改写为 [CONTEXT]/[TASK]、5% token 预算阈值的 rewrite-with-fallback。**OMH-Polyglot 上 tokenization-overhead 比 2.05×**，prompt token **−34%–47%**；**Pareto 严格优于 LLMLingua-2**。 | 2606.03618 | [`40-Cross-Lingual-Token-Arbitrage.pdf`](40-Cross-Lingual-Token-Arbitrage.pdf) | ⭐⭐⭐⭐⭐ |

> 39 号 C3 项目：<https://github.com/liufanfanlff/C3-Context-Cascade-Compression>

---

## 四、综述论文与开源工程工具箱

| 资料 | 作者/来源 | 年份 | 核心贡献 | arXiv ID | 本地 PDF | 优先级 |
|------|----------|------|---------|----------|----------|--------|
| **Prompt Compression for Large Language Models: A Survey** | Zongqian Li 等（University of Cambridge） | NAACL-2025 | **领域全景综述**：抽取式裁剪、生成式改写、隐式向量压缩三大技术路线全覆盖；建立 task-aware / task-agnostic 分类法；详细讨论评价指标与基准。 | 2410.12388 | [`42-Prompt-Compression-Survey.pdf`](42-Prompt-Compression-Survey.pdf) | ⭐⭐⭐⭐⭐ |
| **PCToolkit: A Unified Plug-and-Play Prompt Compression Toolkit of Large Language Models** | Jinyi Li 等（HKUST(GZ) + HKU） | 2024 | **统一即插即用工具箱**：集成 LLMLingua / LongLLMLingua / LLMLingua-2 / Selective Context 等多种压缩算法；支持代码、数学问答等任务测评；模块化设计便于扩展。 | 2403.17411 | [`43-PCToolkit.pdf`](43-PCToolkit.pdf) | ⭐⭐⭐⭐ |
| **An Empirical Study on Prompt Compression for Large Language Models** | (ICLR-2025 Building Trust Workshop) | 2025-04 | **大规模实证对比**：覆盖市面上主流 Prompt 压缩方案的优缺点、幻觉表现、长文本适配能力；为方案选型提供实测数据。 | 2505.00019 | [`44-Prompt-Compression-Empirical-Study.pdf`](44-Prompt-Compression-Empirical-Study.pdf) | ⭐⭐⭐⭐ |

> 43 号 PCToolkit：<https://github.com/3DAgentWorld/Toolkit-for-Prompt-Compression>

---

## 五、补充参考：相关方向的延伸阅读

| 资料 | 关系 | 备注 |
|------|------|------|
| **RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation** (ICLR-2024) | RAG 检索文档前置压缩的工业方案 | 主清单已包含，可作扩展 |
| **SARA: Selective and Adaptive Retrieval-augmented Generation with Context Compression** (arXiv:2507.05633) | 统一 RAG 框架，迭代证据选择 + 压缩向量 | 主清单已包含 |
| **SkillReducer: Optimizing LLM Agent Skills for Token Efficiency** (arXiv:2603.29919) | Agent Skill 压缩，"少即是多"效应 | 主清单已包含 |

---

## 六、阅读优先级建议

### 快速入门（1–2 小时）
1. **LLMLingua-2** (33) — 最贴合「本地小模型前置处理、精简 Token、优化提示词完整性」需求
2. **LongLLMLingua** (32) — 掌握问题感知 + 文档重排序在 RAG 场景的作用
3. **PCToolkit** (43) — 看工程落地框架

### 系统理解（半天）
4. **LLMLingua** (31) — 吃透初代预算控制器 + 分布对齐思路
5. **Selective Context** (34) — 抽取式压缩的基础范式与自信息理论
6. **Gist Tokens** (35) — 隐式向量压缩方向
7. **Prompt Compression Survey** (42) — 建立完整技术图谱

### 前沿跟进（按需）
8. **Context Cascade C3** (39) — 多级级联上限探索
9. **Cross-Lingual Token Arbitrage** (40) — 生产级中间件范式
10. **Nano-Capsulator** (36) / **SLM-Ambiguity** (37) / **Style-Compress** (38) / **Telegraph English** (41) — 生成式改写四大方向
11. **Prompt Compression Empirical Study** (44) — 选型实测对比

---

## 七、技术路线全景图

```
                          Prompt 压缩（Prompt Compression）
                                  │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   抽取式裁剪            生成式改写              隐式向量压缩
  (Extractive)        (Generative)           (Soft Prompt)
        │                     │                     │
   ┌────┴────┐            ┌───┴───┐             ┌────┴────┐
   │         │            │       │             │         │
SC(34)  LLMLingua(31-33)  36,37   38,41         Gist(35)  AutoComp
 PPL     Token 分类器    胶囊   风格符号        软提示    上下文编码
   │         │            │       │             │         │
   └────┬────┴────┬───────┴───────┴───────┬─────┴────┬────┘
        │         │                       │          │
        │      39 (C3 级联)         40 (跨语言边缘) │
        │      多级 SLM 流水线      生产级中间件    │
        │                                            │
        └──────────────┬─────────────────────────────┘
                       │
                 综述/工具
              42, 43, 44
```

---

> **最后更新**：2026-08-11，基于已下载的 14 篇 PDF 与笔记整理；arXiv ID 已按官方页面校验。