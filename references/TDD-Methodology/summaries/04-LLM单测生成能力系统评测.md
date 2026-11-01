---
title: "On the Evaluation of Large Language Models in Unit Test Generation"
source_pdf: "04-Yang-Evaluation_LLM_Unit_Test_Gen_v2.pdf"
arxiv_id: "2406.18181"
arxiv_version: "v2"
authors:
  - "Lin Yang"
  - "Chen Yang"
  - "Shutao Gao"
  - "Weijing Wang"
  - "Bo Wang"
  - "Qihao Zhu"
  - "Xiao Chu"
  - "Jianyi Zhou"
  - "Guangtai Liang"
  - "Qianxiang Wang"
  - "Junjie Chen"
year: 2024
venue: "ASE 2024"
type: "评测对照 + 内容索引"
generated_at: "2026-11-01"
summary_version: "1.0"
---

# 论文摘要：LLM 单测生成能力的系统评测（ASE 2024）

## 1. 适用场景

- 当你打算在生产中用**开源代码 LLM**（CodeLlama / Phind-CodeLlama / DeepSeek-Coder 系，7B–34B）生成 Java 单元测试并需要选型依据时，读这篇：它是首个覆盖 5 款开源 LLM × 多种 prompt 设置的系统实证，并给出与 GPT-4、Evosuite 的同基准硬数字。
- 当你在设计单测生成的 prompt（描述风格用自然语言还是代码注释、焦点类其他方法/构造器/字段等代码特征放不放），或纠结要不要上思维链（Chain-of-Thought, CoT）、检索增强生成（Retrieval-Augmented Generation, RAG）时，读这篇：§3.1 与 §3.3 的消融与显著性检验直接给出哪些设置涨点、哪些掉点。
- 当你需要引用"LLM 单测生成 vs 传统 Evosuite / GPT-4"的编译成功率（Compilation Success Rate, CSR）、行覆盖（Line Coverage）、分支覆盖（Branch Coverage）、缺陷检出数（Number of Detected Defects, NDD）作为对照基线时，读这篇：§3.2 表 4 与 §3.4 表 6 是现成的基准数字。
- 当你要为 LLM 生成测试做**后处理修复**（三类幻觉编译错误）或**输入变异策略**（补缺陷触发输入）时，读这篇：§3.2 的错误类型占比与 §3.4 的未检出归因（PIE 理论三分法）提供了直接的问题定位。

> 锚点：prompt 设计消融（§3.1）/ 开源 LLM vs GPT-4 vs Evosuite（§3.2 表 4）/ CoT·RAG（§3.3 表 5）/ 缺陷检测与归因（§3.4 表 6–7）/ 实践建议（§5）；基准 Defects4J 2.0，17 项目、778 focal methods、413 缺陷。

## 2. 主要观点与方案

**研究问题（§2.1）**：论文围绕四个 RQ 展开——RQ1 prompt 设计（描述风格 + 代码特征）如何影响单测生成效果；RQ2 开源 LLM 相对 GPT-4 与 Evosuite 表现如何；RQ3 上下文学习（In-Context Learning, ICL）方法（CoT、RAG）是否有效；RQ4 生成的单测缺陷检测能力如何。论文指出已有研究集中于闭源 LLM（ChatGPT/CodeX）+ 固定 prompt 策略，开源 LLM 与多样 prompt 因素的作用是空白（§1）。

