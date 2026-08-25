# ContextEngineering 主题论文摘要索引

> 主题：上下文工程——长上下文、编码 Agent 上下文、提示压缩
> 文件数：45（01–30、45 主目录 + 31–44 PromptCompression 子目录）
> 生成日期：2026-08-12（07 号另有 2026-08-17 增补的 v2 版本 PDF）

## 第一部分：长上下文与上下文工程（01–30、45）

### 长上下文窗口与失效（01–06）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-Context就是所需.md](01-Context就是所需.md) | Context Is What You Need: The Maximum Effective Context Window for LLMs | 提出 MECW（最大有效上下文窗口）概念 |
| 02 | [02-长上下文中的信息丢失.md](02-长上下文中的信息丢失.md) | Lost in the Middle: How Language Models Use Long Contexts | U 形性能曲线——中段位置性能塌陷 |
| 03 | [03-长上下文智能退化.md](03-长上下文智能退化.md) | Intelligence Degradation in Long-Context LLMs | 自然长度分布下的智能退化阈值 |
| 04 | [04-注意力归一化局限.md](04-注意力归一化局限.md) | Limitations of Normalization in Attention Mechanism | 注意力归一化的理论局限 |
| 05 | [05-LLM规模极限.md](05-LLM规模极限.md) | On the Fundamental Limits of LLMs at Scale | LLM 规模化的根本性限制 |
| 06 | [06-上下文腐烂.md](06-上下文腐烂.md) | Context Rot: How Increasing Input Tokens Impacts LLM Performance | "上下文腐烂"现象的系统化评测 |

### Agent 上下文与 Harness（07–11）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 07 | [07-AGENTS文件影响.md](07-AGENTS文件影响.md) | On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents | AGENTS.md 对编码 Agent 效率的影响 |
| 08 | [08-形式化上下文.md](08-形式化上下文.md) | Codified Context: Infrastructure for AI Agents in a Complex Codebase | 形式化上下文作为 Agent 基础设施 |
| 09 | [09-知识激活AI技能.md](09-知识激活AI技能.md) | Knowledge Activation: AI Skills as the Institutional Knowledge Primitive for Agentic SE | "技能 = 知识激活"原语 |
| 10 | [10-形式化架构描述.md](10-形式化架构描述.md) | Formal Architecture Descriptors as Navigation Primitives for AI Coding Agents | 形式化架构描述符作为导航原语 |
| 11 | [11-原生软件工程.md](11-原生软件工程.md) | Harness-Native Software Engineering: The Control Plane of Coding Agents | Harness-Native SE 与 8 函数控制面 |

### 仓库级 SWE 基准与 Agent（12–17）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 12 | [12-SWE-bench.md](12-SWE-bench.md) | SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | SWE-bench 评测基准 |
| 13 | [13-RepoGraph仓库图谱.md](13-RepoGraph仓库图谱.md) | RepoGraph: Enhancing AI Software Engineering with Repository-level Code Graph | AST-based 仓库图谱 |
| 14 | [14-SWE智能体.md](14-SWE智能体.md) | SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering | SWE-agent 的 ACI 设计 |
| 15 | [15-Agentless无代理.md](15-Agentless无代理.md) | Agentless: Demystifying LLM-based Software Engineering Agents | 无 Agent 的三阶段流水 |
| 16 | [16-CodeRAG基准.md](16-CodeRAG基准.md) | CodeRAG-Bench: A Benchmark for Retrieval-Augmented Code Generation | 代码 RAG 评测基准 |
| 17 | [17-代码库记忆.md](17-代码库记忆.md) | Codebase-Memory: A Repository-Level Code Understanding System with Persistent Memory | Tree-sitter + SQLite + Louvain 的跨会话记忆 |

### 综述与记忆管理（18–22）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 18 | [18-上下文工程综述.md](18-上下文工程综述.md) | A Survey of Context Engineering: Methods, Evaluation, and Frontiers | 上下文工程领域综述 |
| 19 | [19-大模型记忆.md](19-大模型记忆.md) | Memory in LLMs: Mechanisms, Evaluation and Evolution | LLM 记忆机制综述 |
| 20 | [20-TokenMizer.md](20-TokenMizer.md) | TokenMizer: Graph-Structured Session Memory for Long-Horizon LLM Context Management | 长程会话的图结构记忆 |
| 21 | [21-HORMA.md](21-HORMA.md) | Organize then Retrieve: Hierarchical Memory Navigation for Efficient Agents | 层次化记忆导航 |
| 22 | [22-VISTA.md](22-VISTA.md) | LLM Agents Are Latent Context Managers | 潜在上下文管理与本体感受仪表盘 |

### 仓库级上下文检索与处理（23–30）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 23 | [23-ContextSniper仓库级代码记忆.md](23-ContextSniper仓库级代码记忆.md) | ContextSniper: AntTrail's Token-Efficient Code Memory for Repository-Level Program Repair | Token 高效的仓库级程序修复记忆 |
| 24 | [24-智能体检索基准.md](24-智能体检索基准.md) | Agent Retrieval Bench: Evaluating Repository Context Retrieval for Coding Agents | Agent 检索能力基准 |
| 25 | [25-MRCoder.md](25-MRCoder.md) | MRCoder: An Efficient Context Selecting Approach for Repository-Level Code Generation | 高效上下文选择 |
| 26 | [26-先知后修.md](26-先知后修.md) | Know Before Fix: QA-Driven Repository Knowledge Acquisition for Software Issue Resolution | QA 驱动的仓库知识获取 |
| 27 | [27-可寻址召回压缩.md](27-可寻址召回压缩.md) | Addressable Recall Compaction for Long Context-Window Control in AI Agents | 可寻址召回压缩（ARC） |
| 28 | [28-智能体上下文管理.md](28-智能体上下文管理.md) | ACM: Agentic Context Management for Long Horizon Tasks | 智能体上下文管理 |
| 29 | [29-上下文文件帮助.md](29-上下文文件帮助.md) | Do Context Files Help Coding Agents? A Two-Agent Ablation Study | 上下文文件的双 Agent 消融 |
| 30 | [30-注册表到仓库.md](30-注册表到仓库.md) | From Registry to Repository: How AI Agent Skills Are Written, Adapted, and Maintained | AI 技能从注册表到仓库 |

