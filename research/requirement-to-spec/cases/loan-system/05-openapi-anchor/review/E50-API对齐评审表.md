# E50-API 对齐评审表（第 1 轮，AA1-）

> **这是什么**：设计文档 design.md 的 API 接口声明 ↔ 代码实现（OpenAPI 反向生成物 `gen/openapi.yaml`）的逐条对照评审表。机器区由比对结果转制（2026-08-30，来源 gen/api-doc-code-diff.md，GLM 独立对账零分歧）；人工区（✍ 三列）由评审者填写。
> **条目锚说明**：原交付 design.md 的接口声明无 EP 编号，本表用位置锚（原文摘录），design.md 变更后须按原文摘录重对齐——新项目应先给接口声明编号（EP-xx，method/16 §3.1 两级规则）。
> **评审范围**：判定=`一致` 的行默认免评（机器判定，重生成即复核）；**偏差行（形近变体/未实现/超出/存疑）必评**，按"关联决策"列进组级决策节（DA-x）落决策后回填行内执行标记。行为级发现（L2）不入表、直接进决策节。
> **决策出口三分支**（method/16 §3.1）：回写设计文档 / 修改代码 / 豁免登记。本案例代码为外部原交付不可改——"修改代码"分支降级为"登记为已决策偏差，反馈交付方"。

## 对照表（24 行：design 声明 22 + 代码超出 2）

| 行ID | design 声明(原文摘录) | OpenAPI method+path | 判定 | 证据锚 | 关联决策 | ✍评审结论 | ✍执行标记 | ✍签注 |
|---|---|---|---|---|---|---|---|---|
| AA1-01 | `GET /borrowers` | `GET /api/borrowers` | 一致 | openapi.yaml:26; routes/index.ts:33 | — | | | |
| AA1-02 | `POST /borrowers` | `POST /api/borrowers` | 一致 | openapi.yaml:48; routes/index.ts:39 | — | | | |
| AA1-03 | `GET /borrowers/:id` | `GET /api/borrowers/{id}` | 一致 | openapi.yaml:77; routes/index.ts:36 | DA7 | | | |
| AA1-04 | `PUT /borrowers/:id` | `PUT /api/borrowers/{id}` | 一致 | openapi.yaml:106; routes/index.ts:42 | — | | | |
| AA1-05 | `DELETE /borrowers/:id` | `DELETE /api/borrowers/{id}` | 一致 | openapi.yaml:141; routes/index.ts:45 | — | | | |
| AA1-06 | `GET /loans` | `GET /api/orders` | 形近变体(路径段 loans→orders) | openapi.yaml:375; routes/index.ts:50 | DA1 | | | |
| AA1-07 | `POST /loans` | `POST /api/orders` | 形近变体(loans→orders) | openapi.yaml:403; routes/index.ts:56 | DA1 | | | |
| AA1-08 | `GET /loans/:id` | `GET /api/orders/{id}` | 形近变体(loans→orders) | openapi.yaml:446; routes/index.ts:53 | DA1 | | | |
| AA1-09 | `PUT /loans/:id` | `PUT /api/orders/{id}` | 形近变体(loans→orders) | openapi.yaml:481; routes/index.ts:59 | DA1+DA8 | | | |
| AA1-10 | `DELETE /loans/:id` | `DELETE /api/orders/{id}` | 形近变体(loans→orders) | openapi.yaml:536; routes/index.ts:74 | DA1 | | | |
| AA1-11 | `POST /loans/:id/sign` | `POST /api/orders/{id}/sign` | 形近变体(loans→orders) | openapi.yaml:661; routes/index.ts:65 | DA1 | | | |
| AA1-12 | `POST /loans/:id/complete` | `POST /api/orders/{id}/complete` | 形近变体(loans→orders) | openapi.yaml:572; routes/index.ts:68 | DA1 | | | |
| AA1-13 | `POST /loans/:id/submit` | `POST /api/orders/{id}/submit` | 形近变体(loans→orders) | openapi.yaml:703; routes/index.ts:62 | DA1 | | | |
| AA1-14 | `GET /credit-results` | `GET /api/credits` | 形近变体(credit-results→credits) | openapi.yaml:329; routes/index.ts:79 | DA2 | | | |
| AA1-15 | `POST /credit-results` | —（代码无此路由） | 设计未实现 | routes/index.ts 无对应行；创建内化于 rules/scoring.ts:41 autoApprove | DA4 | | | |
| AA1-16 | `GET /credit-results/:id` | —（代码无此路由） | 设计未实现 | 仅有 GET /credits?order_id=N 过滤列表 | DA4 | | | |
| AA1-17 | `PUT /credit-results/:id` | —（代码无此路由） | 设计未实现 | 同上 | DA4 | | | |
| AA1-18 | `DELETE /credit-results/:id` | —（代码无此路由） | 设计未实现 | 同上 | DA4 | | | |
| AA1-19 | `GET /config/approval` | `GET /api/config/approval` | 一致 | openapi.yaml:221; routes/index.ts:84 | — | | | |
| AA1-20 | `PUT /config/approval` | `PUT /api/config/approval` | 一致 | openapi.yaml:243; routes/index.ts:87 | — | | | |
| AA1-21 | `GET /config/rates` | `GET /api/config/rate` | 形近变体(复数 rates→单数 rate) | openapi.yaml:275; routes/index.ts:90 | DA3 | | | |
| AA1-22 | `PUT /config/rates` | `PUT /api/config/rate` | 形近变体(rates→rate) | openapi.yaml:297; routes/index.ts:93 | DA3 | | | |
| AA1-23 | —（design 未声明） | `GET /api/health` | 代码超出设计 | openapi.yaml:352; routes/health.ts:8 | DA6 | | | |
| AA1-24 | —（design 未声明，但"数据流"小节叙述隐含） | `GET /api/orders/{id}/contract` | 代码超出设计 | openapi.yaml:625; routes/index.ts:71 | DA5 | | | |

