---
title: "The SWE-Bench Illusion: When State-of-the-Art LLMs Remember Instead of Reason"
source_pdf: "21-Liang-SWE_Bench_Illusion_v4.pdf"
arxiv_id: "2506.12286"
arxiv_version: "v4"
authors:
  - "Shanchao Liang"
  - "Spandan Garg"
  - "Roshanak Zilouchian Moghaddam"
year: 2025
venue: "arXiv"
type: "评测对照 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：SWE-Bench 错觉——基准记忆污染问题（精读）

## 1. 适用场景

- 当你要**引用或汇报 SWE-Bench 系列解决率数字**（选型、采购、写报告）前，需要判断分数里有多少是记忆污染增益时，读这篇的量化证据与口径说明。
- 当你要为**自己的代码基准设计污染/记忆探测**时，直接复用这三个任务模板：文件路径识别（仅 issue 文本）、函数复现（函数体挖空）、前缀补全（逐字续写）。
- 当你在**构建新基准**、需要抗污染设计（时间控制 post-cutoff 任务、跨库验证、过滤路径泄漏样本）时，读 §3.2 的三个对照设定与 §6 的方法论呼吁。
- 当你要做**跨基准性能差异分析**（以相似任务间的表现落差作为记忆代理指标，而不依赖训练数据或模型内部访问权）时，读 §1 与 §5.2 的方法论证。
- 当你研究"为什么 agent 在熟悉 repo 上表现更好"或撰写**评测方法学**相关工作时，读 §4 的两类记忆模式（instance-specific / repository-bias）证据链。

> 锚点：Abstract; §1 Introduction; §2 Approach; §3 Experiment Setup; §4 Results; §6 Conclusion。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- 背景：SWE-Bench Verified 已成 LLM 软件工程能力核心基准，Tools + Claude 4 Opus 等已报出超 70% Pass@1；但 LLM 训练语料（LLaMA、PaLM、Codex 等）常包含 SWE-Bench 所源自的同一批公开 GitHub 仓库，训练/评测数据存在重叠（§1）。
- 核心问题：基准分数的提升在多大程度上反映**可泛化的问题求解能力**，而非对训练数据中记忆模式的复现（§1）。
- 切入点：把 issue 解决拆为两个子任务——**bug localization**（应需同时理解问题描述与代码库结构才能定位文件）与 **patch generation**（需理解代码语义并推理出修正），两者都可能被记忆"短路"：模型可能直接回忆起 issue-文件关联或逐字复现修好的代码（§1）。
- 方法论难点：记忆 vs 推理难以直接测量（模型合法地学过编码模式，且无通用编码能力基线）；解法是**跨基准性能差异分析**——真本事应在可比任务间表现一致，而记忆会导致与训练数据可能重叠的任务上异常高分（§1）。
- 三项贡献：跨基准记忆检测框架、两个受控诊断任务设计、基准已受污染的实证证据（76% 无上下文路径准确率 + 高 5-gram 重叠 + 外部基准显著下滑）（§1）。

### 2.2 三个诊断任务（§2.1 File Path Identification Task; §2.2 Function Reproduction Task; §2.3 Prefix Completion Task）

- **文件路径识别（§2.1）**：只给 repo 名 + issue 描述，不给任何仓库结构/代码/元数据，要求预测需修改的单个文件路径；与 GT patch 中任一文件路径精确匹配即正确。因 issue 文本自身可能含路径/import 语句，另设 filtered accuracy 只统计无显式路径提及的样本（§2.1；提示模板 Figure 2/6，含 DISCUSSION/RESPONSE 格式以获取模型推理过程）。
- **函数复现（§2.2）**：给出 issue 描述 + 挖掉 GT patch 所改函数的完整文件（函数签名、docstring 均不可得，仅留带序号的 RESPONSE 占位注释），要求单轮生成完整实现、无 repo 访问；在此约束下仍能高保真复现即说明记住了具体文本序列（§2.2；提示模板 Figure 7）。
- **前缀补全（§2.3）**：提取 GT patch 所改 bug 代码段之前的代码前缀，让模型续写，与 GT 逐字比对最多 N 行（N 为该处 GT 修改行数）；该设定直接镜像自回归预训练，与前一个任务分别在"整函数回忆"与"逐字序列续写"两个尺度上测记忆（§2.3）。

