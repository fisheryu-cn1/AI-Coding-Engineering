---
title: "LLM-based Satisfiability Checking of String Requirements by Consistent Data and Checker Generation"
source_pdf: "07-Chen-LLM_Satisfiability_String_Requirements_v1.pdf"
arxiv_id: "2506.16639"
arxiv_version: "v1"
authors:
  - "Boqi Chen"
  - "Aren A. Babikian"
  - "Shuzhao Feng"
  - "Dániel Varró"
  - "Gunter Mussbacher"
year: 2025
venue: "arXiv"
type: "设计参考 + 内容索引"
generated_at: "2026-08-28"
summary_version: "1.0"
---

## 1. 适用场景

- 当你想**直接从自然语言（NL）字符串需求判定 SAT/UNSAT**，而不想人工把需求形式化为 SMT-LIB2 时，读这篇：它给出"LLM 起草结论 + LLM 生成检查器验证结论"的完整混合流水线（§III–§V）。
- 当你在设计"**LLM 生成检查器/验证器**"类系统并需要评估其**语法/语义可靠性**（含 SMT 表达式等价性形式化验证、Python 函数测试法两种度量）时，读这篇：RQ1 的度量设计与 4 个 LLM 对比数据可直接复用（§VI-B）。
- 当你需要为基于需求的测试（requirements-based testing）**自动生成满足需求组合的一致性字符串测试数据**时，读这篇：SAT 判定的副产品即为证据字符串（§II-A、§VII）。

> 锚点：核心方法 §III（总览）+ §IV（Checker 生成器）+ §V（基于 Checker 的验证器）；实验 §VI-A–§VI-D。

## 2. 主要观点与方案

### 2.1 问题动机：形式方法与 LLM 各有短板

- SMT 求解器（Z3、Ostrich 等）可靠且高效，但要求输入已形式化的需求（SMT-LIB2），人工形式化代价高且对非形式化方法专家困难；且理论受限（如嵌套量词、回文类约束难以处理）（§I）。
- LLM 天然支持 NL 且能生成真实感字符串，但单独用于字符串需求可满足性判定的效果低于形式方法，且缺乏可靠性保证（§I）。
- 已有 LLM+形式检查的试错方法中：SMT 检查 UNSAT 有理论局限；Python 命令式检查高效通用但**不能证明不可满足**——这一互补性是全文设计的基础（§I）。

### 2.2 总体架构：数据生成 + 检查器生成的混合方法

- 输入为 NL 字符串需求的合取，输出 Verification Outcome ∈ {UNSAT, SAT, UNKNOWN}；SAT 时附带满足全部需求的字符串作为可满足性证据（§III）。
- 两阶段：先用 LLM 为每条需求生成 Verification Outcome Checker（检查器），再由 Checker-based verifier 借助检查器验证 LLM 推导的中间结果（LVO）（§III）。
- 优雅降级：反馈循环有预算上限（重试次数），预算耗尽返回 UNKNOWN，并给出"最接近可靠"的 ~SAT/~UNSAT 候选，适合交互式快速迭代场景（§III、§V）。

### 2.3 检查器生成器：分治 + 健全性评估

- 两类检查器：**声明式**（SMT 规约，经求解器可验证 UNSAT，也可把候选字符串作为约束验证一致性）与**命令式**（Python 函数，输入字符串返回布尔值，理论限制少但无法证明 UNSAT）（§IV）。
- 需求拆分：在 complete split（每条需求独立成批，IND）与 no split（整集合单批，BATCH）之间；论文假设并验证了 IND 降低生成复杂度（§IV、§VI-B）。
- 转换提示词：Python 检查器用零样本提示（函数签名 + docstring 含 NL 需求，仿 HumanEval 风格）；SMT 检查器给一个 NL→SMT 表达式的示例对以约束输出格式；统一加入角色描述、思维链、情绪刺激等最佳实践（§IV）。
- 检查器健全性：语法健全性用语言特定解析器判定；语义健全性上，SMT 检查器可与 ground truth 做**形式等价性检查**（转成 SMT 问题交 CVC5 求解），Python 检查器用每条需求 5 正 5 反共 10 个样本的测试法近似（§IV、§VI-B）。不健全批次带反馈重新生成直至全部健全后合并（§IV）。

