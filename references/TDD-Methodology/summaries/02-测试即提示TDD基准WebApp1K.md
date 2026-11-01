---
title: "Tests as Prompt: A Test-Driven-Development Benchmark for LLM Code Generation"
source_pdf: "02-Cui-Tests_as_Prompt_TDD_Benchmark_v1.pdf"
arxiv_id: "2505.09027"
arxiv_version: "v1"
authors:
  - "Yi Cui"
year: 2025
venue: "arXiv（ICLR 2025 投稿，录用状态未核实）"
type: "评测对照 + 内容索引"
generated_at: "2026-11-01"
summary_version: "1.0"
---

# 论文摘要：测试即提示（Tests as Prompt）——WebApp1K 的 LLM-TDD 基准

## 1. 适用场景

- 当你需要评测 LLM 在"测试即规格"条件下的应用层代码生成，想借用或复刻一套现成基准时，读本文的基准构造法：React 单页应用（SPA）模板 + 20 个应用领域 × 5 类 × 10 场景 = 1000 题，每题由一个成功测试与一个失败测试充当提示与验证（§2.1–§2.2，附录 A）。
- 当你的 LLM 前端代码"看起来功能正常却跑不过测试"、需要系统性归因时，读本文的七类错误分类（A–G）及其"根因 → 模型能力"映射，以及"93% 错误日志仅含单一/孪生错误"的诊断结论（§3.3–§3.4）。
- 当你关心测试提示变长（多约束组合）后性能断崖、或推理模型也会被预训练先验带偏时，读双特性升级实验（duo-feature）与指令丢失（instruction loss）案例分析，包括 raw format 下 o1 系列 pass@1 归零的 default export 陷阱（§4，附录 D）。
- 当你打算给 TDD 任务叠加 system prompt、测试注释、失败重试等提示工程手段前，先看附录 C 的负结果：三种提示变体无一对所有模型普适有效，作者明确不推荐。

> 锚点：arXiv 2505.09027v1 — §2.1–§2.2 与 App. A（基准构造）、§3.3–§3.5（错误分析）、§4 与 App. D（长提示衰减）、App. C（提示实验）

## 2. 主要观点与方案

1. **提出 TDD 任务类别：测试同时充当提示与验证。** 传统编码任务由自然语言提示 + 事后测试（作者称 TLD，Test-Last Development）构成；本文让测试用例本身既作提示又作验证标准，LLM 以"事务式"一次性接收全部测试并产出通过全部测试的代码，区别于人类增量式的 TDD 迭代（§1，Tab. 1–2，Fig. 1–2）。作者自称 "build to our knowledge the first TDD benchmark"（§1 贡献列表），并在 §5.5 重申 "this is the first paper focusing on TDD benchmarking"。
2. **基准设计三原则（§2.1）。** 选应用层而非算法/工具题：语义空间未被预训练语料充分覆盖，防背诵；选 React 生态：库齐全、免造轮子，且 SPA 允许单文件实现多功能，输出紧凑易挂钩评测。
3. **任务与测试集构成（§2.2–§2.3，附录 A）。** 1000 道题聚合在 20 个应用领域（博客、电商、行程管理等）；每题由人工设计场景、GPT-4o 生成一个成功测试与一个失败测试（fetchMock 模拟 API + fireEvent 模拟用户操作 + expect 断言），提示约 0.5K token；构造遵循 Self-Instruct 方法论。指标采用 pass@1/5/10，每题最多运行 n=10 次（§2.3，附录 B：temperature=0.2、top_p=0.8 网格搜索定参）。
4. **评测结果：推理模型领跑，题目难度两极分化。** 19 个前沿模型中 o1-preview 以 pass@1=0.952 居首；多数题目失败率低，右侧一小簇题目极难、个别未被任何模型解出（§3.1–§3.2，Tab. 6，Fig. 3）。
5. **发现一：错误集中于七类 A–G，无一模型免疫。** 版本不匹配、文本不匹配、API 调用不匹配、模块未装、API 签名不匹配、作用域违规、UI 元素缺失；93% 错误日志只含单一或孪生错误，说明失败模型产出的是"只差一处"的高质量代码（§3.3–§3.5，Tab. 7，Fig. 4–5）。
6. **发现二（核心论断）：指令遵循与上下文学习才是 TDD 分水岭，通用编码能力既不关键也不充分。** 证据为 TLD 对照实验：把弱模型违反的测试按其已生成代码改写（保持测试结构不变、改动限单条语句）后，7 个弱模型 pass@1 全部大幅跃升（如 llama-v3p1-405b 从 0.3020 升至 0.8850），说明这些模型代码功能健全，败在未跟随测试指令（§3.6，Tab. 8，Fig. 6）。
7. **发现三：输入上下文长度是波及所有模型的瓶颈。** 双特性升级（合并两题为四测试、提示约 1K token）使所有模型 pass@1 显著下降（claude-3.5-sonnet 以 0.75 成为新 SOTA，o1-preview 从 0.952 降至 0.652）；作者怀疑根因是注意力衰减（attention decay）（§4，§4.1，Tab. 9）。
8. **发现四：指令丢失（instruction loss）连推理模型也不能幸免。** o1-preview 在双特性题中丢失"捕获 500 错误并显示 Internal Server Error"的指令且推理链毫无察觉；附录 D 进一步展示非推理模型被"前端校验"最佳实践先验带偏而违背测试期望，以及 raw format 下推理模型从第一步规划就锁死错误路线、pass@1 归零（§4.2，Tab. 10；App. D.1–D.2，Tab. 17–21）。
9. **负结果：提示工程对 TDD 无普适收益。** system prompt、verbose comment、error debugging 三种变体增益在模型间方向不一致（error debugging 从 -79% 到 +111% 剧烈摆动），作者不推荐任何高级提示技巧（App. C，Tab. 16）。此外附录 E 的 LOC 分析显示各模型中位代码行数集中在 35–46 行、与 pass@1 无强相关，成功解的行数分布比失败解更复杂（App. E，Tab. 22–24）；结论重申两大贡献：专用 TDD 基准 + "指令遵循与上下文学习是改进方向"的洞见（§6）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
| --- | --- | --- |
| 单特性基准最高 pass@1（o1-preview） | 0.952 | §3.1 Tab. 6 |
| 单特性 pass@1：o1-mini / deepseek-r1 | 0.939 / 0.927 | §3.1 Tab. 6 |
| 非推理模型最高 pass@1（gpt-4o-2024-08-06） | 0.885（pass@5 0.9047、pass@10 0.909） | §3.1 Tab. 6 |
| 单特性最低 pass@1（llama-v3-8b） | 0.0679 | §3.1 Tab. 6 |
| 双特性基准（约 1K token）最高 pass@1 | claude-3.5-sonnet 0.75；o1-preview 降至 0.652 | §4.1 Tab. 9 |
| 双特性 raw format pass@1 | o1-mini、o1-preview 均 0；gpt-4o 0.026；claude-3.5 0.32 | App. D.2 Tab. 19 |
| TLD 实验 pass@1 提升（改测试迎合代码） | llama-v3p1-405b 0.3020→0.8850；7 个弱模型全部跃升（0.0679–0.3323 → 0.64–0.885） | §3.6 Tab. 8 |
| 语法错误（构建失败）率 | 172 / 160,000 ≈ 0.1% | §3.6 |
| 错误日志仅含单一或孪生错误的占比 | 93% | §3.4 |
| 提示实验相对增益（error debugging） | -79%（deepseek-v2）至 +111%（llama-v3-70b） | App. C Tab. 16 |

