# [注入实验 B] 操作员跨文档矛盾——双侧来源规则同时编码给 Z3
# 复刻对象: giencoder-exam-P0151020 原交付——登记/PRD 侧"操作人员执行通过/驳回"(FLOW-001/002)
#           vs US-006/design/实现侧"自动审批即生效, 无操作员环节"。
# 原交付中两侧各自存活(US 澄清后未回写上游)。本脚本演示: 若翻译位把两侧都忠实编码,
# S4 规则检查立即 unsat 且 unsat core 命名两条规则的文档来源——跨文档矛盾在本层必现。
# 第二段: D-A 决策采纳设计侧后仅留 O2 —— 回到 sat, 演示"决策消解矛盾"闭环。
from z3 import *

Order = DeclareSort('Order')
A = Function('Approved', Order, BoolSort())
OperatorRecorded = Function('OperatorRecorded', Order, BoolSort())
x, o = Const('x', Order), Const('o', Order)

s2 = Solver()
s2.set(unsat_core=True)
s2.assert_and_track(ForAll([x], Implies(A(x), OperatorRecorded(x))),
                    'O1_登记侧_FLOW-002_操作人员基于自动审批结果执行通过或驳回')
s2.assert_and_track(ForAll([x], Implies(A(x), Not(OperatorRecorded(x)))),
                    'O2_设计侧_US006_自动审批即生效无操作员环节')
s2.assert_and_track(A(o), '事实_存在已通过订单')

print('== 第一段: 双侧同时编码(原交付的隐含状态) ==')
print('规则集一致性:', s2.check(), '| core:', list(s2.unsat_core()))

s3 = Solver()
s3.set(unsat_core=True)
s3.assert_and_track(ForAll([x], Implies(A(x), Not(OperatorRecorded(x)))),
                    'O2_设计侧_US006_自动审批即生效无操作员环节')
s3.assert_and_track(A(o), '事实_存在已通过订单')
print('== 第二段: D-A 决策后仅采设计侧 ==')
print('规则集一致性:', s3.check(), '| core(空=自洽):', list(s3.unsat_core()))
