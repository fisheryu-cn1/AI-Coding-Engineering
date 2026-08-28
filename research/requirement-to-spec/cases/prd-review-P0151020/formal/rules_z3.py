# prd-review-P0151020 规则集 Z3 编码（S3 翻译：输入=raw/prd.md §5 规则表+§4 流程原文）
# 翻译忠实原则（评审模式）：双侧语义都按 PRD 原文编码——矛盾显形留给检查器（loan-system Run-7 方法的复用）。
from z3 import *

# --- RULE-001 评分规则（PRD §5：分数≥阈值通过，阈值由配置表维护，PRD 未给默认值——参数化保留）---
s = Solver()
s.set(unsat_core=True)
approved = Bool('approved'); score, threshold = Int('score'), Int('threshold')
s.assert_and_track(Implies(score >= threshold, approved), 'R1_评分达标通过_PRD§5')
s.assert_and_track(Implies(score < threshold, Not(approved)), 'R1b_未达标拒绝_PRD§5')
print('规则集一致性(评分):', s.check(), '| core:', list(s.unsat_core()) if s.check() == unsat else [])

# --- 操作员语义双侧编码（PRD §2 角色表/§4 主流程5 vs §4 异常4）---
Order = DeclareSort('Order')
A = Function('ApprovedResult', Order, BoolSort())     # 自动审批结果
OpAct = Function('OperatorAction', Order, BoolSort()) # 操作人员执行了通过流转
o = Const('o', Order)
s2 = Solver()
s2.set(unsat_core=True)
# 侧1（PRD §4 主流程5+§2 角色表）: 操作人员的通过/驳回"基于自动审批结果执行"——操作动作蕴含结果一致
s2.assert_and_track(ForAll([o], Implies(OpAct(o), A(o))), 'OP-1_主流程5_操作员通过基于审批结果')
# 侧2（PRD §4 异常4）: 不得绕过审批结果直接执行状态变更——审批未通过则操作动作非法
s2.assert_and_track(ForAll([o], Implies(Not(A(o)), Not(OpAct(o)))), 'OP-2_异常4_不得绕过审批结果')
fact = s2.assert_and_track(OpAct(o), '事实_存在操作员通过的订单')
print('操作员双侧规则:', s2.check(), '| core:', list(s2.unsat_core()) if s2.check() == unsat else [])

# --- RULE-004 费率（PRD §5：配置表固定值；PRD §10 待确认无默认值——显式待决标记）---
annual_rate = Real('annual_rate')
s3 = Solver(); s3.set(unsat_core=True)
s3.assert_and_track(annual_rate > 0, 'R4_费率为正_PRD§5配置表语义')
# PRD 未提供默认值（§10 待确认）——按占位策略不硬编码, 待决标记:
print('费率规则(占位):', s3.check(), '| 注: PRD §10 明确默认值待设计阶段——显式待决, 不静默取值')

# --- FLOW-001 状态机边（PRD §5 状态机合法路径原文）---
print('\n状态机检查见 fsm_check.py（六态五迁移, PRD 原文口径）')
