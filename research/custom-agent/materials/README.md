# 方向一：资料归档

按"框架官方资料 / 生态与案例 / 相关研究"分类。每条资料附一句话摘要与用途标注。

## 框架官方资料

| 资料 | 链接 | 摘要与用途 |
|---|---|---|
| pi-mono 仓库 | https://github.com/badlogic/pi-mono | pi 的 monorepo：coding-agent CLI、统一 LLM API、TUI/Web UI 库。方向一的一手资料来源 |
| pi 官网 | https://pi.dev/ | "minimal agent harness" 定位声明；定制机制（extensions/skills/prompt templates/themes）官方说明 |
| pi examples | https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples | SDK 与 extensions 示例集：生命周期钩子、自定义工具、subagent、git 集成、provider 定制——组件模型的直接参照 |
| DSH handbook | https://github.com/Electricitysheep/dsh-handbook | 社区手册：安装、`dsh web` / headless profile、插件模板（cordis.patch.yml 两步挂载）、配置参考。DSH 入门最快路径 |

## 生态与案例

| 资料 | 链接 | 摘要与用途 |
|---|---|---|
| dshfind 插件超市 | https://dshfind.com/zh/plugins | DSH 插件目录（含 RAG、subagent 管理、技能加载器等），观察"第三方组件"实际形态 |
| awesome-dsh-plugin | https://awesome-dsh-plugin.com/ | 500+ 条 DSH 插件清单，可做插件分类统计，归纳生态中已验证的组件类别 |
| Pi Mono Explained | https://hoangyell.com/pi-mono-explained/ | 第三方解读："反框架"设计哲学，理解 pi 定制边界的补充视角 |
| oh-my-pi（omp） | https://github.com/can1357/oh-my-pi | pi 的 fork+增强路线代表（subagents/LSP/advisor），其 /review reviewer 子代理与本项项目评审 skill 的对比见 `materials/ohmypi-reviewer机制对比.md`——分区并行 vs 重复采样、框架提示词 vs 可迭代资产、过程内 vs 阶段间三组对照 |

## 调研产出（2026-08-17，台账 #1/#2/#3）

| 文档 | 摘要与用途 |
|---|---|
| `materials/pi-mono-架构与定制机制.md` | pi-mono 分层架构（pi-ai / pi-agent-core / coding-agent）、JSONL 会话树、系统提示组装、五层定制机制（extensions/skills/templates/themes/provider）与 SDK 能力范围，关键结论附源码路径——组件模型与定制机制研究的一手基础 |
| `materials/dsh-架构与插件生态.md` | DSH 的 cordis.patch.yml 三层挂载（bundle→patch→settings）、插件 API 边界、skill/profile/settings.yaml、客户端 vs 宿主端插件、10 类生态插件归纳，及与 pi 的"配置式 vs 编程式"对比——#2 调研线产出，全部附 URL |
| `materials/团队级AI编码实践调研.md` | 2025-2026 团队采纳实证（DORA 2025、METR RCT、SO 调研）与反方证据、Spec Kit/Kiro/AGENTS.md 团队工作流建制化、多工具分层组合实践——场景分析与"专用 agent 落地土壤"的证据基础 |

## references 库内相关论文（2026-08-17 梳理）

按摘要索引（`references/*/summaries/INDEX.md`）筛选的对方向一有用的存量论文：

| 论文 | 位置 | 对方向一的用途 |
|---|---|---|
| Agent Harness Evolution（Don't Blame the LLM） | `references/AIOS/10` | 定制风险评估的直接证据：固定模型下 harness 变更本身引发质量回归，高风险组件是 **LLM Provider 层 + Context Management 层**——pi/DSH 定制五层中 provider 与上下文注入类扩展的变更需最谨慎；也提示专用 agent 需"Agentic QA"回归门禁 |
| Knowledge Activation: AI Skills | `references/ContextEngineering/09` | "技能 = 知识激活原语"：为组件模型的知识/技能层提供理论定位（skills 不只是提示片段，而是组织知识的最小单元） |
| From Registry to Repository（Agent Skills 实证） | `references/ContextEngineering/30` | 对真实技能库的写法/适配/维护实证——知识/技能层组件的粒度与演化规律，组件库设计的直接输入 |
| LLM-as-Code 与 ActPlane | `references/AIOS/07、08` | harness 的可编程定制面与策略执行（沙箱/权限）参照——对应 pi extensions 编程式定制与 DSH sandbox 接缝 |
| ICAE-Bench | `references/AIOS/11` | 交互式项目构建评测基准——方向一实验"专用 agent 效果评测"的可借鉴口径 |
| AGENTS.md 影响研究 + Do Context Files Help | `references/ContextEngineering/07、29` | 仓库级约定文件的增益消融证据——场景分析框架第 8 问（规范载体成熟度）的论文级支撑 |
| Anthropic Agentic Coding Trends | `references/AIOS/04` | 行业趋势背景（与台账 #3 团队实践调研互证） |

> 2026-08-17：团队实践调研（台账 #3）中引用的 2 篇 arXiv 论文（METR RCT 2507.09089、GenAI 技术债 2601.07786）全文已入库 `references/SEforLLM/`（09、10 号），下载校验见 `references/arxiv_2026-08_manifest.md`。

## 相关研究（本仓库内）

- `research/sdd/OpenSpec_Speckit_Superpowers_OMO框架对比.md` — Superpowers 的 skill 体系是"可复用组件"的成熟参照
- `research/context-engineering/` — 上下文组件（知识图谱、API 卡片、MCP）的已有积累

## 待补充

- [x] ~~pi SDK 参考文档细读摘要~~（2026-08-17 完成，见 `materials/pi-mono-架构与定制机制.md`）
- [x] ~~DSH 插件 API 官方文档细读摘要~~（2026-08-17 完成，见 `materials/dsh-架构与插件生态.md`）
- [ ] 其他 harness（Kimi Code / Claude Code）定制机制对比，用于迁移性分析
