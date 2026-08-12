# 论文摘要：ICAE-Bench（交互式 Coding Agent 评测 — 项目构建场景）

> **原论文标题**：ICAE-Bench: Evaluating Coding Agents as Interactive Project Builders
> **完整 PDF 文件名**：`11-Peng-ICAE_Bench_v1.pdf`
> 作者 / 年份 / 出版：Zhongyuan Peng, Dan Huang, Chuyu Zhang, Caijun Xu, Changyi Xiao, Shibo Hong, David Lo, Lin Qiu, Xuezhi Cao, Jiyuan He, Yixin Cao（Fudan University / Meituan Group / Singapore Management University / Shanghai Innovation Institute），2026，arXiv:2607.21217v1
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **vibe coding / 0-to-1 项目生成** Agent 的评测时：现有 benchmark 多假设任务目标静态 / 显式，ICAE-Bench 把"模糊需求 + 交互澄清"作为评测核心。
- 构建 **多语言跨领域** Agent benchmark（覆盖 12 种语言、12 类应用）时。
- 设计 **可控制的 User Agent**（防止 prompt 泄漏 / 编造需求）时。
- 想把"功能正确"与"工程品质"分开评测时——本文提供 4 类多维诊断。
- 给 Coding Agent 团队做 **fuzzy requirement → working repo** 的能力对比时。
- 与论文 04-Anthropic-Trends、10-Ben_Sghaier 互补：把"vibe coding"行业趋势落到可测 benchmark。

> 锚点：Abstract；§1 Introduction；§3 ICAE-Bench；§4 Experiments；§5 Analysis。

## 2. 主要观点与方案

### 2.1 现状与定位（§1）

- Coding Agent 正从"代码助手"转向"项目构建者"：vibe coding 从模糊意图起步，结合规划、需求澄清、工具使用、调试、仓库级构建。
- 现有 benchmark（HumanEval、MBPP、RepoBench、SWE-bench 等）多假设任务目标静态、显式或不需用户交互，不能评测"边问边建"的能力。
- Commit0 / NL2RepoBench / PRDBench / ProgramBench / RealBench 等 0-to-1 benchmark 也大多给了详细 spec 或固定 scaffold。

### 2.2 ICAE-Bench 的三大设计（§1）

- **从精确反推模糊**：每个任务从真实开源仓库（其行为可执行、可测）出发，构造 GroundPRD 与黑盒行为，再"模糊化"为 Fuzzy PRD（隐藏约束存于 User Agent Data），保留固定行为目标。
- **三档模糊层级 L1 / L2 / L3**：构造信息暴露分级（操作性而非通用心理量表）。
- **多维诊断**：功能正确 + agentic 评估 + 结构评估 + 交互质量。

### 2.3 Benchmark 实例（§3.A）

- 实例形式化：T = (D_f, E, P, U, B)
  - D_f：Fuzzy PRD（初始需求）；
  - E：ultimate-image 执行环境；
  - P：Public set（可被交互恢复的示例）；
  - U：User Agent Data（省略约束 + 完整 P 输入输出 + 交互记录）；
  - B：权威 Native + Enhanced cases（评测目标）。

### 2.4 构造流水线（§3.B, Figure 2）

- 5 阶段：Repo Filter → GroundPRD 合成 + Test refactoring → Fuzzification → Ultimate Image Packaging → Artifact Verification。
- Repo 筛选：原 tests 在 Docker 中通过。
- GroundPRD：从验证后的行为合成自然语言规范。
- Test refactoring：原 tests → 标准化 JSON black-box cases，外部可观察合约保留，内部 API / module 结构剥离。
- Enhanced cases：合成边界值 / 特殊约束 / 压力 / corner cases；与 Native 不重叠；每条须在 golden 实现上通过。
- Fuzzification：3 个模糊层级（L1 最少信息 → L3 接近完整），每层对应不同"被隐藏的约束集"。
- Ultimate Image：基础镜像（各语言 LTS 版本，如表 IV）→ 运行 golden → 安装依赖 → 删除 golden code / 原 tests / 隐藏 artifact；保留 runtime 与依赖栈。

### 2.5 User Agent 设计（§3.E）

- 默认用 **DeepSeek-V3.2** 作为 user-router；模拟严格产品 stakeholder。
- 每个 task 最多 16 query；每 reply 最多覆盖 3 个 matched technical points。
- 三层 leakage 防御：
  - User Agent 看不到 golden code / 原 tests / repo identity / 隐藏 cases；
  - coding agent 看不到 record，仅看到 natural-language reply；
  - evaluation 在 fresh container 注入权威 cases。
- 数据结构：每个 omitted ambiguity point 配 identifier + trigger phrases + grounded response + context pointer + fallback。

### 2.6 评测维度（§3.F）

- **功能正确**：Public / Native / Enhanced pass rate + Overall。
- **Agentic Evaluation**：Semantic similarity、API similarity、Design quality。
- **结构评估**：File count ratio、LOC ratio、class / method / namespace similarity。
- **交互质量**：Constraint coverage (|H|/|C|)、Fallback rate、Budget usage。

