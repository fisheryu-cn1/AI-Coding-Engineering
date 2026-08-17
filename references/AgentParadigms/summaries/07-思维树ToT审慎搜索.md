---
title: "Tree of Thoughts: Deliberate Problem Solving with Large Language Models"
source_pdf: "07-Yao-Tree_of_Thoughts_v2.pdf"
arxiv_id: "2305.10601"
arxiv_version: "v2"
authors:
  - "Shunyu Yao"
  - "Dian Yu"
  - "Jeffrey Zhao"
  - "Izhak Shafran"
  - "Thomas L. Griffiths"
  - "Yuan Cao"
year: 2023
venue: "NeurIPS 2023"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：思维树 ToT——推理时树状审慎搜索

## 1. 适用场景

- 当你的任务 GPT-4 + CoT 已经做得很好（如常规数学/常识题）时**不需要**这篇；当任务是**组合搜索/规划型**（初始决策关键、需要前瞻或回溯、中间状态可被 LM 自评）且 CoT 失效时，读这篇——ToT 即插即用、无需额外训练。
- 当你要为 agent 设计"生成候选—评估—剪枝/回溯"的推理时搜索循环，并需要**思维分解粒度、生成方式、评估方式、搜索算法**四个正交设计维度及其适用条件（何时用采样 vs 提议、打分 vs 投票、BFS vs DFS）时。
- 当你需要引用"自左向右解码导致早期错误不可挽回"的实证（Game of 24 上约 60% CoT 样本第一步就错），或论证 IO/CoT/CoT-SC/self-refine 都是树搜索的特例时。
- 当你要估算树状搜索的**成本**并做性能—成本权衡（分支数 b、投票数、few-shot vs zero-shot、强弱模型混搭生成/评估）时，附录 B.3 给了每题 token 与美元成本实测。
- 当你研究 LM 自评启发式的瓶颈（生成 vs 评估哪个更卡）时，附录 B.2 的 GPT-4/GPT-3.5 交叉实验给出直接证据。

> 锚点：Abstract; §1 Introduction; §3 Tree of Thoughts: Deliberate Problem Solving with LM; §4 Experiments; §6 Discussion; Appendix B.3 Cost and efficiency。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction; §2 Background）

- LM 推理仍是 token 级、自左向右的"System 1"决策，在需要探索、策略性前瞻、或初始决策起关键作用的任务上会失败；人类认知的双过程理论提示需要补充"System 2"式审慎规划——(1) 维护并探索多种备选而非只选一个，(2) 评估现状并主动前瞻/回溯以做全局决策（§1）。
- 沿 Newell & Simon 的经典问题求解观（问题求解 = 组合问题空间上的树搜索），提出 ToT：把问题求解建模为对"思维树"的搜索，每个节点是一个连贯语言序列（thought）作为中间步骤；现有方法两个缺陷——局部不做分支探索、全局无规划/前瞻/回溯（§3 开头）。
- 形式化背景：IO prompting 直接映射输入输出；CoT 顺序采样思维链 z1…zn；CoT-SC 对 k 条链做多数投票（链内无局部探索，且多数投票只在输出空间有限时适用）（§2 Background）。

### 2.2 ToT 框架的四个组件（§3 Tree of Thoughts: Deliberate Problem Solving with LM）

- **思维分解**：thought 粒度按任务设计——几个词（填字）、一行等式（Game of 24）、整段写作计划（Creative Writing）；原则是"小到能多样采样、大到能评估前景"。
- **思维生成 G(pθ, s, k)**：两策略——(a) 从 CoT prompt **i.i.d. 采样** k 个候选（适合思维空间大的任务，如整段计划）；(b) 用"propose prompt"**顺序提议**（适合思维空间受限的任务，如同上下文内避免重复）。
- **状态评估 V(pθ, S)**：两策略——(a) 对每个状态**独立打分**（数值 1–10 或 sure/likely/impossible 分级，依据少量前瞻模拟 + 常识排除）；(b) 跨状态**投票**（适合难以直接打分的开放目标如段落连贯性，类似 step-wise self-consistency）。均可多次采样聚合以换稳健性；这是"用 LM 审慎推理做搜索启发式"，区别于程序化（DeepBlue）或学习式（AlphaGo）启发式。
- **搜索算法**：(a) **BFS**（Algorithm 1）每步保留 b 个最有希望的状态；(b) **DFS**（Algorithm 2）优先探索最有希望的状态、评估不过阈值即剪枝并回溯父节点；A*/MCTS 留作未来工作。
- 概念优势：**通用性**（IO/CoT/CoT-SC/self-refine 均为深度/宽度受限的 ToT 特例）、**模块化**（底模 LM、分解、生成、评估、搜索可独立替换）、**可适配**（按问题性质/模型能力/资源约束调整）、**便利**（无需额外训练）。

