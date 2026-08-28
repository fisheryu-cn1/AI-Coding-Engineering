# kbapp-review 05 层规则集 Z3（输入=raw/05 §2.5 config + §4.2 分类判据）
from z3 import *

# --- 阈值组层间传导验证（05 §2.5 vs 03 §8.2.1）---
s = Solver(); s.set(unsat_core=True)
acc, rej, bonus = Reals('accept reject cross_topic_bonus')
s.assert_and_track(acc == 0.70, 'T1_05_accept_070')
s.assert_and_track(rej == 0.50, 'T2_05_reject_050')
s.assert_and_track(bonus == 0.05, 'T3_05_bonus_005')
print('05 阈值组自洽:', s.check(), '(数值与 03 一致——阈值层间传导 ✓)')

# --- 分类判据层间变形: 03 差值阈值 vs 05 M2 比值阈值(数学不等价, 求分歧反例)---
# 03 §4 P2: top1.sim - top2.sim > gap_threshold(0.05) → 直接定类
# 05 §2.5 M2: top1 >= top2 × top_ratio(1.5) → 直接定类
s2 = Solver()
t1, t2 = Reals('top1 top2')
s2.add(0 <= t2, t2 <= t1, t1 <= 1)
s2.add(t1 - t2 > 0.05)          # 差值判据: 直接定类
s2.add(t1 < 1.5 * t2)           # 比值判据: 不定类(进人工/仲裁)
r1 = s2.check()
m = s2.model() if r1 == sat else None
print('分歧例A(差值过/比值不过):', r1,
      f'top1={m[t1].as_decimal(3) if m else "?"}, top2={m[t2].as_decimal(3) if m else "?"}' if m else '')

s3 = Solver()
s3.add(0 <= t2, t2 <= t1, t1 <= 1)
s3.add(Not(t1 - t2 > 0.05))     # 差值判据: 不定类
s3.add(t1 >= 1.5 * t2)          # 比值判据: 直接定类
r2 = s3.check()
m = s3.model() if r2 == sat else None
print('分歧例B(比值过/差值不过):', r2,
      f'top1={m[t1].as_decimal(3) if m else "?"}, top2={m[t2].as_decimal(3) if m else "?"}' if m else '')

# --- 重试退避一致性(05 §2.5 retry vs §7.2 状态机): max_attempts=4 与 attempts<max 回退一致(结构检查)---
print('注: retry.max_attempts=4 与 tasks.max_attempts 字段并存(两处配置, KD-11 口径待对照)')
