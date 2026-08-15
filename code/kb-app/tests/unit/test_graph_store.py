"""Unit tests for :mod:`kbapp.graph.store` (15 §3.1 / D15-10)."""

from __future__ import annotations

import pytest


def test_factory_rejects_unknown_backend(default_config) -> None:
    """Only 'ladybug' is accepted (15 D15-10 单一选型，删除 Kuzu/Neo4j 路径)."""
    from kbapp.graph.store import GraphError, make_graph_store

    with pytest.raises(GraphError, match="neo4j"):
        make_graph_store("neo4j", default_config)

    with pytest.raises(GraphError, match="kuzu"):
        make_graph_store("kuzu", default_config)


def test_factory_rejects_missing_ladybug_extra(default_config, monkeypatch) -> None:
    """Missing ladybug package → GraphError prompting extra install."""
    import builtins

    from kbapp.graph.store import GraphError, make_graph_store

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ladybug":
            raise ImportError("No module named 'ladybug'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(GraphError, match="graph-ladybug"):
        make_graph_store("ladybug", default_config)


def test_protocol_has_required_methods() -> None:
    """GraphStore protocol defines the six callers depend on (15 §3.1)."""
    from kbapp.graph.store import GraphStore

    required = {"open", "close", "upsert_nodes", "upsert_edges", "query", "shortest_path"}
    assert required.issubset(set(dir(GraphStore)))
