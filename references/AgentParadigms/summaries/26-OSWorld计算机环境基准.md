---
title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments"
source_pdf: "26-Xie-OSWorld_v2.pdf"
arxiv_id: "2404.07972"
arxiv_version: "v2"
authors:
  - "Tianbao Xie"
  - "Danyang Zhang"
  - "Jixuan Chen"
  - "Xiaochuan Li"
  - "Siheng Zhao"
  - "Ruisheng Cao"
year: 2024
venue: "NeurIPS 2024 (D&B)"
type: "评测对照 + 内容索引 + 精读"
generated_at: "2026-08-17"
summary_version: "3.0"
---

# 论文摘要：OSWorld——真实计算机环境 GUI 交互基准

## 1. 适用场景

- 当你要评估 computer-use / GUI agent 在**真实操作系统**（而非 mock 网页或单一应用沙盒）上的端到端任务能力，需要一个可复现的执行式基准时，读这篇：369 个 Ubuntu 任务 + 43 个 Windows 任务，每个都带初始状态配置与专属评估脚本。
- 当你要为自己的 agent 基准搭建"**可复现初始状态 + 终态判定**"基础设施（VM 快照、config 驱动 setup、getter/evaluator 函数库、云文件对比）时，直接参考其环境架构与逐应用评估方案（附录 B.6 给了 LibreOffice/Thunderbird/VLC/Chrome/VS Code/GIMP 各自的判定做法）。
- 当你需要在**截图 / a11y 树 / 截图+a11y / Set-of-Mark** 四种观察空间之间做输入选型，或需要引用"GUI grounding 与操作知识是当前 VLM agent 主要瓶颈"的实证数字时。
- 当你的测试集要包含**不可行任务**（deprecated/hallucinated 功能）以检验 agent 的 FAIL 判定与自我认知，或要做跨 OS（Ubuntu→Windows）迁移一致性分析时。

> 锚点：Abstract; §1 Introduction; §2 OSWORLD Environment; §3 OSWORLD Benchmark; §4 Benchmarking LLM and VLM Agent Baselines; §5 Analysis。

## 2. 主要观点与方案

### 2.1 研究问题与动机（§1 Introduction）

- 现有基准要么只有演示数据无可执行环境（评估假设单一解、错误惩罚替代正确解），要么环境局限于特定应用/域（网页导航、coding、移动端），无法反映真实计算机使用的多样性与复杂度，限制了任务范围与 agent 可扩展性（§1）。
- OSWorld 定位为**首个可扩展的真实计算机环境**：支持任务初始化、执行式评估与交互式学习，覆盖 Ubuntu/Windows/macOS，允许自由原始键鼠控制真实应用（§1; §2）。

### 2.2 环境框架（§2 OSWORLD Environment）

- **任务定义**（§2.1 Task Definition）：形式化为 POMDP (S, O, A, T, R)；执行式奖励 R: S×A→[0,1]，终态达标给 1（或部分达成给小数）、对不可行任务正确预测失败也给分；终止条件为 DONE/FAIL 或达到最大步数（实验中 15 步）。
- **基础设施**（§2.2; §2.2.1 Overview）：宿主机 Coordinator 读取 config 文件 → 创建/恢复 VM 快照 → Task Manager 初始化；Agent 观察截图与 a11y 树，动作以 pyautogui 代码字符串经 Simulator 在 VM 中执行；结束后按 post-config 后处理、回收文件、跑评估脚本。单宿主机可并行多 VM、支持 headless。
- **初始状态构造**（§2.2.2 Initial Task Environment Setup）：刻意模拟"工作进行中的中间态"（软件已开、窗口已乱），采用混合方案（共享基础快照 + 下载文件 + 预处理命令）而非逐题全量快照（每题省去 GB 级存储）；三阶段：启动 VM → 准备文件 → 执行预处理命令。
- **执行式评估**（§2.2.3 Execution-Based Evaluation）：逐任务定制评估脚本 = getter（从 VM 配置文件/环境/云端取关键数据，含实时任务的爬虫动态 getter）+ evaluator（如 is_cookie_deleted、compare_table、check_a11y_tree）；必要时做逆向工程（如解密 Thunderbird 账号信息）、开远程调试端口（Chrome/VLC）、写 VS Code 扩展取证。全库共 **134 个唯一评估函数**。
- **观察空间**（§2.3 Observation Space）：完整桌面截图（含鼠标位置形状，默认 1920×1080）+ XML 格式 a11y 树（Ubuntu 用 ATSPI2/pyatspi，Windows 用 PyWinAuto），对齐人类感知但带来高分辨率长程决策与超长结构化文本的挑战。
- **动作空间**（§2.4 Action Space）：以 pyautogui Python 代码为通用动作（覆盖移动/点击/拖拽/按键/热键等全部人机操作，可内嵌 for 循环等程序结构提升表达力），外加 WAIT/FAIL/DONE 三个特殊动作；附录另提供 computer_13（13 类参数化动作，面向 RL）（§A.3）。

### 2.3 基准构建与统计（§3 OSWORLD Benchmark）

