# 工业界 Agent 框架设计对比 + 设计观点文章梳理

> 状态：已完成初稿（2026-08-17）

调研范围：7 个主流工业界 agent 框架的官方文档，以及 5 篇有影响力的 agent 设计观点文章。资料以官方文档/原文优先，全部附 URL。

---

## A. 框架对比

对比维度：**核心抽象**（框架给开发者提供什么构件）、**控制流归属**（谁来决定下一步做什么——框架代码、开发者显式编排、还是 LLM 动态决策）、**状态管理**（上下文/中间结果如何存放与持久化）、**官方适用场景**。

### A1. LangGraph（LangChain）——图编排

- **核心抽象**：`StateGraph` / `Node` / `Edge`（含条件边、`START`/`END`）。图中共存确定性节点与 LLM 驱动的 agentic 节点。设计灵感来自 Pregel / Apache Beam，接口风格借鉴 NetworkX。定位为"低级编排框架与运行时"（low-level orchestration framework & runtime），只管编排，不抽象提示词与架构。
- **控制流归属**：**开发者显式编排**。图结构由开发者定义；条件边 + 循环边可实现"模型在受限选项内决定分支"的半动态控制。文档明确说它不替你做决策抽象，把控制权留给开发者。
- **状态管理**：共享 `State` 对象（TypedDict/Pydantic），通过 **reducer** 定义状态字段的合并策略（如消息追加）；内置 **checkpointing/persistence**，支持 durable execution、断点恢复、human-in-the-loop（interrupt 任意节点）。
- **官方适用场景**：长时运行、有状态、需持久化与人工介入的复杂 agent；确定性步骤与 AI 决策混合的可审计生产工作流。官方同时说明：若只需常见 LLM+工具循环，它过于低级，建议用更高层抽象（如 Deep Agents）。
- URL: https://docs.langchain.com/oss/python/langgraph/overview （原 https://langchain-ai.github.io/langgraph/ 已迁移至此）

### A2. AutoGen v0.4（Microsoft）——actor 模型重构

- **核心抽象**：`Agent`（继承 `RoutedAgent`，用 `@message_handler` 声明消息处理逻辑）+ `Agent Runtime`（通信基础设施 + 生命周期管理）。消息为 dataclass，按类型路由。v0.4 是对旧版 conversable agent 的彻底重写：从"对话容器"改为显式的异步消息传递框架。
- **控制流归属**：**去中心化，归属各 agent 与消息循环**。官方表述："framework provides a communication infrastructure, and the agents are responsible for their own logic"。控制流由 agent 间消息往来（pub/sub topic + 直接消息）与外部终止条件（`run_until`）共同涌现，无全局编排器。
- **状态管理**：状态保存在各 agent 实例内部（actor 本地状态）；agent 由 runtime 通过工厂函数创建/托管，分布式运行时可跨进程、跨机器、跨语言托管 agent（身份、语言、依赖各自独立）。框架本身不提供全局共享状态。
- **官方适用场景**：多 agent 协作（顺序、并发、群聊、handoff、反思、辩论等模式）；本地单线程嵌入或分布式部署；需要逻辑与传输解耦、自定义消息协议的场景。
- URL: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/quickstart.html ；架构总览 https://microsoft.github.io/autogen/stable/

### A3. CrewAI ——crew（角色扮演协作）+ flow（显式流程）

