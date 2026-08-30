# loan-system 案例群：同一实验对象的五轮实验（P0151020）

> 实验对象：giencoder-exam-P0151020《个人消费贷款管理系统》原交付（需求登记/PRD/设计/代码全链产物）。四轮实验按时间序编号，方法形态逐步扩展：构造→评审→对照→代码比对→接口规格锚点。各轮自成体系（raw/formal/review/reports 完整），入口见各目录 README 或 reports/。

| 轮 | 目录 | 时间 | 实验形态 | 核心产出与发现 |
|---|---|---|---|---|
| 01 | [01-fullchain/](01-fullchain/) | 2026-08-26~28 | **构造模式全链**（S0–S6：登记→翻译→OWL→七项检查→人工决策→执行收官） | Run-1~13 台账；D-B 决策发现需求两状态体系混淆；RULE-003 结构化承接实证；绑定闭包/FSM/队列等机制的发源地 |
| 02 | [02-prd-review/](02-prd-review/) | 2026-08-28 | **评审模式首用**（对 PRD 做文本五项+文字→UML→OWL 全链形式化检验） | check_doc_closure 四项确定性发现（RULE-003 验收断点脚本重现等）+两语义发现（状态混淆在 PRD 源头/操作员六处）；评审模式能力边界定形 |
| 03 | [03-regen-experiment/](03-regen-experiment/) | 2026-08-28 | **对照实验**（pi 修复需求+4p12s 重生成 PRD，验证上游修复的传导） | 语义修复 6/6 传导；LLM 再生成引入形近 ID 变体（FULC/FOW）；UML 联合输入的锚定效应（FINDINGS 11→1）；传导三层边界 |
| 04 | [04-design-code-uml/](04-design-code-uml/) | 2026-08-29 | **设计↔代码 UML 比对**（pi 提取设计/代码双 UML 含方法逻辑，GLM 三段比对） | RULE-003 精确终态（TS 类型层回归+运行时缺失）；六态贯穿但 pending 驻留变异；"提取被迫表态"LLM 再现 |
| 05 | [05-openapi-anchor/](05-openapi-anchor/) | 2026-08-30 | **OpenAPI 锚点实验**（pi 程序化反向生成 OpenAPI+design↔代码比对，GLM 六项评审） | 主张"第三规格锚点"成立：20 端点 byte-identical 自动生成；22 条设计声明仅 7 条一致（形近变体 11/未实现 4/超出 2）全部为 UML 通道不可见；形近变体第三载体（路径） |

> 跨轮结论沉淀在 `notes/日志.md`（第 30~33 场）与方法规范（method/13/14/16/17/18）； kb-app 双层/三层检验是另一实验对象，见 `cases/kbapp-review/`。
