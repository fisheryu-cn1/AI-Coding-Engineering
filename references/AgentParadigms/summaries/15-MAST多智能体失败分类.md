---
title: "Why Do Multi-Agent LLM Systems Fail?"
source_pdf: "15-Cemri-MAST_MAS_Failures_v3.pdf"
arxiv_id: "2503.13657"
arxiv_version: "v3"
authors:
  - "Mert Cemri"
  - "Melissa Z. Pan"
  - "Shuyi Yang"
  - "Lakshya A. Agrawal"
  - "Bhavya Chopra"
  - "Rishabh Tiwari"
year: 2025
venue: "arXiv"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：MAST——多智能体系统失败分类法

## 1. 适用场景

- 在"要不要把单 agent 升级为 MAS"的架构决策上需要证据，或要论证"MAS 失败主要源于系统/组织设计而非底层模型能力"时（§1; §5.3）。
- 上线 MAS 之前按 checklist 写清任务/角色/终止规范与验证机制，或在失败之后对执行轨迹做根因归因——直接对照 14 种失败模式（§4; Appendix A）。
- 需要构建大规模 agent 失败数据集或 LLM-as-a-Judge 自动标注管线时，参考其 Grounded Theory + 多轮 IAA + 标注器校准的完整方法学（§3.1–§3.4）。
- 选型底层 LLM 或比较两个 MAS 框架的失败画像（如 GPT-4o vs Claude 3.7、MetaGPT vs ChatDev）时（§5.1; Appendix F; Appendix I）。
- 设计 MAS 改进干预实验（改 prompt vs 改拓扑）并用统计显著性检验评估效果时（Appendix G; Appendix H）。

> 锚点：Abstract; §1 Introduction; §3 The Multi-Agent Systems Dataset; §4 The Multi-Agent System Failure Taxonomy; §5 Towards better Multi-Agent LLM Systems。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

MAS 在软件工程、科研、通用 agent 等领域被广泛采用，但在流行基准上的性能提升经常很小，甚至不敌单 agent 或 best-of-N 采样等简单基线；论文报告 7 个 SOTA 开源 MAS 的失败率达 41%–86.7%（§1；Appendix B Figure 5 按系统给出成功率 41.0%–86.7%，如 AppWorld/Test-C 86.7%、AG2/OlympiadBench 41.0%）。由于 MAS 失败根因纠缠（模型行为与系统设计的复合效应）且缺乏标准化失败定义，作者提出核心问题：Why do MAS fail?（§1; §3）

### 2.2 MAST-Data 数据集与标注方法学（§3）

- **数据规模**：MAST-Data 共 1642 条带标注执行轨迹，覆盖 7 个主流开源 MAS（MetaGPT、ChatDev、HyperAgent、AppWorld、AG2/MathChat、Magentic-One、OpenManus），任务横跨 coding、math、通用 agent；另发布 MAST-Data-human（IAA 研究中 21 条由 3 名人类专家逐条标注的轨迹）（Abstract; §1; §3.4; Table 1）。
- **Grounded Theory 编码（§3.1）**：先从 5 个框架（HyperAgent/AppWorld/AG2/ChatDev/MetaGPT）收集 150 条轨迹（平均超 15,000 行/条），6 名专家以开放式编码、持续比较、memoing 等技术迭代分析至理论饱和，每名专家投入 20+ 小时。
- **标准化失败标签（§3.2）**：3 名专家对随机轨迹独立标注、3 轮 IAA 迭代精化定义，最终 Cohen's Kappa 达 κ=0.88，共识讨论另花约 10 小时。
- **LLM-as-a-Judge 管线（§3.3）**：用 OpenAI o1 + MAST 定义 + few-shot 人类标注示例做可扩展标注，与专家标注一致性 accuracy 94%、κ=0.77（Table 2）。
- **泛化验证（§3.4）**：在开发期未见的 2 个新 MAS（OpenManus、Magentic-One）与 2 个新基准（MMLU、GAIA）上，人类 IAA 仍达 κ=0.79，证明 MAST 无需修改即可迁移。
- **配置详情（Table 1）**：7 个框架各 30 条（HE+HA+LA）核心配置 + ProgramDev-v2 上 GPT-4o/Claude-3.7/Qwen2.5-Coder-32B/CodeLlama-7b 各 100 条 + AG2 三基准（OlympiadBench 206/GSMPlus 193/MMLU 168）与 Magentic-One GAIA 165 条；闭源 Manus 因不提供完整轨迹被排除（其 ProgramDev 人工评核成功率 60%）（Appendix B.3）。

### 2.3 MAST 分类法全貌（§4; Figure 1; Appendix A）

14 种失败模式归 3 大类，并映射到 Pre-Execution/Execution/Post-Execution 阶段；占比基于 1642 条轨迹（Figure 1）：

