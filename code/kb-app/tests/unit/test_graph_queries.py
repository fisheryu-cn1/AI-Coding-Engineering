"""Unit tests for graph queries (15 §6.2 / D15-9)."""

from __future__ import annotations

import pytest

ladybug = pytest.importorskip("ladybug")


def _seed_full_graph(default_config, registry, paths):
    """造图：Doc D1 + Topic T1 + Entity E1，Doc→Topic, Section→Entity。"""
    from kbapp.core.registry import update_file_fields, upsert_file
    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure

    payload = {
        "sha256": "s",
        "path": "x.md",
        "format": "md",
        "parser": "markdown",
        "structure": "headers",
        "full_text": "intro",
        "sections": [
            {"section_path": "1", "level": 1, "title": "Intro", "page_range": "", "text": "intro"},
        ],
        "warnings": [],
        "chunks": [],
        "extracted_at": "2026-08-15",
    }
    (paths.extracted_dir / "s.json").write_text(__import__("json").dumps(payload), encoding="utf-8")
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D1",
            path="x.md",
            sha256="s",
            mtime=0,
            corpus="references",
            doc_type="paper",
            extract_status="ok",
            status="active",
            title="Paper",
            topic="T1",
        )
        update_file_fields(conn, "D1", topic="T1")

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        sync_document_structure(store, registry, paths, "D1")
        store.upsert_nodes(
            "Entity",
            [
                {
                    "entity_id": "Method:rag",
                    "name": "RAG",
                    "type": "Method",
                    "aliases": "",
                    "description": "",
                }
            ],
        )
        store.upsert_edges(
            "MENTIONS",
            [{"src": "D1#1", "dst": "Method:rag", "weight": 1}],
        )
    finally:
        store.close()


def test_topic_subgraph_collects_nodes(default_config, registry, paths) -> None:
    """topic_subgraph 收集主题 + 邻接 Document/Section/Entity。"""
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import make_graph_store, topic_subgraph

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = topic_subgraph(store, "T1", hops=2, max_nodes=500)
    finally:
        store.close()

    types = {n["type"] for n in result["nodes"]}
    assert "Topic" in types
    assert "Document" in types
    assert "Entity" in types
    assert result["truncated"] is False


def test_topic_subgraph_truncates(default_config, registry, paths) -> None:
    """超 max_nodes 截断并置 truncated=True。"""
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import make_graph_store, topic_subgraph

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        # 注入 600 个 dummy Entity 增加规模
        entities = [
            {
                "entity_id": f"Concept:e{i}",
                "name": f"E{i}",
                "type": "Concept",
                "aliases": "",
                "description": "",
            }
            for i in range(600)
        ]
        store.upsert_nodes("Entity", entities)
        for i in range(600):
            store.upsert_edges(
                "RELATES_TO",
                [
                    {
                        "src": "Concept:e0",
                        "dst": f"Concept:e{i}",
                        "kind": "uses",
                        "weight": 1.0,
                        "evidence_section_id": "",
                    }
                ],
            )
    finally:
        store.close()

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        # hops=2 应该能遍历到 600 个 Entity
        result = topic_subgraph(store, "T1", hops=2, max_nodes=500)
    finally:
        store.close()

    if len(result["nodes"]) >= 500:
        assert result["truncated"] is True
        assert len(result["nodes"]) <= 500


def test_entity_path_within_max_hops(default_config, registry, paths) -> None:
    """shortest_path 返回至少 1 条或空（max_hops 之外）。"""
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import entity_path, make_graph_store

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = entity_path(store, "Method:rag", "Method:rag", max_hops=3)
    finally:
        store.close()
    assert result["src"] == "Method:rag"
    assert result["dst"] == "Method:rag"
    assert result["max_hops"] == 3
    # 同一节点应当返回 0 长度或空
    assert isinstance(result["paths"], list)


