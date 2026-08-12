# 论文摘要：Petri Nets（Cardoso & Valette 教材）

> **原论文标题**：Petri Nets（Cardoso & Valette 著；翻译自葡语版 *Redes de Petri*）
> **完整 PDF 文件名**：`17173-Cardoso_16468.pdf`
> 作者 / 年份：Janette Cardoso, Robert Valette（University of Toulouse / LAAS）；第 1 版葡语原书 1997，英文修订版 2024（HAL 提交 2025-08-27，hal-05225249）
> 摘要类型：教材 / 形式化建模参考
> 生成日期：2026-08-12

## 1. 适用场景

- 需要**形式化分析并发 / 离散事件系统**（制造、调度、工作流、协议）但找不到"轻量级入门 + 严谨定义"双轨材料时。
- 在 **WFMS / 业务流程建模 / 制造执行系统**领域，作为 Petri 网的入门教材使用：覆盖条件/事件、并行/冲突/同步、资源分配。
- 设计或评审模型的**结构正确性**（liveness、boundedness、reversibility、conservative / repetitive 组件）时，需要找到形式化判据。
- 给业务分析师 / 工程师做"形式化建模 + 仿真 + 性质分析"全栈培训。

> 锚点：Foreword；Preface to the Portuguese Edition；Chapter 1（Vocabulary and concepts）。

## 2. 主要观点与方案

### 2.1 Petri 网作为离散事件系统建模语言

- 离散事件系统（DES）由**事件 / 活动 / 过程**三类概念构成；Petri 网中"places = 条件（局部状态）"、"transitions = 事件"、"tokens = 资源 / 真值 / 数据项"。
- 相比有限状态机（FSM），Petri 网保留**结构信息**：从同一状态的出弧可以明确区分"决策"与"独立事件"；避免组合爆炸 `n^k`。
- 区分 **cooperation**（同步协同）、**competition**（资源互斥）、**pseudo-parallelism**（单处理分时）、**true parallelism**（多处理器同时）。
- 提供了从工艺流程、运输系统、传感器/加工系统到工作流的多类建模实例（§1.5）。

> 锚点：§1.1 Systems and Modeling；§1.2 Basic Notions；§1.3 Finite State Machine；§1.4 Informal Presentation；§1.5 Modeling Interactions Between Processes。

### 2.2 形式化定义与行为 / 结构性质

- 形式化定义：PN = (P, T, F, W, M₀)；P/T 为有限集，弧权 W ∈ ℕ⁺，初标记 M₀ : P → ℕ。
- 行为（marking-dependent）性质：k-bounded（二值 / 1-safe）、Live（quasi-live / live / live marked net）、Reversible。
- 结构（marking-independent）性质：Conservative components / Place invariant；Repetitive components / Transition invariant。
- 五种构造 / 分析方法：覆盖树（coverability tree）、reachability set、P-invariants / T-invariants、reduction rules、simulation。

> 锚点：§2.1 Concepts；§2.4 Properties of the Model；§2.5 Structural Properties；§3 Property Analysis；§3.1 Analysis by Marking Enumeration。

### 2.3 高级 Petri 网：时间 / 数据 / 高层

- Interpreted Petri nets：附加数据 / 条件标注，将网与外部世界（执行体、传感器、决策）绑定。
- High-Level Petri Nets：个体化 token（颜色）、谓词使能、面向复杂工业系统。
- Timed Petri Nets：每个 transition 关联 firing duration，处理性能 / 调度。
- Stochastic Petri Nets：fire rate 服从指数分布 → 性能评估。
- 非经典逻辑 / 混合系统：把连续状态变量与离散事件融合（hybrid systems）。

> 锚点：Chapter 4 Interpreted Nets: data and time；Chapter 5 High-Level Petri Nets；Chapter 6 Petri Nets and the Representation of Time；Chapter 7 Implementation Methods；Chapter 8 Petri Nets, Non-Classical Logics, and Hybrid Systems。

### 2.4 应用领域与教学结构

- 应用：柔性制造、离散事件系统、工作流、通信协议、操作系统、编译器、故障容错、神经网络、形式语言、逻辑程序。
- 教学结构：每章给出 Notes（背景 / 引用）、Exercises（自测题），便于自学。
- 配套工具：第 7 章讨论实现方法（仿真器、状态空间生成器）及 C/E Petri 网、P/T Petri 网对应的执行策略。

> 锚点：§1.1.2 Types of systems；§1.7 Notes；§2.7 Exercises；Chapter 7 Implementation Methods。

## 3. 达到的效果

| 度量 / 性质 | 描述 | 锚点 |
|---|---|---|
| 行为性质 | k-bounded（1-bounded = safe）、live、reversible 的形式化判定 | §2.4 |
| 结构性质 | P-invariants / T-invariants → 一致性 / 守恒性 / 可重复性 | §2.5 |
| 分析方法 | 覆盖树（可判定有界性）、关联矩阵方程、化简技术、仿真 | §3 |
| 子类与权衡 | 标记图（marked graphs）是分析最简单的并发模型 | §3 |
| 扩展能力 | 时间 / 随机 / 高层 / 混合系统：接入性能评估与实际工业 | §4–§8 |
| 教学覆盖 | 8 章 + 形式化定义 + 习题 + 注释，适用于高校课程 | 全文 |

> 锚点：Chapter 2 Definitions；Chapter 3 Property Analysis；Chapter 8 Non-Classical Logics and Hybrid Systems。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 教科书 HAL ID | https://hal.science/hal-05225249v1（Cardoso & Valette, 2024 修订版） |
| 葡语原版 | *Redes de Petri*, Cardoso & Valette, Editora da UFSC, ISBN 85-328-0095-5 |
| 关联工具 | Petri net 仿真器（C/E / P/T 网）、Industrial tools（COSA, Staffware 等参考） |
| 关联标准 | WfMC（Workflow Management Coalition）术语集 |
| 学科基础 | Petri 1962 博士论文；MIT Computation Structures Group 1970–1975；Advances in Petri Nets 系列（Springer） |
| 关联论文 | Murata 1989《Petri Nets: Properties, Analysis and Applications》（IEEE 综述） |

> 锚点：Foreword；Preface；§1.7 Notes；Chapter 8 References。

## 5. 一句话索引（给 Agent 用）

> 当需要"形式化建模 + 并发系统正确性分析"的入门教材（兼覆盖工作流、制造、协议），优先用 Cardoso & Valette 的《Petri Nets》——它把有限状态机的局限、Petri 网的形式化定义、行为 / 结构性质、分析方法、时间与随机扩展一站式讲清，是教科书式的"参考手册"。
