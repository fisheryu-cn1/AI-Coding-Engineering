# DSH（DeepSeek Harness）架构与插件生态调研

> 状态：已完成初稿（2026-08-17）

## 0. 背景与信息来源

DeepSeek Harness（命令名 `dsh`）是 DeepSeek AI 开发的开源 agent harness（智能体执行框架），处于 developer preview 阶段，核心理念是 **"Everything is a plugin"（一切皆插件）**，底层由 Cordis 插件框架驱动（设计来自论文 *A Programming Paradigm for Spatiotemporal Composability*）。运行方式：`npx @deepseek-ai/dsh web`（默认 Web UI http://127.0.0.1:3080），源码方式用 pnpm 构建。MIT 协议；官方目前不接受外部 PR。

入口线索核实情况：
- ✅ 官方仓库存在：https://github.com/deepseek-ai/deepseek-harness
- ✅ 社区手册存在：https://github.com/Electricitysheep/dsh-handbook（12 章中英双语白皮书，含 PDF）
- ❌ `dshfind.com` 未找到；实际存在的插件目录/商店为：
  - awesome-dsh-plugin（GitHub: awesome-dsh-plugin/awesome-dsh-plugin，约 4.3k stars，收录 227–270+ 插件、11 大类）
  - 0xsoline/awesome-deepseek-harness（含 CATALOG.md）
  - 社区商店站：dsh.deepseek404.com、deepseek1024.com、dsh-hub.cc（手册称 4000+ 插件）
  - 官方发现机制：GitHub topic `dsh-plugin`（公开仓库已超 700 个）

## 1. Cordis 插件框架与 cordis.patch.yml 挂载机制

### 1.1 Cordis 模型

Cordis（https://github.com/cordiverse/cordis）采用"插件贡献服务"模型。插件向共享 context 贡献三类东西：

1. **服务**（带类型接口的实现）
2. **带类型的事件**（事件总线）
3. **可逆副作用**（插件卸载时自动回退注册）

关键设计："没有特权核心可打补丁"——扩展 dsh 的唯一方式是在其他插件**旁边挂载一个新插件**，而不是 monkey-patch 核心。产品所有部分都是插件：模型适配器、工具注册表、会话日志、甚至 agent 循环本身，均可从配置替换。

### 1.2 Profile / Bundle / Patch 三层组装

运行的 dsh 是启动时按序分层组合的**插件树**：

- **Profile**：存储在 Harness home（`~/.dsh/profiles/web/` 等）的命名组合，列出堆叠的 bundles、树外插件、用户自己的 cordis.patch.yml。内置 `web` 与 `headless` 两种模板。
- **Bundle**：Cordis 配置行及其挂载代码的分发格式，在 package.json 的 `dsh.bundle` 字段指向 bundle 的 patch 文件；profile 在 `dsh.profile.bundles` 列出 bundles。
- **cordis.patch.yml**：用户挂载层，手写 `insert` 条目挂载插件，或按 id 整行覆盖某插件 config。

分层应用顺序（依次叠加，后层覆盖前层，应用到空的 entry 列表上）：
1. profile 列出的各 bundle（按列出顺序）
2. profile 自己的 cordis.patch.yml
3. home 级 patch
4. `--patch` 命令行覆盖

Patch 三条关键约束：
1. `config` 是**整行替换**，不是深度合并；
2. name 不匹配会被**静默跳过**；
3. patch 按条目 **id** 定位，不要求与注册名相等。

诊断工具：`dsh --profile web --dump-config`（带来源注释的组合树）、`--dump-default-config`（仅 bundle 层）。Profile 目录内的 `cordis.yml` 是每次启动重写的空基座，不应手编。

`dsh-base` 是所有 profile 的第一层，提供模型适配器、工具、持久化、沙箱与审批策略、设置、凭据、遥测；`dsh-web-app` 加浏览器应用；`dsh-headless` 是无服务器的单次运行器。

### 1.3 核心包（插件树贡献者）

