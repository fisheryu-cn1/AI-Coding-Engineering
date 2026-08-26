---
title: "Trae Agent: An LLM-based Agent for Software Engineering with Test-time Scaling"
source_pdf: "31-TraeAgent-Test_Time_Scaling_v1.pdf"
arxiv_id: "2507.23370"
arxiv_version: "v1"
authors:
  - "Trae Research Team（字节跳动）"
  - "Pengfei Gao"
  - "Zhao Tian"
  - "Xiangxin Meng"
  - "Xinchen Wang"
  - "Ruida Hu"
  - "Yuanan Xiao"
  - "Yizhou Liu"
  - "Zhao Zhang"
  - "Junjie Chen"
  - "Cuiyun Gao"
  - "Yun Lin"
  - "Yingfei Xiong"
  - "Chao Peng"
year: 2025
venue: "arXiv（技术报告）"
type: "设计参考 + 内容索引"
generated_at: "2026-08-26"
summary_version: "1.0"
---

# 论文摘要：Trae Agent——测试时扩展的软件工程 LLM 代理（字节 Trae 团队）

## 1. 适用场景

- 当你需要**"同任务多轮独立采样再归并"（ensemble reasoning）的 SOTA 实现与证据**（采样-剪枝-归并三段式架构、消融数据、随 N 的扩展曲线）时，读这篇——首个 agent 化（非 prompting 化）的 ensemble 实现，SWE-bench Verified 排行第一。
- 当你要设计**候选方案的选择/剪枝机制**（等价判定、回归测试筛选、投票归并）并需要各组件的独立贡献数据时，读其 §3.3–3.4 与 §5.3–5.4。
- 当你评估"LLM 整体解决率稳定但解决集合跨执行漂移"这一现象的证据与量级时，读其 §2 Motivation。

> 锚点：Abstract; §1 Introduction; §2 Motivation; §3.2 Patch Generation; §3.3 Patch Pruning; §3.4 Patch Selection; §5.1–5.4 Results; §6.1–6.2 Discussion; Tables 1–5; Figures 1–2

## 2. 主要观点与方案

- **问题形式化**：仓库级 issue resolution 建模为**最优解搜索问题**——生成 N 个多样候选 patch，剪枝，选出一个共识解；两个核心挑战=大集成空间搜索难、prompting 式方法（Augment 的 LLM-as-judge、DeiBase 的置信度打分）无状态单轮、缺仓库级理解（§1; §3.1）。
- **动机实证**：N=10 时 Oracle 比 Average 平均高 20.80%（上限随 N 升）而 Adversary 低 27.01%（下限更崩）；Augment/DeiBase 随 N 先升后降（上下限发散+候选过多导致上下文稀释）；平均 40% 候选 patch 冗余或错误——剪枝的必要性由此立论（§2）。
- **三组件架构**（§3.2–3.4）：
  - **生成**：coder agent 七步工作流（分析 issue→探索定位→**复现 bug**→诊断→patch→重跑复现验证→总结如 commit message），工具=文件编辑/Bash/Sequential Thinking/Task Done（Docker 环境 function calling）；**高温采样 N 次独立运行**+Mixture 模式三 LLM（Gemini 2.5 Pro/Claude 3.7 Sonnet/GPT-4.1）轮换增多样性。
  - **分层剪枝**：①patch 去重——unidiff 解析+规范化（去空白/换行/注释）后判等价，语法错误即弃，平均去冗余 28.90%；②回归测试——tester agent 跑原库测试→LLM 筛"真回归子集"（防止把合理的行为变更误判）→逐 patch 执行淘汰；**全败时保守保留全集**；误杀率（FN）仅 3.69%（FP 33.04%——宁留错杀少的设计取向）。
  - **选择**：selector agent 模拟真实程序理解过程——静态（迭代读 issue 引用/被改/依赖代码）+动态（生成并执行单测看各 patch 行为），上限 30 轮工具交互；**majority voting**：selector 并行 N 次投票取多数，前 ⌈N/2⌉ 票一致即早退。
- **剪枝组件可移植**：外挂到 Augment +3.91%、DeiBase +4.72%（§5.1）。
- **ensemble space 与选择效果强相关**：剪枝使候选集平均缩 27.80%–39.15%，空间大小与 Pass@1 呈强负相关（Spearman |ρ|=0.80–1.00）（§5.4; Table 3; Fig.11）。
- **实战地位**：SWE-bench Verified 官方排行第一（Pass@1 **75.20%**，2025-07 时点快照）；开源仓库 8,000+ stars（§6.1; Fig.12）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| SWE-bench Verified 排行榜 | 第一名，Pass@1 75.20%（2025-07 快照） | §6.1; Fig.12 |
| RQ1 总效果（N=3） | 四设置 Pass@1：Gemini 62.27%/Sonnet 66.40%/GPT-4.1 59.00%/Mixture 65.67%，超四基线 5.01%–12.86%（Wilcoxon p<8.00×10⁻⁶） | Table 1 |
| 稳定性 | 三次重复 std 平均 0.19%（基线 0.38%–0.52%） | §5.1 |
| 随 N 扩展（RQ2） | N=1→10 持续上升，各 N 平均超基线 5.83%–14.60%；基线先升后降 | §5.2; Fig.10 |
| 消融（RQ3） | 去整个剪枝 −5.57%；走去重 −3.73%；去回归测试 −3.42%；selector 换 prompting −4.08%；去投票 −4.14%（全 p<7.32×10⁻³） | Table 2; §5.3 |
| 剪枝可移植 | Augment +3.91%、DeiBase +4.72% | §5.1 |
| 剪枝幅度 | ensemble space 平均缩 27.80%–39.15%；空间×效果强相关（Spearman 0.80–1.00） | Fig.11; Table 3 |
| 回归测试判定质量 | 20,000 判定：Accuracy 63.28%/Recall 93.40%/F1 73.95%；FN 率仅 3.69%、FP 率 33.04% | Table 4; §6.2 |
| 实例级影响 | 回归测试使 all-correct 实例 +12.00%、all-incorrect +4.45% | Table 5; §6.2 |
| 动机量级 | N=10：Oracle 较 Average +20.80%、Adversary −27.01%；40% 候选冗余/错误 | §2 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2507.23370 |
| 开源仓库 | github.com/bytedance/trae-agent（8,000+ stars，2025-07） |
| 对比基线 | Augment（LLM-as-judge 式 ensemble）、DeiBase（置信度打分式 ensemble） |
| 产品侧对应 | Trae IDE 的 SOLO 模式（Builder/Coder 双 agent）；本论文为其开源研究线 |
| 关联库内 | AgentParadigms/21（SWE-bench Illusion——记忆污染视角）、20（METR 长任务时程）；ContextEngineering/45（agent 对文档指令的忠实性——ensemble 的多样性前提） |

## 5. 一句话索引（给 Agent 用）

> 字节 Trae 团队：首个 agent 化 ensemble reasoning——coder agent 高温 N 次独立采样（Mixture 轮换三 LLM）→分层剪枝（unidiff 规范化去重去冗余 28.90%+回归测试淘汰，误杀率仅 3.69%）→selector agent 类人程序理解（静态+动态各 30 轮上限）并行多数票归并；SWE-bench Verified 75.20% 第一、超 prompting 式基线 5.83%–14.60%、N=1→10 持续提升而基线退化，剪枝组件可移植（+3.91%/+4.72%）——"重复采样再归并"路线的产品级 SOTA 证据（2507.23370，2025-07）。
