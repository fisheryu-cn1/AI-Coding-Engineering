# 模型绑定清单（prd-review-P0151020）

> 需求 ID 系 = raw/requirements-register.md（PRD 引用的同一编号系）。豁免政策与 loan-system 一致。
> 评审模式注记：本清单锚定的是"PRD 语义的形式化落点"（翻译忠实于 PRD 原文）。

## 豁免政策（policy）

| 范围 | 类型 | 理由 |
|---|---|---|
| BR-* | 前缀豁免 | 业务目标陈述 |
| UI-* | 前缀豁免 | 界面需求（UI-001 锚点在流程图初始边） |
| NFR-* | 前缀豁免 | 工程验收 |
| DEL-* | 前缀豁免 | 交付物清单 |
| FUNC-001 | 逐条豁免 | CRUD 行为，结构由 FIELD 承载 |
| FUNC-003 | 逐条豁免 | 展示行为，结构由 FIELD/UI 承载 |

## 绑定表（bindings）

| 需求ID | 工件 | 元素定位符 | 说明 |
|---|---|---|---|
| FIELD-001 | formal/concept-model.puml | class:Borrower | PRD §6 七字段原文 |
| FIELD-002 | formal/concept-model.puml | class:LoanOrder | PRD §6 原文含六态 status |
| FIELD-003 | formal/concept-model.puml | class:CreditResult | PRD §6；decision 译 String（PRD 未定义取值集——RD-2 弱化） |
| RULE-001 | formal/rules_z3.py | z3tag:R1_评分达标通过 | PRD §5 评分规则 |
| RULE-002 | （暂缓） | （无） | [暂缓] PRD §5 只述"有基础校验"未列字段清单与规则——弱于登记表口径；承接前置同 loan-system Z4 机制 |
| RULE-003 | formal/concept-model.puml | disjoint:LoanPurpose_ | PRD §5/§6 固定枚举 4 类 |
| RULE-004 | formal/rules_z3.py | z3tag:R4_费率为正 | PRD §5 配置表固定值；默认值 PRD 未给（§10 待确认）——占位+显式待决 |
| FLOW-001 | formal/concept-model.puml | disjoint:OrderStatus_ | PRD §6 六态原文（评审忠实：不用 D-B 四态） |
| FLOW-001 | formal/flow-model.puml | trans:rejected&gt;__END__ | 六态五迁移+no_escape_from=[rejected]（PRD §4 边界原文） |
| FLOW-002 | formal/rules_z3.py | z3tag:OP-1_主流程5 | 操作员语义双侧编码（OP-1/OP-2），处理意见记录为行为语义归 R4 场景 |
| FUNC-002 | formal/flow-model.puml | trans:pending&gt;approved | 提交触发自动审批（PRD §4 主流程 2→3） |
