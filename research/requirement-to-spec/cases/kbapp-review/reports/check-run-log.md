# 检查运行台账（kbapp-review）

## Run-1 2026-08-28 双层形式化全链检查（触发原因：开案首检）

```
== 转换 ==
concept-01: OK（8 类/枚举, 6 关联）[首跑失败×2：裸类名 class Chunk / class Topic 违反语法面（须带花括号），
  解析器吞块导致后续类定义丢失——method/13 §2 语法面约定再实证；修复后通过]
concept-03: OK（7 类/枚举, 4 关联）
== HermiT ==
[concept-01] consistent, classes=20 individuals=12
[concept-03] consistent, classes=25 individuals=18
== FSM ==
flow-01（Inbox 三档流+Document 墓碑生命周期）: P1–P5 全 PASS（no_escape=[tombstoned]）
flow-03（变更检测四情形+Inbox 阈值版+三失败终态）: P1–P5 全 PASS（no_escape=[tombstoned, failed, no_text]）
== Z3（01 层）==
FR-6.2 阈值组结构: sat（数值未定——参数化，KD-3 登记）
FR-2.7 成本区间: sat；NFR-4 性能组: sat
== Z3（03 层）==
阈值组自洽: sat sat；降权边界: 0.8×accept(0.56) > reject(0.50) = sat（降档不减档语义——D10）
P4 交集vs并集 反例存在性: sat（例 ct=0.25, dt=1: 交集=0.25 ≤ 上界, 并集=1 击穿）——03"并集击穿"声明证实
```

> 归因：两层结构语义无机器可判矛盾——发现集中于翻译弱化（KD-1/2/3/5）与层间对照（N3 弱化/N4 反向变形/N6 验证缺位/D10 语义交互），见《双层检查与层间溯源报告》。

> **Run-1 附记（2026-08-28）**：四件 UML 的 SVG 已渲染（concept-01/03、flow-01/03，入口见 review/V00-INDEX）。
> 渲染过程修一处语法：no_escape_from 裸行致 PlantUML 报错（loan 案例写在 note 块内故通过）——统一移入 note，
> fsm_check 解析回归验证通过（配置行 note 内可解析）。
