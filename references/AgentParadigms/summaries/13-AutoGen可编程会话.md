---
title: "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"
source_pdf: "13-Wu-AutoGen_v2.pdf"
arxiv_id: "2308.08155"
arxiv_version: "v2"
authors:
  - "Qingyun Wu"
  - "Gagan Bansal"
  - "Jieyu Zhang"
  - "Yiran Wu"
  - "Beibin Li"
  - "Erkang Zhu"
year: 2023
venue: "arXiv"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：AutoGen——基于多智能体会话的 LLM 应用框架

## 1. 适用场景

- 当你要为 LLM 应用挑选**通用多 agent 框架底盘**（可复用 agent 原语 + 可编程会话流，从两人对话到动态群聊）时读这篇。
- 当你要设计**人类介入模式**（human_input_mode=ALWAYS/NEVER、按条件征求输入、人可跳过）并把人作为一等参与者编入多 agent 工作流时。
- 当你想判断"**再加一个专职 agent**"（如 grounding agent 注入常识、safeguard 审查代码）能否以模块化方式修复错误循环或安全风险时。
- 当你要把 AutoGen 与 CAMEL、MetaGPT、BabyAGI、Multi-Agent Debate 等系统按"通用基础设施 / 会话模式 / 可执行代码 / 人类介入"四个维度做选型对比时。
- 当你要决定任务该用多 agent 会话还是单向 pipeline（LangChain、LlamaIndex、Guidance、Semantic Kernel 等）时，Appendix B.1 给出使用准则。
- 当你需要在 MATH、Natural Questions、ALFWorld、OptiGuide、MiniWoB++ 等基准上引用 multi-agent 实现的可对比数字时。

> 锚点：§1 Introduction; §2 The AutoGen Framework; §3 Applications of AutoGen; §4 Discussion; Appendix A Related Work; Appendix B Expanded Discussion。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- 出发点：任务复杂度上升 → 用多 agent 协作放大 LLM agent 能力（引前人证据：多 agent 促发散思维、提升事实性与推理、提供验证）。
- 三个可行性洞察：chat 优化的 LLM（如 GPT-4）能在对话中吸收反馈，agent 间可通过会话互相提供推理、观察、批评与验证；同一 LLM 配不同 prompt/推理设置呈现互补能力，可用多个差异化配置的 agent 模块化组合；LLM 擅长把复杂任务拆成子任务，会话天然承载拆分与整合。
- 两个核心设计问题：(1) 如何设计有能力、可复用、可定制、适合协作的单个 agent；(2) 如何用统一接口容纳广泛的会话模式（单/多轮、不同人类介入模式、静态 vs 动态会话），并允许开发者用自然语言或代码编程 agent 交互。

### 2.2 Conversable Agents（§2.1 Conversable Agents）

- 统一抽象：一切 agent 均为"可对话实体"——基于收发消息维护内部上下文，具备 send / receive / generate_reply 接口，可按编程好的行为模式行动。
- 三类可组合能力后端：1) **LLM**（角色扮演、基于会话史的隐式状态推断、给反馈与吸收反馈、编码，可经新 prompting 技术组合增强）；2) **人类**（human-backed agent 按配置在指定轮次征求输入，可配置频率、条件与跳过）；3) **工具**（执行 LLM 建议的代码或函数调用）。
- 内置类层级：ConversableAgent 为最高层抽象（默认可同时用 LLM、人、工具），AssistantAgent（LLM 后端 AI 助手）与 UserProxyAgent（人/工具后端的用户代理）是两个预配置子类；另提供增强 LLM 推理层（结果缓存、错误处理、消息模板）。

### 2.3 Conversation Programming（§2.2 Conversation Programming）

- 范式定义：把复杂 LLM 工作流统一简化为多 agent 会话。**计算**是会话中心的（agent 动作围绕其参与的会话展开并产生后续消息传递，直至终止条件）；**控制流**是会话驱动的（发给哪个 agent、执行什么计算是 agent 间会话的函数）。
- 设计模式一：统一接口 + **auto-reply 机制**——agent 收到消息即自动调用 generate_reply 并回复发送者，无需额外控制平面；内置基于 LLM 推理、代码/函数执行、人类输入的 reply 函数，也可注册自定义 reply（如回复前先与第三方 agent 商议）。
- 设计模式二：**自然语言与编程语言融合控制**——自然语言控制（系统消息指示纠错重生成、约束输出结构、以 TERMINATE 结束任务）；编程语言控制（终止条件、human_input_mode、最大自动回复数、工具执行逻辑）；以及双向控制转移（代码内发起带控制逻辑的 LLM 推理；LLM function call 切回代码控制）。
- 动态会话两条通用路径：自定义 generate_reply（在当前会话内按消息内容嵌套发起与其他 agent 的会话）与 function calls（LLM 依据会话状态决定调用并向更多 agent 发消息）；GroupChatManager 循环"动态选发言人→收集回复→广播"实现动态群聊。
- 附录 C：AssistantAgent 默认 system message（v0.1.1）即会话编程示范，标注五类 prompting 技术（Role Play、Control Flow、Output Confine、Facilitate Automation、Grounding）；观察 GPT-4 对指令遵循优于 GPT-3.5-turbo，系统设计需为指令未被完美遵循的情形准备异常与容错机制。

