# 软件工程原理 × LLM 系统对照调研

> 状态：已完成初稿（2026-08-17）

本文梳理经典软件工程原理与"LLM 作为软件组件"这一新范式之间的对照关系，明确区分两类证据：**经典文献**（确定性高，出处明确）与**新文献**（2023 年后，部分有争议或尚在演化）。

---

## 一、经典原理出处（确定性高）

### 1.1 Parnas 信息隐藏（1972）

- **出处**：David L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules", *CACM* 15(12), 1972。
- **核心观点**：模块划分的依据不是执行流程，而是"设计决策的隐藏"——每个模块封装一个可能变化的设计决策，接口只暴露抽象，不暴露实现。这是后来面向对象封装、API 设计、微服务边界的理论根基。
- **对照 LLM 系统**：LLM 应用中"prompt + 模型"天然是一个信息隐藏边界极弱的组件——prompt 中混杂了指令、示例、业务规则，调用方与被调方共享同一个自然语言上下文，没有真正的"决策隐藏"。Parnas 的模块化标准为评估"LLM 组件边界应如何划分"提供了最早的尺子。
- 参考链接：
  - https://dl.acm.org/doi/10.1145/361598.361600
  - 经典论文重读：https://www.cs.umd.edu/class/spring2003/cmsc838p/Design/criteria.pdf （课程讲义 PDF）

### 1.2 Brooks《没有银弹》与本质/偶然复杂度（1986/1987）

- **出处**：Frederick P. Brooks, Jr., "No Silver Bullet: Essence and Accidents of Software Engineering", *IEEE Computer* 20(4), 1987（原为 1986 IFIP 演讲）。
- **核心观点**：软件的**本质复杂度**（essence）来自问题域本身的抽象结构——需求的模糊性、概念的一致性等；**偶然复杂度**（accident）来自实现工具与过程。工具只能消灭偶然复杂度，无法动本质分毫。软件的本质困难有四：复杂度、一致性、可变性、不可见性。
- **对照 LLM 系统**：LLM 是否消除了"没有银弹"的断言是当前争论焦点。一种有影响的观点是：LLM 大幅压缩了偶然复杂度（样板代码、语法细节），但需求澄清、概念一致性、变更管理等本质复杂度并未消失，只是转移到了 prompt/eval/spec 层面。
- 参考链接：
  - 原文 PDF：https://faculty.salisbury.edu/~xswang/FSE/Slides/NoSilverBullet.pdf
  - Wikipedia 条目：https://en.wikipedia.org/wiki/No_Silver_Bullet

### 1.3 CBSE 与 Design by Contract

- **CBSE（基于构件的软件工程）**：
  - Szyperski, *Component Software: Beyond Object-Oriented Programming*, Addison-Wesley, 1998。给出经典构件定义：可独立部署、由第三方提供、无（外部）可见状态的单元，仅通过契约通信。
  - Wikipedia：https://en.wikipedia.org/wiki/Component-based_software_engineering
- **Design by Contract（契约式设计）**：
  - Bertrand Meyer, *Object-Oriented Software Construction* (2nd ed.), Prentice Hall, 1997； DbC 概念的系统阐述见 Meyer, "Applying 'Design by Contract'", *IEEE Computer* 25(10), 1992, https://dl.acm.org/doi/10.1109/2.161279 。
  - 核心观点：构件间关系用前置条件、后置条件、不变式显式表达，可检查的契约使复用与组合成为可能。
- **对照 LLM 系统**：LLM 组件的前置/后置条件是概率性满足的，"不变式"随模型版本漂移。这是"LLM 组件 vs 传统 API 契约"差异的理论出发点（详见第三节）。

### 1.4 需求工程与形式化规约：为何未成主流

- **经典文献**：
  - IEEE Std 830-1998（SRS 推荐实践）：https://ieeexplore.ieee.org/document/720574
  - Jackson, *Software Requirements & Specifications: A Lexicon of Practice, Principles and Prejudices*, Addison-Wesley, 1995。
  - 形式化方法代表性成功案例：seL4 微内核验证（Klein et al., SOSP 2009, https://dl.acm.org/doi/10.1145/1629575.1629596）、CompCert 编译器（Leroy, CACM 2009, https://dl.acm.org/doi/10.1145/1593455.1593459）。
- **未成主流的原因**（社区共识 + 系统性研究）：
  - Hillel Wayne, "Why Don't People Use Formal Methods?", https://www.hillelwayne.com/post/why-dont-people-use-formal-methods/ ——总结术语混乱、教育门槛、投资回报认知等障碍。
  - The 2020 Expert Survey on Formal Methods (INRIA/HAL), https://inria.hal.science/hal-03082818/document ——结论：技术上成功但"远未成为主流"。
  - "Whatever Happened to Formal Methods for Security?" (IEEE S&P Magazine / PMC), https://pmc.ncbi.nlm.nih.gov/articles/PMC5120363/ ——成本/收益比在非关键领域不成立。
  - 主要障碍归纳：①成本与时间（形式化开发显著更贵）；②可扩展性（状态爆炸，验证只对小核可行的）；③教育缺口；④ROI 认知——仅在航空航天、密码学、硬件等失败代价极高的领域有明确回报。
