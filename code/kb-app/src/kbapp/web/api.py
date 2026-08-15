"""Read-only API endpoints (15 §6.2).

All GET; never expose write methods. Graph endpoints (subgraph/path)
live in Task 17.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api")


def _state(request: Request):
    s = request.app.state
    return s.registry, s.cfg, s.paths


@router.get("/search")
def search(q: str, limit: int = 10, request: Request = None) -> dict[str, Any]:  # type: ignore[assignment]
    """章节级命中（hybrid 检索）。"""
    from kbapp.llm import get_llm_or_none
    from kbapp.retrieve import search as _search

    registry, cfg, _paths = _state(request)
    llm = get_llm_or_none(cfg)
    result = _search(registry, cfg, q, mode="hybrid", topic=None, limit=limit, llm=llm)
    return {
        "hits": [
            {
                "doc_id": h.doc_id,
                "section_path": h.section_path,
                "title": h.title,
                "score": h.score,
                "snippet": h.snippet,
                "topic": h.topic,
            }
            for h in result.hits
        ],
        "note": result.note,
    }


@router.get("/docs/{doc_id}")
def get_doc(doc_id: str, request: Request) -> dict[str, Any]:
    """文档元数据 + summary + section 树。"""
    from kbapp.core.registry import get_file
    from kbapp.retrieve.assembler import read_summary, section_tree

    registry, _cfg, _paths = _state(request)
    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
    if row is None:
        raise HTTPException(status_code=404, detail="DOC_NOT_FOUND")
    return {
        "doc": {
            "doc_id": row.doc_id,
            "path": row.path,
            "title": row.title,
            "corpus": row.corpus,
            "doc_type": row.doc_type,
            "topic": row.topic,
            "status": row.status,
        },
        "summary": read_summary(registry, row),
        "sections": section_tree(registry, row.doc_id),
    }


@router.get("/topics")
def list_topics_api(request: Request) -> dict[str, Any]:
    from kbapp.core.registry import list_topics

    registry, _cfg, _paths = _state(request)
    with registry.read_only() as conn:
        rows = list_topics(conn)
    return {
        "topics": [
            {"name": t.name, "doc_count": t.doc_count, "description": t.description}
            for t in rows
        ]
    }


@router.get("/status")
def status_api(request: Request) -> dict[str, Any]:
    from kbapp.core.registry import (
        count_chunks,
        count_files_by_extract_status,
        count_files_by_status,
    )
    from kbapp.core.task import count_tasks

    registry, _cfg, paths = _state(request)
    with registry.read_only() as conn:
        by_status = count_files_by_status(conn)
        by_extract = count_files_by_extract_status(conn)
        chunks = count_chunks(conn)
    tasks = {
        "pending": count_tasks(registry, status="pending"),
        "running": count_tasks(registry, status="running"),
        "done": count_tasks(registry, status="done"),
        "failed": count_tasks(registry, status="failed"),
    }
    return {
        "tasks": tasks,
        "library": {
            "docs": sum(by_status.values()),
            "by_status": by_status,
            "by_extract": by_extract,
            "chunks": chunks,
        },
        "graph": {"available": (paths.graph_dir / "graph.lbug").exists()},
    }


@router.get("/graph/subgraph")
def graph_subgraph(
    topic: str,
    hops: int = 2,
    request: Request = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """主题 N 跳子图（500 节点裁剪）。"""
    from kbapp.graph import GraphError, make_graph_store, topic_subgraph

    _registry, cfg, paths = _state(request)
    max_nodes = int(cfg.raw["viz"]["max_nodes"])
    try:
        store = make_graph_store(cfg.raw["graph"]["backend"], cfg)
        store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    except (FileNotFoundError, GraphError):
        raise HTTPException(status_code=503, detail="graph unavailable, run kb index reindex --full")
    try:
        return topic_subgraph(store, topic, hops=hops, max_nodes=max_nodes)
    finally:
        store.close()


@router.get("/graph/path")
def graph_path(
    src: str,
    dst: str,
    max_hops: int = 3,
    request: Request = None,  # type: ignore[assignment]
) -> dict[str, Any]:
    """两实体最短路径。"""
    from kbapp.graph import GraphError, entity_path, make_graph_store

    _registry, cfg, paths = _state(request)
    try:
        store = make_graph_store(cfg.raw["graph"]["backend"], cfg)
        store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    except (FileNotFoundError, GraphError):
        raise HTTPException(status_code=503, detail="graph unavailable, run kb index reindex --full")
    try:
        return entity_path(store, src, dst, max_hops=max_hops)
    finally:
        store.close()


__all__ = ["router"]
