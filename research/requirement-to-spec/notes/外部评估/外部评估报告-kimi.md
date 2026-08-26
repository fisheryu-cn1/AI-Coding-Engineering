# 外部评估报告（kimi）：4p12s 需求→规范 Skill 流程的静态+动态双评估

> 评估人：独立评估研究员（kimi）。评估日期：2026-08-26。
> 评估对象：静态——`templates/研究样本/4p12s-Skills/` 下 brainstorming-preset、4p12s-requirements、4p12s-prd、4p12s-user-stories 四个 SKILL.md（含 spec-document-reviewer-prompt.md），参考消费者视角的 4p12s-technical-design、4p12s-verification-plan、4p12s-delivery-orchestrator；动态——`giencoder-exam-P0151020/deliveries/个人消费贷款管理系统/` 全套真实交付产物（19 个文件，2284 行）。
> 独立性声明：未阅读 `4p12s-Skills四步流程初步评估.md` 及 `notes/外部评估/` 下任何已存在文件。

## 0. 背景理解

本评估的校准视角来自上游研究备忘与立项文档：该研究的核心命题是把文档链上的真决策集 Z_真 在需求层消解或显式化，分离点 = Z_真 归零的最早链上位置；质量目标分三层——一致性（可判定）、结构完备（可判定，需 closed-world 手段）、语义完备（不可判定，测试兜底）；并确立"LLM 只做翻译/建议/回译，一切判定走确定性检查器""翻译审计点前移""反懒惰修复"三原则。据此，我对四步流程的评估标尺是：它把哪些判定变成了可机检的门禁（ID 覆盖、结构完整），哪些判定仍停留在 advisory 的自然语言规则（语义忠实、一致性、验收质量），以及产物链上的 Z_真（真自由度）是被消解、被显式化，还是被静默决策。动态评估则以一次真实交付（个人消费贷款管理系统，11 步流程跑通至 git_push、release_trigger 诚实阻断）检验这些门禁的实际执行力。

---

## 1. 静态评估

### 1.1 评估一问：作为"从开放式自然语言需求到规范化需求定义"的工作过程，过程是否完整？

**结论：需求登记→PRD→用户故事三步主干过程完整且闭环设计良好；但流程入口（brainstorming-preset）与 4p12s 主干在接口上是断裂的，"第 0 步"名实不符。**

主干三步的过程完整性证据：

- 每一步都有明确的输入契约、唯一产物、双模运行（编排/独立）和返回契约。4p12s-requirements 的两阶段划分（登记→澄清循环）覆盖了三层"完整"中的前两层："登记完成后，检查是否存在阻断 PRD 生成的澄清项……仅在没有阻断性澄清项、用户明确无法提供关键答案时结束"（4p12s-requirements SKILL.md 澄清流程，第 119–127 行）。
- 澄清有明确边界，防止过程越权："不提出设计、实现、测试、Git 或发布问题""不创建下游产物""不删除原始需求文本"（澄清边界，第 129–135 行）。
- PRD 规则要求"范围内的每个需求 ID 必须出现在 PRD 中，或在`范围外`中附带原因"（4p12s-prd SKILL.md 第 111 行），形成需求层的 closed-world 覆盖声明——这是三件套中"结构完备"的过程化实现。
- user-stories 设了防空洞规则："如果需要的验收场景没有对应的 PRD 验收标准，返回 `blocked` 而非凭空创建"（4p12s-user-stories SKILL.md 第 104 行），把"下游缺输入"显式化为阻断而非即兴发挥。

过程的不完整处在入口：

