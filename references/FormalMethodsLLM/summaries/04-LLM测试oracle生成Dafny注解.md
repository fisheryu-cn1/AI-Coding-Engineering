---
title: "Automatic Generation of Formal Specification and Verification Annotations Using LLMs and Test Oracles"
source_pdf: "04-Faria-Dafny_Annotations_Test_Oracles_v1.pdf"
arxiv_id: "2601.12845"
arxiv_version: "v1"
authors:
  - "João Pascoal Faria"
  - "Emanuel Trigo"
  - "Vinicius Honorato"
  - "Rui Abreu"
year: 2026
venue: "arXiv"
type: "内容索引"
generated_at: "2026-08-25"
summary_version: "1.0"
---

# 论文摘要：LLM 测试 oracle 自动生成 Dafny 注解（波尔图大学）

## 1. 适用场景

- 当你要**用 LLM 为 Dafny（或其它 design-by-contract 验证语言）自动生成全套注解**——preconditions、postconditions、loop invariants、辅助 ghost predicates/functions、proof helpers（assertions/lemmas）——而非只做 loop invariant 推断时，读这篇。
- 当你要设计 **"LLM 生成 + 机器可查 oracle 验证"闭环**（generate–check–repair–minimize），用强 oracle 抑制 LLM 幻觉、只接受通过形式验证的产物时，读其 §1 与 Fig 1 的双 oracle 方案。
- 当你要论证**测试断言能否当规约 oracle 用**（测试驱动 vs mutation 测试 vs 属性驱动的规约校验之争），或需要"负向测试检测过强后置/过弱前置"的机制时，读其 §6.4 与 §8.2。
- 当你要做**形式验证工具的 IDE 集成与可用性评估**（VSCode 插件、SUS 问卷、交叉实验设计）时，读其 §7。

> 锚点：Abstract; §1 Introduction; §2 Program Verification in Dafny; §4 Prompt Engineering; §6 Experimental Results; §7 IDE Integration; §8 Related Work

## 2. 主要观点与方案

- **问题定位**：Dafny 等验证工具已把验证过程高度自动化，但写注解（pre/postconditions、loop invariants、辅助谓词，以及补偿自动证明器局限的 lemmas/assertions 等 proof helpers）仍需大量专业人力，是形式方法普及的主要障碍；LLM 有望卸下这副担子（§1; §2）。
- **数据集 TESTDAFNY110**：110 个 Dafny 程序的复合数据集——子集 A 取 MBPP-DFY-153 精炼出的 85 个循环程序、子集 B 取前作 LOOPINV100 的 15 个、子集 C 新写 10 个降低训练暴露风险；全部配**静态检查的 assert 测试断言**使其可作 test oracle（§3; Table 1）。56% 的程序需要 proof helpers 才能验证通过（§4）。
- **LLM 与 test oracle 的分工协作机制（核心）**：输入是"剥离全部注解的常规代码 + 注释里的自然语言规约 + 带静态断言的测试方法"，走 **guess–check–repair–minimize** 四步闭环（Fig 1; §5.2）——
  - **LLM 只负责"猜"**：用 Direct prompt（Appendix A.1，few-shot，含语法守则与规约/不变式编写指南）一次性插入全部五类注解，不改实现代码；
  - **Oracle 1 = Dafny verifier（Z3）**：机器判定验证成败并产出结构化错误信息，是"验证 oracle"；
  - **Oracle 2 = 测试断言（静态 test oracle）**：测试方法里的 assert 由 verifier **只用方法 pre/postconditions、忽略方法体**地静态检查，等价于编译期 specification-level oracle——专门暴露"验证能过但规约过弱/错误"的缺陷（如不完整 postcondition）（§2; Fig 2; §6.4）；
  - **repair 反馈回路**：失败则最多 9 轮 Repair prompt（Appendix A.2），回灌 verifier 错误信息 + 常见修复策略目录（序列性质断言、递归函数非递归后置、{:fuel}、测试内辅助断言等），并带反作弊护栏：禁止 `assume`、禁止 `decreases *` 关终止检查、禁止删测试；
  - **oracle 级联**直接编码进 repair prompt：test assertions 为 postconditions 提供 oracle，postconditions 又为 loop invariants 提供 oracle，嵌套循环中外层不变式为内层提供 oracle（Appendix A.2 hint 1）；
  - **minimization**：repair 会累积冗余 proof helpers，用 LCS 对齐找 delta、自底向上由外向内逐段试删，仅当验证成功且验证时间保持才保留删除（Appendix B）。
