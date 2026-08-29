# [注入演示] 陈旧绑定清单——模型已丢枚举，清单未同步

> 仅用于回填实验 A 的检查器对照。绑定行与 `../formal/model-bindings.md` 完全相同，
> 仅差异：concept-model 相关行工件改指变体 `inj-a-rule003-loss.puml`（RULE-003 枚举已删、@decision 块缺失），
> 其余行按 injection 目录相对路径回指正式件。
> 预期结果：恰好 2 条 B 类 FINDING（disjoint:LoanPurpose_ / decision:RULE-004 无法解析），
> 覆盖与反向闭包维持 PASS——证明信号精确定位在"模型漂移"，证明缺失类缺陷可被机器捕获。

## 豁免政策（policy）

| 范围 | 类型 | 理由 |
|---|---|---|
| BR-* | 前缀豁免 | 业务目标陈述，非对象/规则/流程 |
| UI-* | 前缀豁免 | 界面需求，实现在前端层 |
| NFR-* | 前缀豁免 | 工程验收，R5 门禁域 |
| DEL-* | 前缀豁免 | 交付物清单，项目管理层 |
| FUNC-001 | 逐条豁免 | CRUD 行为，结构由 FIELD-001 承载 |
| FUNC-003 | 逐条豁免 | 详情查看展示行为 |

## 绑定表（bindings）

| 需求ID | 工件 | 元素定位符 | 说明 |
|---|---|---|---|
| FIELD-001 | inj-a-rule003-loss.puml | class:Borrower | 变体中类仍在→应保持 OK |
| FIELD-002 | inj-a-rule003-loss.puml | class:LoanOrder | 同上 |
| FIELD-003 | inj-a-rule003-loss.puml | class:CreditResult | 同上 |
| FUNC-002 | ../formal/flow-model.puml | trans:pending&gt;approved | 正式件 |
| RULE-001 | ../formal/rules_z3.py | z3tag:R1_达标通过 | 正式件 |
| RULE-002 | （暂缓） | （无） | [暂缓] SHACL cardinality 词表落地后承接 |
| RULE-003 | inj-a-rule003-loss.puml | disjoint:LoanPurpose_ | 变体中已删→预期 FAIL |
| RULE-004 | inj-a-rule003-loss.puml | decision:RULE-004 | 变体中无 @decision 块→预期 FAIL |
| FLOW-001 | inj-a-rule003-loss.puml | disjoint:OrderStatus_ | 变体中状态互斥注解仍在→OK |
| FLOW-001 | ../formal/flow-model.puml | trans:rejected&gt;__END__ | 正式件 |
| FLOW-002 | ../formal/flow-model.puml | trans:active&gt;closed | 正式件 |
