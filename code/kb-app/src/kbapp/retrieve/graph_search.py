"""Graph-based related/compare queries (15 §5.1).

Both functions are read-only and never fall back to M3 document-level
behavior on graph failure — the CLI checks graph availability beforehand
and reports a clear error (per 15 §5.1 regressive semantic change).
"""

from __future__ import annotations

from typing import Any


def graph_related(
    store: Any,
    *,
    target: str,
    target_type: str,
    hops: int = 1,
    limit: int = 10,
) -> dict:
    """N 跳邻域（默认 1 跳，上限 3；MCP 05 §6 kb_related 契约）。

    Returns ``{"related": [{"id", "type", "relation"}, ...]}``。

    实现注意：lbug 不支持 RETURN 子句里的 list comprehension 与 type(rel)，
    故先抓 RAW 邻域，Python 层完成去重 / 计数。
    """
    hops = max(1, min(int(hops), 3))
    pk = {
        "Entity": "entity_id",
        "Document": "doc_id",
        "Section": "section_id",
        "Topic": "name",
    }.get(target_type, "entity_id")
    # 墓碑过滤（15 §4.1 软删由查询层负责）：终点为墓碑 Document 直接剔除；
    # Section 自身无 valid_to，经父 Document（Section.doc_id）级联剔除。
    # 节点键顺序必须 entity_id → section_id → doc_id → name：Section 同时带
    # 父 doc_id 与自身 section_id，doc_id 在前会把 Section 坍缩成父 Document
    # （复核 R-10）；墓碑判定另用 parent_doc（n.doc_id），与 id 互不干扰。
    # labels(n) 在变长 MATCH 下不可靠（lbug 返回空串），type 由主键列在
    # Python 层推导（复核 R-10 附随）。
    tombstoned = {
        r["doc_id"]
        for r in store.query(
            "MATCH (d:Document) WHERE d.valid_to <> '' RETURN d.doc_id AS doc_id"
        )
    }
    cypher = (
        f"MATCH (a:{target_type} {{{pk}: $target}}) "
        f"MATCH (a)-[r*..{hops}]-(n) "
        f"WHERE n <> a "
        f"RETURN n.entity_id AS eid, n.section_id AS sid, "
        f"       n.doc_id AS did, n.name AS nm, "
        f"       coalesce(n.doc_id, '') AS parent_doc, "
        f"       length(r) AS dist "
        f"ORDER BY dist ASC LIMIT $limit"
    )
    rows = store.query(cypher, {"target": target, "limit": int(limit)})
    seen = set()
    out: list[dict] = []
    for r in rows:
        if r["eid"]:
            rid, rtype = r["eid"], "Entity"
        elif r["sid"]:
            rid, rtype = r["sid"], "Section"
        elif r["did"]:
            rid, rtype = r["did"], "Document"
        else:
            rid, rtype = r["nm"], "Topic"
        if rid in tombstoned or r["parent_doc"] in tombstoned:
            continue  # 墓碑 Document 及其 Section（父文档级联）
        if rid in seen or rid == target:
            continue
        seen.add(rid)
        out.append(
            {
                "id": rid,
                "type": rtype,
                "relation": "",  # lbug 不支持 type(rel)，UI 需要时再 fetch
            }
        )
    return {"related": out}


def graph_compare(
    store: Any,
    *,
    concept: str,
    doc_ids: list[str] | None = None,
    limit: int = 5,
) -> dict:
    """Concept 在 N 文档/实体间的 RELATES_TO 对照（05 §6 kb_compare 契约）。

    Returns ``{"rows": [{"kind", "weight", "evidence_section_id", "src", "dst"}, ...]}``。
    """
    params: dict[str, Any] = {"concept": concept, "limit": int(limit)}
    # doc_ids 限定：lbug 暂不支持 EXISTS 子查询 + 多 MATCH 联合；先按 concept 宽查，
    # 前端按 doc_ids 过滤显示（Task 19 词云/侧栏回填时拉具体 doc_id 范围）。
    cypher = (
        "MATCH (a:Entity {entity_id: $concept})-[r:RELATES_TO]-(b:Entity) "
        "RETURN r.kind AS kind, "
        "       a.entity_id AS src, b.entity_id AS dst, "
        "       coalesce(r.weight, 1.0) AS weight, "
        "       coalesce(r.evidence_section_id, '') AS evidence_section_id "
        "ORDER BY weight DESC LIMIT $limit"
    )
    rows = store.query(cypher, params)
    return {
        "rows": [
            {
                "kind": r["kind"],
                "src": r["src"],
                "dst": r["dst"],
                "weight": float(r["weight"]) if r["weight"] is not None else 1.0,
                "evidence_section_id": r["evidence_section_id"],
            }
            for r in rows
        ]
    }


__all__ = ["graph_compare", "graph_related"]
