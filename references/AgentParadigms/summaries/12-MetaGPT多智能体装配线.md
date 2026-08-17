---
title: "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework"
source_pdf: "12-Hong-MetaGPT_v7.pdf"
arxiv_id: "2308.00352"
arxiv_version: "v7"
authors:
  - "Sirui Hong"
  - "Mingchen Zhuge"
  - "Jiaqi Chen"
  - "Xiawu Zheng"
  - "Yuheng Cheng"
  - "Ceyao Zhang"
year: 2023
venue: "ICLR 2024"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：MetaGPT——SOP 装配线多智能体框架

## 1. 适用场景

- 要把一套成熟的人类工作流程（SOP）编码成 LLM 多 agent 流水线——为每个角色定义 profile/目标/约束并按装配线交接中间产物时（§3.1）。
- 设计 agent 间通信机制：用结构化文档（PRD、系统设计、API 规约）替代自由对话、配共享消息池 + 发布-订阅以对抗信息过载与级联幻觉时（§3.2; Appendix E）。
- 为代码生成 agent 加"可执行反馈"自纠错循环（执行 + 单元测试 + 历史调试记忆，封顶 3 次重试）时（§3.3）。
- 需要一套软件工程向多 agent 评测方案（可执行性 1–4 分级、token/时间成本、生产率、人工修订次数）并对比 AutoGPT/LangChain/AgentVerse/ChatDev 时（§4.1; Table 1; Table 4）。
- 评估装配线范式的边界与演进方向：UI/前端等场景缺口、运行中断/检查点缺失、自改进机制与 agent 经济（AgentStore）展望时（Appendix A; Appendix D）。

> 锚点：Abstract; §1 INTRODUCTION; §3 METAGPT: A META-PROGRAMMING FRAMEWORK; §4 EXPERIMENTS; §5 CONCLUSION。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 INTRODUCTION; §2 RELATED WORK）

天真地把 LLM 串成多 agent 会因级联幻觉产生逻辑不一致，角色扮演式框架尤其易陷入寒暄式空转（"Hi, hello and how are you?"）；已有工作（CAMEL 式角色扮演、ChatDev）未充分利用结构化输出格式的工作流（§1; §2）。作者把人类软件公司的 SOP 引入多 agent 协作，将 meta-programming（"programming to program"）落实为一组各司其职、按既定标准交接的专职 agent（§1）。

### 2.2 框架设计（§3）

- **角色特化 + SOP 工作流（§3.1）**：模拟软件公司定义 5 个角色——Product Manager、Architect、Project Manager、Engineer、QA Engineer；每个 agent 有 name/profile/goal/constraints 及专属工具（PM 可 web 搜索，Engineer 可执行代码）；全员遵循 ReAct 式行为监视环境。流程：PM 产出含 User Stories 与 Requirement Pool 的 PRD → Architect 转成 File List/数据结构/接口定义等系统设计 → Project Manager 做任务分解分配 → Engineer 按规约写代码 → QA Engineer 出测试用例（Figure 1; Figure 3; Appendix B 完整 demo）。
- **通信协议（§3.2）**：(a) 结构化通信接口——每个角色按 schema 产出文档与图（而非对话），类比"传话游戏"中自然语言多轮失真；(b) 共享消息池 + 发布-订阅——所有 agent 向全局消息池发布结构化消息，又按角色兴趣订阅相关信息（Architect 主要关注 PRD，少关注 QA 文档），agent 收齐全部前置依赖后才触发动作，避免一对一通信的拓扑复杂度与信息过载（Figure 2; Appendix E.2）。
- **可执行反馈（§3.3）**：初版实现会漏检错误（幻觉），故 Engineer 生成代码后执行并编写单元测试，依据自身历史执行/调试记忆迭代修改，直到测试通过或达到最多 3 次重试（Figure 2 右）。

### 2.3 实验设置（§4.1）