### 2.3 实验设置（§4 Experiments）

- 统一设定：Chat Completions 版 GPT-4，采样温度 0.7（2023-05-05 至 05-16 实验）；三个连 GPT-4 都会大量失败的新任务（§4 开头; Table 1）。
- **§4.1 Game of 24**：4nums.com 的 1362 局中取较难的 901–1000 号共 100 局；成功 = 合法等式得 24 且每个输入数恰用一次。基线：IO（5-shot）、CoT（含 3 步中间等式）、CoT-SC（k=100）、IO+Refine（k≤10，且用到了正确性 ground-truth 反馈）。ToT 设定：3 步思维分解、propose prompt 逐步提议、BFS b=5、每个候选采 3 次 "sure/maybe/impossible" 评估。
- **§4.2 Creative writing**：输入 4 个随机句（randomwordgenerator.com，100 组），输出以这 4 句分别结尾的 4 段连贯短文，无标准答案；评估用 GPT-4 zero-shot 1–10 打分（每输出采 5 次平均，平均标准差约 0.56）+ 作者盲测两两比较（顺序随机翻转）。基线：zero-shot IO、zero-shot CoT（先写计划）、IO+Refine（k≤5）。ToT 设定：深度 2（仅 1 个中间思维步）——先生成 k=5 个计划投票选优，再基于最优计划生成 k=5 个段落投票选优（b=1）。
- **§4.3 Mini crosswords**：GooBix 156 局 5×5 填字，取 20 局测试（索引 1,6,…,91,96）、5 局做 prompt 示例；三级指标：字母（25/局）、词（10/局）、整局。基线 IO/CoT 各 10 次采样取平均。ToT 设定：DFS——每步把已有词翻译成剩余线索的字母约束，propose prompt 采 5 次并聚合置信度得到有序候选队列；状态评估逐线索判"能否填入"，任一线线索 impossible 即剪枝回溯；后续思维不允许改动已填词（至多 10 步）；DFS 限 100 步，输出最深探索状态。

### 2.4 主要发现（§4.1–§4.3 各结果与消融）

- **Game of 24（Table 2）**：IO 7.3%、CoT 4.0%、CoT-SC 9.0%；ToT b=1 即 45%、b=5 达 **74%**；即便 oracle 的 IO/CoT best-of-100 也只有 33%/49%——多探索节点（b>1）优于多次独立采样。错误分析（Figure 3b）：约 **60% 的 CoT 样本在第一步（前三个词）就已注定失败**，凸显自左向右解码的缺陷。
- **Creative Writing（Figure 5）**：GPT-4 评分 IO 6.19 / CoT 6.93 / ToT **7.56**；人类盲测 100 对中偏好 ToT 41、偏好 CoT 21、38 对"同样连贯"。Refine 在此任务更有效：IO+Refine 提到 7.67、ToT+Refine 提到 7.91——refine 可视为第三种思维生成方式（由旧思维精化出新思维）。
- **Mini crosswords（Table 3）**：字母/词/局三指标 IO 38.7%/14%/0、CoT 40.6%/15.6%/1、ToT **78%/60%/4（20 局解出 4 局）**；oracle 输出（+best state）达 82.4%/67.5%/7 局，说明输出启发式还有提升空间；去掉剪枝（-prune）降至 65.4%/41.5%（虽能找到 4 局正确解但启发式只输出 1 局）；去掉回溯（-backtrack，贪心连续填 20 步）词级仅 20%——**剪枝启发式与回溯都关键**。另发现评估器会把含生僻/过时词（如 "agend"）的正确状态误判为 impossible。
- **规模分析（Figure 3a）**：以访问节点数对齐比较，ToT（b=1…5）曲线始终高于 IO/CoT best-of-k。

### 2.5 扩展、成本与适用边界（Appendix B; §6 Discussion）