### 2.4 六个（+附录 1 个）应用实证（§3 Applications of AutoGen；Appendix D Application Details）

- **A1 数学问题求解**（MATH 数据集，GPT-4，预装 sympy）：场景 1 自主解题直接复用两个内置 agent，对比 AutoGPT、ChatGPT+Plugin(Wolfram Alpha)、ChatGPT+Code Interpreter、LangChain ReAct、Multi-Agent Debate；场景 2 人类在环（仅设 human_input_mode=ALWAYS）；场景 3 多用户协作（student/expert 双 proxy，assistant 经 ask-for-expert 函数调用自动转向专家会话后带回结论）。
- **A2 检索增强代码生成与问答**：Retrieval-augmented Chat 双 agent（User Proxy 扩展 Chroma 向量库、SentenceTransformers/all-MiniLM-L6-v2 检索）；创新点**交互式检索**——检索上下文不含答案时 assistant 回复 UPDATE CONTEXT 触发更多检索而非直接终止；第二个场景演示用最新文档补 GPT-4 训练截止后的 API 知识（FLAML Spark 例）。
- **A3 文本世界决策**（ALFWorld，GPT-3.5-turbo，134 个 unseen 任务，集成 ReAct two-shot prompting）：两 agent 系统（assistant 出计划 + executor 执行并回报观察，动作用 BLEU 相似度对齐合法动作）与 ReAct 持平；新增 grounding agent 在任务开始或 assistant 连续三次重复同一动作时注入常识（"先找到并拿起物体才能检查；先到目标物体处才能使用"），有效跳出错误循环。
- **A4 多 agent 编码**（基于 OptiGuide 供应链优化问答系统重写）：Commander 协调 Writer（写码 + 解读执行结果）与 Safeguard（安全审查，如防信息泄露/恶意代码），通过则用 Python 执行、异常则携日志回传 Writer 重试直至回答或超时；各 agent 记忆隔离防捷径与幻觉。
- **A5 动态群聊**：GroupChatManager 原生支持动态群聊；role-play 式选人 prompt 对比 task-based 选人（后者把角色信息、会话史与下一发言者任务拼进单一 prompt），pilot study 为 12 个手工复杂任务、四 agent 成员（user proxy、engineer、critic、code executor）。
- **A6 会话式国际象棋**：玩家 agent（人 / AI / 混合，可在单局中无缝切换）+ 第三方 board agent 以自定义 reply 解析自然语言着法为 UCI 并校验合法性，非法则回错要求重下；ablation 去掉 board agent 仅靠 prompt 约束时非法着法破坏对局。
- **A7（Appendix D）浏览器在线决策**：MiniWobChat 两 agent（内置 AssistantAgent + 定制 executor 执行浏览器动作并回报 reward/HTML 状态），与专为此基准设计的 RCI 对比。
- 附录 E：BabyAGI / CAMEL / MetaGPT 开箱解数学题的失败样例（MetaGPT 倾向去"开发软件"而不解题；CAMEL 生成的代码无法执行、角色不聚焦解题）。

### 2.5 讨论、使用准则、局限与伦理（§4 Discussion；Appendix B Expanded Discussion；Ethics statement）

- 收益归因（Appendix B）：易用性（内置 agent 开箱即强，A1/A3）；模块化（各 agent 可独立开发、测试、维护，A3–A6）；可编程性（A4 核心代码 430+ 行 → 100 行）；原生人类介入（A1/A2/A5/A6）；协作与对抗式 agent 交互（Safeguard 作为对抗检查者，A4/A6）。
- 使用准则（Appendix B.1）：优先用内置 agent（可先在初始用户消息中加指令提性能而不改系统消息）；从两会话或群聊等简单拓扑起步；优先复用内置 reply 方法；新应用先用 human_input_mode=ALWAYS 调试再转 NEVER；无回环排错需求的单向任务用 LangChain/LlamaIndex/Guidance/Semantic Kernel/Gorilla 或底层推理 API 更合适，也可把外部 agent 包装成 conversable agent、把 LangChain 工具当 agent 的工具后端；推理配置调优可配合 flaml.tune 黑盒优化。
- 未来工作（Appendix B.2）：最优多 agent 工作流设计（哪些任务适合多 agent、给定任务的最优/最省钱工作流）；高能力 agent 构建（CAMEL 失败主因是缺工具/代码执行，说明仅有角色扮演的多会话不足）；规模化下的安全与人类代理（日志、追踪、调试工具；级联失效与利用的 fail-safe；reward hacking 与失控行为；人类监督的合适粒度）。
- 伦理声明：隐私与数据保护、偏见与公平、可问责与透明、信任与依赖、非预期后果（允许 LLM agent 借代码/函数执行改动外部环境——如安装包——有风险，需 safeguard）。
- 定位边界：AutoGen 是通用使能层，不提供正确性保证；工作自述处于早期实验阶段。

