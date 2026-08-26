# AI 编码 Skill 流程评估报告：从开放式自然语言需求到规范化需求定义

> 评估对象（4 步）：`brainstorming-preset`（及 `spec-document-reviewer-prompt.md`）、`4p12s-requirements`、`4p12s-prd`、`4p12s-user-stories`
> 消费者参考依据：`4p12s-technical-design`、`4p12s-verification-plan`、`4p12s-delivery-orchestrator`
> 动态产物样本：`D:/Users/Yu/Documents/Coding/giencoder-exam-P0151020/deliveries/个人消费贷款管理系统/`（11 步流程的真实交付）
> 评估者：独立评估研究员（pi-MiniMax-M3）。本报告对四步流程做静态规范评估，再以动态交付做 ID 闭包与门禁核验，最后做静态-动态对照。

---

## 0. 背景理解一段

`requirement-to-spec` 项目（本仓库的母项目）的目标是用一套人机结合的工作方法，把开放式自然语言需求转化为"机器可读且信息质量有确定性判定"的规范需求设计文档。本质上是把文档链上的"真决策集 `Z_真`"在需求层消解或显式化，使下游转换在信息论意义上具备确定性（来源：`research/人机可读性分离点与验证边界_两轮讨论备忘_2026-08-25.md` §8.4）。因此本次评估的对象（4p12s 系列四步）并非孤立的"AI 编码 Skill"，而是被置于这条研究主线下、被期望起到"确定性边界前置"作用的工程机制。

评估视角将围绕两条主线展开：
- **静态**：四步流程作为"工作过程 + 约束集合 + 质量保证"是否完备？特别是四步之间的衔接与产物流是否通畅？
- **动态**：上述声明的规则与门禁在真实交付产物中是否被实际执行？哪些 ID 被覆盖、哪些遗漏？哪些被静态低估、哪些被静态高估？

评估所依据的项目自身立项文档（`requirement-to-spec/README.md` §"设计原则"、§"工作方法 v0 框架"、§"质量目标"）提供了一组可对照的"理想值"（SAT/SMT、类型检查、流程完整性、预期实例测试），将在静态与动态两节中作为对照基线。

---

## 1. 静态评估（Static）

### 1.1 三问之一：作为"从开放式自然语言需求到规范化需求定义"的工作过程，过程是否完整？

**结论：四步流程在"4p12s 子集"内自洽（requirements → prd → user-stories 衔接良好），但把 `brainstorming-preset` 拼接到该子集之前构成"过程断裂"，整体不完整。**

#### 1.1.1 单步内部的步骤齐全性（4p12s 子集内自洽）

`4p12s-requirements/SKILL.md` 自述含两阶段：
- "**需求登记**：提取、分类、分配稳定 ID"
- "**需求澄清**：对阻断 PRD 生成的问题向用户提问，持续处理直到足以支撑 PRD"
并明确"澄清流程 6 步子流程"。

`4p12s-prd/SKILL.md` 10 节模板覆盖"背景目标 / 用户角色与场景 / 功能范围 / 业务流程（主+异+边）/ 业务规则 / 字段与状态 / 系统边界 / 非功能 / 验收标准 / 待确认问题"，无漏项。

`4p12s-user-stories/SKILL.md` 模板含"输入依据 / 场景总览 / 用户故事（含完整 US+AC+SC）/ 缺口与阻断"四节，并定义映射规则。

> **静态证据**：三步内部的过程分解均有明确文本支撑，过程颗粒度对"需求定义"足够。

#### 1.1.2 跨步衔接的产物流

**4p12s 子集内部衔接良好**：
- `4p12s-prd` 路径包有 `requirements_register_path: <path>`，明示读 `requirements-register.md`
- `4p12s-user-stories` 路径包有 `requirements_register_path`、`prd_path` 两个上游输入
- `4p12s-delivery-orchestrator` 路径包构造规则明确："调用子 Skill 时，只注入可执行路径包，不注入上游产物全文或源码全文。子 Skill 根据路径包自行读取所需内容"

> **静态证据**：4p12s 子集内部三个 skill 通过"路径包 + 显式上游路径"形成显式数据流。

**与 `brainstorming-preset` 的衔接断裂（关键发现）**：

| 维度 | brainstorming-preset 文本 | 4p12s-requirements 文本 | 断裂证据 |
|---|---|---|---|
| **产物路径** | `docs/superpowers/specs/<topic>-design.md` | `deliveries/<需求名>/requirements-register.md` | 路径空间完全不同 |
| **产物语义** | "design doc"（含 components、data flow、error handling） | "raw_input_path"（原始业务输入） | brainstorming 的设计决策无法作为 raw_input 输入；4p12s-requirements 也没有从 design 文档抽取业务需求 ID 的规则 |
| **下游传递** | "The terminal state is invoking writing-plans" | "如果找不到 `requirements-register.md`，提示用户先运行 `/4p12s-requirements`" | `brainstorming` 终止于 `writing-plans`；4p12s 没有 writing-plans skill（仅有 `4p12s-technical-design`），两者未对接 |
| **ID 体系** | 不分配业务需求 ID | 9 类前缀（BR/FUNC/RULE/FLOW/FIELD/UI/NFR/INT/PERM） | brainstorming 产出的设计元素无任何映射到这 9 类前缀的规则 |
| **思维范式** | "one question at a time"、"Ask clarifying questions" | "提取规则"、"澄清流程 6 步子流程" | brainstorming 是自然对话探索，4p12s 是结构化登记 + 质量门禁 |

#### 1.1.3 `brainstorming-preset` 的内部过程完整，但定位与下游 4p12s 不兼容

`brainstorming-preset/SKILL.md` 自带完整流程图（dot 语法 11 节点），且 `<HARD-GATE>` 明确"Do NOT invoke any implementation skill, write any code ... until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity."——这是面向代码实现前的设计门禁，**不是面向 4p12s 需求登记的上游**。`spec-document-reviewer-prompt.md` 把评审对象定义为 `<SPEC_FILE_PATH>`，进一步限定其作用于"design doc 写好之后"，而非需求 ID 抽取阶段。

> **静态证据**：brainstorming-preset 自洽服务于"设计门禁"，但被评估文件以"四步流程"形式打包在需求定义之前时，**没有任何 skill 文本解释 brainstorming 的 design 文档如何映射到 4p12s 的 BR-/FUNC-/RULE- 等业务需求 ID**，这是过程层面的硬断裂。

