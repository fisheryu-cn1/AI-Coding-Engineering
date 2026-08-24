# AIOS 主题论文摘要索引

> 主题：LLM Agent 操作系统、Agent 基础设施与 Harness 演化
> 文件数：14
> 生成日期：2026-08-12（2026-08-24 增补 12、13）

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-LLM操作系统与Agent应用.md](01-LLM操作系统与Agent应用.md) | LLM as OS, Agents as Apps: Envisioning AIOS, Agents and the AIOS-Agent Ecosystem | 提出"AIOS = LLM 操作系统、Agent = 应用"的愿景 |
| 02 | [02-AIOS_LLM智能体操作系统.md](02-AIOS_LLM智能体操作系统.md) | AIOS: LLM Agent Operating System | AIOS 原型：调度/上下文/工具/内存管理 |
| 03 | [03-MemOS记忆增强生成.md](03-MemOS记忆增强生成.md) | MemOS: An Operating System for Memory-Augmented Generation (MAG) in LLMs | 把"记忆"作为一等公民的 OS 抽象 |
| 04 | [04-Anthropic2026Agentic编码趋势.md](04-Anthropic2026Agentic编码趋势.md) | 2026 Agentic Coding Trends Report | 编码 Agent 趋势综述（业界观察） |
| 05a | [05a-LLM作为数据库管理员.md](05a-LLM作为数据库管理员.md) | LLM As DBA | LLM 做 DBA 的自动化方案 |
| 05b | [05b-D-Bot数据库诊断系统.md](05b-D-Bot数据库诊断系统.md) | D-Bot: Database Diagnosis System using LLMs | 数据库自动诊断的 Agent 系统 |
| 06 | [06-PublicAgent多Agent数据开放分析.md](06-PublicAgent多Agent数据开放分析.md) | PublicAgent: Multi-Agent Design Principles From an LLM-Based Open Data Analysis Framework | 多 Agent 数据分析的设计原则 |
| 07 | [07-LLM即代码_Agent程序化编程.md](07-LLM即代码_Agent程序化编程.md) | LLM-as-Code: Agentic Programming for Agent Harness | "LLM 即代码"——把 Harness 当程序化对象 |
| 08 | [08-ActPlane内核级Agent策略执行.md](08-ActPlane内核级Agent策略执行.md) | ActPlane: Programmable OS-Level Policy Enforcement for Agent Harnesses | OS 内核级策略执行（沙箱/权限） |
| 09 | [09-RepoRescue_兼容性救援评测.md](09-RepoRescue_兼容性救援评测.md) | RepoRescue: An Empirical Study of LLM Agents on Whole-Repository Compatibility Rescue | 仓库级兼容性救援评测 |
| 10 | [10-Agent_Harness演化与质量回归.md](10-Agent_Harness演化与质量回归.md) | Don't Blame the LLM: How Agent Harness Evolution Shapes Coding Agent Quality | Harness 演化决定 Agent 质量（关键反直觉发现） |
| 11 | [11-ICAE_Bench交互式项目构建评测.md](11-ICAE_Bench交互式项目构建评测.md) | ICAE-Bench: Evaluating Coding Agents as Interactive Project Builders | 交互式项目构建的 Agent 评测基准 |
| 12 | [12-走向代理操作系统.md](12-走向代理操作系统.md) | Towards an Agent Operating System - Lessons from Classical and Cloud OS | Agent-OS 标准化纲领：13 原语 + 语义鸿沟方法论 |
| 13 | [13-下一代LLM计算光子芯片.md](13-下一代LLM计算光子芯片.md) | What Is Next for LLMs? Next-Generation AI Computing Hardware Using Photonic Chips | 光子芯片 LLM 硬件综述（冯·诺依曼瓶颈仅限硬件层论述） |

## 推荐先读

- **想理解 LLM OS 愿景**：先读 01 → 02 → 03
- **想理解 Harness/Agent 演化与质量**：10 → 07 → 08 → 11
- **想要评测基准**：11 → 09；09 + 11 = 不同粒度的评测
- **想理解 OS 类比的学术工程化谱系与边界**：01 → 02 → 12（12 给出"harness≈OS"类比的语义条件与失效边界）
- **要核实冯·诺依曼瓶颈的硬件层论述**：13（§4.1 / §7.1）

## 与 GraphIt-KB 的相关性

- AIOS 系列提供 Agent 运行时的抽象（调度、内存、上下文管理），GraphIt-KB 的 Inbox/审阅流可借鉴其"任务 + 内存"模型。
- 论文 07（LLM-as-Code）、08（ActPlane）、10（Harness Evolution）直接支撑 GraphIt-KB 评分模块（MCP 配置 + 注册表 + 失败降级）的设计依据。
- 评测基准 11 可作为 GraphIt-KB 自动收集中"评分模块是否真的更准"的对照实验。