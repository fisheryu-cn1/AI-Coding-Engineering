# 个人消费贷款管理系统 技术设计

## 输入依据

| Artifact | Path |
| --- | --- |
| 源需求登记 | deliveries/个人消费贷款管理系统/requirements-register.md |
| PRD | deliveries/个人消费贷款管理系统/prd.md |
| 用户故事 | deliveries/个人消费贷款管理系统/user-stories.md |
| 项目入口文档 | README.md |
| 后端脚手架 | backend/（Express + TypeScript） |
| 前端脚手架 | frontend/（Vue3 + Vite + TypeScript） |

## 项目上下文

| 项目项 | 结论 | 来源 |
| --- | --- | --- |
| 后端框架 | Express 5 + TypeScript（CommonJS），入口 backend/src/index.ts，路由聚合 backend/src/routes/index.ts | backend/package.json、backend/src/index.ts |
| 前端框架 | Vue 3 + Vite + TypeScript，入口 frontend/src/main.ts，根组件 frontend/src/App.vue | frontend/package.json、frontend/src/main.ts |
| 数据库 | 需引入 MySQL 8.0+，当前脚手架未配置数据库驱动/ORM | backend/.env.example |
| 前端路由/状态/请求 | 当前脚手架未引入 Vue Router / Pinia / Axios / Element Plus | frontend/package.json |
| 推荐技术栈 | Vue 3 + Element Plus + Node.js + Express + MySQL 8.0+ | 考试任务说明 |

## 实现范围

### 范围内
- 后端：Borrower / LoanOrder / CreditResult 三实体 CRUD 接口；自动审批评分逻辑；状态机约束；评分规则与费率配置表；接口基础校验；级联删除。
- 前端：申请分步表单（含草稿）、列表查询（关键字）、详情查看、电子签约费率展示、订单完成状态处理。
- 数据：MySQL 初始化 SQL 脚本（含示例数据）。
- 工程：前后端 npm install / npm run build 通过；README。

### 范围外
- 复杂审批链、规则引擎、自动任务、电子签章组件、文件预览、导出报表、多层级统计。操作员人工通过/驳回环节（自动审批即生效）。

## 方案设计

### 模块与职责

**后端（backend/src）**
- `index.ts`：Express 应用入口，注册中间件与路由。
- `db.ts`：MySQL 连接池（mysql2/promise），读取环境变量配置。
- `routes/`：按实体拆分路由——`borrower.ts`、`loanOrder.ts`、`creditResult.ts`、`config.ts`（评分规则与费率配置）、`health.ts`。
- `controllers/`：各路由对应的业务处理，调用 service 层。
- `services/`：业务逻辑——`borrowerService.ts`、`loanOrderService.ts`（含状态机校验、级联删除）、`creditService.ts`（自动审批评分）、`configService.ts`（评分规则/费率读取）。
- `middleware/`：`errorHandler.ts`（现有）、`validate.ts`（请求体基础校验）。
- `rules/`：`scoring.ts`（评分规则计算，从配置读取指标/权重/阈值）、`rates.ts`（费率配置默认值）。

**数据库（表）**
- `borrower`：id、name、id_number、phone、income、employer、position。
- `loan_order`：id、borrower_id、amount、term_months、purpose、interest_rate、status（draft/pending/approved/rejected/active/closed）。
- `credit_result`：id、order_id、score、approved_amount、approved_rate、decision、decision_reason。
- `approval_config`（评分规则参数化配置）：指标、权重、通过阈值。
- `rate_config`（费率配置）：年化利率、服务费、逾期罚息。
- `order_log`（处理意见记录）：order_id、action、comment、created_at。

**前端（frontend/src）**
- `main.ts`：注册 Vue Router、Element Plus、Axios。
- `router/index.ts`：路由配置。
- `api/`：Axios 实例与各模块接口封装（`borrower.ts`、`loanOrder.ts`、`creditResult.ts`、`config.ts`）。
- `views/`：页面——`BorrowerList.vue`、`BorrowerForm.vue`（分步表单）、`BorrowerDetail.vue`、`LoanOrderList.vue`、`LoanOrderDetail.vue`、`ContractSign.vue`（电子签约）、`ApprovalConfig.vue`（评分规则配置）。
- `components/`：公共组件（表单步骤条、费率展示等）。

### 接口、数据流或事件流

**REST 接口（前缀 `/api`）**
- Borrower：`GET/POST /borrowers`、`GET/PUT/DELETE /borrowers/:id`。
- LoanOrder：`GET/POST /loans`、`GET/PUT/DELETE /loans/:id`、`POST /loans/:id/sign`（签署）、`POST /loans/:id/complete`（完成）；提交申请 `POST /loans/:id/submit`。
- CreditResult：`GET/POST /credit-results`、`GET/PUT/DELETE /credit-results/:id`。
- Config：`GET/PUT /config/approval`（评分规则）、`GET/PUT /config/rates`（费率）。