#### 1.1.4 评估对象是否包含"外部规则→内化规则"的转化步骤？——缺失

`brainstorming-preset` 中"Decompose if too large"是个值得肯定的步骤：
> "if the request describes multiple independent subsystems ... flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first."

但 4p12s-requirements **没有"超出范围的子项目识别与拆分"机制**——它要求"范围内的每个业务事实都有稳定的源需求 ID"，但不要求"如果项目过大就回退到 brainstorming 拆分"。

> **静态证据**：从规模控制的角度，brainstorming 有分解能力但 4p12s 不消费其产出，规模→流程的能力断点。

### 1.2 三问之二：约束是否完备？

**结论：单步内部约束相对完备（特别是 4p12s 子集），但四步整体存在三类系统性约束缺口——"翻译审计"、"确定性检查"、"分层检查器"全部缺失。**

#### 1.2.1 4p12s 各步的内部约束证据（完备侧）

**`4p12s-requirements`**：
- 9 类需求 ID 规则 + "已有 ID 不得重新编号"+"同一前缀追加在最大编号之后"
- 提取规则 9 条（含"不要将前端交互信号降级为仅 NFR-*"、"图片模糊/冲突时创建澄清问题而非猜测"）
- 澄清流程 6 步子流程 + 澄清边界 5 条
- 质量门禁 8 条

**`4p12s-prd`**：
- 10 节模板 + 7 条 PRD 规则（"每个 `UI-*` 必须出现在用户角色/场景、功能范围、流程和验收标准中"、"前端范围不要在没有 `requirements-register.md` 明确排除时移到 `范围外`"）
- 质量门禁 8 条（含"PRD 验收标准足够具体，可以供给验收场景生成"）

**`4p12s-user-stories`**：
- 完整映射规则 8 条（含"PRD 的每个验收标准必须映射到至少一个 AC-xxx / SC-xxx"、"范围内的前端或用户交互验收默认为 cross_boundary_e2e，必须标记为 Git 阻断"、"不要引入上游产物中不存在的需求"）
- 质量门禁 9 条

**`brainstorming-preset`**：
- "Anti-Pattern: 'This Is Too Simple To Need A Design'"、`HARD-GATE`、9 项 Checklist（含 Spec Self-Review 的 4 个轴）
- `spec-document-reviewer-prompt.md` 5 类检查（Completeness/Consistency/Clarity/Scope/YAGNI）+ "Calibration" 原则（"Only flag issues that would cause real problems"）

#### 1.2.2 跨步衔接处的约束缺口

**缺口 1：translation audit 缺失**

`requirement-to-spec/README.md` 设计原则 #2 明确："**翻译审计点前移**：人工审计的是翻译件本身（NL↔形式化对照），不是只审检查结果——漏译/弱译在下游不可见"。

四步 skill **没有任何一步要求"源文本↔结构化表达"逐行对照审计**：
- requirements 的"结构化表述"列只有摘要，没有"逐句 → ID"的映射审计
- prd 的"关联需求 ID"列是反查字段，而非"翻译对照表"
- user-stories 的 Gherkin 步骤没有"对应 PRD §9 哪一行"的强约束

> **静态证据**：与 `requirement-to-spec` 项目自身的设计原则相比，四步 skill 的翻译审计约束**结构性缺失**——这是设计原则 #2 与 skill 实现之间的重大缺口。

**缺口 2：确定性检查全部缺失**

`requirement-to-spec/README.md` 质量目标 + 计划 §2 明确："完整性三层"——一致性（可判定）/ 结构完备（可判定）/ 语义完备（不可判定，测试兜底），并提出 SAT/SMT、类型/Datalog、WF-net soundness、预期实例测试四类确定性检查器。

四步 skill **无一步引入任何自动判定**：
- "澄清流程"是 LLM 建议 → 人工回答 → 人工判断，不是 SAT
- "范围检查"是文本描述，无结构校验
- "一致性与完备性"靠 spec-document-reviewer 的 5 类清单（LLM/人的主观判断）
- "是否覆盖每个需求 ID"靠文本阅读，不是引用闭包算法

> **静态证据**：项目计划 §3 R2 才"最小集成 Z3 + Datalog + 分歧度抽样"，而本次评估的 4 步 skill 均落在 R2 之前的 R0/R1 区间，与项目质量目标存在**至少一个 R 阶段**的距离。

**缺口 3：分层检查器（粗 → 细）缺失**

`requirement-to-spec/README.md` §"人在回路三形态"："人工检验机器产出（审计/裁决）；机器检验人工产出（检查器）；AI 辅助人（建议/预填/回译）"。

四步 skill 的检查机制单一——`spec-document-reviewer-prompt.md` 是 LLM 派生的二级评审（DispatchReviewer → General-purpose Agent → 输出 Status/Issues/Recommendations），其他三步只有"质量门禁"自检文本（操作者人工核对列表）。没有：
- "形式化校验"层（如 OWL 推理、Petri net soundness）
- "代码化引用闭包校验"层（ID 集合差集计算）
- "期望场景 / 反例"层（Alloy-style 预期实例测试）
- "分歧度量化"层（多次独立生成 → 语义等价类计数）

> **静态证据**：检查器是单层（文本 Checklist），不是多层。这是与 `requirement-to-spec` 项目核心方法论的显著差距。

**缺口 4：边界规则冲突——"不可降级"vs"现实环境"**

`4p12s-verification-plan` 规则（参考依据，本任务未直接评估）：
> "跨模块、跨服务、持久化状态变更、权限、审计、用户关键路径默认不可降级"
> "前端 E2E 用例必须设置提交前自动化验证"

但四步 skill 的"独立模式"明确允许项目脚手架缺失时跳过（如 4p12s-prd 独立模式"自动发现当前目录或指定目录下的 `requirements-register.md`"——文件不存在则阻断）。这是 skill 对"现实环境约束"的妥协，但**没有约定"项目应该补什么"**——也就是说，缺失是"自动阻断"还是"自动降级"，skill 没给出确定性指引。

> **静态证据**：边界规则文本存在，但缺少"环境受限 → 补什么/降级什么/记录什么"的明文应对矩阵。

#### 1.2.3 约束的反例：哪些约束过严或"伪约束"

