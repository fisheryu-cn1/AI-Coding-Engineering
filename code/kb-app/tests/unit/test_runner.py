"""Unit tests for the pipeline runner (09 §10)."""

from __future__ import annotations

from pathlib import Path

import pytest

from kbapp.core.config import Config
from kbapp.core.fingerprint import fingerprint
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry, get_file
from kbapp.core.task import enqueue_task
from kbapp.pipeline.runner import PipelineCtx, run_pending_tasks


@pytest.fixture
def text_corpus(tmp_path: Path) -> Path:
    """A small text file; the runner will parse + chunk + classify it."""
    p = tmp_path / "doc.md"
    p.write_text(
        "# Topic: Context Engineering\n\nThis document studies retrieval.\n",
        encoding="utf-8",
    )
    return p


def _register_file(registry: Registry, paths: DataPaths, corpus_dir: Path) -> str:
    """Add one md file via scan-like path; return its doc_id."""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.task import enqueue_task

    p = corpus_dir / "doc.md"
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )
        enqueue_task(
            registry,
            kind="parse",
            payload={"doc_id": doc_id},
            conn=conn,
        )
    return doc_id


def test_runner_drains_queue_and_writes_chunks(tmp_path: Path, text_corpus: Path) -> None:
    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    doc_id = _register_file(registry, paths, tmp_path)

    ctx = PipelineCtx(
        cfg=Config.defaults(),
        paths=paths,
        registry=registry,
        llm=None,
    )
    report = run_pending_tasks(ctx)
    # parse 完成后入队 index 任务，runner 串行消费 → 2 个任务 done。
    assert report.tasks_done == 2
    assert report.tasks_failed == 0

    # Files row updated
    row = get_file(registry.connect(), doc_id)
    assert row is not None
    assert row.extract_status in ("ok", "flat")

    # FTS chunks were inserted
    from kbapp.core.registry import count_chunks_by_doc

    assert count_chunks_by_doc(registry.connect(), doc_id) >= 1

    # Cache payload written
    cache_files = list(paths.extracted_dir.glob("*.json"))
    assert cache_files, "cache/extracted/<sha>.json missing"

    # Graph Document 节点已落（index 任务已跑）
    from kbapp.graph.store import make_graph_store

    paths.ensure_dirs()
    store = make_graph_store("ladybug", Config.defaults())
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        rows = store.query(
            "MATCH (d:Document) WHERE d.doc_id = $i RETURN d.title AS t",
            {"i": doc_id},
        )
        assert rows == [{"t": text_corpus} | {"t": "Topic: Context Engineering"}] or len(rows) == 1
    finally:
        store.close()


