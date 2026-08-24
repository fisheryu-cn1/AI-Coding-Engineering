# harness 与冯诺依曼架构的类别关系、业内评价与替代架构路线（[D2]）

> 日期：2026-08-21；话题标签 [D2]（§1 含 [D1] 源码依据；§5 与 D1/D3 交叉）
> 来源：①类别关系映射出自本项目对 pi 源码的逐层研读（工作推进日志第 27 场续 5，一手）；②业内评价与替代路线来自 2026-08-21 联网检索（二手，标注出处；观点类内容区分证据强度）。
> 用途：为"LLM 为核心组件的软件系统"提供体系结构层的类比定位、类比的有效性边界、以及替代设计路线的谱系——子问题 A（系统构成）的架构学背景材料。

---

## 1. 类别关系映射（源码级依据）

核心论断：**harness 与冯诺依曼机不是类比修辞，而是"受限资源上的调度"这一共同问题的两组同构解**——harness 设计时即在借用 OS 概念（缓存、中断、懒加载），映射可逐条落到源码：

| 冯诺依曼/OS | agent harness | 源码/研读依据（pi 本地仓库） |
|---|---|---|
| CPU 控制单元（取指译码） | LLM——下一 token 分布即指令选择；"继续写/发工具调用/停止"是同一条件分布上的三类选择 | `packages/agent/src/agent-loop.ts` 双层循环；stopReason 同源 |
| RAM/寄存器 | 上下文窗口 | 上下文组装三要素 |
| 高速缓存（TTL、寻址约束） | KV cache——5min TTL、**前缀位置寻址**（内容相同位置不同即失效） | `core/cache-stats.ts`、`packages/ai/src/types.ts:595` |
| 磁盘/外存 | 文件系统、git、知识库 | — |
| 内存管理（工作集/换页） | 压缩与微压缩——E≪W 前提下的工作集管理 | 综合报告 §8.4 |
| I/O 指令与外设 | 工具调用（只读=信息补充；写类=状态变换） | — |
| **中断 + 中断安全点** | steering 队列 + turn 边界 drain（blocker 连终答后仍可触发新一轮） | `agent-loop.ts` 注入点；omp advisor 三档投递 |
| 固件/内核镜像 | system prompt（含 AGENTS.md 注入段）——相对稳定前缀 | `core/system-prompt.ts` 八股 |
| 按需加载的共享库 | skills 懒加载（目录常驻、read 取全文、双通道调用） | `harness/skills.ts` |
| 总线 | harness 的消息队列与事件流（单写者模式：引擎 emit、壳落账） | `agent.ts` processEvents |

计算能力层的定位（对应图灵机而非冯诺依曼）：裸 LLM（定长精度 transformer）表达力有上界（Merrill & Sabharwal：⊆ TC⁰）；**agent 框架（无界循环 + 外部存储/工具）才是恢复图灵等价的那层**。最接近的图灵式抽象是持久图灵机（Persistent Turing Machine，Goldin/Wegner 交互机器谱系）：状态跨步持久、流式输入输出——agent = 以 LLM 为概率性转移函数的 PTM。

## 2. 类比的业内评价（检索，2026-08-21）

