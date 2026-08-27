# 模型大纲（人审辅助）

> 人工可读的模型全景。图中看布局（concept-model.svg），这里查细节。状态映射到审计表行。

## 决策注解（Z_真 已消解项）

- @disjoint: OrderStatus_draft, OrderStatus_pending, OrderStatus_approved, OrderStatus_rejected, Order
- @disjoint: LoanPurpose_renovation, LoanPurpose_education, LoanPurpose_travel, LoanPurpose_medical
- 注解说明(RULE-003): 用途枚举4类互斥 —— 本注解行即 RULE-003 在模型层的承接（对照静态评估发现的丢失缺陷）
- 注解说明(FLOW-001): OrderStatus 六态互斥; rejected 为终态的"不可回流"是转换规则非状态互斥, 由流程线承载

## 枚举

- **OrderStatus**: draft | pending | approved | rejected | active | closed
- **LoanPurpose**: renovation | education | travel | medical
- **CreditDecision**: approved | rejected

## 类与属性

- **Borrower**
  - +id : String
  - +name : String
  - +id_number : String
  - +phone : String
  - +income : Decimal
  - +employer : String
  - +position : String
- **LoanOrder**
  - +id : String
  - +amount : Decimal
  - +term_months : Integer
  - +purpose : LoanPurpose
  - +interest_rate : Decimal
  - +status : OrderStatus
- **CreditResult**
  - +score : Integer
  - +approved_amount : Decimal
  - +approved_rate : Decimal
  - +decision_reason : String

## 关联

- Borrower [1] ──places──> LoanOrder [0..*]
- LoanOrder [1] ──hasDecision──> CreditResult [0..1]

## 泛化/语义待决项

- Z1: 评分规则默认阈值/权重取值 (RULE-001) → 决策记录: 配置表+默认60分阈值, 数值约束归 Z3 规则集
- Z2: 固定费率默认值 (RULE-004) → 同上配置表
- Z3: 操作员角色是否执行通过/驳回 (FLOW-002) → **已知矛盾点**: 登记/PRD vs US/design 方向相反,
