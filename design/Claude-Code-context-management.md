# Claude Code 上下文管理与代码生成架构

## 1. 核心入口流程

```
用户输入 → handlePromptSubmit → processUserInput → processTextPrompt → onQuery → query → queryLoop
```

| 文件 | 职责 |
|------|------|
| [handlePromptSubmit.ts](src/utils/handlePromptSubmit.ts) | 处理用户提交的主入口，管理输入解析、引用展开、命令队列 |
| [processUserInput.ts](src/utils/processUserInput/processUserInput.ts) | 核心输入处理：图片压缩、附件提取、slash命令、bash命令路由 |
| [processTextPrompt.ts](src/utils/processUserInput/processTextPrompt.ts) | 将文本输入转换为消息对象，执行 UserPromptSubmit hooks |
| [query.ts](src/query.ts) | 查询主循环，生成流式事件，调用工具，执行 postSampling/stop hooks |

---

## 2. System Prompt 构建

| 文件 | 职责 |
|------|------|
| [constants/prompts.ts](src/constants/prompts.ts) | `getSystemPrompt()` - 构建完整 system prompt 数组，包含静态段落和动态段落 |
| [constants/systemPromptSections.ts](src/constants/systemPromptSections.ts) | 定义 `systemPromptSection()` 和 `DANGEROUS_uncachedSystemPromptSection()` 两种缓存策略的段落 |
| [context.ts](src/context.ts) | `getUserContext()` / `getSystemContext()` - 用户上下文（claude.md）和系统上下文（git status）缓存 |
| [systemPrompt.ts](src/utils/systemPrompt.ts) | `buildEffectiveSystemPrompt()` - 根据 agent/coordinator/custom 优先级组装最终 prompt |
| [queryContext.ts](src/utils/queryContext.ts) | `fetchSystemPromptParts()` - 分离式获取 system prompt 各部分，避免循环依赖 |

---

## 3. 消息构建与 API 调用

| 文件 | 职责 |
|------|------|
| [services/api/claude.ts](src/services/api/claude.ts) | `createMessage()` / `streamRequest()` - API 请求的核心构建逻辑，组装 system prompt blocks、user/system context |
| [utils/messages.ts](src/utils/messages.ts) | `normalizeMessagesForAPI()` / `createUserMessage()` 等消息创建和规范化函数 |
| [utils/api.ts](src/utils/api.ts) | `prependUserContext()` / `appendSystemContext()` - context 注入逻辑，splitSysPromptPrefix 分割静态/动态边界 |

---

## 4. Hooks 系统

| 文件 | 职责 |
|------|------|
| [utils/hooks.ts](src/utils/hooks.ts) | 主 hooks 注册表，`executeUserPromptSubmitHooks()` / `executeStopFailureHooks()` |
| [utils/hooks/execPromptHook.ts](src/utils/hooks/execPromptHook.ts) | LLM-based prompt hook 执行器，条件判断 |
| [utils/hooks/postSamplingHooks.ts](src/utils/hooks/postSamplingHooks.ts) | 采样后 hook，`registerPostSamplingHook()` / `executePostSamplingHooks()` |
| [utils/hooks/apiQueryHookHelper.ts](src/utils/hooks/apiQueryHookHelper.ts) | 创建 API 查询 hook 的工厂函数 |

---

## 5. 工具系统

