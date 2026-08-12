# 论文摘要：Petri Nets: Properties, Analysis and Applications（Murata 综述）

> **原论文标题**：Petri Nets: Properties, Analysis and Applications
> **完整 PDF 文件名**：`PetriNets基础论文.pdf`
> 作者 / 年份：Tadao Murata, Fellow, IEEE（University of Illinois at Chicago）；1989，Proceedings of the IEEE, Vol. 77, No. 4, pp. 541–580
> 摘要类型：Invited tutorial-review / 形式化方法的不可替代综述
> 生成日期：2026-08-12

## 1. 适用场景

- 任何需要**"Petri 网一站式综述"**的场景：选形式化建模工具、写并发系统论文、做工作流 / 协议 / 制造 / 离散事件相关的工程汇报。
- 在 **RAG / 文档检索** 任务中作为 Petri 网概念的"权威定义源"——本综述是 IEEE 历史上引用最广的 Petri 网教程。
- 当需要构造状态方程、矩阵方程来做**自动分析**（simulation / 形式化验证）时，本文的符号无出其右。
- 给 AI Agent 提供"Petri 网能做什么 / 不能做什么"的快速判断依据（tradeoff between modeling generality and analysis capability）。

> 锚点：Abstract；§1 Introduction。

## 2. 主要观点与方案

### 2.1 Petri 网作为并发 / 异步 / 分布式 / 随机系统的普适工具

- Petri 网起源于 Carl Adam Petri 1962 博士论文；1970–1980s 形成欧洲 / 北美两大研究中心（MIT、欧洲 Adv. Course 系列）。
- 主要应用：性能评估、通信协议、分布式软件、分布式数据库、并发 / 并行程序、柔性制造、离散事件系统、多处理器存储系统、数据流计算、容错系统、可编程逻辑 / VLSI、异步电路、操作系统、办公信息系统、形式语言、逻辑程序。
- 关键 trade-off：模型越通用，分析越难——通用性换来代价。

> 锚点：§1 Introduction（历史、应用领域、相关文献）。

### 2.2 形式化定义与触发规则

- Petri 网 5 元组：PN = (P, T, F, W, M₀)。P, T 有限集，弧权 W ∈ ℕ⁺，初标记 M₀ : P → ℕ。
- 触发规则（§2）：① 每个 input place 至少 w(p, t) tokens 时 t enabled；② 可选择 firing；③ firing 移除 input 弧上 tokens，增加 output 弧上 tokens。
- 有限容量（finite capacity）网：增加 strict transition rule，output place 容量限制；可用**互补位变换**（complementary-place transformation）转为无限容量网。
- 典型语义对照：places = 条件 / 缓冲 / 状态；transitions = 事件 / 任务 / 命题子句（Table 1）。

> 锚点：§II Transition Enabling and Firing；Table 1（典型解释）；Table 2（形式化定义）。

### 2.3 行为性质（marking-dependent）与三类分析方法

- 行为性质：reachability、coverability、boundedness（k-bounded / safe）、liveness、reversibility、home state、persistence、synchronic distance、fairness。
- 三种分析方法：① 覆盖树（coverability tree）/ 可达图；② 关联矩阵方程 + 不变量；③ 化简（reduction）技术。
- 关联矩阵 C：m × n 矩阵，元素 C[p, t] = w(t, p) − w(p, t)；状态方程 M = M₀ + C · σ，其中 σ 为 firing count vector。
- P-invariants：Y > 0 s.t. Yᵀ · M = Yᵀ · M₀（守恒量）。T-invariants：X > 0 s.t. C · X = 0（可重复 firing 序列）。

> 锚点：§IV Behavioral and Marking-Dependent Properties；§V Three Methods of Analysis；§V-C Matrix-Equation Approach。

### 2.4 子类与最受关注的标记图（marked graphs）

