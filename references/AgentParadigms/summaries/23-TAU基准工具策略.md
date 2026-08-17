---
title: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains"
source_pdf: "23-Yao-TAU_Bench_v1.pdf"
arxiv_id: "2406.12045"
arxiv_version: "v1"
authors:
  - "Shunyu Yao"
  - "Noah Shinn"
  - "Pedram Razavi"
  - "Karthik Narasimhan"
year: 2024
venue: "ICLR 2025"
type: "评测对照 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：τ-bench——工具-代理-用户交互基准与 pass^k 指标

## 1. 适用场景

- 当你要评测 agent 的**多轮人机交互 + 工具调用 + 域政策遵循**综合能力（客服式零售/航空域，数据库终态自动判分）时读这篇——它是该范式的开创性基准。
- 当你要为生产部署选型引入 **pass^k**（k 次独立试验全部成功）这一"可靠性/一致性"口径、区分"平均能过"与"每次都能过"时，直接采用其 §3 的指标定义与无偏估计公式。
- 当你要自建一个"LLM 模拟用户 + 政策文档 + 可写数据库"的评测域时，照抄其三阶段构建流程（§4：手工 schema/API/政策 → LM 生成数据 → 手工任务标注 + 迭代消歧验证）。
- 当你要分析 function-calling agent 的失败模式（错误参数、错误决策、复合请求部分完成）并做政策消融归因时，用其 §5.2 的失败分解框架。
- 当你在做 agent 的成本核算（长系统提示主导推理成本）或选 function calling vs ReAct 文本格式时，参考 §5.1 的方法对比与成本分析。

> 锚点：Abstract; §1 Introduction; §3 τ-bench: A benchmark for Tool-Agent-User Interaction; §4 Benchmark Construction; §5 Experiments; §6 Discussion。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- 既有 agent 基准（web/代码终端/API）是"信息一次给全"的自主交互，**不测与人交互和域规则遵循**；而真实部署要求 agent：(1) 与人和 API 长程交互逐步收集信息、(2) 精确遵循域政策、(3) 在百万级交互规模上保持一致与可靠（§1）。
- τ-bench（Tool-Agent-User Interaction Benchmark）用模块化组件补上这两块：真实数据库与 API、域政策文档、多样化用户场景指令及 ground truth 标注；首个示范域为客服场景的 τ-retail 与 τ-airline（§1）。

### 2.2 形式化与核心机制（§3）

- 任务建模为 **POMDP** (S, A, O, T, R, U)，S = Sdb ⊗ Suser；数据库转移 Tdb 确定性（Python 函数），用户转移 Tuser 随机（LM 采样）；政策文档部分描述域世界模型（§3）。
- 政策约束分两层：部分由 API 强制（如用不在用户档案的支付方式返回 "Error: payment not found"），部分靠 agent 自律（如按会员等级/舱位算免费托运行李额），后者模拟真实坐席的自由裁量（§3）。
- **用户模拟**：gpt-4-0613 扮演用户，状态 = 任务指令系统提示 + 对话历史；用户**看不到** agent 与工具的交互记录；输出 "###STOP###" 结束回合进入评估（§3）。
- **任务实例**：对 agent 隐藏的用户指令（身份/意图/偏好，设计为在政策下只有唯一合法结局）+ ground truth 数据库写动作与必要输出（§3、Figure 2d）。
- **奖励** r = raction × routput ∈ {0,1}：最终数据库与唯一真值终态一致（raction），且给用户的回复包含全部必要信息（routput，子串匹配）；规则式评估快且忠实，但 r=1 不是合规的充分条件（agent 可能未经确认就写库）（§3）。
- **pass^k 指标**：与代码生成的 pass@k（k 次至少 1 次成功）相对，pass^k 定义为 k 次 i.i.d. 试验**全部**成功的任务比例（无偏估计 E_task[(c/n)^k]），捕捉同一任务在对话随机性下的可靠性；默认主指标为 pass^1 = E[r]（§3）。

### 2.3 基准构建（§4）

