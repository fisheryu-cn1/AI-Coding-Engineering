# SEforLLM 主题论文摘要索引

> 主题：软件工程 × LLM 系统——LLM 作为软件构件、prompt 作为规约、evals/蜕变测试、神经符号混合架构、AI 编码生产力实证、agent harness 架构与表达力上限、人/机可读性与 spec-as-source
> 文件数：17
> 生成日期：2026-08-17（01–10，精读级 summary_version 3.0）；2026-08-24 增补 11–12（精读级 summary_version 1.0）；2026-08-25 增补 13–17（基于 PDF 全文的精读级 summary_version 1.0——来源：人机可读性分离点两轮讨论，备忘见 `../../../research/人机可读性分离点与验证边界_两轮讨论备忘_2026-08-25.md`）

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-LLM作为软件构件分类学.md](01-LLM作为软件构件分类学.md) | Large Language Models as Software Components: A Taxonomy for LLM-Integrated Applications | LLM 构件五维分类学（调用/功能/prompt/技能/输出） |
| 02 | [02-提示使能系统的软件工程.md](02-提示使能系统的软件工程.md) | Promptware Engineering: Software Engineering for Prompt-Enabled Systems | prompt 作为软件制品的工程化议程 |
| 03 | [03-从LLM到SE智能体综述.md](03-从LLM到SE智能体综述.md) | From LLMs to LLM-based Agents for Software Engineering | LLM/agent × SE 任务映射综述 |
| 04 | [04-蜕变测试与LLM双向赋能综述.md](04-蜕变测试与LLM双向赋能综述.md) | Bidirectional Empowerment of Metamorphic Testing and Large Language Models | MT×LLM 双向综述（无 oracle 测试） |
| 05 | [05-LLM蜕变测试NLP任务.md](05-LLM蜕变测试NLP任务.md) | Metamorphic Testing of Large Language Models for NLP Tasks | 191 条蜕变关系库（ICSME 2025） |
| 06 | [06-LLMORPH自动化蜕变测试.md](06-LLMORPH自动化蜕变测试.md) | LLMORPH: Automated Metamorphic Testing of LLMs | MR 自动生成工具 |
| 07 | [07-神经符号控制混合架构.md](07-神经符号控制混合架构.md) | Neuro-Symbolic Control with Large Language Models for Language-Guided Spatial Tasks | 确定性外壳 + 非确定内核 |
| 08 | [08-协议驱动多智能体工程.md](08-协议驱动多智能体工程.md) | Towards Engineering Multi-Agent LLMs: A Protocol-Driven Approach | 借用 Design by Contract 的协议层 |
| 09 | [09-METR随机对照试验.md](09-METR随机对照试验.md) | Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity | RCT：资深开发者用 AI 慢 19% |
| 10 | [10-生成式AI自认技术债.md](10-生成式AI自认技术债.md) | "TODO: Fix the Mess Gemini Created": GenAI-Induced Self-Admitted Technical Debt | AI 诱导的自认技术债（GIST） |
| 11 | [11-深入ClaudeCode设计空间.md](11-深入ClaudeCode设计空间.md) | Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems | 逆向 Claude Code v2.1.88：queryLoop 单循环 + 五层压缩 + 子代理 sidechain |
| 12 | [12-并行性权衡对数精度Transformer上限.md](12-并行性权衡对数精度Transformer上限.md) | The Parallelism Tradeoff: Limitations of Log-Precision Transformers | 对数精度 transformer ⊆ 一致 TC⁰，实践中非图灵完备 |
| 13 | [13-机器与人类对混淆代码的理解.md](13-机器与人类对混淆代码的理解.md) | Do Machines Struggle Where Humans Do? LLM and Human Comprehension of Obfuscated Code | reasoning 模型与人类混淆代码难度对齐（ρ=0.30–0.47）而 coder/instruct 近零；对抗重命名仅在语义置换×标识符干扰共现时触发高置信错误 |
| 14 | [14-代码屏障LLM理解什么.md](14-代码屏障LLM理解什么.md) | The Code Barrier: What LLMs Actually Understand? | 三类混淆×13 模型：重命名 −18.6pp/加密 −21.4pp/死代码仅 −6.2pp；去混淆任务代码专用反超（功能等价≠清晰恢复） |
| 15 | [15-LLM生成代码可读性问题模式.md](15-LLM生成代码可读性问题模式.md) | Characterizing Readability Issue Patterns and the Role of Prompt Design in LLM-Generated Code | LLM 代码可读性总体与人类相当但失败模式相反；prompt 设计作用有界 |
| 16 | [16-AI编码代理如何修改代码.md](16-AI编码代理如何修改代码.md) | How AI Coding Agents Modify Code: A Large-Scale Study of GitHub Pull Requests | agent PR 与人类差异在变更结构而非规模（commits δ=0.54 大效应、additions 仅小效应）；描述-diff 语义对齐略优 |
| 17 | [17-规约驱动开发从代码到契约.md](17-规约驱动开发从代码到契约.md) | Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants | SDD 三级严格度（spec-first/anchored/as-source）+决策树；核心是 spec 由 advisory 变 enforced |

## 推荐先读

- **"LLM 即构件"主线**：01（分类学）→ 02（prompt 制品化）→ 08（DbC 协议层）
- **验证方法论**：04（MT 综述）→ 05（关系库）→ 06（自动化）→ 07（符号外壳）
- **生产力实证**：09（RCT）→ 10（技术债）
- **harness 架构与理论上限**：11（Claude Code 设计空间）→ 12（并行性权衡）——工程样本与理论边界互证
- **人机可读性与 spec-as-source（2026-08-25 增补）**：13（人机混淆理解对齐缺口）→ 14（受控混淆×13 模型）→ 15（可读性平价但失败模式相反）——命题证据三角；16（agent PR 修改结构）支撑规模控制去向；17 接 `../../FormalMethodsLLM/summaries/INDEX.md`（spec-as-source × 形式验证机制配对）

## 与 GraphIt-KB 的相关性

- 本主题支撑 `research/agent-software-design/` 子问题 B"中间产物作为正确性基础设施"与"prompt 作为规约"类比——GraphIt-KB 自身以 Markdown 产物 + 摘要检索层运行，恰是该命题的一个工程样本。
- 04–06（蜕变测试）提供"验收条件可机检化"的候选机制，可借鉴为 GraphIt-KB 文档变更的弱验证手段；09/10 为团队采纳 AI 工具的实证背景（与 `research/custom-agent/materials/团队级AI编码实践调研.md` 互证）。
- 11 + 12 构成"harness 恢复无界计算"论证的证据对：12 给出裸 transformer ⊆ 一致 TC⁰ 的理论上限（自回归外层循环在其形式模型之外），11 给出生产级 harness（单循环 + 工具 + 外部状态）补足无界性的工程样本；与 `research/agent-software-design/materials/harness与冯诺依曼架构类别关系.md` 直接对应。
- 经典 SE 侧（Parnas/Brooks/DbC/CBSE/形式化规约史）为书籍与早期论文，未入 PDF，梳理见 `research/agent-software-design/materials/软件工程原理与LLM系统.md`。
