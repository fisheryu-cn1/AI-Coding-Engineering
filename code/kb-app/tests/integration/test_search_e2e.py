"""Integration test: M3 retrieval CLI（kb search/show/read/topics/related/compare）。"""

from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from kbapp.cli.main import app

runner = CliRunner()


def _setup(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    corpus_dir = tmp_path / "corpus"
    for c in ("references", "research", "design"):
        (corpus_dir / c).mkdir(parents=True)
    (corpus_dir / "references" / "rag.md").write_text(
        "# Retrieval Augmented Generation\n\n## Overview\n\nRAG combines LLMs "
        "with knowledge graph retrieval.\n",
        encoding="utf-8",
    )
    (corpus_dir / "design" / "kg.md").write_text(
        "# Knowledge Graph\n\n## Design\n\nThe knowledge graph stores entities.\n",
        encoding="utf-8",
    )
    runner.invoke(app, ["--data-dir", str(data_dir), "init"])
    cfg_path = data_dir / "config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["corpus_roots"] = {
        "references": str(corpus_dir / "references"),
        "research": str(corpus_dir / "research"),
        "design": str(corpus_dir / "design"),
    }
    cfg_path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "scan"])
    runner.invoke(app, ["--data-dir", str(data_dir), "index", "run"])
    return data_dir


def test_search_and_read_endtoend(tmp_path: Path) -> None:
    data_dir = _setup(tmp_path)

    r = runner.invoke(app, ["--data-dir", str(data_dir), "search", "knowledge graph"])
    assert r.exit_code == 0, r.stdout
    assert "Knowledge Graph" in r.stdout

    r = runner.invoke(app, ["--data-dir", str(data_dir), "show", "D0001"])
    assert r.exit_code == 0, r.stdout
    assert "章节树" in r.stdout

    r = runner.invoke(
        app,
        [
            "--data-dir",
            str(data_dir),
            "read",
            "D0001",
            "§1 Retrieval Augmented Generation > §2 Overview",
        ],
    )
    assert r.exit_code == 0, r.stdout
    assert "RAG combines" in r.stdout


def test_search_vector_mode_errors(tmp_path: Path) -> None:
    data_dir = _setup(tmp_path)
    r = runner.invoke(app, ["--data-dir", str(data_dir), "search", "x", "--mode", "vector"])
    assert r.exit_code == 1
    assert "P1" in (r.stdout + r.stderr)


def test_topics_lists_seeded_topics(tmp_path: Path) -> None:
    data_dir = _setup(tmp_path)
    r = runner.invoke(app, ["--data-dir", str(data_dir), "topics"])
    assert r.exit_code == 0, r.stdout
    assert "ContextEngineering" in r.stdout


def test_search_topic_global_mode(tmp_path: Path) -> None:
    data_dir = _setup(tmp_path)
    r = runner.invoke(app, ["--data-dir", str(data_dir), "search", "x", "--mode", "topic-global"])
    assert r.exit_code == 0, r.stdout


def test_embedding_backend_warning_when_local_without_deps(tmp_path: Path) -> None:
    """embedding.backend != none 且依赖缺失 → 警告按 none 运行（11 §5 / P2-5）。"""
    data_dir = _setup(tmp_path)
    cfg_path = data_dir / "config.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["embedding"]["backend"] = "local"
    cfg_path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")

    r = runner.invoke(app, ["--data-dir", str(data_dir), "topics"])
    assert r.exit_code == 0
    assert "按 none 运行" in (r.stdout + r.stderr)