- **核心抽象**：`Agent`（role/goal/backstory 角色化设定）、`Task`（description + expected_output + 指派 agent）、`Crew`（agents + tasks + process）。Crew 之上另有 `Flow`：基于事件/步骤装饰器的显式工作流编排（`@start`/`@listen`），用于把多个 crew 串成确定性 pipeline。推荐 YAML 配置（`@CrewBase` + `@agent`/`@task`/`@crew` 装饰器）。
- **控制流归属**：双层。**Crew 内部**默认 `sequential`（按任务列表顺序）或 `hierarchical`（由 manager_llm/manager_agent 管理者 agent 动态分派与验证——控制流交给 LLM 管理者）；**Flow 层**则回到开发者显式编排。可选 `planning` 让 AgentPlanner 先为每个任务生成计划注入描述。
- **状态管理**：Crew 级 memory（短期/长期/实体记忆，可配置 provider 与 embedder）；工具结果 cache；`CrewOutput`（raw/JSON/Pydantic/tasks_output/token 用量）；支持 `crewai replay -t <task_id>` 从某任务重放（本地保存最近 kickoff 的任务输出）。Flow 层有独立的共享 state 对象。
- **官方适用场景**：快速搭建多角色协作的"团队式"任务流水（分析→写作→评审类）；开发者定位偏非重度框架用户，强调开箱即用；需要确定性时升级到 Flow。
- URL: https://docs.crewai.com/concepts/crews ；Flow: https://docs.crewai.com/concepts/flows

### A4. OpenAI Agents SDK ——极简原语 + handoff/guardrails

- **核心抽象**：刻意收敛为四个原语：`Agent`（LLM + 指令 + 工具，自带循环直到完成）、`Handoff`（agent 间交接/委派，或 agents-as-tools 的 manager 模式）、`Guardrail`（输入/输出校验器，与 agent 执行并行运行、fail fast）、`Tracing`（内置可视化调试）。另有 `Session`（持久化记忆层，后端支持 SQLite/SQLAlchemy/Redis/MongoDB/Dapr 等）。
- **控制流归属**：**单 agent 内由模型驱动循环**（模型自主调工具直到完成）；**多 agent 间由模型决策 handoff**（LLM 交接），框架不提供图/流程编排器——编排逻辑要么写在 agent 指令里，要么由宿主代码决定何时启动哪个 agent。
- **状态管理**：本地运行（本地变量）或 `Runner` 的多 agent 会话；Session 抽象负责跨轮上下文持久化；tracing 贯穿全链路。
- **官方适用场景**：官方文档给出明确分界——需要运行时管理轮次/工具执行/护栏/交接/会话、产出产物或跨多步协调、需可恢复执行（sandbox agents）时用 SDK；短期流程、想自己控制循环与状态时直接用 Responses API。
- URL: https://openai.github.io/openai-agents-python/

### A5. Google ADK（Agent Development Kit）

- **核心抽象**：`Agent`（LLM agent / managed agent / graph workflow）、`Tool`（自定义函数、MCP、OpenAPI 三类）、`Session/State`（会话上下文 + 状态 + memory + 事件，支持 rewind、上下文压缩与模型上下文缓存）、多 agent 层级与模板工作流（Sequential/Loop/Parallel）。支持 Python/Java/Go/TypeScript/Kotlin 多语言。
- **控制流归属**：多种模式并存——图工作流（开发者显式：路由、数据流、人工介入、动态流）、模板工作流（声明式组合）、以及多 agent 间的 **LLM 编排**（transfer/路由由模型决定）。Callbacks 机制允许在流程各阶段插入自定义逻辑。
- **状态管理**：Session 服务为中心：会话状态、事件流、memory、上下文压缩、缓存，均有框架级服务与 API。
- **官方适用场景**：企业级 agent 构建到部署（adk web 可视化、adk api_server、Cloud Run/GKE/Agent Runtime），强调评估、可观测性、安全、A2A 协议互操作、实时/语音交互；多语言、多云部署需求。
- URL: https://adk.dev/get-started/ （原 https://google.github.io/adk-docs/ 已迁移）

### A6. AgentScope（阿里）——消息中心（v1）→ ReAct+中间件（v2）

