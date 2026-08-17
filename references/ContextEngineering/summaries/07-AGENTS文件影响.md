# 论文摘要：On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents（AGENTS.md 对 AI 编码 Agent 效率的影响）

> **原论文标题**：On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents
> **完整 PDF 文件名**：`07-Lulla-Impact_of_AGENTS_md.pdf`（另有 2026-08-17 增补的 v2 版本 `07-Lulla-Impact_of_AGENTS_md_v2.pdf`）
> 作者 / 年份 / 出版：Jai Lal Lulla, Seyedmoein Mohsenimofidi, Matthias Galster, Jie M. Zhang, Sebastian Baltes, Christoph Treude（SMU / Heidelberg / Bamberg / KCL），2026，arXiv:2601.20404v1，ICSE JAWs 2026
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- **为新仓库编写 / 评估 AGENTS.md** 时：作为"为什么值得加"的经验证据（runtime ↓ 28.64%，output tokens ↓ 16.58%）。
- **设计 Coding Agent 上下文供给策略** 时：仓库级持久指令文件相对 ephemeral prompt 的工程价值。
- **做 Agent 效率基准 / 成本分析** 时：作为 reference 方法（paired within-task、Wilcoxon 检验、isolation 容器）。
- **规划 Coding Agent 评估管线** 时：作为 PR-replay + LLM 改写 issue 的模板。
- **评估 CLAUDE.md / copilot-instructions.md** 等其他 agent context 文件时：参考本文方法学。

> 锚点：Abstract；§1 Introduction；§2 Background；§3 Study Design；§4 Results；§5 Research Roadmap。

## 2. 主要观点与方案

### 2.1 研究问题

- **RQ**：仓库根目录有 AGENTS.md 时，自主 AI 编码 Agent 完成开发任务所需的资源是否更少？
- "资源"操作化为：① Token 用量（input / cached input / output）；② Wall-clock time-to-completion。
- 采用 **paired within-task 设计**：同一仓库、同一任务（PR），仅切换 AGENTS.md 是否存在。

### 2.2 实验设置（§3 Study Design）

- **Agent**：OpenAI Codex（gpt-5.2-codex），通过 Python wrapper + Codex CLI 调用。
- **数据筛选**：
  - 起步 132 repos；过滤为"根目录仅一个 AGENTS.md" → 89 repos；
  - 用 gpt-oss-120b + Ollama 分类，仅保留含 (i) conventions / best practices、(ii) architecture / project structure、(iii) project description 的 AGENTS.md → 26 repos；
  - 随机抽 10 repos，每 repo 最多 15 个 merged PR，约束：add+del ≤ 100 LoC、≤ 5 modified files、merged、PR 创建和合并都在 AGENTS.md 引入后、仅改 code；
  - 最终 10 repos × ~12 PRs ≈ 124 PRs。
- **任务构造**：checkout pre-merge commit，提取彼时 AGENTS.md；用 gpt-oss-120b 把 PR diff + 文件树改写为 GitHub-issue 格式（problem / expected behavior / constraints / acceptance criteria）。
- **运行环境**：每个 repo 一个隔离 Docker 容器；agent 仅在容器内操作；无 cache 跨任务复用。
- **实验条件**：同一 task 跑两次 — With / Without AGENTS.md（仅删一个文件，其余一致）。
- **质量 sanity check**：人工抽 50 PR 对比 agent 输出与 merged PR，确认非空、非 trivial。

### 2.3 主要结果（§4 Results，Table 1）

- **Wall-clock time**：均值 162.94s → 129.91s（Δ 20.27%）；中位数 98.57s → 70.34s（**Δ 28.64%**）；std 182.24s → 136.84s（Δ 24.91%）。**Wilcoxon signed-rank p < 0.05**。
- **Input tokens**：mean 353,010 → 318,651（Δ 9.73%）；median 116,609 → 120,587（**反而 ↑ 3.41%**）。
- **Cached input tokens**：mean 328,877 → 296,078（Δ 9.97%）；median 103,424 → 104,448（微升 0.99%）。
- **Output tokens**：mean 5,744.81 → 4,591.46（Δ 20.08%）；median 2,925 → 2,440（**Δ 16.58%**）；std 6,987 → 5,161（Δ 26.13%）。**Wilcoxon p < 0.05**。
- 解读：mean vs median 差异表明 AGENTS.md 主要削减少量**高成本运行**（很可能是探索性 navigation 减少带来的尾部优化）；output 节省大于 input 节省，符合"少做规划轮次"假设。

