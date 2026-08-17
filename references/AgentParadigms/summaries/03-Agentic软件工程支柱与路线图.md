---
title: "Agentic Software Engineering: Foundational Pillars and a Research Roadmap"
source_pdf: "03-Hassan-Agentic_SE_Pillars_Roadmap_v3.pdf"
arxiv_id: "2509.06216"
arxiv_version: "v3"
authors:
  - "Ahmed E. Hassan"
  - "Hao Li"
  - "Dayi Lin"
  - "Bram Adams"
  - "Tse-Hsun Chen"
  - "Yutaro Kashiwa"
year: 2025
venue: "arXiv"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：Agentic 软件工程支柱与路线图（Hassan）

## 1. 适用场景

- 当你要判断**某类 SE 任务该交给 agent 到什么程度**（L2 任务级 agentic vs L3 目标级 agentic vs L4 领域自治）并为决策找坐标系时，读 §2 的 L0–L5 分级框架。
- 当你要**设计人机双工作台**（人类编排/审查侧 + agent 执行侧）或结构化协作工件（任务简报、流程脚本、导师规则、咨询包、合并证据包）时，读 §4.2–§4.3 与 §5。
- 当你要**评估 agent 生成代码是否"可合并"**、需要 SWE-Bench 系列与 GitHub 大规模实证数字做论据时，读 §3.3–§3.4。
- 当你要区分 **1-to-1 agentic coding 与 N-to-N agentic software engineering**、论证团队级治理与可追溯性必要时，读 §6.3。
- 当你要规划 **agent 时代的 SE 研究议程或教育/课程改革**（持久记忆、agent 原生工具链、代码经济学、后 IDE 界面）时，读 §7。

> 锚点：Abstract; §2 From Agency to Autonomy: A Hierarchical Framework for AI in SE; §4 Motivational Example; §5 The Engineering Activities of SASE; §7 From Vision to Reality。

## 2. 主要观点与方案

### 2.1 问题与动机（§1 Introduction; §3.1 Industrial Relevance）

- 自主编码 agent（Google Jules、OpenAI Codex、Anthropic Claude Code、Cognition Devin）已贡献数十万级被合并 PR，但存在"速度 vs 信任"鸿沟：产出常含隐性回归、表面修复与工程卫生问题；同时出现掌握新实践的 100x/1000x 超级开发者（§1）。
- 行业五因素使 SE 成为生成式 AI 的主战场：高薪人力、富训练数据（代码库/工单/commit）、可度量结果（编译错误、测试结果、缺陷率，利于 RL 奖励函数）、自动化安全网（测试与 CI）、能力可迁移；前沿厂商竞争的实质是"SE 数据飞轮"（§3.1）。
- 论文定位：提出 SASE（Structured Agentic Software Engineering）作为概念脚手架与结构化词汇，催化社区讨论而非给出定论（§1）。

### 2.2 SE 自动化等级框架（§2 From Agency to Autonomy）

- 先区分 agency（执行既定计划的能力）与 autonomy（自行制定目标/计划的能力），再类比 SAE 自动驾驶分级给出 L0–L5：L0 手工编码（SE 1.0，Notepad/vi/emacs）、L1 token 补全（SE 1.5，IDE 自动补全）、L2 任务级 agentic（SE 2.0，GitHub Copilot/Amazon CodeWhisperer）、L3 目标级 agentic（SE 3.0，Devin/Claude Code/Jules/Codex 所处层级）、L4 特定领域自治（SE 4.0，沿技术栈或质量属性两轴专业化，如 GPT-5 面向前端 Web 开发特化）、L5 通用领域自治（SE 5.0，目前仅概念/研究阶段、尚不存在）（§2）。
- §3.2 用同一两轴区分 Workflow Agents（高 agency：流程由人硬编码，需手工改编排逻辑）与 Autonomous Agents（高 autonomy：给定高层目标后自行规划推理调工具，可用自然语言迭代改进，即"用英文散文编写与改接的 FMware"）。

### 2.3 现状证据（§3.3; §3.4）

