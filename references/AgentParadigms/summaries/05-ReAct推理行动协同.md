---
title: "ReAct: Synergizing Reasoning and Acting in Language Models"
source_pdf: "05-Yao-ReAct_v3.pdf"
arxiv_id: "2210.03629"
arxiv_version: "v3"
authors:
  - "Shunyu Yao"
  - "Jeffrey Zhao"
  - "Dian Yu"
  - "Nan Du"
  - "Izhak Shafran"
  - "Karthik Narasimhan"
year: 2022
venue: "ICLR 2023 (Oral)"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：ReAct——语言模型中推理与行动的协同范式

## 1. 适用场景

- 当你要为**需要外部工具/环境交互**的任务选默认 agent 控制流（Thought-Action-Observation 单循环）时读这篇。
- 当你要权衡"**推理引导行动 vs 行动获取信息**"，并设计 ReAct 与 CoT 互相回退（backoff）的组合策略时。
- 当你要评估**少样本提示 vs 模仿/强化学习**的性价比（1–2 个 in-context 示例对抗 10^3–10^5 条训练轨迹）时。
- 当你要对 agent 失败模式做**错误分类**（幻觉、检索失败、推理循环、标签过期）并据此选缓解手段时。
- 当你要设计**人类在线编辑 thought** 的人机协同接口（改一两句推理即可纠偏整条轨迹）时。
- 当你需要复现或移植 ReAct prompting（附录 C 给出 HotpotQA/FEVER/ALFWorld/WebShop 全部 prompt 模板）或换用 GPT-3 等其他基座模型（Appendix A.1）时。

> 锚点：Abstract; §1 INTRODUCTION; §2 REACT: SYNERGIZING REASONING + ACTING; §3 KNOWLEDGE-INTENSIVE REASONING TASKS; §4 DECISION MAKING TASKS; §5 RELATED WORK; §6 CONCLUSION。

## 2. 主要观点与方案

### 2.1 动机与核心思想（§1 INTRODUCTION；§2）

- 人类学背景：人类在行动间穿插内部言语（inner speech）来自我调节、制定策略、维护工作记忆；做菜时用语言追踪进度、处理异常（"没盐了用酱油代替"）、判断何时需要外部信息。
- 两条既有路线各自的缺陷：CoT 推理是**静态黑箱**——不接地于外部世界，导致事实幻觉与推理过程中的错误传播（Figure 1(1b)）；行动生成类方法只用语言先验预测动作，**缺乏对高层目标的抽象推理与工作记忆**。
- ReAct：让 LLM 以交错方式同时生成**推理轨迹（reasoning traces）与任务专属动作**——推理用于归纳、追踪、更新行动计划并处理异常（reason to act）；行动用于与知识库/环境交互获取额外信息注入推理（act to reason）。

### 2.2 方法形式化与特性（§2）

- 形式化：扩充动作空间 **Â = A ∪ L**（L 为语言空间）。thought 不影响外部环境、不产生观察反馈，仅基于当前上下文 c_t 组合有用信息并更新 c_t+1 以支撑后续推理/行动；有用 thought 类型包括分解目标建计划、注入常识、从观察中抽取要点、追踪进度切换子目标、处理异常调整计划等。
- 实现设定：冻结的 PaLM-540B 配少样本 in-context 示例（人类标注的动作-thought-观察轨迹）；知识密集任务用**密集 thought**（thought 与动作逐轮交替），决策任务用**稀疏 thought**（由模型自行决定 thought 出现时机）；语言空间无界，学习困难，因此依赖强语言先验（大模型）。
- 四个特性：A) 设计直观（标注者照抄自己的思考即可，无需 ad-hoc 格式/示例挑选）；B) 通用灵活（适配 QA、事实核查、文字游戏、网页导航等不同动作空间与推理需求）；C) 强健（仅 1–6 个示例即泛化，稳定超过 only-reasoning / only-acting 基线）；D) 人类可对齐可控制（可检查推理与事实正确性，可通过编辑 thought 在线纠偏）。

### 2.3 知识密集任务：设置、方法与结果（§3.1 SETUP；§3.2 METHODS；§3.3 RESULTS AND OBSERVATIONS）