- **核心抽象**：v1 论文的核心是**消息中心**（message-centric）：`Msg` 消息体 + `Agent` + 显式 `Pipeline`/`MsgHub` 控制流原语，"一切交互皆消息"。2025 年 AgentScope 2.0 重构：转向以 `ReActAgent`（reasoning-acting 循环）为单一核心抽象，吸收 middleware（上下文工程、记忆、RAG、防护等以中间件注入）、模型上下文协议、agent service（文件/搜索/浏览器/数据库等外置服务）等思想，兼容 A2A 与 MCP。
- **控制流归属**：v1 归属开发者的显式编排（Pipeline/MsgHub 组合 agent）；v2 归属单 agent 内的 ReAct 循环，多 agent 协同仍可用 pipeline 原语显式组装。
- **状态管理**：消息与对话历史为状态载体；v2 提供记忆/上下文中间件与 state 管理；支持容错（retry）与分布式多进程。
- **官方适用场景**：多 agent 对话式应用与研究实验；v2 强调"能看懂、可理解、可信任"的 agent，适合构建可靠的单体 ReAct agent + 外部服务，也保留多 agent 能力。
- URL: https://github.com/agentscope-ai/agentscope ；文档 https://doc.agentscope.io/ ；v1 论文（arXiv:2402.14034）

### A7. HF smolagents ——code agent（写代码即行动）

- **核心抽象**：`CodeAgent` / `ToolCallingAgent`。核心主张：agent 的"行动"不是发 JSON 工具调用，而是**直接写一段 Python 代码**（`code_block` = action），在受限执行环境（e2b 沙箱或本地 Python 解释器）中运行；代码中的变量就是中间状态。Tool 就是一个带类型提示的 Python 函数 + 描述。仅依赖 `transformers` + `jinja2`，极轻量。
- **控制流归属**：单 agent 的 ReAct 式循环（thought → code action → observation 重新注入），循环由框架驱动，"下一步做什么"由模型写的代码决定；多 agent 可用 managed agent（一个 agent 作为另一 agent 的 tool）。
- **状态管理**：状态 = 执行代码中的变量 + 对话历史（logs 追加到 prompt），无独立持久化层（刻意保持简单）。
- **官方适用场景**：轻量、需要高透明度与组合性（代码可分支/循环/直接操作对象而非串 JSON）的 agent；快速原型与本地/开源模型（有多个 SOTA 开源模型的 agent 排行）；不适合重持久化、长事务的企业流程。
- URL: https://huggingface.co/docs/smolagents/index ；博客 https://huggingface.co/blog/smolagents

### 框架横向小结

| 框架 | 核心隐喻 | 控制流归属 | 状态管理重心 |
|---|---|---|---|
| LangGraph | 数据流图（Pregel 系） | 开发者显式（图）| 共享 State + checkpoint |
| AutoGen v0.4 | Actor / 消息传递 | 去中心化（消息涌现）| agent 本地状态，无全局 |
| CrewAI | 角色团队 + 流程 | hierarchical 时交 LLM 管理者；Flow 显式 | crew memory + replay |
| OpenAI Agents SDK | 极简原语 | 单 agent 模型循环 + 模型 handoff | Session 持久化 |
| Google ADK | 企业应用平台 | 图 / 模板 / LLM 编排三态并存 | Session 服务为中心 |
| AgentScope | 消息中心 →（v2）ReAct + 中间件 | v1 显式 pipeline；v2 ReAct 循环 | 消息历史 + 记忆中间件 |
| smolagents | 代码即行动 | 模型写代码 | 代码变量 + 对话日志 |

一个值得注意的共性趋势：**从"框架替你编排"（早期 LangChain AgentExecutor、AutoGen v0.2 群聊）退回到"开发者显式编排 + 模型在受限点决策"**（LangGraph、AutoGen 重写、CrewAI Flow、AgentScope v2），与 B 部分的多篇观点文章相互印证。

---

## B. 设计观点文章

### B1. Anthropic《Building Effective Agents》（2024-12）