- **系统与软件**（§3.1 Operating System and Software Environments）：主集建于 Ubuntu（开源性利于 setup/评估 API），聚焦 8 个代表性应用：Chrome、VLC、Thunderbird、VS Code、LibreOffice（Calc/Writer/Impress）、GIMP，加终端/文件管理器等 OS 基础应用；另迁移 43 个 Windows 任务（Excel/Word/PPT，版权原因需用户自行激活）。
- **任务来源与标注**（§3.2 Tasks）：任务取自真实用户场景（官方教程、TikTok/YouTube、WikiHow、Reddit/Quora/Superuser/StackOverflow、Coursera/Udemy、博客），按浏览量/投票筛选；多应用协作任务靠作者头脑风暴补充；刻意收录 **30 个不可行任务**；另整合 **84 例**自 NL2Bash、Mind2Web、SheetCopilot、PPTC、GAIA。9 名 CS 学生耗时 3 个月、约 1800 人时（650 单应用 + 750 workflow + 400 复核），加上约 400 人时收集整合任务；每题 setup 约 1 人时、评估脚本约 2 人时；质检由未参与标注的作者以 agent 身份试做并迭代。
- **统计**（§3.3 Data Statistics）：共 369 任务 = 268 单应用（72.6%）+ 101 跨应用 workflow（27.4%）；含 84 整合（22.8%）与 30 不可行（8.1%）；302 个不同初始状态、134 个评估脚本。表 4 与 17 个既有环境对比：OSWorld 是唯一具备"可控执行环境 + 计算机级环境可扩展性 + 中间态初始化 + 134 个执行式评估函数"的基准。
- **人类表现**（§3.4 Human Performance）：人类中位完成时间 **111.94s**（WebArena 抽样 100 例同设定为 35.38s），人类成功率约 **72.36%**（WebArena 88%），证明任务更耗时更难；分类别人类成功率：OS 75.00%、Office 71.79%、Daily 70.51%、Professional 73.47%、Workflow 73.27%（表 5）。

### 2.4 基线实验设置（§4.1 LLM and VLM Agent Baselines）

- 模型：闭源 GPT-3.5/GPT-4/GPT-4V/GPT-4o、Gemini-Pro/Gemini-ProV/Gemini-Pro-1.5、Claude-3 Opus、Qwen-Max；开源 Mixtral-8x7B、Llama-3-70B、CogAgent。
- 四种输入设定：a11y 树（过滤后紧凑制表符格式，规则见附录 C.3）、纯截图（1920×1080）、截图+a11y 树、Set-of-Mark（用 a11y 树画编号边界框 + 元数据，模型按编号指定操作对象）。
- 实现细节（附录 C.1）：(observation, action) 对的 few-shot 方案失败（纯截图仅 2.79%），改用 chat 模式保留最近 3 轮观察与动作；temperature 1.0、top-p 0.9、最大生成 1500 token；每任务最多 15 步、30 分钟。

### 2.5 主要发现（§4.2 Results）

- **LLM/VLM 远不能胜任数字助手**：a11y 树输入下最强语言模型成功率 2.37%–12.24%（最佳 GPT-4 12.24%）；纯截图下最强 VLM 仅 5.26%（GPT-4V）–5.80%（Gemini-ProV）；全部设定总区间 0.99%–12.24%，对比人类 72.36%（§4.2）。
- **Agent 跨任务类型方差远大于人类**：CLI 型 OS 任务好于 GUI 型 Office 任务（部分子集 0%，如 LibreOffice Calc 常为 0）；跨应用 workflow 普遍低于 5%，最高仅 6.57%（GPT-4V+SoM）；人类各类稳定在约 70%（波动 <5%）（§4.2）。
- **a11y 树与 SoM 的效果因模型而异**：GPT-4V/Claude-3 加 a11y 树有提升，Gemini-Pro 结论反转；SoM 对 GPT-4V 反而低于截图+a11y 树（12.17%→11.77%），推测因 OS 内分辨率更高、元素更多导致噪声抵消辅助作用，且坐标级细操作无法用边界框建模（§4.2; 附录 D.5/D.6）。
- **纯截图虽最弱但是长期终极配置**：不依赖额外信息、贴近人类感知，a11y 树并非所有软件都支持且 token 量大（§4.2）。

### 2.6 深入分析（§5 Analysis）

