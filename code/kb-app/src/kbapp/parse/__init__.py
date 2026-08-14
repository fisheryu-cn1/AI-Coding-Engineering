"""Document parsers (M2; 设计 05 §3.2 + 09 §1/§4).

Public API:

- :func:`parse_path` — dispatch by extension, returns a :class:`ParseResult`
  and an :class:`ExtractMeta` carrying page-count/coverage/parser-name info
  used by the chunk + classify stages.
- :class:`ParseResult`, :class:`Section` — schema (05 §3.2).
- :class:`ExtractMeta` — page count, coverage, parser name (for cache key +
  extract_status decision).

Per-format modules live next to this package:

- :mod:`kbapp.parse.txt` — plain text → flat structure
- :mod:`kbapp.parse.md` — markdown-it-py → tree structure
- :mod:`kbapp.parse.html` — Trafilatura → tree structure (or flat on failure)
- :mod:`kbapp.parse.docx` — python-docx → flat structure
- :mod:`kbapp.parse.pdf_fast` — pymupdf4llm (PyMuPDF fast path; 09 §4 三级判定)
- :mod:`kbapp.parse.registry` — format dispatch + cache key
- :mod:`kbapp.parse.manifest` — summaries/*.md frontmatter/binding (09 §5)
- :mod:`kbapp.parse.chunk` — section-aware chunking + fts_chunks (09 §6)
"""

from __future__ import annotations

from kbapp.parse.base import (
    ExtractMeta,
    ParseError,
    Parser,
    ParseResult,
    Section,
)
from kbapp.parse.registry import (
    ALLOWED_EXTENSIONS,
    extension_for,
    extract_meta_for_path,
    parse_path,
)

__all__ = [
    "ALLOWED_EXTENSIONS",
    "ExtractMeta",
    "ParseError",
    "ParseResult",
    "Parser",
    "Section",
    "extract_meta_for_path",
    "extension_for",
    "parse_path",
]
