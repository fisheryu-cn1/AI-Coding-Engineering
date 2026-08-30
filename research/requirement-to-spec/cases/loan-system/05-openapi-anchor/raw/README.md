# raw/：实验输入（2026-08-30 复制）

- design.md：原交付设计文档（175 行，与 04 轮同一输入；API 契约在"REST 接口（前缀 `/api`）"小节——4 组共 22 条 method+path 声明）
- 代码（外部指针，不复制）：`D:\Users\Yu\Documents\Coding\giencoder-exam-P0151020\backend\src\`（TypeScript/Express；路由集中在 `routes/index.ts`+`routes/health.ts`，挂载 `app.use('/api', router)` 于 `index.ts:21`，health 二级挂载 `router.use('/health', healthRouter)` 于 `routes/index.ts:20`）
- 实验设计（用户指示）：pi 执行"代码→OpenAPI 程序化反向生成 + design.md↔OpenAPI 比对"，GLM 评审（独立 grep 对账作第二通道）——验证备忘 §12.5-①"OpenAPI 第三规格锚点"主张
