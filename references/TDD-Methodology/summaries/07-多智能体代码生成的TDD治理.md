---
title: "TDD Governance for Multi-Agent Code Generation via Prompt Engineering"
source_pdf: "07-Hasanli-TDD_Governance_Multi_Agent_v1.pdf"
arxiv_id: "2604.26615"
arxiv_version: "v1"
authors:
  - "Tarlan Hasanli"
  - "Shahbaz Siddeeq"
  - "Bishwash Khanal"
  - "Pyry Kotilainen"
  - "Tommi Mikkonen"
  - "Pekka Abrahamsson"
year: 2026
venue: "arXiv（PROMPT-SE 2026 workshop 投稿）"
type: "设计参考 + 内容索引"
generated_at: "2026-11-01"
summary_version: "1.0"
---

# 论文摘要：多智能体代码生成的 TDD 治理（提示工程路径）

## 1. 适用场景

- 当你要设计多智能体（multi-agent）LLM 编码流水线，担心模型的非确定性（non-determinism）与幻觉导致工作区状态失控，需要"模型只提案、引擎独占写权限"的分层治理架构时，读 §3.2 Governance-Centric Architecture。
- 当你想把 TDD（Test-Driven Development，测试驱动开发）纪律——测试先行、最小实现、有界修复——从"口头建议"变成提示词级与工作流级可强制执行（enforceable）的约束时，读 §3.1–3.2。
- 当你要为 LLM 修复循环（repair loop）设计终止策略（重试预算、失败签名去重、等价提案检测），防止无限重试与成本失控时，读 §3.2 Bounded Repair and Loop Control。
- 当你要构建机器可读的工程规范宣言（manifesto）——用 JSON 字段（原意图、AI 原生解释、操作约束、反模式）同时驱动提示构造与运行时校验时，读 §3.1 Manifesto representation。
- 当你需要评估"治理强度 vs. 提示 token 成本"的取舍，或为受监管领域规划可审计（auditable）的 AI 辅助开发时，读 §4。

> 锚点：多智能体 LLM 编码治理 / TDD 提示工程 / 提案-执行权限分离 / 有界修复循环 / 机器可读 TDD 宣言。

## 2. 主要观点与方案

- **问题**：LLM 加速开发但不稳定——同一提示两次生成的测试输出零相同的比例在复杂基准上最高达 75.76%（引自 Ouyang et al. [15]，§2）；幻觉、复现性缺口使多智能体设置下小错误沿工作流扩散（§1）。现有测试引导（test-guided）提示方法提升正确性，却不强制流程纪律：相位顺序（phase ordering）、最小实现、有界修复（§2）。开放问题：如何把经典 TDD 原则翻译成可强制执行、治理感知的提示结构（§2 末三条观察）。
- **治理框架构成（§3.1）**：作者把原则抽取语料限定为 Kent Beck [1] 与 Robert C. Martin [12,13] 两个规范源头；入选标准是"规范性（must/should）陈述"且"违反它属于 deadline 压力下的历史常见对策（如批量提交改动、削弱测试、跳过重构）"。经人工概念级综合，原则归一化为"标签 + 人类时代原意图 + 出处"的结构化记录，并按四类组织（Table 1）：Order（测试先行、Red→Green→Refactor 顺序）、Granularity（最小失败测试、最小通过代码、一次一个失败测试）、Feedback quality（FAST/独立/可重复/自校验/及时的测试与有意义断言）、Design hygiene（绿灯期持续去重重构）。每条原则再编码为 JSON 宣言中的治理对象，含标识符、标题、原意图、AI 原生解释、操作约束、反模式；解释字段用于角色提示构造，约束/反模式字段映射到运行时强制点（相位闸门、范围限制、提案校验、有界修复控制）（§3.1 Manifesto representation，宣言 URL 见脚注 1）。
- **机制（§3.2）**：分层架构把生成自治权与状态权威分离——LLM 永不直接写文件系统，只返回结构化补丁提案（patch proposal）；提案须经 4 道闸门——(1) 结构校验（schema 与内容）、(2) 策略执行（禁改路径、目录限制）、(3) 相位一致性检查、(4) 可选人工或规则审批——之后由编排引擎原子地（atomically）应用变更。相位导向工作流：planner 把规格分解为带预期测试结果的有序步骤，先建立失败测试（RED）才允许生成实现（GREEN），测试失败进入修复循环，通过后可选重构（Figure 2）。有界修复：每个 GREEN 步最多 N=3 次修复尝试；每轮计算失败签名 S = {异常类型, 失败测试, 规范化消息}，签名连续重复、修复无有效代码变更（patch 对比检测）或提案与先前语义等价即提前终止。原则到机制的映射：测试先行由 planner 排序 + 引擎级 FAIL 闸门强制；最小实现由提示范围限制 + 引擎拒绝 no-op/无关变更强化；行为保持由应用后测试执行闸门 + 重构期测试失败自动回滚保证；受控重构仅在测试通过后允许，且校验禁止功能修改与测试编辑（§3.2 From Principles to Enforceable Mechanisms）。
- **提示分布（§3.2 Prompt Distribution Across Agent Roles）**：TDD 纪律不编码在单条指令中，而是由 6 类角色提示协调涌现：System（治理不变量、结构化输出、相位纯度）、Planner（带预期测试结果的有序步骤，如 FAIL→PASS）、Test Generation（RED 期约束：输出仅限测试文件、断言须与规格对齐且有意义）、Implementation（最小必要变更、禁止无关功能添加）、Failure Repair（注入结构化失败上下文，强制最小局部修复）、Review（质量闸门：测试评审期间禁止改产品代码、防止过度规格与虚构需求）。
- **实验/案例（§4）**：论文没有实验章节。仅称"初始实验表明，相比基线提示，显式相位分离与验证闸门减少了不稳定重试循环"；测试先行与最小实现"似乎"限制了投机性代码生成与功能膨胀；并提醒 manifesto 注入须与 token 约束权衡（治理强度 vs. 提示紧凑性）。
- **发现与局限（§4）**：主要收益是把开发纪律显式编码进生成式工作流本身，使纪律"塑造生成轨迹"而非事后补救（§ AI-Native TDD as Process Encoding）。自述局限：宣言派生约束主要在提示层强制、运行时验证仅部分完成；有界自治可能限制复杂重构场景的探索；实证验证仍属初步；扩展到大型多模块仓库需更先进的规划与不变量强制。未来工作：仓库级工业环境 + CI/CD 集成评估稳定性、缺陷率与可复现性；可配置治理等级；面向监管域的可审计 AI 辅助开发。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
| --- | --- | --- |
| GREEN 步修复尝试上限 | N = 3 次（固定重试预算，设计参数） | §3.2 Bounded Repair and Loop Control |
| 变更应用前的验证闸门数 | 4 道：结构校验、策略执行、相位一致性、可选人工/规则审批 | §3.2 Governance-Centric Architecture |
| 角色提示类别数 | 6 类：System / Planner / Test Generation / Implementation / Failure Repair / Review | §3.2 Prompt Distribution Across Agent Roles |
| 原则分类数（抽取语料 2 位作者：Beck、Martin） | 4 类：Order / Granularity / Feedback quality / Design hygiene | §3.1 + Table 1 |
| 背景动机数据：同一提示两次生成测试输出零相同的比例 | 最高 75.76%（引自 Ouyang et al. [15]，非本文实验） | §2 |
| 本文自评效果 | "初始实验"定性称相位分离+验证闸门较基线提示减少不稳定重试循环；无数值、无基准名、无显著性 | §4 |

