"""Plain text parser (设计 05 §3.2).

A text file has no headers, so the structure is always ``"flat"`` and we
synthesize one section per blank-line paragraph. ``page_range`` falls back
to ``None`` (the runner uses ``#L<line>`` anchors downstream).
"""

from __future__ import annotations

from pathlib import Path

from kbapp.parse.base import ExtractMeta, ParseResult, Section

PARSER_NAME = "txt"

#: Maximum characters per synthetic section (matches chunk_size default).
SECTION_TARGET = 2048


def parse_txt(path: Path) -> tuple[ParseResult, ExtractMeta]:
    """Parse ``path`` and return ``(ParseResult, ExtractMeta)``.

    Splits on blank lines; merges short adjacent blocks up to
    :data:`SECTION_TARGET` so the chunk stage still benefits from section
    boundaries when the file is mostly long paragraphs.
    """
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        from kbapp.parse.base import ParseError

        raise ParseError(f"读取 TXT 失败：{path} ({e})") from e

    paragraphs = [p.strip() for p in text.split("\n\n")]
    paragraphs = [p for p in paragraphs if p]

    sections: list[Section] = []
    buf: list[str] = []
    buf_lines = 0
    start_line = 0

    def flush(buf: list[str], start_line: int, buf_lines: int) -> Section | None:
        joined = "\n\n".join(buf).strip()
        if not joined:
            return None
        end_line = start_line + buf_lines - 1
        path_str = f"全文 (L{start_line + 1}-L{end_line + 1})"
        return Section(
            section_path=path_str,
            level=1,
            title="全文",
            page_range=f"L{start_line + 1}-L{end_line + 1}",
            text=joined,
        )

    line_cursor = 0
    for para in paragraphs:
        n_lines = para.count("\n") + 1
        candidate = "\n\n".join(buf + [para]) if buf else para
        if len(candidate) > SECTION_TARGET and buf:
            flushed = flush(buf, start_line, buf_lines)
            if flushed:
                sections.append(flushed)
            buf = [para]
            start_line = line_cursor
            buf_lines = n_lines
        else:
            buf.append(para)
            if not buf[:-1]:  # first para in this buffer
                start_line = line_cursor
            buf_lines = sum(p.count("\n") + 1 for p in buf)
        line_cursor += n_lines + 1  # +1 for the blank line

    if buf:
        flushed = flush(buf, start_line, buf_lines)
        if flushed:
            sections.append(flushed)

    if not sections:
        # Empty file → single placeholder section so downstream stages don't
        # choke on zero sections.
        sections.append(
            Section(section_path="全文", level=1, title="全文", page_range=None, text="")
        )

    full_text = "\n\n".join(s.text for s in sections)
    meta = ExtractMeta(
        parser=PARSER_NAME,
        format="txt",
        page_count=None,
        header_count=0,
        coverage=None,
    )
    return (
        ParseResult(
            full_text=full_text,
            sections=sections,
            structure="flat",
            parser=PARSER_NAME,
            warnings=[],
        ),
        meta,
    )


__all__ = ["PARSER_NAME", "parse_txt"]