def test_topic_subgraph_excludes_tombstoned_documents(default_config, registry, paths) -> None:
    """R-2：墓碑 Document 不进 topic_subgraph；其 Section / 独有实体随父级联剔除。"""
    import json

    _seed_full_graph(default_config, registry, paths)  # D1 topic T1, D1#1→rag

    from kbapp.core.registry import update_file_fields, upsert_file
    from kbapp.graph import make_graph_store, topic_subgraph
    from kbapp.graph.sync import sync_document_structure

    # D2 同 topic T1，D2#1 提及 rag + 独有实体 dead
    payload2 = {
        "sha256": "s2",
        "path": "y.md",
        "format": "md",
        "parser": "markdown",
        "structure": "headers",
        "full_text": "dead end",
        "sections": [
            {"section_path": "1", "level": 1, "title": "Body", "page_range": "", "text": "dead"},
        ],
        "warnings": [],
        "chunks": [],
        "extracted_at": "2026-08-15",
    }
    (paths.extracted_dir / "s2.json").write_text(json.dumps(payload2), encoding="utf-8")
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D2",
            path="y.md",
            sha256="s2",
            mtime=0,
            corpus="references",
            doc_type="paper",
            extract_status="ok",
            status="active",
            title="Paper2",
            topic="T1",
        )
        update_file_fields(conn, "D2", topic="T1")

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        sync_document_structure(store, registry, paths, "D2")
        store.upsert_nodes(
            "Entity",
            [
                {
                    "entity_id": "Method:dead",
                    "name": "Dead",
                    "type": "Method",
                    "aliases": "",
                    "description": "",
                }
            ],
        )
        store.upsert_edges(
            "MENTIONS",
            [
                {"src": "D2#1", "dst": "Method:rag", "weight": 1},
                {"src": "D2#1", "dst": "Method:dead", "weight": 1},
            ],
        )
        # 软删 D2（读路径只看 valid_to，属性被全覆盖不影响本断言）
        store.upsert_nodes(
            "Document",
            [{"doc_id": "D2", "valid_to": "2026-08-16T00:00:00Z"}],
        )
    finally:
        store.close()

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = topic_subgraph(store, "T1", hops=2, max_nodes=500)
    finally:
        store.close()

    ids = {n["id"] for n in result["nodes"]}
    assert "D1" in ids
    assert "Method:rag" in ids
    assert "D2" not in ids
    assert "D2#1" not in ids
    assert "Method:dead" not in ids


# ---------------------------------------------------------------------------
# R-5：node_neighbors —— 节点 1 跳邻域（图谱页单击下钻）
# ---------------------------------------------------------------------------


def _seed_second_doc_mentions(default_config, registry, paths) -> None:
    """D2 同 topic T1，D2#1 提及 Method:rag（复用 R-2 测试的造数模式）。"""
    import json

    from kbapp.core.registry import update_file_fields, upsert_file
    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure

    payload2 = {
        "sha256": "s2",
        "path": "y.md",
        "format": "md",
        "parser": "markdown",
        "structure": "headers",
        "full_text": "rag again",
        "sections": [
            {"section_path": "1", "level": 1, "title": "Body", "page_range": "", "text": "rag"},
        ],
        "warnings": [],
        "chunks": [],
        "extracted_at": "2026-08-15",
    }
    (paths.extracted_dir / "s2.json").write_text(json.dumps(payload2), encoding="utf-8")
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D2",
            path="y.md",
            sha256="s2",
            mtime=0,
            corpus="references",
            doc_type="paper",
            extract_status="ok",
            status="active",
            title="Paper2",
            topic="T1",
        )
        update_file_fields(conn, "D2", topic="T1")

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        sync_document_structure(store, registry, paths, "D2")
        store.upsert_edges("MENTIONS", [{"src": "D2#1", "dst": "Method:rag", "weight": 1}])
    finally:
        store.close()


def _tombstone_doc(default_config, paths, doc_id) -> None:
    """读路径过滤只看 valid_to，直接写墓碑值即可。"""
    from kbapp.graph.store import make_graph_store

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        store.upsert_nodes("Document", [{"doc_id": doc_id, "valid_to": "2026-08-16T00:00:00Z"}])
    finally:
        store.close()


def _open_ro(default_config, paths):
    from kbapp.graph import make_graph_store

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    return store


def test_node_neighbors_entity_collects_sections_docs(default_config, registry, paths) -> None:
    """Entity 邻居：MENTIONS 反向到 Section + 其父 Document，边含两类。"""
    _seed_full_graph(default_config, registry, paths)  # D1 topic T1, D1#1→Method:rag

    from kbapp.graph import node_neighbors

    store = _open_ro(default_config, paths)
    try:
        result = node_neighbors(store, "Method:rag", "Entity")
    finally:
        store.close()

    by_id = {n["id"]: n for n in result["nodes"]}
    assert by_id["D1"]["type"] == "Document"
    assert by_id["D1#1"]["type"] == "Section"
    edge_pairs = {(e["src"], e["dst"], e["rel"]) for e in result["edges"]}
    assert ("D1", "D1#1", "CONTAINS_SECTION") in edge_pairs
    assert ("D1#1", "Method:rag", "MENTIONS") in edge_pairs
    assert result["truncated"] is False


