"""Unit tests for :mod:`kbapp.retrieve.resolve`（13 §2.1 doc 引用解析）。"""

from __future__ import annotations

from kbapp.core.registry import insert_chunk, upsert_file, upsert_topic
from kbapp.retrieve.resolve import resolve_doc


def _seed(registry) -> None:
    with registry.transaction() as conn:
        upsert_topic(conn, name="CodeGraph")
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/kg.md",
            sha256="s1",
            mtime=0,
            corpus="design",
            status="active",
            extract_status="ok",
            title="Knowledge Graph",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 Graph",
            title="Graph",
            text="x",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/kg2.md",
            sha256="s2",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="Knowledge Graph Two",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 Graph",
            title="Graph",
            text="x",
        )


def test_resolve_doc_by_doc_id(registry) -> None:
    _seed(registry)
    res = resolve_doc(registry, "D0001")
    assert res.row is not None and res.row.doc_id == "D0001"
    assert res.candidates == []


def test_resolve_doc_by_exact_path(registry) -> None:
    _seed(registry)
    res = resolve_doc(registry, "/c/kg.md")
    assert res.row is not None and res.row.doc_id == "D0001"


def test_resolve_doc_by_path_suffix_unique(registry) -> None:
    _seed(registry)
    res = resolve_doc(registry, "kg2.md")
    assert res.row is not None and res.row.doc_id == "D0002"


def test_resolve_doc_by_title_substring_unique(registry) -> None:
    _seed(registry)
    res = resolve_doc(registry, "Knowledge Graph Two")
    assert res.row is not None and res.row.doc_id == "D0002"


def test_resolve_doc_ambiguous_returns_candidates(registry) -> None:
    """多文档歧义命中不回首个，返回候选 path（13 §2.1）。"""
    _seed(registry)
    res = resolve_doc(registry, "Graph")
    assert res.row is None
    assert set(res.candidates) == {"/c/kg.md", "/c/kg2.md"}


def test_resolve_doc_not_found(registry) -> None:
    _seed(registry)
    res = resolve_doc(registry, "zzz")
    assert res.row is None
    assert res.candidates == []
