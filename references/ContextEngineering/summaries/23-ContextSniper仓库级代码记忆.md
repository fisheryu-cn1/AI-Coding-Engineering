# 论文摘要：ContextSniper（AntTrail 仓库级代码记忆）

> **原论文标题**：ContextSniper: AntTrail's Token-Efficient Code Memory for Repository-Level Program Repair
> **完整 PDF 文件名**：`23-Luk-ContextSniper_v3.pdf`
> 作者 / 年份 / 出版：Chiwang Luk, Matin Mohammad Najafi, Zhifeng Jia, Wei Yang, Xiuchang Li, Jinwei Zhu, Yang Ren, Lei Chen, Gao Cong（Huawei & HKUST(GZ) & NTU），2026，arXiv:2607.01916v3
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 为**仓库级代码修复（repository-level program repair）**智能体设计上下文访问层：把 noisy repo / runtime 输出筛成"证据包 (evidence packet)"，以替代 read-try-fail-reread 循环。
- 在不替换宿主智能体（host agent）的前提下，作为**插入层**插入 MCP / Plugin 工具与现有 Claude Code、OpenClaw 协同工作。
- 当需要在 token 经济性 + 修复质量间取得平衡时：在 SWE-bench Lite 50-task 配对对照下，对 OpenClaw 减 51.5% total token，对 Claude Code 减 38.9%，提交修复率基本不变。
- 当需要把 RAG、prompt 压缩、agent-tool 输出过滤三类思路整合成**单一上下文访问层**时。

> 锚点：Abstract；§1 Introduction（Figure 1A/B/C 三视角）。

## 2. 主要观点与方案

### 2.1 核心主张（"broadly retrieve, narrowly expose"）

- 仓库代码修复里既有相关又有噪声的上下文同时堆进 prompt，导致"重复 grep → 长文件读 → 长日志" 循环；扩大 prompt 既不省钱也不提升修复率。
- 与上下文压缩不同：ContextSniper 不试图把 prompt 均匀缩减，而是**保留源可追溯的证据包**（保留路径、行号、可执行脚本可被切回原内容）。
- 与现有 RAG / 输出过滤系统不同：它把"读、bash、长输出"直接在进入 context window 之前门控掉，而不是事后压 prompt。

### 2.2 架构（§3, Figure 2）

- **双族记忆 L0-L2 层级**（§3.2）：
  - **Code memory**（代码侧）：L0 抽象 / L1 路径 + 符号 + ctags + graph 关系 + BM25 / L2 = AST 切片（Python 用 tree-sitter，其他用行窗）。
  - **Action memory**（动作侧）：L0 sniped 视图 / L1 tool/path/status/type / L2 = 原始 read 或 bash 输出。
  - **AGFS-Agent File System** 后端（外部仓库）。
- **memory ↔ repository 两阶段同步**（§3.3）：
  - 第一阶段在 agent 写入 / 编辑 / 跑测试的 hook 上即时刷新（编辑验证目标路径 → 应用替换 → 触发该文件 re-chunking）。
  - 第二阶段在新一轮用户提示时再做差异校验（不只匹配 hook，避免 stale memory 影响下一轮）。
- **adaptive top-k 检索 + hybrid ranker**（§3.4, Algorithm Figure 4）：
  - 多路由（embedding + BM25 + ctags symbol + graph 关系 + ripgrep fallback），加权 RRF；traceback / behavioral / stateful debugging 自动分配 budget。
  - `intent ← InferIntent(q, A)`、`routes ← PlanRoutes(intent)`、`k* = min(k0, BudgetToK(B))`、再 expand-to-L2 → dedup → prune。
- **意图感知的 context gate**（§3.5, Algorithm Figure 5）：
  - 输入 `FileRead → 保留请求区域 + 本地定义 + 邻居`；`CommandOutput → 命令 + 失败断言 + 验证信号`；其他 → 状态信号。
  - 保守原则：宁可少扔不给全删；metadata 标记 `sniped`，原样本放入 action memory L2 并 attach 一行 recovery hint，agent 可要求 expand。