### 2.3 实验设置（§3.1 Benchmarks; §3.2 Additional experiment settings; §3.3 Metrics; §3.4 Models; §3.5 Prompt Templates）

- **主基准**：SWE-Bench-Verified（人工校验子集，12 个开源 Python 仓库 500 题）；SWE-Bench-C#（内部基准，11 个 C# 仓库 75 题，测跨语言迁移）；RefactorBench（100 道手工多文件重构任务取 39 题，issue 平均仅 14.6 tokens，搜索空间 1149.2 文件更大更难）（§3.1; Table 1——Verified/C#/RefactorBench 平均文件数 763.5/716.7/1149.2，issue 长度 451.2/586.2/14.6 tokens）。
- **三个对照设定（§3.2）**：Full-SWE-Bench（从全量 SWE-Bench 随机抽 200 题且不在 Verified 内）；SWE-Bench Extra（同 12 仓库但多为数据集截止日期之后新建的 217 个新 issue，区分实例级 vs 仓库级记忆的关键）；Outside-Repo Tasks（不在 SWE-Bench 内但大概率入训练集的 7 个热门仓库——jupyter/notebook、celery、aiohttp、scipy、numpy、pytorch、pandas——构造的 245 题）（§3.2.1–§3.2.3）。
- **指标（§3.3）**：Accuracy（与任一 GT 路径精确匹配的百分比）；Filtered Accuracy（仅统计 issue 无路径/import 泄漏的样本，Table 2 给出各基准提及比例：Verified 27.0% 提及/73.0% 未提及）；5-gram Consecutive Overlap（生成 5-gram 与 GT 精确匹配比例，频率感知防止重复短语膨胀）；Instance-Level Verbatim Match（前缀补全中至少一个 hunk 与 GT 完全一致的实例占比）。
- **模型（§3.4）**：10 个 SoTA 模型——OpenAI 侧 GPT-4o（2024-05/2024-08）、GPT-4.1、o3、o3-mini、o4-mini；Anthropic 侧 Claude 3.5 Sonnet、3.7 Sonnet、4 Sonnet、4 Opus；chat/Claude 生成上限 2,048 tokens，o 系 4,096；默认采样、官方 API。函数复现任务因资源限制只跑了 o3-mini 一个推理系模型（§4.3 脚注 1）。

### 2.4 主要发现（§4.1–§4.5）

