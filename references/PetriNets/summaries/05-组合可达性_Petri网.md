# 论文摘要：Reachability via Compositionality in Petri Nets

> **原论文标题**：Reachability via Compositionality in Petri nets
> **完整 PDF 文件名**：`Reachability via Compositionality in Petri nets.pdf`
> 作者 / 年份：Paweł Sobociński, Owen Stephens（ECS, University of Southampton, UK）；2014，arXiv:1303.1399v2 [cs.LO] 21 Apr 2014
> 摘要类型：研究论文 / 形式化方法 + 工具
> 生成日期：2026-08-12

## 1. 适用场景

- 在 **1-bounded（1-safe）Petri 网** 上做 **reachability 检查** 时，发现全局状态空间枚举指数爆炸——本文给出组合性 + 弱等价的替代方案。
- 需要**自动分解 / 验证 / 形式化评估**典型基准（如 bounded buffer Bₙ、计数网 Tₙ、哲学家 Pₕₙ）的工具实现思路。
- 当工作流 / 协议 / 通信系统呈现**重复 / 模块化结构**时，本文的 memoisation 策略能给出线性时间 / 大幅加速。
- 把过程代数 / 范畴论（prop、Span(Graph)）与 net 验证打通：bisimilarity / 弱等价同余性。

> 锚点：Abstract；§1 Introduction。

## 2. 主要观点与方案

### 2.1 核心思想：把结构分解 + 边界交互作为可达性凭证

- 许多异步系统是**正则结构**：可视为多个相同通信组件的合成；组件间通信只需少量边界信息。
- 1-bounded 网的 reachability 本身是 **PSPACE-complete**（Cheng–Esparza–Palsberg 1993），但若能找到"良好分解"，可达性可几乎线性解决。
- 使用 **PNB（Petri Nets with Boundaries）代数** 表达"沿边界组合"（`;`）与"非交互并行"（`⊗`）两种操作；要求 step semantics（而非 interleaving）以保持组合性。

> 锚点：§1 Introduction（Remark 1—Bₙ 局部上可独立推进）。

### 2.2 理论路径：PNB → NFA → 弱闭包 → 最小 DFA

- 组件 PNB → NFA：状态 = reachable markings（每个 place 1-1 对应 0/1），转移标签为左右 boundary 交互的 α/β 二进制串。
- 关键定义：`▲min(A)` = ε-closure + 最小化后的 DFA，其中 ε = 0^k/0^l，对应"无边界交互"的内部动作。
- 弱等价（weak language equivalence）对 PNB 的 `;` 与 `⊗` 是同余 → 组合前先最小化组件，组合后再最小化，安全无损。
- **核心定理 9**（正确性）：trans(−) 递归定义的最小 DFA 与"全局网直接构造的最小 DFA" 同构。

> 锚点：§1.1–§1.4（Definition 2、Theorem 4 / Theorem 7 / Theorem 9）；§1.3 Weak closure and minimisation。

### 2.3 自动化：分解算法 + Haskell 实现 + 备忘录

- 分解算法（Decomposer）：① 优先寻找"删去某 transition 即断开"的分解，多解时选最平衡；② 否则寻找"删去某 place 即断开"的分解；二次多项式时间。
- 不行时再 greedy 选最小边界 / 任意组合。
- 关键技术：NFA 闭包 + 最小化（Brzozowski 1962）；用 **ROBDD** 编码 transition 关系（二进制标签 → X 子集），避免状态爆炸。
- 实现：Haskell 工具，源代码 + 实验数据可下载（[11] / ICALP 2013 artifact）。

> 锚点：§2 Implementation；§2.1 Decomposer；§2.2 NFA ε-closure and minimisation。

### 2.4 实验结果：Bₙ、Tₙ、Pₕₙ

- 缓冲网 Bₙ（右分解）：n=65536 时 0.228s 完成最小 DFA 构造（图 8a）—— 实际所需 firing sequence 长度 2.15×10⁹。
- 平衡 / 左分解分别给出 74.7s / 失败。
- 计数网 Tₙ（balanced 分解）：n=16 时 25.0s（图 8b）。
- 哲学家 Pₕₙ：固定点出现在 PₕRow₃（最小 DFA 有 10 状态），n=1024 时 3.7s 仍保持稳定，远优于传统状态空间。

> 锚点：§2.3 Experimental Results；Figure 8 / 12 / 13 / 15。

### 2.5 与其他状态空间缩减方法对比

- Unfolding（McMillan 1995）：构造完整 prefix，类比于我们的"先构造分解，再 traverse"。
- Symmetry reduction（Starke 1991, Schmidt 2000）：与 memoisation 思想类似——每类等价结构只翻译一次。
- 本文：关注的是"组件间交互的边界协议"，而非"等价状态合并"——便于"为什么不可达"做局部归因。

> 锚点：§3 Related Work。

## 3. 达到的效果

| 度量 / 现象 | 结果 | 锚点 |
|---|---|---|
| 实验——Bₙ 右分解 n=65536 | 0.228s | 图 8a |
| 实验——Bₙ 平衡分解 n=256 | 74.7s | 图 8a |
| 实验——Tₙ 平衡分解 n=16 | 25.0s | 图 8b |
| 实验——Pₕₙ n=1024（deadlock 检查） | 3.7s（固定点 PₕRow₃） | 图 12b |
| 复杂度下界 | 1-bounded 网 reachability PSPACE-complete | 引 [4] Cheng et al. 1993 |
| 理论保证 | Theorem 4 (Compositionality) + Theorem 7 (Weak semantics) + Theorem 9 (Correctness) | §1.1–§1.4 |
| 适用范围 | 重复 / 模块化 / 树形 / 环形结构良好 | §2.3 讨论 |
| 局限 | 稠密网（clique）边界膨胀 → NFA 不可控 | §2.3 末段 |

> 锚点：Theorem 4 / 7 / 9；Figure 8 / 12；§3 Related Work。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/1303.1399v2 |
| 工具实现 | Penrose（Sobociński 组 Haskell 实现） |
| 关联论文 | CONCUR 2010《Representations of Petri net interactions》（Sobociński）；CONCUR 2011 Bruni–Melgratti–Montanari |
| 关联代数 | Span(Graph)（Katis–Sabadini–Walters, AMAST 1997）；LMCS 9(3):16, 2013 |
| 复杂度标杆 | 1-safe 网 PSPACE-complete（Cheng–Esparza–Palsberg, FSTTCS 1993） |
| BDD | Brzozowski 1962 最小化；ROBDD 编码技术 |
| 关联方法 | Unfolding（McMillan 1995，Esparza–Römer–Vogler 2002）；Symmetry reduction（Starke 1991，Schmidt 2000） |
| 关联论文（Bₙ） | 后续扩展覆盖 coverability、参数化 verify |

> 锚点：References（[1]–[19]）。

## 5. 一句话索引（给 Agent 用）

> 当需要对**模块化 / 重复结构**的 1-bounded Petri 网做 reachability 检查时，**用 PNB 分解 + ROBDD 编码 NFA + 弱等价最小化 + memoisation** 的路线（本文 / Penrose）：它把指数长度 firing sequence 化为近线性时间，并能局部归因"为什么不可达"——这是顺序状态空间方法和 CRT 验证的工业级替代。
