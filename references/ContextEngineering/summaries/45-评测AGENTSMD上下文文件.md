---
title: "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
source_pdf: "45-Gloaguen-Evaluating_AGENTS_md_v2.pdf"
arxiv_id: "2602.11988"
arxiv_version: "v2"
authors:
  - "Thibaud Gloaguen"
  - "Niels Mündler"
  - "Mark Müller"
  - "Veselin Raychev"
  - "Martin Vechev"
year: 2026
venue: "arXiv"
type: "评测对照 + 内容索引"
generated_at: "2026-08-25"
summary_version: "1.0"
---

# 论文摘要：评测 AGENTS.md 上下文文件（ETH Zurich & LogicStar）

## 1. 适用场景

- 当你要决定**是否在仓库中维护 AGENTS.md / CLAUDE.md 等 context file、或是否让 agent 默认执行 /init 生成**时，读这篇——它给出"不显著提升成功率、成本却 +20% 以上"的大规模对照证据，直接检验并反驳了主流 agent 厂商的推荐。
- 当你要**设计或评测 agent 自动生成 context file 的能力**、需要一套严格评测框架时，读其 CTXBENCH 五阶段构建流水线与 NONE/LLM/DEV 三设置对照（§3; §4.1）。
- 当你要**制定 context file 的内容规范**（该写什么、不该写什么）时，读其 trace 分析与内容消融：指令会被遵循、repository overview 与既有文档冗余、testing/tooling 类指令推高成本（§4.3; §B）。
- 当你需要**从含 context file 的小众仓库挖 SWE-bench 式任务**（LLM 重写任务描述 + 生成回归测试）时，读其 §3 流水线与 §C 质量校验方法。

> 锚点：Abstract; §1 Introduction; §3 CTXBENCH; §4 Experimental Evaluation; §5 Limitations and Future Work

## 2. 主要观点与方案

