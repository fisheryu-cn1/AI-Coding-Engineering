# 评审入口（V00-INDEX，intelli-metric）

> 案例状态：UML v0.2（经人工审计修正）+BDD 样板 v0.1。尚未进入 S4 全链检查循环（SHACL 实例闭包待补 ABox 样本）。

## 文件地图

| 文件 | 性质 | 说明 |
|---|---|---|
| [E30-翻译审计表.md](E30-翻译审计表.md) | **E（填写件）** | 第 1 轮人工审计（2026-08-30，用户 15 项发现）：TA1-01~15 全部成立已修正；归因=提取缺失 13（含 3 项未读全文档）+混合 2+需求未明 1.5 |
| [T6-预期场景库.md](T6-预期场景库.md) | E（填写件） | BDD 样板：AI 样例 14 场景（4-5-5，含 SC13/14 审计驱动补充）+✍人工扩充区 |
| [../formal/](../formal/) | G/V | concept-req（30 类+63 方法）/flow-metric（五态 9 迁移）及 SVG/OWL 产物 |
| [../README.md](../README.md) | V | 案例说明+检查状态+@decision 清单 |

## 本次待办（第 1 轮后）

- flow-metric 两个 @decision 待项目方确认：修复定义的版本语义（本版本回退 vs 新版本）/delisted 重新上架语义；
- concept 三个 @decision 待确认：依赖图谱 metric 级补全（需求盲区）/owner 与 manager 关系/元数据统计项可选；
- T6 人工扩充区（六类指引）。
