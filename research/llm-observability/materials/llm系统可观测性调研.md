# LLM 作为核心组件的软件系统可观测性与评估——调研报告

> 状态：已完成初稿（2026-08-17）

服务方向三（`research/llm-observability/`）主题 A：LLM 核心软件的可观测性评估。按三个研究问题组织：

- **RQ-A1 可观测设计**：观测点分层、日志契约、开销与采样、隐私治理、与三支柱的关系；
- **RQ-A2 数据收集与整理**：OTel GenAI 语义约定、OpenInference、trace 数据模型、轨迹与产物的统一组织、评测数据集管理；
- **RQ-A3 迭代决策支持**：离线/在线评估闭环、LLM-as-judge 信度、漂移检测、A/B 与灰度、回归门禁。

**证据强度标记**（全文通用）：

| 标记 | 含义 |
|---|---|
| 【实证】 | arXiv 论文（含实验数据，可能未经同行评审终稿） |
| 【规范】 | 官方标准/规范文档（OTel、OpenInference、官方产品文档） |
| 【商业】 | 厂商博客、竞品对比页（有立场偏差，仅作功能面参考） |
| 【本地】 | 本仓库已有材料（pi 框架、DSH、VISTA、Agentic QA，未重新调研） |

---

## 1. A1：如何在系统设计中加入可观测设计

### 1.1 观测点分层

跨来源汇总，LLM 系统的观测点可归为五层，自上而下构成一棵 trace 树：

