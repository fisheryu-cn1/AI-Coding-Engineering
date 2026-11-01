---
title: "Empowering Agile-Based Generative Software Development through Human-AI Teamwork"
source_pdf: "22-Zhang-AgileGen_Human_AI_Teamwork_v2.pdf"
arxiv_id: "2407.15568"
arxiv_version: "v2"
authors:
  - "Sai Zhang"
  - "Zhenchang Xing"
  - "Ronghui Guo"
  - "Fangzhou Xu"
  - "Lei Chen"
  - "Zhaoyuan Zhang"
  - "Xiaowang Zhang"
  - "Zhiyong Feng"
year: 2024
venue: "arXiv"
type: "设计参考 + 内容索引"
generated_at: "2026-09-21"
summary_version: "1.0"
---

# 论文摘要：AgileGen——人机团队的敏捷生成式软件开发（Gherkin 验收标准 + 轻量迭代验收）

## 1. 适用场景

- 当你要设计"**最终用户（非程序员）直接驱动 Agent 生成完整软件**"的人机协作流程，需要一套"人做决策、Agent 做实现"的分工范式时，读这篇——它把用户参与点精确放在每次迭代的两端（需求/场景决策、验收与建议决策），中间全自动化。
- 当你需要解决"**用户原始需求不完整、缺少验收标准**"导致生成软件偏离隐性需求的问题时，读其 Gherkin 补全验收标准 + Gherkin↔自然语言双向交互桥的设计。
- 当你要为"**需求与生成代码的语义一致性**"找机制（而非只靠 prompt）时，读其 consistency factor（从 Gherkin 场景导出可测试业务用例驱动代码生成与自动修改）。
- 当你需要一份生成式软件开发 Agent 的**能力对比基线**（Passive/Auto-Thinking/Multi-Agent/Questioning 四类 vs Human-AI Teamwork）或人评+自动评测的完整实验设计模板（CodeBLEU/Pass@1/Code Executability/UEQ/Likert）时，读 §1、§4–§5。

> 锚点：§1 Introduction; §2 Motivation & Innovation; §3 Design of Human-AI Collaborative AgileGen; §4 Experimental Setup; §5 Experiment Results; §6 Discussion

## 2. 主要观点与方案

