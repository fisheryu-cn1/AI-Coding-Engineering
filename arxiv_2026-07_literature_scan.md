# 2026 年 7 月 arXiv 论文检索与阅读建议

> 检索窗口：2026-07-01 至 2026-07-31  
> 整理日期：2026-08-03  
> 项目：GraphIt · AI Coding Engineering Knowledge Base

## 1. 检索范围与筛选标准

本次检索围绕项目的核心研究主线展开：AI Coding Agent、仓库级代码理解、上下文工程、Agent Memory、代码图谱、GraphRAG、本体工程、SDD 和 Agent Harness。检索范围覆盖 arXiv 的 `cs.AI`、`cs.SE`、`cs.CL`、`cs.IR`、`cs.KR`，以标题和摘要中的 `repository-level code`、`coding agent`、`context management`、`memory`、`GraphRAG`、`ontology`、`requirement-to-code` 等关键词进行候选筛选。

筛选优先保留：

- 直接服务 Coding Agent 的仓库检索、代码生成或软件维护论文；
- 能落到 GraphIt 的上下文选择、压缩、溯源和动态检索设计的论文；
- 代码图、软件知识图谱、GraphRAG、本体或需求—代码追踪论文；
- 提供新 Benchmark、真实仓库实证或可复现实验的工作。

以下内容是基于 arXiv 元数据、摘要和初步资料扫描形成的收集与阅读建议；“已下载”不等于“已完成全文精读”。论文版本、同行评审状态和许可条件应以论文页面为准。

## 2. P0：优先下载与精读

