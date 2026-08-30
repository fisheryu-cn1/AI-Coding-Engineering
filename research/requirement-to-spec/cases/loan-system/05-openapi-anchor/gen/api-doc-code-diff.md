# design.md 接口声明 ↔ openapi.yaml 路由对照

> **范围**
> - **design.md 来源**：`raw/design.md` 中 **「REST 接口（前缀 `/api`）」** 小节逐条声明。
> - **openapi.yaml 来源**：`gen/openapi.yaml`（由 `extract_routes.cjs` 对 `backend/src/` 提取生成，共 20 个 operation、12 条 path）。
> - **判定列**：五类——`一致` / `形近变体` / `设计未实现` / `代码超出设计` / `等价但语义存疑`。
> - **代码证据列**：行号定位到源代码文件（`backend/src/...`）或 `openapi.yaml` 中 path/method 起始行。

---

## 一、逐条对照表

### 1.1 Borrower

| # | design 原文声明（method + path） | OpenAPI method + path | 判定 | 备注 | 代码证据 |
|---|---|---|---|---|---|
| 1 | `GET /borrowers` | `GET /api/borrowers` | 一致 | method+path 双匹配；`/api` 前缀由 `app.use('/api', router)` 注入 | openapi.yaml:26；routes/index.ts:33 |
| 2 | `POST /borrowers` | `POST /api/borrowers` | 一致 | 同上；含 `validateBorrower` 中间件 | openapi.yaml:54；routes/index.ts:39 |
| 3 | `GET /borrowers/:id` | `GET /api/borrowers/{id}` | 一致 | `:id` ↔ `{id}` 等价 | openapi.yaml:102；routes/index.ts:36 |
| 4 | `PUT /borrowers/:id` | `PUT /api/borrowers/{id}` | 一致 | 含 `validateBorrower` 中间件 | openapi.yaml:131；routes/index.ts:42 |
| 5 | `DELETE /borrowers/:id` | `DELETE /api/borrowers/{id}` | 一致 | — | openapi.yaml:185；routes/index.ts:45 |

### 1.2 LoanOrder

| # | design 原文声明 | OpenAPI method + path | 判定 | 备注 | 代码证据 |
|---|---|---|---|---|---|
| 6 | `GET /loans` | `GET /api/orders` | 形近变体 | 路径段 `loans` → `orders`；语义同指「贷款订单」 | openapi.yaml:375；routes/index.ts:50 |
| 7 | `POST /loans` | `POST /api/orders` | 形近变体 | 同上；含 `validateLoanOrder` 中间件 | openapi.yaml:403；routes/index.ts:56 |
| 8 | `GET /loans/:id` | `GET /api/orders/{id}` | 形近变体 | 同上 | openapi.yaml:446；routes/index.ts:53 |
| 9 | `PUT /loans/:id` | `PUT /api/orders/{id}` | 形近变体 | 同上；含 `validateLoanOrder` 中间件 | openapi.yaml:481；routes/index.ts:59 |
| 10 | `DELETE /loans/:id` | `DELETE /api/orders/{id}` | 形近变体 | 同上 | openapi.yaml:536；routes/index.ts:74 |
| 11 | `POST /loans/:id/sign` | `POST /api/orders/{id}/sign` | 形近变体 | 路径段 loans→orders | openapi.yaml:661；routes/index.ts:65 |
| 12 | `POST /loans/:id/complete` | `POST /api/orders/{id}/complete` | 形近变体 | 同上；body 接受可选 `comment`（代码 OrderFlowService.complete 显式消费） | openapi.yaml:572；routes/index.ts:68 |
| 13 | `POST /loans/:id/submit` | `POST /api/orders/{id}/submit` | 形近变体 | 同上 | openapi.yaml:703；routes/index.ts:62 |

### 1.3 CreditResult

| # | design 原文声明 | OpenAPI method + path | 判定 | 备注 | 代码证据 |
|---|---|---|---|---|---|
| 14 | `GET /credit-results` | `GET /api/credits` | 形近变体 | 路径段 `credit-results` → `credits`；单复数与连字符差异 | openapi.yaml:329；routes/index.ts:79 |
| 15 | `POST /credit-results` | — | 设计未实现 | 代码无对应路由；creditResult 由 LoanOrderService.submit → autoApprove 内部创建（rules/scoring.ts:46-65），不对外暴露 POST | routes/index.ts（无此行） |
| 16 | `GET /credit-results/:id` | — | 设计未实现 | 代码未提供按 ID 查 CreditResult 的端点；仅有 `GET /credits?order_id=N` 按订单过滤的列表 | routes/index.ts（无此行） |
| 17 | `PUT /credit-results/:id` | — | 设计未实现 | 同上 | routes/index.ts（无此行） |
| 18 | `DELETE /credit-results/:id` | — | 设计未实现 | 同上 | routes/index.ts（无此行） |

### 1.4 Config

| # | design 原文声明 | OpenAPI method + path | 判定 | 备注 | 代码证据 |
|---|---|---|---|---|---|
| 19 | `GET /config/approval` | `GET /api/config/approval` | 一致 | — | openapi.yaml:221；routes/index.ts:84 |
| 20 | `PUT /config/approval` | `PUT /api/config/approval` | 一致 | 无 validate 中间件；configService 直接 Object.assign | openapi.yaml:243；routes/index.ts:87 |
| 21 | `GET /config/rates` | `GET /api/config/rate` | 形近变体 | 路径段复数 `rates` → 单数 `rate` | openapi.yaml:275；routes/index.ts:90 |
| 22 | `PUT /config/rates` | `PUT /api/config/rate` | 形近变体 | 同上 | openapi.yaml:297；routes/index.ts:93 |

### 1.5 design.md 未声明但代码实现的端点

