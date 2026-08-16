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
    from kbapp.core.registry import update_file_fields, upsert_file
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
        "sections": [
            {
                "section_path": "1",
                "level": 1,
                "title": "Intro",
                "page_range": "",
                "text": "RAG uses Vector DB",
            }
        ],
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
            "sections": [
                {
                    "section_path": "1",
                    "level": 1,
                    "title": "Intro",
                    "page_range": "",
                    "text": "Vector DB",
                }
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
                {
                    "entity_id": "Method:rag",
                    "name": "RAG",
                    "type": "Method",
                    "aliases": "",
                    "description": "",
                },
                {
                    "entity_id": "Tool:vector-db",
                    "name": "Vector DB",
                    "type": "Tool",
                    "aliases": "",
                    "description": "",
                },
            ],
        )
        store.upsert_edges(
            "RELATES_TO",
            [
                {
                    "src": "Method:rag",
                    "dst": "Tool:vector-db",
                    "kind": "uses",
                    "weight": 1.0,
                    "evidence_section_id": "",
                }
            ],
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
    from kbapp.retrieve.graph_search import graph_related

    # 加一条 3 节点的链 X→RAG→Vector DB→Y
    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        store.upsert_nodes(
            "Entity",
            [
                {
                    "entity_id": "Concept:x",
                    "name": "X",
                    "type": "Concept",
                    "aliases": "",
                    "description": "",
                },
                {
                    "entity_id": "Concept:y",
                    "name": "Y",
                    "type": "Concept",
                    "aliases": "",
                    "description": "",
                },
            ],
        )
        store.upsert_edges(
            "RELATES_TO",
            [
                {
                    "src": "Concept:x",
                    "dst": "Method:rag",
                    "kind": "part-of",
                    "weight": 1.0,
                    "evidence_section_id": "",
                },
                {
                    "src": "Tool:vector-db",
                    "dst": "Concept:y",
                    "kind": "uses",
                    "weight": 1.0,
                    "evidence_section_id": "",
                },
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


def test_graph_related_excludes_tombstoned_documents(
    default_config, registry, paths, tmp_path
) -> None:
    """R-2：墓碑 Document 及其 Section（父文档级联）不进 graph_related 邻域。"""
    _seed_graph_graph_for_search(default_config, registry, paths, tmp_path)

    from kbapp.graph.store import make_graph_store
    from kbapp.retrieve.graph_search import graph_related

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        # 挂 MENTIONS：D1#1→rag，D2#1→vector-db（D2 经 D2#1 可达）
        store.upsert_edges(
            "MENTIONS",
            [
                {"src": "D1#1", "dst": "Method:rag", "weight": 1},
                {"src": "D2#1", "dst": "Tool:vector-db", "weight": 1},
            ],
        )
        # 软删 D2（直接写墓碑值；读路径过滤只看 valid_to）
        store.upsert_nodes(
            "Document",
            [{"doc_id": "D2", "valid_to": "2026-08-16T00:00:00Z"}],
        )
    finally:
        store.close()

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = graph_related(
            store, target="Method:rag", target_type="Entity", hops=3, limit=20
        )
    finally:
        store.close()
    ids = {r["id"] for r in result["related"]}
    assert "D1" in ids  # 活文档仍可达（rag←D1#1→D1）
    assert "D2" not in ids
    assert "D2#1" not in ids


def test_graph_related_section_ids_not_collapsed_to_parent(
    default_config, registry, paths, tmp_path
) -> None:
    """回归 R-10：related 的 Section 邻居须以 section_id 现身，不被坍缩成父 doc_id。"""
    _seed_graph_graph_for_search(default_config, registry, paths, tmp_path)

    from kbapp.graph.store import make_graph_store
    from kbapp.retrieve.graph_search import graph_related

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        result = graph_related(store, target="D1", target_type="Document", hops=1, limit=10)
    finally:
        store.close()

    by_id = {r["id"]: r for r in result["related"]}
    assert "D1#1" in by_id, f"Section 邻居缺失或被坍缩：{list(by_id)}"
    assert by_id["D1#1"]["type"] == "Section"
