# 贷款系统业务规则的 Z3 编码（来自 RULE-001~004 与待决项 Z1 默认值）
from z3 import *

s = Solver()
s.set(unsat_core=True)

score, threshold = Int('score'), Int('threshold')
amount = Int('amount'); income = Int('income')
approved = Bool('approved')

# RULE-001 (Z1 默认): 评分>=阈值(60) => 通过; 否则拒绝
s.assert_and_track(Implies(score >= threshold, approved), 'R1_达标通过')
s.assert_and_track(Implies(score < threshold, Not(approved)), 'R1b_未达标拒绝')
s.add(threshold == 60)

# 健全性事实: 分数非负有界
s.add(score >= 0, score <= 100)
# E2E 证据回填的样例: 低收入大额申请评分48 -> 拒绝
s.add(score == 48, amount == 200000, income == 5000)

r = s.check()
print('规则集一致性:', r)
assert r == sat
# R1b 触发验证（对应原始缺陷 RULE-003 类比的覆盖检验: 每条规则至少一个模型触达）
s.push()
s.add(approved == False); print('48分场景 -> 拒绝 可满足:', s.check() == sat)
s.pop()
s.push()
s.add(score == 72, income == 30000, amount == 80000)
s.add(approved == True); print('72分场景 -> 通过 可满足:', s.check() == sat)
s.pop()
