---
title: "A Comprehensive Empirical Evaluation of Agent Frameworks on Code-centric Software Engineering Tasks"
source_pdf: "18-Gao-Agent_Frameworks_Code_SE_Eval_v1.pdf"
arxiv_id: "2511.00872"
arxiv_version: "v1"
authors:
  - "Zhuowen Yin"
  - "Cuifeng Gao"
  - "Chunsong Fan"
  - "Wenzhang Yang"
  - "Yinxing Xue"
  - "Lijun Zhang"
year: 2025
venue: "arXiv"
type: "评测对照 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：7 个 Agent 框架在代码中心 SE 任务上的系统实证

## 1. 适用场景

- 在**软件开发 / 漏洞检测 / 程序修复**三类代码任务上选型通用 agent 框架（AgentOrchestra、OWL、SE-Agent、Trae、GPTswarm、OpenHands、SWE-Agent），需要效果/效率/成本三维实测对比数据时读这篇。
- 要用实证依据决策"**多 agent 编排 vs 单 agent + 专用工具**"（含机制解释：交互开销、上下文溢出、幻觉传播）时，读 §5.1。
- 要复用或评估**代码类 agent 基准与统一评测协议**（SRDD 1,200 / LLM-SmartAudit 115 / SWE-bench Lite 300，统一 DeepSeek-v3.1 后端、100 步上限）时，读 §3.3–§3.4。
- 要分析 agent 的 **token 成本结构**（多 agent 集中在 planning、单 agent 集中在 execution/editing）与输入缓存对账单的影响时，读 §4.3。

> 锚点：§3.1 Research Questions; §3.3 Benchmark Suite; §3.4 Evaluation Framework; §4 Results and Analysis; §5.1 More steps, better effectiveness?

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 INTRODUCTION; §2 Background; §3.1 Research Questions）

既有实证两大局限：只盯单一任务（多为 APR）、只看孤立维度（如 traceability 或效果），缺乏全景。本文首次对 7 个通用框架 × 3 类代码中心任务做三维系统实证。§2.1 采用 Google Agent White Paper 的 agent 定义（Model + Tools + Orchestration），并区分单/多 agent 范式；§2.2 界定三个代码中心任务；§3.1 抽象出通用 agentic workflow 范式（三层：Orchestration and Reasoning、Collaborative Role、Tool Augmentation），据此提出 RQ1 效果（能否完成任务）、RQ2 效率（推理循环与工具使用过程）、RQ3 开销（token 成本及其阶段分布）。

### 2.2 实验设计（§3.2 Studied Agent Frameworks; §3.3 Benchmark Suite; §3.4 Evaluation Framework）

- **框架选择（§3.2）**：两条纳入标准——C1 能同时做三类任务（排除任务专用系统）、C2 公开可得；共 7 个：AgentOrchestra（分层多 agent，TEA 协议）、OWL（Planner/Coordinator/Worker 层级多 agent）、SE-Agent（自进化轨迹优化：初始轨迹池 + 反思修订 + 跨轨迹融合 + 多维选择，单 agent 执行 + summary agent）、Trae（ByteDance，Code Agent 迭代生成候选补丁 + 两阶段剪枝 + Selector 排序 + 投票）、GPTswarm（agent 为可优化计算图）、OpenHands（事件流交互 + CodeAct + 多 agent 委托）、SWE-Agent（Princeton，agent–computer interface ACI）。
- **基准（§3.3）**：软件开发用 SRDD（1,200 条自然语言需求，Education 210 / Work 240 / Life 330 / Game 270 / Creation 150）；漏洞检测用 LLM-SmartAudit（115 个智能合约 = common-vulnerability 102 + CVE 13，覆盖 10 类常见漏洞 + 5 类 CVE 漏洞）；程序修复用 SWE-bench Lite（300 实例、12 个 Python 仓库）。
- **指标与设置（§3.4）**：Quality = Completeness × Executability × Consistency（ChatDev 官方脚本 + OpenAI text-embedding-ada-002）；Accuracy = TPs/(TPs+FPs)；Repair_Rate 走官方 Docker 评估协议；效率用平均轨迹步数、修正次数、修正率；开销记美元与 token。统一设置：步数上限 100；后端全用 DeepSeek-v3.1（输入 $0.56/M、输出 $1.69/M、缓存 $0.07/M token）；各框架默认工具集与默认 agent 数（AgentOrchestra 软件开发用 4 个 agent，BrowserUse agent 在检测/修复任务剔除）；提示分别沿用 ChatDev、LLM-SmartAudit、SWE-Agent 已验证配置；SE-Agent 按官方示例跑 3 次迭代（summary operator 为 null / alternative_strategy / traj_pool_summary）。

