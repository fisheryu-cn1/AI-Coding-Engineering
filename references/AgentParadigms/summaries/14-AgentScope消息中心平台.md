---
title: "AgentScope: A Flexible yet Robust Multi-Agent Platform"
source_pdf: "14-Gao-AgentScope_v2.pdf"
arxiv_id: "2402.14034"
arxiv_version: "v2"
authors:
  - "Dawei Gao"
  - "Zitao Li"
  - "Xuchen Pan"
  - "Weirui Kuang"
  - "Zhijian Ma"
  - "Bingchen Qian"
year: 2024
venue: "arXiv"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：AgentScope——消息中心式多智能体平台（v1 论文）

## 1. 适用场景

- 要从零设计或选型一个**消息为中心**（一切交互皆消息，消息可序列化、可跨进程传递）的多 agent 平台时，读这篇拿完整架构参照（核心原语、三层架构、控制流原语）。
- 要为 LLM 应用设计**分层容错**（重试 / 规则修正 / 可定制 handler / agent 级自评 / 日志兜底）或对抗 LLM 输出格式错误时，读 §4 的四级错误分类与五层机制。
- 要把单机 agent 原型**低成本迁移到分布式**（跨进程/跨机部署、自动并行），或做多模态数据的 URL 化传输（消息只带 URL、按需加载）时，读 §8 与 §5。
- 要给无 Python 经验的用户提供**零代码搭建** agent 应用的工作站（DAG 拖拽 → JSON 直跑或编译成 Python）时，读 §3.4。
- 追踪 AgentScope v1→v2 演进（2025 年重构为 ReActAgent 单核 + 中间件）时，本文是 v1 架构原点。

> 锚点：§1 Introduction; §2.1 Basic Concepts in AgentScope; §3 High Usability; §4 Fault-Tolerant Mechanisms; §5 Multi-Modal Applications; §8 Actor-based Distributed Framework

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

多 agent 应用开发面临四类挑战：① 多 agent 场景要求平台同时兼顾 versatility（差异化配置、SOP/动态工作流、一对一/广播通信）与 handiness；② LLM 幻觉与指令遵循不稳定，单个未处理错误会在系统内级联传播（"aberrations are tinderboxes"）；③ 多模态数据、工具调用、外部知识（RAG）的系统级支持缺乏通用平台接口；④ 分布式部署（agent 分属不同组织、跑在不同机器）需要专业分布式编程与调优经验。AgentScope 以消息交换为核心通信机制逐一应对。

### 2.2 核心概念与三层架构（§2.1 Basic Concepts in AgentScope; §2.2 Architecture of AgentScope）

- 四个贯穿全平台的概念（§2.1）：**Message**——Python dict，必填 name/content、可选 url（指向多模态数据），自动生成 UUID+时间戳保证可追溯；**Agent**——reply（输入消息产出响应）与 observe（只处理不回复）双接口；**Workflow**——agent 执行与消息交换的有序序列，支持非 DAG 结构与并行；**Service functions vs Tools**——前者是返回 ServiceResponse 的功能 API，后者是带功能描述与预置参数的"加工后"服务函数（因 LLM 不能可靠理解 API 细节、更不能代填 API key 等参数）。
- 三层架构 + 用户交互（§2.2）：utility layer（模型 API 调用、服务函数等底层操作，内置自动重试）→ manager and wrapper layer（资源与 API 服务管理、可定制容错接口）→ agent layer（工作流与消息编程接口）；用户交互面含带注记终端、Web UI、一键把命令行应用变图形界面的 Gradio 接口（`as_studio application.py`）与拖拽零代码工作站。

### 2.3 易用性设计（§3 High Usability）

- **§3.1 Syntactic Sugar for Multi-Agent Workflows**：Pipeline 抽象把 sequential、if-else、switch、while-loop、for-loop 等消息传递模式封装为可复用组件（函数式与面向对象双风格）；MsgHub 广播机制让组内新消息自动扩散给所有参与者，支持运行时 hub.add/delete/broadcast。
- **§3.2 Resource-Rich Environment**：内置服务函数（web search、DB query、代码执行等，ServiceFactory 一键转 OpenAI 兼容 JSON）；8 种预置 agent 模板（UserAgent、DialogAgent、DictDialogAgent、ReActAgent、ProgrammerAgent、TextToImageAgent、RpcUserAgent、RpcDialogAgent，Table 1）。
- **§3.3 Multi-Agent Oriented Demonstration Interfaces**：agent 颜色/图标区分与"第一人称视角"体验；监控模块跟踪模型/API 用量与财务成本，可设预算阈值自动告警。
- **§3.4 Towards Graphical Application Development**：拖拽工作站把应用表达为 DAG，节点分六类（model、service/tool、agent、pipeline、message、copy）；ASDiGraph 数据结构支持两条执行路线——JSON 直接按拓扑序运行（direct-run），或把 JSON 编译为完整 Python 脚本（to-Python compiler）。
- **§3.5 Automatic Prompt Tuning**：用户只给自然语言简述即可自动生成系统提示（auto_sys_prompt），支持手动/按上下文自动更新提示；in-context learning 一键开关，提供 random、similar questions、similar answers 等示范匹配策略并可自定义。

