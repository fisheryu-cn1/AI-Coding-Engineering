---
title: "Event-B Agent: Towards LLM Agent for Formal Model Synthesis and Repair"
source_pdf: "02-Wang-Event_B_Agent_v1.pdf"
arxiv_id: "2605.17475"
arxiv_version: "v1"
authors:
  - "Hongshu Wang"
  - "Xinyue Zuo"
  - "Yuhan Sun"
  - "Qin Li"
  - "Yamine Ait Ameur"
  - "Jin Song Dong"
year: 2026
venue: "FSE 2026（arXiv 2026-05）"
type: "设计参考 + 内容索引"
generated_at: "2026-08-25"
summary_version: "1.0"
---

# 论文摘要：Event-B Agent 形式模型合成与修复（NUS / ECNU / IRIT）

## 1. 适用场景

- 当你要设计**"自然语言需求 → 可验证形式模型"的 LLM 端到端流水线**（模型合成与证明修复闭环，而非孤立的单点任务）时，读这篇——它给出首个把 refinement 开发、模型构造与证明推导协同起来的 correct-by-construction 框架。
- 当你要**自动化"分离点位置决策"**——即需求应被分配到哪个抽象层级/refinement 层级、层与层之间用什么 gluing invariants 串联——时，读其 §4.2 Refinement Strategy Planning，这是 LLM 规划 refinement 切分方案的直接参考。
- 当你评估**model checking vs theorem proving 在 LLM 形式化中的角色分工**（有界反例引导修复 + 无界证明保证），或需要**形式模型质量度量体系**（PDR / RC / RF + Refinement PDR）时，读其 §4.4 与 §5.1。

> 锚点：Abstract; §1 Introduction; §4 Methodology; §4.2 Refinement Strategy Planning; §4.4 Model & Proof Repair; §5 Evaluation

## 2. 主要观点与方案

