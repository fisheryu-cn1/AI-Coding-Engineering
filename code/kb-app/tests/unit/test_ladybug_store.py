"""Unit tests for :mod:`kbapp.graph.ladybug_store` (15 §3.1, §3.3)."""

from __future__ import annotations

import pytest

ladybug = pytest.importorskip("ladybug")

from kbapp.graph.ladybug_store import LadybugStore  # noqa: E402


@pytest.fixture
def store(default_config, tmp_path):
    s = LadybugStore(default_config)
    s.open(str(tmp_path / "g"), "rw")
    yield s
    s.close()


def test_upsert_and_query_roundtrip(store) -> None:
    """upsert 幂等：二次 MERGE 覆盖字段，不创建重复节点。"""
    store.upsert_nodes("Topic", [{"name": "t1", "description": "d1"}])
    store.upsert_nodes("Topic", [{"name": "t1", "description": "d2"}])  # 幂等
    rows = store.query(
        "MATCH (t:Topic) WHERE t.name = $n RETURN t.description AS d",
        {"n": "t1"},
    )
    assert rows == [{"d": "d2"}]


def test_shortest_path(store) -> None:
    """shortest_path 返回 [{nodes, rels, length}] 形状。"""
    store.upsert_nodes(
        "Entity",
        [
            {"entity_id": "a", "name": "A", "type": "Concept", "aliases": "", "description": ""},
            {"entity_id": "b", "name": "B", "type": "Concept", "aliases": "", "description": ""},
        ],
    )
    store.upsert_edges(
        "RELATES_TO",
        [
            {
                "src": "a",
                "dst": "b",
                "kind": "uses",
                "weight": 1.0,
                "evidence_section_id": "s1",
            }
        ],
    )
    paths = store.shortest_path(("Entity", "a"), ("Entity", "b"), max_hops=3)
    assert paths[0]["length"] == 1


def test_readonly_rejects_write(default_config, tmp_path) -> None:
    """ro 模式下尝试写应报错。"""
    s = LadybugStore(default_config)
    s.open(str(tmp_path / "g2"), "rw")
    s.close()
    ro = LadybugStore(default_config)
    ro.open(str(tmp_path / "g2"), "ro")
    try:
        with pytest.raises(Exception):
            ro.upsert_nodes("Topic", [{"name": "x", "description": ""}])
    finally:
        ro.close()


def test_upsert_edges_requires_both_endpoints(store) -> None:
    """upsert_edges 端点缺失时静默跳过（无 node 无 edge）。"""
    store.upsert_edges(
        "RELATES_TO",
        [
            {"src": "nope", "dst": "also_nope", "kind": "uses", "weight": 1.0, "evidence_section_id": ""}
        ],
    )
    rows = store.query("MATCH ()-[r:RELATES_TO]->() RETURN count(r) AS n")
    assert rows and rows[0]["n"] == 0


def test_close_is_idempotent(default_config, tmp_path) -> None:
    """close 重复调用安全。"""
    s = LadybugStore(default_config)
    s.open(str(tmp_path / "g3"), "rw")
    s.close()
    s.close()  # 二次不应 raise
