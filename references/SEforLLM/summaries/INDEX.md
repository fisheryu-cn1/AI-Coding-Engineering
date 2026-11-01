# SEforLLM 主题论文摘要索引

> 主题：软件工程 × LLM 系统——LLM 作为软件构件、prompt 作为规约、evals/蜕变测试、神经符号混合架构、AI 编码生产力实证、agent harness 架构与表达力上限、人/机可读性与 spec-as-source
> 文件数：23
> 生成日期：2026-08-17（01–10，精读级 summary_version 3.0）；2026-08-24 增补 11–12（精读级 summary_version 1.0）；2026-08-25 增补 13–17（基于 PDF 全文的精读级 summary_version 1.0——来源：人机可读性分离点两轮讨论，备忘见 `../../../research/人机可读性分离点与验证边界_两轮讨论备忘_2026-08-25.md`）；2026-08-30 增补 18–19（反向文档化课题文献，来源：备忘 §13 第 36 场方向再检验·课题 C-2）；2026-09-21 增补 22（人在环中的生成式敏捷开发方法论参考，精读级 summary_version 1.0）、20（Agentic Agile-V 过程控制框架，精读级 summary_version 1.0）、21（AI 生成代码技术债大规模实证，精读级 summary_version 1.0）、23（一人小队棕地企业案例，精读级 summary_version 1.0）

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
| 18 | [18-反向文档工程Reversa.md](18-反向文档工程Reversa.md) | Reversa: A Reverse Documentation Engineering Framework for Converting Legacy Software into Operational Specifications for AI Agents | 反向文档工程（遗留系统→可追溯操作规格）的开山定义+框架；备忘 §13.4-C2 课题生成侧直接先行 |
| 19 | [19-从代码逆向恢复用户故事.md](19-从代码逆向恢复用户故事.md) | Reverse Engineering User Stories from Code using Large Language Models | LLM 从源码恢复用户故事的 prompt 设计实证；反向整理到需求层（比 Reversa 更近业务语义）；C2 课题生成侧 |
| 20 | [20-AgenticAgileV过程控制框架.md](20-AgenticAgileV过程控制框架.md) | Agentic Agile-V: From Vibe Coding to Verified Engineering in Software and Hardware Development | Agile-V 生命周期 + SCOPE-V 任务循环 + R0–R3 风险分级证据门；证据基底：AIDev 932,791 PR、Google RCT −21%、METR +19%、RealBench 系统级 pass@1=0%；无自有实验 |
| 21 | [21-AI生成代码技术债大规模实证.md](21-AI生成代码技术债大规模实证.md) | Debt Behind the AI Boom: A Large-Scale Empirical Study of AI-Generated Code in the Wild | 302.6k AI 归因提交×6,299 仓库 commit 级静态分析；484,366 个引入问题（89.3% code smells）；22.7% 存活至仓库 HEAD（分母 464,900 可追踪问题）；五种工具均 >15% 提交引入问题 |
| 22 | [22-AgileGen人机团队敏捷开发.md](22-AgileGen人机团队敏捷开发.md) | Empowering Agile-Based Generative Software Development through Human-AI Teamwork | 人在迭代两端决策（Gherkin 场景+验收建议）、Agent 中间生成；Pass@1 超 ChatDev_24 16.4%，去 Gherkin 消融 −41.9% |
| 23 | [23-一人小队棕地企业案例.md](23-一人小队棕地企业案例.md) | One Developer Is All You Need: A Case Study of an AI-Augmented One-Person Squad in a Brownfield Enterprise | Itaú 棕地单案例：1 名 staff engineer + 4 Agent 走 SDD，3/6 sprint 交付、AI 代码首审接受 90%、直接人力成本 −88%；约束项是规格质量与机构知识而非模型能力；单案例 n=1 属边界测试 |

## 推荐先读

- **"LLM 即构件"主线**：01（分类学）→ 02（prompt 制品化）→ 08（DbC 协议层）
- **验证方法论**：04（MT 综述）→ 05（关系库）→ 06（自动化）→ 07（符号外壳）
- **生产力实证**：09（RCT）→ 10（自认技术债）→ 21（工具归因技术债：22.7% 存活至 HEAD）——SATD 自述与静态检测两口径互证
- **harness 架构与理论上限**：11（Claude Code 设计空间）→ 12（并行性权衡）——工程样本与理论边界互证
- **人机可读性与 spec-as-source（2026-08-25 增补）**：13（人机混淆理解对齐缺口）→ 14（受控混淆×13 模型）→ 15（可读性平价但失败模式相反）——命题证据三角；16（agent PR 修改结构）支撑规模控制去向；17 接 `../../FormalMethodsLLM/summaries/INDEX.md`（spec-as-source × 形式验证机制配对）
- **人在环中的生成式开发（2026-09-21 增补）**：22（AgileGen：Gherkin 验收标准 + 两端决策 + 轻量迭代）↔ 17（spec-anchored 一级：spec 与代码全程同步）——敏捷人机协作与 SDD 严格度谱系互为参照
- **过程控制与团队形态（2026-09-21 增补）**：20（Agentic Agile-V：conversation-to-contract 门 + R0–R3 风险分级证据门）→ 23（一人小队单案例：规格质量与机构知识是约束项）↔ 17（SDD 严格度谱系）——框架、案例、谱系三视角互证"agentic 时代瓶颈在过程而非 prompt"

## 与 GraphIt-KB 的相关性

- 本主题支撑 `research/agent-software-design/` 子问题 B"中间产物作为正确性基础设施"与"prompt 作为规约"类比——GraphIt-KB 自身以 Markdown 产物 + 摘要检索层运行，恰是该命题的一个工程样本。
- 04–06（蜕变测试）提供"验收条件可机检化"的候选机制，可借鉴为 GraphIt-KB 文档变更的弱验证手段；09/10 为团队采纳 AI 工具的实证背景（与 `research/custom-agent/materials/团队级AI编码实践调研.md` 互证）。
- 11 + 12 构成"harness 恢复无界计算"论证的证据对：12 给出裸 transformer ⊆ 一致 TC⁰ 的理论上限（自回归外层循环在其形式模型之外），11 给出生产级 harness（单循环 + 工具 + 外部状态）补足无界性的工程样本；与 `research/agent-software-design/materials/harness与冯诺依曼架构类别关系.md` 直接对应。
- 经典 SE 侧（Parnas/Brooks/DbC/CBSE/形式化规约史）为书籍与早期论文，未入 PDF，梳理见 `research/agent-software-design/materials/软件工程原理与LLM系统.md`。