### 2.3 效果 RQ1（§4.1 Effectiveness of Agent Frameworks (RQ1)）

- **软件开发**：无全能框架，三指标各有王者——完整性 AgentOrchestra 0.86 最高（全体均值 0.69，Trae 最低 0.53）；可执行性 OpenHands 在 Game/Education/Life/Creation 四类满分 1.00（全体均值 0.79）；一致性 GPTswarm 0.85 最高（均值 0.79）。综合质量分 OpenHands 0.47 最佳（全体均值 0.36）。
- **漏洞检测**：七框架表现接近——GPTswarm 77% 最高、AgentOrchestra 44% 最低、SE-Agent (Iter-2) 约 70% 居中，七框架平均约 66%，无一突破 90%；GL 类型全体基本检不出，PR、UD 类型接近 100%。
- **程序修复**：SE-Agent (Iter-3) 54%（161/300）最高，7 个框架中仅 4 个修复约半数问题；AgentOrchestra 3%、GPTswarm 5%、OWL 10% 显著更差——原因是它们未使用 Patch 工具、无法生成正确 diff 格式补丁。django（114 例）上 Trae 与 SE-Agent (Iter-3) 各修 68 例最佳；flask（3 例）所有框架 0 例（实例数与难度未必相关）。

### 2.4 效率 RQ2（§4.2 Efficiency of Agent Frameworks (RQ2)）

- **轨迹步数**：软件开发平均 28.31 步（OpenHands 81.28 最长）；漏洞检测平均 10.40 步（AgentOrchestra 46.5 最长）；程序修复平均 57.44 步（Trae 78.1 最长，构成为 41.1 条 Bash 命令 + 30 次文件编辑 + 6 步问题分析 + 1 步收尾；GPTswarm 因 CodeReact 固定恰好 3 个 React 循环仅 2.90 步最短）。论文在引言与结论均指出 SE-Agent (Iter-3) 在全部实验中累计步数最长。
- **修正行为**：AgentOrchestra 在软件开发与漏洞检测修正最多（16.7 次 / 41.54%；21.04 次 / 45.25%），OpenHands 在程序修复最多（25.20 次 / 36.36%）；GPTswarm 与 OWL 修正极少并非高效，而是自监控缺失（无 Git 版本控制、无 unidiff 校验等工具）——修正次数缺失可能意味着错误检测机制缺失。
- **总论**：效率更多取决于推理深度、协调策略与反馈整合，而非 agent 数量；OpenHands 修正多但行为稳定收敛，体现较强反思能力。

### 2.5 开销 RQ3（§4.3 Overhead of Agent Frameworks (RQ3)）

- **货币成本（Table 10）**：三任务总花费 $875.05；软件开发最贵 $544.90 > 程序修复 $287.75 > 漏洞检测最省 $42.40。框架维度：AgentOrchestra $370.19 最贵（软件开发单项 $292.01；程序修复单迭代 $64.05，SE-Agent 三迭代累计 $106.91）；GPTswarm 全部任务仅 $16.29 最省；漏洞检测最低单耗为 SE-Agent (Iter-1) $0.29。
- **token 消耗（Table 11）**：OpenHands 三个任务 token 均最多（软件开发输入 1.26B + 输出 30.54M）但因输入缓存定价（$0.07/M）成本并非最高；GPTswarm 是唯一输出 token 多于输入 token 的框架，其余框架输入均大于输出。
- **阶段分解（Fig. 2–4）**：多 agent 系统 token 集中在 planning——AgentOrchestra 的 Planning agent 占 65.8%–67.2%，OWL 的 User agent 占 80.7%–94.2%；单 agent 系统集中在 execution 与 editing——程序修复执行占 45.3%–56.2%，漏洞检测编辑占 72.8%–80.4%，软件开发 GPTswarm 因 IO-agent 架构 100% 为编辑。

