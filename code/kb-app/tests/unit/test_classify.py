"""Unit tests for the keyword classifier (09 §7) and topic scoring."""

from __future__ import annotations

from pathlib import Path

from kbapp.pipeline.classify import (
    DOC_TYPES,
    decide_doc_type,
    decide_topic,
    llm_arbitrate_doc_type,
    score_topics,
)


def test_score_topics_weights_title_hits_3x() -> None:
    """09 §7.1: title hit weights 3x body hit; one hit per term per region."""
    kw = {
        "ContextEngineering": ["context", "retrieval", "augmented"],
        "ai-coding": ["agent", "coding"],
    }
    scores = score_topics(title="Context retrieval augmented", body="random text", keywords=kw)
    # 3 distinct title hits × 3 weight = 9
    assert scores[0].topic == "ContextEngineering"
    assert scores[0].score == 9
    assert scores[0].title_hits == 3


def test_score_topics_one_hit_per_term() -> None:
    """重复的同一个关键词只计 1 次（one hit per term per region）。"""
    kw = {"Topic": ["foo"]}
    scores = score_topics(title="foo foo foo", body="", keywords=kw)
    assert scores[0].title_hits == 1
    assert scores[0].score == 3  # 3 × 1


def test_score_topics_case_insensitive() -> None:
    kw = {"ContextEngineering": ["RETRIEVAL"]}
    scores = score_topics(title="Retrieval-Augmented", body="x", keywords=kw)
    assert scores[0].topic == "ContextEngineering"
    assert scores[0].score == 3


def test_decide_topic_picks_best_above_threshold() -> None:
    scores = [
        _score("ContextEngineering", 6),
        _score("ai-coding", 2),
    ]
    topic, needs_confirm = decide_topic(scores=scores, min_keyword_score=2, top_ratio=1.5)
    assert topic == "ContextEngineering"
    assert needs_confirm is False


def test_decide_topic_below_threshold_needs_confirm() -> None:
    scores = [_score("ContextEngineering", 1)]
    topic, needs_confirm = decide_topic(scores=scores, min_keyword_score=2, top_ratio=1.5)
    assert topic is None
    assert needs_confirm is True


def test_decide_topic_top_ratio_fails_needs_confirm() -> None:
    scores = [
        _score("ContextEngineering", 4),
        _score("ai-coding", 3),  # 4 / 3 < 1.5 → ambiguous
    ]
    topic, needs_confirm = decide_topic(scores=scores, min_keyword_score=2, top_ratio=1.5)
    assert topic is None
    assert needs_confirm is True


def test_decide_topic_empty_scores_needs_confirm() -> None:
    topic, needs_confirm = decide_topic(scores=[], min_keyword_score=2, top_ratio=1.5)
    assert topic is None
    assert needs_confirm is True


# ---------------------------------------------------------------------------
# doc_type decision (09 §7.3 priority chain)
# ---------------------------------------------------------------------------


def test_decide_doc_type_curated_summary_is_paper(tmp_path: Path) -> None:
    p = tmp_path / "anything.txt"
    assert decide_doc_type(path=p, corpus="references", summary_source="curated") == "paper"


def test_decide_doc_type_arxiv_id_in_filename_is_paper(tmp_path: Path) -> None:
    p = tmp_path / "2607.03691.pdf"
    assert decide_doc_type(path=p, corpus="research", summary_source=None) == "paper"


def test_decide_doc_type_design_corpus_or_path(tmp_path: Path) -> None:
    p = tmp_path / "x.md"
    assert decide_doc_type(path=p, corpus="design", summary_source=None) == "design"
    nested = Path("/home/me/research/design/foo.md")
    assert decide_doc_type(path=nested, corpus="references", summary_source=None) == "design"


def test_decide_doc_type_default_pdf_is_paper(tmp_path: Path) -> None:
    p = tmp_path / "untitled.pdf"
    assert decide_doc_type(path=p, corpus="research", summary_source=None) == "paper"


def test_decide_doc_type_md_default_is_other(tmp_path: Path) -> None:
    p = tmp_path / "note.md"
    assert decide_doc_type(path=p, corpus="research", summary_source=None) == "other"


def test_doc_types_constant_is_stable() -> None:
    assert set(DOC_TYPES) == {"paper", "design", "other"}
    # Order matters for tests that rely on it.
    assert DOC_TYPES == ("paper", "design", "other")


def _score(topic: str, score: int):
    from kbapp.pipeline.classify import TopicScore

    return TopicScore(topic=topic, score=score, title_hits=score // 3, body_hits=score)


# ---------------------------------------------------------------------------
# LLM doc_type fallback (09 §7.3 rule ⑤)
# ---------------------------------------------------------------------------


def test_llm_arbitrate_doc_type_returns_llm_answer() -> None:
    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"doc_type": "design"}'

    out = llm_arbitrate_doc_type(llm=_FakeLLM(), title="t", body="b")
    assert out == "design"


def test_llm_arbitrate_doc_type_falls_back_to_other_on_error() -> None:
    class _BoomLLM:
        def complete(self, messages, **kw) -> str:
            raise RuntimeError("down")

    out = llm_arbitrate_doc_type(llm=_BoomLLM(), title="t", body="b")
    assert out == "other"


def test_llm_arbitrate_doc_type_rejects_unknown_label() -> None:
    class _LiarLLM:
        def complete(self, messages, **kw) -> str:
            return '{"doc_type": "slides"}'

    out = llm_arbitrate_doc_type(llm=_LiarLLM(), title="t", body="b")
    assert out == "other"
