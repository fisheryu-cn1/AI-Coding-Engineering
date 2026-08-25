# pi-mono 架构与定制机制调研报告

> 状态：已完成初稿（2026-08-17）

调研对象：本地仓库 `d:\users\yu\documents\coding\pi`（GitHub: earendil-works/pi-mono），只读引用。文中路径均相对 pi 仓库根。

---

## 1. 这个仓库是什么？

**问题**：pi-mono 的整体定位与包结构是什么？

**结论**：pi 是一个"自我可扩展的极简编码代理框架"（self extensible coding agent），口号是 "Pi Agent Harness"。核心设计：把传统编码代理内置的功能（子代理、plan mode、权限弹窗、MCP、todo）全部外置为可选扩展，保持核心最小化。来源：`README.md`、`packages/coding-agent/README.md` 的 Philosophy 一节。

### packages/ 结构（`README.md` All Packages 表 + 各包 README）

```
packages/
├── ai/              @earendil-works/pi-ai          统一多厂商 LLM API（OpenAI/Anthropic/Google/Bedrock 等 30+ 提供商）
├── agent/           @earendil-works/pi-agent-core  有状态代理运行时：agent loop、工具执行、事件流
├── coding-agent/    @earendil-works/pi-coding-agent 交互式编码代理 CLI（即 `pi` 命令，核心调研对象）
├── tui/             @earendil-works/pi-tui         差分渲染终端 UI 库（CSI 2026 同步输出、组件化）
├── protocol/        通信协议（CBOR、codec、framing、schemas）
├── client/ server/  RPC 客户端/服务端封装
├── evals/           评测框架
├── telemetry/       厂商中立遥测契约与 schema
└── session-backends/sqlite-node  SQLite 会话后端（独立包，核心包不捆绑原生依赖）
```

各包职责补充：
- `packages/agent/README.md`：消息流为 `AgentMessage[] → transformContext() → convertToLlm() → Message[] → LLM`。AgentMessage 支持通过 declaration merging 扩展自定义消息类型（`custom` role），只在调用 LLM 边界处转换/过滤。
- `packages/agent/src/agent-loop.ts`：导出 `agentLoop()` / `agentLoopContinue()`，事件序列为 `agent_start → turn_start → message_start/end → (流式 assistant) → 工具执行 → turn_end → agent_end`（`runLoop`/`streamAssistantResponse`/`executeToolCalls`）。

---

## 2. coding-agent 核心架构

**问题**：`pi` 的运行时由哪些部分组成？

**结论**：`packages/coding-agent/src/` 分层清晰：

```
src/
├── cli.ts / main.ts        入口
├── cli/                    参数解析、认证、会话选择、项目信任
├── core/                   核心：agent-session、session-manager、system-prompt、
│                           skills、prompt-templates、slash-commands、extensions/、tools/、
│                           compaction/、model-registry、sdk.ts、settings-manager…
├── modes/                  四种运行模式：interactive/、print-mode、json-event、rpc
├── extensions/             内置扩展（llama.cpp 集成）
├── client/ server/ bun/    RPC / Bun 打包支撑
```

### 2.1 运行模式（`packages/coding-agent/README.md` Modes 表）

- 默认：交互 TUI 模式
- `-p/--print`：打印即退出（stdin 可管道并入首条 prompt）
- `--mode json`：全事件 JSON 行输出（`docs/json.md`）
- `--mode rpc`：进程集成 RPC（严格 LF 分隔 JSONL，`docs/rpc.md`）

### 2.2 JSONL 会话树（`docs/session-format.md`）

**问题**：会话如何持久化与分支？

