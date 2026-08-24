---
title: "What Is Next for LLMs? Next-Generation AI Computing Hardware Using Photonic Chips"
source_pdf: "13-NextGen-LLM-Computing-Photonic-Chips.pdf"
arxiv_id: "2505.05794"
arxiv_version: "v1"
authors:
  - "Renjie Li"
  - "Wenjie Wei"
  - "Qi Xin"
  - "Xiaoli Liu"
  - "Sixuan Mao"
  - "Erik Ma"
  - "Zijian Chen"
  - "Malu Zhang"
  - "Haizhou Li"
  - "Zhaoyu Zhang"
year: 2025
venue: "arXiv（Preprint, Under review；CUHK-Shenzhen / UESTC / NUS / UIUC / UC Berkeley）"
type: "内容索引 + 精读"
generated_at: "2026-08-24"
summary_version: "1.0"
---

# 论文摘要：下一代 LLM 计算硬件——光子芯片（含 2D 材料、自旋电子与 SNN 路线综述）

## 1. 适用场景

- **核实"冯·诺依曼瓶颈"论述的准确出处与层级时必读**：本文对冯·诺依曼瓶颈的讨论全部位于**硬件层**（处理单元与存储单元物理分离导致数据搬运的能耗/延迟），见 §1、§4.1、§7.1、§7.2、§7.7；它**不是**"LLM/harness 层面冯·诺依曼瓶颈倒置"论的出处，引用时应改述为"以光子/神经形态硬件缓解存算分离瓶颈的路线图综述"（见 §2.2）。
- 调研 **LLM 专用光子计算硬件路线图**（MZI 网格、微环谐振器权重库、WDM 并行、光子张量核）时通读全文（§2、§7.5）。
- 评估 **光子/自旋电子/SNN 衬底跑 Transformer 的可行性与四大瓶颈**（长上下文内存、TB 级数据集存储、ADC/DAC 精度开销、原生非线性缺失）时（§7.1–§7.4）。
- 需要 **主流 LLM 机制（CoT/Reflexion/RLHF/长上下文/MoE/MLA）的硬件视角梳理** 作为映射目标参照时（§5）。

> 锚点：Abstract；§1 Introduction；§2 光子组件；§3 2D 材料；§4 自旋电子；§5 Transformer/LLM 原理；§6 SNN；§7 Current Challenges and Future Directions；§8 Conclusion。

## 2. 主要观点与方案

### 2.1 动机：LLM 能耗墙与 CMOS 极限（Abstract、§1）

- GPT-3 训练耗电约 **1300 MWh**，业界预测下一代模型或需**吉瓦级（城市级）**电力预算；Meta 在超过 **10⁵ 块 NVIDIA H100** 的集群上训练 Llama 4；晶体管逼近 **~3 nm** 物理极限、摩尔定律停滞；"冯·诺依曼架构受 memory-processor 瓶颈制约速度与能效 [1]"——四者合成 LLM 算力需求与传统 CMOS 硬件能力间日益扩大的鸿沟。
- 总判断（Abstract）：光子计算系统在吞吐与能效上**有可能**（potentially）超越电子处理器**数量级**，但需在内存（长上下文窗口/长 token 序列）与超大数据集存储上取得突破。

### 2.2 冯·诺依曼瓶颈：论述位置与层级（§1、§4.1、§4.2、§7.1、§7.2、§7.7）

本文对冯·诺依曼瓶颈的讨论分散在五处，**全部是硬件 memory-compute 分离层面**：