- 基准侧（§3.3）：通过测试 ≠ 可合并——29.6% 的"plausible"修复在严格复测中引入行为回归或错误；GPT-4 补丁经人工细审后真实解决率从 12.47% 跌至 3.97%；agent 补丁常局限于单文件、许多通过单测却败于更广 CI 检查（风格或隐性回归）。SWE-Bench Verified（OpenAI 与原作者合作的人工校验 500 题子集）上 GPT-4o 在 2024-08 发布时解 33%，2025 年中领先 agentic 方案超 70%；后因数据污染，OpenAI 推荐改用 SWE-Bench Pro。
- 野外侧（§3.4）：Jeff Dean 预计 agent 将达初级开发者水平；Claude Code 早期研究发现 agent 辅助贡献集中于重构/文档/测试，83.8% 的 PR 最终被合并、过半直接合并无进一步修改；AIDev 数据集含 932,791 个 agent 撰写 PR、跨 116,211 个仓库（截至 2025-08-01）；对 15,451 个重构实例（来自 12,256 个 agent PR）的研究显示 agent 多做局部一致性重构（改名/类型更新）、少架构级改动；2,303 个 Agent README（1,925 仓库）研究显示安全与性能要求远少于功能指引；4,550 个 agent PR 的研究显示日志与可观测性做法不一致、常需人在评审中纠正。

### 2.4 动机示例与缺口分析（§4 Motivational Example）

- 工作流（§4.1 The New Workflow）：开发者从 coder 转为 specifier，7 张工单花约 1.5 小时撰写自然语言规格与指引，agent 团队异步并行产出 28 个候选 PR（每工单 4 个，N-version programming 的回归）；4 张工单一次通过、3 张需迭代规格后重触发。
- 工件缺口（§4.2 The Process and Artifact Gaps）：§4.2.1 BriefingScript——比模糊工单更严格的一等工件，含 What & Success Criteria（可验证清单 + 前置条件/不变量）、架构上下文、战略建议、潜在 Gotchas；版本化、机器可读（Markdown/YAML/JSON），定位为 Knuth"literate programming"的 agent 化演进与活文档。§4.2.2 多维导师反馈——显式且持久的 MentorScript 规则、agent 从具体纠正推断一般规则、覆盖全 SE 生命周期的过程反馈、对多方案（N-version）的综合反馈。§4.2.3 LoopScript——声明式 SOP 语言，显式控制严谨度（全自治 vs 多级评审），替代主提示里的 ad-hoc prompt hacking。§4.2.4 Merge-Readiness Pack（MRP）五项证据标准——功能完备、验证可靠（含 agent 自建测试计划）、工程卫生（静态分析/lint/复杂度）、理由与沟通清晰、完全可审计（冻结的版本化轨迹），支持渐进式披露。
- 工具缺口（§4.3 The Tooling Gaps）：§4.3.1 ACE（Agent Command Environment）——人类 Agent Coach 的指挥中心：N-version 可视化比对与混搭、超越文本 diff 的架构影响视图、三类脚本的撰写/版本/归档/分析、上下文策展、按能力与成本组队并评估/降级/退役 agent、可切回传统 IDE 做外科手术式修改、语音辅助（Whisper/Talon Voice/Cursorless）。§4.3.2 AEE（Agent Execution Environment）——为 agent 优化而非为人：hyper-debugger、语义检索、以抽象符号结构操作代码的结构化编辑器、自监控基础设施（漏洞、异常算力开销、虚拟环境自修复），只把需要战略干预的问题上抛人类。

### 2.5 SASE 五类工程活动（§5 The Engineering Activities of SASE）

