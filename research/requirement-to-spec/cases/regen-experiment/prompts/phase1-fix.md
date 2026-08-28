你是需求文档的交付方代理人。你此前产出的《个人消费贷款管理系统》需求登记表经过外部评审，收到以下评审意见与修复方案。请按指令修改登记表。

输入文件（只读）：D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\regen-experiment\raw\requirements-register-orig.md
输出文件（新建，不修改输入件）：D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\regen-experiment\raw\requirements-register-fixed.md

修复指令（共六项，均有评审裁决依据；除这些外不得改动其他内容、不得新增/删除需求条目、不得改动 ID 体系与表格结构）：

1.【状态维度拆分】评审发现：登记表把"单据流程状态"与"审批结果"两个状态体系混在一起（FLOW-001 六态含 approved/rejected，同时 FIELD-003 又有 decision 字段）。修复：将两个维度拆分——
   a) 单据流程状态改为四态：draft（草稿，起始点）→ 提交 → pending（待处理）→ 自动审批 → active（签约生效）→ closed（完成，统一终态；无论审批结果如何，完成全部流程处理后归结到 closed）；
   b) 审批结果独立为 CreditResult.decision 字段的取值集，三值：待审核（审批未出结果）/ approved（通过）/ rejected（拒绝）；
   c) 原"rejected 为终态不可回流 pending"改写为："closed 为统一终态不可重开；审批结果一经形成不可翻转（作为单据属性持久化）"；
   d) 审批通过路径 pending→active、审批拒绝路径 pending→closed，流程节点区分保留用于后续完整版本挂载处理逻辑或外部系统数据交换。
   涉及行：FLOW-001、FIELD-002（status 字段取值）、FIELD-003（decision 字段）、范围与风险表"状态机合法路径"行。

2.【操作员语义消解】评审发现：登记表多处"操作人员执行通过/驳回"与下游用户故事"自动审批即生效"矛盾（原始需求歧义）。裁决：确认为原始需求歧义，MVP 按最简原则处理——自动审批结果即生效，无人工操作环节。修复：FLOW-001/FLOW-002 中所有"操作人员执行通过/驳回"的表述改为自动审批直接驱动状态流转；处理意见记录保留为系统记录的决策原因（decision_reason）；如需保留人工环节表述，只能作为"完整版扩展"注记且不得出现在 MVP 主流程描述中。

3.【decision 取值集】（随指令 1）FIELD-003 结构化表述补明确取值集：decision 取值 ∈ {待审核, approved, rejected}。

4.【费率默认值】裁决输入：年化利率 3.5%、服务费率 1%、逾期罚息率 5%。修复：范围与风险表"固定费率默认值"行补上述默认值（可注"产品确认，配置表可调"）；澄清问题表可补一条 Q-004 记录该确认。

5.【必填与校验清单】裁决输入：金额、期限、身份证、电话四个字段全必填；保存草稿与直接提交同样触发表单校验规则（草稿≠免校验）。修复：RULE-002 结构化表述补上述清单与草稿校验语义。

6.【状态词拼写统一】评审发现下游文档曾出现"rejection"拼写漂移。修复：本表所有状态词严格使用枚举值原文（draft/pending/approved/rejected/active/closed 或拆分后的四态与三值），不得出现变体拼写。

完成后输出修改说明（每项指令的落实位置简述）。
