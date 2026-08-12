# 论文摘要：ActPlane（OS 级 Agent 策略强制执行）

> **原论文标题**：ActPlane: Programmable OS-Level Policy Enforcement for Agent Harnesses
> **完整 PDF 文件名**：`08-Zheng-ActPlane.pdf`
> 作者 / 年份 / 出版：Yusheng Zheng, Tianyuan Wu, Quanzhi Fu, Tong Yu, Wenan Mao, Tao Ma, Dan Williams, Wei Wang, Andi Quinn（UC Santa Cruz / Virginia Tech / HKUST / eunomia-bpf / Alibaba Group），2026，arXiv:2606.25189v2
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **Agent Harness 内的安全 / 合规 / 流程策略执行层** 时：本文给出从自然语言意图到内核执行的完整工程路径。
- 解决 **"自然语言策略"与"具体系统动作"间的语义鸿沟** 时（"提交前跑测试" → 哪条测试命令？）。
- 当需要在 **跨事件 / 数据流**（如 "data read from .env must not reach the network"）维度做强制执行时。
- 评估 **eBPF + 信息流控制（IFC）** 在 Agent Harness 中的可行性与开销。
- 设计 **policy domain** 隔离多个 Agent / 多级 authority（user / platform / parent agent）时。
- 与论文 07-LLM-as-Code 互补：07 把控制流交给程序，ActPlane 把策略交给 OS 内核。

> 锚点：Abstract；§1 Introduction；§2 Motivation；§3 Design；§4 Implementation；§5 Evaluation。

## 2. 主要观点与方案

### 2.1 问题（§1, §2）

- AI Agent 越来越在生产中通过 harness 运行，policy engine 负责执行"提交前跑测试"等安全 / 效能策略。
- **现有方案不足**：
  - Tool-call guardrails（拦截 API 调用）：**漏掉绕过 tool layer 的间接系统动作**（如 agent 写的脚本里 `git commit`）。
  - OS 沙箱（chroot / namespace / Landlock）：只控资源访问，**不控动作**；且返回 opaque denials（EPERM），不告诉 agent 哪条策略被违反。

### 2.2 关键洞见与设计要求

- **洞见**：policy context 在离 task 最近的 agent 那里（解释 "run tests" → `go test ./...`），enforcement 必须在 OS（覆盖所有路径）。
- **设计要求 1**：policy DSL 要足够高层让 agent 可靠生成，又要足够具体可编译为确定性内核检查；**81%** 项目含跨事件 / 数据流策略，需跟踪状态。
- **设计要求 2**：agent 不能削弱高 authority 安全约束或影响其他 agent 的策略。

### 2.3 ActPlane 架构（§3, Figure 8）

- **Project-level policies**：每个仓库内的策略（Worker Agent 视角）。
- **Userspace DSL**：agent 用 `rule tests-before-commit: kill exec "git" "commit" if AGENT unless after exec "go" "test" exits 0` 这种语法声明策略。
- **Compiler**：把 DSL 编译到 eBPF。
- **IFC Policy Engine**：在内核中执行。
- **Semantic feedback**：违反时返回结构化反馈（"blocked: commit without tests; run npm test first"），不是 EPERM。
- **Authority checker**：policy domain 隔离，子进程绑定 authority。

### 2.4 DSL 与 IFC（§3.2–3.4）

- DSL 示例（Figure 1）：
  - `rule tests-before-commit: kill exec "git" "commit" if AGENT unless after exec "go" "test" exits 0`
  - `rule no-delete-data: block unlink "/data/**" if AGENT`
- 用 **eBPF + IFC**：标签附加到 process / file / socket 状态；`block` / `kill` 拒绝违规；`notify` 引导 agent 行为。
- **跨进程 / 文件 / 网络的数据流追踪** 支持 `read ".env" cannot reach socket()` 这类约束。

### 2.5 实证研究（§2.2）

