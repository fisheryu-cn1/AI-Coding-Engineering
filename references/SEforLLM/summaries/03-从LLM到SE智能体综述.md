---
title: "From LLMs to LLM-based Agents for Software Engineering: A Survey of Current, Challenges and Future"
source_pdf: "03-Jin-LLM_Agents_for_SE_Survey_v2.pdf"
arxiv_id: "2408.02479"
arxiv_version: "v2"
authors:
  - "Haolin Jin"
  - "Linghan Huang"
  - "Haipeng Cai"
  - "Jun Yan"
  - "Bo Li"
  - "Huaming Chen"
year: 2024
venue: "arXiv"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：从 LLM 到 SE 智能体系统映射综述

## 1. 适用场景

- 需要判断手头的 LLM 应用/框架"算不算 LLM-based agent"时读这篇：§III.E Table V 给出 6 条判据（LLM 为大脑、决策与规划、自主用工具、方案评估选择为基本 1–4 条；多轮上下文交互、自主学习为进阶 5–6 条），可直接当评审 checklist 用。
- 要为某个 SE 活动（需求工程、代码生成、自主决策、软件设计、测试生成、安全维护）做 LLM→agent 化选型、找代表性框架/基线/benchmark/指标时读这篇：§IV–§IX 每章按"LLM 任务 / agent 任务 / benchmark / 指标"四段梳理，§X.C 汇总 benchmark 与 top-10 指标分布。
- 写 SE+LLM 相关工作或综述、需要与 7 篇既有综述（Fan ICSE-FoSE、Hou TOSEM SLR 等）做差异化定位时读 §II.A Table II（唯一显式做 "Agent Distinction" 的综述）。
- 设计 agent 评测方案、纠结选 Success Rate 还是 Pass@1/Accuracy 时读 §X.C.2 与 Fig.14（LLM 侧 Accuracy 20.9% 居首，agent 侧 Success Rate 20.0% 居首）。
- 找 SE agent 方向的研究选题/开源点时读 §X.D 六项挑战与 §X.E 四项机遇（标准化评测缺失、多智能体误差传播、工具集成脆弱、跨任务迁移弱、交互式数据稀缺、认知透明度）。

> 锚点：§I. INTRODUCTION; §II.A Existing Works; §III.E LLM in Software Engineering; §IV–§IX 各 SE 主题章; §X.C Benchmarks and Metrics; §X.D Challenges and Opportunities; §X.E Opportunities for Future Research。

## 2. 主要观点与方案

### 2.1 动机与研究问题（§I. INTRODUCTION）

静态 LLM 在 SE 中有三大短板：上下文长度受限、幻觉、不能用外部工具（§I）。LLM-based agent 以 LLM 为决策/行动核心，结合 RAG 与工具调用补足自主性与自改进能力。作者自称是首篇勾勒 SE 领域"LLM→agent"转变的综述，覆盖六大 SE 主题：需求工程与文档、代码生成与软件开发、自主学习与决策、软件设计与评估、测试生成、安全与维护（§I 列表）。四个研究问题：RQ1 SOTA 技术与实践（§IV–§IX）；RQ2 LLM 与 agent 在 SE 任务表现上的关键差异（§IV–§IX）；RQ3 常用 benchmark 与评估指标（§IV–§IX + §X）；RQ4 实验中最常用的模型（§X）。

### 2.2 综述方法与差异化定位（§II.A Existing Works; §II.B Methodology）

- 与既有综述对比：Table II 对比 [19][8][18][20][21][17][22] 七篇 2023–2024 综述（Fan ICSE-FoSE、Hou et al. SLR 等），均覆盖 Benchmarks/Metrics，仅本文同时勾选 "Agent in SE" 与 "Agent Distinction"，即唯一显式区分 LLM 与 LLM-based agent 的 SE 综述（§II.A）。早期综述普遍缺需求工程内容、且发表时间跨度大导致各 SE 任务内容深浅不一（§II.A）。
- 数据源与时间窗：DBLP + arXiv，聚焦 2023 下半年至 2024 年 12 月（选择 DBLP 因其 CS 会议策展质量、arXiv 因预印本时效性，区别于常见 Scopus/WoS）（§II.B-1）。检索用 Table IV 六主题关键词，主题内 OR、跨主题与 LLM 词 AND；Table III 纳入/排除标准（如排除 <7 页、灰色文献、非英文、与 SE/LLM 无实质相关）；辅以 snowballing（§II.B-2/3/4）。
- 语料画像：共 139 篇（Fig.1 为 2020–2024 趋势，agent 论文集中在 2023–2024）；Fig.3 venue 分布：arXiv 56 篇 40.3%，Others 27 篇 19.4%，NeurIPS 14 篇 10.1%，ICSE 9 篇 6.5%，ACL/ESEC-FSE 各 5 篇 3.6%，59.7% 来自同行评审 venue（§II.B-4）。Table I 给出六主题任务粒度分布（Security & Maintenance 43、Code Gen 35、REQ 28、AUTO 30、Design 19、Test 15，多任务论文重复计数）。

