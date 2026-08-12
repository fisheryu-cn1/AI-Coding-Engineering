# 论文摘要：SWE-Explore（把仓库探索拆出来独立评估）

> **原论文标题**：SWE-Explore: Benchmarking How Coding Agents Explore Repositories
> **完整 PDF 文件名**：`09-Zhang-SWE_Explore.pdf`
> 作者 / 年份 / 出版：Shaoqiu Zhang, Yuhang Wang, Jialiang Liang, Yuling Shi, Wenhao Zeng, Maoquan Wang, Shilin He, Ningyuan Xu, Siyu Ye, Kai Cai, Xiaodong Gu；上海交通大学 / 新疆大学 / UIUC / CUHK；arXiv:2606.07297v1，2026-06-05
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 评估 Coding Agent 时，**把"仓库探索"从 end-to-end 修复中拆出来**作为独立评测目标（而不是只看 Pass/Fail）。
- 构造**轨迹监督的 line-level ground truth**：用成功解决同一 issue 的多个 Agent 轨迹交叉验证。
- 横向比较经典检索（BM25、TF-IDF、Potion/RAG）vs. 学术定位器（LocAgent、OrcaLoca、CoSIL、AutoCodeRover）vs. 通用 Agent（OpenHands、Mini-SWE-Agent、AweAgent、Claude Code、Codex）。
- 用"restricted-context validation"验证探索指标与下游修复的相关性。
- 需要**多语言、跨 203 仓库、848 个 issue**的仓库级代码任务评测集。

> 锚点：摘要；§1 Introduction；§2 Related Work；§3 Benchmark；§4 Experiments。

## 2. 主要观点与方案

### 2.1 核心论点

- SWE-bench 把任务当成二分类（解决/未解决），掩盖了失败到底发生在"探索"还是"合成补丁"。
- **SWE-Explore** = 仅给仓库 + issue，要求 explorer 在固定行预算内返回排序的代码区域（file path + [start, end]）。
- ground truth 来自"独立成功轨迹"交叉的 read actions，加 LLM 精化 + 人工审核。
- 从 coverage、ranking、context-efficiency 三个维度评估，且每个指标都和下游修复做相关性验证。

### 2.2 方法

- **任务**：`f: (q, R) ↦ P = (r1, ..., rK)`，K=5（平均每实例 4.7 个核心 region）。
- **数据**：SWE-bench Verified + SWE-bench-Pro + SWE-bench Multilingual 过滤后 848 实例 / 10 语言 / 203 仓库。
- **轨迹来源**：GPT-5.4 / Gemini-3-Pro / Sonnet-4.6 / GLM-5.1 / Kimi-K2.6 等强 LLM 跑成功的轨迹（|T| ≥ 2）。
- **Region 提取**：从 read actions（editor view / cat/head/tail/sed -n / grep -n）归一化到 (path, [s,e])。
- **Ground truth**：保守交集 Rint + 模型特有可选集 Ropt + LLM 精化 + 人工审核。
- **指标**：
  - Coverage/Accuracy：Precision、Recall@B、F1、HitFile、HitRegion。
  - Ranking：nDCG@B（按 line budget）、FUH（首次有用命中位置）。
  - Efficiency/Noise：Context Efficiency、NoiseRegion、NoiseFile。
- **Restricted-context validation**：把 explorer 的输出作为唯一可见上下文喂给固定 patcher，看下游 resolve rate 是否与探索分数相关。

> 锚点：§3 Benchmark；图 4（示例）；Table 1（与同类基准对比）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 基准规模 | 848 实例、10 语言、203 仓库 | §3.2 |
| 平均 ground-truth | 4.3 文件 / 4.7 region / 1,578 行 | Table 2 |
| 下游验证（Oracle 修复率） | 59.7% | Table 3 |
| 强相关指标 | Context Efficiency r=0.950；FUH r=0.928；Rec@100 r=0.926 | Table 4 |
| 强负相关 | NoiseRegion r=−0.812；NoiseFile r=−0.808 | Table 4 |
| 最佳 Agentic Explorer（K=5） | CoSIL HitReg 0.544 / Prec 0.581 / nDCG@500 0.824 | Table 6 |
| 最佳文件级定位 | AweAgent HitFile 0.682 / Claude Code 0.667 | Table 6 |
| 关键结论 | Agentic explorers 明显优于经典检索；文件级已强，但 line-level coverage 与高效 ranking 仍是分水岭 | §4 |

> 锚点：Table 3 / Table 4 / Table 6；§4.2。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2606.07297v1，2026-06-05 |
| 代码 | https://github.com/Qiushao-E/SWE-Explore-Bench |
| 数据 | https://huggingface.co/datasets/SWE-Explore-Bench/SWE-Explore-Bench |
| 配套阅读 | `03-RepoGraph仓库级代码图谱增强AI软件工程.md`（行级图谱 plug-in）、`07-LLM智能体看代码仓库.md`（视觉辅助）、`10-CodeNib多视图数据系统.md`（多视图上下文服务） |

> 锚点：References。

## 5. 一句话索引（给 Agent 用）

> 评估 Coding Agent 时**别只看 Pass/Fail**：SWE-Explore 用轨迹监督给出 **848 实例 / 10 语言 / 203 仓库的 line-level ground truth**，并验证 **Context Efficiency / FUH / Rec@100 与下游修复强相关**（r ≥ 0.92），可直接用来横向比较检索器、定位器与通用 Agent——也是代码图谱效果评估的天然靶子。
