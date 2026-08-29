你是软件设计分析员。任务：从设计文档提取完整 UML 模型（概念类图+状态机），**包括为类设计的方法及其逻辑细节描述**。

输入（只读）：D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\design-code-uml\raw\design.md
输出两个文件：
1. D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\design-code-uml\formal\design-concept.puml —— 概念类图
2. D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\design-code-uml\formal\design-flow.puml —— 状态机（若设计文档有状态流转描述）

提取规则：
1. **类**：设计文档提到的领域实体类（如 Borrower/LoanOrder/CreditResult——以文档实际名称为准）+设计的服务/模块层（若文档描述了服务、控制器、数据层）。每类：属性（+name : Type 格式）+**方法**（+name(参数) : 返回值 格式）。
2. **方法与逻辑描述（本任务核心）**：为每个领域类/服务类设计方法——方法名与签名从设计文档的描述推导（如"自动审批按评分规则计算"→ LoanOrder.approve() 或 CreditResult.evaluate()，以文档语义为准）；每个方法上方或类注释区用 PlantUML 注释行写逻辑描述：' @logic <方法名>: <一两句逻辑细节，注明 design.md 出处节号>。设计文档未明确的方法不要发明。
3. **枚举**：文档出现的枚举（如状态、用途类型）用 enum X { ... }，字面量逐行。
4. **语法约定（必须遵守）**：类定义必须带花括号（class X { ... }，空类也要 {}）；方法行格式 +name(args) : Ret；关联 A "1" --> "0..*" B : label；单引号开头为注释行。
5. **状态机**（design-flow.puml）：若文档描述状态流转（如订单状态迁移），用 [*] --> state / a --> b : 事件 语法完整建模，终态 --> [*]。

完成后输出：提取到的类清单（名称+方法数）与状态机状态清单，以及任何你认为设计文档含糊或缺失、无法决定建模的点（如实列出）。