- URL: https://www.anthropic.com/research/building-effective-agents （中文版：https://www.anthropic.com.cn/research/building-effective-agents ）
- **核心主张**：agent 不是"更炫的技术"，而是"用 LLM 完成任务的最简可靠单元"。区分两个层次——**workflows**（开发者预编排代码路径、LLM 只在节点上调用）与 **agents**（LLM 自己掌控循环、决定下一步用什么工具直到完成）。大多数场景用不到 agent，workflow 就够。
- **论据**：成功率随任务分解与步骤数衰减；管理复杂度（保持系统"可理解"）比堆能力更重要；成本与延迟随自主性上升。给出 5 种 workflow 模式（prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer）+ 1 种 autonomous agent 模式，均附代码。
- **适用边界**：适用所有 LLM 应用设计；明确说"先找最简方案"，只有开放式、步数不可预知的问题才值得上 autonomous agent。该文基本是后续各框架"显式编排回归"的源头文本。

### B2. Cognition（Devin 团队）《Don't Build Multi-Agents》（2025-06）

- URL: https://cognition.ai/blog/dont-build-multi-agents
- **核心主张**：生产环境中不要构建多 agent 系统；两个原则——(1) **Share context**：子 agent 间上下文发散会导致决策冲突；(2) **Actions carry implicit decisions**：一个 agent 的行动携带隐式决策，另一 agent 无法撤销，错误会复合。
- **论据**：Devin 内部实验——并行子 agent 各自埋点冲突的失败案例；多 agent 看似提速，实际因协调失败返工而更慢；单 agent 长上下文 + 选择性压缩优于分割上下文。
- **适用边界**：作者自己声明是"方向性经验"（directional，非教条），承认读多写少的只读任务（如并行搜索/代码审查、Anthropic 式 research orchestrator）可以安全并行；争议点在于该边界如何划。与 B5（Anthropic 多 agent 系统）形成正面交锋。

### B3. HumanLayer《12-Factor Agents》（2025）

- URL: https://github.com/HumanLayer/12-factor-agents （正文 https://compass.humanlayer.dev/ ）
- **核心主张**：类比 12-factor app，agent 应由 12 条工程原则构成，核心精神是**"用自然语言做控制流、以 LLM 谓词做分支"的耐用代码结构**：1) 自然语言是核心接口；2) 控制流对开发者可见；3) agent = 循环（LLM 调用 + 上下文管理）；4) 工具是你的防错边界（tools as guardrail 面）；5) 状态与代码合一；6) 短小扁平的 agent 优先；7) 工具即人机接触面（hijack 接管点）；8) 结构化输出融入循环；9) 把你的上下文当工程产物管理（收缩/压缩）；10) 小而专的模型驱动小而专的循环；11) 拥抱单态（one big state machine 优于隐式多 agent）；12) 无所畏惧地重写（换模型/改 prompt 即改代码）。
- **论据**：大量来自 HumanLayer 客户生产部署的案例（客服、DevOps 等），主张几乎所有"高级框架功能"（RAG、memory、subagent）都可以用"prompt + 循环 + 工具"直接实现。
- **适用边界**：面向构建长期维护的生产 agent 的工程团队；明确偏向"代码中心"而非"框架中心"，不否认大型并行研究类系统的价值，但主张从最小结构起步。

### B4. Harrison Chase《Towards a Cognitive Architecture for Agents》（2025-09，LangChain 博客，后改版收录为 "Ambient Agents" 系列 / 字幕 "context engineering" 讨论的一部分）

- URL: https://blog.langchain.com/towards-a-cognitive-architecture-for-agents/ （RSS/转载对照：https://www.latent.space/p/langchain-cognitive-architecture ）
- **核心主张**：当前 LLM 缺少类似 System 2 的"认知架构"——需要显式设计**长期记忆（memory/knowledge）、规划（planning）、执行（doing）三者分离又协同**的结构。提出以"环境/上下文工程"为中心：agent 不只是"循环+工具"，而应是围绕记忆（写入/整理/检索）、任务队列（pull 模型：agent 主动拉取下一个任务而非被推送）与子 agent（隔离上下文、按需 fork）组织的认知系统。这也是 LangGraph/LangMem/Agent Inbox 产品路线的思想底稿。
- **论据**：观察纯 ReAct 循环在长任务上退化（上下文膨胀、无任务边界、无经验沉淀）；借心理学双过程理论说明补丁式 prompt 工程到不了 System 2 能力；主张把"学会的任务"固化为可复用结构（记忆/技能），而不是每次从零推理。
- **适用边界**：面向长周期、可积累经验的 agent（个人助理、ambient agents）；短期任务用不上这套重型结构。社区批评主要在"记忆-规划-执行三分是否只是把框架功能重新包装"。

