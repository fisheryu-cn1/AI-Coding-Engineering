# 论文摘要：SWE-bench（仓库级代码修复基准）

> **原论文标题**：SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
> **完整 PDF 文件名**：`12-Jimenez-SWE_bench.pdf`
> 作者 / 年份**：Carlos E. Jimenez et al.（Princeton / Georgia Tech），2024，ICLR 2024
> 摘要类型：Agent 设计参考 + 评测基线
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **仓库级代码修复 Agent / SWE-Agent / SWE-Eval** 时：把 SWE-bench（Verified / Lite / Multilingual / Multimodal）当成事实基线。
- 编写 **Agent 评测报告** 时：参考 SWE-bench 的 task 构造、容器化执行、fail-to-pass / pass-to-pass 测试协议。
- 做 **能力对比 / 路线图** 时：本基准是 2024 年起衡量 LLM 在"真实软件工程任务"上能力的核心 anchor。
- 评估 **长上下文、检索、ACI（Agent-Computer Interface）** 设计时，SWE-bench 是验证端到端收益的标准靶。
- 用于 Agent **DAG 设计参考**：理解 localization → edit → test 这条流水线的来源与边界。

> 锚点：Abstract；§1 Introduction；§3 Task Construction；§6 Evaluation。

## 2. 主要观点与方案

### 2.1 核心任务定义

- 任务：给定一个 **GitHub issue** 与 **代码仓库 snapshot**，模型需生成一个 **patch**（对真实代码库文件的修改），并在 **容器化环境**中执行仓库现有测试套件验证。
- 关键指标：**Resolved rate** = 通过 **全部** fail-to-pass（issue 引入的失败→修复后通过）+ **保留** pass-to-pass（修复前通过、修复后仍通过）的比例。
- 数据规模：**2,294 个 task**，来自 **12 个流行的 Python 仓库**（如 Django、matplotlib、scikit-learn、spaCy、astropy、pytest、xarray、pylint、wandb、marshmallow、seaborn、flask），每个 task 来源于真实的 pull request。

### 2.2 任务构造（§3 Task Construction）

- **拉取候选 PR**：扫描 GitHub 上合入到目标 12 仓库的 PR，过滤"代码变更 + 测试更新"组合。
- **筛选条件**：必须包含 issue 描述；只接受安装后可执行测试的项目；PR 必须在 2022 年后创建以避免早期 benchmark 泄漏；过滤"trivial / docs only / auto-generated" PR。
- **测试拆分**：将测试集拆为 fail-to-pass（验证 issue 是否被修复）与 pass-to-pass（防止回归），人工校验 ground-truth patch 能让所有 fail-to-pass 通过且不影响 pass-to-pass。

### 2.3 评测环境

- **Docker 容器化执行**：每个 task 在一个隔离环境中运行，使用 `pytest`（或目标仓库的 test runner）作为判定器。
- **执行预算**：默认 30 分钟 wall-clock，限制 token 输出与磁盘 IO。
- **指标**：Resolved（主指标）、% of fail-to-pass tests passed、% of pass-to-pass tests preserved。

### 2.4 经验与教训

- **检索/导航成本极高**：SWE-bench 任务平均要修改 1.7 个文件、涉及跨多个目录的依赖；模型需要定位正确的代码位置才能产出有效 patch。
- **容器化测试必要性**：避免"看起来通过但实际破坏"——这是 SWE-bench 区别于 HumanEval/MBPP 的关键设计。
- **早期结果**：论文报告的最强基线（截至发表时）≈ 1.96% resolved（Claude-3 Opus 等），后来成为 Agent 突破的标志事件——SWE-agent 在 GPT-4 下达到 12.5%，SWE-agent + Claude 3.5 Sonnet 突破 23%+。

### 2.5 衍生版本

- **SWE-bench Lite**（300 task）：人工精选子集，便于快速评测与消融。
- **SWE-bench Verified**（500 task）：OpenAI 人工校验后的高质量子集，与 SWE-bench Multimodal（视觉截图版）配套。
- **SWE-bench Multilingual**：覆盖 9+ 种语言的仓库级任务。
- **SWE-rebench**（Badertdinov et al. 2025）：自动化 + 去污染的滚动任务集（见 §3 构造同款思路）。
- **SWE-EVO**：将任务延伸到跨多文件/多迭代的软件演化场景（见 Harness-Native SE 论文的对比）。

## 3. 达到的效果

| 度量 / 现象 | 数值 / 结论 | 锚点 |
|---|---|---|
| Task 总数 | 2,294（来自 12 个 Python 仓库） | §3 |
| 每个 task 平均需修改的文件数 | ~1.7（多文件/跨目录依赖常见） | §3 |
| 评测 wall-clock 预算 | 30 分钟 / task | §4 |
| 论文基线 resolved rate（best prior） | ~1.96%（Claude-3 Opus / GPT-4 等基础 LLM） | §5, Table 2 |
| 后续里程碑 | SWE-agent + GPT-4 12.5%；Claude 3.5 Sonnet + Agent 23%+；AutoCodeRover 等进一步提升 | 外部里程碑（见 13/14 摘要） |
| 测试拆为 fail-to-pass + pass-to-pass | 防止"删测试也通过"的退化方案 | §4 |
| Pass@1 vs resolved | resolved 更严格：必须同时保持 pass-to-pass | §4 |

> 锚点：§3 Task Construction；§4 Evaluation Harness；§5 Experimental Setup & Results；§7 Discussion。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2310.06770（ICLR 2024） |
| 数据集 | SWE-bench / SWE-bench Lite / Verified / Multimodal / Multilingual（后续衍生） |
| 评测框架 | Docker 容器 + pytest；详见官方仓库 `princeton-nlp/SWE-bench` |
| 关联工作 | SWE-agent（Yang et al.）→ 见本主题 14；Agentless → 15；RepoGraph → 13；AutoCodeRover（多文件定位） |
| 协议基线 | pass-to-pass / fail-to-pass 双轨、resolved rate、% of regression tests preserved |
| 配套工具 | `swe-bench` CLI、`SWE-bench docker` 镜像、各家 Agent harness（如 SWE-Agent / OpenHands） |

> 锚点：§3 Task Construction Pipeline；§4 Evaluation Harness；References。

## 5. 一句话索引（给 Agent 用）

> 做仓库级 SWE Agent 评测时，**以 SWE-bench 的"GitHub issue + 仓库 snapshot + Docker 化测试 + fail-to-pass/pass-to-pass"协议为事实基线**，并明确报告检索/ACI/执行底座这些 harness 变量——单看 resolved 数字而不固定 harness 会得出错误结论。