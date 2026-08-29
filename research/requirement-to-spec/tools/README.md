# tools/：审核方法工具包

> v1（2026-08-29 固定）。全部位于 `scripts/`，确定性程序、零 LLM（语义摘要属 LLM 语义岗，不进判定）。
> **统一入口**：`python scripts/run_checks.py <case_dir> [--heavy]`——常规轻检查链五件一条命令（转换验证/状态机/规则/绑定闭包/执行队列），`--heavy` 加 HermiT 一致性。完整清单与用法见 `../method/19-审核方法总装.md` §3。

## 环境

- Python ≥3.10 + `pip install -r ../requirements.txt`（owlready2/pyshacl/rdflib/z3-solver；镜像备选见文件头注释）
- Java ≥17（仅 HermiT 需要，owlready2 自带引擎 jar）
- TypeScript 提取器需 typescript@**5.x**（7.x 断代），路径经 `P2S_TYPESCRIPT` 环境变量注入
- 就绪验证：`python scripts/check_env.py --smoke` → 应 ALL_PASS

## 脚本清单

| 脚本 | 一句话 | 依赖 |
|---|---|---|
| run_checks.py | 案例统一检查入口（轻链五件+可选 HermiT） | 下列各件 |
| puml2xmi.py / puml2owl.py | PlantUML 类图子集解析/→OWL+SHACL 确定性转换 | owlready2, rdflib |
| fsm_check.py | 状态机五性质（可达/共可达/终态封闭/无死锁/显式禁回） | 标准库 |
| check_model_bindings.py | 需求↔模型绑定三闭包（--id-regex 适配 FR 等编号体系） | 标准库 |
| check_doc_closure.py | 文档级五项（私造/形近变体/覆盖/验收映射/词表漂移/验收行 ID） | 标准库 |
| diff_models.py | 同骨架 puml 五维层间 diff（类/属性/枚举/关联/方法名） | puml2xmi |
| collect_review_actions.py | review/ 执行队列聚合（含裁决解锁与退回归组） | 标准库 |
| ast_extract_py.py | Python AST→PlantUML（标准库 ast，零依赖） | 标准库 |
| ast_extract_ts.cjs | TypeScript AST→PlantUML（typescript@5；P2S_TYPESCRIPT 注入） | typescript@5 |
| check_env.py | 环境检测+全组件冒烟 | 全部 |

## 规划中（R2+）

- pip 包化（p2s 命令行）；分歧度采样脚本（R4）；pre-commit 门禁（R5）；pi 适配器 skills（R3，plan/02 §4）。
