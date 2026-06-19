# Petri 网与组合分析（Compositional Analysis）学习资源清单

> 整理日期：2026-04-30
> 说明：本清单收录学习Petri网基础理论、组合分析/组合验证、Petri网代数、进程代数及相关工具所需的核心教材、讲义、论文与在线资源。按主题分层，由浅入深排列。

---

## 目录

1. [Petri 网基础入门](#一-petri-网基础入门)
2. [组合分析 / 组合验证（Compositional Verification）](#二-组合分析--组合验证compositional-verification)
3. [Petri 网代数（PNB / PBC / PNA）](#三-petri-网代数pnb--pbc--pna)
4. [进程代数（Process Algebra: CSP / CCS / ACP）](#四-进程代数process-algebra-csp--ccs--acp)
5. [工作流网（Workflow Nets）](#五-工作流网workflow-nets)
6. [图重写系统（Graph Rewriting / Groove）](#六-图重写系统graph-rewriting--groove)
7. [组合验证工具与教程](#七-组合验证工具与教程)
8. [经典教材与参考书](#八-经典教材与参考书)

---

## 一、Petri 网基础入门

### 1.1 经典教材与讲义

| 资源名称 | 作者 | 类型 | 获取链接 | 难度 | 说明 |
|---------|------|------|---------|------|------|
| **Petri Nets: A Comprehensive Introduction** | Cardoso, Zilio et al. | 教材/讲义 | [HAL PDF](https://hal.science/hal-05225249v1/file/17173-Cardoso_16468.pdf) | ⭐⭐ | 2024年新版英文教材，涵盖基础模型、分析技术、解释网、高级网、时间网，附大量练习。最适合初学者入门。 |
| **Petri Nets Lecture Notes (TUM)** | Javier Esparza等 | 课程讲义 | [TUM 2021SS PDF](https://teaching.model.in.tum.de/2021ss/petri/material/PNSkript.pdf) | ⭐⭐⭐ | 慕尼黑工业大学讲义，系统覆盖可达性、状态方程、不变量、S/T系统、自由选择网，含AutomataTutor练习题。 |
| **Petri Nets (for Planners)** | B. Bonet, P. Haslum | 会议教程 | [ICAPS 2011 PDF](https://bonetblai.github.io/tutorials/icaps11-petri.pdf) | ⭐⭐ | ICAPS 2011规划会议教程，从规划视角切入Petri网，涵盖复杂度、分析技术与特殊网类。 |
| **From Petri Nets to Colored Petri Nets: A Tutorial** | V. Gehlot, C. Nigro | 综述教程 | [Simulation SU PDF](http://simulation.su/uploads/files/default/2019-gehlot-1.pdf) | ⭐⭐ | 从基本Petri网到着色Petri网的渐进式教程，附建模与仿真案例。 |
| **Petri Nets: Properties, Analysis and Applications** | T. Murata | 经典论文 | Proceedings of the IEEE, 1989 | ⭐⭐ | Petri网领域最经典的综述论文，所有研究者的必读入门文献。 |

### 1.2 进阶专著

| 资源名称 | 作者 | 说明 |
|---------|------|------|
| **Petri Net Theory and the Modeling of Systems** | J. L. Peterson (1981) | Petri网理论奠基性教材，系统介绍可达性树、矩阵方程、复杂度与可判定性。 |
| **Petri Nets for Systems Engineering** | C. Girault, R. Valk (2003) | 系统工程视角，涵盖验证、实现方法、柔性制造系统、工作流系统等应用。 |
| **Discrete, Continuous and Hybrid Petri Nets** | R. David, H. Alla (2004/2010) | 离散、连续与混合Petri网的统一框架，适合控制与制造系统背景的学习者。 |
| **Coloured Petri Nets: Modelling and Validation of Concurrent Systems** | K. Jensen, L. M. Kristensen (2009) | 着色Petri网权威教材，附CPN Tools实践指导。 |
| **Time and Petri Nets** | L. Popova-Zeugmann (2013) | 时间Petri网的专门教材，涵盖时间窗与时序逻辑。 |

### 1.3 在线课程与视频

- **MIT OpenCourseWare**: Search "Discrete Event Systems" — 包含Petri网在离散事件系统中的基础应用。
- **YouTube**: Search "Petri nets tutorial" — 大量入门级可视化讲解（推荐 channel: *Univ. of Twente* 和 *Process Mining* 系列）。
- **Process Mining Course** (Coursera / TU/e): Wil van der Aalst 主讲，虽聚焦流程挖掘，但包含大量Petri网建模与分析基础。

---

## 二、组合分析 / 组合验证（Compositional Analysis / Compositional Verification）

### 2.1 核心理论论文与讲义

| 资源名称 | 作者 | 类型 | 获取链接 | 难度 | 说明 |
|---------|------|------|---------|------|------|
| **Algebraic Process Verification** | J.F. Groote, M.A. Reniers | 专著章节/讲义 | [CWI PDF](https://ir.cwi.nl/pub/1129/1129D.pdf) | ⭐⭐⭐⭐ | 系统介绍μCRL（带数据的ACP扩展）、线性进程方程（LPE）、不变量、锥与焦点方法、合流性，含SLIP和IEEE 1394协议案例。 |
| **Compositional Verification in Action** | H. Garavel, F. Lang, L. Mounier | 综述 | [Inria PDF](https://cadp.inria.fr/ftp/publications/cadp/Garavel-Lang-Mounier-18.pdf) | ⭐⭐⭐⭐ | Graf & Steffen组合最小化思想的完整综述，附CADP工具工业案例（TCP、Eurocontrol、SCSI-2、NoC等）。 |
| **Compositional model checking of concurrent systems, with Petri nets** | P. Sobociński, O. Stephens | 教程论文 | [arXiv:1603.00976](https://arxiv.org/abs/1603.00976) | ⭐⭐⭐⭐ | PNB组合模型检验的权威教程，将组合性与进程等价结合，解释Penrose工具原理。 |
| **Reachability via Compositionality in Petri nets** | P. Sobociński, O. Stephens | 研究论文 | [arXiv:1303.1399](https://arxiv.org/pdf/1303.1399) | ⭐⭐⭐⭐ | PNB组合可达性分析的开创性论文，含完整算法与正确性证明。 |
| **A Framework for Compositional Verification of Security Protocols** | S. Andova et al. | 研究论文 | [CISPAPDF](https://people.cispa.io/cas.cremers/downloads/papers/AnCrGjMaMjRa2008-compositional_framework.pdf) | ⭐⭐⭐⭐ | 安全协议组合验证的经典框架，定义独立性条件，证明秘密性/认证性的组合保持。 |
| **Compositional Information Flow Security for Concurrent Programs** | Rossi et al. | 研究论文 | [JCS PDF](https://www.dsi.unive.it/~srossi/Papers/JCS-multithreaded.pdf) | ⭐⭐⭐⭐ | 并发程序信息流安全的组合式展开框架，涵盖非干扰与降级的组合推理。 |

### 2.2 组合验证方法学

| 资源名称 | 作者 | 说明 |
|---------|------|------|
| **Compositional Reachability Analysis** | S. Cheung, J. Kramer | 组合可达性分析的经典方法，将分布式程序视为层次化子系统组合。 |
| **Compositional Top-down Verification of Concurrent Systems using Rely-Guarantee** | ACL 2020 | 自顶向下的组合验证教程，使用CSim²框架进行并发系统的分层属性保持证明。 |
| **Compositional Verification of Concurrent Systems by Combining Bisimulations** | LNCS 2019 | 结合强/弱互模拟的组合最小化方法，扩展μ-演算公式检验能力。 |
| **Rely-Guarantee Reasoning** | C. B. Jones, I. Hayes et al. | 假设-保证推理的基础文献，组合并发程序验证的基石方法。 |

---

## 三、Petri 网代数（PNB / PBC / PNA）

### 3.1 Petri Nets with Boundaries (PNB)

| 资源名称 | 作者 | 类型 | 获取链接 | 说明 |
|---------|------|------|---------|------|
| **Compositional model checking of concurrent systems, with Petri nets** | Sobociński & Stephens | 教程 | [arXiv](https://arxiv.org/abs/1603.00976) | PNB的完整教程，介绍边界端口的图形代数、同步/并行组合、状态图最小化。 |
| **Reachability via Compositionality in Petri nets** | Sobociński & Stephens | 论文 | [arXiv](https://arxiv.org/pdf/1303.1399) | PNB组合可达性的算法、正确性证明与实验结果。 |
| **A Compositional Algebra of Petri Nets** | P. Sobociński | 博士论文相关 | [Southampton Thesis](https://eprints.soton.ac.uk/385201/) | 完整阐述PNB的组合语义、与Span(Graph)代数的关系、行为等价。 |

### 3.2 Petri Box Calculus (PBC) & Petri Net Algebra (PNA)

| 资源名称 | 作者 | 类型 | 说明 |
|---------|------|------|------|
| **Petri Net Algebra** | E. Best, R. Devillers, M. Koutny | 专著 (Springer 2001) | PBC/PNA领域的权威专著。系统阐述控制流与同步通信的Petri网代数，以及M-nets（高阶着色网代数）。 |
| **The Box Calculus: A New Causal Algebra with Multi-label Communication** | Best, Devillers, Hall (1992) | 论文 | PBC的原始论文，定义box概念与多标签通信。 |
| **Algebras of Coloured Petri Nets and Their Applications** | L. Pomello et al. | HDR论文/综述 | [HAL PDF](https://hal.science/tel-02309973v1/file/Pom-HDR-2009.pdf) | 综述PBC家族（ABC、ARCD、M-nets等）及其在安全协议建模中的应用。 |

### 3.3 组合性相关的Petri网分解

| 资源名称 | 作者 | 说明 |
|---------|------|------|
| **Automatic Decomposition of Petri Nets into Automata Networks** | Garavel et al. (2020) | 自动分解工具链的完整介绍，比较图着色、最大团、SAT/SMT等方法。 |
| **On Compositionality of Boundedness and Liveness for Nested Petri Nets** | ACM (2014) | 嵌套Petri网的有界性与活性组合分析的理论结果。 |
| **Structural Decomposition and Decentralized Control of Petri Nets** | Ye, Zhou et al. (IEEE TSMC 2018) | 基于整数线性规划的Petri网结构分解，应用于去中心化控制。 |

---

## 四、进程代数（Process Algebra: CSP / CCS / ACP）

### 4.1 CSP (Communicating Sequential Processes)

| 资源名称 | 作者 | 类型 | 获取链接 | 难度 | 说明 |
|---------|------|------|---------|------|------|
| **Communicating Sequential Processes** | C.A.R. Hoare | 经典教材 | 出版书 (1985) | ⭐⭐⭐ | CSP奠基之作。必读的经典，建立进程代数的通信与并发基础。 |
| **Understanding Concurrent Systems** | A.W. Roscoe | 教材 | Springer (2011) | ⭐⭐⭐⭐ | Hoare之后CSP最全面的教材，涵盖操作语义、指称模型、FDR工具使用、工业案例。 |
| **The Theory and Practice of Concurrency** | A.W. Roscoe | 教材 | Prentice-Hall (1998) | ⭐⭐⭐⭐ | Roscoe早期教材，系统性阐述CSP理论，与FDR工具深度集成。 |
| **A Tutorial Introduction to CSP in Unifying Theories of Programming** | A. Cavalcanti, J. Woodcock | 教程 | [York PDF](https://www-users.york.ac.uk/~alcc500/publications/papers/CW06.pdf) | ⭐⭐⭐⭐ | 在UTP统一理论框架下介绍CSP语义，适合已具备基础的学习者。 |
| **Concurrent Programming Lecture: Introduction to CSP** | R. Hall | 课程讲义 | [FU Berlin PDF](http://www.inf.fu-berlin.de/lehre/WS01/19530-V/lectures/Lecture13.pdf) | ⭐⭐ | 简洁的CSP入门讲义，涵盖基本进程、前缀、选择、并行组合等核心概念。 |

### 4.2 CCS & ACP

| 资源名称 | 作者 | 类型 | 获取链接 | 难度 | 说明 |
|---------|------|------|---------|------|------|
| **A Gentle Introduction to Process Algebras** | R. De Nicola | 综述教程 | [LMU PDF](https://www.pst.ifi.lmu.de/Lehre/fruhere-semester/sose-2013/formale-spezifikation-und-verifikation/intro-to-pa.pdf) | ⭐⭐⭐ | 温柔入门CCS、CSP、ACP三大进程代数，对比操作/指称/代数语义，介绍行为等价。 |
| **Process Algebra: An Algebraic Theory of Concurrency** | W. Fokkink | 教程/讲义 | [VU Amsterdam PDF](https://www.cs.vu.nl/~wanf/pubs/cai09-tutorial.pdf) | ⭐⭐⭐ | ACP风格的进程代数教程，从BPA到并行通信、递归、静默步、抽象，附交替位协议案例。 |
| **Communication and Concurrency** | R. Milner | 经典教材 | Prentice-Hall (1989) | ⭐⭐⭐⭐ | Milner的CCS经典教材，与Hoare的CSP并列为进程代数必读。 |

### 4.3 进程代数在安全协议中的应用

| 资源名称 | 作者 | 说明 |
|---------|------|------|
| **Survey of Security Protocol Verification based on Process Algebra** | 多篇综述 | ResearchGate可检索，涵盖CSP/FDR方法在安全协议分析中的应用。 |
| **Formal verification and security analysis of FastDFS using CSP** | 2025, IoT Journal | CSP建模分布式文件系统的近期工业案例，使用PAT模型检验器。 |
| **A Better Composition Operator for Quantitative Information Flow Analyses** | McIver et al. (ESORICS 2017) | QIF分析中的新组合算子`⋈`，解决合谋敌手建模问题。 |

---

## 五、工作流网（Workflow Nets）

### 5.1 核心理论文献

| 资源名称 | 作者 | 类型 | 获取链接 | 难度 | 说明 |
|---------|------|------|---------|------|------|
| **Verification of Workflow Nets** | W.M.P. van der Aalst | 经典论文 | [vdaalst.com PDF](https://www.vdaalst.com/publications/p44.pdf) | ⭐⭐⭐ | 工作流网声音性（Soundness）的定义、验证技术与变换规则的奠基论文。证明声音性等价于扩展网的活性+有界性。 |
| **The Application of Petri Nets to Workflow Management** | W.M.P. van der Aalst | 经典论文 | Journal of Circuits, Systems and Computers, 1998 | ⭐⭐⭐ | 将Petri网应用于工作流管理的开创性论文，定义WF-nets并讨论分析需求。 |
| **Soundness of Workflow Nets: Classification, Decidability, Analysis** | W.M.P. van der Aalst et al. | 综述论文 | [vdaalst.com PDF](https://www.vdaalst.com/publications/p628.pdf) | ⭐⭐⭐⭐ | 系统分类声音性的各种变体（经典、弱、广义、松弛声音性），讨论可判定性与分析复杂度。 |
| **Workflow Model Compositions Preserving Relaxed Soundness** | A. Zimmermann et al. | 研究论文 | [BPM 2006 PDF](https://www.tu-ilmenau.de/fileadmin/Bereiche/IA/sse/Mitarbeiter/Armin_Zimmermann/Publications/Conferences_Workshops/2006.BPM.pdf) | ⭐⭐⭐⭐ | 证明WF-nets在顺序/并行/层次/资源组合下保持松弛声音性的经典结果。 |
| **Resource-Constrained Workflow Nets** | W.M.P. van der Aalst et al. | 研究论文 | [ResearchGate](https://www.researchgate.net/publication/220444782_Resource-Constrained_Workflow_Nets) | ⭐⭐⭐⭐ | 引入资源约束工作流网，讨论资源共享场景下的声音性问题。 |

### 5.2 工作流网工具

| 工具 | 说明 | 链接 |
|------|------|------|
| **Woflan** | 经典的WF-net声音性分析工具 | [TU/e Legacy] |
| **YAWL** | Yet Another Workflow Language，基于WF-nets的工作流引擎 | [yawlfoundation.org](http://www.yawlfoundation.org/) |
| **POWL** | Partially Ordered Workflow Language，近期新兴的工作流表示法 | 相关论文见 arXiv:2602.15739 |

---

## 六、图重写系统（Graph Rewriting / Graph Transformation Systems）

### 6.1 核心资源

| 资源名称 | 作者 | 类型 | 获取链接 | 难度 | 说明 |
|---------|------|------|---------|------|------|
| **GROOVE 官网与教程** | University of Twente | 工具+教程 | [groove.cs.utwente.nl](https://groove.cs.utwente.nl/) | ⭐⭐ | 图重写工具GROOVE的官方网站，提供可下载工具、YouTube视频教程、使用文档。 |
| **GROOVE Tutorial Videos** | UTwente | 视频 | [YouTube / 官网](https://groove.cs.utwente.nl/tutorials.html) | ⭐⭐ | 包含基础功能介绍、图/规则编辑、类型图、可视化、模型检验等视频教程。 |
| **Tutorial Introduction to Graph Transformation** | 多人 | 综述教程 | [ResearchGate](https://www.researchgate.net/publication/284879445_Tutorial_introduction_to_graph_transformation_A_software_engineering_perspective) | ⭐⭐⭐ | 从软件工程视角介绍图转换的基础概念与应用。 |
| **Model Checking Dynamic States in GROOVE** | A. Rensink | 论文 | [Leicester PDF](https://www.cs.le.ac.uk/events/segravis/material/Rensink-spin2006.pdf) | ⭐⭐⭐ | 在GROOVE生成的状态空间上应用CTL模型检验，含循环缓冲区案例。 |
| **CTL Model Checking in Groove** | Rensink et al. | 论文 | [SPIN 2006 PDF](https://spinroot.com/spin/symposia/ws06/015.pdf) | ⭐⭐⭐ | GROOVE中CTL模型检验的算法与实验结果。 |
| **Graph Rewriting for Testing Domain-specific Models** | Wolter et al. | 论文 | [JOT 2025](https://www.jot.fm/issues/issue_2025_02/a4.pdf) | ⭐⭐⭐ | 使用GROOVE对RBAC等特定领域模型进行安全属性测试的近期案例。 |

### 6.2 图重写数学基础

| 资源名称 | 作者 | 说明 |
|---------|------|------|
| **Fundamentals of Algebraic Graph Transformation** | H. Ehrig et al. (Springer 2006) | 代数图转换的权威教材，双推出（DPO）方法的数学基础。 |
| **Graph Structure and Monadic Second-Order Logic** | B. Courcelle, J. Engelfriet (Cambridge 2012) | 图代数与可识别图语言的数学基础，适合理解自动机函子方法。 |

---

## 七、组合验证工具与教程

### 7.1 CADP (Construction and Analysis of Distributed Processes)

| 资源名称 | 类型 | 获取链接 | 说明 |
|---------|------|---------|------|
| **CADP 官方网站** | 工具主页 | [cadp.inria.fr](http://cadp.inria.fr) | INRIA开发的异步系统验证工具箱，近50个工具，支持组合验证。 |
| **CADP Tutorial (AFADL 2012)** | 演示文稿 | [Inria PDF](http://convecs.inria.fr/doc/presentations/Lang-Serwe-AFADL-12.pdf) | 详细教程，涵盖LOTOS/EXP.OPEN/BCG_MIN/PROJECTOR/EVALUATOR等工具的使用。 |
| **CADP Tutorial (FM 2012)** | 演示文稿 | [Inria PDF](http://convecs.inria.fr/doc/presentations/Mateescu-FM-12.pdf) | 另一版CADP教程，侧重状态空间生成、组合验证、分布式验证。 |
| **CADP: A Modular Toolbox** | 综述论文 | [arXiv:2111.08203](https://arxiv.org/pdf/2111.08203) | 近期CADP综述，讨论组合验证的自动化策略（smart reduction、CEGAR、semicomposition）。 |

### 7.2 PAT (Process Analysis Toolkit)

| 资源名称 | 说明 | 链接 |
|---------|------|------|
| **PAT 官网** | 新加坡国立大学开发的模型检验工具，支持CSP、RTS、概率/实时/时序扩展 | [pat.comp.nus.edu.sg](http://pat.comp.nus.edu.sg/) |

### 7.3 Penrose (PNB Model Checker)

| 资源名称 | 说明 | 链接 |
|---------|------|------|
| **Penrose 项目** | 基于PNB组合代数的Petri网可达性检验器 | 与 Sobociński 的 PNB 论文配套 |

### 7.4 其他重要工具

| 工具 | 说明 |
|------|------|
| **FDR3/4** | CSP精化检验器，工业标准工具，由 Oxford 开发。 |
| **Scyther** | 安全协议自动分析工具，支持组合验证框架。 |
| **CPN Tools** | 着色Petri网建模与仿真工具，Jensen团队开发。 |
| **TINA** | 时间Petri网分析工具箱，附编辑器与多种分析器。 |

---

## 八、经典教材与参考书

### 8.1 按主题推荐的必读书单

#### 【优先级1：Petri网基础】
1. **Cardoso et al. — Petri Nets: A Comprehensive Introduction**（2024新版，免费PDF，最推荐）
2. **Murata — Petri Nets: Properties, Analysis and Applications**（1989经典综述，必读）
3. **Jensen & Kristensen — Coloured Petri Nets**（2009，着色网权威）

#### 【优先级2：组合分析/组合验证】
4. **Garavel, Lang, Mounier — Compositional Verification in Action**（2018综述，含大量工业案例）
5. **Groote & Reniers — Algebraic Process Verification**（μCRL/ACP组合验证的系统教程）
6. **Sobociński & Stephens — Compositional model checking of concurrent systems, with Petri nets**（PNB组合模型检验教程）

#### 【优先级3：进程代数】
7. **Hoare — Communicating Sequential Processes**（1985，CSP奠基）
8. **Roscoe — Understanding Concurrent Systems**（2011，CSP现代综合教材）
9. **De Nicola — A Gentle Introduction to Process Algebras**（2013讲义，三大代数对比）
10. **Milner — Communication and Concurrency**（1989，CCS经典）

#### 【优先级4：Petri网代数与高级主题】
11. **Best, Devillers, Koutny — Petri Net Algebra**（2001，PBC/PNA权威专著）
12. **van der Aalst — Verification of Workflow Nets**（1997，WF-net基础）
13. **Ehrig et al. — Fundamentals of Algebraic Graph Transformation**（2006，图重写数学基础）

### 8.2 学习路径建议

```
第一阶段（2-4周）
  ├── Cardoso et al. 教材（第1-3章：Petri网基础定义与分析）
  ├── Murata 综述论文
  └── 使用 CPN Tools / TINA 完成简单建模练习

第二阶段（3-4周）
  ├── De Nicola 讲义（进程代数三大家族概览）
  ├── Roscoe CSP 教材（前8章：核心语法与语义）
  └── 使用 PAT 或 FDR 验证简单并发系统

第三阶段（4-6周）
  ├── Sobociński & Stephens PNB 教程（组合模型检验）
  ├── Best et al. Petri Net Algebra（选读控制流与同步章节）
  ├── van der Aalst WF-net 论文（声音性验证）
  └── Garavel et al. 组合验证综述（CADP方法学）

第四阶段（进阶/研究）
  ├── Groote & Reniers 代数验证（μCRL/LPE/锥与焦点）
  ├── Andova et al. 安全协议组合框架
  ├── GROOVE 图重写工具实践
  └── 阅读相关领域最新论文（AI能力组合、范畴弦图等）
```

---

*本清单基于公开可获取的学术资源整理，所有PDF链接均为免费开放获取版本。建议优先阅读标注"⭐⭐"难度及"必读"说明的资源。*
