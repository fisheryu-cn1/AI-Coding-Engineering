"""Parser contracts (设计 05 §3.2).

A parser turns a path into a :class:`ParseResult` carrying the full text, a
flat list of :class:`Section` records, and the ``structure`` flag
(``"tree"`` if sections are header-driven, ``"flat"`` otherwise). It also
attaches an :class:`ExtractMeta` carrying the page count + coverage used by
the chunk stage (and ``extract_status`` decision) downstream.

``Parser`` is the contract every per-format module fulfils. The registry
(``parse/registry.py``) dispatches by extension and returns a plain dataclass
pair so the runner pipeline can stay format-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

#: ``structure`` values (05 §3.2).
Structure = Literal["tree", "flat"]


@dataclass
class Section:
    """One section (header boundary or fallback paragraph).

    ``page_range`` is rendered as a string:

    - PDF: ``"1-3"`` (page numbers; inclusive).
    - HTML / MD / TXT / DOCX: ``"L12-L45"`` (0-based line numbers) or
      ``None`` if unknown. The HIT anchor layer (M3) maps this back to
      ``file://path#L<line>`` (05 §3.5 / §6 Hit.anchor).
    """

    section_path: str  # e.g. "§1 引言"
    level: int
    title: str
    page_range: str | None
    text: str


@dataclass
class ParseResult:
    """What every parser returns (05 §3.2)."""

    full_text: str
    sections: list[Section]
    structure: Structure
    parser: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class ExtractMeta:
    """Side-channel metadata carried alongside :class:`ParseResult`.

    The chunk + classify stages use this for cache keying (``parser`` +
    ``format``) and for the ``extract_status`` decision (page coverage ratio,
    page count, header count). Kept separate from ``ParseResult`` so cache
    payloads stay slim.
    """

    parser: str  # one of TXT_PARSER / MD_PARSER / HTML_PARSER / DOCX_PARSER / PDF_PARSER
    format: str  # extension without dot, lowercased
    page_count: int | None = None
    header_count: int = 0  # any-level headings detected
    coverage: float | None = None  # nonspace chars / (pages × page_char_norm)


class ParseError(Exception):
    """Raised when a parser fails irrecoverably.

    The runner catches this in :func:`stage_parse` and translates to
    ``extract_status='failed'`` + ``status='needs_confirm'`` so the file
    surfaces in ``kb status`` for manual inspection.
    """


@runtime_checkable
class Parser(Protocol):
    """Parser protocol — every per-format module exposes one of these."""

    name: str
    formats: tuple[str, ...]

    def parse(self, path: Path) -> tuple[ParseResult, ExtractMeta]: ...


__all__ = [
    "ExtractMeta",
    "ParseError",
    "ParseResult",
    "Parser",
    "Section",
    "Structure",
]