def test_runner_max_tasks_caps_iterations(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    # Enqueue 3 dummy tasks but cap at 2.
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate

    doc_ids = []
    for i in range(3):
        # Each task requires a real file to pass stage_parse.
        p = tmp_path / f"d{i}.md"
        p.write_text(f"# Title {i}\n\nbody {i}.\n", encoding="utf-8")
        sha, mtime = fingerprint(p)
        with registry.transaction() as conn:
            doc_id = apply_new_or_duplicate(
                conn,
                action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
                corpus="references",
                is_duplicate=False,
            )
            enqueue_task(
                registry,
                kind="parse",
                payload={"doc_id": doc_id},
                conn=conn,
            )
            doc_ids.append(doc_id)

    ctx = PipelineCtx(
        cfg=Config.defaults(),
        paths=paths,
        registry=registry,
        llm=None,
        max_tasks=2,
    )
    report = run_pending_tasks(ctx)
    assert report.tasks_done == 2
    # 中间产物：3 parse - 2 done = 1 parse pending；前 2 个 parse 各自入队 1 个
    # index，所以挂账 1 个 parse + 2 个 index = 3 pending。
    from kbapp.core.task import count_tasks

    assert count_tasks(registry, status="pending") == 3


def test_runner_leaves_non_parse_tasks_pending(tmp_path: Path) -> None:
    """Non-parse tasks stay pending (never swallowed as done) — M3+ handles them (P3-6)."""
    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    enqueue_task(registry, kind="classify", payload={"foo": "bar"})
    ctx = PipelineCtx(
        cfg=Config.defaults(),
        paths=paths,
        registry=registry,
        llm=None,
    )
    report = run_pending_tasks(ctx)
    assert report.tasks_done == 0
    assert report.tasks_failed == 0

    from kbapp.core.task import count_tasks

    assert count_tasks(registry, status="pending") == 1


def test_runner_no_tasks_returns_empty_report(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()
    ctx = PipelineCtx(
        cfg=Config.defaults(),
        paths=paths,
        registry=registry,
        llm=None,
    )
    report = run_pending_tasks(ctx)
    assert report.tasks_done == 0
    assert report.tasks_failed == 0


def test_stage_classify_needs_confirm_clears_topic(tmp_path: Path) -> None:
    """needs_confirm must clear a stale topic and rebalance doc_count (P2-3)."""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import (
        adjust_topic_doc_count,
        get_file,
        get_topic,
        update_file_fields,
        upsert_topic,
    )
    from kbapp.pipeline.stages import stage_classify

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "doc.md"
    p.write_text("# Note\n\nrandom content\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )
        upsert_topic(conn, name="ContextEngineering")
        adjust_topic_doc_count(conn, "ContextEngineering", 1)
        update_file_fields(conn, doc_id, topic="ContextEngineering", extract_status="flat")

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=None)
    stage_classify(doc_id, ctx)

    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
        topic = get_topic(conn, "ContextEngineering")
    assert row.topic is None
    assert row.status == "needs_confirm"
    assert topic.doc_count == 0


def test_stage_parse_writes_title_and_cache_metrics(tmp_path: Path) -> None:
    """stage_parse persists files.title and cache page_count/header_count/coverage (P3-3)."""
    import json

    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import get_file
    from kbapp.pipeline.stages import stage_parse

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "doc.md"
    p.write_text("# My Title\n\nBody text here.\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=None)
    assert stage_parse(doc_id, ctx).status == "ok"

    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
    assert row.title == "My Title"

    cache = json.loads((paths.extracted_dir / f"{sha}.json").read_text(encoding="utf-8"))
    assert "page_count" in cache
    assert "header_count" in cache
    assert "coverage" in cache
    assert cache["header_count"] >= 1


def test_stage_summarize_writes_auto_summary_and_chunk(tmp_path: Path) -> None:
    """stage_summarize 写 auto_summaries/<doc_id>.md + $summary 伪 chunk（11 §3）。"""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import get_file
    from kbapp.pipeline.stages import stage_chunk, stage_parse, stage_summarize

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "doc.md"
    p.write_text("# Title\n\nBody text.\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"l1": "一句话", "l2": "观点", "l3": "细节"}'

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=_FakeLLM())
    assert stage_parse(doc_id, ctx).status == "ok"
    assert stage_chunk(doc_id, ctx).status == "ok"
    assert stage_summarize(doc_id, ctx).status == "ok"

    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
        chunk = conn.execute(
            "SELECT section_path, text FROM fts_chunks WHERE chunk_id = ?",
            (f"{doc_id}#summary",),
        ).fetchone()
    assert row.summary_source == "auto"
    assert row.summary_path
    assert (paths.auto_summaries_dir / f"{doc_id}.md").exists()
    assert chunk is not None and chunk["section_path"] == "$summary"
    assert "一句话" in chunk["text"]


def test_stage_classify_enqueues_summarize_when_llm_available(tmp_path: Path) -> None:
    """分类成功后入队 summarize 任务（11 §3.1 触发条件）。"""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import update_file_fields
    from kbapp.core.task import list_tasks
    from kbapp.pipeline.stages import stage_classify

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "note.md"
    p.write_text("# Note\n\ncontent\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )
        update_file_fields(conn, doc_id, extract_status="flat")

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"doc_type": "paper"}'

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=_FakeLLM())
    stage_classify(doc_id, ctx)

    summarize_tasks = [t for t in list_tasks(registry, limit=100) if t.kind == "summarize"]
    assert len(summarize_tasks) == 1
    assert summarize_tasks[0].payload.get("doc_id") == doc_id


def test_stage_classify_skips_summarize_for_curated(tmp_path: Path) -> None:
    """curated 非 stale 文档不入队 summarize（11 §3.1 curated 跳过）。"""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import update_file_fields
    from kbapp.core.task import list_tasks
    from kbapp.pipeline.stages import stage_classify

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "note.md"
    p.write_text("# Note\n\ncontent\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )
        update_file_fields(
            conn,
            doc_id,
            extract_status="flat",
            summary_source="curated",
            summary_stale=0,
        )

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"doc_type": "paper"}'

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=_FakeLLM())
    stage_classify(doc_id, ctx)

    summarize_tasks = [t for t in list_tasks(registry, limit=100) if t.kind == "summarize"]
    assert summarize_tasks == []


def test_stage_classify_llm_fallback_for_doc_type(tmp_path: Path) -> None:
    """doc_type rule ⑤ uses the LLM client when available (09 §7.3 / P2-2)."""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import get_file, update_file_fields
    from kbapp.pipeline.stages import stage_classify

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "note.md"  # .md in references → falls through to 'other'
    p.write_text("# Note\n\ncontent\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )
        update_file_fields(conn, doc_id, extract_status="flat")

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"doc_type": "design"}'

    ctx = PipelineCtx(
        cfg=Config.defaults(),
        paths=paths,
        registry=registry,
        llm=_FakeLLM(),
    )
    stage_classify(doc_id, ctx)

    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
    assert row.doc_type == "design"


def test_stage_summarize_stale_curated_preserves_provenance(tmp_path: Path) -> None:
    """stale-curated：写 auto 临时文件与 $summary 伪 chunk，但 provenance 不变（11 §3.1）。

    ``summary_source``/``summary_path``/``summary_stale`` 全部保持原值，
    auto_summaries/<doc_id>.md 照常写出。
    """
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import get_file, update_file_fields
    from kbapp.pipeline.stages import stage_chunk, stage_parse, stage_summarize

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "doc.md"
    p.write_text("# Title\n\nBody text.\n", encoding="utf-8")
    curated = tmp_path / "curated_summary.md"
    curated.write_text("人工策展摘要\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )
        update_file_fields(
            conn,
            doc_id,
            summary_source="curated",
            summary_path=str(curated),
            summary_stale=1,
        )

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"l1": "一句话", "l2": "观点", "l3": "细节"}'

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=_FakeLLM())
    assert stage_parse(doc_id, ctx).status == "ok"
    assert stage_chunk(doc_id, ctx).status == "ok"
    assert stage_summarize(doc_id, ctx).status == "ok"

    auto_path = paths.auto_summaries_dir / f"{doc_id}.md"
    assert auto_path.exists(), "auto 临时摘要文件应已写出"
    assert "一句话" in auto_path.read_text(encoding="utf-8")

    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
        chunk = conn.execute(
            "SELECT section_path, text FROM fts_chunks WHERE chunk_id = ?",
            (f"{doc_id}#summary",),
        ).fetchone()
    # provenance 不丢：三个字段全部未变。
    assert row.summary_source == "curated"
    assert row.summary_path == str(curated)
    assert row.summary_stale == 1
    # $summary 伪 chunk 写的是 auto 文本。
    assert chunk is not None and chunk["section_path"] == "$summary"
    assert "一句话" in chunk["text"]


