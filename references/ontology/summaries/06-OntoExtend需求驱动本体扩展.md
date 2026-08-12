# 论文摘要：OntoExtend（需求驱动且可扩展的 LLM 本体扩展框架）

> **原论文标题**：OntoExtend: A Framework for Requirement-driven and Scalable Ontology Extension with LLMs
> **完整 PDF 文件名**：`07-Lippolis-OntoExtend_v1.pdf`
> 作者 / 年份：Anna Sofia Lippolis, Mohammad Javad Saeedizade, Stefan Schmid, Simon Blattner, Robin Keskisärkkä, Aldo Gangemi, Eva Blomqvist, Andrea Giovanni Nuzzolese，2026，arXiv:2607.17963（Linköping Univ / Univ of Bologna / Bosch / ISTC-CNR）
> 摘要类型：Agent 设计参考 + 内容索引
> 生成日期：2026-08-12

## 1. 适用场景

- 在 **企业级本体维护** 场景下，按"新 competency question → 增量扩展现有本体" 的模式工作（与"从零生成"区别开来）。
- 解决 **大本体 + LLM 上下文窗口限制** 的冲突：用 RAG 检索相关片段，再交给 LLM 扩展。
- 需要在 **结构正确性 + 功能正确性** 双维度评估 LLM 输出（OOPS! 陷阱 / 语法 / 一致性 / 需求验证 / 多余元素）。
- 适用于 **跨域复用**：论文展示了 EU 项目本体（Onto-DESIDE）+ Bosch 工业本体两类用例。

> 锚点：摘要（Abstract）；§1 Introduction；§3 OntoExtend；§4 Experimental setup；§5 Evaluation。

## 2. 主要观点与方案

### 2.1 核心论点

- 现有 LLM 本体工程大多集中于"从零生成"或"评测"，**缺少"针对新需求复用现有本体进行扩展"** 的系统方案。
- Ontology extension 比 from-scratch generation 更难：本体常含数百类/属性，超 LLM 上下文；长上下文下模型易被无关细节误导。
- OntoExtend = RAG（基于 ontology 元素） + LLM 扩展 + 集成回主本体。

### 2.2 三段管线

- ① Ontology Retriever：从输入本体中按 CQ 检索相关命名类 / 属性 / 公理（fragment）。
- ② Ontology Extender：把 fragment + CQ 喂给 LLM，生成缺失片段。
- ③ Ontology Integrator：把生成的 fragment 集成回扩展后的本体。

### 2.3 研究问题（RQ）

- RQ1：哪种 embedding 配置最适合从本体中检索 CQ 相关 fragment？
- RQ2：哪些 LLM 最擅长扩展 fragment 以正确建模 CQ？
- RQ3：评估生成 fragment 的质量需要哪些准则？
- RQ4：扩展本体的强项与弱点是什么？

### 2.4 评估方法

- 39 条 CQ 来自两个用例：Onto-DESIDE（EU 项目）+ Bosch 工业本体。
- 评估维度：结构（OOPS! / syntax / consistency / superfluous elements）+ 功能（requirement verification / user evaluation / expert assessment）+ 跨域（domain generalization / real-world ontology）+ 可扩展性（scalability）。

### 2.5 主要发现

- 生成片段结构问题少；通过所有功能测试；本体工程师评级为"小到中等修订"。
- 对 CQ 特异性与建模 profile 敏感——LQ 越具体，扩展越精准。

> 锚点：§3 OntoExtend；§4 Experimental setup；§5 Evaluation；§6 Results；§7 Discussion。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 用例数 | 2（Onto-DESIDE、Bosch 工业本体） | §4 |
| CQ 数量 | 39 条 | 摘要 |
| 结构问题 | 极少 | §6 Results |
| 功能测试 | 全部通过 | §6 Results |
| 专家评级 | 小到中等修订 | 摘要 |
| 评估维度 | 11 个（OOPS!/Syntax/Consist./Req.verif./Superfl.el./User/Expert/Domain gen./Real-world/Scal.） | Table 1 |
| 与既有方法对比 | 唯一同时满足 11 维度的方法（Table 1 "Ours" 行全 Y） | Table 1 |
| 资源 | 代码 + 数据（39 CQs + ontologies）：github.com/dersuchendee/OntoExtend | §1 |

> 锚点：§3 OntoExtend；§4 Experimental setup；§5 Evaluation；Table 1。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2607.17963 |
| 代码 / 数据 | https://github.com/dersuchendee/OntoExtend |
| 单位 | Linköping University / University of Bologna / Bosch / ISTC-CNR |
| 关联方法 | APTO（Soares et al.）、Phrase2Onto、Taxoria（Wu）、Online clustering（Wu）、Multi-LLM workflow（Kholmska）、AI Ontology curation（Joachimiak）、OOPS! 本体陷阱扫描、RAG ontology construction |
| 关联背景 | Onto-DESIDE（EU 项目本体）、CQs / competency questions（本体需求规约） |

> 锚点：§1 Introduction；§2 Related Work；Table 1。

## 5. 一句话索引（给 Agent 用）

> "新增 CQ → RAG 检索现有本体 fragment → LLM 扩展 fragment → Integrator 集成"——给 Agent 一条**需求驱动的本体增量维护**流水线，搭配 11 维结构 + 功能 + 专家评估，让 LLM 输出在企业级本体上可控可用。