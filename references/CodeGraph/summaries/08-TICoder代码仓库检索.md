# 论文摘要：TICoder（用测试驱动规划 + 实现感知复用做仓库级代码生成）

> **原论文标题**：TICoder: A Repository-Level Code Generation Framework with Test-Driven Planning and Implementation-Aware Reuse
> **完整 PDF 文件名**：`08-Nan-TICoder.pdf`
> 作者 / 年份 / 出版：Siyu Nan, Yaling Luo, Jian Wang, Neng Zhang, Bing Li；武汉大学 / 华中师范大学；arXiv:2606.08135v1，2026-06-06
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 给 Coding Agent 装上**测试用例驱动的规划器**：让测试作为行为规约指导实现步骤分解。
- 需要"实现感知"地复用仓库内的**被调函数（callee）**：不能只看功能相似，还要看实现相似与典型用法。
- 仓库级 RAG 框架遇到"功能相近但实现在仓库里没现成代码"时，**改用多函数组合生成**而不是硬匹配单函数。
- 评估**多个 LLM backbone**（GPT-4o-mini、DeepSeek-V3、Qwen2.5-Coder）下的代码生成提升。
- 在 CoderEval / DevEval 仓库级基准上做生成质量对比。

> 锚点：摘要；§1 Introduction；§2 Related Work；§3 Motivating Example；§4 Method。

## 2. 主要观点与方案

### 2.1 核心论点

- 现有 RAG + 规划方法存在两大问题：
  - **L1**：缺乏测试驱动的行为指导，规划与行为不一致。
  - **L2**：忽视被调函数的实现逻辑，检索到的函数难以有效复用。
- **TICoder = Test-driven planning + Implementation-aware reuse**。
- 规划阶段：**LLM-as-Planner + LLM-as-Judge** 迭代精化（judge-and-reflection 过程）。
- 复用阶段：**双视角检索（功能相似 + 实现相似）** + **双阶段选择（结构聚类 + 困惑度过滤）**。
- 上下文：NL 需求 + 测试 + 检索到的 callee 函数 + 选中的用法模式。

### 2.2 方法

- **Test-Driven Iterative Planning**：
  1. 初始规划（基于 NL 需求）。
  2. 测试用例作行为规约，引导实现步骤细化。
  3. Judge LLM 评估、反射、迭代。
- **Implementation-Aware Reuse**：
  1. **Dual-View Retrieval**：功能相似性 + 实现相似性（生成步骤的代码表示后做相似度计算）。
  2. **Dual-Stage Selection**：结构聚类（按实现模式分组）+ 困惑度过滤（挑最自然的用法）。
- **增强生成**：把 NL、测试、callee、usage pattern 一起喂给生成 LLM。

> 锚点：§4 Method；图 1（动机示例）；图 2（流水线）；Table 1（对比表）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 基准 | CoderEval、DevEval | §5 |
| Backbone LLM | GPT-4o-mini、DeepSeek-V3、Qwen2.5-Coder | §5 |
| 平均提升 | 比 SOTA 基线高 **+11.52%** | Abstract / §5 |
| 对比方法 | A3 Codgen、AllianceCoder、CodePlan、RepoScope、RepoCoder、RLCoder、CoCoGen | Table 1 |
| 关键增益 | 1) 测试驱动规划带来更精确的步骤；2) 实现感知检索带更准的 callee；3) 用法模式提升实际调用正确率 | §5 |

> 锚点：Table 1；§5 Experiments；图 1（动机示例）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2606.08135v1，2026-06-06 |
| 基准 | CoderEval、DevEval |
| Backbone | GPT-4o-mini、DeepSeek-V3、Qwen2.5-Coder |
| 配套阅读 | `09-SWE_Explore仓库探索.md`（探索能力评测）、`03-RepoGraph仓库级代码图谱增强AI软件工程.md`（行级图谱） |

> 锚点：§5 Experiments；References。

## 5. 一句话索引（给 Agent 用）

> 仓库级代码生成要想"规划靠得住、复用不踩坑"，就**把测试当行为规约驱动规划（Judge-and-Reflect）**，并用**功能 + 实现双视角检索** + **结构聚类 + 困惑度双阶段选择**识别真正可复用的 callee——CoderEval/DevEval 上**比 SOTA +11.52%**。