**正面谱系**：Karpathy 2023 年"LLM OS"类比（LLM=CPU、context=RAM、工具=外设、agent 框架=进程）→ 2025-06 演讲 [Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) 升级为"LLM 兼具公用设施/晶圆厂/操作系统三重属性"、agent 基础设施类比 1960s 分时系统、预计需约十年达到 OS 级成熟度。学术工程化：**AIOS**（Rutgers，LLM 代理操作系统——调度/资源分配）、**MemGPT**（虚拟上下文管理）、[Towards an Agent Operating System](https://arxiv.org/html/2607.25076v1)（版本控制与安全区）。

**三条主要批评**（要点）：

1. **隐喻不稳定**：Karpathy 自己在 CPU/OS/主机/晶圆厂之间滑动——说明类比是说明性的而非严格的体系结构（[HN 讨论](https://news.ycombinator.com/item?id=44314423)等社区评论）。
2. **冯诺依曼瓶颈被倒置复制**：经典冯诺依曼假设"计算贵、存储便宜"；LLM 恰好相反——上下文窗口（"RAM"）是最稀缺资源（[arXiv 2505.05794](https://arxiv.org/html/2505.05794v1) 及相关评论）。这是对我们 E≪W 推导（综合报告 §8.4）的独立印证。
3. **"把历史倒进上下文不是记忆"**：OS 类比在持久记忆管理上失效——真正的 OS 有完善的进程内存管理，agent 的"记忆"（会话恢复/压缩/检索）至今是补丁集合（本项目 notes/08/09 的设计正是针对此缺口的工程化）。

**评价小结**：类比在**资源调度面**（缓存/中断/懒加载/分层存储）生产性强且与源码事实吻合；在**控制语义面**（转移概率性、无真抢占式多道程序设计）失效。引用时应限定在调度面。

## 3. 主流设计意见谱系（"这种架构思路是否合理"）

| 立场 | 代表 | 主张 | 与本研究的关系 |
|---|---|---|---|
| 简单优先/workflow 派 | [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) | workflow（预定义代码路径编排 LLM）优先于 agent（LLM 自主决定路径）；能用最简单方案就不加自主性 | 即范式决策树 Q4 的静态分解分支；kb-app 是其实例（决策密度=节点内） |
| 单代理 + 上下文工程派 | [Cognition: Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) | 多代理两大失败根因：上下文不能共享（传话游戏）+ 过早拆解；"context engineering"取代 prompt engineering | 与我们的两因素模型（因素 2）同构；对照分析 2-2 的基线纪律（多角色主张先赢过多采样）与之呼应 |
| 审慎多代理派 | Anthropic 多代理研究系统 + [LangChain 综合](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems) | 读密集可并行、写密集慎用；角色/终止规范 + 独立验证器就位才上 MAS | 决策树 Q5 四前置检查同构（MAST FC1/FC3 数字） |
| 黑板折中派 | [arXiv 2510.01285](https://arxiv.org/abs/2510.01285)、[2507.01701](https://arxiv.org/abs/2507.01701)、[Google Research](https://research.google/pubs/blackboard-multi-agent-systems-for-information-discovery-in-data-science/) | 全局共享结构化状态对象替代有损消息传递，解"传话游戏" | **本研究的"跨阶段靠文档"就是黑板思想的文档形态**（意见卡/待确认卡/清单=黑板条目）——未引用该谱系而独立收敛，互证 |

## 4. 与 harness 思路不同但具备理论合理性的架构路线

1. **黑板架构（blackboard，1970s 专家系统谱系复兴）**：控制流不归任何单一循环，多个知识源围绕共享黑板竞相贡献；LLM 版把"中心 agent + 共享结构化状态"作为消息传递与单代理两极的中间形态。理论合理性：解耦控制与状态、天然容纳异质贡献者。
2. **主动推理/自由能（active inference，Friston 谱系）**：以内在的自由能最小化驱动取代外部 reward——生成模型 + 期望自由能驱动的策略选择（[The Missing Reward, arXiv 2508.05619](https://arxiv.org/html/2508.05619v1)；[FEP 与神经语言模型](https://ceur-ws.org/Vol-3923/Paper_3.pdf)）。理论合理性：感知-行动统一的变分原理；工程成熟度尚低（社区存疑：[r/RL 讨论](https://www.reddit.com/r/reinforcementlearning/comments/1fbu536/any_successful_story_of_active_inference_free/)）。**与本研究的接口**：上一轮讨论中"工具调用≈期望信息增益超过内化成本的行为规律"与自由能最小化形式同构（预期惊奇最小化）。
3. **workflow/代码编排（LLM 退居节点内）**：控制流完全归确定性代码，LLM 只在节点内做受限决策——本研究源项目 kb-app 的范式；与 harness（LLM 全局决策）是决策密度谱系的两端（决策树第三刻度：节点内/衔接处/全局）。
4. **倒置形态（LLM 作为子程序）**：传统程序按需调用模型（"Software 3.0"的一部分）——模型不是核心组件而是库函数；适用面窄但工程确定性最高。
5. **形式谱系**：POMDP（通用骨架）、语言模型程序=马尔可夫链（Parr/Friston 团队，可靠性界——与 pass^k 实践直接对接）、ASM（harness 语义规约）、PTM（交互式图灵侧抽象）——见日志第 27 场续 5 的讨论记录。

**谱系总评**：这些路线与 harness 不是互斥选型而是**控制流归属 × 状态管理位置**二维空间中的不同区域（即决策树的两维框架）；黑板改"状态位置"（共享外置），workflow 改"控制归属"（代码），主动推理改"驱动信号"（内在目标）。harness 路线（LLM 全局决策 + 会话内状态）只是该空间中工程上先跑通的一格。

## 5. 对本研究的输入

1. §1 映射表 + §2 批评第 2 条（冯诺依曼假设倒置）为综合报告 §8.4 的 E≪W 推导提供独立外部印证；
2. §3 表末行：本项目"文档传递式协同"与黑板谱系的独立收敛，可作为对照分析增补或 V1 总纲"多轮归并"章的理论参照（登记，不即行）；
3. 类比使用纪律：**限定调度面**——本报告及后续行文引用"harness≈OS"时不应外推到控制语义（转移概率性无 OS 级抢占/隔离保证）。

## 6. 出处清单

一手：pi 本地仓库源码（§1 列）；综合报告 §8.4；日志第 27 场续 5。二手（检索时点 2026-08-21）：Karpathy [LLM OS/2025 演讲](https://www.youtube.com/watch?v=LCEmiRjPEtQ)、[AIOS→MemGPT 综述](https://builder.aws.com/content/2eojjD2E7TBgPFJmB2FGAtrSSBh/the-rise-of-the-llm-os-from-aios-to-memgpt-and-beyond)、[arXiv 2505.05794](https://arxiv.org/html/2505.05794v1)、[Anthropic](https://www.anthropic.com/engineering/building-effective-agents)、[Cognition](https://cognition.com/blog/dont-build-multi-agents)、[LangChain](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems)、黑板（[2510.01285](https://arxiv.org/abs/2510.01285)/[2507.01701](https://arxiv.org/abs/2507.01701)/[Google](https://research.google/pubs/blackboard-multi-agent-systems-for-information-discovery-in-data-science/)）、主动推理（[2508.05619](https://arxiv.org/html/2508.05619v1)/[CEUR](https://ceur-ws.org/Vol-3923/Paper_3.pdf)）。观点类内容证据强度为"观点/专家"级，已逐条标注。
