# 实验环境清单与冒烟测试记录（2026-08-26 搭建）

> 用途：R1/R2 管线（NL→UML→OWL+BDD 验证）本地环境。机器要求实测：普通笔记本（Java 25 + Python 3.13）即可，全部组件总磁盘 <150MB，实验规模内存 <1.5GB。

## 组件清单

| 组件 | 版本 | 来源/安装 | 状态 |
|---|---|---|---|
| Java (Temurin) | 25.0.3 LTS | 本机已有 | ✅ |
| z3-solver | 5.1.0 | `pip install z3-solver`（**清华镜像**：`-i https://pypi.tuna.tsinghua.edu.cn/simple`；PyPI 直连被重置 10054） | ✅ |
| owlready2 | 0.51 | 同上 | ✅ |
| pyshacl | 0.40.1 | 同上 | ✅ |
| rdflib | 7.6.0 | 同上 | ✅ |
| HermiT | 1.4.5.519 | Maven Central：`net.sourceforge.owlapi:org.semanticweb.hermit`（1.9MB）→ 拷入 `site-packages/owlready2/hermit.jar`（owlready2 的 sync_reasoner_hermit 需要该位置；首次调用自动解压） | ✅ |
| PlantUML | 1.2026.7 | Maven Central：`net.sourceforge.plantuml:plantuml`（图形渲染用） | ✅（仅渲染） |
| model2owl | master | `git clone --depth 1 https://github.com/OP-TED/model2owl`（网络恢复后成功）；Saxon-HE 10.6 经 SourceForge zip 装入 `saxon/saxon.jar` | ✅（2026-08-26 深夜验证） |
| 冒烟脚本 | — | `sandbox/smoke_z3.py`、`smoke_owl.py`、`smoke_shacl.py`、`mini.puml` | ✅ |

## 冒烟测试结果（四项）

| # | 组件 | 结果 | 关键发现 |
|---|---|---|---|
| 1 | Z3 | ✅ | 两条矛盾业务规则（评分阈值通过 vs 高额必拒）→ `unsat` + **unsat core 直接返回中文规则名** `[R1_评分达阈值即通过, R2_高额必须拒绝]`——矛盾检测+冲突定位一体完成 |
| 2 | PlantUML XMI 导出 | ❌ **衔接件断裂** | 1.2026.7 的 `-xmi/-txmi/-xmi:argo` 均抛 `UnsupportedOperationException`，`-help` 已无该选项——**主线版本已移除/废弃 XMI 模型导出**（plantuml.com/xmi 为遗留文档页）。老版 8059 同样异常 |
| 3 | owlready2+HermiT | ✅ | 编程构建贷款最小本体（6 状态类+disjoint+属性域值域）→ 推理 0.5s；注入矛盾类（同时是互斥的 draft 与 rejected）→ HermiT 判 `Weird ≡ owl:Nothing`（unsatisfiable class）——**"矛盾规则"在 OWL 侧的检测形态实证** |
| 4 | pySHACL | ✅ | 数据图+SHACL shape（status 必填+六值枚举）→ 正确检出 MinCount 违规并输出**中文 message**；教学发现：枚举外的非法值（order2.status=teleported）未被报告，因其**缺少 `a ex:LoanOrder` 类型声明**——targetClass 只圈显式声明类型的节点，闭包校验同样依赖显式断言（需补 sh:targetObjectsOf 类 shape 覆盖"未声明类型的引用"） |

## 对管线设计的三条结论

1. **XMI 通道废弃，改自写映射器**：LLM→PlantUML/Mermaid 文本类图→**自写轻量解析→owlready2 直接构建 OWL**（跳过 XMI 与 model2owl）。类图语法极简（class/属性/关联/泛化/多重性），映射规则按备忘 §9.3 语义差异表显式化（disjoint 为显式决策项非默认）。少两个外部依赖，符合低锁定原则；model2owl 的映射文档保留为规则参照。
2. **PlantUML/Mermaid jar 保留用于图形渲染**（`-tsvg` 正常），文本为源、图形为审的工作流不变。
3. **BDD 双检的两侧执行器均已就绪**：OWL 侧（HermiT 一致性/unsatisfiable + 蕴含）+ 闭包侧（pySHACL minCount/枚举/cardinality）+ 规则侧（Z3 unsat core）——三件套运行时全部冒烟通过。

## model2owl 验证记录（2026-08-26 深夜补）

两步流程跑通（绕过 make，Windows Git Bash 无 make）：

