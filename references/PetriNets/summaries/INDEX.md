# PetriNets 主题论文摘要索引

> 主题：Petri 网基础、组合模型检查、工作流验证、可达性分析
> 文件数：6
> 生成日期：2026-08-12

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-Cardoso_PetriNets工作流模型.md](01-Cardoso_PetriNets工作流模型.md) | Petri Nets（Cardoso & Valette 著；译自葡语版 *Redes de Petri*） | Petri 网基础教材（含工作流） |
| 02 | [02-并发系统组合模型检查.md](02-并发系统组合模型检查.md) | Compositional model checking of concurrent systems, with Petri nets | 并发系统的组合模型检查（Sobociński） |
| 03 | [03-PetriNets基础论文.md](03-PetriNets基础论文.md) | Petri Nets: Properties, Analysis and Applications (Murata 1989) | 经典 Petri 网综述（170+ 引用） |
| 04 | [04-PetriNets讲义.md](04-PetriNets讲义.md) | Petri Nets — Lecture Notes (Esparza) | Petri 网决策问题讲义 |
| 05 | [05-组合可达性_Petri网.md](05-组合可达性_Petri网.md) | Reachability via Compositionality in Petri nets | 通过组合性解决可达性（Sobociński & Stephens） |
| 06 | [06-工作流网验证.md](06-工作流网验证.md) | Verification of Workflow Nets (van der Aalst) | 工作流网验证 + WOFLAN 工具 |

## 推荐阅读路线

- **从基础到前沿**：03（Murata 综述）→ 01（Cardoso 教材）→ 04（Esparza 讲义）→ 02（组合模型检查）
- **工作流方向**：06（WF-net 验证）→ 01（Cardoso 第 7–8 章工作流部分）
- **组合可达性专题**：05（论文主体）→ 02（教程风格概述）

## 与 GraphIt-KB 的相关性

- Petri 网对 GraphIt-KB 主要提供**形式化方法参考**——论文 06（工作流网验证）的"健全性 ↔ 活性 + 有界性"思路可作为未来"流水线正确性证明"的灵感来源。
- 论文 03 / 04 的"判定问题 / 半判定 / 高效子类"分层方法学与 GraphIt-KB 的"分层存储 / 分层检索"在思路上平行。
- 本主题当前规模较小（6 篇），作为形式化方法的补充资料，不直接进入核心检索路径。