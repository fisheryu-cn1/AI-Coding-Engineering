---
title: "SWE-bench Multimodal: Do AI Systems Generalize to Visual Software Domains?"
source_pdf: "22-Yang-SWE_Bench_Multimodal_v1.pdf"
arxiv_id: "2410.03859"
arxiv_version: "v1"
authors:
  - "John Yang"
  - "Carlos E. Jimenez"
  - "Alex L. Zhang"
  - "Kilian Lieret"
  - "Joyce Yang"
  - "Xindi Wu"
year: 2024
venue: "arXiv"
type: "评测对照 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：SWE-bench Multimodal——视觉软件域上的迁移崩塌

## 1. 适用场景

- 当你要评估自己的编码 Agent / 修复流水线在**非 Python 语言 + 含图像 issue**上的可迁移性（front-end、可视化、游戏等视觉软件域），或需要现成的 JavaScript 视觉 bug 修复基准时，读这篇。
- 当你在设计**语言无关（language-agnostic）的 agent scaffold**（ACI 编辑命令、故障定位模块、工具集）并想避开"Python 特化"陷阱时读这篇——§3.1/§4.1 给出了 Agentless、AutoCodeRover、Moatless 迁移失败的具体机理。
- 当你要给多模态编码 agent 配"网页渲染 / 截图 / 看图"工具并量化其收益与成本代价时读这篇（SWE-agent M 的工具表与消融分析）。
- 当你要从 GitHub 真实 issue 构建自己的 SWE-bench 式数据集、复用其"筛选→环境搭建→一致性过滤→人工验证"流水线时读这篇（§2.2 五步法 + 附录 B）。
- 当你需要证据论证"针对单一 benchmark 调优的流水线不可迁移、scaffold 的语言/模态无关性本身是能力边界"时引用这篇。

> 锚点：Abstract; §1 INTRODUCTION; §2.2 COLLECTION; §3.1 DO EXISTING SYSTEMS GENERALIZE?; §4 RESULTS。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 INTRODUCTION; §2.1 PRELIMINARIES）

- SWE-bench 已成为编码 agent 最主流基准（2,294 个任务、12 个 Python 仓库，F2P/P2P 单测验证），SWE-bench Lite 榜首成绩自 2023 年 10 月的 3% 涨到 43%（§1）。
- 但它只覆盖真实软件工程的一小部分：17 个仓库几乎全是 PyPI 式 Python 包、结构雷同，且**只有 5.6% 的任务含图像**、从未考察图像/视频在软件任务中的作用（§1; §2.1 Limitations）。
- 论文核心问题："Do AI Systems Generalize to Visual Software Domains?"——选择前端 JavaScript 作为未覆盖域的代表性切入口（JavaScript 是近十年最流行语言，issue 天然图文混排）（§1）。

### 2.2 基准构建流水线（§2.2 COLLECTION; Appendix B.1–B.3）

五步收集法（135k PR → 最终 619 任务）：
1. 选库：GitHub 搜索 ≥5,000 stars 且 ≥500 PRs 的 JavaScript 用户可见库，人工挑出 17 个（每库源码 ≥70% JS/TS，无 Python）（§2.2）。
2. 筛含视觉素材的 [issue, PR] 对（issue 文本或测试代码中有指向 jpg/png/gif/mov 的链接）：135k PR → 1,478 候选（§2.2; Table 13）。
3. 搭建 JS 执行环境：SWE-bench 的 Docker 不支持 JS，需加装 Node.js、Chrome 等；逐库编写安装/测试脚本，**平均每库 10 小时人工试错**；1,478 → 679 可运行（§2.2）。
4. 剔除不稳定测试（同一 patch 多次运行结果不一致）：679 → 643（§2.2）。
5. 人工验证并删除不可能完成的任务（24 个）：643 → **619 最终任务**（摘要作 617）；测试集 517 任务/12 库，开发集 102 任务/5 库，且每库在测试集有"等价"库便于方案迁移（§2.2; §2.3; Appendix A.1）。
- 额外资产工程：下载所有图像/视频/复现代码（防止链接失效）；约 17% 任务含在线 IDE 链接（CodeSandbox 63、JSFiddle 25、CodePen 21、StackBlitz 5），需脚本/浏览器自动化抽取并后处理成可直跑网站（Appendix B.3）。

