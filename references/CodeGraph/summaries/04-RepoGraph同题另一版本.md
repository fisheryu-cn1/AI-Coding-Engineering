# 论文摘要：RepoGraph 同题另一版本（arXiv v2 排版对照）

> **原论文标题**：RepoGraph: Enhancing AI Software Engineering with Repository-Level Code Graph
> **完整 PDF 文件名**：`RepoGraph_Enhancing_AI_Software_Engineering_with_Repository-level_Code_Graph (2).pdf`
> 作者 / 年份 / 出版：Siru Ouyang et al.（同 `03-RepoGraph仓库级代码图谱增强AI软件工程.md`）；2025-03-18 arXiv:2410.14684v2
> 摘要类型：Agent 设计参考 + 内容索引（与 ICLR 会议版对偶）
> 生成日期：2026-08-12

## 1. 适用场景

- 当你拿到的是 **arXiv 预印本（v2，2025-03）**而不是 ICLR 会议版时——本摘要用于在两者之间对齐。
- 复现 RepoGraph 时，需要**对照两份 PDF 的图/表编号**差异（arXiv 版与 ICLR 版的 Figure 2 / Figure 10 / Table 4 排版略不同）。
- 需要引用 arXiv 编号（2410.14684v2）而不是会议版时的合规参考。
- 内容层面与 `03-` 完全等价；适合在阅读时**只读其一**的策略下作"两份之一"的选择记录。

> 锚点：PDF 首页 arXiv 元数据（2410.14684v2，18 Mar 2025）。

## 2. 主要观点与方案

### 2.1 与会议版的差异（轻量 diff）

- **作者列表、机构、摘要、§1–§5 正文**完全一致；arXiv 版在 `REPOGRAPH` 之间多打了若干空格（如 `R EPO G RAPH`），是 PDF 排版问题不是内容差异。
- **Figure 2**：arXiv 版把"仓库图构造（a）/ 程序化框架集成（b）/ 智能体框架集成（c）"展开在双栏右侧；ICLR 版同样的图以单栏形式呈现。**图本身相同**。
- **Table 1**（与同类工作比较）：arXiv 版与 ICLR 版表格内容完全一致（行：DraCo / Aider / RepoUnderstander / CodexGraph / RepoGraph，列：Line-level / File-level / Repo-level）。
- **Table 2**（SWE-bench-Lite 主结果）：数字、列结构完全一致。
- **Table 4**（消融）：两份 PDF 的消融项一致。
- **新增差异点**：arXiv v2 标注了 `arXiv:2410.14684v2 [cs.SE] 18 Mar 2025`，ICLR 版无 arXiv 编号水印。
- **行数差异**：arXiv v2 文本提取约 1,464 行；ICLR 版约 1,635 行（多出附录文字/参考文献）。

### 2.2 内容速览（与 `03-` 等价）

- 核心方案：以代码行为节点、以 invoke/contain 为边的仓库级图谱；`search_repograph(term)` 取 k-hop ego-graph；作为 plug-in 接入 RAG / Agentless / SWE-Agent / AutoCodeRover。
- 主要结果：SWE-bench-Lite 平均相对 +32.8%；跨 CrossCodeEval 同样有效。

> 锚点：PDF 首页；Figure 2；Table 1/2/4。

## 3. 达到的效果

| 度量 | 结果 | 锚点 |
|---|---|---|
| SWE-bench-Lite 平均改进 | +32.8% | Table 2 |
| 与会议版内容一致性 | 100% 正文；附录文字略有出入 | PDF 全文 diff |
| 与会议版排版差异 | 仅 Figure/Table 位置 + arXiv 编号水印 | 首页、Figure 2 |
| 适用复现 | arXiv v2 可作为 ICLR 版等价物 | §1–§5 |
| 不适用场景 | 若必须引用会议版（带 ICLR 页码）需另取版本 | 引用规范 |

> 锚点：两份 PDF 全文对照；arXiv 编号 v2 时间戳。

## 4. 参考项目 / 资源

| 类别 | 链接 / 说明 |
|---|---|
| 论文 | arXiv:2410.14684v2（cs.SE，18 Mar 2025） |
| 代码 | https://github.com/ozyyshr/RepoGraph |
| 会议版对应摘要 | `03-RepoGraph仓库级代码图谱增强AI软件工程.md` |
| 内容等价性结论 | 选其一即可；引用时优先 arXiv 编号或 ICLR 2025 |

> 锚点：PDF 首页；参考文献。

## 5. 一句话索引（给 Agent 用）

> 本 PDF 与 `03-` 的 ICLR 版**内容完全等价**，仅排版与 arXiv 编号水印不同——读其中一份即可，若要引用请用 `arXiv:2410.14684v2 (ICLR 2025)`。