### 上下文文件实证（45，2026-08-25 增补）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 45 | [45-评测AGENTSMD上下文文件.md](45-评测AGENTSMD上下文文件.md) | Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents? | AGENTS.md 三设置大规模对照：不提成功率、成本 +20% |

## 第二部分：提示压缩（31–44，子目录 PromptCompression/）

### 经典方法（31–36）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 31 | [31-LLMLingua提示压缩.md](31-LLMLingua提示压缩.md) | LLMLingua: Coarse-to-Fine Prompt Compression | 粗到细的提示压缩（基线方法） |
| 32 | [32-LongLLMLingua长上下文压缩.md](32-LongLLMLingua长上下文压缩.md) | LongLLMLingua: Prompt Compression for Long Context Scenarios | 长上下文场景的提示压缩 |
| 33 | [33-LLMLingua2.md](33-LLMLingua2.md) | LLMLingua-2: Task-Agnostic Prompt Compression via Token Classification | 任务无关的 token 分类压缩 |
| 34 | [34-SelectiveContext选择上下文.md](34-SelectiveContext选择上下文.md) | Selective Context: Self-Information Based Content Filtering | 自信息百分位过滤 |
| 35 | [35-Gist摘要标记.md](35-Gist摘要标记.md) | Learning to Compress Prompts with Gist Tokens | Gist token（soft prompt 压缩） |
| 36 | [36-NanoCapsulator.md](36-NanoCapsulator.md) | Nano-Capsulator: NL-Formatted Prompt Compression with Reward | NL 形式封装 + 语义保持奖励 |

### 风格/语言/级联类（37–41）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 37 | [37-小模型模糊性.md](37-小模型模糊性.md) | DisambiguSLM: Small LM Resolves LLM Prompt Semantic Ambiguity | 小模型消解提示语义模糊性 |
| 38 | [38-风格压缩.md](38-风格压缩.md) | Style-Compress: LLM-Based Prompt Compression Considering Task-Specific Styles | 5 种风格维度的压缩 |
| 39 | [39-上下文级联C3.md](39-上下文级联C3.md) | C3: Context Cascade Compression via Cascaded Two-LLM | 两 LLM 级联压缩 |
| 40 | [40-跨语言token套利.md](40-跨语言token套利.md) | Cross-Lingual Token Arbitrage for Code Agent Context Windows | 跨语言 token 套利 |
| 41 | [41-电报英文.md](41-电报英文.md) | Telegraph English: Semantic Prompt Compression via Structured Symbolic Rewriting | 结构化符号改写 |

### 综述与工具（42–44）

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 42 | [42-提示压缩综述.md](42-提示压缩综述.md) | Prompt Compression for Large Language Models: A Survey | 提示压缩综述（2024-10） |
| 43 | [43-压缩工具包.md](43-压缩工具包.md) | PCToolkit: A Unified Plug-and-Play Prompt Compression Toolkit | 统一即插即用压缩工具包 |
| 44 | [44-压缩实证研究.md](44-压缩实证研究.md) | An Empirical Study on Prompt Compression for LLMs | 6 方法 × 3 LLM × 13 数据集的实证 |

## 推荐阅读路线

- **理解长上下文窗口的真相**：01 → 02 → 06 → 03（"MECW → U 形曲线 → 上下文腐烂 → 退化阈值"）
- **理解 Agent 上下文工程全貌**：18（综述）→ 11（Harness Native）→ 17 / 20（代码库记忆 / TokenMizer）→ 23（ContextSniper）
- **理解 SWE Agent 与仓库交互**：12（基准）→ 13 / 14（图谱 / Agent）→ 15（无 Agent）→ 16（CodeRAG）
- **评估 context file 的真实收益**：45（4 agent×三设置大规模对照）→ 07（效率影响）→ 29（双 Agent 消融）（"成本 +20% 不提性能 → 效率维度 → 机制消融"）
- **理解提示压缩的演进**：31（基线）→ 32（长上下文）→ 33（任务无关）→ 34 / 35（替代路线）→ 42（综述）→ 43 / 44（工具 + 实证）

## 与 GraphIt-KB 的相关性

- 论文 01（MECW）直接支撑 GraphIt-KB 的"上下文预算"设计（FR-3.2 中 token 预算默认 8k 即受此启发）。
- 论文 02（U 形曲线）支撑检索结果排序策略——相关文档应放首尾。
- 论文 11 / 17 / 20 直接支撑"Agent 长程上下文/记忆"的概念建模，与 GraphIt-KB 的"章节级图谱 + 主题质心 + 主题冷启动"机制呼应。
- 论文 27 / 28（ARC / ACM）提供"压缩+遗忘"机制，与 NFR-3 的"原文不可变"约束互补。
- 论文 31–44 系列是 GraphIt-KB 未来"上下文组装"模块的可选压缩后端参考。
- 论文 45（AGENTS.md 评测）警示：KB 向 Agent 注入的摘要/上下文也应以"任务级收益"严格评测（本篇的三设置对照 + trace 分析即范式），而非默认"多上下文更好"。