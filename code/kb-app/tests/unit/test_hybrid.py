"""Unit tests for :mod:`kbapp.retrieve.hybrid`（11 §2 两路召回 + RRF）。"""

from __future__ import annotations

from kbapp.core.config import Config
from kbapp.core.registry import Registry, insert_chunk, upsert_file, upsert_topic
from kbapp.retrieve.hybrid import search, topic_panorama


def _seed(registry: Registry) -> None:
    """播 3 篇文档 + 章节 chunk + topic 供检索测试。"""
    with registry.transaction() as conn:
        upsert_topic(conn, name="ContextEngineering")
        upsert_topic(conn, name="CodeGraph")

        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/rag.md",
            sha256="s1",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="Retrieval Augmented Generation",
            topic="ContextEngineering",
        )
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 Overview",
            title="Overview",
            text="RAG combines large language models with knowledge graph retrieval.",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/kg.md",
            sha256="s2",
            mtime=0,
            corpus="design",
            status="active",
            extract_status="ok",
            title="Knowledge Graph",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 Graph",
            title="Graph",
            text="A knowledge graph stores entities and relationships.",
        )
        upsert_file(
            conn,
            doc_id="D0003",
            path="/c/note.md",
            sha256="s3",
            mtime=0,
            corpus="research",
            status="active",
            extract_status="ok",
            title="Notes",
            topic=None,
        )
        insert_chunk(
            conn,
            chunk_id="D0003#c001",
            doc_id="D0003",
            section_path="§1 Note",
            title="Note",
            text="unrelated note about cooking recipes.",
        )


def test_search_fts_returns_relevant_section(registry: Registry) -> None:
    _seed(registry)
    cfg = Config.defaults()
    result = search(registry, cfg, "knowledge graph")
    assert result.hits, "expected FTS hits"
    assert result.hits[0].doc_id == "D0002"
    assert result.hits[0].section_path == "§1 Graph"
    # snippet 非空（聚合后保留最高分 chunk 文本）
    assert result.hits[0].snippet


def test_search_short_ascii_uses_synonym_expansion(registry: Registry) -> None:
    """2 字符缩写 'KG' 经同义扩展命中 knowledge graph（11 §2.2）。"""
    _seed(registry)
    cfg = Config.defaults()
    result = search(registry, cfg, "KG")
    assert result.hits, "expected synonym-expanded hits for 'KG'"
    # 同义扩展的 FTS 相关命中排在最前（裸 LIKE '%kg%' 已被禁用，不会误中 unrelated）
    assert result.hits[0].doc_id == "D0002"


def test_search_short_ascii_no_bare_like_false_positive(registry: Registry) -> None:
    """ASCII 缩写禁用裸 LIKE：'contain' 不应因含 'ai' 子串被命中（11 §2.2）。"""
    _seed(registry)
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D0004",
            path="/c/container.md",
            sha256="s4",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="Container Guide",
            topic=None,
        )
        insert_chunk(
            conn,
            chunk_id="D0004#c001",
            doc_id="D0004",
            section_path="§1 Containers",
            title="Containers",
            text="How to build containers and contain workloads.",
        )
    from kbapp.retrieve.hybrid import _fts_chunk_hits
    from kbapp.retrieve.query_understanding import merged_synonyms

    synonyms = merged_synonyms({})
    with registry.read_only() as conn:
        hits = _fts_chunk_hits(conn, "AI", synonyms, extra_terms=[], doc_ids=None, limit=10)
    # 'AI' → 'artificial intelligence'（seed 无该词）；'contain' 不应因 'ai' 子串命中
    assert all(h[0] != "D0004" for h in hits)


def test_search_topic_hard_filter(registry: Registry) -> None:
    """--topic 硬过滤：FTS 仅在 T 文档集内执行（11 §2.1）。"""
    _seed(registry)
    cfg = Config.defaults()
    result = search(registry, cfg, "graph", topic="CodeGraph")
    assert result.hits
    assert {h.doc_id for h in result.hits} == {"D0002"}


def test_search_graph_mode_returns_structural_list(registry: Registry) -> None:
    _seed(registry)
    cfg = Config.defaults()
    result = search(registry, cfg, "ContextEngineering", mode="graph")
    assert result.hits, "expected topic-navigation hits"
    assert result.hits[0].doc_id == "D0001"


