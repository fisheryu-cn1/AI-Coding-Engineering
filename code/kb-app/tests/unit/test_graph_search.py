"""Unit tests for graph-based related/compare search (15 §5.1)."""

from __future__ import annotations

import json

import pytest

ladybug = pytest.importorskip("ladybug")


def _seed_graph_graph_for_search(default_config, registry, paths, tmp_path):
    """造一图：2 docs（D1/D2）+ 共享 Entity + Topic。

    D1.RAG --RELATES_TO--> D2.Vector DB
    D1.ABOUT_TOPIC--> "ContextEngineering"
    D2.ABOUT_TOPIC--> "ContextEngineering"
    """
    from kbapp.core.registry import upsert_file, update_file_fields
    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure

    # 第一篇
    payload1 = {
        "sha256": "s1",
        "path": "a.md",
        "format": "md",
        "parser": "markdown",
        "structure": "headers",
        "full_text": "RAG uses Vector DB",
        "sections": [{"section_path": "1", "level": 1, "title": "Intro", "page_range": "", "text": "RAG uses Vector DB"}],
        "warnings": [],
        "chunks": [],
        "extracted_at": "2026-08-15",
    }
    (paths.extracted_dir / "s1.json").write_text(json.dumps(payload1), encoding="utf-8")
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D1",
            path="a.md",
            sha256="s1",
            mtime=0,
            corpus="references",
            doc_type="paper",
            extract_status="ok",
            status="active",
            title="Paper A",
            topic="ContextEngineering",
        )
        update_file_fields(conn, "D1", topic="ContextEngineering")

    # Open a single store and do all the rest
    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        sync_document_structure(store, registry, paths, "D1")

        # 第二篇
        payload2 = {
            "sha256": "s2",
            "path": "b.md",
            "format": "md",
            "parser": "markdown",
            "structure": "headers",
            "full_text": "Vector DB",
            "sections": [{"section_path": "1", "level": 1, "title": "Intro", "page_range": "", "text": "Vector DB"}],
            "warnings": [],
            "chunks": [],
            "extracted_at": "2026-08-15",
        }
        (paths.extracted_dir / "s2.json").write_text(json.dumps(payload2), encoding="utf-8")
        with registry.transaction() as conn:
            upsert_file(
                conn,
                doc_id="D2",
                path="b.md",
                sha256="s2",
                mtime=0,
                corpus="references",
                doc_type="paper",
                extract_status="ok",
                status="active",
                title="Paper B",
                topic="ContextEngineering",
            )
            update_file_fields(conn, "D2", topic="ContextEngineering")

        sync_document_structure(store, registry, paths, "D2")

        # 给 D1/D2 注入共享 Entity + RELATES_TO
        store.upsert_nodes(
            "Entity",
            [
                {"entity_id": "Method:rag", "name": "RAG", "type": "Method", "aliases": "", "description": ""},
                {"entity_id": "Tool:vector-db", "name": "Vector DB", "type": "Tool", "aliases": "", "description": ""},
            ],
        )
        store.upsert_edges(
            "RELATES_TO",
            [{"src": "Method:rag", "dst": "Tool:vector-db", "kind": "uses", "weight": 1.0, "evidence_section_id": ""}],
        )
    finally:
        store.close()


def test_graph_related_returns_neighbors(default_config, registry, paths, tmp_path) -> None:
    """graph_related：实体 1 跳邻域 + 关系 kind。"""
    _seed_graph_graph_for_search(default_config, registry, paths, tmp_path)

    from kbapp.graph.store import make_graph_store
    from kbapp.retrieve.graph_search import graph_related

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = graph_related(
            store,
            target="Method:rag",
            target_type="Entity",
            hops=1,
            limit=10,
        )
    finally:
        store.close()
    assert "related" in result
    assert any(r["id"] == "Tool:vector-db" for r in result["related"])


def test_graph_related_hops_caps(default_config, registry, paths, tmp_path) -> None:
    """hop 上限：hops=1 应该不返回 2 跳之外的节点。"""
    _seed_graph_graph_for_search(default_config, registry, paths, tmp_path)

    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure
    from kbapp.retrieve.graph_search import graph_related

    # 加一条 3 节点的链 X→RAG→Vector DB→Y
    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        store.upsert_nodes(
            "Entity",
            [
                {"entity_id": "Concept:x", "name": "X", "type": "Concept", "aliases": "", "description": ""},
                {"entity_id": "Concept:y", "name": "Y", "type": "Concept", "aliases": "", "description": ""},
            ],
        )
        store.upsert_edges(
            "RELATES_TO",
            [
                {"src": "Concept:x", "dst": "Method:rag", "kind": "part-of", "weight": 1.0, "evidence_section_id": ""},
                {"src": "Tool:vector-db", "dst": "Concept:y", "kind": "uses", "weight": 1.0, "evidence_section_id": ""},
            ],
        )
    finally:
        store.close()

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = graph_related(store, target="Concept:x", target_type="Entity", hops=1, limit=10)
        ids = [r["id"] for r in result["related"]]
        # 1 跳：应只到 RAG，到不了 Vector DB / Y
        assert "Method:rag" in ids
        assert "Tool:vector-db" not in ids
        assert "Concept:y" not in ids
    finally:
        store.close()


def test_graph_compare_by_kind(default_config, registry, paths, tmp_path) -> None:
    """graph_compare：按 kind 列出 entity 关联。"""
    _seed_graph_graph_for_search(default_config, registry, paths, tmp_path)

    from kbapp.graph.store import make_graph_store
    from kbapp.retrieve.graph_search import graph_compare

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = graph_compare(store, concept="Method:rag", limit=10)
    finally:
        store.close()
    assert "rows" in result
    assert any("uses" in r.get("kinds", []) or r.get("kind") == "uses" for r in result["rows"])
