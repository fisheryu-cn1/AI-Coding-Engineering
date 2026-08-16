"""Knowledge graph module (M5; 15 §3).

Provides:

- :data:`GRAPH_NODES` / :data:`GRAPH_RELS` — backend-neutral schema (15 §3.2)
- :class:`GraphStore` protocol + :func:`make_graph_store` factory (15 §3.1)
- :func:`reset_graph` utility (15 §3.3)
- :func:`sync_document_structure` / :func:`stage_index_graph` / :func:`stage_tombstone_graph`
- :func:`is_core_doc` / :func:`norm` — extract gating + entity dedup (15 §4.1/§4.2)
- :func:`topic_subgraph` / :func:`entity_path` / :func:`node_neighbors` — graph queries
  shared by CLI & Web (15 §6.2)
"""

from __future__ import annotations

from kbapp.graph.extract import is_core_doc, norm
from kbapp.graph.queries import entity_path, node_neighbors, topic_subgraph
from kbapp.graph.schema import (
    ENTITY_TYPES,
    GRAPH_NODES,
    GRAPH_RELS,
    REL_KINDS,
    NodeDef,
    RelDef,
)
from kbapp.graph.store import GraphError, GraphStore, make_graph_store

__all__ = [
    "ENTITY_TYPES",
    "GRAPH_NODES",
    "GRAPH_RELS",
    "GraphError",
    "GraphStore",
    "NodeDef",
    "REL_KINDS",
    "RelDef",
    "entity_path",
    "is_core_doc",
    "make_graph_store",
    "node_neighbors",
    "norm",
    "topic_subgraph",
]
