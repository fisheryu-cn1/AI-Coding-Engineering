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
