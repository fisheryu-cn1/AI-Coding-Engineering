"""Unit tests for :mod:`kbapp.graph.schema` (15 §3.2)."""

from __future__ import annotations


def test_schema_covers_15_spec() -> None:
    """图 Schema 收敛为 4 节点 4 边（15 §3.2 / D15-2）。"""
    from kbapp.graph import GRAPH_NODES, GRAPH_RELS

    assert {n.label for n in GRAPH_NODES} == {"Document", "Section", "Entity", "Topic"}
    assert [(r.label, r.src, r.dst) for r in GRAPH_RELS] == [
        ("CONTAINS_SECTION", "Document", "Section"),
        ("MENTIONS", "Section", "Entity"),
        ("ABOUT_TOPIC", "Document", "Topic"),
        ("RELATES_TO", "Entity", "Entity"),
    ]
    pk = {n.label: n.pk for n in GRAPH_NODES}
    assert pk == {
        "Document": "doc_id",
        "Section": "section_id",
        "Entity": "entity_id",
        "Topic": "name",
    }


def test_no_removed_edges() -> None:
    """15 D15-2：砍除 Chunk 节点/CONTAINS_CHUNK/MENTIONS_ENTITY/CITES/SUPERSEDES/SAME_AS。"""
    from kbapp.graph import GRAPH_NODES, GRAPH_RELS

    labels = {n.label for n in GRAPH_NODES}
    assert "Chunk" not in labels
    rel_labels = [r.label for r in GRAPH_RELS]
    for absent in (
        "CONTAINS_CHUNK",
        "MENTIONS_ENTITY",
        "CITES",
        "SUPERSEDES",
        "SAME_AS",
    ):
        assert absent not in rel_labels


def test_entity_types_and_rel_kinds_are_controlled() -> None:
    """实体类型与关系 kind 受控词表（15 §3.2 / §4.2）。"""
    from kbapp.graph import ENTITY_TYPES, REL_KINDS

    assert set(ENTITY_TYPES) == {
        "Concept",
        "Method",
        "Tool",
        "Dataset",
        "Person",
        "Organization",
    }
    assert set(REL_KINDS) == {
        "extends",
        "contradicts",
        "applies",
        "evaluates",
        "improves-on",
        "part-of",
        "instance-of",
        "uses",
        "compares",
    }


def test_props_map_ladybug_types() -> None:
    """属性类型字典为 LadybugDB 类型（STRING/INT64/DOUBLE）；后端在此翻译。"""
    from kbapp.graph import GRAPH_NODES

    doc = next(n for n in GRAPH_NODES if n.label == "Document")
    assert doc.pk == "doc_id"
    assert doc.props["valid_to"] == "STRING"
    assert doc.props["title"] == "STRING"

    ent = next(n for n in GRAPH_NODES if n.label == "Entity")
    assert ent.pk == "entity_id"
    assert ent.props["name"] == "STRING"
    assert ent.props["type"] == "STRING"