### 2.4 分级容错机制（§4 Fault-Tolerant Mechanisms）

先做四级错误分类——accessibility errors（服务暂时不可达）、rule-resolvable errors（如 JSON 缺右括号）、model-resolvable errors（格式对但内容错：参数/语义/编程错误）、unresolvable errors（如 API key 过期）——再对应五层机制：① API 与模型 wrapper 的自动重试（可设最大次数）；② 规则修正工具（补全括号、从字符串提取 JSON），不重调 LLM 故省时省钱；③ 可定制 fault handler（parse_func / fault_handler / max_retries 三参数）；④ agent 级容错（借 memory、msghub 做 self-critique、pairwise critique、human-augmented critique 查语义错误）；⑤ 定制日志系统兜底（新增 CHAT 日志级别记录 agent 间对话 + WebUI 监控）。

### 2.5 多模态支持（§5 Multi-Modal Applications）

多模态数据生命周期三段解耦：生成（本地文件或 DALL-E、GPT-4V 等模型 wrapper）→ 存储（file manager 本地保存并返回 URL）→ 传输（消息只附带 URL，接收方按需加载）。URL 附带消息的三点收益：减小消息体避免网络带宽引发的错误/延迟；文本与多模态内容可被下游并行/分别处理；便于终端与 Web UI 呈现。

### 2.6 工具使用（§6 Tool Usage; §6.1 Customization for Experienced Developers）

基于 ReAct 算法 + service toolkit 组件，四步流程：Function Preparation（注册函数并预置参数，自动生成 JSON schema 描述）→ Instruction Preparation（工具指令与调用格式模板：JSON 放 Markdown 代码块，含 thought/speak/function 字段）→ Iterative Reasoning（LLM 分析局面、决策下一步）→ Iterative Acting（解析响应、执行函数；响应解析错误与函数执行错误携详细信息回传 LLM 纠正，其余运行时错误交开发者）。§6.1 面向熟练开发者：JSON schema 描述可直接喂 OpenAI/DashScope 等原生函数调用 API；提供 Markdown 块、JSON 块、可组合多标签内容三类响应解析器来自定义调用格式。

### 2.7 RAG 支持（§7 Agents with Retrieval-Augmented Generation）

针对多 agent 场景重复建索引的浪费，提供：一站式配置（单个 .json 文件收纳全部 RAG 配置，天然兼容 Workstation）；knowledge bank（最小管理单元为 RAG object，带唯一 knowledge_id，持久化供复用）；RAG agent（如 LlamaIndexAgent，继承 RAGAgentBase）可同时加载多个 RAG 对象、运行时插入/删除/替换知识（含监控目录自动更新）、按重要度/可信度定制多对象检索结果的融合权重、并可重组查询多次检索。

### 2.8 Actor 分布式框架（§8 Actor-based Distributed Framework）

先摆明两组路线取舍：集中式 vs 去中心化协调（前者易理解易调试但中心节点脆弱、难扩展）、静态 vs 动态工作流（类比早期 TensorFlow 静态图 vs PyTorch 动态图：静态可全图优化但必须执行前定图，动态灵活牺牲优化）。AgentScope 选 actor 模型取得三点：无需静态图的自动并行优化；把分布式工作流编程简化为单个 Python 函数内的过程式风格；本地/分布式混合部署（开发者无需区分）。引入 **placeholder 消息**解决 actor 间传值未就绪问题——主进程不阻塞继续执行，仅当控制流（if-else/循环）确需真实值时临时阻塞取回（Example 9）。一键部署：agent server 在远程机接收请求并自动初始化 agent 实例；AgentScope Studio 作为统一消息中心汇聚展示所有分布式 agent 消息，并支持远程开关 agent server。

### 2.9 示例应用（§9 Signature Applications of AgentScope）

