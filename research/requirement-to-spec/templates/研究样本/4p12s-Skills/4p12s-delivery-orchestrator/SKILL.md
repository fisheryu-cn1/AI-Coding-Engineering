---
name: "4p12s-delivery-orchestrator"
display_name: "4p12s-delivery-orchestrator"
description: "|"
version: "1.0.1"
---

# 端到端交付主控流程

**Announce at start:** "I'm using the 4p12s-delivery-orchestrator skill to run the end-to-end delivery workflow."

## 概述

本 Skill 是端到端交付系统的**调度器 + 裁判**。它不亲自执行任何 Step 的具体工作，而是：

- 维护唯一状态账本 `delivery-state.md`
- 按 11 步固定顺序和门禁条件推进
- 构造路径包、调用子 Skill、接收 `STEP_RESULT`
- 复核产物结构、决定推进还是阻断
- 触发回退时决定回退到哪个 Step
- 自动推进，不等用户确认（除 requirements 的阻断性澄清）

## 固定流程

```text
requirements
-> prd
-> user_stories
-> design
-> verification_plan
-> tasks
-> implementation
-> verification_integration
-> verification_e2e
-> git_push
-> release_trigger
```

唯一完成条件：

```text
workflow_status=release_triggered
release_trigger=passed
deploy-log.md##Release Trigger 有真实发布 API 或发布脚本调用结果
```

PRD、设计、任务完成、验证通过、Git push 都不是终点。

## 子 Skill 映射

| Step | 子 Skill | 产物 |
| --- | --- | --- |
| requirements | `4p12s-requirements` | `requirements-register.md` |
| prd | `4p12s-prd` | `prd.md` |
| user_stories | `4p12s-user-stories` | `user-stories.md` |
| design | `4p12s-technical-design` | `design.md` |
| verification_plan | `4p12s-verification-plan` | `verification-plan.md` |
| tasks | `4p12s-implementation-tasks` | `tasks/` |
| implementation | `4p12s-implementation-execution`（每个 Task 单独调用一次） | `tasks/TASK-xxx.md` 证据 |
| verification_integration | `4p12s-integration-test` | `verification-result.md` 集成部分 |
| verification_e2e | `4p12s-e2e-test` | `verification-result.md` E2E 部分 |
| git_push | `4p12s-git-push` | `deploy-log.md##Git Push` |
| release_trigger | `4p12s-deployment-execution` | `deploy-log.md##Release Trigger` |

## 路径包构造

调用子 Skill 时，只注入可执行路径包，不注入上游产物全文或源码全文。子 Skill 根据路径包自行读取所需内容。

```yaml
workflow_root:          # 端到端工作流目录路径
delivery_dir:           # 当前交付目录路径
repo_root:              # 当前代码仓库根路径
project_entry_path:     # 项目入口文档路径，优先 .gientech/AGENTS.md
current_step:           # 当前 Step 名称
current_task:           # 仅 implementation 阶段填写
selected_task_path:     # 仅 implementation 阶段填写
dependency_task_paths:  # 仅 implementation 阶段填写，已 passed 的依赖 Task 文件路径列表
state_path:             # delivery-state.md 路径
instruction_path:       # 当前子 Skill 路径
input_paths:            # 当前子 Skill 必须读取的上游产物路径
output_paths:           # 当前子 Skill 必须创建或更新的产物路径
allowed_write_paths:    # 当前子 Skill 允许写入的路径边界
required_previous_steps: # 已 passed 的前置 Step 列表
resume_policy:          # 异常恢复时应优先从哪些产物重建现场
```

## 交付目录

```text
deliveries/<需求名>/
├── delivery-state.md
├── requirements-register.md
├── prd.md
├── user-stories.md
├── design.md
├── verification-plan.md
├── tasks/
│   ├── index.md
│   ├── TASK-001.md
│   └── TASK-xxx.md
├── verification-result.md
└── deploy-log.md
```

新建交付目录时，必须先创建并确认 `delivery-state.md`，再调用任何子 Skill。

## 状态账本

`delivery-state.md` 是唯一状态账本。每次推进前读取它，每次 Step 或 Task 状态变化后重写它。

初始结构：

```markdown
# 交付状态

- workflow: end_to_end_delivery
- delivery_name:
- workflow_status: running
- current_step: requirements
- current_task:
- blocking_reason:
- next_action: 调用 requirements Skill 生成 requirements-register.md
- updated_at:

## Step Checklist

| Step | Artifact | Status | Evidence |
| --- | --- | --- | --- |
| requirements | requirements-register.md | running | |
| prd | prd.md | pending | |
| user_stories | user-stories.md | pending | |
| design | design.md | pending | |
| verification_plan | verification-plan.md | pending | |
| tasks | tasks/ | pending | |
| implementation | tasks/ | pending | |
| verification_integration | verification-result.md（集成部分） | pending | |
| verification_e2e | verification-result.md（E2E 部分） | pending | |
| git_push | deploy-log.md##Git Push | pending | |
| release_trigger | deploy-log.md##Release Trigger | pending | |

## Task Checklist

| Task ID | Task File | Status | Linked Story/Acceptance | Evidence |
| --- | --- | --- | --- | --- |
```

合法状态：

```text
Step/Task: pending | running | passed | blocked | failed
workflow_status: running | blocked | failed | release_triggered
```

不得使用 `todo`、`done`、`complete`、`success` 等状态别名。

## 执行事务

每个 Step 按同一事务执行：