**评测框架（§2）**：
- 模型（§2.2）：从 Hugging Face 代码 LLM 榜单出发，选定 5 款开源模型——CodeLlama-7B-Instruct（CL-7B）、CodeLlama-13B-Instruct（CL-13B）、Phind-CodeLlama-34B-v2（PD-34B）、DeepSeekCoder-6.7B-Instruct（DC-7B）、DeepSeekCoder-33B-Instruct（DC-33B）；另以 GPT-4 为闭源参照，Evosuite 为传统技术参照。
- Prompt 设计（§2.3）：两个维度——描述风格（自然语言 NL vs 代码语言 CL 注释）× 六个代码特征（焦点方法体 FMb、焦点方法参数 FMp、焦点类构造器 FCc、焦点类字段 FCf、焦点类其他方法 FCm、相关类构造器 RCc）；以 FMb 为基础做逐特征去除的消融实验。
- ICL 方法（§2.4）：CoT（先描述焦点方法再生成测试）与 RAG（用 CodeBERT 编码、按余弦相似度检索项目内最相似方法及其测试作为示例）。
- 基准与实现（§2.5–2.6）：Defects4J 2.0 的 17 个 Java 项目，取 778 个 focal methods（涉及 413 个缺陷）；tree-sitter 抽取生成测试，JaCoCo 收集覆盖；VLLM 加速，实验耗费约 3,000 NVIDIA A100 GPU 小时；temperature 设为 0。
- 度量（§2.7）：CSR、CovL、CovB，RQ4 加 NDD；统计检验用 Wilcoxon 秩和检验（p<0.05）+ rank-biserial 效应量（>0.3 视为有意义差异）。

**主要发现（§3，共 9 条 Finding）**：
- RQ1（§3.1）：描述风格应与模型训练数据对齐——CL-7B/CL-13B 用 NL 显著更好（六个指标全部显著），PD-34B/DC-7B/DC-33B 对风格稳健（Finding 1）；FCm 对语法有效性贡献最大（去掉后 CSR 显著降 2.14%–14.92%），但其长文本挤占生成空间，去掉后平均生成测试数从 3,654 升至 5,434、覆盖率反升（Finding 2）；代码特征的影响因基座模型代码理解能力而异，为给定 LLM 选对特征可大幅提升效果（Finding 3）。
- RQ2（§3.2）：其他任务上的模型排序不能迁移到单测生成（PD-34B 与 DC-33B 的相对优劣在两任务上相反），GPT-4 仍最强（Finding 4）；但所有 LLM（含 GPT-4）三项指标全面落后 Evosuite，根因是 34.44%–61.78% 的生成测试语法无效，源于幻觉引出的三类编译错误：未解析符号 30.68%、参数不匹配 17.25%、抽象类实例化 10.38%（Finding 5）。
- RQ3（§3.3）：CoT 对代码理解强的 DeepSeek-Coder 两款有增益（DC-7B 行覆盖 +2.72%）、对 CodeLlama 三款反而有害（CL-13B −6.45%）（Finding 6）；RAG 全线负收益（如 PD-34B 行覆盖 −9.28%），因检索到的测试（平均 12.10 行、每方法 2.41 个）与 LLM 擅长生成的测试（5.60 行、6.94 个）差距过大（Finding 7）。
- RQ4（§3.4）：缺陷检测能力弱——平均 87.13% 的缺陷没有任何可编译的有效测试；在可测缺陷中也仅检出 29.27%–60.00%（平均 47.28%）（Finding 8）。对未检出缺陷按 PIE 理论人工标注（Cohen's Kappa = 0.95）：主因是缺少触发缺陷的特定输入（占未检出缺陷平均 74.99%），其次覆盖不足，断言不当占比最小（每模型 0–2 个缺陷）（§3.4 表 7，Finding 9）。

**局限归因（§4 Threats to Validity）**：消融仅逐个去除特征、未穷举组合，各 LLM 用的是局部最优而非全局最优 prompt 设置；CoT/RAG 的适配方式合理但未必最优；Defects4J 存在潜在数据泄漏（经比对无完全匹配、测试数量差异大，威胁有所缓解）；温度设 0 控制随机性。

