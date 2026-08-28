# 模型绑定清单（kbapp-review）

> 需求 ID 系 = raw/01（FR-x.y/NFR-x）。定位符语法同 method/13 §7。检查命令：
> `python tools/scripts/check_model_bindings.py cases/kbapp-review --id-regex 'FR-\d+(?:\.\d+)?' --register cases/kbapp-review/raw/01-功能需求文档.md`

## 豁免政策（policy）

| 范围 | 类型 | 理由 |
|---|---|---|
| FR-1.6 | 逐条豁免 | 原文跳转=UI 交互行为 |
| FR-1.7 | 逐条豁免 | 缓存策略=实现优化（注：cache JSON Schema 本次已补建 concept-05-api 侧，可后续转正） |
| FR-2.5 | 逐条豁免 | 比较分析=检索服务组合（kb_compare 接口域，非结构语义） |
| FR-2.6 | 逐条豁免 | 可视化=前端域 |
| FR-6.1 | 逐条豁免 | 来源配置=配置文件域 |
| NFR-* | 前缀豁免 | 非功能约束（工程验收域）；NFR-4 时延缺验证已记报告 |

| FR-1 | 逐条豁免 | 组标题（子条目 FR-1.1~1.8 承载） |
| FR-2 | 逐条豁免 | 组标题（子条目承载） |
| FR-3 | 逐条豁免 | 组标题（子条目承载） |
| FR-4 | 逐条豁免 | 组标题（子条目承载） |
| FR-5 | 逐条豁免 | 组标题（子条目承载） |
| FR-6 | 逐条豁免 | 组标题（子条目承载） |

## 绑定表（bindings）

| 需求ID | 工件 | 元素定位符 | 说明 |
|---|---|---|---|
| FR-1.1 | formal/concept-05-api.puml | interface:Parser | 五格式解析契约 |
| FR-1.2 | formal/concept-01.puml | enum:DocType | 六类文档（开放 Topic 见 KD-1） |
| FR-1.3 | formal/concept-03.puml | attr:Section.section_path | 章节结构化 |
| FR-1.4 | formal/concept-05-graph.puml | attr:Section.summary | 章节级摘要属性 |
| FR-1.5 | formal/concept-03.puml | attr:Document.sha256 | 元数据登记 |
| FR-1.8 | formal/concept-05-graph.puml | attr:Document.summary_path | curated 复用绑定 |
| FR-2.1 | formal/concept-03.puml | enum:EntityType | 实体六类 |
| FR-2.2 | formal/concept-03.puml | enum:EntityType | 消歧弱化已记（N3——D15-13 碰撞去重，见三层报告） |
| FR-2.3 | formal/concept-03.puml | assoc:ABOUT_TOPIC | 主题索引 |
| FR-2.4 | formal/concept-05-api.puml | interface:GraphStore | 关联阅读查询支撑（shortest_path） |
| FR-2.7 | formal/rules-03.py | z3tag:P4I_交集语义 | 成本约束 |
| FR-3.1 | formal/concept-03.puml | enum:RetrMode | 检索四模式 |
| FR-3.2 | formal/concept-05-api.puml | class:Hit | 上下文组装产物（anchor 锚点=FR-3.5） |
| FR-3.3 | formal/concept-05-graph.puml | attr:Document.summary_l1 | 分层供给 L1/L2 |
| FR-3.4 | formal/flow-03.puml | trans:pending&gt;accepted | MCP 服务支撑（Inbox 流为代表；工具清单属接口域） |
| FR-3.5 | formal/concept-05-api.puml | attr:Hit.anchor | 溯源锚点 |
| FR-4.1 | formal/flow-03.puml | trans:indexed&gt;tombstoned | 变更检测四情形 |
| FR-4.2 | formal/concept-05.puml | enum:ExtractStatus | 增量处理状态 |
| FR-4.3 | formal/flow-05.puml | trans:new&gt;indexed | 全量重建路径 |
| FR-4.4 | formal/concept-03.puml | attr:Document.valid_to | 墓碑软删除 |
| FR-4.5 | formal/flow-03.puml | trans:candidate&gt;pending | 触发调度（collect 流） |
| FR-4.6 | formal/flow-05.puml | trans:tombstone_modify&gt;new | 维护路径（KD-10 缺口注记） |
| FR-5.1a | formal/concept-03.puml | assoc:CONTAINS_SECTION | 结构图谱双层节点 |
| FR-5.1b | formal/concept-03.puml | assoc:MENTIONS | 实体挂章节（P1——M5 后可用） |
| FR-5.2 | formal/concept-05-graph.puml | attr:Section.summary | 摘要到章节 |
| FR-5.3 | formal/concept-05-api.puml | attr:Hit.section_path | 检索最小单位=章节 |
| FR-6.2 | formal/rules-03.py | z3tag:T1_accept默认070 | 三档处置 |
| FR-6.3 | formal/flow-03.puml | trans:watchlist&gt;accepted | 人在回路 |
| FR-6.4 | formal/flow-05.puml | trans:running&gt;done | 报告任务路径 |
| FR-6.5 | formal/concept-05.puml | enum:TaskStatus | 调度任务机（幂等注记） |
| FR-6.6 | formal/concept-05-api.puml | interface:ScoringModule | 评分插件契约 |
| FR-6.7 | formal/concept-05.puml | attr:InboxRecord.scoring_version | 可追溯字段 |
