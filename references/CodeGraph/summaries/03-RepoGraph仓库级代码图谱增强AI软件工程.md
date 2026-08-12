# 论文摘要：RepoGraph（用仓库级代码图谱增强 AI 软件工程）

> **原论文标题**：RepoGraph: Enhancing AI Software Engineering with Repository-Level Code Graph
> **完整 PDF 文件名**：`RepoGraph_Enhancing_AI_Software_Engineering_with_Repository-level_Code_Graph.pdf`
> 作者 / 年份 / 出版：Siru Ouyang, Wenhao Yu, Kaixin Ma, Zilin Xiao, Zhihan Zhang, Mengzhao Jia, Jiawei Han, Hongming Zhang, Dong Yu；UIUC / Tencent AI Seattle Lab / Rice / Notre Dame；ICLR 2025
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 把 LLM Coding Agent 从"按文件/函数拼上下文"升级到"**按仓库级依赖图谱定位**"时——例如 SWE-bench、SWE-Agent、AutoCodeRover、Agentless 集成。
- 需要给 LLM **行级（line-level）结构化上下文**，而不是粗糙的整文件/类时。
- 同时接入**程序化框架（procedural，如 RAG、Agentless）**和**智能体框架（agentic，如 SWE-Agent、AutoCodeRover）**两种场景。
- 想在 SWE-bench / CrossCodeEval 类基准上做"仓库上下文工程"的 plug-in 评估。
- 与其他"仓库级代码图谱"（RepoUnderstander、CodexGraph、RepoCoder、GraphCoder）做横向对照。

> 锚点：摘要；§1 Introduction；§3 RepoGraph；§4 Experiments。

## 2. 主要观点与方案

### 2.1 核心论点

- **现有方法对仓库结构建模粒度不够**：RAG 只能做"文件级相似性"；Agentless 把仓库压成扁平文档；Agent 框架没有全局结构意识，容易陷入局部最优。
- **以"代码行"为节点、以"调用/包含"为边**构造仓库级图谱，弥补 line-level / file-level / repo-level 三层之间的粒度空缺。
- **Ego-graph 检索**：每次只取出与当前搜索词相关的 k-hop 自我中心子图，扁平化后注入 prompt。
- **作为 plug-in**：对 procedural / agentic 框架只需在动作空间中加一个 `search_repograph()`，其余保持不变。

### 2.2 方法

- **构造步骤**：
  1. **Code line parsing**：用 tree-sitter 解析每个源文件，识别函数/类/变量/类型的定义与引用，过滤掉非相关文件。
  2. **Project-dependent relation filtering**：剔除标准库 / 内建 / 第三方无关关系。
  3. **Graph organization**：节点是代码行，节点属性包含 name、fname、kind（def/ref）、category、line；边分 `E_invoke`（调用关系）和 `E_contain`（包含关系）。
- **检索方式**：`search_repograph(term)` 取该 term 的 k-hop ego-graph（k 默认 1-2），扁平化后追加到 prompt。
- **集成方式**：
  - **Procedural 框架**（RAG、Agentless）：在 localization 和 edition 阶段各调用一次 `search_repograph`。
  - **Agent 框架**（SWE-Agent、AutoCodeRover）：把 `search_repograph` 作为一个新动作加入 agent 动作空间，term 由 agent 自主决定。

> 锚点：§3.1 Construction；§3.2 Utility；图 2；§4 Experiments。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| SWE-bench-Lite 提升 | procedural 与 agent 框架平均相对改进 **+32.8%** | §4 |
| RAG (GPT-4) | resolve 2.67 → 5.33；patch apply 29.33 → 47.67 | Table 2 |
| Agentless (GPT-4o) | resolve 27.33 → 29.67；patch apply 97.33 → 98.00 | Table 2 |
| AutoCodeRover (GPT-4) | resolve 19.00 → 22.67（与 leaderboard 同步） | Table 2 |
| 跨基准迁移 | CrossCodeEval 同样带来提升 | §4 |
| 关键设计点 | line-level 节点粒度 + k-hop ego-graph 检索 + 通用 action 接口 | §3 |

> 锚点：§4 Experiments；Table 2；Table 4（k-hop 消融）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | ICLR 2025 会议版（与 arXiv:2410.14684v2 同源，PDF 排版不同） |
| 代码 | https://github.com/ozyyshr/RepoGraph |
| 集成基线 | SWE-Agent、AutoCodeRover、Agentless、RAG (BM25) |
| 对比工作 | RepoUnderstander（Ma et al. 2024）、CodexGraph（Liu et al. 2024）、DraCo、Aider、CodePlan |
| 配套阅读 | `08-TICoder代码仓库检索.md`（实现感知复用）、`09-SWE_Explore仓库探索.md`（探索能力评测）、`10-CodeNib多视图数据系统.md`（多视图仓库上下文服务） |

> 锚点：§2 Related Work；附录。

## 5. 一句话索引（给 Agent 用）

> 给 SWE 类 Agent 加一个**行级 ego-graph 检索动作**（`search_repograph(term)`），把"找相关代码"从字符串相似提升到"定义-引用依赖图上的局部遍历"，即可在 SWE-bench-Lite 上**全方法平均 +32.8%**；这是仓库级图谱作为 Agent 通用 plug-in 的最有力证据。
