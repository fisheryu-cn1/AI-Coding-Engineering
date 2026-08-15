"""图查询（15 §6.2 / D15-9）：CLI 与 Web 共用。

- :func:`topic_subgraph` — 主题 2 跳子图，带 500 节点裁剪
- :func:`entity_path` — 两实体最短路径（max_hops=3）
"""

from __future__ import annotations

from typing import Any

# 边类型枚举（按 15 §3.2 四类边）
_SUBGRAPH_RELS = "|".join(
    [
        "CONTAINS_SECTION",
        "MENTIONS",
        "ABOUT_TOPIC",
        "RELATES_TO",
    ]
)


def topic_subgraph(
    store: Any,
    topic: str,
    *,
    hops: int = 2,
    max_nodes: int = 500,
) -> dict:
    """从 Topic 出发变长遍历 N 跳，超 ``max_nodes`` 截断并置 ``truncated``。"""
    hops = max(1, min(int(hops), 3))
    max_nodes = max(1, int(max_nodes))

    # 1. 1 跳 Document 集（Topic-:ABOUT_TOPIC→Document）
    docs = {
        r["doc_id"]
        for r in store.query(
            "MATCH (t:Topic {name: $topic})<-[:ABOUT_TOPIC]-(d:Document) RETURN d.doc_id AS doc_id",
            {"topic": topic},
        )
    }
    # 2. Section 集（顺 Document 走 CONTAINS_SECTION）
    section_ids: set[str] = set()
    if docs:
        docs_csv = ",".join(repr(d) for d in docs)
        for r in store.query(
            f"MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section) WHERE d.doc_id IN [{docs_csv}] "
            f"RETURN s.section_id AS sid",
            {},
        ):
            section_ids.add(r["sid"])
    # 3. Entity 集（顺 Section 走 MENTIONS）
    entity_ids: set[str] = set()
    if section_ids:
        secs_csv = ",".join(repr(s) for s in section_ids)
        for r in store.query(
            f"MATCH (s:Section)-[:MENTIONS]->(e:Entity) WHERE s.section_id IN [{secs_csv}] "
            f"RETURN e.entity_id AS eid",
            {},
        ):
            entity_ids.add(r["eid"])
    # 4. 跳数扩展（hops=2 时一并拉 Entity 之间的 RELATES_TO 邻居）
    if hops >= 2 and entity_ids:
        ents_csv = ",".join(repr(e) for e in entity_ids)
        for r in store.query(
            f"MATCH (a:Entity)-[:RELATES_TO]-(b:Entity) "
            f"WHERE a.entity_id IN [{ents_csv}] AND b.entity_id IN [{ents_csv}] "
            f"RETURN DISTINCT b.entity_id AS eid",
            {},
        ):
            entity_ids.add(r["eid"])

    # 5. 装配 payload
    nodes_payload: list[dict] = [
        {"id": topic, "label": topic, "type": "Topic", "dist": 0},
    ]
    seen: set[str] = {topic}
    for d in sorted(docs):
        if d in seen:
            continue
        nodes_payload.append({"id": d, "label": d, "type": "Document", "dist": 1})
        seen.add(d)
    for s in sorted(section_ids):
        if s in seen:
            continue
        nodes_payload.append({"id": s, "label": s, "type": "Section", "dist": 2})
        seen.add(s)
    for e in sorted(entity_ids):
        if e in seen:
            continue
        nodes_payload.append({"id": e, "label": e, "type": "Entity", "dist": 2})
        seen.add(e)

    truncated = len(nodes_payload) > max_nodes
    if truncated:
        nodes_payload = nodes_payload[:max_nodes]

    # 6. 边：在可见节点集内
    new_seen = {n["id"] for n in nodes_payload}
    edges_payload: list[dict] = []
    if new_seen:
        for rel in ["CONTAINS_SECTION", "MENTIONS", "ABOUT_TOPIC", "RELATES_TO"]:
            ids_csv = ",".join(repr(n) for n in new_seen)
            cypher_edges = (
                f"MATCH (a)-[r:{rel}]->(b) "
                f"WHERE coalesce(a.entity_id, a.doc_id, a.section_id, a.name) IN [{ids_csv}] "
                f"AND coalesce(b.entity_id, b.doc_id, b.section_id, b.name) IN [{ids_csv}] "
                f"RETURN coalesce(a.entity_id, a.doc_id, a.section_id, a.name) AS src, "
                f"       coalesce(b.entity_id, b.doc_id, b.section_id, b.name) AS dst"
            )
            for r in store.query(cypher_edges, {}):
                if r["src"] in new_seen and r["dst"] in new_seen:
                    edges_payload.append({"src": r["src"], "dst": r["dst"], "rel": rel})
    return {
        "nodes": nodes_payload,
        "edges": edges_payload,
        "truncated": truncated,
        "max_nodes": max_nodes,
    }


def entity_path(store: Any, src: str, dst: str, *, max_hops: int = 3) -> dict:
    """两实体最短路径（max_hops=3 封顶）。"""
    max_hops = max(1, min(int(max_hops), 3))
    paths = store.shortest_path(("Entity", src), ("Entity", dst), max_hops=max_hops)
    return {
        "src": src,
        "dst": dst,
        "max_hops": max_hops,
        "paths": paths,
    }


__all__ = ["entity_path", "topic_subgraph"]
