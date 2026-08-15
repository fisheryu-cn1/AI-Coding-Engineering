"""Graph structure sync (15 §4.1 / DoD B1 前半).

Pulls Document / Section / Topic facts from the SQLite registry + parse
cache JSON and upserts them into the graph. Idempotent: re-running
replaces the same row's properties via MERGE.

MVP-simplified schema (15 §3.2 / D15-2):

- Nodes: Document / Section / Topic (no Chunk)
- Edges: CONTAINS_SECTION / ABOUT_TOPIC (no CITES, no SUPERSEDES, no
  Section→Topic — Section topic is derived via the parent Document)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry, get_file


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sync_document_structure(
    store: Any,
    registry: Registry,
    paths: DataPaths,
    doc_id: str,
) -> dict[str, int]:
    """Upsert Document + Section + Topic + CONTAINS_SECTION + ABOUT_TOPIC.

    Returns metrics: ``{"sections": N, "topic": 0|1}``.
    """
    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
    if row is None:
        return {"sections": 0, "topic": 0}

    cache_path = paths.extracted_dir / f"{row.sha256}.json"
    sections: list[dict] = []
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            sections = cached.get("sections") or []
        except (OSError, json.JSONDecodeError):
            sections = []

    document_node = {
        "doc_id": row.doc_id,
        "title": row.title or "",
        "path": row.path,
        "sha256": row.sha256,
        "doc_type": row.doc_type or "",
        "corpus": row.corpus,
        "arxiv_id": row.arxiv_id or "",
        "version": row.version or "",
        "authors": row.authors or "",
        "published": row.published or "",
        "summary_l1": "",
        "summary_l2": "",
        "summary_path": row.summary_path or "",
        "valid_from": row.updated_at or _now_iso(),
        "valid_to": "",
    }
    store.upsert_nodes("Document", [document_node])

    section_nodes: list[dict] = []
    section_edges: list[dict] = []
    for order, sec in enumerate(sections):
        sid = f"{doc_id}#{sec.get('section_path', str(order))}"
        page_range = sec.get("page_range") or ""
        section_nodes.append(
            {
                "section_id": sid,
                "doc_id": doc_id,
                "section_path": str(sec.get("section_path", str(order))),
                "level": int(sec.get("level", 0) or 0),
                "title": sec.get("title", "") or "",
                "summary": "",
                "page_range": page_range,
                "seq": order,
            }
        )
        section_edges.append({"src": doc_id, "dst": sid, "seq": order})
    if section_nodes:
        store.upsert_nodes("Section", section_nodes)
        store.upsert_edges("CONTAINS_SECTION", section_edges)

    topic_added = 0
    if row.topic:
        store.upsert_nodes("Topic", [{"name": row.topic, "description": ""}])
        store.upsert_edges(
            "ABOUT_TOPIC",
            [{"src": doc_id, "dst": row.topic, "confidence": 1.0}],
        )
        topic_added = 1

    return {"sections": len(section_nodes), "topic": topic_added}


__all__ = ["sync_document_structure"]
