---
title: "An LLM Compiler for Parallel Function Calling"
source_pdf: "09-Kim-LLMCompiler_v3.pdf"
arxiv_id: "2312.04511"
arxiv_version: "v3"
authors:
  - "Sehoon Kim"
  - "Suhong Moon"
  - "Ryan Tabrizi"
  - "Nicholas Lee"
  - "Michael W. Mahoney"
  - "Kurt Keutzer"
year: 2023
venue: "ICML 2024"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：LLMCompiler——函数调用的任务 DAG 并行执行

## 1. 适用场景

- 多工具调用任务要**降低延迟与成本**（把串行 ReAct 循环改为并行派发）、且不想绑定 OpenAI 专有并行函数调用时，读这篇。
- 要设计"**模型生成计划（DAG）/ 代码调度执行**"的 agent 架构，尤其是带**动态重规划**（依赖图随中间结果重建，如迭代式 ToT 搜索）的执行器时读这篇。
- 需要量化或规避 ReAct 串行循环的两类失败模式（重复调用同一函数、基于不完整中间结果提前停止）时读这篇（Appendix A 给了分布级证据）。
- 要评测并行函数调用框架、需要带依赖模式的基准（论文自建的 ParallelQA：search→math 依赖、2–5 路可并行）时读这篇。
- 为开源模型（LLaMA-2 等）补上并行函数调用能力、或做 agent 延迟性能工程（Planner 开销、straggler 效应、流式流水线）时读这篇。

> 锚点：Abstract; §1 Introduction; §3 Methodology; §4 LLMCompiler Details; §5 Results。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- LLM 的函数/工具调用主流范式是 ReAct 式"调用→观察→再推理"串行循环：延迟高（每步都要 LLM 往返）、成本高（重复调用 LLM）、且把中间观察拼回 prompt 会干扰执行流，诱发两类失败——重复调用同一函数、基于不完整中间结果提前停止（§1）。
- 核心思想：借鉴**经典编译器**自动识别可并行指令并管理依赖的做法，为 LLM 函数调用构建一个"编译器"，自动编排并行调用；这是首个同时改善延迟、成本与准确率的函数调用编排框架（§1）。

### 2.2 相关工作定位（§2 Related Work; §2.1–2.3; Appendix C.1, F）

- vs Skeleton-of-Thought：后者只支持无依赖的 embarrassingly parallel 负载；LLMCompiler 生成带相互依赖的任务 DAG，覆盖编码/数学等复杂场景（§2.1）。
- vs OpenAI 并行函数调用（1106 版）：仅限其专有模型；LLMCompiler 开源模型可用，且延迟/成本更优（最高再快 35%、省 2.57×）（§2.1; §5.1; §5.2）。
- vs Decomposed Prompting / Step-Back / Plan-and-Solve 等提示法：它们只为提准；LLMCompiler 用 Planner 识别可并行模式，目标是降延迟同时保准确（§2.2）。
- vs ReWOO：ReWOO 用 planner 解耦推理与执行以省 token，但无并行调用、无动态重规划；LLMCompiler 两者都支持（§2.2）。
- vs TPTU / ViperGPT / HuggingGPT 端到端 plan-and-solve：分别缺并行、缺重规划或限特定域；LLMCompiler 是 planning + replanning + 并行 + 全域的组合（§2.2; Table E.3; Appendix F）。

### 2.3 三组件架构（§3 Methodology）