- **路径识别的梯度衰减 = instance-specific memorization（§4.1.1）**：各模型在 Verified 上 60–76%、Full-SWE-Bench 上 57–71%、SWE-Bench Extra 上 50–68%，同一批仓库内逐步衰减，说明模型对被广泛传播/优化的精选题有不成比例的记忆（§4.1.1; Figure 8）。
- **外部仓库骤降 = repository-bias memorization（§4.1.2）**：Outside-Repo 任务（同样热门、同样大概率被训练）准确率一律 <53%；与 SWE-Bench 内高分形成鲜明对比，说明成功依赖的不只是仓库热度，而是对 SWE-Bench 12 仓库特定架构与问题分布的过拟合；RefactorBench 更低的部分原因受其超短 issue（14.6 tokens）混杂（§4.1.2; Table 1）。
- **过滤后模式依旧（§4.2）**：仅看 issue 不含显式路径的样本，Verified 仍最高（约 50–66%）、外部任务骤降的模式保持——这是最关键发现：定位能力不是表面字符串匹配，而是基于记忆的仓库/实例知识（§4.2; Figure 9）。
- **模型族差异（§4.1.3）**：OpenAI chat 系各基准间表现无稳定排序；o3 高于 o3-mini/o4-mini（能力更强或过拟合更重）；Claude 家族代际稳定提升（Sonnet 4 在 RefactorBench 上例外）；跨厂商一致的层级 Verified > Full > Extra > C#/Refactor/Outside 说明是训练数据暴露的系统性模式而非单家问题（§4.1.3）。
- **函数复现（§4.3）**：Verified 上 5-gram 重叠最高 34.9%，而 SWE 生态外最高仅 18.2%（RefactorBench 18.1%、Outside 13.9%）；层级为 Verified 34.9% > Full 28.7% > Extra 18.2%，且 Extra 与外部基准持平——尽管来自相同仓库，证明模型记住的是"被人工评估选入基准的规范解"，不是对仓库的一般熟悉度（§4.3; Figure 10）。
- **前缀补全直接记忆（§4.4）**：Verified 上 8 个模型的实例级逐字复现率为 11.7%–31.6%；Claude 家族随代际单调上升 12.1%→12.3%→21.4%→31.6%（Claude 4 Opus 近三分之一实例可逐字生成）；GPT 家族稳定在 17.4%–18.4%（训练数据清洗或架构差异）；o3-mini 最低 11.7%。仅有前缀、无任何问题描述即能逐字续写，强烈指向记忆而非推理（§4.4; Table 3）。
- **Δ5 对照（§4.5）**：定义 Δ5 = overlap5(生成, GT 补丁) − overlap5(生成, buggy 代码)，正值说明模型保留的是"修好之后"的代码碎片。Claude 在 Verified/Full/Outside 上持续为正，OpenAI 较弱（一般 < +2pp）；除 Claude 3.5 Sonnet 与 GPT-4.1 外所有模型在 Extra（post-cutoff 补丁不可能入训练集）上 Δ5 为负——补丁未见时记忆信号消失甚至反转，构成对照验证；GPT-4* 家族在 SWE-Bench C# 上差分最大（约 +3~5pp）超过 Claude，提示对 C#/.NET 补丁代码暴露更重或去重更松（§4.5; Figure 11）。

### 2.5 与已有抗污染方法的对比（§5.1 Coding Benchmarks and Agents; §5.2 Benchmark Contamination）

- 已有基准（SWE-Bench、BigCodeBench、SWE-Gym、EvoEval）与 agent 系统（SWE-agent、OpenDevin）的快速进步难以分辨真求解 vs 模式匹配（§5.1）。
- 现有抗污染两条路线的局限（§5.2）：**task mutation**（EvoEval 语义变换、AST 级变异、TaskEval 提示变体）能揭示对特定题面形式的过拟合；**metric-based probing**（perplexity、NLL、n-gram）不需改任务，但对商业模型拿不到隐状态，且 n-gram 相似度对复杂补丁是噪声指标（功能正确的解必然与 GT 有文本重叠）。
- 本文定位：**跨基准分析框架**——不需训练数据访问权与模型内部，即可在任何代码基准上系统检测可疑性能模式，是对上述两条路线的补充（§5.2）。

### 2.6 结论与呼吁（§6 Conclusion）

- 结论：10 个模型的系统评估证实两类记忆——instance-specific（SWE-Bench 生态内的梯度衰减，路径识别与函数复现双重证据）与 repository-bias（外部仓库上路径识别最多跌 47 个百分点，尽管这些仓库同样热门）；跨模型家族/厂商一致，说明是训练期对 SWE-Bench Verified 数据的系统性暴露（§6）。
- 呼吁：领域急需带**时间控制**（防训练泄漏）、**跨仓库验证**（测超出熟悉代码库的泛化）、**系统化跨基准分析**（区分记忆与可迁移技能）的评测框架；报告的进步应反映真实软件工程能力而非对数据集特定伪迹的过拟合（§6）。
- 含义（对读数者）：SWE-Bench Verified 分数含记忆成分，"SOTA 解决率"不可直接解读为通用软件工程能力；引用时须注明污染口径。