### 2.3 数据集特征刻画（§2.3 FEATURES; Appendix A.2, A.3; D.1–D.4）

- **图像多样性**：862 张 problem-statement 图像分七类——网页 UI 截图 401、代码截图 194、图示/图表 107、报错信息 54、地图 35、艺术图 38、数据可视化 28；类别与具体仓库强耦合（如地图图仅出自 openlayers）（§2.3; Table 20）。
- **多媒体形态**：221 任务有多图、70 任务有视频（bpmn-js 有 43 个 gif 复现）、carbon 有 67 组 actual/expected 对照图；69 个任务（Chart.js、openlayers）用**像素级视觉测试**判分，共 273 张参考截图（§2.3; A.2）。
- **图像必要性（人工标注）**：80%（691/862）的图像"无法用文本无损表达"；83.5%（465/557）的含图任务被标注为"缺图不可解"——图不是装饰而是解题必需（§2.3; D.2; D.3）。
- **难度曲线**：13% <15min、43% 15min–1h、38% 1–4h、6% >4h；整体比 SWE-bench 更难更长（SWE-bench Lite 对应为 24.5/53.3/19.4/2.8），标注者间 Fleiss' kappa 0.78（§2.3; Table 21; D.4）。
- **改动更分散**：仅 40% 任务改单文件（SWE-bench 为 83%）、32.5% 改单函数（SWE-bench 65%）；28%（174 个）参考解改动 ≥2 种文件类型（js/tsx/scss/html/lua 等）；中位数任务：issue 文本 105 词、代码库 549K 行/1799 文件、gold patch 改 27 行/2 文件/3 函数、1 个 F2P + 5 个 P2P 测试（§2.3 Table 2; §4.1; A.2 Table 8; A.3）。
- **多语言 issue**：55 个任务含非英文（38 个中文，26 个来自阿里巴巴 next 组件库）（A.2）。

### 2.4 既有系统可迁移性考察与适配（§3.1 DO EXISTING SYSTEMS GENERALIZE?; C.1）

对 SWE-bench 榜首开源系统逐一考察，发现"为 Python/SWE-bench 深度定制"是普遍问题：
- **SWE-agent**（LM + shell + ACI，Python 特定组件最少）：可迁移。评测三配置——SWE-agent Base（原版 ACI）、SWE-agent JS（编辑命令换 ESLint 语法检查）、SWE-agent M（再加 `open webpage`/`screenshot`/`open image` 等浏览器与看图命令，用 Xvfb/xwd 模拟显示器）（§3.1; Table 14; C.1）。
- **Agentless**（两阶段 localize-then-repair，定位依赖 Python `ast`）：直接换 tree-sitter 仍为 0%（Python 中心假设残留），作者从零写了自定义 JS 解析器（15 小时人工），才得到可用的 Agentless JS（§3.1; §4.1; C.1）。
- **AutoCodeRover / Moatless**：定位/检索 API 深度绑定 Python AST 与 SWE-bench 仓库先验，重写等于再造一个新系统，**放弃评测**（§3.1; C.1）。
- **RAG 基线**：继承 SWE-bench 的 BM25（pyserini）检索与提示结构，patch 示例换成 JavaScript，并在提示中加入 issue 链接里的复现代码（§3.1; C.1）。

### 2.5 实验设置（§3.2 EXPERIMENT SETUP; C.2）

- 模型：仅 GPT-4o（gpt-4o-2024-08-06）与 Claude 3.5 Sonnet（claude-3-5-sonnet-20240620）——当时唯一同时满足长上下文+多模态+结构化输出的 LM（§3.2）。
- 基线五个系统：RAG、SWE-agent Base/JS/M、Agentless JS；全部只在开发集上调参（鼓励社区遵循"开发集迭代、测试集只评一次"惯例）（§3.2; A.1; C.2）。
- 指标：% Resolved（主指标）与 $ Avg. Cost（每任务平均推理成本）（§3.2）。
- 超参搜索：SWE-agent 历史展示窗口 {5, 9}（50 个开发任务）；RAG 上下文 {32K, 64K, 100K} × 是否带图（每个配置跑 5 次取均值）（C.2; Tables 15–16）。