- **对照"prompt 作为规约"的关键类比**：
  - prompt 在 LLM 应用中事实上扮演了"规约"角色——用（自然）语言描述期望行为、约束与示例，正对应需求文档/SRS 的地位；evals 对应验收测试/一致性检查。历史教训是：**形式化规约败给了"够用的非形式化描述 + 测试"**，而 prompt 是比自然语言 SRS 更弱、比代码更强的中间态。形式化方法史提示的开放问题是：LLM 系统会不会重复"规约成本 > 收益"的老路，还是 evals + 统计抽样提供了历史上缺失的廉价检查手段。

---

## 二、"LLM 作为软件组件"新文献（2023–2026，部分有争议）

### 2.1 LLM 作为软件组件 / SE for & with LLM 综述

- **Weber et al., "Large Language Models as Software Components: A Taxonomy for LLM-Integrated Applications", arXiv:2406.10300 (2024)**，https://arxiv.org/abs/2406.10300 ——最直接以"LLM 即构件"为题的分类学研究，讨论 LLM 集成应用的架构模式。
- **Hou et al., "Large Language Models for Software Engineering: A Systematic Literature Review"（ACM TOSEM 2024）**，https://dl.acm.org/doi/10.1145/3695988 ——SE with LLM 权威综述，含测试、验证章节。
- **"From LLMs to LLM-based Agents for Software Engineering"**, arXiv:2408.02479, https://arxiv.org/abs/2408.02479 ——LLM/Agent 在 SE 任务中的综述。
- **"Software Engineering for Prompt-Enabled Systems"**, arXiv:2503.02400, https://arxiv.org/abs/2503.02400 ——把 prompt 当作与 LLM 及其他组件交互的"软件制品"来研究其工程化（版本、测试、演化）。

### 2.2 Prompt-as-specification 相关讨论

- "Software Engineering for Prompt-Enabled Systems"（同上，arXiv:2503.02400）是目前最接近"prompt 是规约"论题的正式论文。
- 社区/工业界讨论（非同行评审，观点性强）：
  - Anthropic 等厂商的 prompt 工程指南把 prompt 定位为"行为规约 + 上下文"，如 https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview 。
  - Simon Willison 博客对"prompt 是程序/规约"的多次讨论：https://simonwillison.net/ 。
  - Berkeley CS194/CS294 等课程将 prompt 类比为 spec + code：https://cs194.stanford.edu/ （相关课程材料随学期更新）。
- **争议点**：prompt 既非可执行语义也非可验证契约——它是"给统计模型的软约束"，同一 prompt 在不同模型/版本下行为漂移，因此"prompt 即规约"的类比被部分研究者（如上述 taxonomy 论文的引用讨论）认为是**不完备类比**，需补充 evals 作为"操作性规约"。

### 2.3 Evals 方法论（工业界主导，方法论尚在成型）

