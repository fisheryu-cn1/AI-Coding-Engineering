# 评审入口（V00-INDEX，kbapp-review）

> 双层评审案例：01 需求层与 03 设计层分别形式化后做层间溯源。核心交付=《双层检查与层间溯源报告》。

## 图形入口（SVG，人审用；文本为源）

| 图 | 内容 | 层 |
|---|---|---|
| `../formal/concept-01.svg` | 术语概念模型（Document/Section/Chunk/Entity/Topic/Inbox + 双枚举） | 01 需求层 |
| `../formal/flow-01.svg` | Inbox 三档审核流 + Document 墓碑生命周期 | 01 需求层 |
| `../formal/concept-03.svg` | 图谱 Schema（四节点四边 + corpus/kind 枚举） | 03 设计层 |
| `../formal/flow-03.svg` | 变更检测四情形 + Inbox 阈值版 + 三失败终态 | 03 设计层 |

## 只读材料

- 报告：`../reports/双层检查与层间溯源报告.md`（N1-N6/D1-D10 归因）
- 证据：`../reports/check-run-log.md` Run-1
- 被评审件：`../raw/`（01/03 复制件）
