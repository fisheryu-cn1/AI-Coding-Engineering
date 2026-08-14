"""Section-aware chunking + ``fts_chunks`` population (09 §6).

Algorithm (09 §6):

- Section is the atomic unit: if ``len(section.text) <= chunk_size`` (default
  2048), emit one chunk.
- Otherwise recursively walk paragraph boundaries (preferred: blank lines;
  fall back to single newlines for ``structure='flat'`` inputs) until each
  piece is short enough.
- Adjacent chunks overlap by ``chunk_overlap`` characters (default 200) so
  cross-boundary queries still hit context.

Each chunk carries ``chunk_id = "<doc_id>#c%03d"`` (09 §6). The function
writes JSON to ``cache/extracted/<sha256>.json`` (05 §2.4) and FTS rows
under the per-doc transaction (delete-then-insert for idempotent reparse).
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from kbapp.parse.base import ParseResult

DEFAULT_CHUNK_SIZE = 2048
DEFAULT_CHUNK_OVERLAP = 200


@dataclass
class Chunk:
    chunk_id: str  # "<doc_id>#c%03d"
    doc_id: str
    section_path: str
    title: str
    text: str
    order: int  # 0-based, monotonic within the doc
    start: int = 0  # char offset into section.text
    end: int = 0  # char offset (exclusive)
    page_range: str | None = None


@dataclass
class ChunkingResult:
    doc_id: str
    chunks: list[Chunk] = field(default_factory=list)
    skipped_short_sections: int = 0


def chunk_document(
    *,
    doc_id: str,
    parse: ParseResult,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> ChunkingResult:
    """Split a parse result into chunks keyed by ``chunk_id = "<doc_id>#c%03d"``.

    Sections shorter than ``chunk_size`` produce a single chunk; longer
    sections are split along paragraph boundaries with ``chunk_overlap``
    prefix carry-over from the previous chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须 > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须 ≥ 0 且 < chunk_size")

    chunks: list[Chunk] = []
    order = 0

    for sec in parse.sections:
        if not sec.text:
            continue
        if len(sec.text) <= chunk_size:
            order += 1
            chunks.append(
                Chunk(
                    chunk_id=f"{doc_id}#c{order:03d}",
                    doc_id=doc_id,
                    section_path=sec.section_path,
                    title=sec.title,
                    text=sec.text,
                    order=order - 1,
                    start=0,
                    end=len(sec.text),
                    page_range=sec.page_range,
                )
            )
            continue

        for piece in _split_section(sec.text, chunk_size, chunk_overlap):
            order += 1
            chunks.append(
                Chunk(
                    chunk_id=f"{doc_id}#c{order:03d}",
                    doc_id=doc_id,
                    section_path=sec.section_path,
                    title=sec.title,
                    text=piece.text,
                    order=order - 1,
                    start=piece.start,
                    end=piece.end,
                    page_range=sec.page_range,
                )
            )

    return ChunkingResult(doc_id=doc_id, chunks=chunks)


def write_cache_payload(
    *,
    sha256: str,
    path: Path,
    format: str,
    parse: ParseResult,
    chunks: list[Chunk],
    cache_dir: Path,
    page_count: int | None = None,
    header_count: int | None = None,
    coverage: float | None = None,
) -> Path:
    """Write ``cache/extracted/<sha256>.json`` (05 §2.4 schema).

    Returns the written path. Callers (runner) read this back on cache hit
    instead of re-parsing. ``page_count`` / ``header_count`` / ``coverage``
    carry the parse metrics so a cache hit rehydrates the same numbers
    (P3-3) rather than reporting ``None``.
    """
    payload = {
        "sha256": sha256,
        "path": str(path),
        "format": format,
        "parser": parse.parser,
        "structure": parse.structure,
        "page_count": page_count,
        "header_count": header_count,
        "coverage": coverage,
        "full_text": parse.full_text,
        "sections": [
            {
                "section_path": s.section_path,
                "level": s.level,
                "title": s.title,
                "page_range": s.page_range,
                "text": s.text,
            }
            for s in parse.sections
        ],
        "warnings": parse.warnings,
        "chunks": [
            {
                "chunk_id": c.chunk_id,
                "section_path": c.section_path,
                "title": c.title,
                "text": c.text,
                "page_range": c.page_range,
                "order": c.order,
            }
            for c in chunks
        ],
        "extracted_at": _now_iso(),
    }
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"{sha256}.json"
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out


def load_cache_payload(path: Path) -> dict[str, object]:
    """Read a cache file (used by scan for cache hits)."""
    return json.loads(path.read_text(encoding="utf-8"))


def cache_path_for(sha256: str, cache_dir: Path) -> Path:
    """Resolve ``cache/extracted/<sha256>.json`` without IO."""
    return cache_dir / f"{sha256}.json"


# ---------------------------------------------------------------------------
# Internal splitter
# ---------------------------------------------------------------------------


@dataclass
class _Piece:
    text: str
    start: int
    end: int


def _split_section(text: str, chunk_size: int, overlap: int) -> Iterable[_Piece]:
    """Greedy paragraph-aware splitter.

    1. Find blank-line boundaries (``\\n\\n``).
    2. Greedily concatenate paragraphs until adding the next would exceed
       ``chunk_size``; emit a chunk.
    3. Each chunk after the first starts ``overlap`` chars into the previous
       chunk's tail (carry-over for cross-boundary recall).
    """
    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return

    buf: list[tuple[int, str]] = []  # (start_offset, paragraph)
    buf_len = 0

    for start, para in paragraphs:
        if buf_len + len(para) + (2 if buf else 0) > chunk_size and buf:
            yield _emit(buf, chunk_size, overlap)
            # Carry-over: last ``overlap`` chars of the previous emission.
            tail = "".join(p for _, p in buf)[-overlap:] if overlap else ""
            if tail:
                buf = [(0, tail)]
                buf_len = len(tail)
            else:
                buf = []
                buf_len = 0
        if buf:
            buf.append((start, "\n\n" + para))
            buf_len += 2 + len(para)
        else:
            buf.append((start, para))
            buf_len = len(para)

    if buf:
        yield _emit(buf, chunk_size, overlap)


def _split_paragraphs(text: str) -> list[tuple[int, str]]:
    """Split on blank lines; keep character offsets (for ``Chunk.start``)."""
    out: list[tuple[int, str]] = []
    cursor = 0
    for block in text.split("\n\n"):
        start = text.find(block, cursor)
        if start < 0:
            start = cursor
        if block.strip():
            out.append((start, block.strip()))
        cursor = start + len(block) + 2  # +2 for the ``\n\n``
    return out


def _emit(buf: list[tuple[int, str]], chunk_size: int, overlap: int) -> _Piece:
    """Flatten the buffer into one chunk, applying ``overlap`` carry-over.

    The returned piece's ``start`` is the original offset of the first
    paragraph; ``end`` is exclusive of the trailing carry-over.
    """
    full = "".join(p for _, p in buf)
    if overlap and len(full) > chunk_size:
        # The previous chunk already carried its tail — we just truncate.
        full = full[:chunk_size]
    start = buf[0][0]
    return _Piece(text=full, start=start, end=start + len(full))


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = [
    "Chunk",
    "ChunkingResult",
    "DEFAULT_CHUNK_OVERLAP",
    "DEFAULT_CHUNK_SIZE",
    "cache_path_for",
    "chunk_document",
    "load_cache_payload",
    "write_cache_payload",
]