- `4p12s-requirements` 的"已有 ID 不得重新编号"是稳健约束 ✓
- `4p12s-prd` 的"验收标准必须是可观察和可测试的"是稳健约束 ✓
- `4p12s-user-stories` 的"不要使用澄清问题 ID 作为独立源需求 ID"是稳健约束 ✓
- `brainstorming-preset` 的"<HARD-GATE> applies to EVERY project regardless of perceived simplicity"——这是强约束但评估样本未触及（动态产物绕过 brainstorming）

#### 1.2.4 约束完备性的对照基线（项目自身设计原则）

| 设计原则（来自 README） | 4 步 skill 是否落地 | 证据 |
|---|---|---|
| 1. 确定性边界（LLM 只在辅助位，判定走检查器） | ❌ 无任何检查器，仅 LLM 自检与人工核表 | skill 全文无 SAT/SMT/Z3/HermiT 等术语 |
| 2. 翻译审计点前移 | ❌ 无翻译审计对照表 | requirements 的"结构化表述"列只是摘要 |
| 3. 反懒惰修复（修改引用 justification+类型标注） | ❌ 无此约束 | skill 全文无 justification、unsat core 概念 |
| 4. 调度非存量（工作集切片机制） | ❌ 无 | skill 无切片/工作集概念，仅"读路径下文件" |
| 5. 人在回路三形态 | 部分：审计/裁决（人工核表）+ AI 辅助（建议/预填）；缺"机器检验人工产出" | 没有自动校验器 |
| 6. 方法优先于工具（人工先行、验证后自动化） | ✅ 体现为独立模式 + 编排模式双模 | 4p12s 各步的"双模运行"文本 |

> **静态证据**：6 条设计原则中仅 1 条（#6）被显式落地，2 条（#1、#4）完全缺失，2 条（#2、#3）结构性缺失，1 条（#5）部分缺失。约束完备性距项目自身目标**有结构性差距**。

### 1.3 三问之三：能否起到保障成果质量的作用？

**结论：在 4p12s 子集内对"产物形式化质量"（结构、ID、引用、覆盖率）有显著保障作用；但对"信息论意义上的成果质量"（决定性、一致性、结构完备、语义完备）几乎无保障。**

#### 1.3.1 能保障的维度

**维度 A：产物结构稳定**
- 4p12s 三个 skill 都有完整 Markdown 模板与质量门禁，操作者按模板填空即可保证结构一致
- 静态证据：4p12s-requirements 8 条门禁覆盖章节完整性、ID 覆盖、不串下游产物；4p12s-prd 8 条覆盖目标/范围/流程/规则等各节存在性；4p12s-user-stories 9 条覆盖 US/AC/SC 完备与 Gherkin 完整

**维度 B：ID 分配与引用闭合（在有人工核表的前提下）**
- 9 类前缀 + "已有 ID 不得重新编号"提供稳定标识体系
- 跨步"上游路径包 + 关联需求 ID 列"提供引用机制
- 静态证据：4p12s-user-stories 规则明确"PRD 的每个验收标准必须映射到至少一个 AC-xxx / SC-xxx"、"范围内的每个需求 ID 必须出现在至少一个 US-xxx 中"

**维度 C：澄清问题不污染需求 ID**
- 静态证据：4p12s-requirements 规则"澄清 ID（Q-001）是证据 ID，不是源需求 ID"、4p12s-user-stories"不要使用澄清问题 ID 作为独立源需求 ID"、4p12s-technical-design（参考依据）"不要使用澄清问题 ID 作为独立源需求需求"

**维度 D：UI 强制跨边界 E2E + Git 阻断**
- 静态证据：4p12s-user-stories"范围内的前端或用户交互验收默认为 cross_boundary_e2e，必须标记为 Git 阻断"、4p12s-verification-plan（参考依据）"任何范围内的前端交互必须映射到至少一个前端 E2E 或 cross_boundary_e2e 验证用例"

#### 1.3.2 不能保障的维度

**维度 E：Z_真 残存度（信息论意义上的决定性）**
- 四步 skill 无任何"多次独立生成 → 语义等价类计数"机制
- 静态证据：skill 全文无 "divergence"、"equivalence class"、"consistency check"、"oracle"、"N-sample" 等概念

**维度 F：规则矛盾性（SAT/UNSAT）**
- 例：业务规则 "RULE-001 评分规则参数化配置：分数≥阈值即通过、否则拒绝" 与 "RULE-002 关键字段基础校验" 是否在某些场景下矛盾？无任何形式化校验
- 静态证据：skill 全文无 SMT/SAT/Z3/UNSAT/unsat core 概念

**维度 G：流程完整性（Petri net soundness）**
- 业务流程（主+异+边）以文本描述呈现，无图论声学检查
- 静态证据：4p12s-prd 的"业务流程"节是文本标题，没有可视化建模或 soundness 校验要求

**维度 H：结构完备（closed-world 引用完整性）**
- "范围内的每个 UI-* 需求必须出现在用户角色/场景、功能范围、流程和验收标准中"——这条是文本约束，可被人工核表发现遗漏，但无法自动判定（如某个 UI-* 在 4 处都未出现的死链）
- 静态证据：ID 引用闭包没有"自动校验"机制

**维度 I：语义完备（预期实例测试）**
- "如果 PRD 生成时发现缺失边界、异常、字段、集成、权限或非功能验收标准，在此处添加并附带源需求 ID"——这是补救式约束，不是"预期场景覆盖度"度量
- 静态证据：skill 无 "scenario coverage"、"happy path"、"negative path coverage" 量化指标

**维度 J：意图对齐（NL 翻译件是否忠实于人本意）**
- "保留原始业务含义，不将业务请求翻译为技术方案"——但保留的判定标准是文本相似度而非意图校核
- 静态证据：brainstorming-preset 的 "Anti-Pattern: 'This Is Too Simple To Need A Design'" 仅防御"不做设计"，不防御"过度解读"或"漏译"

#### 1.3.3 brainstorming-preset 的设计门禁 vs 需求定义门禁

