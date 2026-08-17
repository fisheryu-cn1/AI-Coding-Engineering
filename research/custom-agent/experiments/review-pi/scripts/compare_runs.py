# -*- coding: utf-8 -*-
"""compare_runs.py —— 跨 run 意见集一致性分析（pass^k 口径的近似）。

用法：python scripts/compare_runs.py reviews/2026-08-17-f62f287*.md

口径：
  - 意见签名 = (级别, 溯源主文件名, 标题首关键词集合的交集键)——不做语义对齐，
    签名相同视为"同一问题被两个 run 都发现"；
  - 输出：两两 Jaccard、三 run 共有/独有计数（pass^3 的意见级近似），
    以及各 run 意见数与级别分布。
"""
import glob, io, itertools, re, sys, collections


def parse(path):
    text = io.open(path, encoding="utf-8").read()
    ops = []
    for m in re.finditer(r"^###\s*\[(P[0-3])\]\s*(.+)$", text, re.M):
        sev, title = m.group(1), m.group(2).strip()
        # 溯源行：意见块内下一处 "- 溯源：`...`"
        tail = text[m.end(): m.end() + 600]
        sm = re.search(r"溯源[^\n]*?([\w./-]+\.(?:py|ts|js|html|md))", tail)
        src = sm.group(1).split("/")[-1] if sm else "?"
        key = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", " ", title).strip().lower()
        ops.append((sev, src, key))
    return ops


def sig(op):
    sev, src, key = op
    words = [w for w in key.split() if len(w) > 1][:3]
    return (sev, src, tuple(sorted(words)))


def main(paths):
    runs = {p: parse(p) for p in paths}
    for p, ops in runs.items():
        dist = collections.Counter(o[0] for o in ops)
        print(f"{p.split('/')[-1]}: {len(ops)} 意见 {dict(sorted(dist.items()))}")
    sets = {p: {sig(o) for o in ops} for p, ops in runs.items()}
    print("\n两两一致性（签名 Jaccard）：")
    for a, b in itertools.combinations(paths, 2):
        sa, sb = sets[a], sets[b]
        inter = len(sa & sb)
        print(f"  {a.split('/')[-1]} ∩ {b.split('/')[-1]}: {inter} / 并 {len(sa | sb)} = {inter/len(sa | sb):.0%}")
    if len(paths) >= 3:
        common = set.intersection(*sets.values())
        union = set.union(*sets.values())
        print(f"\n三 run 共有（≈pass^3 命中面）：{len(common)} / 全并集 {len(union)} = {len(common)/len(union):.0%}")
        only1 = [s for s in union if sum(s in sets[p] for p in paths) == 1]
        print(f"仅单 run 出现（不稳定意见）：{len(only1)}")
        for s in only1[:8]:
            print("   ", s[0], s[1], " ".join(s[2])[:60])


if __name__ == "__main__":
    main(sorted(sys.argv[1:]))
