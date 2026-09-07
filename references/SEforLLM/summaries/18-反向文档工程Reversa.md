---
title: "Reversa: A Reverse Documentation Engineering Framework for Converting Legacy Software into Operational Specifications for AI Agents"
source_pdf: "18-Oliveira-Reversa_Reverse_Documentation_v1.pdf"
arxiv_id: "2605.18684"
arxiv_version: "v1"
authors:
  - "Sanderson Oliveira de Macedo"
  - "Ronaldo Martins da Costa"
year: 2026
venue: "arXiv（预印本，2026-05-18）"
type: "先行工作（反向文档生成侧） + 设计参考"
generated_at: "2026-08-30"
summary_version: "1.0"
---

# 论文摘要：Reversa——把遗留软件反向文档化为 AI 代理可用的操作规格

## 1. 适用场景

- 当你需要**"反向文档工程"的可操作定义与多智能体实现**（从遗留系统派生可追溯、带置信标注的操作规格，供编码代理而非人类读者消费）时，读这篇。
- 当你要为 **LLM 生成文档的"虚假确定性"问题**设计防线（confirmed/inferred/gap 三分类 + 缺口登记 + 人审问题清单）时，读其 §3.5 与 §5.3。
- 当你要设计**遗留系统迁移（如 COBOL→Go）的规格驱动重建流程**（inventory→模块分析→单元级规格→parity 场景→重建计划）时，读其 §3–§5。
- 当你在做**"反向生成物忠实性的验证"研究**，需要引用生成侧自认的评估空白（置信指数系自评、expert precision/agent utility 未测量）时，读其 §4 Table 3 与 §7。

> 锚点：Abstract; §1 Introduction（5 贡献/4 RQ）; §2 Related Work（Table 1）; §3 Framework（Fig.1; Fig.2; Table 2）; §4 Evaluation（Table 3）; §5 ATM Case（Fig.3; Table 4–7）; §6 Discussion; §7 Threats; §8 Conclusion

## 2. 主要观点与方案

### 2.1 问题定义：反向文档工程（§1; §2.5）

- 遗留系统沉淀的业务规则、架构决策与操作例外大多隐含在代码、数据、配置与维护实践中；LLM 编码代理则依赖可靠上下文、正确性判据与行为契约才能低风险修改真实系统——两者之间缺一座系统性桥梁（Abstract; §1）。**反向文档工程（reverse documentation engineering）**=从既有系统派生技术文档与操作规格，使行为、架构、领域规则、缺口与置信级别显式化（§1）。
- 与经典逆向工程划界：不是从二进制恢复代码，也不自动重构/现代化系统，而是派生"文档契约"（documentary contracts）指导 AI 辅助维护、迁移与演化；明确声明"不取代人工验证、不主张经验优越性"（§1; §2.1）。
- 定位综合（§2.5; Table 1）：经典逆向工程提供概念基础但输出对准编码代理；LLM 仓库文档（RepoAgent 等）须补 traceability/confidence/gaps 才能操作化；需求/规格生成（ReqInOne、AutoReSpec 等）多以既有需求/注释为源，Reversa 以遗留系统本身为源；软件代理线（SWE-bench/SWE-agent 等）通常假设任务与正确性判据已备，Reversa 提供其前置层。
- 关键动机证据（§2.2，引 Macke & Doyle [23]）：**错误的文档会损害 LLM 代码理解，而缺失或不完整的文档未必造成同类损害**——直接支撑核心设计决定：文档断言必须携带显式置信级别与缺口，而非把脆弱推断写成事实。

### 2.2 框架：多智能体流水线 + 三层架构（§3）