### 2.6 讨论：更多步数≠更好效果（§5.1 More steps, better effectiveness?）

按 RQ2 分组对比多 agent 系统（AgentOrchestra、OWL）与单 agent 系统（SE-Agent worker、Trae、GPTswarm、OpenHands、SWE-Agent）：① 软件开发——多 agent 完整性在全部五类占优，但单 agent 可执行性显著更好、一致性略优，综合最佳为 OpenHands（单 agent）0.47，单 agent 略占优；② 漏洞检测——15 类漏洞中 9 类双方持平，单 agent 在 6 类（Access Control、Logic Error、GL、IO、TM、USE）胜出，且不存在多 agent 独有检出的类型；③ 程序修复——单 agent 在全部 12 个仓库优于多 agent。机制解释：多 agent 中规划 agent 与下游专职 agent 交互开销大→信息过载→overthinking 与错误决策；输入 token 超出 LLM 最大上下文导致信息丢失，加之内生幻觉在 agent 间传播；单 agent 上下文小、历史可全量访问，对 FP 与幻觉更可控。理论上规划的泛化优势实证上未兑现，且多 agent 会传播相同错误（其他 agent 察觉不了彼此输出中的错误）。两个成功反例：SE-Agent"垂直迭代"（单 agent 执行 + 轨迹总结，修复率 47.33%→53.00%→53.67%）与 GPTswarm"横向分组总结"（每组结束总结经验教训，助其拿下漏洞检测最高准确率）——轨迹总结是无训练增强手段。核心可操作结论：**加专用工具优于加专职 agent**。

### 2.7 威胁效度、相关工作与结论（§5.2 Threats to Validity; §6 Related Work; §7 Conclusion）

- **威胁（§5.2）**：内部——只评通用框架（专用 agent 单任务可能更强）、无覆盖全生命周期的统一基准、单一后端 LLM（DeepSeek-V3.1，控制成本所致，未来应换基座）；外部——发布代码与论文设计有出入（如 Trae 部分辅助组件未在官方示例实现），已固定随机种子并如实报告实际 agent/角色配置。
- **相关工作（§6）**：任务专用框架（ExpeRepair、SemAgent）vs 通用框架；基准谱系（HumanEval/MBPP、SRDD vs ProjectDev 等、SySeVR/CWE-BenchJava、Defects4J/QuixBugs、SWE-bench 家族）；实证类工作（Gao et al. [15]：15 个 SE 任务上 MAS 复杂任务更优、SAS 简单任务更高效，提出级联混合范式；Ceka et al. 执行轨迹；Meng et al. 修 bug 细粒度实证）。
- **结论（§7）**：agent 效果总体中等——OpenHands 软件开发质量平衡最佳、GPTswarm 漏洞检测最准、程序修复仍难（仅部分框架修约半数问题）；多 agent 框架成本集中于规划阶段、单 agent 集中于执行/编辑。

