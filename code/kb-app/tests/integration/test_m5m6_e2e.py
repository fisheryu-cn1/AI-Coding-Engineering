"""M5/M6 端到端验收（15 §8 / Task 20 DoD D4 全链路）。

真实语料小子集走 `init → scan → run`（此处用合成语料 + fake LLM，CI 无网络；
真实 MiniMax LLM 验收见 Task 20 Step 1 实机执行记录）：
- 图内 Document 数 = files 数
- is_core 文档全部有 Entity
- 非 core 文档无 extract 任务（无实体）
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def _seed_corpus(tmp_path: Path) -> Path:
    """4 篇语料：2 篇 core（paper/design + core topic）、2 篇 non-core。

    文件名含 arxiv ID 格式（如 2401.00001.md）以触发 doc_type=paper；
    corpus=design 触发 doc_type=design。topic 经 classify.topic_keywords
    关键词打分落地（core 命中 core_topics，non-core 落 NULL → needs_confirm）。
    """
    root = tmp_path / "corpus"
    (root / "references").mkdir(parents=True)
    (root / "research").mkdir()
    (root / "design").mkdir()

    # core 1: paper + ContextEngineering topic（arxiv ID 文件名 → paper）
    (root / "references" / "2401.00001.md").write_text(
        "# Context Engineering\n\nRAG uses Vector DB. RAG uses Vector DB.\n",
        encoding="utf-8",
    )
    # core 2: design + ai-coding topic（corpus=design → design）
    (root / "design" / "ai-design.md").write_text(
        "# AI Coding Design\n\nRAG uses Vector DB for code search.\n",
        encoding="utf-8",
    )
    # non-core 1: research corpus, 无关主题
    (root / "research" / "random.md").write_text(
        "# Random\n\nunrelated content.\n",
        encoding="utf-8",
    )
    # non-core 2: research corpus, 命中 core 关键词但 doc_type=other（.md 非 paper/design）
    (root / "research" / "note.md").write_text(
        "# Note\n\ncontext engineering notes.\n",
        encoding="utf-8",
    )
    return root


class _FakeLLM:
    """Fake LLM：按 purpose 分派；无网络、确定性输出。"""

    def complete(self, messages, **kwargs):
        purpose = kwargs.get("purpose", "classify")
        if purpose == "summarize":
            return json.dumps({"l1": "L1 summary", "l2": "L2 summary", "l3": "L3 summary"})
        if purpose == "arbitrate":
            return json.dumps({"doc_type": "other"})
        # extract：core 文档（标题含 core 主题）产实体 + 关系
        title_blob = " ".join(m.get("content", "") for m in messages)
        if "Context Engineering" in title_blob or "AI Coding" in title_blob:
            return json.dumps(
                {
                    "entities": [
                        {"name": "RAG", "type": "Method", "aliases": [], "description": ""},
                        {"name": "Vector DB", "type": "Tool", "aliases": [], "description": ""},
                    ],
                    "relations": [
                        {
                            "src": "RAG",
                            "dst": "Vector DB",
                            "kind": "uses",
                            "weight": 1.0,
                            "evidence_section_id": "",
                        },
                    ],
                }
            )
        return json.dumps({"entities": [], "relations": []})


@pytest.mark.integration
def test_m5m6_e2e_full_pipeline(tmp_path: Path, monkeypatch) -> None:
    """init → scan → run 全链路；图谱 + 实体 + 抽取。"""
    from typer.testing import CliRunner

    from kbapp.cli.main import app
    from kbapp.core.config import Config, dump_config
    from kbapp.core.paths import DataPaths
    from kbapp.core.registry import Registry
    from kbapp.graph import make_graph_store

    corpus = _seed_corpus(tmp_path)
    data_dir = tmp_path / "data"
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()

    cfg = Config.defaults()
    cfg.raw["corpus_roots"] = {
        "references": str(corpus / "references"),
        "research": str(corpus / "research"),
        "design": str(corpus / "design"),
    }
    cfg.raw["core_topics"] = ["ContextEngineering", "context-engineering", "ai-coding"]
    cfg.raw["extract"]["doc_types"] = ["paper", "design"]
    # classify 关键词打分：core 文档据此落地 core topic（is_core 的 topic 门）
    cfg.raw["classify"]["topic_keywords"] = {
        "ContextEngineering": ["context engineering"],
        "ai-coding": ["ai coding"],
    }
    dump_config(cfg, paths.config_path)

    monkeypatch.setenv("GRAPHIT_KB_DATA_DIR", str(data_dir))

    # 用 fake LLM 替换真实 client（CI 无网络）。注意：`run_cmd` 在 cli/index.py
    # 内以 `from kbapp.llm import get_llm_or_none` 绑定到局部名，须 patch 使用点。
    import kbapp.cli.index as index_mod

    monkeypatch.setattr(index_mod, "get_llm_or_none", lambda _cfg: _FakeLLM())

    runner = CliRunner()

    # 1. init
    r = runner.invoke(app, ["init"])
    assert r.exit_code == 0, r.stdout

    # 2. scan
    r = runner.invoke(app, ["index", "scan"])
    assert r.exit_code == 0, r.stdout

    # 3. run（triggers parse → index → extract）
    r = runner.invoke(app, ["index", "run", "--max-tasks", "50"])
    assert r.exit_code == 0, r.stdout

    # 4. 验证图结构
    registry = Registry(paths.registry_db)
    registry.initialize()
    with registry.read_only() as conn:
        rows = conn.execute("SELECT doc_id, topic, doc_type, status FROM files").fetchall()
    files = [dict(r) for r in rows]
    non_dup_ids = {f["doc_id"] for f in files if f["status"] != "duplicate"}

    store = make_graph_store("ladybug", cfg)
    store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    try:
        docs = store.query("MATCH (d:Document) WHERE d.valid_to = '' RETURN d.doc_id AS id")
        doc_ids = {r["id"] for r in docs}
        # 断言 1：图内 Document 数 = files 数（无 duplicate 时）
        assert doc_ids == non_dup_ids, (
            f"graph docs {sorted(doc_ids)} != files {sorted(non_dup_ids)}"
        )

        entity_rows = store.query(
            "MATCH (s:Section)-[:MENTIONS]->(e:Entity) RETURN DISTINCT s.doc_id AS did"
        )
        docs_with_entities = {r["did"] for r in entity_rows}

        core_ids = {
            f["doc_id"]
            for f in files
            if (f["topic"] or "") in cfg.raw["core_topics"]
        }
        # 断言 2：is_core 文档全部有 Entity
        assert core_ids and core_ids <= docs_with_entities, (
            f"core docs missing entities: {core_ids - docs_with_entities}"
        )
        # 断言 3：非 core 文档无实体（无 extract 任务）
        non_core_ids = non_dup_ids - core_ids
        assert not (non_core_ids & docs_with_entities), (
            f"non-core docs leaked entities: {non_core_ids & docs_with_entities}"
        )
    finally:
        store.close()