- **Function Calling Planner**（§3.1）：用 LLM 把自然语言请求分解为任务及其依赖，输出形如 `$1 = search(Microsoft Market Cap); $2 = search(Apple Market Cap); $3 = math($1 / $2); $4 = llm($3)` 的 DAG；后续任务的输入用占位变量 `$id` 引用前序输出；由预定义 prompt 约束语法（每任务一行、ID 严格递增、最大化并行度、内置 `finish()`/join 动作）（§3.1; Appendix H）。
- **Task Fetching Unit**（§3.2）：灵感来自现代处理器的指令取指单元；按贪心策略一旦任务依赖就绪立即派发给 Executor，并把占位变量替换为真实前序输出——用简单的取指+队列机制实现，**不需要额外 LLM**（§3.2）。
- **Executor**（§3.3）：异步并发执行被派发任务（Fetching Unit 保证派发的任务相互独立）；每个任务有独立 memory 存中间结果；工具可以是计算器/搜索/API，也可以是针对特定任务的 LLM agent（§3.3）。
- **Dynamic Replanning**（§3.4）：类比程序运行时分支——复杂场景下 Executor 把中间结果回传 Planner，重新生成新一轮任务 DAG，循环直至产出最终答案；这是静态 DAG 无法覆盖的动态执行模式（§3.4）。

### 2.4 使用接口与流式优化（§4 LLMCompiler Details）

- 用户只需提供两样东西（§4.1）：① 工具定义（描述+参数规格，与 ReAct/OpenAI function calling 同级要求）；② 可选的 Planner in-context 示例（演示任务分解与依赖格式；各基准所用示例见 Appendix G，只需几行）。
- **Streamed Planner**（§4.2）：类比指令流水线，Planner 异步流式产出依赖图，任务依赖一满足即被执行，隐藏 Planner 延迟；对工具耗时长的负载收益最大（ParallelQA 提速 1.30×，HotpotQA/Movie Rec 仅 1.01×/1.03×）（§4.2; Table C.1）。

### 2.5 实验设置（§5 Results 开头; Appendix D, I）

- 模型与部署：闭源 gpt-3.5-turbo（1106，HotpotQA/Movie Rec）、gpt-4-turbo（1106，ParallelQA）、gpt-4（0613，Game of 24）；开源 LLaMA-2 70B（2×A100-80GB，vLLM）。温度 0（Game of 24 的 thought proposer/state evaluator 0.7）；OpenAI 随机性下跑 3 次取均值；HotpotQA/Movie Rec/ParallelQA 分别 3/1/5-shot（Appendix D）。
- 基线：ReAct（含加防循环/防早停提示的 ReAct†）、OpenAI 并行函数调用、ToT（Game of 24）、LATS/LASER（WebShop，取自原论文）；另与 TPTU-SA/OA 对比（Appendix F.1）。延迟以 ReAct† 为基准（原版 ReAct 的循环/早停使延迟不可测）（§5.1; Table 1）。
- **ParallelQA 基准构造**（§5.2; Appendix I）：受 IfQA 启发，113 例"实体事实属性的数学问题"，需 search+math 两工具且 math 参数依赖 search 输出；选 56 个 Wikipedia 首段可答的实体以排除检索失败；最大可并行任务数 2–5、join 次数 2–3；GPT-4 生成、人工标注。
- 指标：准确率/成功率、端到端延迟、输入/输出 token 数与按 GPT 定价折算的成本（§5.1; Table 1–3）。

### 2.6 主要结果（§5.1–§5.4）

