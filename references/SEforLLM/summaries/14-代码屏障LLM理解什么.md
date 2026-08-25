---
title: "The Code Barrier: What LLMs Actually Understand?"
source_pdf: "14-Nikiema-Code_Barrier_v1.pdf"
arxiv_id: "2504.10557"
arxiv_version: "v1"
authors:
  - "Serge Lionel Nikiema"
  - "Jordan Samhi"
  - "Abdoul Kader Kaboré"
  - "Jacques Klein"
  - "Tegawendé F. Bissyandé"
year: 2025
venue: "arXiv"
type: "内容索引"
generated_at: "2026-08-25"
summary_version: "1.0"
---

# 论文摘要：The Code Barrier——LLM 对混淆代码到底理解什么（卢森堡大学 SnT）

## 1. 适用场景

- 当你需要**"LLM 是真语义理解还是表层模式匹配"的受控实验证据**（如设计对抗性代码评测、论证模型对标识符命名的依赖、评估 LLM 分析非规范代码的可靠性）时，读这篇——它用三类渐进混淆（lexical/structural/semantic）量化了理解退化的具体来源。
- 当你要为**逆向工程 / 恶意代码分析场景选型或评估 LLM 反混淆（deobfuscation）能力**、判断"功能测试通过 ≠ 语义恢复"这一陷阱时，读其 §4.3。
- 当你要**构建"分离记忆与理解"的代码理解 benchmark** 时，可复用其 Obscura 数据集构造法：去语境化描述归一化（双 LLM 评委 + 0.5 阈值）+ 编译-执行-输入输出比对的反混淆验证流水线（§3.2; §3.4）。
- 当你要为**面向 AI 协作的代码规范排优先级**（有意义的命名 vs 清理死代码 vs 注释语言统一）时，读其 §4.1–4.2 的量化对比。

> 锚点：Abstract; §1 Introduction; §2.3 Code Obfuscation Techniques; §3 Methodology; §4 Experimental Results; §5 Discussion

## 2. 主要观点与方案

- **评测设计**：把代码混淆当作"结构化测试框架"——混淆在保功能的同时故意破坏可读性，迫使模型超出表层模式恢复语义。三类混淆对应三个维度：变量重命名（lexical）、死代码注入（structural）、整型/字符串字面量加密（semantic）；用两个互补任务度量理解：❶ 生成混淆代码的准确描述，❷ 反混淆（§1; §2.3; §3.1）。
- **Obscura 数据集**：基于 CodeNet 的 Java250（250 题、>75,000 个实现、平均每题约 300 个实现），每题保留按 cyclomatic complexity 选出的最复杂实现 s⁺ 与最简单实现 s⁻，外加去注释版本 s；用 GPT-4o 把叙事式题面 d 归一化为去语境描述 d′（250 条全部人工校验，27 条不精确者手工重写；双评委相似度 0.9–1），再用开源工具 Obfuscator 生成 s⁺_ren / s⁺_dead / s⁺_enc 三个混淆变体（§3.2.1–3.2.3; Table 1）。
- **被测模型**：13 个 LLM，分三类——通用（GPT-4o、GPT-3.5-turbo、DeepSeek-R1-Distill-Qwen-7B、Mistral-7B、gemma-2-9b、Llama-3.1-8B、Qwen2.5-7B）、代码微调（CodeLlama-7b、CodeGemma-7b）、代码专构（Mamba-Codestral-7B、DeepSeek-Coder-V2-Lite、StarChat2-15b、StarCoder2-15b-instruct）（§3.3; Table 2）。
- **评判机制**：描述任务用双 LLM 评委（GPT-4o + Claude Sonnet 3.7 / DeepSeek-reason）打 0–1 相似度，任一低于 0.5 判为不准确；反混淆任务走编译→执行→与 ground-truth 输入输出比对；统计检验用 Mann-Whitney-Wilcoxon（§3.4; §3.5）。
- **Finding 1（基线反转）**：非混淆代码上，通用模型（尤其 GPT-4o、DeepSeek-R1）描述准确率反超代码专用模型，挑战"领域微调必然更强"的假设；注释有无的效果经 MWW 检验不显著（这些注释较短、非 Javadoc 风格）（§4.1.1）。
- **Finding 2（注释语言）**：注释语言效应因模型而异——GPT-4/GPT-3.5/Mistral/QwenCoder 用日文原文更好，DeepSeek-R1/Llama/CodeGemma/StarChat 用英译更好；日文注释密度显著更高（中位 10% vs 5%），翻译后的更全面注释可能才是提升主因（§4.1.2）。
- **Finding 3（混淆敏感性分层）**：变量重命名伤害最大（平均 −18.6 pp）、字面量加密次之（−21.4%）、死代码注入最小（−6.2%）——LLM 主要依赖标识符词法语义与字面量可读性，而非结构理解；死代码基本能被过滤（§4.2.1; Fig 6）。
- **Finding 4（高信息密度盲区）**：全体模型一致失败的 13 个样本呈现"复杂度高、token 少"特征——把复杂逻辑压缩进紧凑实现（"more with less"）的代码是当前架构的特定盲区（§4.2.2; Fig 7）。
- **Finding 5（失败模式分化）**：失败时顶级模型（GPT-4o、GPT-3.5、Codestral）从不产出编程领域之外的内容（误解而非幻觉），而专为代码设计的 StarChat 领域无关输出错误率最高（55–78%），属灾难性上下文丢失（§4.2.3; Fig 8）。
- **Finding 6/7（任务反转 + 语义残留）**：反混淆任务上代码专用模型普遍反超通用模型（GPT 家族除外）——描述与反混淆动用理解的不同侧面；且通过功能测试的反混淆代码常仍是"部分混淆"状态：变量重命名最可逆（平均 22.7% 语义恢复成功）、死代码 16.3%、字符串/整型加密最难 12.7%（§4.3.1–4.3.2; Fig 9–10）。
- **解释模型与实践含义**：作者提出 LLM 以"表层模式识别 + 结构分析 + 语义整合尝试"的分层方式处理代码；实践上有意义命名比清理死代码更能提升 LLM 可处理性、高度优化/紧凑代码库上 LLM 辅助更不可靠、安全场景的反混淆辅助必须有人工监督（§5.1–5.2）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| 基线描述准确率（非混淆，最强模型） | GPT-4o 约 87%（有注释）/ 约 84%（无注释），差异不显著（MWW） | §4.1.1; Fig 3 |
| 注释对描述的影响 | 8/13 模型有注释更好，平均 +3.7%，DeepSeek-R1 最高 +11.5%；Mistral/CodeLlama/Codestral/StarChat 无注释反而 +2.9/+5.0/+2.9/+2.2 pp | §4.1.1 |
| 日文注释译为英文 | 6 个模型提升，DeepSeek-R1 +37.5%；注释密度：日文（译后）最高达总行数 25% vs 英文约 7–8%，中位 10% vs 5% | §4.1.2; Fig 4–5 |
| 变量重命名 → 描述准确率 | 平均 −18.6 个百分点（部分模型降幅 >30 pp）；GPT-4o 最鲁棒仅 −7.3% | §4.2.1; Fig 6 |
| 死代码注入 → 描述准确率 | 平均仅 −6.2%（QwenCoder/Mistral/GPT-4o 几乎不受影响） | §4.2.1 |
| 字面量加密 → 描述准确率 | 平均 −21.4%；GPT-4o 降 19.9% 但仍最高（加密代码上 58.8%） | §4.2.1 |
| 全模型一致失败样本（13 个） | 圈复杂度均值 38.7 vs 全集 32.5；token 均值 405.5 vs 664.0（MWW p=0.007，token 差异显著、复杂度不显著）；token 标准差 171.4 vs 336.5 | §4.2.2; Fig 7 |
| 领域无关描述错误率 | StarChat 最高 55–78%；GPT-4o/GPT-3.5/Codestral 为 0（从不产出非代码内容） | §4.2.3（Finding 5） |
| 反混淆：编译率 vs 功能正确率差距 | 死代码混淆下多个模型编译 60–70% 但测试通过仅 40–50% | §4.3.1; Fig 9 |
| 反混淆：变量重命名（最易） | 最佳模型编译率 >60%、测试通过率达 90% | §4.3.1 |
| 语义恢复成功率（通过功能测试后的描述相似度验证） | 变量重命名 22.7% / 死代码移除 16.3% / 字面量加密 12.7%（平均） | §4.3.2; Fig 10 |
| 评测规模 | 13 个 LLM；Obscura 250 题（源自 CodeNet Java250，>75,000 实现、平均约 300/题）；描述相似度校验 250 对（0.9–1）；含注释子集 139/250（其中英文注释 101 题） | §3.2.1–3.2.2; §3.3; §3.4.1; §4.1.1 |