- **FC1 System Design Issues（44.2%）**：FM-1.1 Disobey Task Specification（11.8%）、FM-1.2 Disobey Role Specification（1.50%）、FM-1.3 Step Repetition（15.7%，单模式最高）、FM-1.4 Loss of Conversation History（2.80%）、FM-1.5 Unaware of Termination Conditions（12.4%）。Insight 1：失败不只是底层模型问题——设计良好的 MAS 用同一模型即可获得性能增益（§4 FC1）。
- **FC2 Inter-Agent Misalignment（32.3%）**：FM-2.1 Conversation Reset（2.20%）、FM-2.2 Fail to Ask for Clarification（6.80%）、FM-2.3 Task Derailment（7.40%）、FM-2.4 Information Withholding（0.85%）、FM-2.5 Ignored Other Agent's Input（1.90%）、FM-2.6 Reasoning-Action Mismatch（13.2%）。Insight 2：MCP/A2A 等通信标准化不足以解决 FC2——同框架内自然语言交流也出错，本质是"theory of mind"塌缩，需要更深的社交推理能力（§4 FC2）。
- **FC3 Task Verification（23.5%）**：FM-3.1 Premature Termination（6.20%）、FM-3.2 No or Incomplete Verification（8.20%）、FM-3.3 Incorrect Verification（9.10%）。Insight 3：需要多级验证——仅靠末段低层检查（如能否编译）不够，ChatDev 生成的国际象棋程序通过编译检查却有运行时规则缺陷（§4 FC3）。
- 在 210 条轨迹子集（每系统前 30 条）上类别分布为 41.8%/36.9%/21.3%（Figure 4）；三类别间相关性低（0.17–0.32），支持分类结构有效性（Appendix E）。

### 2.4 失败分布与模型/架构影响（§5）

- **系统特异性画像（§5.1）**：AppWorld（星型拓扑、无预定义流程）高发 FM-3.1 过早终止；OpenManus 高发 FM-1.3 步骤重复；HyperAgent 主导模式为 FM-1.3 与 FM-3.3——没有一刀切的解法。
- **模型影响（§5.1; Appendix F）**：MetaGPT 内 GPT-4o 总体优于 Claude 3.7 Sonnet，FC1 失败少 39%；两模型 FC3 都高，说明验证难题与模型选择相对独立。
- **架构影响（§5.1; Appendix F）**：同用 GPT-4o，MetaGPT 比 ChatDev 在 FC1/FC2 上少 60–68% 失败（SOP 约束强），但 FC3 多 1.56 倍（ChatDev 有专门 testing/review 阶段）——架构选择重塑失败分布。
- **开源模型（Appendix I）**：Qwen2.5-Coder-32B-Instruct 显著稳健于 CodeLlama-7b-Instruct-hf，但两者失败频率均高于闭源模型（GPT-4o/Claude 3）。
- **失败致命度（Appendix J.1）**：成功轨迹并非无失败；FM-1.5、FM-2.4 几乎只出现在失败轨迹（致命），而 FM-3.2/FM-3.3 在成功轨迹中也高频（系统性弱点但不立即致死）；基准越难失败率越高（GSM vs MMLU vs OlympiadBench）（Appendix J.2）。
- **MAST 作为开发工具（§5.2）**：聚合成功率会掩盖细节，LLM 标注器 + MAST 可给出定量失败画像，干预后可复查哪些模式被消解、有何 trade-off（Appendix H.3）。

### 2.5 干预案例研究：战术性修补 vs 结构性重设计（§5.3; Appendix G; Appendix H）

- **策略框架（Appendix G, Table 4）**：战术性方法（清晰角色/任务定义、会话模式设计、自验证、交叉验证、模块化 agent）见效不一致；结构性策略（全面验证+单测生成、标准化通信协议、概率置信度、记忆/状态管理、RL 微调）才是根本，但属开放研究问题。
- **Case Study 1：AG2-MathChat（Appendix H.1）**：GSM-Plus 随机 200 题、6 次重复。GPT-4 下改进 prompt（加验证段）显著有效，新拓扑（Problem Solver/Coder/Verifier 三角色、仅 Verifier 可终止）无统计显著增益（Wilcoxon p=0.4）；GPT-4o 下两者均显著（p=0.03）——效果依赖底层 LLM。
- **Case Study 2：ChatDev（Appendix H.2）**：角色规范修补（仅上级 agent 可终结会话、Verifier 关注边界用例）与拓扑改造（DAG→循环图、CTO 确认所有 review 满足后才终止）均提升 ProgramDev-v0（32 任务）与 HumanEval 成绩，但提升有限、完成率仍低。
- **核心结论（§5.3）**：同模型下干预最高 +15.6%，说明 MAS 失败可通过更好系统设计解决；但高可靠性需组合式变革（组织结构 + 模型级改进），借鉴高可靠性组织理论。

### 2.6 工具与成本（Appendix C; Appendix D; Appendix K）