### 2.3 预备概念与 agent 判定标准（§III. PRELIMINARIES）

- §III.A–B：LLM 简史（规则→ML/NN→LSTM/RNN→2017 Transformer→GPT 系列，GPT-3 175B 参数）与三类架构：Encoder-Decoder（CodeT5+）、Encoder-only（BERT）、Decoder-only（GPT、LLaMA）。
- §III.C：agent 概念沿革（AlphaGo、复旦 agent 综述、ExpeL、具身 agent VOYAGER）；数据增强四法（同义替换、回译、改写、合成数据生成，Fig.4）；RAG 与长上下文互补（成本上 RAG 可比全 token 方案便宜约 99%）。
- §III.D：单 agent 弱点（长上下文不一致、幻觉难根除）vs 多 agent 六项优势（上下文共享、分工专业化、鲁棒纠错、上下文一致性、可扩展、动态问题求解）。
- §III.E：**核心贡献之一——Table V 六条 LLM-based agent 判据**（综合 SWE-agent、CODEAGENT、AutoCodeRover、GOEX、MetaGPT、AgentVerse、Reflexion、ExpeL 等文献共识）：1) LLM 是大脑；2) 具备决策与规划；3) 能自主决定何时/用哪个工具并整合结果；4) 能从多个同质结果中评估选优；5) 多轮交互并保持上下文；6) 自主学习与适应。1–4 为基本 agency，5–6 为进阶非必需。

### 2.4 六大 SE 主题逐一梳理（§IV–§IX，每章 LLM 任务/agent 任务/Benchmark/指标四段式）

