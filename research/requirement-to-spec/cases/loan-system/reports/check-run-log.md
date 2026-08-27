# 检查运行台账（check-run-log）

> **这是什么**：本项目 loan-system 案例全部机器检查与人工决策的证据流水账。**只追加不删改**。
> **怎么读**：每节 = 一次运行的完整原始输出 + 差异归因。第一次来？先读 `../../method/14-检查规程与人工决策指南.md`（各检查项含义/重跑命令/人工决策记录方法），再回来按时间序读证据。
> **当前状态速览**：HermiT 一致 ✅ / Z3 v3 双场景 ALL_PASS+幂等 ✅ / 决定性基线 sha256 已立（v2 基准）✅ / 绑定闭包检查 6 项 PASS ✅ / 流程线 fsm_check P1–P5 全 PASS ✅（负控四命中自证非空转）/ 已裁决 D-A ✅ / 待人工决策：D-B decision 弱化、C 类审计勾选——见指南"人工决策点"表。

> 全部证据为实际运行捕获。运行环境：Windows / Python 3.13 / Java 25 (Temurin)。

## Run-1 HermiT 一致性推理（concept.owl.rdf）

```
* Owlready2 * Running HermiT...
    java -Xmx2000M -cp D:\Program Files\Python313\Lib\site-packages\owlready2\hermit;D:\Program Files\Python313\Lib\site-packages\owlready2\hermit\HermiT.jar org.semanticweb.HermiT.cli.CommandLine -c -O -D -I file:///C:/Users/Yu/AppData/Local/Temp/tmp2nm94xhh
* Owlready2 * HermiT took 0.6619255542755127 seconds
* Owlready * (NB: only changes on entities loaded in Python are shown, other changes are done but not listed)
[RESULT] consistent=True
classes=18 individuals=12
LoanPurpose literals: ['renovation', 'education', 'travel', 'medical']
OrderStatus literals: ['active', 'approved', 'closed', 'draft', 'pending', 'rejected']
```

## Run-2 Z3 规则集（RULE-001 + Z1 默认阈值 60，双场景触达）

```
规则集一致性: sat
48分场景 -> 拒绝 可满足: True
72分场景 -> 通过 可满足: False   ← v1 脚本 BUG（score==48 事实未隔离，污染第二场景）
```

> **证据留痕价值实证**：v1 台账捕获的此异常，经定位为脚本自身缺陷（非规则矛盾）——恰为"转换确定+检查器确定⇒失败可追因"的演示。

## Run-2b Z3 v2（事实隔离修正后）

```
规则集一致性: sat | core(空=自洽): []
场景48分: 可满足=%s, 规则判定=拒绝(期望) -> True False
场景72分: 可满足=%s, 规则判定=通过(期望) -> True True
重复求解一致: True
```

> **[台账修订 r1 2026-08-27]** 本节至下节之间原本存在粘贴围栏错位：Run-2b 的空围栏、Run-3 标题重复两次、
> Z3 v2 输出与 puml2owl 输出互相嵌套。本修订仅做**围栏归位与小节归属重排**：全部证据行字符未改动；
> 下方两行当时手工占位未填的空值行照录（真实基线值即其下一行的 beb9… 值与再下节的 ee90… 汇总）。

## Run-3 puml2owl 决定性回归

```
OK: D:/Users/Yu/Documents/Coding/AI-Coding-Engineering/research/requirement-to-spec/cases/loan-system/formal/concept.owl.rdf（6 类/枚举, 2 关联）+ .shacl.ttl
概念模型产物 sha256（决定性基线）：
concept.owl.rdf  sha256:
concept.shacl.ttl sha256:
beb9e9338efacb8df01e925b2ad5425f2ef666f2329e6409d8bcc20bfeca6f99 *D:/Users/Yu/Documents/Coding/AI-Coding-Engineering/research/requirement-to-spec/cases/loan-system/formal/concept.owl.rdf
```

- `concept.owl.rdf` sha256: `beb9e9338efacb8df01e925b2ad5425f2ef666f2329e6409d8bcc20bfeca6f99`
- `concept.shacl.ttl` sha256: `ee90910b95dd9e45b74009fed8cf1ca7b8c95683adec43c0208ed0760bc9cef8`

## 附：决定性回归首验记录（补齐动作实况）

