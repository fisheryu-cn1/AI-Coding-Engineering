"""Backend-neutral graph schema (15 §3.2; D15-2 MVP 简化).

The schema is the **single source of truth** for what nodes and edges exist
in the knowledge graph. Each backend (e.g. LadybugDB) consumes this module
and translates it into native DDL. Schema changes are guaranteed to ripple
through every backend because they all read this module.

15 §3.2 落图范围（MVP 简化）：

- 节点四类：Document / Section / Entity / Topic
- 边四类：CONTAINS_SECTION / MENTIONS / ABOUT_TOPIC / RELATES_TO
- 砍除：Chunk 节点 + CONTAINS_CHUNK + MENTIONS_ENTITY + CITES + SUPERSEDES + SAME_AS
- 不落 Section→Topic（主题归类在文档级，Section 主题经父 Document 反查）
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NodeDef:
    """One node label + its primary key + property type map.

    ``props`` maps property name to a LadybugDB type token (``STRING`` /
    ``INT64`` / ``DOUBLE``). The Store layer re-renders these to whatever
    concrete DDL the backend needs.
    """

    label: str
    pk: str
    props: dict[str, str]


@dataclass(frozen=True)
class RelDef:
    """One edge label + endpoints + property type map."""

    label: str
    src: str
    dst: str
    props: dict[str, str]


# Type tokens (LadybugDB dialect; backend-neutral intent).
_S = "STRING"
_I = "INT64"
_D = "DOUBLE"


GRAPH_NODES: tuple[NodeDef, ...] = (
    NodeDef(
        "Document",
        "doc_id",
        {
            "title": _S,
            "path": _S,
            "sha256": _S,
            "doc_type": _S,
            "corpus": _S,
            "arxiv_id": _S,
            "version": _S,
            "authors": _S,
            "published": _S,
            "summary_l1": _S,
            "summary_l2": _S,
            "summary_path": _S,
            "valid_from": _S,
            "valid_to": _S,
        },
    ),
    NodeDef(
        "Section",
        "section_id",
        {
            "doc_id": _S,
            "section_path": _S,
            "level": _I,
            "title": _S,
            "summary": _S,
            "page_range": _S,
            "order": _I,
        },
    ),
    NodeDef(
        "Entity",
        "entity_id",
        {
            "name": _S,
            "type": _S,
            "aliases": _S,
            "description": _S,
        },
    ),
    NodeDef(
        "Topic",
        "name",
        {"description": _S},
    ),
)


GRAPH_RELS: tuple[RelDef, ...] = (
    RelDef(
        "CONTAINS_SECTION",
        "Document",
        "Section",
        {"order": _I},
    ),
    RelDef(
        "MENTIONS",
        "Section",
        "Entity",
        {"weight": _I},
    ),
    RelDef(
        "ABOUT_TOPIC",
        "Document",
        "Topic",
        {"confidence": _D},
    ),
    RelDef(
        "RELATES_TO",
        "Entity",
        "Entity",
        {
            "kind": _S,
            "weight": _D,
            "evidence_section_id": _S,
        },
    ),
)


# 实体类型受控词表（15 §3.2 / §4.2）——LLM 抽取时强制收敛。
ENTITY_TYPES: tuple[str, ...] = (
    "Concept",
    "Method",
    "Tool",
    "Dataset",
    "Person",
    "Organization",
)

# 关系 kind 受控词表（15 §3.2 / §4.2）。LLM 抽到的越界 kind 丢弃并计数。
REL_KINDS: tuple[str, ...] = (
    "extends",
    "contradicts",
    "applies",
    "evaluates",
    "improves-on",
    "part-of",
    "instance-of",
    "uses",
    "compares",
)


__all__ = [
    "ENTITY_TYPES",
    "GRAPH_NODES",
    "GRAPH_RELS",
    "NodeDef",
    "REL_KINDS",
    "RelDef",
]
