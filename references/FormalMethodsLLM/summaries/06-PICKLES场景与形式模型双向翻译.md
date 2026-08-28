---
title: "PICKLES: a Natural Language Framework for Requirement Specification and Model-Based Testing"
source_pdf: "06-Rodriguez-PICKLES_BDD_Formal_Models_v1.pdf"
arxiv_id: "2604.26572"
arxiv_version: "v1"
authors:
  - "María Belén Rodríguez"
  - "Petra van den Bos"
year: 2026
venue: "JOT / ECMFA 2026"
type: "设计参考 + 内容索引"
generated_at: "2026-08-28"
summary_version: "1.0"
---

## 1. 适用场景

- 当你要把 BDD（Gherkin Given–When–Then）场景**双向翻译**为形式化模型（STS）再自动生成高覆盖测试用例时，读这篇——它给出了从 DSL 语法（EBNF 文法）到 STS 语义映射、再到 Pickles 测试用例回译的完整形式化定义（§4、§6）。
- 当你在做"多场景 → 单一主模型（master model）"的**场景组合/编排**设计，需要选择/顺序组合算子（choice ⋏ / sequential ▷）的数学定义时，读 §5（Definition 2–4）。
- 当你需要向工业界/非技术干系人论证"结构化自然语言规格 + 形式化语义"这条路线的覆盖率收益（转移覆盖 30%→100%、输入覆盖 1.5%→100% 的量化对比）时，引用 §8.2、§8.3 的案例数据。

> 锚点：论文原生 §1（贡献列表）、§4（语法与翻译）、§5（组合）、§8（讨论/收益分析）。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1）

工业实践存在张力：自然语言（BDD）可及性强但有歧义、测试套件臃肿难维护；形式化 MBT 模型精确但可读性差、组织接受度低。现有方法迫使从业者二选一。论文提出 PICKLES（Precise Input and Control-flow Keyword-based Language for tEst Scenarios），让规格与测试用例都保持人类可读，同时获得 MBT 的自动测试生成能力（§1）。五大贡献：PicklesDSL（§4）、Pickles↔STS 双向翻译（§4、§6）、主模型组合（§5）、原型工具（§7）、Technolution 交通管理工业案例（§3、§8）。

### 2.2 形式化基础（§2）

- BDD/Gherkin 回顾：场景即 Given–When–Then 结构，靠 step 实现挂接 Cucumber/Robot Framework/Behave 等工具（§2.1）。
- 语义靶模型为符号迁移系统 STS = (L, l₀, V_l, V_p, Γ, I, R)，带位置变量、门参数、guard 与赋值（switch 元组），沿用 Van den Bos & Tretmans 2019 定义（§2.3）。
- DSL 用类正则 EBNF 的上下文无关文法描述，语义通过 ⟦·⟧ 映射到 STS 元素（§2.4）。

### 2.3 PicklesDSL 设计与 →STS 翻译（§3、§4）

- 案例规格套件 = Variable Settings 前奏（声明变量类型与值域：primitive/array/struct 递归构造）+ 若干 Scenario；Technolution 案例含 4 个场景（故障检测器在关键路段内/外导致 AV / PART AV / NOT AV，以及控制器失联禁用系统）（§3，Listing 1）。
- Given/When/Then 语义约束：Given=SUT 前置条件；When=外部主动发起的交互；Then=SUT 可观察动作；每场景至少一个 When 和一个 Then（§4.1）。
- 翻译机制（§4.2）：
  - 规格套件：每个 Scenario 映射为一个 STS；含 InitialCond（"the system is in its initial state"）的为 primary STS（S_p），否则为 secondary（S_s）；所有变量同时生成同标识符的位置变量与门参数（§4.2.1、§4.2.2）。
  - Guard Block：变量+量词/比较算子+AND/OR 构成谓词，映射为 switch guard；Given 中的 guard 约束位置变量（初始 guard IG），When/Then 中的约束门参数；`stored?` 前缀显式引用位置变量；array guard 支持量词（at least/at most/exactly/all），struct guard 支持属性级条件（§4.2.3）。
  - Given/When/Then 块：When 步→输入 switch，Then 步→输出 switch，参数赋值回位置变量以供后续步骤使用；假设各场景位置集不相交、交互（gate, 参数序列）跨场景一致（§4.2.4、§4.2.5）。

