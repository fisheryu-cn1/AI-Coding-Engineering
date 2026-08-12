# 论文摘要：RepoGraph（仓库级代码图谱增强 Agent）

> **原论文标题**：RepoGraph: Enhancing AI Software Engineering with Repository-level Code Graph
> **完整 PDF 文件名**：`13-Ouyang-RepoGraph.pdf`
> 作者 / 年年：Wenxin Ouyang et al.，2024
> 摘要类型：Agent 设计参考 + 上下文工程方案
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **仓库级 SWE Agent 的检索 / 上下文构造** 时：本工作给出把代码库转为细粒度图、再喂给 Agent 的端到端方案。
- 处理 **跨文件、多跳依赖** 的代码定位任务（multi-hop localization），需要超过纯向量检索的精确度时。
- 做 **检索增强 vs 图增强** 的方案对比时：本工作给出一种轻量 AST 抽取 + 2-hop ego-network 的折中方案。
- 给 Agent **维护 PR-style test 补丁链** 或 **提交级上下文** 时：本工作提供了将 diff 与图节点对齐的接口。
- 在 **仓库级 / 项目级 RAG 工具** 中需要选择粒度（chunk vs function vs entity）时，本工作是参考案例之一。

> 锚点：Abstract；§1 Introduction；§3 Method；§4 Repository-level Code Graph Construction。

## 2. 主要观点与方案

### 2.1 问题与动机

- 现有 SWE Agent 多依赖 **全文检索（BM25）或向量检索（embedding similarity）** 来定位需要修改的代码段，对 **跨文件、跨符号** 的依赖追踪能力不足。
- 单纯拼接仓库 chunk 会导致 **上下文窗口爆炸**，且向量检索对函数签名/调用关系的语义匹配并不精准。
- 解决思路：在 **仓库级代码图谱（Repository-level Code Graph）** 上做检索/上下文选择，比"扁平 chunk + embedding"更适合 SWE 任务。

### 2.2 仓库级代码图谱（§4 Construction）

- **解析粒度**：以 **AST（抽象语法树）为骨架**，抽取 function / class / method / variable / import 等实体作为节点。
- **边类型**：调用（call）、继承（inheritance）、导入（import）、实例化（instantiation）、数据流（data flow）等。
- **范围**：覆盖整个仓库（whole repository）的图，不是 per-issue 子图。

### 2.3 RepoGraph 的核心抽象

- **2-hop ego-network（局部 ego 图）**：围绕"与 issue 相关的入口点"做 1-hop + 2-hop 邻居展开，作为 Agent 的上下文窗口。
- **入口点选取**：由 BM25 / embedding 检索在仓库级图中选若干 seed 节点（典型为 issue 关键词命中位置），然后 2 跳内扩展。
- **序列化**：把 ego-network 序列化为"节点摘要 + 出/入边 + 代码片段"的列表，按"距离 seed 跳数 + 重要度"排序喂给 LLM。

### 2.4 在 SWE Agent 中的集成（§3 / §5）

- 用 RepoGraph 替换 SWE-agent / Agentless 的"先全文/向量检索，再 patch"的检索模块。
- 仍然保留 **localize → edit → test** 的三阶段流水线（图只作用于 localization 阶段）。
- 实现在不同 Agent 上可插拔：对 SWE-agent 提供节点级 hint，对 Agentless 提供结构化 function list。

### 2.5 评测（§6）

- 任务：SWE-bench（及其 Lite 子集）。
- 主要对照：
  1. 全文检索 + LLM（vanilla baseline）。
  2. 向量检索 + LLM（embedding RAG）。
  3. RepoGraph（本文方法）。
- 度量：resolved rate；定位准确率（localization F1）；定位召回（多文件情况）。

## 3. 达到的效果

| 度量 / 现象 | 数值 / 结论 | 锚点 |
|---|---|---|
| SWE-bench Lite resolved 提升 | RepoGraph 在多模型上稳定高于 BM25 / embedding RAG 基线 | §6 |
| 定位精度（文件级 / 函数级） | 优于纯向量检索，尤其在多跳依赖场景 | §6 |
| 上下文规模 | 通过 2-hop 截断，把超大仓库压缩到 LLM 可承受窗口 | §4 |
| 与 SWE-agent / Agentless 兼容 | 作为可插拔 retrieval module，无需改 Agent 主循环 | §3, §5 |
| AST 抽取成本 | 一次性的离线构建成本，运行时开销极低 | §4 |

> 锚点：§4 Repository-level Code Graph Construction；§5 Integration；§6 Experiments。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | 见论文 PDF `13-Ouyang-RepoGraph.pdf` |
| 关联方法 | SWE-agent（论文 14）、Agentless（论文 15）、AutoCodeRover、GraphCoder |
| 评测基线 | SWE-bench / SWE-bench Lite（论文 12）、LocBench（定位子任务基准） |
| 关联工具 | Tree-sitter / LSP / SCIP（可作为 AST 抽取后端）；embeddings（BGE / OpenAI / Contriever） |
| 后续工作 | 用知识图谱/类型图做更丰富的图；把 PR / commit history 也纳入图边 |

> 锚点：§3 Method Overview；§4 Graph Construction；§6 Experiments；References。

## 5. 一句话索引（给 Agent 用）

> 给 SWE Agent 做 **仓库级检索** 时，**用 RepoGraph 风格的"仓库级 AST 图 + 2-hop ego-network"取代纯向量检索**：先在图上选 seed，再做局部扩展序列化，比扁平 chunk 更适合跨文件、跨符号的依赖追踪——这是把"图增强 RAG"接入 SWE Agent 的标准做法。