"""Unit tests for :mod:`kbapp.retrieve.assembler`（11 §2 输出侧 / FR-3.2/3.3）。"""

from __future__ import annotations

from kbapp.retrieve.assembler import compare_documents


def test_compare_documents_returns_table() -> None:
    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return "| 维度 | A | B |"

    out = compare_documents(
        _FakeLLM(),
        [("D0001", "Doc A", "summary a"), ("D0002", "Doc B", "summary b")],
    )
    assert out == "| 维度 | A | B |"


def test_compare_documents_falls_back_on_error() -> None:
    class _Boom:
        def complete(self, messages, **kw) -> str:
            raise RuntimeError("down")

    assert compare_documents(_Boom(), [("D0001", "A", "s"), ("D0002", "B", "s")]) is None


def test_compare_documents_requires_two_entries() -> None:
    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return "table"

    assert compare_documents(_FakeLLM(), [("D0001", "A", "s")]) is None
    assert compare_documents(None, [("D0001", "A", "s"), ("D0002", "B", "s")]) is None


def _seed_assemble(registry) -> None:
    """播 2 篇同 topic 文档 + 1 篇异 topic，供 assemble_for_task 检索。"""
    from kbapp.core.registry import insert_chunk, upsert_file, upsert_topic

    with registry.transaction() as conn:
        upsert_topic(conn, name="CodeGraph")
        upsert_topic(conn, name="ContextEngineering")
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
            text="A knowledge graph stores entities and relationships.",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/rag.md",
            sha256="s2",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="RAG",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 Overview",
            title="Overview",
            text="Retrieval augmented generation uses a knowledge graph.",
        )
        upsert_file(
            conn,
            doc_id="D0003",
            path="/c/ce.md",
            sha256="s3",
            mtime=0,
            corpus="research",
            status="active",
            extract_status="ok",
            title="Context Engineering",
            topic="ContextEngineering",
        )
        insert_chunk(
            conn,
            chunk_id="D0003#c001",
            doc_id="D0003",
            section_path="§1 Context",
            title="Context",
            text="Context engineering manages agent memory and prompts.",
        )


def test_section_tree_strips_composite_title(registry) -> None:
    """R-1（13 §3）：kb_show.sections[].title 剥复合标签，保持章节标题语义。"""
    from kbapp.core.registry import insert_chunk, upsert_file
    from kbapp.retrieve.assembler import section_tree

    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/06-Hong-Context_Rot.md",
            sha256="s1",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="Context Rot",
            topic=None,
        )
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 Introduction",
            title="06-Hong-Context_Rot | Introduction",
            text="body",
        )
    tree = section_tree(registry, "D0001")
    assert tree == [{"section_path": "§1 Introduction", "title": "Introduction"}]


def test_assemble_for_task_builds_context_and_sources(registry) -> None:
    """M4（13 §4）：assemble_for_task 确定性组装，sources 与 context_block 一致。"""
    from kbapp.core.config import Config
    from kbapp.retrieve.assembler import assemble_for_task

    _seed_assemble(registry)
    out = assemble_for_task(registry, Config.defaults(), "knowledge graph", budget=8000)
    assert "D0001" in out["context_block"]
    assert "D0002" in out["context_block"]
    assert out["used"] == len(out["context_block"]) // 4
    # sources 只含实际拼入的文档，锚点非空。
    assert {s["doc_id"] for s in out["sources"]} == {"D0001", "D0002"}
    assert all(s["section_path"] for s in out["sources"])


def test_assemble_for_task_truncates_by_budget(registry) -> None:
    """M4（13 §4）：超预算先砍尾部文档，sources 与被砍文档严格一致。"""
    from kbapp.core.config import Config
    from kbapp.retrieve.assembler import assemble_for_task

    _seed_assemble(registry)
    out = assemble_for_task(registry, Config.defaults(), "knowledge graph", budget=1)
    assert len(out["sources"]) == 1


def test_assemble_for_task_topics_filter(registry) -> None:
    """M4（13 §4）：topics 非空时逐 topic 硬过滤检索合并去重。"""
    from kbapp.core.config import Config
    from kbapp.retrieve.assembler import assemble_for_task

    _seed_assemble(registry)
    out = assemble_for_task(
        registry, Config.defaults(), "knowledge graph", budget=8000, topics=["CodeGraph"]
    )
    assert {s["doc_id"] for s in out["sources"]} == {"D0001", "D0002"}