- **需求工程与文档（§IV）**：LLM 侧 PRCBERT 在 PROMISE 上 F1 96.13%（超 NoRBERT/BERT-MLM）；SpecGen 生成 70% 程序规约（超 Houdini/Daikon）；BERT-MLM 补全缺失需求词 precision 82%；PathOCL 用 15 个 UML 模型+168 条英文规约做 OCL 生成（§IV.A）。Agent 侧：AISD 人机协同将用例通过率从 24.1% 提到 75.2%；多 agent 半结构化公文生成；HARA 安全需求（迭代周期从数月缩到一天）；ALAS 在 Austrian Post 六个敏捷团队改用户故事；Graph-RAG+CoT/ToT 合规审查 F1 87.93%（NASA X-38）；Sami et al. 用 PO/QA/Dev/Manager 角色仿真全流程（§IV.B）。Benchmark 缺标准化：多为自建（NFR 249 条/15 项目、PURE 40 份规约 23,000+ 句、CAASD 72 任务），agent 侧转向 SRS Broker/SRS Aero 等场景化合规基准（§IV.D）。指标从 precision/recall/F1 与 Likert/RUST 转向 ISO/IEC 29148、INVEST 与多角色人类反馈（§IV.E，Table VI）。
- **代码生成与软件开发（§V）**：LLM 侧 Copilot 使 HTTP server 任务快 55.8%；SQL-PaLM 文本转 SQL 测试准确率 77.3%/执行准确率 82.7%；print debugging 在中等 LeetCode +17.9%；Cycle 自改进 +63.5%；TICODER 测试驱动交互正确率 84% vs 基线 40%；ALGO 用 LLM 自生成 oracle verifier，一次性通过率较 Codex 提升 8×、较 CodeT 2.6×（§V.A）。Agent 侧：ChatGPT 自协作（分析/编码/测试三角色）HumanEval 较 GPT-4 最高提升 29.9%；L2MAC 用外存扩展上下文 HumanEval Pass@1 90.2%；SoA 超 Reflexion 5%；MetaGPT/ChatDev（平均 409.84 秒、$0.2967 出一套软件）/AGILECoder（DCGG 跨文件依赖图+ProjectDev 基准）仿真瀑布/敏捷生命周期；AgentCoder 在 HumanEval-ET pass@1 77.4%（前 SOTA 69.5%）；SWE-agent 靠 ACI 接口设计在 SWE-bench 达 12.5%、HumanEvalFix 87.7%；ClarifyGPT 主动澄清歧义使 GPT-4 Pass@1 相对 +11.66%（§V.B）。Benchmark 以 HumanEval（164 题）/MBPP（427 题）为主，agent 侧加 ToolBench（16,464 条 RESTful API 指令）/APIBench/CAASD；指标从 Pass@k/BLEU 扩展到 Win Rate、human revision cost、成本与生产力（§V.D–E，Table VII）。
- **自主学习与决策（§VI）**：LLM 侧发现"更多调用未必更好"（投票推理系统性能随调用数非线性先升后降）；SELF-DEBUGGING 在 Spider/TransCoder 准确率 +212%；LLM-as-judge 在 MT-Bench/Chatbot Arena 上与人类高度一致（§VI.A）。Agent 侧：Reflexion 用语言反馈把 HumanEval 首过率 80.1%→91.0%、ALFWorld +22%、HotPotQA +14%；ExpeL 经验池+洞见抽取实现跨任务迁移（Fig.7）；AgentVerse/CAMEL/BOLAA/More Agents（加 agent 数提升推理）；SELF 自进化使 GSM8K +6.82%；GPTSwarm 在 GAIA 上较最优方法提升达 90.2%；GoEx 提出 post-facto validation 运行时（§VI.B）。Benchmark 由静态（Defects4J、MMLU、MBPP）转向交互式（HotpotQA、ALFWorld、FEVER、WebShop 1.18M 商品）；指标出现 P/C/A-Score 等感知-认知-行动维度（§VI.D–E，Table VIII）。
- **软件设计与评估（§VII）**：与编码/需求/自治主题高度交叠，LLM 多用于"评估"而非高层设计：ChatGPT 日志摘要/代词消解 100% 成功但代码评审/漏洞检测弱；HLS 硬件协同设计建 Chrysalis 数据集（11 个开源 HLS 集 1000+ 函数级设计）；RaWi GUI 检索原型 precision@k +40%；教育场景 ChatGPT 答对 77.5% 软件测试题、解释正确率仅 53.0%（§VII.A）。Agent 侧：Auto-GPT 暴露跳步/幻觉/循环缺陷；ChatDev/LLMARENA（动态多 agent 博弈环境）；Flows 概念框架使 AI 独立解题率 +21pp、人机协作率 +54pp；HuggingGPT 以 ChatGPT 编排 HF 模型（§VII.B）。
- **测试生成（§VIII）**：LLM 侧 ChatGPT 安全测试在 55 个应用中挖出 24 个 PoC 漏洞；AdbGPT Android 错误复现 81.3%；LIBRO 在 Defects4J/GHRB 复现 33.5%/32.2%；Fuzz4All 通用 fuzzing 覆盖率平均 +36.8%、9 个系统发现 98 bug；COVERUP 行覆盖 62%→81%；ChatGPT vs EvoSuite 语句覆盖 55.4% vs 74.2%（207 个 Java 类），但 ChatGPT 在 17.9% 类上反超（§VIII.A）。Agent 侧：AgentCoder MBPP pass 89.9%；TestChain 在 LeetCode-hard 准确率 71.79%（超基线 13.84%）；XUAT-Copilot 微信支付 UAT 多 agent（计划/状态检查/参数选择）Pass@1 88.55% vs 单 agent 22.65%（450 条用例）；作者判断"纯为测试生成建 agent 框架是 overkill"，agent 测试研究多落在修复/回放类任务（§VIII.B–C，Fig.8）。
- **安全与维护（§IX）**：LLM 侧 WizardCoder 微调把 Java 漏洞检测 ROC AUC 从 CodeBERT 的 0.66 提到 0.69，而纯 GPT-3 零样本 AUC 仅 0.51（近随机）；GRACE 融合 Code Property Graph 使 F1 +28.65%；PRIMEVUL 揭露基准虚高（7B 模型 BigVul F1 68.26% vs PRIMEVUL 仅 3.09%）；EvalGPTFix（151 对 2023 AtCoder Java 修复对）上 ChatGPT 基础 prompt 修复 109 bug（recall 72.19%）；NAVRepair C/C++ 修复精度 +26%；SRepair 双 LLM 在 Defects4J 修 300 个单函数错误、较此前技术至少 +85%；PENTESTGPT 任务完成率超 GPT-3.5 228.6%、超 GPT-4 58.6%（§IX.A）。Agent 侧：LDB 基本块级调试 HumanEval 73.8%→82.9%；FixAgent 修 QuixBugs 79 bug 中 78 个（含 9 个此前未修复）、Codeflaws 正确率 96.5%；RepairAgent 状态机式自主修复 Defects4J 186 个 bug（164 个正确）；AutoCodeRover 用 AST 两段式（上下文检索 agent+补丁生成 agent）解 GitHub issue；MAGIS 四角色协作；ACFIX 挖掘 RBAC 实践+多 agent 辩论修复 94.92% 访问控制漏洞（裸 GPT-4 仅 52.54%）；GPTLENS 对抗式智能合约审计 76.9% vs 传统 38.5%；GPT-4 agent 仅凭 CVE 描述利用一日漏洞成功率 87%（§IX.B）。