### 2.6 主要结果（§4 RESULTS; Table 3）

- 测试集全员低迷：SWE-agent 系列平均 11.5% resolved，RAG 平均 5.5%，Agentless JS 平均 3.9%；最佳单配置 SWE-agent M + GPT-4o 12.2%（Abstract 表述为 12% vs 次优 6%）（§4; Table 3; Abstract）。
- 换 LM（GPT-4o ↔ Claude 3.5 Sonnet）与加 JS 专属定制对绝对性能影响很小；多模态工具的收益在消融中方向不明但存在亮点（§4）。
- 时间维度分析：按任务原始解决年份切分，**未发现训练集泄漏带来的测试集优势**——SWE-agent M (GPT-4o) 在其知识截止（2023-10）之后的任务上反而更好（post 47.1% vs pre 11.0%；按 post 分布重加权后 pre 27.6%）（§4; C.3; Tables 18–19）。

### 2.7 分析：视觉理解、定位模块与多模态工具（§4.1 ANALYSIS; Tables 4–5; Figure 3）

- **视觉理解是硬瓶颈**：去掉图像后所有系统都掉分（如 SWE-agent JS + GPT-4o 11.0%→8.0%，Claude 16.0%→13.0%；RAG + Claude 14.1%→11.2%）；在标注"图像必要"的子集上掉分更狠（SWE-agent JS 带图 17.6% vs 无图 11.1%）；纯文本图像子集几乎不受影响（23.1% vs 23.1%），非文本视觉内容才是主要信息增量（Table 4; Table 5）。
- **定位模块过度 Python 工程化**：Agentless JS 文件定位 F1 仅 0.142（SWE-agent 0.367）；典型失败——grommet-6749 中以箭头函数声明式定义的 `Tab` 组件不被识别，修复阶段干脆用命令式重写整个组件，而参考解只是小改声明式实现；给定原始代码时 GPT-4o 本可正确定位（§4.1）。
- 由此提出核心设计论断：**可泛化的 LM 软件工程系统应强调"交互"而非"问题求解"**——把求解负担留给 LM，为人 LM-first 地建导航/操作环境的工具，而不是把 LM 嵌进人工流水线的固定环节（§4.1）。
- **多模态工具双刃剑**：SWE-agent M 的网站工具约占 20% 动作（GPT-4o 在 38.3% 实例上建站截图、平均 7.5 张截图，用于迭代复现与验证）；但也使成本超限终止的尝试近乎三倍；若剔除因成本提前终止的低质量提交，GPT-4o 正确提交占比从 10.4% 近乎翻倍到 19.6%（Claude 无此收益）——记录整体"ambiguous"（§4.1; Figure 3）。

### 2.8 相关工作定位（§5 RELATED WORK）

- 定位为软件工程基准（SWE-bench）与多模态代码生成（Design2code、MMCode、Plot2Code 等）两条线的合流，且用真实 GitHub 任务克服合成短题的局限（§5）。
- 首个**有意义地耦合"网页导航"与"软件工程"**两类 agent 任务的基准：agent 可在代码修改与其浏览器渲染效果之间迭代（此前 web 工具多为纯文本表示、无明确下游目标）（§5）。

### 2.9 结论、局限与未来工作（§6 CONCLUSION; Appendix E LIMITATIONS）