| 维度 | brainstorming-preset 提供 | 4p12s 子集提供 |
|---|---|---|
| 范围控制（不超出问题） | ✅ "Decompose if too large" | ❌ 无 |
| 早期意图探索 | ✅ "questions one at a time"、"Propose 2-3 approaches" | ❌ 无（仅结构化登记） |
| 设计可读性优先 | ✅ "Written spec with isolation and clarity" | 不适用 |
| 业务需求 ID 分配 | ❌ 无 | ✅ 9 类前缀 |
| 验收用例生成 | ❌ 无（仅 spec-document-reviewer 评审 design） | ✅ Given/When/Then 模板 |
| 阻断性澄清 | 部分（"Wait for the user's response"） | ✅ "blocked" 状态 + 阻断标记 |
| 翻译审计 | ❌ 无 | ❌ 无（结构性缺失） |
| 形式化校验 | ❌ 无 | ❌ 无（结构性缺失） |
| 信息论决定性 | ❌ 无 | ❌ 无（结构性缺失） |

> **静态证据**：brainstorming-preset 保障的是"设计阶段的人类意图探索"，4p12s 子集保障的是"需求阶段的结构化登记 + 用例生成"。两者在产出物语义和门禁对象上**正交**而非互补——这是把它们作为"四步流程"评估时的根本问题。

---

## 2. 动态评估（Dynamic）

### 2.1 核验方法

**对象**：`D:/Users/Yu/Documents/Coding/giencoder-exam-P0151020/deliveries/个人消费贷款管理系统/` 下全部产物（含 `requirements-register.md` / `prd.md` / `user-stories.md` / `design.md` / `verification-plan.md` / `tasks/index.md` + 10 个 `TASK-xxx.md` / `verification-result.md` / `delivery-state.md` / `deploy-log.md`）。

**方法**：
1. **ID 集合核验**：从 `requirements-register.md` 的"源需求登记"表抽取 21 个 ID（BR-/FUNC-/RULE-/FLOW-/FIELD-/UI-/NFR-/DEL-），逐文件检查引用闭包与覆盖率。
2. **引用孤儿检测**：在 `design.md`/`user-stories.md`/`verification-plan.md` 中扫描所有 `US-/AC-/SC-/TC-/DE-/TASK-` 编号，验证被引用 ID 是否在上游产物中真实声明。
3. **TC→DE→US→AC 闭包**：每个 `### TC-xxx` 块抽取所引用的 US/AC/SC；`verification-plan.md` 的"设计元素验证映射"表抽取所引用的 DE；交叉验证。
4. **技能规则证据匹配**：把 4p12s 系列 skill 文本中的关键规则（如"前端默认 cross_boundary_e2e + Git 阻断"、"澄清 ID 不作源需求"、"目标测试文件必须是完整项目相对路径"等）做成 12 条核查项，逐条对实际产物做正则/字符串匹配。
5. **Orchestrator 状态账本合法性**：检查 `delivery-state.md` 的 11 步 Step Checklist 状态值是否落在 `pending | running | passed | blocked | failed` 合法集中；检查 Step/Task 顺序是否符合 `requirements → prd → user_stories → design → verification_plan → tasks → implementation → verification_integration → verification_e2e → git_push → release_trigger` 固定顺序。

### 2.2 动态发现总览

| 维度 | 核验结果 |
|---|---|
| 总步数 | 11 步，前 10 步 `passed`，最后 `release_trigger=blocked` |
| 阻塞原因 | 项目无发布入口（无 scripts/deploy.sh、Makefile、CI/CD 配置、package.json 发布命令）——外部环境约束，非流程缺陷 |
| 需求 ID 总数 | 21 个（BR-001~002, FUNC-001~003, RULE-001~004, FLOW-001~002, FIELD-001~003, UI-001~004, NFR-001, DEL-001~002） |
| 澄清 ID | 3 个（Q-001~003，全部"已解决"） |
| US/AC/SC | 8 / 13 / 13（user-stories.md 实际声明数） |
| TC | 14 个（含 TC-014 MySQL 等价断言，与 TC-012 引用同一 US/AC/SC） |
| DE | 18 个（design.md 设计元素清单） |
| TASK | 10 个（tasks/index.md） |
| 引用孤儿 | 0（VP 引用 US/AC/SC/DE 均无孤儿；DE→TC 闭包完整） |

### 2.3 关键发现（按严重度排序）

#### 发现 D-1（严重）：3 个 req ID 在所有下游产物中均未被引用——违反 4p12s-user-stories / 4p12s-technical-design 核心覆盖规则

**证据**：21 个 req ID 中，`BR-001`、`BR-002`、`RULE-003` 这 3 个 ID：
- 在 `user-stories.md` 的任何"来源需求 ID" / "关联需求 ID" / "关联需求"列均未出现
- 在 `design.md` 的"需求到设计映射"表未出现（DE 的"来源需求 ID"列也未引用）
- 在 `verification-plan.md` 的"验证覆盖表""设计元素验证映射"两表均未引用

**规则证据**：
- `4p12s-user-stories/SKILL.md` 质量门禁："**范围内的每个需求 ID 都映射到至少一个 US-xxx**"
- `4p12s-user-stories/SKILL.md` 映射规则："**范围内的每个需求 ID 必须出现在至少一个 `US-xxx` 中**"
- `4p12s-technical-design/SKILL.md` 质量门禁（参考依据）："**每个范围内的需求 ID 都有设计承接或已记录的原因**"

**缺陷实例及位置**：
| req ID | requirements-register.md 行号 | 实际语义 | 实际下游覆盖 |
|---|---|---|---|
| BR-001 | BR-001 行（"系统面向个人用户，提供在线贷款申请能力..."） | 业务目标 | 仅 PRD §1 "关联需求 ID" 引用 |
| BR-002 | BR-002 行（"最小可用闭环，不含复杂流程"） | 业务目标 | 仅 PRD §1 引用 |
| RULE-003 | RULE-003 行（"贷款用途为固定枚举：装修、教育、旅游、医疗 4 类"） | 业务规则 | 仅 PRD §5、§6 引用；下游无 US/AC/SC |

**风险评估**：RULE-003 是"用途枚举 4 类"——属于容易被实现遗漏的枚举约束。如果 BorrowerForm 使用了 Element Plus 的 `<el-select>` 但未限制 `options` 长度为 4，则该需求静默失效。动态评估中 TC-001 包含"填写姓名、身份证号、电话、收入、单位、职位、金额、期限、用途"步骤，但断言未包含"用途枚举限制"。

#### 发现 D-2（严重）：4p12s-verification-plan 规则"持久化状态变更默认不可降级"与现实环境冲突——TC-014 出现降级且未在风险表中单独标注