- **Embarrassingly parallel**（§5.1）：HotpotQA 比较集（1.5k 题、2 路）GPT 下 LLMCompiler 62.00%、3.95s（1.80× vs ReAct† 7.12s；OAI 并行 1.61×）；Movie Recommendation（500 例、8 路）GPT 下 77.13%、5.47s（**3.74×**，比 OAI 并行再快 ~35%），LLaMA-2 下 77.80%（vs ReAct 70.00%）、2.82×。成本：HotpotQA 省 3.37×、Movie Rec 省 **6.73×**（vs ReAct），且比 OAI 并行更省（提示只含计划不含观察）（Table 1; Table 2）。
- **带依赖的并行**（§5.2）：ParallelQA 上 gpt-4-turbo 2.15×（16.69s vs 35.90s，89.38% vs ReAct 89.09%）；LLaMA-2 70B 2.27× 且准确率 68.14% vs 59.59%（**+8.55 分≈9%**，对应 ReAct 约 20% 样本重复调用）；成本省 4.65×（vs ReAct）/2.57×（vs OAI 并行）（Table 1; Table 2; §5.2）。
- **动态重规划**（§5.3）：Game of 24（100 局）+ ToT 式"thought proposer / state evaluator / top k select"三工具，单轮内并行、轮间 replan：gpt-4 下 75.33% 成功率（vs ToT 74.00%）、83.6s（**2.89×**）；LLaMA-2 下 32.00%（vs 30.00%）、456.02s（2.09×，正文记 2.01×）（Table 1; §5.3）。
- **交互式决策**（§5.4）：WebShop（500 条指令）用 search+explore 两工具并行探索全部 ~10 个候选商品：gpt-3.5-turbo 成功率 48.2%（N=500）vs ReAct 19.8%（+28.4）、LATS 38.0（+6）；gpt-4 下 55.6% vs ReAct 35.2（+20.4）、LASER 50.0（+5.6）；延迟 **101.7×** vs LATS（10.48s vs 1066s）、2.69× vs LASER；比 ReAct 略慢（Planner 开销）但成功率收益远大（Table 3; §5.4; Abstract）。

### 2.7 机理分析与失败案例（Appendix A, B, E）

- **ReAct 失败解剖**（Appendix A）：Movie Rec（GPT）约 85% 样本提前停止（未搜满 8 部电影就作答），LLMCompiler 99% 完成全量搜索；加防早停提示（ReAct†）68.60→72.47 仍不彻底。HotpotQA（LLaMA-2）约 10% 样本函数调用 >4 次陷入循环，这些样本 ReAct 准确率 <10%、LLMCompiler 约 50%（Fig A.1–A.4）。少数（<3%）ReAct 三调用样本靠换实体名重试反超 LLMCompiler——串行自适应的残余优势。
- **LLMCompiler 失败归因**（Appendix B，ParallelQA 10.6% 失败=36 例）：Planner 仅占 8%（配好工具定义+示例后全程仅 3 例）、Executor 占 64%（math 工具选错属性/单位换算错）、最终输出过程占 28%（从观察归纳结论出错）；后两类 ReAct 同样存在，LLMCompiler 因只给每个工具相关上下文而略少。
- **延迟建模**（Appendix E.1–E.2）：ReAct 延迟=Σ(规划+执行)；LLMCompiler=Σ规划+最长执行（流式更优），理论上限加速≈任务数 N、下限≈1；实测 Movie Rec 中 Planner（1.88s）+最终作答（1.62s）占整体延迟一半以上，最慢搜索（1.13s）约为平均任务（0.61s）2 倍（straggler）；结论是要拿高加速须压 Planner 开销与 straggler。ParallelQA 弱扩展实验显示 ReAct 延迟随可并行任务数线性增长、LLMCompiler 增长平缓（Fig E.5）。
- **顺序型负载也适用**（Appendix E.3）：HotpotQA bridge 集（本质串行）LLMCompiler 26.3% / 4.70s vs ReAct 22.7% / 7.07s——靠 replanning 覆盖纯串行工作流。

### 2.8 结论与未来工作（§6 Conclusions）