- **问题定位**（§1; §2.1; Fig.3）：用户原始需求 69% 以非正式自然语言表达（引 Kassab & Laplante 2022），普遍缺少验收标准；现有四类 Agent 各有硬伤——Auto-Thinking/Multi-Agent 走瀑布模型导致幻觉误差逐级累积且用户无法中途介入，Questioning Agent（GPT-Engineer/gpt-pilot）的提问是编程导向的（如"数据库怎么设计"），超出最终用户的领域知识。敏捷方法的用户协作+轻量迭代可削减瀑布累积误差，难点在于用户需求语义与 Agent 代码语义之间的鸿沟。
- **Human-AI Teamwork 分工模型**（§2.2; §3.1; Fig.5）：人擅长决策与验收、Agent 擅长自动生成，故把最终用户放在每次迭代的两端——①需求决策（一句话自然语言需求）→②场景决策（对生成的场景做确认/增加/删除/修改）→中间 Agent 自动完成视觉设计与代码生成→③验收与建议决策（点击 Code Execution Link 试用原型，用自然语言提修改建议，进入下一轮迭代）。
- **Gherkin 作语义一致性桥梁**（§2.2; §3.3.1）：首次把 BDD 的 Gherkin 语言引入生成式 Agent——用 Gherkin 场景为不完整需求补全验收标准；但正式 DSL 对最终用户不友好，故设计**交互桥**（Gherkin→NL 展示给用户决策、NL→Gherkin 回收决策结果），让用户始终用自然语言交互。决策后的 Gherkin∗ 再导出 **consistency factor**（每个场景至少一个含输入输出样例的业务逻辑用例），驱动 Auto Modification 自动修正代码功能正确性（§3.3.2）。
- **记忆池机制**（§3.2.1; §3.3.1）：SQLite3 存储历届用户"需求→决策后场景"的经验条目，新需求按 Jaccard 相似度（阈值 0.7）检索最相似条目作为场景设计示例，随使用持续积累以降低用户决策成本（实验中为保证公平未预置经验，效果留待后续验证，§6）。
- **实现形态**（§3.2.2; §4.3）：Gradio 交互界面；AI-Chain 式 prompt 有向循环图（含人类决策点，绕过即退化为端到端生成，可扩展性强）；基座 GPT-3.5-turbo / GPT-4-1106-preview，temperature 0.3；以 Web 应用（.html/.css/.js）为演示载体，框架设计不限于 Web。
- **评测设计**（§4; §5）：三问结构——RQ1 有效性（自动指标 CodeBLEU/Pass@1/Time/Pro_Code/Cost + 人评 Code Executability 0–3 分 + UEQ 六维），数据集为 50projects50days 改造成的 40 个项目（30 个开源 + 10 个参与者自创需求）与 ChatDev 的 SRDD 数据集分层抽样 20 个项目；RQ2 消融（逐一移除 Gherkin/Visual Design/Consistency Factor 直至只剩裸模型）；RQ3 交互体验（7 点 Likert 五维 + 交互案例）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| Pass@1（50projects50days，30 项目） | AgileGen(GPT3.5) 62.5%，超最优基线 ChatDev_24(GPT3.5) 16.4%；AgileGen(GPT4) 71.5%，超 GPT4o+CoT 24.7% | §5.1.1; Fig.9 |
| CodeBLEU（同上） | AgileGen(GPT3.5) 0.339（+0.089 vs ChatDev_24）；AgileGen(GPT4) 0.362（+0.105 vs GPT4o+CoT）；两版本合计占 73.3% 项目最优、83.3% 次优 | §5.1.1; Fig.9 |
| Code Executability 人评（40 项目，20 名参与者） | AgileGen 50% 项目得满分 3、45% 得 2；满分比例超 ChatDev_24 47.5%（后者满分仅 2.5%）；AutoGPT 0+1 分占 97.5% | §5.1.2; Fig.10 |
| Code Executability（SRDD 20 项目） | AgileGen 85% 得 2、15% 得 3；ChatDev_24(GPT3.5) 55% 仅得 1；ChatDev_24(GPT4) 50% 得 0 | §5.1.2; Fig.11 |
| UEQ 用户满意度（26 题，−3~+3） | 总均分 1.26，六维中五维均分 >+1，"Attractiveness""Dependability" 表现突出，仅 "Novelty" 低于 +1 | §5.1.2; Fig.12 |
| 消融：去 Gherkin（GPT3.5） | Pass@1 62.5%→20.6%（−41.9%），CodeBLEU −0.196，Code Executability 2.250→1.325 | §5.2; Table 6 |
| 消融：裸模型 w/o Anything | GPT3.5 Pass@1 仅 6.3%（−56.2%）；GPT4 35.2%（−27.3%）——性能主要来自框架设计而非基座模型 | §5.2; Table 6 |
| 效率与成本 | AgileGen(GPT3.5) 平均 68.6s/项目、0.0110$；较 ChatDev 省约 2 倍、较 AutoGPT 省约 4 倍成本 | §5.1.1; Table 5 |
| 交互体验（RQ3，另招 20 名参与者，7 点 Likert） | 五维（Match Goal/Think Through/Transparent/Controllable/Collaborative）全部高于均值，GPT-4 版 "Match goal" 突出；多数参与者每项目约 3 轮交互修改 | §5.3.1; Fig.17 |

注：论文未报告统计显著性检验（无 p 值/置信区间），人评样本量为两组各 20 名参与者。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2407.15568 |
| 源代码 | https://github.com/HarrisClover/AgileGen（Gradio 交互系统） |
| 复现包 | AgileGen-50projects50days-Experiment、AgileGen-SRDD-Experiment、AgileGen-Human-Agent-Interaction-Experiment（均在 github.com/HarrisClover 下） |
| 评测数据集 | 50projects50days（github.com/bradtraversy/50projects50days，取 30 项目+10 个用户自创需求）；SRDD（ChatDev，1200 条软件任务 prompt，分层抽样 20 条） |
| 基线系统 | AutoGPT、ChatDev_23/ChatDev_24、GPT-Engineer、GPT3.5/GPT4/GPT4o+CoT |
| 方法谱系 | BDD/Gherkin/Cucumber（验收标准与可执行规约）；AI Chains（Wu et al., CHI'22，交互量表亦出自此文）；敏捷方法轻量迭代思想 |
| 关联论文 | 本库 SEforLLM/17（规约驱动开发：spec-anchored 一级与本文 Gherkin 验收标准思路互通）、MetaGPT/ChatDev 系列（瀑布式多智能体对照） |

## 5. 一句话索引（给 Agent 用）

> AgileGen（arXiv 2407.15568v2，2024）：面向最终用户的人机团队敏捷生成式开发框架——用户只在每次迭代两端做决策（需求、Gherkin 场景确认/增删改、原型验收与建议），中间由 Agent 自动生成；核心机制是用 Gherkin 为不完整需求补全验收标准、Gherkin↔自然语言交互桥降低用户门槛、consistency factor 驱动代码自动修正、记忆池积累决策经验。在 40 个 Web 项目上 Pass@1 62.5%（GPT3.5）/71.5%（GPT4），超 ChatDev_24 16.4%；人评满分率 50%（超 ChatDev_24 47.5%）；消融显示去 Gherkin 后 Pass@1 降 41.9%，裸模型仅 6.3%；两组各 20 人用户研究给出 UEQ 均分 1.26、Likert 五维全高于均值（无显著性检验）。