- **Hamel Husain 系列**（当前 evals 方法论最有影响的实践来源）：
  - "LLM Evals: Everything You Need to Know", https://hamel.dev/blog/posts/evals-faq/
  - "The Ultimate AI Evals FAQ (Now New & Improved)", https://hamelhusain.substack.com/p/the-ultimate-ai-evals-faq-now-new
  - 与 Shreya Shankar 合授课程 AI Evals for Engineers & PMs：https://maven.com/parlance-labs/evals
  - 著作《Evals for AI Engineers》(O'Reilly)：https://www.oreilly.com/library/view/evals-for-ai/9798341660717/
  - 核心主张：先做错误分析（人工读真实失败样本），再建 eval；evals 必须落到具体失败模式上（"grounded"），而非抽象质量分。
  - 传播文：The Pragmatic Engineer, "A pragmatic guide to LLM evals for devs", https://newsletter.pragmaticengineer.com/p/evals ——提出以 evals 替代 "vibes-based development"。
- **对应 SE 原理**：这套方法论实质上是"验收测试驱动 + 回归测试套件"的回归，eval suite ≈ 非确定性组件的测试规约。

### 2.4 Metamorphic Testing（蜕变测试）

LLM 输出无唯一 oracle，蜕变测试（Chen 等人 1998 年提出的经典技术， https://dl.acm.org/doi/10.1145/174679.174684 ）成为 LLM 测试的主流方案之一：

- **Zheng et al., "Bidirectional Empowerment of Metamorphic Testing and Large Language Models: A Systematic Survey", arXiv:2605.13898 (2026)**, https://arxiv.org/abs/2605.13898
- **Cho et al., "Metamorphic Testing of Large Language Models for NLP Tasks" (ICSME 2025)**, arXiv:2511.02108, https://arxiv.org/abs/2511.02108 ——整理了 191 条蜕变关系（MR）。
- **LLMORPH: Automated Metamorphic Testing of Large Language Models**, arXiv:2603.23611, https://arxiv.org/abs/2603.23611
- 意义：MT 为"非形式化决策逻辑"提供了无需精确 oracle 的弱验证手段，是经典 SE 技术直接迁移到 LLM 的最佳案例。

### 2.5 Neuro-symbolic 混合架构与 guardrails

- **Dong et al., "Safeguarding Large Language Models: A Survey" (Artificial Intelligence Review, Springer, 2025)**, https://link.springer.com/article/10.1007/s10462-025-11389-2 ——guardrails框架的系统综述。
- **Neuro-Symbolic Control with Large Language Models**, arXiv:2512.17321, https://arxiv.org/html/2512.17321v2 ——LLM 接收符号化状态+任务描述的混合控制。
- Bamberg 大学 "Neuro-Symbolic Verification of LLM Outputs for Data-Sensitive Domains"（形式符号方法+神经语义分析混合验证架构），https://fis.uni-bamberg.de/entities/publication/afdcb500-b05c-4ca9-b64e-e7ff34e01517
- 观点文（非同行评审）："The Neurosymbolic Guardrail", https://medium.com/graph-praxis/the-neurosymbolic-guardrail-why-your-rag-system-cant-catch-the-errors-that-actually-matter-4abf07e62e5c ——主张 RAG 无法捕获逻辑错误，需要符号验证护栏。
- **对应 SE 原理**：即"确定性外壳包裹非确定内核"——用传统代码/约束求解器做外层控制流与校验，LLM 只做局部决策。这是 CBSE 思想在概率组件上的复兴。

---

## 三、争论焦点：LLM 组件 vs 传统 API 契约；非形式化决策逻辑的规约与验证

### 3.1 与传统 API 契约的系统性差异

| 维度 | 传统 API/构件（Szyperski/Meyer 传统） | LLM 组件 |
|---|---|---|
| 语义 | 确定性；契约可精确陈述 | 概率性；满足契约是分布意义上的 |
| 版本 | 显式版本、语义化版本控制 | 模型静默更新，同一版本内行为随采样参数漂移 |
| 契约可检查性 | 前置/后置条件可机器检查 | 契约以自然语言 prompt 表达，不可直接执行检查 |
| 测试 oracle | 输出确定，可断言 | 无唯一 oracle，需依赖 MT/LLM-as-judge/人工 |
| 失败模式 | 异常、错误码 | 幻觉：自信但错误的"类型正确"输出 |
| 组合 | 契约推断保证组合正确性 | 组合后行为涌现，契约不可加 |

相关论证文献：arXiv:2406.10300（taxonomy）；Hou et al. TOSEM 2024 综述测试/验证章节。

### 3.2 各方观点

- **"prompt 即规约"乐观派**：prompt + eval suite 构成新型规约-验证对，形式化历史失败的原因（规约太贵）被 LLM 降低了——可以用自然语言写规约。多见于工业界（Hamel Husain、Anthropic 文档）。
- **审慎派**：自然语言规约本身有歧义，且 LLM 对规约的满足是概率性的；需要把"操作性规约"下放到 evals 与 MT 关系（Cho et al. 2025），或引入 DbC 式协议层（"Towards Engineering Multi-Agent LLMs: A Protocol-Driven Approach", arXiv:2510.12120, https://arxiv.org/abs/2510.12120 ，显式借用 Design by Contract 建模多智能体协作）。
- **混合架构派**（neuro-symbolic / guardrails）：不给 LLM 组件写完整契约，而是用确定性外壳（类型约束、schema 校验、符号验证器、运行时护栏）把非确定内核的失败面限制在可检查范围内——Dong et al. 2025 综述与 Bamberg 的混合验证工作是代表。
- **回望 Brooks**：争论的深层结构仍是"没有银弹"——LLM 压缩偶然复杂度后，本质复杂度（澄清需求、定义"正确行为"、管理变更）转移到 spec/eval 工程，这恰是经典需求工程的领地。

---

## 四、证据分类小结

**经典文献（确定性高）**：Parnas 1972；Brooks 1987；Meyer 1992/1997（DbC）；Szyperski 1998（CBSE）；Chen et al. 1998（蜕变测试）；IEEE 830；形式化方法史（seL4、CompCert、2020 Expert Survey、Hillel Wayne）。

**新文献（2023–2026，有争议/演化中）**：arXiv:2406.10300（LLM 即构件 taxonomy）；arXiv:2503.02400（prompt-enabled 系统）；Hou et al. TOSEM 2024 综述；Hamel Husain evals 方法论（工业实践，非同行评审）；arXiv:2511.02108 与 arXiv:2605.13898（MT×LLM）；arXiv:2510.12120（DbC 式多智能体协议）；Dong et al. 2025 guardrails 综述；neuro-symbolic 验证工作。
