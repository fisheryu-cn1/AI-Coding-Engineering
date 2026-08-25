---
title: "Characterizing Readability Issue Patterns and the Role of Prompt Design in LLM-Generated Code"
source_pdf: "15-Ye-Readability_Issues_LLM_Code_v2.pdf"
arxiv_id: "2605.13280"
arxiv_version: "v2"
authors:
  - "Hengzhi Ye"
  - "Fengyuan Ran"
  - "Weiwei Xu"
  - "Minghui Zhou"
year: 2026
venue: "arXiv"
type: "内容索引"
generated_at: "2026-08-25"
summary_version: "1.0"
---

# 论文摘要：LLM 生成代码可读性问题模式与提示设计（北京大学）

## 1. 适用场景

- 当你需要**"LLM 生成代码 vs 人类手写代码"可读性的大规模成对实证基线**（如制定 AI 生成代码的 review/准入策略、论证是否需要专门的可读性门槛）时，读这篇——2,735 个真实场景 × 5 个前沿 LLM 的同任务配对比较。
- 当你要为 **LLM 典型可读性问题设计检测/清理工具**（linter 规则、CI 检查项）时，读其 §VI 的问题模式清单——尤其是三个开放编码发现的 LLM 特有模式：Unknown API、Redundant Variables、Overblanking。
- 当你要决定**在 prompt 中投入哪些维度改善生成代码可读性**（function signature / constraints / style description 的取舍与上限）时，读其 §VII 的受控变体实验。
- 当你需要一个**可复用的代码可读性评估模型**（TF/BWF/PF/DF 四类特征 + 特征选择）或 LLM-人类可读性 benchmark 构建方法时，读 §IV 与贡献清单。

> 锚点：Abstract; §I Introduction; §III Methodology; §IV Readability Model; §V RQ1; §VI RQ2; §VII RQ3; §VIII Discussion

## 2. 主要观点与方案

