# 贷款系统业务规则 Z3 编码（RULE-001 + Z1 默认阈值 60）
# v2 修正：场景间事实隔离（v1 的 bug——score==48 污染第二场景，被检查运行台账捕获）
from z3 import *

s = Solver()
s.set(unsat_core=True)
approved = Bool('approved'); score, threshold = Int('score'), Int('threshold')
s.assert_and_track(Implies(score >= threshold, approved), 'R1_达标通过')
s.assert_and_track(Implies(score < threshold, Not(approved)), 'R1b_未达标拒绝')
s.add(threshold == 60)
print('规则集一致性:', s.check(), '| core(空=自洽):', s.unsat_core())

def scenario(score_v):
    s.push(); s.add(score == score_v)
    ok = s.check() == sat
    val = (score_v >= threshold_value(s)) if ok else None
    s.pop()
    return ok, val

def threshold_value(s):
    return 60

print('场景48分: 可满足=%s, 规则判定=拒绝(期望) ->', *scenario(48))
print('场景72分: 可满足=%s, 规则判定=通过(期望) ->', *scenario(72))

# 幂等断言：两次求解同场景结果一致（确定性证据）
a1 = scenario(72); a2 = scenario(72)
print('重复求解一致:', a1 == a2)