- **问题定位**：现有 LLM 形式化工作多为孤立任务——只做定理证明（模型固定）、或只用 model checking 验证模型合成（PAT-Agent），而有界模型检查的"无反例"只保证 bound 内正确。论文把形式开发形式化为**模型与证明工件的联合状态空间** (M0, π0) ⇝ … ⇝ (Mn, πn)，每步可同时修订模型与证明，健全性由可靠证明系统下的 πt 保证；并支持跨 refinement 层级的增量开发（§1; §2.2）。
- **动机示例**：最小值搜索系统中，GPT-5 / Cursor / PAT-Agent 的模型各有缺陷（Cursor 初始化即违规、GPT-5 的 stop 事件 guard 过弱、PAT-Agent 模型只在 minRanF=3 单例下"看起来正确"）；Event-B Agent 通过"抽象模型只证 FUN-1 + 具体模型细化"的 refinement 结构消除这些缺陷（§2.1; Fig. 1–2）。
- **总体架构（neurosymbolic）**：语义任务（refinement 规划、模型合成、修复决策）交给专职 LLM，确定性组件（Event-B 编译器、model checker、SMT solver、theorem prover、模式匹配、原子修复函数执行）保证可靠性；三阶段循环：Refinement Strategy Planning → Model Synthesis → Model & Proof Repair，逐层推进直到全部需求处理完（§4.1; Fig. 4）。
- **Refinement Strategy Planning（分离点位置决策自动化的关键机制）**：规划 LLM 把需求全集 REQ **划分为 n 个不相交子集 REQ_Mi（REQ = ∪REQ_Mi）**——REQ_M1 是初始抽象模型的需求，REQ_Mi 是第 i 层新增需求，即**由 LLM 决定每条需求落在哪个 refinement 层级**（抽象边界/分离点的位置）；同时在层 i−1 与 i 之间**提出 gluing invariants 集合 Ig_i**（先自然语言、模型合成阶段形式化），故第 i 层实际引入 REQ_Mi ∪ Ig_i，Ig_i 用于保持前 i−1 层已满足的全部需求；逐层正确性按 Eq. 2 归纳定义（§4.2.3）。gluing invariants 因 LLM 生成无正确性保证，采用两步验证：(1) model checker 反例检查与矛盾检测，(2) 先于其他证明尝试与 gluing invariants 相关的证明，全部通过才被接受进模型（§4.2.2）。最小值搜索示例中策略为 2 步：REQ_M1={FUN-1}，REQ_M2={FUN-2..FUN-6}，Ig_2={inv_g2}（§4.2.3）。
- **Model Synthesis**：用编码 Event-B 文法（Fig. 3）的 **JSON schema 做模式引导生成**（语言无关、可迁移到其他规格语言），再用"编译错误回传 LLM"的合成–修复循环保证 well-formedness（类型正确）；合成细化模型时以上一层抽象模型为上下文，refinement 健全性由 refinement PO 保证（§4.3）。
- **Model & Proof Repair**：(1) 先经 ProB 有界模型检查找 invariant 违例（LLM 建议 bound），反例轨迹回传修复模型（§4.4.1; Fig. 5）；(2) 再用定理证明覆盖全部执行——PO 由自动 prover/SMT solver 尝试 discharge，失败时进入修复引导：**repair rules recommendation** 从证明状态（M、π、PO 类型、修复历史 R(M,π)）模式匹配出 7 类修复规则（Table 2，经验归纳、非穷尽，无匹配则回退默认规则）（§4.4.2）；**fix strategy decision LLM** 被限制只能从原子修复函数库中选择执行，函数分 4 类：模型修改 / 证明修改 / 模型–证明联合修改 / 信息检索（§4.4.3）。**修复健全性**由验证管线而非规则保证：修复序列仅在合并效果 discharge 目标 PO 时被接受，每次模型修改后重放全部证明（§4.4.4）。
- **实验设置**：27 个形式系统（Abrial 经典案例 + 真实系统 EB4EB 等），按需求数分 Simple（3–8）/ Medium（9–13）/ Complex（14–24）三档各 9 个，生成模型平均 PO 数为 89.22 / 173.7 / 284.3；backbone 为 GPT-5（medium reasoning，2025-08-07 版）；基线为 LLM+auto provers（Rodin PP + CVC4/Z3）、Cursor、改造到 Event-B 的 PAT-Agent；度量 PDR（一致性）、RC（需求覆盖）、RF（需求满足），并用 Refinement PDR 验证"refinement 正确性假设"（§5.1）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| 一致性 PDR（总体） | 97.86%（基线：LLM+auto provers 89.20%、Cursor 90.07%、PAT-Agent 95.56%）；各复杂度分档均 >97.0%（Cursor 波动 12.5%） | §5.2; Table 3 |
| 需求覆盖 RC（总体） | 97.13%，超次优 4.63% | §5.2; Table 3 |
| 需求满足 RF（总体） | 93.79%，超次优 18.01% | §5.2; Table 3 |
| RF/RC 比值 | 0.97（基线 0.75 / 0.77 / 0.82） | §5.2 |
| Refinement PDR（总体） | 92.56%（完整版）vs 67.69%（仅 refinement 消融）；Complex 档 82.13% vs 46.53% | §5.3; Table 5 |
| 消融（总体 PDR/RC/RF） | 无组件 0.9559/0.8363/0.7701；仅 refinement 0.9650/0.8955/0.8350；仅修复引导 0.9693/0.9494/0.8665；完整 0.9786/0.9713/0.9379 | §5.3; Table 4 |
| 效率（总体） | 每系统平均 74.45 分钟、57.33 次 LLM 调用、1,657,865.15 tokens；其中规划 1.20 min/1 次/5,348.19 tokens，合成 25.07 min/13.59 次，修复 43.71 min/42.74 次 | §5.4; Table 6 |
| 单 PO 平均 discharge 时间 | 0.24 分钟（分档 0.18 / 0.30 / 0.22，全部 <0.30） | §5.4 |
| refinement 过程中指标演化 | PDR 全程维持 97.86–98.50%；RC 从抽象层 31.19% 升至最终 97.13%，RF 从 30.24% 升至 93.79% | §5.5; Fig. 6 |
| 原子修复函数分布（成功贡献） | 模型修改 38.36%、证明修改 33.62%、联合修改 18.97%、信息检索 9.10% | §5.5; Fig. 7 |
| 评估规模 | 27 个形式系统，平均 182.41 个 PO | §1; §5.1 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2605.17475 |
| 论文 DOI（FSE 2026, Proc. ACM Softw. Eng.） | https://doi.org/10.1145/3808218 |
| 代码 | https://github.com/HongshuW/EventB_Agent |
| 数据与工件 | Zenodo: https://doi.org/10.5281/zenodo.19642103 |
| 工具链 | Rodin IDE（Event-B IDE，含 PP prover / SMT 集成）、ProB（model checker）、CVC4 / Z3 |
| 基线 | PAT-Agent（ASE 2025，arXiv:2509.23675）；Cursor（通用编码 agent） |
| 背景教材 | Abrial, *Modeling in Event-B*（2010），数据集经典案例来源 |

## 5. 一句话索引（给 Agent 用）

> NUS/ECNU/IRIT：Event-B Agent——LLM 端到端从自然语言需求合成并修复 Event-B 形式模型，三阶段（refinement 策略规划→schema 引导合成→模型&证明修复）；LLM 在规划阶段把需求划分为 n 个不相交子集分配到各 refinement 层级并用 gluing invariants 串联（分离点位置决策自动化），修复限原子函数、健全性由 PO 验证管线保证。27 个系统（平均 182.41 PO）上 PDR 97.86%（最强基线 95.56%）、RC 97.13%（+4.63%）、RF 93.79%（+18.01%）、RF/RC=0.97；每系统平均 74.45 分钟、单 PO 平均 0.24 分钟（FSE 2026，arXiv 2605.17475v1）。