### 2.5 跨主题讨论：模型、主题交叠与基准/指标（§X.A–§X.C）

- 实验模型（§X.A）：139 篇共出现 82 个不同 LLM；高频为 GPT-3.5、GPT-4、LLaMA2、Codex；自主决策主题 agent 论文中 GPT-3.5 用于 16/23 篇、GPT-4 用于 12/23 篇；需求工程 agent 实验只出现 GPT-3.5/GPT-4 两款；CodeLlama 集中出现于编码/测试/安全。agent 研究倾向用少数通用强模型而非领域专用模型（§X.A，Fig.10–11）。
- 主题交叠（§X.B，Table XII，Fig.12）：LLM 论文以需求工程（26.3%）与安全维护（22.4%）为主、合计近半；agent 论文以自主学习决策（29.9%，23 篇）居首、代码生成次之（21.1%，16 篇），需求与测试的 agent 化仍少。最频繁交叠：CODE×TEST、CODE×AUTO、AUTO×SEC 各 3 篇——agent 正成为跨域桥梁。
- 基准与指标（§X.C）：HumanEval/MBPP 双方最常用；agent 转向 FEVER/HotpotQA/SWE-bench/ProjectDev/API-Bank 等多轮工具型基准，Defects4J 因单步特性在 agent 研究中罕见；指标 top-10（Fig.14）：LLM 侧 Accuracy 20.9%、Pass Rate 16.4%、F1/Correctness 各 11.9%、Exact Match 6.0%；agent 侧 Success Rate 20.0%、Accuracy 15.7%、Pass@1 12.9%、R/P/F1 各 8.6%、Efficiency 5.7%、Win Rate 4.5%——评测重心从静态输入输出正确性转向端到端成功率与资源消耗。

### 2.6 六项挑战（§X.D Challenges and Opportunities）

1) 缺标准化 agent 定义与评测协议（Table V 只是工作定义，统一基准缺失，妨碍复现与横向比较）；2) 多 agent 工作流复杂与误差传播（同步/错误恢复/上下文共享难，异步交互易级联误解）；3) 工具集成瓶颈与外部依赖管理（编译器/测试框架/版本控制接口脆弱，缺工具延迟/失败/部分可观测下的评测策略）；4) 缺跨任务泛化与知识迁移（MetaGPT/MAGIS/SWE-agent 只在特定任务内积累经验，元学习与任务无关迁移未建立）；5) 数据稀缺与仿真环境不足（静态 HumanEval/MBPP 无法评测谈判、角色冲突、工具驱动推理等多轮多角色行为）；6) 认知透明度与可信度（自主性越高推理越不透明，安全敏感场景的决策轨迹可解释性是部署障碍）。

### 2.7 四项未来机遇（§X.E Opportunities for Future Research）

1) 统一 agent 分类学与多维评测框架，贯通"需求→设计→测试→安全部署"的端到端 agent 流水线（CAASD、API-Bank 可作起点）；2) 强化 agent 记忆与反思机制（显式记忆池、错误轨迹分析、目标驱动复盘，参考 ExpeL/Reflexion/Graph-RAG）；3) 人机协作与多模态具身 agent（角色感知输出粒度、决策可追溯、任务交接；扩展到 GUI 操作、可视化调试、嵌入式控制，参考 VOYAGER）；4) 走向真实工程部署（项目级上下文建模与动态追踪，如 DCGG；从单次执行器进化为"开发工作流协作者"，参考 MapCoder/MetaGPT/ClarifyGPT/AgentCoder/L2MAC）。

### 2.8 结论与局限（§XI. CONCLUSION）

