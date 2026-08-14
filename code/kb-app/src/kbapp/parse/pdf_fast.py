"""PDF fast-path parser via PyMuPDF / pymupdf4llm (设计 03 §4 P1 + 09 §4).

User decision (M2 实施确认): no OCR is in scope; every PDF in the corpus is
expected to have a text layer that PyMuPDF can read directly. This module
therefore collapses the original "快路径 / Docling 降级 / 扫描版 no_text"
three-level cascade into a two-outcome one:

- text-layer found (any non-empty result) → fast path; coverage + header
  count decide whether ``structure='tree'`` or ``structure='flat'`` (per
  09 §4 coverage = nonspace chars / (pages × page_char_norm), and
  ``parse.pdf_fast_min_headers``).
- text-layer missing → :class:`ParseError` with a recognisable message so
  the runner can mark ``extract_status='no_text'`` (09 §4 末段).

The ``pymupdf4llm.to_markdown(path, page_chunks=True)`` call returns a list
of per-page dicts (``metadata`` carries page/page_count/file_path;
``text`` is the page markdown; ``toc_items`` is the outline). We use those
page chunks to compute coverage and to attach ``page_range`` per section.
"""

from __future__ import annotations

import re
from pathlib import Path

from kbapp.parse.base import ExtractMeta, ParseError, ParseResult, Section

PARSER_NAME = "pymupdf4llm"


def _nonspace_len(s: str) -> int:
    return sum(1 for ch in s if not ch.isspace())


def parse_pdf(
    path: Path,
    *,
    page_char_norm: int = 1500,
    min_coverage: float = 0.85,
    min_headers: int = 3,
) -> tuple[ParseResult, ExtractMeta]:
    """Parse ``path`` (PDF) via pymupdf4llm.

    Returns ``(ParseResult, ExtractMeta)``. On no-text PDFs (scanned images),
    raises :class:`ParseError` so the runner can mark
    ``extract_status='no_text'``.
    """
    try:
        import pymupdf4llm  # provided by parse extra
    except ImportError as e:  # pragma: no cover
        raise ParseError(f"pymupdf4llm 未安装（pip install 'kbapp[parse]'）: {e}") from e

    try:
        chunks = pymupdf4llm.to_markdown(str(path), page_chunks=True)
    except Exception as e:
        raise ParseError(f"PDF 解析失败：{path} ({e})") from e

    if not chunks:
        raise ParseError(f"PDF 无可解析内容：{path}")

    page_count = len(chunks)
    full_text_parts: list[str] = []
    sections: list[Section] = []

    # Aggregate TOC across pages (most reliable signal for headings).
    # Page numbers are derived from chunk order (1-based): pymupdf4llm's
    # ``metadata.page`` is version-dependent (None / 0-based on some
    # releases), while TOC pages are always 1-based — enumeration keeps the
    # two on the same base (M3 DoD 复核修复：TOC 分节正文全空)。
    toc_items: list[tuple[int, str, int]] = []  # (level, title, page)
    for idx, ch in enumerate(chunks):
        page_no = idx + 1
        text = ch.get("text", "") or ""
        full_text_parts.append(text)
        for ti in ch.get("toc_items") or []:
            # pymupdf4llm: [level, title, page]
            if isinstance(ti, (list, tuple)) and len(ti) >= 3:
                toc_items.append((int(ti[0]), str(ti[1]), int(ti[2])))

        # Section boundaries come from TOC when present; else one section
        # per page (treated as flat).
        if toc_items:
            continue
        sections.append(
            Section(
                section_path=f"§{len(sections) + 1} 第 {page_no} 页",
                level=1,
                title=f"第 {page_no} 页",
                page_range=str(page_no),
                text=text,
            )
        )

    full_text = "\n\n".join(full_text_parts)
    nonspace = _nonspace_len(full_text)
    coverage = nonspace / max(1, page_count * page_char_norm) if page_count else 0.0

    # No-text PDF → coverage essentially zero; surface as ParseError so
    # the runner marks ``extract_status='no_text'``.
    if coverage < 0.05 or nonspace < 50:
        raise ParseError(f"PDF 无文本层（疑似扫描版）：{path} (coverage={coverage:.3f})")

    if toc_items:
        sections = _sections_from_toc(toc_items, full_text, chunks, page_count)
        structure: str = "tree"
        header_count = len(toc_items)
    else:
        # No TOC: treat as tree only if we found >= min_headers markdown
        # headings (``#`` lines), else flat.
        header_lines = sum(1 for line in full_text.splitlines() if re.match(r"^#{1,6}\s", line))
        if header_lines >= min_headers:
            structure = "tree"
            header_count = header_lines
            sections = _sections_from_markdown_headings(full_text, page_count, chunks)
        else:
            structure = "flat"
            header_count = header_lines
            # sections already populated per-page above

    warnings: list[str] = []
    if coverage < min_coverage:
        warnings.append(f"low_coverage={coverage:.2f}")
    if structure == "flat" and header_count < min_headers:
        warnings.append("header_detection_failed")

    return (
        ParseResult(
            full_text=full_text,
            sections=sections,
            structure=structure,  # type: ignore[arg-type]
            parser=PARSER_NAME,
            warnings=warnings,
        ),
        ExtractMeta(
            parser=PARSER_NAME,
            format="pdf",
            page_count=page_count,
            header_count=header_count,
            coverage=coverage,
        ),
    )