### 2.4 基于检查器的验证器：反馈分级与预算控制

- LLM 先零样本推导 LVO（SAT+data 或 UNSAT），再由检查器验证：UNSAT 结论只能靠声明式（SMT）检查器验证；SAT+data 结论可同时用声明式与命令式检查器（§V）。
- 三级反馈机制：V（仅校验、错则重试）、VF（把历史错误 LVO 作为反例加入提示）、VFE（反例 + 指明违反了哪些具体需求）（§VI-C）。
- LVO 质量评估：SAT+data 被判 UNSAT 时，质量 = 数据满足的需求占比；预算耗尽时按"保存的 UNSAT 数 vs 最优 SAT 数据满足率"选出最佳保存 LVO 返回（§V）。
- 不直接返回 SMT 检查器自己生成的数据：因其缺乏真实感且 LLM 生成的检查器本身可能出错（§V）。
- 关键失效模式：**LLM 输出与检查器同时出错但相互一致**时会产生错误结论，反馈无法完全消除，未来需冗余/交叉验证检查器（§V Failure mode）。

### 2.5 实验设计要点

- 4 个 LLM（GPT-4o、GPT-4o-mini、Llama3.1-8b、DeepSeek-V3）；数据集为 12 类字符串变量（Email、Password、Palindrome、括号序列、DNA 等）派生的 340 个 NL 需求集，含正/负需求的等价类划分组合；ground truth 由人工 SMT-LIB2 形式化后交 CVC5（5 秒超时）标注，最终 283 SAT / 57 UNSAT（§VI-A）。
- 声明式检查器用 CVC5 验证（方法不绑定求解器，可换 Z3/Z3str）；温度设 0（开源）/0.01（GPT）/0.1（需受控变化时）；重试预算：检查器生成 2 次、验证器 5 次（§VI-A）。
- 三个 RQ 分层：RQ1 单评检查器生成、RQ2 用 ground-truth 检查器评验证器（理论上界）、RQ3 端到端全 LLM 无 ground truth（§VI）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
| --- | --- | --- |
| Python 检查器语法准确率 | 全部 4 个 LLM、BATCH 与 IND 均为 100% | §VI-B（Table II） |
| Python 检查器测试准确率 | DeepSeek-V3 / GPT-4o / GPT-4o-mini 均 100%；Llama3.1-8b（IND）约 98% | §VI-B（Table II） |
| SMT 检查器准确率（IND） | GPT-4o 与 DeepSeek-V3：语法 >85%、测试 >75%；Llama3.1-8b：语法与测试均 <20% | §VI-B（Fig. 6） |
| 拆分策略增益 | IND 在全部 LLM 上一致优于 BATCH；GPT-4o-mini 提升超 10%，GPT-4o 约 3% | §VI-B |
| GSR（数据生成成功率，GPT-4o） | 直接生成 78.45% → Python+V 91.87%；全部配置中最高为 Hybrid 92.23% | §VI-C（Table III） |
| GSR（Llama3.1-8b） | 直接 25.80% → SMT+V 55.48%（翻倍以上） | §VI-C（Table III） |
| UNSAT 判定 F1（Llama3.1-8b） | 直接 34.29% → Hybrid+VFE 87.10% | §VI-C（Table III） |
| Hybrid+VFE 总体最优 | GSR 57.24%–92.23%（4 个 LLM 中 3 个最高）；F1 82.59%–93.04%（全部 LLM 最高） | §VI-C |
| 端到端（RQ3，无 ground truth） | 3/4 个验证器 GSR 比值 >95%（相对 ground-truth 检查器上界）；全部验证器 F1 比值 >60%，最好约 88%（GPT-4o-mini 验证器 + DeepSeek-V3 检查器） | §VI-D（Fig. 7） |
| 数据集规模 | 340 个 NL 需求集、12 类字符串变量；ground truth 283 SAT / 57 UNSAT | §VI-A |