**数据流（主流程）**
1. 前端分步表单录入 → 保存草稿（draft）`POST /loans`。
2. 提交申请 `POST /loans/:id/submit` → 状态转 pending。
3. 后端触发自动审批 `creditService.approve()` → 读评分规则配置计算分数 → 通过则生成 CreditResult 且订单转 approved；拒绝则生成 decision=拒绝及 reason 且订单转 rejected（自动审批即生效）。
4. 详情/签约页读取订单与费率 → 申请人确认签署 `POST /loans/:id/sign` → 订单转 active。
5. 操作员完成处理 `POST /loans/:id/complete` → 订单转 closed，记录处理意见。

### 状态流与边界情况

- 状态机：`draft → pending →（自动审批）approved/rejected → active → closed`。
- draft 为起始点，未提交不入审批。
- rejected 为终态，不可回流 pending。
- 非法流转（如 pending→closed、rejected→pending）由 service 层状态机校验拒绝。
- 删除可针对所有状态；删除 loan_order 时级联删除 credit_result 与 order_log。
- 自动审批即生效，无操作员人工通过/驳回环节。

### 权限、审计、安全或合规

- 基础输入校验：金额>0、期限为正整数、身份证号/电话格式、必填项。
- 处理意见记录（order_log）：订单状态变化时写入 action 与 comment。
- 本次最小闭环不引入登录认证，前端直接访问业务接口（范围外项）。

### 配置、数据迁移或兼容性

- 环境变量：后端 `.env` 增加 `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`。
- 提供 `sql/init.sql`：建表 + 示例数据 + 默认评分规则/费率配置。
- 评分规则与费率以配置表维护（参数化），提供默认合理值。

### 错误处理与恢复

- 复用现有 `errorHandler.ts` 全局错误处理，返回统一错误结构。
- validate 中间件返回 400 与字段错误提示。
- 数据库连接失败由连接池错误处理，接口返回 500。

## 设计元素清单

| 设计元素 ID | 类型 | 名称 | 所属模块 | 来源需求 ID | 关联用户故事/验收场景 | 是否需要实现 | 是否需要验证 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DE-01 | 后端 | db.ts（MySQL 连接池） | 后端 | DEL-001、NFR-001 | US-008/AC-012 | 是 | 是 | mysql2 连接池 |
| DE-02 | 后端 | borrower 路由+服务 | 后端 | FUNC-001、FIELD-001 | US-001/AC-001,AC-002,AC-003 | 是 | 是 | Borrower CRUD |
| DE-03 | 后端 | loanOrder 路由+服务 | 后端 | FUNC-001、FUNC-002、FIELD-002、FLOW-001 | US-001/AC-001,AC-003、US-003/AC-006、US-006/AC-010 | 是 | 是 | LoanOrder CRUD+状态机+级联删除 |
| DE-04 | 后端 | creditResult 路由+服务 | 后端 | FUNC-002、FIELD-003 | US-004/AC-008 | 是 | 是 | CreditResult CRUD |
| DE-05 | 后端 | scoring 评分规则 | 后端 | RULE-001 | US-004/AC-008 | 是 | 是 | 自动审批评分 |
| DE-06 | 后端 | config 路由+服务 | 后端 | RULE-001、RULE-004 | US-004/AC-008、US-005/AC-009 | 是 | 是 | 评分规则/费率配置 |
| DE-07 | 后端 | validate 校验中间件 | 后端 | RULE-002 | US-002/AC-005、US-003/AC-007 | 是 | 是 | 基础校验 |
| DE-08 | 后端 | order_log 处理意见 | 后端 | FLOW-002 | US-006/AC-010 | 是 | 是 | 状态变化记录 |
| DE-09 | 数据库 | 建表+示例 SQL | 数据 | DEL-001 | US-008/AC-013 | 是 | 是 | sql/init.sql |
| DE-10 | 前端 | router 路由配置 | 前端 | FUNC-001、FUNC-002、FUNC-003 | US-001~US-006 | 是 | 是 | Vue Router |
| DE-11 | 前端 | api Axios 封装 | 前端 | FUNC-001、FUNC-002、FUNC-003 | US-001~US-006 | 是 | 是 | 接口调用 |
| DE-12 | 前端 | BorrowerForm 分步表单 | 前端 | UI-001、RULE-002 | US-002/AC-004,AC-005 | 是 | 是 | 分步填写+草稿+必填 |
| DE-13 | 前端 | BorrowerList 列表 | 前端 | UI-002、UI-003 | US-001/AC-002 | 是 | 是 | 关键字查询 |
| DE-14 | 前端 | BorrowerDetail 详情 | 前端 | UI-004 | US-001/AC-001 | 是 | 是 | 详情查看 |
| DE-15 | 前端 | ContractSign 电子签约 | 前端 | FUNC-003、RULE-004、UI-004 | US-005/AC-009 | 是 | 是 | 费率展示+签署 |
| DE-16 | 前端 | LoanOrderDetail 状态处理 | 前端 | FLOW-001、FLOW-002 | US-006/AC-010 | 是 | 是 | 完成处理 |
| DE-17 | 前端 | ApprovalConfig 评分规则配置 | 前端 | RULE-001 | US-004/AC-008 | 是 | 是 | 参数化配置 |
| DE-18 | 文档 | README 更新 | 交付物 | DEL-002 | US-008/AC-013 | 是 | 是 | 环境/启动/页面入口 |