### B5. Anthropic《How We Built Our Multi-Agent Research System》（2025-06）

- URL: https://www.anthropic.com/engineering/built-multi-agent-research-system
- **核心主张**：在**开放式研究（广度优先、读多写少、可并行切分**）场景中，多 agent 编排显著优于单 agent（内部评估中比 Opus 单 agent 提升 90.2%）；且 token 消耗与效果正相关（"more tokens, more performance"）。关键设计：lead agent 制定计划并动态拆分子任务、子 agent 并行搜索、结果只回传压缩摘要；工具设计针对 agent 心智（工具描述清晰、控制权限边界）；用"prompt 工程不是刷题而是研究方法论"的态度迭代。
- **论据**：运营分析与用户反馈显示单 agent 在信息过载与单线程深度搜索上失败；多 agent 并行扩展搜索广度；效果高度依赖 orchestrator 质量（plan 质量、任务描述保真度——呼应 B2 的 context 发散问题）。
- **适用边界**：官方明确划界——多 agent 适合"read-heavy、可并行"的研究型任务；**不适合**写多读少的紧密耦合任务（代码库级工程），此时错误复合与上下文不一致的代价超过并行收益。这条边界恰好是对 Cognition 一文的回应。

---

## C. 综合观察（供后续研究引用）

1. **显式编排回归**：几乎所有主流框架的"第二代"设计（LangGraph、AutoGen v0.4、CrewAI Flow、AgentScope v2）都把控制流从"框架/群聊涌现"收回到"开发者显式结构 + 模型在受限决策点自主"，与 Anthropic workflows-vs-agents 的主张一致。
2. **状态是新的分水岭**：框架差异越来越体现在状态管理（LangGraph checkpoint、ADK Session 服务、Agents SDK Session、AgentScope v2 中间件），而非编排原语本身。
3. **多 agent 之争尚未定论，但边界在收敛**：Cognition（反多 agent，写密集场景）与 Anthropic（挺多 agent，读密集可并行场景）实际主张兼容——共识是"上下文一致性是多 agent 的第一风险，并行只适合无副作用子任务"。
4. **认知架构是下一个竞争层**：Harrison Chase 指出编排原语已同质化，长期记忆/任务队列/子 agent 隔离等"认知结构"成为差异点；HumanLayer 则反向主张最小因子化——两者的张力本身是值得研究的设计光谱。

## 参考资料汇总

- LangGraph: https://docs.langchain.com/oss/python/langgraph/overview
- AutoGen: https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/quickstart.html
- CrewAI: https://docs.crewai.com/concepts/crews / https://docs.crewai.com/concepts/flows
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- Google ADK: https://adk.dev/get-started/
- AgentScope: https://github.com/agentscope-ai/agentscope / https://doc.agentscope.io/
- smolagents: https://huggingface.co/docs/smolagents/index / https://huggingface.co/blog/smolagents
- Anthropic Building Effective Agents: https://www.anthropic.com/research/building-effective-agents
- Cognition Don't Build Multi-Agents: https://cognition.ai/blog/dont-build-multi-agents
- HumanLayer 12-Factor Agents: https://github.com/HumanLayer/12-factor-agents
- Harrison Chase Cognitive Architecture: https://blog.langchain.com/towards-a-cognitive-architecture-for-agents/
- Anthropic Multi-Agent Research System: https://www.anthropic.com/engineering/built-multi-agent-research-system