- **数据集**：HumanEval（164 题手写编程任务）、MBPP（427 个 Python 任务）、自建 SoftwareDev（70 个代表性软件开发任务——小游戏、图像处理、数据可视化等工程向任务；主实验随机选 7 个代表任务评测）（§4.1; Appendix C.1 Table 8）。
- **指标**：HumanEval/MBPP 用 unbiased Pass@k；SoftwareDev 用人工评估 + 统计——(A) Executability 1–4 分（1 不可用 / 2 可运行 / 3 近乎完美 / 4 无瑕）、(B) 成本（时间/token/费用）、(C) 代码统计（文件数/每文件行数/总行数）、(D) Productivity（token/代码行，越低越好）、(E) 人工修订次数（§4.1）。
- **基线**：代码模型 AlphaCode/InCoder/CodeGeeX/CodeGen/CodeX/CodeT、通用模型 PaLM/GPT-4；系统对比 AutoGPT、LangChain(REPL)、AgentVerse、ChatDev（§4.1）。

### 2.4 主要结果（§4.2; Figure 4; Table 1; Table 4）

- 配 GPT-4 在 HumanEval/MBPP 上 Pass@1 分别 85.9%/87.7%，为当时 SoTA（GPT-4 基线 67.0%）；论文声称在复杂软件项目实验中达成 100% 任务完成率（§1; §4.2）。
- SoftwareDev 上几乎全面优于 ChatDev：可执行性 3.75 vs 2.25（接近 4 分无瑕）；耗时 503s vs 762s；代码量更大（251.4 行/5.1 文件 vs 77.5 行/1.9 文件）；token 更多（31,255 vs 19,292）但生产率反而更高（124.3 vs 248.9 tokens/行）；人工修订 0.83 vs 2.5（Table 1）。
- 与通用框架对比：MetaGPT 平均可执行性 3.9，ChatDev 2.1，AutoGPT/LangChain/AgentVerse 均 1.0（无法产出可执行代码，短小、逻辑不全、难处理跨文件依赖）（Appendix C.2 Table 4）。

### 2.5 能力与消融（§4.3; §4.4）

- **能力矩阵（§4.3 Table 2）**：MetaGPT 覆盖 PRD 生成、技术设计生成、API 接口生成、代码生成、预编译执行、基于角色的任务管理、代码审查，其余框架普遍缺失前几项。
- **角色消融（§4.4 Table 3）**：仅 Engineer 时产出不可用代码（可执行性 1.0、修订 10 次、83 行/$0.915）；逐步加角色持续改善，4 角色配置可执行性 4.0、修订降至 2.5（费用升至 $1.385，属可接受代价）。
- **可执行反馈消融（§4.4）**：加入反馈使 HumanEval/MBPP Pass@1 分别 +4.2%/+5.4%（81.7→85.9、82.3→87.7），可执行性 3.67→3.75、人工修订 2.25→0.83（Figure 4; Table 1）。

### 2.6 附加分析（Appendix C）

- **不同 LLM 后端（Table 5，5 任务）**：GPT-4 可执行性 3.8（552.94s、修订 1.2）；GPT-3.5 为 2.8；Deepseek Coder 33B 仅 1.4（1186.20s）——框架可运行于多种后端但 GPT-4 明显最优。
- **指令层级（Table 6）**：高层短指令（13.2 词）可执行性 3.8，详细指令（42.2 词）4.0 但生产率更低（163.8 vs 118.0 tokens/行）——SOP 使简短输入也能产出接近详细规格的软件。
- **GPT 变体敏感性（Table 7）**：gpt-4-0613 直连 HumanEval 平均 0.724，regex 解码后 0.812，加系统提示 0.800；gpt-3.5-turbo 无提示词时难返回正确代码（0.357→0.577）。
- **70 任务全量（Table 9，纯 MetaGPT w/o feedback）**：平均 4.71 个代码文件/191.57 行代码/3 个文档 240 行、prompt 26,626.86 + completion 6,218 tokens、516.71s、$1.12/任务、0.51 次修订、可执行性 3.36。

### 2.7 展望、局限与伦理（Appendix A; Appendix D; Appendix E; §5 CONCLUSION）

