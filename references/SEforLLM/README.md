# SEforLLM 参考资料目录

本目录收集"软件工程 × LLM 系统"论文：LLM 作为软件构件、prompt 作为规约（promptware）、evals/蜕变测试、神经符号混合架构、AI 编码生产力与质量实证。2026-08-17 批次入库（10 篇，来源：research 理论框架调研材料引用）并同日完成全文精读（摘要精读级 v3.0），下载校验见 [`../arxiv_2026-08_manifest.md`](../arxiv_2026-08_manifest.md)。

## 文件清单

| 文件 | 说明 |
|------|------|
| `01-Weber-LLMs_as_Software_Components_v1.pdf` | LLM 作为软件构件：集成应用架构分类学（MSR 2025） |
| `02-Chen-SE_for_Prompt_Enabled_Systems_v2.pdf` | Promptware Engineering：prompt 作为软件制品的研究议程 |
| `03-Jin-LLM_Agents_for_SE_Survey_v2.pdf` | LLM/Agent × SE 系统映射综述 |
| `04-Zheng-MT_LLM_Survey_v1.pdf` | 蜕变测试 × LLM 双向赋能系统综述 |
| `05-Cho-MT_of_LLMs_NLP_v1.pdf` | LLM 蜕变测试：191 条蜕变关系（ICSME 2025） |
| `06-Cho-LLMORPH_v1.pdf` | LLMORPH：MR 自动生成的蜕变测试工具 |
| `07-Ali-Neuro_Symbolic_Control_LLM_v1.pdf` | 神经符号控制：确定性外壳 + 非确定内核 |
| `08-Mao-Protocol_Driven_Multi_Agent_v1.pdf` | 协议驱动多智能体工程（借用 Design by Contract） |
| `09-Becker-METR_RCT_AI_Dev_Productivity_v2.pdf` | METR RCT：资深开发者用 AI 反慢 19% |
| `10-Mujahid-GenAI_Self_Admitted_Tech_Debt_v1.pdf` | GenAI 诱导的自认技术债（"TODO: Fix the Mess Gemini Created"） |

摘要索引见 [`summaries/INDEX.md`](summaries/INDEX.md)。

## 快速定位

- **"LLM 即构件"主线**：01 → 02 → 08（分类学 → prompt 制品化 → DbC 协议层）
- **验证方法论**：04 → 05 → 06 → 07（MT 综述 → 关系库 → 自动化 → 符号外壳）
- **生产力实证**：09 → 10（RCT → 技术债）

## 与经典文献的关系

经典侧（Parnas 信息隐藏、Brooks 没有银弹、Meyer DbC、Szyperski CBSE、形式化规约史）为书籍与早期论文，未入库 PDF；对照梳理见 `research/agent-software-design/materials/软件工程原理与LLM系统.md`。