- LLMCompiler 用 Planner + Task Fetching Unit + Executor 把串行动态推理改为并行编排，跨开源/闭源模型取得最高 **3.7× 延迟、6.7× 成本、~9% 准确率**提升，且优于 OpenAI 并行函数调用（§6; Abstract）。
- 未来方向：在此基础上提升 LLM 执行复杂大规模任务的能力与效率，推动 LLM 应用开发范式（§6）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| HotpotQA 比较（GPT，1.5k 题） | 62.00%、3.95s、1.80× vs ReAct†（7.12s）；OAI 并行 62.05%、1.61× | Table 1; §5.1 |
| Movie Recommendation（GPT，8 路） | 77.13%、5.47s、**3.74×** vs ReAct†；比 OAI 并行（2.76×）再快最高 35%；LLaMA-2 77.80% vs ReAct 70.00% | Table 1; §5.1 |
| ParallelQA（带依赖） | gpt-4-turbo 2.15×（16.69s vs 35.90s）；LLaMA-2 2.27×、准确率 68.14% vs 59.59%（+8.55≈9%） | Table 1; §5.2; Abstract |
| 成本节省（GPT 定价） | vs ReAct：HotpotQA 3.37×、Movie Rec **6.73×**、ParallelQA 4.65×；vs OAI 并行：ParallelQA 2.57×（Abstract 总口径最高 6.7×） | Table 2; §5.1; §5.2; Abstract |
| Game of 24（重规划，100 局） | gpt-4：75.33% vs ToT 74.00%、83.6s vs 241.2s（**2.89×**）；LLaMA-2：32.00% vs 30.00%、456.02s vs 952.06s（2.09×） | Table 1; §5.3 |
| WebShop（500 指令） | 成功率 48.2%（gpt-3.5，vs ReAct 19.8 即 +28.4）/55.6%（gpt-4，vs ReAct 35.2 即 +20.4）；延迟 **101.7×** vs LATS、2.69× vs LASER | Table 3; §5.4 |
| ReAct 失败模式量化 | Movie Rec 约 85% 样本提前停止；HotpotQA(LLaMA-2) 约 10% 样本 >4 次调用循环，该子集准确率 <10%（LLMCompiler 约 50%） | Appendix A; Fig A.1–A.4 |
| LLMCompiler 失败归因 | ParallelQA 失败 10.6%：Planner 8% / Executor 64% / 最终输出 28% | Appendix B |
| 流式 Planner 消融 | ParallelQA 21.72s→16.69s（1.30×）；HotpotQA 1.01×、Movie Rec 1.03× | Table C.1; §4.2 |
| 顺序型负载（HotpotQA bridge） | 26.3%、4.70s vs ReAct 22.7%、7.07s（+4 点准确率） | Table E.2; Appendix E.3 |
| vs TPTU（HotpotQA 比较，GPT） | 62.00% vs TPTU-SA 34.16% / TPTU-SA† 44.59% / TPTU-OA 57.50%；延迟 1.51× vs TPTU-SA† | Table F.4; Appendix F.1 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2312.04511 |
| 代码 | https://github.com/SqueezeAILab/LLMCompiler （SqueezeAILab 开源实现） |
| 自建基准 | ParallelQA（113 例，search+math 依赖模式；构造细节见 Appendix I） |
| 评测基准 | HotpotQA（arXiv:1809.09600）、Movie Recommendation（BIG-Bench, Srivastava et al. 2022）、Game of 24 / ToT（arXiv:2305.10601 同作者体系）、WebShop（arXiv:2207.01206）、IfQA（arXiv:2309.03495） |
| 基线系统 | ReAct（arXiv:2210.03629）、ReWOO（arXiv:2305.18323）、OpenAI 并行函数调用（1106）、LATS、LASER、TPTU、ViperGPT、HuggingGPT |
| 基础设施 | LLaMA-2 70B + vLLM（2×A100-80GB）、LangChain LLMMathChain 式 math 工具 |
| 本库关联 | 本目录 05（ReAct 基线）、07（ToT 的动态重规划案例） |

## 5. 一句话索引（给 Agent 用）

> 多工具调用要提速降本 / 设计 DAG 计划执行器时读这篇：LLMCompiler（ICML 2024）借经典编译器思想，用 **Function Calling Planner（生成 `$1 = search(...)` 式任务 DAG）+ Task Fetching Unit（依赖就绪即派发、免 LLM）+ Executor（并发执行）+ 动态重规划** 替代串行 ReAct；实测最高 **3.7× 加速、6.7× 成本节省（vs ReAct；vs OpenAI 并行调用再省 2.57×）、~9% 准确率提升（LLaMA-2 68.14% vs 59.59%）**，WebShop 101.7× 加速且成功率 48.2% vs ReAct 19.8%——"计划归模型、调度归代码"的工程范本。
