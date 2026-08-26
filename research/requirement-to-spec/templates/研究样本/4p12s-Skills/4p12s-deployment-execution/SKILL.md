---
name: "4p12s-deployment-execution"
display_name: "4p12s-deployment-execution"
description: "|"
version: "1.0.1"
---

# 发布触发

**Announce at start:** "I'm using the 4p12s-deployment-execution skill to trigger the release."

## 概述

在 Git 推送成功后触发发布 API 或发布脚本，并将返回状态写入 `deploy-log.md##Release Trigger`。

只产出固定结论：请求已受理、请求失败、凭证缺失、入口缺失、结果无法判断。

Pull Request / Merge Request 创建、MR ready、等待合并都不是发布触发。

## 双模运行

### 编排模式

路径包必须包含：

```yaml
repo_root:
delivery_dir:
state_path:
project_entry_path:
deploy_log_path:        # 当前交付目录 deploy-log.md
release_notes_path:     # 发布说明（如有）
output_paths:
allowed_write_paths:    # 仅 deploy-log.md##Release Trigger
```

### 独立模式

自动发现：
- 当前 Git 仓库根目录
- `deploy-log.md` 中的 `## Git Push` 章节
- 项目入口文档和发布说明
- 发布入口：`scripts/deploy.sh`、`package.json` 发布命令、Makefile、CI 配置

## 发布入口发现

按以下优先级确定发布方式：

1. 项目根目录 `scripts/deploy.sh`
2. 项目入口文档指定的发布脚本、命令、CI/CD 平台或发布说明
3. `package.json`、Makefile、CI 配置或仓库脚本中明确命名的发布命令
4. 用户在当前交付中显式指定的发布方式

如果无法确定发布入口、发布环境、目标分支或凭证来源，返回 `blocked`，不得猜测。

## 凭证规则

- 不得在 Skill 指令、交付文档或代码中写入 CI/CD webhook URL、api-token、账号密码或长期凭证
- 发布凭证只能来自项目认可的位置（环境变量、凭证管理器、CI/CD 平台配置、项目入口文档）
- 如果发布命令需要凭证但当前环境不可用，返回 `blocked`

## 执行流程

1. 读取 `delivery-state.md`、`deploy-log.md`、项目入口文档和发布说明
2. 从 Git Push 证据中提取提交哈希、目标分支和远端信息
3. 发现发布入口，优先使用 `scripts/deploy.sh`
4. 执行发布命令或调用发布 API
5. 记录命令、环境、提交哈希、目标分支、HTTP/进程状态和响应摘要
6. 写入 `deploy-log.md##Release Trigger`
7. 返回 `STEP_RESULT`

不得创建 MR/PR，不得等待 MR/PR 合并。

## deploy-log.md##Release Trigger

```markdown
## Release Trigger

- trigger_time:
- commit_hash:
- target_branch:
- environment:
- deploy_entry:
- deploy_command:
- exit_code:
- credential_source:
- response_summary:
- result:

| 项目 | API/脚本 | HTTP/进程状态 | 响应摘要 | 结论 |
| --- | --- | --- | --- | --- |
```

结论只使用固定枚举：
- 请求已受理
- 请求失败
- 凭证缺失
- 入口缺失
- 结果无法判断

## STEP_RESULT（编排模式）

```yaml
step: release_trigger
status: running | passed | blocked | failed
output_files:
  - <delivery_dir>/deploy-log.md
required_inputs_checked:
  - <delivery_dir>/delivery-state.md
  - <delivery_dir>/deploy-log.md##Git Push
  - <project_entry_path>
commands_run:
gate_evidence:
blocking_reason:
next_action:
```

证据解释：
- 发布 API 返回 HTTP 成功状态，或发布脚本退出码为 0 且响应表明请求已受理：`gate_evidence` 记录请求已受理证据
- API 请求失败、脚本退出码非 0：`gate_evidence` 记录失败响应
- 凭证缺失、发布入口缺失：`blocking_reason` 记录缺失条件
- MR/PR 创建、MR/PR ready、等待合并：必须返回 `blocked`
- 只记录"代码已提交""代码已推送"不能作为发布触发证据

## 边界

- 不更新 `delivery-state.md`（编排模式下）
- 不决定 workflow terminal state
- 不改写 `deploy-log.md##Git Push`
- 不创建、打开、准备或等待 Pull Request / Merge Request
