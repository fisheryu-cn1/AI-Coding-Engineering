# 模型绑定清单（model-bindings）

> **这是什么**：需求 ID 与形式化模型元素的机器可查对照。翻译位维护，检查器 `tools/scripts/check_model_bindings.py` 消费。
> **为什么**：回填实验 A 证明"枚举静默丢失"对 HermiT/pySHACL 双层不可见（缺省世界=一致）——缺失类缺陷的唯一确定性防线是本清单的反向闭包：每个已接受的非豁免需求必须有 ≥1 个**可解析**的模型落点。
> **状态标记**（说明列前缀）：无 = 已绑定；`[暂缓]` = 当前词表无法承接但已指明承接路径（不是豁免）。

## 豁免政策（policy）

| 范围 | 类型 | 理由 |
|---|---|---|
| BR-* | 前缀豁免 | 业务目标陈述，非对象/规则/流程（同 review/30-翻译审计-S3.md TA1-09 行注） |
| UI-* | 前缀豁免 | 界面需求，实现在前端层，不入形式化模型 |
| NFR-* | 前缀豁免 | 工程验收（构建），R5 门禁域 |
| DEL-* | 前缀豁免 | 交付物清单，项目管理层 |
| FUNC-001 | 逐条豁免 | 申请信息 CRUD——通用增删改查界面行为，结构由 FIELD-001 本体承载，无独立模型语义 |
| FUNC-003 | 逐条豁免 | 合同详情查看——展示行为（同 UI-004），无独立模型语义 |

## 绑定表（bindings）

| 需求ID | 工件 | 元素定位符 | 说明 |
|---|---|---|---|
| FIELD-001 | formal/concept-model.puml | class:Borrower | 7 属性全量在此类下 |
| FIELD-002 | formal/concept-model.puml | class:LoanOrder | borrower_id 由 places 关联承接（D-裁决对接简化） |
| FIELD-003 | formal/concept-model.puml | class:CreditResult | decision 字段弱化待 D-B（审计表已记） |
| FUNC-002 | formal/flow-model.puml | trans:pending&gt;approved | 可形式化核心=提交触发自动审批；其记录 CRUD 属 FUNC-001 同类豁免范围 |
| RULE-001 | formal/rules_z3.py | z3tag:R1_达标通过 | 数值规则归 Z3；阈值默认 60 为 Z1 决策默认值 |
| RULE-002 | （暂缓） | （无） | [暂缓] 必填/格式校验需 SHACL cardinality 词表（缺口③）——词表就位后绑定 sh:minCount 组 |
| RULE-003 | formal/concept-model.puml | disjoint:LoanPurpose_ | 枚举互斥=承接主体；配套 enum:LoanPurpose |
| RULE-004 | formal/concept-model.puml | decision:RULE-004 | 外部配置衔接点决策注解（@decision 行）；费率默认值编码待 Z2 |
| FLOW-001 | formal/concept-model.puml | disjoint:OrderStatus_ | 六态互斥（模型部分） |
| FLOW-001 | formal/flow-model.puml | trans:rejected&gt;__END__ | 流转部分=流程线承载；rejected 终态不可回流断言在 fsm_check |
| FLOW-002 | formal/flow-model.puml | trans:active&gt;closed | 完成流转；处理意见记录为标签文本约束（R4 场景检验域） |

## 定位符语法（供检查器与人工双向核对）

`class:X` / `enum:X` / `attr:C.A` / `assoc:L` / `disjoint:前缀_` / `decision:关键词` —— 于 PlantUML 文本匹配；
`z3tag:T` —— 于 Python 文本子串匹配（须出现在 assert_and_track 规则名中）；
`trans:A&gt;B` —— 于状态图 `A --> B` 迁移行匹配，`B=__END__` 表示终态（`X --> [*]`）。

> 维护纪律：绑定行变更 = 模型元素变更的一部分，随 .puml/.py 同一提交变更；检查器 FAIL 时禁止只改清单不改模型的"迁就式修复"（反懒惰红线）。
