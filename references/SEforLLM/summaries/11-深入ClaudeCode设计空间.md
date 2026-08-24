---
title: "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems"
source_pdf: "11-Liu-Dive_into_Claude_Code_v2.pdf"
arxiv_id: "2604.14228"
arxiv_version: "v2"
authors:
  - "Jiacheng Liu"
  - "Xiaohan Zhao"
  - "Xinyi Shang"
  - "Zhiqiang Shen"
year: 2026
venue: "arXiv"
type: "Agent 设计参考 + 内容索引 + 精读"
generated_at: "2026-08-24"
summary_version: "1.0"
---

# 论文摘要：Dive into Claude Code——生产级编码 Agent 的设计空间（v2.1.88 源码逆向 + 三系统对比）

## 1. 适用场景

- 当你要**设计或评审一个 agent harness**（工具循环、权限门控、上下文压缩、子代理委派、会话持久化）并需要一个已验证的生产级参照系时，读这篇。
- 当你需要**准确引用 Claude Code 的具体实现机制做架构论证**——queryLoop 单循环、五层上下文整形管线、CLAUDE.md 以 user-context 消息注入、子代理 sidechain 隔离——时读这篇（本研究逆向资料对比的权威对照物，全部主张附 Tier B 源码锚点）。
- 当你要评估**"harness 工程价值 vs 模型能力"**（换 harness 可使同一模型长程任务分数差 18 分；决策逻辑仅占代码 1.6%）时，读这篇。
- 当你要设计**权限/安全分层**（deny-first 规则、7 种权限模式、7 层独立防御、批准疲劳 93% 的应对）或**扩展机制分层**（MCP/plugins/skills/hooks 按上下文成本分级）时，读这篇。
- 当你要对比**不同部署形态的 agent 架构**（CLI 会话式 / 多渠道网关 / 单进程多表面）如何回答同一组设计问题时，读这篇（§10 三系统对比）。

> 锚点：Abstract; §1 Introduction; §3 Architecture Overview; §4 Turn Execution; §7 Context Construction; §10 Comparative Analysis; Appendix Evidence Base。

## 2. 主要观点与方案

### 2.1 方法与证据分级（Abstract; §1; Appendix）

- 对 Claude Code **公开可读的 TypeScript 源码**（v2.1.88，npm 提取，约 1,884 个文件、约 512K 行）做源码级设计空间分析，辅助以官方文档与社区分析；贯穿示例任务 "Fix the failing test in auth.test.ts" 从 §3 追踪到 §9。
- 三级证据分级（Appendix）：**Tier A**（产品文档/工程文章，表意图）、**Tier B**（引用具体文件与函数的源码验证，最强层）、**Tier C**（社区分析/对比推断，配对冲措辞）。局限性：静态单一快照；逆向只能证明"实现了什么"，不能证明设计意图或生产开关状态。

### 2.2 价值→原则→架构的追溯框架（§2; Table 1; §3.2; §3.3）

- **五个人类价值**：Human Decision Authority（人类决策权威）、Safety/Security/Privacy、Reliable Execution、Capability Amplification、Contextual Adaptability；经 **13 条设计原则**（如 deny-first with human escalation、graduated trust spectrum、defense in depth、context as scarce resource、append-only durable state、isolated subagent boundaries、values over rules 等，Table 1）追溯到具体实现。
- 高层 **7 组件**结构（user / interfaces / agent loop / permission system / tools / state & persistence / execution environment，Figure 1），展开为 **5 层子系统**：surface（入口与渲染）、core（agent loop + 压缩管线）、safety/action（权限、hooks、扩展、工具、沙箱、子代理）、state（上下文组装、运行时状态、持久化、CLAUDE.md+memory、sidechain）、backend（执行后端）（§3.3; Figure 3）。
- 第 6 个横切问题（§2.4）：架构几乎不为**长期开发者能力**（理解保持、代码库一致性、人才管线）提供显式机制——论文将其作为贯穿性质疑而非第 6 价值。

### 2.3 queryLoop：单循环即系统中心（§3.1; §3.4; §4.1–4.2; §4.4–4.5）

