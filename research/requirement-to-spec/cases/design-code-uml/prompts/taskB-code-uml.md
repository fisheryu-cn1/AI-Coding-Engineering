你是代码结构分析员。任务：从实际代码提取完整 UML 模型（概念类图+状态机），方法直接取自代码真实签名。

输入（只读，排除 __tests__ 与 dist 目录）：
- 后端：D:\Users\Yu\Documents\Coding\giencoder-exam-P0151020\backend\src\（TypeScript/Express：types.ts 实体定义、services/ 四个服务、rules/ 评分与费率规则、store.ts、routes/、middleware/）
- 前端：D:\Users\Yu\Documents\Coding\giencoder-exam-P0151020\frontend\src\（Vue3+TS：api/、views/ 五个页面、router/）

输出两个文件：
1. D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\design-code-uml\formal\code-concept.puml —— 代码类图
2. D:\Users\Yu\Documents\Coding\AI-Coding-Engineering\research\requirement-to-spec\cases\design-code-uml\formal\code-flow.puml —— 状态机（若代码中有状态迁移逻辑）

提取规则：
1. **实体与类型**：types.ts 中的接口/类型 → 类（属性按代码真实定义）；数据库 store 层（store.ts）若承载实体操作则建模其方法。
2. **服务类**：services/ 下每个服务 → 类，方法**逐个取自代码真实导出函数**（+name(参数) : 返回值 格式，参数名可简化）；每个方法用注释行写实现摘要：' @logic <方法名>: <一两句实际实现逻辑，注明来源文件>。
3. **规则模块**：rules/ 的评分与费率逻辑 → 类或函数组，注明默认阈值/费率等常量的**实际代码值**。
4. **前端**：api/ 的接口客户端 → 类；views/ 页面提取其领域相关的状态与操作（组件内部 UI 细节不建模）；router 提取路由表为注释。
5. **枚举与常量**：代码中的枚举/字面量联合类型/常量集合（如状态值、用途值——注意查 purpose 字段的实际类型与校验）用 enum 建模；若代码中某字段是自由 string 且无枚举，如实建模为 string 并在注释注明。
6. **语法约定**：类定义必须带花括号；方法行 +name(args) : Ret；关联 A "1" --> "0..*" B : label。
7. **状态机**：找出代码中实际的状态迁移逻辑（如订单状态变更的函数/路由），完整建模为状态图，迁移标注触发函数名。

完成后输出：提取到的类清单（名称+方法数）、代码中 purpose 字段的实际类型与取值约束（如实报告）、状态机的实际状态集合与迁移，以及任何代码与常规模型不符的点。
