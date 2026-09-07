# intelli-metric 案例：UML 生成与 BDD 样板（2026-08-30；同日经人工审计修正为 v0.2）

> **v0.2（审计轮）**：用户对 v0.1 评审提出 6 主+9 次项缺口——经 E30 翻译审计逐条核实**全部成立零误报**，归因=提取缺失 13（其中 3 项根因=建模时未读全 02/03 文档）+混合 2+需求侧真缺口 1.5 处；模型已全部修正（+3 类+6 关联+2 状态机边）。详见 review/E30-翻译审计表.md。

> **任务**（用户指示）：用目前的 UML 生成方法为 intelli-metric 项目生成完整 UML 并制作 SVG，同时生成 BDD 样板供人工继续扩充。
> **项目现状**：智能化低代码数据指标分析平台（Python/FastAPI 六模块+React 前端），**backend 全部为占位 stub**——故本案例为**构造模式**（需求→UML→SVG→检查链），非代码提取模式。

## 产物导览

| 文件 | 内容 |
|---|---|
| `raw/` | 输入：需求梳理三份（01 总览与功能分解 / 02 权限设计 / 03 指标服务与监控，v0.1~v0.3）+ README |
| `formal/concept-req.puml` + `.svg` | **概念类图 v0.2**：七域 30 类+6 枚举（+DatabaseMetadata/BatchJob/AlertRule），**24 类含 63 个方法**（每方法带 @logic 逻辑摘要+来源 F/R 锚——方法梳理自需求动作语句与状态机迁移；被动数据类 FieldMetadata/OntologyEntity/Role 等无方法）；注解词表（@required/@pattern/@decision） |
| `formal/flow-metric.puml` + `.svg` | **指标版本生命周期状态机 v0.2**：五态 9 迁移（+修复回草稿边、处置恢复走重测双路径），口径变更=新版本个体 |
| `formal/concept-req.owl.rdf` / `.shacl.ttl` | puml2owl 确定性转换产物（33 类/27 关联） |
| `review/E30-翻译审计表.md` | 第 1 轮人工审计：15 项逐条评估+归因（评审=用户，评估执行=GLM） |
| `review/V00-INDEX.md` | 评审入口 |
| `review/T6-预期场景库.md` | **BDD 样板**：AI 样例 14 场景（主线 4/边界 5/异常 5，含 2 条审计驱动补充）+✍人工扩充区（六类 AI 覆盖不了的指引+模板行）——备忘 §12.2 三步生产模式第一步 |

## 检查状态（2026-08-30 首轮）

- fsm_check 五性质：**ALL_PROPERTIES_HOLD**（P1 可达/P2 共可达/P3 终态封闭/P4 无死锁/P5 禁回清单空）；
- puml2owl 转换（v0.2）：36 类/枚举+32 关联；**转换决定性 IDENTICAL**（两次运行 sha256 一致）；**方法补齐后转换产物 byte-identical 零变化**（方法行不进 OWL，方法维度属 LLM 语义岗——method/13 分层）；
- HermiT 一致性：**consistent**（48 类含推理派生）；
- SHACL 实例闭包：未跑（ABox 断言样本属 S4 检查循环，待案例进入全链检验时补）。

## 建模中的 @decision 清单（待项目方确认，Z_真 显式化；v0.2 更新）

> v0.2 变化：撤销 1 项（paused 恢复验证——F-SV-02 第 5 步已明确，按双路径建模）；新增 3 项（图谱 metric 级=需求盲区显式化/修复定义版本语义/统计项可选）。

1. **状态挂 MetricVersion 而非 MetricDefinition**（F-LC-04 多版本并存+R-M-3 权限随指标实体继承——生命周期挂版本、权限挂定义）；
2. **服务降级=MonitorFlag 运行期标记而非状态机状态**（R-MON-1"恢复后自动解除"为可逆监控信号 vs paused 为管理动作）；
3. **delisted 为版本个体终态，"重新上架"=定义层新版本个体**（F-LC-06 原图下架无出边；保守路径，IM-SC12 场景可反证）；
4. **paused→published 恢复为轻量直连**（F-LC-07"处置后需重新试算/测试验证方可恢复"的严格读应经 testing）；
5. 凭据建模为 DataSource 属性（非独立类）；组织节点 Principal 为预留。

> 以上 3/4 与 T6 人工扩充指引第 4 条一一对应——决策确认后各补一条场景（决策与场景互驱）。
