# -*- coding: utf-8 -*-
"""score_review.py —— 评审意见卡 vs 评估标注集的启发式召回评分器（v1）。

v0→v1 修正（2026-08-17 首跑教训）：
  1. 关键词只取 ASCII 标识符（函数/变量/SQL 关键字）——中文短语是案例特定措辞，
     v0 把整句中文当作单 token 导致永不命中；
  2. 新增 --anchor 锚点过滤：只评 review_base 匹配本次评审锚点的案例
     （不同锚点的缺陷在本次评审时点可能已修复，跨锚点计分是误罚）。

口径（启发式，仍需人工复核）：
  - 命中：≥2 个标识符在意见卡文本出现，或 1 个标识符 + 溯源文件信号（半命中）；
  - 输出：召回率、逐案例明细（含命中关键词）、意见条数；
  - 局限：不做语义匹配（同义改写漏计），pass^k 一致性需多次运行后对比多份意见卡。
"""
import argparse, io, json, os, re, sys

STOP = set("the and for with not from into void this that when then else return".split())


def keywords(text: str, topn: int = 6) -> list[str]:
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z_0-9]{2,}", text) if w.lower() not in STOP]
    seen: list[str] = []
    for w in words:
        if w not in seen:
            seen.append(w)
    return seen[:topn]


def load_cases(path):
    cases = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def load_reviews(folder, commit_filter=None):
    texts = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md"):
            continue
        if commit_filter and commit_filter[:7] not in name:
            continue
        texts[name] = io.open(os.path.join(folder, name), encoding="utf-8").read()
    return texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviews", default="reviews")
    ap.add_argument("--cases", default="evals/cases.jsonl")
    ap.add_argument("--commit", default=None, help="只评文件名含该 hash 前缀的意见卡")
    ap.add_argument("--anchor", default=None, help="只评 review_base 以该锚点开头的案例（评审范围过滤）")
    args = ap.parse_args()

    cases = load_cases(args.cases)
    if args.anchor:
        cases = [c for c in cases if c["review_base"].startswith(args.anchor)]
        print(f"锚点过滤 {args.anchor}：案例 {len(cases)} 条")

    reviews = load_reviews(args.reviews, args.commit)
    if not reviews:
        print("未找到意见卡（reviews/ 为空或 --commit 过滤无匹配）")
        sys.exit(1)
    blob = "\n".join(reviews.values())
    low = blob.lower()

    hit, miss = [], []
    for c in cases:
        kws = keywords(c["expected_finding"])
        kw_hits = [k for k in kws if k.lower() in low]
        src_hit = any(f.replace("\\", "/").split("/")[-1] in blob for f in c.get("files", []))
        ok = len(kw_hits) >= 2 or (len(kw_hits) >= 1 and src_hit)
        (hit if ok else miss).append((c["id"], kws, kw_hits, src_hit))

    n = len(cases)
    print(f"案例总数 {n} | 命中 {len(hit)} | 启发式召回率 {len(hit)/n:.0%}")
    for cid, kws, kh, sh in miss:
        print(f"  MISS {cid}: 命中 {kh or '无'} / 全组 {kws} | 溯源文件信号 {'有' if sh else '无'}")
    opinion_count = len(re.findall(r"^#{2,3}\s*\[?P[0-3]", blob, re.M))
    print(f"意见卡内分级意见条数 ~{opinion_count}（未被案例覆盖者视为潜在新发现/误报，需人工复核）")


if __name__ == "__main__":
    main()