### 2.6 相关工作对比（Appendix A Related Work，Table 1）

- 单 agent 系统（AutoGPT、ChatGPT+Code Interpreter/Plugin、LangChain Agents、Transformers Agent）均不支持 agent 间协作；LangChain 即便有多 agent 实现也是绕开 Agents 子包从零写的。
- 多 agent 系统：Multi-Agent Debate（agent 只是 LLM 推理实例、无工具与人类、预定义顺序）、CAMEL（Inception prompting、无原生工具执行、仅静态模式）、BabyAGI（静态模式）、MetaGPT（面向软件开发的专用方案而非通用基础设施）。
- Table 1 四维对比：AutoGen 是唯一同时具备"通用基础设施 ✓ + flexible（静态与动态）会话模式 + 可执行 LLM 代码 + 人类介入（chat/skip）"的系统。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| MATH 整个测试集（5000 题，GPT-4）正确率 | AutoGen 69.48% vs vanilla GPT-4 55.18% | §3 A1; Appendix D |
| MATH 定性评测（2 道 level-5 题，各测 3 次） | AutoGen 3/3 与 2/3；AutoGPT、LangChain ReAct、Multi-Agent Debate 均 0/3 | Appendix D Table 2 |
| 人类在环几何题（3 次尝试） | AutoGen 3/3；ChatGPT+Code Interpreter 与 ChatGPT+Plugin 各 2/3；AutoGPT 0/3 | Appendix D A1 Scenario 2 |
| Natural Questions 问答（GPT-3.5-turbo，F1 与 Recall） | AutoGen 25.88% / 66.65%；去掉交互式检索 22.79% / 62.59%；DPR 基线 15.12% / 58.56% | §3 A2 |
| 交互式检索触发率 | NQ 上约 19.4% 的问题触发 UPDATE CONTEXT（带来额外 LLM 调用） | Appendix D A2 |
| ALFWorld 134 个 unseen 任务平均成功率（GPT-3.5-turbo） | 三 agent 69% vs 两 agent 54%、ReAct 54%（grounding agent 带来 +15 个百分点）；best-of-3 下 77% vs ReAct 66% | §3 A3; Appendix D Table 3 |
| OptiGuide 核心工作流代码量 | 从 430+ 行降到 100 行（约 4x 节省） | §3 A4; Appendix B |
| OptiGuide 用户时间与交互成本 | 平均解题约 1.5 分钟 vs ChatGPT+Code Interpreter 4 分 35 秒（约 3x 节省）；用户交互减少 3.03x–4.88x（五个数据集，含标准差） | §3 A4; Appendix D Table 4 |
| 不安全代码识别 F1（100 个安全/不安全各半的编码任务） | 多 agent 设计 vs 单 agent +8%（GPT-4）、+35%（GPT-3.5-turbo） | §3 A4 |
| 动态群聊 12 任务（GPT-4） | 群聊（role-play 选人）成功 11 个 vs 两 agent 9 个 vs task-based 选人 8 个；平均 LLM 调用数 4.5 vs 6.8 vs 4.0 | §3 A5; Appendix D Table 5–6 |
| MiniWoB++（49 个任务） | MiniWobChat 成功率 52.8% vs RCI 56.4%（低 3.6 个百分点；按每任务 0.1 容差两者各胜同等数量任务） | Appendix D A7 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2308.08155（v2，2023-10-03） |
| 开源框架 | https://github.com/microsoft/autogen（论文以该开源库为实现载体；联系邮箱 auto-gen@outlook.com） |
| 基准 | MATH、Natural Questions、ALFWorld、MiniWoB++、OptiGuide 供应链场景（论文各应用所用） |
| 依赖组件 | Chroma 向量数据库；SentenceTransformers（all-MiniLM-L6-v2 嵌入，A2 检索器） |
| 关联读本 | 本目录 05（ReAct，A3 直接集成其 prompting）、12（MetaGPT，专用多 agent 对比项）、14（AgentScope 消息中心路线） |

## 5. 一句话索引（给 Agent 用）

> 要选通用多 agent 框架或理解"会话即工作流"抽象时读这篇：AutoGen 把一切 agent 统一为可组合 LLM/人/工具的 conversable agent，以"会话编程"（自然语言与代码融合控制 auto-reply 会话流，无额外控制平面）覆盖双人对话到动态群聊；实证含 MATH 全集 69.48%（vanilla GPT-4 55.18%）、ALFWorld 加 grounding agent 54%→69%、OptiGuide 代码 430 行→100 行并省约 3x 用户时间、不安全代码识别 F1 +35%（GPT-3.5-turbo）；定位通用使能层，正确性保证与规模化安全留作开放问题。
