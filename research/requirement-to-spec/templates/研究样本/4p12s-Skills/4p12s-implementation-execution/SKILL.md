---
name: "4p12s-implementation-execution"
display_name: "4p12s-implementation-execution"
description: "|"
version: "1.0.1"
---

# 开发任务执行

**Announce at start:** "I'm using the 4p12s-implementation-execution skill to execute the development task."

## 概述

执行主流程选定的一个开发 Task。按 TDD 步骤逐项完成：写失败测试 → 红灯验证 → 实现 → 绿灯验证。

本阶段只做开发任务。不写 E2E 测试，不运行真实集成测试，不启动完整服务做 E2E，不提交、推送或发布。

## 双模运行

### 编排模式

路径包必须包含：

```yaml
repo_root:
delivery_dir:
state_path:
project_entry_path:
tasks_index_path:
selected_task_path:     # 当前选定的 TASK-xxx.md
current_task:           # 当前 Task ID
dependency_task_paths:  # 已 passed 的依赖 Task 文件路径列表
requirements_register_path:
prd_path:
user_stories_path:
design_path:
output_paths:
allowed_write_paths:    # 当前 Task 文件、该 Task 计划中的产品代码和测试代码
```

### 独立模式

自动发现：
- 当前目录或指定目录下的 `tasks/index.md` 和 `tasks/TASK-xxx.md`
- 上游产物（requirements-register.md、prd.md、user-stories.md、design.md）
- 项目入口文档和相关源码

独立模式按 `tasks/index.md` 中的顺序选择第一个未完成的 Task 执行，或用户指定 Task ID。

## 执行边界

只允许：
- 执行选定的一个 Task
- 修改该 Task 文件计划中的产品代码和测试代码
- 按 TDD 写失败测试、运行红灯、实现、运行绿灯
- 更新该 `TASK-xxx.md` 的 checkbox、证据和结果记录
- 返回 STEP_RESULT

不得：
- 执行其他 Task
- 改写 `tasks/index.md`
- 更新 `delivery-state.md`
- 写 `verification-result.md`
- 写 E2E 测试代码
- 运行最终集成测试或最终 E2E
- 提交、推送、发布
- 发现计划不合适时擅自重拆任务

## 步骤状态

Task 文件中的步骤状态只使用 Markdown checkbox：

```markdown
- [ ] Step N: <步骤名>
- [x] Step N: <步骤名>
```

执行规则：
- 每完成一个步骤，必须立即把该 Step 从 `- [ ]` 改为 `- [x]`，并写入证据
- 每次更新 checkbox 后，必须重新读取 Task 文件确认落盘
- 返回 `passed` 前，必须最后读取 Task 文件确认没有 `- [ ] Step`
- 只要还有任何 TDD 步骤不是 `- [x]`，不得返回 `passed`

## 执行流程

```text
读取 tasks/index.md
-> 读取 selected TASK-xxx.md
-> 读取 dependency_task_paths 中每个依赖 Task 的 ## 结果记录
-> 校验 Task 与目录清单一致
-> 审查 TDD 步骤和文件计划是否完整
-> 读取当前 Task 直接相关代码和测试
-> Step 1 编写失败测试
-> 将 Step 1 checkbox 改为 - [x]，写入证据，并重新读取确认落盘
-> Step 2 运行红灯验证，确认失败原因指向目标能力缺失
-> 将 Step 2 checkbox 改为 - [x]，写入证据，并重新读取确认落盘
-> Step 3 实现最小产品代码
-> 将 Step 3 checkbox 改为 - [x]，写入证据，并重新读取确认落盘
-> Step 4 运行绿灯验证
-> 将 Step 4 checkbox 改为 - [x]，写入证据，并重新读取确认落盘
-> 必要时运行 lint/typecheck/build 等检查
-> 更新 ## 结果记录
-> 最后一次重新读取 Task 文件，自检所有 checkbox
-> 返回 STEP_RESULT
```

不要跳过红灯。编译、lint、类型检查不能作为红灯验证。

## TDD 要求

必须完成：
1. 编写失败测试
2. 运行红灯命令，确认失败原因指向目标能力缺失
3. 实现最小产品代码和必要支撑代码
4. 运行绿灯命令，确认通过

证据要求：
- `tdd_red_result` 记录 `cwd`、`command`、`exit_code`、`result`、`output_summary`、`expected_failure_reason`
- `tdd_green_result` 记录 `cwd`、`command`、`exit_code`、`result`、`output_summary`
- `commands_run` 中的每条命令都有结构化证据
- `changed_files` 和 `tests_added_or_changed` 中列出的路径必须存在

## 结果记录

必须更新选定 Task 的 `## 结果记录`：

```yaml
changed_files:
tests_added_or_changed:
commands_run:
  - cwd:
    command:
    exit_code:
    result:
    output_summary:
tdd_red_result:
tdd_green_result:
additional_checks:
requirement_ids_covered:
user_stories_covered:
remaining_risks:
```

命令证据必须结构化。不能只写 `PASS`、`FAIL`、`通过`、`失败`。

## 通过条件

只有同时满足以下条件，才能返回 `passed`：

- 当前 Task 的所有 TDD checkbox 都是 `- [x]`
- 已重新读取确认没有 `- [ ] Step`
- 每个完成步骤都有证据
- 红灯验证真实执行且失败原因指向目标能力缺失
- 绿灯验证真实执行且通过
- 结果记录完整
- 当前 Task 的关联需求和用户故事在结果记录中可追踪

## STEP_RESULT（编排模式）

```yaml
step: implementation
status: running | passed | blocked | failed
output_files:
  - <selected_task_path>
required_inputs_checked:
  - <delivery_dir>/tasks/index.md
  - <selected_task_path>
  - <delivery_dir>/requirements-register.md
  - <delivery_dir>/prd.md
  - <delivery_dir>/user-stories.md
  - <delivery_dir>/design.md
  - <project_entry_path>
commands_run:
gate_evidence:
  checkbox_audit:
    - step:
      status: "- [x]"
      evidence:
blocking_reason:
next_action:
```

`gate_evidence.checkbox_audit` 必须列出当前 Task 的每个 TDD Step，且每项 status 都必须是 `- [x]`。

## 边界

- 不执行其他 Task
- 不写 E2E 测试
- 不运行集成测试或 E2E
- 不提交、不推送、不发布
- 不更新 `delivery-state.md`（编排模式下）