注：本文为 5 页 workshop 投稿短文，无系统性实证评估；作者自述 "Empirical validation remains preliminary"（§4）。表中数值或为框架设计参数，或引自他人文献；论文未报告任何样本量、对照设置、统计显著性检验。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
| --- | --- |
| 论文本身 | https://arxiv.org/abs/2604.26615 （v1，2026-04-29 提交；arXiv comments 标注 Submitted to PROMPT-SE 2026；PDF 版权块沿用 EASE 2026 会议模板） |
| TDD 原则宣言（JSON） | https://github.com/shahbazsiddeeq/TDD-manifesto/blob/main/tdd_principles_manifesto.json （论文脚注 1 给出） |
| 原则抽取语料 | Kent Beck,《Test-Driven Development: By Example》(2002)；Robert C. Martin,《Clean Code》(2009) 与《The Clean Coder》(2011)（§3.1 限界语料） |
| 相关被引工作 | TiCoder [5]（ICSE-Companion 2024）；TDFlow, arXiv:2510.23761 [8]；Tests as Prompt / WebApp1K, arXiv:2505.09027 [3]；LLM4TDD [16]（LLM4Code 2024）；LLM 代码生成非确定性研究 [15]（ACM TOSEM 34(2), 2025） |
| 实验基准 / 数据集 / 代码实现 | 论文未给出（无实验基准；除宣言 JSON 外未提供系统代码仓库链接） |
| 资助 | Business Finland 项目 GEENIUS (2545/31/2024)、ANSE (1822/31/2025) |

## 5. 一句话索引（给 Agent 用）

> Hasanli 等（2026，arXiv:2604.26615v1，5 页 workshop 投稿）提出 AI 原生 TDD 治理框架：从 Beck/Martin 两个源头抽取 TDD 原则并归为 4 类，编码为机器可读 JSON 宣言，经 6 类角色提示分布到规划/生成/修复/验证各阶段；LLM 仅产出结构化提案，引擎经 4 道闸门后原子应用，GREEN 步修复上限 N=3、失败签名重复即终止。作者仅以定性"初始实验"称相位分离加验证闸门较基线提示减少不稳定重试循环，无任何量化结果与显著性检验，宣言约束主要停留在提示层、运行时验证仅部分实现。