### 2.4 主模型组合（§5）

定义两个组合算子并构造主模型：Choice 组合 ⋏（统一初始位置，汇合分支，Definition 2）；Sequential 组合 ▷（把 S1 的 sink 位置并入 S2 初始位置，Definition 3）；主模型 = S_ini ▷ (S_sys ▷ S_sys)，其中 S_ini=⋏S_p、S_sys=⋏全部 STS（Definition 4）。主模型可能非确定、可能含不可达位置/场景——不可达场景向场景作者反馈"场景写错或该场景在系统上不可测"（§5）。

### 2.5 测试生成与 Pickles 回译（§6）

- 形式化测试用例 = (switch 序列 r₀…rₙ, 位置变量初值 ini, 参数值序列 w̄₀…w̄n)，采用 Van den Bos & Tretmans 2019 的方法达 100% switch 覆盖，path condition 用 SMT 求解器取值（§6.1）。
- 回译到 Pickles：输出 switch 的具体值被忽略、替换为对应 guard 以校验 SUT 实际观察值；Given 段展开为全部位置变量初值；测试用例保持 Gherkin 结构，可直接用标准 BDD 工具自动化（§6.2）。

### 2.6 实现与发现（§7、§8、§9、§10）

- 原型：Python + Lark 解析库；双模式（规格翻译：Pickles 文本→JSON STS；测试翻译：JSON STS+测试→Pickles 文本）；原型版主模型暂不剔除不可满足路径（§7）。工具与复现指令公开于 Zenodo。
- 三项关键优势（§8）：(i) 人类可读+形式语义双保证，可读测试构成规格作者的反馈控制回路（§8.1）；(ii) 自动场景组合暴露"隔离执行发现不了的交互性 bug"，并支撑 shift-left 测试（§8.2）；(iii) 输入/输出参数化带来早期类型/值域一致性检查，并缓解测试者确认偏差（§8.3）。
- 相关工作按 5 主题综述；最接近的是 Zameni 等（BDDTS 手工翻译、顺序组合算子被本文采纳）；FRET/T-EARS 等有形式化无测试生成；UML→Gherkin 类无参数化；作者断言无现有方法同时覆盖全部 5 主题（§9）。
- 未来工作：多案例规模化评估、开发者体验实证研究、非确定性控制流表达式、场景标注 criticality/失败概率、时间约束、以及用 LLM 辅助从既有 Gherkin 用例自动泛化迁移到 Pickles（§10）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
| --- | --- | --- |
| 案例规格套件场景数（Technolution 交通管理组件） | 4 个场景 | §3 |
| BDD 隔离执行下的转移覆盖 | 8/26 个转移，约 30% | §8.2 |
| Pickles 生成测试的转移覆盖 | 100%（提升 70 个百分点） | §8.2 |
| 手工达到 100% 覆盖所需测试 vs Pickles 输入 | ≥7 个测试 vs 4 个场景 | §8.2 |
| Scenario 02 单条守卫输入表示的不同输入组合 | 112（2·(1+10+45)） | §8.3 |
| Scenario 01 / 03 输入 switch 允许取值数 | 175 / 11（Scenario 04 无参数） | §8.3 |
| 单组硬编码值实际覆盖的系统输入比例 | 约 1.5%（即输入覆盖提升 98.5%） | §8.3、§10 |
| 结论口径的覆盖提升 | 转移覆盖 >70%、输入覆盖 98.5% | §10 |

## 4. 参考项目 / 资源

