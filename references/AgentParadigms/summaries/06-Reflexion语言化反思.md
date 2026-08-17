---
title: "Reflexion: Language Agents with Verbal Reinforcement Learning"
source_pdf: "06-Shinn-Reflexion_v4.pdf"
arxiv_id: "2303.11366"
arxiv_version: "v4"
authors:
  - "Noah Shinn"
  - "Federico Cassano"
  - "Edward Berman"
  - "Ashwin Gopinath"
  - "Karthik Narasimhan"
  - "Shunyu Yao"
year: 2023
venue: "NeurIPS 2023"
type: "设计参考 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：Reflexion——语言化反思强化（verbal reinforcement learning）外循环

## 1. 适用场景

- 任务具备可验证成败信号（单元测试、环境判定、exact match）且允许迭代重试，想在 ReAct/CoT 内循环外再加"评估→语言反思→重试"外循环时读这篇。
- 想不更新权重就让 agent 从失败中积累经验（把反思文本存入 episodic memory 并注入下次尝试上下文）时。
- 为编程 agent 设计"自生成单元测试 + 测试失败触发反思"的 pass@1 合格流程，或评估自评信号质量（flaky test 假阳/假阴）风险时。
- 需要反思式 agent 的适用边界证据：何时有效（ALFWorld/HotPotQA/HumanEval）、何时失效（WebShop 局部最优、弱模型无自纠能力）时。
- 需要新代码生成基准（LeetcodeHardGym：40 道 GPT-4 预训练截止后的 LeetCode hard 题、19 种语言）时。

> 锚点：Abstract; §1 Introduction; §3 Reflexion: reinforcement via verbal reflection; §4 Experiments; §5 Limitations。

## 2. 主要观点与方案

### 2.1 动机与核心主张（§1 Introduction; §2 Related work）

- LLM agent 以往只能靠 in-context 示例教学，传统梯度 RL 样本与算力开销大。Reflexion 提出"语言强化"：把环境/内部的二元或标量反馈放大为自然语言反思总结，作为下次 episode 的附加上下文，充当"语义梯度"（§1）。
- 反馈来源三途：简单二元环境反馈、常见失败的预定义启发式、自评估（LLM 二元分类或自写单元测试）（§1）。
- 相对传统 RL 的四点优势：轻量免微调、反馈可细粒度指向具体动作、episodic memory 显式可解释、为后续动作提供明确 hint；两点劣势：依赖 LLM 自评能力、无形式化收敛保证（§1）。
- §2 用两张特性表对比相关工作：决策/推理侧的 Self-Refine（仅单次生成自 refine）、beam search、decider 模型、retry 模式等缺持久记忆或二元奖励；编程侧的 AlphaCode/CodeT/Self-Debugging/CodeRL 依赖隐藏测试（失去 pass@1 资格）或无自反思步骤。

### 2.2 框架组件与迭代流程（§3 Reflexion: reinforcement via verbal reflection）

- **Actor（Ma）**：基于 LLM 生成文本与动作，可用 CoT 或 ReAct 作为生成策略，并附加记忆 mem 提供额外上下文（政策 = 记忆编码 + LLM 参数）。
- **Evaluator（Me）**：给轨迹打分 r_t = Me(τt)；变体包括 exact match（推理）、任务定制启发式（决策）、LLM 自评（决策/编程）。
- **Self-Reflection 模型（Msr）**：输入稀疏奖励（如二元成败）+ 当前轨迹 + 持久记忆，生成具体、第一人称、可执行的经验总结——比标量奖励信息量大。
- **双轨记忆**：trajectory 为短期记忆，sr_t 追加进长期记忆 mem；mem 以最大条数 Ω（通常 1–3）滑窗截断以适配上下文上限。
- **Reflexion 过程（Algorithm 1）**：生成轨迹 → Evaluator 评估 → Self-Reflection 生成 sr_t 追加 mem → 重置环境进入下一 trial，循环直至 Evaluator 通过或达最大尝试次数。

### 2.3 实验设置（§4 Experiments）

- 决策：ALFWorld 134 个环境、6 类任务，ReAct 作动作生成器；两种自评——LLM 自然语言分类与手写启发式（同一动作同响应重复 >3 轮，或动作数 >30 判为低效规划）；基线组触发自评后跳过反思直接重试（§4.1）。
- 推理：HotPotQA 100 题；CoT 6-shot（Q→A 与 Q,Cgt→A 隔离纯推理）、ReAct 2-shot（Wikipedia API 检索）、self-reflection 2-shot；题间用 exact match 给二元信号，失败任务重试至连续 3 次失败（§4.2）。
- 编程：HumanEval/MBPP 的 Python 及经 MultiPL-E 翻译的 Rust；新基准 LeetcodeHardGym（40 道 2022-10-08 即 GPT-4 预训练截止后的 LeetCode hard 题，19 语言）。用 CoT 生成多样单元测试、AST 过滤语法无效项、采样最多 6 条组成测试套件；记忆上限 1 条经验（§4.3）。

### 2.4 主要结果与分析（§4.1 Sequential decision making: ALFWorld; §4.2 Reasoning: HotpotQA; §4.3 Programming）

