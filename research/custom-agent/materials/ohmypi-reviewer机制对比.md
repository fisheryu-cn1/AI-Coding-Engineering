# oh-my-pi 的 reviewer 子代理机制：检索与本项目 code-review skill 对比（[D1]）

> 日期：2026-08-21；话题标签 [D1]（§4.3 含 [D1+D3]）
> 检索背景：研究者要求对比业界同类实现与本项目的代码评审 skill（规则集 v5 + 评审工作方法总纲 V1.0）。检索时点 2026-08-21，全部结论基于公开文档与源码提示词文件，未做实测运行。
> 检索对象：**oh-my-pi（omp）**，can1357 开发的 pi 分支（约 26.6k stars）——"Coding agent with the IDE wired in"，在 pi 极简内核上增加 subagents、LSP/DAP、hindsight memory、hashline edits 等。它与本项目实验框架 pi 同源，是"pi 生态 fork+增强"路线的代表。
> 来源：README（github.com/can1357/oh-my-pi）、docs/advisor-watchdog.md、docs/models.md、packages/coding-agent/src/prompts/review-request.md 与 prompts/agents/reviewer.md（编排与评审两级提示词原文）、omp.sh/docs、pi.dev/packages/pi-pr-review、tintinweb/pi-subagents。引用以 2026-08 快照为准。

## 1. omp 的评审机制：三层结构

### 1.1 /review 编排层（prompts/review-request.md，Handlebars 模板）

- 输入装配：变更文件表（路径±行数×类型）、被排除文件及原因、内嵌 diff（过大时按文件给预览）、附加指令。
- **分发策略**：编排代理用 `task` 工具（`agent: "reviewer"` + tasks 数组）派发——多代理时**按局部性分组**（同目录/同模块、功能相关、测试与其实现同组），每个 reviewer 只负责分配到的文件（"Focus ONLY on assigned files"）；单代理时只建一个任务。
- 约束：reviewer 使用供给的 diff hunks、"NEVER re-run git diff"；产出以增量 yield 段落流出（findings 与 verdict 字段），不调独立提交工具。
- `/review` 与 `/green` 是**最低优先级命令**——用户或项目级同名命令可覆盖（omp.sh/docs/slash）。

### 1.2 reviewer 专业化层（prompts/agents/reviewer.md，框架内置代理提示词）

- **角色**："Code review specialist"，使命"Find bugs author wants fixed before merge"；跑在 `@slow`（强模型）角色上；只读工具面（read/grep/glob/bash/lsp/web_search/ast_grep）；可再派 `scout` 子代理。
- **方法**：取 patch（git diff / jj diff / gh pr diff）→ **读每个改动文件的全文件上下文**（非仅 hunks）→ 增量流出 findings → 出 verdict。
- **跨边界追踪规则**（提示词中最具体的检查程序）：凡 patch 引入的类型/变体/值跨越函数或模块边界（事件、消息、枚举、IPC 载荷等），必须定位消费侧的分发点（switch/路由/处理器注册表），"silent drop、no-op 或 discard 即报缺陷"；且"分发点常在 diff 之外，下结论前必须读它"——提示词自述这是集成类漏检的主因。
- **立项准则（须全部满足）**：可证明的影响与具体代码路径（禁推测）、可操作的离散修复、明确非有意为之、由该 patch 引入、无未声明假设、与代码库规范相称。
- **定级与裁决**：P0（阻断发布/运维、普适无条件）~P3 四级带例证；每条 finding 与总体 verdict 各带 0.0–1.0 confidence；verdict 为二值枚举（correct/incorrect）+ 1–3 句说明。
- **产出 schema**：祈使句标题 ≤80 字符、单段正文、priority/confidence/file_path/行范围（≤10 行且**必须与 diff 重叠**）；建议块只给保真替换代码。
- **禁止**：不报存量缺陷、不给"考虑改进 X"式泛泛建议、不推测作者意图、评审忽略风格/文档/nits、bash 只读（diff/log/show）。

### 1.3 advisor 过程内评审层（docs/advisor-watchdog.md）

与 /review 的事后评审正交：**评审者常驻**，读主代理每轮 transcript 增量（含推理、工具意图与结果），可自带只读工具检查工作区，把建议注入回主会话——"does not approve actions or mutate primary session state"。