- **Host-agent 边界（§3.6）**：宿主决定 plan / 编辑 / 验证；插入层决定什么上下文进 prompt。同一适配可接 Claude Code（MCP）与 OpenClaw（plugin）两种 host。

> 锚点：§3.1 System Overview；§3.2 Memory Hierarchy（Figure 3）；§3.3 Synchronization；§3.4 SearchCode（Figure 4）；§3.5 ContextGate（Figure 5）；§3.6 Host-Agent Boundary。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| OpenClaw SWE-bench Lite 50-task 对照 token reduction | -51.5%（1.36M → 0.66M/token） | Table 2; Figure 6 |
| OpenClaw cost reduction | -36.4%（$0.635 → $0.404） | Table 2 |
| OpenClaw tool/action count reduction | -46.4%（32.1 → 17.2） | Table 2 |
| OpenClaw 提交修复率 | ContextSniper 24.0% vs baseline 26.0%（-2pp ≈ 持平） | Table 2 |
| Claude Code SWE-bench Lite 50-task token reduction | -38.9%（85.97M → 52.55M） | Table 2 |
| Claude Code cost reduction | -27.3%（$15.09 → $10.97） | Table 2 |
| Per-task token 散点 | 45/50 matched tasks 节省；5/50 涨幅 9.6–152.3% | §4.3 Task-Level Failure Analysis; Figure 7 |
| 5-task Django 试点 vs mem0/Letta/OpenViking/Serena/LlamaIndex/TencentDB | 平均 token 量最低、与其他主流 memory 系统效率对比优势明显；任务通过率不弱 | §4.4 Comparison; Figure 10 |
| Retrieval recall（Recall@1 / @3 / @5 各仓库） | 多数仓库早期返回即覆盖目标文件；个别仓库差距成为 token 上升原因 | Figure 9 |

> 锚点：§4.2 Main Results（Table 2, Figure 6, Figure 7）；§4.3 Task-Level Failure Analysis；§4.4 5-task Pilot（Figure 10）。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| AntTrail 总体引擎 | https://gitcode.com/datagallery/AntTrail （论文讨论的是修复模块） |
| ContextSniper 评估 harness | https://gitcode.com/lukchiwang/ContextSniper （pilot testing scripts） |
| 评测基准 | SWE-bench Lite（Jimenez et al. 2024）50 tasks/repo |
| 宿主智能体 | OpenClaw 1.6× / Claude Code via MCP |
| 主要基线（context-access 视角） | SWE-agent / AutoCodeRover / Agentless；Codebase-Memory（Tree-Sitter + MCP）；RepoGraph；KGCompass |
| Prompt / retrieval compression | LLMLingua / LongLLMLingua；RECOMP / COMPACT / Selective Context / AutoCompressor；ctxbudgeter；Token Reducer |
| Agent-tool 输出过滤 | RTK（Rust CLI proxy，60–90% savings）；Headroom（library + proxy + MCP，60–95% savings）；Bearing（workflow 级 fresh context） |
| 关键依赖 | tree-sitter（Python AST 切分）；AGFS（c4pt0r/agfs）；Universal ctags；ripgrep；BM25（Robertson & Zaragoza）；RRF（Cormack et al. 2009） |
| 测试模型 | Claude Haiku 4.5（Claude Code 用） |

> 锚点：§1.3 Contributions（Table 1 定位表）；§2 Background and Related Work（§2.1–§2.5 五条线）；§4.1 Experimental Setup。

## 5. 一句话索引（给 Agent 用）

> 给仓库级 coding agent 做上下文访问层时，**别只压缩 prompt，应在仓库/工具输出进入 prompt 之前先做"证据狙击"**：双族 L0/L1/L2 记忆（代码 + 动作）+ 两阶段同步（hook + 任务边界）+ 意图感知 context gate（sniped 标记 + L2 可恢复）让 OpenClaw 在 SWE-bench Lite 上 -51.5% token / -36.4% cost，Claude Code -38.9% token / -27.3% cost，提交修复率几乎不掉。
