# 检查运行台账（check-run-log，prd-review-P0151020）

> 本案例全部机器检查证据流水账，只追加不删改。判定标准：tools/scripts/check_doc_closure.py 文档首节；案例背景见 ../reports/PRD评审报告.md。

## Run-1 2026-08-28 PRD 五项闭包检查（触发原因：评审模式开案首检）

```
命令: python tools/scripts/check_doc_closure.py cases/prd-review-P0151020/raw/prd.md \
        cases/prd-review-P0151020/raw/requirements-register.md \
        --accept "## 9. 验收标准" \
        --vocab draft,pending,approved,rejected,active,closed,borrower,loanorder,creditresult \
        --exempt BR-001,BR-002

== check_doc_closure: cases/prd-review-P0151020/raw/prd.md ==
登记 ID 21 | 文档引用 ID 21 | 豁免 ['BR-001', 'BR-002']
A 私造/悬挂: 0 | B 未承接 0 / 弱承接线索 1 | C 验收断点: 1 | D 词表漂移: 1 | E: 触发
FINDING[B]: 弱承接(线索): BR-001 仅出现 1 次
FINDING[C]: 验收断点: RULE-003 在验收节零出现（规则/范围有承接但无验收行）
FINDING[D]: 词表漂移: "rejection" 不在受控词表（最近 "rejected"，出现 1 次）
FINDING[E]: 验收行无 ID 列: 验收节表首列不是 ID/编号/AC——验收行无法被下游精确引用
VERDICT: FINDINGS(4)
```

> 归因：①C 命中即 2026-08-26 三方评估人工发现的核心缺陷（RULE-003 全链丢失的 PRD 侧起点）——脚本独立重现；
> ②D/E 为历次评估未报的新捕获；③A 零命中（无私造前缀，拓扑层干净）；④语义级两项（状态体系混淆/
> 操作员 6 处）由人工定位，见审计表结构级发现节与报告 §1 #5/#6。

## Run-2 2026-08-28 文字—UML—OWL 全链验证（触发原因：评审完整性补齐——用户指出仅文本层不完整）

> S3 翻译（忠实原则：按 PRD 原文编码，不引入我方裁决——六态状态机/操作员双侧语义/decision 译 String）。
> 形式化工件：formal/{concept-model.puml, flow-model.puml, rules_z3.py, model-bindings.md}。

```
== 转换 == OK: concept.owl.rdf（5 类/枚举, 2 关联）+ .shacl.ttl
== HermiT == consistent, classes=15 individuals=10
== Z3 ==
规则集一致性(评分): sat | core: []
操作员双侧规则: sat | core: []        ← OP-1(§4主流程5)与OP-2(§4异常4)互为逆否命题——PRD 内部操作员语义逻辑自洽的形式化证据
费率规则(占位): sat | 注: PRD §10 明确默认值待设计阶段——显式待决
== FSM（六态五迁移，PRD §4/§5 原文口径）==
P1–P4 PASS；P5 no_escape_from=['rejected']: PASS（首跑曾为空配置——P5 无断言≠验证条款，已按 PRD §4 边界原文补挂）
== 绑定闭包 ==
首验 FINDING[A]×2: FUNC-001/003 豁免政策合并书写致解析失败（检查器正确抓到政策表书写错误）；
拆行后: 覆盖 10/10 | 解析 10/10 | 反向 0 | DEFERRED: RULE-002（显式暂缓）| VERDICT: PASS
```

> 归因：①PRD 形式化模型全部检查通过——**PRD 的结构语义（实体/状态机/规则）自身无机器可判定的矛盾**，
> 其缺陷（Run-1 四项+语义两项）全部在承接映射层与语义盲区层，不在形式化层；②操作员双侧 sat 是
> "PRD 内自洽、矛盾在跨文档层"判断的形式化证据（OP-1/OP-2 逆否等价）；③两个过程发现：no_escape
> 空配置≠验证（显式断言才忠实）、豁免政策合并书写被检查器拦截。