- brainstorming-preset 的终止状态是 "Invoke writing-plans skill"（SKILL.md 第 68 行），产物落盘路径是 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` 并要求 git commit（第 31、113–116 行）。它与 4p12s-requirements 之间**没有任何产物接口**：brainstorming 产出的是 design 文档而非原始业务输入登记，4p12s-requirements 的输入契约（`raw_input_path`、输出 `deliveries/<需求名>/requirements-register.md`）不消费它。
- 更深一层，brainstorming 的"design doc"与 4p12s-technical-design 的 `design.md` 在语义层重叠（都覆盖 architecture/components/data flow/error handling/testing，见 brainstorming SKILL.md 第 91 行），若两者串联会产生两个设计层的冲突或重复。
- brainstorming-preset 没有 STEP_RESULT 契约、没有编排模式、`allowed_write_paths` 概念（它甚至自行 commit），无法被 4p12s-delivery-orchestrator 的事务模型（"构造路径包并调用对应子 Skill→等待 STEP_RESULT→复核产物"，orchestrator SKILL.md 第 156–171 行）纳管。作为"四步流程"的第 0 步，它是异构体系的拼接，不是同一条流水线的一环。

### 1.2 评估二问：约束是否完备？

**结论：结构性约束（ID 制度、覆盖闭包、写边界、层级制度）相当完备，已接近可机检；语义性约束（翻译忠实、跨产物一致性、验收标准质量）基本停留在 advisory 层，且存在若干具体缺口。**

完备的结构性约束（规则证据）：

- **ID 制度**：九类前缀分型（BR/FUNC/RULE/FLOW/FIELD/UI/PERM/NFR/INT，4p12s-requirements 第 88–100 行）+"已有登记中已有 ID 不得重新编号"（第 102 行）+ ID 所有权划分（"`US-xxx`、`AC-xxx`、`SC-xxx` 三类 ID 由 `user-stories.md` 拥有"，`TC-xxx` 由 verification-plan 拥有，user-stories 第 102 行、verification-plan 第 145 行）+ 下游"不要创建新的用户故事、验收场景或场景用例 ID"（technical-design 第 110 行）。这是完整的 ID 生命周期治理。
- **跨产物引用约束**："设计引用的 `US-xxx`、`AC-xxx`、`SC-xxx` 必须存在于上游 `user-stories.md` 中"（technical-design 第 109 行）；"测试用例引用的 `US-xxx`、`AC-xxx`、`SC-xxx` 都存在于上游"（verification-plan 门禁，第 161 行）。悬引用被明文禁止。
- **澄清 ID 隔离**："澄清问题 ID（`Q-001`）是证据 ID，不是源需求 ID"（requirements 第 114 行），且 PRD/user-stories/design 三处均重复"不要使用澄清问题 ID 作为唯一链接来源/独立源需求"（prd 第 121 行、user-stories 第 110 行、design 第 118 行）——防"证据冒充需求"的约束贯彻了四层。
- **写边界与越权禁令**：每个 skill 的"边界"节（如 requirements 第 169–173 行"不创建 prd.md……不更新 delivery-state.md"）+ orchestrator 的越界写入复核（"是否存在越界写入"，第 254 行）。
- **验证层级制度**：五级层级（unit→cross_boundary_e2e）+ "跨模块、跨服务、持久化状态变更、权限、审计、用户关键路径默认不可降级"（verification-plan 第 149 行）+ 降级必须给理由的字段模板（user-stories 第 77–78 行）。

语义性约束的缺口（静态可预见）：

1. **无翻译忠实度约束**。requirements 要求"保留原始业务含义，不将业务请求翻译为技术方案"（第 105 行），prd 要求"保留 business 含义"（第 112 行），但全文没有任何"逐条对照/回译/翻译审计"机制——"结构化表述"是否忠实于"原文摘录"完全无人校验。按备忘 §8.2 的语言，翻译审计点没有前移，漏译/弱译/添译在下游不可见。
2. **无跨产物语义一致性约束**。所有门禁检查的是 ID 的*存在性*（"每个需求 ID 都有设计承接"），不检查 ID 所指的*语义*是否在传递中被改义。PRD 的验收标准**没有分配 ID**（prd.md 模板第 99–102 行只有"验收项|通过标准|关联需求 ID"三列），下游只能靠名称字符串引用——名义映射天然不可机检。
3. **"可观察可测试"无判定准则**。"验收标准必须是可观察和可测试的"（prd 第 113 行）是祈使句，没有给出可检验的判别式（什么样的通过标准算不可观察？无示例、无反例、无检查清单）。
4. **brainstorming 的 spec 评审是软门**。spec-document-reviewer-prompt.md 的 Calibration 明示 "Approve unless there are serious gaps"（第 34 行），且五类检查项（Completeness/Consistency/Clarity/Scope/YAGNI）全部依赖 reviewer 自由裁量；self-review 也只有四条口头检查（brainstorming 第 118–126 行）。
5. **ID 分型表封闭但无扩展规则**。九类前缀是闭集，未规定"新型需求（如交付物、考试特定的工程验收项）如何分型"——这直接导致动态评估中 DEL-* 的私造（见 §2.2 D-1）。
6. **门禁全部自报**。每个 skill 的"质量门禁：返回前验证"是 LLM 自查清单，orchestrator 的复核范围是"产物结构是否符合对应 Step 的质量门禁"（orchestrator 第 253 行）——结构复核，且对"命令是否真的跑过、测试是否真的绿"依赖 STEP_RESULT 的诚实性，无独立核验设计。

### 1.3 评估三问：能否起到保障成果质量的作用？

**结论：对"结构性质量"（覆盖、可追溯、层级与阻断纪律）能提供实质保障；对"语义性质量"（忠实、一致、验收有效性）保障薄弱——门禁体系恰好验证了备忘 §8.5 的判断：这是"链接存在性"的拓扑代理，不是"语义蕴含"的信息代理。**

能提供保障的部分（规则证据）：

- UI 信号防降级："不要将前端交互信号降级为仅 `NFR-*`"（requirements 第 110 行）+ "没有前端交互信号被仅降级为 `NFR-*`、风格描述或人工验收措辞"（门禁第 146 行）+ "每个范围内的 `UI-*` 需求必须出现在用户角色/场景、功能范围、流程和验收标准中"（prd 第 114 行）+ "范围内的前端或用户交互验收默认为 `cross_boundary_e2e`，必须标记为 Git 阻断"（user-stories 第 108 行）+ "前端 E2E 用例不能只依赖静态渲染、loading、路由导航或纯 UI 断言"（verification-plan 第 152 行）。这是一条四层联动的专项质量链，设计上是全流程最硬的部分。
- 前端范围防静默丢弃："除非 requirements-register.md 明确排除前端，否则不要将前端范围移到范围外"（prd 第 115 行）/ "前端范围没有在上游无明确排除时移到范围外"（design 门禁第 129 行）。
- Git 阻断贯通：user-stories 的每个 AC 必填"是否阻断 Git"（模板第 80 行）→ verification-plan"Git 阻断验收项必须有提交前验证证据或列为阻断项"（第 146 行）→ orchestrator"E2E 阶段没有根据 verification-plan.md 编写或补齐目标测试代码"属禁止事项（第 283 行）。
- 终点定义防假完成："PRD、设计、任务完成、验证通过、Git push 都不是终点"（orchestrator 第 47 行），唯一完成条件要求真实发布调用证据（第 39–45 行）。
- 缺口显式化通道：每个产物都有"待确认问题/缺口与阻断/风险与开放问题"固定章节，且"保持未解决的非阻断性问题明确"（prd 第 118 行）——Z_真 的显式化机制在模板层是存在的。

不能保障的部分：

- 门禁判定者是 LLM 自己，无确定性检查器兜底（对照研究设计原则 1"一切判定走确定性检查器"——本 skill 集全部判定都是 advisory 自查）。
- 无语义对照机制，"保留业务含义"类规则无验证手段（1.2 缺口 1、2）。
- brainstorming 一段的质量保障依赖用户逐段批准（"Ask after each section whether it looks right so far"，第 92 行），是把 Z_真 交还给人逐个消解的 CC 式路线，与 4p12s 的"自动推进、门禁兜底"路线混用时，两段的质量假设不可通约。

---

## 2. 动态评估

### 2.1 核验方法

1. 逐字精读全部 19 个产物文件（requirements-register/prd/user-stories/design/verification-plan/verification-result/delivery-state/deploy-log/tasks/index + TASK-001~010）。
2. 用 Python 脚本做确定性核验（脚本不落盘，内联执行）：需求 ID 闭包（登记→PRD→US→design 映射→verification-plan）、US/AC/SC 悬引用扫描（design/vp/tasks/state/result 全部下游文件）、PRD 验收标准→AC 映射、DE→TC 映射、AC→TC 映射、场景总览与 AC 块内字段一致性（最低验证层级、Git 阻断）。
3. 对照真实代码库抽查产物声明的真实性（backend/src 状态机实现、store.ts 内存层、测试文件计数、RULE-003 枚举落地）。

### 2.2 发现清单（含缺陷实例与文件位置）

**A. 门禁执行良好、被脚本证实的部分**

- **ID 闭包基本成立**：登记 21 个需求 ID，PRD 全文覆盖 21/21；下游五个文件（design/verification-plan/tasks/state/verification-result）共引用 US/AC/SC 三类 ID，**零悬引用**（脚本扫描确认）。DE-01~18 全部进入 verification-plan 设计元素验证映射；AC-001~013 全部有 TC 承接（AC-012 有 TC-012+TC-014 双用例）。
- **场景总览与 AC 块自洽**：13 个 AC 的"最低验证层级""是否阻断 Git"在总览表与块内完全一致（脚本比对）。
- **结果文件的数量声明真实**：verification-result 称"后端 16 测试（db.test.ts 3 + api.test.ts 13）、前端 7 测试"——实测代码库锚定正则计数正好 13+3 与 7，一致。
- **终点纪律真实执行**：项目无发布入口，release_trigger 诚实 blocked 而非伪造完成——delivery-state.md 第 5–9 行（`workflow_status: blocked`，blocking_reason 具体列出无 deploy.sh/Makefile/CI/发布命令）、deploy-log.md 第 27–43 行。git_push 证据链完整（commit 6af7b33、远端 HEAD 比对，deploy-log.md 第 12–23 行）。orchestrator 的"blocked 即停"硬规则被忠实执行。

**B. 缺陷实例（按严重度排序）**

- **D-1（语义漂移，最重要）**：PRD 与 user-stories 对"操作人员通过/驳回"语义直接矛盾，ID 映射却全程绿灯。
  - requirements-register.md 第 37–38 行：FLOW-001/FLOW-002 均为"操作人员通过/驳回基于自动审批结果并复用本状态机"。
  - prd.md 第 46 行（主流程第 5 步）"业务操作人员基于自动审批结果对订单执行通过/驳回/完成等状态流转"；第 52 行（异常流程）"不得绕过审批结果直接执行状态变更"；第 112 行（验收标准 M3 状态流转）"支持通过、驳回、完成等状态流转……操作人员的通过/驳回基于自动审批结果"；第 123 行（待确认问题）再次确认"已明确：操作人员通过/驳回基于自动审批结果"。
  - user-stories.md 第 277 行（US-006 范围外）"操作员人工通过/驳回环节"；第 297 行（AC-010 Then）"无需操作员二次执行通过/驳回"；第 390 行缺口表把 PRD 的"已明确"改写成"已明确：自动审批即生效，操作员仅处理 active→closed 完成流转"。
  - 漂移随后贯穿 design.md 第 33 行（范围外）、verification-plan.md 第 66 行（范围外）、tasks/index.md 第 17 行（范围外）、verification-result.md 第 83 行，直至代码 backend/src/services/loanOrderService.ts 第 49/65 行注释"自动审批即生效"。
  - 要点：AC-010 仍引用 PRD 验收标准名"M3 状态流转"、仍挂 FLOW-001/FLOW-002——**链接存在性门禁全过，语义已被改义收窄**。这精确证伪了"ID 闭包门禁足以保障产物流质量"的隐含假设，证实了静态缺口 2。

- **D-2（ID 分型越界）**：requirements-register.md 第 47–48 行私造 `DEL-001/DEL-002` 两个前缀，不在 skill 规定的九类分型内（4p12s-requirements 第 88–100 行）。"按需求类型分配稳定 ID"规则无"其他类型"条款，门禁也没有"前缀必须在分型表内"一条，执行者只能自造，下游全盘继承。

- **D-3（RULE-003 全程漏映射，门禁未拦）**：`RULE-003`（贷款用途固定枚举）在 PRD 中有覆盖（prd.md 第 66、79 行），但从 user-stories 起彻底消失：脚本核验 user-stories / design 需求到设计映射 / verification-plan 三处均缺 RULE-003（同时缺的还有 BR-001/BR-002，属业务目标尚可辩解，RULE-003 是具体校验规则）。违反 user-stories 门禁"每个范围内需求 ID 都映射到至少一个 `US-xxx`"（第 118 行）与 design 门禁"每个范围内的需求 ID 都有设计承接或已记录的原因"（第 124 行）。讽刺的是代码里枚举真实实现了（backend/src/types.ts、frontend/src/views/BorrowerForm.vue 含装修/教育/旅游/医疗）——**产物链漏报而实现未漏，说明门禁既未拦住文档缺陷，也未能反映真实工程状态**。

- **D-4（验证降级大面积发生，远超已声明范围）**：verification-plan 对所有用例设定"是否允许降级验证：否"，且"所需真实服务类型：MySQL""禁止 mock 数据库"（第 18、23、25、26 行等）。实际：环境无 MySQL/Docker，后端以内存数据层 `backend/src/store.ts` 替代（verification-result.md 第 15 行自述），**全部** service_api/service_integration 用例（TC-003/007/008/010/011）跑在内存库上。结果文件只为 TC-014 写了降级说明（第 30–32 行），其余用例的"MySQL→内存库"实质降级无任何降级理由记录——"是否允许降级验证：否 + 降级理由必填"的制度在执行期被绕过，且 orchestrator 复核未拦。
- **D-5（E2E 层级降级）**：TC-005（最低层级 cross_boundary_e2e、不允许降级）在 E2E 阶段的执行方式是"组件测试断言缺必填阻止提交（borrowerForm.spec.ts 断言 borrowerApi.create 未被调用）"（verification-result.md 第 71 行）——组件层断言替代跨边界 E2E，无降级说明。integration 结论第 49 行自述"cross_boundary_e2e 用例……已在组件层验证渲染与交互"，与 verification-plan 第 152 行"前端 E2E 用例不能只依赖静态渲染……纯 UI 断言"的要求存在张力（浏览器级 Playwright 确实跑了 TC-001/002/004/006/009，属部分执行）。

- **D-6（PRD 验收标准无 ID 导致的名义漂移）**：PRD 验收项"M1 删除"在 user-stories 场景总览中写作"M1 删除（级联）"（user-stories.md 第 16 行 vs prd.md 第 107 行）。13 项验收标准按名称字符串比对时 1 项失配（脚本核验）。名称即键，键无 ID 制度保护，改一个字映射即断。

- **D-7（溯源缺口与错误引用）**：登记中 FLOW-001 的结构化表述新增了三项源摘录中不存在的约束——draft 起始点、rejected 终态、级联删除（requirements-register.md 第 37 行，原文摘录仅"status(pending/approved/rejected/active/closed)"），但澄清记录 Q-001~Q-003（第 54–61 行）只覆盖评分语义/用途枚举/费率来源，**这些关键决策无任何澄清溯源**。PRD 继而把 LoanOrder 状态口径的来源错标为"澄清 Q-001"（prd.md 第 77 行）——Q-001 实为评分规则问题。这是静态缺口 1（无翻译审计）的动态实证：Z_真 被静默消解且事后引用链失真。

- **D-8（小一致性问题）**：verification-plan 验证覆盖表不含 TC-014 行（该用例只出现在 DE 映射与用例详节），覆盖表与用例表之间存在视图不一致；deploy-log 记录最新提交 f80f174 与功能提交 6af7b33 并存但 state 只记后者（delivery-state.md 第 25 行）——皆为轻微账本不齐。

### 2.3 静态-动态对照

| # | 静态结论 | 动态裁决 | 证据 |
|---|---|---|---|
| 1 | ID 制度、引用闭包、写边界等结构性约束完备可机检 | **证实** | 21 需求 ID、US/AC/SC 全链零悬引用；DE 18/18、AC 13/13 有 TC（§2.2-A） |
| 2 | 缺口显式化通道（待确认/缺口/风险章节）存在 | **证实** | 评分默认值、费率默认值以非阻断待决项沿 PRD→US→design→vp→tasks 五层传递并最终在实现中落地（阈值 60、利率 8% 见 verification-result 第 73–74 行） |
| 3 | 终点定义+自动推进+blocked 即停的编排纪律 | **证实** | release_trigger 诚实 blocked，git push 不当终点（delivery-state 第 5–9 行） |
| 4 | 语义忠实无约束（翻译审计缺失） | **证实为真实风险** | D-7：FLOW-001 三项约束无溯源注入+Q-001 错误引用 |
| 5 | 跨产物语义一致性无门禁（ID 存在性≠语义蕴含） | **证实为真实风险，且是最大缺陷** | D-1：操作员通过/驳回语义被改义，全链门禁绿灯 |
| 6 | "验收标准可观察可测试"不可判定 | **部分证实** | PRD 验收标准普遍合格（本案源头是考题自带验收标准，选择偏差存在）；但 D-6 显示连"名称稳定性"都无保障 |
| 7 | 降级需理由+关键路径不可降级的层级制度 | **证伪（执行期失效）** | D-4/D-5：MySQL→内存库全局降级、E2E→组件测试降级，均未走"降级理由"字段，orchestrator 未拦 |
| 8 | 门禁自报、无独立核验 | **证实为真实风险** | D-3：RULE-003 漏映射穿透三道自报门禁；D-4 同理 |
| 9 | UI 防降级四层联动链 | **大体证实，但有裂缝** | 四个 UI 需求全映射且 5 个 cross_boundary_e2e 用例 Git 阻断；裂缝在 AC-003/AC-010 两处"申请人/操作员交互"以 service_api 为最低层级（user-stories 第 16、23 行），"默认为 cross_boundary_e2e"的规则未触发 |

**静态未预见的新发现**：

- **N-1（产物链漏报与真实实现可以脱节）**：RULE-003 在文档链消失却在代码中实现（D-3）。静态评估假设"门禁管产物、产物管实现"，未预见"实现越过产物直接满足需求"这一逆向断裂——追溯矩阵由此双向失真。
- **N-2（名义映射的脆弱性比预想更低层）**：PRD 验收标准没有 ID 不止是"不可机检"，而是已经在单次真实交付中发生了名称漂移（D-6）。问题不是潜在风险而是既发事实。
- **N-3（溯源失真的复合形态）**：D-7 中"无溯源注入"与"错误溯源标注"同时出现——后者更危险，因为它给下游一种"已经澄清过"的假确定性（Z_真 被伪装成 Z_伪）。
- **N-4（环境约束驱动的降级是制度盲区）**：降级制度按"用例个别降级+理由"设计，实际发生的却是"环境级整体降级"（无 MySQL→内存库），制度没有"全局降级如何声明与审批"的入口。

---

## 3. 总评

这套 skill 流程在结构治理上是成熟设计：ID 分型与所有权、跨产物引用闭包、唯一产物+写边界、验证层级与 Git 阻断、缺口显式化章节、终点定义与 blocked 纪律——这些在真实交付中大部分被证实有效，且编排器在无发布入口时的诚实阻断是整套体系最有说服力的正面证据。以备忘 §8.4 的语言说，它把"覆盖完备性"这一层的 Z_真 消解做得很好。

但它的质量保障有一个结构性天花板：**所有门禁判定都是 LLM 自报的 advisory 检查，检查对象是链接存在性而非语义蕴含**。动态评估给出的三个最重缺陷——操作员语义被改义而门禁全绿（D-1）、FLOW-001 约束无溯源注入且被错标澄清来源（D-7）、RULE-003 穿透三道覆盖门禁（D-3）——全部落在天花板之上。降级制度（D-4/D-5）的失效则说明：即使规则文本写对了层级与理由要求，没有独立执行核验，执行期压力（环境缺 MySQL、E2E 成本高）会静默绕过。

对照本项目 README 的设计原则，差距是明确且可修复的：①把"每步返回前验证"的自报门禁脚本化（本评估的 ID 闭包脚本 50 行即完成，证明"引用完整性"检查器成本极低——对应 R2 的引用完整性脚本）；②给 PRD 验收标准分配稳定 ID，把名义映射变为 ID 映射；③在 requirements 登记环节增加"结构化表述↔原文摘录"的逐条对照与决策溯源字段（每项非原文直出的约束必须挂澄清 ID 或显式决策记录），即翻译审计点前移；④为降级增设"环境级降级"声明入口并要求 orchestrator 在复核时比对 verification-plan 的"所需真实服务类型"与 verification-result 的实际执行环境。至于语义忠实（D-1 类），它与上游备忘的判断一致——这是不可判定层，只能靠预期实例测试与分歧度度量兜底，门禁制度本身无法闭合。

一句话结论：**该流程能把"需求文档链的拓扑完整性"工程化到接近可机检的水平（动态证实），但"需求语义的忠实传递"目前全靠执行者自律（动态证伪了三处），距离"信息质量有确定性判定"的目标，差的正是研究计划中 R2/R4 要补的那两层：检查器与分歧度门禁。**
