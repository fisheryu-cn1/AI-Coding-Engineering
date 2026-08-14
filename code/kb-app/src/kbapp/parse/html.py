"""HTML parser via Trafilatura (设计 05 §3.2 + 02 §3 D6).

Trafilatura is the canonical "main text + boilerplate strip" extractor;
``extract(..., output_format="markdown")`` preserves heading structure we
can re-walk as sections. When Trafilatura returns ``None`` (rare: empty
HTML, redirects, JS-only pages), we fall back to a very simple
``<h1>..<h6>`` / ``<p>`` walker so the chunk stage still gets sections.
"""

from __future__ import annotations

import re
from pathlib import Path

from kbapp.parse.base import ExtractMeta, ParseError, ParseResult, Section

PARSER_NAME = "trafilatura"


def parse_html(path: Path) -> tuple[ParseResult, ExtractMeta]:
    """Parse ``path`` (HTML or HTM) and return ``(ParseResult, ExtractMeta)``."""
    try:
        raw = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise ParseError(f"读取 HTML 失败：{path} ({e})") from e

    try:
        import trafilatura  # local import — only present under parse extra

        md = trafilatura.extract(
            raw,
            include_comments=False,
            include_tables=True,
            output_format="markdown",
            favor_precision=False,
        )
    except Exception as e:  # pragma: no cover - trafilatura import failure
        md = None
        warnings = [f"trafilatura_unavailable: {e}"]
    else:
        warnings = []

    if not md:
        return _fallback_parse(raw, warnings=warnings or ["trafilatura_returned_none"])

    # Walk markdown for headings (re-use markdown-it-py parsing).

    sections, header_count = _walk_markdown_sections(md)

    return (
        ParseResult(
            full_text=md,
            sections=sections,
            structure="tree" if header_count else "flat",
            parser=PARSER_NAME,
            warnings=warnings,
        ),
        ExtractMeta(
            parser=PARSER_NAME,
            format="html",
            page_count=None,
            header_count=header_count,
            coverage=None,
        ),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _walk_markdown_sections(md: str) -> tuple[list[Section], int]:
    """Inline copy of markdown section walking (avoids temp-file I/O)."""
    from markdown_it import MarkdownIt

    tokens = MarkdownIt().parse(md)
    headings: list[tuple[int, str, int, int]] = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            level = int(t.tag[1])
            inline = tokens[i + 1]
            title = (inline.content or "").strip()
            map_start = t.map[0] if t.map else 0
            headings.append((level, title, map_start, -1))
            i += 3
            continue
        i += 1

    if not headings:
        line_count = md.count("\n") + 1
        return (
            [
                Section(
                    section_path="全文",
                    level=1,
                    title="全文",
                    page_range=f"L1-L{line_count}",
                    text=md.strip(),
                )
            ],
            0,
        )

    lines = md.splitlines()
    for idx, h in enumerate(headings):
        if idx + 1 < len(headings):
            headings[idx] = (h[0], h[1], h[2], headings[idx + 1][2])
        else:
            headings[idx] = (h[0], h[1], h[2], len(lines))

    sections: list[Section] = []
    for level, title, line_start, line_end in headings:
        sec_text = "\n".join(lines[line_start:line_end]).strip()
        sections.append(
            Section(
                section_path=_path_label(len(sections) + 1, title),
                level=level,
                title=title or "(无标题)",
                page_range=f"L{line_start + 1}-L{line_end}",
                text=sec_text,
            )
        )
    return sections, len(headings)


def _path_label(idx: int, title: str) -> str:
    short = title[:30] + "…" if len(title) > 30 else title
    return f"§{idx} {short}".strip()


# Tag-based fallback for when Trafilatura returns None.
_TAG_RE = re.compile(r"<(h[1-6]|p)[\s>](.*?)</\1>", re.IGNORECASE | re.DOTALL)


def _fallback_parse(html: str, *, warnings: list[str]) -> tuple[ParseResult, ExtractMeta]:
    """Walk ``<h1..h6>`` and ``<p>`` tags to build sections.

    Sections are line-indexed by counting newlines before each match.
    """
    lines = html.splitlines(keepends=False)
    sections: list[Section] = []
    current_title = "全文"
    current_level = 1
    buf: list[str] = []
    section_start_line = 0

    def flush(end_line: int) -> None:
        text = "\n".join(buf).strip()
        if not text and not sections:
            return
        sections.append(
            Section(
                section_path=f"§{len(sections) + 1} {current_title}",
                level=current_level,
                title=current_title,
                page_range=f"L{section_start_line + 1}-L{end_line}",
                text=text,
            )
        )

    for m in _TAG_RE.finditer(html):
        line_no = html.count("\n", 0, m.start())
        tag = m.group(1).lower()
        inner = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if tag.startswith("h"):
            # New section header
            flush(line_no)
            current_level = int(tag[1])
            current_title = inner or "(无标题)"
            buf = []
            section_start_line = line_no
        else:
            buf.append(inner)

    flush(len(lines))

    if not sections:
        sections.append(
            Section(
                section_path="全文",
                level=1,
                title="全文",
                page_range=None,
                text=re.sub(r"<[^>]+>", "", html).strip(),
            )
        )

    full_text = "\n\n".join(s.text for s in sections)
    return (
        ParseResult(
            full_text=full_text,
            sections=sections,
            structure="flat",
            parser=PARSER_NAME,
            warnings=warnings,
        ),
        ExtractMeta(
            parser=PARSER_NAME,
            format="html",
            page_count=None,
            header_count=sum(1 for s in sections if s.title != "全文"),
            coverage=None,
        ),
    )


__all__ = ["PARSER_NAME", "parse_html"]
