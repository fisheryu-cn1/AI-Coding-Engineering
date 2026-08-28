#!/usr/bin/env python3
"""diff_models: 两张同骨架 puml 类图的元素级 diff（层间对照的机械化工具，method/17 候选件）

前提（公共骨架原则）：两图须建模同一对象族的相邻层形态（下游图包含上游图的同源元素）。
输出五类差异：仅上层类 / 仅下层类 / 共有类属性差（新增/移除）/ 枚举字面量差 / 关联差。
用法: diff_models.py <upper.puml> <lower.puml>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from puml2xmi import parse_puml


def load(p):
    classes, enums, assocs, gens = parse_puml(open(p, encoding='utf-8').read())
    attrs = {c: {a[1] for a in info['attrs']} for c, info in classes.items()}
    edges = {(a, b, label) for a, _, b, _, label in assocs}
    return attrs, enums, edges


def main():
    up, lo = sys.argv[1], sys.argv[2]
    uA, uE, uR = load(up)
    lA, lE, lR = load(lo)
    print(f'== diff_models: 上层 {os.path.basename(up)} → 下层 {os.path.basename(lo)} ==')
    print(f'上层: 类 {len(uA)} 枚举 {len(uE)} 关联 {len(uR)} | 下层: 类 {len(lA)} 枚举 {len(lE)} 关联 {len(lR)}')
    n = 0
    only_u = set(uA) - set(lA)
    only_l = set(lA) - set(uA)
    for c in sorted(only_u):
        print(f'FINDING[类]: 仅上层有 {c}（下游丢失——保真性检查点）'); n += 1
    for c in sorted(only_l):
        print(f'FINDING[类]: 仅下层有 {c}（新增——溯源检查点）'); n += 1
    for c in sorted(set(uA) & set(lA)):
        added = lA[c] - uA[c]
        removed = uA[c] - lA[c]
        for a in sorted(added):
            print(f'FINDING[属性]: {c}.{a} 下层新增（溯源检查点）'); n += 1
        for a in sorted(removed):
            print(f'FINDING[属性]: {c}.{a} 下层移除（保真性检查点）'); n += 1
    for e in sorted(set(uE) & set(lE)):
        added = set(lE[e]) - set(uE[e])
        removed = set(uE[e]) - set(lE[e])
        for x in sorted(added):
            print(f'FINDING[枚举]: {e} 新增字面量 {x}'); n += 1
        for x in sorted(removed):
            print(f'FINDING[枚举]: {e} 移除字面量 {x}'); n += 1
    for e in sorted(set(uE) - set(lE)):
        print(f'FINDING[枚举]: 仅上层有枚举 {e}'); n += 1
    for e in sorted(set(lE) - set(uE)):
        print(f'FINDING[枚举]: 仅下层有枚举 {e}'); n += 1
    for r in sorted(uR - lR):
        print(f'FINDING[关联]: 仅上层有 {r[0]}--{r[2]}:{r[4]}（下游丢失）'); n += 1
    for r in sorted(lR - uR):
        print(f'FINDING[关联]: 仅下层有 {r[0]}--{r[2]}:{r[4]}（新增）'); n += 1
    print('VERDICT:', 'IDENTICAL' if n == 0 else f'DIFFS({n})')


if __name__ == '__main__':
    main()
