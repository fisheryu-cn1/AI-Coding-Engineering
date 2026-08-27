#!/usr/bin/env python3
"""fsm_check: PlantUML 状态图子集 → 确定性结构性质检查（三件套第三支·流程线，缺口①）

性质集（全部可判定，不依赖 LLM；对象为有穷状态机而非一般 WF-net——
MVP 贷款流无并发，R2+ 出现并行分支时升级 WF-net soundness 工具链，见工具选型备注）：
  P1 可达性     初始态可达所有状态（无死状态）
  P2 共可达性   所有状态可达某终态（无陷阱：进得去出不来）
  P3 终态封闭   终态无出边
  P4 无死锁     非终态至少一条出边
  P5 显式禁回   no_escape_from 配置的终态经任何迁移序列不可到达其他状态
no_escape_from 来源优先级: 命令行 --no-escape > .puml 内注释配置行 `no_escape_from=[a,b]`。
用法: fsm_check.py <model.puml> [--no-escape 态名 ...]
退出码: 0=ALL_PROPERTIES_HOLD, 1=VIOLATION。
"""
import argparse, re, sys

TRANS_RE = re.compile(r'^\s*(\S+)\s*-->\s*(\S+)\s*(?::\s*(.+?))?\s*$')


def parse(path):
    text = open(path, encoding='utf-8').read()
    body = re.search(r'@startuml(.*)@enduml', text, re.S)
    if not body:
        sys.exit('ERR: 未找到 @startuml/@enduml')
    trans = []
    for line in body.group(1).splitlines():
        m = TRANS_RE.match(line)
        if m:
            src, dst, label = m.groups()
            trans.append((src, dst or '', (label or '').strip()))
    init = {d for s, d, _ in trans if s == '[*]'}
    states = ({s for s, _, _ in trans if s != '[*]'}
              | {d for _, d, _ in trans if d != '[*]'})
    terminals = {s for s, d, _ in trans if d == '[*]' and s != '[*]'}
    out_edges = {}
    for s, d, l in trans:
        if s != '[*]' and d != '[*]':
            out_edges.setdefault(s, []).append((d, l))
    n_inner = len(trans) - sum(1 for s, d, _ in trans if '[*]' in (s, d))
    return trans, sorted(states), sorted(init), sorted(terminals), out_edges, n_inner


def reach(start, out_edges):
    seen, todo = set(), [start]
    while todo:
        x = todo.pop()
        if x in seen:
            continue
        seen.add(x)
        todo.extend(d for d, _ in out_edges.get(x, []))
    return seen


def check(states, init, terminals, out_edges, no_escape):
    results = []

    r_init = set().union(*(reach(i, out_edges) for i in init)) if init else set()
    unreachable = sorted(set(states) - r_init)
    results.append(('P1 可达性(自初始态)', not unreachable,
                    f'不可达={unreachable}' if unreachable else 'OK'))

    traps = sorted(s for s in states if not (reach(s, out_edges) & set(terminals)))
    results.append(('P2 共可达性(至终态)', not traps,
                    f'无法到达任何终态={traps}' if traps else 'OK'))

    leaky = sorted(t for t in terminals if out_edges.get(t))
    results.append(('P3 终态封闭', not leaky,
                    f'终态仍有出边={leaky}' if leaky else 'OK'))

    dead = sorted(s for s in states if s not in terminals and not out_edges.get(s))
    results.append(('P4 无死锁(非终态有出边)', not dead,
                    f'死端={dead}' if dead else 'OK'))

    escapes = []
    for t in no_escape:
        hit = sorted(reach(t, out_edges) - {t})
        if hit:
            escapes.append(f'{t} -> {hit}')
    results.append((f'P5 显式禁回(no_escape_from={no_escape})', not escapes,
                    '; '.join(escapes) if escapes else 'OK'))

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('puml')
    ap.add_argument('--no-escape', nargs='*', default=None)
    args = ap.parse_args()

    trans, states, init, terminals, out_edges, n_inner = parse(args.puml)
    print(f'== fsm_check: {args.puml} ==')
    print(f'状态({len(states)}): {states}')
    print(f'初始: {init} | 终态: {terminals} | 迁移数: {n_inner}')

    cfg = args.no_escape
    if cfg is None:
        src = open(args.puml, encoding='utf-8').read()
        m = re.search(r'^\s*no_escape_from\s*=\s*\[(.*?)\]', src, re.M | re.S)
        cfg = [x.strip() for x in m.group(1).split(',') if x.strip()] if m else []

    verdict = True
    for name, ok, detail in check(states, init, terminals, out_edges, cfg):
        verdict = verdict and ok
        print(f'{name}: {"PASS" if ok else "FAIL"} ({detail})')
    print('VERDICT:', 'ALL_PROPERTIES_HOLD' if verdict else 'VIOLATION_FOUND')
    sys.exit(0 if verdict else 1)


if __name__ == '__main__':
    main()
