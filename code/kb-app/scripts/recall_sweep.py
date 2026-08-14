"""M3 召回抽检执行器（11 §10-7 DoD；非 pytest，手工/CI 运行）。

用法（在 code/kb-app 下）：

    uv run python scripts/recall_sweep.py            # 按当前环境（有 key 即在线档）
    uv run python scripts/recall_sweep.py --offline  # 强制离线档（不挂 LLM）

读取 tests/integration/fixtures/recall_queries.yaml，对每条查询调用
``kbapp.retrieve.search``（mode=hybrid, limit=10），统计：

- success@10：top-10 含 ≥1 篇 expect 文档的查询占比（在线档门槛 ≥80%）
- recall@10：每条查询 top-10 去重 doc 命中 expect 的比例，附记参考

退出码：在线档 success@10 < 0.8 → 1；离线档只记录、不作门槛，恒 0。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from kbapp.cli._common import resolve_data_dir
from kbapp.core.config import load_config
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry
from kbapp.llm import get_llm_or_none
from kbapp.retrieve import search

FIXTURE = (
    Path(__file__).resolve().parent.parent
    / "tests"
    / "integration"
    / "fixtures"
    / "recall_queries.yaml"
)
THRESHOLD = 0.8


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="强制离线档（不挂 LLM）")
    ap.add_argument("--json", type=Path, default=None, help="明细输出 JSON 路径")
    args = ap.parse_args()

    queries = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))["queries"]
    data_dir = resolve_data_dir(None)
    paths = DataPaths.from_data_dir(data_dir)
    cfg = load_config(paths.config_path)
    registry = Registry(paths.registry_db)
    registry.initialize()
    llm = None if args.offline else get_llm_or_none(cfg)
    tier = "offline" if llm is None else "online"

    rows: list[dict] = []
    for q in queries:
        result = search(registry, cfg, q["query"], mode="hybrid", limit=10, llm=llm)
        doc_ids = list(dict.fromkeys(h.doc_id for h in result.hits))  # 去重保序
        expect = set(q["expect"])
        hit_set = expect & set(doc_ids)
        success = bool(hit_set)
        recall = len(hit_set) / len(expect) if expect else 0.0
        rows.append(
            {
                "query": q["query"],
                "type": q["type"],
                "expect": sorted(expect),
                "top10": doc_ids,
                "success": success,
                "recall@10": round(recall, 3),
            }
        )

    n = len(rows)
    n_success = sum(r["success"] for r in rows)
    success_at_10 = n_success / n if n else 0.0
    mean_recall = sum(r["recall@10"] for r in rows) / n if n else 0.0

    print(f"\n== 召回抽检（{tier} 档，{n} 条查询）==")
    for r in rows:
        mark = "OK " if r["success"] else "MISS"
        print(f"[{mark}] {r['type']:<12} {r['query']!r}  recall@10={r['recall@10']}")
        if not r["success"]:
            print(f"       expect={r['expect']}  top10={r['top10']}")
    print(f"\nsuccess@10 = {n_success}/{n} = {success_at_10:.1%}（在线档门槛 ≥{THRESHOLD:.0%}）")
    print(f"mean recall@10 = {mean_recall:.1%}（附记，不作门槛）")

    if args.json:
        args.json.write_text(
            json.dumps(
                {
                    "tier": tier,
                    "success@10": success_at_10,
                    "mean_recall@10": mean_recall,
                    "rows": rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"明细已写入 {args.json}")

    if tier == "online" and success_at_10 < THRESHOLD:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
