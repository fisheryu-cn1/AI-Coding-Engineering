---
title: "GAIA: A Benchmark for General AI Assistants"
source_pdf: "25-Mialon-GAIA_v1.pdf"
arxiv_id: "2311.12983"
arxiv_version: "v1"
authors:
  - "Grégoire Mialon"
  - "Clémentine Fourrier"
  - "Craig Swift"
  - "Thomas Wolf"
  - "Yann LeCun"
  - "Thomas Scialom"
year: 2023
venue: "ICLR 2024"
type: "评测对照 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：GAIA——通用助手能力基准（人类容易 ≠ 机器容易）

## 1. 适用场景

- 评估通用 AI 助手（组合推理 + 多模态 + 网页浏览 + 工具使用协同）或为自研 Agent 挑选基准、设计对照基线（人类 / 搜索引擎 / GPT-4±插件 / AutoGPT）时读这篇。
- 设计"对人类简单、对 AI 难"且防数据污染、答案可自动判分的任务构造方法（反向于 MMLU 式"对人类越来越难"的潮流）时。
- 需要量化证据论证"工具链/harness 完备性应与模型选择同级"、或论证静态基准必须动态演进时。

> 锚点：§1 Introduction; §3.1 A convenient yet challenging benchmark; §3.4 Building and extending GAIA; §4 LLMs results on GAIA; §5 Discussion。

## 2. 主要观点与方案

### 2.1 研究问题（§1 Introduction）

LLM 在"对人类难"的基准上逼近饱和（GPT-4 于 MMLU 86.4% vs 非专家人类 34.5%、专家估计 89.8%，§1 脚注1），但通用助手所需的真实世界能力缺乏合适度量。作者反向立论：概念简单、需准确执行长动作序列的任务更能刻画 AGI 进展（类比 Proof of Work：难解、易验），并置于 t-AGI 与 Morris et al. 的 AGI 分级框架（§1）。

### 2.2 基准设计四原则（§3.1）

1. **概念简单但真实**：多步推理、多模态、多样工具，反潮流不以"难倒人类"为目标；
2. **可解释**：少量高质问题、推理轨迹可核验（人类 92% 成功即任务简单）；
3. **抗记忆/不可博弈**：答案设计上不在预训练语料明文出现、非选择题、轨迹可查，污染可检测且可换题；
4. **易用**：答案为简短、唯一的事实型答案，零样本作答，评测不敏感于 prompt 设置。

### 2.3 评测协议（§3.2）

- 每题唯一正确答案，归一化后"准精确匹配"自动判分；系统 prompt 约定 FINAL ANSWER 输出模板（数值不带单位/逗号、字符串不带冠词缩写，Figure 2）；评分函数随 leaderboard 发布。

### 2.4 组成（§3.3; Appendix C）

- 466 题分三级：L1（≤1 工具、≤5 步，146 题）、L2（约 5–10 步、多工具组合，245 题）、L3（任意长动作序列，75 题），定义被模型成绩单调递减所验证（§4）。
- 能力覆盖（按标注者作答统计，Figure 3 左）：网页浏览 355 / 编码 154 / 多模态 138 / 多文件读取 129 / 无需工具 32；附件以 xlsx(29)、png(18)、pdf(15)、txt(13) 为主（Figure 6）；作答耗时与步数正相关、与工具数不相关（Figures 7–8）。

### 2.5 构建与验证流程（§3.4; Appendix D）

- 人类出题（作者 + Surge AI 付费标注者）：须基于可持久信源（Wikipedia、arXiv 等，L2/L3 组合多信源），答案不得以明文存在于互联网、随时间不变、唯一且"有趣"；附 robots.txt 合规检查（Appendix D 指令清单）。
- 双重独立验证：623 道新题各由 2 名新标注者独立作答，55% 双同意、27% 一致一错、18% 双不同意，整体 68% 直接有效（L1 75% / L2 68% / L3 47%，Table 3）；每题含验证约 2 小时。
- 应对网页证据漂移：题面钉死证据版本/日期；发布 166 题标注开发集 + 300 题留答案做 leaderboard（§1）。

### 2.6 实验设置与主要发现（§4）

