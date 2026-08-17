# -*- coding: utf-8 -*-
"""score_review.py —— 评审意见卡 vs 评估标注集的启发式召回评分器（v0）。

用法：
  python scripts/score_review.py --reviews reviews/ --cases evals/cases.jsonl [--commit <hash>]

口径（启发式 v0，见 evals/README.md）：
  - 命中判定：案例的 expected_finding 关键词组在对应意见卡文本（含标题/溯源/证据）中出现
    （关键词组 = 从 expected_finding 提取的 ≥2 个领域词，见 KEYWORD_STOPWORDS）；
  - 输出：召回率、逐案例 命中/未命中 明细、误报粗计（意见卡中未被任何案例覆盖的意见条数）；
  - 局限：不做语义匹配（同义改写漏计），pass^k 一致性需多次运行后用本脚本对比多份意见卡。
"""
import argparse, io, json, os, re, sys

STOP = set("the a of in to和与的在中对由被为 on for with is are not no 或 及 其 该 此 将 把 从".split())

def keywords(text: str, topn: int = 4):
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z_0-9]{2,}|[\u4e00-\u9fff]{2,}", text) if w.lower() not in STOP]
    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    rank = sorted(freq, key=lambda w: -freq[w])[:topn]
    return rank

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
        key = name
        if commit_filter and commit_filter[:7] not in name:
            continue
        texts[key] = io.open(os.path.join(folder, name), encoding="utf-8").read()
    return texts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviews", default="reviews")
    ap.add_argument("--cases", default="evals/cases.jsonl")
    ap.add_argument("--commit", default=None, help="只评与该 commit 相关的意见卡（按文件名包含 hash 前缀匹配）")
    args = ap.parse_args()

    cases = load_cases(args.cases)
    reviews = load_reviews(args.reviews, args.commit)
    if not reviews:
        print("未找到意见卡（reviews/ 为空或 --commit 过滤无匹配）"); sys.exit(1)
    blob = "\n".join(reviews.values())

    hit, miss = [], []
    for c in cases:
        kws = keywords(c["expected_finding"])
        ok = all(k.lower() in blob.lower() for k in kws) if kws else False
        # 宽松口径：溯源 file 若在意见卡出现也算半个信号
        src_hit = any(f.replace("\\", "/").split("/")[-1] in blob for f in c.get("files", []))
        (hit if ok else miss).append((c["id"], kws, src_hit))

    n = len(cases)
    print(f"案例总数 {n} | 命中 {len(hit)} | 严格召回率 {len(hit)/n:.0%}")
    for cid, kws, sh in miss:
        print(f"  MISS {cid}: 关键词 {kws} | 溯源文件信号 {'有(半命中)' if sh else '无'}")
    opinion_count = len(re.findall(r"^#{2,3}\s*\[?P[0-3]", blob, re.M))
    print(f"意见卡内分级意见条数 ~{opinion_count}（未被案例覆盖者视为潜在误报，需人工复核）")

if __name__ == "__main__":
    main()
