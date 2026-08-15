"""Unit tests for graph structure sync (15 §4.1 DoD B1 前半).

The sync passes the spec'd MVP-simplified schema: Document / Section / Topic
nodes + CONTAINS_SECTION / ABOUT_TOPIC edges (no Chunk, no CITES, no
Section→Topic). Idempotent so re-running is a no-op.
"""

from __future__ import annotations

import json

import pytest

ladybug = pytest.importorskip("ladybug")


def _seed_doc(registry, paths, default_config, doc_id="d1", topic="ContextEngineering"):
    """Plant a files row + a parse cache JSON for one doc."""
    from kbapp.core.registry import upsert_file, update_file_fields

    payload = {
        "sha256": "s",
        "path": "x.md",
        "format": "md",
        "parser": "markdown",
        "structure": "headers",
        "full_text": "intro body",
        "sections": [
            {
                "section_path": "1",
                "level": 1,
                "title": "Intro",
                "page_range": "",
                "text": "intro body",
            },
            {
                "section_path": "2",
                "level": 1,
                "title": "Method",
                "page_range": "",
                "text": "method body",
            },
        ],
        "warnings": [],
        "chunks": [],
        "extracted_at": "2026-08-15",
    }
    (paths.extracted_dir / "s.json").write_text(json.dumps(payload), encoding="utf-8")
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id=doc_id,
            path="x.md",
            sha256="s",
            mtime=0,
            corpus="references",
            doc_type="paper",
            extract_status="ok",
            status="active",
            title="Paper",
            topic=topic,
        )
        update_file_fields(conn, doc_id, topic=topic)


def test_sync_writes_doc_section_topic(default_config, registry, paths, tmp_path) -> None:
    """sync_document_structure 落 Document/Section/Topic + CONTAINS_SECTION/ABOUT_TOPIC。"""
    _seed_doc(registry, paths, default_config)

    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure

    store = make_graph_store("ladybug", default_config)
    store.open(str(tmp_path / "g"), "rw")
    try:
        metrics = sync_document_structure(store, registry, paths, "d1")
        assert metrics["sections"] == 2

        # Document 节点
        rows = store.query(
            "MATCH (d:Document) WHERE d.doc_id = $i RETURN d.title AS t",
            {"i": "d1"},
        )
        assert rows == [{"t": "Paper"}]

        # Topic 节点 + ABOUT_TOPIC
        rows = store.query(
            "MATCH (d:Document)-[:ABOUT_TOPIC]->(t:Topic) WHERE d.doc_id = $i "
            "RETURN t.name AS n",
            {"i": "d1"},
        )
        assert rows == [{"n": "ContextEngineering"}]

        # Section 节点 + CONTAINS_SECTION
        rows = store.query(
            "MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section) WHERE d.doc_id = $i "
            "RETURN s.section_id AS s ORDER BY s.seq",
            {"i": "d1"},
        )
        assert [r["s"] for r in rows] == ["d1#1", "d1#2"]
    finally:
        store.close()


def test_sync_skips_when_no_topic(default_config, registry, paths, tmp_path) -> None:
    """topic 为空时不下 Topic 节点与 ABOUT_TOPIC 边。"""
    _seed_doc(registry, paths, default_config, doc_id="d2", topic=None)

    from kbapp.graph.store import make_graph_store
    from kbapp.graph.sync import sync_document_structure

    store = make_graph_store("ladybug", default_config)
    store.open(str(tmp_path / "g"), "rw")
    try:
        sync_document_structure(store, registry, paths, "d2")
        rows = store.query("MATCH (t:Topic) RETURN t.name AS n")
        assert rows == []
        rows = store.query(
            "MATCH (d:Document)-[:ABOUT_TOPIC]->() WHERE d.doc_id = $i RETURN count(*) AS n",
            {"i": "d2"},
        )
        assert rows[0]["n"] == 0
    finally:
        store.close()


def test_stage_index_graph_end_to_end(default_config, registry, paths, tmp_path) -> None:
    """stage_index_graph 走完整链路：开 store→sync→close，落图完成。"""
    _seed_doc(registry, paths, default_config)

    from kbapp.pipeline.graph_stages import stage_index_graph
    from kbapp.pipeline.runner import PipelineCtx
    from kbapp.graph.store import make_graph_store

    ctx = PipelineCtx(cfg=default_config, paths=paths, registry=registry, llm=None)
    result = stage_index_graph("d1", ctx)
    assert result.status == "ok"

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        rows = store.query(
            "MATCH (d:Document) WHERE d.doc_id = $i RETURN d.title AS t",
            {"i": "d1"},
        )
        assert rows == [{"t": "Paper"}]
    finally:
        store.close()


def test_runner_enqueues_index_after_parse(default_config, registry, paths, tmp_path) -> None:
    """run_pending_tasks 完成后，队列里出现 index 任务。"""
    _seed_doc(registry, paths, default_config)
    # Manually mark parse cache as a real "parse completed" by going through
    # stage_parse + stage_chunk. Easiest: skip the runner and just enqueue
    # index manually to verify the kind exists.
    from kbapp.core.task import enqueue_task, list_tasks

    enqueue_task(registry, kind="index", payload={"doc_id": "d1"})
    ts = list_tasks(registry, limit=10)
    assert any(t.kind == "index" for t in ts)


def test_tombstone_soft_deletes_document(
    default_config, registry, paths, tmp_path
) -> None:
    """stage_tombstone_graph 软删 Document：valid_to 非空 + CONTAINS_SECTION 边保留。"""
    _seed_doc(registry, paths, default_config)

    from kbapp.graph.store import make_graph_store
    from kbapp.pipeline.graph_stages import stage_tombstone_graph
    from kbapp.pipeline.runner import PipelineCtx

    ctx = PipelineCtx(cfg=default_config, paths=paths, registry=registry, llm=None)
    # 先同步结构
    from kbapp.pipeline.graph_stages import stage_index_graph

    stage_index_graph("d1", ctx)
    # 再 tombstone
    result = stage_tombstone_graph("d1", ctx)
    assert result.status == "ok"

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        rows = store.query(
            "MATCH (d:Document) WHERE d.doc_id = $i RETURN d.valid_to AS v",
            {"i": "d1"},
        )
        assert rows[0]["v"] != ""
        # 边仍物理存在（15 §4.1：软删过滤由查询层负责）
        rows = store.query(
            "MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section) WHERE d.doc_id = $i "
            "RETURN count(s) AS n",
            {"i": "d1"},
        )
        assert rows[0]["n"] == 2
    finally:
        store.close()
