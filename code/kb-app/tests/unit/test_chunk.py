"""Unit tests for the FTS5 chunker (:mod:`kbapp.parse.chunk`)."""

from __future__ import annotations

from kbapp.parse.base import ParseResult, Section
from kbapp.parse.chunk import chunk_document


def _parse_result(sections: list[Section]) -> ParseResult:
    return ParseResult(
        full_text="\n".join(s.text for s in sections),
        sections=sections,
        structure="tree",
        parser="test",
    )


def test_short_section_is_one_chunk() -> None:
    sec = Section(
        section_path="§1",
        level=1,
        title="Tiny",
        page_range=None,
        text="short body",
    )
    out = chunk_document(
        doc_id="D0001", parse=_parse_result([sec]), chunk_size=2048, chunk_overlap=200
    )
    assert len(out.chunks) == 1
    assert out.chunks[0].chunk_id == "D0001#c001"
    assert "short body" in out.chunks[0].text


def test_long_section_is_split_with_overlap() -> None:
    long_text = ("alpha beta gamma.\n\n" * 200).strip()
    sec = Section(
        section_path="§1",
        level=1,
        title="Long",
        page_range=None,
        text=long_text,
    )
    out = chunk_document(
        doc_id="D0002",
        parse=_parse_result([sec]),
        chunk_size=512,
        chunk_overlap=64,
    )
    assert len(out.chunks) >= 2
    # Each emitted chunk respects the size cap.
    for c in out.chunks:
        assert len(c.text) <= 512


def test_chunk_ids_are_doc_scoped_and_sequential() -> None:
    secs = [
        Section("§A", 1, "A", None, "A" * 100),
        Section("§B", 1, "B", None, "B" * 100),
    ]
    out = chunk_document(
        doc_id="D0042",
        parse=_parse_result(secs),
        chunk_size=200,
        chunk_overlap=20,
    )
    ids = [c.chunk_id for c in out.chunks]
    assert ids[0].startswith("D0042#c")
    # Sequential three-digit numbering, 1-based
    assert ids[0] == "D0042#c001"
    assert ids == [f"D0042#c{i + 1:03d}" for i in range(len(ids))]


def test_chunk_inherits_section_path_and_title() -> None:
    sec = Section(
        section_path="§2/§2.1",
        level=2,
        title="Sub",
        page_range=None,
        text="hello",
    )
    out = chunk_document(
        doc_id="D0001",
        parse=_parse_result([sec]),
        chunk_size=2048,
        chunk_overlap=200,
    )
    assert out.chunks[0].section_path == "§2/§2.1"
    assert out.chunks[0].title == "Sub"


def test_empty_parse_yields_no_chunks() -> None:
    out = chunk_document(
        doc_id="D0001",
        parse=_parse_result([]),
        chunk_size=2048,
        chunk_overlap=200,
    )
    assert out.chunks == []
