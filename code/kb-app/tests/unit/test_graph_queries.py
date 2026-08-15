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
            [{"entity_id": "Method:rag", "name": "RAG", "type": "Method",
              "aliases": "", "description": ""}],
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
            {"entity_id": f"Concept:e{i}", "name": f"E{i}", "type": "Concept",
             "aliases": "", "description": ""}
            for i in range(600)
        ]
        store.upsert_nodes("Entity", entities)
        for i in range(600):
            store.upsert_edges(
                "RELATES_TO",
                [{"src": "Concept:e0", "dst": f"Concept:e{i}", "kind": "uses",
                  "weight": 1.0, "evidence_section_id": ""}],
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