### 2.7 数据集规模（§3.D, Table V）

- 12 语言：C#, C++, Dart, Go, Java, JavaScript, Kotlin, PHP, Python, Ruby, Rust, TypeScript。
- 40 tasks/language = **480 tasks**；ICAE-Bench-Lite 50 tasks（按 LOC 选小仓库）。
- Golden LOC：最大 2,918,810；最小 318；中均 35,533。
- File count：最大 17,488；最小 4；中均 258。

### 2.8 评测配置（§4）

- 6 模型：GPT-5.5、Claude-Opus-4.8、Claude-Sonnet-4.6、GLM-5.1、Gemini-3.1-Pro、MiniMax-M2.5。
- 框架：Claude Code + OpenHands。
- User Agent backbone：DeepSeek-V3.2；budget 16 query。
- 4 个 RQ：① fuzzy → 仓库实现能力；② 交互对 gap 的修复度；③ 瓶颈定位；④ 框架 / backbone / budget / 思考设置 / 环境 / 语言的敏感性。

> 锚点：§1 Introduction; §3.A Instance Definition; §3.B Construction; §3.C Verification; §3.E User Agent; §3.F Metrics; §4 Experiments。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 任务总数 | **480 tasks / 12 languages**（ICAE-Bench-Lite 50） | §3.D, Table V |
| 最佳 Overall pass rate（full ICAE-Bench，Claude Code） | **Claude-Opus-4.8：38.2%**（最高） | §4.B, Table VI |
| GPT-5.5 Overall | 37.2% | Table VI |
| Gemini-3.1-Pro Overall | 27.0% | Table VI |
| GLM-5.1 Overall | 26.6% | Table VI |
| Claude-Sonnet-4.6 Overall | 21.8% | Table VI |
| MiniMax-M2.5 Overall | 0.8% | Table VI |
| ICAE-Bench-Lite 最佳 Overall | **GPT-5.5：53.3%** | Table VII |
| ICAE-Bench-Lite Claude-Opus-4.8 | 48.2% | Table VII |
| Public pass rate（Opus-4.8） | 48.5%；Enhanced 35.5% | Table VI |
| Agentic 评分最高 Semantic similarity | Sonnet-4.6：22.9%（但 Overall 仅 21.8%） | Table VI |
| GroundPRD 仍是最强 upper bound（4/6 模型） |  | §4.B, Figure 6 |
| 瓶颈定位：信息-to-execution gap | 大于 requirement-access gap | §4.B |
| 失败模式统计（per 480 repo） | Opus-4.8: mismatch 387, missing 120, no-test 29, exec 25 | Figure 9 |
| GPT-5.5 失败：mismatch 443 / missing 179 / no-test 0 / exec 25 |  | Figure 9 |
| Per-language best model varies |  | Table VIII |
| Constraint coverage（Opus-4.8） | 69.6%（full），67.8%（lite） | Tables VI-VII |

> 锚点：§4.B Main Results; Table VI; Table VII; Table VIII; Figure 6; Figure 9; §4.C Analysis。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2607.21217 |
| 代码仓库 | https://github.com/ALEX-nlp/ICAE-EVAL |
| 评测模型 | GPT-5.5、Claude-Opus-4.8、Claude-Sonnet-4.6、GLM-5.1、Gemini-3.1-Pro、MiniMax-M2.5 |
| User Agent backbone | DeepSeek-V3.2（默认） |
| Agent 框架 | Claude Code、OpenHands |
| 关联 benchmark | HumanEval、MBPP、RepoBench、M2RC-Eval、SWE-bench、Multi-SWE-bench、SWE-Bench Pro、SWE-Compass、Commit0、NL2RepoBench、PRDBench、ProgramBench、RealBench、HumanEvalComm、Orchid、When Benchmarks Talk、Ask or Assume |
| 关联项目 | 与论文 09-RepoRescue（agent 能力评测）、论文 04-Anthropic-Trends（vibe coding 趋势）、论文 10-Ben_Sghaier（harness 演化）共同构成"AI Agent × Coding"系列参考 |

> 锚点：Abstract; §2 Related Work (A Software-Agent Benchmarks, B 0-to-1 Repository Generation, C Ambiguity and Clarification); §4 Experiments。

## 5. 一句话索引（给 Agent 用）

> 当需要评测 **vibe coding / 0-to-1 项目生成 / 模糊需求澄清** 能力的 Agent 时，ICAE-Bench 是最贴合当前行业实践的基准：**480 tasks / 12 languages + 3 层 Fuzzy PRD（L1–L3） + grounded User Agent（防泄漏）+ 多维评估（功能 / agentic / 结构 / 交互）**——实验揭示两个独立 gap（requirement-access 与 information-to-execution），且 **当前最强模型 Overall 仅 38.2%**（Claude-Opus-4.8），说明"边问边建"远未饱和，是 Coding Agent 团队下一阶段能力建设的关键靶点。