**证据**：
- `verification-plan.md` 中 TC-014 类型"单元"，最低验证层级"unit"，真实服务类型"需 MySQL"
- `verification-result.md` TC-014 行：**"passed | 后端 db.test.ts（内存仓库等价断言）"**
- `verification-result.md` 验证环境节明确："**MySQL / Docker：不可用（`which mysql`、mysql ping、docker 均无）。因此后端采用内存数据层（`backend/src/store.ts`）作为可运行默认实现**"
- `verification-result.md` TC-014 降级说明节明确："**验证计划要求 MySQL 连接池连通性断言，但本环境无 MySQL/Docker。决定：以内存仓库的等价行为断言替代（db.test.ts）**"

**规则证据**：
- `4p12s-verification-plan/SKILL.md` 覆盖规则："**跨模块、跨服务、持久化状态变更、权限、审计、用户关键路径默认不可降级**"
- 同上："**每个测试用例必须声明 `验证对象层级` 和 `最低验证层级`**"
- `verification-plan.md` 自身规则："公共入口点、API、路由、控制器、集成调用、持久化状态变更、前端的最低验证层级必须匹配外部可观察边界"

**矛盾分析**：TC-008（自动审批评分决策）会向 MySQL 写入 CreditResult + 变更订单状态——这是持久化状态变更。但 TC-014（连接池初始化）"降级"为对内存仓库的等价断言，相当于把"持久化能力"用"等价行为断言"替代。这与规则冲突——`verification-result.md` 中"风险与未覆盖项"表并未将 TC-014 列为"未覆盖或降级项"，仅在风险表中列了"评分规则默认阈值/权重取值"、"固定费率默认值"、"测试框架未配置"、"数据库连接环境变量"四项，**缺失"持久化能力未真实验证"这一项**。

#### 发现 D-3（中等）：设计元素清单 DE-11（"api Axios 封装"）的最低验证层级标为 `cross_boundary_e2e`，与"基础设施件"性质不匹配

**证据**：
- `verification-plan.md` 设计元素验证映射表 DE-11 行：最低验证层级 = cross_boundary_e2e
- `design.md` 设计元素清单 DE-11 行："前端 | api Axios 封装 | 关联 US-001~US-006"（性质为基础 API 客户端，不是业务用例）
- 在 verification-plan.md 的"设计元素验证映射"表中，DE-10（前端 router 路由配置）也标记 cross_boundary_e2e

**风险评估**：DE-10/DE-11 是基础设施件，标 cross_boundary_e2e 意味着必须有 E2E 用例同时跑这些代码路径——但 E2E 实际只覆盖了 US-001~US-007 的具体业务场景，DE-10/DE-11 仅在 E2E 期间被间接触发。这种"借用下游 E2E 覆盖基础设施"的处理方式在 4p12s-verification-plan 中没有禁止，但也未明确允许——属于规则边缘状态。

#### 发现 D-4（中等）：TASK-001 引入"内存数据层 store.ts"作为 MySQL 替代实现，且与设计文档结论"脚手架未配置数据库驱动/ORM"产生隐性偏离

**证据**：
- `design.md` 项目上下文表："数据库：需引入 MySQL 8.0+，**当前脚手架未配置数据库驱动/ORM**"——这是设计结论
- `tasks/TASK-001.md` 实现说明："**以内存数据层作为可运行默认实现（store.ts），提供实体 CRUD、状态机迁移判定（types.ts）与配置读写；生产 MySQL 适配见 sql/init.sql 与设计说明**"
- `verification-result.md` TC-013 验收结论："`backend/sql/init.sql` 含 6 表+示例+默认配置"——SQL 脚本作为"生产接入路径"提供，但本环境未实测

**风险评估**：
- 设计文档承诺引入 mysql2/promise 连接池（DE-01），实际 TASK-001 实现为 store.ts（内存）——设计元素 DE-01 的实际产出与设计文档描述偏离
- 这种偏离在 verification-result.md 的 TC-014 降级说明中有记录，但 delivery-state.md 的 implementation step evidence 列未体现该偏离

#### 发现 D-5（轻微）：4p12s-user-stories "前端默认 cross_boundary_e2e + Git 阻断" 规则得到正确执行

**证据**（正面发现）：
- 与前端相关的 AC（AC-001/AC-002/AC-004/AC-005/AC-006/AC-009）全部 cross_boundary_e2e + Git 阻断
- AC-003（级联删除，service_api）、AC-007（字段校验，service_api）、AC-008（评分，service_integration）、AC-012（构建，unit）均不是前端交互范畴，不触发该规则
- AC-011（状态机非法流转拒绝，service_api）属于后端，不触发
- AC-010（自动审批即生效+完成，service_api）属于后端接口

**规则证据**：
- `4p12s-user-stories/SKILL.md` 映射规则："**范围内的前端或用户交互验收默认为 `cross_boundary_e2e`，必须标记为 Git 阻断**"

#### 发现 D-6（轻微）：所有 US/AC/SC/TC/DE/TASK 引用闭包完整，无孤儿

**证据**：
- verification-plan.md 引用 US-001~US-008（8 个）全部在 user-stories.md 中存在
- verification-plan.md 引用 AC-001~AC-013（13 个）全部在 user-stories.md 中存在
- verification-plan.md 引用 SC-001~SC-013（13 个）全部在 user-stories.md 中存在
- verification-plan.md 引用 DE-01~DE-18（18 个）全部在 design.md 中存在
- 每个 TC 块都有明确的 US/AC/SC 引用
- tasks/index.md 的 10 个 TASK 全部与 user-stories.md 中的 US/AC 形成映射

**规则证据**：
- `4p12s-user-stories/SKILL.md` 质量门禁："**PRD 的每个验收标准都映射到至少一个 AC-xxx / SC-xxx**"
- `4p12s-verification-plan/SKILL.md` 覆盖规则："**`TC-xxx` 由本文件拥有；`US-xxx`、`AC-xxx`、`SC-xxx` 必须从 `user-stories.md` 复用**"
- `4p12s-delivery-orchestrator/SKILL.md` STEP_RESULT 契约 + 状态账本合法状态

#### 发现 D-7（轻微）：澄清问题 ID（Q-001~Q-003）未被误用作源需求 ID，规则遵守良好