- **自改进（Appendix A.1）**：当前各项目独立执行；作者实现递归修改 agent 约束提示的机制——每个项目结束后 agent 批判性总结反馈并更新 constraint prompt、存入长期记忆供后续项目继承；局限是只改角色特化约束、未动结构化通信接口。
- **多 agent 经济（Appendix A.2）**：结合 NLSOM 的 Economy of Minds 思想与 DeepWisdom AgentStore——agent 以明码标价提供服务、按用量计费、可插拔升级。
- **局限（Appendix D.1）**：系统侧——缺少 UI/前端场景的专用 agent 与多模态工具，且尽管代码量居同类之最，仍难满足真实应用的多样复杂需求；用户侧——难以中途打断某个 agent 或设置检查点（checkpoint）。
- **伦理（Appendix D.2）**：失业与技能过时（自然语言编程降低门槛）、透明与问责（开源、人类可发起/观察/中止、工程师对结果负责）、隐私（本地运行、不收集数据，可配开源 LLM 后端）。
- **结论（§5）**：SOP + 角色特化 + 消息池/订阅 + 可执行反馈构成灵活可移植的多 agent 平台，多基准 SoTA；也是规范化 LLM 多 agent 框架的早期尝试。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| HumanEval Pass@1（vs GPT-4 基线） | 85.9%（GPT-4 为 67.0%），当时 SoTA | §1; §4.2 Figure 4 |
| MBPP Pass@1 | 87.7% | §1; §4.2 Figure 4 |
| 可执行反馈增益（vs w/o feedback） | HumanEval +4.2%（81.7→85.9）、MBPP +5.4%（82.3→87.7） | §4.4 Figure 4 |
| SoftwareDev 可执行性（vs ChatDev） | 3.75 vs 2.25（1–4 分制，4 为无瑕） | §4.2 Table 1 |
| SoftwareDev 平均可执行性（vs 通用框架） | MetaGPT 3.9 vs ChatDev 2.1 vs AutoGPT/LangChain/AgentVerse 1.0（7 任务） | Appendix C.2 Table 4 |
| 运行时间（vs ChatDev） | 503s vs 762s | §4.2 Table 1 |
| Token 用量 / 生产率（vs ChatDev） | 31,255 vs 19,292 tokens（更多）；124.3 vs 248.9 tokens/行（更优） | §4.2 Table 1 |
| 人工修订次数（vs ChatDev） | 0.83 vs 2.5 | §4.2 Table 1 |
| 代码规模（vs ChatDev） | 251.4 行/5.1 文件 vs 77.5 行/1.9 文件 | §4.2 Table 1 |
| 角色消融 | 仅 Engineer 可执行性 1.0/修订 10 次 → 4 角色可执行性 4.0/修订 2.5（$0.915→$1.385） | §4.4 Table 3 |
| 不同 LLM 后端 | GPT-4 可执行性 3.8 / GPT-3.5 2.8 / Deepseek Coder 33B 1.4（5 任务） | Appendix C.2 Table 5 |
| 指令层级影响 | 高层指令 3.8 vs 详细指令 4.0（生产率 163.8 vs 118.0 tokens/行） | Appendix C.2 Table 6 |
| 70 任务全量（w/o feedback） | 平均 $1.12/任务、191.57 行代码、516.71s、可执行性 3.36 | Appendix C.2 Table 9 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2308.00352（v7，ICLR 2024 会议论文） |
| 代码 | https://github.com/geekan/MetaGPT（论文给出；现迁移至 FoundationAgents/MetaGPT） |
| 基准 | SoftwareDev 数据集：70 个软件开发任务（11 个含完整 prompt 见 Table 8） |
| 关联平台 | DeepWisdom AgentStore（http://beta.deepwisdom.ai，多 agent 经济/服务市场） |
| 关联 | 本目录 15（MAST——MetaGPT 为其被分析框架之一）、13（AutoGen 会话式路线对照） |

## 5. 一句话索引（给 Agent 用）

> 要把人类 SOP 变成多 agent 装配线时读这篇：MetaGPT 把软件公司工作流编码进提示序列（PM→Architect→Project Manager→Engineer→QA 五角色，ReAct 式），agent 间以结构化文档（PRD/系统设计/接口规约）而非自由对话交接，配共享消息池 + 发布-订阅抗信息过载，Engineer 用可执行反馈迭代（执行+单测，最多 3 次重试）；配 GPT-4 在 HumanEval/MBPP Pass@1 达 85.9%/87.7%（SoTA，反馈贡献 +4.2%/+5.4%），SoftwareDev 可执行性 3.75/4 优于 ChatDev 2.25，且 503s<762s、人工修订 0.83<2.5、生产率 124.3<248.9 tokens/行，代价是 token 总量更高；局限在 UI/前端场景与运行中断/检查点。