- 设置（§3.1）：HotpotQA（多跳 QA）与 FEVER（事实核查，SUPPORTS/REFUTES/NOT ENOUGH INFO），均为 question-only 设定（不给支撑段落）；动作空间为简化 Wikipedia API：search[entity]（返回词条前 5 句或 top-5 相似词条）、lookup[string]（返回页面中下一句含该串的句子，模拟 Ctrl+F）、finish[answer]；刻意弱于 SOTA 检索器，以逼模型用显式语言推理来检索。
- 方法（§3.2）：HotpotQA/FEVER 分别随机取 6/3 个训练样例手工编写 ReAct 轨迹作 few-shot（更多示例不提性能）；基线由 ReAct 轨迹消融构造——Standard、CoT（去动作与观察）、CoT-SC（21 条采样、温度 0.7 取多数）、Act（去 thought）；组合策略：ReAct→CoT-SC（ReAct 在 HotpotQA/FEVER 分别 7/5 步内无答案则回退）与 CoT-SC→ReAct（多数答案出现次数 < n/2 则回退）；微调用 STaR 式 bootstrap——以 ReAct 生成的 3,000 条答案正确轨迹微调 PaLM-8/62B 解码完整轨迹。
- 结果（§3.3，PaLM-540B，Table 1）：ReAct 在两任务上均超 Act（HotpotQA 27.4 vs 25.7 EM；FEVER 60.9 vs 58.9 Acc）；对 CoT 有胜有负（FEVER 60.9 vs 56.3 胜；HotpotQA 27.4 vs 29.4 略负）；最佳提示方法是组合：HotpotQA 上 ReAct→CoT-SC 35.1 EM、FEVER 上 CoT-SC→ReAct 64.6 Acc；两种组合在不同 CoT-SC 采样数下均稳定超 CoT-SC，用 3–5 个样本即达 CoT-SC 21 样本性能（Figure 2）。
- 行为差异分析（Table 2，HotpotQA 各抽 50 条对/错轨迹共 200 例人工标注）：CoT 成功样本中假阳性 14%（ReAct 6%），幻觉占其失败主因 56%（ReAct 0%）；ReAct 轨迹更接地、事实驱动，但交替结构约束降低推理灵活性——推理错误 47%（CoT 16%），典型模式是重复生成先前的 thought/action 跳不出循环（作者猜测与贪心解码有关，beam search 可能缓解）；检索无信息（23% 失败）会带偏推理且难恢复；另有 29%/28% 为标签歧义（含标签过期，Appendix A.2 例：仅 ReAct 借真实网络交互拿到最新答案）。
- 微调结果（Figure 3）：PaLM-8/62B 上提示式 ReAct 四法中最差（小模型难从示例学推理+行动）；但仅用 3,000 条轨迹微调后 ReAct 反超成最佳——PaLM-8B 微调 ReAct 超所有 PaLM-62B 提示方法，PaLM-62B 微调 ReAct 超所有 540B 提示方法；微调 Standard/CoT 明显差于微调 ReAct/Act，因前者教模型记忆（可能幻觉的）事实，后者教模型（推理并）行动取数这一更可泛化的技能。

### 2.4 决策任务：设置与结果（§4 DECISION MAKING TASKS）

- ALFWorld 设置：6 类家务任务、任务实例可含 50+ 地点、专家策略需 50+ 步；每类随机标注 3 条轨迹、取 2 条排列构造 6 个 prompt；134 个 unseen 评测局、task-specific 设定；基线 BUTLER 为每类 10^5 条专家轨迹训练的模仿学习 agent（另有 GPT-2 微调方法因跨任务训练不纳入）。Act prompt 用同一批轨迹去 thought，构成受控对比。
- ALFWorld 结果（Table 3）：最佳 ReAct 试验平均成功率 71%，显著超最佳 Act（45%）与 BUTLER（37%）；最差 ReAct（48%）仍胜两者最佳；六组受控试验中 ReAct 对 Act 相对增益 33%–90%、平均 62%；定性上无 thought 的 Act 无法分解目标为子目标、丢失环境状态（附录 D.2.2 的循环失败轨迹）。
- WebShop 设置：1.18M 真实商品、12k 人类指令、500 条测试指令；动作含 search、click 商品/选项、Buy Now；1-shot prompting；对比 IL（1,012 条人类轨迹训练）与 IL+RL（再加 10,587 条训练指令）；指标为平均 score（属性覆盖率）与成功率 SR。
- WebShop 结果（Table 4）：ReAct 66.6 score / 40.0 SR，绝对提升 10 个百分点成功率超此前最佳；Act 已与 IL/IL+RL 持平（62.3/30.1 vs 59.9/29.1、62.4/28.7）；人类专家 82.1/59.6 仍远未达到（人类做更多商品探索与查询改写）。
- 内部推理 vs 外部反馈消融（ReAct-IM，Appendix B.2）：将同批轨迹重标为 Inner Monologue 式稠密外部反馈 thought（只分解当前目标与当前子目标），ReAct 71 vs ReAct-IM 53 整体成功率——IM 式反馈缺子目标完成判断、下一子目标决策与常识定位（如"台灯常在桌上"），证明 ReAct 的价值在于**灵活稀疏的内部推理**而非简单反应外部反馈。

### 2.5 人机协同与模型迁移（Appendix A.1；Appendix A.3）

- 人类 thought 编辑（Figure 5，ALFWorld）：删掉 Act 17 的一句幻觉 thought、在 Act 23 加提示，轨迹即彻底改向并成功；相比敲几十个动作，人只需编辑两三句 thought——且这种在途策略编辑对 Act 与既往 RL 方法难以实现（无法改参数、改个别动作不改其余行为），也超出 IM 式对话更新目标的范围（可改模型内部信念与推理风格）。
- 模型迁移（Table 5）：GPT-3（text-davinci-002，贪心解码）在 HotpotQA（500 验证问题子集）30.8 EM 与 ALFWorld（134 任务）78.4 成功率均超 PaLM-540B（29.4 / 70.9），或因指令微调；证明 ReAct prompting 跨基座有效。