**统计**：一致 7 / 形近变体 11 / 设计未实现 4 / 代码超出设计 2；待评审行 = 17（一致行免评）；待决策决策节 = 10（DA1–DA10）。

---

## DA 组级决策节（八行语法：前三机器区、后五人工区；结论未决策必须留空）

## DA1 订单资源路径命名（AA1-06~13，8 行）
- 决策要求: design.md 接口清单把贷款订单资源命名为 `/loans`（8 个端点全组），代码实现为 `/api/orders`。两者语义同指"贷款订单"（LoanOrder 实体），仅资源命名不同。需要决定哪一侧是权威命名：选项 A=以代码为准回写 design.md（8 处 loans→orders）；选项 B=以设计为准修改代码路由（本案不可改，登记为已决策偏差并反馈交付方）；选项 C=其他命名（需给出理由）。决策时注意：design.md"数据流"小节的叙述（如 `POST /loans/:id/submit`）与接口清单同用 loans，回写需两处同步。
- 机器执行: [决策后执行: 按结论回写 design.md 接口清单+数据流小节（选项 A），或登记偏差反馈（选项 B）] 
- 证据依据: 第 35 场比对（gen/api-doc-code-diff.md #6–#13；GLM 独立 grep 对账同判）；命名漂移为跨主体系统性现象（03 轮 ID 变体 FULC/FOW 同类）。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA2 审批结果资源命名（AA1-14）
- 决策要求: design.md 命名 `/credit-results`（审批结果），代码为 `/api/credits`（仅 1 个列表端点）。命名差异不止单复数（credit-results 是复合词、credits 是缩略），需决策权威命名并与 DA4 联动考虑（若 DA4 决策大幅收窄 CreditResult 的接口面，命名影响的端点数随之变小）。选项 A=回写 design.md 为 credits；B=登记偏差反馈代码改名；C=其他。
- 机器执行: [决策后执行: 回写 design.md 或登记偏差；与 DA4 联动展开]
- 证据依据: 第 35 场比对 #14；gen/api-doc-code-diff.md 可疑点 3。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA3 费率配置路径命名（AA1-21~22）
- 决策要求: design.md 写 `/config/rates`（复数），代码为 `/api/config/rate`（单数），GET/PUT 两端点。纯单复数差异，语义无歧义。选项 A=回写 design.md 为 rate（改动最小）；B=登记偏差反馈代码改 rates；C=其他。
- 机器执行: [决策后执行: 回写 design.md 两处或登记偏差]
- 证据依据: 第 35 场比对 #21–#22。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA4 CreditResult 写操作取舍（AA1-15~18，4 行）
- 决策要求: design.md 声明审批结果（CreditResult）具备全套 CRUD：POST 创建、按 ID 查询/修改/删除；代码只实现 1 个只读列表（GET /credits，支持 order_id 过滤），创建动作内化在提交流程（submit→autoApprove 自动生成），修改/删除完全缺失。两头各有道理：审批结果是系统派生数据，人工 POST 创建在语义上本就可疑（代码方向可能更合理）；但 PUT/DELETE 缺失意味着审批结果不可修正、不可删除——若业务要求纠错能力（如误判复核后重审），则是实现缺口。需要需求方决策：选项 A=确认收窄（回写 design.md 删除 4 条声明，派生数据只读——需确认"误判纠错"走什么路径，如重走提交流程）；B=确认缺口（登记偏差反馈交付方补实现）；C=部分保留（如仅补按 ID 查询）。此为设计未表态的分歧点，方法价值在显形而非预设对错。
- 机器执行: [决策后执行: 回写 design.md 删/改声明，或登记偏差；结论涉需求语义时同步检查需求侧条目是否需补充（登记表 FUNC 体系）]
- 证据依据: 第 35 场比对 #15–#18；rules/scoring.ts:41 autoApprove 为创建唯一路径；gen/api-doc-code-diff.md 可疑点 2。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA5 contract 端点归属（AA1-24）
- 决策要求: 代码实现了 `GET /api/orders/{id}/contract`（签约页合同详情，services/orderFlowService.ts contractDetail），design.md 接口清单未列出，但"数据流（主流程）"第 4 步叙述（详情/签约页读取订单与费率）隐含了它。决策：选项 A=回写 design.md 接口清单补此端点（推荐——叙述已有依据）；B=认定越权实现（登记偏差）。同时暴露模板级问题：接口声明存在"清单+叙述"双源时清单级比对会漏隐含项——处置意见请一并给出（如"接口只在清单声明、叙述引用清单"入设计模板规约）。
- 机器执行: [决策后执行: 回写 design.md 清单；模板意见并入 method/12 候选]
- 证据依据: 第 35 场比对 #24；design.md"数据流"小节第 4 步。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA6 health 端点豁免（AA1-23）
- 决策要求: 代码实现 `GET /api/health`（健康检查），design.md 未声明。运维惯例接口通常不入业务设计文档。决策：选项 A=豁免登记（本表记录在案即可，不改文档——推荐）；B=回写 design.md 补运维接口小节。
- 机器执行: [决策后执行: 若选 A 仅落本节结论；若选 B 回写 design.md]
- 证据依据: 第 35 场比对 #23；routes/health.ts:8（注：pi 比对表原引 routes/index.ts:28 为行号误差，实际挂载在 routes/index.ts:22）。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA7 缺失资源的伪成功响应（行为级，关联 AA1-03 等 GET by id）
- 决策要求: GET /api/borrowers/{id}（及同类按 ID 查询）在资源不存在时返回 HTTP 200 且 body.data 为 undefined（borrowerService.get 返回 undefined、handle() 包装不抛 404），openapi.yaml 未声明 404。这是 API 行为级缺陷候选：客户端无法凭状态码区分"存在/不存在"。决策处置：A=登记偏差反馈交付方（补 404 或在 design 明确"200+空 data"约定）；B=认定为约定（回写 design.md 明确该行为）。注意此发现超出 API 对齐比对的结构层，属行为级（L2）——规则化检查不可达，由深读/运行时测试发现。
- 机器执行: [决策后执行: 登记偏差或回写约定；若修 openapi.yaml 需先改代码（本案不可改）]
- 证据依据: gen/api-doc-code-diff.md 可疑点 5；GLM 抽查源码属实（services/borrowerService.ts:9-11）。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA8 PUT 端点的半 PATCH 语义（行为级，关联 AA1-09）
- 决策要求: PUT /api/orders/{id} 实现为浅合并（{...existing, ...data}）且强制把 status 重置为 'draft'（loanOrderService.save），仅 draft 状态允许编辑。与 HTTP PUT 的"整体替换"语义不符（更接近 PATCH），且 status 重置是隐式副作用（客户端未知）。决策：A=登记偏差（语义+副作用两项反馈交付方）；B=认定为约定（回写 design.md"PUT=草稿部分更新+状态保持 draft"）。
- 机器执行: [决策后执行: 登记偏差或回写约定]
- 证据依据: gen/api-doc-code-diff.md 可疑点 6；GLM 抽查源码属实（services/loanOrderService.ts:22-37）。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA9 错误响应格式不统一（行为级）
- 决策要求: 错误响应存在两种格式：validate/handle 路径返回 {code: <数字>, message}，errorHandler 中间件返回 {success: false, message}（middleware/errorHandler.ts:15-18）。openapi.yaml 的 ErrorResponse schema 已同时包含两者字段。客户端需做两套解析。决策：A=登记偏差（反馈交付方统一格式）；B=认定现状（ErrorResponse 保持双字段，注明解析约定）。
- 机器执行: [决策后执行: 登记偏差或注明约定]
- 证据依据: gen/api-doc-code-diff.md 可疑点 4；GLM 抽查源码属实。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 

## DA10 creditService 模块漂移（行为级/文档回写）
- 决策要求: design.md"数据流"第 3 步写 `creditService.approve()`，代码中不存在 creditService（services/ 下为 borrower/config/loanOrder/orderFlow 四服务），自动审批逻辑实际在 rules/scoring.ts 的 autoApprove 函数（第 41 行起）。属设计文档的模块组织描述与实现漂移。决策：A=回写 design.md（数据流第 3 步改为 scoring.autoApprove 并修正模块叙述）；B=登记偏差。
- 机器执行: [决策后执行: 回写 design.md 数据流小节或登记偏差]
- 证据依据: gen/api-doc-code-diff.md 可疑点 3；GLM 抽查属实（services/ 目录清单+rules/scoring.ts:41）。
- 状态: 待决策(第1轮)
- 结论: 
- 附记: 
- 签注: 
- 沿革: 