- 三阶段（§4）：Stage I 手工协同设计最简但自洽的数据库 schema、API 与政策（参考并简化真实域）；Stage II 用 gpt-4 生成可扩展的数据采样代码并人工修 bug（可按需生成如 1 万用户）；Stage III 手工写用户指令并用 gpt-4-turbo function-calling agent 试跑迭代消歧——每个 τ-retail 任务跑 **>40 次**试验，专查零/低成功率任务的歧义——真值标注可直接复制编辑 agent 的动作（§4、Figure 7）。
- τ-retail（§4.1）：500 users / 50 products / 1,000 orders，7 写 + 8 非写 API，115 任务；业务为取消/修改 pending 订单、退换 delivered 订单、改地址、查信息；关键规则：每单只能取消/修改一次、退换一次、不能跨产品类型换（§4.1、Table 1）。
- τ-airline（§4.1）：500 users / 300 flights（20 个美国城市间）/ 2,000 reservations，6 写 + 7 非写 API，50 任务；订改退与退款补偿，政策更 ad-hoc（支付方式组合限制、按会员等级×舱位的行李额、改签/取消条件），构成多跳推理难题（§4.1、Table 1）。
- 四个关键特性（§4.2）：真实对话与工具使用（LM 生成开放式自然用户话语）；开放多样任务（以质换量，小任务集 × 多试验即可分辨模型）；忠实规则式评估（唯一终态比对替代人工判断）；模块化扩展（代码库开源，便于社区加域加任务）。

### 2.4 实验设置（§5）

- 模型（§5）：OpenAI gpt-4o / gpt-4-turbo / gpt-4-32k / gpt-3.5-turbo；Anthropic claude-3-opus / sonnet / haiku；Google gemini-1.5-pro / flash；Mistral mistral-large / mixtral-8x22b；AnyScale meta-llama-3-70B（仅后两者开权重）；因难度不测 7/13B 小模型。
- 方法（§5）：主力为原生 function calling（FC，政策作系统提示，每轮自主决定回复用户或调工具）；对照 text 格式 ReAct 与 Act-only；明确排除 self-reflection（真实坐席只有一次服务机会）与 planning 类方法（实时性不足）；每任务限 30 个 agent 动作，主结果 ≥3 trials，agent 温度 0.0、用户温度 1.0。

### 2.5 主要发现（§5.1）

- **模型对比**（Table 2，pass^1，FC）：gpt-4o 最佳（retail 61.2 / airline 35.2 / 加权平均 48.2），gpt-4-turbo 57.7/32.4/45.1，gpt-4-32k 56.5/33.0/44.8，claude-3-opus 44.2/34.7/39.5，mistral-large 26.6，gpt-3.5-turbo 仅 15.4，llama-3-70B 14.6；开源权重模型与专有明显差距，所有模型都远未解决 τ-bench（§5.1）。
- **方法对比**：FC 一致优于 text 格式方法；ReAct 加推理轨迹稳定优于 Act-only；给 FC agent 加 "think" 函数无提升（FC 模型未朝该推理形式训练）（§5.1、Figure 3）。
- **pass^k 一致性**：gpt-4o 在 τ-retail pass^1 >60%，但 pass^8 跌破 25%；可靠性随 k 快速衰减是部署核心风险（§5.1、Figure 4、Abstract）。
- **成本**：gpt-4o FC agent + gpt-4 用户模拟在 τ-retail 每 task 分别 $0.38/$0.23，跑完一 trial 约 $200；agent 侧 95.9% 成本在输入提示（长政策 + 函数定义）（§5.1）。

### 2.6 研究挑战分析（§5.2）

- 失败分解：抽 115 条 gpt-4o FC 轨迹（τ-retail，1 trial），40 失败（pass^1 = 65.2%），其中 4 条为用户指令 typo/歧义（修复），余 36 条 agent 失败分四类（§5.2、Figure 5）。
- **错误参数/复杂库存推理**：工具类型对但参数填错（占约 25%）；幻觉调用方面 gpt-4o 每任务仅 0.46 次不存在 ID 的调用，gpt-3.5-turbo FC / Act 达 2.08 / 6.34 次（§5.2）。
- **错误信息**：漏给用户要的信息、算错总价或给错信息致用户决策偏离（§5.2）。
- **错误决策/政策遵循**（约 25%）：如政策规定"exchange 工具每单只能调一次、须收集齐所有换购项再调用"，gpt-4o 却先换一件导致第二件无法换、最终转人工（§5.2、Appendix C.2.1）。
- **复合请求部分完成**（约 19%）：ground truth 写动作越多越难（Figure 6）；如用户要修正所有订单地址，agent 只修了提及的那一单（§5.2、Appendix C.2.3）。
- **政策消融**（Table 3）：从系统提示移除政策后，τ-retail gpt-4o 61.2→56.8（−4.4）、gpt-3.5 20.0→14.5（−5.5）——简单域靠常识即可；τ-airline gpt-4o 33.2→10.8（−22.4）而 gpt-3.5 仅 −1.2——复杂 ad-hoc 规则只有强模型真正在用政策（§5.2）。

### 2.7 讨论、局限与未来工作（§6）