| 文件 | 职责 |
|------|------|
| [Tool.ts](src/Tool.ts) | `Tools` / `ToolUseContext` - 工具注册表和上下文传递 |
| [tools/*/prompt.ts](src/tools) | 各工具的 prompt 定义（如 [BashTool/prompt.ts](src/tools/BashTool/prompt.ts)） |
| [services/tools/toolOrchestration.ts](src/services/tools/toolOrchestration.ts) | `runTools()` - 工具执行编排 |

---

## 6. 上下文压缩

| 文件 | 职责 |
|------|------|
| [services/compact/compact.ts](src/services/compact/compact.ts) | `buildPostCompactMessages()` - 压缩后的消息构建 |
| [services/compact/autoCompact.ts](src/services/compact/autoCompact.ts) | 自动压缩触发逻辑 |
| [query/tokenBudget.ts](src/query/tokenBudget.ts) | token 预算管理 |

---

## 7. 代码改写类请求的上下文控制

### 7.1 上下文范围控制机制

Claude Code **没有使用 AST 来选择局部代码片段作为上下文**。它采用的是以下策略：

#### 基于行号的简单上下文窗口

[readEditContext.ts](src/utils/readEditContext.ts) - 核心文件读取逻辑：

```typescript
// 通过needle（搜索字符串）在文件中定位，返回匹配位置±contextLines行
export async function readEditContext(
  path: string,
  needle: string,
  contextLines = 3,  // 默认3行上下文
): Promise<EditContext | null>
```

**算法特点**：
- 扫描文件查找 `needle` 字符串位置
- 以 line boundary 为准，向前后扩展 `contextLines` 行
- 使用 8KB 分块扫描 + straddle overlap 处理跨边界匹配
- 最大扫描 10MB（`MAX_SCAN_BYTES`）

#### FileEditTool 的 old_string 匹配模式

[FileEditTool/utils.ts](src/tools/FileEditTool/utils.ts)：

```typescript
// old_string 使用精确字符串匹配（非 AST）
// 查找失败时尝试 quote normalization（弯引号→直引号）
findActualString(fileContent, searchString)
```

**特点**：
- `old_string` 必须是文件中的**精确子串**
- 如果模型输出的 `old_string` 包含弯引号而文件是直引号，会自动 normalized
- 提供 4 行上下文片段用于 diff 显示 (`getSnippetForPatch`)

### 7.2 工具描述层的上下文限制

[FileEditTool/prompt.ts](src/tools/FileEditTool/prompt.ts)：

```typescript
// 指导模型使用最小唯一性 old_string
const minimalUniquenessHint =
  `Use the smallest old_string that's clearly unique —
   usually 2-4 adjacent lines is sufficient.`
```

**设计意图**：让模型自己选择足够小但唯一的片段，而非系统自动选择。

### 7.3 搜索/读取操作的折叠机制

[collapseReadSearch.ts](src/utils/collapseReadSearch.ts)：

```typescript
// 将连续的 Read/Grep/Bash 搜索操作折叠成群组
// 避免每个搜索操作都单独占用上下文token
collapseReadSearchGroups(messages, tools)
```

**折叠规则**：
- 连续的 search/read 操作被合并为单个摘要
- 非搜索类 bash 命令（如 `git commit`）不会被折叠
- `old_string` 不唯一时编辑会失败（要求重新提供更多上下文）

### 7.4 上下文压缩（Compact）

[services/compact/compact.ts](src/services/compact/compact.ts)：

当上下文接近 200K token 限制时：
1. 调用 LLM 生成对话摘要（`getCompactPrompt`）
2. 保留最近的 tool results 和关键消息
3. 用摘要替换早先的对话历史

### 7.5 System Prompt 中的代码编辑指导

[constants/prompts.ts](src/constants/prompts.ts) 的 `getUsingYourToolsSection()`:

```typescript
// 强制要求先 Read 再 Edit
`You must use your ${FILE_READ_TOOL_NAME} tool at least once in the
 conversation before editing.`
```

### 7.6 Tree-sitter 的使用场景（仅限 Bash 安全分析）

[utils/bash/treeSitterAnalysis.ts](src/utils/bash/treeSitterAnalysis.ts)：

Tree-sitter AST 解析**仅用于 Bash 命令的安全验证**：
- 提取 `quoteContext`（引号上下文）
- 检测 `compoundStructure`（复合命令结构）
- 识别 `dangerousPatterns`（危险模式：command substitution, heredoc 等）

**不是**用于代码编辑的上下文选择。

---

## 8. 关键架构特点

1. **Prompt 缓存分离**：静态内容（`SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 之前）使用 `scope: 'global'` 缓存，动态内容按会话管理
2. **异步分段解析**：使用 `systemPromptSection()` 懒加载和缓存动态段落
3. **分层 Hook**：UserPromptSubmit hooks → API 调用 → PostSampling hooks → Stop hooks
4. **Context 注入时机**：userContext 和 systemContext 在 API 调用前通过 `prependUserContext()` / `appendSystemContext()` 注入
5. **工具权限上下文**：通过 `ToolUseContext` 在整个查询生命周期传递权限状态
6. **代码编辑设计哲学**：系统提供基础的文件内容读取和匹配机制，上下文范围的决策（如选择哪些行）由模型根据 `old_string` 的唯一性要求自行决定。这避免了 AST 解析的语言特异性，保持了工具的通用性
7. **搜索操作折叠**：连续搜索操作合并 token 以节省上下文空间

---

## 9. 文件定位索引

### 上下文管理核心
- `src/context.ts` - 用户/系统上下文缓存
- `src/constants/prompts.ts` - System prompt 构建
- `src/constants/systemPromptSections.ts` - Prompt 段落缓存管理
- `src/utils/systemPrompt.ts` - Prompt 组装优先级
- `src/utils/queryContext.ts` - Prompt 部分分离获取

### 代码改写相关
- `src/utils/readEditContext.ts` - 基于行号的上下文窗口读取
- `src/tools/FileEditTool/utils.ts` - old_string 精确匹配与 normalization
- `src/tools/FileEditTool/prompt.ts` - Edit 工具描述
- `src/utils/collapseReadSearch.ts` - 搜索操作折叠

### 压缩与优化
- `src/services/compact/compact.ts` - 上下文压缩
- `src/services/compact/autoCompact.ts` - 自动压缩触发
- `src/utils/bash/treeSitterAnalysis.ts` - Bash 安全分析（AST）

### API 层
- `src/services/api/claude.ts` - API 请求构建
- `src/utils/messages.ts` - 消息规范化
- `src/utils/api.ts` - Context 注入
