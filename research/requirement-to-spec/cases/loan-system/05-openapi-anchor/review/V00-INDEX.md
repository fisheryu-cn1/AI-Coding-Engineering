# 评审入口（V00-INDEX，05-openapi-anchor）

> API 对齐评审位（检查项 8，method/14/16 §3.1）。机器区已由第 35 场比对结果转制（GLM 独立对账零分歧），等待人工评审。

## 本次待办（第 1 轮，2026-08-30 建）

- **待评审行 17**（偏差行；判定=一致的 7 行免评）：E50 表 AA1-06~18、AA1-21~24
- **待裁决决策节 10**：DA1 订单资源命名（8 行组）/ DA2 审批结果命名 / DA3 费率命名（2 行组）/ DA4 CreditResult 写操作取舍（4 行组）/ DA5 contract 端点归属 / DA6 health 豁免 / DA7 伪成功响应 / DA8 PUT 半 PATCH / DA9 错误双格式 / DA10 creditService 模块漂移
- 全部裁决并执行后：重跑 `extract_routes.cjs` + 比对重生（回归签收，method/16 §3.1 第 6 条）

## 文件地图

| 文件 | 性质 | 说明 |
|---|---|---|
| [E50-API对齐评审表.md](E50-API对齐评审表.md) | **E（填写件）** | AA1-01~24 对照表+DA1~DA10 决策节；人工区待填 |
| [../gen/api-doc-code-diff.md](../gen/api-doc-code-diff.md) | G（生成物，只读） | 比对工作副本（LLM 辅助生成+GLM 复核）；E50 机器区的来源 |
| [../gen/openapi.yaml](../gen/openapi.yaml) | G（生成物，只读） | 代码反向生成规格（extract_routes.cjs 直接产物，byte-identical） |
| [../gen/extract_routes.cjs](../gen/extract_routes.cjs) | G（工具，只读） | 反向生成脚本（收编 tools/ 候选） |
| [../raw/design.md](../raw/design.md) | raw（只读） | 被评审的 API 契约源（"REST 接口"小节） |
| [../reports/OpenAPI锚点实验报告.md](../reports/OpenAPI锚点实验报告.md) | 报告（只读） | 实验全过程+六项评审+结论 |

## 与群内其他评审位的关系

01-fullchain 的 review/（E30 翻译审计/E41 决策记录）管需求→模型链；本目录管设计契约→代码链（检查位 8 独有）。决策 ID 命名空间跨轮全局唯一（DA-* 为 API 对齐域专用前缀）。
