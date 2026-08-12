# 论文摘要：TokenMizer（图结构会话记忆）

> **原论文标题**：TokenMizer: Graph-Structured Session Memory for Long-Horizon LLM Context Management
> **完整 PDF 文件名**：`20-Mishra-TokenMizer.pdf`
> 作者 / 年份：Shweta Mishra（独立研究者），2026-07，arXiv:2606.06337
> 摘要类型：系统方案 / Agent 设计参考
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **长周期 LLM 会话**（多轮、跨任务）时，需要把"超出有效上下文窗口"的会话状态以结构化方式保存。
- 想用 **MCP 工具** 让 Agent **自己管理自己** 的会话记忆（checkpoint / resume）时，本文给出端到端实现。
- 实现 **会话图 + 类型化节点 / 边 + 8 状态生命周期** 时，本文是参考实现（含 schema、API、SQLite 表结构）。
- 想做 **决策溯源 / 时间旅行查询**（"在某时刻 Agent 以为用了哪个数据库"）时，本文的 bitemporal validity + DecisionTransition 是直接可用方案。
- 在终端、IDE 或 CI 上落 **OpenAI-compatible proxy**，无需改应用代码就能接入持久记忆，本文给出 v0.3.1 的实现与评测。

> 锚点：Abstract；§I Introduction；§IV Design: The Session Graph；§V Serving Layer；§VI Inspection & Interoperability。

## 2. 主要观点与方案

### 2.1 问题与动机

- 长周期会话不断积累 token，**实际可用窗口（Maximum Effective Context Window, MECW）** 远小于广告窗口（例：复杂编码任务 MECW 仅约 16k vs 128k advertised）。
- 三大常用缓解（**截断 / 摘要 / 检索**）都 **把历史当扁平文本**，丢失"会话可恢复"的核心结构：决策与理由、任务状态、文件修改史。
- 例：摘要会把"选了 Redis"与"考虑过 Redis 但否决"混在一起；检索会漏掉结构上关键但语义距离远的事实。

### 2.2 核心方案：会话图 + 类型化 schema

- 把 LLM 会话视为 **结构化的、可修订的知识体**。
- 维护一个 **类型化知识图**，在上下文预算边界处用"基于图状态的 token-budgeted 序列化"替换原始 transcript。
- **Schema（14 node types / 7 edge types / 8-state lifecycle）**：
  - **节点类型**：TASK / FILE / ERROR / TEST / SCHEMA（动作类）；DECISION / DEPENDENCY / API / ENDPOINT（决策类）；GOAL / ENVIRONMENT / PROJECT / CONCEPT / AGENT（上下文类）。
  - **边类型**：DEPENDS_ON / RELATED_TO / IMPLEMENTS / FIXES / BLOCKS / PART_OF / SUPERSEDES。
- **8 状态生命周期**：在传统 4 状态（pending / in-progress / done / ...）上扩展 SUPERSEDED / INVALIDATED / ARCHIVED + MODIFIED 别名；**核心状态转移单调**——下移被拒绝以防提取噪声回退已确认进度。

### 2.3 关键设计

- **Bitemporal validity**：每个节点有 valid_from / valid_until 区间（开区间 = 当前有效），支持 **time-travel 查询**："数据库决策被反转之前，会话以为什么？"
- **Decision-Transition Records**：决策被取代时，独立持久化触发者、原因、证据原文、置信度差；独立于图剪枝以保 audit trail。
- **Hybrid Extraction**：默认是 **确定性正则表达式管线**（无 LLM 调用），可选后台 LLM 提取覆盖隐式措辞（"let's go with Redis"）。
- **Validation Layer**：候选节点过 confidence 阈值（默认 0.50）+ 类型校正（扩展名 → FILE；URL → ENDPOINT）。
- **Checkpoints & Resume Tiers**：85% MECW 触发或 REST/CLI/MCP 手动触发；按重要性顺序写入 **critical (≤100 token) / standard (≤300) / full (≤600)** 三档 resume；增量 diff 存储（O(Δ) 而非 O(|G|)）。
- **保护节点**：DECISION / GOAL / ENVIRONMENT / SCHEMA 不会被剪枝——保留会话定义性上下文。

### 2.4 Serving Layer（§V）

- **透明 OpenAI-compatible proxy**（FastAPI + Uvicorn）：客户端仅改 base_url 即可；无 session_id 时直通。
- **9 个 provider adapter**：Anthropic、OpenAI、DeepSeek、Mistral、OpenRouter、Grok、Cohere、Gemini、Ollama。
- **SSE 流式**：本地实现 Anthropic / OpenAI-compatible / Ollama 流；语义缓存命中流为单 chunk；图抽取与统计在流结束后跑——**不增加 TTFT**。
- **Security middleware**：状态变更端点需 API key；chat 路径加 prompt-injection 防护 + rate limit；**凭据脱敏**（API key / 私钥 / 密码 → `[REDACTED]`）在入口一次完成，下游路径天然安全。

