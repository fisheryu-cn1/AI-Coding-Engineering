"""Unit tests for /api/docs read paths (15 §6.2; R-2 墓碑过滤 / R-7 404 口径)。

覆盖：词云聚合（_aggregate_entities）、文档侧栏（_doc_mentions /
_doc_related_docs）对墓碑 Document 的过滤，以及 deleted/duplicate 文档
GET /api/docs/{id} 返回 404 DOC_NOT_FOUND。
"""

from __future__ import annotations

import json

import pytest

fastapi = pytest.importorskip("fastapi")
ladybug = pytest.importorskip("ladybug")

from fastapi.testclient import TestClient  # noqa: E402

_TOMBSTONE_TS = "2026-08-16T00:00:00Z"


@pytest.fixture
def client(registry, default_config, paths):
    from kbapp.web.server import create_app

    app = create_app(registry=registry, cfg=default_config, paths=paths)
    return TestClient(app)


def _upsert_doc(registry, doc_id, *, status="active", topic="T1", title=None):
    from kbapp.core.registry import update_file_fields, upsert_file

    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id=doc_id,
            path=f"{doc_id}.md",
            sha256=f"s-{doc_id}",
            mtime=0,
            corpus="references",
            doc_type="paper",
            extract_status="ok",
            status=status,
            title=title or f"Doc {doc_id}",
            topic=topic,
        )
        update_file_fields(conn, doc_id, topic=topic)


def _seed_two_docs_graph(registry, paths, default_config):
    """造图：D1/D2 同 topic T1，各自 section 都提及共享实体 Method:rag。"""
    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure

    for doc_id in ("D1", "D2"):
        _upsert_doc(registry, doc_id)
        payload = {
            "sha256": f"s-{doc_id}",
            "path": f"{doc_id}.md",
            "format": "md",
            "parser": "markdown",
            "structure": "headers",
            "full_text": "RAG",
            "sections": [
                {
                    "section_path": "1",
                    "level": 1,
                    "title": "Intro",
                    "page_range": "",
                    "text": "RAG",
                }
            ],
            "warnings": [],
            "chunks": [],
            "extracted_at": "2026-08-15",
        }
        (paths.extracted_dir / f"s-{doc_id}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        sync_document_structure(store, registry, paths, "D1")
        sync_document_structure(store, registry, paths, "D2")
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
            [
                {"src": "D1#1", "dst": "Method:rag", "weight": 1},
                {"src": "D2#1", "dst": "Method:rag", "weight": 2},
            ],
        )
    finally:
        store.close()


def _tombstone_in_graph(paths, default_config, doc_id):
    """读路径过滤只看 valid_to，直接写墓碑值即可（属性全覆盖不影响断言）。"""
    from kbapp.graph.store import make_graph_store

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        store.upsert_nodes("Document", [{"doc_id": doc_id, "valid_to": _TOMBSTONE_TS}])
    finally:
        store.close()


# ---------------------------------------------------------------------------
# R-7：deleted / duplicate 文档 404
# ---------------------------------------------------------------------------


def test_get_doc_404_for_deleted(client, registry) -> None:
    """R-7：status='deleted' 文档 GET /api/docs/{id} 返 404 DOC_NOT_FOUND。"""
    _upsert_doc(registry, "DX", status="deleted")
    r = client.get("/api/docs/DX")
    assert r.status_code == 404
    assert r.json() == {"detail": "DOC_NOT_FOUND"}


def test_get_doc_404_for_duplicate(client, registry) -> None:
    """R-7：status='duplicate' 文档同样按 DOC_NOT_FOUND 404（对齐 resolve_doc）。"""
    _upsert_doc(registry, "DY", status="duplicate")
    r = client.get("/api/docs/DY")
    assert r.status_code == 404
    assert r.json() == {"detail": "DOC_NOT_FOUND"}


def test_get_doc_200_for_active(client, registry) -> None:
    """R-7 对照：active 文档仍 200。"""
    _upsert_doc(registry, "DA", status="active")
    r = client.get("/api/docs/DA")
    assert r.status_code == 200
    assert r.json()["doc"]["doc_id"] == "DA"


