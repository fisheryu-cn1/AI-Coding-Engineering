# review-pi 评估集：代码评审 agent 标注案例（cases.jsonl）

从本仓库 `design/kb-app/` 历史 code review 报告（10/12/14/17 号）构造的"代码评审 agent"评估标注集。
每个案例 = 一个**带缺陷的代码状态**（git 提交，作为评审输入）+ **期望发现的缺陷标注**（来自真实评审报告并被修复提交证实）。

- 案例文件：`cases.jsonl`（16 条，每行一个 JSON）
- 构造日期：2026-08-17
- 缺陷来源：真实多轮人机评审 + 独立复核 + 修复闭环，非合成标注
- **语料质量注记（notes/07）**：三个案例项目的开发均采用 A-B 交叉评审环（模型 A 写 → 模型 B 评审 → A 复核确认 → 修复 → B 复审），本标注集全部条目经 B 发现 + A 复核 + 修复提交三重验证

## 0. 语义归属核定（2026-08-18 第 4 场，f62f287 锚点 11 案例）

对 run2/run3（skill v2）意见卡的人工语义核定结论（区别于启发式关键词口径）：

| 案例 | 语义归属 | 核定依据 |
|---|---|---|
| R-1/R-2/R-3/R-4/R-5/R-7 | **命中**（run2/3 均显式意见） | 实录第 3 场 §3.2 |
| **R-10** | **命中**（run2/3 均显式 P1："coalesce 把 Section PK 错配成 doc_id，UI 端 src/dst 全错"） | 本场核定——v1 仅"可移植性风险"半命中，v2 机械化键清单后升级为键序语义缺陷 |
| R-13 | 半命中 | RR-8 v2 清单缺 layout 项（v3 已补） |
| **R-8** | **未命中** | run2/3 的关键词命中为 regex 误配；`kb serve viz` 只捕获 uvicorn 缺失、fastapi 缺失裸 ImportError 未被发现 → skill v3 在 RR-7 增"可选依赖 try/except 兜底完备性"检查点 |
| **R-12** | **未命中** | RR-8 v2 只做正向检查（引用文件存在）；R-12 是反向缺陷（graph.js 调用 app.js 定义而页面缺引）→ skill v3 增反向依赖检查（调用图 vs script 清单） |

**语义严格口径（skill v2）＝ 7/11**；启发式 11/11 为上界。R-8/R-12 修复效果待 skill v3 复测。

### 补充核定（2026-08-18，run4/run5，skill v3）

| 案例 | 语义归属 | 核定依据 |
|---|---|---|
| **17/R-12**（于 6e1abeb 锚点验证） | **命中**（v3 RR-8 反向检查首战） | run4 P1："graph.html 未引入 app.js，fetchJson 三处调用 ReferenceError，三功能静默失效"——v2 盲区在 v3 修复 |
| 17/F-1 | **命中** | run4 P1：api_key 读取后未透传 kwargs；且发现 milestone-log 登记"已落地"失实 |
| 17/F-2、17/F-3 | **命中** | run4 同一条 P1：无总输入预算 + max_tokens 默认 1024 被 think 吃 |
| 14/N-3b | **命中** | run5 P1：lock.py POSIX-only 头注 + 全测试树零 skipif（Windows 242 项无法通过） |
| 14/N-3a | **未命中** | run5 未复现期望的连接泄漏缺陷（启发式关键词命中为正则误配）；但在同一问题域（测试套件登记状态）发现 README"154 项"与实测 242 项不符——"未复现期望缺陷、但同一问题域有真发现"是否计部分分（期望意见粒度）留 P2 阶段评审讨论 |

**16 案例全景基线**：语义严格 11/16（69%）、含半命中 11.5/16（72%）；启发式 16/16（上界）。R-8 的 v3 修复待 f62f287 复跑验证。

> **工具口径补充（2026-08-19 第 8 场）**：评估工具 v2 另提供**签名口径**（案例 files 与意见溯源的文件末两段键重合，机械中间口径）——当前各锚点最佳卡合计 14/16；与语义终审的差异项（run8 的 R-4、run4 的 F-1）均为"意见溯源未列案例对象文件"所致，已反哺为意见卡溯源规范性观察项。三口径（启发式上界 > 签名 > 语义终审）可用 `scripts/score_review.py score` 同工具复算。

## 1. Schema（每行字段）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | str | `<报告号>/<条目号>`，如 `17/R-1`、`17/F-1`、`14/N-3a` |
| `source_report` | str | 来源评审报告路径（仓库相对），如 `design/kb-app/17-M5M6代码评审报告.md` |
| `fix_commit` | str | 修复该缺陷的提交全 hash（fix diff 即"标准答案 diff"） |
| `review_base` | str | fix_commit 的**父提交**全 hash——评审输入锚定的代码状态（缺陷尚在） |
| `files` | list[str] | 相关文件路径列表（仓库相对，取自 fix diff 与报告证据行号） |
| `expected_finding` | str | 期望评审意见（一句话，含缺陷本质；必须能仅由 review_base 状态的代码观察推出） |
| `severity` | str | 报告中的级别：P0/P1/P2/P3（17 号 R 系列与 F 系列按报告标注；14 号 N 系列按复核记录标注） |
| `evidence` | str | 报告中的 file:line 或章节引用 |

## 2. 案例分布

