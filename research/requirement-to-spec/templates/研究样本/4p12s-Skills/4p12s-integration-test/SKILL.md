---
name: "4p12s-integration-test"
display_name: "4p12s-integration-test"
description: "|"
version: "1.0.1"
---

# 集成测试

**Announce at start:** "I'm using the 4p12s-integration-test skill to run integration verification."

## 概述

运行真实 API 和服务间集成验证。在内部完成运行、归因、修复、重跑的完整循环。

## 双模运行

### 编排模式

路径包必须包含：

```yaml
repo_root:
delivery_dir:
state_path:
project_entry_path:
verification_plan_path:
verification_result_path:
user_stories_path:
prd_path:
output_paths:
allowed_write_paths:    # verification-result.md、修复所需的产品代码和测试代码
```

### 独立模式

自动发现：
- 当前目录或指定目录下的 `verification-plan.md`、`verification-result.md`
- 项目入口文档（`.gientech/AGENTS.md`、`AGENTS.md`）
- 项目测试配置和集成测试文件
- 输出路径：与上游产物同目录的 `verification-result.md`

独立模式从 `verification-plan.md` 中筛选集成测试类型的 TC 执行。

## 执行流程

1. 读取路径包中的必要文件
2. 从 `verification-plan.md` 中筛选集成测试类型的 TC
3. 优先读取 `.gientech/AGENTS.md`，不存在时读取 `project_entry_path`
4. 从项目入口文档发现集成测试执行命令、服务启动方式、端口/地址和健康检查方式

### STEP-01: 服务启动

**强规则：必须执行；缺少任一证据都不得返回 `passed`。**

- 从 `verification-plan.md` 提取当前集成 TC 所需真实服务类型、测试数据要求、禁用 Mock 规则和真实接口断言
- 从项目入口文档发现后端/API `cwd`、启动或连接命令、地址/端口、健康检查
- 如果无法唯一确定命令、端口、健康检查或测试数据准备方式，返回 `blocked`
- 实际执行启动命令，在后台启动后端服务
- 记录最小执行证据
- 执行健康检查
- 记录健康检查结果

### STEP-02: 测试数据准备

- 按 `verification-plan.md` 中的测试数据要求准备初始数据
- 记录数据准备的最小执行证据
- 如果无测试数据要求，说明不适用原因

### STEP-03: 运行集成测试

- 执行从项目入口文档发现的集成测试命令
- 逐项执行每个集成测试 TC
- 记录每个 TC 的最小执行证据

### 修复循环

如果集成测试失败：

1. 对每个失败 TC，归因失败原因（产品代码、测试代码、环境、数据、配置）
2. 渐进式披露：修复代码时，按失败 TC → `user-stories.md` → `prd.md` 的路径，只读取关联条目
3. 修复对应的产品代码或测试代码
4. 重跑失败 TC + 受影响的回归项
5. 重复直到全部通过或达到 5 轮上限
6. 超过 5 轮后返回 `blocked|failed`

## 输出文件

追加写入 `verification-result.md` 的集成部分：

```markdown
## 集成验证结果

### 执行摘要

- 执行时间：
- 环境：
- 后端服务地址：
- 后端启动命令：
- 健康检查结果：
- 验证结论：验证通过 / 验证失败 / 验证阻断
- Git 阻断项：无 / 有

### 最小执行证据规则

- 只记录发现来源、执行动作、命令摘要、结果、关键输出摘要
- 命令摘要格式：`<cwd> <command>`
- 不记录完整 stdout/stderr
- 不能只写"完成""已执行""通过"

### 需求追踪审计

| 源需求 ID | 验证用例 | 自动化测试文件 | 验证结果 |
| --- | --- | --- | --- |

### 服务启动证据

- 发现来源：
- 启动动作：
- 命令摘要：`<cwd> <command>`
- 启动结果：
- 关键输出摘要：
- 健康检查摘要：

### 验证命令与结果

| 发现来源 | 动作 | 命令摘要 | 环境/数据 | 结果 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- |

### 用例执行结果

| 用例 ID | 关联需求 ID | 类型 | 是否提交前必须执行 | 自动化测试文件 | 命令摘要 | 结果 | 关键输出摘要 |
| --- | --- | --- | --- | --- | --- | --- | --- |

### 失败与修复记录

| 项目 | 关联需求 ID | 归因 | 处理动作 | 当前结果 |
| --- | --- | --- | --- | --- |
```

## 强规则

- **没有服务启动证据不得返回 `passed`**
- **没有健康检查结果不得返回 `passed`**
- **"测试代码已创建"、"文件存在"、"CI 稍后运行"、纯编译通过不是集成测试通过证据**
- **每个集成测试 TC 必须有真实执行记录**
- **只有 STEP-01 到 STEP-03 都满足完成条件并有证据，才允许返回 `passed`**

## STEP_RESULT（编排模式）

```yaml
step: verification_integration
status: running | passed | blocked | failed
output_files:
  - <delivery_dir>/verification-result.md
required_inputs_checked:
  - <delivery_dir>/delivery-state.md
  - <delivery_dir>/verification-plan.md
  - <repo_root>/.gientech/AGENTS.md（存在时必须读取）
  - <project_entry_path>
commands_run:
gate_evidence:
blocking_reason:
next_action:
```

## 边界

- 不运行 E2E 测试
- 不提交、不推送、不触发发布
- 不更新 `delivery-state.md`（编排模式下）
- 不报告流程终点状态
