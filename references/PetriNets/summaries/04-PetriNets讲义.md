# 论文摘要：Petri Nets Lecture Notes（Esparza 讲义）

> **原论文标题**：Petri Nets — Lecture Notes
> **完整 PDF 文件名**：`PNSkript.pdf`
> 作者 / 年份：Prof. Javier Esparza（TU München）；2022-04-25 版
> 摘要类型：教学讲义 / 形式化方法参考
> 生成日期：2026-08-12

## 1. 适用场景

- **学界 / 研究生课程**：作为 Petri 网基础与决策过程的入门讲义，涵盖语法、语义、模型、分析技术、判定 / 半判定过程以及具有高效决策的子类。
- 在 **RAG / 长上下文检索** 中作为 Petri 网"概念最小集"——比 Murata 综述更紧凑、比教材更严谨。
- 实现 **reachability / coverability / boundedness / liveness** 判定算法时，需要找到严格的递归 / 不动点形式。
- 给 LLM / Agent 提供"Petri 网分析算法的现代教材模板"——含 BDD / 符号实现提示与复杂度边界。

> 锚点：Abstract / 封面信息；Chapter 1 Basic definitions。

## 2. 主要观点与方案

### 2.1 预备知识：复杂度类与归约

- 课时 1 系统复习 P, NP, PSPACE, NPSPACE, EXPTIME, EXPSPACE、归约、硬性、完备性。
- **Savitch 定理**：NPSPACE = PSPACE（用于后文中"判定过程可放进 PSPACE" 的论证）。
- 序列、关系、向量、矩阵的基础符号铺垫——为 Petri 网的矩阵方程、状态方程、S-invariant / T-invariant 提供线性代数工具。

> 锚点：§1.1 Preliminaries（Numbers、Relations、Sequences、Vectors and matrices、Complexity Classes、Reductions）。

### 2.2 Part I：语法、语义、模型

- **Petri 网定义**：N = (S, T, F)，S 为 places（圆圈），T 为 transitions（方块），F ⊆ (S × T) ∪ (T × S) 为流关系；标记 M : S → ℕ。
- 触发规则：t 在 marking M 下 enabled 当且仅当 •t ⊆ M（每个 input place 至少一个 token）；fire 后 M 通过减去 •t 增加 t• 得 M'。
- **Step semantics**（并发 firing）：多个独立 transition 可同时触发；与 interleaving 区别于保持因果 / 并发结构。
- 多重集（multiset）形式的标记；firing sequence、firing vector、序列触发语义。

> 锚点：Chapter 1 Basic definitions；§1.2 Syntax；§1.3 Semantics（firing rules）。Chapter 2 Modelling with Petri nets（典型建模模式）。

### 2.3 Part II：分析技术

- **Chapter 3 Decision procedures**（判定过程）：针对 bounded Petri 网的决策程序——boundedness、coverability、reachability（全网无界不再可判定）。
  - 算法 1：**Reachability graph**（状态空间枚举）—— 可判定 Boundedness、Coverability、Reachability 问题（bounded 情形）。
  - 算法 2：**Coverability tree**（用 ω 表示"任意大"以确保终止）—— 同样可判定 Coverability / Boundedness。
- **Chapter 4 Semi-decision procedures**（半判定过程）：
  - 4.1 线性方程组 / 线性规划：状态方程 M = M₀ + C · σ 判定 structural boundedness。
  - 4.2 S-invariants（P-invariants）：Yᵀ · M = Yᵀ · M₀ 不变 → 守恒 / 有界性。
  - 4.3 T-invariants：X > 0 s.t. C · X = 0 → repeatable occurrence 序列。
  - 4.4 Siphons / Traps：影响 liveness 的结构识别。
  - 4.5 反向 firing / 反向 reachability。
- **Chapter 5 Petri net classes with efficient decision procedures**：具有高效判定过程的子类——例如 marked graphs（用线性代数判 liveness / boundedness）、free-choice nets、communication-free nets。

> 锚点：Chapter 3 Decision procedures（§3.1 Bounded nets/Reachability graph、Coverability tree）；Chapter 4 Semi-decision procedures；Chapter 5 Petri net classes with efficient decision procedures。

### 2.4 复杂度与判定性边界

- **Boundedness** for general Petri nets：decidable（§3）。
- **Reachability** for general Petri nets：decidable（Mayr 1981 / Kosaraju 1982 重要结论，§3 引用）。
- **Liveness** 在一般网下：从 boundedness + liveness 联合判 lateral 路径。
- **PSPACE** 边界：1-safe 网 Reachability PSPACE-complete（Cheng–Esparza–Palsberg 1993）。
- **EXPSPACE** 边界：free-choice Petri nets Reachability EXPSPACE-hard。

> 锚点：Chapter 3 结论；Chapter 5（高效子类）。

## 3. 达到的效果

| 度量 / 性质 | 描述 | 锚点 |
|---|---|---|
| 决策程序 | 有界 Petri 网：boundedness、coverability、reachability 全部可判定 | Chapter 3 |
| 半决策程序 | 结构性质 + S/T invariant + siphon / trap + 反向可达 | Chapter 4 |
| 高效子类 | marked graphs、free-choice、communication-free 等用线性代数或多项式时间判 | Chapter 5 |
| 复杂度 | 1-safe 网 PSPACE-complete；free-choice EXPSPACE-hard | 引 Cheng et al. 1993 |
| 教学结构 | 2 部分 / 5 章，覆盖语法 + 5 种分析技术 + 复杂度分级 | 全文 |
| 实现提示 | 半判定程序常用于工业工具；BDD 编码提及 | Chapter 4 / 5 |

> 锚点：Chapter 3–5 章节合集。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 讲义出处 | TU München 课程（Esparza 现任教职前版本）；约 2022 版课程资料 |
| 关联教材 | Murata 1989《Petri Nets: Properties, Analysis and Applications》；Reisig《Petri Nets》；Desel & Esparza《Free Choice Petri Nets》 |
| 判定性证明 | Mayr 1981、Kosaraju 1982（Reachability）、Reutenauer 1990（线性代数路径） |
| BDD / 符号实现 | BDD 章节（Chapter 4 末） |
| 工具 | INA（Integrated Net Analyzer）、LoLA、Petri Net Kernel、TAPAAL、GreatSPN |
| 课程关联 | 与作者已发表论文互通（e.g., LTL Model Checking via Net Unfoldings） |

> 锚点：Chapter 3–5 References；Esparza 主页研究主线。

## 5. 一句话索引（给 Agent 用）

> 当需要 Petri 网的形式化起点 + 决策 / 半决策过程 + 复杂度分级 + 高效子类的**教程式参考**时，**直接用 Esparza 2022 讲义**——它把语法、step semantics、reachability graph、coverability tree、S/T invariant、siphon / trap、marked graphs / free-choice 子类按"判定 vs 半判定 vs 高效"三档精确分层，是 Petri 网分析算法实现的"教科书模板"。