- 用户模拟器局限：指令可能有 typo/歧义；用户（合理地）不掌握复杂域政策；模拟 LM 自身在推理、计算、长上下文记忆与指令对齐上有限——但这也反映真实用户的多样性，责任在 agent（§6）。
- 其他改进方向：给模拟器加系统性检查保证唯一结局、政策做得更复杂、增加评估指标（如用 LM 检查规则遵循）、改进标注流程；**隐式偏置**：用 gpt-4-turbo FC agent 调 user prompt 可能向该模型倾斜（§6）。
- 对 agent 的核心结论：基于 LM function calling 的 agent **缺乏足够的一致性与规则遵循能力**支撑真实应用；需改进长程信息跟踪/记忆与上下文中聚焦关键信息的能力；域微调或 agent 脚手架是候选补救（§6）。
- 附录补充：A 任务难度谱（每任务 ≥40 gpt-4-turbo trials）；B 完整 API 清单（Table 4：retail 6 读 + 7 写 + calculate/transfer_to_human_agents；airline 5 读 + 6 写）；C/D 三类失败的完整轨迹与一条成功订票轨迹（certificate 支付规则、动态改意图处理）。

> 锚点：§1 Introduction; §3 τ-bench: A benchmark for Tool-Agent-User Interaction; §3 Pass^k metric; §4 Benchmark Construction; §4.1 Domains; §4.2 Key Characteristics; §5 Experiments; §5.1 Main results; §5.2 Research challenge analysis; §6 Discussion; Appendix B; Appendix C。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| gpt-4o FC pass^1（retail / airline / 加权平均） | 61.2 / 35.2 / 48.2（12 模型中最佳） | §5.1; Table 2 |
| gpt-4-turbo / gpt-4-32k / claude-3-opus 平均 pass^1 | 45.1 / 44.8 / 39.5 | §5.1; Table 2 |
| gpt-3.5-turbo / llama-3-70B 平均 pass^1 | 15.4 / 14.6（开源与专有差距显著） | §5.1; Table 2 |
| gpt-4o τ-retail pass^8 | <25%（pass^1 >60%，k 增大急跌） | §5.1; Abstract; Figure 4 |
| 方法对比 | FC > ReAct > Act（SOTA 模型上一致）；FC 加 "think" 无提升 | §5.1; Figure 3 |
| 移除域政策后 pass^1 | τ-retail：gpt-4o 61.2→56.8；τ-airline：gpt-4o 33.2→10.8（−22.4） | §5.2; Table 3 |
| 幻觉 ID 工具调用（次/任务，τ-retail） | gpt-4o 0.46 vs gpt-3.5-turbo FC 2.08 / Act 6.34 | §5.2 |
| gpt-4o 失败分解（115 任务 1 trial，pass^1 65.2%） | 36 个 agent 失败：错误决策约 25%、复合请求部分完成约 19% | §5.2; Figure 5 |
| 成本（gpt-4o FC + gpt-4 用户，τ-retail） | agent/用户每 task $0.38/$0.23；一 trial 约 $200；agent 侧 95.9% 为输入提示成本 | §5.1 |
| 基准规模 | retail 115 任务（500 users/50 products/1,000 orders）；airline 50 任务（500 users/300 flights/2,000 reservations）；每 retail 任务 ≥40 试验消歧 | §4.1; Table 1; §4 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2406.12045 |
| 代码与数据 | https://github.com/sierra-research/tau-bench（论文脚注声明 Code and data） |
| 后续扩展 | τ²-bench（本目录 24-Barres-TAU2_Bench_Dual_Control_v1.pdf，双控版）；FlowBench / IntellAgent / APIGen-MT / ToolSandbox（§2 Related Work 中的 follow-up） |
| 用户模拟基础 | Park et al., Generative Agents, 2023（LM 模拟人类角色，参考文献 [15]） |
| 指标背景 | pass@k 出自 HumanEval（Chen et al., 2021，参考文献 [5]）；本文提出其对偶指标 pass^k |

## 5. 一句话索引（给 Agent 用）

> τ-bench（Sierra，2024，ICLR 2025）用 **LLM 模拟用户（gpt-4-0613）+ 域政策系统提示 + 数据库终态比对判分**构建工具-代理-用户交互基准（τ-retail 115 任务 / τ-airline 50 任务），并提出可靠性指标 **pass^k**（k 次独立试验全部成功）。主结果：最佳 gpt-4o function calling pass^1 仅 61.2%（retail）/35.2%（airline），**pass^8 <25%**；移除政策使 airline 掉 22.4 个百分点；失败集中在错误参数、错误决策（约 25%）与复合请求部分完成（约 19%）——"平均能过"不等于"每次能过"，生产选型必须看 pass^k 并配规则护栏。
