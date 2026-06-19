# OpenSpec、Speckit、Superpowers与OMO在SDD方面的深度研究报告

## 摘要

随着AI编码助手在2026年全面进入多智能体协作时代，**规范驱动开发（Specification-Driven Development, SDD）** 已从理论概念迅速演变为工业级实践标准。SDD的核心理念在于：在编写任何代码之前，先编写一份结构化的规范文档（Spec），使规范成为人类开发者与AI共同的"唯一事实来源（Single Source of Truth）"，而代码仅是规范的最终实现产物。本报告深入剖析了当前SDD生态中四个代表性工具框架——**OpenSpec**、**GitHub Speckit**、**Superpowers**和**Oh My OpenAgent (OMO)**——在核心逻辑、亮点设计、适用场景、优劣势等方面的深度差异，并结合Coding Agent的近期发展趋势，对SDD的未来演进方向进行了系统性展望。

---

## 1. 规范驱动开发（SDD）概述

### 1.1 SDD的定义与核心理念

规范驱动开发（SDD）是一种以"规范（Specification）"为核心驱动力的软件开发方法论。其理论根基可追溯至形式化方法与契约式编程，但在2025-2026年AI编码助手大规模普及的背景下获得了全新的实践维度。传统软件开发中，需求文档、设计文档与代码实现之间长期存在"语义鸿沟"——需求以自然语言描述，设计以图表和文档呈现，而代码则以编程语言实现，三者之间的转换依赖开发者的主观理解，导致信息丢失、需求漂移和架构腐化。SDD通过将规范提升为开发流程的"一等公民"，建立了一套从需求到实现的结构化转换管道。

SDD的理论框架包含三个关键层次：**Spec-First（规范优先）** 强调在编码前定义可验收的规格与任务拆分；**Spec-Anchored（规范锚定）** 将规范作为持续集成和持续交付流程中的验证锚点，确保实现不偏离规范；**Spec-as-Source（规范即源码）** 则将规范视为系统的最终真相来源，代码仅是规范的派生产物。这三个层次代表了SDD从辅助性实践到核心开发范式的演进路径，团队可根据项目特征和成熟度选择合适的层次。

### 1.2 SDD与传统开发范式的对比

与传统的Test-Driven Development（TDD）相比，SDD将"规范"置于比"测试"更根本的位置。TDD强调"先写测试、后写代码"，但测试本身仍需基于对需求的理解，且测试代码的可读性对非技术人员存在门槛。SDD则将规范视为连接业务人员、产品经理、开发人员和AI助手的通用语言，规范文档使用Markdown等轻量级格式，包含用户场景、功能需求、验收标准、边界案例等结构化信息，既可供人类审阅，也可作为AI生成代码和测试的上下文基础。

与Behavior-Driven Development（BDD）相比，SDD的范围更为广泛。BDD主要关注通过Given-When-Then格式描述应用行为，侧重于测试场景的可读性。而SDD不仅涵盖行为描述，还包括架构决策、接口契约、数据模型、非功能性需求等系统级规范，其目标是建立完整的"系统知识库"而非仅仅是测试场景库。

### 1.3 AI时代SDD的复兴动因

2025年至2026年，AI编码助手从简单的代码补全工具进化为能够自主理解代码库、执行多文件编辑、运行测试并提交Pull Request的"编码智能体（Coding Agent）"。这一能力跃迁带来了两个关键挑战：一是AI助手在长对话中容易"遗忘"原始需求，导致实现偏离初衷；二是AI生成的代码缺乏可追溯的需求依据，使得代码审查和后期维护变得困难。SDD正是应对这些挑战的系统性解决方案——通过将需求固化为持久化的规范文档，SDD为AI助手提供了稳定的"外部记忆"，同时为团队建立了从需求到实现的完整审计链。

---

## 2. OpenSpec：轻量级规范变更管理框架

### 2.1 核心逻辑：Artifact依赖链与Delta Spec系统

**OpenSpec**由Fission AI团队开发，定位为一款轻量级、便携式的规范驱动开发框架，专为AI编程助手设计。其核心理念是将AI辅助开发组织为一系列可追踪的变更（Changes），每个变更围绕一组结构化的工件（Artifacts）展开。OpenSpec的核心逻辑建立在一条**Artifact依赖链**之上：

```
proposal.md → design.md → specs/*.md → tasks.md → 代码实现 → 归档
   (为什么做)    (怎么做)     (做成什么样)   (分几步做)   (动手做)    (存档)
```