| 层 | 观测对象 | 标准承载 | 证据 |
|---|---|---|---|
| L1 Agent 循环层 | agent 的计划/推理步骤、循环轮次、子 agent 委派 | OTel `invoke_agent` 父 span；OpenInference `AGENT` span kind | 【规范】[OTel 博客](https://opentelemetry.io/blog/2026/genai-observability/)、[OpenInference spec](https://arize-ai.github.io/openinference/spec/traces) |
| L2 Provider 请求边界 | 每次模型调用：模型名、token 数、finish reason、延迟 | `chat` span + `gen_ai.*` 属性；指标 `gen_ai.client.operation.duration` / `gen_ai.client.token.usage` | 【规范】[OTel 博客](https://opentelemetry.io/blog/2026/genai-observability/) |
| L3 工具调用边界 | 工具名、参数、结果、异常（含 MCP 工具） | `execute_tool` span；OTel GenAI 仓库含 MCP 专有约定 | 【规范】[semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) |
| L4 会话/轨迹层 | 多轮会话结构、用户/成本归因 | Langfuse session/user 实体；OpenInference trace 树 | 【规范】[Langfuse docs](https://langfuse.com/docs) |
| L5 中间产物层 | 送入上下文的文档/代码/检索结果等工件 | OpenInference `Retriever`/`Reranker` span 的 document 属性；Weave objects 版本化产物 | 【规范】[OpenInference](https://arize-ai.github.io/openinference/spec/traces)、[W&B Weave](https://docs.wandb.ai/weave) |

要点与含义：

- **OTel 官方给出的参考 trace 形态**是一个 `invoke_agent` 父 span，子节点为每轮 LLM 调用的 `chat` span 与每次工具调用的 `execute_tool` span——这等于官方背书了"agent 循环作为 trace 根、provider/工具边界作为内层"的分层结构【规范】。
- 工程意义：观测点应预埋在**边界**（provider SDK 包装层、工具注册/分发层）而非散落在业务代码里；OTel/OpenInference 的自动 instrumentation 正是这么做的（OpenInference 提供 33+ 框架的自动埋点【商业，[Arize AX 文档](https://arize.com/docs/ax/concepts/otel-openinference/overview)】）。
- 本地参照：pi 框架的 telemetry/evals 包、DSH 会话日志即 L4/L5 层的现成实现（见 §6）【本地】。

### 1.2 日志契约："模型可见即落盘"（model-visible means logged）

- 本地 DSH 的会话日志不变量：**凡进入模型上下文的内容全量落盘**，因为复现、调试、评估都依赖真实上下文而非理想化重放【本地】。
- 与标准的对照：OTel GenAI 采取**相反默认**——内容捕获（`gen_ai.input.messages`、`gen_ai.output.messages`、`gen_ai.system_instructions`、工具参数/结果）默认关闭、需显式 opt-in，理由是"提示与工具参数可能含敏感数据"；默认只发元数据（模型名、token 数、时长）【规范】[OTel 博客](https://opentelemetry.io/blog/2026/genai-observability/)。
- 两者不矛盾而是一个设计空间的两端：**采集端契约**（落盘粒度：元数据-only vs 全量上下文）与**治理端契约**（谁能看、存多久、如何脱敏）可以解耦——DSH 把"落盘"作为不变量保证可复现性，把"使用"交给治理层；OTel 把风险在采集端就压到最低。对研究方向三而言，这是一个值得形式化的张力点：分层可见性（本地全量 + 导出脱敏 + 访问分级）。
- 学术侧的支撑：HarnessFix 表明，把执行轨迹编译为可分析的中间表示、并对失败做步骤级归因，能产出经回归验证的修复（基准提升 6.3%–18.4%）——即"轨迹可落盘、可结构化"直接产生迭代价值【实证】[arXiv:2606.06324](https://arxiv.org/abs/2606.06324)。

### 1.3 观测开销与采样策略

- **内容捕获是主要开销源**：prompt/completion 体积远大于元数据；OTel 用默认关闭缓解【规范】[OTel 博客](https://opentelemetry.io/blog/2026/genai-observability/)。
- **评估本身的开销**：对每条轨迹都跑 LLM-as-judge 成本高。最新实证（failure-aware observability）采用**选择性 judge**（在线信号 + 语义接地指标先筛、再对可疑段做 LLM 评估），并发现大量 token 浪费发生在"早预警信号已出现之后"——观测的价值不仅在经济 itself，还在于触发提前干预【实证】[arXiv:2606.01365](https://arxiv.org/abs/2606.01365)。
- **采样**：OTel 生态通用的头部采样（按 trace 丢弃）/尾部采样（按"错误或慢"保留全量）策略可直接迁移到 LLM 轨迹：正常轨迹低比例采样、失败/超时/高成本轨迹全量保留。此为工程共识性做法，属设计建议而非规范。
- 与本地问题的关联：notes 中"观测的观测"（观测体系自身成本与信度如何度量）正对应这一层【本地】。

### 1.4 隐私与数据治理（PII 脱敏）

- OTel 官方《Handling Sensitive Data》指南 + Collector 的 **redaction processor**（正则删除/打码）与 attributes processor（丢弃/改写属性）是标准抓手【规范】[opentelemetry.io/docs/security/handling-sensitive-data](https://opentelemetry.io/docs/security/handling-sensitive-data/)。
- OpenInference 规范明确要求：prompt/completion 常含个人信息，必须可在导出前按字段粒度 mask【规范】[OpenInference spec](https://arize-ai.github.io/openinference/spec/)；Arize AX 落地为 regex 或 Microsoft Presidio 两种打码路径【商业】[Arize AX: mask & redact](https://arize.com/docs/ax/instrument/mask-and-redact-data)。
- 常见管道模式：应用内（导出前 wrapper）→ Collector（集中 redaction）→ 存储（加密+访问控制）。厂商文档（Dynatrace、Dash0 等）一致采用 collector 级集中脱敏【商业】[Dynatrace redact](https://docs.dynatrace.com/docs/ingest-from-opentelemetry/collector/use-cases/redact)。
- 对 DSH 式"全量落盘"契约的启示：全量采集与合规并不必然冲突——脱敏放在导出边界（本地存储 → 对外平台）而非采集边界，前提是本地存储本身有访问治理。这与本仓库 manifest+SHA256+红线校验的数据治理链路同构【本地，`notes/00` §4】。

### 1.5 与传统可观测性三支柱（logs/metrics/traces）的关系

- **统一在 OTel 信号体系内**：GenAI 约定同时定义 spans（结构：agent/chat/tool 树）、metrics（`gen_ai.client.operation.duration` 延迟直方图、`gen_ai.client.token.usage` token 计量，可按模型过滤）、events/logs（流式 token 事件、异常）——即"第四类观测量（内容与质量）被折叠回三支柱，用属性与事件承载"【规范】[OTel 博客](https://opentelemetry.io/blog/2026/genai-observability/)、[semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai)。
- **超出三支柱的部分**：任务质量（成功率、幻觉率、评分）没有传统支柱对应物。工业上的做法是新增第一类实体：OpenInference 定义 `Evaluator` span kind 与 Guardrail span kind【规范】；Langfuse 用独立的 scores 实体（numeric/boolean/categorical，`POST /api/public/scores` 写入）【规范】[Langfuse docs](https://langfuse.com/docs)。
- 定位结论（供 RQ-A1 引用）：运行面（延迟/token/成本/异常）可完全复用三支柱与既有 APM；质量面是增量，需要"评估即数据"的新实体与新的采集契约——这正是方向三的定位价值。

---

## 2. A2：如何有效收集和整理观测数据

### 2.1 OpenTelemetry GenAI 语义约定

【规范】来源：[opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/)（迁移公告）与独立仓库 [github.com/open-telemetry/semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai)。

- **现状**：GenAI 约定已从核心 semconv 仓库**迁出到专用仓库**，覆盖 GenAI 客户端、agent、MCP 及 provider 专有约定（OpenAI/Anthropic/AWS Bedrock/Azure 等）；用 Weaver 管理对核心约定的依赖；提供 Python 合规矩阵等参考实现。注意：schema URL 仍标 TODO、整体仍处演进期（非 frozen stable），引用时应锁定版本。
- **关键 span 属性**：`gen_ai.request.model`、`gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`、`gen_ai.response.finish_reasons`；opt-in 内容：`gen_ai.system_instructions`、`gen_ai.input.messages`、`gen_ai.output.messages`【规范，OTel 博客转述】。
- **关键指标**：`gen_ai.client.operation.duration`（延迟直方图）、`gen_ai.client.token.usage`（输入/输出 token 计量）——直接服务成本核算与延迟回归检测【规范】。
- **生态采纳**：Datadog（v1.37+ 原生摄取）、Dynatrace、MLflow 等已支持；此前 OpenLLMetry 的约定已并入 OTel【商业+规范】[Datadog 博客](https://www.datadoghq.com/blog/llm-otel-semantic-convention/)、[Dynatrace 社区帖](https://community.dynatrace.com/t5/OTel/OpenLLMetry-semantic-conventions-are-now-part-of-OpenTelemetry/td-p/267984)、[MLflow 文档](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/genai-semconv/)。

### 2.2 OpenInference（Arize 发起的开放规范）

【规范】来源：[spec/traces](https://arize-ai.github.io/openinference/spec/traces)、[GitHub spec/traces.md](https://github.com/Arize-ai/openinference/blob/main/spec/traces.md)、[OTel 与 OpenInference 关系](https://arize.com/docs/ax/concepts/otel-openinference/overview)。

- **定位**：构建在 OTel 之上的 AI 应用语义约定（"OTel 管管道，OpenInference 管含义"）。
- **span kind 枚举**（存于属性 `openinference.span.kind`）：`CHAIN` / `RETRIEVER` / `RERANKER` / `LLM` / `EMBEDDING` / `AGENT` / `TOOL` / `GUARDRAIL` / `EVALUATOR` / `PROMPT`——比 OTel GenAI 当前约定更细（多了 Guardrail、Evaluator、Reranker、Embedding），尤其 `EVALUATOR` 把"评估"本身建模为 span，是质量面数据化的关键设计。
- **通用属性**：`input.value` / `output.value`（+ mime_type）、`llm.input_messages`（内含 `message.role` / `message.content`）；span events 承载时点事件（如首 token）；span status：Unset/Ok/Error。
- **规范性要求**：属性键值非空、类型受限（string/bool/number 及数组）；敏感内容须可按字段 mask（见 §1.4）。

### 2.3 trace/span 数据模型；轨迹与产物的统一组织

- **数据模型主干**：trace（树）→ span（名称/父子/时间戳/属性/事件/状态）→ session/user 维度聚合（Langfuse 以 session 支持多轮会话与用户级成本归因【规范】[Langfuse docs](https://langfuse.com/docs)）；产物侧 Weave 用 objects 对任意工件做版本化，使"轨迹中引用的产物"可追溯、可比对【规范】[W&B Weave](https://docs.wandb.ai/weave)。
- **轨迹（trajectory）作为一等数据的实证样板**：
  - MAST-Data：1600+ 条标注轨迹、14 种失败模式 3 大类，来自 7 个多 agent 框架——证明"原始轨迹 → 人工标注 → 结构化失败分类数据集"的管线可行且有价值【实证】[arXiv:2503.13657](https://arxiv.org/abs/2503.13657)。
  - Who&When 数据集：127 个系统的 LLM 调用日志，标注了"哪个 agent、哪一步"两级失败归因【实证】[arXiv:2505.00212](https://arxiv.org/abs/2505.00212)。
- **统一组织的核心难题**：轨迹（时间树、行为）与产物（内容、版本）分属两种粒度，工业界尚未统一模型；Langfuse/Weave/Phoenix 各自为政。本方向的机会：以"轨迹节点引用产物哈希"的方式把产物锚进轨迹（与本仓库 manifest + SHA256 的治理方式同构【本地】）。
- **采集面**：网关式采集（LiteLLM 等 LLM 网关导出 OTLP）正在成为不侵入业务代码的主流路径【规范+商业，[Langfuse docs](https://langfuse.com/docs)】。

### 2.4 评测数据集管理

- 工业共识形态（各家均具备）：从生产 trace 一键转为 dataset → dataset 版本化 → 实验对比（prompt/model 两变量）：
  - LangSmith：datasets + evaluators + annotation queues【规范】[docs.smith.langchain.com](https://docs.smith.langchain.com)；
  - Langfuse：datasets + experiments（UI 内无代码对比 prompt/model）+ annotation queues【规范】[Langfuse docs](https://langfuse.com/docs)；
  - Weave：dataset 版本化 + evaluation run 追踪【规范】[Weave evaluations](https://docs.wandb.ai/weave/guides/core-types/evaluations)；
  - Braintrust：experiments 为主轴，强调"上线前定义好 evals"【规范】[braintrust.dev/docs/evaluate](https://www.braintrust.dev/docs/evaluate)。
- 学术侧对应：Agent-as-a-Judge 的 DevAI 基准把"层级化需求（55 任务 365 需求）"作为数据集组织单元，比单条 pass/fail 更接近真实迭代需要【实证】[arXiv:2410.10934](https://arxiv.org/abs/2410.10934)。
- 与 Hamel Husain 方法论的衔接（已了解，仅定位）：其"错误分析优先、从生产数据长出小而毒的评测集"路径，正需要 §2.3 的"trace → dataset"管道作为工程底座。

---

## 3. A3：如何根据积累数据为系统迭代提供决策支持

### 3.1 离线评估（补充 Hamel 方法论之外的新方法）

- **Agent-as-a-Judge**：用 agent 系统评估 agent 系统，对**中间过程**（而非仅最终输出）给出反馈；在 DevAI 上与人类评估可靠性相当、优于普通 LLM-as-judge【实证】[arXiv:2410.10934](https://arxiv.org/abs/2410.10934)。
- **评测方法谱系综述**：《Survey on Evaluation of LLM-based Agents》从基础能力/应用基准/通用 agent/维度/框架五个视角梳理，指出成本效率、安全、鲁棒性维度仍缺【实证】[arXiv:2503.16416](https://arxiv.org/abs/2503.16416)；《A Survey on LLM-as-a-Judge》系统化 judge 的偏差与治理方法，并给出 judge 可靠性基准【实证】[arXiv:2411.15594](https://arxiv.org/abs/2411.15594)。
- **轨迹条件化评测**：DiagEval 提出对交互式软件按"轨迹条件"评测（静态分析不够，需执行）【实证】[arXiv:2605.17439](https://arxiv.org/abs/2605.17439)。

### 3.2 在线评估（用户反馈与接管信号）

- **平台机制**：Langfuse 支持在生产 trace 上跑在线 evals（judge/代码评估器/用户反馈三类）与 annotation queues 人工标注；Braintrust 的 online scoring 对生产数据持续打分【规范】[Langfuse docs](https://langfuse.com/docs)、[Braintrust docs](https://www.braintrust.dev/docs)。
- **用户接管/干预信号**：未见标准化术语或统一基准（"takeover rate"在 LLM agent 语境下无成熟文献），但相邻实证支持其有效性：
  - Agentic ROI 论证 agent 的信息质量是以"agent 时间 + **用户监督** + 基础设施"为代价换来的——用户监督/干预应作为质量-成本联合指标的一等公民【实证】[arXiv:2505.17767](https://arxiv.org/html/2505.17767v1)；
  - 2026 年对生产个人助理 agent 的 8 周纵向研究发现最危险的失败类别是"模型把错误包装成流畅可信叙事交付用户"（fail-plausible）——这类失败恰恰只能靠用户侧信号（接管、追问、纠正）暴露【实证】[arXiv:2606.14589](https://arxiv.org/abs/2606.14589)。
- 结论：接管率/修正率适合作为**在线质量代理指标**自研（区分"接管=质量差"与"接管=用户谨慎"需结合上下文），证据强度属于"有相邻实证支持的设计建议"。

### 3.3 LLM-as-judge 的信度问题

- **位置偏差**：系统性研究提出交换稳定性/重复稳定性等度量，偏差随 judge 模型与任务形式变化；缓解靠交换-平均【实证】[arXiv:2406.07791](https://arxiv.org/abs/2406.07791)。
- **自我偏好**：NeurIPS 2024 工作揭示其机制在于**困惑度**——模型偏爱自己的输出因为困惑度低，而非身份意识；后续工作给出统计度量与校准方法【实证】[arXiv:2410.21819](https://arxiv.org/abs/2410.21819)、[arXiv:2508.06709](https://arxiv.org/abs/2508.06709)。
- **工程化缓解清单**（综合上述实证 + 平台文档）：rubric 化评分标准、交换平均、多 judge 共识、与人工标注对齐的抽样校准、judge 版本固化（judge 本身变更要纳入回归门禁）。
- 与本地 Agentic QA 的关联：judge 的信度问题直接决定"自动质量门禁"的可信上限【本地】。

### 3.4 漂移检测

- 学术基线：对文本分布漂移，**embedding + MMD**（最大均值差异）优于传统 PSI/KL 关键词特征法——为 LLM 输入/输出漂移检测提供了方法锚点【实证】[arXiv:2312.02337](https://arxiv.org/abs/2312.02337)。
- 工业实践：AWS 规范性指引给出生产 LLM 漂移监控框架（输入分布偏移 + 质量退化两类）【规范】[AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/gen-ai-lifecycle-operational-excellence/prod-monitoring-drift.html)；LangKit/Galileo 等提供现成漂移监控【商业】[Galileo 盘点](https://galileo.ai/blog/best-llm-output-drift-monitoring-platforms)。
- LLM 系统特有的第三类漂移：**上游模型/路由变更引发的 Silent 回归**（同 prompt 不同模型版本）——这是评测门禁（§3.5）而非统计检测的职责，也是本方向"能力预算锚点（pass^k）"的动机之一【本地，notes/00 §2】。

### 3.5 A/B、灰度与回归门禁

- **PR 级门禁**：promptfoo 提供官方 GitHub Action，监控 prompt/配置文件变更 → 自动运行 eval → pass-rate 低于阈值则阻断合并，断言类型含确定性检查、LLM-judge、相似度、红队【规范，开源】[promptfoo CI/CD](https://www.promptfoo.dev/docs/integrations/ci-cd/)、[promptfoo-action](https://github.com/promptfoo/promptfoo-action)。
- **实验对比**：Braintrust experiments / Langfuse prompt 版本 + labels（无代码变更切流量）+ 版本间延迟/成本/质量对比【规范】[Braintrust](https://www.braintrust.dev/docs/evaluate)、[Langfuse docs](https://langfuse.com/docs)。
- **回归的"检出盲区"实证**：HarnessFix 专门针对"harness 缺陷"（工具配置/提示/流程编排层面的错误），其修复以**回归验证的补丁**形式交付——印证本方向判断：通用 CI 检不出 harness/prompt 层质量回归，需要 trace 接地的专用机制【实证】[arXiv:2606.06324](https://arxiv.org/abs/2606.06324)。这与本地 Agentic QA 的结论一致【本地】。
- **早预警干预**：failure-aware observability 显示"预警信号出现后的干预"能显著削减浪费计算——把观测从事后取证推进到运行中干预【实证】[arXiv:2606.01365](https://arxiv.org/abs/2606.01365)。

### 3.6 错误分析驱动的优先级排序（决策框架）

- **MAST 分类学**：14 种失败模式 × 3 大类（系统设计、agent 间错位、任务验证缺位），可直接作为"下个迭代修什么"的优先级框架（本地 notes 已引 FC3 = 验证缺位占 23.5% 作为动机）【实证】[arXiv:2503.13657](https://arxiv.org/abs/2503.13657)。
- **自动化失败归因仍是开放问题**：Who&When 基准上最强推理模型表现也很差——"从轨迹自动定位哪个 agent 哪一步出错"远未解决，当前迭代决策仍需人工错误分析为主、自动归因为辅【实证】[arXiv:2505.00212](https://arxiv.org/abs/2505.00212)。
- **agent 框架本身的失败谱**：34 个可编程任务基准 + 三层失败原因分类，指出规划与自诊断是主要短板【实证】[arXiv:2508.13143](https://arxiv.org/abs/2508.13143)。
- **事故复盘制度化**：《Incident Analysis for AI Agents》借用传统事故报告框架，提出 agent 事故应记录的三类因素（系统/情境/认知）与开发者应保留的信息清单——为"LLM 系统事故复盘"提供规范起点【实证】[arXiv:2508.14231](https://arxiv.org/abs/2508.14231)。

---

## 4. 工业平台功能盘点

每家 3-5 句，URL 附后。对比结论部分参考了第三方横评【商业】：[Digital Applied 2026 横评](https://www.digitalapplied.com/blog/agent-observability-platforms-langsmith-langfuse-arize-2026)、[ZenML 对比](https://www.zenml.io/blog/langfuse-vs-phoenix)、[Pydantic 计价口径对比](https://pydantic.dev/articles/ai-observability-pricing-comparison)。

| 平台 | 核心定位与功能 | trace 模型 | 评估能力 | 形态 |
|---|---|---|---|---|
| **LangSmith**（LangChain） | LangChain/LangGraph 原生最深集成；datasets、evaluators、prompt 管理（commit 历史）、annotation queues、automations、监控与告警 | agent/run 树，框架原生 run schema | 在线评估器跑生产 trace；人工标注队列；版本对比 | 闭源 SaaS（座位+用量计价）。[docs](https://docs.smith.langchain.com)、[官方对比页](https://www.langchain.com/resources/langsmith-vs-arize) |
| **Langfuse** | 框架无关的开源可观测；100+ 集成；session/user 成本归因；prompt 版本+labels 热切换 | 基于 OTel 的 trace 树（OTLP 原生摄取） | 在线 evals（judge/代码/用户反馈）+ 离线 datasets/experiments + annotation queues + scores API | 开源可自部署（核心开源，云版用量计价）。[docs](https://langfuse.com/docs) |
| **Arize Phoenix** | OpenInference 标准发源地；notebook 内探索式分析强项；Arize AX 为商业版 | OpenInference span 树（10 种 span kind） | LLM-as-judge、检索指标、retrieval/eval notebook 工作流 | 开源可自部署 + Arize 云。[docs](https://arize.com/docs/phoenix/tracing/concepts-tracing/what-are-traces)、[GitHub](https://github.com/Arize-ai/phoenix) |
| **Braintrust** | "主动可观测"：评优先（上线前定义 evals）、experiments、playground 并排对比 prompt/model | experiment → span 树 | remote evals、online scoring、生产监控闭环 | 商业 SaaS + 开源 SDK。[docs](https://www.braintrust.dev/docs)、[evaluate](https://www.braintrust.dev/docs/evaluate) |
| **W&B Weave** | "instrument-everything"：任意函数/LLM 调用自动 trace；objects 产物版本化 | op 树（LLM/tool/generic op） | evaluations against datasets、scorer、跨 run 对比；与 W&B 实验生态打通 | 商业（W&B 生态），SDK 开源。[docs](https://docs.wandb.ai/weave)、[GitHub](https://github.com/wandb/weave) |
| **Honeycomb** | 传统高基数可观测厂商路线：OTLP 原生摄取 GenAI 属性，强项是高基数 ad-hoc 查询与气泡分析 | 标准 OTel span | 无专门 LLM eval 体系（judge/数据集需自建） | 商业 SaaS。[blog](https://www.honeycomb.io/blog/fast-ai-feedback-loops-honeycomb-opentelemetry) |
| **Grafana Cloud（LLMOps）** | OTel + Loki/Tempo/Mimir 承载；OpenLIT 提供开箱 AI 栈监控（成本/token/延迟）；grafana-llm-app 插件统一 LLM 网关 | 标准 OTel | 面板与告警为主，eval 需拼装 | 开源生态 + 云。[指南](https://grafana.com/blog/a-complete-guide-to-llm-observability-with-opentelemetry-and-grafana-cloud/)、[OpenLIT](https://grafana.com/docs/grafana-cloud/observe-and-act/monitor-applications/ai-observability/) |
| **promptfoo**（补充） | 开源评测 + CI 门禁：YAML 声明测试与断言，pass-rate 阈值阻断 PR；含红队 | 本地 eval 结果树 | 断言式评测（确定性/judge/相似度/自定义） | 开源。[CI/CD](https://www.promptfoo.dev/docs/integrations/ci-cd/) |

横向观察（供选型与自建边界决策）：

- **trace 标准正在收敛到 OTel/OTLP**（Langfuse、Honeycomb、Grafana、Datadog 均原生），LangSmith 是最大例外（自有 schema）。
- **评估闭环深度**与**框架绑定深度**成正比：LangSmith（深绑定）> Braintrust/Weave（SDK 绑定）> Langfuse/Phoenix（标准绑定）> Honeycomb/Grafana（不提供）。
- 本地判断：自建方法的合理边界是"OTel GenAI 采集 + 自有质量层（scores/evals/门禁）"，把运行面交给标准【本地，notes/00 §6 末条 + 本报告 §1.5】。

---

## 5. 学术进展（2024–2026 代表性论文）

以下 10 篇均逐一核实过 arXiv 页面（标题/作者/日期/摘要）：

| # | 论文 | 年份 | 证据类型 | 一句话要点 |
|---|---|---|---|---|
| 1 | Why Do Multi-Agent LLM Systems Fail?（MAST）[arXiv:2503.13657](https://arxiv.org/abs/2503.13657) | 2025 | 实证 | 14 种失败模式 3 大类 + 1600+ 标注轨迹数据集；7 个 SOTA 多 agent 系统失败率 41%–86.7% |
| 2 | Which Agent Causes Task Failures and When?（Who&When）[arXiv:2505.00212](https://arxiv.org/abs/2505.00212) | 2025 | 实证 | 首个自动失败归因任务 + 127 系统日志数据集；最强模型表现也差——自动归因是开放问题 |
| 3 | Exploring Autonomous Agents: Why They Fail [arXiv:2508.13143](https://arxiv.org/abs/2508.13143) | 2025 | 实证 | 34 任务基准 + 三层失败分类；规划与自诊断为 agent 框架主要短板 |
| 4 | Incident Analysis for AI Agents [arXiv:2508.14231](https://arxiv.org/abs/2508.14231) | 2025 | 框架 | 借传统事故分析提出 agent 事故报告框架：系统/情境/认知三因素与应留存信息清单 |
| 5 | Early Diagnosis of Wasted Computation in Multi-Agent LLM Systems via Failure-Aware Observability [arXiv:2606.01365](https://arxiv.org/abs/2606.01365) | 2026 | 实证 | 在线信号 + 语义接地 + 选择性 judge 的"失败感知可观测"；大量 token 浪费发生在早预警之后 |
| 6 | From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws（HarnessFix）[arXiv:2606.06324](https://arxiv.org/abs/2606.06324) | 2026 | 实证 | 轨迹编译为中间表示 → 归因到 harness 工件 → 回归验证补丁；基准提升 6.3%–18.4% |
| 7 | When Errors Become Narratives: Silent Failures in a Production LLM Agent Runtime [arXiv:2606.14589](https://arxiv.org/abs/2606.14589) | 2026 | 实证 | 生产 agent 8 周纵向研究：22 起静默失败 5 类；最危险的是"fail-plausible"（错误被包装成可信叙事） |
| 8 | Agent-as-a-Judge [arXiv:2410.10934](https://arxiv.org/abs/2410.10934) | 2024 | 方法+基准 | 用 agent 评 agent、对中间过程给反馈；DevAI 基准（55 任务 365 层级需求） |
| 9 | A Systematic Study of Position Bias in LLM-as-a-Judge [arXiv:2406.07791](https://arxiv.org/abs/2406.07791) | 2024 | 实证 | 位置偏差的系统度量（交换/重复稳定性）；随 judge 模型与形式变化 |
| 10 | Self-Preference Bias in LLM-as-a-Judge [arXiv:2410.21819](https://arxiv.org/abs/2410.21819) | 2024 | 实证 | 自我偏好源于低困惑度而非身份意识；可量化与缓解 |

辅助参考（未逐篇深核，正文已标注）：LLM-as-judge 综述 [arXiv:2411.15594](https://arxiv.org/abs/2411.15594)（已核）、agent 评估综述 [arXiv:2503.16416](https://arxiv.org/abs/2503.16416)（已核）、文本分布漂移 embedding-MMD [arXiv:2312.02337](https://arxiv.org/abs/2312.02337)、self-bias 统计度量 [arXiv:2508.06709](https://arxiv.org/abs/2508.06709)、DiagEval [arXiv:2605.17439](https://arxiv.org/abs/2605.17439)、Agentic ROI [arXiv:2505.17767](https://arxiv.org/html/2505.17767v1)。

趋势小结：2024 年集中在 judge 信度；2025 年转向 agent/多 agent 失败实证与事故框架；**2026 年出现"observability"直接进入论文标题**（#5 #6 #7），且都以生产轨迹为数据源——与本方向"观测数据是迭代资产"的立论高度合拍。

---

## 6. 与本地框架机制的关系（已有材料，仅引用）

- **pi 框架 telemetry/evals 包**【本地，`custom-agent/materials/` 两份框架调研】：L1–L3 层观测点的现成开源实现参照，可作为实验载体。
- **DSH 会话日志不变量（model-visible means logged）**【本地】：与 OTel "内容默认关闭"构成日志契约设计空间的两个端点（§1.2），是本方向可形式化的核心命题。
- **VISTA 仪表盘**【本地，`references/ContextEngineering/22`】：上下文占用/本体感受观测的原型，对应运行面的"上下文占用"指标。
- **Agentic QA（harness 质量回归）**【本地，`references/AIOS/10`】：与 HarnessFix（#6）互证——通用 CI 检不出 harness 层质量回归，需 trace 接地的专用门禁。
- **manifest + SHA256 + 摘要层治理**【本地，`design/kb-app/`，notes/00 §4】：观测数据治理（RQ-A2）在文档域的已实现参照，可与 §2.3 的"产物锚定进轨迹"设计对接。

---

## 7. 综合结论与研究机会

1. **运行面已标准化，质量面没有**：延迟/token/成本/异常有 OTel GenAI + 三支柱兜底；任务成功率/幻觉率/接管率仍缺统一数据契约——方向三的增量应放在质量层（scores/evals 实体 + 门禁语义），而非再造 trace 管道。
2. **日志契约是可研究的设计空间**："全量落盘 + 导出治理"（DSH 式）与"默认元数据 + opt-in 内容"（OTel 式）两端之间，分层可见性/采样/脱敏的组合尚无系统化研究。
3. **轨迹→资产管线是实证热点但自动化程度低**：MAST/Who&When 证明标注轨迹的价值，也证明自动归因之难；"从生产轨迹半自动长出评测集"（Hamel 方法论的工程化）是清晰的系统贡献点。
4. **门禁可信度受制于 judge 信度**：位置/自我偏好偏差的实证已充分，工程化的校准协议（rubric、交换、对齐抽样、judge 版本固化）可作为本方向的方法输出。
5. **在线质量信号（接管率/修正率/fail-plausible 检出）是空白**：2026 年生产纵向研究刚刚开始触及，无标准度量——与"能力预算锚点（pass^k、时间地平线）"结合可形成完整决策框架。