- **§1（引言）**：仅一句动机性表述——"von Neumann architectures suffer from memory-processor bottlenecks that constrain speed and energy efficiency"，作为探索光子计算的动因之一。
- **§4.1（神经形态计算背景，最完整定义）**："传统计算系统遭受'冯·诺依曼瓶颈'——**处理与存储单元的物理分离**导致数据搬运中过度的能耗与延迟；该瓶颈被处理器与内存间不断扩大的性能差距（'memory wall'）加剧。现代计算机需兆瓦级功率模拟基础脑功能，而生物脑仅用 **20 W**。"神经形态计算以三创新回应：**存算共置、模拟编码、大规模并行连接**。
- **§7.1（关键反向论点）**：光子加速器普遍**缺乏大片上内存**缓冲长 token 序列；没有片上 SRAM/NVM，光子系统必须把激活/KV/中间状态流进流出——"**重新引入冯·诺依曼瓶颈**"（reintroducing the von Neumann bottleneck），迫使实现从外部 DRAM/磁盘取上下文、打断全光流水线；RAG 类近实时检索多 TB 语料进一步加剧。引用 Ning 等："数据搬运常常构成整个系统的瓶颈——不仅在传统电子处理器，也在光学处理器。"
- **§7.2**：LLM 训练/知识库涉及多 TB 数据集，分析师警告面向 LLM 的"memory wall"正在增长；片上 flash 存权重可把芯片 I/O 削减 **1000×**，但数据staging/缓存/总线带宽仍是关键瓶颈。
- **§7.7**：出路是协同设计——光子张量核与共置存储体/控制逻辑紧耦合（compute-in-memory）可"缓解冯·诺依曼开销"；长期成功来自把 Transformer 算法（稀疏、低精度、模型划分）匹配到"**非冯·诺依曼光子芯片**"的能力。
- **结论（供引用修正）**：本文没有提出任何"harness/LLM 架构层把冯·诺依曼瓶颈倒置"的论点；其 vN 论述 = 硬件存算物理分离 + 神经形态/光子存算共置路线的动机，以及光子芯片自身可能重蹈该瓶颈的警告。

### 2.3 光子计算组件版图（§2）

- **微环谐振器 MRR（§2.1）**：谐振实现 WDM 多波长无串扰传输与光频梳（Kerr 非线性）生成；热光效应/相变材料实现类 ReLU 非线性。
- **马赫-曾德尔干涉仪 MZI（§2.2）**：每个 MZI = 2×2 复域酉变换，级联 mesh 可分解任意 N 维酉矩阵 → 可编程权重矩阵，实现光矩阵-向量乘法（MVM）——Transformer 线性层的核心映射对象。
- **超表面（§2.3）**：亚波长结构调相位/幅度/偏振，衍射域高并行计算（D²NN/DONN）；**4f 系统（§2.3 末）**：透镜傅里叶变换 + 频谱面调制实现线性滤波。
- **激光器（§2.4）**：VCSEL 阵列锁相做前向传播；DFB-SA/FP-SA 实现脉冲（Q-switching）输出——**光子脉冲神经元**基本单元。

### 2.4 2D 材料集成（§3）

- 石墨烯（单原子层吸收 ~2.3% 入射光、超高载流子迁移率）与 TMDC（可调带隙、强激子效应）互补；集成技术：转移印刷、混合集成、vdW 异质结；晶圆级 CMOS 兼容石墨烯工艺已验证。
- 应用：石墨烯调制器 **>100 GHz**（混合集成达 THz 级调制速度）、宽谱光电探测器、超薄波导、片上非线性光学。
- 案例（§3.4）：**MIT 全集成光子处理器** [35]——NOFU 非线性单元，关键计算延迟 **<0.5 ns**、精度 **>92%**（比肩现有技术），商用工艺制造；**Columbia Kerr 频率梳**光互连 [36] 提升带宽密度降能耗；**Black Semiconductor FabONE** 石墨烯芯片间互连。
- 挑战（§3.5）：超薄材料大规模制造脆弱、环境稳定性（需封装）、与 CMOS 工艺集成的界面工程。

### 2.5 自旋电子神经形态器件（§4）

- 核心优势（§4.2）：本征非易失（闲置零静态功耗）、>1 GHz 超快动力学、~10¹⁵ 次耐久；磁化翻转随机性天然映射概率发放；多态磁化（畴壁、斯格明子）提供模拟忆阻行为——"从物理层协同设计解决 memory-processor 二分"。
- 器件与应用（§4.2–§4.3）：MTJ 超顺磁模式（CoFeB/MgO 达 **604% TMR**）；4 个同步 STNO 实时元音识别 **96%** 准确率、超等效深度学习网 **17%**、单次分类 **3 mW**；斯格明子贝叶斯推断（天气预测 **92%**，10⁵ 随机态内存采样，比 GPU 省 **10×** 蒙特卡洛能耗）；AFM 器件 **100 ps** 开关、**4 fJ**/突触更新、10¹² 周期 <0.1% 权重漂移；储备池计算：单 vortex-STNO 等效 **400 神经元**（Mackey-Glass NMSE 0.012）、斯格明子储备 20 µW 处理 10 MHz EEG 做癫痫检测；愿景：全自旋网络 **>100 TOPS @ <10 mW**。

### 2.6 Transformer/LLM 机制梳理（§5）