- 配置：WATCHDOG.yml 名册（每个 advisor 可配独立模型/工具/指令）+ WATCHDOG.md 顾问性指引（不注入主代理上下文）。
- 分级投递（advise 工具）：nit（不打断，步边界批量）／concern（打断式转向）／blocker（终答后仍可触发新一轮）。
- **防噪设计**（emission guard）：每次更新至多接受一条建议；无内容短语过滤（"lgtm"被抑制）；4096 条 FIFO 去重；速率限制；immuneTurns 默认 3（限制打断频率）；破坏性模式的建议进隔离区。
- 隔离：独立工具会话与用量核算、自身压缩周期、自身旧建议过滤（防递归自审）；JSONL 留痕但"never a peer"（不可被消息/复活/杀死）。

### 1.4 基础设施

task 扇出支持工作区隔离（pi-iso 多后端）；子代理产物为 schema 校验对象，父代理经 `agent://<id>/findings.0.path` 按路径取字段；`learn`/`manage_skill` 可把经验教训提升为受管 skill。

## 2. 与本项目 code-review skill 的逐维对比

| 维度 | omp reviewer 体系 | 本项目（规则集 v5 + 总纲 V1.0） |
|---|---|---|
| 知识载体 | 框架内置代理提示词（reviewer.md，随版本发布，用户可用同名命令覆盖） | 独立可迭代的知识资产（skill：规则集/模板/指南/工作单 + CHANGELOG），Agent Skills 标准、跨框架分发 |
| 知识来源 | 通用评审专业能力的一次性编码 | 从被评项目缺陷史挖掘提炼（自举），带溯源标注（先验/案例渗入） |
| 知识验证 | 无评估面配套 | **规约-验证对**：每资产配锚定真实缺陷的评估集，三口径召回 + pass^k 复测（v1→v5 五轮） |
| 并行语义 | **分区**：N 个 reviewer 按文件局部性分摊，每文件单次覆盖 | **重复采样**：同全量任务多轮独立运行再归并（单轮召回实测 31–46%，约半数发现单轮独有） |
| 定级纪律 | P0–P3 定义表内建于提示词 + 自报 confidence | P0–P3 + **分级依据陈述强制**（实测：无依据组 4 个 P0 复核全偏高；带依据组唯一 P0 有真实事故背书）；置信靠跨轮复现而非自报 |
| 裁决形态 | 二值 verdict（correct/incorrect）+ confidence，交人决策 | 归并仲裁（主题并集/交集定置信/冲突标记）→ 人工三介入点 → **合并权在人**收口 |
| 跨边界检查 | 明文程序（emitter→consumer 分发点必读） | 同族做法：规则带执行程序（RR-4 四查、RR-8 双向化、五步机械化） |
| 输出契约 | 框架级 schema 校验（yield 对象 + agent:// 寻址） | 生产端格式契约（意见卡模板单行字段）+ 评分器消费 + 适配器原则 |
| 锚定方式 | patch 锚定（行范围必须重叠 diff；不报存量缺陷） | 评估场景锚点状态全量评审 + **五通道隔离**（防答案渗漏）；实战复审对修复 diff |
| 过程内评审 | advisor 常驻逐轮纠偏（nit/concern/blocker 分级 + 防噪） | 阶段间 A-B 闭环（应答须反证→修复→独立复审四档→人工合并），复审与修复者异工具异模型 |
| 人工环节 | verdict 供人参考（无过程规范） | 人工介入规范化：待办清单五字段、决策文档内联摘录/自足表述两硬规范、错判五类复核清单 |
| 停止条件 | 无（框架功能，随版本演进） | 显式四信号 + "机制验证完转入迁移验证"；部署前先测裸模型基线 |

## 3. 三个关键分析

### 3.1 分区并行 ≠ 重复采样：两类"多代理评审"解决不同问题

omp 的 N 个 reviewer 是**空间切分**（按文件分组、每文件恰好一个评审者）——解决吞吐与上下文聚焦问题；本项目的多轮是**时间切分**（同一全量任务独立重复）——解决采样方差与查全问题。两者正交，但不可互相替代：按本项目 E5 证据（单轮召回 31–46%，约半数发现为单轮独有，同文件问题的发现本身是随机变量），**分区式并行中每个文件仍只有一次采样机会**——分到该文件的 reviewer 单轮漏了就是全组漏了。omp 用 advisor（过程内第二双眼睛）与强模型（@slow）部分补偿，但其 sweep-then-verdict 的主路径仍是每文件单采样。反之，本项目的重复采样在 omp 上可直接实现（同锚点多跑几次 /review 再归并）——两者可组合：分区管规模、重复管查全、advisor 管过程。

