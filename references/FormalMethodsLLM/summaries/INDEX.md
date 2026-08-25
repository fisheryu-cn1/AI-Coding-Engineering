# FormalMethodsLLM 主题论文摘要索引

> 主题：形式方法 × LLM——形式规格合成、闭环可验证代码生成、refinement×LLM（correctness-by-construction）、意图对齐、验证注解生成、行为等价性检测
> 文件数：5
> 生成日期：2026-08-25（首批，基于 PDF 全文的精读级摘要 summary_version 1.0——来源：人机可读性分离点与验证边界两轮讨论，备忘见 `../../../research/人机可读性分离点与验证边界_两轮讨论备忘_2026-08-25.md`）

## 论文列表

| # | 摘要文件 | 原论文标题 | 一句话定位 |
|---|---|---|---|
| 01 | [01-Clover闭环可验证代码生成.md](01-Clover闭环可验证代码生成.md) | Clover: Closed-Loop Verifiable Code Generation | docstring/代码/形式注解三组件六边一致性检查（Dafny），对抗错误例 0 假阳性（CAV 2024，Stanford） |
| 02 | [02-EventB代理形式模型合成.md](02-EventB代理形式模型合成.md) | Event-B Agent: Towards LLM Agent for Formal Model Synthesis and Repair | LLM agent 规划 refinement 层级分配——分离点位置决策自动化（FSE 2026） |
| 03 | [03-意图对齐形式规格合成.md](03-意图对齐形式规格合成.md) | Intent-aligned Formal Specification Synthesis via Traceable Refinement | 测试→需求 traceability map 钉住每步局部修复；Opus 4.5 规格生成 +46.8% |
| 04 | [04-LLM测试oracle生成Dafny注解.md](04-LLM测试oracle生成Dafny注解.md) | Automatic Generation of Formal Specification and Verification Annotations Using LLMs and Test Oracles | LLM 猜注解 + verifier/test oracle 双 oracle 级联判真：repair@8=98.2%、规约逻辑等价 96.4% |
| 05 | [05-基础模型检测重构行为变化.md](05-基础模型检测重构行为变化.md) | Detecting Behavioral Changes in Python Refactoring Implementations with Foundation Models | FM 零样本 diff oracle：F1 0.77、发现 13 个真实重构引擎 bug（开发者接受 12/13） |

## 推荐先读

- **"分离点上游推"方向论证**：02（Event-B Agent，refinement 层级=分离点）→ 03（意图对齐=上游推的真墙与机制）→ 01（Clover，"经过验证的文档层"=伪代码锚点弱形式）
- **闭环验证的 oracle 谱系**：01（三态一致性）→ 04（verifier+test 双 oracle 级联）
- **稳定再生的等价性验证（空位③）**：05 + 经典 regression verification（未入库线索，见备忘 §5.2）

## 与 GraphIt-KB 的相关性

- 该目录是"**重构经济学可行域 = 自动验证覆盖域**"命题（讨论备忘 §4）的证据层：01/04 是验证边界的机制候选（文档层一致性/注解双 oracle），02 是边界位置决策的自动化实现，03 是边界上移的成本与解法（意图对齐），05 是再生成收敛的验证件——与 `../../SEforLLM/summaries/17-规约驱动开发从代码到契约.md`（spec-as-source 愿景）构成"范式愿景 × 验证机制"配对。
- 01（Clover docstring×注解×代码互检）为 KB 的"中间产物作为正确性基础设施"子问题提供可验证文档层范式参照；04 的 oracle 级联（test assertions→postconditions→invariants 编入 repair prompt）是"验证语义谱系中间档"的现成样本（空位②素材）。
- `../../ContextEngineering/summaries/45-评测AGENTSMD上下文文件.md` 的实测（LLM 生成 context file 成功率不升、成本 +20% 显著）提示：把规格/文档喂给 agent 的收益取决于文档质量层——该约束必须计入 spec-as-source 范式的收益模型。