- **难度/可行性/应用数**（§5.1）：按人类用时分组，GPT-4V(SoM) 在 Easy/Medium/Hard 上为 16.78%/13.12%/4.59%，人类为 84.91%/81.08%/49.57%（Hard 对模型近乎不可解）；不可行任务判定 16.67% 略好于可行任务 13.34%；单应用 13.74% 约为跨应用 6.57% 的两倍。
- **多模态观察变量**（§5.2）：分辨率——纯截图性能随分辨率单调提升，SoM 在降采样 0.4（768×432）反而最佳、0.2 明显下降；历史——a11y 树文本轨迹历史越长越好（单次观察 90 分位 6343.60 token，约需 6000 上下文覆盖 90% 案例），截图历史无增益（当前 VLM 不擅长从图像提取上下文）；鲁棒性——28 个原成功率 50.79% 的任务上加扰动，改窗口位置降至 36.5%、窗口最小化降至 25.39%、无关软件遮挡降至 15.04%（降幅 60%–80%），agent 缺乏窗口状态管理策略。
- **跨 OS 一致性**（§5.3）：GPT-4V 纯截图在 Ubuntu 4.88% vs Windows 2.55%，相关系数 **0.7**，方法论可跨 OS 迁移。
- **定性分析**（§5.4）：成功案例如两次调用 ffmpeg 抽取/去除视频字幕；550 个失败样本中 **>75% 存在鼠标点击不准**（规划对但执行坐标错），并连锁引发重复点击与环境噪声困境（误触弹窗/广告）；专业软件先验缺乏（GIMP 调亮度找不到入口）；人类与 agent 难度感知错位（人类擅长的文字/设计类 agent 差；agent 擅长"代码可解"任务但可能违反指令如用 ffmpeg 替代 GIMP）；Claude-3 Opus 平均比 GPT-4V 低 2.84–7.76 个百分点，表现为规划合格但 grounding 细节幻觉（把双击当选中、B 列当 C 列）。

### 2.7 结论、局限与未来工作（§6 Related Work; §7 Conclusion and Future Work）

- 相关工作定位（§6）：对比 coding/web/mobile 三类多模态基准与 GUI grounding 数据集，OSWorld 独有开放式 OS 级交互 + 多样评估脚本；VLM 侧指出长程规划、截图细节感知、像素坐标定位与世界知识均有提升空间。
- 未来方向（§7）：(1) 增强 VLM 的 GUI grounding（对窗口变化鲁棒、图像形式的上下文/历史编码、更高分辨率与坐标精度）；(2) agent 架构上的探索、记忆与反思，以及个性化定制；(3) **安全**——目前评估只判任务对错、无法度量潜在破坏性副作用，缺可靠安全指标，VM 隔离只是权宜；(4) 扩展数据与环境（更多专业域），a11y 树质量跨应用参差需更智能的过滤与缺失处理，需要无痛的人类操作数据采集管道。
- 局限（§3.2 Quality control）：尽管四轮复核投入 400+ 人时，误报/漏报仍可能进一步通过红队减少，留作未来工作。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| 基准规模 | 369 个 Ubuntu 任务（268 单应用 72.6% + 101 workflow 27.4%；30 不可行 8.1%；84 整合 22.8%）+ 43 个 Windows 分析集 | Abstract; §3.3 |
| 评估基础设施 | 134 个唯一执行式评估函数、302 个不同初始状态（远超此前基准，WebArena 为 5） | §3.3; Table 4 |
| 人类成功率 | 72.36%（中位用时 111.94s；对照 WebArena 人类 88%、35.38s） | §3.4; §4.2 |
| 最佳模型总成功率 | 12.24%（GPT-4 + a11y 树）vs 人类 72.36%；全部基线区间 0.99%–12.24% | §4.2; Table 5 |
| 纯截图输入最佳 | GPT-4V 5.26%、Gemini-ProV 5.80%（1920×1080） | §4.2 |
| 跨应用 workflow 最佳 | 6.57%（GPT-4V + Set-of-Mark），普遍低于 5% | §4.2; §5.1 |
| Hard 任务（>180s） | GPT-4V(SoM) 4.59% vs 人类 49.57% | §5.1 |
| 窗口扰动鲁棒性 | 原始 50.79% → 改位置 36.5% / 最小化 25.39% / 遮挡 15.04% | §5.2 |
| 跨 OS 迁移 | Ubuntu 4.88% vs Windows 2.55%，相关系数 0.7（GPT-4V 纯截图） | §5.3 |
| 主要错误模式 | 550 个失败样本中 >75% 含鼠标点击不准；Claude-3 平均低于 GPT-4V 2.84–7.76 个百分点 | §5.4 |

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 arXiv | https://arxiv.org/abs/2404.07972 |
| 项目页 | https://os-world.github.io（代码、环境、基线实现、数据全部开源） |
| 代码仓库 | https://github.com/xlang-ai/OSWorld（论文脚注 1 指向项目页） |
| 关联基准 | 本目录 25（GAIA，被整合 84 例来源之一）、22（VisualWebArena，SoM 设定参考） |

## 5. 一句话索引（给 Agent 用）

> OSWorld：首个跨真实操作系统（Ubuntu/Windows/macOS）的可扩展真实计算机环境 + 369 任务基准，快照式"中间态"初始化 + 逐任务执行式评估（134 个评估函数、302 个初始状态）。结果：人类 72.36% vs 最佳模型 12.24%（GPT-4+a11y 树；纯截图最高仅 5.80%），瓶颈是 GUI grounding（失败样本 >75% 含点击不准）与操作知识，跨应用 workflow 最高 6.57%，跨 OS 相关系数 0.7。含义：评估 computer-use agent 必须执行式判定终态；截图/a11y/SoM 输入各有利弊，纯截图是长期终极配置。
