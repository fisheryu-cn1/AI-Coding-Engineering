# 论文摘要：HORMA（分层组织检索的记忆智能体）

> **原论文标题**：Organize then Retrieve: Hierarchical Memory Navigation for Efficient Agents
> **完整 PDF 文件名**：`21-Hsu-HORMA.pdf`
> 作者 / 年份 / 出版：Hao-Lun Hsu, Nikki Lijing Kuang, Boyi Liu, Zhewei Yao, Yuxiong He（Duke University & Snowflake AI Research），2026，arXiv:2606.11680
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计**长视野智能体（long-horizon agent）**的工作记忆系统：解决历史轨迹无限增长造成的上下文过载、信息稀释、推理质量下降与推理成本升高。
- 设计**内存构建（组织）与内存检索解耦**的双模块架构：用 RD 分离减少联合优化中的信用分配（credit assignment）模糊。
- 设计**文件层级结构 + 自演进技能库（skill library）**：让智能体用 Bash 工具在层级目录里导航检索，记忆管理员从轨迹对比中学出内生 / 外生技能。
- 在严格上下文预算（ALFWorld 1950/2200 tokens、LoCoMo 10K、LongMemEval 50K）下，对比压缩型、嵌入检索型、状态外部记忆型方案，给效率-性能 Pareto 的实测参考。

> 锚点：Abstract；§1 Introduction（Figure 1）；§4.1 Memory-Augmented Agent Policy。

## 2. 主要观点与方案

### 2.1 核心问题与主张（"先组织、再检索"）

- LLM 智能体在长视野任务中存在"历史囤积者 vs. 损坏性压缩"二选一困境：纯追加耗尽上下文 + 增加延迟，纯摘要 / 折叠则不可逆丢失细粒度信息。
- 现有外部记忆系统把经验当成扁平条目，依靠语义相似度检索，无法捕捉**时间层级与因果依赖**，退化为浅层语义匹配。
- HORMA 把工作记忆外化成层级文件系统工作空间，由两类智能体协作：**Memory Manager M_m** 负责组织（结构化记忆构建），**Retrieval Agent M_r** 负责检索（导航式 + Bash 工具）。

### 2.2 方法结构

- **M-MDP 形式化**（§4.1）：把外部记忆 F_t 并入状态空间，分解为 π(a_t | o_t, F_t, q) = M_r(C_t | F_t, q)·M_θ(a_t | o_t, C_t, q)。
- **层级组织**（§4.2）：每个原始轨迹入库到时间戳目录，并由 M_m 抽取"人 / 实体 / 事件"等结构化笔记链接到原始轨迹，保留可追溯性。
- **递归技能精化**（§4.3）：定义 endogenous / exogenous 两类对比子集——H 成功 H' 失败（信息丢失） vs H 失败 H' 成功（缓解 hallucination / lost-in-the-middle）——用对比反馈精化管理 prompt P_m，等价于 textual gradient descent。
- **基于 GRPO 的检索 RL**（§4.4）：用 Bash 命令（ls/cd/grep/cat + select/done）在工作空间导航，奖励函数 r(C_t, E) = |C_t ∩ E|/|C_t ∪ E|（Jaccard 与 ground-truth evidence 的重叠），鼓励"最小但充分"的上下文；Qwen3.5-4B 上训练一次，跨 ALFWorld / LoCoMo / LongMemEval 跨域 OOD 泛化。
- **关键架构选择**：记忆构建 = 由强 LLM（Claude Sonnet 4.5）维持的持续管理技能积累过程（异步）；记忆检索 = 通过 RL 训练的轻量级检索智能体（同步），两者解耦。

> 锚点：§3 Preliminaries；§4.1–§4.4；Algorithm 1（附录）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| ALFWorld Small (1950 tok 预算) 成功率 | HORMA 56.7%，优于最优 baseline 27.0% (HIAGENT) | Table 1 |
| ALFWorld Large (2200 tok 预算) 成功率 | HORMA 73.9%，Pass-rate 排名第一 | Table 1 |
| LoCoMo 10K 上下文预算 Overall L-J | HORMA 51.6%，接近 No-limit 55.9% | Table 2 |
| LongMemEval 50K 上下文预算 Overall L-J | HORMA 55.9%，No-limit 20.4% / 仅 Qwen3.5-4B 检索器达 58.0%（最优） | Table 2 |
| LoCoMo token 用量占比 | 3.07% – 22.17% of baseline token usage | Figure 2(b) |
| LongMemEval token 用量占比 | 1.24% – 16.19% of baseline token usage | Figure 2(b) |
| Skill 库从空增至 63 项（LongMemEval 4 轮精化后） | 任务性能随技能数单调提升 | Figure 3(c)；Tables 9–11 |
| 检索器 OOD 泛化（Qwen3.5 4B GRPO 检索器） | LoCoMo 27→42.2%；LongMemEval 30.8→58.0% | Table 3 |

> 锚点：§5.2 Main Results（Tables 1–2，Figure 2）；§5.3 Analysis（Table 3，Figure 3）；附录 A.1–A.3 配置；附录 C Skill Examples（Tables 9–11）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | arXiv:2606.11680 |
| 评测基准 | ALFWorld（Shridhar et al. 2021）；LoCoMo（Maharana et al. 2024）；LongMemEval（Wu et al. 2025） |
| 主要基线 | ReSum (Wu et al. 2025)；Acon (Kang et al. 2025)；HIAGENT (Hu et al. 2025)；A-MEM (Xu et al. 2025)；Mem0 (Chhikara et al. 2025)；Embedding Retrieval；Truncation / Slide Window / Fold |
| 训练 RL 算法 | GRPO（DeepSeekMath, Shao et al. 2024） |
| 模型 | Claude Sonnet 4.5（主智能体 + 管理器）；Qwen3.5 4B（轻量级 RL 检索器） |
| 数据 | LoCoMo 训练集：前 7 个对话，1089 QA；测试集：3 对话，519 QA |
| 开源代码 | 无显式公开代码仓库（论文描述 prompt 模板见附录 D.4–D.6） |

> 锚点：§2 Related Work（压缩 / RL / 技能演进 三条主线）；§5.1 Experimental Setup；附录 B Implementation Details（Table 8 GRPO 超参数）。

## 5. 一句话索引（给 Agent 用）

> 设计长视野 Agent 工作记忆时，**别把"组织"和"检索"放在同一个 RL 目标里**：让强 LLM 异步通过对比轨迹学习记忆管理技能（domain-specific endogenous / exogenous skills），让轻量 LLM 同步在结构化文件层级里用 Bash 工具做导航式检索并以 evidence-Jaccard 奖励训练——HORMA 在三大长视野基准上以 1–22% 的 token 用量达到了接近无预算上限的水平。