| 类别 | 链接/说明 |
| --- | --- |
| 论文（arXiv） | https://arxiv.org/abs/2604.26572 |
| 工具与复现工件 | Zenodo: https://doi.org/10.5281/zenodo.19710432 （Rodriguez 2026，含翻译与组合步骤的原型） |
| 解析库依赖 | Lark：https://github.com/lark-parser/lark （Python EBNF 解析） |
| 理论基础 | Van den Bos & Tretmans 2019, "Coverage-Based Testing with Symbolic Transition Systems"（TAP）：STS 定义、100% switch 覆盖测试生成、SMT path condition |
| 组合算子先例 | Zameni et al. 2025（FORTE'25，BDDTS 顺序组合）；Zameni et al. 2024（SANER-C'24，BDD 场景→BDDTS 中间语言，手工翻译） |
| 结构化自然语言规格相关工作 | FRET（NASA）、T-EARS、RTCM（ISSTA'15）、SysReq-CNL/NAT2TESTSCR（Carvalho et al. 2014）、Structured English Grammar（Autili et al. 2015） |
| 可复用 BDD 工具链（测试落地端） | Cucumber、Robot Framework、Behave |
| 工业案例来源 | Technolution B.V.（荷兰，交通管理系统遥测组件，原 Cucumber BDD 用例） |
| 资助 | NWO 项目 Evidence-driven Black-box Checking (EVI)，编号 OCENW.M.23.155 |

## 5. 一句话索引（给 Agent 用）

> PICKLES 论文（Rodríguez & van den Bos，Twente，2026）证明了一条"BDD 分路→形式化"的可行管线：用带 Variable Settings（类型/值域）与 Guard Block 的 Gherkin 扩展 DSL，把每个场景自动翻译成 STS，经 choice/sequential 组合成 master model，再用 Van den Bos & Tretmans 的 MBT 算法生成测试并回译为人类可读的 Pickles 用例。在 Technolution 交通管理案例（4 个场景、26 个转移的 master model）上，BDD 隔离执行仅覆盖 30%（8/26）转移、约 1.5% 输入空间，而 Pickles 以同样 4 个场景达到 100% 转移覆盖（+70pp）与 98.5% 输入覆盖提升；手工达到同等覆盖需 ≥7 个测试。查 DSL 语法语义→§4，组合算子→§5，回译→§6，工具→§7，收益量化→§8。

## 6. 与本仓库研究的相关性注记

- **最强先例邻居**：该论文是检索到的、与本仓库 requirement-to-spec 方向（BDD 分路编排 / 场景↔形式化模型双通道）最接近的完整先例——它同样走"结构化自然语言场景 ⇄ 形式模型"双向通道（⟦·⟧ 与 ⟦·⟧⁻¹ 两套映射，§4/§6），且 master model = S_ini ▷ (S_sys ▷ S_sys)（§5, Definition 4）本质上就是一条场景编排代数。可将其 choice/sequential 组合算子与 primary/secondary STS（§4.2.1）作为我们场景编排语义的直接对照基线。
- **差异点 1（场景独立性纪律）**：PICKLES 靠两条语法层假设保证可组合性——场景位置集两两不相交、同 gate 的参数序列跨场景一致（§4.2.5，作者称可自动检查）；我们的场景独立性纪律是显式的、构造前的约束层（而非翻译后可检查假设），并在组合前即保证闭包性质，不再依赖事后 satisfiability 剔除（对比 §5 的不可达场景反馈机制）。
- **差异点 2（两维标注路由 + 需求锚定）**：PICKLES 的场景路由维度仅有 primary/secondary（是否 InitialCond，§4.2.1），criticality/失败概率标注被列为未来工作（§10）；我们的两维标注路由在其停步处继续推进。此外 PICKLES 的场景↔STS 追踪依赖"标识符对应关系被记录"的隐性约定（§4.2.2/§4.2.5），我们的需求锚定绑定闭包把这一约定升级为显式的、可验证的绑定结构——审阅其 §8.1 的"可读测试构成规格反馈回路"论证时，锚定闭包正是该回路工程化所缺的一环。
