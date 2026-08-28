# kbapp-review 01 层规则集 Z3（输入=raw/01 原文；评审忠实原则）
from z3 import *

# --- FR-6.2 三档阈值序关系（01 未定数值——参数化验证结构约束）---
s = Solver(); s.set(unsat_core=True)
acc, rej = Reals('accept_threshold reject_threshold'); score = Real('score')
s.assert_and_track(acc > rej, 'FR62_阈值序_accept须大于reject')
s.assert_and_track(Implies(score >= acc, Bool('is_pending')), 'FR62_上档入待审')
s.assert_and_track(Implies(And(rej <= score, score < acc), Bool('is_watchlist')), 'FR62_中档入边界')
s.assert_and_track(Implies(score < rej, Bool('is_logged_only')), 'FR62_下档仅台账')
print('FR-6.2 阈值组结构:', s.check(), '| core:', list(s.unsat_core()) if s.check() == unsat else [])

# --- FR-2.7 成本约束 ---
s2 = Solver(); s2.set(unsat_core=True)
ratio = Real('structured_ratio')   # 被实体抽取的文档占比
s2.assert_and_track(ratio >= 0.15, 'FR27_下界15%')
s2.assert_and_track(ratio <= 0.25, 'FR27_上界25%')
print('FR-2.7 成本区间:', s2.check(), '| core:', list(s2.unsat_core()) if s2.check() == unsat else [])

# --- NFR-4 性能预算（01 数值, 三条独立约束）---
s3 = Solver(); s3.set(unsat_core=True)
pdf_t, search_t, assemble_t = Reals('pdf_minutes search_seconds assemble_seconds')
s3.assert_and_track(pdf_t < 2, 'NFR4_增量单篇分钟')
s3.assert_and_track(search_t < 3, 'NFR4_检索秒')
s3.assert_and_track(assemble_t < 10, 'NFR4_组装秒')
print('NFR-4 性能组:', s3.check())

# --- FR-6.2 数值缺位登记（非检查, 显式化）：阈值数值 01 未定义 → KD-3 待人工
print('KD-3: accept/reject 阈值数值在 01 层未定义（03 §8.2.1 给出 0.70/0.50 默认——设计层消解）')
