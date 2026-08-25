# 方向二：资料归档

按"设计范式 / 软件工程原理 / 案例与系统"分类。每条资料附一句话摘要与用途标注。

## 本仓库内既有成果（直接素材）

| 资料 | 路径 | 与本方向的关系 |
|---|---|---|
| SDD 框架对比 | `research/sdd/OpenSpec_Speckit_Superpowers_OMO框架对比.md` | 子问题 B 的直接基础：规范作为人机共同事实来源 |
| Spring 架构与 AI 自动化 | `research/architecture/Spring架构与AI自动化演进策略分析.md` | 子问题 B 的实证：隐式架构对 LLM 的理解障碍 |
| 上下文工程系列 | `research/context-engineering/` | 子问题 A 的素材：知识图谱/向量库与 LLM 的结合模式 |
| 形式化方法分析 | `research/theory/图代数与任务拆分安全性分析.md` | 组件组合安全性的形式化视角 |
| 信息容量评估 | `research/theory/信息容量评估与关键信息提取.md` | 中间产物信息量评估的工具 |
| kb-app 设计文档链 | `design/kb-app/`（01–17 号文档） | 完整的"需求→详设→评审"产物链，回溯式案例分析素材 |
| AI 代码生成上下文控制框架 | `design/AI代码生成上下文控制_设计分析框架.md` | 中间产物设计的已有思考 |

## references 库内相关论文（2026-08-17 梳理）

按摘要索引（`references/*/summaries/INDEX.md`）筛选的对方向二有用的存量论文：

| 论文 | 位置 | 对方向二的用途 |
|---|---|---|
| Formal Architecture Descriptors | `references/ContextEngineering/10` | 形式化架构描述符作为编码 agent 的导航原语——**中间产物规范命题（02 第 4 节）的直接同类工作**：中间产物的设计标准是"可机检性"的实例证据 |
| Codified Context | `references/ContextEngineering/08` | 复杂代码库中形式化上下文基础设施——"结构化工件承载人机交互"（Hassan 工件支柱）的工程实现参照 |
| Harness-Native Software Engineering | `references/ContextEngineering/11` | 编码 agent 的 8 函数控制面——"代码退居衔接层"论点的极端化实例（控制面收敛为少数原语） |
| Agent Harness Evolution | `references/AIOS/10` | harness 工程过程实证（hyper-churn、质量回归、Agentic QA 缺口）——子问题 B"工程过程层"（Hassan 四支柱）的现实注脚 |
| TraceDev | `references/CodeGraph/12` | 需求→代码的多 agent 追溯框架——中间产物链（需求/设计/任务工件）在 MAS 中的契约化实例 |
| Specification-Based Code–Text–Code | `references/CodeGraph/05` | 规约驱动的"代码-文本-代码"再工程循环——"规范作为人机共同事实来源"（子问题 B）的形态变体 |
| RAG → Multi-Agent Systems 综述 | `references/KnowledgeEngineering/04` | RAG 到 MAS 的演进谱系——子问题 A"LLM 与传统组件结合方式"的光谱补充 |
| SWE-bench / SWE-agent / Agentless | `references/ContextEngineering/12–15` | 已在学术梳理中引用的基准与 scaffold 原文（12 号为 SWE-bench 本体） |

## 外部资料（已收集）

| 资料 | 路径 | 一句话摘要与用途 |
|---|---|---|
| Agent 设计范式学术梳理（2026-08-16） | `materials/agent范式-学术梳理.md` | 20+ 篇文献（综述/ReAct 等经典范式/多智能体/失败模式/benchmark 边界）的结构化梳理，附范式选型决策框架——子问题 A 的理论框架素材 |
| 工业框架设计对比（2026-08-17） | `materials/agent框架-工业设计对比.md` | 7 个主流框架（LangGraph/AutoGen/CrewAI/OpenAI Agents SDK/ADK/AgentScope/smolagents）按核心抽象/控制流/状态管理/适用场景对比 + 5 篇设计观点文章（Anthropic、Cognition、12-Factor 等）——"框架把什么固化、留给用户什么"的证据基础 |
| 软件工程原理与 LLM 系统（2026-08-17） | `materials/软件工程原理与LLM系统.md` | 经典原理（Parnas/Brooks/CBSE/形式化规约）与 "LLM 作为组件"新文献（prompt-as-spec、evals、metamorphic testing、neuro-symbolic）的对照梳理——"prompt 作为规约"类比的理论基础 |
| harness 与冯诺依曼架构类别关系（2026-08-21） | `materials/harness与冯诺依曼架构类别关系.md` | 源码级映射表（LLM=控制单元/上下文=RAM/KV cache=带TTL缓存/steering=中断/skills=懒加载库）＋业内评价（Karpathy 谱系、冯诺依曼瓶颈倒置批评）＋设计意见四派＋替代架构五路线（黑板/主动推理/workflow/PTM 形式谱系）——子问题 A 的架构学定位；E≪W 的独立外部印证 |

> 2026-08-17：上表及学术梳理中引用的 36 篇 arXiv 论文全文已入库 `references/AgentParadigms/`（26 篇）与 `references/SEforLLM/`（10 篇），下载校验见 `references/arxiv_2026-08_manifest.md`；全部摘要已按 `design/kb-app/06-摘要构建与命名规范.md` 完成**全文精读级**重写（frontmatter + 五段 + §锚点 + 精读标记，summary_version 3.0），索引见各主题 `summaries/INDEX.md`。精读核实修正了 4 处转述误差（MAST v3 占比、More Agents 无 COVER/CONF、SAS/MAS 级联精确数字、18 号框架名单与结论），已回填学术梳理材料。

## 外部资料（待收集）

- [x] ~~Agent 设计范式综述类论文（ReAct、plan-and-execute、multi-agent 的原始论文与对比综述）~~（2026-08-16 完成，见上表）
- [ ] 工作框架文档精读：LangChain/LangGraph（图编排范式）、阿里 AgentScope（多 agent 范式）——实际项目主力框架，范式对比需映射到二者
- [ ] 商用 AI 编码工具的能力边界资料：Claude Code、Qoder、Codebuddy（方向一"工具亮点识别"的输入，[D1+D2] 共享素材）
- [x] ~~LLM 软件工程（SE for LLM / LLM for SE）的近期综述，如 agentic software engineering 方向~~（2026-08-16 完成，含 Wang/Liu/Hassan 三篇综述，见上表）
- [ ] 经典软件工程对照：基于构件的软件工程（CBSE）、规约方法、需求工程相关文献
- [ ] 开源 Agent 系统架构案例：LangGraph、AutoGen、CrewAI 等的架构文档（对比已见 `materials/agent框架-工业设计对比.md`）
- [ ] 非常见范式空位扫描（**有界**：限已收 26 篇精读 + 工业对比谱系内，服务研究目的②——候选：计划-执行-验证外循环的标准化、code-as-action 与工具调用混合、级联路由作为默认控制流；发现候选作场景一可选组件，不单独立项）
- [ ] references/ 目录中 AIOS、CodeGraph、ontology 等论文的针对性摘录（AgentParadigms/SEforLLM 两主题已随 2026-08 入库完成初评摘要）

## 归档规范

- 论文/案例读完一篇就在本表登记一行：一句话摘要 + 对本方向哪个子问题有用
- 篇幅较长的摘要单独成文，放在本目录下，文件名带日期前缀