def test_stage_summarize_idempotent_replay(tmp_path: Path) -> None:
    """重跑 stage_summarize 幂等：$summary 伪 chunk 先删后插只有一条，auto 文件一致（11 §3.4）。"""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.pipeline.stages import stage_chunk, stage_parse, stage_summarize

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "doc.md"
    p.write_text("# Title\n\nBody text.\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"l1": "一句话", "l2": "观点", "l3": "细节"}'

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=_FakeLLM())
    assert stage_parse(doc_id, ctx).status == "ok"
    assert stage_chunk(doc_id, ctx).status == "ok"
    assert stage_summarize(doc_id, ctx).status == "ok"
    auto_path = paths.auto_summaries_dir / f"{doc_id}.md"
    first_content = auto_path.read_text(encoding="utf-8")
    assert stage_summarize(doc_id, ctx).status == "ok"

    with registry.read_only() as conn:
        rows = conn.execute(
            "SELECT chunk_id FROM fts_chunks WHERE chunk_id = ?",
            (f"{doc_id}#summary",),
        ).fetchall()
    assert len(rows) == 1, "重跑后应只有一条 <doc_id>#summary（先删后插幂等）"
    assert auto_path.read_text(encoding="utf-8") == first_content


def test_stage_summarize_skip_when_llm_absent(tmp_path: Path) -> None:
    """LLM 不可用：stage_summarize 返回 skip，不写文件不写伪 chunk；读取侧回退不断链（11 §3.1）。"""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.core.registry import get_file
    from kbapp.pipeline.stages import stage_chunk, stage_parse, stage_summarize
    from kbapp.retrieve.assembler import read_summary

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "doc.md"
    p.write_text("# Title\n\nBody text.\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=None)
    assert stage_parse(doc_id, ctx).status == "ok"
    assert stage_chunk(doc_id, ctx).status == "ok"
    result = stage_summarize(doc_id, ctx)
    assert result.status == "skip"

    assert not (paths.auto_summaries_dir / f"{doc_id}.md").exists()
    with registry.read_only() as conn:
        chunk = conn.execute(
            "SELECT chunk_id FROM fts_chunks WHERE chunk_id = ?",
            (f"{doc_id}#summary",),
        ).fetchone()
        row = get_file(conn, doc_id)
    assert chunk is None
    # 检索读取侧回退：无摘要时 read_summary 返回 None（不断链，仅信号降档）。
    assert read_summary(registry, row) is None


def test_stage_chunk_writes_composite_title(tmp_path: Path) -> None:
    """R-1（13 §3）：stage_chunk 写 ``{stem} | {章节标题}`` 复合 title 进 FTS。"""
    from kbapp.core.files import ACTION_NEW, ScanAction, apply_new_or_duplicate
    from kbapp.core.fingerprint import fingerprint
    from kbapp.pipeline.stages import stage_chunk, stage_parse

    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    registry = Registry(paths.registry_db)
    registry.initialize()

    p = tmp_path / "06-Hong-Context_Rot.md"
    p.write_text("# Introduction\n\nContext rot degrades models.\n", encoding="utf-8")
    sha, mtime = fingerprint(p)
    with registry.transaction() as conn:
        doc_id = apply_new_or_duplicate(
            conn,
            action=ScanAction(ACTION_NEW, None, str(p), sha, mtime),
            corpus="references",
            is_duplicate=False,
        )

    ctx = PipelineCtx(cfg=Config.defaults(), paths=paths, registry=registry, llm=None)
    assert stage_parse(doc_id, ctx).status == "ok"
    assert stage_chunk(doc_id, ctx).status == "ok"

    with registry.read_only() as conn:
        rows = conn.execute("SELECT title FROM fts_chunks WHERE doc_id = ?", (doc_id,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["title"] == "06-Hong-Context_Rot | Introduction"
