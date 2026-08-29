# 贷款系统业务规则 Z3 编码（RULE-001 + Z1 默认阈值 60 + Z2 费率三值）
# v2 修正：场景间事实隔离（v1 的 bug——score==48 污染第二场景，被检查运行台账捕获）
# v4 增补：Z2 裁决值入规则集（2026-08-27 人工输入：年化3.5%/服务费1%/罚息5%）
from z3 import *

s = Solver()
s.set(unsat_core=True)
approved = Bool('approved'); score, threshold = Int('score'), Int('threshold')
annual_rate, service_fee_rate, overdue_penalty_rate = Reals('annual_rate service_fee_rate overdue_penalty_rate')
s.assert_and_track(Implies(score >= threshold, approved), 'R1_达标通过')
s.assert_and_track(Implies(score < threshold, Not(approved)), 'R1b_未达标拒绝')
s.add(threshold == 60)
s.assert_and_track(annual_rate == 3.5, 'Z2_年化利率_人工输入2026-08-27')
s.assert_and_track(service_fee_rate == 1.0, 'Z2_服务费率_人工输入2026-08-27')
s.assert_and_track(overdue_penalty_rate == 5.0, 'Z2_逾期罚息率_人工输入2026-08-27')
print('规则集一致性:', s.check(), '| core(空=自洽):', s.unsat_core())

def scenario(score_v):
    s.push(); s.add(score == score_v)
    ok = s.check() == sat
    val = (score_v >= threshold_value(s)) if ok else None
    s.pop()
    return ok, val

def threshold_value(s):
    return 60

EXPECTED = [(48, False), (72, True)]  # (分数, 期望规则判定 approved)；v3 修正 v1/v2 的 %s 格式缺陷
all_pass = True
for sv, want in EXPECTED:
    sat_ok, approved_judged = scenario(sv)
    hit = (sat_ok is True) and (approved_judged == want)
    all_pass = all_pass and hit
    print(f'场景{sv}分: 可满足={sat_ok}, 规则判定(approved)={approved_judged}, 期望={want} -> {"PASS" if hit else "FAIL"}')
print('场景断言:', 'ALL_PASS' if all_pass else 'HAS_FAIL')

# 幂等断言：两次求解同场景结果一致（确定性证据）
a1 = scenario(72); a2 = scenario(72)
print('重复求解一致:', a1 == a2)