- §5.1 BriefingEng（简报工程）：融合 RE 与敏捷/Scrum 数十年积累，把简报当一等工件；机器为主要消费者、任务粒度更细、AI 辅助撰写三点使形式化比传统 SRS 更可行。
- §5.2 ALE（Agentic Loop Engineering）：根植 DevOps 的声明式管道与可观测性；LoopScript 规定任务分解与并行（可用异构模型组队，如 Gemini 2.5 Pro 做规划、Claude Opus/Sonnet 做编码）、工作流严谨度、基于证据的验收标准；关键指标从单任务延迟转向系统总吞吐。
- §5.3 ATME（AI Teammate Mentorship Engineering）：MentorScript 即"mentorship-as-code"——机器可读的团队规范规则书，规则自身过质量门（lint、单测、冲突检测），agent 行为可回溯到其依据的规则（借 PromptExp、Watson 等提示解释与推理观测技术）。
- §5.4 AGE（Agentic Guidance Engineering）：人从被动批准者变为按需顾问；消费 CRP（agent 发起的咨询包）与 MRP，产出 Version Controlled Resolution（VCR），与被回应工件显式关联、可审计。
- §5.5 ATLE & ATIE（生命周期与基础设施工程）五个核心概念：持久记忆与决策日志；agent 优先代码实践（DRY 可反转——克隆简化 agent 推理，GitClear 报告 GitHub 重复代码激增佐证；Clean Code 的 ROI 变清晰；偏好 Rust/TypeScript 等编译期强安全语言）；agent 原生工具链（人只需 precision@K 小 K，agent 可接受 precision@100 再由下级 agent 后处理；富构造性反馈如 Rust 编译器信息；Agent-Native MCP server 与自改进的工具描述，Anthropic 已在实践）；工程化多智能体团队（Modularity 与 Separation of Concerns 更关键，专用 agent 限定工具与安全策略以控制"爆炸半径"，可催生"agent store"市场；Claude Code 已从单体转向多 sub-agent 架构）；终身队友（从一次性承包商到持有 institutional knowledge 的伙伴，Devin 的 DeepWiki 为早期例；空闲算力主动扫描技术债/文档缺口并以 BriefingScript 提案，最终把 SE 3.0 推向 SE 4.0）。

### 2.6 讨论（§6 Discussion）

- §6.1 指出现有工具在最基础的 SE 需求上缺位：CLI 类（如 Claude Code）交互易逝、对话上下文只存在于终端回滚缓冲；Copilot 类平台虽以 PR 锚定历史，但导师内容与代码互不联动、回滚代码不回滚 agent 状态；尚无主流系统提供 agent 内部状态可观测性或"代码+提示+对话"的统一互联版本控制。
- §6.2 回应 Bitter Lesson 质疑：规模化通用方法在数据充沛处最强，新颖任务与数据稀缺领域仍需人提供结构与连接；现代超级工程师的核心技能是"控制二重性"——何时强加结构化工作流、何时放手让 agent 用规模化学习。
- §6.3 论证 agentic SE ≠ agentic coding：SE 本质是团队运动，需管理复杂性、跨角色协调与共享工件的长期可持续；SASE 以 CRP 等显式持久工件支撑 1-to-N、N-to-1（agent 向专家升级咨询）、N-to-N 混合协作可管理、可审计。

### 2.7 研究路线图与教育（§7 From Vision to Reality）

- §7.1 BriefingEng：BriefingScript 语言/模式（表达力、可学性、机器可校验的平衡）、AI 辅助撰写与评审（歧义检测、边界用例生成、性质化验收标准）、代码与证据回溯到简报条款的可追溯性及 N-version 多方案评审。
- §7.2 ALE：LoopScript 设计（分解、并行、检查点、升级规则、证据要求）、人在环控制（暂停/改道/止损而不重启全循环）、MRP 证据充分性标准与更富信息量的工具反馈信号。
- §7.3 ATME：MentorScript 规则抽象（从风格约束到架构原则）、规则自身的 lint/测试/冲突检测/回归检查、从重复人类反馈推断候选规则并保持可审计。
- §7.4 ATLE：持久记忆模型（持续学习 + 图/向量库/决策记录等外置记忆、SE 特定的记忆压缩）、主动维护的调度与价值估计、agent 优先代码原则的实证与经济学模型。
- §7.5 ATIE：后 IDE 人机界面（编排、对比、路由咨询、审计证据）、面向 agent 的分布式算力织物（隔离、可复现、调度、成本控制，衔接 SLA-aware CodeLLM serving）、agent 原生工具链（机器可读协议、结构化诊断、语义检索、自描述操作）。
- §7.6 教育：课程须从"训练学生当 agent（写代码/测试）"转向"管理 agent 舰队"——系统级思维、架构推理、严谨规格、mentorship-as-code；这是整体教学重构而非加一门提示工程课。