| 论文 | arXiv 版本 | 主题 | 与 GraphIt 的关系 | 阅读关注点 | 本地 PDF |
|---|---|---|---|---|---|
| [ContextSniper](https://arxiv.org/abs/2607.01916) | 2607.01916v3，7 月 2 日 | 代码记忆、精确证据选择 | 面向仓库修复的代码/行动记忆和混合排序 | 代码记忆的层级、候选过滤和 Token—效果权衡 | [PDF](references/ContextEngineering/23-Luk-ContextSniper_v3.pdf) |
| [Agent Retrieval Bench](https://arxiv.org/abs/2607.24882) | 2607.24882v1，7 月 27 日 | 仓库上下文检索评测 | 将“找对上下文”从最终代码生成中独立出来 | file-level retrieval 任务、相关性定义和评测指标 | [PDF](references/ContextEngineering/24-Qin-Agent_Retrieval_Bench_v1.pdf) |
| [CodeNib](https://arxiv.org/abs/2607.25431) | 2607.25431v1，7 月 28 日 | 多视图仓库上下文服务 | 统一词法、向量、结构索引和符号导航 | 版本化索引、视图融合、边界上下文和生命周期成本 | [PDF](references/CodeGraph/10-Yu-CodeNib_v1.pdf) |
| [MRCoder](https://arxiv.org/abs/2607.26805) | 2607.26805v1，7 月 29 日 | 仓库级上下文选择 | 直接对应 GraphIt 的分层上下文和冗余控制 | 如何在相关性、完整性和 Token 成本之间取舍 | [PDF](references/ContextEngineering/25-Wang-MRCoder_v1.pdf) |
| [Know Before Fix](https://arxiv.org/abs/2607.11111) | 2607.11111v1，7 月 13 日 | QA 驱动仓库知识获取 | 将 Agent 的知识缺口转化为主动检索问题 | “缺什么信息”如何识别，QA 如何驱动后续图查询 | [PDF](references/ContextEngineering/26-Lin-Know_Before_Fix_v1.pdf) |
| [Addressable Recall Compaction](https://arxiv.org/abs/2607.25066) | 2607.25066v1，7 月 27 日 | 可寻址上下文压缩 | 与 API 卡片、按 URI 拉取详情和 Grounding 直接对应 | 压缩引用、归档日志、无损恢复和证据 ID 设计 | [PDF](references/ContextEngineering/27-Dang-Addressable_Recall_Compaction_v1.pdf) |
| [CODENS](https://arxiv.org/abs/2607.18356) | 2607.18356v1，7 月 20 日 | Pull Request 到软件知识图谱 | 将代码变更转换为可查询的 typed software KG | 增量抽取、实体关系 Schema、变更溯源和图遍历 | [PDF](references/CodeGraph/11-Kelious-CODENS_v1.pdf) |
| [RAGU](https://arxiv.org/abs/2607.11683) | 2607.11683v1，7 月 13 日 | 多阶段 GraphRAG | 可参考抽取、去重、摘要和社区发现的分层管线 | 单次抽取与多阶段 consolidation 的差异 | [PDF](references/KnowledgeEngineering/02-Komarov-RAGU_v1.pdf) |
| [OwlPath](https://arxiv.org/abs/2607.27249) | 2607.27249v1，7 月 28 日 | OWL2 代码知识压缩 | 连接代码图、代码本体和结构化上下文查询 | 本体建模粒度、推理成本、最小代码证据的生成 | [PDF](references/ontology/06-Zhang-OwlPath_v1.pdf) |

## 3. P1：重要选读

| 论文 | arXiv 版本 | 主题 | 与 GraphIt 的关系 | 阅读关注点 | 本地 PDF |
|---|---|---|---|---|---|
| [TraceDev](https://arxiv.org/abs/2607.18886) | 2607.18886v1，7 月 21 日 | 需求到代码追踪 | 连接 SDD、设计文档、代码修改与验证 | traceability graph 的节点、边和验证闭环 | [PDF](references/CodeGraph/12-Chen-TraceDev_v1.pdf) |
| [PAGE-RAG](https://arxiv.org/abs/2607.19301) | 2607.19301v1，7 月 21 日 | 证据接地的 GraphRAG | 强调图是原文的语义骨架，而不是唯一事实源 | 图不完整时如何回退到原文，如何保持 grounding | [PDF](references/KnowledgeEngineering/03-Chen-PAGE_RAG_v1.pdf) |
| [OntoExtend](https://arxiv.org/abs/2607.17963) | 2607.17963v1，7 月 20 日 | 需求驱动本体扩展 | 对 GraphIt 的统一 Context Schema 和领域本体演进有帮助 | competency questions、Schema 约束和扩展评测 | [PDF](references/ontology/07-Lippolis-OntoExtend_v1.pdf) |
| [ACM](https://arxiv.org/abs/2607.23809) | 2607.23809v1，7 月 26 日 | 长程 Agent 上下文管理 | 补充项目对 Compaction、外部记忆和生命周期管理的研究 | 上下文编辑触发条件、信息损失和成本 | [PDF](references/ContextEngineering/28-Li-Agentic_Context_Management_v1.pdf) |
| [Agent Harness Evolution](https://arxiv.org/abs/2607.03691) | 2607.03691v2，7 月 4 日 | Harness 演化与 Agent 质量 | 衔接 AIOS、Agent Harness 和上下文管理研究 | Harness 更新、质量回归、控制变量和效率指标 | [PDF](references/AIOS/10-Ben_Sghaier-Agent_Harness_Evolution_v2.pdf) |
| [ICAE-Bench](https://arxiv.org/abs/2607.21217) | 2607.21217v1，7 月 23 日 | 交互式项目构建评测 | 将任务从“修一个明确 Bug”扩展到不完整意图到项目 | 需求澄清、规划、工具使用、调试和仓库构建的联合评测 | [PDF](references/AIOS/11-Peng-ICAE_Bench_v1.pdf) |
| [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250) | 2607.27250v1，7 月 28 日 | `AGENTS.md` / `CLAUDE.md` 消融 | 可验证项目对静态上下文文件的预期，不把规则效果想当然 | 真实仓库实验、任务边界、正确性与效率指标 | [PDF](references/ContextEngineering/29-Khatri-Do_Context_Files_Help_v1.pdf) |
| [From Registry to Repository](https://arxiv.org/abs/2607.00911) | 2607.00911v2，7 月 1 日 | Agent Skills 工程化 | 与项目的 API 卡片、Skill 和上下文工件管理方向相连 | Skill 的编写、适配、演化、复用和质量治理 | [PDF](references/ContextEngineering/30-Gao-Registry_to_Repository_v2.pdf) |

## 4. 推荐阅读路线

### 路线 A：仓库上下文检索

1. [Agent Retrieval Bench](https://arxiv.org/abs/2607.24882)
2. [ContextSniper](https://arxiv.org/abs/2607.01916)
3. [Know Before Fix](https://arxiv.org/abs/2607.11111)
4. [CodeNib](https://arxiv.org/abs/2607.25431)
5. [MRCoder](https://arxiv.org/abs/2607.26805)

目标是回答：GraphIt 的最小检索单元应当是文件、函数、API 卡片还是证据子图？如何将“知识缺口”纳入检索控制器？

### 路线 B：上下文压缩与长期记忆

1. [Addressable Recall Compaction](https://arxiv.org/abs/2607.25066)
2. [ACM](https://arxiv.org/abs/2607.23809)
3. 现有 [TokenMizer](references/ContextEngineering/20-Mishra-TokenMizer.pdf)、[HORMA](references/ContextEngineering/21-Hsu-HORMA.pdf) 和 [VISTA](references/ContextEngineering/22-Xu-VISTA.pdf)
4. 比较压缩是否可恢复、记忆是否有版本、证据是否可追溯。

### 路线 C：代码图、GraphRAG 与本体

1. [RAGU](https://arxiv.org/abs/2607.11683)
2. [PAGE-RAG](https://arxiv.org/abs/2607.19301)
3. [CODENS](https://arxiv.org/abs/2607.18356)
4. [OwlPath](https://arxiv.org/abs/2607.27249)
5. [OntoExtend](https://arxiv.org/abs/2607.17963)

重点比较：图是索引、推理空间还是语义骨架；图不完整时如何回退到原文；代码图、文档图和需求图如何通过统一 Schema 连接。

### 路线 D：SDD、Harness 与评测

1. [TraceDev](https://arxiv.org/abs/2607.18886)
2. [ICAE-Bench](https://arxiv.org/abs/2607.21217)
3. [Agent Harness Evolution](https://arxiv.org/abs/2607.03691)
4. [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250)

建议将最终任务成功率之外的指标纳入 GraphIt 评测：检索召回率、上下文精度、Token 成本、Grounding 完整度、知识新鲜度、轨迹效率和错误恢复能力。

## 5. 资料收集与阅读记录清单

- [ ] 记录 arXiv ID、版本号、提交日期和官方下载链接
- [ ] 保存 PDF、摘要页、代码仓库和 Benchmark 链接
- [ ] 记录 Context Unit、检索策略、Schema、压缩机制和 Grounding 方式
- [ ] 记录数据集、模型、基线、主要指标和限制
- [ ] 标注“已下载 / 已完成检索评估 / 待全文精读 / 已精读”状态
- [ ] 将论文结论映射到 GraphIt 的数据接入、图构建、存储索引、检索服务或 MCP 层
- [ ] 对涉及长上下文的论文记录压缩比、召回率、任务成功率和 Token 成本
- [ ] 对涉及知识图谱的论文记录实体关系 Schema、来源溯源、版本和冲突处理机制

## 6. 收录说明

- 本批次 17 篇论文只保存一份 canonical PDF；跨主题论文通过索引交叉链接，不复制 PDF。
- 新增 PDF 文件名包含版本号，例如 `_v1`、`_v2`、`_v3`，以便复现实验和追踪版本变化。
- 下载明细、页数、文件大小和 SHA-256 见 [arxiv_2026-07_manifest.md](references/arxiv_2026-07_manifest.md) 与 [arxiv_2026-07_SHA256SUMS](references/arxiv_2026-07_SHA256SUMS)。
- 既有的 [2026 年 6 月文献扫描](research/arxiv_2026-06_literature_scan.md) 保留不变；本报告是 7 月增量清单。

## 7. 官方检索入口

- [arXiv 官方 API](https://export.arxiv.org/api/query?id_list=2607.01916,2607.24882,2607.25431,2607.26805,2607.11111,2607.25066,2607.18356,2607.11683,2607.27249,2607.18886,2607.19301,2607.17963,2607.23809,2607.03691,2607.21217,2607.27250,2607.00911&max_results=20)
- [arXiv cs.SE 2026 年 7 月列表](https://arxiv.org/list/cs.SE/2026-07)