- ALFWorld：ReAct+Reflexion（启发式自评）完成 130/134，12 轮迭代内较基线绝对 +22%；基线 ReAct 幻觉率收敛在 22% 无长期恢复。反思收益两类：定位长轨迹早段错误（改动作或换全局计划）、跨 trial 穷举式搜索房间（§4.1; Figure 3）。
- HotPotQA：temperature 0.7 下 ReAct-only / CoT-only / CoT(GT)-only 后续 trial 一题未新增解决；Reflexion 使 ReAct +20%；CoT(GT) 仍有 39% 题答错，Reflexion 在无 GT 答案前提下 +14%。消融：在 episodic memory（EPM，重放最近轨迹）之上，自反思再 +8% 绝对——refine-only 不如 reflection 引导的 refine（§4.2; Figure 4）。
- 编程：HumanEval(PY) 91% 超 GPT-4 的 80.1%；HumanEval(RS) 68% vs 60%、MBPP(RS) 75.4% vs 70.9%、LeetcodeHard(PY) 15% vs 7.5% 全面刷新 SOTA；唯 MBPP(PY) 77.1% 低于 GPT-4 80.1%（Table 1）。
- MBPP 落后归因（Table 2 TP/FN/FP/TN 分解）：假阳率 P(错|自测全过) 在 MBPP 为 16.3% 而 HumanEval 仅 1.4%，flaky/错误测试使 agent 过早提交；假阴优于假阳——agent 可借反思识别错误测试并保留原实现（§4.3）。
- 组件消融（HumanEval Rust 最难 50 题，GPT-4；Table 3）：去自测生成 0.52 < 基线 0.60 = 去自反思 0.60 < 完整 Reflexion 0.68——无测试则无法判断实现正确性、被迫全程迭代做有害修改；无反思则测试/编译错误指示无法转化为有效修复，说明盲目 trial-and-error 调试在难任务上无效（§4.3）。

### 2.5 模型强度、失效面与局限（Appendix A Evaluation with additional models; Appendix B.1 WebShop Limitation; §5 Limitations）

- 自我纠错是强模型的涌现能力：starchat-beta 上 Reflexion 0.26 = 基线 0.26 无提升；CoT(GT)+text-davinci-003 / gpt-3.5-turbo / gpt-4 为 0.60/0.57/0.68 → 0.77/0.71/0.80，ReAct 对应 0.30/0.26/0.39 → 0.55/0.38/0.51（Appendix A Tables 4–5）。
- WebShop（100 环境，2-shot ReAct+Reflexion）：4 个 trial 无改进即终止，且失败后写不出有用的自反思——需要高度多样/创造性探索的任务易陷局部最优；对比 ALFWorld（动作空间可从观察读出）与 HotPotQA（Wikipedia 搜索空间更宽容）（Appendix B.1; Figure 6）。
- §5 局限：语言层策略优化仍会收敛到非最优局部极小；记忆只是滑窗，未来可扩展为向量库或 SQL 库；测试驱动开发对非确定生成器、带 API 副作用的非纯函数、随硬件变化的输出、并行/并发行为难以规格化输入输出映射。

### 2.6 结论、伦理与复现（§6 Broader impact; §7 Conclusion; §8 Reproducibility）

- 结论：verbal reinforcement 让 agent 从错误中学习并显著超过主流决策方法；未来可把传统 RL 技术搬进语言层（自然语言 value learning、off-policy 探索）（§7）。
- Broader impact：放大自动化收益与滥用风险；同时语言化反思让 agent 更可解释、可诊断——例如工具调用前可审查其反思意图（§6）。
- 复现警告：自治代码实验务必使用隔离执行环境，生成代码未经校验即运行（§8）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| HumanEval (PY) pass@1 | 91.0%（前 SOTA：CodeT+GPT-3.5 65.8%、GPT-4 80.1%） | §4.3 Table 1; Abstract |
| HumanEval (RS) pass@1 | 68.0% vs GPT-4 60.0% | §4.3 Table 1 |
| MBPP (PY) pass@1 | 77.1% vs GPT-4 80.1%（自测假阳率 16.3% 拖累） | §4.3 Table 1; Table 2 |
| MBPP (RS) / LeetcodeHard (PY) pass@1 | 75.4% vs 70.9%；15.0% vs 7.5% | §4.3 Table 1 |
| ALFWorld | 完成 130/134，12 轮内绝对 +22%（启发式自评） | §4.1 |
| HotPotQA | ReAct+Reflexion +20%；CoT(GT)+Reflexion 无 GT 答案下 +14% | §1; §4.2 |
| 自反思 vs EPM 消融 | 在 episodic memory 之上再 +8% 绝对 | §4.2 Figure 4(c) |
| 组件消融（HumanEval RS 最难 50 题） | 完整 0.68 > 基线/去自反思 0.60 > 去自测 0.52 | §4.3 Table 3 |
| 弱模型边界 | starchat-beta：Reflexion 0.26 = 基线 0.26，零提升 | Appendix A Table 4 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2303.11366 |
| 代码 / 数据 | https://github.com/noahshinn024/reflexion （Abstract：放出全部 code、demos、datasets） |
| 新基准 | LeetcodeHardGym：40 道 2022-10-08 后发布的 LeetCode hard 题、19 种语言（§1; §4.3） |
| 关联 | 本目录 05（ReAct 内循环）、19（self-conditioning：含错上下文的反面证据） |

## 5. 一句话索引（给 Agent 用）

> 任务可验证、可重试时把"从失败中学习"外置到语言层：Reflexion 用 Actor+Evaluator+Self-Reflection+双轨记忆把稀疏反馈转成第一人称语言反思存档并在下次尝试注入（不更新权重），HumanEval pass@1 达 91%（vs GPT-4 80.1%）、ALFWorld +22%、HotPotQA +20%；自反思比单纯重放轨迹再 +8%。失效面：自测假阳（MBPP 16.3% vs HumanEval 1.4%）、弱模型零提升（starchat-beta 0.26）、WebShop 式局部最优——选型先确认反馈信号可靠且模型够强。