| # | OpenAPI method + path | 判定 | 备注 | 代码证据 |
|---|---|---|---|---|
| 23 | `GET /api/health` | 代码超出设计 | health check 是工程惯例；design.md REST 列表未显式列出，但 backend/src/routes/health.ts 实现并在 index.ts 挂载 | openapi.yaml:352；routes/health.ts:8；routes/index.ts:28 |
| 24 | `GET /api/orders/{id}/contract` | 代码超出设计 | design.md 描述「详情/签约页读取订单与费率」时未列出独立 contract 端点；代码由 OrderFlowService.contractDetail 暴露 | openapi.yaml:625；routes/index.ts:71；services/orderFlowService.ts:60-79 |

---

## 二、偏差汇总

| 类别 | 计数 | 偏差明细 | 一句话说明 + 代码证据 |
|---|---|---|---|
| **一致** | 7 | #1, #2, #3, #4, #5, #19, #20 | 仅 Borrower CRUD 与 `/config/approval` 双匹配；其余均有路径命名分歧 |
| **形近变体** | 11 | #6–#13（loans→orders × 8）；#14（credit-results→credits × 1）；#21–#22（rates→rate × 2） | design.md 路径段命名与代码不一致：`/loans` ↔ `/orders`、`/credit-results` ↔ `/credits`、`/config/rates` ↔ `/config/rate`；语义目标相同（同一实体），仅字面不同 |
| **设计未实现** | 4 | #15（POST /credit-results）、#16（GET /credit-results/:id）、#17（PUT /credit-results/:id）、#18（DELETE /credit-results/:id） | 代码只暴露 `GET /credits?order_id=N`（按订单过滤的列表），其余 CRUD 缺失；CreditResult 由 LoanOrderService.submit → autoApprove 内部创建（rules/scoring.ts:46-65） |
| **代码超出设计** | 2 | #23（GET /api/health）、#24（GET /api/orders/{id}/contract） | health 为工程惯例可默认接受；`/orders/{id}/contract` 是「详情/签约页」需要但未在 design REST 列表中显式声明的端点 |
| **等价但语义存疑** | 0 | — | 未发现路径/方法双匹配但语义不一致的情况 |

**统计校验**
- design 声明共 22 条 = 7（一致） + 11（形近变体） + 4（设计未实现）= **22 ✓**
- openapi.yaml 实现共 20 条 = 7（一致） + 11（形近变体） + 2（代码超出设计）= **20 ✓**

---

## 三、附：可疑点（与偏差表正交，仅作观察记录）

1. **路径段命名漂移**：design.md 全篇使用 `/loans`、`/credit-results`、`/config/rates`；代码使用 `/orders`、`/credits`、`/config/rate`。建议人工核对 design.md 的「数据流（主流程）」小节（如 `POST /loans/:id/submit` 等）与 routes/index.ts 实际声明的差异，并以代码为准回填 design.md（或反向修正代码）。
2. **CreditResult 实体半实现**：design 声明 5 个端点，代码仅实现 1 个（`GET /credits` 列表）。其余 4 个 CRUD 端点完全缺失；creditResult 的创建在 `LoanOrderService.submit` → `autoApprove` 中完成（rules/scoring.ts:46-65），并非通过 HTTP POST。若 product owner 期望 CreditResult 可独立管理（查看、修改、删除审批结果），则后端实现不完整。
3. **内部函数命名差异**：design.md 「数据流（主流程）」步骤 3 写「`creditService.approve()`」，但代码中实际函数为 `rules/scoring.ts:autoApprove()`，且 services/ 下没有 `creditService` 文件；说明 design.md 的「模块与职责」与代码存在演进漂移（design 设想 services/creditService.ts，代码合并到 rules/scoring.ts）。
4. **错误响应字段不统一**：validate 中间件与 routes/index.ts:handle() 返回 `{code: <number>, message: <string>}`；errorHandler（middleware/errorHandler.ts）返回 `{success: false, message: <string>}`。两份 schema 共存于 openapi.yaml 的 `ErrorResponse` 中，字段不冲突但表达不一致——客户端需做两套解析。
5. **GET /api/borrowers/{id} 的"伪成功"**：代码 `BorrowerService.get` 返回 `Borrower | undefined`，handle() 不抛 404——缺失 ID 时 HTTP 状态仍为 200，body.data 为 undefined。openapi.yaml 中该 op 未声明 404，与代码行为一致；但这是潜在 bug，建议在代码层补 404 或在 design.md 中明确"未找到时 200 + 空 data"约定。
6. **PUT /api/orders/:id 行为半 PUT 半 PATCH**：代码 `LoanOrderService.save` 对存在的 ID 调用 `store.updateOrder` 做浅合并（`{...existing, ...data, id}`），仅在 status === 'draft' 时允许，且将 status 重置为 'draft'。这与 HTTP PUT 的「整体替换」语义不完全相符，更接近 PATCH。openapi.yaml 沿用 PUT 名称，未做语义标注。
7. **请求体必填字段的依据**：本对照表与 openapi.yaml 中"required"列表仅来自 `middleware/validate.ts` 的显式 `if (!X)` 校验；其他可选字段（如 Borrower.income、employer、position）虽在 types.ts 定义但代码不强制必填，故未列入 required。

> **生成器说明**：openapi.yaml 由 `gen/extract_routes.cjs` 对 `backend/src/index.ts`、`backend/src/routes/*.ts`、`backend/src/types.ts` 纯正则解析生成，零 LLM 参与。中间件（validateBorrower / validateLoanOrder）的识别要求调用点形如 `router.METHOD(path, mw1, mw2, ..., handler)`，且 handler 必须是箭头函数（`=>`）或 `function(...)`；若工程改用 HOF（如 `createRouter({...})`）或装饰器，本提取器会失效。