## 需求到设计映射

| 需求 ID | 用户故事/验收场景 | 设计承接 | 影响文件或模块 |
| --- | --- | --- | --- |
| FUNC-001 | US-001/AC-001,AC-002,AC-003 | DE-02、DE-03、DE-10~14 | borrower/loanOrder 路由、前端列表/表单/详情 |
| FUNC-002 | US-003/AC-006、US-004/AC-008 | DE-03、DE-04、DE-05、DE-06 | loanOrder/creditResult、scoring、config |
| FUNC-003 | US-005/AC-009、US-006/AC-010 | DE-03、DE-08、DE-15 | loanOrder 签署/完成、order_log、ContractSign |
| FIELD-001 | US-001/AC-001 | DE-02、DE-09 | borrower 表 |
| FIELD-002 | US-001/AC-001 | DE-03、DE-09 | loan_order 表 |
| FIELD-003 | US-004/AC-008 | DE-04、DE-09 | credit_result 表 |
| RULE-001 | US-004/AC-008 | DE-05、DE-06、DE-17 | scoring、config、ApprovalConfig |
| RULE-002 | US-002/AC-005、US-003/AC-007 | DE-07、DE-12 | validate、BorrowerForm |
| RULE-004 | US-005/AC-009 | DE-06、DE-15 | rate_config、ContractSign |
| FLOW-001 | US-006/AC-010、US-007/AC-011 | DE-03 | loanOrder 状态机 |
| FLOW-002 | US-006/AC-010 | DE-08 | order_log |
| UI-001 | US-002/AC-004 | DE-12 | BorrowerForm 分步+草稿 |
| UI-002 | US-001/AC-002 | DE-13 | BorrowerList 关键字查询 |
| UI-003 | US-003/AC-006 | DE-13 | 列表查询新记录 |
| UI-004 | US-005/AC-009 | DE-14、DE-15 | 详情页 |
| NFR-001 | US-008/AC-012 | DE-01、DE-10~18 | 前后端构建 |
| DEL-001 | US-008/AC-013 | DE-09 | sql/init.sql |
| DEL-002 | US-008/AC-013 | DE-18 | README |

## 测试与验证设计

| 用户故事/验收场景 | 验证方式 | 提交前是否必须验证 | 说明 |
| --- | --- | --- | --- |
| US-001/AC-001 | cross_boundary_e2e | 是 | 申请 CRUD 主链路 |
| US-001/AC-002 | cross_boundary_e2e | 是 | 关键字查询 |
| US-001/AC-003 | service_api | 是 | 级联删除 |
| US-002/AC-004 | cross_boundary_e2e | 是 | 分步+草稿 |
| US-002/AC-005 | cross_boundary_e2e | 是 | 必填提示 |
| US-003/AC-006 | cross_boundary_e2e | 是 | 提交转 pending |
| US-003/AC-007 | service_api | 是 | 后端字段校验 |
| US-004/AC-008 | service_integration | 是 | 自动审批评分 |
| US-005/AC-009 | cross_boundary_e2e | 是 | 合同费率+签署 |
| US-006/AC-010 | service_api | 是 | 自动审批即生效+完成+意见 |
| US-007/AC-011 | service_api | 是 | 状态机非法流转拒绝 |
| US-008/AC-012 | unit（构建） | 是 | npm install/build |
| US-008/AC-013 | component | 是 | SQL/README 检查 |

## 风险与开放问题

| 项目 | 关联需求 ID | 影响 | 下一步动作 | 是否阻断开发计划 |
| --- | --- | --- | --- | --- |
| 评分规则默认阈值/权重取值 | RULE-001 | M2 评分决策默认行为 | 实现时提供默认评分模型（如收入占比、负债率、通过阈值 60） | 否 |
| 固定费率默认值 | RULE-004 | 合同费率展示默认值 | 实现时提供默认费率配置（年化利率、服务费、逾期罚息） | 否 |
| 需新增依赖（mysql2、Vue Router、Axios、Element Plus） | NFR-001 | 依赖安装 | 实现阶段安装并验证 npm install/build | 否 |
| 数据库连接环境变量 | DEL-001 | 后端启动 | 配置 .env 与 SQL 脚本 | 否 |