- **多模型并行组合**：每次尝试同时跑 Claude Opus 4.5（T=0.5）与 GPT-5.2（R=Low），按 (i) 语法有效 → (ii) 过 verifier → (iii) LOC 更少 → (iv) 验证更快 的优先级选优（§5.2）。
- **负向测试兜底**：对过强 postcondition/过弱 precondition 这类验证通过但规约错的边缘情况，用 `//@invalid`（预期失败的负向测试语句）逐个取消注释重跑 verifier，验证成功即报错并携错误消息重试 LLM；4 个此类程序全部修复（§6.4; Fig 9）。
- **难度归因（logistic regression）**：以程序结构特征（LOC L、注解行数 A、proof-helper 注解数 H）+ 模型配置为因子的逻辑回归显示，成功概率随 H 下降最陡——**proof helpers 对当前 LLM 是不成比例的难度来源**，超过标准规约元素（§6.3; §6.5 RQ4）。
- **防污染论证**：老模型 GPT-4（知识截止早于数据来源仓库）与新模型差距和 LiveBench 一致；子数据集归属对成功无显著效应，说明结果主要反映结构复杂度而非训练暴露（§6.1; §6.3; §6.6）。
- **与前人工作的差异**：相比 AutoSpec（属性驱动）、SpecGen（人工评估语义充分性）、Lu et al. 的 mutation 测试法，本文用**常规测试方法 + 静态检查断言作语义 oracle**，并对齐开发者既有工作流；相比 Laurel/DAISY 只做 assertion 发现且无迭代修复，本文把 proof helper 生成纳入端到端迭代修复（§8.2; §8.3）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| 总成功率（多模型 Claude Opus 4.5+GPT-5.2，repair prompting） | repair@8 = 98.2%（108/110），平均仅 2 次尝试；未解的 2 题为 FastModularExponentiation、PrimeFactorization（手工解分别需 4、10 条 lemmas） | §6.1; §6.5 RQ1 |
| 多模型 repair 曲线 | r@5 = 94.5%，r@10 = 98.2% | Table 2; Fig 5 |
| 多模型 direct prompting | pass@1 = 50.9%，pass@5 = 57.3%，额外 LOC 仅 7.9% | Table 2; Fig 4 |
| 单模型最佳平衡（Claude Opus 4.5 T=0.5，repair） | r@5 = 90.0%，r@10 = 96.4%，平均 4.41¢ 与 15.8 s /API 调用 | Table 2; §6.1 |
| 成本/速度极值（repair 策略） | 最低成本 DeepSeek-V3.2 0.07¢/调用；最快 GPT-5.2 R=None 9.1 s/调用 | Table 2; §6.1 |
| Dafny verifier 验证耗时 | 平均 9.7 s/任务（剔除超时案例后 1.9 s） | §6.1 |
| repair 解膨胀与最小化 | repair 多模型额外 LOC 63.2% → 最小化后 10.6%（移除 58% 注解 LOC，平均 1.4 s/移除行）；GPT-5.2 R=Low 膨胀最重达 153% | Table 2; §6.1; §6.5 RQ3; Appendix B |
| 生成规约质量（vs 专家手工解） | 逻辑等价 96.4%（106/110）；复杂度相当 82.7%（同措辞 10.9%+同语法 10.0%+同语义 61.8%）；不等价 3.6%（1 过强后置 0.9% + 3 过弱前置 2.7%，全部经负向测试+重试修复） | Table 3; §6.4; §6.5 RQ3 |
| test oracle 有效性 | 165 个失败尝试（Claude Opus 4.5，repair）中 7 个为"方法体验证通过但测试断言失败"（弱/缺 postcondition）——测试可靠暴露规约缺陷 | §6.4 |
| 难度回归判别力 | AUC = 0.907（110 程序 × 14 配置 = 1,540 对；单配置 0.80–1.00）；β_L = −0.0735、β_A = −0.0475、β_H = −0.5825，均 p < 0.001 | §6.3; Fig 7 |
| 语法错误率 | GPT-4 达 27%，Claude Opus 4.5 仅 1% | §6.2; Fig 6 |
| 数据污染证据 | GPT-4 pass@5 = 29.1% vs GPT-5.2 R=None 36.4%（差 7.3 pp，与 LiveBench 上的代际差一致）；子数据集因子 χ²(2) = 0.79，p = 0.67（不显著） | §6.1; §6.3; §6.6 |
| 与 Lu et al. 直接对比 | 64 个重叠任务上对方 pass@5 = 87.5%（仅 pre/post），本文多模型 repair@6 = 100%（含 invariants 与 proof helpers 联合生成） | §8.2 |
| 相关基线（相关工作自报） | AutoSpec 79%（251 个 C 程序、5 次内）；SpecGen 72.5%（385 个 Java 程序）；Laurel 56.6%（143 个任务、10 次内）；DAISY 63.2%（单缺失断言）/31.7%（多缺失，506 程序） | §8.2; §8.3 |
| IDE 可用性研究 | 7 名硕士生 × 6 任务（交叉设计）：成功率 85.7%（工具）vs 42.1%（手工）；完成时间 6.2 min vs 11.1 min；SUS 74.6/100 | §7.2 |
| 数据集规模 | 110 程序 = 85（MBPP-DFY-153 精炼）+ 15（LOOPINV100）+ 10（新写）；实现 2,505 LOC、注解 1,211 LOC（其中 proof-helper 注解 188）；56% 程序需 proof helpers | §3; Table 1; §4 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2601.12845（v1，2026-01-19；拟投 Science of Computer Programming） |
| TESTDAFNY110 数据集 + 实验脚本 | https://github.com/joaopascoalfariafeup/testdafny110 |
| Dafny AI Assistant（VSCode 插件） | https://github.com/emantrigo/dafny-plugin（支持 OpenAI/Anthropic/DeepSeek/xAI，含 provider 优先级与透明 failover） |
| Dafny 语言 | https://github.com/dafny-lang/dafny（验证器 v4.11.0，Z3 后端） |
| 前作（本文是其扩展） | Faria/Trigo/Abreu, Automatic generation of loop invariants in Dafny with LLMs, FSEN 2025（LOOPINV100，仅 loop invariants） |
| 关联对比方法 | AutoSpec（CAV 2024）、SpecGen（ICSE 2025）、MutDafny（ICSE 2026）、Laurel（OOPSLA 2025）、DAISY（arXiv:2511.00125）、dafny-annotator（arXiv:2411.15143）、Lu et al. ICFEM 2025 mutation 法 |

## 5. 一句话索引（给 Agent 用）

> 波尔图大学：在 TESTDAFNY110（110 个 Dafny 程序，测试断言静态检查作规约 oracle）上，Claude Opus 4.5+GPT-5.2 多模型 guess–check–repair–minimize 闭环以 repair@8 = 98.2%（平均 2 次尝试）生成全套 pre/postconditions、loop invariants 与 proof helpers——LLM 只猜，Dafny verifier 判验证成败、测试断言揭过弱规约；生成规约 96.4% 与专家逻辑等价；repair 的 63.2% 额外 LOC 经自动 minimization 降至 10.6%；logistic 回归（AUC 0.907）显示 proof helpers 是难度主导（β_H=−0.58）；VSCode 插件可用性 85.7% vs 手工 42.1%（2601.12845 v1，2026-01）。