> 锚点：§2.1 File Path Identification Task; §2.2 Function Reproduction Task; §2.3 Prefix Completion Task; §3.2 Additional experiment settings; §4.1 File Path Identification Accuracy; §4.2 File Path Identification Accuracy on Filtered Instances; §4.3 Function Reproduction Result; §4.4 Direct Memorization on SWE-Bench Verified; §4.5 Comparison of 5-Gram Overlap for Buggy V.S. Ground Truth Code Snippet; §6 Conclusion。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 文件路径识别（仅 issue 文本，无 repo） | SWE-Bench Verified 上各模型 60–76%，最高 76%（o3） | Abstract; §4.1 Figure 8 |
| vs 外部热门仓库任务 | Outside-Repo（245 题、7 repo）准确率一律 **<53%**；RefactorBench 受超短 issue（14.6 tokens）影响更低 | §4.1.2; §3.1 Table 1 |
| SWE 生态内梯度（instance-specific） | Verified 60–76% > Full 57–71% > Extra 50–68% | §4.1.1 Figure 8 |
| 过滤后准确率（issue 无路径提及；Verified 73.0% 样本未提及） | 模式保持：Verified 仍最高（约 50–66%），外部任务骤降 | §4.2 Figure 9; Table 2 |
| 函数复现 5-gram 重叠 | Verified 最高 **34.9%** vs 生态外最高 18.2%（RefactorBench 18.1%、Outside 13.9%） | Abstract; §4.3 Figure 10 |
| 同仓库新题对照 | SWE-Bench Extra 18.2% ≈ 外部基准水平（同 12 仓库、post-cutoff issue） | §4.3 |
| 前缀补全逐字复现（Verified） | 8 模型 **11.7%–31.6%**；Claude 家族 12.1%→31.6% 单调升（Claude 4 Opus 31.6%）；GPT 家族 17.4%–18.4%；o3-mini 11.7% 最低 | §4.4 Table 3 |
| Δ5（补丁 vs buggy 相似度差） | Claude 在 Verified/Full/Outside 为正；Extra 上除 Claude 3.5 Sonnet 与 GPT-4.1 外全为负；GPT-4* 在 C# 上约 +3~5pp 最大 | §4.5 Figure 11 |
| 外部仓库路径识别跌幅 | 最多 **47 个百分点**（file-path identification，vs 外部 repo） | §6 Conclusion |
| 评测规模 | 10 个 OpenAI/Anthropic SoTA 模型；Verified 500 / Full 200 / Extra 217 / Outside 245 / RefactorBench 39 / C# 75 题 | §3.1; §3.2; Table 2 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2506.12286（v4，2025-12-01；Purdue University + Microsoft） |
| 被检基准 | SWE-Bench Verified（500 题，OpenAI 人工校验子集，https://openai.com/index/introducing-swe-bench-verified/）；SWE-Bench（https://arxiv.org/abs/2310.06770） |
| 对照基准 | RefactorBench（https://arxiv.org/abs/2503.07832，100 道多文件重构任务，本文用 39 题）；SWE-Bench-C#（Microsoft 内部基准，未公开） |
| 关联本目录 | ContextEngineering/12（SWE-bench 原文）、22 号（多模态迁移崩塌）；EvoEval（arXiv:2503.02296）与 TaskEval（arXiv:2407.21227）为任务变异路线对照 |

## 5. 一句话索引（给 Agent 用）

> 《The SWE-Bench Illusion》用三个诊断任务证明 SoTA LLM 在 SWE-Bench Verified 上部分靠**记忆**而非推理：仅凭 issue 文本（无仓库结构）识别 bug 文件路径准确率最高 76%（o3），而不在 SWE-Bench 内的热门仓库任务一律 <53%；函数复现 5-gram 连续重叠在 Verified 上达 34.9%、生态外仅 18.2%；前缀补全逐字复现实例占 11.7%–31.6%（Claude 4 Opus 31.6%）。提出 instance-specific 与 repository-bias 两类记忆模式，跨 10 个 OpenAI/Anthropic 模型一致成立，外部仓库路径识别最多跌 47 个百分点；引用 SWE-Bench 榜单须注明污染口径，新基准需时间控制与跨库验证。
