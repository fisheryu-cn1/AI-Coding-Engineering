# -*- coding: utf-8 -*-
"""score_review.py —— 评审意见卡评估工具（v2：评分 + 配对合一）。

子命令：
  score —— 意见卡 × 标注案例集（evals/cases.jsonl）：
           · 口径A 启发式上界（v1 保留：expected_finding 的 ASCII 标识符 ≥2 命中，或 1 个 + 文件信号）；
           · 口径B 签名口径（意见"溯源"文件与案例 files 规范化路径重合）；
           · 错误排除检测：案例对象文件出现在"未发现问题的检查项"节 → 错误排除嫌疑（人工核对，
             对应"测试只能作为行为记录"反例信号）；
           · 未命中案例输出同域候选清单（与 expected_finding 标识符重合 ≥1 的意见标题）——
             B1"待确认问题"人工归类的输入，非自动判定。
  pair  —— 意见卡 × 意见卡：意见配对与 pass^k 近似（原 compare_runs.py 并入，该脚本已删除）。

v1→v2（2026-08-19 第 8 场；依据第 6 场签名伪影诊断 + P2 阶段评审决策）：
  1. 意见身份 =（规则编号集合 ∪ 规范化文件路径集合）稳定标识——级别漂移、措辞改写、
     标题重排不再影响配对（run7/run8 人工配对已验证该口径双向 100%）；
  2. 意见解析按意见卡模板格式契约：`### [P0-3]` 标题 + 单行"- 类型/溯源/维度"字段，
     溯源中"路径:行号"为机器可读写法；
  3. compare_runs.py 并入 pair 子命令；
  4. 新增错误排除检测与 B1 未命中工作清单。

用法：
  python scripts/score_review.py score --reviews reviews --cases evals/cases.jsonl \\
         [--commit f62f287] [--anchor f62f287] [--json out.json]
  python scripts/score_review.py pair reviews/A.md reviews/B.md [...]
"""
import argparse, io, itertools, json, os, re, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

STOP = set("the and for not from into void this that when then else return with".split())
PATH_RE = re.compile(
    r"[\w./\\-]+\.(?:py|pyi|ts|js|mjs|cjs|html|htm|css|md|json|toml|yaml|yml|txt|sql|sh|cfg|ini)"
    r"(?::\d+(?:[-\u2013]\d+)?)?"
)
RULE_RE = re.compile(r"\bRR-\d+[a-c]?\b")
OP_RE = re.compile(r"^###\s*\[(P[0-3])\]\s*(.+?)\s*$", re.M)
TITLE_STOP = {"graph", "design", "review", "commit", "python", "static", "html",
              "console", "version", "default", "config"}


def title_ids(title):
    """标题标识符（≥5 字符，剔通用词）——配对的辅证判据：
    文件粒度签名区分不了同一文件内的多个缺陷，需标题共享具体标识符才认作同一问题。"""
    return {w for w in re.findall(r"[a-z_][a-z_0-9]{4,}", title.lower())
            if w not in TITLE_STOP}


def keywords(text, topn=6):
    """v1 口径：expected_finding 中的 ASCII 标识符（前 topn 个，去重）。"""
    words, seen = [], []
    for w in re.findall(r"[A-Za-z_][A-Za-z_0-9]{2,}", text):
        if w.lower() not in STOP and w not in seen:
            seen.append(w)
    return seen[:topn]


def normalize_path(p):
    p = re.sub(r"[`'\"]", "", p)
    p = re.sub(r":[0-9][0-9\-–]*$", "", p)
    return p.replace("\\", "/").strip().lower()


SELF_ASSET_RE = re.compile(r"review-rules|opinion-card-template|issue-type-guide|rule-revision-worksheet")


def extract_paths(text):
    """从文本提取评审对象文件路径；剔除对 skill 自身资产（规则文档/模板）的引用——
    那些是评审依据而非评审对象，混入签名会虚增跨意见相似度。"""
    return sorted({normalize_path(p) for p in PATH_RE.findall(text)
                   if not SELF_ASSET_RE.search(p)})


