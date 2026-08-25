# FormalMethodsLLM 参考资料目录

本目录收集"**形式方法 × LLM**"论文：形式规格合成、闭环可验证代码生成、refinement/correctness-by-construction 与 LLM 的结合、验证反馈驱动的多轮修复。2026-08-25 建目录并首批入库 5 篇 PDF——来源：人机可读性分离点与验证边界两轮讨论（备忘见 [`../../research/人机可读性分离点与验证边界_两轮讨论备忘_2026-08-25.md`](../../research/人机可读性分离点与验证边界_两轮讨论备忘_2026-08-25.md)），主题对应"分离点上游推"研究方向（验证边界决定重构经济学）。**摘要待 PDF 全部到齐后依 [`../design/kb-app/06-摘要构建与命名规范.md`](../design/kb-app/06-摘要构建与命名规范.md) 基于全文生成**，届时建 `summaries/INDEX.md`。下载校验见 [`../arxiv_2026-08_manifest.md`](../arxiv_2026-08_manifest.md)。

## 文件清单

| 文件 | 说明 |
|------|------|
| `01-Sun-Clover_Closed_Loop_Verifiable_v4.pdf` | Clover（CAV 2024, Stanford）：docstring/代码/形式注解三态一致性闭环验证（Dafny）——"经过验证的文档层"范式 |
| `02-Wang-Event_B_Agent_v1.pdf` | Event-B Agent（FSE 2026）：LLM agent 规划 refinement 策略（需求分配到各层级）——"分离点位置决策自动化"的论文级实现 |
| `03-Ye-Intent_Aligned_Formal_Spec_v1.pdf` | 意图对齐的形式规格合成（via Traceable Refinement, Berkeley 系）——"规格是否对齐意图"是分离点上游推的核心难题 |
| `04-Faria-Dafny_Annotations_Test_Oracles_v1.pdf` | LLM+测试 oracle 自动生成 Dafny 验证注解（波尔图大学） |
| `05-Oliveira-Behavioral_Changes_Refactoring_FM_v1.pdf` | 基础模型 oracle 检测 Python 重构行为变化（2026-08）——"稳定再生的等价性验证"空位锚点 |

摘要索引见 [`summaries/INDEX.md`](summaries/INDEX.md)（5 篇均基于 PDF 全文的精读级摘要，2026-08-25 生成）。下载校验见 [`../arxiv_2026-08_manifest.md`](../arxiv_2026-08_manifest.md)。

## 快速定位

- **闭环验证范式**：01（Clover 三态一致性）→ 04（注解自动生成）
- **refinement 阶梯（分离点上游推）**：02（Event-B Agent）→ 03（意图对齐）
- **等价性验证（稳定再生成）**：05
- 与 `../SEforLLM/17`（spec-as-source 学术化）成对：17 给范式愿景，本目录给验证机制。

## 线索级（未入库）

Refine4LLM（TOSEM 2025, DOI 10.1145/3704905）、Ferrari et al. Formal RE×LLM 路线图（ScienceDirect）、NL→Dafny 实证（preprints.org）、DafnyBench——见备忘 §5.2，待 OA 确认后补录。