**结论**：
- 会话为 JSONL 文件，存于 `~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl`（按工作目录组织）。
- 每条 entry 有 `id` / `parentId`，形成**单文件内的树结构**（v2 引入；v3 将 `hookMessage` 改名 `custom`），支持原位分支 `/tree`、复制分支到新文件 `/fork`、`/clone`、CLI `--fork`。
- entry 即 AgentMessage：`user` / `assistant`（含 text/thinking/toolCall 内容块、usage、stopReason）/ `toolResult` / `bashExecution` / `custom`（扩展可自定义）。
- 压缩（compaction）是有损摘要，但完整历史保留在 JSONL 中，可用 `/tree` 回溯；可被扩展接管（`docs/compaction.md`，`src/core/compaction/`）。

### 2.3 工具系统

**问题**：默认给模型哪些工具？

**结论**：默认仅 4 个工具：`read`、`write`、`edit`、`bash`（`packages/coding-agent/README.md` Quick Start；`src/core/system-prompt.ts` 中 `selectedTools || ["read", "bash", "edit", "write"]`）。grep/find/ls 均靠 bash 完成。工具实现在 `src/core/tools/`；扩展可注册新工具或整体替换内置工具（`pi.registerTool` + `pi.setActiveTools`）。

### 2.4 系统提示组装（`src/core/system-prompt.ts`，`buildSystemPrompt()`）

组装顺序：
1. `customPrompt`（`.pi/SYSTEM.md` / `~/.pi/agent/SYSTEM.md` 整体替换）或默认提示（角色定义 + 工具清单 + 指导原则）；
2. `appendSystemPrompt`（`APPEND_SYSTEM.md` 追加不替换）；
3. `<project_context>` 包裹的 AGENTS.md/CLAUDE.md 上下文文件（全局 + 父目录 + 当前目录拼接，支持 `AGENTS.override.md`）；
4. skills 清单（`formatSkillsForPrompt`，仅当有 read 工具时注入）；
5. `Current working directory`。

特色：默认提示内嵌 pi 自身文档路径（README/docs/examples），指示模型"被问到 pi 本身时去读文档"——代理自解释。指导原则按实际可用工具动态生成（如有 bash 无 grep 则加"用 bash 做 ls/rg/find"）。

---

## 3. 定制机制全集

**问题**：用户可以在哪些层面定制 pi？各自的注册方式与能力边界？

**结论**：五大机制 + 一个分发层（Pi Packages），资源查找统一由 `src/core/resource-loader.ts` 管理，热重载命令 `/reload`。

### 3.1 Extensions（TypeScript 模块，能力最强）

- **注册方式**：默认导出工厂函数 `export default function (pi: ExtensionAPI) {...}`（可 async），放在 `~/.pi/agent/extensions/`、`.pi/extensions/` 或 pi package；也可 CLI `-e` 加载。来源：`docs/extensions.md`（近 3000 行，最详尽的文档）、`src/core/extensions/`。
- **事件钩子清单**（`docs/extensions.md` Events 一节）：
  - 启动/信任：`project_trust`
  - 资源：`resources_discover`（动态注入 skills/prompts/themes）
  - 会话：`session_start`、`session_info_changed`、`session_before_switch`、`session_before_fork`、`session_before_compact` / `session_compact`、`session_before_tree` / `session_tree`、`session_shutdown`
  - 代理：`before_agent_start`、`agent_start` / `agent_end` / `agent_settled`、`turn_start` / `turn_end`、`message_start` / `message_update` / `message_end`、`tool_execution_start/update/end`、`context`、`before_provider_headers`、`before_provider_request`、`after_provider_response`
  - 模型：`model_select`、`thinking_level_select`
  - 工具：`tool_call`（可拦截/改参/阻止）、`tool_result`
  - 其他：`user_bash`、`input`