- 结论：SWE-bench M 是首个评估编码 agent 处理真实视觉软件任务的基准；现有系统最高解决率仅 12.2%；基准应促使社区构建不过拟合 SWE-bench/Python 的通用、语言无关方案（§6）。
- 局限（作者自陈）：范围可在三个轴扩展——更多语言（Python/C++/Rust）、更多模态（音频等）、更多任务/库；扩展极耗人力，宁缺毋滥；模型与环境（更强浏览能力、更多工具、未来 GPT/Claude 版本）都待改进（Appendix E）。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 基准规模 | 619 任务 / 17 个 JS 库（135k PR → 1,478 → 679 → 643 → 619；摘要作 617）；测试集 517 任务/12 库 | §2.2; §2.3; Table 13 |
| 图像必要性（人工标注） | 83.5%（465/557）含图任务"缺图不可解"；80%（691/862）图像无法用文本无损表达 | §2.3; D.2; D.3 |
| 最佳系统解决率（test，GPT-4o） | SWE-agent M 12.2%（$2.94/任务）；Abstract 表述：12% vs 次优 6% | Table 3; Abstract |
| 系统平均解决率（test） | SWE-agent 系列 11.5% vs RAG 5.5% vs Agentless JS 3.9% | §4 |
| Agentless JS 迁移代价 | 不适配=0%（dev）；tree-sitter 直换仍 0%；自写 JS 解析器耗 15 小时后 dev 仅 4.6%（Table 3 平均） | §3.1; §4.1; Table 3 |
| 文件定位 F1（dev，Claude 3.5 Sonnet） | Agentless JS 0.142 vs SWE-agent 0.367 | §4.1 |
| 去图消融（dev） | SWE-agent JS：GPT-4o 11.0%→8.0%、Claude 16.0%→13.0%；RAG：GPT-4o 10.0%→8.0%、Claude 14.1%→11.2% | Table 4 |
| 图像必要性分层（dev，Claude） | "必要"子集 SWE-agent JS 带图 17.6% vs 无图 11.1%；纯文本图子集 23.1% vs 23.1%（不掉分） | Table 5 |
| 多模态工具对提交质量 | 剔除成本超限提交后，GPT-4o 正确提交占比 10.4%→19.6%（近乎翻倍）；但成本超限终止尝试约增 3 倍 | §4.1; Figure 3 |
| 污染检查（GPT-4o 截止期前后） | post-cutoff 47.1% vs pre-cutoff 11.0%（重加权 27.6%）——无泄漏迹象 | §4; C.3; Table 19 |
| 难度分布（100 任务人工标注） | <15min 13%、15min–1h 43%、1–4h 38%、>4h 6%（SWE-bench Lite：24.5/53.3/19.4/2.8） | §2.3; Table 21; D.4 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2410.03859 |
| 数据 / 代码 / 排行榜 | https://www.swebench.com/multimodal （论文脚注：Data, code, and leaderboard） |
| 上游基准 SWE-bench | Jimenez et al., 2024a, arXiv:2310.06770 |
| 评测基线系统 | SWE-agent（arXiv:2405.15793）；Agentless（arXiv:2407.01489）；AutoCodeRover（arXiv:2404.05427）；Moatless（github.com/aorwall/moatless-tools，JS AST 支持见 PR #34）；BM25 RAG 基线（pyserini） |
| 视觉测试工具链 | Puppeteer（github.com/puppeteer/puppeteer）、Pixelmatch（github.com/mapbox/pixelmatch）、ESLint、Xvfb/xwd |
| 本库关联 | ContextEngineering/12（SWE-bench 原文）、AgentParadigms/21（基准污染问题） |

## 5. 一句话索引（给 Agent 用）

> 评估编码 agent 可迁移性 / 需要视觉软件域基准时读这篇：SWE-bench Multimodal（arXiv:2410.03859）从 17 个 JavaScript 前端库筛出 **619 个含图像任务**（83.5% 人工标注"缺图不可解"），单测+像素级视觉测试判分；SWE-bench 榜首系统迁移后大幅崩塌——**最佳 SWE-agent M + GPT-4o 仅解决 12.2%**（次优约 6%），Agentless/AutoCodeRover/Moatless 因 Python 特化 AST 定位几乎不可迁移（Agentless 适配后仍 4.6%，定位 F1 0.142 vs 0.367）；结论：LM-first、语言无关交互式 scaffold 才是方向。