- **单个 queryLoop() 异步生成器**（query.ts）是系统中心：无论交互终端、headless CLI（`claude -p`）、Agent SDK 还是 IDE 集成，全部表面汇入同一循环，只有渲染/交互层不同（§3.1）。精确辨析（§3.4）：QueryEngine 只是 headless/SDK 的会话包装，委托给 query()（其内部包装 queryLoop()）；**交互式 CLI 直接调 query() 完全绕过 QueryEngine**——共享代码路径是循环函数而非引擎类。
- 每轮固定 9 步（§4.1）：设置解析 → 单一可变 State 对象初始化（7 个 continue 点整对象覆写）→ 取压缩边界后消息 → **五层 pre-model shaper** → 模型调用（流式）→ tool_use 派发 → 权限门 → 工具执行回填 → 无 tool_use 即停。生成器设计（yield StreamEvent 等）在保持单一同步控制流的同时支持 UI 流式输出。
- 工具执行双路径（§4.2）：主路径 StreamingToolExecutor 在模型流式输出时即开始执行；回退路径 runTools() 按 partitionToolCalls() 分组批处理。并发安全（只读）工具并行、互斥（改状态如 shell）串行，结果按请求顺序缓冲回放（模型预期结果顺序一致）；兄弟 abort 控制器在任一 Bash 出错时终止其余子进程。
- 恢复机制（§4.4）：输出 token 上限升级重试（每轮至多 3 次）、反应式压缩（每轮至多一次）、prompt_too_long 先试 collapse 溢出恢复与反应式压缩再终止、流式回退、fallback model。**5 种停止条件**（§4.5）：纯文本、maxTurns、上下文溢出、hook 干预、显式中止。
- 循环遵循 ReAct 模式，刻意**不做图式路由或树搜索**（对照 LangGraph 状态图、LATS 树搜索），以简单性与延迟换搜索完备性；子代理委派是唯一接近 orchestrator-workers 模式的用法（§4.1）。

### 2.4 五层上下文整形管线（§4.3; §7.3; §3.6）

- **每次模型调用前**，五个 shaper 按代价升序串行作用于 messagesForQuery（query.ts:365-453）：①**budget reduction**（applyToolResultBudget()，恒活跃）按每条工具结果大小上限把超大输出替换为 content reference；②**snip**（HISTORY_SNIP 门控）轻量裁剪较老历史段；③**microcompact** 恒跑时间路径、可选缓存感知路径（CACHED_MICROCOMPACT 门控，用真实 cache_deleted_input_tokens 推迟边界消息）按 tool_use_id 细粒度压缩；④**context collapse**（CONTEXT_COLLAPSE 门控）对历史做**读时投影**——不改动 REPL 存储的完整历史，仅替换送入模型的视图（摘要存 collapse store，故跨轮持续）；⑤**auto-compact** 前四层后仍超阈值才触发，经 compactConversation() 生成完整模型摘要。
- 压缩输出结构 [boundaryMarker, ...summaryMessages, ...messagesToKeep, ...attachments, ...hookResults]；边界以 headUuid/anchorUuid/tailUuid 注记，供读时链修补——**几乎只追加**、不改写已落盘的 transcript 行（§7.3; §9.2）。
- 设计理念为**惰性降级**：最便宜、破坏最小的压缩先执行；代价是五层交互难以被用户完全预测，且压缩大多不可见（auto-compact 在 transcript 中可见、microcompact 留边界标记、collapse 无用户可见输出）（§7.3; §12.3）。压缩路径是否复用主对话 prompt cache 的实验注释：false 路径 98% cache miss、占 fleet cache_creation 0.76%（§7.3）。
- 管线之外的配套节流（§3.6）：CLAUDE.md 懒加载（嵌套目录指令按需载入）、延迟工具 schema（ToolSearch）、子代理摘要式返回、每工具结果预算。绑定资源是上下文窗口（200K / Claude 4.6 系列 1M）（§3.1）。

### 2.5 CLAUDE.md：user-context 注入与四级层次（§7.1; §7.2; Figure 6）