- 架构与机制回顾（§5.1–§5.6）：自注意力/多头/位置编码；CoT（§5.2，PaLM 540B 少样本 CoT 在 GSM8K 达 SOTA、超微调 175B GPT-3）；自反思 Reflexion（§5.3，GPT-4 agent 在 HumanEval 达 **91%**）；RLHF 三段流水线与 DPO（§5.4，DeepSeek 用 DPO）；Toolformer 自监督工具调用（§5.5）；长上下文（§5.6：ALiBi 1K→2K 外推、RoPE 2K→8K/16K、NTK-aware 插值把 CodeLlama 16K→100K、FlashAttention 线性内存；有效上下文从 ~1K 推到 **100K**）。
- 三家模型解剖（§5.7–§5.9）：ChatGPT（decoder-only + RLHF，胜在训练/对齐而非新架构）；LLaMA（7B–65B，RoPE+SwiGLU+pre-norm，**13B 在多项基准超 GPT-3 175B**，SentencePiece ~32k 词表）；DeepSeek（~2T 双语 token，MoE 稀疏激活 + MLA 潜空间压缩 KV + FP8 + DualPipe 双流水线，R1 在 V3 上加 RL）。
- 硬件映射视角：attention 的 Q/K/V 是**数据依赖的动态矩阵**，需可重构光子/自旋电路（§1）；GeLU 等模拟非线性与归一化在光/自旋介质中实现仍是主要挑战（§1、§7.4）。

### 2.7 SNN 路线（§6）

- 编码（§6.2）：rate vs temporal 编码 + 视觉/听觉/嗅觉/触觉专用编码；高效模型（§6.3）：Spikformer 等把自注意力与脉冲神经元合并、ANN-to-SNN 转换；学习（§6.4）：生物可塑性（STDP 多尺度）vs 深度学习优化（ANN 转换 vs 替代梯度直接训练）；应用（§6.5）：脉冲驱动量化 SNN 在 COCO/ADE20K 上参数量降 **83.94%**、能耗降 **79.36%** 且保持精度；专用硬件谱系（SIES、Skydiver、DeepFire、FireFly）。
- 光子 SNN 指标（§6.1，Table 2）：光子 STDP 延迟 0.1 ps/0.3 aJ/spike vs 电子 CMOS 500 ps/100 aJ；面积效率 800 vs 50 TOPS/mm²；微环 LIF 时间常数 15 ps，20 GHz 脉冲频率超生物六个数量级；WDM 支持 C+L 波段 ≥80 并行通道。

### 2.8 七大挑战与方向（§7）

长上下文内存（§7.1，缺片上内存→重引入 vN 瓶颈）；TB 级存储与 I/O（§7.2，memory wall；片上 flash 权重省 1000× I/O）；精度与转换开销（§7.3，一个光子 Transformer 加速器中 **ADC/DAC 占芯片面积 >50%** 成性能瓶颈）；原生非线性缺失（§7.4，softmax/GELU 仍需回 CMOS）；光子注意力架构（§7.5，MZI 张量核、Ce:YIG 磁光非易失多比特权重、Lightening-Transformer 与 HyAtten 验证动态张量核路线）；神经形态/脉冲光子 LLM（§7.6，事件驱动+稀疏性匹配光子优势）；系统集成与协同设计（§7.7，光-电协同封装、片上光网络、量化/并行/布局软件栈适配）。

> 锚点：§1 Introduction；§2.1–§2.4；§3.1–§3.5；§4.1–§4.3；§5.1–§5.9；§6.1–§6.5；§7.1–§7.7；§8 Conclusion；Table 1（2D 材料非线性光学参数）；Table 2（仿生平台性能基准）。

## 3. 达到的效果