- **研究问题与双基准设计**：AGENTS.md 类 context file 已进入 60'000+ 开源仓库并被厂商强推，但其对真实任务的效果从未被严格评测。作者在两类互补场景实验：SWE-BENCH Lite（300 任务、11 个热门 Python 仓库、无开发者 context file，只能测 LLM 生成）与自建 CTXBENCH（138 实例、12 个小众仓库、全部含开发者提交的 context file，三设置齐备）（§1; §4.1）。四个 agent×模型组合：CLAUDE CODE+SONNET-4.5、CODEX+GPT-5.2、CODEX+GPT-5.1 MINI、QWEN CODE+QWEN3-30B-CODER（本地 vLLM 部署）。
- **CTXBENCH 五阶段构建**：GitHub 搜索根目录含 AGENTS.md/CLAUDE.md、Python 主语言、有测试套件、≥400 PR 的仓库 → 规则+LLM 双重过滤 PR（须引用 issue、改 Python 文件、引入确定性可测行为；不要求 PR 自带测试，由 LLM 补生成）→ coding agent 自动搭建环境（仅保留至少一个测试通过者，占过滤后实例 87%）→ LLM 重写为 6 段式标准化任务描述（防泄漏解法）→ LLM 生成回归测试（fail-on-base/pass-on-patch，人工去过拟合，25/138 实例被手工修测试）。全程 GPT-5.2+CODEX，从 5694 个 PR 得 138 实例，生成测试对修改代码平均覆盖 75%（§3; Table 1; §C）。
- **主结论：不提性能、稳增成本**：LLM 生成的 context file 在 8 个 agent×benchmark 设置中 5 个降低成功率（平均 −0.5% SWE-BENCH / −2% CTXBENCH，p=0.87 / 0.37，不显著），但在每个设置都增加步数（平均 +2.45 / +3.92）与成本（+20% / +23%，p<0.001%）。开发者提交文件（DEV）平均 +2.4%（p=0.21 不显著），显著优于 LLM 生成（p=0.038；§1 表述为平均领先 7%），对除 CLAUDE CODE 外的所有 agent 有提升，但同样增加步数（+3.34）与成本（至多 +19%）（§4.2; Table 2; Table 3; Table 6）。
- **机制：指令被遵循 → 更多测试/探索/推理，但 overview 无效**：trace 分析（GPT-OSS-120B judge，334 个 intent 归并为 10 类）显示 context file 使 agent 更多跑测试、grep/read/write 更多文件、更多用仓库特定工具；工具被提及才被使用（uv 1.6 vs <0.01 次/实例）——无收益不能归因于指令遵循差。模型厂商力荐的 repository overview（SONNET-4.5 生成文件 100% 含 overview）不能减少 agent 触及 PR 修改文件所需的步数（GPT-5.1 MINI 反而显著变多，因为它反复查找并重读已注入上下文的 context file）。遵循额外指令也更"费脑子"：GPT-5.2 reasoning tokens +22%（SWE-BENCH）（§4.3; Figure 4–6; §A.2）。
- **消融与替代解释排除**：换更强模型生成（SWE +2% / CTX −3%）、换 CODEX/CLAUDE CODE 生成 prompt、context file 长度、删除 Overview/Tooling/Testing 类别、按知识截止切分的训练污染（截止前实例占 17%/40%/12%/12%）均不改变结论。唯一例外：人工删除仓库全部文档（*.md、示例、docs/）后，LLM 生成的 context file 平均 +2.7% 且反超开发者版本——说明其内容主要是冗余文档，也解释了小众无文档仓库上的正面坊间证据（§4.4; §B; Table 7; Figure 12–14）。
- **作者建议**：暂缓默认使用 LLM 生成的 context file（与厂商推荐相反）；人工文件只写 README 之外的非标准约定/非功能要求；任何 context file 改动上线前须像本工作一样严格评测（§1; §6）。局限：仅 Python、仅任务解决率（未测安全/效率）（§5）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| LLM 生成 context file 对成功率（vs None） | SWE-BENCH −0.5%、CTXBENCH −2%（CMH 检验 p=0.87 / 0.37，不显著；8 设置中 5 个下降） | §4.2; Table 3 |
| LLM 生成文件对成本/步数（vs None） | 成本 +20%（SWE-BENCH）/ +23%（CTXBENCH）（p<0.001%）；步数平均 +2.45 / +3.92（置换检验 p=0.0287 / 0.00004） | §4.2; Table 2; Table 6 |
| 开发者文件（DEV）vs None | 成功率平均 +2.4%（p=0.21 不显著）；步数 +3.34、成本至多 +19% | §4.2 |
| DEV vs LLM 生成 | 显著更优（p=0.038）；§1 表述为平均领先 7% | §1; §4.2; Table 3 |
| CTXBENCH 成功率明细（None→LLM→DEV，%） | SONNET-4.5 73.2→65.2→70.3；GPT-5.2 65.2→68.1→68.1；GPT-5.1 MINI 54.3→50.7→55.8；QWEN3-30B 45.7→47.1→53.6（SWE-BENCH None→LLM：59.9→58.7 / 56.6→54.4 / 47.7→47.6 / 31.1→32.4） | Table 5 |
| 指令遵循度（工具被提及 vs 未提及，次/实例） | uv：1.6 vs <0.01；仓库特定工具（repo_tool）：2.5 vs <0.05 | §4.3; Figure 9 |
| overview 存在率与有效性 | SONNET-4.5 生成文件 100% 含 overview、GPT-5.2 99%、QWEN3-30B 95%、GPT-5.1 MINI 36%；但不缩短触及相关文件的步数（排除 3% 从未触及的实例；GPT-5.1 MINI 显著变长） | §4.3 |
| reasoning tokens（vs None） | LLM 文件：GPT-5.2 +22%（SWE-BENCH）/ +14%（CTXBENCH）、GPT-5.1 MINI +10% / +10%；DEV 文件：GPT-5.2 +20%、GPT-5.1 MINI +2%（论文未按基准拆分） | §4.3; Figure 6 |
| 删除仓库全部文档后 | LLM 生成文件平均 +2.7% 且优于 DEV（CTXBENCH，排除 CLAUDE CODE） | §B; Figure 12 |
| 类别消融（GPT-5.2） | 无类别显著影响准确率；删 Testing 类显著降成本：CTXBENCH $0.4715→$0.3730（p=0.023）、SWE-BENCH $0.3272→$0.2756（p=0.0035） | §B; Table 7 |
| CTXBENCH 构建产出 | 138 实例 / 12 仓库（自 5694 个 PR）；环境搭建通过率 87%；生成测试对修改代码平均覆盖 75%（2.5%–100%） | §3; Table 1 |
| 任务描述精炼迁移到 SWE-BENCH | 准确率约 +15%（GPT-5.2：70.8% vs 原始 57.0%；QWEN3-30B：46.9% vs 30.3%），模型排序不变 | §C; Table 8 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2602.11988 |
| CTXBENCH 基准 | 论文自建（§3）；源仓库许可证 Apache-2.0/MIT/AGPL-3.0/GPL-3.0/BSD-3-Clause（§D）；正文未附独立发布仓库链接 |
| AGENTS.md 格式 | https://agents.md/（论文 [1]，报告 60'000+ 公开仓库采用） |
| 被评测 agent | Claude Code（https://code.claude.com/docs/en/overview）、Codex（https://github.com/openai/codex）、Qwen Code（https://github.com/QwenLM/Qwen3-Coder） |
| 对照基准 | SWE-bench（ICLR 2024，[15]；本文用 Lite 300 任务） |
| 关联工作（context file 实证/生成） | Agent READMEs 实证（arXiv:2511.12884，[9]）；Context Engineering for AI Agents in OSS（arXiv:2510.21413，[20]）；Agentic Context Engineering（arXiv:2510.04618，[41]） |
| 本库关联摘要 | ContextEngineering/07（AGENTS.md 效率影响）、29（Do Context Files Help 双 Agent 消融）——同属 context file 实证族 |

## 5. 一句话索引（给 Agent 用）

> ETH Zurich & LogicStar：在 SWE-bench Lite（300 任务）+ 自建 CTXBENCH（138 实例、12 个含开发者 context file 的小众仓库）上，用 4 个 coding agent（Claude Code/Sonnet-4.5、Codex/GPT-5.2、Codex/GPT-5.1 Mini、Qwen Code/Qwen3-30B）× None/LLM 生成/DEV 三设置对照——context file 不显著提升成功率（SWE −0.5% p=0.87、CTX −2% p=0.37），成本却 +20%/+23%（p<0.001%）；DEV 显著优于 LLM 生成（p=0.038、平均高 7%）但对 None 仅 +2.4%（不显著）；指令被良好遵循（uv 1.6 vs <0.01 次/实例）而 overview 无效；仓库无文档时 LLM 文件才 +2.7%。建议：暂缓 LLM 生成的 AGENTS.md，人工文件只写 README 之外的非标准约定（2602.11988 v2，2026-06）。