def test_topic_panorama_groups_by_topic(registry: Registry) -> None:
    _seed(registry)
    cfg = Config.defaults()
    groups = topic_panorama(registry, cfg)
    names = {g["name"] for g in groups}
    assert "ContextEngineering" in names
    assert "CodeGraph" in names


def test_graph_path_empty_when_no_topic_and_not_sparse(registry: Registry) -> None:
    """无主题命中且 topic 不稀疏 → 图路空列表（P1-1）。"""
    from kbapp.retrieve.hybrid import _graph_chunk_hits

    _seed(registry)  # NULL 占比 1/3 < 0.5
    with registry.read_only() as conn:
        hits, degraded = _graph_chunk_hits(
            conn,
            "cooking recipes",
            ["ContextEngineering", "CodeGraph"],
            max_docs=10,
            max_sections=20,
        )
    assert hits == []
    assert degraded is False


def test_graph_path_degrades_only_when_topic_sparse(registry: Registry) -> None:
    """topic 稀疏（NULL 占比 ≥ 0.5）才退化 corpus/doc_type 导航（P1-1）。"""
    from kbapp.retrieve.hybrid import _graph_chunk_hits

    _seed(registry)
    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D0004",
            path="/c/x.md",
            sha256="s4",
            mtime=0,
            corpus="research",
            status="active",
            extract_status="ok",
            title="X",
            topic=None,
        )
        insert_chunk(
            conn,
            chunk_id="D0004#c001",
            doc_id="D0004",
            section_path="§1 X",
            title="X",
            text="x.",
        )
    # 现 NULL 占比 2/4 = 0.5 → 退化
    with registry.read_only() as conn:
        hits, degraded = _graph_chunk_hits(
            conn,
            "cooking",
            ["ContextEngineering", "CodeGraph"],
            max_docs=10,
            max_sections=20,
        )
    assert degraded is True
    assert hits != []


def test_chinese_long_query(registry: Registry) -> None:
    """中文长查询经 trigram FTS 命中中文 chunk，chunk→section 聚合正常（11 §2.2）。

    中文句子无空白、整串为一个 ≥3 字符词元，走 FTS MATCH 子串命中；同 section
    的两个命中 chunk 聚合后只输出一条 section 命中。
    """
    with registry.transaction() as conn:
        upsert_topic(conn, name="ContextEngineering")
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/rag.md",
            sha256="s1",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="检索增强生成",
            topic="ContextEngineering",
        )
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 方法",
            title="方法",
            text="本节讨论上下文工程中的检索增强生成技术，包括索引与召回。",
        )
        # 同 section 第二个 chunk 也命中——聚合后仍只出一条 §1 方法。
        insert_chunk(
            conn,
            chunk_id="D0001#c002",
            doc_id="D0001",
            section_path="§1 方法",
            title="方法",
            text="再次强调上下文工程中的检索增强生成技术的重要性。",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/cook.md",
            sha256="s2",
            mtime=0,
            corpus="research",
            status="active",
            extract_status="ok",
            title="杂记",
            topic="ContextEngineering",
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 杂记",
            title="杂记",
            text="完全无关的烹饪内容，讨论红烧肉与烘焙食谱。",
        )
    cfg = Config.defaults()
    result = search(registry, cfg, "上下文工程中的检索增强生成技术")
    assert result.hits, "expected trigram FTS hit for Chinese long query"
    assert result.hits[0].doc_id == "D0001"
    assert result.hits[0].section_path == "§1 方法"
    assert result.hits[0].snippet
    # chunk→section 聚合：同 section 两个命中 chunk 只输出一条。
    section_hits = [h for h in result.hits if h.doc_id == "D0001" and h.section_path == "§1 方法"]
    assert len(section_hits) == 1
    assert all(h.doc_id != "D0002" for h in result.hits)


