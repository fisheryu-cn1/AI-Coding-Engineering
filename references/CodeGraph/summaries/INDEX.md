# CodeGraph 主题论文摘要索引

> 主题：代码图谱、仓库级结构、LLM 编码 Agent 的图表示
> 文件数：12
> 生成日期：2026-08-12

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-代码图谱教材.md](01-代码图谱教材.md) | CodeGraph: A Foundational Textbook/Survey on Code Graphs | 代码图谱综述/教材级参考 |
| 02 | [02-代码属性图漏洞建模与发现.md](02-代码属性图漏洞建模与发现.md) | Modeling and Discovering Vulnerabilities with Code Property Graphs | CPG 用于漏洞建模与发现 |
| 03 | [03-RepoGraph仓库级代码图谱增强AI软件工程.md](03-RepoGraph仓库级代码图谱增强AI软件工程.md) | RepoGraph: Enhancing AI Software Engineering with Repository-Level Code Graph | RepoGraph（仓库级图谱用于编码 Agent）主版本 |
| 04 | [04-RepoGraph同题另一版本.md](04-RepoGraph同题另一版本.md) | RepoGraph（同题另一版） | 与 03 互补的另一版（不同侧重） |
| 05 | [05-基于规约的代码-文本-代码.md](05-基于规约的代码-文本-代码.md) | Specification-Based Code–Text–Code Reengineering for LLM-Mediated Software Evolution | 规约驱动的"代码-文本-代码"循环 |
| 06 | [06-可安全审计的LLM智能体图表示.md](06-可安全审计的LLM智能体图表示.md) | Towards Security-Auditable LLM Agents: A Unified Graph Representation | 安全审计的 Agent 统一图表示 |
| 07 | [07-LLM智能体看代码仓库.md](07-LLM智能体看代码仓库.md) | LLM Agents Can See Code Repositories | Agent 视角的仓库观察方法 |
| 08 | [08-TICoder代码仓库检索.md](08-TICoder代码仓库检索.md) | TICoder: A Repository-Level Code Generation Framework with Test-Driven Planning and Implementation-Aware Reuse | 测试驱动 + 实现感知的代码生成 |
| 09 | [09-SWE_Explore仓库探索.md](09-SWE_Explore仓库探索.md) | SWE-Explore: Benchmarking How Coding Agents Explore Repositories | 编码 Agent 仓库探索行为的基准 |
| 10 | [10-CodeNib多视图数据系统.md](10-CodeNib多视图数据系统.md) | CodeNib: A Multi-View Data System for Serving Repository Context to Coding Agents | 多视图仓库上下文供给服务 |
| 11 | [11-CODENS代码变更转文档.md](11-CODENS代码变更转文档.md) | CODENS: Transforming Code Changes into Living, Accessible, and Queryable Documentation | 代码变更 → 可查询文档 |
| 12 | [12-TraceDev需求到代码追溯.md](12-TraceDev需求到代码追溯.md) | TraceDev: A Traceability-Driven Multi-agent Framework for Requirement-to-Code Development | 需求→代码的多 Agent 追溯框架 |

## 推荐先读

- **想理解代码图谱基本概念**：01 → 02 → 03
- **编码 Agent 与仓库交互**：09 → 10 → 07
- **仓库级上下文供给如何服务 Agent**：10 → 03 → 11

## 与 GraphIt-KB 的相关性

- 论文 03（RepoGraph）与 GraphIt-KB 的核心场景强相关——"把仓库级图谱作为编码 Agent 的上下文"是 GraphIt 设计初衷之一；GraphIt-KB 的"主题索引 + 章节级图谱 + 检索"是更轻量级的近似。
- 论文 10（CodeNib）的"多视图服务"模式可作为 GraphIt-KB Web UI 文档页"左章节树 / 中内容 / 右关联"布局的设计参照。
- 论文 06（可安全审计的 Agent 图表示）与 GraphIt-KB 的"Web UI 写操作锁约定"思路一致——把写动作表达为可审计的图变更。