§9.1 基本对话（UserAgent+DialogAgent；兼容 OpenAI chat/embedding/DALL-E、HuggingFace、ModelScope 及 FastChat/vllm/Flask 本地模型）；§9.2 群聊与 @mention（filter_agents 识别被点名 agent）；§9.3 狼人杀游戏（6 玩家两阵营，约一百行代码，夜/昼阶段靠 msghub 组织）；§9.4 分布式部署两模式——单机多进程（`.to_dist()`）与多机多进程（RpcAgentServerLauncher + 指定 host/port），本地↔分布式仅改 agent 配置、工作流代码零修改；§9.5 用多个 LlamaIndexAgent 构建 AgentScope copilot；§9.6 SearcherAgent+多 AnswererAgent 并行的网页检索问答；§9.7 ReActAgent + DAIL-SQL + query_sqlite 服务做 NL2SQL；§9.8 Workstation 拖拽实现（含静态检查规则）。

### 2.10 相关工作、结论与演进注记（§10 Related Works; §11 Conclusion）

- 定位（§10）：与语言 agent 框架（Transformers-Agents、LangChain/LangServe/LangSmith、AutoGPT、ModelScope-Agent）和多 agent 框架（AutoGen、MetaGPT、AGENTS、OpenAgents、ChatDev、CAMEL、AgentSims）对比，AgentScope 的差异化卖点是易用 + 容错 + actor 分布式。
- 结论与未来工作（§11）：以消息交换与分布式机制降低多 agent 开发门槛；未来方向包括更深入的 RAG 集成、随任务需求演化的自适应通信协议与交互模态。
- 演进注记（非论文内容）：2025 年 AgentScope 2.0 重构为 ReActAgent 单核 + 中间件注入上下文/记忆/RAG，v1 的显式 Pipeline 降为兼容层——本文即该演进的起点。

> 锚点：§2.1 Basic Concepts; §2.2 Architecture; §3.1–§3.5; §4; §5; §6; §7; §8; §9.1–§9.8; §10; §11

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 消息原语设计 | Msg 为 Python dict：2 必填字段（name、content）+ 1 可选（url 指向多模态数据），UUID+时间戳唯一标识 | §2.1 Basic Concepts |
| 内置 agent 模板 | 8 种：UserAgent、DialogAgent、DictDialogAgent、ReActAgent、ProgrammerAgent、TextToImageAgent、RpcUserAgent、RpcDialogAgent | §3.2 Table 1 |
| 控制流原语 | Pipeline 共 5 类：sequential、if-else、switch、while-loop、for-loop；另有 MsgHub 广播（支持运行时增删参与者） | §3.1 |
| 容错覆盖 | 4 级错误分类（accessibility / rule-resolvable / model-resolvable / unresolvable）× 5 层机制（自动重试、规则修正、自定义 handler、agent 级 critique、日志） | §4 |
| 零代码工作站 | 应用表达为 DAG，6 类节点（model、service/tool、agent、pipeline、message、copy），支持 JSON 直跑与编译为 Python 两条路线 | §3.4 |
| 代码规模 | 狼人杀 6 玩家角色扮演游戏用约一百行代码实现 | §9.3 |
| 本地↔分布式迁移成本 | 仅改 agent 配置（`.to_dist()` / RpcAgentServerLauncher），工作流代码零修改 | §9.4 |
| 模型后端兼容 | OpenAI chat/embedding/DALL-E、HuggingFace、ModelScope、FastChat/vllm/Flask 本地模型 | §9.1 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2402.14034 |
| 代码（论文发布地址） | https://github.com/modelscope/agentscope （仓库现迁移至 agentscope-ai 组织：https://github.com/agentscope-ai/agentscope） |
| 示例代码与附录 | 狼人杀完整代码与运行对话历史（论文 Appendix A/B 的 standalone conversation 与 werewolf 示例）在上述仓库 |
| 关联 | 本目录 13（AutoGen 会话式编排路线对照）；AgentScope 2.0 演进对照见目录内工业框架对比材料 |

## 5. 一句话索引（给 Agent 用）

> 选"消息中心"式多智能体平台时读这篇：AgentScope（Alibaba，arXiv:2402.14034v2）以 Msg 消息体（name/content/url）+ Agent（reply/observe）+ Pipeline/MsgHub 为核心原语、三层架构（utility / manager-wrapper / agent）承载全部能力：四级错误分类×五层容错、多模态 URL 解耦传输、ReAct+service toolkit 工具链、knowledge bank 共享 RAG 索引、actor 模型实现本地↔分布式零改工作流迁移（.to_dist()），狼人杀 6 玩家仅约一百行代码——是"一切交互皆消息"架构的代表性实现与 AgentScope v1→v2 演进起点。
