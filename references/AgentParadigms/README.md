# AgentParadigms 参考资料目录

本目录收集 Agent 设计范式论文：综述框架、经典范式原始论文（ReAct / Reflexion / ToT / plan 类 / 认知架构）、多智能体协作范式、失败模式与 benchmark 边界研究。2026-08-17 批次入库（26 篇，来源：research 理论框架调研材料引用）并同日完成全文精读（摘要精读级 v3.0）；2026-08-21 增补批次（4 篇：黑板×2 + 主动推理×2，来源：harness×冯诺依曼类别关系材料引用），下载校验均见 [`../arxiv_2026-08_manifest.md`](../arxiv_2026-08_manifest.md)。

## 文件清单

| 文件 | 说明 |
|------|------|
| `01-Wang-Survey_LLM_Autonomous_Agents_v7.pdf` | LLM 自主智能体综述——Profiling/Memory/Planning/Action 四模块框架（FCS 2024） |
| `02-Liu-Survey_Agents_for_SE_v2.pdf` | SE 智能体综述——SE 任务 × agent 组件矩阵（TOSEM） |
| `03-Hassan-Agentic_SE_Pillars_Roadmap_v3.pdf` | Agentic SE 四支柱（Actors/Processes/Tools/Artifacts）+ 自治分级 L0–L5 |
| `04-He-Multi_Agents_for_SE_Review_v4.pdf` | SE 场景 LLM 多智能体系统综述（TOSEM 2025） |
| `05-Yao-ReAct_v3.pdf` | ReAct：推理-行动循环（ICLR 2023 Oral） |
| `06-Shinn-Reflexion_v4.pdf` | Reflexion：语言化反思外循环（NeurIPS 2023） |
| `07-Yao-Tree_of_Thoughts_v2.pdf` | Tree of Thoughts：推理时树状搜索（NeurIPS 2023） |
| `08-Wang-Plan_and_Solve_v3.pdf` | Plan-and-Solve：静态计划 + 顺序执行（ACL 2023） |
| `09-Kim-LLMCompiler_v3.pdf` | LLMCompiler：任务 DAG 并行派发（ICML 2024） |
| `10-Park-Generative_Agents_v2.pdf` | Generative Agents：记忆流 + 反思 + 规划（UIST 2023） |
| `11-Li-CAMEL_v2.pdf` | CAMEL：角色扮演对话协作（NeurIPS 2023） |
| `12-Hong-MetaGPT_v7.pdf` | MetaGPT：SOP 装配线 + 中间产物契约（ICLR 2024） |
| `13-Wu-AutoGen_v2.pdf` | AutoGen：可编程会话协议（v0.2 路线原点） |
| `14-Gao-AgentScope_v2.pdf` | AgentScope：消息中心式多 agent 平台（v1 论文） |
| `15-Cemri-MAST_MAS_Failures_v3.pdf` | MAST：多智能体失败分类法（FC1 规范缺失 41.77%） |
| `16-Li-More_Agents_Is_All_You_Need_v2.pdf` | 采样投票规模化（best-of-N baseline，TMLR 2025） |
| `17-Gao-Single_or_Multi_Agent_Both_v1.pdf` | SAS↔MAS 级联混合（优势随模型变强收窄，ASE 2025） |
| `18-Gao-Agent_Frameworks_Code_SE_Eval_v1.pdf` | 7 个 agent 框架代码中心任务实测 |
| `19-Sinha-Illusion_Diminishing_Returns_v3.pdf` | 长程执行测量与 self-conditioning 效应（ICLR 2026） |
| `20-Kwa-METR_Long_Task_Horizon_v4.pdf` | METR：50% 任务时间地平线（每 7 个月翻番） |
| `21-Liang-SWE_Bench_Illusion_v4.pdf` | SWE-Bench Illusion：基准记忆污染 |
| `22-Yang-SWE_Bench_Multimodal_v1.pdf` | SWE-bench Multimodal：视觉域迁移崩塌 |
| `23-Yao-TAU_Bench_v1.pdf` | τ-bench：工具-代理-用户交互 + pass^k（ICLR 2025） |
| `24-Barres-TAU2_Bench_Dual_Control_v1.pdf` | τ²-bench：双控环境协调能力测量 |
| `25-Mialon-GAIA_v1.pdf` | GAIA：通用助手基准（人类 92% vs GPT-4 15%） |
| `26-Xie-OSWorld_v2.pdf` | OSWorld：真实计算机 GUI 环境基准（NeurIPS 2024 D&B） |
| `27-Han-Blackboard_Advanced_MAS_v1.pdf` | 黑板架构 LLM 多智能体——黑板取代 memory + 控制单元调度（六基准平均 81.68） |
| `28-Salemi-Blackboard_Information_Discovery_v2.pdf` | 黑板广播 + 自愿应答的数据发现系统（vs 主从式受控对照，规模越大增益越大） |
| `29-Wen-Missing_Reward_ActiveInference_v1.pdf` | 以主动推理内在自由能取代外部 reward 的概念论文（有公式伪代码、无实验） |
| `30-Raffa-FEP_ActiveInference_NeuralLM_CEUR3923.pdf` | FEP 与神经语言模型接口的概念短文（被动生成 vs 主动行动边界，CEUR Vol-3923） |

摘要索引见 [`summaries/INDEX.md`](summaries/INDEX.md)（含阅读路线与研究方向关联）。

## 快速定位

- **想理解 agent 架构全貌**：01 → 02 → 03（三层文献骨架）
- **想选控制流范式**：05（循环）→ 08（静态计划）→ 09（DAG）→ 07（树搜索）
- **想判断要不要多智能体**：15（失败分类）→ 16 → 17 → 18
- **想做可靠性设计**：19（self-conditioning）→ 20（时间地平线）→ 23（pass^k）