- **ExtensionAPI 方法**：`pi.on`、`pi.registerTool`、`pi.registerCommand`、`pi.registerShortcut`、`pi.registerFlag`、`pi.registerProvider` / `pi.unregisterProvider`、`pi.registerMessageRenderer` / `registerEntryRenderer` / `registerMarkdownTransformer`、`pi.sendMessage` / `sendUserMessage` / `appendEntry`、`pi.setActiveTools` / `getActiveTools` / `getAllTools`、`pi.setModel` / `setThinkingLevel`、`pi.exec`、`pi.events`。
- **ExtensionContext 能力**：`ctx.ui`、`ctx.sessionManager`、`ctx.modelRegistry`、`ctx.signal`（AbortSignal）、`ctx.getContextUsage()`、`ctx.compact()`、`ctx.getSystemPrompt()`、命令上下文可 `newSession` / `fork` / `navigateTree` / `switchSession` / `reload`。
- **UI 定制**：对话框、widgets、status line、footer、自定义编辑器、overlay、自动补全 provider、主题色。
- **能力边界**：官方明说可以用扩展实现子代理、plan mode、权限门禁、自定义压缩、MCP 集成、"把 pi 伪装成 Claude Code"、甚至跑 Doom——即扩展即全部。
- **安全边界**：项目信任机制（`src/core/project-trust.ts`、trust.json）决定 `.pi/` 项目资源与扩展是否加载；非交互模式用 `defaultProjectTrust`（ask/always/never）。

### 3.2 Skills（按需能力包，Agent Skills 标准）

- **注册方式**：`SKILL.md` 目录，放 `~/.pi/agent/skills/`、`~/.agents/skills/`、`.pi/skills/`、`.agents/skills/`（从 cwd 向上查找）或 pi package。来源：`docs/skills.md`、`src/core/skills.ts`。
- **调用**：`/skill:name` 手动，或模型根据系统提示中的 skill 清单自动 read SKILL.md 按需加载。
- **能力边界**：纯指令（Markdown + frontmatter name/description），不含代码执行；理念是"CLI 工具 + README 替代 MCP"。

### 3.3 Prompt Templates（可复用提示片段）

- **注册方式**：Markdown 文件（支持 `{{var}}` 占位），放 `~/.pi/agent/prompts/`、`.pi/prompts/` 或 package；`/name` 展开。来源：`docs/prompt-templates.md`、`src/core/prompt-templates.ts`。

### 3.4 Themes（终端主题）

- **注册方式**：主题文件放 `~/.pi/agent/themes/`、`.pi/themes/`；内置 `dark` / `light`；支持热重载（改文件立即生效）。来源：`docs/themes.md`。

### 3.5 Provider / 模型定制

- 静态：`~/.pi/agent/models.json` 声明自定义 provider/模型（限 OpenAI/Anthropic/Google 兼容 API），见 `docs/models.md`。
- 动态：扩展 `pi.registerProvider()`——工厂内调用会排队待 runner 初始化后应用；可注册完整 `Provider`（含 auth 交互 `login/resolve`、`refreshModels` 动态模型目录、自定义 streaming API），见 `docs/extensions.md#piregisterprovidername-config`、`docs/custom-provider.md`、示例 `examples/extensions/custom-provider-anthropic/`。

### 3.6 Pi Packages（分发层）

- package.json 加 `pi` 键声明 extensions/skills/prompts/themes 目录（否则按约定目录自动发现），经 npm/git/ssh/https 安装到 `~/.pi/agent/{npm,git}/` 或项目本地 `.pi/`；`pi config` 可启用/禁用单项资源。来源：`docs/packages.md`、README.md Pi Packages 一节。

### 3.7 其他定制点

- 设置：`~/.pi/agent/settings.json`（全局）与 `.pi/settings.json`（项目覆盖），`docs/settings.md`。
- 快捷键：`~/.pi/agent/keybindings.json`（`docs/keybindings.md`）。
- 上下文文件：AGENTS.md/CLAUDE.md 层级拼接 + `AGENTS.override.md`。

---

## 4. SDK 能力范围

**问题**：`createAgentSession()` 等 SDK 能做到什么？

**结论**：`src/core/sdk.ts` + `docs/sdk.md`（1200+ 行）。核心入口：