- **五个设计目标**（§3.1）：①产出操作契约而非叙事解释；②每个相关断言可追溯到遗留证据（文件/模块/路由/schema/查询）；③不确定性显式化（confirmed/inferred/gap）；④安装不破坏遗留工程（文件登记+版本化+manifest 保护）；⑤跨编码代理引擎可移植。
- **三层架构**（§3.2）：Node.js CLI（`npx reversa install .`，命令含 install/update/status/uninstall/add-agent/add-engine/export-diagrams）；安装与保全层（引擎探测、提示词、文件写入、校验、manifest）；代理层（可安装 skills）；工件层（`_reversa_sdd/` 下的 inventory、模块分析、单元级规格、traceability 矩阵、gaps、置信报告）。
- **可移植安装与 SHA-256 manifest**（§3.3）：安装时探测 13 种引擎（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、Antigravity、Kiro、Opencode、Cline、Roo Code、GitHub Copilot、Aider、Amazon Q Developer），为每种引擎写入对应入口文件（AGENTS.md/CLAUDE.md/GEMINI.md 或引擎专属规则）；`.reversa/_config/files-manifest.json` 记录安装文件的 SHA-256 哈希，将文件分类为 intact/modified/missing——更新时保留用户改过的文件，卸载时不误删非 Reversa 内容。
- **代理团队**（§3.4; Table 2）：Discovery 团队 = orchestrator（reversa）+ scout（项目表面测绘）→ archaeologist（模块技术分析）→ detective（隐含业务规则/状态/权限/例外提取）→ architect（架构综合与影响矩阵）→ writer（写成单元级规格 requirements.md/design.md/tasks.md + traceability）→ reviewer（复核断言置信与缺口，产出 confidence-report.md/questions.md/gaps.md）；另有 Migration 团队（重建/现代化规划）与 Code Forward 团队（新意图→需求→与既有规格一致性审计）。角色分解的理由不是断言多代理必然更优，而是在任务间建立检查点，使错误断言可回溯到引入阶段（§6）。
- **置信/缺口/可追溯模型**（§3.5）：confirmed=代码或可验证工件中有直接证据；inferred=有模式/命名/流程/结构支撑但不得写成确定；gap=无法安全确定、需人审。更完整的文档级别下生成 `traceability/code-spec-matrix.md` 与 `traceability/spec-impact-matrix.md`。
- **闭环**（§3.6; Fig.2）：discovery（抽取知识）→ migration（消费规格做现代化决策与 parity 规格）→ Code Forward（以规格为基准审计新需求）——反向文档成为**被维护的操作工件**而非静态文档；论文自认此闭环在本文仅为设计贡献 + 初步探索证据（§3.6）。

### 2.3 评估协议（§4; Table 3）

- 7 个候选度量：file coverage / unit coverage / traceability density / confidence distribution / blocking gaps / expert precision / agent utility；另要求记录运营成本（执行时间、人机交互次数、生成问题数、工件大小、traceability 维护与评审工作量）。**ATM 案例中 expert precision 与 agent utility 标注为"未测量"**（Table 3; §7）。
- 基线设计（§4）：①单一仓库文档 prompt（无角色分解）；②无先验规格的通用编码代理；③常规文档或静态分析工具。明确"不应按文本量比较，而按 utility、traceability、显式不确定性、引导后续行动的能力比较"。

### 2.4 探索性案例：ATM COBOL→Go（§5; Fig.3; Table 4–7）