| review_base | fix_commit | 来源 | 案例 | 级别 |
|---|---|---|---|---|
| `f62f287` | `3ffebf0` | 17 §8.2/§9.2 | R-1, R-2, R-3, R-4, R-5, R-7, R-8, R-10, R-11, R-12, R-13（11 条） | P0×3, P1×5, P2×1, P3×2 |
| `6e1abeb` | `71a498f` | 17 §5 | F-1, F-2, F-3（3 条） | P0×3 |
| `e7c9aa9` | `63dae68` | 14 §10 | N-3a, N-3b（2 条） | P3×2 |

合计 16 条：P0×6 / P1×5 / P2×1 / P3×4。

三条锚点链均已逐一验证：缺陷在 review_base 可观察（git show 实读代码），在 fix_commit 被修复（diff 实读核对）。

## 3. 构造方法

1. 通读 `design/kb-app/10/12/14/17` 四份评审报告，摘出**代码级**且报告"修复记录"章节声称已修的条目。
2. 在 git 历史中定位修复提交：`git log --oneline --all` + `git show <fix> --stat` 逐文件比对报告的修复描述。本仓库 kb-app 的关键修复提交：
   - `3ffebf0`：17 号复核 R-1~R-13 修复闭环（tombstone 生命周期 + 图读墓碑过滤 + 图谱页交互）；
   - `71a498f`：17 号 §5 验收发现的 F-1~F-3（api_key 透传 / 抽取输入上界 / extract_max_tokens）；
   - `63dae68`：14 号 §10 复核的 N-2/N-3（Windows 测试兼容 + Python 钉 3.12）；
   - `e7c9aa9`：M2–M4 全部代码（含 10/12 号与 14 号 §5/§9 的修复）以单个 squash 提交入库。
3. 案例评审输入锚定在 fix_commit 的父提交（`git rev-parse <fix>^`），并用 `git show <review_base>:<file>` 实读代码确认缺陷状态可观察、行号证据成立；再读 fix diff 确认修复与报告描述一致。
4. 质量门槛：`expected_finding` 必须**仅由 review_base 状态的代码**（含文件缺失、import 关系、SQL/配置语义）即可推出，不依赖运行时或外部环境知识。不满足者放弃（见 §4）。

## 4. 放弃条目清单及原因

| 范围 | 条目 | 放弃原因 |
|---|---|---|
| 10 号（M2）全部代码级条目 | P0-1/P0-2、P1-1/P1-2、P2-1~P2-4、P3 系列 | M2–M4 代码以 squash 提交 `e7c9aa9` 一次性入库且**已含全部修复**；其父提交 `a53503f` 不含 M2 任何代码——缺陷状态在 git 历史中不存在，无法锚定 |
| 12 号（M3）全部代码级条目 | P1-1~P1-6、P2-1~P2-5、D-1~D-5 | 同上：修复发生在 `e7c9aa9` 之前的工作树，无缺陷态提交 |
| 14 号 §5/§9 全部条目 | P1-1/P1-2、P2-1~P2-6、P3-1/3/4/5/6 | 评审对象为"工作树未提交状态"，修复后随 `e7c9aa9` 入库（已验证该提交中 `scripts/recall_sweep.py` 即拆行后版本），无缺陷态锚点 |
| 14 号 §10 N-2 | `.python-version` 3.11→3.12 | 缺陷本质是 Python 3.11 捆绑 SQLite 3.38.4 的 FTS5 非 ASCII LIKE 行为，属环境事实，无法由代码状态观察推出（违反质量门槛） |
| 17 号 R-6 | 验收留档空心化 | 非代码缺陷（缺 `.playwright-mcp/` 截图等佐证文件），无法由代码观察 |
| 17 号 R-9 | 增量陈旧（MENTIONS 残边等） | 维持 P3 登记随 P1 处置，**未修复**，无修复提交可锚定 |
| 17 号 O-1/O-2 | 推理模型空响应 / summary_max_tokens 偏小 | 遗留观察登记未修，无修复提交；O-2 亦依赖运行时暴露 |

## 5. 如何重现评审输入

```bash
cd D:/Users/Yu/Documents/Coding/AI-Coding-Engineering

# 1) 查看某案例的评审输入状态（缺陷尚在）
git show <review_base>                              # 提交元信息
git show <review_base>:code/kb-app/src/kbapp/graph/ladybug_store.py   # 指定文件全文

# 2) 标准答案 diff（该案例的修复）
git show <fix_commit> -- <files>

# 3) 不切分支的只读检出走查
git worktree add ../kbapp-review-case f62f287       # 17/R-* 系列
git worktree add ../kbapp-review-case 6e1abeb       # 17/F-* 系列
git worktree add ../kbapp-review-case e7c9aa9       # 14/N-* 系列
# 用完：git worktree remove ../kbapp-review-case
```

评审 agent 的输入 = review_base 状态下的 `files`（或整个 kb-app 源码树），期望输出应命中 `expected_finding` 所述缺陷；评分可用 fix_commit diff 做定位比对（文件 + 缺陷语义双匹配）。

## 6. 已知限制

- 三条锚点均为单点提交，同 base 的 11 个案例（17/R-*）共享 `f62f287`，相互不独立；若需要独立采样可按案例只喂 `files` 列出的文件。
- `17/R-13` 的 expected_finding 只覆盖缺陷群中在 review_base 代码可直接观察的子集（缺 layout、无视口管理）；该条目其余子缺陷（render 竞态、brush 选中态被清空）在修复过程中才引入/暴露，无法在 review_base 观察。
- `14/N-3a`/`N-3b` 为测试代码缺陷（平台兼容），severity 按报告 P3，适合作低权重案例。