- 首次运行回归脚本即报 **DRIFT**：基线（手工复制的旧 v2.owl，51 triples，单行枚举修复前的代码产物）与重跑（63 triples）`isomorphic=False`。
- 处置：以当前代码重建基准后复验 **DETERMINISTIC**（sha256 一致）。
- 结论：①"同输入必同输出"在当前代码版本成立；②drift 检出的差异是**真实的语义漂移**（枚举字面量子类化前后），证明该脚本有能力拦截模型变更——正是 R5 门禁需要的性质。
* Owlready2 * Running HermiT...
    java -Xmx2000M -cp D:\Program Files\Python313\Lib\site-packages\owlready2\hermit;D:\Program Files\Python313\Lib\site-packages\owlready2\hermit\HermiT.jar org.semanticweb.HermiT.cli.CommandLine -c -O -D -I file:///C:/Users/Yu/AppData/Local/Temp/tmp4ippilzy
* Owlready2 * HermiT took 0.7079486846923828 seconds
* Owlready * (NB: only changes on entities loaded in Python are shown, other changes are done but not listed)
[RESULT] Run-4(裁决后重跑) consistent=True
classes=18 individuals=12
Z3 v2: PASS
baseline : 1bd6ca2108ceee7d9c99688fb340e5624a12660aa850c9f2f4290e2135d15189
rerun    : 1bd6ca2108ceee7d9c99688fb340e5624a12660aa850c9f2f4290e2135d15189
DETERMINISTIC

> **Run-4 归因**：触发原因=人工审计三项裁决回写（FLOW-002/RULE-004/FIELD-002，见 translation-audit-done.md）。模型结构未变（仅注释区），全链仍绿——D-A 决策闭环完成。

## Run-5 2026-08-27 Z3 v3 场景断言输出（触发原因：缺陷修复——%s 格式缺陷）

> v1/v2 的 `print('…=%s', x)` 漏格式化运算符导致 Run-2b/Run-3 记录中出现 `%s` 字面量（小瑕疵遗留项）。
> v3 改为期望表驱动断言（48→False / 72→True），并新增整链 ALL_PASS 判定行。语义结果与 v2 完全一致。

```
规则集一致性: sat | core(空=自洽): []
场景48分: 可满足=True, 规则判定(approved)=False, 期望=False -> PASS
场景72分: 可满足=True, 规则判定(approved)=True, 期望=True -> PASS
场景断言: ALL_PASS
重复求解一致: True
```

> Δ 与 Run-2b 的差异：输出格式修复+判定改为机器可断言的 PASS/FAIL；sat/core/方向语义零变化。

## Run-6 2026-08-27 缺陷回填实验 A——RULE-003 枚举静默丢失（injection/inj-a-rule003-loss.puml）

> 注入方式：正式件 puml 中删除 enum LoanPurpose 整块、@disjoint 锚点行，purpose 属性类型退化为 String
> （复刻原交付同类丢失形态）。转换正常完成：

```
OK: cases/loan-system/injection/inj-a-rule003-loss.owl.rdf（5 类/枚举, 2 关联）+ .shacl.ttl
```

探针1 变体本体一致性（HermiT）：
```
== 探针1: 变体(枚举丢失)一致性 ==
[HermiT-mutant] consistent=True 则概念层静默, classes=13 individuals=8
```
探针2 变体 SHACL（BDD 断言样本含 hasPurpose "renovation" 自由文本）：
```
[SHACL-mutant] Conforms: True
```
探针3 正式件负例对照（个体同时落入 LoanPurpose_renovation 与 _medical 两个 disjoint 类）：
```
[HermiT-baseline-negative] HermiT 检出不一致 -> CAUGHT
（异常类型 owlready2.base.OwlReadyInconsistentOntologyError）
```

> Δ 归因结论：**结构三件套捕"误用"不捕"缺失"**——枚举在场时负例即触发不一致（可用）；枚举丢失时
> 概念层 consistent=True、SHACL Conforms=True 双静默（封闭世界下"什么都没说"就是一致）。缺失类缺陷
> 由检查项 6（绑定闭包）兜底，见 Run-9。

## Run-7 2026-08-27 缺陷回填实验 B——操作员跨文档矛盾双侧编码（injection/inj-b-operator-conflict_z3.py）