这条链条体现了从意图到实现的渐进式细化过程。**proposal.md**回答"为什么要做这个变更"，记录变更的动机、目标和范围；**design.md**回答"如何技术实现"，包含架构决策、技术选型和接口设计；**specs/*.md**回答"做成什么样"，使用RFC 2119标准关键词（SHALL/MUST/SHOULD/MAY）和Given-When-Then场景格式定义具体行为；**tasks.md**则将实现拆分为可逐项勾选的任务清单。

OpenSpec最具创新性的设计是其**Delta Spec（差异规范）系统**。与重写整个规范不同，每个变更的规范仅描述与当前系统行为的差异，使用ADDED、MODIFIED、REMOVED三个操作标记：

```markdown
## ADDED Requirements
### Requirement: Two-Factor Authentication
The system MUST support TOTP-based two-factor authentication.

## MODIFIED Requirements
### Requirement: Session Expiration  
The system MUST expire sessions after 15 minutes of inactivity.
(Previously: 30 minutes)

## REMOVED Requirements
### Requirement: Remember Me
(Deprecated in favor of 2FA.)
```

当变更完成并归档时，这些Delta Spec自动合并回主规范（`openspec/specs/`目录），形成不断演进的"活文档（Living Documentation）"。这种设计借鉴了Git的分支模型——主规范如同主分支，变更规范如同功能分支，归档操作相当于合并。这带来了三个关键优势：一是避免了在并行开发多个功能时的规范冲突；二是变更审查者只需关注差异部分，无需审阅完整规范；三是系统规范的演进历史被完整保存，可随时追溯任何功能点的变更脉络。

### 2.2 亮点设计

#### 2.2.1 轻量级与零依赖架构

OpenSpec的安装仅需一行命令：`npm install -g @fission-ai/openspec`，无需Python环境、无需API密钥、无需MCP服务器。这种极简的依赖模型使其在任何Node.js 20.19+环境中即可运行，特别适合对安全和隐私要求严格的企业环境。与其他SDD工具相比，OpenSpec的每次变更输出约250行文档（对比Speckit的约800行），显著降低了审查负担和AI上下文消耗。

#### 2.2.2 Brownfield（棕地）优先设计

OpenSpec明确将"现有代码库的持续演进"作为核心场景，而非仅关注从零开始的新项目。通过`openspec init`初始化时，OpenSpec会分析现有项目结构并生成AGENTS.md文件——一份"给机器人的README"，指导AI助手如何阅读项目规范。对于已有系统的新功能开发，开发者只需描述变更范围，OpenSpec自动生成Delta Spec，无需重写整个系统规范。

#### 2.2.3 可配置Schema系统

OpenSpec允许团队定义自定义的Schema来适应不同的工作流需求。内置Schema包括`spec-driven`（完整规范驱动）、`tdd-driven`（测试驱动开发）和`rapid`（快速迭代），团队也可以通过YAML文件定义自己的Artifact序列和模板。例如，合规严格的团队可以添加风险评估和审计记录Artifact，研究驱动型团队可以增加技术探索阶段。

#### 2.2.4 跨Agent兼容性

OpenSpec支持30多种AI编码助手，包括Claude Code、Cursor、GitHub Copilot、Windsurf、Cline等，通过生成工具特定的斜杠命令（如Claude Code的`/opsx:propose`、Cursor的`/openspec-proposal`）实现深度集成。所有规范文件均为纯Markdown格式，可直接在Git中版本控制、差异比较和Pull Request审阅。

### 2.3 适用场景

OpenSpec在以下场景中表现尤为出色：

**中大型前端模块迭代**：当变更涉及多个页面、组件或API接口时，OpenSpec的变更文件夹结构确保所有相关规范集中管理，避免需求散落在聊天记录中。接口与页面结构先对齐、组件与路由变更有据可查、联调与验收标准可追溯。

**遗留系统现代化**：对于需要逐步添加规范文档的棕地项目，OpenSpec的Delta机制允许团队以增量方式建立规范体系，无需一次性重写整个系统的文档。每次功能增强或Bug修复都是补充规范的机会。

**合规与审计要求严格的行业**：金融、医疗、政府等领域需要完整的变更审计链。OpenSpec的归档机制（`openspec/changes/archive/YYYY-MM-DD-{change}/`）自动保存每次变更的完整上下文，包括提案、设计、任务、规范和验证报告，满足合规审查要求。

**多Agent并行开发**：当团队使用OpenCode等支持SubAgent的平台时，每个变更可在独立的Git WorkTree中由不同Agent并行处理，最终按顺序合并和归档，保持主规范的一致性。

### 2.4 优劣势分析

| 维度 | 优势 | 劣势 |
|------|------|------|
| **学习曲线** | 平缓，3个核心命令即可上手 | 高级功能（自定义Schema、并行开发）需要一定学习成本 |
| **平台依赖** | 零依赖，npm全局安装即可，无需API密钥 | 需要Node.js环境（20.19+） |
| **规范管理** | Delta Spec系统高效管理变更，避免冲突 | 统一规范文档在大型系统中可能变得庞大 |
| **AI兼容性** | 支持30+种AI助手，无供应商锁定 | 不同AI助手间的体验可能存在细微差异 |
| **流程灵活性** | 流体式工作流，可跳过不必要的步骤 | 较少的强制性检查点，依赖团队自律 |
| **社区生态** | GitHub 45.8k+ Stars，活跃社区 | 相比GitHub Speckit，企业级案例相对较少 |
| **输出量** | 约250行/变更，审查负担轻 | 信息量较少可能在复杂场景下不够充分 |
| **TDD支持** | 通过Schema可选启用 | 不强制TDD，需团队自行约束 |

### 2.5 选型考量

选择OpenSpec的核心判断标准是：**团队是否需要在现有代码库上以最小开销建立规范的变更管理流程**。如果项目已经运行一段时间，团队成员使用不同的AI助手，且希望规范与代码共同演进而非成为额外负担，OpenSpec是最合适的起点。其"流体优于 rigid"的设计理念特别适合敏捷团队，但这也意味着团队需要具备一定的自律性来维护规范质量。

---

## 3. GitHub Speckit：结构化全生命周期治理框架

### 3.1 核心逻辑：Constitution驱动的七阶段流水线

**GitHub Speckit**（官方名称Spec Kit）是GitHub推出的开源SDD工具集，代表了结构化治理派的设计理念。其核心逻辑围绕一份**Constitution（宪法）** 文档展开——这不是比喻，而是字面意义上的项目"宪法"，一份由团队共同制定的、定义所有开发决策必须遵循的原则的治理文档。

Constitution的典型条款包括：
- **Article I - 规范驱动开发**：每个功能必须首先以独立规范开始，包含用户场景、可独立测试的功能需求、可衡量的验收标准、边界案例和错误场景。
- **Article II - 独立用户故事**：每个用户故事必须可独立测试和交付，使用Given-When-Then格式描述，并标注优先级（P1/P2/P3）。
- **Article III - 测试优先开发（非协商）**：测试必须在实现之前编写，严格遵循红-绿-重构循环。
- **Article IV - 宪法合规性**：所有实现计划必须通过Constitution Check门控才能进入实现阶段。
- **Article V - 简洁与清晰**：优先选择简单清晰的方案而非巧妙复杂的方案，遵循YAGNI原则。

基于Constitution，Speckit定义了一条严格的**七阶段流水线**：

```
Constitution → Specify → Clarify → Plan → Analyze → Tasks → Implement
  (项目原则)   (功能定义)  (需求澄清) (技术规划) (一致性分析) (任务拆解) (代码实现)
```

每个阶段都有明确的输入、输出和验收标准，团队不能跳过阶段或逆向流动。`/speckit.specify`命令将高层功能描述转换为完整的结构化规范；`/speckit.clarify`识别并修复规范中的模糊区域；`/speckit.plan`生成技术实现计划；`/speckit.analyze`进行跨工件一致性检查；`/speckit.tasks`将计划拆解为有序任务；最后`/speckit.implement`才进入代码生成。

### 3.2 亮点设计

#### 3.2.1 Constitution治理机制

Constitution是Speckit区别于其他SDD工具的根本特征。它不仅是一套模板或检查清单，而是具有"宪法权威"的治理文档——当其他开发实践与Constitution冲突时，Constitution优先。修改Constitution需要正式的修订流程：书面提案、影响分析、版本号递增、同步影响报告、利益相关者批准。这种设计确保了项目标准和开发纪律不会因为时间压力或人员变动而被侵蚀。

#### 3.2.2 强制阶段门控

每个阶段转换都必须满足明确的门控条件：规范阶段必须有清晰的用户场景和需求；规划阶段必须通过Constitution Check或提供违规的合理理由；任务阶段必须识别所有基础/阻塞任务；实现阶段必须通过所有测试并满足验收标准。这些门控防止了"边做边想"的即兴开发模式，确保每一步都有充分的思考和文档支撑。

#### 3.2.3 编号化的特征管理

Speckit为每个功能分配顺序编号（001、002、003...），功能分支、规范目录和任务ID均基于该编号命名。这种编号系统使得团队成员可以快速定位任何功能的规范、实现和讨论，也为新成员理解项目历史提供了清晰的导航结构。

#### 3.2.4 丰富的模板生态

Speckit提供了spec-template.md、plan-template.md、tasks-template.md、agent-file-template.md等多种模板，覆盖了从功能规范到技术计划、从任务拆解到AI Agent配置的全流程。这些模板不仅提供了结构，还内嵌了最佳实践指导，如"每个需求必须可独立测试"、"验收标准必须使用可衡量的语言"等。

### 3.3 适用场景

**从零开始的新项目（Greenfield）**：Speckit的设计理念是"从零开始时就做好"——通过Constitution确立项目原则，通过严格的阶段流水线确保每个功能都经过充分的规划和审查。对于新项目的早期阶段，这种结构化方法可以避免技术债务的积累。

**需要清晰角色分离的团队**：当团队中有产品经理、架构师、开发工程师等明确角色分工时，Speckit的阶段流水线天然映射到这些角色——产品经理主导Specify阶段，架构师主导Plan阶段，开发工程师主导Implement阶段。

**代码质量和一致性至关重要的项目**：金融系统、医疗设备软件、航空航天等领域，代码错误可能导致严重后果。Speckit的强制TDD、Constitution合规检查和阶段门控为这些高风险领域提供了额外的安全保障。

**大型团队和分布式团队**：当团队规模超过20人，或团队成员分布在不同地域和时区时，Speckit的结构化流程和编号化管理体系确保所有人遵循统一的标准，减少沟通成本和误解风险。

### 3.4 优劣势分析

| 维度 | 优势 | 劣势 |
|------|------|------|
| **治理强度** | Constitution提供强有力的项目治理，防止标准侵蚀 | 前期投入大，需要团队共同制定和维护Constitution |
| **流程严谨性** | 七阶段流水线确保充分的规划和审查 | 流程刚性，快速Bug修复或小改动也可能经历完整流程 |
| **TDD支持** | 内置强制TDD，红-绿-重构循环成为硬性要求 | 对于不需要全面测试覆盖的项目可能过度 |
| **文档完整性** | 每功能约800行文档，信息充分 | 文档量大，审查负担重，AI上下文消耗多 |
| **学习曲线** | 结构清晰，有丰富模板 | 较陡峭，需要理解Constitution概念和七阶段流程 |
| **社区与背书** | GitHub官方出品，75k+ Stars，最大社区 | GitHub生态锁定风险（尽管是开源的） |
| **平台依赖** | 纯Markdown，跨平台 | 需要Python环境和uv/pipx安装 |
| **迭代速度** | 结构化流程减少返工 | 前期规划耗时，可能延缓首次交付 |

### 3.5 选型考量

选择Speckit的核心判断标准是：**团队是否愿意在项目早期投入时间建立严格的治理框架，以换取长期的代码质量和一致性**。如果团队规模较大、角色分工明确、代码质量要求极高，且项目处于早期阶段，Speckit是最适合的选择。但对于小型团队或需要快速迭代的项目，Speckit的严格流程可能被视为"重装流程"或"再造瀑布"，此时OpenSpec的轻量级方法可能更为合适。

---

## 4. Superpowers：多Agent协作的工程质量执行框架

### 4.1 核心逻辑：Skill驱动的自动触发工作流

**Superpowers**由Jesse Vincent开发，是一套为AI编码助手（主要是Claude Code）设计的软件开发技能框架。与OpenSpec和Speckit的"命令式"交互不同（用户需要显式调用`/opsx:propose`或`/speckit.specify`），Superpowers采用了独特的**Skill自动触发机制**——用户只需用自然语言描述需求，Superpowers自动识别需求类型并激活相应的技能（Skill）。

Superpowers的核心工作流如下：

```
Brainstorming → Git Worktree → Writing Plans → Subagent Dev → Finishing Branch
  (需求探索)      (环境隔离)      (计划编写)      (子代理开发)     (分支收尾)
```

**Brainstorming（头脑风暴）技能**在需求不明确时自动触发，通过苏格拉底式对话逐个提问，澄清需求细节，输出design.md设计文档。**Writing Plans（编写计划）技能**在设计确认后自动触发，将工作拆解为2-5分钟可完成的"一口大小"任务，每个任务包含精确的文件路径、完整代码示例和验证步骤。**Subagent-Driven Development（子代理驱动开发）技能**在计划确认后自动触发，为每个任务派遣独立的子代理（Subagent）实现。**Finishing Branch（分支收尾）技能**在实现完成后自动触发，执行合并、创建PR、保留或丢弃分支等收尾操作。

### 4.2 亮点设计

#### 4.2.1 子代理驱动开发（Subagent-Driven Development）

这是Superpowers最具创新性的设计。在传统的AI编码工作流中，一个Agent处理整个任务，随着对话长度增加，上下文窗口逐渐饱和，导致"上下文污染"和遗忘。Superpowers通过为每个任务派遣**全新的子代理**来解决这一问题：

1. **Implementer Subagent**：负责代码实现，拥有干净的上下文窗口，只关注当前任务
2. **Spec Reviewer Subagent**：审查实现是否符合规范要求
3. **Code Quality Reviewer Subagent**：审查代码质量、安全性和最佳实践

每个子代理完成后，其结果由Reviewer Subagent进行两阶段审查（规范合规性审查+代码质量审查），发现的问题由Fix Subagent修复。这种"一个任务一个代理"的模型避免了上下文污染，确保了高质量的实现。

#### 4.2.2 强制TDD（RED-GREEN-REFACTOR）

当用户在需求描述中提到"TDD"、"test-driven"或"write tests first"时，**test-driven-development技能**自动激活，强制执行完整的TDD循环：

1. 🔴 **RED**：先编写测试，运行确认测试失败
2. 🟢 **GREEN**：编写最小实现代码使测试通过
3. 🔵 **REFACTOR**：在测试保持通过的前提下重构代码
4. 重复上述循环

这种强制性是Superpowers的核心价值——没有TDD技能时，AI助手"可能"会写测试；有了TDD技能后，AI助手"必须"遵循TDD流程。

#### 4.2.3 Git Worktree隔离

Superpowers的`using-git-worktrees`技能为每个变更创建独立的Git WorkTree（工作树），实现物理隔离的开发环境。这带来了三个关键优势：一是避免了在开发过程中意外修改主分支；二是支持多个变更的并行开发；三是每个WorkTree都有独立的构建和测试环境，确保变更的独立性。

#### 4.2.4 四道硬性门控（Four Hard Gates）

Superpowers定义了四个不可逾越的门控：
1. **无规范不计划**：没有批准的规范就不能生成计划
2. **无计划不任务**：没有计划就不能拆解任务
3. **无失败测试不编码**：没有先看到测试失败就不能写实现代码
4. **无验证证据不完成**：没有新的验证证据就不能声明完成

这些门控确保了AI助手不会"跳过思考直接动手"，从根本上防止了"Vibe Coding"的随意性。

### 4.3 适用场景

**对代码质量有极致要求的项目**：当团队需要95%+的测试覆盖率、严格的代码审查流程和一致的架构标准时，Superpowers的强制TDD和子代理审查机制提供了工程级的质量保障。

**使用Claude Code等支持Subagent的平台**：Superpowers的子代理驱动开发需要底层平台支持Subagent派遣，目前主要在Claude Code、Cursor等平台上运行。如果团队使用这些平台，Superpowers可以最大化其多Agent能力。

**新项目的早期建设（Greenfield）**：与Speckit类似，Superpowers特别适合从零开始的项目。强制TDD确保了从第一天起就有全面的测试覆盖，子代理审查确保了代码质量的一致性和高标准。

**需要减少人为干预的自动化工作流**：当团队希望AI助手能够自主完成从需求澄清到代码提交的全流程时，Superpowers的Skill自动触发和门控机制提供了高度的自动化能力，人类只需在关键节点进行审批。

### 4.4 优劣势分析

| 维度 | 优势 | 劣势 |
|------|------|------|
| **代码质量** | 强制TDD + 子代理审查 = 工程级质量保障 | Token消耗高（多个子代理并行运行） |
| **自动化程度** | Skill自动触发，几乎无需手动干预 | 自动化程度高可能导致人类对过程的失控感 |
| **上下文隔离** | 每个任务新子代理，零上下文污染 | 需要支持Subagent的平台（Claude Code等） |
| **TDD执行** | 强制RED-GREEN-REFACTOR循环 | 对简单项目可能过度，增加不必要的开销 |
| **Git集成** | 自动WorkTree隔离，物理环境分离 | 平台依赖性强，不支持纯ChatGPT等工具 |
| **Token效率** | 低（多Agent并行消耗大量Token） | 预算敏感团队需要谨慎使用 |
| **规范管理** | 规范嵌入design.md，与实现紧密结合 | 无独立的规范知识库，长期维护可能困难 |
| **审查客观性** | 独立的Reviewer Subagent提供客观审查 | 审查标准依赖Skill定义，灵活性有限 |

### 4.5 选型考量

选择Superpowers的核心判断标准是：**团队是否使用支持Subagent的AI平台，且对代码质量有极高要求**。如果团队已经在使用Claude Code或Cursor，且项目需要严格的TDD实践和高质量的代码输出，Superpowers是最强大的选择。但需要注意的是，Superpowers的Token消耗显著高于其他工具，预算敏感团队需要进行成本评估。此外，Superpowers不适合简单的脚本开发或快速原型验证，其完整的流程在这些场景下可能显得过度。

---

## 5. Oh My OpenAgent（OMO）：多模型智能体编排骨架

### 5.1 核心逻辑：多模型编排与纪律智能体协作

**Oh My OpenAgent**（社区简称OMO，曾用名oh-my-opencode）是一个面向OpenCode的多模型智能体编排骨架（Multi-Model Agent Orchestration Harness）。与OpenSpec、Speckit和Superpowers专注于规范管理不同，OMO的核心定位是**将单一AI代理转变为一个协调的虚拟开发团队**——通过在不同任务间路由到最适合的AI模型，实现"The Right Brain for the Right Job"。

OMO的架构围绕一组**Discipline Agents（纪律智能体）** 展开，每个智能体被分配特定的角色和最适合其任务的AI模型：

| 智能体 | 角色 | 推荐模型 | 职责 |
|--------|------|----------|------|
| **Sisyphus** | 主编排器 | Claude Opus 4.7 / Kimi K2.6 | 规划、委派专家、推进任务至完成 |
| **Hephaestus** | 深度执行者 | GPT-5.5 | 探索代码库、研究模式、端到端自主执行 |
| **Prometheus** | 战略规划师 | Claude Opus 4.7 / Kimi K2.6 | 访谈式需求澄清、范围识别、详细计划制定 |
| **Atlas** | 任务指挥家 | Claude Sonnet 4.6 | 执行Prometheus计划、分发任务、验证完成 |
| **Oracle** | 架构顾问 | Claude Opus 4.7 | 架构咨询、调试分析、反模式识别 |
| **Librarian** | 文档/代码搜索 | Claude Haiku 4.5 | 外部文档和开源代码搜索 |
| **Explore** | 快速代码库扫描 | Claude Haiku 4.5 | 快速文件探索和代码库导航 |
| **Metis** | 预规划顾问 | Claude Sonnet 4.6 | 审查Prometheus计划中的遗漏 |
| **Momus** | 高精度计划审查 | Claude Opus 4.7 | 压力测试计划、识别风险 |
| **Multimodal-Looker** | 视觉分析 | GPT-5.4 | 截图和图像分析、UI原型解读 |

OMO的核心工作流由`ultrawork`（或`ulw`）命令触发，这是一个"一键启动"的自主执行模式：用户只需输入`ultrawork`，OMO自动完成以下流程：

1. **IntentGate（意图门控）**：分析用户的真实意图，避免字面误解
2. **Sisyphus编排**：主编排器评估任务复杂度，决定工作策略
3. **智能体委派**：根据任务类型委派给最适合的专家智能体
4. **并行执行**：多个智能体同时工作，如一个写代码、一个研究模式、一个检查文档
5. **持续验证**：每个完成的任务都经过独立验证
6. **学习到完成**：系统持续工作直到100%完成，不会中途停止

### 5.2 亮点设计

#### 5.2.1 多模型智能路由

OMO的核心创新在于**模型感知路由（Model-Aware Routing）**。不同于使用单一模型处理所有任务，OMO根据任务类型、复杂度和成本要求自动选择最优模型组合：
- **编排与通信**：Claude/Kimi/GLM（擅长理解和协调）
- **深度推理与架构**：GPT-5.4/5.5（擅长复杂推理）
- **视觉/前端任务**：Gemini 3.1 Pro（擅长图像理解）
- **速度与实用**：MiniMax/Grok（快速响应）

这种路由不仅考虑能力匹配，还考虑成本优化——简单搜索任务使用低成本模型，关键架构决策使用最强模型。

#### 5.2.2 Team Mode（团队模式）

OMO v4.0引入了Team Mode，将"一个带子代理的代理"转变为真正的多代理系统。一个主代理编排多达8个并行成员，所有成员通过专用工具（`team_create`、`team_send_message`、`team_task_create`、`team_status`等）实时通信。团队成员在tmux布局中同时工作，用户可以在网格窗口中观察每个成员的实时进展。

Team Mode还提供了预构建的团队模板：
- **hyperplan**：5个"敌对"智能体从不同角度撕碎你的计划，在写一行代码前发现所有问题
- **security-research**：3个漏洞猎人+2个PoC工程师并行审计代码库，按实际可利用性校准严重程度

#### 5.2.3 Hash-Anchored Editing（哈希锚定编辑）

传统AI代理在编辑代码时面临"Harness Problem"——由于行号偏移或上下文丢失，编辑错误率高达约93.3%。OMO引入了**LINE#ID**内容哈希验证机制：每一行代码都带有内容哈希值，编辑操作在应用前必须验证哈希匹配，将编辑成功率从约6.7%提升到68.3%。

#### 5.2.4 Ralph Loop与Todo Enforcer

**Ralph Loop**（`/ulw-loop`）是一个自引用循环，系统会持续工作直到100%完成，不会因为上下文窗口限制或API故障而停止。**Todo Enforcer**则是一个任务执行保障机制——如果Agent进入空闲状态，系统会自动将其拉回任务，确保用户的任务得到完成。

#### 5.2.5 54+生命周期钩子

OMO暴露了54+（Team Mode下61个）生命周期钩子，允许开发者在任务执行的各个阶段注入自定义逻辑。这些钩子支持shell命令、HTTP调用或LLM提示，使得团队可以在不修改核心代码的情况下定制工作流。

### 5.3 适用场景

**复杂的大型项目**：当任务涉及多文件、多步骤、多角色的开发工作时，OMO的多智能体协作能力显著超越单一代理。例如"新增一个完整的后台管理模块"，需要处理菜单、权限、验证、路由、模型关系、列表筛选等多个方面，OMO的任务拆分和专家委派确保不遗漏任何边角。

**跨领域集成项目**：当项目需要前后端协同、多种技术栈整合时，OMO的类别路由系统自动将视觉任务分配给Gemini、架构任务分配给GPT-5.5、编排任务分配给Claude，实现真正的"专业分工"。

**需要高强度规划的长期项目**：对于持续多天的复杂重构或新系统构建，Prometheus的规划模式提供详细的访谈式需求澄清和计划制定，Atlas的执行模式确保计划被忠实执行，Ralph Loop确保任务不被中断。

**Token预算充足的团队**：OMO的功能强大但"非常废token"——多模型并行、多Agent协作、持续验证都消耗大量Token。适合Token预算充足且追求最高质量输出的团队。

### 5.4 优劣势分析

| 维度 | 优势 | 劣势 |
|------|------|------|
| **多模型编排** | 自动路由到最适合的模型，能力最大化 | 配置复杂，需要管理多个API密钥和订阅 |
| **智能体协作** | 10+纪律智能体专业分工，团队协作级效率 | 系统极重，学习曲线陡峭 |
| **编辑可靠性** | Hash-Anchored Editing将编辑成功率提升10倍 | 需要特定的OpenCode环境支持 |
| **自主执行** | ultrawork一键启动，几乎无需人工干预 | 自主度高可能导致过程不透明 |
| **Token消耗** | 极高（多模型并行+多Agent+持续验证） | 预算敏感团队可能无法承受 |
| **平台依赖** | 必须运行在OpenCode之上 | 不支持直接使用Claude Code或Cursor |
| **复杂度** | 适合最复杂的工程任务 | 小修小改用OMO如同"杀鸡用牛刀" |
| **兼容性** | 完整兼容Claude Code的hooks、skills、MCPs | 需要OpenCode作为基础平台 |

### 5.5 选型考量

选择OMO的核心判断标准是：**团队是否已经在使用OpenCode，且需要处理极其复杂的开发任务**。如果项目的复杂度达到了"需要一支AI工程团队"而非"一个AI助手"的程度，OMO是最强大的选择。但对于日常的小修小改或中等复杂度的功能开发，OMO的重型工作流可能显得过度，此时使用OpenCode的轻量模式或Superpowers可能更为高效。

---

## 6. 四框架综合对比分析

### 6.1 核心维度对比矩阵

| 维度 | OpenSpec | Speckit | Superpowers | OMO |
|------|----------|---------|-------------|-----|
| **一句话定位** | 轻量级规范变更管理 | 结构化全生命周期治理 | 多Agent工程质量执行 | 多模型智能体编排骨架 |
| **核心理念** | 规范先行，变更可追溯 | Constitution驱动，阶段门控 | Skill自动触发，TDD强制 | 多模型协作，纪律智能体 |
| **架构模式** | Artifact链 + Delta Spec | 七阶段流水线 | Skill触发 + Subagent驱动 | 智能体编排 + 模型路由 |
| **TDD支持** | 可选（通过Schema） | 强制（Constitution III） | 强制（RED-GREEN-REFACTOR） | 依赖底层Agent |
| **多Agent支持** | 不内置 | 不内置 | 核心功能（Subagent驱动） | 核心功能（10+纪律智能体） |
| **规范存储** | 独立specs/目录，Delta合并 | 每功能独立spec目录 | 嵌入design.md | 不直接管理规范 |
| **平台要求** | 任何AI助手（30+） | 任何AI助手（30+） | Claude Code/Cursor等Subagent平台 | 必须OpenCode |
| **安装方式** | npm全局安装 | Python + uv/pipx | Skill安装 | bunx oh-my-opencode install |
| **API密钥** | 不需要 | 不需要 | 依赖平台 | 需要多个提供商密钥 |
| **输出量/变更** | ~250行 | ~800行 | ~400-600行 | 不固定 |
| **Token效率** | 高 | 中 | 低 | 极低 |
| **学习曲线** | 平缓 | 中等 | 中等 | 陡峭 |
| **社区规模** | 45.8k Stars | 75k Stars | 快速增长 | 新兴 |
| **适用项目类型** | 棕地（Brownfield）优先 | 绿地（Greenfield）优先 | 绿地（Greenfield）优先 | 任何复杂项目 |
| **最佳团队规模** | 1-20人 | 5-50人 | 1-10人 | 3-30人 |

### 6.2 核心能力雷达图分析

**规范管理能力**：Speckit > OpenSpec > Superpowers > OMO
- Speckit的Constitution和七阶段流水线提供了最完整的规范生命周期管理
- OpenSpec的Delta Spec系统在规范演进方面独具特色
- Superpowers将规范嵌入design.md，管理相对简单
- OMO不直接管理规范，依赖外部工具

**代码质量保障**：Superpowers > Speckit > OMO > OpenSpec
- Superpowers的强制TDD和Subagent审查提供了最强质量保障
- Speckit的Constitution强制TDD但无自动审查
- OMO依赖底层Agent的质量实践
- OpenSpec将TDD作为可选项

**多Agent协作**：OMO > Superpowers > OpenSpec > Speckit
- OMO的10+纪律智能体和Team Mode无可匹敌
- Superpowers的Subagent驱动开发实现了任务级并行
- OpenSpec支持Subagent但不内置多Agent逻辑
- Speckit主要面向单Agent工作流

**灵活性与适配性**：OpenSpec > OMO > Speckit > Superpowers
- OpenSpec的流体工作流和可配置Schema最灵活
- OMO的54+钩子允许深度定制
- Speckit的固定流水线限制了灵活性
- Superpowers的自动触发机制灵活性有限

**轻量性与易用性**：OpenSpec > Speckit > Superpowers > OMO
- OpenSpec的npm安装和零依赖最轻量
- Speckit结构清晰但有Python依赖
- Superpowers需要Subagent平台支持
- OMO的重型架构配置最复杂

**Token效率**：OpenSpec > Speckit > Superpowers > OMO
- OpenSpec的单Agent模式和轻量输出最高效
- Speckit的多阶段流程消耗适中
- Superpowers的多Subagent模式消耗较高
- OMO的多模型并行消耗最大

### 6.3 选型决策树

```
START
  │
  ├─ 团队使用OpenCode?
  │   ├─ Yes → 任务复杂度是否极高（多文件/多步骤/多角色）?
  │   │         ├─ Yes → OMO（最强多Agent能力）
  │   │         └─ No → OpenSpec + Superpowers组合
  │   └─ No → 团队使用Claude Code/Cursor?
  │             ├─ Yes → 是否需要强制TDD和最高代码质量?
  │             │         ├─ Yes → Superpowers
  │             │         └─ No → OpenSpec
  │             └─ No → 使用GitHub Copilot/其他助手?
  │                       ├─ Yes → OpenSpec（最广泛兼容）
  │                       └─ No → Speckit（结构化治理）
  │
  ├─ 项目类型?
  │   ├─ 从零开始（Greenfield）→ Speckit或Superpowers
  │   └─ 现有系统（Brownfield）→ OpenSpec
  │
  ├─ 团队规模?
  │   ├─ 1-5人 → OpenSpec或Superpowers
  │   ├─ 5-20人 → OpenSpec或Speckit
  │   └─ 20+人 → Speckit（Constitution治理）
  │
  ├─ 代码质量要求?
  │   ├─ 极高（金融/医疗/航空）→ Superpowers + Speckit
  │   ├─ 高（企业级应用）→ OpenSpec + TDD Schema
  │   └─ 中等（内部工具/原型）→ OpenSpec
  │
  └─ Token预算?
      ├─ 紧张 → OpenSpec（最高效率）
      ├─ 中等 → Speckit或OpenSpec
      └─ 充足 → OMO或Superpowers
```

### 6.4 组合使用策略

实践中，许多团队采用**组合策略**来发挥各工具的优势：

**OpenSpec + Superpowers**：OpenSpec管理规范变更（"写什么"），Superpowers管理实现执行（"怎么做"）。通过OpenSpec的TDD Schema，可以将Superpowers的TDD强制机制融入规范流程。

**OpenSpec + OMO**：OpenSpec提供规范的变更管理和审计链，OMO提供强大的多Agent执行能力。在OpenCode环境中，两者可以无缝协作——OpenSpec定义"做什么"，OMO的ultrawork执行"怎么做"。

**Speckit + Superpowers**：Speckit提供项目级治理和Constitution，Superpowers提供任务级执行质量保障。这种组合适合需要同时满足治理要求和代码质量要求的大型项目。

**渐进式采用路径**：团队可以从小处开始——先用OpenSpec建立轻量级规范实践，随着项目复杂度增加引入Superpowers的TDD执行，最后在需要时升级到OMO的多Agent编排。

---

## 7. 选型建议

### 7.1 按团队规模选型

**个人开发者（1人）**：
- **首选OpenSpec**：轻量级、低学习成本、跨平台兼容，个人开发者可以快速建立规范习惯而不增加过多 overhead。
- **备选Superpowers**：如果使用Claude Code且对代码质量有极高要求，Superpowers的自动化TDD和审查机制可以弥补个人审查的不足。

**小型团队（2-10人）**：
- **首选OpenSpec**：Delta Spec系统天然支持并行开发，避免多人修改同一规范文件的冲突。轻量级流程不会拖慢小团队的迭代速度。
- **备选Speckit**：如果团队成员经验差异较大，或需要统一的项目标准，Speckit的Constitution和模板可以提供必要的结构。

**中型团队（10-50人）**：
- **首选Speckit**：Constitution治理机制在中型团队中价值凸显，确保所有子团队遵循统一标准。七阶段流水线为角色分工提供了清晰边界。
- **备选OpenSpec + Superpowers组合**：如果团队使用多种AI助手，OpenSpec的跨平台兼容性使其成为规范管理的统一层，Superpowers则为使用Claude Code的子团队提供质量保障。

**大型团队（50+人）**：
- **首选Speckit**：Constitution的"宪法权威"在大型组织中至关重要，防止标准在各部门间分化。编号化特征管理和阶段门控为复杂协调提供了结构。
- **OMO用于核心复杂项目**：对于跨部门的大型重构或新系统建设，OMO的多Agent编排能力可以协调多个专家团队的协作。

### 7.2 按项目类型选型

**Greenfield项目（从零开始）**：
- **Speckit**："从零开始就做好"的理念与Greenfield项目完美契合。Constitution确立项目原则，七阶段流水线确保每个功能都经过充分规划。
- **Superpowers**：如果团队使用Claude Code，Superpowers的强制TDD可以从第一天起建立测试文化。

**Brownfield项目（现有系统演进）**：
- **OpenSpec**：Delta Spec系统是Brownfield项目的杀手级功能。无需重写整个系统规范，每次变更只需描述差异。
- **避免Speckit**：Speckit的Greenfield导向在棕地项目中可能导致"规范与代码脱节"的问题。

**快速原型/MVP开发**：
- **OpenSpec（Rapid Schema）**：快速迭代模式允许跳过不必要的文档步骤，同时保留核心的规范对齐价值。
- **避免Speckit和OMO**：完整的流程和重型架构会显著拖慢原型开发速度。

**关键任务系统（金融/医疗/航空）**：
- **Superpowers + Speckit**：Superpowers的强制TDD和审查机制确保代码质量，Speckit的Constitution和审计链满足合规要求。
- **OpenSpec（ADR Schema）**：如果需要架构决策记录，OpenSpec的spec-driven-with-adr Schema提供了完整的决策追溯能力。

### 7.3 按技术栈和平台选型

**Claude Code用户**：
- **Superpowers**：原生为Claude Code设计，Subagent驱动开发体验最佳。
- **OMO**：如果使用OpenCode，OMO完整兼容Claude Code的所有功能。
- **OpenSpec**：通过`/opsx:`命令集集成，体验良好。

**Cursor用户**：
- **OpenSpec**：Cursor的原生集成支持`/openspec-proposal`等命令。
- **Superpowers**：Cursor支持Subagent，但体验略逊于Claude Code。

**GitHub Copilot用户**：
- **OpenSpec**：通过`.github/prompts/`集成，是Copilot用户的最佳选择。
- **Speckit**：同样支持Copilot，但流程更重。

**OpenCode用户**：
- **OMO**：OMO是OpenCode的"官方级"增强插件，ultrawork模式提供了无与伦比的自主执行能力。
- **OpenSpec**：OpenSpec也支持OpenCode，适合作为轻量级规范层。

### 7.4 按预算选型

**Token预算紧张（个人/初创公司）**：
- **OpenSpec**：单Agent模式、轻量输出（~250行）、无API密钥需求，成本最低。
- **避免OMO和Superpowers**：多Agent/多Subagent模式消耗大量Token。

**Token预算中等（成长型公司）**：
- **OpenSpec + Speckit**：OpenSpec用于日常变更，Speckit用于关键功能的严格治理。
- **Superpowers**：如果团队规模小且使用Claude Code，Superpowers的质量回报值得投入。

**Token预算充足（大型企业）**：
- **OMO**：多模型并行虽然消耗大，但对于复杂任务的效率提升显著。
- **Superpowers + Speckit**：组合使用覆盖规范治理和代码质量两个维度。

---

## 8. Coding Agent发展趋势与SDD未来展望

### 8.1 2026年Coding Agent的关键趋势

2026年被业界广泛认为是"AI Agent元年"，Coding Agent领域呈现出以下关键趋势：

**从单Agent到多Agent团队的转变**：2026年2月，Claude Code推出Agent Teams、Codex CLI增加并行Agent、Windsurf支持5个并行Cascade Agent、Grok Build支持8个同时Agent。多Agent协调从实验性功能变为所有主流工具的标配。这一转变的根本原因在于底层模型能力的跃升——Agent能够在长自主会话中保持连贯行为，而Git WorkTree提供了安全的并行编辑隔离。

**长运行Agent（Long-Running Agents）**：早期Agent处理的是几分钟内完成的离散任务（修复Bug、编写函数）。到2026年，Agent能够连续工作数天甚至数周，从高层规范构建完整应用和系统，人类只需在关键决策点提供战略监督。Rakuten的工程师测试显示，Claude Code可以在7小时内自主完成vLLM（1250万行代码）中特定激活向量提取方法的实现，准确率达到99.9%。

**角色转型：从实现者到编排者**：工程师的价值贡献正在从编写代码转向系统架构设计、Agent协调、质量评估和战略问题分解。主要人类角色变为编排编写代码的AI Agent、评估其输出、提供战略方向并确保系统为正确利益相关者解决正确问题。掌握编排能力的工程师可以同时推进多个功能的开发，应用其判断力的范围远超个体实现时代。

**MCP（Model Context Protocol）成为互操作标准**：MCP在2026年被至少5个主要AI客户端采用，成为Agent与外部工具、数据库、API交互的标准协议。这使得SDD工具可以与CI/CD、项目管理、监控系统等企业基础设施深度集成。

**自主测试和维护Agent**：70%的常规维护任务（依赖更新、Lint修复、测试生成）已由自主Agent处理。Agent能够观察应用变化并自动生成相关测试、检测未覆盖代码路径、自我修复失败测试、优化测试套件。

### 8.2 SDD的演进方向

基于上述趋势，SDD在未来2-3年将呈现以下演进方向：

#### 8.2.1 从"规范优先"到"规范即代码"

当前的SDD实践中，规范（Markdown文件）和代码（源码文件）仍是两个独立的工件。未来，规范将逐步"可执行化"——规范文档不仅是人类和AI的参考，更是可以直接验证和执行的"活契约"。具体表现为：

- **规范直接生成测试**：Given-When-Then场景自动转换为可执行测试用例，规范更新时测试同步更新。
- **规范驱动接口契约**：API规范（如OpenAPI）直接从功能规范派生，接口变更必须回归规范。
- **规范即类型系统**：高级类型系统的约束直接从规范中提取，编译器在编译时验证实现是否符合规范。

Speckit的"Specifications don't serve code, code serves specifications"理念将成为技术现实。

#### 8.2.2 多Agent协作的规范编排

随着多Agent成为标配，SDD需要扩展到"多Agent间的规范协调"：

- **规范分配**：主规范自动拆解为子规范，分配给不同的专家Agent。
- **规范合并**：并行开发的Agent完成后，其子规范自动合并为主规范，冲突由编排Agent解决。
- **跨Agent规范验证**：一个Agent的实现变更自动触发相关Agent的规范合规性检查。

OMO的Team Mode和Superpowers的Subagent驱动开发是这一方向的早期实践，但未来的规范编排将更加自动化和智能化。

#### 8.2.3 自适应规范流程

当前的SDD工具（Speckit除外）仍要求团队选择固定的工作流程。未来，SDD工具将根据项目特征、团队习惯和变更复杂度**自适应地调整流程**：

- **小改动自动简化**：Bug修复自动跳过完整规划阶段，直接进入Task + Implement。
- **大改动自动增强**：架构变更自动激活额外的风险评估和架构评审阶段。
- **团队习惯学习**：系统学习团队的规范书写习惯和审查偏好，逐渐个性化流程。

OpenSpec的Schema系统为这种自适应提供了技术基础，未来可以通过AI分析自动推荐最优Schema。

#### 8.2.4 规范的知识图谱化

随着系统规模增长，扁平的Markdown规范文件将难以管理。未来，规范将**知识图谱化**——功能需求、架构决策、接口契约、数据模型等规范元素将以图谱节点形式存储，相互之间的关系以边表示。这将带来：

- **影响分析自动化**：变更一个需求时，自动识别所有受影响的相关规范和实现。
- **规范导航可视化**：通过图谱可视化浏览系统规范，而非在文件夹中翻找Markdown文件。
- **规范推理**：AI可以对规范图谱进行推理，回答"如果修改X，Y和Z会受到什么影响？"等复杂问题。

OpenSpec的"Living Architecture"讨论和Delta Spec的合并机制为这种演进提供了过渡路径。

#### 8.2.5 跨项目规范复用

在微服务架构和多项目组织中，相似的功能规范被重复书写是常见痛点。未来，SDD工具将支持**跨项目规范复用**：

- **规范库（Spec Library）**：组织级的规范组件库，如"用户认证规范"、"支付流程规范"等可被多个项目引用。
- **规范继承**：项目规范继承自组织基础规范，只需描述差异部分。
- **规范市场**：开源社区共享通用领域规范（如电商、社交、金融），团队可以直接引用并适配。

Speckit的Constitution机制可以扩展为组织级的"规范宪法"，OpenSpec的Delta Spec机制天然适合描述"相对于标准规范的差异"。

### 8.3 挑战与风险

SDD的快速发展也带来了一系列挑战：

**规范漂移（Spec Drift）**：尽管SDD强调规范优先，但在时间压力下，团队可能直接修改代码而忘记更新规范，导致规范与实际实现脱节。未来的SDD工具需要自动检测规范漂移并提供修复建议。

**规范过度工程（Over-Specification）**：过度详细的规范可能限制AI的创造性问题解决能力，或在需求不确定时导致大量返工。SDD工具需要智能判断"何时足够详细，何时保持模糊"。

**工具碎片化**：当前SDD生态存在多种不兼容的工具和方法论，团队选择和学习成本较高。行业可能需要标准化组织（如W3C或OMG）来推动SDD标准的统一。

**安全与合规风险**：自主Agent可以访问代码库、执行命令和提交代码，带来了新的安全风险——恶意Agent或被劫持的Agent可能造成严重破坏。SDD工具需要内置安全机制，如规范变更的人工审批、Agent权限的细粒度控制等。

### 8.4 2027-2028年展望

根据arXiv 2026年6月的研究论文《How AI Agents Are Fundamentally Restructuring the Software Paradigm》，Agent工程将经历四个演进阶段：

**Stage I: 工具增强（2023-2025）**：Agent在人类主导的工作流中充当助手，人类负责问题分解、架构设计和正确性验证。

**Stage II: 单任务自主（2025-2027）**：Agent开始拥有从规范到部署的完整任务所有权，人类从"执行者"转变为"指定做什么和验证做了什么"。

**Stage III: 多Agent团队（2026-2029）**：专业Agent作为团队协调，模仿人类工程组织。"产品经理Agent"将业务需求转化为技术规范；"架构师Agent"设计系统结构；"开发者Agent"实现组件；"QA Agent"测试和验证。共享记忆和可观测性成为关键基础设施。

**Stage IV: 自进化生态系统（2028+）**：Agent获得改进自身架构、为新问题域生成专门子Agent、无需人工干预适应环境变化的能力。此时"软件"与"Agent"的界限完全消融——Agent就是系统，系统持续进化。人类参与转向元级治理：设定伦理边界、定义价值函数、确保对齐。

在这一演进路径中，SDD将从"人类编写规范指导AI"转变为"AI生成规范人类审批"，最终演变为"AI自主维护规范并确保实现合规"。规范将从"开发辅助文档"进化为"系统的基因代码"——定义系统是什么、能做什么、不能做什么的根本法则。

---

## 9. 结论

OpenSpec、Speckit、Superpowers和OMO代表了2026年SDD生态的四种不同哲学路径，它们并非竞争关系，而是面向不同场景、不同团队、不同需求的互补选择：

- **OpenSpec**以"轻量级变更管理"为核心，通过Delta Spec系统和流体工作流，为现有代码库的演进提供了最小阻力的规范实践路径。其"Brownfield优先"的设计哲学使其成为大多数已运行项目的首选。

- **Speckit**以"结构化治理"为核心，通过Constitution和七阶段流水线，为从零开始的项目和大型团队提供了严格的规范生命周期管理。其"规范即权威"的理念适合对代码质量和一致性有极致要求的场景。

- **Superpowers**以"工程质量执行"为核心，通过Skill自动触发和Subagent驱动开发，将TDD和代码审查提升到了自动化的新高度。其"强制纪律"的设计理念适合追求工程卓越的技术团队。

- **OMO**以"多模型智能编排"为核心，通过Discipline Agents和Team Mode，将单一AI助手扩展为协调的虚拟开发团队。其"The Right Brain for the Right Job"的理念适合处理最复杂的工程挑战。

对于绝大多数团队，**建议从OpenSpec开始**——它提供了最低的学习曲线和最高的灵活性，使团队能够快速体验SDD的价值。随着项目复杂度的增长，可以逐步引入Superpowers的TDD执行（如果使用Claude Code）或Speckit的治理框架（如果团队规模扩大）。对于已经在使用OpenCode且面临极其复杂任务的团队，OMO提供了终极的多Agent协作能力。

展望未来，随着Coding Agent从"工具"进化为"团队成员"再进化为"自主团队"，SDD将从"最佳实践"转变为"必要条件"。规范不仅是人类与AI的协作契约，更是AI团队内部协调的根本依据。在这一趋势下，今天的SDD工具选择不仅影响当前的开发效率，更决定了团队在未来AI原生开发范式中的竞争力。

---

## 参考文献

1. GitHub. "Spec-driven development with AI: Get started with a new open source toolkit." GitHub Blog, 2025.
2. Fission AI. "OpenSpec: Spec-driven development (SDD) for AI coding assistants." GitHub Repository, 2025.
3. Jesse Vincent. "Superpowers: Skills for Claude Code." GitHub Repository, 2025.
4. code-yeongyu. "Oh My OpenAgent: Multi-model agent orchestration harness." GitHub Repository, 2025.
5. Den Delimarsky. "Spec-driven development with AI." Den Delimarsky Blog, 2025.
6. arXiv. "Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants." arXiv:2602.00180, 2026.
7. arXiv. "How AI Agents Are Fundamentally Restructuring the Software Paradigm." arXiv:2606.05608, 2026.
8. Anthropic. "2026 Agentic Coding Trends Report." Anthropic Resources, 2026.
9. Gartner. "40% of enterprise applications will feature task-specific AI agents by end of 2026." Gartner Predictions, 2026.
10. Google Cloud. "AI Agent Trends 2026 Report." Google Cloud, 2026.

---

*报告完成日期：2026年6月*
