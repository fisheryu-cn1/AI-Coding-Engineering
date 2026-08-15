"""Unit tests for entity extraction (15 §4.2 / D15-13).

key invariants:

- entity_id = f"{type}:{norm(name)}" — same type + normalized name MERGE
- MENTIONS weight = name occurrence count in section text
- RELATES_TO.kind ∈ REL_KINDS; unknown kind dropped + counted
- No SAME_AS, no merge/redirect logic
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ladybug = pytest.importorskip("ladybug")


# ---------------------------------------------------------------------------
# norm / is_core_doc / entity_id pure-function tests
# ---------------------------------------------------------------------------


def test_norm_collides_across_cases_and_whitespace() -> None:
    from kbapp.graph.extract import norm

    assert norm("Retrieval-Augmented Generation") == norm("retrieval_augmented generation")
    assert norm("RAG") == norm("rag") == norm(" rag ")


def test_entity_id_format() -> None:
    from kbapp.graph.extract import entity_id

    assert entity_id("Method", "RAG") == "Method:rag"
    assert entity_id("Tool", "Vector DB") == "Tool:vector-db"


def test_is_core_doc_intersection_and_extra_docs(default_config) -> None:
    from kbapp.graph.extract import is_core_doc

    cfg = default_config
    assert is_core_doc(cfg, topic="ContextEngineering", doc_type="paper", doc_id="d1")
    assert is_core_doc(cfg, topic="context-engineering", doc_type="design", doc_id="d2")
    assert not is_core_doc(cfg, topic="random", doc_type="paper", doc_id="d3")
    assert not is_core_doc(cfg, topic="ContextEngineering", doc_type="note", doc_id="d4")

    cfg.raw["extract"]["extra_docs"] = ["d4"]
    assert is_core_doc(cfg, topic="ContextEngineering", doc_type="note", doc_id="d4")


# ---------------------------------------------------------------------------
# sync pipeline + extract end-to-end
# ---------------------------------------------------------------------------


def _seed_doc_for_extract(
    registry, paths, default_config, doc_id="d1", topic="ContextEngineering", doc_type="paper"
):
    """Plant files row + parse cache with RAG / Vector DB mentions."""
    from kbapp.core.registry import upsert_file, update_file_fields

    payload = {
        "sha256": "s",
        "path": "x.md",
        "format": "md",
        "parser": "markdown",
        "structure": "headers",
        "full_text": "RAG uses Vector DB. RAG uses Vector DB again.",
        "sections": [
            {
                "section_path": "1",
                "level": 1,
                "title": "Intro",
                "page_range": "",
                "text": "RAG uses Vector DB. RAG uses Vector DB again.",
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
            doc_type=doc_type,
            extract_status="ok",
            status="active",
            title="Paper",
            topic=topic,
        )
        update_file_fields(conn, doc_id, topic=topic)


class _FakeLLM:
    def __init__(self, payload):
        self._payload = payload
        self.calls = 0

    def complete(self, messages, **kwargs):
        self.calls += 1
        return json.dumps(self._payload)


def test_run_extract_writes_entities_mentions_relations(
    default_config, registry, paths, tmp_path
) -> None:
    """LLM 抽取 → Entity + MENTIONS + RELATES_TO；未知 kind 丢弃并计数。"""
    _seed_doc_for_extract(registry, paths, default_config)

    payload = {
        "entities": [
            {"name": "RAG", "type": "Method", "aliases": [], "description": "Retrieval-Augmented Generation"},
            {"name": "Vector DB", "type": "Tool", "aliases": [], "description": "Vector store"},
            {"name": "RAG", "type": "Method", "aliases": ["RAG"], "description": "dup"},  # 重复
        ],
        "relations": [
            {"src": "RAG", "dst": "Vector DB", "kind": "uses", "weight": 1.0, "evidence_section_id": "d1#1"},
            {"src": "RAG", "dst": "Vector DB", "kind": "uses", "weight": 0.5, "evidence_section_id": "d1#1"},  # 同对同 kind
            {"src": "RAG", "dst": "Vector DB", "kind": "kungfu", "weight": 1.0, "evidence_section_id": "d1#1"},  # 未知 kind
        ],
    }
    llm = _FakeLLM(payload)

    from kbapp.core.registry import get_file
    from kbapp.graph.extract import run_extract
    from kbapp.graph.store import make_graph_store
    from kbapp.pipeline.graph_stages import stage_index_graph
    from kbapp.pipeline.runner import PipelineCtx

    # 先入 Section 节点（反查 MENTIONS 端点必须存在；sync 先于 extract）
    ctx = PipelineCtx(cfg=default_config, paths=paths, registry=registry, llm=None)
    stage_index_graph("d1", ctx)

    with registry.read_only() as conn:
        row = get_file(conn, "d1")

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        metrics = run_extract(
            store=store,
            registry=registry,
            paths=paths,
            doc_id="d1",
            row=row,
            llm=llm,
            cfg=default_config,
        )
    finally:
        store.close()

    # 2 entities (RAG dedup), 1 RELATES_TO (冲突取 weight 高者), 1 dropped kind
    assert metrics["entities"] == 2
    assert metrics["relates_to"] == 1
    assert metrics["dropped_kind"] == 1

    # 复读验证
    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        rows = store.query(
            "MATCH (e:Entity) WHERE e.entity_id = $i RETURN e.name AS n, e.type AS t",
            {"i": "Method:rag"},
        )
        assert rows and rows[0]["n"] == "RAG"
        # MENTIONS weight = 实体名在 section 文本出现次数
        rows = store.query(
            "MATCH (s:Section)-[m:MENTIONS]->(e:Entity) RETURN e.entity_id AS eid, m.weight AS w"
        )
        weights = {r["eid"]: int(r["w"]) for r in rows}
        assert weights["Method:rag"] == 2
        assert weights["Tool:vector-db"] == 2
        # RELATES_TO 1 条
        rows = store.query(
            "MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity) RETURN a.entity_id AS a, b.entity_id AS b, r.kind AS k"
        )
        assert len(rows) == 1
        assert rows[0]["k"] == "uses"
    finally:
        store.close()


def test_run_extract_idempotent_replay(
    default_config, registry, paths, tmp_path
) -> None:
    """重复调用：不产生重复 Entity/RELATES_TO，无 SAME_AS（15 D15-13 唯一去重口径）。"""
    _seed_doc_for_extract(registry, paths, default_config)

    payload = {
        "entities": [{"name": "RAG", "type": "Method", "aliases": [], "description": ""}],
        "relations": [],
    }

    from kbapp.core.registry import get_file
    from kbapp.graph.extract import run_extract
    from kbapp.graph.store import make_graph_store
    from kbapp.pipeline.graph_stages import stage_index_graph
    from kbapp.pipeline.runner import PipelineCtx

    ctx = PipelineCtx(cfg=default_config, paths=paths, registry=registry, llm=None)
    stage_index_graph("d1", ctx)

    with registry.read_only() as conn:
        row = get_file(conn, "d1")

    for _ in range(2):
        llm = _FakeLLM(payload)
        store = make_graph_store("ladybug", default_config)
        store.open(str(paths.graph_dir / "graph.lbug"), "rw")
        try:
            run_extract(
                store=store,
                registry=registry,
                paths=paths,
                doc_id="d1",
                row=row,
                llm=llm,
                cfg=default_config,
            )
        finally:
            store.close()

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        rows = store.query("MATCH (e:Entity) RETURN e.entity_id AS id")
        assert len(rows) == 1
        assert rows[0]["id"] == "Method:rag"
        # 15 D15-13：消歧仅靠 entity_id 碰撞；同 entity_id 第二次 upsert 是 MERGE
    finally:
        store.close()


def test_run_extract_skip_on_missing_llm(
    default_config, registry, paths, tmp_path
) -> None:
    """LLM 不可用 → skip，不抛异常。"""
    _seed_doc_for_extract(registry, paths, default_config)

    from kbapp.core.registry import get_file
    from kbapp.graph.extract import run_extract
    from kbapp.graph.store import make_graph_store

    with registry.read_only() as conn:
        row = get_file(conn, "d1")

    store = make_graph_store("ladybug", default_config)
    store.open(str(paths.graph_dir / "graph.lbug"), "rw")
    try:
        metrics = run_extract(
            store=store,
            registry=registry,
            paths=paths,
            doc_id="d1",
            row=row,
            llm=None,
            cfg=default_config,
        )
    finally:
        store.close()
    assert metrics == {"entities": 0, "mentions": 0, "relates_to": 0, "dropped_kind": 0, "skipped": 1}