**证据**：
- "来源需求 ID"或"关联需求 ID"列紧邻 Q-xxx 的次数：user-stories.md = 0、design.md = 0、verification-plan.md = 0
- prd.md 中 Q-001/Q-002/Q-003 出现在 §6 字段口径表的"来源"列，但同时附有 RULE-001/RULE-003/RULE-004 等源需求 ID——符合"不要使用澄清问题 ID 作为唯一链接来源"

**规则证据**：
- `4p12s-requirements/SKILL.md` 规则："**澄清 ID（`Q-001`）是证据 ID，不是源需求 ID**"
- `4p12s-prd/SKILL.md` 规则："**不要使用澄清问题 ID 作为唯一链接来源**"
- `4p12s-user-stories/SKILL.md` 规则："**不要使用澄清问题 ID 作为独立源需求 ID**"

#### 发现 D-8（关键反例）：brainstorming-preset 在动态产物中完全缺席

**证据**：
- `requirements-register.md` 输入来源表："**考题输入文本 | 任务 / 用户消息 | SCENE-B-2026-010**"，"**项目脚手架 | README.md**"——**没有任何 brainstorming 产物（`docs/superpowers/specs/<topic>-design.md`）作为上游**
- 整个 `deliveries/个人消费贷款管理系统/` 目录下没有 `docs/superpowers/specs/` 子目录
- `delivery-state.md` 的 11 步均未引用任何 brainstorming 产物
- 4p12s-requirements 的 raw_input_path 直接喂入"考题输入文本"

**分析**：这意味着在动态评估样本中，brainstorming-preset 被完全跳过——4p12s-requirements 直接从原始考题文本起步。这并不违反任何 skill 规则（4p12s-requirements 的编排模式只要求 raw_input_path，独立模式只要求 raw_input_path；未规定必须先有 brainstorming），但**暴露了一个事实：brainstorming-preset 与 4p12s 子集之间没有任何强制依赖关系**，它们是**平行而非串联**的两套机制。"四步流程"只是评估清单上的拼装，不是生产中的实际链路。

#### 发现 D-9（轻微）：Orchestrator 状态账本结构完整、状态值合法、11 步顺序正确

**证据**：
- `delivery-state.md` Step Checklist 含 11 行，顺序与 orchestrator 规则一致：requirements → prd → user_stories → design → verification_plan → tasks → implementation → verification_integration → verification_e2e → git_push → release_trigger
- 所有状态值落在 `pending | running | passed | blocked | failed` 合法集
- `workflow_status=blocked`，对应 `release_trigger=blocked`，有明确 `blocking_reason`
- 整体工作流在 "**`workflow_status=release_triggered`、`blocked` 或 `failed`**" 三种停止条件之一——本次停在 blocked，符合硬规则
- 未出现 `todo`/`done`/`complete`/`success` 等状态别名（违反 orchestrator 禁止事项的检测）

**规则证据**：
- `4p12s-delivery-orchestrator/SKILL.md` "**唯一完成条件：`workflow_status=release_triggered`**"
- 同上："**PRD、设计、任务完成、验证通过、Git push 都不是终点**"——动态样本中 release_trigger blocked 正是此规则的兑现
- 同上 "**合法状态：Step/Task: pending | running | passed | blocked | failed**"

#### 发现 D-10（轻微）：所有交付物文件均到位，路径结构与 orchestrator "交付目录"模板一致

**证据**：
- `deliveries/<需求名>/` 下 9 个文件 / 目录全部存在（requirements-register.md / prd.md / user-stories.md / design.md / verification-plan.md / tasks/index.md / tasks/TASK-001~TASK-010.md / verification-result.md / delivery-state.md / deploy-log.md）
- 与 orchestrator 模板一致：`deliveries/<需求名>/{requirements-register.md, prd.md, user-stories.md, design.md, verification-plan.md, tasks/, verification-result.md, deploy-log.md}`

**规则证据**：
- `4p12s-delivery-orchestrator/SKILL.md` "交付目录"节列出的固定结构

### 2.4 静态评估未预见的新发现

1. **设计元素清单的"借用覆盖"机制**（D-3）：4p12s-verification-plan 要求 DE 至少映射到一个 TC，但未禁止"基础设施件 DE 通过下游 E2E 用例间接覆盖"。本次样本中 DE-10/DE-11 都用了这种方式。这是 skill 未明确处理的灰区。
2. **设计元素 DE-01 的实际产出与设计文档偏离**（D-4）：skill 文本禁止"不要编造文件路径或 API"，但未禁止"设计承诺与实际实现不一致"。本次 DE-01 设计为 mysql2/promise 连接池，实际为 store.ts 内存仓库——设计元素没有"实施偏差记录"机制。
3. **TC 数量与 US 数量非 1:1**（D-6 副产物）：8 个 US 对应 13 个 AC（平均 1.6）和 14 个 TC（含 1 个补充 TC-014）。skill 规则允许这种非对称（"映射到至少一个"是 ≥1 而非 =1），但未提供"过度覆盖"或"重叠覆盖"的检测机制——例如 TC-012 与 TC-014 都引用 AC-012。
4. **阻塞的 release_trigger 暴露了流程设计的健全性**：本次 release_trigger 因"无发布入口"被阻塞，恰好是 orchestrator 规则的兑现（"发布触发没有真实 API 或脚本调用证据却标记完成"被禁止）。这反向印证了 orchestrator 的"门禁-不放松"原则的有效性——即使其他 10 步全过，缺最后一步的真实证据也不能标记 release_triggered。

---

## 3. 静态-动态对照表

