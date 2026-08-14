"""Markdown parser via markdown-it-py (设计 05 §3.2 + 06).

Markdown is the most structure-rich plain-text format we ingest: headings
H1–H6 give us the section tree, and ``page_range`` becomes the line span
of the section so downstream chunks can carry the original line offsets.

Algorithm (matches the pattern in 06 §5):
1. ``MarkdownIt().parse(text)`` → token stream.
2. Walk ``heading_open`` tokens, capture level/title/line start.
3. Maintain a heading stack; the current path is built from active heads.
4. Each section's text is the lines between this heading's ``map[0]`` and
   the next heading's ``map[0]`` (or EOF).
"""

from __future__ import annotations

from pathlib import Path

from markdown_it import MarkdownIt

from kbapp.parse.base import ExtractMeta, ParseError, ParseResult, Section

PARSER_NAME = "markdown-it"


def parse_md(path: Path) -> tuple[ParseResult, ExtractMeta]:
    """Parse a Markdown file into sections keyed by heading tree."""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise ParseError(f"读取 MD 失败：{path} ({e})") from e

    tokens = MarkdownIt().parse(text)

    # Collect headings: list of (level, title, line_start, line_end_exclusive)
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
            i += 3  # skip inline + heading_close
            continue
        i += 1

    if not headings:
        # No headings → treat entire file as one flat section (L1..Ln).
        line_count = text.count("\n") + 1
        return (
            ParseResult(
                full_text=text,
                sections=[
                    Section(
                        section_path="全文",
                        level=1,
                        title="全文",
                        page_range=f"L1-L{line_count}",
                        text=text.strip(),
                    )
                ],
                structure="flat",
                parser=PARSER_NAME,
                warnings=["no_headings"],
            ),
            ExtractMeta(
                parser=PARSER_NAME,
                format="md",
                page_count=None,
                header_count=0,
                coverage=None,
            ),
        )

    # Fill heading end_line (the line where the next heading starts).
    lines = text.splitlines()
    for idx, h in enumerate(headings):
        if idx + 1 < len(headings):
            headings[idx] = (h[0], h[1], h[2], headings[idx + 1][2])
        else:
            headings[idx] = (h[0], h[1], h[2], len(lines))

    # Build sections. Use a heading-stack so nested H2/H3 sit under the
    # nearest H1 ancestor. ``section_path`` looks like "§1 引言 > §1.1 背景".
    sections: list[Section] = []
    stack: list[tuple[int, str, int, int]] = []

    def current_path() -> str:
        parts = (_path_label(idx + 1, s[1]) for idx, s in enumerate(stack))
        return " > ".join(parts)

    for level, title, line_start, line_end in headings:
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title, line_start, line_end))
        sec_text = "\n".join(lines[line_start:line_end]).strip()
        sections.append(
            Section(
                section_path=current_path(),
                level=level,
                title=title or "(无标题)",
                page_range=f"L{line_start + 1}-L{line_end}",
                text=sec_text,
            )
        )

    warnings: list[str] = []
    if all(h[0] == 1 for h in headings):
        # No sub-headings — accept as tree but note.
        warnings.append("only_h1")

    full_text = "\n\n".join(s.text for s in sections)
    return (
        ParseResult(
            full_text=full_text,
            sections=sections,
            structure="tree",
            parser=PARSER_NAME,
            warnings=warnings,
        ),
        ExtractMeta(
            parser=PARSER_NAME,
            format="md",
            page_count=None,
            header_count=len(headings),
            coverage=None,
        ),
    )


def _path_label(idx: int, title: str) -> str:
    """Render one stack entry as ``"§N <title>"`` (truncated for readability)."""
    short = title[:30] + "…" if len(title) > 30 else title
    return f"§{idx} {short}".strip()


__all__ = ["PARSER_NAME", "parse_md"]