# ---------------------------------------------------------------------------
# R-2：词云 / 侧栏过滤墓碑 Document
# ---------------------------------------------------------------------------


def test_aggregate_entities_exclude_tombstoned(registry, default_config, paths) -> None:
    """R-2 词云：墓碑文档的 MENTIONS 不再聚合实体；活文档照常。"""
    _seed_two_docs_graph(registry, paths, default_config)
    _tombstone_in_graph(paths, default_config, "D2")

    from kbapp.web.api import _aggregate_entities

    assert _aggregate_entities(registry, default_config, paths=paths, doc_ids=["D2"]) == []
    ents = _aggregate_entities(registry, default_config, paths=paths, doc_ids=["D1"])
    assert [e["id"] for e in ents] == ["Method:rag"]


def test_doc_mentions_exclude_tombstoned(client, registry, default_config, paths) -> None:
    """R-2 侧栏：被软删文档自己的 mentioned_entities 置空。"""
    _seed_two_docs_graph(registry, paths, default_config)
    _tombstone_in_graph(paths, default_config, "D2")

    r = client.get("/api/docs/D2")  # registry status 仍 active → 200
    assert r.status_code == 200
    assert r.json()["mentioned_entities"] == []
    r = client.get("/api/docs/D1")
    assert [e["id"] for e in r.json()["mentioned_entities"]] == ["Method:rag"]


def test_doc_related_docs_exclude_tombstoned(client, registry, default_config, paths) -> None:
    """R-2 侧栏：related_docs 不再经共享实体关联到墓碑文档。"""
    _seed_two_docs_graph(registry, paths, default_config)
    _tombstone_in_graph(paths, default_config, "D2")

    r = client.get("/api/docs/D1")
    assert r.status_code == 200
    related_ids = [d["doc_id"] for d in r.json()["related_docs"]]
    assert "D2" not in related_ids


# ---------------------------------------------------------------------------
# R-5：/api/graph/neighbors 端点（节点单击下钻）
# ---------------------------------------------------------------------------


def test_graph_neighbors_schema(client, registry, default_config, paths) -> None:
    """R-5：neighbors 响应契约 {id,type,nodes[{id,label,type}],edges[{src,dst,rel}],truncated}。"""
    _seed_two_docs_graph(registry, paths, default_config)

    r = client.get("/api/graph/neighbors", params={"id": "Method:rag", "type": "Entity"})
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "Method:rag"
    assert body["type"] == "Entity"
    assert body["truncated"] is False
    assert all(set(n) == {"id", "label", "type"} for n in body["nodes"])
    assert all(set(e) == {"src", "dst", "rel"} for e in body["edges"])
    neighbor_ids = {n["id"] for n in body["nodes"]}
    assert neighbor_ids == {"D1", "D2", "D1#1", "D2#1"}


def test_graph_neighbors_filter_tombstoned(client, registry, default_config, paths) -> None:
    """R-5/R-2：端点口径一致——墓碑 Document 不出现在邻居里。"""
    _seed_two_docs_graph(registry, paths, default_config)
    _tombstone_in_graph(paths, default_config, "D2")

    r = client.get("/api/graph/neighbors", params={"id": "Method:rag", "type": "Entity"})
    assert r.status_code == 200
    neighbor_ids = {n["id"] for n in r.json()["nodes"]}
    assert neighbor_ids == {"D1", "D1#1"}


def test_graph_neighbors_400_invalid_type(client, registry, default_config, paths) -> None:
    """未知节点类型 → 400。"""
    _seed_two_docs_graph(registry, paths, default_config)

    r = client.get("/api/graph/neighbors", params={"id": "x", "type": "Bogus"})
    assert r.status_code == 400


def test_graph_neighbors_503_when_graph_missing(client) -> None:
    """图库缺失 → 503（口径同 subgraph/path 端点）。"""
    r = client.get("/api/graph/neighbors", params={"id": "x", "type": "Entity"})
    assert r.status_code == 503
    assert "graph unavailable" in r.json()["detail"]
