"""Unit tests for summaries/*.md manifest binding (09 §5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from kbapp.parse.manifest import (
    SummaryMeta,
    bind_summaries_to_corpus,
    parse_summary,
)


def test_parse_frontmatter_extracts_fields(tmp_path: Path) -> None:
    p = tmp_path / "summary.md"
    p.write_text(
        "---\n"
        "title: 'Paper Foo'\n"
        "source_pdf: '10-Foo_v2.pdf'\n"
        "arxiv_id: '2607.03691'\n"
        "arxiv_version: 'v2'\n"
        "authors: ['Alice', 'Bob']\n"
        "year: 2026\n"
        "venue: 'ACM'\n"
        "---\n",
        encoding="utf-8",
    )
    meta = parse_summary(p)
    assert meta.title == "Paper Foo"
    assert meta.source_pdf == "10-Foo_v2.pdf"
    assert meta.arxiv_id == "2607.03691"
    assert meta.arxiv_version == "v2"
    assert meta.authors == ["Alice", "Bob"]
    assert meta.year == 2026
    assert meta.venue == "ACM"


def test_parse_blockquote_extracts_legacy_fields(tmp_path: Path) -> None:
    p = tmp_path / "legacy.md"
    p.write_text(
        "# 论文摘要：Foo\n\n"
        "> **原论文标题**：Foo Bar\n"
        "> **完整 PDF 文件名**：`10-Foo_v2.pdf`\n"
        "> **作者 / 年份 / 出版**：Alice, Bob / 2026 / ACM\n"
        "> **摘要类型**：内容索引\n"
        "> **生成日期**：2026-08-12\n",
        encoding="utf-8",
    )
    meta = parse_summary(p)
    # blockquote "原论文标题" overrides H1 (legacy precedence).
    assert meta.title == "Foo Bar"
    assert meta.source_pdf == "10-Foo_v2.pdf"
    assert meta.authors == ["Alice", "Bob"]
    assert meta.year == 2026
    assert meta.venue == "ACM"
    assert meta.summary_type == "内容索引"
    assert meta.generated_at == "2026-08-12"


def test_parse_blockquote_embeds_arxiv_in_source_pdf(tmp_path: Path) -> None:
    p = tmp_path / "legacy.md"
    p.write_text(
        "> **完整 PDF 文件名**：arXiv:2607.03691v2\n",
        encoding="utf-8",
    )
    meta = parse_summary(p)
    assert meta.source_pdf == "arXiv:2607.03691v2"
    assert meta.arxiv_id == "2607.03691"
    assert meta.arxiv_version == "v2"


def test_parse_frontmatter_without_closing_raises(tmp_path: Path) -> None:
    p = tmp_path / "broken.md"
    p.write_text("---\nkey: value\n", encoding="utf-8")
    from kbapp.parse.base import ParseError

    with pytest.raises(ParseError):
        parse_summary(p)


def test_bind_summaries_to_corpus_matches_by_basename() -> None:
    summaries = [
        SummaryMeta(
            source_pdf="10-Foo_v2.pdf",
            title=None,
            arxiv_id=None,
            arxiv_version=None,
        ),
        SummaryMeta(
            source_pdf="not-in-corpus.pdf",
            title=None,
            arxiv_id=None,
            arxiv_version=None,
        ),
    ]
    corpus_paths = {"/refs/10-Foo_v2.pdf"}
    out = bind_summaries_to_corpus(summaries, corpus_paths)
    assert "/refs/10-Foo_v2.pdf" in out
    assert "not-in-corpus.pdf" not in {s.source_pdf for s in out.values()}


def test_bind_skips_summaries_without_source_pdf() -> None:
    summaries = [
        SummaryMeta(
            source_pdf=None,
            title="orphan",
            arxiv_id=None,
            arxiv_version=None,
        ),
    ]
    out = bind_summaries_to_corpus(summaries, {"/any.pdf"})
    assert out == {}