def test_cjk_short_term_like_fallback(registry: Registry) -> None:
    """含 CJK 的 2 字符词（"图谱"，分词后 <3 字符）走 LIKE 子串兜底命中（11 §2.2）。

    语料中唯一含 "图谱" 的文本只能经 ``text LIKE '%图谱%'`` 命中（trigram FTS
    对 <3 字符词元不命中），借此断言兜底路径生效。
    """
    with registry.transaction() as conn:
        upsert_topic(conn, name="CodeGraph")
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/kg.md",
            sha256="s1",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="知识图谱构建",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 概述",
            title="概述",
            text="本节介绍图谱的构建流程与存储方案。",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/note.md",
            sha256="s2",
            mtime=0,
            corpus="research",
            status="active",
            extract_status="ok",
            title="无关",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 杂记",
            title="杂记",
            text="这里讨论红烧肉与烘焙食谱。",
        )
    cfg = Config.defaults()
    result = search(registry, cfg, "图谱")
    assert result.hits, "expected LIKE fallback hit for CJK short term"
    assert {h.doc_id for h in result.hits} == {"D0001"}
    assert result.hits[0].section_path == "§1 概述"


def test_graph_path_truncation(registry: Registry) -> None:
    """图路有界化（11 §2.1）：文档数截断到 max_docs、section 总数截断到 max_sections。"""
    with registry.transaction() as conn:
        upsert_topic(conn, name="CodeGraph")
        # 4 篇文档 × 2 个 section = 8 条潜在图路命中，远超注入上限。
        for i in range(4):
            doc_id = f"D{i + 1:04d}"
            upsert_file(
                conn,
                doc_id=doc_id,
                path=f"/c/g{i}.md",
                sha256=f"s{i}",
                mtime=0,
                corpus="references",
                status="active",
                extract_status="ok",
                title=f"Graph Doc {i}",
                topic="CodeGraph",
            )
            for j in range(2):
                insert_chunk(
                    conn,
                    chunk_id=f"{doc_id}#c{j + 1:03d}",
                    doc_id=doc_id,
                    section_path=f"§{j + 1} S{j}",
                    title=f"S{j}",
                    text=f"body {i} {j}",
                )
    cfg = Config.defaults()
    cfg.raw["search"]["graph"] = {"max_docs": 2, "max_sections": 3, "weight": 0.5}
    result = search(registry, cfg, "CodeGraph", mode="graph")
    # section 总数截断到 max_sections=3，且文档不超过 max_docs=2。
    assert len(result.hits) == 3
    assert len({h.doc_id for h in result.hits}) <= 2
    # 对照：默认上限下同一查询返回更多（4 文档 × 2 section）。
    full = search(registry, Config.defaults(), "CodeGraph", mode="graph")
    assert len(full.hits) > len(result.hits)


def test_rerank_reorders_by_llm_ranking() -> None:
    """LLM 重排（11 §2.4）：按返回的 ranking 顺序重排 top-K。"""
    from kbapp.retrieve.hybrid import SearchHit, _rerank

    def _hit(doc_id: str) -> SearchHit:
        return SearchHit(
            doc_id=doc_id,
            path=f"/c/{doc_id}.md",
            section_path="§1 X",
            title=doc_id,
            score=0.0,
            corpus="references",
            doc_type=None,
            topic=None,
            snippet=doc_id,
        )

    hits = [_hit("D0001"), _hit("D0002"), _hit("D0003")]

    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"ranking": [2, 0, 1]}'

    out = _rerank(_FakeLLM(), "q", hits, top_k=3)
    assert [h.doc_id for h in out] == ["D0003", "D0001", "D0002"]


def test_rerank_falls_back_on_error() -> None:
    from kbapp.retrieve.hybrid import SearchHit, _rerank

    def _hit(doc_id: str) -> SearchHit:
        return SearchHit(
            doc_id=doc_id,
            path=f"/c/{doc_id}.md",
            section_path="§1 X",
            title=doc_id,
            score=0.0,
            corpus="references",
            doc_type=None,
            topic=None,
            snippet=doc_id,
        )

    hits = [_hit("D0001"), _hit("D0002")]

    class _Boom:
        def complete(self, messages, **kw) -> str:
            raise RuntimeError("down")

    out = _rerank(_Boom(), "q", hits, top_k=2)
    assert [h.doc_id for h in out] == ["D0001", "D0002"]


def test_section_title_strips_composite() -> None:
    """R-1（13 §3）：section_title 剥复合标签，无分隔符幂等返回。"""
    from kbapp.retrieve.hybrid import section_title

    assert section_title("06-Hong-Context_Rot | Introduction") == "Introduction"
    assert section_title("Plain Title") == "Plain Title"