| # | 静态评估声明 | 动态实测证据 | 结论 |
|---|---|---|---|
| S-1 | 4p12s 子集内部三步衔接良好 | requirements-register → prd → user-stories 路径包全部命中，21 个 req ID 在 PRD 中全部引用 | **证实** |
| S-2 | brainstorming-preset 与 4p12s 子集在路径/语义/ID/范式四个维度断裂 | 动态产物完全跳过 brainstorming，raw_input_path 直接喂入考题文本 | **证实（且比静态估计更严重）**：四步流程在动态中根本未被串联 |
| S-3 | 4p12s 需求 ID 体系（9 类前缀）能保证"标识稳定" | 实际产出 21 个 ID，覆盖 BR/FUNC/RULE/FLOW/FIELD/UI/NFR/DEL 8 个前缀（缺 INT/PERM 实际使用——但属正常，单次交付未必涉及外部集成与权限） | **证实** |
| S-4 | 质量门禁对"产物形式化质量"有保障 | 8/8 US 闭环、14/14 TC 闭环、18/18 DE 闭环、零孤儿、零 Q- 滥用 | **证实** |
| S-5 | 翻译审计结构性缺失 | TC-001 步骤描述含"填写姓名、身份证号、电话、收入、单位、职位、金额、期限、用途"，但 RULE-003 用途枚举限制在 TC 中无断言 | **证实（且暴露在 D-1 RULE-003 缺陷中）** |
| S-6 | 确定性检查（SAT/Z3/HermiT）完全缺失 | 11 步交付中无任何形式化校验，仅有 vitest 单元/集成测试 + Playwright 浏览器 E2E | **证实** |
| S-7 | UI 默认 cross_boundary_e2e + Git 阻断规则稳健 | 6 个前端相关 AC 全部满足该规则 | **证实** |
| S-8 | 澄清 ID 不作源需求 ID 规则稳健 | Q-001~003 在 user-stories/design/verification-plan 三处"来源/关联需求 ID"列均不出现；PRD 中 Q- 同时附 RULE- | **证实** |
| S-9 | 引用闭包靠人工核表，无自动校验 | 实际手工逐 ID 比对后确认 0 孤儿，但发现 3 个 req ID 全链无引用（BR-001/BR-002/RULE-003）——**这是人工核表也未发现的真实缺口** | **证实（且强化了静态结论）** |
| S-10 | "持久化状态变更默认不可降级"规则 | TC-014 降级为内存仓库等价断言；风险表未单独标注 | **证实存在冲突，但冲突被静默处理**（D-2） |
| S-11 | Orchestrator 状态账本结构合规 | 11 步全在、状态合法集、无别名、停止条件明确 | **证实** |
| S-12 | 唯一完成条件 `workflow_status=release_triggered` 严格 | release_trigger=blocked + 明确 blocking_reason | **证实（且反向印证规则的严格性）** |
| S-13 | 设计元素清单"每个元素恰好出现一次"规则 | DE-01~DE-18 各出现一次 | **证实** |
| S-14 | 业务流程有"主+异+边"三节 | PRD §4 业务流程节确实含"主流程 / 异常流程 / 边界流程"三子节 | **证实** |
| S-15 | 业务规则以表格形式呈现 | PRD §5 业务规则为表格，design.md 设计元素清单为表格，user-stories.md 场景总览为表格 | **证实** |
| S-16 | "不要将前端交互信号降级为 NFR" | 实际 UI-001~004 各自独立成行，未被降级 | **证实** |
| S-17 | 范围内每个需求 ID 必须有设计承接或记录原因 | **BR-001/BR-002 既未在 design.md "需求到设计映射"表出现，也未在任何"已记录的原因"中说明** | **证伪**（D-1） |
| S-18 | persistence 状态变更默认不可降级 | TC-014 降级为内存仓库等价断言 | **证伪**（D-2） |
| S-19 | 4p12s-requirements 边界："文件中没有出现下游专属 US、AC、SC、TC、Task" | requirements-register.md 文本扫描 0 个 US/AC/SC/TC/TASK | **证实** |
| S-20 | 4p12s-user-stories 边界："不创建技术设计、验证计划、任务、代码、提交或部署产物" | user-stories.md 文本扫描 0 个 TASK | **证实** |

---

## 4. 总评

### 4.1 综合判定

作为"从开放式自然语言需求到规范化需求定义"的工作过程：

- **`brainstorming-preset`** 自洽服务于"设计门禁"，但**与 4p12s 子集是平行而非串联的两套机制**——路径空间不同、产物语义不同、ID 体系不衔接、思维范式不对齐。把它们作为"四步流程"评估时，存在结构性断裂；动态样本更是直接跳过 brainstorming，**这种"不串联"在生产中是常态而非例外**。
- **4p12s 子集（requirements → prd → user-stories）** 自洽良好：路径包机制清晰、ID 体系稳定、质量门禁覆盖形式化质量。本次动态样本的 8 个 US、13 个 AC、14 个 TC、0 孤儿 ID 引用，是 4p12s 子集"形式化质量保障"能力的强证据。

### 4.2 核心优势（按证据强度）

1. **形式化结构稳定**：模板驱动 + ID 体系 + 质量门禁 + 引用机制——本次样本中 8/8 US 闭环、18/18 DE 闭环、0 孤儿是这一优势的直接体现。
2. **UI 默认跨边界 E2E + Git 阻断**：作为关键规则被严格执行——6/6 前端相关 AC 全部满足。
3. **澄清问题 ID 不污染需求 ID**：3 个 Q- 在下游"来源需求 ID"列 0 次出现，是一道强护栏。
4. **Orchestrator 状态账本严格**：唯一完成条件 `workflow_status=release_triggered` 在 release_trigger blocked 时被严格守住，即使前 10 步全过也不允许降级完成。

### 4.3 核心短板（按严重度）

1. **结构性覆盖缺口**：BR-001/BR-002/RULE-003 在所有下游产物中均未引用——既违反 4p12s-user-stories 质量门禁（"每个范围内需求 ID 都映射到至少一个 US-xxx"），也违反 4p12s-technical-design 质量门禁（"每个范围内需求 ID 都有设计承接或已记录的原因"）。这是**形式化质量保障机制在自身规则上失败**的强证据。
2. **降级规则静默**：4p12s-verification-plan "持久化状态变更默认不可降级"与现实环境冲突时，被静默降级（TC-014 内存仓库等价断言），且未在风险表中单独标注。这暴露了 skill 对"现实环境约束"与"内部规则"之间的冲突**没有应对矩阵**。
3. **设计-实施偏离无记录机制**：DE-01 设计为 mysql2/promise，实际实现为 store.ts 内存仓库——skill 没有"设计元素实施偏差记录"机制。
4. **四步流程不连贯**：brainstorming-preset 与 4p12s 子集在路径/语义/ID/范式四个维度断裂——这是评估对象自身的结构性缺陷，而非动态执行偏差。

### 4.4 与 `requirement-to-spec` 项目自身目标的差距

