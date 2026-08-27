# case-template：新案例骨架（p2s-kit v0）

> 用法：`cp -r templates/case-template cases/<你的案例名>`，然后按三步初始化（见下）。
> 结构与规约依据 method/10（各阶段签收门）与 method/16（review/ 目录规范）。

## 目录结构与放置物

| 目录 | 放什么 | 依据/模板 |
|---|---|---|
| `raw/` | 原始需求存档（S0，不可变）+ 需求登记表（S1，AI 预填→人工确认） | T1-需求登记表 |
| `review/` | 人工评审界面（S3–S4 签注与决策发生地） | T3-翻译审计表 / T4-人工决策记录；命名 E/V/G 前缀（16 号 §2） |
| `formal/` | 概念模型 puml+注解、流程线 puml、绑定清单、Z3 规则集 | method/13（词表）/ §7（绑定清单） |
| `reports/` | 检查台账（只追加）+ 案例报告 | T5-检查台账 |
| `regression/` | 决定性基线（首转后固化 sha256） | method/15 §2 |

## 初始化三步

1. `raw/` 放入原始需求与 T1 登记表（S0–S1）；
2. `formal/` 建概念模型 puml（首版翻译后）→ 跑 `python tools/scripts/puml2owl.py <puml> <out前缀>` → 把首转产物复制入 `regression/baseline/` 作为决定性基准；
3. `review/` 按 T3/T4 复制建 E30-翻译审计 / E41-人工决策记录，V00-INDEX 写本次待办。

环境就绪验证：`python tools/scripts/check_env.py --smoke`（应 ALL_PASS）。

各目录内 README 详述该目录规约。
