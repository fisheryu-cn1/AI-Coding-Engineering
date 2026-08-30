你是接口规格提取工程师。任务：把 Express 后端代码的 API 路由**程序化**提取为 OpenAPI 3.0.3 规格，再与设计文档的接口章节做对照。本实验验证"代码→OpenAPI 确定性反向生成 + 文档↔代码一致性比对"链路（研究备忘 §12.4 / §12.5-①，OpenAPI 作为第三个机器可读规格锚点的候选）。

输入（只读，排除 `__tests__` 与 `dist`）：
- 后端代码：`D:\Users\Yu\Documents\Coding\giencoder-exam-P0151020\backend\src\`（TypeScript/Express：`index.ts` 应用入口与路由挂载、`routes/index.ts` 与 `routes/health.ts`、`services/` 四个服务、`middleware/validate.ts` 与 `errorHandler.ts`、`types.ts` 实体定义、`store.ts`）
- 设计文档：`D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\loan-system\05-openapi-anchor\raw\design.md`（API 契约在"REST 接口（前缀 `/api`）"小节，另参考"数据流（主流程）"小节中出现的接口调用）

输出三件（目录 `D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\loan-system\05-openapi-anchor\gen\`）：

1. **`extract_routes.cjs`** —— 提取脚本。硬性要求：
   - 纯程序化：正则或 AST 均可，自选并在完成报告中说明选择理由与局限。若选 TypeScript Compiler API：注意 giencoder 工程内的 typescript@7 是原生重构断代版（5.x API 失效），需自行安装 typescript@5.x 到临时目录并通过环境变量注入路径，**不得改动 giencoder 工程的 package.json**；
   - 零 LLM 参与、可重复运行、确定性输出（同一输入必然同一输出）；
   - 提取内容：HTTP 方法；**完整路径**（应用挂载前缀 + router 路径拼接，注意 `:id` 转 OpenAPI `{id}`）；handler 函数名（作为 operationId 或描述）；中间件链（如 validate——转为请求校验的描述性注记）；
   - 请求/响应 schema：能从 `types.ts` 的 interface/类型定义**确定性对应**的，转为 `components/schemas` 并以 `$ref` 引用；无法从代码确定的（如 handler 内 inline `res.json({...})` 字面量——可以扫，扫不到就标），给最小合法占位并加 `x-uncertain: true` 扩展字段。**红线：不得编造任何字段名或类型**——宁可标注"代码中无 schema 信息"；
   - 运行方式写进脚本头部注释：`node extract_routes.cjs <backend-src目录> -o openapi.yaml`。

2. **`openapi.yaml`** —— 上述脚本生成的 OpenAPI 3.0.3 文档（`info`/`servers`/`paths`/`components` 结构完整）。必须是脚本运行的直接产物。

3. **`api-doc-code-diff.md`** —— design.md 接口声明 ↔ openapi.yaml 对照表。表为五列：| design 原文声明（逐条拆分到 method+path 粒度） | OpenAPI method + path | 判定 | 备注 | 代码证据（file:line 或 openapi.yaml 行号） |。判定五类：
   - `一致`（method+path 双匹配，`:id` 与 `{id}` 等价）
   - `代码超出设计`（OpenAPI 有、design.md 未声明）
   - `设计未实现`（design.md 声明、OpenAPI 无）
   - `形近变体`（语义相近但 method 或 path 不完全一致——路径段差异、单复数、动词命名差异等）
   - `等价但语义存疑`（路径匹配但你读代码后发现语义与 design 描述不符）
   表后附**偏差汇总**：每条偏差给出代码证据（file:line）与一句话说明。

完成后在 stdout 输出执行报告：①路由总数与来源文件分布；②schema 推导覆盖率（多少 operation 有请求/响应 schema、多少标 `x-uncertain`）；③design↔code 偏差清单（哪几条、各属哪类）；④提取局限清单——哪些 API 信息在代码中根本不存在、无法进入 OpenAPI（如：无 JSDoc/注释时的业务语义、无运行时才知道的响应码分支）；⑤你作为执行者观察到的 design.md 或代码的可疑点（如有）。