> 锚点：§3.2; §3.3; §3.4; §4.1; §4.2; §4.3; §5.1; §5.2; §6; §7

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 软件开发综合质量（SRDD 1,200 实例） | OpenHands 最高 0.47，vs 全体框架平均 0.36 | §4.1 Table 4 |
| 软件开发单项指标 vs 均值 | 完整性 AgentOrchestra 0.86 vs 均值 0.69（Trae 最低 0.53）；可执行性 OpenHands 四类 1.00 vs 均值 0.79；一致性 GPTswarm 0.85 vs 均值 0.79 | §4.1 Table 4 |
| 漏洞检测准确率（LLM-SmartAudit 115 合约） | GPTswarm 77% 最高 vs AgentOrchestra 44% 最低（中位约 70%，SE-Agent Iter-2）；七框架平均约 66%，无一超 90% | §4.1 |
| 程序修复率（SWE-bench Lite 300 实例） | SE-Agent (Iter-3) 54%（161/300）最高；仅 4/7 框架修复约半数；AgentOrchestra 3%、GPTswarm 5%、OWL 10% | §4.1 Table 6 |
| 单仓库对比 | django（114 例）Trae 与 SE-Agent (Iter-3) 各修 68 例最佳；flask（3 例）所有框架均 0 例 | §4.1 Table 6 |
| 平均轨迹步数 | 软件开发 28.31 步（OpenHands 81.28 最长）；漏洞检测 10.40 步（AgentOrchestra 46.5 最长）；程序修复 57.44 步（Trae 78.1 最长、GPTswarm 2.90 最短） | §4.2 Tables 7–9 |
| 修正行为极值 | AgentOrchestra 修正率 41.54%（软件开发）、45.25%（漏洞检测）均为最高；程序修复 OpenHands 25.20 次 / 36.36% 最高 | §4.2 |
| 三任务货币开销 | 总计 $875.05：软件开发 $544.90 > 程序修复 $287.75 > 漏洞检测 $42.40；框架级 AgentOrchestra $370.19 最贵 vs GPTswarm $16.29 最省 | §4.3 Table 10 |
| token 消耗特征 | OpenHands 软件开发输入 1.26B 全场最高（靠缓存压成本）；GPTswarm 唯一输出>输入的框架 | §4.3 Table 11 |
| SE-Agent 垂直迭代收益（程序修复） | 修复率 47.33% → 53.00% → 53.67%（两轮 summary 迭代后） | §5.1 |
| 多 agent vs 单 agent | 程序修复单 agent 在全部 12 个仓库胜出；漏洞检测 15 类中单 agent 6 类胜、9 类平、0 类为多 agent 独有；软件开发综合最佳 OpenHands（单 agent）0.47 | §5.1 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2511.00872 |
| 实验结果仓库 | https://github.com/YCHYZW/Agents-for-Software-Engineering （论文脚注 1，全部实验结果公开） |
| 基准：SRDD | https://github.com/OpenBMB/ChatDev/tree/main/SRDD （1,200 条软件开发需求） |
| 基准：LLM-SmartAudit | https://github.com/LLMAudit/LLMSmartAuditTool （115 个智能合约漏洞） |
| 基准：SWE-bench Lite | https://www.swebench.com/lite.html （300 个真实 GitHub issue） |
| 被测框架 | AgentOrchestra、OWL、SE-Agent、Trae、GPTswarm、OpenHands、SWE-Agent（各仓库地址见论文 Table 1） |
| 关联 | 本目录 17（Gao et al. "Single-agent or Multi-agent Systems? Why Not Both?"，即本文 [15]，级联范式互为印证）、16（best-of-N 基线） |

## 5. 一句话索引（给 Agent 用）

> 为代码类 SE 任务选 agent 框架时读这篇：7 个通用框架 × 3 任务（SRDD 1,200 / LLM-SmartAudit 115 / SWE-bench Lite 300，统一 DeepSeek-v3.1 后端）三维实证：效果仅中等——软件开发质量 OpenHands 0.47 最佳、漏洞检测 GPTswarm 77% 最高、程序修复最高 54%（SE-Agent Iter-3）且仅 4/7 框架修约半数；单 agent 系统三类任务整体优于多 agent（交互开销、上下文溢出、幻觉传播），加专用工具优于加 agent；软件开发最贵（$544.90），AgentOrchestra $370.19 最贵、GPTswarm $16.29 最省，多 agent 成本集中在 planning、单 agent 集中在 execution/editing。
