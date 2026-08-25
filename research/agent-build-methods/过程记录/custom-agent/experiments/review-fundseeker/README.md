# review-fundseeker 工作区（P3：留出项目的评审冷启动）

> 定位（决策清单 §D）：fundseeker 是**留出项目**——从未参与评审 skill 的任何迭代，用于检验规则集的真实泛化能力。本工作区管理 P3 的评估集与运行记录；skill 零适配部署到目标仓库（拷贝 `../review-pi/.pi/skills/code-review/` 原样至 `D:\Users\Yu\Documents\Coding\FundSeeker\.pi\skills\`，不修改任何内容）。
> 建立：2026-08-20（第 18 场）。

## 1. 当前状态与阻塞

- **git 历史待恢复**：本地目录 `D:\Users\Yu\Documents\Coding\FundSeeker` 无 `.git`（zip 解压而来）。已就地 `git init` 并配置 remote（github.com/fisheryu-cn1/fundseeker）；**网络恢复后执行 `git fetch origin --unshallow` 或 `--depth=100` 即可取回历史**——锚点状态与修复 diff 全部经 `git show <hash>:<path>` 读取，不 checkout、不动工作树。
- 评估集 `cases-fs.jsonl` 的 expected_finding 已可从工作树内两份报告起草（见 §3）；`review_base`/`fix_commit` 哈希待 fetch 后回填。

## 2. 隔离设计（P3 专项核对）

- **research/AGENTS.md 不在注入路径**：pi 从 FundSeeker 目录启动，向上遍历不经过本仓库（不同树根）——第 16 场发现的注入通道天然不存在；仍按新规程带 `-nc`（批跑命令：`cd /d/Users/Yu/Documents/Coding/FundSeeker && pi -a -nc -p "<提示>"`）。
- 目标仓库自有 `CODEBUDDY.md`（agent 说明文件）——pi 不会自动注入（只认 AGENTS.md/CLAUDE.md），评审者可将其作为被评审仓库的合法文档阅读。
- 禁读清单（提示词纪律）：锚点内既有评审报告（docs/ 下两份评审报告与其修复记录）、reviews/、本工作区目录；一切内容读取经 `git show <锚点>:<路径>`。

## 3. 评估集草案（源自《持仓相似性-CLI与调度-v1.01-评审报告》，复审报告证实修复）

| 草案号 | 缺陷（expected_finding 草案） | 级别 |
|---|---|---|
| FS-1 | cron 脚本 `fundseeker_similarity_cron.sh` 的 `START_DATE` 等必填参数未按文档示例兜底，直接运行报错（P0 阻塞） | P0 |
| FS-2 | OpenClaw 调度 YAML 示例沿用 cron 的同一参数缺陷（一致性偏离） | P1 |
| FS-3 | 设计文档 §3.3 `cluster` 输出关键字段表遗漏核心字段（文档-实现不一致） | P1 |
| FS-4 | `cmd_pipeline` 输出字段不完整 | P2 |
| FS-5 | cron 脚本缺少 shellcheck 验证 | P2/P3 |
| FS-6~9 | 其余 P2/P3 工程性问题（待从报告 §4 逐条展开） | P2/P3 |

- 三个修复锚点（05d66d3 / b3a0342 / c5ee3e3，P2 阶段评估时认定覆盖 RR-6/RR-7b 类缺陷）与上表的对应关系、以及第四份文档（docs/ver1.0 目录的更早评审）是否贡献更多案例——待 git 历史恢复后核对定稿。
- 复审报告另载一项"额外收益"发现（`--skip-cluster` 时 `k` 参数解析 bug，修复记录未声明）——闭环价值的又一实例（复审抓未声明项），记入 P3 观察材料。

## 4. P3 运行计划（首批）

1. git 历史恢复 → 评估集定稿（cases-fs.jsonl，锚点=各修复提交的父状态）；
2. **冷启动首轮**：skill v5 零适配，新规程（`-a -nc`、逐通道隔离），run-fs1；
3. **同模型多次运行投票对照**（对照分析 2-2 要求的基线臂）：同锚点 3 次聚簇执行（KV 缓存友好）；
4. 泛化检验清单观察（Vision-Sudoku 四类缺口模式在 fundseeker 上是否真实出现）；
5. 收敛速度度量（对照源项目迭代轮次）与阶段-模型性价比实验（notes/09 §2）。

## 5. 登记

- 工作区 README（本文件）；运行记录与工件按 review-pi 同命名约定放目标仓库 `reviews/`（随 run 拷回本工作区归档）；
- B3 迭代停止条件已补写（`../review-pi/.pi/skills/code-review/assets/rule-revision-worksheet.md` §4，2026-08-20）——P3 前置项清零。

## 6. 协议修正（2026-08-20，fs-run3 发现）：定位命令不得携带修复提交信息

`git show <fix> --stat` 默认输出提交信息与主题行——而修复提交的主题行往往直接陈述缺陷（如"add flock to prevent cron retry overlap"），构成**提示词指令自带的答案渗漏通道**（历次运行均存在；fs-run3 的证据公开引用了该信息而暴露此通道）。修正：变更地图定位一律改用 `git diff <fix>^ <fix> --stat`（仅文件与行数统计，无提交信息）。fs-run1/fs-run3 的命中数字标注"修复主题行经 --stat 可见"存疑注；后续补一次信息盲复跑（fs-run1b，用修正协议）以校准影响。

## 7. 真实修复应用（2026-08-20 启动，研究者授权：项目实际使用中，以实验确认缺陷做真实修复并复审）

> 定位：研究成果的**真实应用**——评审→修复→修复复审闭环在真实生产项目上走通；观测数据入研究（修复工作方法总结的素材，反哺 V1 人在回路总纲）。

- **第一步·存量核实**（哪些确认缺陷在当前 HEAD 仍存在；部分已被 b3a0342/05d66d3 历史修复消化）：初查发现 runner.py:630/635 仍有两处裸 `except Exception:`（吞错类候选）；`--holding-years` 上限、全失败退出码、多季度折叠等需逐项精查（下一场）。
- **修复范围原则**：只修经对比分析复核确认的真缺陷；数据模型级改动（如多季度折叠）单独评估风险；每项修复带最小测试。
- **复审**：修复提交后用 review-recheck 提示模板跑 B 复审（四档结论 + 回归检查），闭环工件按命名约定归档。
