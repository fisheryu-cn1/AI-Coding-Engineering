#!/usr/bin/env python3
"""diff_models: 两张同骨架 puml 类图的元素级 diff（层间对照的机械化工具，method/17 候选件）

前提（公共骨架原则）：两图须建模同一对象族的相邻层形态（下游图包含上游图的同源元素）。
输出五类差异：仅上层类 / 仅下层类 / 共有类属性差（新增/移除）/ 枚举字面量差 / 关联差。
用法: diff_models.py <upper.puml> <lower.puml>
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from puml2xmi import parse_puml


OP_RE = None  # 延迟初始化（避免顶层 import 失败顺序问题）
import re as _re
_OP_LINE = _re.compile(r'^([+\-#~])?\s*([\w]+)\s*\(.*\)\s*(?::\s*(.+?))?$')


def _methods(text):
    """从 puml 文本解析各类的操作行（+name(args): Ret）；与属性正则互斥（带参括号行不匹配属性）。"""
    out, cur = {}, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("'"):
            continue
        m = _re.match(r'^(?:abstract\s+)?(?:class|interface)\s+(\w+)', line)
        if m:
            cur = m.group(1); out.setdefault(cur, set()); continue
        if line == '}':
            cur = None; continue
        mo = _OP_LINE.match(line)
        if mo and cur:
            out[cur].add(mo.group(2))
    return out


def load(p):
    text = open(p, encoding='utf-8').read()
    classes, enums, assocs, gens = parse_puml(text)
    attrs = {c: {a[1] for a in info['attrs']} for c, info in classes.items()}
    edges = {(a, b, label) for a, _, b, _, label in assocs}
    return attrs, enums, edges, _methods(text)


def main():
    up, lo = sys.argv[1], sys.argv[2]
    uA, uE, uR, uM = load(up)
    lA, lE, lR, lM = load(lo)
    print(f'== diff_models: 上层 {os.path.basename(up)} → 下层 {os.path.basename(lo)} ==')
    print(f'上层: 类 {len(uA)} 枚举 {len(uE)} 关联 {len(uR)} 方法 {sum(len(v) for v in uM.values())} | 下层: 类 {len(lA)} 枚举 {len(lE)} 关联 {len(lR)} 方法 {sum(len(v) for v in lM.values())}')
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
        print(f'FINDING[关联]: 仅上层有 {r[0]}--{r[2]}:{r[2] if len(r)<3 else r[2]}（下游丢失）'); n += 1
    for r in sorted(lR - uR):
        print(f'FINDING[关联]: 仅下层有 {r[0]}--{r[2]}（新增）'); n += 1
    for c in sorted(set(uM) & set(lM)):
        for m in sorted(lM[c] - uM[c]):
            print(f'FINDING[方法]: {c}.{m}() 下层新增（签名漂移检查点）'); n += 1
        for m in sorted(uM[c] - lM[c]):
            print(f'FINDING[方法]: {c}.{m}() 下层移除（签名漂移检查点）'); n += 1
    for c in sorted(set(uM) - set(lM)):
        print(f'FINDING[方法]: 仅上层有操作集 {c}（{len(uM[c])} 个方法）'); n += 1
    for c in sorted(set(lM) - set(uM)):
        print(f'FINDING[方法]: 仅下层有操作集 {c}（{len(lM[c])} 个方法）'); n += 1
    print('VERDICT:', 'IDENTICAL' if n == 0 else f'DIFFS({n})')


if __name__ == '__main__':
    main()
