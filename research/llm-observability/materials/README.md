# 方向三：资料归档

按"框架内观测机制 / LLM 系统可观测性 / 开发过程观测"分类。每条资料附一句话摘要与用途标注（对应 RQ-A1~A3 / RQ-B1~B3）。

## 仓库内既有素材（直接输入）

| 资料 | 位置 | 摘要与用途 |
|---|---|---|
| Agent Harness Evolution（Agentic QA） | `references/AIOS/10` | 固定模型下 harness 变更引发质量回归、现行 CI/CD 检不出——RQ-A1/A3 的动机证据与"质量回归门禁"原型 |
| VISTA（LLM Agents Are Latent Context Managers） | `references/ContextEngineering/22` | 本体感受仪表盘：agent 自身上下文状态的实时观测——上下文侧观测点设计参照 |
| ACM: Agentic Context Management | `references/ContextEngineering/28` | 长程任务的上下文管理即观测对象——RQ-A2 数据模型输入 |
| METR 时间地平线 / τ-bench pass^k | `references/AgentParadigms/20、23` | 能力预算与可靠性口径（80% 地平线、pass^k）——RQ-A3 生产配额锚点 |
| MAST 失败分类 | `references/AgentParadigms/15` | FC3 验证缺位 23.5% + 14 种失败模式——错误分析与迭代优先级框架（RQ-A3） |
| METR RCT / GIST 技术债 | `references/SEforLLM/09、10` | 开发者生产力测量方法学（RCT、自感知偏差）与 AI 技术债实证——RQ-B1/B2 |
| DORA 2025 / 团队实践调研 | `custom-agent/materials/团队级AI编码实践调研.md` | 组织级 AI 采纳与交付稳定性相关性、评审负担——RQ-B1~B3 的实证基线 |
| pi telemetry/evals 包、DSH 会话日志不变量 | `custom-agent/materials/pi-mono-架构与定制机制.md、dsh-架构与插件生态.md` | 两框架现成的观测机制（遥测契约、model-visible means logged、evals 框架）——RQ-A1 载体 |
| GraphIt-KB manifest+摘要+校验链 | `design/kb-app/06-摘要构建与命名规范.md` | 文档域观测数据治理的已实现参照（台账-摘要-红线校验三环）——RQ-A2 |
| SE 原理 × LLM 对照 | `agent-software-design/materials/软件工程原理与LLM系统.md` | evals 方法论（Hamel Husain）、蜕变测试——RQ-A3 验证手段 |

## 首轮调研产出（2026-08-17，台账 #7/#8）

| 文档 | 摘要与用途 |
|---|---|
| `materials/llm系统可观测性调研.md` | LLM 核心软件可观测性：观测分层设计、trace 标准（OTel GenAI/OpenInference）、工业平台（LangSmith/Langfuse/Phoenix 等）、学术进展、质量评估与迭代闭环——RQ-A1~A3 |
| `materials/AI辅助开发过程观测调研.md` | AI 辅助开发过程观测：三类对象（人/AI 工具/协同）的量化体系、DORA/SPACE/DevEx 框架、人机协作度量学术进展、落地方法与反模式——RQ-B1~B3 |

## 待收集

- [ ] OpenTelemetry GenAI 语义约定 / OpenInference 规范原文细读
- [ ] LangSmith / Langfuse / Arize Phoenix / Braintrust 等平台的功能矩阵对比（选定参照集）
- [ ] LLM 系统事故复盘（postmortem）案例集
- [ ] 人-AI 结对编程的受控研究（2024–2026）
- [ ] AIDev 数据集（Hassan）与 agent PR 规模化分析方法