- **遗留表征**（§5.1; Table 4）：教育性项目、简化银行域、单用户单进程 ATM（GnuCOBOL + C 键盘读取辅助）；parity 范围 5 个活动模块（MENU/CONTA/EXTRATO/UTIL/kbdread）；索引与顺序 .DAT 文件持久化；无自动化测试/CI-CD/Docker。排除 2 个组件：ADD-CLIENTE（域外技术操作）、x25-communication（有规格无实现）。目标系统=Go + SQLite + Gherkin parity 测试。
- **流水线执行**（§5.2）：2026-05-04 至 05-07 执行；discovery 产出 inventory/代码分析/架构/领域模型/状态机/依赖/questions/gaps/置信报告；migration 产出 briefing/范式与拓扑决策/迁移策略/风险登记/cutover 计划/目标架构/领域与数据模型/数据迁移计划/parity 规格/Gherkin 测试/编码交接。
- **置信与缺口**（§5.3; Table 5; Table 6）：活动范围共分类 **517 条断言 = 490 confirmed + 24 inferred + 3 gaps**；按 confirmed=1.0、inferred=0.5 的加权规则得内部置信指数 **97.1%**——论文明确该指数是流水线自分类的汇总，"**不应解释为事实精度**"（无外部审计）。模块级指数：menu 98.5% / conta 97.8% / extrato 95.9% / util 96.7% / kbdread 97.9%。项目级登记 **10 个缺口**：3 critical + 3 moderate + 2 cosmetic + 2 out of scope；处理结果=5 个经记录在案的人审决策解决、3 个残留、2 个移出 parity 范围。
- **重建进度**（§5.3; Table 7）：迁移计划 11 个任务，盘点时 9 个完成，Docker parity 进行中，最终 cutover 与最终验证未完成——论文据此只主张"过程结构化与合理性"，不主张迁移成功（§5.3; §7 结论效度）。
- **谨慎解释**（§5.4; §7）：单系统、简化域、单干系人、教育性迁移；无与单代理/常规文档工具/无规格执行的受控比较（内部效度）；confidence distribution/gaps/任务完成度不直接度量事实准确性、代理效用或最终迁移成功（构念效度）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| 断言分类（活动范围） | 517 条 = 490 confirmed + 24 inferred + 3 gaps | Abstract; §5.3 |
| 内部置信指数 | 97.1%（confirmed=1.0/inferred=0.5 加权；流水线自评、无外部审计，原文声明"不应解释为事实精度"） | §5.3; Table 5 |
| 模块级置信指数 | menu 98.5%（32 条）/ conta 97.8%（129 条）/ extrato 95.9%（124 条）/ util 96.7%（115 条）/ kbdread 97.9%（90 条） | Table 5 |
| 项目缺口登记 | 10 个：3 critical、3 moderate、2 cosmetic、2 out of scope；5 解决 / 3 残留 / 2 移出范围 | §5.3; Table 6 |
| Gherkin parity 场景 | 53 个（覆盖 login/balance/withdrawal/deposit/transfer/statement/金额格式化/键盘掩码；原系统无任何自动化测试） | Abstract; §5.2; Fig.3 |
| 重建计划进度 | 11 个任务完成 9 个；Docker parity 进行中；cutover 与最终验证未完成 | Abstract; §5.3; Table 7 |
| parity 模块范围 | 5 个活动模块（MENU/CONTA/EXTRATO/UTIL/kbdread）；2 个组件排除 | §5.1; Table 4 |
| 支持的代理引擎 | 13 种（Claude Code、Codex、Cursor、Gemini CLI、Windsurf、Antigravity、Kiro、Opencode、Cline、Roo Code、GitHub Copilot、Aider、Amazon Q Developer） | §3.3 |
| 评估协议度量 | 7 个候选度量，其中 2 个（expert precision、agent utility）在案例中未测量 | §4; Table 3 |
| 贡献与研究问题 | 5 项贡献、4 个 RQ（RQ1 流水线/RQ2 置信机制/RQ3 角色分解/RQ4 评估协议） | §1 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2605.18684 |
| 框架本体 | Reversa：Node.js CLI（`npx reversa install .`），工件落 `_reversa_sdd/`，SHA-256 manifest 保全（§3.2–§3.3；公开仓库链接原文未明确） |
| 代理角色 | Table 2 的 9 个角色/团队：reversa、scout、archaeologist、detective、architect、writer、reviewer、Migration、Code Forward |
| 关键引文 | Macke & Doyle（错误文档损害 LLM 代码理解，NAACL 2024 Findings [23]）；RepoAgent [22]；SWE-bench [15]/SWE-agent [38]；ChatDev [26]；traceability 影响映射研究（Tian et al. [30]） |
| 关联论文 | 本库 17-SDD（spec-first/anchored/as-source 正向谱系——Reversa 是其"从代码反向到契约"的对偶）；规格生成侧：AutoReSpec [5]、ReqInOne [42]、Xie et al. [37] |