### 2.8 相关工作、结论与附录（§8; §9 Conclusion; Appendix A）

- §8 对比已有实践：PDAR 循环 + Product Requirement Prompt（Amazon Kiro 的 spec-driven 五段结构：Goal & Why / What & Success Criteria / All Needed Context / Implementation Blueprint / Validation Loop）、Superpowers 技能插件、元提示文件（CLAUDE.md、AGENT.md、.clinerules）、BMAD 敏捷多智能体框架；§8.4 归纳 SASE 五点差异化——mentorship-as-code、双工作台（ACE/AEE）、以 MRP 为目标工件、CRP 一等公民化（人类成为可调用的专家端点）、ATLE/ATIE 生命周期与基础设施。
- §9 结论：SE 3.0 的未来不由 agent 速度定义，而由"指导、编排与信任 agent"的能力定义。
- Appendix A 用 REST API 限流场景给出三个完整 YAML 风格实例：BriefingScript（A.1）、CRP 架构决策咨询（A.2，含选项/权衡/agent 推荐）、MRP（A.3，含 24/24 单测通过、92% 覆盖率、圈复杂度上限 6 对阈值 10、k6 负载下第 101 次请求返回 429 等证据字段）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| SWE-Bench "plausible" 修复复测 | 29.6% 引入行为回归或被判定错误 | §3.3 Brief Survey of Today's Agentic Solutions on Benchmarks like SWE-Bench |
| GPT-4 补丁真实解决率（人工细审 vs 原始） | 由 12.47% 降至 3.97% | §3.3 |
| SWE-Bench Verified 进展（500 题，vs 初期） | GPT-4o 2024-08 为 33%，2025 年中领先 agentic 方案超 70% | §3.3 |
| Claude Code agent 辅助 PR 合并率 | 83.8%，其中过半未经进一步修改直接合并 | §3.4 Brief Survey of Today's Agentic Solutions in the Wild using GitHub Data |
| AIDev 数据集规模 | 932,791 个 agent 撰写 PR、116,211 个仓库（截至 2025-08-01） | §3.4 |
| agent 重构行为实证 | 15,451 个重构实例、来自 12,256 个 agent PR：偏局部一致性重构 | §3.4 |
| 动机示例吞吐 | 7 张工单、约 1.5 小时规格撰写，产出 28 个并行候选 PR（每工单 4 个）；4 张一次通过、3 张需迭代 | §4.1 The New Workflow |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2509.06216 |
| 系列前作 | Towards AI-Native Software Engineering (SE 3.0): A Vision and a Challenge Roadmap（arXiv:2410.06107，§1 引用） |
| 关联数据集 | AIDev: Studying AI Coding Agents on GitHub（arXiv:2602.09185，§3.4 引用） |
| 相关基准 | SWE-Bench / SWE-Bench Verified（人工校验 500 题）/ SWE-Bench Pro（§3.3 讨论） |
| 提及的工业实践 | Amazon Kiro（PRP 五段结构）、BMAD-METHOD、Superpowers、CLAUDE.md/AGENT.md 元提示（§8.1–§8.2） |
| 工件实例 | Appendix A 的 BriefingScript/CRP/MRP 完整 YAML 示例（§A.1–§A.3） |

## 5. 一句话索引（给 Agent 用）

> Hassan 等（arXiv:2509.06216v3）提出 SASE：以 SE for Humans / SE for Agents 二元性重构四支柱 Actors/Processes/Tools/Artifacts，人类转为 Agent Coach，经 ACE/AEE 双工作台与版本化工件（BriefingScript/LoopScript/MentorScript/CRP/MRP/VCR）协作；§2 类比 SAE 分级 L0–L5（L3=SE 3.0）；证据：SWE-Bench plausible 修复 29.6% 有回归、GPT-4 真实解决率 12.47%→3.97%、Verified 上 33%→70%+；§5 定义 BriefingEng/ALE/ATME/AGE/ATLE&ATIE 五类活动，§7 给路线图与教育重构；属观点性愿景论文。