- 普通 Petri 网 → 子类：① State Machine（SM）；② Marked Graphs（MG）；③ Free-choice nets；④ Extended Free-choice nets；⑤ Simple nets；⑥ Extended Simple nets。
- **Marked graphs** 每个 place 恰好一个 input transition + 一个 output transition。可用线性代数完全判定 liveness 与 boundedness，且 closed under 多种网操作；是并发系统最易分析的模型。
- 化简规则：删除 redundancy / 合并等价节点 / 删除死 transition，目的是缩小网同时保留性质。

> 锚点：§VI Subclasses of Petri Nets and Their Analyses；§VII In-Depth Analysis and Synthesis of Marked Graphs。

### 2.5 结构性质（marking-independent）

- Structural liveness / boundedness：与初标记无关。
- 充分条件：presence of live / bounded T-invariants、不变量约束。
- Siphon / Trap：影响 liveness 的结构识别。

> 锚点：§VIII Structural Properties。

### 2.6 时间 / 随机 / 高层 Petri 网

- Timed Petri Nets：每个 transition 关联 firing time / delay。
- Stochastic Petri Nets (SPN)：fire rate 服从指数分布 → 性能评估（吞吐、响应时间、利用率）。
- High-Level Petri Nets（predicate-transition / colored Petri nets）：token 携带个体化信息，提高模型紧凑性。
- 应用：SPN 用于多处理器系统、柔性制造系统；逻辑程序与 Petri 网等价（Kowalski / Petri 双边关系）。

> 锚点：§IX Introduction to Timed, Stochastic, and High-Level Petri Nets。

## 3. 达到的效果

| 度量 / 性质 | 描述 | 锚点 |
|---|---|---|
| 行为性质 | reachability、coverability、boundedness、liveness、reversibility、persistence、synchronic distance、fairness | §IV |
| 分析方法 | 覆盖树、矩阵方程、化简技术 三种 | §V |
| 子类可分析性 | Marked Graphs 可用线性代数判定 | §VII |
| 结构性质 | structural liveness / boundedness、siphon、trap | §VIII |
| 适用扩展 | Timed / Stochastic / High-level / Logic Programs | §IX |
| 工程工具 | 列出 1986 时主流 Petri 网工具集 | §X（前部） |
| 工程覆盖 | 200+ 引用、35 万 PDF page views 的高被引综述 | 全文 |

> 锚点：§IV–§IX；References；Index。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文出处 | Proceedings of the IEEE, Vol. 77, No. 4, April 1989, pp. 541–580 |
| 早期文献 | Peterson 1981《Petri Net Theory and the Modeling of Systems》；[10] 第一本 Petri 网书 |
| 综述 / 高级系列 | Best 1987（free-choice hiatus）；Desel & Esparza 1995《Free Choice Petri Nets》；Reisig 1985《Petri Nets》 |
| 工具 | 1986 时主流工具列表（[163]–[170]），含 GreatSPN、ARP、PROT、ExSpect 等 |
| 进一步阅读 | [26] 1987 综合书目 2074 entries；Petri Net Newsletter（[27]） |
| 关联会议 | Int. Workshop on Petri Nets and Performance Models（1985、1987 起） |
| 时间 / 随机扩展 | Molloy 1982 SPN 论文；Marsan et al. 1984 GSPN；Ajmone Marsan 1990 综述 |
| 高层 Petri 网 | Genrich & Lautenbach 1981（Predicate-Transition Nets）；Jensen 1981–1992（Colored Petri Nets） |

> 锚点：References（[1]–[170]）；§X Concluding Remarks。

## 5. 一句话索引（给 Agent 用）

> 当需要"Petri 网是什么、能做什么、怎么分析、有什么子类、怎么扩展"的全景答案时，**直接引用 Murata 1989 这篇 IEEE 综述**——它是 Petri 网领域的"百科全书"，覆盖了行为 / 结构性质、三种分析方法、子类（特别是 marked graphs）、时间 / 随机 / 高层扩展，并给出 1986 年工具清单与 170+ 引用索引。