| 包 | 职责 | ctx key |
|---|---|---|
| core/session | 只追加 SessionEvent 日志与内存存储 | ctx.sessions |
| core/system-prompt | prompt 段落与工具 schema 组装 | ctx.systemPrompt |
| core/tools | 作用域工具注册表与受保护执行管道 | ctx.tools |
| core/agent | Agent 接口、活动注册表、agent/* 事件 | ctx.agents |
| core/agent-loop | 默认 agent 驱动循环 | ctx.agentLoop |
| core/scope | 每 agent 作用域注册原语 | 库，无 key |
| llm/llm | 消息/流词汇与适配器接缝 | ctx.llm |

会话日志不变量："model-visible means logged"——凡到达模型请求的内容必须可从日志重建，运行时断言强制保证。

## 2. 插件 API 能力边界

事件分三类：
- **会话事件**（session/event）：持久事实，写入日志并广播，需在重载后存活时使用；
- **Agent 事件**（agent/*）：携带活动 Agent——inbox、step、status、request、validation、continuation；
- **能力事件**：把策略和适配器挂到接缝（fs/*、tools/*、telemetry/*）。

主要扩展点（能力接缝，每个接缝含 Service Definition / Provider / Consumer 三角色）：
- 模型 provider → 在 `ctx.llm` 注册适配器
- 模型可见工具 → 在 `ctx.tools` 注册，schema 自动加入 prompt 组装
- 单会话不同能力集 → 组合 agent preset（服务行需 isolate realm）
- Shell 执行 → `ctx.shell` 后端（本地经 ctx.subprocess 生成）
- 持久终端 → `ctx.terminals` 后端 + dsh-tool-terminal
- 人工命令 → `ctx.commands`，无需模型 turn 即可分发
- 后台任务 → `ctx.jobs`（job_* 工具收集/停止）
- 文件系统 → `ctx.fs` provider 或 fs/* 事件
- 进程限制 → `ctx.sandbox` 后端，spawn 前包装 argv
- 拦截请求/工具/turn → 相应 agent/* 或 tools/* 事件（waterfall 模式，监听者须调 next() 委托）
- 模型可见上下文注入 → `agent.inject()`，进入下一个被接受的请求
- 会话标题 / 目标管理 / 会话分叉 → ctx.sessionTitle / ctx.goals / ctx.sessions.fork()
- 某 agent 作用域内注册 → 用该 agent 的 agent.ctx

文件系统与子进程 provider 共享一个"执行世界"，指向远程沙箱时 Bash、PTY、LSP 随之迁移。Turn 流程为：turn/start → 组装 prompt → agent/pre-step → step/start → agent/request → llm/stream → assistant/chunk → tool/call → tools 管道 → step/end → agent/turn-stopping → turn/end。

**边界结论**：DSH 插件 API 覆盖模型接入、工具、事件拦截、FS/沙箱/终端、UI 组件注册等宿主内所有接缝，但定制以"注册/监听/替换服务行"为主，不修改核心代码。

## 3. Skill 体系、Profile（headless）与 settings.yaml

- **Skill 体系**：skill 以 `SKILL.md` 定义，存放在 `.agents/skills/` 目录（官方仓库自带如 dsh-doc-standards 的 SKILL.md）。社区插件（如 dsh-memory-evolve）支持 Skill 演化、从 Claude Code 迁移 Skill（claude-bridge）。
- **Profile（headless）**：`dsh --profile headless "任务描述"` 无交互执行、打印结果即退出，适合 CI/脚本；首次使用自动从模板初始化；注意 headless 默认走 deepseek-official 路由，仍要求 DEEPSEEK_API_KEY。另有 Python SDK（`pip install deepseek-harness-sdk`）。
- **settings.yaml**（`~/.dsh/settings.yaml`，由 dsh-settings-file 热发布、可在 UI 编辑）：用户运行时可改项，热生效。主要字段：
  - `agent-default-model`：默认 provider+model 路由
  - `llm-pi-ai.providers`：自定义 provider（apiKeyEnv、api: openai-completions、baseURL、models）；另有 llm-deepseek 扁平形态
  - `permission.defaultPreset`：权限预设（如 danger-full-access）
  - 分层优先级：patch（部署者、静态、需重启）vs settings（用户、动态、热生效）
- **凭据**：`~/.dsh/.credentials.yaml`（0600，原子写入）；环境变量优先级：进程 env > 工作目录 .env > ~/.dsh/.env。

## 4. Web UI 客户端插件 vs 宿主端插件

- **宿主端（Cordis 插件树）**：模型适配器、工具、沙箱、事件等在宿主侧挂载，经 dsh-base 等组合；这是 Cordis patch 体系的主体。
- **Web UI 客户端插件**：前端通过驱动 `ctx.agents` 并从 session/event 渲染来集成；为 Web 客户端添加 Chat 节点的方式是 "register a ConversationNodeDefinition + keyed renderer"。
- 生态中大量插件本质是 Web UI 增强（侧边栏、看板、皮肤、小游戏），说明客户端渲染层也是一等扩展面；客户端插件依赖宿主暴露的 ctx 服务与事件流。

## 5. 插件生态类别归纳（代表插件）

GitHub `dsh-plugin` topic 公开仓库已超 700 个；awesome-dsh-plugin 收录 227–270+ 插件、11 大类，可通过 `dsh plugin add` 安装。

| 类别 | 代表插件 | 说明 |
|---|---|---|
| UI 增强 | DSH Better Sidebar、dsh-TUI、dsh-web-ui | 侧边栏集成文件/终端/Git 形成迷你 IDE；Claude Code 风格全屏终端 UI（思考流、TPS 仪表）；Web 界面含任务看板、Git 图谱 |
| 工具集成 | dsh-github-connector、dsh-at-file、ego-lite 浏览器插件 | 对话中管理 GitHub；输入框 @file 引用文件；为 AI 打造的 Chromium 浏览器，提供 13 个 ego_* 结构化工具 |
| 记忆 / RAG | dsh-memory-evolve | 可进化长期记忆，记录项目约定与架构决策，Git 分支感知、支持多 DSH 实例共享记忆 |
| 多智能体 | dsh-agent-teams、dsh-suite（Lord/Serf） | 现场组建子 agent 团队拆分任务；文件式多智能体编排（Lord 派活、Serf 干活） |
| 迁移兼容 | dsh-plugin-claude-bridge、dsh-claude-move | 迁移 Claude Code 的记忆/Skill/CLAUDE.md，甚至整体搬移旧会话 |
| 成本/上下文监控 | context-vista | 查看上下文 Token 占用；社区有 99% 缓存命中率账单实测 |
| 安全/恢复 | dsh-undo、dsh-record-replay | 回滚被 agent 改崩的上下文；录制操作供复现 |
| 知识沉淀 | dsh-obsidian-export、dsh-share | 对话一键沉淀到 Obsidian / 一键分享 |
| 多模态 | ModLens | 外挂视觉模型，先提取结构化信息再交给 DeepSeek 推理 |
| 娱乐 | dsh-minigames、dsh-ads、deepseek-manners、电子宠物 | 小游戏、怀旧广告、趣味回复、二次元电子宠物 |

另有插件质量检查工具（33 项检查：Manifest、Patch、构建产物、Hub 收录等）。

## 6. DSH vs Pi：配置式组装 vs 编程式定制

- **DSH（配置式组装）**：定制方式是声明式配置层叠——bundle → cordis.patch.yml（YAML insert/覆盖）→ settings.yaml；"没有特权核心可打补丁"，通过在插件树旁挂载新插件、注册服务行来扩展；普通用户改 YAML 即可重组 harness，甚至替换 agent 循环本身。适合部署者组装、用户运行时调节。
- **Pi（编程式定制）**：badlogic（Mario Zechner / earendil-works，https://github.com/earendil-works/pi）的 TypeScript monorepo（npm workspaces，7 个核心子包），走极简路线（<1000 token 系统提示词 + 4 个核心工具），扩展以 **TypeScript 代码写 extension** 为主，提供"监听介入"与"完全自定义"两类扩展能力，不是简单钩子系统；15+ 内置 provider、树状会话、上下文压缩。
- **对比证据**：Pi 架构解析强调"反对更多工具/更长提示词/复杂规划链"的反直觉极简立场，扩展即编程；DSH 的 patch/bundle/profile 体系则是纯配置文件驱动的分层组装。51CTO 对比文章（https://www.51cto.com/article/836597.html）以"编排型（配置）vs 自主型"框架讨论相关取舍。可概括为：**DSH 把组装面开放给配置（YAML），Pi 把定制面开放给代码（TS extension）**；二者分别代表"可组合配置产品"与"可编程库/框架"两条路线。

## 7. 资料来源

- 官方仓库 README（中文）：https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md
- 官方架构文档：https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
- 官方开发者预览页：https://deepseek.com/harness/ 、https://deepseek.com/harness/en/
- 社区配置文档：https://deepseekdocs.com/en/docs/user-guide/configuration
- dsh-handbook 社区手册：https://github.com/Electricitysheep/dsh-handbook （生态章 docs/07-ecosystem.md）
- 手册推荐帖：https://github.com/deepseek-ai/deepseek-harness/discussions/831
- awesome-dsh-plugin 相关：https://juejin.cn/post/7673872542772428851 、https://github.com/0xsoline/awesome-deepseek-harness/blob/main/CATALOG.md
- 插件生态报道（量子位）：https://www.qbitai.com/2026/08/473597.html
- dsh-suite：https://github.com/whyihaveyou/dsh-suite
- 知乎架构报告：https://zhuanlan.zhihu.com/p/2071576464810682036
- Ollama 集成（settings.yaml 实例）：https://docs.ollama.com/integrations/deepseek-harness
- headless/provider 教程：https://ofox.ai/blog/deepseek-harness-dsh-setup-custom-providers-2026/
- Pi 框架：https://github.com/earendil-works/pi ；解析文 https://zhuanlan.zhihu.com/p/2004665077618458930 、https://zhuanlan.zhihu.com/p/2071363866802574677 、https://panzhixiang.com/2026/pi-agent-extension-design/ 、https://blog.csdn.net/zhonglinzhang/article/details/160282618
- 对比文：https://www.51cto.com/article/836597.html
