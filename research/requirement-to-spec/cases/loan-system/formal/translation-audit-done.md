# 翻译审计对照表（loan-system，v1）

> 依据：method/13 §4。审计单位：领域专家（人工）——LLM 可预填，结论列须人复核。
> 覆盖范围：requirements-register.md 的实体/规则/流程类条目（BR/UI/NFR/DEL 类结构性条目不进概念模型，见末节）。

| 条目ID | NL 原文（摘录） | UML 元素 | 采用注解 | 审计结论 |
|---|---|---|---|---|
| FIELD-001 | Borrower: id, name, id_number, phone, income, employer, position | class Borrower 全部属性 | — | 确认 |
| FIELD-002 | LoanOrder: id, borrower_id, amount, term_months, purpose, interest_rate, status | class LoanOrder 属性（borrower_id 由 places 关联承接） | — | 确认，此处是与外部系统对接点，MVP阶段先简化设计 |
| FIELD-003 | CreditResult: id, order_id, score, approved_amount, approved_rate, decision, decision_reason | class CreditResult（order_id→hasDecision 关联；decision→枚举子类待定） | — | **弱化**：decision 字段译为整体类但未拆 decision 值语义，确认 |
| RULE-003 | 贷款用途固定枚举 4 类 | enum LoanPurpose{4} + @disjoint | @disjoint ×1 组 | （结构化承接实证锚点）确认，MVP简化设计 |
| FLOW-001(部分) | OrderStatus 六态；draft 起始、rejected 终态 | enum OrderStatus{6} + @disjoint | @disjoint ×1 组 | **部分**："不可回流"为转换规则，本模型不承载（流程线缺口①） |
| FLOW-002 / Z3待决 | 操作员是否执行通过/驳回 | 未建模——登记为待决注释 | — | **待裁决**（两侧矛盾已知，翻译位采用登记侧语义并声明）确认为原始需求歧义，MVP阶段按最简原则忽略人工处理环节 |
| RULE-001 / Z1 | 评分规则参数化+默认阈值 | rules_z3.py（非 OWL——数值规则归 Z3） | — | 按混合架构分工落位 |
| RULE-004 / Z2 | 合同费率配置默认值 | 同上（未编码——R1 下一步） | — | 确认为缺口，此处应作为MVP系统与外部系统的衔接点，例如：对接一个外部配置文件。MVP初期实现中退化为固定值 |
| FUNC-001~003 | M1/M2/M3 功能模块 | 结构承载于类+关联（行为不在概念模型层） | — | 非本模型职责 |

**不进模型的条目**：BR-001/002（目标）、UI-001~004（界面，实现在前端侧）、NFR-001（构建）、DEL-001/002（交付物）——均为流程/工程约束而非领域本体对象。

**审计结论汇总**：待澄清 1（FLOW-002 方向裁决）；弱化 1（CreditResult.decision）；其余已人工审核。