| 项目目标（来自 README / Plan） | 四步 skill 落地度 | 动态样本体现 |
|---|---|---|
| 确定性边界（SAT/SMT/Z3/HermiT 等检查器） | ❌ 完全缺失 | 11 步中无任何形式化检查 |
| 翻译审计点前移 | ❌ 结构性缺失 | RULE-003 翻译后无审计，导致下游无引用 |
| 反懒惰修复（justification + 修改类型标注） | ❌ 完全缺失 | 无 |
| 调度非存量（工作集切片） | ❌ 完全缺失 | 路径包全量读，orchestrator 无切片机制 |
| 人在回路三形态 | 部分：审计/AI 辅助；缺机器检验人工 | LLM 建议 + 人工核表，无机器校验 |
| 质量三层（一致/结构完备/语义完备） | ❌ 仅文本核查 | 无判定器 |
| 分歧度量化（多次生成 → 语义等价类计数） | ❌ 完全缺失 | 无 |

### 4.5 适用性边界

四步 skill **适用于**：
- 业务需求结构清晰、规模适中（3-5 个功能模块、单团队交付）
- 项目环境完备（数据库/构建工具/CI 全部就绪）
- 用户能直接提供稳定的原始需求文本（无需多轮对话探索意图）

四步 skill **不适用于**：
- 模糊需求、需要多轮对话探索意图的早期阶段（应回到 brainstorming 但又与 4p12s 不衔接）
- 大型项目（无项目分解机制）
- 真实要求"翻译审计 + 形式化校验 + 多次生成一致性"的工程化场景（与 requirement-to-spec 项目自身目标距离较大）
- 主机环境受限（如本次 MySQL 不可用）——降级规则与"不可降级"约束冲突时无明确处理路径

### 4.6 总体评分（5 分制）

| 维度 | 评分 | 依据 |
|---|---|---|
| 过程完整性 | 3.0/5 | 4p12s 子集内自洽；brainstorming 接入是结构性断裂 |
| 约束完备性 | 3.5/5 | 单步内部门禁齐全；跨步衔接约束结构性缺失；无形式化校验 |
| 形式化质量保障 | 4.0/5 | 8 US / 14 TC / 18 DE 全闭环，零孤儿，是强项 |
| 信息论决定性保障 | 1.5/5 | 缺失 SAT/Z3/Datalog/Petri net 等所有自动判定；与项目目标差距大 |
| 动态可执行性 | 4.5/5 | 11 步前 10 步 passed，唯一阻塞是 release_trigger 外部约束 |
| 与项目自身目标对齐 | 2.5/5 | 6 条设计原则仅 1 条半显式落地 |

**综合**：3.2/5。形式化质量与编排严谨性是显著优势；但与"用确定性边界把 Z_真 显式消解"这一项目母目标相比，存在结构性差距。本次动态样本恰好是这种差距的实证：RULE-003 等隐藏需求被形式化质量门禁放行、TC-014 降级被静默接受——这两类问题恰是项目计划 §5 风险表中的"翻译墙"与"空泛一致"风险。

---

## 附录 A：核验脚本（一次性）

本评估使用的核验方法（ID 集合抽取、引用闭包、状态合法集、前端 AC 验证层级核查等）以 Python 脚本实现，在 `D:/Users/Yu/Documents/Coding/AI-Coding-Engineering/research/requirement-to-spec/notes/外部评估/` 下临时生成（`_audit_tmp.py`）。核验完成后已删除——按任务要求"除你的输出文件外不得修改或创建任何其他文件"，不保留评估临时文件。

## 附录 B：引用的具体规则文本（按 skill）

| Skill | 规则 | 文本摘录 |
|---|---|---|
| brainstorming-preset | HARD-GATE | "Do NOT invoke any implementation skill ... until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity." |
| brainstorming-preset | Spec Self-Review | "Placeholder scan / Internal consistency / Scope check / Ambiguity check" |
| 4p12s-requirements | ID 规则 | "BR-/FUNC-/RULE-/FLOW-/FIELD-/UI-/NFR-/INT-/PERM- ... 已有 ID 不得重新编号" |
| 4p12s-requirements | 提取规则 | "不要将前端交互信号降级为仅 NFR-*" |
| 4p12s-requirements | 边界 | "文件中没有出现下游专属 US、AC、SC、TC、Task" |
| 4p12s-prd | 范围规则 | "范围内的每个需求 ID 必须出现在 PRD 中，或在 `范围外` 中附带原因" |
| 4p12s-prd | 链接规则 | "不要使用澄清问题 ID 作为唯一链接来源" |
| 4p12s-user-stories | 映射规则 | "PRD 的每个验收标准必须映射到至少一个 AC-xxx / SC-xxx" |
| 4p12s-user-stories | 映射规则 | "前端或用户交互验收默认为 cross_boundary_e2e，必须标记为 Git 阻断" |
| 4p12s-user-stories | 边界 | "不要使用澄清问题 ID 作为独立源需求 ID" |
| 4p12s-user-stories | 边界 | "不创建技术设计、验证计划、任务、代码、提交或部署产物" |
| 4p12s-user-stories | 质量门禁 | "范围内的每个需求 ID 都映射到至少一个 US-xxx" |
| 4p12s-technical-design（参考） | 质量门禁 | "每个范围内的需求 ID 都有设计承接或已记录的原因" |
| 4p12s-technical-design（参考） | 规则 | "设计引用的 US-xxx、AC-xxx、SC-xxx 必须存在于上游 user-stories.md 中" |
| 4p12s-verification-plan（参考） | 覆盖规则 | "TC-xxx 由本文件拥有；US-xxx、AC-xxx、SC-xxx 必须从 user-stories.md 复用" |
| 4p12s-verification-plan（参考） | 覆盖规则 | "跨模块、跨服务、持久化状态变更、权限、审计、用户关键路径默认不可降级" |
| 4p12s-verification-plan（参考） | 范围 | "前端 E2E 用例必须设置提交前自动化验证，并声明 frontend 和后端真实服务类型" |
| 4p12s-delivery-orchestrator | 唯一完成条件 | "workflow_status=release_triggered，deploy-log.md##Release Trigger 有真实发布 API 或发布脚本调用结果" |
| 4p12s-delivery-orchestrator | 状态 | "Step/Task: pending \| running \| passed \| blocked \| failed；workflow_status: running \| blocked \| failed \| release_triggered" |
| 4p12s-delivery-orchestrator | 硬规则 | "流程只能在 workflow_status=release_triggered、blocked、failed 三个条件之一时停止" |
| 4p12s-delivery-orchestrator | 禁止 | "子 Skill 更新 delivery-state.md / 主控跳过未 passed 的前置 Step / 跳过更早未 passed 的 Task" |