def sig_key(path):
    """路径规范化键：取末两段（目录/文件）。
    意见卡对同一文件的记法不一（仓库全路径 / 包内相对路径 / 带锚点前缀的 git show 记法），
    末两段在单仓库场景下是稳定的等价类；单段路径原样保留。"""
    parts = [p for p in path.split("/") if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else path


def paths_match(a, b):
    ka, kb = sig_key(normalize_path(a)), sig_key(normalize_path(b))
    return ka == kb


def files_match(fs_a, fs_b):
    ka = {sig_key(normalize_path(f)) for f in fs_a}
    kb = {sig_key(normalize_path(f)) for f in fs_b}
    return bool(ka & kb)


def load_card(path):
    text = io.open(path, encoding="utf-8").read()
    mo = re.search(r"^#{2,3}\s*意见.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    sec_ops = mo.group(1) if mo else ""
    mn = re.search(r"^##\s*未发现.*?$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    sec_nd = (mn.group(1) if mn else "")
    heads = list(OP_RE.finditer(sec_ops))
    opinions = []
    for i, m in enumerate(heads):
        body = sec_ops[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(sec_ops)]
        # 兼容两种溯源字段：契约式"- 溯源：<路径:行号> + ..."与合并式"- 溯源 + 证据（…）："
        src = re.search(r"^-\s*溯源[^：:\n]*[：:]\s*(.+)$", body, re.M)
        typ = re.search(r"^-\s*类型[：:]\s*(.+)$", body, re.M)
        dim = re.search(r"^-\s*维度[：:]\s*(.+)$", body, re.M)
        src_line = src.group(1).strip() if src else ""
        files = extract_paths(src_line)
        if not files:
            # 容错（登记契约偏离）：合并式溯源的路径在证据代码块内——扫意见块全文提取
            files = extract_paths(body)
        rules = sorted(set(RULE_RE.findall((dim.group(1) if dim else "") + " " + m.group(2))))
        keys = sorted({sig_key(f) for f in files})
        opinions.append({
            "sev": m.group(1),
            "title": m.group(2),
            "type": typ.group(1).split("（")[0].strip() if typ else "",
            "files": files,
            "keys": keys,
            "rules": rules,
        })
    return {"path": path, "text": text, "opinions": opinions, "nd": sec_nd}


def signature(op):
    """意见稳定标识：规则编号 ∪ 文件路径规范化键（与级别/措辞/标题无关）。"""
    return frozenset(op["keys"]) | set(op["rules"])


def load_cases(path):
    cases = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


# ---------------------------------------------------------------- score ----

def cmd_score(args):
    cases = load_cases(args.cases)
    if args.anchor:
        cases = [c for c in cases if c["review_base"].startswith(args.anchor)]
        print(f"锚点过滤 {args.anchor}：案例 {len(cases)} 条")
    names = [n for n in sorted(os.listdir(args.reviews))
             if n.endswith(".md") and (not args.commit or args.commit in n)]
    cards = [load_card(os.path.join(args.reviews, n)) for n in names]
    if not cards:
        print("未找到意见卡（reviews/ 为空或 --commit 过滤无匹配）")
        sys.exit(1)
    low = "\n".join(c["text"] for c in cards).lower()
    nd_low = "\n".join(c["nd"] for c in cards).lower()
    all_ops = [op for c in cards for op in c["opinions"]]
    covered = set()

    n_a = n_b = 0
    rows, b1 = [], []
    for case in cases:
        kws = keywords(case["expected_finding"])
        kw_hits = [k for k in kws if k.lower() in low]
        sig_ops = [op for op in all_ops if files_match(case.get("files", []), op["files"])]
        hit_a = len(kw_hits) >= 2 or (len(kw_hits) >= 1 and bool(sig_ops))
        hit_b = bool(sig_ops)
        # 错误排除嫌疑只在签名未命中时有意义：命中案例的文件同时出现在"未发现"节
        # 多为清单枚举（如 RR-4 写入点清单），不构成"把缺陷排除掉"
        acquit = (not hit_b) and any(
            f.replace("\\", "/").split("/")[-1].lower() in nd_low
            for f in case.get("files", []))
        n_a += hit_a
        n_b += hit_b
        for op in sig_ops:
            covered.add(id(op))
        row = {
            "id": case["id"],
            "heuristic": hit_a, "signature": hit_b, "acquittal_suspect": acquit,
            "kw_hits": kw_hits, "sig_opinions": [op["title"] for op in sig_ops],
        }
        rows.append(row)
        if hit_b:
            note = f"HIT(签名×{len(sig_ops)})"
        elif hit_a:
            note = "HIT(仅启发式——待语义核定)"
        else:
            note = "MISS"
        if not hit_b:
            # B1 人工归类输入：与 expected_finding 标识符重合 ≥1 的意见（同域候选，非自动判定）
            cand = [op["title"] for op in all_ops
                    if set(k.lower() for k in kws) & set(
                        re.findall(r"[a-z_][a-z_0-9]{2,}", op["title"].lower()))]
            if cand:
                row["same_domain_candidates"] = cand
                b1.append((case["id"], cand))
        flag = "  ⚠对象见'未发现'节（错误排除嫌疑）" if acquit else ""
        print(f"  {note:14s} {case['id']:8s} kw={kw_hits or '无'}{flag}")

    k = len(all_ops)
    print(f"\n案例 {len(cases)} | 卡 {len(cards)} 张 | 意见 {k} 条")
    print(f"口径A 启发式上界：{n_a}/{len(cases)}（{n_a/len(cases):.0%}）")
    print(f"口径B 签名（文件重合）：{n_b}/{len(cases)}（{n_b/len(cases):.0%}）")
    ac = sum(1 for r in rows if r["acquittal_suspect"])
    if ac:
        print(f"错误排除嫌疑（对象出现在'未发现'节）：{ac} 条——须人工核对")
    if b1:
        print(f"\nB1 待语义核定/未命中工作清单（同域候选＝与 expected_finding 标识符重合 ≥1，供人工归类，非自动判定）：")
        for cid, cand in b1:
            print(f"  {cid}:")
            for t in cand:
                print(f"    - {t[:90]}")
    print(f"\n意见覆盖：命中占用 {len(covered)} 条；未覆盖 {k - len(covered)} 条为潜在新发现（需人工复核）")
    if args.json:
        io.open(args.json, "w", encoding="utf-8").write(json.dumps(
            {"rows": rows, "summary": {"cases": len(cases), "heuristic": n_a, "signature": n_b,
                                        "opinions": k, "covered": len(covered)}},
            ensure_ascii=False, indent=1))


# ----------------------------------------------------------------- pair ----

def cmd_pair(args, paths):
    cards = [load_card(p) for p in paths]
    for c in cards:
        sev = {}
        typ = {}
        for op in c["opinions"]:
            sev[op["sev"]] = sev.get(op["sev"], 0) + 1
            if op["type"]:
                typ[op["type"]] = typ.get(op["type"], 0) + 1
        print(f"{os.path.basename(c['path'])}: {len(c['opinions'])} 意见 "
              f"{dict(sorted(sev.items()))} | 类型 {dict(sorted(typ.items()))}")

    for a, b in itertools.combinations(cards, 2):
        pairs = []
        for i, oa in enumerate(a["opinions"]):
            for j, ob in enumerate(b["opinions"]):
                sa, sb = signature(oa), signature(ob)
                if sa and sb:
                    # 重叠系数（交集 / 较小一方）：两次评审对同一问题常一条写得宽、一条拆得窄，
                    # 用 Jaccard（交集 / 并集）会因并集变大而把真实配对拉到阈值之下
                    ov = len(sa & sb) / min(len(sa), len(sb))
                    if ov > 0:
                        pairs.append((ov, i, j))
        pairs.sort(reverse=True)
        used_a, used_b, matched = set(), set(), []
        for ov, i, j in pairs:
            if i in used_a or j in used_b:
                continue
            oa, ob = a["opinions"][i], b["opinions"][j]
            # 双判据（精确率优先）：签名重叠 ≥0.5 且标题共享具体标识符。
            # 文件粒度签名区分不了同文件多缺陷；无标识符佐证的一律进人工核验清单，
            # 宁可少自动配对，不可错配（错配会无声污染 pass^k 统计——签名 v1 的教训）。
            if ov >= 0.5 and title_ids(oa["title"]) & title_ids(ob["title"]):
                used_a.add(i)
                used_b.add(j)
                matched.append((i, j, ov))
        na, nb = len(a["opinions"]), len(b["opinions"])
        print(f"\n{os.path.basename(a['path'])} × {os.path.basename(b['path'])}"
              f"（配对阈值 重叠系数≥0.5，签名=规则∪文件键）：")
        print(f"  配对 {len(matched)} | A 侧配对率 {len(used_a)}/{na}（{len(used_a)/na:.0%}）"
              f" | B 侧配对率 {len(used_b)}/{nb}（{len(used_b)/nb:.0%}）")
        drift = [(i, j) for i, j, _ in matched
                 if a["opinions"][i]["sev"] != b["opinions"][j]["sev"]]
        print(f"  级别漂移：{len(drift)} 对", end="")
        for i, j in drift[:6]:
            print(f"  [{a['opinions'][i]['sev']}→{b['opinions'][j]['sev']}] "
                  f"{a['opinions'][i]['title'][:40]}", end="；")
        print()
        print("  配对明细（供人工核验）：")
        for i, j, jj in sorted(matched, key=lambda x: -x[2]):
            print(f"    OV={jj:.2f} [{a['opinions'][i]['sev']}|{b['opinions'][j]['sev']}] "
                  f"{a['opinions'][i]['title'][:44]} ≈ {b['opinions'][j]['title'][:44]}")
        for side, used, ops in (("A", used_a, a["opinions"]), ("B", used_b, b["opinions"])):
            un = [op for idx, op in enumerate(ops) if idx not in used]
            if un:
                print(f"  {side} 侧未配对 {len(un)} 条：")
                for op in un[:8]:
                    print(f"    - [{op['sev']}] {op['title'][:80]}")

    if len(cards) >= 3:
        sets = [{signature(op) for op in c["opinions"] if signature(op)} for c in cards]
        common = set.intersection(*sets)
        union = set.union(*sets)
        print(f"\n全卡共有签名（≈pass^{len(cards)} 命中面，按签名精确相等）："
              f"{len(common)} / 并集 {len(union)} = {len(common)/max(len(union),1):.0%}")


def main():
    ap = argparse.ArgumentParser(description="评审意见卡评估工具 v2（score/pair）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score", help="意见卡 × 标注案例集召回评分")
    s.add_argument("--reviews", default="reviews")
    s.add_argument("--cases", default="evals/cases.jsonl")
    s.add_argument("--commit", default=None, help="只评文件名含该 hash 前缀的意见卡")
    s.add_argument("--anchor", default=None, help="只评 review_base 以该锚点开头的案例")
    s.add_argument("--json", default=None, help="结果写出 JSON 文件")
    p = sub.add_parser("pair", help="意见卡 × 意见卡配对（pass^k 近似）")
    p.add_argument("cards", nargs="+", help="两张及以上意见卡路径")
    args = ap.parse_args()
    if args.cmd == "score":
        cmd_score(args)
    else:
        cmd_pair(args, args.cards)


if __name__ == "__main__":
    main()
