"""End-to-end integration test: ``kb init`` + ``kb index scan/run`` cycle.

Exercises the M2 CLI surface against a temp corpus and validates the full
state machine (file discovery → doc_id allocation → enqueue → run → FTS).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from kbapp.cli.main import app
from kbapp.core.paths import DataPaths
from kbapp.core.registry import (
    Registry,
    count_chunks,
    get_file,
    list_files,
)

runner = CliRunner()


def _patch_corpus_roots(data_dir: Path, corpus_dir: Path) -> None:
    cfg_path = data_dir / "config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["corpus_roots"] = {
        "references": str(corpus_dir / "references"),
        "research": str(corpus_dir / "research"),
        "design": str(corpus_dir / "design"),
    }
    cfg_path.write_text(
        yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def test_init_scan_run_endtoend(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)

    # Sample corpus: 1 PDF-shaped text, 1 MD, 1 txt.
    (corpus_dir / "references" / "paper.md").write_text(
        "# Title\n\nBody about retrieval-augmented context engineering.\n",
        encoding="utf-8",
    )
    (corpus_dir / "research" / "notes.txt").write_text(
        "Research notes: agentic AI coding workflows.\n",
        encoding="utf-8",
    )
    (corpus_dir / "design" / "arch.md").write_text(
        "# Design\n\nKnowledge graph architecture overview.\n",
        encoding="utf-8",
    )

    # 1. init
    r = runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    assert r.exit_code == 0, r.stdout
    _patch_corpus_roots(data_dir, corpus_dir)

    # 2. scan — must allocate doc_ids and enqueue 3 parse tasks.
    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    assert r.exit_code == 0, r.stdout
    paths = DataPaths.from_data_dir(data_dir)
    reg = Registry(paths.registry_db)
    with reg.read_only() as conn:
        files = list_files(conn)
    assert len(files) == 3
    doc_ids = {f.doc_id for f in files}
    assert {"D0001", "D0002", "D0003"} == doc_ids

    # 3. run — drains queue, populates FTS.
    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "run"])
    assert r.exit_code == 0, r.stdout
    assert count_chunks(reg.connect()) >= 3

    # 4. status — files have extract_status ok/flat.
    r = runner.invoke(app, ["--data-dir", str(data_dir), "status"])
    assert r.exit_code == 0, r.stdout
    assert "SCHEMA_VERSION" in r.stdout


def test_scan_idempotent_second_pass(tmp_path: Path) -> None:
    """Second scan must not allocate new doc_ids (零变更)."""
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    (corpus_dir / "references" / "a.md").write_text("# A\n\nbody\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)

    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])

    reg = Registry(data_dir / "registry.sqlite")
    with reg.read_only() as conn:
        files = list_files(conn)
    assert len(files) == 1


def test_add_external_file(tmp_path: Path) -> None:
    """``kb index add`` registers an external file with corpus='external'."""
    data_dir = tmp_path / "data"
    ext_file = tmp_path / "extra.md"
    ext_file.write_text("# External\n\nnotes\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])

    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "add", str(ext_file)])
    assert r.exit_code == 0, r.stdout

    reg = Registry(data_dir / "registry.sqlite")
    with reg.read_only() as conn:
        files = list_files(conn, corpus="external")
    assert len(files) == 1
    assert files[0].path == str(ext_file.resolve())


def test_add_duplicate_path_errors(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    ext_file = tmp_path / "extra.md"
    ext_file.write_text("# E\n", encoding="utf-8")
    runner.invoke(app, ["--data-dir", str(data_dir), "init"])

    runner.invoke(app, ["--data-dir", str(data_dir), "index", "add", str(ext_file)])
    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "add", str(ext_file)])
    assert r.exit_code == 1


def test_set_topic_updates_doc_count(tmp_path: Path) -> None:
    """``set-topic`` should immediately update ``topics.doc_count``."""
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    (corpus_dir / "references" / "f.md").write_text("# F\n\nbody\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "run"])

    # Now override topic for D0001.
    r = runner.invoke(
        app,
        ["--data-dir", str(data_dir), "index", "set-topic", "D0001", "ai-coding"],
    )
    assert r.exit_code == 0, r.stdout

    reg = Registry(data_dir / "registry.sqlite")
    from kbapp.core.registry import get_topic

    with reg.read_only() as conn:
        topic = get_topic(conn, "ai-coding")
        row = get_file(conn, "D0001")
    assert topic is not None and topic.doc_count == 1
    assert row.topic == "ai-coding"
    assert row.status == "active"


def test_status_runs_against_populated_db(tmp_path: Path) -> None:
    """Status should render topics table + needs_confirm list when populated."""
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    (corpus_dir / "references" / "g.md").write_text("# G\n\nbody\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "run"])

    r = runner.invoke(app, ["--data-dir", str(data_dir), "status"])
    assert r.exit_code == 0
    assert "topics" in r.stdout
    # needs_confirm: default classify.topic_keywords={} → all docs land in NC queue
    assert "needs_confirm" in r.stdout


def test_move_preserves_doc_id(tmp_path: Path) -> None:
    """Moving a file across corpora keeps its doc_id and is not tombstoned (P0-1)."""
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    src = corpus_dir / "references" / "a.md"
    src.write_text("# A\n\nbody\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])

    dst = corpus_dir / "research" / "a.md"
    src.rename(dst)

    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    assert r.exit_code == 0, r.stdout

    reg = Registry(data_dir / "registry.sqlite")
    with reg.read_only() as conn:
        files = list_files(conn)
    assert len(files) == 1
    assert files[0].doc_id == "D0001"
    assert files[0].path == str(dst)
    assert files[0].status != "deleted"


def test_delete_two_files_no_crash(tmp_path: Path) -> None:
    """Deleting two files in one scan must not hit the UNIQUE(path) constraint (P0-2)."""
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    a = corpus_dir / "references" / "a.md"
    b = corpus_dir / "references" / "b.md"
    a.write_text("# A\n\nbody\n", encoding="utf-8")
    b.write_text("# B\n\nbody\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])

    a.unlink()
    b.unlink()

    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    assert r.exit_code == 0, r.stdout

    reg = Registry(data_dir / "registry.sqlite")
    with reg.read_only() as conn:
        files = list_files(conn)
    assert len(files) == 2
    assert {f.status for f in files} == {"deleted"}


def test_manifest_mismatch_reported(tmp_path: Path) -> None:
    """A summary whose source_pdf matches nothing is reported + written to reports/ (P1-2)."""
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    (corpus_dir / "references" / "a.md").write_text("# A\n\nbody\n", encoding="utf-8")
    sum_dir = corpus_dir / "references" / "summaries"
    sum_dir.mkdir(parents=True)
    (sum_dir / "s.md").write_text(
        "---\ntitle: 'X'\nsource_pdf: 'missing.pdf'\n---\n",
        encoding="utf-8",
    )

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)
    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    assert r.exit_code == 0, r.stdout
    assert "manifest 不匹配" in r.stdout

    paths = DataPaths.from_data_dir(data_dir)
    reports = list(paths.reports_dir.glob("manifest_mismatch_*.json"))
    assert reports, "expected a manifest mismatch report in reports/"


def test_reindex_full_clears_fts(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    (corpus_dir / "references").mkdir(parents=True)
    (corpus_dir / "research").mkdir(parents=True)
    (corpus_dir / "design").mkdir(parents=True)
    (corpus_dir / "references" / "h.md").write_text("# H\n\nbody\n", encoding="utf-8")

    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    _patch_corpus_roots(data_dir, corpus_dir)
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "run"])

    reg = Registry(data_dir / "registry.sqlite")
    chunks_before = count_chunks(reg.connect())
    assert chunks_before >= 1

    r = runner.invoke(app, ["--data-dir", str(data_dir), "index", "reindex", "--full"])
    assert r.exit_code == 0, r.stdout
    assert count_chunks(reg.connect()) == 0