def _sections_from_toc(
    toc_items: list[tuple[int, str, int]],
    full_text: str,
    chunks: list[dict],
    page_count: int,
) -> list[Section]:
    """Build sections from TOC outline; each section covers pages [start, next_start)."""
    # Sort & dedupe by page; keep first occurrence per (level, title, page).
    seen = set()
    cleaned: list[tuple[int, str, int]] = []
    for level, title, page in sorted(toc_items, key=lambda x: (x[2], x[0])):
        key = (level, title.strip(), page)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(key)

    sections: list[Section] = []
    for i, (level, title, start_page) in enumerate(cleaned):
        end_page = cleaned[i + 1][2] - 1 if i + 1 < len(cleaned) else page_count
        # Collect text from chunks whose page is within [start_page, end_page].
        # Chunk page = 枚举序号 +1（1-based，与 TOC 同基；metadata.page 不可靠）。
        text_parts: list[str] = []
        for idx, ch in enumerate(chunks):
            p = idx + 1
            if start_page <= p <= end_page:
                t = ch.get("text") or ""
                if t.strip():
                    text_parts.append(t)
        sec_text = "\n\n".join(text_parts).strip()
        page_range = f"{start_page}-{end_page}" if end_page > start_page else str(start_page)
        sections.append(
            Section(
                section_path=f"§{len(sections) + 1} {title}",
                level=level,
                title=title,
                page_range=page_range,
                text=sec_text,
            )
        )
    return sections


def _sections_from_markdown_headings(
    full_text: str,
    page_count: int,
    chunks: list[dict],
) -> list[Section]:
    """Fallback: derive sections from ``#`` / ``##`` / ``###`` lines."""
    headings: list[tuple[int, str, int]] = []  # (level, title, line)
    for line_no, line in enumerate(full_text.splitlines()):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            headings.append((len(m.group(1)), m.group(2), line_no))

    if not headings:
        # No headings either → one section per page
        return [
            Section(
                section_path=f"§{i + 1} 第 {i + 1} 页",
                level=1,
                title=f"第 {i + 1} 页",
                page_range=str(i + 1),
                text=(chunks[i].get("text") if i < len(chunks) else "") or "",
            )
            for i in range(page_count)
        ]

    lines = full_text.splitlines()
    sections: list[Section] = []
    for i, (level, title, start) in enumerate(headings):
        end = headings[i + 1][2] if i + 1 < len(headings) else len(lines)
        sec_text = "\n".join(lines[start + 1 : end]).strip()
        # Approximate page_range by mapping line numbers to page numbers
        # using the cumulative page sizes; cheap heuristic.
        page_start = _line_to_page(start, full_text, page_count)
        page_end = _line_to_page(end - 1, full_text, page_count)
        page_range = f"{page_start}-{page_end}" if page_end > page_start else str(page_start)
        sections.append(
            Section(
                section_path=f"§{len(sections) + 1} {title}",
                level=level,
                title=title,
                page_range=page_range,
                text=sec_text,
            )
        )
    return sections


def _line_to_page(line_no: int, full_text: str, page_count: int) -> int:
    """Map a 0-based line number to a 1-based page number by chunking text."""
    lines = full_text.splitlines()
    if page_count <= 0:
        return 1
    bucket = max(1, len(lines) // page_count)
    return min(page_count, line_no // bucket + 1)


__all__ = ["PARSER_NAME", "parse_pdf"]
