# 论文摘要：SeeRepo（让 LLM 智能体"看见"代码仓库）

> **原论文标题**：LLM Agents Can See Code Repositories
> **完整 PDF 文件名**：`07-Ma-LLM_Agents_See_Code_Repositories.pdf`
> 作者 / 年份 / 出版：Dongjian Ma, Silin Chen, Yufei Yang, Yuling Shi, Yanfu Yan, Xiaodong Gu；上海交通大学 / 西安交通大学 / 浙江大学；arXiv:2606.14061v3，2026-06-19
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 为多模态 LLM（MLLM）Coding Agent 设计**视觉模态辅助**时，评估"用图像代替/补充文本"对效果和成本的影响。
- 决定**仓库图谱的呈现方式**（仅文本 vs. 仅图像 vs. 文本+图像；嵌套 / 表格 / 图布局；固定 vs. 动态深度）。
- 在 **SWE-bench Verified**、SWE-Rebench 2026.03、SWE-QA 上做 multimodal coding agent 评估。
- **降低 Agent 的 token 成本**同时保持准确率：例如 GPT-5-mini 上节省 25% 输入 token、26% 成本。
- 决定**视觉工具该在哪个阶段调用**（探索 / 定位 / 修复 / 验证）。

> 锚点：摘要；§1 Introduction；§3 Experimental Setup；§4 Results。

## 2. 主要观点与方案

### 2.1 核心论点

- **纯视觉替代文本会显著恶化效果**：vision-only 模式下所有模型精度下降（最大 −34.1），token 成本反而上升。
- **视觉作为补充模态有效**：text + vision 混合界面可在保持/提升准确率的同时省 26% token 成本。
- **结构导向渲染（Graph layout）效率最高**；动态深度优于固定深度。
- **在 fault localization 阶段调用视觉最有效**；在 repair / validation 阶段调用会引入噪声。

### 2.2 方法

- **数据/工具**：Mini-SWE-Agent + SeeRepo 扩展工具；仓库图（contains / imports / inherits / invokes 四类关系）；Graphviz 渲染为 PNG。
- **模型**：GPT-5-mini、GPT-5.1、Doubao-Seed-2.0-Lite、Kimi K2.5。
- **基准**：SWE-bench Verified（500 实例）、SWE-Rebench 2026.03（110 实例，41 仓库）、SWE-QA。
- **指标**：Pass@1、Overall Score、API Calls、Input Tokens、Output Tokens、Average Cost。
- **四种研究问题**：
  - RQ1：vision-only 效果如何？→ 全部下降。
  - RQ2：text + vision 混合能否兼顾效果与成本？→ 是。
  - RQ3：哪种视觉布局最好？→ Graph 布局。
  - RQ4：在哪一阶段调用视觉？→ 定位阶段。

> 锚点：§2 Background；§3 Experimental Setup；§4 Results；图 1 / 图 2 / Table 1。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| vision-only 精度下降 | GPT-5-mini 55.0% → 41.4%（−13.6）；Doubao 51.0% → 16.9%（−34.1）；Kimi K2.5 70.3% → 55.0%（−15.3） | Table 1 |
| vision-only 成本 | GPT-5-mini +42%；Doubao +268%；Kimi K2.5 +27% | Table 1 |
| 混合模式（GPT-5-mini） | Pass@1 55.4%（+0.4）；输入 token −25%；成本 −26% | §4 |
| 混合模式（GPT-5.1） | 成本 −46%；准确率微降（−2.2） | §4 |
| 混合模式（Kimi K2.5） | Pass@1 68.8% → 70.6%（+1.8）；成本 −3% | §4 |
| 最佳视觉布局 | Graph layout：输入 token −25% / 成本 −26% / Pass@1 55.4%（+0.4） | §4 RQ3 |
| 最佳调用阶段 | Fault localization 阶段 | §4 RQ4 |
| 跨基准迁移 | SWE-Rebench、SWE-QA 同样得到"精度保持 + 成本下降" | §4 |

> 锚点：Table 1；§4 RQ1–RQ4；图 2。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2606.14061v3，2026-06-19 |
| 代码与数据 | https://github.com/cslsolow/SeeRepo |
| 底层 Agent | Mini-SWE-Agent |
| 渲染工具 | Graphviz |
| 配套阅读 | `09-SWE_Explore仓库探索.md`（仓库探索能力评测）、`10-CodeNib多视图数据系统.md`（多视图上下文服务） |

> 锚点：§3 Implementation；参考文献。

## 5. 一句话索引（给 Agent 用）

> **别让 Agent 只能看代码文本**：把仓库依赖图渲染为 PNG 作为文本的**补充**（不是替代），在 fault localization 阶段调用、用 Graph layout 和动态深度，可在 SWE-bench Verified 上做到 **GPT-5-mini 输入 token −25%、成本 −26%、Pass@1 +0.4**——多模态仓库上下文是真实可量化的省 token 路径。