- **可读性评估模型**（§IV; Table III）：整合四类文献指标族——TF 文本/语义 16 维、BWF 结构/排版 26 维、PF 信息论/熵 4 维、DF 视觉/几何 15 维，共 61 维候选特征；在 Dorn 数据集（360 个人类标注 snippet）上做 10 折分层交叉验证 + Sequential Forward Selection（SFS），25 特征模型达 77.5% Accuracy / 83.8% AUC，优于任一单一特征族（最高 BWF+SFS 72.9%/80.5%）与 Scalabrino 的 LFS 配置（72.8%/73.7%）。
- **实验设计**（§III-A; §III-B; §III-C）：2,735 个 prompt-人类实现对（WoC 1,000 + LeetCode 1,735；Python 函数级 5–100 行、2022 前 snapshot 保证人类手写），输入 GPT-5、Claude-4.6、DeepSeek-v4、Gemini 3、Qwen 3.5（temperature=0，max tokens=4,096）；LeetCode 子集须通过平台测试（pass@1 94.5%–95.6%）才进入比较。RQ3 用可读性最优的 Claude-4.6，在 164 HumanEval + 164 MBPP 上构造 8 个 prompt 维度的受控变体（每基线 16 个 prompt，共 5,248 对；通过测试保留 5,024）。
- **RQ1 总体相当、情境有别**（§V; Table IV; Fig 2）：LLM 代码总体可读性与人类相当甚至略优——WoC 上五个模型 win rate 全部过半（51.30%–64.70%），LeetCode 上优势收窄（总体 51.15%），GPT-5 在均值与 win rate 上均低于人类（2.93 vs 3.17；41.76%）；Wilcoxon 配对检验 p<0.001 但效应量小（r=0.104，N=13,263）。分布上人类代码更一致（四分位距更紧），LLM 代码跨任务方差更大。解读：竞赛题人类已有稳定解法模式、提升空间小；真实工程代码"功能优先"使人类代码更不整齐，LLM 靠预训练风格正则获益。
- **RQ2 失败模式相反：人类"欠生产"、LLM"过生产"**（§VI; Table V; Table VI）：对每来源随机 500 对做混合演绎-归纳主题分析（best-case sampling：每任务取五模型中最可读输出；维度编码 Cohen's Kappa 0.81–0.89，模式编码 0.73–0.85）。维度层：人类难读代码集中在 BWF（76）+TF（72），LLM 难读代码集中在 TF（60）+PF（53）——LLM 少排版问题、多语义表达与信息负载问题。模式层：人类最常见 Deficient Comments（DC 60）与 Inconsistent Style（IS 58），Redundant Comments 极少（RC 3）；LLM 最常见 Excessive Complexity（EC 48）与 Redundant Comments（RC 24），Code Duplication 极少（CD 2）。开放编码新增三个 LLM 特有模式：**Unknown API**（无充分上下文的外部库调用，无论真假 API）、**Redundant Variables**（多变量同职能造成不必要间接层）、**Overblanking**（无语义边界的过度空行）。两组总分相近可由完全不同的底层原因造成。
- **RQ3 提示设计作用显著但有界**（§VII; Fig 4; Table VII）：随机森林回归（n_estimators=100）特征重要性排序：function signature 0.4011 > constraints 0.2042 > style description 0.1781 > persona 0.0708 > few-shot 0.0588 > task category 0.0455 > IO contract 0.0415——贴近生成代码"形态"的维度关联更强。t-test + permutation（10,000 次）三角验证：增量设置（最小任务描述 + 一维）中仅 style description（p=0.001）与 constraints（p=0.000）显著；消融设置（全维 prompt − 一维）中仅去掉 function signature 显著（p=0.003）。但模型 R²<0.3：prompt 维度只解释可读性变化的一部分，应视作轻量杠杆而非决定因素。
- **讨论：readability debt 与工具化方向**（§VIII）：LLM 典型问题（逻辑膨胀、冗余注释、未解释 API）会累积成"生成时看似可接受、实则抬高未来理解与维护成本"的可读性债；建议 benchmark 超越正确性评估可读性、review/CI 工具加入 LLM 特有检查（逻辑膨胀、变量冗余、未解释 API）、以及"自动检测问题→生成针对性精炼指令"的工具方向；多轮交互中每轮阅读成本累积、不因最终输出变好而抵消，故单轮可读性仍是前提（§VIII-A）。局限性：函数级粒度使 High Coupling 不可见；best-case 采样与最强模型设定下结论描述的是"强 LLM 输出的残余可读性弱点"（§VIII-C）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| 可读性模型性能（Dorn 360 snippet，10 折 CV） | 最佳 All-features+SFS（25 特征）77.5% Accuracy / 83.8% AUC；默认 21 特征 74.4% / 83.4%；全 61 特征 71.7% / 80.5%；LFS 72.8% / 73.7% | §IV-B; Table III |
| RQ1 WoC win rate（人类均值 -0.15） | 五模型 51.30%（Qwen 3.5）– 64.70%（Gemini 3），全部过半；总体 57.46%（LLM 均值 0.22） | §V; Table IV |
| RQ1 LeetCode win rate | 总体 51.15%（LLM 3.25 vs 人类 3.15）；Claude-4.6 最高 57.75%；GPT-5 低于人类 41.76%（2.93 vs 3.17） | §V; Table IV |
| LLM-人类配对差异 | Wilcoxon signed-rank p<0.001，效应量 r=0.104（N=13,263 对）——统计显著但幅度小 | §V |
| RQ2 维度分布（Human-bad vs LLM-bad） | Human：BWF 76 / TF 72 / DF 45 / PF 21；LLM：TF 60 / PF 53 / DF 30 / BWF 26 | §VI; Table V |
| RQ2 问题模式（Human-bad vs LLM-bad） | Human：DC 60 / IS 58 / EC 41 / RC 3 / CD 6；LLM：EC 48 / RC 24 / PN 21 / DC 10 / CD 2；HC 两组均 0 | §VI; Table VI |
| 主题分析编码信度 | 维度 Cohen's Kappa 0.81–0.89（均值 0.84）；模式 0.73–0.85（均值 0.79） | §III-D |
| RQ3 prompt 维度特征重要性 | function signature 0.4011 > constraints 0.2042 > style description 0.1781 > persona 0.0708 > few-shot 0.0588 > task category 0.0455 > IO contract 0.0415 | §VII; Fig 4 |
| RQ3 统计显著性（阈值 p<0.01） | 增量设置：style description p=0.001、constraints p=0.000；消融设置：仅 function signature p=0.003（t-test 与 permutation 一致） | §VII; Table VII |
| RQ3 解释力上限 | 随机森林 R²<0.3——prompt 维度仅解释部分可读性变化 | §VII |
| 生成代码功能正确性（pass@1） | LeetCode：GPT-5 95.6%、Claude-4.6 94.5%、DeepSeek-v4 95.6%、Gemini 3 95.5%、Qwen 3.5 95.0%；Set B：MBPP 95.1%、HumanEval 96.3% | §III-C |
| 评估规模 | 2,735 对（WoC 1,000 + LeetCode 1,735）× 5 模型；RQ2 人工标注 1,000 对（每来源 500）；RQ3 5,248 个 prompt 变体（保留 5,024） | §III-A; §III-B; §III-D |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2605.13280（v2，2026-08-03） |
| 数据源 | World of Code（version U，c2fbb commit-to-file 映射，2021-10 发布）；LeetCode（2022 前 Python 高赞题解） |
| 受控实验基准 | MBPP、HumanEval（各 164 题，RQ3 prompt 维度变体的构造基础） |
| 可读性指标族出处 | TF：Scalabrino et al.；BWF：Buse & Weimer（2008）；PF：Posnett et al.（2011）；DF：Dorn（2012）；模型验证用 Dorn 数据集（360 snippet，人类二值标注） |
| 被评估 LLM | GPT-5、Claude-4.6、DeepSeek-v4、Gemini 3、Qwen 3.5 |
| 关联论文（主题互证，非本文引用链） | 本库 SEforLLM/10（GenAI 自认技术债——"readability debt"概念互证）；本库 SEforLLM/13（人机代码可读性对比主题同批入库） |

注：论文未提供公开代码/数据集 artifact 链接（技术细节声明在 supplementary appendix）。

## 5. 一句话索引（给 Agent 用）

> 北大 Ye 等：在 2,735 个 WoC+LeetCode 场景 × 5 前沿 LLM 上成对比较代码可读性——LLM 代码总体与人类相当且略优（WoC win rate 51.30%–64.70%，Wilcoxon p<0.001 但 r 仅 0.104），但失败模式相反：人类"欠生产"（DC 60、IS 58、RC 仅 3），LLM"过生产"（EC 48、RC 24，另有 Unknown API/Redundant Variables/Overblanking 三个特有模式）；prompt 设计中 function signature（重要性 0.4011）、constraints、style description 关联最强（增量设置 p≤0.001，消融仅 signature 显著 p=0.003），但 RF R²<0.3 作用有界——是轻量杠杆而非完整解（2605.13280 v2，2026-08）。