```bash
# Step1 预处理命名空间（输出 interm/enriched-namespaces.xml）
java -jar saxon/saxon.jar -s:test/ePO-default-config/namespaces.xml -xsl:src/xml/enriched-namespaces.xsl -o:interm/enriched-namespaces.xml
# Step2a UML(XMI)→OWL core；Step2b →SHACL（参数必须传绝对路径！）
java -jar saxon/saxon.jar -s:test/test-multi-xmi/ePO_CM.xml -xsl:src/owl-core.xsl -o:output/ePO_core.tmp.rdf "enrichedNamespacesPath=<绝对路径>/interm/enriched-namespaces.xml" "importsPath=<绝对路径>/test/ePO-default-config/imports.xml"
java -jar saxon/saxon.jar -s:test/test-multi-xmi/ePO_CM.xml -xsl:src/shacl-shapes.xsl -o:output/ePO_shacl.ttl  "enrichedNamespacesPath=<绝对路径>" "importsPath=<绝对路径>"
```

- 结果：OWL core 504KB / **2499 triples / 657 subjects**，SHACL **5546 triples**，rdflib 均可加载 ✅
- 踩坑 2 条：① `enrichedNamespacesPath` 相对路径被按**样式表目录**解析（doc() 基准 URI），必须传绝对路径；② 输出实为 **RDF/XML**，与扩展名无关（Makefile 的 convert 步骤才转 turtle）——rdflib 解析用 `format='xml'`
- **管线决策更新**：XMI 通道经 model2owl 复活，映射器路线现有两选项——A）自写"文本类图→XMI 2.5.1"生成器（XML 模板机械映射）→model2owl 全链（**SHACL 自动生成**——BDD 闭包校验 shape 免手写，另白送 UML 合规检查与 glossary）；B）自写"文本类图→OWL"直映射（少一层、完全自控，按备忘 §9.3 差异表）。R1/R2 时以"文本→XMI 生成器的机械度"为判定标准做选型实验。

## puml2xml 验证结论（2026-08-26，A1 出局）

- clone 成功并检视示例输出：puml2xml 产出 **UML 1.4 XMI**（`xmi.version="1.1"`、`UML:Class` 大写命名空间）——与 model2owl 要求的 **XMI 2.5.1/UML 2.5**（`uml:Model`/`packagedElement`，对照其测试输入 ePO_CM.xml：1151 个 packagedElement）**差两个代际，结构不兼容**。且本机无 Docker/OCaml（其构建依赖）。
- **A1 路线出局**。选型更新：**B'（自写 PlantUML 类图→XMI 2.5.1 生成器→model2owl）升为最优候选**——目标格式有现成完整范例（ePO_CM.xml 即 EA 导出的标准样本，覆盖类/属性/关联/枚举全部形态）、映射面仅类图子集、产出白拿 model2owl 的 SHACL/合规检查/glossary；A2（Umple）保留备选（件成熟但 LLM 生成 Umple 语料弱）。

## model2owl 深度验证结论（2026-08-26 深夜二次，重要证伪）

- 全链联调发现：model2owl 的 XSL 选择器读取的是 `/xmi:XMI/xmi:Extension/elements` 与 `connectors`（`properties/@ea_type` 等）——**实际消费 Enterprise Architect 私有导出格式**（其标准 packagedElement 区只用于注释关联），标准 UML 2.5.1 XMI 对其不可见（转换"成功"但产出空本体）。
- **"现成 UML→OWL 管线"证伪**：model2owl 是 EA→内部格式→OWL 工具，非通用 XMI 工具；逆向 EA 扩展格式（2MB 样例、数百字段）成本不可控。
- **最终管线定案（B 方案）**：LLM→PlantUML 类图→`tools/scripts/puml2owl.py`（自写直映射：复用 puml2xmi 的解析器 + owlready2 构建 OWL + 自生成 SHACL）→HermiT/Z3/pySHACL。puml2xmi.py 的 XMI 生成保留为标准工具互操作备件。

## B 方案全链闭环（2026-08-26 深夜终局）

`tools/scripts/puml2owl.py`（复用 puml2xmi 解析器，~140 行）+ `puml2xmi.py` 解析层：**LLM→PlantUML 类图→OWL+SHACL 全链一次走通**——mini.puml（贷款 3 类+状态枚举+关联）→ 51 triples 本体（Borrower/LoanOrder/OrderStatus/6 字面量/places）→ **HermiT 推理 0.73s 一致通过**。管线最终形态：`puml2owl.py → HermiT/Z3/pySHACL`，零外部转换依赖。

联调踩坑追加：①owlready2 0.51 Windows 下 turtle 序列化产出 0 字节（bug），用 format='rdfxml' 规避；②个体创建用类调用而非 types.new_individual；③model2owl 的 XSL 选择器读 `xmi:Extension`（EA 私有区）——"标准 XMI 输入"证伪。
