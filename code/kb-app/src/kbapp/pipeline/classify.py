"""降级分类 (09 §7) — keyword scoring + doc_type rules.

M2 skips the M3 embedding-centroid design. Classification is a pure
keyword-counting pass over the first chapter title and the first 4000
characters of body text, with optional LLM fallback when available.

Algorithms
----------

**Topic scoring (09 §7.1)**::

    score(topic) = 3 * title_hits + 1 * body_hits
    best1, best2 = top2(scores)
    if best1.score >= min_keyword_score
       and best1.score >= best2.score * top_ratio:
        topic = best1.topic
    else:
        topic = None
        files.status = 'needs_confirm'

Both scores are computed case-insensitively; a keyword match counts once
per term per region (title or body) — duplicating a word in the body does
not inflate the score.

**doc_type (09 §7.3)** — first match wins, in priority order:

1. ``files.summary_source == 'curated'`` → ``paper``
2. Filename matches arXiv ID regex (``\\d{4}\\.\\d{4,5}``) → ``paper``
3. ``corpus == 'design'`` or path contains ``/design/`` → ``design``
4. Extension ``.pdf`` → ``paper``
5. Otherwise → ``other``

Rule ⑤ takes an **optional LLM fallback** (:func:`llm_arbitrate_doc_type`)
when a client is available (09 §7.3); without one it stays ``other`` (09
§7.4 — classification works fully offline).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path as PathLib
from typing import Any

# 09 §7.3 doc_type enum.
DOC_TYPES: tuple[str, ...] = ("paper", "design", "other")

# arXiv ID pattern (06 §4.5 example: ``2607.03691`` / ``2607.03691v2``).
_ARXIV_ID_RE = re.compile(r"\b\d{4}\.\d{4,5}\b")


# ---------------------------------------------------------------------------
# Topic scoring
# ---------------------------------------------------------------------------


@dataclass
class TopicScore:
    topic: str
    score: int
    title_hits: int
    body_hits: int


def score_topics(
    *,
    title: str,
    body: str,
    keywords: dict[str, list[str]],
    body_limit: int = 4000,
) -> list[TopicScore]:
    """Score each topic against ``title`` + first ``body_limit`` chars of body.

    ``keywords`` maps ``topic → list[str]``. Case-insensitive; one hit per
    term per region (title or body). Returns topics with ``score > 0``,
    sorted by score desc, then by topic name asc (stable order for tests).
    """
    title_lc = title.lower()
    body_lc = body[:body_limit].lower()
    out: list[TopicScore] = []
    for topic, kws in keywords.items():
        if not kws:
            continue
        th = sum(1 for kw in kws if kw.lower() in title_lc)
        bh = sum(1 for kw in kws if kw.lower() in body_lc)
        total = 3 * th + bh
        if total > 0:
            out.append(TopicScore(topic=topic, score=total, title_hits=th, body_hits=bh))
    out.sort(key=lambda s: (-s.score, s.topic))
    return out


def decide_topic(
    *,
    scores: list[TopicScore],
    min_keyword_score: int,
    top_ratio: float,
) -> tuple[str | None, bool]:
    """Apply the 09 §7.1 thresholds.

    Returns ``(topic, needs_confirm)``. ``needs_confirm=True`` means the
    caller should set ``files.status='needs_confirm'`` and leave topic NULL.
    """
    if not scores:
        return None, True
    best = scores[0]
    second = scores[1] if len(scores) > 1 else None
    if best.score < min_keyword_score:
        return None, True
    if second is not None and best.score < second.score * top_ratio:
        return None, True
    return best.topic, False


# ---------------------------------------------------------------------------
# doc_type decision (09 §7.3)
# ---------------------------------------------------------------------------


def decide_doc_type(
    *,
    path: PathLib,
    corpus: str,
    summary_source: str | None = None,
) -> str:
    """Return one of :data:`DOC_TYPES` per the priority chain."""
    # 1. curated summary binding wins
    if summary_source == "curated":
        return "paper"
    # 2. arXiv ID in filename
    if _ARXIV_ID_RE.search(path.name):
        return "paper"
    # 3. corpus / path-based
    if corpus == "design" or "/design/" in str(path).replace("\\", "/"):
        return "design"
    # 4. PDF default
    if path.suffix.lower() == ".pdf":
        return "paper"
    # 5. fallback
    return "other"


def llm_arbitrate_doc_type(
    *,
    llm: Any,
    title: str,
    body: str,
    doc_id: str | None = None,
) -> str:
    """LLM fallback for doc_type rule ⑤ (09 §7.3).

    Called only when the rule chain falls through to ``other`` and an LLM
    client is available. Any failure (unavailable / malformed JSON) keeps
    ``other`` — classification must never crash the pipeline (09 §7.4).
    """
    import json

    prompt = (
        "Classify the document type. Reply with JSON only: "
        '{"doc_type": "paper"|"design"|"other"}.\n\n'
        f"Title: {title[:200]}\n\nBody:\n{body[:2000]}"
    )
    try:
        raw = llm.complete(
            [{"role": "user", "content": prompt}],
            json_mode=True,
            max_tokens=64,
            purpose="arbitrate",
            doc_id=doc_id,
        )
        data = json.loads(raw)
        dt = str(data.get("doc_type", "other")).strip().lower()
        return dt if dt in DOC_TYPES else "other"
    except Exception:
        return "other"


__all__ = [
    "DOC_TYPES",
    "TopicScore",
    "decide_doc_type",
    "decide_topic",
    "llm_arbitrate_doc_type",
    "score_topics",
]