注：模型清单为 Tab. 6 的 19 个前沿模型（o1-preview、o1-mini、deepseek-r1 三个推理模型因推理成本仅测 pass@1、每题 1 次；其余 16 个模型每题最多 10 次，n=10，测 pass@1/5/10）；样本规模为 1000 题 × 16 模型 × 10 次 = 160,000 个解（§3.2 脚注 1、§3.6）。论文未报告任何统计显著性检验，"significant" 仅作定性表述（§3.6、§4.1）。注意论文自身数字不一致：摘要与 §3.1 称 19 个模型，§6 结论却写 "18 frontier LLMs"。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
| --- | --- |
| 本文 arXiv | https://arxiv.org/abs/2505.09027 （v1，2025-05-13，Yi Cui，ONEKQ Lab） |
| 前作（WebApp1K #1） | https://arxiv.org/abs/2409.05177 —— 同一基准的更早论文；本 PDF 未引用它，但 arXiv 管理员注记两者存在文本重叠（背景核实信息，非 PDF 内容） |
| 同工作 ICLR 2025 投稿 | https://openreview.net/forum?id=sqciWyTm70 —— 题为 "Tests as Instructions"，录用状态未核实（背景核实信息，非 PDF 内容） |
| 榜单 / 代码 | https://huggingface.co/spaces/onekq-ai/WebApp1K-models-leaderboard —— 论文引用的唯一代码类资源（参考文献 (web, 2024)，§1） |
| 基准构造方法 | Self-Instruct（Wang et al., 2023, arXiv:2212.10560），附录 A 遵循其方法论 |

## 5. 一句话索引（给 Agent 用）

> WebApp1K（"Tests as Prompt"，arXiv 2505.09027）以 1000 道 React 应用题（20 领域，成功 + 失败测试对既当提示又当验证）评测 LLM 的 TDD 代码生成：单特性下 o1-preview pass@1 最高 0.952、claude-3.5 0.8808；测试加倍至约 1K token 后全员显著下降，claude-3.5 以 0.75 居首；弱模型在 TLD 对照实验中 pass@1 从 0.07–0.33 跃升至 0.64–0.89，证明指令遵循与上下文学习、而非通用编码能力才是 TDD 分水岭；错误归为 A–G 七类、93% 为单一/孪生错误，无一模型免疫。
