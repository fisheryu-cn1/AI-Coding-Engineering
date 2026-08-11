/* GraphIt-KB 原型展示数据
 * 全部内容来自项目真实资料：
 *  - arxiv_2026-07_literature_scan.md / research/arxiv_2026-06_literature_scan.md
 *  - references/{ContextEngineering,CodeGraph,KnowledgeEngineering,AIOS}/ 下的 README 与解读文档
 *  - research/README.md（各研究报告的核心问题与关键结论）
 *  - design/kb-app/01~04 设计文档（系统定位、Schema、交互规格）
 * 论文的章节正文（text）凡无全文可摘抄者，均以 "[示意]" 标注，为基于 arXiv 摘要/初评的合理转述。
 */
const KB = {

  /* 主题域：节点与 chips 着色依据（低饱和度色板） */
  topics: [
    { id: "ContextEngineering",    name: "ContextEngineering",    color: "#cda36b", desc: "长上下文失效、上下文压缩与供给" },
    { id: "context-engineering",   name: "context-engineering",   color: "#b48fa8", desc: "上下文工程工程化研究（research/）" },
    { id: "CodeGraph",             name: "CodeGraph",             color: "#93b795", desc: "代码图谱与仓库级上下文服务" },
    { id: "KnowledgeEngineering",  name: "KnowledgeEngineering",  color: "#b3a1d1", desc: "GraphRAG、知识工程与混合架构" },
    { id: "ontology",              name: "ontology",              color: "#7fb5ad", desc: "本体工程与知识表示" },
    { id: "AIOS",                  name: "AIOS",                  color: "#84a3c4", desc: "Agent 操作系统与 Harness" },
    { id: "sdd",                   name: "sdd",                   color: "#8f9fc9", desc: "规范驱动开发" },
    { id: "theory",                name: "theory",                color: "#9ba0be", desc: "信息理论与形式化方法" },
    { id: "PetriNets",             name: "PetriNets",             color: "#c9b98f", desc: "Petri 网与进程建模" },
    { id: "architecture",          name: "architecture",          color: "#a5b07a", desc: "传统架构与 AI 自动化演进" },
    { id: "industry",              name: "industry",              color: "#d1a0a4", desc: "AI 对行业与劳动力市场的影响" },
    { id: "ai-coding",             name: "ai-coding",             color: "#d19a6f", desc: "AI 代码生成工具研究" }
  ],

  /* 文档（20 篇，path 均为项目内真实相对路径） */
  docs: [
    {
      id: "context-rot",
      title: "Context Rot: 长上下文失效研究报告",
      type: "网页",
      topic: "ContextEngineering",
      authors: "Chao Hong 等",
      version: null,
      arxivId: null,
      path: "references/ContextEngineering/06-Hong-Context_Rot.html",
      summary: "提出“上下文腐化”（Context Rot）概念：输入变长时模型性能系统性下降，归纳腐化、干扰、混淆、错位四种失效模式。在 18 个模型上做多任务评测，并比较压缩、检索、结构化供给三类缓解策略。与 GraphIt 的相关性：直接支撑 MECW 预算与分层供给设计。",
      sections: [
        { path: "§1", title: "引言", summary: "长上下文失效问题定义：窗口扩大不等于能力增强。",
          text: "[示意] 随着主流模型把上下文窗口扩展到数十万甚至百万级 token，一种普遍假设是“更长的输入意味着更强的能力”。本报告系统检验这一假设，并提出“上下文腐化”概念：随着输入长度增加，模型对关键信息的利用能力会系统性退化。", entities: ["e-context-rot", "e-context-eng"] },
        { path: "§2", title: "长上下文的失效模式", summary: "四种失效：腐化 / 干扰 / 混淆 / 错位。",
          text: "[示意] 报告将长上下文失效归纳为四类：腐化（关键信息被稀释后丢失）、干扰（无关内容抢占注意力）、混淆（相似内容相互干扰）、错位（位置偏置导致首尾与中部信息利用不均）。这一分类与 Lost in the Middle 的位置偏置观察一脉相承并有所推广。", entities: ["e-context-rot", "e-lost-middle"] },
        { path: "§3", title: "实验", summary: "18 个模型、多任务评测，长度是独立的退化变量。",
          text: "[示意] 实验覆盖 18 个主流模型与多类任务，控制任务难度不变、仅改变上下文长度与噪声比例，结果显示性能随长度增长而单调退化，且退化曲线因模型而异。这说明长上下文失效是普遍现象而非个别模型缺陷。", entities: ["e-context-rot"] },
        { path: "§4", title: "缓解策略", summary: "压缩、检索、结构化供给三类手段的对比。",
          text: "[示意] 报告比较了三类缓解手段：对历史上下文做压缩、用检索替代全量注入、以及结构化地组织供给内容。结论倾向“少而准”的供给策略——这正是 GraphIt 采用混合检索与章节级供给的理论依据。", entities: ["e-hybrid-search", "e-rag", "e-context-eng"] }
      ]
    },
    {
      id: "contextsniper",
      title: "ContextSniper: 面向仓库修复的代码记忆与精确证据选择",
      type: "论文",
      topic: "ContextEngineering",
      authors: "Luk 等",
      arxivId: "2607.01916",
      version: "v3",
      path: "references/ContextEngineering/23-Luk-ContextSniper_v3.pdf",
      summary: "面向仓库级缺陷修复的代码/行动记忆机制与混合排序。阅读关注点：代码记忆的层级、候选过滤和 Token—效果权衡。（2026 年 7 月 P0 论文，2607.01916v3）",
      sections: [
        { path: "§1", title: "引言：仓库修复中的记忆问题", summary: "修复任务需要跨文件证据，Agent 记忆粗放导致 token 浪费。",
          text: "[示意] 仓库级缺陷修复要求 Agent 在大量文件中定位少量关键证据。现有 Agent 的记忆机制要么全量保留、要么粗暴截断，前者成本高昂，后者丢失关键上下文。ContextSniper 将“记住什么”建模为精确证据选择问题。", entities: ["e-repo-retrieval", "e-context-eng"] },
        { path: "§2", title: "代码与行动记忆", summary: "代码记忆分层组织，行动记忆记录已执行的修复轨迹。",
          text: "[示意] 论文区分两类记忆：代码记忆按仓库结构分层组织（仓库—文件—符号），行动记忆记录 Agent 已执行的查看、编辑与测试动作，避免重复探索。层级化设计使候选证据可以先粗筛再精排。", entities: ["e-repo-retrieval"] },
        { path: "§3", title: "候选过滤与混合排序", summary: "词法 + 向量的混合排序，在候选过滤阶段控制规模。",
          text: "[示意] 候选证据先经轻量过滤缩减规模，再以词法与向量信号混合排序。论文强调排序质量比单一路径的召回更影响最终修复成功率，这与 GraphIt 的混合检索（向量 + 图 + 全文 + RRF）设计一致。", entities: ["e-hybrid-search", "e-rag"] },
        { path: "§4", title: "实验与 Token—效果权衡", summary: "在修复成功率与 token 成本之间给出权衡曲线。",
          text: "[示意] 实验在仓库级修复基准上报告了成功率与 token 消耗的权衡曲线：精确证据选择使同等成本下的修复成功率显著提升。Token—效果权衡是 GraphIt 上下文预算（MECW）设计的直接参照。", entities: ["e-swebench", "e-context-eng"] },
        { path: "§5", title: "讨论", summary: "记忆机制与检索机制的边界。",
          text: "[示意] 作者讨论了记忆与检索的分工：稳定、复用度高的内容入记忆，任务相关、变化快的内容走检索。这一边界划分对知识库的“记忆层 vs 检索层”架构有参考价值。", entities: ["e-context-eng"] }
      ]
    },
    {
      id: "agent-retrieval-bench",
      title: "Agent Retrieval Bench: 仓库上下文检索评测",
      type: "论文",
      topic: "ContextEngineering",
      authors: "Qin 等",
      arxivId: "2607.24882",
      version: "v1",
      path: "references/ContextEngineering/24-Qin-Agent_Retrieval_Bench_v1.pdf",
      summary: "将“找对上下文”从最终代码生成中独立出来评测：定义 file-level retrieval 任务、相关性标准与指标。阅读关注点：检索任务定义、相关性定义和评测指标。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "动机", summary: "生成成功率混杂了检索与生成两种能力，需要单独评检索。",
          text: "[示意] 现有基准以最终代码生成结果论成败，检索不准与生成不强被混为一谈。Agent Retrieval Bench 把仓库上下文检索独立出来评测，使“找对上下文”成为可单独优化的目标。", entities: ["e-repo-retrieval", "e-swebench"] },
        { path: "§2", title: "任务定义", summary: "file-level retrieval：给定 issue 返回相关文件集合。",
          text: "[示意] 基准的核心任务是文件级检索：给定仓库与 issue 描述，系统需返回与修复相关的文件排序列表。文件级粒度在标注可行性与实用价值之间取得平衡。", entities: ["e-repo-retrieval"] },
        { path: "§3", title: "相关性定义与标注", summary: "相关性分级标准与 ground truth 构造。",
          text: "[示意] 论文给出可操作的相关性分级（直接需修改 / 提供关键上下文 / 无关），并说明 ground truth 的构造与校验流程。相关性定义是检索系统评测中最易被忽视、却最影响结论可信度的部分。", entities: ["e-repo-retrieval"] },
        { path: "§4", title: "指标与评测结果", summary: "召回、排序质量与效率的多维指标。",
          text: "[示意] 评测覆盖召回率、排序质量与检索成本等维度，对多类检索方法做了横向比较。结果显示纯向量检索在仓库场景存在明显短板，结构化信号是必要的补充。", entities: ["e-hybrid-search", "e-rag"] },
        { path: "§5", title: "对检索系统设计的启示", summary: "最小检索单元与评测先行。",
          text: "[示意] 作者建议将“最小检索单元”的选择（文件 / 函数 / 片段）与下游任务联合评估，并在系统迭代中坚持评测先行。GraphIt 将检索最小单位定为 Section，正是这一思路的对应实践。", entities: ["e-repo-retrieval"] }
      ]
    },
    {
      id: "mrcoder",
      title: "MRCoder: 仓库级上下文选择",
      type: "论文",
      topic: "ContextEngineering",
      authors: "Wang 等",
      arxivId: "2607.26805",
      version: "v1",
      path: "references/ContextEngineering/25-Wang-MRCoder_v1.pdf",
      summary: "仓库级上下文选择方法，直接对应 GraphIt 的分层上下文与冗余控制。阅读关注点：如何在相关性、完整性和 Token 成本之间取舍。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "仓库级上下文选择问题", summary: "相关性与完整性冲突，且都受 token 预算约束。",
          text: "[示意] 仓库级代码生成需要在相关性（选的都对）与完整性（要的都选）之间取舍，而两者共同受 token 预算约束。MRCoder 将上下文选择形式化为预算约束下的选择问题。", entities: ["e-repo-retrieval", "e-context-eng"] },
        { path: "§2", title: "分层上下文组织", summary: "仓库—模块—文件—符号的分层表示。",
          text: "[示意] MRCoder 将仓库组织为分层表示，使选择可以先在粗粒度层做排除、再在细粒度层做精排。分层思想与 GraphIt 的 Document—Section—Chunk 层级一致。", entities: ["e-repo-retrieval"] },
        { path: "§3", title: "冗余控制", summary: "去重与互补性建模，抑制同质化候选。",
          text: "[示意] 论文显式建模候选之间的冗余：内容高度重叠的候选在预算紧张时只保留代表项。冗余控制直接回应 Context Rot 中“干扰与混淆”两类失效模式。", entities: ["e-context-rot", "e-context-eng"] },
        { path: "§4", title: "实验", summary: "与检索基线的端到端对比。",
          text: "[示意] 实验在仓库级任务上对比了多种检索与选择基线，MRCoder 在同等 token 预算下取得更优的任务成功率，验证了“选择优于堆叠”的假设。", entities: ["e-repo-retrieval", "e-swebench"] },
        { path: "§5", title: "局限与讨论", summary: "静态选择与动态需求的差距。",
          text: "[示意] 作者指出静态一次选择难以适应 Agent 多轮交互中变化的信息需求，按需、增量式的上下文供给是后续方向——这与 GraphIt 的“渐进展开”交互原则一致。", entities: ["e-context-eng"] }
      ]
    },
    {
      id: "arc-compaction",
      title: "Addressable Recall Compaction: 可寻址上下文压缩",
      type: "论文",
      topic: "ContextEngineering",
      authors: "Dang 等",
      arxivId: "2607.25066",
      version: "v1",
      path: "references/ContextEngineering/27-Dang-Addressable_Recall_Compaction_v1.pdf",
      summary: "可寻址的上下文压缩：压缩引用、归档日志、无损恢复与证据 ID 设计，与 API 卡片、按 URI 拉取详情和 Grounding 直接对应。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "压缩的信息损失问题", summary: "摘要式压缩不可逆，丢失的细节无法找回。",
          text: "[示意] 长程 Agent 必须压缩历史上下文，但摘要式压缩不可逆：一旦细节被压掉，后续步骤需要时无法找回，造成隐性信息损失。ARC 的目标是让压缩“可寻址、可恢复”。", entities: ["e-arc", "e-context-eng"] },
        { path: "§2", title: "可寻址引用设计", summary: "压缩后在上下文中保留可解引用的指针。",
          text: "[示意] 压缩后的内容在上下文中以引用（指针）形式保留，每个引用对应归档存储中的完整原文，模型可按需解引用取回细节。这与 GraphIt 的“API 卡片 + 按 URI 拉取详情”策略同构。", entities: ["e-arc", "e-mcp"] },
        { path: "§3", title: "归档日志与无损恢复", summary: "归档层保证任何压缩都可回放到原文。",
          text: "[示意] 所有被压缩的内容以追加式日志归档，引用解析可无损恢复原文。压缩因此从“有损丢弃”变为“延迟读取”，信息损失在工程上被消除。", entities: ["e-arc"] },
        { path: "§4", title: "证据 ID 与 Grounding", summary: "每条引用带证据 ID，支撑生成内容的溯源核验。",
          text: "[示意] 引用与证据 ID 绑定，使 Agent 生成内容中的每个事实性断言都能回溯到归档原文。证据 ID 机制为 RAG 系统的 grounding 核验提供了可操作的工程方案。", entities: ["e-arc", "e-rag", "e-kg"] },
        { path: "§5", title: "评测", summary: "恢复准确率与成本对比。",
          text: "[示意] 评测显示可寻址压缩在长程任务上显著优于摘要式压缩，且token成本低于全量保留。压缩是否可恢复、证据是否可追溯，应成为上下文系统的基本评测维度。", entities: ["e-context-eng"] }
      ]
    },
    {
      id: "codenib",
      title: "CodeNib: A Multi-View Data System for Serving Repository Context to Coding Agents",
      type: "论文",
      topic: "CodeGraph",
      authors: "Yu 等",
      arxivId: "2607.25431",
      version: "v1",
      path: "references/CodeGraph/10-Yu-CodeNib_v1.pdf",
      summary: "多视图仓库上下文服务：统一词法、向量、结构索引和符号导航。阅读关注点：版本化索引、视图融合、边界上下文和生命周期成本。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "仓库上下文服务的问题", summary: "单一索引无法同时满足导航、搜索与理解需求。",
          text: "[示意] Coding Agent 对仓库的消费方式多样：精确符号导航、模糊语义搜索、结构关系查询。单一索引形态无法同时服务这些需求。CodeNib 将仓库上下文服务建模为多视图数据系统问题。", entities: ["e-repo-retrieval", "e-code-graph"] },
        { path: "§2", title: "多视图索引", summary: "词法、向量、结构三类索引并存。",
          text: "[示意] 系统为同一仓库维护词法（标识符精确匹配）、向量（语义相似）与结构（符号关系）三类索引视图，各视图共享统一的存储与版本底座。多视图并存是混合检索在代码领域的具体化。", entities: ["e-hybrid-search", "e-code-graph", "e-rag"] },
        { path: "§3", title: "符号导航与视图融合", summary: "跨视图融合与边界上下文的按需供给。",
          text: "[示意] 查询可在视图间跳转：从向量召回的候选文件，经结构视图展开相关符号，再以词法视图精确定义位置。论文还讨论了“边界上下文”——只提供接口边界而非完整实现——的供给策略。", entities: ["e-code-graph", "e-repo-retrieval"] },
        { path: "§4", title: "版本化索引与生命周期成本", summary: "索引随代码演进的版本管理与成本模型。",
          text: "[示意] 仓库持续演进使索引维护成为主要成本。CodeNib 引入版本化索引，按变更增量更新视图，并给出索引生命周期的成本模型。这与 GraphIt 的哈希指纹增量索引设计直接对应。", entities: ["e-code-graph"] },
        { path: "§5", title: "实验", summary: "多视图服务对 Agent 任务的成功率与成本影响。",
          text: "[示意] 实验评估了多视图上下文服务对 coding agent 任务成功率与 token 成本的影响，统一服务优于临时拼装的检索组合。", entities: ["e-repo-retrieval", "e-swebench"] }
      ]
    },
    {
      id: "codens",
      title: "CODENS: Transforming Code Changes into Living, Accessible, and Queryable Documentation",
      type: "论文",
      topic: "CodeGraph",
      authors: "Kelious 等",
      arxivId: "2607.18356",
      version: "v1",
      path: "references/CodeGraph/11-Kelious-CODENS_v1.pdf",
      summary: "将 Pull Request 代码变更转换为可查询的 typed software KG。阅读关注点：增量抽取、实体关系 Schema、变更溯源和图遍历。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "代码变更与文档脱节", summary: "PR 中的变更知识随合并即流失。",
          text: "[示意] Pull Request 承载了大量设计意图与变更理由，但合并后这些知识即流失在历史中。CODENS 试图把代码变更持续转化为“活的、可访问、可查询”的文档。", entities: ["e-code-graph", "e-kg"] },
        { path: "§2", title: "Typed Software KG Schema", summary: "变更、实体与关系的类型化 Schema。",
          text: "[示意] 论文设计了类型化的软件知识图谱 Schema，把 PR 中的代码实体、变更动作与讨论内容统一建模为带类型的节点与边。Schema 先行与 GraphIt 的“Schema 先验抽取”一致。", entities: ["e-kg", "e-code-graph", "e-llm-graph-transformer"] },
        { path: "§3", title: "增量抽取管线", summary: "按 PR 增量构建，避免全量重抽。",
          text: "[示意] CODENS 以 PR 为增量单元抽取图谱，新变更只触发局部更新。增量构建使图谱能跟随仓库持续演化，避免全量重抽的成本。", entities: ["e-code-graph"] },
        { path: "§4", title: "变更溯源与图遍历", summary: "从文档回溯变更、沿图遍历影响面。",
          text: "[示意] 图谱支持双向查询：从文档条目回溯产生它的代码变更，或从一次变更沿图遍历其影响面。变更溯源是图谱相对纯文本 Wiki 的核心增量价值。", entities: ["e-kg", "e-traceability"] },
        { path: "§5", title: "评估", summary: "文档鲜活度与查询可用性评估。",
          text: "[示意] 评估关注生成文档的鲜活度（与代码演进的同步程度）与查询回答质量，显示变更驱动的图谱文档明显优于静态生成文档。", entities: ["e-code-graph"] }
      ]
    },
    {
      id: "tracedev",
      title: "TraceDev: A Traceability-Driven Multi-agent Framework for Requirement-to-Code Development",
      type: "论文",
      topic: "CodeGraph",
      authors: "Chen 等",
      arxivId: "2607.18886",
      version: "v1",
      path: "references/CodeGraph/12-Chen-TraceDev_v1.pdf",
      summary: "追踪性驱动的需求到代码多智能体框架：将需求、规划、代码和验证组织为可追踪链。适合与 SDD 研究交叉阅读。（2026 年 7 月 P1 论文）",
      sections: [
        { path: "§1", title: "需求—代码断裂问题", summary: "生成代码后需求意图无法回溯。",
          text: "[示意] AI 生成代码规模越大，需求意图与代码实现之间的断裂越严重：评审者难以回答“这段代码对应哪条需求”。TraceDev 把可追踪性作为需求到代码开发的一等约束。", entities: ["e-traceability", "e-sdd"] },
        { path: "§2", title: "Traceability Graph 设计", summary: "需求、规划、代码、验证四类节点与追踪边。",
          text: "[示意] 框架维护一张 traceability graph：需求、规划步骤、代码工件与验证结果作为节点，节点间的追踪边记录派生关系。图的节点、边设计直接决定追踪能力上限。", entities: ["e-traceability", "e-kg"] },
        { path: "§3", title: "多智能体开发流程", summary: "规划、实现、验证 Agent 沿图协作。",
          text: "[示意] 多个专职 Agent（规划、实现、验证）沿 traceability graph 协作：每个 Agent 的产出都挂接到图上相应节点，使开发过程天然留下可审计轨迹。", entities: ["e-traceability", "e-sdd"] },
        { path: "§4", title: "验证闭环", summary: "验证结果回写图，未通过项沿追踪边定位。",
          text: "[示意] 验证环节的结论回写到图中：失败的验证可沿追踪边反向定位到具体需求与实现片段，形成需求—代码—验证的闭环。", entities: ["e-traceability"] },
        { path: "§5", title: "实验", summary: "追踪驱动的开发对正确性与可维护性的影响。",
          text: "[示意] 实验比较了有/无追踪性约束的多智能体开发，追踪驱动版本在需求覆盖率与缺陷定位效率上均有优势。", entities: ["e-sdd", "e-traceability"] }
      ]
    },
    {
      id: "ragu",
      title: "RAGU: A Multi-Step GraphRAG Engine with a Compact Domain-Adapted LLM",
      type: "论文",
      topic: "KnowledgeEngineering",
      authors: "Komarov 等",
      arxivId: "2607.11683",
      version: "v1",
      path: "references/KnowledgeEngineering/02-Komarov-RAGU_v1.pdf",
      summary: "多阶段 GraphRAG 引擎：抽取、去重、摘要和社区发现的分层管线，可参考其单次抽取与多阶段 consolidation 的差异。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "GraphRAG 的抽取质量瓶颈", summary: "单次抽取的实体噪声沿管线放大。",
          text: "[示意] GraphRAG 系统的问答质量上限由构建期的实体/关系抽取质量决定。单次抽取的噪声会在索引、社区发现与摘要阶段逐级放大。RAGU 主张以多阶段管线替代一次性抽取。", entities: ["e-graphrag", "e-rag"] },
        { path: "§2", title: "多阶段管线", summary: "抽取 → 去重 → 摘要 → 社区发现的分层处理。",
          text: "[示意] RAGU 将构建过程拆为抽取、去重、摘要、社区发现多个阶段，每阶段可用不同策略与模型。分层管线使每一步的质量可单独度量和改进。", entities: ["e-graphrag", "e-community"] },
        { path: "§3", title: "去重与 consolidation", summary: "跨文档实体归并与冲突消解。",
          text: "[示意] 多阶段 consolidation 对跨文档抽取的实体做归并与冲突消解，显著降低重复节点率。这与 GraphIt 的实体融合（嵌入初筛 + LLM 确认 + SAME_AS 边）机制同构。", entities: ["e-graphrag", "e-kg"] },
        { path: "§4", title: "社区发现与摘要", summary: "社区结构支撑全局性问题回答。",
          text: "[示意] 在归并后的实体图上做社区发现，并对每个社区生成摘要，使系统能回答“这个领域整体在讨论什么”类全局问题。社区摘要是 GraphRAG 相对朴素 RAG 的标志性增量。", entities: ["e-community", "e-graphrag"] },
        { path: "§5", title: "领域适配小模型与评测", summary: "compact domain-adapted LLM 的成本优势。",
          text: "[示意] 论文使用紧凑的领域适配 LLM 承担抽取任务，在保持质量的同时大幅降低构建成本。对本地知识库而言，构建期 LLM 成本是自动收集可行性的关键约束。", entities: ["e-graphrag", "e-rag"] }
      ]
    },
    {
      id: "page-rag",
      title: "PAGE-RAG: Evidence-Grounded Adaptive Graph Retrieval for Long-Document QA",
      type: "论文",
      topic: "KnowledgeEngineering",
      authors: "Chen 等",
      arxivId: "2607.19301",
      version: "v1",
      path: "references/KnowledgeEngineering/03-Chen-PAGE_RAG_v1.pdf",
      summary: "证据接地的自适应图检索：图是原文的语义骨架而非唯一事实源；图不完整时回退原文保持 grounding。（2026 年 7 月 P1 论文）",
      sections: [
        { path: "§1", title: "GraphRAG 的 grounding 问题", summary: "图答错了却没有机制回退到原文。",
          text: "[示意] 图检索给出的答案若图本身不完整就会出错，而多数 GraphRAG 系统缺少“图不足时回退原文”的机制。PAGE-RAG 把证据接地作为图检索的一等属性。", entities: ["e-graphrag", "e-rag"] },
        { path: "§2", title: "图作为语义骨架", summary: "图组织导航，事实仍以原文为准。",
          text: "[示意] 论文的核心立场：图是原文的语义骨架——负责组织与导航，但事实的唯一来源仍是原文。这一立场与 GraphIt “图谱补 RAG 之短、全程可溯源”的设计完全一致。", entities: ["e-kg", "e-graphrag"] },
        { path: "§3", title: "自适应图检索与回退", summary: "按图证据充分度决定是否回退原文。",
          text: "[示意] 检索过程自适应：图内证据充分时沿图回答，不足时自动回退到原文段落补充。回退机制以证据指针实现，与可寻址压缩的引用设计互补。", entities: ["e-graphrag", "e-arc", "e-hybrid-search"] },
        { path: "§4", title: "长文档问答评测", summary: "长文档 QA 上的 grounding 完整度对比。",
          text: "[示意] 在长文档问答基准上，PAGE-RAG 在答案正确性与 grounding 完整度上同时优于纯图与纯向量基线，验证了“骨架 + 回退”策略的有效性。", entities: ["e-graphrag", "e-rag"] },
        { path: "§5", title: "讨论", summary: "图的完备性假设应当被放弃。",
          text: "[示意] 作者主张放弃“图必须完备”的假设：局部构建的图配合可靠的回退机制，在成本与效果上都优于追求全量抽取。这为 GraphIt “只结构化 15–25% 核心实体”的克制策略提供了论据。", entities: ["e-kg", "e-graphrag"] }
      ]
    },
    {
      id: "owlpath",
      title: "OwlPath: OWL2 代码知识压缩与结构化上下文查询",
      type: "论文",
      topic: "ontology",
      authors: "Zhang 等",
      arxivId: "2607.27249",
      version: "v1",
      path: "references/ontology/06-Zhang-OwlPath_v1.pdf",
      summary: "用 OWL2 本体压缩代码知识：连接代码图、代码本体和结构化上下文查询。阅读关注点：本体建模粒度、推理成本、最小代码证据的生成。（2026 年 7 月 P0 论文）",
      sections: [
        { path: "§1", title: "代码知识的结构化压缩", summary: "用本体表达代码知识以压缩上下文。",
          text: "[示意] 将代码知识表达为本体实例后，同等语义的上下文体积显著小于源码文本。OwlPath 探索用 OWL2 本体作为代码知识的压缩表示，服务上下文受限的代码生成。", entities: ["e-owl2", "e-code-graph", "e-context-eng"] },
        { path: "§2", title: "OWL2 代码本体建模", summary: "类、属性与公理的建模粒度选择。",
          text: "[示意] 论文讨论代码本体的建模粒度：过细则实例爆炸、推理不可行，过粗则丢失可查询性。粒度选择是本体工程在代码领域落地的核心权衡。", entities: ["e-owl2", "e-kg"] },
        { path: "§3", title: "推理与结构化查询", summary: "OWL2 推理的成本与按需物化。",
          text: "[示意] 基于 OWL2 的推理可导出隐含关系，但全量推理成本高。论文采用按需物化策略，把推理结果作为可缓存的查询答案。推理成本是本路线相对纯图数据库的主要额外开销。", entities: ["e-owl2"] },
        { path: "§4", title: "最小代码证据生成", summary: "从本体答案反查最小代码证据。",
          text: "[示意] 查询命中本体实例后，系统反查支撑该实例的最小代码证据片段，供生成时引用。最小证据生成把本体的符号结论与代码原文连接起来，保证可溯源。", entities: ["e-owl2", "e-code-graph", "e-traceability"] },
        { path: "§5", title: "评估", summary: "压缩率、查询正确性与推理开销。",
          text: "[示意] 评估报告了本体表示的压缩率、结构化查询正确率与推理开销，显示本体路线在“精确结构化查询”场景优于纯向量检索，但构建与维护成本更高。", entities: ["e-owl2", "e-hybrid-search"] }
      ]
    },
    {
      id: "harness-evolution",
      title: "Don't Blame the Large Language Model: How Agent Harness Evolution Shapes Coding Agent Quality",
      type: "论文",
      topic: "AIOS",
      authors: "Oussama Ben Sghaier 等",
      arxivId: "2607.03691",
      version: "v2",
      path: "references/AIOS/10-Ben_Sghaier-Agent_Harness_Evolution_v2.pdf",
      summary: "Harness 演化如何塑造 coding agent 质量：模型不变时，Harness 更新本身会显著改变评测表现。阅读关注点：Harness 更新、质量回归、控制变量和效率指标。（2026 年 7 月 P1 论文）",
      sections: [
        { path: "§1", title: "“别怪模型”：Harness 的作用", summary: "同一模型在不同 Harness 下表现差异显著。",
          text: "[示意] 论文的核心论点：coding agent 的质量差异中有相当部分来自 Harness（脚手架）而非模型本身。在控制模型不变时，Harness 的演化即可显著改变任务成功率与行为模式。", entities: ["e-harness", "e-context-eng"] },
        { path: "§2", title: "Harness 演化追踪方法", summary: "把 Harness 版本作为实验变量追踪。",
          text: "[示意] 作者将 Harness 的版本演进（工具定义、提示结构、上下文管理策略的变更）作为独立变量纳入实验设计，追踪每次变更对质量的影响。", entities: ["e-harness"] },
        { path: "§3", title: "质量回归与控制变量", summary: "Harness 更新引入的隐性质量回归。",
          text: "[示意] 实验发现 Harness 更新常引入隐性质量回归：某些任务改善的同时另一些任务退化。缺乏控制变量的对比会把 Harness 的功过错误归因于模型。", entities: ["e-harness", "e-swebench"] },
        { path: "§4", title: "效率指标", summary: "成功率之外：token 成本、轨迹长度与恢复能力。",
          text: "[示意] 论文主张在最终成功率之外跟踪效率指标：token 成本、轨迹长度、错误恢复能力等。这与 GraphIt 评测维度（检索召回、上下文精度、token 成本、grounding 完整度）的扩展方向一致。", entities: ["e-harness", "e-context-eng"] },
        { path: "§5", title: "结论", summary: "Harness 工程应被视为一等工程对象。",
          text: "[示意] 结论：Harness 应作为一等工程对象被版本化、测试与评审。Agent 系统的质量改进空间有相当比例在模型之外。", entities: ["e-harness"] }
      ]
    },
    {
      id: "kg-agent-context",
      title: "知识图谱管理 Agent 上下文",
      type: "研究报告",
      topic: "context-engineering",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "research/context-engineering/知识图谱管理Agent上下文.md",
      summary: "论证用知识图谱管理设计文档/API 文档、并在代码生成每步动态提取上下文的可行性：GraphRAG/TREEFRAG 可将上下文压缩比提升至 18:1–24:1 且保持 94%+ 准确率；关键在于细粒度 schema、步骤感知检索、生成器感知压缩。",
      sections: [
        { path: "§1", title: "问题：上下文是瓶颈", summary: "大型项目生成的瓶颈不在模型而在上下文组织。",
          text: "本报告的核心问题：能否用知识图谱管理设计文档/API 文档，并在代码生成每一步动态提取所需上下文。调研结论：可行且已有大量支撑。大型项目生成的瓶颈不在模型能力，而在上下文的组织、任务拆分与验证闭环。", entities: ["e-context-eng", "e-kg"] },
        { path: "§2", title: "顶层设计", summary: "图谱作为项目知识的统一组织层。",
          text: "顶层设计：用知识图谱统一组织设计文档与 API 文档，生成过程中的每一步按需从图中动态提取上下文，替代简单的文本堆叠。图谱在此既是索引，也是推理空间。", entities: ["e-kg", "e-graphrag"] },
        { path: "§3", title: "压缩证据", summary: "GraphRAG/TREEFRAG 的实测压缩比。",
          text: "调研中的关键量化证据：GraphRAG/TREEFRAG 可将上下文压缩比提升至 18:1–24:1，同时保持 94%+ 的任务准确率。这说明结构化检索可以在大幅压缩 token 的同时保住关键信息。", entities: ["e-graphrag", "e-rag", "e-community"] },
        { path: "§3.1", title: "GraphRAG 路线", summary: "实体图 + 社区摘要支撑全局问答。",
          text: "[示意] GraphRAG 路线以实体关系图加社区摘要组织知识，适合回答跨文档的全局性问题；其构建成本集中在实体抽取与归并阶段。", entities: ["e-graphrag", "e-community"] },
        { path: "§3.2", title: "TREEFRAG 路线", summary: "树状层级摘要支撑长文档导航。",
          text: "[示意] TREEFRAG 以树状层级摘要组织长文档，检索沿树自顶向下逐层细化，天然契合“渐进展开”的供给方式。", entities: ["e-rag"] },
        { path: "§4", title: "关键技术", summary: "细粒度 schema、步骤感知检索、生成器感知压缩。",
          text: "报告归纳的三个关键成功因素：细粒度的 schema 设计（决定检索可达精度）、步骤感知的检索策略（按生成步骤供给不同上下文）、生成器感知的压缩（压缩服务于后续生成而非阅读）。", entities: ["e-kg", "e-hybrid-search"] },
        { path: "§5", title: "落地路线", summary: "统一 schema 与上下文质量指标。",
          text: "后续方向：设计统一的上下文 schema，兼容设计文档、API 文档、代码结构三类来源；建立上下文质量评估指标（压缩比、召回率、任务成功率、token 成本）。", entities: ["e-context-eng"] }
      ]
    },
    {
      id: "api-info-strategy",
      title: "API 信息提供策略",
      type: "研究报告",
      topic: "context-engineering",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "research/context-engineering/API信息提供策略.md",
      summary: "回答“生成代码时应提供完整 API 说明还是仅引用 URL”：分层渐进式提供最优——先注入 API 概要卡片，模型按需通过工具拉取详细文档；过早/过度检索会引入噪声。",
      sections: [
        { path: "§1", title: "问题：给多少 API 信息", summary: "完整说明、仅 URL、还是介于两者之间。",
          text: "核心问题：生成代码时应提供完整的 API 说明文档，还是仅提供引用 URL 让模型自行检索？两种极端分别对应成本失控与信息不足。", entities: ["e-context-eng", "e-rag"] },
        { path: "§2", title: "策略对比", summary: "三种提供策略的实证比较。",
          text: "[示意] 报告对比了全量注入、仅 URL、分层渐进三种策略：全量注入成本高且引入噪声；仅 URL 对模型检索能力要求过高；分层渐进在成本与正确率上同时占优。", entities: ["e-rag"] },
        { path: "§3", title: "分层渐进式供给", summary: "先概要卡片，再按需拉取详情。",
          text: "结论：分层渐进式提供最优——先注入 API 概要卡片（名称、签名、用途一句话），模型在生成过程中按需通过工具拉取详细文档。这与可寻址压缩（ARC）的“引用 + 解引用”机制同构。", entities: ["e-context-eng", "e-mcp", "e-arc"] },
        { path: "§4", title: "噪声控制", summary: "过早/过度检索反而降低生成质量。",
          text: "重要提醒：过早或过度检索会向上下文引入噪声，降低生成质量。检索时机与检索量需要作为策略参数显式控制——这正是 Context Rot 研究揭示的干扰效应。", entities: ["e-context-rot", "e-hybrid-search"] },
        { path: "§5", title: "结论与建议", summary: "API 卡片作为上下文基础设施。",
          text: "建议将 API 卡片作为上下文基础设施的一部分：卡片先验注入、详情按需拉取、拉取行为本身可作为信号反馈优化卡片质量。", entities: ["e-context-eng", "e-mcp"] }
      ]
    },
    {
      id: "sdd-compare",
      title: "OpenSpec / Speckit / Superpowers / OMO 框架对比",
      type: "研究报告",
      topic: "sdd",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "research/sdd/OpenSpec_Speckit_Superpowers_OMO框架对比.md",
      summary: "SDD 正从概念变为工业实践：OpenSpec（Delta Spec/Artifact）、Speckit（GitHub 原生）、Superpowers（多智能体）、OMO（自修正约束）各有侧重；规范正在成为人类与 AI 的共同事实来源。",
      sections: [
        { path: "§1", title: "SDD 从概念到工业实践", summary: "规范驱动开发进入工具化阶段。",
          text: "报告的核心问题：当前 SDD 工具框架的核心差异与适用场景。关键结论：SDD 正从概念变为工业实践，规范（Spec）正在成为人类与 AI 的共同事实来源。", entities: ["e-sdd"] },
        { path: "§2", title: "四框架概览", summary: "OpenSpec / Speckit / Superpowers / OMO 定位速览。",
          text: "四个框架各有侧重：OpenSpec 以 Delta Spec 与 Artifact 管理变更；Speckit 走 GitHub 原生工作流；Superpowers 采用多智能体协作；OMO 强调自修正约束。", entities: ["e-sdd"] },
        { path: "§3", title: "核心差异对比", summary: "变更管理、工作流耦合与智能体结构差异。",
          text: "[示意] 报告从变更管理方式、与既有工作流的耦合度、智能体协作结构三个维度系统对比了四框架的差异，并给出选型决策树。", entities: ["e-sdd"] },
        { path: "§4", title: "适用场景", summary: "按团队与项目形态选型。",
          text: "[示意] 不同框架适配不同团队形态：GitHub 重度团队适合 Speckit；需要严格变更审计的项目适合 OpenSpec；探索多智能体开发的团队可参考 Superpowers 与 OMO。", entities: ["e-sdd"] },
        { path: "§5", title: "与上下文工程的结合", summary: "规范文档作为上下文基础设施。",
          text: "后续方向：将 SDD 与上下文工程打通——规范文档本身作为上下文基础设施的一部分，代码生成过程严格锚定规范（Spec-as-Source）。", entities: ["e-sdd", "e-context-eng", "e-traceability"] }
      ]
    },
    {
      id: "graphit-design",
      title: "GraphIt 软件设计方案",
      type: "设计方案",
      topic: "KnowledgeEngineering",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "design/GraphIt_软件设计方案.md",
      summary: "项目的奠基性设计方案：主张图谱补 RAG 之短（多跳推理、语义相关≠相似），确立混合检索、Schema 先验抽取、结构感知分块、哈希指纹增量等核心决策。",
      sections: [
        { path: "§1", title: "图谱补 RAG 之短", summary: "多跳推理、语义相关≠相似。",
          text: "方案主张：图谱补 RAG 之短——向量检索解决“相似”，图谱解决“相关”；多跳关联推理是图谱相对纯向量方案的结构性增量。", entities: ["e-kg", "e-rag", "e-graphrag"] },
        { path: "§2", title: "混合检索架构", summary: "向量 + 图 + 全文 + RRF 融合。",
          text: "检索层采用混合架构：向量检索、图遍历与全文检索三路并行，以 RRF 融合排序。该决策源自 GraphIt 方案与四份设计文档的共识。", entities: ["e-hybrid-search", "e-rag", "e-kg"] },
        { path: "§3", title: "Schema 先验抽取", summary: "限定类型与关系集合，JSON 输出附证据。",
          text: "实体抽取采用 Schema 先验：在 prompt 中限定实体类型与关系类型集合，要求 JSON 输出并附章节级证据定位；候选实体经嵌入初筛、LLM 确认后归并。", entities: ["e-kg", "e-llm-graph-transformer"] },
        { path: "§4", title: "结构感知分块与增量索引", summary: "按章节结构分块，哈希指纹驱动增量。",
          text: "分块感知文档结构（章节路径作为元数据），索引以哈希指纹识别变更、墓碑标记软删除，实现秒级增量更新与目录重组零重抽取。", entities: ["e-hybrid-search"] },
        { path: "§5", title: "存储与工具选型", summary: "LadybugDB + LanceDB + bge-m3 的本地化组合。",
          text: "存储选型：图库选 LadybugDB（嵌入式，Kùzu 社区继任 fork）而非 Neo4j，单机本地化优先；向量库 LanceDB；嵌入模型 bge-m3。不引入 AST 路线。", entities: ["e-ladybugdb", "e-bge-m3", "e-kg"] }
      ]
    },
    {
      id: "wiki-hybrid",
      title: "Wiki 与图数据库混合架构策略笔记",
      type: "设计方案",
      topic: "KnowledgeEngineering",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "design/Wiki与图数据库混合架构策略笔记.md",
      summary: "Wiki 与图数据库分工的克制方案：只结构化 15–25% 的核心实体，其余内容留在 Wiki；图负责关联导航，Wiki 负责完整内容。",
      sections: [
        { path: "§1", title: "Wiki 与图数据库的分工", summary: "内容留 Wiki，关联入图。",
          text: "[示意] 笔记的基本立场：Wiki 擅长承载完整、可编辑的内容，图数据库擅长表达实体间关联；混合架构让两者各做擅长的事，而非把全部内容搬进图里。", entities: ["e-kg", "e-rag"] },
        { path: "§2", title: "混合架构设计", summary: "图索引与 Wiki 内容以锚点互链。",
          text: "[示意] 架构上，图中的实体与关系节点通过锚点链接回 Wiki 页面段落；Wiki 页面中的实体提及则反向索引到图。双向锚点保证任一入口都可走通全程。", entities: ["e-kg"] },
        { path: "§3", title: "克制的结构化策略", summary: "只结构化 15–25% 核心实体。",
          text: "核心策略是克制：只结构化 15–25% 的核心实体，其余留 Wiki。过度结构化会显著抬高构建与维护成本，而边际收益递减——PAGE-RAG 后续“放弃图的完备性假设”的论证与此呼应。", entities: ["e-kg", "e-graphrag"] },
        { path: "§4", title: "查询路由", summary: "关联类查询走图，内容类查询走 Wiki。",
          text: "[示意] 查询按类型路由：多跳关联与路径类查询走图遍历，全文与模糊语义查询走 Wiki 检索，两者结果在应用层汇合。", entities: ["e-hybrid-search", "e-rag"] },
        { path: "§5", title: "风险与折中", summary: "双写一致性与边界漂移。",
          text: "[示意] 笔记也记录了折中代价：图与 Wiki 双写的一致性维护、以及“哪些算核心实体”的边界随时间漂移，需要定期复核。", entities: ["e-kg"] }
      ]
    },
    {
      id: "task-split-safety",
      title: "图代数与任务拆分安全性分析",
      type: "研究报告",
      topic: "theory",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "research/theory/图代数与任务拆分安全性分析.md",
      summary: "图代数 / Petri 网 / 进程代数在任务拆分安全性分析中的应用：形式化方法可证明组合保持性，但并非所有安全属性都天然可组合；隐式信息流、状态爆炸、分解最优性仍是瓶颈。",
      sections: [
        { path: "§1", title: "任务拆分的安全性问题", summary: "拆分后的子任务组合是否保持原安全属性。",
          text: "核心问题：把大任务拆给多个 Agent 执行时，拆分后的组合是否保持原有的安全属性。这属于形式化方法中的组合保持性问题。", entities: ["e-formal"] },
        { path: "§2", title: "图代数与进程代数", summary: "用代数结构刻画任务组合。",
          text: "报告梳理了图代数与进程代数在任务组合建模中的应用：组合算子（顺序、并行、选择）上的安全属性保持性可以被严格定义与证明。", entities: ["e-formal"] },
        { path: "§3", title: "Petri 网建模", summary: "并发与资源约束下的任务网模型。",
          text: "Petri 网用于刻画任务拆分后的并发行为与资源约束：库所—变迁结构可表达任务间依赖与互斥，可达性分析用于验证死锁与安全性。", entities: ["e-petri", "e-formal"] },
        { path: "§4", title: "组合保持性的边界", summary: "并非所有安全属性都天然可组合。",
          text: "关键结论：形式化方法可证明组合保持性，但并非所有安全属性都天然可组合；隐式信息流、状态爆炸、分解最优性仍是主要瓶颈。", entities: ["e-formal", "e-petri"] },
        { path: "§5", title: "对 AI Coding 的启示", summary: "为任务拆分设计可验证的安全约束。",
          text: "后续方向：借鉴形式化方法思想，为 AI Coding 中的任务拆分设计可验证的安全约束；多 Agent 并行开发的拆分安全性需要显式建模而非经验保证。", entities: ["e-formal"] }
      ]
    },
    {
      id: "scan-2026-07",
      title: "2026 年 7 月 arXiv 论文检索与阅读建议",
      type: "研究报告",
      topic: "context-engineering",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "arxiv_2026-07_literature_scan.md",
      summary: "2026 年 7 月 arXiv 增量扫描：17 篇 P0/P1 论文的收集与阅读建议，覆盖仓库上下文检索、上下文压缩、GraphRAG、本体与 Harness 评测，并给出四条推荐阅读路线。",
      sections: [
        { path: "§1", title: "检索范围与筛选标准", summary: "围绕项目核心主线的关键词筛选。",
          text: "本次检索围绕项目的核心研究主线展开：AI Coding Agent、仓库级代码理解、上下文工程、Agent Memory、代码图谱、GraphRAG、本体工程、SDD 和 Agent Harness。检索范围覆盖 arXiv 的 cs.AI、cs.SE、cs.CL、cs.IR、cs.KR。", entities: ["e-repo-retrieval", "e-graphrag"] },
        { path: "§2", title: "P0：优先下载与精读", summary: "9 篇 P0 论文清单。",
          text: "P0 共 9 篇：ContextSniper、Agent Retrieval Bench、CodeNib、MRCoder、Know Before Fix、Addressable Recall Compaction、CODENS、RAGU、OwlPath。优先保留直接服务 Coding Agent 仓库检索、能落到 GraphIt 上下文选择/压缩/溯源设计的工作。", entities: ["e-repo-retrieval", "e-arc", "e-owl2"] },
        { path: "§3", title: "P1：重要选读", summary: "8 篇 P1 论文清单。",
          text: "P1 共 8 篇：TraceDev、PAGE-RAG、OntoExtend、ACM、Agent Harness Evolution、ICAE-Bench、Do Context Files Help Coding Agents?、From Registry to Repository。", entities: ["e-traceability", "e-harness", "e-sdd"] },
        { path: "§4", title: "推荐阅读路线", summary: "四条路线：检索 / 压缩记忆 / 图与本体 / SDD 与评测。",
          text: "路线 A（仓库上下文检索）回答：GraphIt 的最小检索单元应当是文件、函数、API 卡片还是证据子图？路线 C（代码图、GraphRAG 与本体）重点比较：图是索引、推理空间还是语义骨架；图不完整时如何回退到原文。", entities: ["e-repo-retrieval", "e-graphrag", "e-owl2"] },
        { path: "§5", title: "收录说明", summary: "canonical PDF 与版本号文件名规范。",
          text: "本批次 17 篇论文只保存一份 canonical PDF；跨主题论文通过索引交叉链接，不复制 PDF。新增 PDF 文件名包含版本号（如 _v1、_v2、_v3），以便复现实验和追踪版本变化。", entities: [] }
      ]
    },
    {
      id: "scan-2026-06",
      title: "2026 年 6 月 arXiv 文献扫描",
      type: "研究报告",
      topic: "context-engineering",
      authors: "项目研究组",
      arxivId: null,
      version: null,
      path: "research/arxiv_2026-06_literature_scan.md",
      summary: "2026 年 6 月基础扫描：13 篇值得关注的论文，覆盖 Agentic 编程/AIOS 治理、代码图谱与仓库级代码生成、上下文工程/Agent 记忆、GraphRAG/知识图谱构建四个方向。",
      sections: [
        { path: "§1", title: "检索策略", summary: "主题锚定 + OpenAlex 元数据校验。",
          text: "以 references/README.md 中 7 个主题目录为关键词骨架做主题锚定，时间范围 2026-06-01 至 2026-07-12；通过 OpenAlex API 校验论文元数据（标题、作者、发表日期、citation count）。", entities: [] },
        { path: "§2", title: "整体结论", summary: "13 篇论文、四个方向、三档优先级。",
          text: "共发现 13 篇值得关注的论文，分布在 Agentic 编程/AIOS 治理（3 篇）、代码图谱与仓库级代码生成（4 篇）、上下文工程/Agent 记忆（3 篇）、GraphRAG/知识图谱构建（3 篇）。所有论文均为极新预印本，引用数为 0，引用不能作为否定依据。", entities: ["e-harness", "e-code-graph"] },
        { path: "§3", title: "必读论文（High）", summary: "LLM-as-Code、ActPlane 等 4 篇。",
          text: "必读档包括 LLM-as-Code（把确定性控制流从 LLM 剥离交还程序，上下文由调用树 DAG 构成）与 ActPlane（用自然语言声明策略、经 eBPF 在内核层强制执行的 Agent Harness 策略面）。", entities: ["e-harness", "e-context-eng"] },
        { path: "§4", title: "代码图谱与仓库级生成", summary: "仓库视觉表示、测试驱动规划与探索基准。",
          text: "代码图谱方向包括：LLM Agents Can See Code Repositories（视觉图作为补充模态最多减少 26% 输入 token）、TICoder（测试驱动规划 + 实现感知复用）、SWE-Explore（仓库探索能力基准，覆盖 848 个 issue、203 个仓库）。", entities: ["e-code-graph", "e-repo-retrieval", "e-swebench"] },
        { path: "§5", title: "上下文工程与 GraphRAG", summary: "Agent 记忆三篇与 GraphRAG 构建三篇。",
          text: "上下文工程方向新增 TokenMizer（图结构会话记忆）、HORMA（层级记忆导航）、VISTA（可感知上下文的 Agent 仪表盘）；GraphRAG 方向包括 Core-based Hierarchies（k-core 分解替代 Leiden 社区检测）等。", entities: ["e-context-eng", "e-graphrag", "e-community"] }
      ]
    }
  ],

  /* 实体（23 个真实概念，type ∈ Concept/Method/Tool/Dataset） */
  entities: [
    { id: "e-context-rot", name: "Context Rot", type: "Concept", desc: "上下文腐化：输入变长时模型对关键信息利用能力的系统性退化。" },
    { id: "e-lost-middle", name: "Lost in the Middle", type: "Concept", desc: "长上下文的位置偏置现象：模型对首尾信息的利用显著好于中段。" },
    { id: "e-context-eng", name: "上下文工程", type: "Concept", desc: "为 Agent 提供高质量、可控、低成本上下文的工程学科。" },
    { id: "e-rag", name: "RAG", type: "Method", desc: "检索增强生成：先检索相关片段再条件化生成。" },
    { id: "e-graphrag", name: "GraphRAG", type: "Method", desc: "以实体关系图与社区摘要组织知识的检索增强范式。" },
    { id: "e-kg", name: "知识图谱", type: "Concept", desc: "以实体—关系结构组织知识的表示与存储方式。" },
    { id: "e-code-graph", name: "代码图谱", type: "Concept", desc: "以图结构表达代码实体与依赖关系的仓库表示。" },
    { id: "e-cpg", name: "代码属性图（CPG）", type: "Method", desc: "融合 AST/CFG/PDG 的统一属性图，漏洞模式可表达为图遍历。" },
    { id: "e-hybrid-search", name: "混合检索", type: "Method", desc: "向量 + 图 + 全文多路检索并以 RRF 融合。" },
    { id: "e-bge-m3", name: "bge-m3", type: "Tool", desc: "多语言多功能嵌入模型，GraphIt-KB 的向量化选型。" },
    { id: "e-ladybugdb", name: "LadybugDB", type: "Tool", desc: "嵌入式图数据库（Kùzu 社区继任 fork），GraphIt-KB 图库选型。" },
    { id: "e-llm-graph-transformer", name: "LLMGraphTransformer", type: "Tool", desc: "用 LLM 将文本转换为图谱三元组的抽取工具。" },
    { id: "e-mcp", name: "MCP", type: "Concept", desc: "Model Context Protocol：Agent 按需消费上下文与工具的协议。" },
    { id: "e-repo-retrieval", name: "仓库级代码检索", type: "Concept", desc: "在整个代码仓库尺度上定位任务相关证据的检索问题。" },
    { id: "e-arc", name: "可寻址压缩（ARC）", type: "Method", desc: "压缩后保留可解引用指针、可无损恢复的上下文压缩机制。" },
    { id: "e-community", name: "社区发现", type: "Method", desc: "在实体图上发现社区结构并生成摘要，支撑全局性问答。" },
    { id: "e-traceability", name: "需求—代码追踪", type: "Concept", desc: "需求、规划、代码与验证之间的可回溯关联。" },
    { id: "e-owl2", name: "OWL2 本体", type: "Concept", desc: "W3C 本体语言，支持形式化语义与推理的知识表示。" },
    { id: "e-petri", name: "Petri 网", type: "Method", desc: "库所—变迁结构的并发系统建模与可达性分析方法。" },
    { id: "e-sdd", name: "规范驱动开发（SDD）", type: "Concept", desc: "以结构化规范为人类与 AI 共同事实来源的开发范式。" },
    { id: "e-swebench", name: "SWE-bench", type: "Dataset", desc: "真实仓库 issue 修复基准，coding agent 事实标准评测。" },
    { id: "e-harness", name: "Agent Harness", type: "Concept", desc: "包裹模型的脚手架：工具定义、提示结构与控制流。" },
    { id: "e-formal", name: "形式化方法", type: "Concept", desc: "以数学结构刻画与验证系统性质的方法体系。" }
  ],

  /* 实体间 RELATES_TO（kind ∈ extends/contradicts/applies/evaluates/part-of），evidence 指向真实章节 */
  relates: [
    { from: "e-graphrag", to: "e-rag", kind: "extends", evidence: { doc: "ragu", sec: "§1" } },
    { from: "e-hybrid-search", to: "e-rag", kind: "extends", evidence: { doc: "graphit-design", sec: "§2" } },
    { from: "e-graphrag", to: "e-kg", kind: "applies", evidence: { doc: "kg-agent-context", sec: "§3.1" } },
    { from: "e-code-graph", to: "e-kg", kind: "extends", evidence: { doc: "codens", sec: "§2" } },
    { from: "e-cpg", to: "e-code-graph", kind: "part-of", evidence: { doc: "codenib", sec: "§2" } },
    { from: "e-owl2", to: "e-code-graph", kind: "applies", evidence: { doc: "owlpath", sec: "§1" } },
    { from: "e-context-rot", to: "e-lost-middle", kind: "extends", evidence: { doc: "context-rot", sec: "§2" } },
    { from: "e-kg", to: "e-context-eng", kind: "applies", evidence: { doc: "kg-agent-context", sec: "§1" } },
    { from: "e-bge-m3", to: "e-hybrid-search", kind: "applies", evidence: { doc: "graphit-design", sec: "§5" } },
    { from: "e-ladybugdb", to: "e-kg", kind: "applies", evidence: { doc: "graphit-design", sec: "§5" } },
    { from: "e-llm-graph-transformer", to: "e-graphrag", kind: "applies", evidence: { doc: "graphit-design", sec: "§3" } },
    { from: "e-arc", to: "e-context-eng", kind: "part-of", evidence: { doc: "arc-compaction", sec: "§1" } },
    { from: "e-community", to: "e-graphrag", kind: "part-of", evidence: { doc: "ragu", sec: "§4" } },
    { from: "e-traceability", to: "e-sdd", kind: "applies", evidence: { doc: "tracedev", sec: "§1" } },
    { from: "e-swebench", to: "e-repo-retrieval", kind: "evaluates", evidence: { doc: "agent-retrieval-bench", sec: "§1" } },
    { from: "e-mcp", to: "e-context-eng", kind: "applies", evidence: { doc: "api-info-strategy", sec: "§3" } },
    { from: "e-petri", to: "e-formal", kind: "part-of", evidence: { doc: "task-split-safety", sec: "§3" } },
    { from: "e-formal", to: "e-sdd", kind: "applies", evidence: { doc: "task-split-safety", sec: "§5" } },
    { from: "e-sdd", to: "e-context-eng", kind: "applies", evidence: { doc: "sdd-compare", sec: "§5" } },
    { from: "e-arc", to: "e-context-rot", kind: "contradicts", evidence: { doc: "arc-compaction", sec: "§3" } }
  ],

  /* 文档间 CITES / SUPERSEDES。CITES 基于 arxiv_2026-07 扫描的阅读路线同组关系构建（原型示意） */
  docLinks: [
    { from: "mrcoder", to: "agent-retrieval-bench", type: "CITES", note: "同组阅读路线 A：仓库上下文检索" },
    { from: "contextsniper", to: "agent-retrieval-bench", type: "CITES", note: "同组阅读路线 A：仓库上下文检索" },
    { from: "page-rag", to: "ragu", type: "CITES", note: "同组阅读路线 C：GraphRAG 方法论" },
    { from: "codens", to: "ragu", type: "CITES", note: "同组阅读路线 C：增量抽取与图构建" },
    { from: "tracedev", to: "sdd-compare", type: "CITES", note: "交叉阅读：需求—代码追踪 × SDD" },
    { from: "scan-2026-07", to: "scan-2026-06", type: "SUPERSEDES", note: "7 月增量清单取代 6 月扫描（后者保留不变）" }
  ],

  /* Inbox：本次收集运行报告 + 候选（均为 2026-06/07 扫描中的真实论文，尚未入库） */
  inbox: {
    report: { runAt: "2026-08-03 09:12", added: 17, deduped: 4, dropped: 3, source: "arXiv cs.AI / cs.SE / cs.CL / cs.IR / cs.KR" },
    candidates: [
      { id: "c1", title: "Know Before Fix: QA 驱动的仓库知识获取", source: "arXiv 2607.11111v1 · cs.SE · 2026-07-13", score: 0.91, topic: "ContextEngineering",
        summary: "将 Agent 的知识缺口转化为主动检索问题：识别“缺什么信息”，以 QA 驱动后续图查询。阅读关注点：知识缺口识别与检索控制器。" },
      { id: "c2", title: "Agentic Context Management (ACM): 长程 Agent 上下文管理", source: "arXiv 2607.23809v1 · cs.AI · 2026-07-26", score: 0.87, topic: "ContextEngineering",
        summary: "补充项目对 Compaction、外部记忆和生命周期管理的研究。阅读关注点：上下文编辑触发条件、信息损失和成本。" },
      { id: "c3", title: "ICAE-Bench: Evaluating Coding Agents as Interactive Project Builders", source: "arXiv 2607.21217v1 · cs.SE · 2026-07-23", score: 0.85, topic: "AIOS",
        summary: "将任务从“修一个明确 Bug”扩展到不完整意图到项目构建：需求澄清、规划、工具使用、调试和仓库构建的联合评测。" },
      { id: "c4", title: "Do Context Files Help Coding Agents? — AGENTS.md / CLAUDE.md 消融", source: "arXiv 2607.27250v1 · cs.SE · 2026-07-28", score: 0.82, topic: "ContextEngineering",
        summary: "真实仓库上的消融实验，验证静态上下文文件的预期效果，不把规则效果想当然。关注任务边界、正确性与效率指标。" },
      { id: "c5", title: "From Registry to Repository: Agent Skills 的工程化演进", source: "arXiv 2607.00911v2 · cs.SE · 2026-07-01", score: 0.78, topic: "ContextEngineering",
        summary: "与项目的 API 卡片、Skill 和上下文工件管理方向相连：Skill 的编写、适配、演化、复用和质量治理。" },
      { id: "c6", title: "OntoExtend: 需求驱动的本体扩展", source: "arXiv 2607.17963v1 · cs.KR · 2026-07-20", score: 0.76, topic: "ontology",
        summary: "对 GraphIt 的统一 Context Schema 和领域本体演进有帮助。阅读关注点：competency questions、Schema 约束和扩展评测。" },
      { id: "c7", title: "TokenMizer: 图结构会话记忆", source: "arXiv 2026-06 · references 既有馆藏补评", score: 0.71, topic: "ContextEngineering",
        summary: "Graph-Structured Session Memory：把会话历史组织为图以控制记忆规模。已有 PDF（20-Mishra-TokenMizer.pdf），待评估是否正式入库建图。" },
      { id: "c8", title: "Core-based Hierarchies for Efficient GraphRAG", source: "arXiv 2603.05207v2 · 2026-06-02 更新", score: 0.68, topic: "KnowledgeEngineering",
        summary: "用 k-core 分解替代 Leiden 社区检测，提升 GraphRAG 构建效率与可复现性。已有 PDF（01-Hossain），待与 RAGU 的社区发现路线对比。" }
    ]
  },

  /* 状态页 mock 数据 */
  status: {
    chunks: 1246, vectors: 1246, edges: 3891,
    timeline: [
      { time: "2026-08-10 22:14", event: "增量索引完成：6 文件变更（解析→分类→摘要→索引），耗时 3m42s", ok: true },
      { time: "2026-08-03 09:12", event: "收集运行完成：候选 17 篇（去重 4、淘汰 3），进入 Inbox 待审核", ok: true },
      { time: "2026-08-03 08:40", event: "Docling 解析失败：1 个 PDF（扫描版无文本层），已标记待 OCR", ok: false },
      { time: "2026-07-28 21:03", event: "全量重建（--no-cache）：18 篇文档、102 章节，耗时 41m", ok: true },
      { time: "2026-07-12 10:26", event: "目录重组：references/PetriNets 6 文件移动，仅更新路径，零重抽取", ok: true }
    ],
    failed: [
      { id: "t-1042", task: "P1 解析（Docling）", target: "references/ContextEngineering/05-Mohsin-Fundamental_Limits_of_LLMs_at_Scale.pdf", error: "扫描版 PDF 无文本层，需要 OCR 通道", time: "2026-08-03 08:40" },
      { id: "t-1037", task: "P3 摘要（LLM）", target: "references/KnowledgeEngineering/from_rag_to_multi_agent_systems.pdf §7", error: "LLM 网关 429 限流，重试 3 次失败", time: "2026-07-28 21:31" },
      { id: "t-1019", task: "P4 实体抽取", target: "design/软件详设提取为图谱的方案.md §4", error: "输出 JSON 校验失败（evidence 字段缺失）", time: "2026-07-28 21:19" }
    ],
    tokens: [
      { month: "2026-04", in: 420, out: 96 },
      { month: "2026-05", in: 1180, out: 240 },
      { month: "2026-06", in: 2050, out: 410 },
      { month: "2026-07", in: 3420, out: 655 },
      { month: "2026-08", in: 890, out: 172 }
    ]
  }
};