结论重申：LLM-based agent 的出现使 SE 各主题研究面显著拓宽，在任务、benchmark、指标上与传统 LLM 呈系统性差异（§XI）。方法学局限（作者自述于 §II.B）：仅检索 DBLP/arXiv（未含 IEEE Xplore/ACM DL 之外的库）、时间窗限定 2023H2–2024.12、≥7 页门槛，可能漏收短文与更早工作；多主题论文重复计数使 Fig.2 统计>139。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 综述语料规模 | 139 篇论文（2020–2024 收集，聚焦 2023H2–2024.12，DBLP+arXiv+snowballing） | §II.B Methodology |
| 差异化定位 | Table II 对比 7 篇既有综述，仅本文同时具备 Agent in SE 与 Agent Distinction 两列 ✓ | §II.A Table II |
| 实验模型多样性 | 139 篇共 82 个不同 LLM；AUTO 主题 agent 论文 GPT-3.5 用于 16/23 篇、GPT-4 用于 12/23 篇 | §X.A Experiment Models |
| 主题分布对比 | LLM 论文：REQ 26.3% 居首、SEC 22.4%（合计近半）；agent 论文：AUTO 29.9%（23 篇）居首、Code 21.1%（16 篇） | §X.B Topics Overlapping |
| 指标偏好对比 | LLM top：Accuracy 20.9%、Pass Rate 16.4%；agent top：Success Rate 20.0%、Pass@1 12.9%，并新增 Efficiency 5.7%/Cost 4.3% | §X.C.2 Evaluation Metrics |
| Benchmark 迁移 | 双方最常用 HumanEval/MBPP；agent 侧转向 FEVER/HotpotQA/SWE-bench/API-Bank，Defects4J 因单步特性在 agent 研究罕见 | §X.C.1 Benchmarks |
| Agent 判定标准 | 6 条判据（1–4 基本、5–6 进阶），综合 SWE-agent/AutoCodeRover/GOEX/MetaGPT 等 8+ 框架共识 | §III.E Table V |
| 代表性 agent 增益（vs LLM 基线） | SWE-agent SWE-bench pass@1 12.5%、HumanEvalFix 87.7%（ACI 接口设计）；XUAT-Copilot Pass@1 88.55% vs 单 agent 22.65%；ACFIX 94.92% vs 裸 GPT-4 52.54% | §V.B; §VIII.B; §IX.B |
| 代表性 LLM 任务效果 | Reflexion 使 HumanEval 首过率 80.1%→91.0%（ALFWorld +22%、HotPotQA +14%）；Fuzz4All 覆盖率平均 +36.8%、发现 98 bug；Copilot 使 HTTP server 任务提速 55.8% | §VI.B; §VIII.A; §V.A |
| 基准可信度警示 | PRIMEVUL：同一 7B 模型 BigVul F1 68.26% vs PRIMEVUL 仅 3.09%，证明既有漏洞基准显著高估 code LM | §IX.A |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2408.02479 （v2，2025-04-13） |
| 综述方法学表格 | Table III 纳入/排除标准；Table IV 六主题检索关键词；Table V agent 六判据；Table VI–XI 六主题指标总表；Table XII 主题交叠计数 |
| 代表性 agent 框架（综述内重点分析） | SWE-agent、AutoCodeRover、MetaGPT、ChatDev（arXiv:2307.07924）、AGILECoder、MapCoder、L2MAC、AgentCoder、ClarifyGPT、FixAgent、RepairAgent（arXiv:2403.17134）、MAGIS、ACFIX、XUAT-Copilot、Reflexion、ExpeL、AgentVerse、CAMEL、GoEx |
| 代表性 LLM 方法（综述内重点分析） | PRCBERT、SpecGen、PathOCL、SQL-PaLM、TICODER、ALGO、RepoCoder、Fuzz4All、SymPrompt、COVERUP、AdbGPT、LIBRO、GRACE、NAVRepair、MOREPAIR、SRepair、PENTESTGPT |
| 关键 benchmark（论文汇总） | HumanEval、MBPP、SWE-bench、Defects4J、CAASD、ToolBench、APIBench、HotpotQA、ALFWorld、FEVER、WebShop、PRIMEVUL、EvalGPTFix、EvalPlus、ConDefects、Fuzz4All 所测 GCC/Clang/Go/javac/Qiskit |
| 数据源 | DBLP（https://dblp.org）与 arXiv（https://arxiv.org） |

## 5. 一句话索引（给 Agent 用）

> Jin et al. 综述（arXiv:2408.02479v2）：按六大 SE 主题（需求工程/代码生成/自主决策/软件设计/测试生成/安全维护）梳理 2023H2–2024.12 的 139 篇文献，显式区分 LLM 与 LLM-based agent 的任务、benchmark 与指标（Table II 中唯一做 Agent Distinction 的综述），给出 6 条 agent 判据（Table V）；发现 agent 论文以自主决策居首（29.9%）、指标以 Success Rate 20.0% 最常用（LLM 侧 Accuracy 20.9%），139 篇共 82 个实验模型，并总结 6 项挑战（缺标准定义/评测、多 agent 误差传播、工具集成、跨任务迁移、数据稀缺、透明度）与 4 项机遇（统一评测与端到端流水线、记忆反思、人机/具身多模态、项目级部署）。