**实践建议（§5 Implications，共 7 条）**：为给定 LLM 预实验调优 prompt；用静态分析剔除与焦点方法无依赖的方法以平衡信息量与生成空间；经验性选模型而非照搬其他任务的榜单；针对单测任务定制 ICL（建高质量检索库）；设计后处理规则/错误回喂修复无效测试；对生成测试的输入做变异（边界值、历史缺陷触发值）提升检出；用单测生成数据做监督微调（SFT）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| GPT-4 CSR / 行覆盖 / 分支覆盖 | 52.96% / 40.43% / 31.78% | §3.2 表 4 |
| 最佳开源 PD-34B CSR / 行覆盖 / 分支覆盖 | 49.07% / 37.45% / 32.35% | §3.2 表 4 |
| 其余开源模型 CSR（CL-7B / CL-13B / DC-7B / DC-33B） | 38.17% / 38.94% / 49.22% / 45.65% | §3.2 表 4 |
| Evosuite CSR / 行覆盖 / 分支覆盖 | 85.71% / 78.91% / 76.59% | §3.2 表 4 |
| LLM 生成测试语法无效比例区间 | 34.44%–61.78% | §3.2 |
| 三类幻觉编译错误占比（未解析符号 / 参数不匹配 / 抽象实例化） | 30.68% / 17.25% / 10.38% | §3.2 |
| 去掉 FCm 后 CSR 显著降幅区间 | 2.14%–14.92%（全部显著） | §3.1 表 2 |
| 去掉 FCm 后平均生成测试数变化 | 3,654 → 5,434（覆盖反升，如 CL-7B 行覆盖 +9.26%） | §3.1 表 3 |
| CoT 对行覆盖的影响 | DC-7B +2.72%、DC-33B +0.69%；CL-7B −3.04%、CL-13B −6.45%、PD-34B −0.02% | §3.3 表 5 |
| RAG 对行覆盖的影响 | 五款开源模型全线下降，降幅 3.34%–9.28%（PD-34B −9.28%） | §3.3 表 5 |
| 缺陷检出数 NDD / 可测缺陷数 NTD（CL-7B / CL-13B / PD-34B / DC-7B / DC-33B / GPT-4） | 12/41、15/28、30/63、24/60、33/62、39/65 | §3.4 表 6 |
| 缺陷检出率区间与均值 | 29.27%–60.00%，平均 47.28% | §3.4 |
| 无任何有效（可编译）测试的缺陷比例（均值） | 87.13% | §3.4 |
| 未检出缺陷中"缺特定触发输入"占比（均值） | 74.99% | §3.4 Finding 9 |

注：模型规模为 5 款开源 LLM（7B–34B）+ GPT-4（参照）+ Evosuite（默认设置）；数据集为 Defects4J 2.0 的 17 个 Java 项目、778 个 focal methods、413 个缺陷；实验耗费约 3,000 A100 GPU 小时。论文报告了显著性：Wilcoxon 秩和检验 p<0.05 且 rank-biserial 效应量 >0.3 才判定为显著差异（表 1–3、表 5 中加粗处）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | https://arxiv.org/abs/2406.18181 |
| 论文（ACM 正式版） | https://doi.org/10.1145/3691620.3695529 |
| 代码与数据（项目主页） | https://github.com/LeonYang95/LLM4UT （论文 §2.6 "All of our code and data are available at our project homepage"，参考文献 [5]） |
| 基准数据集 | Defects4J 2.0：835 个真实缺陷、17 个开源 Java 项目；本文取 778 个 focal methods / 413 个缺陷（§2.5） |
| 被评测模型 | CodeLlama-7B/13B-Instruct、Phind-CodeLlama-34B-v2、DeepSeekCoder-6.7B/33B-Instruct（Hugging Face 公开权重）；GPT-4（OpenAI API） |
| 对比传统工具 | Evosuite（默认设置，§3.2）；覆盖率收集工具 JaCoCo；测试抽取 tree-sitter（§2.6） |
| 逐项目 focal methods / 缺陷数量明细 | 论文因篇幅放在项目主页（§2.5，未在正文给出） |

## 5. 一句话索引（给 Agent 用）

> ASE 2024 首个针对开源 LLM 单测生成的系统实证：在 Defects4J 2.0（17 个 Java 项目、778 个焦点方法、413 个缺陷）上评测 5 款开源代码 LLM（7B–34B），对照 GPT-4 与 Evosuite。结论：prompt 设计（描述风格对齐训练数据、精选代码特征）影响巨大；所有 LLM 覆盖率全面落后 Evosuite（GPT-4 行覆盖 40.43% vs Evosuite 78.91%），主因 34.44%–61.78% 生成测试因幻觉语法无效；直接套用 CoT/RAG 不升反降（RAG 五模型全线下降）；缺陷检测弱——平均 87.13% 缺陷无可编译测试，可测缺陷仅检出 47.28%（区间 29.27%–60.00%），主因缺触发缺陷的特定输入（占未检出 74.99%）。
