"""summaries/*.md manifest binding (09 §5 + 06 §4).

Two header formats exist in the corpus (06 §4.5):

1. **YAML frontmatter** (newer convention, 06 §4.1):

   ```markdown
   ---
   title: "..."
   source_pdf: "10-Foo_v2.pdf"
   arxiv_id: "2607.03691"
   arxiv_version: "v2"
   ...
   ---
   ```

2. **Blockquote header** (legacy, 06 §4.5; the only format actually present
   in the corpus today per the M2 design exploration): the first non-empty
   line is the H1 title, followed by ``> **字段**：值`` lines, e.g.::

       # 论文摘要：Foo

       > **原论文标题**：Foo Bar
       > **完整 PDF 文件名**：`10-Foo_v2.pdf`
       > 作者 / 年份 / 出版：Alice, 2026, ACM
       > 摘要类型：内容索引
       > 生成日期：2026-08-12

   Both formats produce the same :class:`SummaryMeta` record. The runner
   matches ``source_pdf`` against filenames in the corpus and sets
   ``files.summary_source='curated'`` + ``files.summary_path`` accordingly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from kbapp.parse.base import ParseError

#: Mapping from YAML frontmatter keys to canonical SummaryMeta fields.
#: Keys are the exact names expected by the manifest parser (06 §4.2).
_FRONT_KEYS = {
    "title": "title",
    "source_pdf": "source_pdf",
    "arxiv_id": "arxiv_id",
    "arxiv_version": "arxiv_version",
    "authors": "authors",
    "year": "year",
    "venue": "venue",
    "type": "type",
    "generated_at": "generated_at",
    "summary_version": "summary_version",
}

#: Mapping from blockquote labels to canonical fields (06 §4.5).
_BLOCK_MAP = {
    "原论文标题": "title",
    "完整 PDF 文件名": "source_pdf",
    "作者 / 年份 / 出版": "authors_year_venue",
    "作者/年份/出版": "authors_year_venue",
    "作者": "authors_year_venue",
    "摘要类型": "type",
    "生成日期": "generated_at",
}

#: arXiv ID + version parser (06 §4.5: ``arXiv:2607.03691v2``).
_ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})(v(\d+))?", re.IGNORECASE)


@dataclass
class SummaryMeta:
    """Manifest record parsed from a ``summaries/*.md`` file."""

    source_pdf: str | None  # the binding key; matches against corpus filenames
    title: str | None
    arxiv_id: str | None
    arxiv_version: str | None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    summary_type: str | None = None
    generated_at: str | None = None
    summary_version: str | None = None
    path: Path | None = None  # the summary file path (for diagnostic)
    raw: dict[str, object] = field(default_factory=dict)

    def cache_payload(self) -> dict[str, object]:
        """JSON-serializable view (for cache/extracted/<sha256>.json)."""
        return {
            "source_pdf": self.source_pdf,
            "title": self.title,
            "arxiv_id": self.arxiv_id,
            "arxiv_version": self.arxiv_version,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "summary_type": self.summary_type,
            "generated_at": self.generated_at,
            "summary_version": self.summary_version,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_summary(path: Path) -> SummaryMeta:
    """Parse a single summary file. Raises :class:`ParseError` on read failure.

    Accepts both frontmatter and blockquote headers; returns the same
    :class:`SummaryMeta` shape.
    """
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise ParseError(f"读取 summary 失败：{path} ({e})") from e

    if text.startswith("---"):
        meta = _parse_frontmatter(text)
    else:
        meta = _parse_blockquote(text)

    meta.path = Path(path)
    return meta


def bind_summaries_to_corpus(
    summaries: list[SummaryMeta],
    corpus_pdf_paths: set[str],
) -> dict[str, SummaryMeta]:
    """Map each summary's ``source_pdf`` to a corpus path.

    The scan loop consumes the returned dict and writes
    ``files.summary_source='curated'`` + ``files.summary_path`` for matched
    PDFs. Summaries whose ``source_pdf`` maps to no corpus file are surfaced
    by the caller as ``SUMMARY_MANIFEST_MISMATCH`` and written to ``reports/``
    (06 §4.4) — this function only performs the matching.
    """
    # Index corpus paths by basename (e.g. "10-Foo_v2.pdf").
    by_basename = {Path(p).name: p for p in corpus_pdf_paths}
    out: dict[str, SummaryMeta] = {}
    for s in summaries:
        if not s.source_pdf:
            continue
        if s.source_pdf in by_basename:
            out[by_basename[s.source_pdf]] = s
    return out


# ---------------------------------------------------------------------------
# Parsers (private)
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> SummaryMeta:
    """Parse a markdown file with ``---\\n…\\n---`` YAML header (06 §4.1)."""
    end = text.find("\n---", 3)
    if end < 0:
        raise ParseError("frontmatter 缺少结束符 '---'")
    fm_text = text[3:end].lstrip("\n")
    try:
        data = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        raise ParseError(f"frontmatter YAML 解析失败：{e}") from e
    if not isinstance(data, dict):
        raise ParseError("frontmatter 必须是 mapping")

    raw = dict(data)
    meta = SummaryMeta(
        source_pdf=data.get(_FRONT_KEYS["source_pdf"]),
        title=data.get(_FRONT_KEYS["title"]),
        arxiv_id=data.get(_FRONT_KEYS["arxiv_id"]),
        arxiv_version=data.get(_FRONT_KEYS["arxiv_version"]),
        authors=list(data.get(_FRONT_KEYS["authors"]) or []),
        year=data.get(_FRONT_KEYS["year"]),
        venue=data.get(_FRONT_KEYS["venue"]),
        summary_type=data.get(_FRONT_KEYS["type"]),
        generated_at=str(data.get(_FRONT_KEYS["generated_at"]) or "") or None,
        summary_version=str(data.get(_FRONT_KEYS["summary_version"]) or "") or None,
        raw=raw,
    )
    return meta


# Blockquote header parser. Tolerates:
# - ``> **字段**：值`` and ``> 字段：值`` variants
# - ``> 作者 / 年份 / 出版：Alice, 2026, ACM`` (combined line)
# - arXiv ID embedded as ``arXiv:XXXX.XXXXXvN``
# - H1 title ``# 论文摘要：…`` on the first non-empty line
def _parse_blockquote(text: str) -> SummaryMeta:
    meta = SummaryMeta(
        source_pdf=None,
        title=None,
        arxiv_id=None,
        arxiv_version=None,
    )

    # First non-empty line — try H1 title.
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            meta.title = s.lstrip("#").strip()
        break

    # Walk blockquote lines
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith(">"):
            continue
        body = line.lstrip(">").strip()
        # Match ``**字段**\s*[::：]\s*值`` and strip the prefix.
        # Use a non-greedy quantifier on the field and ensure the colon
        # immediately follows the closing ``**``.
        m = re.match(r"^\*\*(.+?)\*\*\s*[::：]\s*(.*)$", body)
        if m:
            label = m.group(1).strip()
            value = m.group(2).strip().strip("`").strip()
        elif ":" in body or "：" in body:
            if "：" in body:
                label, _, value = body.partition("：")
            else:
                label, _, value = body.partition(":")
            label = label.strip()
            value = value.strip().strip("`").strip()
        else:
            continue

        canon = _BLOCK_MAP.get(label)
        if canon is None:
            continue
        if canon == "authors_year_venue":
            _split_authors_year_venue(value, meta)
        elif canon == "title":
            meta.title = value
        elif canon == "source_pdf":
            meta.source_pdf = value
            # The legacy format sometimes embeds arXiv inline.
            m = _ARXIV_RE.search(value)
            if m:
                meta.arxiv_id = m.group(1)
                if m.group(3):
                    meta.arxiv_version = f"v{m.group(3)}"
        elif canon == "type":
            meta.summary_type = value
        elif canon == "generated_at":
            meta.generated_at = value

    return meta


def summary_body_text(path: Path) -> str:
    """返回摘要正文（去除 YAML frontmatter 元数据头，11 §3.1/§3.4）。

    用于 scan 时从策展文件构建 `$summary` 伪 chunk（纯策展库也进 FTS）。
    """
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            text = text[end + 4 :]
    return text.strip()


def _split_authors_year_venue(value: str, meta: SummaryMeta) -> None:
    """Split ``Alice, Bob / 2026 / ACM`` into authors/year/venue.

    The legacy format is loosely punctuated — we accept ``,`` / ``;`` /
    ``、`` / ``/`` between the three slots.
    """
    # Try `` / `` separator first.
    parts = [p.strip() for p in re.split(r"\s*/\s*", value) if p.strip()]
    if len(parts) >= 3:
        authors = re.split(r"[,，;；、]", parts[0])
        meta.authors = [a.strip() for a in authors if a.strip()]
        try:
            meta.year = int(re.findall(r"\d{4}", parts[1])[0])
        except (IndexError, ValueError):
            meta.year = None
        meta.venue = parts[2]
        return
    if len(parts) == 2:
        # Could be ``authors / year-venue`` collapsed
        authors = re.split(r"[,，;；、]", parts[0])
        meta.authors = [a.strip() for a in authors if a.strip()]
        m = re.match(r"(\d{4})\s*[,，]?\s*(.+)?", parts[1])
        if m:
            try:
                meta.year = int(m.group(1))
            except ValueError:
                meta.year = None
            meta.venue = (m.group(2) or "").strip() or None
        return
    # Last resort: search for the year anywhere in the string.
    m = re.search(r"(\d{4})", value)
    if m:
        try:
            meta.year = int(m.group(1))
        except ValueError:
            meta.year = None


__all__ = [
    "SummaryMeta",
    "bind_summaries_to_corpus",
    "parse_summary",
    "summary_body_text",
]