## 5. 一句话索引（给 Agent 用）

> 双作者框架论文（2605.18684 v1，2026-05）：定义"反向文档工程"=从遗留系统派生可追溯、带置信标注的操作规格供编码代理消费；多智能体流水线（scout→archaeologist→detective→architect→writer→reviewer + Migration/Code Forward 团队）+ Node.js CLI 跨 13 种代理引擎 + SHA-256 manifest 保全；核心机制=confirmed/inferred/gap 三分类置信模型 + code-spec/spec-impact 追溯矩阵 + 缺口登记；COBOL→Go ATM 探索案例产出 517 条断言（490/24/3）、内部置信指数 97.1%（流水线自评、无外部审计、非事实精度）、10 个缺口（5 解决/3 残留/2 移出）、53 个 Gherkin parity 场景、11 任务完成 9；expert precision 与 agent utility 未测量，最终 parity 与 cutover 未完成——定位为框架+评估协议+首个探索性证据点，非有效性结论。

## 6. 与本仓库研究的相关性注记

- **与 C-2 课题的对应（生成侧先行工作）**：研究备忘 §13.4-C2 立项"反向文档化的可信度验证"——敏捷多轮迭代后由 LLM 反向整理过程文档以替代前期重文档。Reversa 正是该方向的**生成侧**直接先行工作：它把遗留系统转为可追溯操作规格，并证明反向产物可以结构化为"操作规格 + 三分类置信标注 + code↔spec 追溯矩阵 + 缺口清单"（§3.5），即为 C-2 中被验证对象提供了已发表的工件形态参照。差异按备忘既定表述：**他们生成、我们验证**。
- **可借鉴机制**：①confirmed/inferred/gap 三分类与 1.0/0.5 加权置信指数（§3.5; §5.3）——为验证层提供了被验对象的元数据 schema（每条断言自带"证据是否直接"的自声明，验证器可按类别分派不同强度的检查）；②`traceability/code-spec-matrix.md` 与 `spec-impact-matrix.md` 的声明级锚定（§3.5）——与本仓库绑定闭包同构，可复用为"反向生成物↔代码/迭代历史"的锚点载体；③"错误文档比缺失文档更有害"（§2.2 引 Macke & Doyle）——论证验证层必要性的文献锚；④SHA-256 manifest 的 intact/modified/missing 三态分类（§3.3）——与 diff_models 的工件级比较思路互通；⑤Table 3 评估协议（7 度量+成本记录+基线设计）可被 C-2 实验直接继承，尤其其"专家精度/代理效用未测量"的空白自认。
- **论文未覆盖、本仓库可贡献的验证层空白**：Reversa 的 97.1% 置信指数是流水线自分类的汇总，论文自认"无外部审计、不应解释为事实精度"（§5.3; §7 内部效度），且全文没有任何确定性的忠实性检查器——忠实性最终仍落在人工评审。本仓库 requirement-to-spec 已有工具体系恰可补位：cases/loan-system/05-openapi-anchor 的 OpenAPI 反向生成 **byte-identical** 经验证明"反向生成物 ↔ 代码事实"可做确定性等价判定；tools/scripts/diff_models.py 可做规格级 diff。把绑定闭包/一致性/diff 检查应用于"反向生成物↔代码/迭代历史"的忠实性验证，正是 C-2 的核心贡献位，也恰好落在 Reversa 明示的 next steps（"evaluate the artifacts with experts…controlled comparison with baselines"，§8）中未提供自动化手段的空档。
