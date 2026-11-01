# TDD-Methodology 参考资料目录

本目录收集"TDD × LLM 测试生成"论文：同源生成（代码与测试出自同一模型）的失效机制、AI 生成测试的质量实证、人机分工与 TDD 流程治理。2026-11-01 首批入库 8 篇——来源为研究者提供的「测试全绿但业务跑偏」问题论文清单（三类：失效机制 / 实证研究 / 治理方法论）。

入库纪律：全部条目经 arXiv 官方 abs 页 / Springer 章节页核对元数据（标题/作者/版本/日期/venue）后下载，pypdf 校验页数与首页题名；摘要为基于 PDF 全文的精读级 summary_version 1.0（依 `../design/kb-app/06-摘要构建与命名规范.md`）。**清单中若干数字与结论主张经全文核对不成立**，逐条勘误见 [`summaries/INDEX.md`](summaries/INDEX.md) 末节与 [`../arxiv_2026-11_manifest.md`](../arxiv_2026-11_manifest.md) 勘误记录——引用本目录任何数字请以摘要为准，勿以原清单为准。

## 文件清单

| 文件 | 说明 |
|------|------|
| `01-Konstantinou-Risk_of_Coding_Before_Testing_v1.pdf` | 同一 LLM 先码后测的错误传播（error propagation / aligned failures）：检出率 25%→约 14%，提示工程救不回（arXiv 2026，SnT 卢森堡） |
| `02-Cui-Tests_as_Prompt_TDD_Benchmark_v1.pdf` | Tests as Prompt / WebApp1K：测试即提示的 LLM-TDD 基准，1000 题×19 模型（曾以《Tests as Instructions》投 ICLR 2025，录用未核实） |
| `03-Jain-TestGenEval_v2.pdf` | TestGenEval：11 个高星开源仓库、68,647 条测试的真实单测基准；GPT-4o 全文件生成覆盖率仅 35.2%（ICLR 2025，Meta FAIR+CMU） |
| `04-Yang-Evaluation_LLM_Unit_Test_Gen_v2.pdf` | 5 款开源 LLM+GPT-4 参照的单测生成系统评测：覆盖率全面低于 EvoSuite，主因缺缺陷触发输入（ASE 2024） |
| `05-Alves-Quality_Assessment_Python_Tests_v1.pdf` | LLM 生成 Python 测试的质量评估：64.9% 错误为断言失效、41.2% 坏味道欠内聚（EASE 2025） |
| `06-Mock-Generative_AI_TDD_Preliminary_XP2024.pdf` | 生成式 AI 辅助 TDD 的人机分工 5 人初步实验：需质量监督、全自动组测试薄弱（XP 2024 Workshops, LNBIP 524） |
| `07-Hasanli-TDD_Governance_Multi_Agent_v1.pdf` | 多智能体代码生成的 TDD 治理：宣言 JSON + 提示/引擎双层强制、修复上限 N=3、提案级 4 道闸门（设计短文，无量化实验） |
| `08-Piya-LLM4TDD_Best_Practices_v1.pdf` | LLM4TDD：人写测试、ChatGPT 迭代生成代码的流水线，70 题 LeetCode 成功率 88.5%（arXiv 2023） |

摘要索引见 [`summaries/INDEX.md`](summaries/INDEX.md)；下载台账与哈希见 [`../arxiv_2026-11_manifest.md`](../arxiv_2026-11_manifest.md) 与 [`../arxiv_2026-11_SHA256SUMS`](../arxiv_2026-11_SHA256SUMS)。

## 快速定位

- **理解「测试全绿、业务跑偏」的机制**：01（同源生成独立性丧失）→ 03（覆盖率/有效性差距的基准证据）→ 02（测试作提示时指令遵循分化）
- **自查 AI 生成测试的质量**：04（覆盖率/检出率 + 失效归因）→ 05（错误类型与测试坏味道分布）——注意 04 的实际归因与直觉相反（断言不当是最小类，主因是缺缺陷触发输入）
- **人机分工与流程治理**：06（人机分工初步证据）→ 08（人写测试的流水线实践）→ 07（治理机制设计）——07 无实证，取其机制设计不取其效果主张

## 与其他主题目录的关系

- 与 [`../SEforLLM/`](../SEforLLM)：17（Spec-Driven Development：spec 由 advisory 变 enforced）、22（AgileGen：Gherkin 验收标准 + 人在迭代两端决策）与本目录 06/07/08 同属"测试/规约作为契约"谱系——本目录补失效机制侧（01/02）与生成质量侧（03/04/05）。
- 与 `research/requirement-to-spec`（BDD 生命周期，备忘 §11）：01 的"错误代码+自洽错误测试"闭环是「测试全绿但需求偏离」的机制解释；07 的权限隔离/有界修复是 BDD 闸门设计的直接参照（须注意其无实证支撑）。