def test_graph_path_strips_composite_title(registry: Registry) -> None:
    """R-1：图路 `_sections_for_doc` 剥复合标签，返回纯章节标题（13 §3）。"""
    from kbapp.retrieve.hybrid import _sections_for_doc

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
    with registry.read_only() as conn:
        sections = _sections_for_doc(conn, "D0001")
    assert sections == [("§1 Introduction", "Introduction")]


def test_exact_boost_protects_original_query(registry: Registry) -> None:
    """R-2（13 §3）：原查询语义命中得分 ×exact_boost，扩展路命中得分不变。"""
    from kbapp.retrieve.hybrid import _fts_chunk_hits
    from kbapp.retrieve.query_understanding import merged_synonyms

    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/rot.md",
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
            section_path="§1 Rot",
            title="Rot",
            text="context rot degrades model quality over time.",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/llmlingua.md",
            sha256="s2",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="LLMLingua",
            topic=None,
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 Lingua",
            title="Lingua",
            text="llmlingua compresses prompts aggressively.",
        )

    synonyms = merged_synonyms({})
    with registry.read_only() as conn:
        base = _fts_chunk_hits(
            conn,
            "context rot",
            synonyms,
            extra_terms=["llmlingua"],
            doc_ids=None,
            limit=10,
            exact_boost=1.0,
        )
        boosted = _fts_chunk_hits(
            conn,
            "context rot",
            synonyms,
            extra_terms=["llmlingua"],
            doc_ids=None,
            limit=10,
            exact_boost=1.3,
        )
    base_scores = {r[0]: r[4] for r in base}
    boosted_scores = {r[0]: r[4] for r in boosted}
    assert set(base_scores) == {"D0001", "D0002"}
    # 原查询语义命中（D0001）得分 ×1.3；扩展路命中（D0002）得分不变。
    assert boosted_scores["D0001"] == base_scores["D0001"] * 1.3
    assert boosted_scores["D0002"] == base_scores["D0002"]


def test_exact_boost_no_op_without_expansion(registry: Registry) -> None:
    """R-2 回归锁：无扩展词时 exact_boost 不施加，绝对分值不变（13 §3）。"""
    from kbapp.retrieve.hybrid import _fts_chunk_hits
    from kbapp.retrieve.query_understanding import merged_synonyms

    with registry.transaction() as conn:
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/rot.md",
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
            section_path="§1 Rot",
            title="Rot",
            text="context rot degrades model quality over time.",
        )
    synonyms = merged_synonyms({})
    with registry.read_only() as conn:
        base = _fts_chunk_hits(
            conn,
            "context rot",
            synonyms,
            extra_terms=[],
            doc_ids=None,
            limit=10,
            exact_boost=1.0,
        )
        boosted = _fts_chunk_hits(
            conn,
            "context rot",
            synonyms,
            extra_terms=[],
            doc_ids=None,
            limit=10,
            exact_boost=1.3,
        )
    assert base == boosted


def test_like_ranking_title_above_text(registry: Registry) -> None:
    """R-3（13 §3）：纯 LIKE 路 title 命中 1.0 > text 命中 0.5，确定性排序。"""
    from kbapp.retrieve.hybrid import _fts_chunk_hits
    from kbapp.retrieve.query_understanding import merged_synonyms

    with registry.transaction() as conn:
        upsert_topic(conn, name="CodeGraph")
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/g1.md",
            sha256="s1",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="图谱构建",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 概述",
            title="图谱构建",
            text="本节介绍知识表示。",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/g2.md",
            sha256="s2",
            mtime=0,
            corpus="references",
            status="active",
            extract_status="ok",
            title="杂记",
            topic="CodeGraph",
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 杂记",
            title="杂记",
            text="这里讨论图谱的存储方案。",
        )

    synonyms = merged_synonyms({})
    with registry.read_only() as conn:
        hits = _fts_chunk_hits(conn, "图谱", synonyms, extra_terms=[], doc_ids=None, limit=10)
    assert [(h[0], h[4]) for h in hits] == [("D0001", 1.0), ("D0002", 0.5)]
