"""Contract test suite for the GraphStore (15 §3.3).

Single backend (LadybugDB) — these tests pin the schema and query layer
behavior that other layers (CLI / MCP / Web) depend on. If we ever need
to swap backends, the new store must pass this same suite.
"""

from __future__ import annotations

import pytest

ladybug = pytest.importorskip("ladybug")

from kbapp.graph.store import make_graph_store  # noqa: E402


@pytest.fixture
def store(default_config, tmp_path):
    s = make_graph_store("ladybug", default_config)
    s.open(str(tmp_path / "g"), "rw")
    yield s
    s.close()


def _seed(store):
    store.upsert_nodes(
        "Document",
        [
            {
                "doc_id": "d1",
                "title": "T1",
                "path": "",
                "sha256": "",
                "doc_type": "paper",
                "corpus": "references",
                "arxiv_id": "",
                "version": "",
                "authors": "",
                "published": "",
                "summary_l1": "",
                "summary_l2": "",
                "summary_path": "",
                "valid_from": "2026-01-01",
                "valid_to": "",
            },
        ],
    )
    store.upsert_nodes(
        "Section",
        [
            {
                "section_id": "d1#1",
                "doc_id": "d1",
                "section_path": "1",
                "level": 1,
                "title": "Intro",
                "summary": "",
                "page_range": "",
                "seq": 0,
            },
        ],
    )
    store.upsert_edges(
        "CONTAINS_SECTION",
        [{"src": "d1", "dst": "d1#1", "seq": 0}],
    )


def test_contract_upsert_and_traverse(store) -> None:
    """建点建边 + 单跳遍历。"""
    _seed(store)
    rows = store.query(
        "MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section) "
        "WHERE d.doc_id = $id RETURN s.title AS t",
        {"id": "d1"},
    )
    assert rows == [{"t": "Intro"}]


def test_contract_two_hop(store) -> None:
    """2 跳遍历：Topic←Document→Section。"""
    _seed(store)
    store.upsert_nodes("Topic", [{"name": "ce", "description": ""}])
    store.upsert_edges(
        "ABOUT_TOPIC",
        [{"src": "d1", "dst": "ce", "confidence": 0.9}],
    )
    rows = store.query(
        "MATCH (t:Topic)<-[:ABOUT_TOPIC]-(d:Document)-[:CONTAINS_SECTION]->(s:Section) "
        "WHERE t.name = $n RETURN s.section_id AS sid",
        {"n": "ce"},
    )
    assert rows == [{"sid": "d1#1"}]


def test_contract_soft_delete_filter(store) -> None:
    """valid_to != '' 视为软删，查询层过滤。"""
    _seed(store)
    store.upsert_nodes(
        "Document",
        [
            {
                "doc_id": "d1",
                "title": "T1",
                "path": "",
                "sha256": "",
                "doc_type": "paper",
                "corpus": "references",
                "arxiv_id": "",
                "version": "",
                "authors": "",
                "published": "",
                "summary_l1": "",
                "summary_l2": "",
                "summary_path": "",
                "valid_from": "2026-01-01",
                "valid_to": "2026-08-15",
            }
        ],
    )
    rows = store.query(
        "MATCH (d:Document) WHERE d.valid_to = '' RETURN d.doc_id AS id",
        {},
    )
    assert rows == []


def test_contract_shortest_path(store) -> None:
    """shortest_path 至少返回一条记录 + length 数值。"""
    store.upsert_nodes(
        "Entity",
        [
            {"entity_id": "x", "name": "X", "type": "Concept", "aliases": "", "description": ""},
            {"entity_id": "y", "name": "Y", "type": "Concept", "aliases": "", "description": ""},
        ],
    )
    store.upsert_edges(
        "RELATES_TO",
        [
            {"src": "x", "dst": "y", "kind": "uses", "weight": 1.0, "evidence_section_id": ""}
        ],
    )
    paths = store.shortest_path(("Entity", "x"), ("Entity", "y"))
    assert paths and paths[0]["length"] >= 1
