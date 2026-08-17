# ContextEngineering 文献目录

本目录收集上下文工程（Context Engineering）相关核心论文，按阅读报告中的编号组织。当前已包含 2026 年 7 月新增的仓库上下文、压缩与 Agent Skills 论文。另有综述和扩展参考资料单独列出。

## 文件命名规则

```
[序号]-[作者姓氏]-[简短标题].[pdf|html|txt]
```

- **序号**：与阅读报告中的文献编号一一对应，便于快速定位。
- **作者姓氏**：主要作者或第一作者的姓氏。
- **简短标题**：论文核心概念的关键词，使用下划线 `_` 代替空格。

## 目录结构

```
references/ContextEngineering/
├── 01-Paulsen-Context_Is_What_You_Need.pdf
├── 02-Liu-Lost_in_the_Middle.pdf
├── ...
├── 17-Vogel-Codebase_Memory.pdf
├── 18-Mei-Survey_of_Context_Engineering.pdf   # 奠基性综述：首次将 Context Engineering 作为正式学科提出
├── 19-Zhang-Memory_in_Large_Language.pdf      # 扩展综述：LLM 记忆机制、评估与治理
├── 20-Mishra-TokenMizer.pdf                   # 2026-06：图结构会话记忆（Graph-Structured Session Memory）
├── 21-Hsu-HORMA.pdf                           # 2026-06：层级记忆导航（Hierarchical Memory Navigation）
├── 22-Xu-VISTA.pdf                            # 2026-06：可感知上下文的 Agent 仪表盘（Proprioceptive Dashboard）
├── 06-Hong-Context_Rot.html           # 仅有一篇 HTML 研究报告
├── 06-Hong-Context_Rot_files/         # HTML 引用的静态资源
├── 阅读报告_上下文工程文献综述.md      # 完整综述与横向比较
├── 上下文工程_核心参考资料清单.md      # 领域关键论文、工业实践、框架定义与工具资源索引
├── README.md                          # 本文件
└── notes/                             # PDF 的文本摘录/笔记
    ├── 01-Paulsen-Context_Is_What_You_Need.txt
    ├── ...
    └── 11-Mishra-Harness_Native_Software_Engineering.txt
```

### F 组：2026 年 7 月新增：仓库上下文、压缩与 Agent Skills

| 编号 | 文件 | 主题 |
|---|---|---|
| 23 | `23-Luk-ContextSniper_v3.pdf` | 代码记忆与精确证据选择 |
| 24 | `24-Qin-Agent_Retrieval_Bench_v1.pdf` | 仓库上下文检索评测 |
| 25 | `25-Wang-MRCoder_v1.pdf` | 仓库级上下文选择 |
| 26 | `26-Lin-Know_Before_Fix_v1.pdf` | QA 驱动仓库知识获取 |
| 27 | `27-Dang-Addressable_Recall_Compaction_v1.pdf` | 可寻址上下文压缩 |
| 28 | `28-Li-Agentic_Context_Management_v1.pdf` | 长程 Agent 上下文管理 |
| 29 | `29-Khatri-Do_Context_Files_Help_v1.pdf` | `AGENTS.md` / `CLAUDE.md` 消融研究 |
| 30 | `30-Gao-Registry_to_Repository_v2.pdf` | Agent Skills 的工程化演进 |

> 新增文件名中的 `_vN` 表示 arXiv 版本号；论文优先级和下载校验信息见 [`../arxiv_2026-07_manifest.md`](../arxiv_2026-07_manifest.md)。

### 2026 年 8 月版本更新

| 编号 | 文件 | 说明 |
|---|---|---|
| 07 | `07-Lulla-Impact_of_AGENTS_md_v2.pdf` | 07 号论文（arXiv:2601.20404）的 v2 版本记录（v1 原文件保留）。下载校验信息见 [`../arxiv_2026-08_manifest.md`](../arxiv_2026-08_manifest.md) |

### G 组：Prompt 压缩专题（独立子目录）

为了避免主目录 PDF 数量膨胀，专门建立 [`PromptCompression/`](PromptCompression/) 子目录聚焦「**本地小模型前置处理、削减无效 Token、完善提示词完整性**」方向：

| 子目录文件 | 主题 |
|---|---|
| `PromptCompression/31-LLMLingua.pdf` | 微软首代抽取式压缩（EMNLP-2023） |
| `PromptCompression/32-Long-LLMLingua.pdf` | 问题感知长上下文压缩（ACL-2024） |
| `PromptCompression/33-LLMLingua-2.pdf` | GPT-4 蒸馏 token 分类器（ACL-2024 Findings，重点） |
| `PromptCompression/34-Selective-Context.pdf` | 自信息过滤基础范式（EMNLP-2023） |
| `PromptCompression/35-Gist-Tokens.pdf` | 软提示压缩开山之作（NeurIPS-2023） |
| `PromptCompression/36-Nano-Capsulator.pdf` | NL 格式胶囊改写（2024） |
| `PromptCompression/37-SLM-Ambiguity.pdf` | SLM 显式解决提示词歧义（2026） |
| `PromptCompression/38-Style-Compress.pdf` | 任务自适应风格压缩（2024） |
| `PromptCompression/39-Context-Cascade-C3.pdf` | 多级 SLM 级联 20×–40× 压缩（2025） |
| `PromptCompression/40-Cross-Lingual-Token-Arbitrage.pdf` | 跨语言边缘预处理中间件（2026） |
| `PromptCompression/41-Telegraph-English.pdf` | 符号化结构化改写（2026） |
| `PromptCompression/42-Prompt-Compression-Survey.pdf` | 领域全景综述（NAACL-2025） |
| `PromptCompression/43-PCToolkit.pdf` | 即插即用统一工具箱（2024） |
| `PromptCompression/44-Prompt-Compression-Empirical-Study.pdf` | ICLR-2025 Workshop 实测对比 |

> 详见 [`PromptCompression/README.md`](PromptCompression/README.md) 与 [`PromptCompression/PromptCompression_参考资料清单.md`](PromptCompression/PromptCompression_参考资料清单.md)。其中 34/35 号的 arXiv ID 在外部参考清单中标注有误，已按 arXiv 官方页面校正（2304.04408 → 2304.12102；2304.03418 → 2304.08467）。



## 分组速查

| 组 | 主题 | 编号 |
|---|---|---|
| A 组 | 长上下文能力的极限与失效机制 | 01–06 |
| B 组 | 上下文工程的基础设施化 | 07–11 |
| C 组 | 代码特异性上下文技术 | 12–17 |
| D 组 | 奠基性与扩展综述 | 18–19 |
| E 组 | 2026 年 6 月新增：Agent 记忆与上下文管理 | 20–22 |
| F 组 | 2026 年 7 月新增：仓库上下文、压缩与 Agent Skills | 23–30 |
| G 组 | **Prompt 压缩专题（独立子目录）** | 31–44（见 `PromptCompression/`） |

## 使用建议

- 想快速了解某篇论文：先看 `notes/` 下对应编号的 txt 摘要。
- 想系统阅读：按阅读报告中的 A→B→C 顺序阅读 PDF/HTML。
- 找代码图谱/AI Coding 相关：直接查看 C 组（12–17）。