- 设置：GPT-4（±插件；插件无 API、人工按题挑选，故为"oracle"估计）、GPT-4 Turbo、AutoGPT（GPT-4 后端）、搜索引擎、人类共 6 条基线；有 API 者跑 3 次取均值（§4; Table 4）。
- 发现 1（工具增强有效）：GPT-4+插件 L1 30.3% vs 裸 GPT-4 9.1%，且呈现回溯、查询精炼、长计划执行等行为（§4; Figures 9–10）。
- 发现 2（自动编排反而更差）：AutoGPT L2 仅 0.4%（低于裸 GPT-4 的 2.6%），且慢（7.6–11.7 分钟）；人 + GPT-4+插件的分数/时间比最佳（§4; Table 4）。
- 发现 3（裸模型靠记忆）：GPT-4 无法处理文件与多模态，其"网浏题"得分主要来自正确记忆中间信息；谜题类 L1 题常失败（§4; Figure 5; Figure 11）。
- 发现 4（搜索引擎非充分基线）：搜索在 L1 部分可得答案（7.4%），L2/L3 失效——LLM 助手有取代搜索引擎的潜力（§4）。

### 2.7 讨论、局限与未来工作（§5; §6）

- 闭源助手复现性差（API 行为随时间漂移、插件不可经 API 访问）；GAIA 仅评最终答案故对随机性鲁棒（§5）。
- "静态基准是制造中的坏基准"：拟逐年移除失效题、增补新题以维持效度（§5）。
- GAIA 要求全自动化（答案零近似），区别于部分自动化；全自动化的社会经济收益归属是支持开源的论据（§5）。
- 局限：不评推理轨迹与工具调用日志（OpenAI API 未提供）、无歧义题标注成本高（每题约 2 小时）、仅标准英语（全球 80% 人口非英语母语，约半数网页非英文）（§6）。未来：多语言扩展、人/模型轨迹评测、纳入带日志的开源模型（§5; §6）。

> 锚点：Abstract; §1 Introduction; §2 Related work; §3.1–§3.4; §4 LLMs results on GAIA; Figure 4; Figure 5; §5 Discussion; §6 Limitations; Appendix B Datacard; Appendix C; Appendix D Table 3; Table 4。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 人类成功率 | 总体 92%（L1 93.9 / L2 91.8 / L3 87.3） | Abstract; §3.4; Table 4 |
| GPT-4 + 插件 | 总体 ≈15%（L1 30.3 / L2 9.7 / L3 0） | Abstract; Table 4 |
| GPT-4（无工具） | L1 9.1±2.5 / L2 2.6±0.6 / L3 0 | Table 4 |
| GPT-4 Turbo | L1 13.0±2.1 / L2 5.5±1.4 / L3 0 | Table 4 |
| AutoGPT（GPT-4 后端） | L1 14.4 / L2 0.4 / L3 0；耗时 7.6–11.7 分钟 | Table 4 |
| 搜索引擎基线 | L1 7.4 / L2 0 / L3 0；耗时 7.4 分钟 | Table 4 |
| 人类作答耗时 | L1 6.8 / L2 10.5 / L3 17.7 分钟 | §1; Table 4 |
| 题目一次通过率 | 68%（623 题双人独立验证） | §3.4; Table 3 |
| 能力覆盖（题数） | 网页浏览 355 / 编码 154 / 多模态 138 / 文件读取 129 / 无工具 32 | §3.3; Figure 3 |
| 规模与发布 | 466 题 = L1 146 + L2 245 + L3 75；166 开发集 + 300 leaderboard | Abstract; §1; Table 4 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2311.12983 |
| 基准与代码 | https://huggingface.co/gaia-benchmark |
| Leaderboard | https://huggingface.co/spaces/gaia-benchmark/leaderboard |
| 对照系统 | AutoGPT（git hash ed172de…，§4 脚注7）；GPT-4 及其插件生态 |
| 对比基准 | MMLU / GSM8K（§1）；ToolQA、Gentopia、Gorilla APIBench、API-Bank、AgentBench、OpenAGI（§2） |
| 关联 | 本目录 26（OSWorld：GUI 侧能力短板，与 GAIA 的 L3 全零互证） |

## 5. 一句话索引（给 Agent 用）

> 评估通用 AI 助手时读这篇：GAIA 的 466 道真实世界问题（L1 146 / L2 245 / L3 75）对人类简单——92% 成功、每题 6.8–17.7 分钟——但对带插件的 GPT-4 仅约 15%（L1 30.3 / L2 9.7 / L3 0），AutoGPT 自动编排更差（L2 0.4%）；解题需网页浏览（355 题）、编码、多模态与文件读取协同，答案唯一可自动判分且抗污染；结论：通用助手瓶颈在工具链与多步执行而非知识量，静态基准须动态演进。
