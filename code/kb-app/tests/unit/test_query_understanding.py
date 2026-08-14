"""Unit tests for :mod:`kbapp.retrieve.query_understanding` (11 §2.1/§2.2/§2.3)."""

from __future__ import annotations

from kbapp.retrieve.query_understanding import (
    BUILTIN_SYNONYMS,
    is_cjk,
    llm_expand_query,
    match_topics,
    merged_synonyms,
    norm,
    split_terms,
)


def test_norm_lowercases_and_splits_camelcase() -> None:
    assert norm("ContextEngineering") == "context engineering"
    assert norm("CodeGraph") == "code graph"


def test_norm_collapses_hyphens_and_spaces() -> None:
    assert norm("context-engineering") == "context engineering"
    assert norm("  RAG  ") == "rag"


def test_norm_collision_equivalence() -> None:
    assert norm("ContextEngineering") == norm("context-engineering")


def test_is_cjk_detects_chinese() -> None:
    assert is_cjk("知识图谱")
    assert not is_cjk("knowledge")


def test_split_terms() -> None:
    assert split_terms("knowledge graph") == ["knowledge", "graph"]
    assert split_terms("知识图谱") == ["知识图谱"]


def test_merged_synonyms_user_overrides_builtin() -> None:
    merged = merged_synonyms({"AI": ["custom ai meaning"]})
    assert "custom ai meaning" in merged["ai"]
    assert "rag" in merged  # builtin preserved


def test_match_topics_word_boundary_for_ascii() -> None:
    # "ai" 不应命中 "explain"（词边界）
    assert match_topics("explain context engineering", ["AI"]) == []
    assert match_topics("context engineering for llm", ["ContextEngineering"]) == [
        "ContextEngineering"
    ]


def test_match_topics_substring_for_cjk() -> None:
    assert match_topics("知识图谱相关", ["知识图谱"]) == ["知识图谱"]


def test_match_topics_returns_norm_equivalent_group() -> None:
    topics = ["ContextEngineering", "context-engineering"]
    assert set(match_topics("context engineering", topics)) == set(topics)


def test_llm_expand_query_returns_terms() -> None:
    class _FakeLLM:
        def complete(self, messages, **kw) -> str:
            return '{"terms": ["knowledge graph", "知识图谱"]}'

    assert llm_expand_query(_FakeLLM(), "KG") == ["knowledge graph", "知识图谱"]


def test_llm_expand_query_falls_back_on_error() -> None:
    class _Boom:
        def complete(self, messages, **kw) -> str:
            raise RuntimeError("down")

    assert llm_expand_query(_Boom(), "x") == []


def test_builtin_synonyms_cover_abbreviations() -> None:
    assert "artificial intelligence" in BUILTIN_SYNONYMS["ai"]
    assert "知识图谱" in BUILTIN_SYNONYMS["kg"]