- 封装为 Python 库 `pip install agentdash`，传入轨迹即返回失败模式标注（Appendix C）；LLM 标注器管线开源。
- ProgramDev（30 题）与 ProgramDev-v2（100 题）数据集开放（Appendix D）。
- LLM 标注器平均成本 $1.8/条，随轨迹长度变化：AppWorld $0.3740 至 OpenManus $4.1409（Appendix K, Table 9）。

### 2.7 结论与局限（§6; §4; Appendix B.3）

结论：MAST-Data + MAST + LLM 标注器构成 MAS 失败研究的实证基础与标准化语言，指向具体研究方向（§6）。局限：作者明言 MAST 不声称穷尽所有失败模式（§3; §4）；幻觉、指令遵循等基础模型限制被有意排除在分类重点之外（§4）；闭源系统（Manus）因无完整轨迹无法纳入细粒度分析（Appendix B.3）；LLM 标注器对症状相似的不同根因模式（最大相关 0.63）可能混淆（Appendix E）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 三大失败类别占比（1642 条轨迹） | FC1 系统设计 44.2%、FC2 智能体间失调 32.3%、FC3 任务验证 23.5% | §4; Figure 1 |
| 最常见单一失败模式 | FM-1.3 Step Repetition 15.7%、FM-2.6 Reasoning-Action Mismatch 13.2%、FM-1.5 Unaware of Termination 12.4%、FM-1.1 Disobey Task Spec 11.8% | §4; Figure 1 |
| 专家标注一致性 | 3 轮 IAA 后 Cohen's Kappa κ=0.88（3 名专家） | §3.2 |
| LLM 标注器 vs 人类 | accuracy 94%、κ=0.77（o1 few-shot） | §3.3; Table 2 |
| 未见过系统泛化 | OpenManus/Magentic-One + MMLU/GAIA 上人类 IAA κ=0.79 | §3.4 |
| 数据规模 | MAST-Data 1642 条标注轨迹 / GT 分析 150 条、平均 >15,000 行/条 / MAST-Data-human 21 条 | §1; §3.1; §3.4 |
| 210 条子集类别分布 | FC1 41.8%、FC2 36.9%、FC3 21.3%（每系统前 30 条） | §5; Figure 4 |
| 模型对比（vs Claude 3.7） | MetaGPT 内 GPT-4o 的 FC1 失败少 39%，FC3 两者皆高 | §5.1; Appendix F |
| 架构对比（vs ChatDev） | MetaGPT FC1/FC2 失败少 60–68%，但 FC3 多 1.56 倍（同为 GPT-4o、ProgramDev-v2） | §5.1; Appendix F |
| 干预：角色规范修补 | ChatDev 任务成功率 +9.4%（同一 user prompt 与 GPT-4o） | §4 FC1; Appendix H |
| 干预：拓扑改造 | ChatDev ProgramDev-v0 25.0%→40.6%（+15.6pp）、HumanEval 89.6%→91.5% | §4 FC3; Appendix H Table 5 |
| 干预：AG2-MathChat | GPT-4o 下 GSM-Plus 84.25±1.86%→89.00±1.38%（improved prompt）/88.83±1.51%（new topology），Wilcoxon p=0.03 | Appendix H.1 Table 5 |
| LLM 标注成本 | 平均 $1.8/条轨迹（AppWorld $0.3740–OpenManus $4.1409） | Appendix K Table 9 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2503.13657（v3，NeurIPS 2025 Datasets and Benchmarks Track） |
| 代码 / 标注器 | https://github.com/multi-agent-systems-failure-taxonomy/MAST（含 LLM annotator 管线） |
| 数据集 | https://huggingface.co/datasets/mcemri/MAST-Data（MAST-Data 1642 条 + MAST-Data-human） |
| Python 库 | `pip install agentdash`（MAST 标注即用库） |
| 基准 | ProgramDev（30 题）/ ProgramDev-v2（100 题），仓库 traces 目录下 |
| 被分析的 MAS | MetaGPT / ChatDev / HyperAgent / AppWorld / AG2(MathChat) / Magentic-One / OpenManus（Table 1） |
| 关联 | 本目录 12（MetaGPT——MAST 的被分析框架之一）、17/18（SAS vs MAS 实证对照） |

## 5. 一句话索引（给 Agent 用）

> 诊断多 agent 系统失败或决定"要不要上 MAS"时读这篇：MAST 用 Grounded Theory + 6 名专家（κ=0.88）从 150 条轨迹归纳出 14 种失败模式 3 大类，再用 o1 LLM-as-a-Judge（accuracy 94%、κ=0.77）标注 7 框架共 1642 条轨迹——系统设计问题 44.2%、智能体间失调 32.3%、任务验证不足 23.5%，最常见为步骤重复 15.7% 与推理-行动错配 13.2%；干预实验（ChatDev 改角色规范 +9.4%、改拓扑 +15.6pp）证明失败主因是组织设计而非模型能力，但战术性修补后完成率仍低，需结构级重设计（多级验证、标准化协议）。
