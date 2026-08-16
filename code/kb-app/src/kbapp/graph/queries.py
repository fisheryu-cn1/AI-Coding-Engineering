"""图查询（15 §6.2 / D15-9）：CLI 与 Web 共用。

- :func:`topic_subgraph` — 主题 2 跳子图，带 500 节点裁剪
- :func:`node_neighbors` — 节点 1 跳邻域（图谱页单击下钻，R-5）
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

    # 1. 1 跳 Document 集（Topic-:ABOUT_TOPIC→Document；排除墓碑，15 §4.1）
    docs = {
        r["doc_id"]
        for r in store.query(
            "MATCH (t:Topic {name: $topic})<-[:ABOUT_TOPIC]-(d:Document) "
            "WHERE d.valid_to = '' RETURN d.doc_id AS doc_id",
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
    # 节点键顺序必须是 entity_id → section_id → doc_id → name：Section 同时带
    # 父 doc_id 与自身 section_id，doc_id 在前会把 Section 坍缩成父 Document
    # （自环/重复边缺陷，复核 R-10）。
    new_seen = {n["id"] for n in nodes_payload}
    edges_payload: list[dict] = []
    if new_seen:
        for rel in ["CONTAINS_SECTION", "MENTIONS", "ABOUT_TOPIC", "RELATES_TO"]:
            ids_csv = ",".join(repr(n) for n in new_seen)
            cypher_edges = (
                f"MATCH (a)-[r:{rel}]->(b) "
                f"WHERE coalesce(a.entity_id, a.section_id, a.doc_id, a.name) IN [{ids_csv}] "
                f"AND coalesce(b.entity_id, b.section_id, b.doc_id, b.name) IN [{ids_csv}] "
                f"RETURN DISTINCT coalesce(a.entity_id, a.section_id, a.doc_id, a.name) AS src, "
                f"       coalesce(b.entity_id, b.section_id, b.doc_id, b.name) AS dst"
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


_NODE_TYPES = ("Document", "Section", "Entity", "Topic")


def node_neighbors(store: Any, node_id: str, node_type: str, *, limit: int = 100) -> dict:
    """节点 1 跳邻域（图谱页单击下钻；R-5）。

    - Entity：MENTIONS 反向到 Section（及其存活父 Document）、RELATES_TO 双向到其他 Entity
    - Document：CONTAINS_SECTION 到 Section、ABOUT_TOPIC 到 Topic（自身须非墓碑）
    - Section：父 Document（滤墓碑）、MENTIONS 到 Entity
    - Topic：ABOUT_TOPIC 反向到存活 Document
    邻居为 Document 或其父 Document 时一律过滤 ``valid_to`` 墓碑（15 §4.1 / R-2 口径）。
    """
    if node_type not in _NODE_TYPES:
        raise ValueError(f"未知节点类型：{node_type!r}（{_NODE_TYPES}）")
    limit = max(1, min(int(limit), 500))

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add_node(nid: str, label: str, ntype: str) -> None:
        nodes.setdefault(nid, {"id": nid, "label": label or nid, "type": ntype})

    def add_edge(src: str, dst: str, rel: str) -> None:
        edges.append({"src": src, "dst": dst, "rel": rel})

    if node_type == "Entity":
        # MENTIONS 反向：提及该实体的 Section + 存活父 Document（墓碑级联剔除）
        for r in store.query(
            "MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section)-[:MENTIONS]->"
            "(e:Entity {entity_id: $id}) WHERE d.valid_to = '' "
            "RETURN d.doc_id AS did, d.title AS dtitle, "
            "s.section_id AS sid, s.title AS stitle ORDER BY sid",
            {"id": node_id},
        ):
            add_node(r["did"], r["dtitle"], "Document")
            add_node(r["sid"], r["stitle"], "Section")
            add_edge(r["did"], r["sid"], "CONTAINS_SECTION")
            add_edge(r["sid"], node_id, "MENTIONS")
        # RELATES_TO 双向
        for direction, cypher in (
            ("out", "MATCH (e:Entity {entity_id: $id})-[:RELATES_TO]->(o:Entity) "),
            ("in", "MATCH (e:Entity {entity_id: $id})<-[:RELATES_TO]-(o:Entity) "),
        ):
            for r in store.query(
                cypher + "RETURN o.entity_id AS oid, o.name AS oname ORDER BY oid",
                {"id": node_id},
            ):
                add_node(r["oid"], r["oname"], "Entity")
                if direction == "out":
                    add_edge(node_id, r["oid"], "RELATES_TO")
                else:
                    add_edge(r["oid"], node_id, "RELATES_TO")
    elif node_type == "Document":
        # 中心文档自身为墓碑时视为不存在（读路径只看 valid_to）
        live = store.query(
            "MATCH (d:Document {doc_id: $id}) WHERE d.valid_to = '' RETURN d.doc_id AS did",
            {"id": node_id},
        )
        if live:
            for r in store.query(
                "MATCH (d:Document {doc_id: $id})-[:CONTAINS_SECTION]->(s:Section) "
                "RETURN s.section_id AS sid, s.title AS stitle ORDER BY sid",
                {"id": node_id},
            ):
                add_node(r["sid"], r["stitle"], "Section")
                add_edge(node_id, r["sid"], "CONTAINS_SECTION")
            for r in store.query(
                "MATCH (d:Document {doc_id: $id})-[:ABOUT_TOPIC]->(t:Topic) "
                "RETURN t.name AS tname ORDER BY tname",
                {"id": node_id},
            ):
                add_node(r["tname"], r["tname"], "Topic")
                add_edge(node_id, r["tname"], "ABOUT_TOPIC")
    elif node_type == "Section":
        for r in store.query(
            "MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section {section_id: $id}) "
            "WHERE d.valid_to = '' RETURN d.doc_id AS did, d.title AS dtitle",
            {"id": node_id},
        ):
            add_node(r["did"], r["dtitle"], "Document")
            add_edge(r["did"], node_id, "CONTAINS_SECTION")
        for r in store.query(
            "MATCH (s:Section {section_id: $id})-[:MENTIONS]->(e:Entity) "
            "RETURN e.entity_id AS eid, e.name AS ename ORDER BY eid",
            {"id": node_id},
        ):
            add_node(r["eid"], r["ename"], "Entity")
            add_edge(node_id, r["eid"], "MENTIONS")
    else:  # Topic
        for r in store.query(
            "MATCH (d:Document)-[:ABOUT_TOPIC]->(t:Topic {name: $id}) "
            "WHERE d.valid_to = '' RETURN d.doc_id AS did, d.title AS dtitle ORDER BY did",
            {"id": node_id},
        ):
            add_node(r["did"], r["dtitle"], "Document")
            add_edge(r["did"], node_id, "ABOUT_TOPIC")

    # 规模保护：确定性裁剪（按 id 排序），边随可见节点过滤（中心节点恒可见）
    keep = {nid for nid, _n in sorted(nodes.items())[:limit]}
    keep.add(node_id)
    return {
        "id": node_id,
        "type": node_type,
        "nodes": [nodes[nid] for nid in sorted(keep) if nid != node_id],
        "edges": [e for e in edges if e["src"] in keep and e["dst"] in keep],
        "truncated": len(nodes) > limit,
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


__all__ = ["entity_path", "node_neighbors", "topic_subgraph"]