### 3.2 同一条规则的两种载体：框架提示词 vs 可迭代资产

reviewer.md 的跨边界追踪规则与本项目规则的"执行程序"层（如 RR-4 四查）完全同族——都认识到"光有规则条文不够，必须写清检查程序"。差异在载体与生命周期：omp 把它**固化进框架**（用户拿到即用、随版本统一升级，但用户侧无迭代与验证手段——覆盖式定制是唯一出口）；本项目把它做成**独立资产 + 评估面**（规约-验证对），可以从被评项目缺陷史生长、修订走工作单、每版复测、并可整体迁移（fundseeker 零适配三锚点全中）。这正对应本项目"模板 vs 填充方法"的核心区分：omp 卖的是模板，本研究的贡献是填充与验证方法。值得一提，omp 声明继承磁盘上既有 skills（.claude/.cursor 等多来源）——本项目工作包是 Agent Skills 标准的纯 Markdown skill，理论上可直接装入 omp 运行（D1-S5 迁移注记的免费增量）。

### 3.3 过程内 vs 阶段间：时间轴上的互补

advisor 在**错误发生的前一拍**拦截（读主代理增量、concern 打断式转向），本项目 A-B 闭环在**阶段边界**拦截（复审四档结论 + 对修复 diff 的回归检查 + 人工合并闸门）。本项目的实测（修复者两次低级失误，一次被自身冒烟、一次被独立复审拦截）支持阶段间复审的价值；advisor 的价值在更早、更便宜，且其**防噪工程设计**（每次更新至多一条、内容过滤、去重、immuneTurns、隔离区）是本项目总纲未覆盖的问题——常驻评审者的主要风险是噪声淹没，omp 给出了成套对策，可作为总纲"多轮归并"之外的"过程内评审"扩展候选。反向地，本项目实证过的两条 omp 未覆盖：自报 confidence 不可尽信（错误背书只在对照中暴露），以及人工裁定环节的过程规范（合并权在人）。

## 4. 对 V1.1 的借鉴候选（登记，不即行）

1. **分级投递三档**（nit/concern/blocker）与 emission guard 防噪设计——若 V1.1 增补"过程内轻量复核"章节的现成参照；
2. **verdict 二值化 + 1–3 句说明**——归并报告的最终裁决行可采此形态（现在是仲裁结论 + 人工介入，形态可更收敛）；
3. **行范围与 diff 重叠约束**——意见卡定位字段的机检红线候选（本项目已发现行号漂移现象，该约束是框架级解法）；
4. 分区×重复**组合策略**——大规模变更（百文件级）下先分区再组内双采样的成本-查全权衡，列为待检验命题。

## 5. 局限

- 全部基于文档与提示词静态研读，未实测 omp（其 verdict 质量与 advisor 噪声率无一手数据）；
- omp 迭代快（docs 含 ERRATA 文件），本对比以 2026-08-21 快照为准；
- 本项目侧数字均为已有实测（口径见评估口径卡与 fs 对比分析），两体系的场景差异（merge 评审 vs 缺陷史评估）使部分维度不对等，已在表中标明。

## 6. 登记与来源

- 话题分类 [D1]；本文并入 materials 索引；对 #20 报告无追溯修改（其文献对话范围限于 36 篇论文，工程实现对比属 D1 生态材料）。
- 来源：[oh-my-pi 仓库](https://github.com/can1357/oh-my-pi)｜[advisor-watchdog 文档](https://github.com/can1357/oh-my-pi/blob/main/docs/advisor-watchdog.md)｜[models 文档](https://github.com/can1357/oh-my-pi/blob/main/docs/models.md)｜[review-request.md](https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/prompts/review-request.md)｜[agents/reviewer.md](https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/prompts/agents/reviewer.md)｜[omp.sh/docs](https://omp.sh/docs)｜[pi-pr-review 包](https://pi.dev/packages/pi-pr-review)｜[tintinweb/pi-subagents](https://github.com/tintinweb/pi-subagents)
