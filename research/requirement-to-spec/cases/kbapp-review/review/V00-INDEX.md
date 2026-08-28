# 评审入口（V00-INDEX，kbapp-review）

> 三层评审案例：01 需求层 / 03 概要设计 / 05 详细设计分别形式化，做层内检验+层间溯源+翻译完整性审计。
> **报告导览（按时间序读）**：①《双层检查与层间溯源报告》（01↔03 轮，源于需求六项/设计新生十项+细化合理性框架 §4）→ ②《三层检验报告-05详细设计》（05 自身+05↔03+05↔01；§8 公共骨架修正；§9 翻译完整性审计与 BDD 首练）。

## 当前状态速览（2026-08-28 续十后）

形式化件 9 件（01×2 / 03×3 / 05×4）全部转换+HermiT 一致；FSM 四张五性质全 PASS；Z3 三组（含判据分歧反例）；绑定闭包 32/32 PASS（FR 体系适配）；决定性 DETERMINISTIC；BDD 首练 6 场景+负控。发现累计：KD-1~13 + N1–N6 + D1–D10（归因见两份报告）。

## 图形入口（SVG，人审用；文本为源）

| 图 | 内容 | 层 |
|---|---|---|
| `../formal/concept-01.svg` | 术语概念模型（六实体+双枚举） | 01 需求层 |
| `../formal/flow-01.svg` | Inbox 三档审核流 + Document 墓碑生命周期 | 01 需求层 |
| `../formal/concept-03.svg` | 图谱 Schema（四节点四边+四枚举，含检索模式） | 03 概要设计 |
| `../formal/flow-03.svg` | 变更检测四情形 + Inbox 阈值版 + 三失败终态 | 03 概要设计 |
| `../formal/flow-03-parse.svg` | 解析三级判定（85% 覆盖率/降级链） | 03 概要设计（Run-3 补） |
| `../formal/concept-05.svg` | SQLite 注册库（files/tasks/inbox+六枚举） | 05 详细设计 |
| `../formal/concept-05-graph.svg` | 图 Schema 落地版（与 03 同骨架，diff 基准） | 05 详细设计（§8 补） |
| `../formal/concept-05-api.svg` | 接口契约（GraphStore/Parser/Scoring 等） | 05 详细设计（Run-3 补） |
| `../formal/flow-05.svg` | tasks 重试机 + files.status 墓碑双语义 | 05 详细设计 |

## 只读材料

- 报告：`../reports/双层检查与层间溯源报告.md`（01↔03 轮，含 §4 细化合理性框架）；`../reports/三层检验报告-05详细设计.md`（05 轮+§8/§9 修正审计）
- 证据：`../reports/check-run-log.md` Run-1~3
- 场景库：`../review/T6-预期场景库.md`（BDD 首练，6 场景+两陷阱实测）
- 绑定：`../formal/model-bindings.md`（FR↔模型 32 行，--id-regex 适配）
- 被评审件：`../raw/`（01/03/05 复制件）