### 2.6 相关工作、结论、局限与伦理（§5 RELATED WORK；§6 CONCLUSION；ETHICS STATEMENT；REPRODUCIBILITY STATEMENT）

- 相关工作（§5）：推理线（CoT、least-to-most、zero-shot CoT、CoT-SC、Selection-Inference、STaR、Scratchpad、faithful reasoning）均为孤立固定推理，ReAct 把动作与观察纳入连贯推理流；决策线（WebGPT、BlenderBot/Sparrow/SimpleTOD、SayCan、Inner Monologue）不显式建模推理或依赖昂贵人工反馈/数据集；Inner Monologue 是最接近的闭环先行工作，但其"内心独白"仅是环境状态反馈的注入。
- 结论与局限（§6）：复杂任务的大动作空间需要更多示例，易超出 in-context 上下文长度限制；提示式设定下对推理/行动行为的支持有限；HotpotQA 微调初见成效，更多高质量人工标注是进一步提升之道；未来方向为多任务规模化和与强化学习等互补范式结合。
- 伦理（Ethics）：连接 LLM 与外部环境动作空间有风险（检索不当/隐私信息、有害动作）；实验以限定站点（Wikipedia、WebShop 研究基准不可真买、不可编辑词条）与无危险动作空间来最小化风险。
- 可复现性：主实验基于未公开的 PaLM；附录 C 提供全部 prompt，Appendix A.1 补 GPT-3 实验，GPT-3 ReAct 代码见项目页。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| HotpotQA EM（PaLM-540B） | ReAct 27.4 vs CoT 29.4、Act 25.7、Standard 28.7；最佳提示 ReAct→CoT-SC 35.1；监督 SoTA 67.5 | §3.3 Table 1 |
| FEVER 准确率（PaLM-540B） | ReAct 60.9 vs CoT 56.3、Act 58.9、Standard 57.1；最佳提示 CoT-SC→ReAct 64.6；监督 SoTA 89.5 | §3.3 Table 1 |
| 幻觉占比（HotpotQA 200 例人工分析） | CoT 失败中幻觉 56%、成功中假阳性 14%；ReAct 分别为 0% 与 6% | §3.3 Table 2 |
| 组合策略采样效率 | ReAct+CoT-SC 用 3–5 个样本达到 CoT-SC 21 样本的性能 | §3.3 Figure 2 |
| 微调扩展性（3,000 轨迹） | PaLM-8B 微调 ReAct 超所有 PaLM-62B 提示方法；PaLM-62B 微调 ReAct 超所有 540B 提示方法 | §3.3 Figure 3 |
| ALFWorld 平均成功率（134 unseen 任务） | 最佳 ReAct 71% vs 最佳 Act 45%、BUTLER 37%（绝对 +34 个百分点）；最差 ReAct 48% 仍胜两者最佳；对 Act 相对增益 33%–90%、均值 62% | §4 Table 3 |
| ALFWorld 消融（IM 式 thought） | ReAct 71% vs ReAct-IM 53% 整体成功率 | §4 Table 3 |
| WebShop（500 测试指令） | ReAct 66.6 score / 40.0 SR vs Act 62.3 / 30.1、IL 59.9 / 29.1、IL+RL 62.4 / 28.7（SR 绝对 +10 个百分点）；人类专家 82.1 / 59.6 | §4 Table 4 |
| 示例需求 | ALFWorld/WebShop 仅 1–2 个 in-context 示例、未微调（对手用 10^3–10^5 条轨迹训练） | Abstract; §4 |
| GPT-3（text-davinci-002）迁移 | HotpotQA 30.8 EM、ALFWorld 78.4%，均超 PaLM-540B 的 29.4 / 70.9 | Appendix A.1 Table 5 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2210.03629（v3，ICLR 2023 Oral） |
| 项目页与代码 | https://react-lm.github.io/（含 GPT-3 ReAct prompting 代码与全部 prompt） |
| 基准 | HotpotQA、FEVER、ALFWorld、WebShop（论文四大实验基准） |
| 关联读本 | 本目录 06（Reflexion 外循环）、09（LLMCompiler 并行化）、13（AutoGen A3 直接集成 ReAct prompting） |

## 5. 一句话索引（给 Agent 用）

> 要为带工具/环境交互的任务选控制流基线时读这篇：ReAct（ICLR 2023 Oral，arXiv:2210.03629）把动作空间扩充为 Â=A∪L，让 PaLM-540B 以 Thought-Action-Observation 交错生成、用推理引导行动、用行动喂给推理；仅 1–2 个 in-context 示例：ALFWorld 最佳 71% 成功率（最佳 Act 45%、BUTLER 37%，绝对 +34 个百分点）、WebShop 40% SR（绝对 +10 个百分点）；HotpotQA/FEVER 上与 CoT 互补，组合后 35.1 EM / 64.6 Acc，且幻觉失败从 CoT 的 56% 降到 0%（代价是推理错误率升高、检索失败会沿轨迹传播）；大动作空间受上下文长度限制，微调 3,000 条轨迹即可让小模型反超大模型提示。