### 2.5 Inspection & Interoperability（§VI）

- **Dashboard & Analytics**：自包含监控面板（GET /）、token 节省、每层管线状态、节点类型分布、交互式图视图。
- **Visualization Exports**：D3 JSON / 自包含 HTML / Obsidian Canvas——便于设计评审与个人知识管理桥接。
- **MCP Integration**：stdio MCP server 暴露 5 个工具：`checkpoint_session` / `resume_session` / `get_graph_stats` / `analyze_file` / `get_savings_stats`，MCP 与 REST 共享状态。还提供 Claude Code 插件与 `.claude-plugin/` marketplace manifest。

### 2.6 实现与体量

- ~9,500 行 Python 3.10+，FastAPI + tiktoken (cl100k_base) + SQLite。
- 220 个测试函数：unit / integration / chaos-recovery / memory-accuracy。
- 所有阈值（MECW %、confidence floor、cache similarity、compression minimum）YAML 可配。

### 2.7 评测（§VIII–§IX）

- **诚实小评测**：3 个合成会话 / 启发式提取 / 单基线 / 每个数字可溯源到一份 results 文件。
- **任务定义**：Recall per category（task / decision / file），信息损失 L = 1 − (Rec_task + Rec_dec + Rec_file)/3；Token efficiency η = |R|/100。
- **基线**：plain-summary baseline（关键字扫描整段 transcript，hand-specified tech list 与 ground-truth 词汇重叠，**有利于基线**）。
- **关键结果**：graph extraction 在 task recall 与基线并列（75.6%）；**decision recall 85.0% vs 70.0%**；file recall 100% vs 91.7%。Standard-tier resume 201–302 token；full-session 提取耗时 8.1–529.9 ms。
- **坦承的局限**：n=3 合成会话、措辞有利于启发式（隐式措辞未测）、弱基线（vs LLM summary）、精度未报告、压缩/缓存未评测、延迟扩展未画像、无端到端 resumption 度量、无跨会话记忆。

## 3. 达到的效果

| 度量 / 现象 | 数值 / 结论 | 锚点 |
|---|---|---|
| MECW 假设 | 16k（vs advertised 128k） | §III, Figure 6 |
| Schema 规模 | 14 node types / 7 edge types | §IV-A |
| 生命周期 | 8 state（含 superseded / invalidated / archived） | §IV-B |
| Bitemporal | valid_from / valid_until + time-travel API | §IV-C |
| DecisionTransition | trigger / reason / evidence / confidence_delta，独立于图剪枝 | §IV-D |
| Checkpoint 触发 | 85% MECW / REST / CLI / MCP | §IV-F |
| Resume tiers | critical ≤100 / standard ≤300 / full ≤600 token | §IV-F |
| Provider adapters | 9（Anthropic / OpenAI / DeepSeek / Mistral / OpenRouter / Grok / Cohere / Gemini / Ollama） | §V-A |
| MCP tools | 5（checkpoint / resume / get_graph_stats / analyze_file / get_savings_stats） | §VI-C |
| 节点类型数 | 5 action + 4 decision + 5 context | §IV-A |
| Task recall（heuristic vs baseline） | 75.6% vs 75.6%（平） | Table III |
| Decision recall | 85.0% vs 70.0%（+15 pp mean） | Table III |
| File recall | 100% vs 91.7% | Table III |
| Resume token 数（standard tier） | 201–302 token（mean 254.3） | Table III |
| Full-session 提取耗时 | 8.1–529.9 ms（mean 187.2） | Table III |
| 实现规模 | ~9.5k 行 Python + 220 tests | §VII |
| 已知 ceiling effects | file 100% / decision 接近 100%；隐式措辞未测 | §XI |

> 锚点：§IV–§VII Design & Implementation；§VIII–§IX Evaluation；§XI Limitations。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2606.06337（v2，2026-07-03） |
| 代码与基准 | https://github.com/Shweta-Mishra-ai/tokenmizer（MIT 协议） |
| 关联工作 | MemGPT（OS 风格分层记忆）、LangChain KG Memory、GraphRAG、LLMLingua / LongLLMLingua、RECOMP、Active Context Compression、Sentence-BERT（语义缓存）、Model Context Protocol |
| 配套工具 | FastAPI、Uvicorn、tiktoken (cl100k_base)、SQLite、sentence-transformers |
| 可视化 | D3 JSON、自包含 HTML、Obsidian Canvas |

> 锚点：§VI–§VII；§XII Conclusion；References。

## 5. 一句话索引（给 Agent 用）

> 给长周期 LLM 会话做"会话级记忆 OS"时，参考 TokenMizer 的架构：**14 类节点 / 7 类边 / 8 状态生命周期 + bitemporal 有效区间 + 独立 DecisionTransition 表 + 三档 token-budgeted resume + OpenAI-compatible proxy + MCP 工具暴露**——把会话当作结构化的、可修订的知识体，而不是扁平文本，是 Agent 跨会话/跨任务的工程模板。