- 数据集：64 个 GitHub 仓库，含 CLAUDE.md / AGENTS.md（median 20K stars，84 instruction files，2116 statements）。
- 关键发现：
  - **64%** 语句是 policy（70.1% 仓库以 policy 为主）。
  - **83%** 涉及系统动作（system-observable）；其中 17% semantic-only、38% content、29% per-event、16% cross-event。
  - **81%** 仓库至少含一条 cross-event policy；43% 覆盖全部 4 个 enforcement 等级。
  - **73.6%** 系统级 policy 非 self-contained（需 project 或 task context 解析）；cross-event policy 95% context-dependent。

### 2.6 评测（§5）

- Decision-compliance benchmark：ActPlane 解决违规 **2.0–3.2×** 多于 prompt-filter / tool-regex / FIDES（tool-level IFC）/ 无反馈 kernel IFC。
- Personal-assistant 安全 benchmark（361 任务）：**ActPlane 阻止 74%** baseline-unsafe behaviors（加载 agent 生成的安全策略为 higher-authority 规则）。
- 开销：end-to-end 1.9%、kernel build 场景最高 8.4%。

> 锚点：§1 Introduction; §2.2 Empirical Study（Figure 2-7）; §3.1-3.4 Design（Figure 8）; §5 Evaluation。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| Decision-compliance benchmark 解决违规数 | **2.0–3.2×** 多于 prompt-filter / tool-regex / FIDES / 无反馈 kernel IFC | §5, Abstract |
| Personal-assistant 安全（361 任务） | **74%** unsafe behaviors 被阻止 | §5, Abstract |
| End-to-end overhead | 1.9%（Agent workload） | §5, Abstract |
| Kernel build overhead | 8.4% | §5, Abstract |
| 仓库实证：policy 占总语句比例 | **64%**（statements），70.1%（仓库） | §2.2 |
| 系统级 policy 中 cross-event 比例 | **16%**；81% 仓库至少 1 条 | §2.2 |
| 系统级 policy 中 context-dependent | **73.6%**（cross-event 95% context-dependent） | §2.2 |
| IFC 引擎实现 | 基于 eBPF，支持 process / file / socket 标签传播 | §3.4 |

> 锚点：§2.2 Empirical Study (Figure 2 / 3 / 4 / 5 / 6 / 7); §5 Evaluation; Abstract。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2606.25189 |
| 官方代码 | https://github.com/eunomia-bpf/ActPlane |
| 工具基础 | eBPF / bpftool / Eunomia-bpf 框架 |
| 关联工作 | Claude Code、Codex（被作为典型 harness 引用）；FIDES（tool-level IFC）；OS 沙箱（chroot、namespace、Landlock） |
| 引用指令文件 | CLAUDE.md、AGENTS.md（仓库内 2116 statement 数据集） |
| 关联论文 | 与 07-LLM-as-Code（程序化控制流）、02-AIOS（OS 级 Agent 调度）、10-Ben_Sghaier（harness 演化）共同构成 Agent Harness 系列 |

> 锚点：§1 Introduction; §2.2 Empirical Study（数据集来源 GitHub 64 repos）；§3 Design（Figure 8）；§5 Evaluation。

## 5. 一句话索引（给 Agent 用）

> 当设计 **Agent Harness 安全 / 合规策略执行层** 时，ActPlane 是目前工程完整度最高的参考：**eBPF + IFC 在内核强制执行 + DSL 让 agent 自声明策略 + semantic feedback（而非 EPERM）+ policy domain authority 分级**——2.0–3.2× 解决违规、74% 阻止 unsafe behavior、1.9–8.4% 开销是说服力数字；最重要的是 16% 跨事件 policy 才是 harness 设计盲点（tool-call 拦截完全看不到），这是 07-LLM-as-Code 的"程序掌控控制流"无法覆盖的另一面——两者合用才能形成完整的 Agent Harness 防护。