### 2.4 作者推测的机制

- AGENTS.md 把仓库结构 / 约定 / 常用命令 **upfront 写明**，减少 agent 探索式 navigation 与 model 重复请求。
- 未来工作方向：分析 agent 执行 trace，比较 planning 轮次、exploration 步数、重复请求量。

### 2.5 Research Roadmap（§5）

- 扩展规模：更多 repo、更多 PR、多种 agent / model family。
- 评估更广维度：correctness、maintainability、developer alignment；不只 efficiency。
- 分析 AGENTS.md 内容特征（specificity、organization、workflow guidance）对效率的影响。

> 锚点：Abstract；§3.1 Data Collection & Analysis（Agent Selection / Repository Sampling / PR Selection / Pre-PR Reconstruction / Issue Generation / Experimental Conditions / Running / Metrics）；§4 Results（Table 1, Figure 1）；§5 Roadmap。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| Wall-clock median | 98.57s → 70.34s，**Δ 28.64%**（Wilcoxon p < 0.05） | Table 1 |
| Wall-clock mean | 162.94s → 129.91s，Δ 20.27% | Table 1 |
| Output token median | 2,925 → 2,440，**Δ 16.58%**（Wilcoxon p < 0.05） | Table 1 |
| Output token mean | 5,744.81 → 4,591.46，Δ 20.08% | Table 1 |
| Input token mean | 353,010 → 318,651，Δ 9.73% | Table 1 |
| Cached input token mean | 328,877 → 296,078，Δ 9.97% | Table 1 |
| Cached input token median | 103,424 → 104,448（基本不变） | Table 1 |
| Std dev 缩减 | wall-clock 24.91% ↓ / output 26.13% ↓ | Table 1 |
| 被评测 repo 数 | 10（from 132 → 89 → 26 → 10） | §3.1.2, §3.1.3 |
| PR 数 | 124 | Abstract |
| Sanity check | 50 PR 人工对比 | §3.1.7 |
| 任务输入构造模型 | gpt-oss-120b（Ollama） | §3.1.5 |
| 任务成功率 / 完成行为 | 报告"comparable task completion behavior"（未做 correctness 量化） | Abstract |
| 关联 AGENTS.md 部署规模 | 60,000+ repos（2025） | §1 |

> 锚点：§3.1 Study Design；§4 Results；Table 1；Figure 1；Abstract。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | arXiv:2601.20404v1（2026-01-28），ICSE JAWs 2026 |
| Online appendix | https://doi.org/10.5281/zenodo.18348507（含 Python wrapper、task 输入、PR 数据、运行脚本） |
| 评测 Agent | OpenAI Codex CLI，gpt-5.2-codex |
| 工具 | Docker（每 repo 独立容器）；Ollama + gpt-oss-120b（AGENTS.md 分类 + issue 改写） |
| AGENTS.md 规范 | https://agents.md/（60,000+ repos 采纳） |
| 关联工作 | Chatlatanagulchai et al. 2025（Agent READMEs, arXiv:2511.12884）；Mohsenimofidi et al. 2026（Context Engineering for AI Agents, MSR 2026）；SWE-bench（Jimenez 2024, arXiv:2310.06770）；SWE-agent（Yang 2024）；AutoCodeRover（Zhang 2024, arXiv:2404.05427）；EET（Guo 2026, arXiv:2601.05777）；Chatlatanagulchai 2025；Jiang & Nam 2025（arXiv:2512.18925） |
| 关联生态 | OpenAI Codex AGENTS.md docs（[16]）；GitLab Duo AGENTS.md（[7]） |

> 锚点：§1 Introduction；§2 Related Work；§3 Study Design；References [1]–[21]。

## 5. 一句话索引（给 Agent 用）

> **为仓库加一个根目录 AGENTS.md 是性价比最高的 Agent 上下文工程**——在 OpenAI Codex (gpt-5.2-codex) 上 paired within-task 实验显示 median wall-clock ↓ 28.64%、output tokens ↓ 16.58%（均 Wilcoxon p < 0.05），而 task completion 行为保持可比；推荐任何面向 AI coding agent 的仓库把"架构 / 约定 / 项目描述"放进 AGENTS.md，并把它当成可版本控制、可协同维护的 agent 引导层。