- 上下文组装中，getSystemContext()（git status 等，memoized）**追加进 system prompt**；getUserContext()（CLAUDE.md 层次 + 日期）经 prependUserContext() **前插到消息数组，作为 user-context 消息而非 system prompt**（§7.1; §7.2）。架构后果：CLAUDE.md 遵从是**概率性的**，与 deny-first 权限规则的**确定性执法**形成刻意分离——guidance（CLAUDE.md）与 enforcement（permission rules）双轨（§7.2）。
- 四级层次（claudemd.ts）：managed（如 /etc/claude-code/CLAUDE.md，OS 级策略）→ user（~/.claude/CLAUDE.md）→ project（CLAUDE.md、.claude/CLAUDE.md、.claude/rules/*.md）→ local（CLAUDE.local.md，gitignore）；文件发现自 CWD 向上遍历至根，**越靠近当前目录优先级越高（越晚加载、模型注意力越多）**；嵌套目录规则懒加载使指令集随探索演化（§7.2）。支持 @include 指令（仅叶子文本节点，循环引用防护）。
- 记忆检索**不用 embedding/向量索引**：用 LLM 扫描记忆文件头部按需选出至多 5 个相关文件，以文件粒度呈现——以可检查性换选择性（§7.2）。

### 2.6 子代理委派与 sidechain（§8.1–8.3; Figure 7）

- 委派入口是 **AgentTool**（Task 为遗留别名），与其他工具同样经 buildTool() 工厂派发，**重入 queryLoop() 于隔离上下文窗口**；输入含委派 prompt、可选子代理类型、隔离模式、权限覆写与工作目录。至多 6 种内建类型（Explore / Plan / General-purpose / Claude Code Guide / Verification / Statusline-setup，随 feature flag 与入口而定）；自定义代理经 .claude/agents/*.md（正文为 system prompt，frontmatter 配 tools/model/permissionMode/hooks/isolation 等）。
- **sidechain 转录**（sessionStorage.ts:247）：每个子代理写独立 .jsonl + .meta.json，可审计但不膨胀父会话文件；**仅最终响应文本与元数据返回父上下文**（summary-only return），完整子代理历史永不进入父窗口。多数调用需自包含 prompt（默认不继承父对话史；fork-subagent 路径例外）。
- 隔离三档（§8.2）：worktree（临时 git worktree）、remote（内部）、in-process（默认，共享文件系统、隔离对话上下文）。权限覆写规则：父已处 bypassPermissions/acceptEdits/auto 时父模式优先；allowedTools 显式给出时两层作用域（SDK 级保留、会话级替换）。Agent teams 消耗约为 plan mode 标准会话 **7×** 的 token（Anthropic 2025b），团队协调用**文件锁 + 收件箱 JSON**（零依赖、可调试）而非消息中间件（§8.3）。

### 2.7 权限系统：7 模式与 7 层防御（§5; §3.5; Figure 4）

- **7 种权限模式**（types/permissions.ts）：plan / default / acceptEdits / auto / dontAsk / bypassPermissions / bubble（内部）；外部可见 5 种，auto 由 TRANSCRIPT_CLASSIFIER 门控、bubble 用于子代理向父终端升级。**deny-first**：deny 恒压 allow，宽 deny 不能被窄 allow 推翻；支持工具级与内容级（如 Bash(prefix:npm)）匹配。
- 动机是实证的：用户批准 **93%** 的权限弹窗（Hughes 2026），批准疲劳使交互确认不可单独依赖，故安全必须独立于人的警觉（deny-first、预过滤、沙箱并行生效）（§5 引言; §12.3）。
- **7 层独立防御**（§3.5）：工具预过滤（deny 工具在模型视野中移除）→ deny-first 规则求值 → 模式约束 → auto-mode ML 分类器（yoloClassifier.ts，两段式 fast-filter + CoT）→ shell 沙箱（授权与隔离两轴独立）→ resume 不恢复会话级权限 → hook 拦截（PreToolUse 可改输入/否决）。独立性假设有反例：>50 个子命令的命令因解析开销回退为单一通用批准（Adversa.ai）；预信任初始化顺序漏洞（hooks/MCP/设置解析先于信任对话框，CVE-2025-59536 CVSS 8.7、CVE-2026-21852 CVSS 5.3）（§5.4; §12.3）。拒绝被设计为**路由信号**而非硬停：模型收到拒绝原因后改试更安全方案（§5.2）。

### 2.8 扩展机制：按上下文成本分层的四件套（§6; Table 2; Figure 5）

- **MCP servers**（外部工具集成，多传输：stdio/SSE/HTTP/WebSocket/SDK 等 8+ 变体；上下文成本高——工具 schema）、**plugins**（打包分发层，manifest 含 10 类组件；中等）、**skills**（SKILL.md frontmatter 15+ 字段，经 SkillTool 元工具注入指令；低——仅描述常驻）、**hooks**（27 种事件，5 种安全相关、22 种生命周期；默认零上下文）。
- 单一机制无法覆盖"零上下文生命周期钩子 → schema 重型工具服务器"全谱，故按成本梯度分层；代价是学习曲线与组合交互（§6.3; §12.3）。工具池经 assembleToolPool() 五步组装（枚举→模式过滤→deny 预过滤→MCP 合并→按名去重，内建优先）：至多 **54 个内建工具（19 无条件 + 35 条件）**，simple 模式仅 Bash/Read/Edit 3 个；42 个工具子目录、约 86 个 slash 命令（§6.2; Appendix Table 7-8）。

### 2.9 会话持久化：append-only 与不恢复权限（§9; Figure 8）

- 三条独立持久化通道：会话转录（每会话每项目一个 JSONL，主要只追加）、全局 prompt 历史（history.jsonl，倒序读取支持 ↑/ctrl+r）、子代理 sidechain。**resume 重放转录、fork 从既有会话派生，但均不恢复会话级权限**——会话被视为隔离信任域，重授权优于隐式信任延续（§9.2）。"checkpoints" 实为文件级快照（--rewind-files，存 ~/.claude/file-history/）（§9.2）。选择可审计的 JSONL 而非可富查询的数据库，是以查询力换透明与可版本控制（§9.1）。

### 2.10 三系统对比：同一问题、不同部署语境的答案（§10; Table 3; §10.3）

- 对比 **OpenClaw**（本地优先 WebSocket 网关守护进程，默认端口 18789，多渠道个人助理）与 **Hermes Agent**（Nous Research，单 Python 进程，角色由入口点决定：hermes/hermes-agent/hermes-acp；两个 SQLite 文件 state.db + kanban.db 持久化）沿 6 维：系统范围、信任模型、agent 运行时、扩展架构、记忆与上下文、多代理与路由。
- 三个观察（§10.3）：①§3.1 的设计问题跨部署形态稳定，答案随语境变化；②不同押注——Claude Code 逐动作安全评估 + 循环为架构中心 + 扩展改单一上下文窗口；OpenClaw 网关周界级访问控制 + 控制面为中心；Hermes 逐动作批准但多表面渲染 + 可插拔记忆/模型后端；③三者经 **ACP 可组合**（OpenClaw 可托管 Claude Code；Hermes 兼居 host/guest 两侧）——设计空间是分层的而非平坦分类。Hermes 细节为 Tier B/文档勘误（如 SECURITY.md 记 approval on/auto/off 而源码为 manual/smart/off；委派深度文档记 2 而源码 MAX_DEPTH=1，论文引用源码）（§10 脚注 4）。

### 2.11 讨论：harness 哲学与六个开放方向（§12; §13; §14）

- **确定性 harness 内的模型判断**是贯穿承诺（§12.1; §12.7）：社区分析估计仅约 **1.6%** 代码是 AI 决策逻辑、**98.4%** 为运维性 harness（LLM 作为无状态补全端点被调用）；实证佐证 harness 价值——固定模型只换 harness 使长程任务分数差至多 18 分（Ding et al. 2026），Fable 5 的功能/安全通过率随 harness 变动 10 分以上（Compagna 2026）。三条横切承诺：分级分层（而非单体机制）、append-only（可审计优先于查询力）、确定性 harness 内的模型判断。
- 价值张力与实证预测（§12.2; §12.4）：有界上下文 + 子代理隔离在架构上预测模式重复与约定违反（相邻工具证据：Cursor 采纳致复杂度 +40.7%、首月速度尖峰 +281% 后第三月回落基线；304K AI 提交审计中约 1/4 AI 引入问题留存；Claude Code 上的最小对研究：代码整洁度不改变通过率但降 token 7–8%、文件重访 34%）。长期能力证据：RCT 中资深开发者慢 19% 而自感 +20%、理解测试低 17%、EEG 神经连接减弱、入门级招聘降 25%（§12.2）。
- **六个开放方向**（§13）：①静默失败与可观测-评测鸿沟；②跨会话持久（静态指令与单会话转录之间缺一层）；③harness 边界演化（where/when/what/with whom，如 KAIROS 主动架构、v2.1.154 dynamic workflows 以 JS 编排脚本扇出至多 1000 个子代理）；④horizon scaling（会话→科学计划尺度的任务时长）；⑤治理与外部审计（GPAI 行为准则、MIT AI Agent Index 仅 13.3% 有 agent 安全卡）；⑥长期开发者能力作为一等设计问题。结论（§14）：最重大的开放问题不是加更多自主性，而是**随时间保持人类能力**。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| 分析对象规模 | Claude Code v2.1.88，约 1,884 文件 / 约 512K 行 TypeScript（npm 提取） | Appendix Evidence Base |
| 概念框架规模 | 5 价值观 × 13 设计原则 × 7 组件 × 5 子系统层 | §2; Table 1; §3.2; §3.3 |
| 决策逻辑占比 | 约 1.6% 为 AI 决策逻辑，98.4% 为运维性 harness（社区分析估计） | §3.1; §12.1; §12.7 |
| 上下文整形管线 | 5 层（budget reduction 恒活跃 / snip·HISTORY_SNIP / microcompact·含缓存感知路径 / context collapse·CONTEXT_COLLAPSE / auto-compact 默认启用可关） | §4.3; §7.3 |
| 工具池 | 至多 54 内建工具（19 无条件 + 35 条件）；simple 模式 3 个；42 工具子目录、约 86 个 slash 命令 | §6.2; Appendix Table 8 |
| 权限系统 | 7 模式（5 外部 + auto + bubble）；7 层独立防御；用户批准率约 93% | §5.1; §3.5; §2.1 |
| 扩展机制 | 4 种（MCP/plugins/skills/hooks）按上下文成本 高/中/低/零 分层；27 种 hook 事件（5 安全 + 22 生命周期）；插件 10 类组件 | §6; Table 2; §6.1 |
| CLAUDE.md 层次 | 4 级（managed/user/project/local）；LLM 扫描文件头按需选至多 5 个记忆文件，无向量索引 | §7.2 |
| 子代理 | 至多 6 种内建类型；agent teams 耗约为标准会话 7× token；sidechain = 独立 .jsonl + .meta.json，仅摘要返回 | §8.1; §8.3 |
| harness 价值实证 | 固定模型换 harness：长程任务分数差至多 18 分（Ding et al. 2026）；Fable 5 功能/安全通过率随 harness 变动 ≥10 分（Compagna 2026） | §12.1 |
| 使用行为实证 | 27% 任务无该工具不会尝试（132 人内部调查）；auto-approve 率随使用从 <50 会话约 20% 升至 750 会话 40%+；沙箱使权限弹窗减约 84% | §1; §2.1; §12.3 |
| 长期能力证据 | RCT 慢 19%（自感 +20%）；复杂度 +40.7%、首月速度 +281%；304K AI 提交约 1/4 问题留存；理解测试低 17%；入门招聘降 25%；整洁输入降 token 7–8%、文件重访 34% | §12.2; §12.4; §2.4 |
| 三系统对比 | 6 维 × 3 系统；ACP 可组合（OpenClaw 可托管 Claude Code；Hermes 兼居 host/guest） | §10; Table 3; §10.3 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2604.14228（v2，2026-07-02，cs.SE） |
| 论文配套仓库 | https://github.com/VILA-Lab/Dive-into-Claude-Code（Abstract；维护 companion 设计空间笔记） |
| 分析对象 | Claude Code v2.1.88 TypeScript 源码（npm 提取；官方文档 https://code.claude.com/docs）；社区重实现 5 例见 Appendix Table 9（ClawCodex、Claw Code、claude-code-working 等） |
| 对比系统 | OpenClaw（多渠道个人助理网关）；Hermes Agent（Nous Research，单进程多表面，含 SQLite/Kanban 子系统） |
| 本仓库关联 | 入库来源：`research/agent-software-design/materials/harness与冯诺依曼架构类别关系.md`（见 `references/arxiv_2026-08_manifest.md` 备注）；同主题 01（LLM 构件分类学）、07（确定性外壳+非确定内核）、08（DbC 协议层）、09（METR RCT）互证；本研究的逆向架构对比（五层压缩、子代理隔离、queryLoop）以本文 v2 为对照基准 |

## 5. 一句话索引（给 Agent 用）

> 需要 Claude Code 内部机制的可靠锚点时读这篇：Liu 等逆向 v2.1.88 源码（1,884 文件/512K 行 TS）刻画其设计空间——核心是 query.ts 中单个 queryLoop() 异步生成器（所有表面汇入同一循环）、每次模型调用前五层整形（budget reduction/snip/microcompact/context collapse/auto-compact）、CLAUDE.md 四级层次以 user-context 消息注入而非 system prompt、子代理 sidechain 隔离且仅摘要返回；98.4% 代码是运维 harness（决策逻辑仅 1.6%），固定模型换 harness 可使长程任务差 18 分；与 OpenClaw/Hermes 对比显示同一设计问题在不同部署语境答案不同。
