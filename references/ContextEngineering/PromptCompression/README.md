# PromptCompression 子目录

> 聚焦「**LLM 提示词压缩（Prompt Compression）**」主题的论文合集，覆盖抽取式裁剪、生成式改写、隐式向量压缩、多级级联、超长上下文、综述与工程工具集六大方向。
>
> 本子目录隶属于 [`../README.md`](../README.md)（上下文工程 ContextEngineering），对应 **G 组：Prompt 预处理与压缩**。所有论文已下载到本地，可离线阅读；摘要见 [`notes/`](notes/)。

## 目录结构

```
references/ContextEngineering/PromptCompression/
├── 31-LLMLingua.pdf                 # EMNLP-2023 微软首代抽取式压缩
├── 32-Long-LLMLingua.pdf            # ACL-2024  问题感知长上下文压缩
├── 33-LLMLingua-2.pdf               # ACL-2024 Findings GPT-4 蒸馏 token 分类器
├── 34-Selective-Context.pdf         # EMNLP-2023 自信息过滤基础范式
├── 35-Gist-Tokens.pdf               # NeurIPS-2023 软提示压缩
├── 36-Nano-Capsulator.pdf           # NeurIPS-2024 NL 格式胶囊改写
├── 37-SLM-Ambiguity.pdf             # 2026       SLM 解决提示词歧义
├── 38-Style-Compress.pdf            # 2024       任务自适应风格压缩
├── 39-Context-Cascade-C3.pdf        # 2025       多级 SLM 级联压缩 20x–40x
├── 40-Cross-Lingual-Token-Arbitrage.pdf   # 2026 代码 Agent 边缘预处理中间件
├── 41-Telegraph-English.pdf         # 2026       符号化结构化改写
├── 42-Prompt-Compression-Survey.pdf # NAACL-2025 全领域综述
├── 43-PCToolkit.pdf                 # 2024       统一工程工具箱
├── 44-Prompt-Compression-Empirical-Study.pdf  # ICLR-2025 Workshop 实测对比
├── README.md                        # 本文件
├── notes/                           # 论文文本摘录
│   ├── 31-LLMLingua.txt
│   ├── 32-Long-LLMLingua.txt
│   ├── 33-LLMLingua-2.txt
│   └── ... (其余 11 篇)
└── PromptCompression_参考资料清单.md  # 完整分类与重点标注
```

## 文件命名规则

沿用 `../` 上下文工程主目录的 `[序号]-[作者姓氏]-[简短标题].pdf` 规则；序号延续主目录（31–44），便于在主清单与阅读报告中交叉引用。

## 论文分组速查

### G-1：微软 LLMLingua 系列（工业落地首选）

| 编号 | 文件 | 主题 |
|---|---|---|
| 31 | `31-LLMLingua.pdf` | 微软首代：困惑度驱动 + 预算控制器 + 分布对齐；20× 压缩 |
| 32 | `32-Long-LLMLingua.pdf` | 长上下文：问题感知 + 文档重排序 + 子序列恢复；NaturalQuestions +21.4% |
| 33 | `33-LLMLingua-2.pdf` | GPT-4 蒸馏 token 分类器；3–6× 速度提升，抽取式裁剪新标杆 |

### G-2：抽取式压缩基础范式

| 编号 | 文件 | 主题 |
|---|---|---|
| 34 | `34-Selective-Context.pdf` | 自信息（self-information）过滤；EMNLP-2023 基础方法 |
| 35 | `35-Gist-Tokens.pdf` | 软提示压缩开山之作；26× 压缩，40% FLOPs 降低 |

### G-3：生成式改写与提示词优化

| 编号 | 文件 | 主题 |
|---|---|---|
| 36 | `36-Nano-Capsulator.pdf` | NL 格式胶囊改写；81.4% 长度压缩，跨 LLM 可迁移 |
| 37 | `37-SLM-Ambiguity.pdf` | SLM 显式解决歧义、补全残缺约束；$0.02/任务 |
| 38 | `38-Style-Compress.pdf` | 抽取/抽象风格自适应；训练免费，仅 10 样本适应 |
| 41 | `41-Telegraph-English.pdf` | 符号化结构化改写协议 |

### G-4：多级级联与超长上下文压缩

| 编号 | 文件 | 主题 |
|---|---|---|
| 39 | `39-Context-Cascade-C3.pdf` | 小→大模型级联；20× 压缩比 98% 精度，40× 仍 93% |

### G-5：2026 最新工程向论文

| 编号 | 文件 | 主题 |
|---|---|---|
| 40 | `40-Cross-Lingual-Token-Arbitrage.pdf` | 跨语言 token 套利 + 边缘预处理中间件（生产级） |

### G-6：综述与开源工程工具

| 编号 | 文件 | 主题 |
|---|---|---|
| 42 | `42-Prompt-Compression-Survey.pdf` | NAACL-2025 全景综述：抽取/生成/隐式三分 |
| 43 | `43-PCToolkit.pdf` | 即插即用统一工具箱 |
| 44 | `44-Prompt-Compression-Empirical-Study.pdf` | ICLR-2025 Workshop 大规模实证对比 |

## 使用建议

- **入门路径**：先读 `33-LLMLingua-2`（最贴合「本地小模型前置处理、精简 Token」需求），再追 `31-LLMLingua` → `32-Long-LLMLingua` 吃透微软技术演进。
- **范式扩展**：`34-Selective-Context` 理解自信息基础范式；`35-Gist-Tokens` 掌握隐式向量压缩方向。
- **生成式改写**：`36/37/38/41` 适合需要补全歧义、强化指令完整性的场景。
- **长上下文压缩**：`32/39/40` 适用于 RAG、代码 Agent 等超长上下文场景。
- **全景与落地**：`42-Prompt-Compression-Survey` 建立完整技术图谱；`43-PCToolkit` 做本地工程实现。

## 与上下文工程主目录的关联

| 主题维度 | 关联主目录章节 |
|---|---|
| 抽取式压缩对应「上下文选择」 | A 组「长上下文能力的极限」（01–06）解释为何压缩必要 |
| 生成式改写对应「上下文生成」 | F 组「Agent 上下文管理」（23–30）解释压缩后如何组织 |
| 工具与工业实践 | 主清单 § 五「关键工具与开源项目」已包含 LLMLingua、Mem0 |

## 重要修正与版本说明

> ⚠️ **arXiv ID 校验**：下列 arXiv ID 在原外部参考清单中标注有误，本目录已按 arXiv 官方页面校正：

| 本地编号 | 原参考清单标注 | **实际正确 arXiv ID** | 论文全名 |
|---|---|---|---|
| 34 | 2304.04408 | **2304.12102** | Unlocking Context Constraints of LLMs: Enhancing Context Efficiency of LLMs with Self-Information-Based Content Filtering |
| 35 | 2304.03418 | **2304.08467** | Learning to Compress Prompts with Gist Tokens |

> 36 号 Nano-Capsulator 应取 `2402.18700v1`（v2 内容已被覆盖为无关论文）。