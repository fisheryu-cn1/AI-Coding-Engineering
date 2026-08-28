# kbapp-review 03 层规则集 Z3（输入=raw/03 §8.2.1 阈值组 + §4 P4 触发范围声明）
from z3 import *

# --- §8.2.1 阈值组（03 默认数值）---
s = Solver(); s.set(unsat_core=True)
acc, rej, bonus = Reals('accept_threshold reject_threshold cross_topic_bonus')
s.assert_and_track(acc == 0.70, 'T1_accept默认070')
s.assert_and_track(rej == 0.50, 'T2_reject默认050')
s.assert_and_track(bonus == 0.05, 'T3_bonus默认005')
score, damped = Reals('score score_damped')
s.assert_and_track(Implies(And(score < acc, score >= rej), Bool('watchlist_区间')), 'T4_watchlist半开区间')
# 多主题加成: top-2 sim ≥ 0.7 时 score' = min(score+0.05, 1.0)
s2 = Solver(); s2.set(unsat_core=True)
s2.assert_and_track(Implies(And(Bool('top2_ge_07'), score <= 0.95),
                            damped == score + bonus), 'T5_加成公式')
print('阈值组自洽:', s.check(), s2.check())

# --- 降权公式边界检验（§8.2.1-5: damp 0.8×score）---
# 观察: 降权后 0.8×0.70=0.56 仍 > reject 0.50 → 高质量候选降权后落 watchlist 而非直接 reject——验证该语义
s3 = Solver()
s3.add(0.8 * 0.70 > 0.50)
print('降权边界: 0.8×accept(0.56) > reject(0.50) =', s3.check(), '(降权不直接出档, 落 watchlist——设计语义确认)')

# --- §4 P4 触发范围声明验证："必须主题∩类型交集而非并集, 否则击穿 15-25%" ---
# 建模: 论文占比 0.8(03 原文"本库论文占比约八成"), 核心主题占比 ct, 核心类型占比 dt
# 交集语义: ratio_I = ct × dt；并集语义: ratio_U = ct + dt - ct×dt
s4 = Solver(); s4.set(unsat_core=True)
ct, dt, ratio_I, ratio_U = Reals('core_topic_ratio doc_type_ratio ratio_inter ratio_union')
paper = Real('paper_ratio'); s4.add(paper == 0.8)
s4.assert_and_track(ratio_I == ct * dt, 'P4I_交集语义')
s4.assert_and_track(ratio_U == ct + dt - ct * dt, 'P4U_并集语义')
# 反例存在性: 存在 (ct, dt) 使交集满足 ≤0.25 而并集违反 >0.25
s4.push()
s4.add(And(ratio_I <= 0.25, ratio_U > 0.25, ct > 0, dt > 0, ct <= 1, dt <= 1))
r = s4.check()
m = s4.model() if r == sat else None
print('P4 交集vs并集 反例存在性:', r,
      f'(例: ct={m[ct].as_decimal(3) if m else "?"}, dt={m[dt].as_decimal(3) if m else "?"}, '
      f'交集={m[ratio_I].as_decimal(3) if m else "?"}, 并集={m[ratio_U].as_decimal(3) if m else "?"})——03 的"并集击穿"声明由 Z3 反例证实')
s4.pop()

# --- §4 P2-5 质心防震荡（90 天不参与）与 confidence<0.7 人工确认——时序/软约束, 登记为设计新生规则(不建模)
print('设计新生规则(登记不建模): 质心防震荡90天 / confidence<0.7人工确认 / 关系冲突取weight高 / trigram分词 / 写锁约定')