| 度量 | 结果（数值） | 锚点 |
|---|---|---|
| GPT-3 训练耗电 | ~1300 MWh（1.3×10³ MWh）；未来模型或需吉瓦级 | Abstract；§1 |
| Llama 4 训练集群 | >10⁵ 块 NVIDIA H100 | §1 |
| 晶体管特征尺寸极限 | ~3 nm | §1 |
| 生物脑 vs 计算机功率 | 20 W vs 兆瓦级（模拟基础脑功能） | §4.1 |
| MIT 全集成光子处理器 | 关键计算延迟 <0.5 ns；精度 >92%；商用工艺 | §3.4 [35] |
| 石墨烯调制器工作频率 | >100 GHz（混合集成方案达 THz 级速度） | §3.2、§3.3 [33] |
| STNO 元音识别 | 96% 准确率，超等效 DL 网络 17%，3 mW/次分类 | §4.3 [46] |
| 斯格明子贝叶斯推断 | 天气预测 92%；10⁵ 随机态；能耗较 GPU 降 10× | §4.3 [44] |
| AFM 突触 | 100 ps 开关；4 fJ/更新；10¹² 周期 0.1% 漂移 | §4.2–§4.3 |
| 全自旋网络愿景 | >100 TOPS @ <10 mW 系统功率 | §4.3 |
| 光子 vs 电子 SNN 平台 | 光子 STDP：0.1 ps / 0.3 aJ/spike / 800 TOPS/mm²，对比 CMOS 500 ps / 100 aJ / 50 TOPS/mm² | §6.1 Table 2 |
| 光子脉冲频率 | 20 GHz（超生物对应物六个数量级）；WDM ≥80 并行通道 | §6.1 |
| 脉冲驱动量化 SNN（COCO/ADE20K） | 参数量 −83.94%，能耗 −79.36%，精度可比 | §6.5 [97] |
| ADC/DAC 面积占比（某光子 Transformer 加速器） | >50%（性能瓶颈） | §7.3 |
| 片上 flash 存权重 | 芯片 I/O 减少 1000× | §7.2 |
| LLM 有效上下文长度演进 | ~1K → 100K tokens（ALiBi/RoPE/NTK 插值/FlashAttention 组合） | §5.6 |
| Reflexion（GPT-4 agent） | HumanEval 91% | §5.3 [42] |
| LLaMA-13B vs GPT-3 175B | 多项基准 13B 胜出 | §5.8 [55] |
| DeepSeek 训练数据 | ~2 万亿 token（英+中），FP8 + MoE + MLA | §5.9 [48][58] |
| 总体判断 | 光子计算吞吐/能效**可能**超电子处理器数量级；内存与存储是前置突破条件 | Abstract |

> 说明：本表为综述汇编值，均出自本文正文/表格；方括号为本文所引原始文献编号。本文无自有统一实验。

> 锚点：见各行的 § 锚点列。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2505.05794 |
| MIT 全集成光子 DNN 芯片 | Bandyopadhyay et al., Nature Photonics 18:1335–1343 (2024)，本文 [35] |
| Columbia Kerr 频率梳光互连 | Rizzo et al., Nature Photonics 17:781–790 (2023)，本文 [36] |
| Black Semiconductor FabONE | 石墨烯芯片间互连设施（graphene-info 报道，本文 [37]） |
| 光子注意力路线 | Lightening-Transformer（动态操作光子张量核）、HyAtten（§7.5，未附链接） |
| LLM 机制原始文献 | Vaswani Transformer [39]；CoT Wei et al. [41]；Reflexion/Shinn [42]；RLHF [46]；DPO [47]；Toolformer [49]；ALiBi [50]；RoPE [51]；FlashAttention [52]；Qwen [53]；GPT-4 [54]；LLaMA [55][57]；DeepSeek [48][58][59] |
| 光子计算奠基工作 | Shen et al. 深度学习 MZI 光子电路 [5]；Feldmann 光子张量核/PCM [3][25]；Xu 光子卷积加速 [2] |
| 关联主题 | 与库内 AIOS/01–03（LLM OS 抽象）正交：本文提供其"硬件层存算瓶颈"侧的背景证据 |

> 锚点：§3.4 Case Study；§7.5 Photonic Attention Architectures；References [1]–[103]。

## 5. 一句话索引（给 Agent 用）

> arXiv 2505.05794（Li et al., 2025）：面向 LLM 能耗墙（GPT-3 训练 ~1300 MWh、下一代或达吉瓦级、Llama 4 用 >10⁵ 块 H100）的光子芯片硬件综述，覆盖 MZI/MRR/WDM 光矩阵计算、2D 材料、自旋电子与 SNN 路线；其冯·诺依曼瓶颈论述仅在硬件层（§4.1 存算物理分离 + memory wall；§7.1 光子缺片上内存反而会"重新引入"该瓶颈），不能作为 harness 层"瓶颈倒置"的出处；结论：光子计算吞吐/能效有望超电子数量级，但长上下文内存、TB 级存储、ADC/DAC 占片 >50% 与原生非线性缺失是主要拦路虎。