def test_node_neighbors_entity_relates_to_bidirectional(default_config, registry, paths) -> None:
    """Entity 邻居含 RELATES_TO 双向的其他 Entity，边方向保留。"""
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import make_graph_store, node_neighbors

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        store.upsert_nodes(
            "Entity",
            [
                {
                    "entity_id": "Concept:vec",
                    "name": "Vector",
                    "type": "Concept",
                    "aliases": "",
                    "description": "",
                }
            ],
        )
        store.upsert_edges(
            "RELATES_TO",
            [
                {
                    "src": "Method:rag",
                    "dst": "Concept:vec",
                    "kind": "uses",
                    "weight": 1.0,
                    "evidence_section_id": "D1#1",
                }
            ],
        )
    finally:
        store.close()

    store = _open_ro(default_config, paths)
    try:
        out = node_neighbors(store, "Method:rag", "Entity")
        back = node_neighbors(store, "Concept:vec", "Entity")
    finally:
        store.close()

    assert "Concept:vec" in {n["id"] for n in out["nodes"]}
    assert ("Method:rag", "Concept:vec", "RELATES_TO") in {
        (e["src"], e["dst"], e["rel"]) for e in out["edges"]
    }
    # 反向查询同样到达，且边方向不变（src/dst 不随查询方向翻转）
    assert ("Method:rag", "Concept:vec", "RELATES_TO") in {
        (e["src"], e["dst"], e["rel"]) for e in back["edges"]
    }


def test_node_neighbors_document_and_section(default_config, registry, paths) -> None:
    """Document 邻居=Section+Topic；Section 邻居=父 Document+Entity。"""
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import node_neighbors

    store = _open_ro(default_config, paths)
    try:
        doc = node_neighbors(store, "D1", "Document")
        sec = node_neighbors(store, "D1#1", "Section")
    finally:
        store.close()

    doc_ids = {n["id"] for n in doc["nodes"]}
    assert doc_ids == {"D1#1", "T1"}
    assert ("D1", "T1", "ABOUT_TOPIC") in {(e["src"], e["dst"], e["rel"]) for e in doc["edges"]}
    sec_ids = {n["id"] for n in sec["nodes"]}
    assert sec_ids == {"D1", "Method:rag"}


def test_node_neighbors_excludes_tombstoned_documents(default_config, registry, paths) -> None:
    """R-5/R-2：墓碑 Document 不作为 Entity 邻居出现，其 Section 级联剔除。"""
    _seed_full_graph(default_config, registry, paths)
    _seed_second_doc_mentions(default_config, registry, paths)  # D2#1→Method:rag
    _tombstone_doc(default_config, paths, "D2")

    from kbapp.graph import node_neighbors

    store = _open_ro(default_config, paths)
    try:
        result = node_neighbors(store, "Method:rag", "Entity")
    finally:
        store.close()

    ids = {n["id"] for n in result["nodes"]}
    assert "D1" in ids
    assert "D2" not in ids
    assert "D2#1" not in ids


def test_node_neighbors_tombstoned_document_returns_empty(default_config, registry, paths) -> None:
    """中心节点为墓碑 Document 时视为不存在：邻居为空。"""
    _seed_full_graph(default_config, registry, paths)
    _tombstone_doc(default_config, paths, "D1")

    from kbapp.graph import node_neighbors

    store = _open_ro(default_config, paths)
    try:
        result = node_neighbors(store, "D1", "Document")
    finally:
        store.close()

    assert result["nodes"] == []
    assert result["edges"] == []


def test_node_neighbors_rejects_unknown_type(default_config, registry, paths) -> None:
    """未知节点类型抛 ValueError（端点映射 400）。"""
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import node_neighbors

    store = _open_ro(default_config, paths)
    try:
        with pytest.raises(ValueError):
            node_neighbors(store, "x", "Bogus")
    finally:
        store.close()


def test_topic_subgraph_section_keys_no_self_loops(default_config, registry, paths) -> None:
    """回归 R-10：边装配的节点键须以 section_id 优先于 doc_id。

    修复前 coalesce(..., doc_id, section_id, ...) 会把 Section 坍缩成父
    Document，产生 D1→D1 自环与重复边（G6 报 "Edge already exists"）。
    """
    _seed_full_graph(default_config, registry, paths)

    from kbapp.graph import topic_subgraph

    store = _open_ro(default_config, paths)
    try:
        result = topic_subgraph(store, "T1", hops=2, max_nodes=500)
    finally:
        store.close()

    edges = {(e["src"], e["dst"], e["rel"]) for e in result["edges"]}
    assert all(e["src"] != e["dst"] for e in result["edges"])
    assert ("D1", "D1#1", "CONTAINS_SECTION") in edges
    assert ("D1#1", "Method:rag", "MENTIONS") in edges
    assert ("D1", "T1", "ABOUT_TOPIC") in edges