## 4. 参考项目 / 资源

| 类别 | 链接/说明 |
| --- | --- |
| 论文（arXiv） | https://arxiv.org/abs/2506.16639 |
| 匿名化实验工件（Zenodo） | https://doi.org/10.5281/zenodo.15679384（论文引用 [36]） |
| SMT 求解器（声明式检查器后端） | CVC5（实验所用）；论文声明可替换为 Z3 / Z3str（§VI-A） |
| 字符串专用求解器 | Ostrich（相关工作对比对象，§I） |
| 结构化输出框架 | LangChain output parsers（§II-C） |
| 前置工作（同一团队） | Babikian et al., "Exploring LLMs for Requirements on String Values", MO2RE 2025：https://mo2re.github.io/assets/preprints/BCM-LLMsForStringRequirments-MO2RE25.pdf（依赖人工形式化，本文去除了该步骤）（§VII） |
| 评测参考基准/方法 | HumanEval 风格零样本提示（§IV）；等价类划分构造需求组合（§VI-A） |

## 5. 一句话索引（给 Agent 用）

> Chen 等（arXiv 2506.16639v1, 2025）提出 LLM 混合方法判定 NL 字符串需求可满足性：LLM 推导 SAT/UNSAT 结论，同时 LLM 自动生成声明式（SMT/CVC5）与命令式（Python）检查器验证该结论，配合 VFE 反馈循环与预算降级，无需人工形式化。在 340 个需求集、4 个 LLM 上，Python 检查器测试准确率达 100%（三个 LLM），Hybrid+VFE 使 GSR 最高至 92.23%、UNSAT 判定 F1 达 82.59%–93.04%（Llama3.1-8b 的 F1 从 34.29% 提至 87.10%），端到端 GSR 达 ground-truth 检查器上界的 95% 以上。注意残余风险：LLM 与其生成的检查器同时出错但一致时结论仍会错。

## 6. 与本仓库研究的相关性注记

- **同一问题的两条路线对照**：我们的 requirement-to-spec 项目走"人工把需求规则编码为 Z3 可判定的规格→Z3 检查可满足性"的传统路线；该论文走"LLM 直接消化 NL→LLM 生成检查器自验证"的自动化路线，且明确以"免去人工 SMT-LIB2 形式化"为核心卖点（§I Added Value、§VIII）——这正击中我们人工编码的最大成本项，是评估是否引入 LLM 辅助形式化时的关键参照系。
- **"LLM 辅助形式化验证"趋势的代表性工作**：其架构（生成器 agent + 验证器 agent 的多智能体式分工，见 §VII 末段自述）与我们"LLM 只起草不判定"红线可对照：它让 LLM 同时承担起草（LVO）与判定工具的生成（checker），可靠性靠语法解析器 + 形式等价检查（CVC5）+ 测试法三重外部锚定（§IV 健全性评估），即"LLM 产物必须被非 LLM 机制客观检验"这一点与我们红线精神一致，但检验工具本身（checker）仍由 LLM 生成，存在自举风险。
- **正确性保障机制的边界值得借鉴**：论文自己承认关键失效模式是"LLM 输出与检查器都错但相互一致"（§V Failure mode），且 Llama3.1-8b 的 SMT 检查器准确率 <20%（§VI-B）说明小模型生成形式规格不可靠——这为我们坚持"判定必须落在 Z3/CVC5 这类成熟求解器、LLM 至多做翻译草稿并由人审"的立场提供了实证支撑；同时其形式等价性检查（把"两个 SMT 表达式等价"转成可求解的 SMT 问题）是校验 LLM 起草规格正确性的可直接复用技术。
