# 论文摘要：Agentless（无 Agent 的 SWE 流水线）

> **原论文标题**：Agentless: Demystifying LLM-based Software Engineering Agents
> **完整 PDF 文件名**：`15-Xia-Agentless.pdf`
> 作者 / 年份：Chunqiu Steven Xia et al.，2024
> 摘要类型：Agent 设计参考 + 流程化方案
> 生成日期：2026-08-12

## 1. 适用场景

- 设计 **仓库级 SWE 流水线** 时，需要在"自由 Agent 探索" vs "固定三阶段流水线"之间做权衡——本文证明后者在 SWE-bench 上能匹敌甚至超越前者。
- 想要 **可复现、低成本** 的 SWE 评测流水线：避免自由 Agent 带来的运行方差、token 爆炸、循环陷阱。
- 需要 **明确定位 + 最小补丁** 的工作流（适合 code review、安全补丁场景）。
- 给团队落地 **CI-bot 类自动修复工具** 时，本文是参考实现。
- 在 SWE-bench（论文 12）/ SWE-bench Lite 上做 **可比 baseline**。

> 锚点：Abstract；§1 Introduction；§2 Method；§3 Evaluation。

## 2. 主要观点与方案

### 2.1 核心观点

- **"Agentless"并不意味着没有 LLM，而是反对给 LLM 完全自由的 Agent 循环**。把任务拆成几个固定阶段，每阶段用最小的 LLM 调用，**总体表现与 SWE-agent 持平或更好**。
- 反对过度复杂化：自由 Agent 容易陷入循环、过度检索、产生膨胀 patch。

### 2.2 三阶段流水线

1. **Localization（定位）**
   - **Step 1：File-level localization**：让 LLM 在仓库文件树中挑出可能需要修改的文件列表。
   - **Step 2：类/函数/行级 localization**：用 BM25 / embedding 在挑出的文件内做细粒度定位，输出函数/行号列表。
   - 输出"高置信度位置"的集合作为下一阶段的输入。

2. **Repair（修复）**
   - **Step 3：让 LLM 生成 Search/Replace 风格的 diff**（而非完整文件重写）。Search/Replace diff 必须**精确匹配**待替换内容，无法匹配则跳过。
   - 多样性采样：并行生成多个 candidate patch（不同 temperature / 不同 prompt），挑选通过测试的版本。

3. **Validation（验证）**
   - **Step 4：自动跑测试套件**，按 SWE-bench 的 fail-to-pass + pass-to-pass 协议判定。
   - 若所有 candidate 都失败，则 fallback 到更激进的 prompt 或更多候选。

### 2.3 与 SWE-agent 的关键差异

| 维度 | SWE-agent | Agentless |
|---|---|---|
| 主循环 | 自由 ReAct（多次 bash/edit） | 三阶段固定流水线 |
| 文件编辑 | `str_replace_editor` 全文串替换 | Search/Replace diff（精确匹配） |
| 检索 | LM 自驱 + ripgrep | BM25/embedding + 结构化输出 |
| 可复现性 | 较低（不同 run 路径不同） | 较高（流水线确定） |
| Token 消耗 | 通常较高 | 通常显著较低 |
| SWE-bench 表现 | GPT-4 ≈ 12.5% | 同等/略高（论文报告） |

### 2.4 关键设计取舍

- **Search/Replace diff 而非 unified diff**：避免 LM 输出缩进错误、上下文行错位等常见 patch 错误。
- **多采样 + 自动筛选**：通过 candidate 数量弥补 LLM 单次回答的不确定性，**不靠增加推理深度**。
- **可拒绝**：若 Search 串无法唯一匹配，LM 应放弃而非猜——这是 **可控性优先** 的工程取舍。

## 3. 达到的效果

| 度量 / 现象 | 数值 / 结论 | 锚点 |
|---|---|---|
| SWE-bench resolved rate | 与 GPT-4 + SWE-agent 持平或更高（论文报告） | §3 |
| Token 消耗 / 运行时间 | 显著低于 SWE-agent（多采样策略仍可控制总开销） | §3 |
| 可复现性 | 三阶段流水线确定性强，方差小 | §2 |
| 失败模式 | 多为 Search/Replace 不匹配；可控可观察 | §3 |
| 多采样收益 | candidate 数从 1 提升到 N 通常带来单调收益 | §2.2 |
| 与 RepoGraph 兼容 | localization 阶段可换用图检索作为 oracle | 关联论文 13 |

> 锚点：§2 Method；三阶段细节；§3 Evaluation。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | `15-Xia-Agentless.pdf`（arXiv / 后续 venue） |
| 代码仓库 | `OpenAutoCoder/Agentless`（公开） |
| 评测基线 | SWE-bench / SWE-bench Lite（论文 12）、SWE-bench Verified |
| 关联工作 | SWE-agent（论文 14，自由 Agent）、RepoGraph（论文 13，图增强定位）、AutoCodeRover |
| 关键工具 | BM25 / embedding retrieval、Search/Replace diff 协议、pytest harness |

> 锚点：§2 Method；§3 Evaluation；References。

## 5. 一句话索引（给 Agent 用）

> 设计仓库级自动修复流水线时，**优先采用 Agentless 风格的三阶段（Localization → Search/Replace Repair → Validation）+ 多采样 + 可拒绝机制**：固定流水线比自由 Agent 更可控、更便宜、且在 SWE-bench 上能持平或更好——这是给 Agent 做"工程化版本"的事实模板。