```text
读取 delivery-state.md
-> 审计前置 Step 是否 passed
-> 审计当前 Step 子 Skill 和路径包
-> 将当前 Step 写为 running
-> 重新读取 delivery-state.md 确认落盘
-> 构造路径包并调用对应子 Skill
-> 等待 STEP_RESULT 和产物落盘
-> 复核产物
-> 重写 delivery-state.md
-> 若 passed，不得停止，必须在同一轮中继续下一 Step
```

## 自动推进规则

所有 Step 默认自动推进，不等待用户确认。

**硬规则：流程只能在以下三个条件之一时停止：**

1. `workflow_status=release_triggered`
2. 某 Step 返回 `blocked`（外部依赖类阻断）
3. 某 Step 返回 `failed`（达最大修复轮次）

除 `requirements` 阶段的阻断性澄清外，状态汇报不是用户确认点。以下表达只能写入状态账本或日志，不能作为暂停理由：

- 已进入某个 Step
- 当前 Step 已 passed，准备进入下一 Step
- 当前任务是 `TASK-xxx`
- 下一步将调用某个子 Skill
- 下一步将执行某命令

## implementation 执行模型

`implementation` Step 按 `tasks/index.md##Task 目录清单` 从上到下逐个执行：

```text
读取 delivery-state.md
-> 读取 tasks/index.md 和所有 TASK-xxx.md
-> 检查 Task 顺序和依赖方向
-> 选择第一个未 passed Task
-> 收集该 Task 的已 passed 依赖 Task 文件路径
-> 将 current_step=implementation、current_task=<Task ID>、该 Task 状态写为 running
-> 重新读取 delivery-state.md 确认落盘
-> 调用 4p12s-implementation-execution Skill 执行该 Task
-> 将该 Task 写为 passed、blocked 或 failed
-> 若还有未 passed Task，继续下一个
-> 全部 Task passed 后，implementation=passed
```

Task 通过条件：

- `STEP_RESULT.status=passed` 明确声明所有 TDD checkbox 已落盘为 `- [x]`
- `gate_evidence.checkbox_audit` 覆盖每个 TDD Step，每项 status 都是 `- [x]`
- 每个完成步骤都有证据
- 有真实红灯验证，失败原因指向目标能力缺失
- 有真实绿灯验证，命令通过
- 结果记录中的文件和命令证据可复核

## 验证与修复

`verification_integration` 负责真实集成验证。

`verification_e2e` 负责完整 E2E 阶段。每个验证 Step 最多 5 轮修复。超过后返回 `blocked` 或 `failed`。

## 回退规则

当前 Step 发现上游产物无法支撑工作时，回退到最早需要修正的 Step：

- 业务范围、验收场景、Given/When/Then 不清：回退 `user_stories` 或 `prd`
- 模块、入口、接口契约、数据流、文件归属不清：回退 `design`
- 验证用例、目标测试文件/目录、真实服务类型、测试数据、禁用 Mock 规则或真实接口断言不清：回退 `verification_plan`
- 执行阶段无法从项目入口文档唯一发现命令、端口或健康检查：当前验证 Step 返回 `blocked`
- Task 文件结构、顺序、依赖、步骤或证据模板不合格：回退 `tasks`

回退必须写回 `delivery-state.md`，把 `current_step` 和 `next_action` 指向需要重新执行的子 Skill。

## 现场重建

每次执行 Step 或 Task 前都从文件系统重建现场：

1. 读取本 Skill 的流程规则
2. 读取 `delivery-state.md`
3. 校验当前 Step 路径包中的 `input_paths`、`output_paths` 和 `allowed_write_paths`
4. 只在复核门禁需要时读取当前 Step 的关键产物结构
5. 若状态账本和文件产物冲突，以文件产物为准

不得凭上下文摘要或旧 `next_action` 继续推进。

## 安全控制

每次子 Skill 返回后，主控必须复核：

- 产物文件是否按预期创建或更新
- 产物结构是否符合对应 Step 的质量门禁
- 是否存在越界写入（子 Skill 写了 `allowed_write_paths` 之外的文件）
- `STEP_RESULT.required_inputs_checked` 是否覆盖了路径包中要求的所有输入
- 是否存在安全凭证泄露

违反任一项，不得推进。

## STEP_RESULT 契约

所有子 Skill 必须返回：

```yaml
step:
status: running | passed | blocked | failed
output_files:
required_inputs_checked:
commands_run:
gate_evidence:
blocking_reason:
next_action:
```

`STEP_RESULT.status=passed` 只表示该子 Skill 的产物或单个 Task 完成。是否推进，由主控复核产物后决定。

## 禁止事项

- 子 Skill 更新 `delivery-state.md`
- 主控跳过未 passed 的前置 Step
- 主控跳过目录中更早未 passed 的 Task 去执行后面的 Task
- Task 阶段运行最终真实集成或最终 E2E
- E2E 阶段没有根据 `verification-plan.md` 编写或补齐目标测试代码
- Git push 后把流程当作完成
- 发布触发没有真实 API 或脚本调用证据却标记完成

## 项目上下文渐进式注入

主流程在构建子 Skill 路径包前，应先探测项目仓库中是否存在编码规范、开发命令速查、测试策略等约定文档（如 `**/编码指引.md`、`**/开发命令速查.md`、`**/测试策略.md` 或同类语义文件），存在时将对应文件的关键内容注入路径包，不存在则跳过。子 Skill 不得因缺失此类文件而阻断。

## 启动流程

当用户触发此 Skill 时：

1. 确认项目路径和业务需求输入
2. 创建交付目录 `deliveries/<需求名>/`
3. 初始化 `delivery-state.md`
4. 按 Step 顺序开始执行，自动推进
5. 直到 `release_triggered`、`blocked` 或 `failed` 才停止