注：Fig 3/4/6/8/9/10 为图形化数据，正文未给出逐模型精确值，上表仅收录正文明确陈述的数值；§4.2.2 的两组中位数在 PDF 提取文本中与"更高/更少"的叙述自相矛盾，未收录。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2504.10557（v1，2025-04-14，cs.SE） |
| 数据集基底 | IBM Project CodeNet（Java250 子集：250 题、55 语言、14M+ 样本；arXiv:2105.12655） |
| 混淆工具 | Obfuscator（superblaubeere27，开源 Java 混淆器）：https://github.com/superblaubeere27/obfuscator |
| 被测模型（Table 2） | GPT-4o、GPT-3.5-turbo、DeepSeek-R1-Distill-Qwen-7B、Mistral-7B-Instruct-v0.2、gemma-2-9b-it、Llama-3.1-8B、Qwen2.5-7B-Instruct、CodeLlama-7b、codegemma-7b-it、Mamba-Codestral-7B-v0.1、DeepSeek-Coder-V2-Lite-Instruct、starchat2-15b-v0.1、starcoder2-15b-instruct-v0.1 |
| 人类理解基线（引文） | Feitelson & Mizrahi 2020（有意义命名可提升人类理解达 30%，§2.3.1） |
| 关联论文（本库） | SEforLLM/13（Le et al.，机器与人类对混淆代码的理解）：同属受控混淆测量族——本篇建立"混淆即评测"范式与 LLM 侧基线，13 号引入人类对照并按混淆层级细分；两文结论互证（均发现重命名/词法层敏感） |

## 5. 一句话索引（给 Agent 用）

> 卢森堡大学 SnT：把代码混淆用作 LLM 语义理解的受控测试框架——自建 Obscura（CodeNet Java250 的 250 题 × 变量重命名/死代码/字面量加密三类混淆），在 13 个 LLM 上测描述与反混淆：重命名使描述准确率平均降 18.6 pp、字面量加密降 21.4%、死代码仅 6.2%，GPT-4o 最鲁棒（加密下仍 58.8%）；描述任务上通用模型反超代码专用模型，反混淆任务则相反（GPT 家族除外）；通过功能测试的反混淆代码平均仅 12.7–22.7% 真正恢复语义，结论是当前 LLM 主要依赖词法表层而非深层结构理解（arXiv 2504.10557 v1，2025-04）。