- **新任务（B.1）**：几行代码实现 zero-shot ToT-BFS（采 5 策略投票→采 5 解投票），GSM8K 100 题子集 IO 51 / CoT 86 / ToT 90，StrategyQA 73 / 82 / 83——GPT-4+CoT 已很强的任务上提升有限（StrategyQA 瓶颈在外部知识而非推理）。
- **新模型（B.2）**：GPT-3.5 上 ToT>CoT>IO 仍成立：Game of 24 19%（vs GPT-4 74%）；Creative Writing 6.62（GPT-3.5+ToT 超过 GPT-4+IO 的 6.19、接近 GPT-4+CoT 的 6.93）。交叉实验：GPT-4 生成+GPT-3.5 评估 = 64%，GPT-3.5 生成+GPT-4 评估 = 31% → 该任务瓶颈在**思维生成**，且生成/评估可用不同模型混搭降成本。
- **成本（B.3）**：Game of 24 每题 ToT 5.5k 生成 token / $0.74（CoT best-of-100 为 6.7k / $0.47 但只有 49%）；Creative Writing ToT 约 5 倍于 IO/CoT 的 token 与费用（$0.32/题）；主实验约 $106（Game24+CW），填字 DFS 在 $100 内；总体比 CoT 多 5–100 倍生成 token。可调 b/投票数/shot 数/模型档位做权衡；BFS 可在找到解后早停。
- **局限与结论（§6 Discussion）**：ToT 对 GPT-4 已擅长的多数任务并非必要；仅探索了三个相对简单的挑战任务；搜索类方法资源开销大（靠模块化灵活性 + 开源模型降本）；未来方向包括与外部环境交互的搜索、以及用 ToT 式高层反事实决策数据微调 LM。结论：LM 的"System 1"可被基于树搜索的"System 2"有益增强，同时 LM 也补足了经典搜索难以形式化的任务（如创意写作）——古典 AI 与 LM 的交汇是兴奋方向。Broader Impact：树状语言推理可读、可解释，利于人类对齐。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| Game of 24 成功率 | IO 7.3% / CoT 4.0% / CoT-SC 9.0% → ToT(b=5) 74%（b=1 即 45%）；oracle best-of-100：IO 33%、CoT 49% | Abstract; §4.1; Table 2 |
| Game of 24 错误模式 | 约 60% CoT 样本在第一个思维步（前三个词）即失败 | §4.1; Figure 3 |
| Creative Writing GPT-4 评分 | IO 6.19 / CoT 6.93 / ToT 7.56；+Refine：IO 7.67、ToT 7.91 | §4.2; Figure 5 |
| Creative Writing 人类盲测 | 100 对中偏好 ToT 41 / 偏好 CoT 21 / 同样连贯 38 | §4.2; Figure 5 |
| Mini Crosswords（字母/词/局） | IO 38.7%/14%/0、CoT 40.6%/15.6%/1 → ToT 78%/60%/4 局（20 局解 4） | §4.3; Table 3 |
| 填字消融 | oracle 输出 7/20 局；-prune 词级 41.5%；-backtrack 词级仅 20% | §4.3; Table 3 |
| 新任务泛化（zero-shot ToT） | GSM8K：CoT 86 → ToT 90；StrategyQA：82 → 83 | Appendix B.1; Table 4 |
| 弱模型与混搭 | GPT-3.5+ToT：填字游戏 Game24 19%、CW 6.62；GPT-4 生成+GPT-3.5 评估 64% vs 反向 31% | Appendix B.2; Table 5–6 |
| 成本 | Game of 24 每题 5.5k token/$0.74（CoT 0.9k/$0.07 量级）；总体为 CoT 的 5–100 倍生成 token | Appendix B.3; Table 7–8 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2305.10601 |
| 代码仓库（含全部 prompt 与轨迹） | https://github.com/princeton-nlp/tree-of-thought-llm（prompts 在 src/tot/prompts，轨迹在 logs） |
| 数据来源 | 4nums.com（Game of 24）、randomwordgenerator.com（Creative Writing 句子）、GooBix（Mini Crosswords） |
| 关联 | 本目录 05（ReAct，同作者前作）、09（LLMCompiler 对 ToT 的并行化/重规划）；RAP（arXiv:2305.14992，并发工作，MCTS 变体） |

## 5. 一句话索引（给 Agent 用）

> ToT 把 LLM 推理从 token 级自左向右解码升级为"思维节点"树搜索：思维分解 + 候选生成（i.i.d. 采样/顺序提议）+ LM 自评（打分/投票）+ BFS/DFS 前瞻回溯，无需训练。GPT-4 上 Game of 24 成功率 4%（CoT）→ 74%（b=5），创意写作 GPT-4 评分 6.93→7.56 且人类盲评 41:21 偏好，5×5 填字词级 15.6%→60%（oracle 7/20 局）。代价：生成 token 为 CoT 的 5–100 倍（Game of 24 $0.74/题）；适用边界：组合搜索/规划、中间状态可自评的任务，GPT-4+CoT 已擅长的任务收益有限。
