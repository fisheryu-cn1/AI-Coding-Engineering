# 检查运行台账（check-run-log）

> **这是什么**：本项目 loan-system 案例全部机器检查与人工决策的证据流水账。**只追加不删改**。
> **怎么读**：每节 = 一次运行的完整原始输出 + 差异归因。第一次来？先读 `../../method/14-检查规程与人工决策指南.md`（各检查项含义/重跑命令/人工决策记录方法），再回来按时间序读证据。
> **当前状态速览**：HermiT 一致 ✅ / Z3 v2 双场景正确+幂等 ✅ / 决定性基线 sha256 已立（v2 基准）✅ / 待人工决策 3 项（D-A 操作员方向、D-B decision 弱化、C 类审计勾选）——见指南"人工决策点"表。

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

## Run-3 puml2owl 决定性回归

```
OK: D:/Users/Yu/Documents/Coding/AI-Coding-Engineering/research/requirement-to-spec/cases/loan-system/formal/concept.owl.rdf（6 类/枚举, 2 关联）+ .shacl.ttl
```
概念模型产物 sha256（决定性基线）：
concept.owl.rdf  sha256:
concept.shacl.ttl sha256:
beb9e9338efacb8df01e925b2ad5425f2ef666f2329e6409d8bcc20bfeca6f99 *D:/Users/Yu/Documents/Coding/AI-Coding-Engineering/research/requirement-to-spec/cases/loan-system/formal/concept.owl.rdf
```
规则集一致性: sat | core(空=自洽): []
场景48分: 可满足=%s, 规则判定=拒绝(期望) -> True False
场景72分: 可满足=%s, 规则判定=通过(期望) -> True True
重复求解一致: True
```

## Run-3 puml2owl 决定性基线

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