```
== 第一段: 双侧同时编码(原交付的隐含状态) ==
规则集一致性: unsat | core: [O1_登记侧_FLOW-002_操作人员基于自动审批结果执行通过或驳回, O2_设计侧_US006_自动审批即生效无操作员环节, 事实_存在已通过订单]
== 第二段: D-A 裁决后仅采设计侧 ==
规则集一致性: sat | core(空=自洽): []
```

> Δ 归因：跨文档语义矛盾若被翻译位同时忠实编码，Z3 立即 unsat 且 **unsat core 按规则名点名文档来源**；
> 决策消解一侧后回到 sat。原交付中两侧各自存活到实现层的原因并非不可判定，而是从未有双侧同台的机会
> ——方法价值在翻译位强制落点+本检查兜底。

## Run-8 2026-08-27 流程线检查器上线——fsm_check 五性质 + 负控验证（缺口①关闭）

正式件 `formal/flow-model.puml`（FLOW-001 全流转 + D-A 裁决后自动审批语义，SVG 已渲染人审）：

```
== fsm_check: cases/loan-system/formal/flow-model.puml ==
状态(6): ['active', 'approved', 'closed', 'draft', 'pending', 'rejected']
初始: ['draft'] | 终态: ['closed', 'rejected'] | 迁移数: 5
P1 可达性(自初始态): PASS (OK)
P2 共可达性(至终态): PASS (OK)
P3 终态封闭: PASS (OK)
P4 无死锁(非终态有出边): PASS (OK)
P5 显式禁回(no_escape_from=['rejected']): PASS (OK)
VERDICT: ALL_PROPERTIES_HOLD
```

负控 `injection/inj-c-flow-flaws.puml`（注入禁回回流/终态泄漏/死端三缺陷，验证非空转）：

```
P1 可达性(自初始态): PASS (OK)
P2 共可达性(至终态): FAIL (无法到达任何终态=['obsolete_review'])
P3 终态封闭: FAIL (终态仍有出边=['closed', 'rejected'])
P4 无死锁(非终态有出边): FAIL (死端=['obsolete_review'])
P5 显式禁回(no_escape_from=['rejected']): FAIL (rejected -> ['active', 'approved', 'closed', 'obsolete_review', 'pending'])
VERDICT: VIOLATION_FOUND
```

> Δ 归因：三处注入被 P2/P3/P4/P5 分别精准命中且 P1 正确保持 PASS——检查器具区分力非一票否决。
> 范围声明：当前为 FSM 性质子集；MVP 贷款流无并发，出现并行分支时按工具选型备注升级 WF-net soundness。

## Run-9 2026-08-27 检查项 6 上线——绑定闭包主清单 PASS + 陈旧清单对照（injection/bindings-inj-a-demo.md）

主清单（`formal/model-bindings.md`）：首验 FAIL(23) 系检查器自身 bug（ID 正则漏连字符→11 行全部误判
BADROW）；修复后又一处 trans 定位符无法解析，定位为脚本对 `[*]` 的转义缺左括号（另一处工件路径笔误在
本清单内修正）。全程判定基准未被迁就修正，修毕 PASS：

```
== check_model_bindings: loan-system ==
登记 ID 21 个 | 豁免前缀 ['BR', 'DEL', 'NFR', 'UI'] | 豁免单条 2 | 绑定行 11
覆盖闭包 OK=10/10 | 解析闭包 OK=10 | 反向闭包 FINDING=0
DEFERRED: RULE-002 (RULE-002)
VERDICT: PASS
```

陈旧清单对照（同表但 RULE-003/RULE-004 行指向枚举丢失变体——模拟"清单未随模型同步漂移"）：

```
FINDING[B]: 定位符无法解析(模型漂移?): RULE-003 -> disjoint:LoanPurpose_
FINDING[B]: 定位符无法解析(模型漂移?): RULE-004 -> decision:RULE-004
VERDICT: FAIL(2)
```

> Δ 归因：覆盖/解析/反向三闭包全部按设计工作；DEFERRED 机制使"暂缓但显式"（RULE-002 待 SHACL
> cardinality 词表）合法存在而不误报；对 Run-6 变体的漂移被精确捕获到行级定位符——**缺失类缺陷自此有
> 确定性防线**，回填实验 A 的逃逸通道关闭。