```typescript
import { createAgentSession, ModelRuntime, SessionManager } from "@earendil-works/pi-coding-agent";
const { session } = await createAgentSession({ sessionManager: SessionManager.inMemory(), modelRuntime: await ModelRuntime.create() });
await session.prompt("...");
```

- `createAgentSession()` 选项覆盖：目录、模型（自定义 provider/模型/API key/OAuth）、系统提示（custom/append/guidelines）、工具选择与自定义工具、**扩展加载**、skills、上下文文件、slash 命令、会话管理、设置。
- `AgentSession` 暴露 prompt、事件订阅、消息队列（steering/follow-up 语义与 TUI 一致）。
- 进阶：`createAgentSessionRuntime()` / `AgentSessionRuntime` 支持多会话与运行时替换；亦可用底层 `Agent` + `AgentState`（pi-agent-core）完全自控。
- 还提供 `runPrintMode` / `runRpcMode` / `InteractiveMode` 程序化运行模式，及 `ResourceLoader` 手动资源发现。
- 13 个渐进示例：`examples/sdk/01-minimal.ts` 到 `13-session-runtime.ts`。

---

## 5. examples/ 示例类别

**问题**：官方示例覆盖哪些场景？

**结论**：`packages/coding-agent/examples/`（总览 `examples/README.md`）：

- `sdk/`：13 个 SDK 渐进示例（最小会话 → 自定义模型/提示/工具/扩展/skills/会话/全控制/session-runtime）。
- `extensions/`（70+ 个）：生命周期与安全门禁（confirm-destructive、dirty-repo-guard、tool-override）、自定义工具（todo、question、qna、subagent、结构化输出）、命令与快捷键、UI 定制（custom footer/header/editor、overlay、snake/space-invaders/doom 游戏、rainbow-editor）、git 集成（checkpoint、auto-commit、merge-and-resolve）、系统提示与压缩定制（system-prompt-header、custom-compaction）、外部集成（ssh、sandbox、gondolin 微虚拟机、file-trigger、mac-system-theme）、自定义 provider（anthropic 流、GitLab Duo）、动态工具/资源（dynamic-tools、dynamic-resources）。

---

## 6. 设计哲学

**问题**：README/docs 传达的核心设计原则？

**结论**（`packages/coding-agent/README.md` Philosophy 一节 + 根 `README.md`）：

1. **"Adapt pi to your workflows, not the other way around"**——激进可扩展，避免 fork 内部代码。
2. **No MCP**：用"CLI 工具 + README"（即 skills）或自建 MCP 扩展。
3. **No sub-agents / No plan mode / No permission popups / No built-in todos / No background bash**：一律交给扩展或包生态（子代理可 tmux 多开 pi；后台任务用 tmux 获得完整可观测性）。
4. **无内置权限系统**：默认继承启动用户权限，需要边界就容器化/沙箱（`docs/containerization.md` 给出 Gondolin 微虚拟机、Docker、OpenShell 三种模式）。
5. **会话数据开放**：鼓励发布 OSS 会话到 Hugging Face 以改进真实任务评测。
6. **供应链硬化**：依赖精确 pin、`--ignore-scripts`、shrinkwrap、min-release-age 等成体系（根 README Supply-chain hardening）。
7. **自我解释的代理**：系统提示内嵌自身文档路径，让模型能教用户用 pi。

---

## 7. 对"定制代理"研究的启示（简评）

- pi 的定制层级是递进的：**配置（settings/keybindings）→ 内容（SYSTEM.md/AGENTS.md/prompts/themes）→ 能力（skills，纯指令）→ 代码（extensions，全功能插件）→ 分发（pi packages）**，每层注册方式统一（约定目录 + package manifest）。
- 事件总线 + ExtensionAPI 是其可扩展性的支点：几乎所有生命周期阶段（含 provider 请求前后、压缩前后、树导航前后）都有钩子。
- 会话树 JSONL（id/parentId 单文件分支）是低成本支持探索与回溯的关键数据结构设计。
