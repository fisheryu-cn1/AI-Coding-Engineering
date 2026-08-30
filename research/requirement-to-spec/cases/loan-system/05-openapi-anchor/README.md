# 05-openapi-anchor：OpenAPI 锚点实验（第 05 轮，2026-08-30）

验证备忘 §12.5-① 主张：**OpenAPI 作为第三个机器可读规格锚点**（继 UML-OWL、BDD 之后，接口侧）。pi 执行"代码→OpenAPI 程序化反向生成 + design.md↔OpenAPI 比对"，GLM 六项独立评审。

一句话结果：主张成立——35KB 零依赖脚本全自动生成 20 端点合规规格（byte-identical 可复跑）；比对显形 22 条设计声明中仅 7 条与代码一致（形近变体 11/未实现 4/代码超出 2），**全部为 04 轮 UML 通道不可见的发现**。

| 位置 | 内容 |
|---|---|
| `prompts/task-openapi.md` | pi 任务书（程序化提取红线/零编造红线/五类判定） |
| `raw/` | 输入：design.md（API 契约小节 22 条声明）+ 代码外部指针 |
| `gen/extract_routes.cjs` | pi 产出：纯正则零依赖提取脚本（方法选择与局限见头部注释） |
| `gen/openapi.yaml` | 脚本直接产物：OpenAPI 3.0.3，12 path/20 operation/10 schema，x-uncertain 3 处定义 |
| `gen/api-doc-code-diff.md` | 24 行逐条判定比对表+偏差汇总+7 条可疑点 |
| `review/E50-API对齐评审表.md` | **E 填写件**：AA1-01~24 对照+DA1~DA10 组级决策节（待人工：17 偏差行+10 决策） |
| `review/V00-INDEX.md` | 评审入口（本次待办+文件地图） |
| `reports/OpenAPI锚点实验报告.md` | **入口**：实验设计/评审六项/内容与方法双层结论/局限/§7 发现的组织化 |

发现速览：路径形近变体三组（/loans↔/orders、/credit-results↔/credits、/config/rates↔/rate——形近变体缺陷的第三种载体，前两种为 ID 变体与枚举子类化）；CreditResult 半实现（设计 5 端点→代码 1，派生实体 CRUD 取舍的待决策分歧）；行为级发现四条（伪成功 200/PUT 半 PATCH/错误双格式/creditService 模块漂移）。
