"""Pipeline graph stages (M5; 15 §4.1).

Three stage functions wired into the runner:

- :func:`stage_index_graph` — open the graph store, sync document
  structure, close. Branched on parse success.
- :func:`stage_tombstone_graph` — set ``valid_to`` on the Document node
  (soft delete, do not physically remove edges).
- :func:`stage_extract_graph` — entity + relation extraction (15 §4.2);
  gated by :func:`kbapp.graph.extract.is_core_doc`.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from kbapp.core.task import TerminalError
from kbapp.graph import (
    GraphError,
    is_core_doc,
    make_graph_store,
)
from kbapp.graph.sync import sync_document_structure
from kbapp.pipeline.stages import StageResult

if TYPE_CHECKING:
    from kbapp.pipeline.runner import PipelineCtx


_logger = logging.getLogger(__name__)


def _open_store(ctx: PipelineCtx):
    backend = ctx.cfg.raw["graph"]["backend"]
    store = make_graph_store(backend, ctx.cfg)
    # LadybugDB 把路径当作单文件处理（内部 mmap 多个 wal/lock 文件）；目录
    # 路径会拒绝。约定 graph_dir/graph.lbug 作为入口文件。
    store.open(str(ctx.paths.graph_dir / "graph.lbug"), "rw")
    return store


def stage_index_graph(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """Open graph store → sync structure → close; raises TerminalError on hard fail."""
    store = _open_store(ctx)
    try:
        metrics = sync_document_structure(store, ctx.registry, ctx.paths, doc_id)
    except GraphError as e:
        raise TerminalError(f"图库不可用：{e}") from e
    finally:
        store.close()
    return StageResult("ok", metrics=metrics)


def stage_tombstone_graph(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """Soft-delete the Document node by stamping ``valid_to``."""
    from datetime import UTC, datetime

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    store = _open_store(ctx)
    try:
        store.upsert_nodes(
            "Document",
            [{"doc_id": doc_id, "valid_to": now}],
        )
    except GraphError as e:
        raise TerminalError(f"图库不可用：{e}") from e
    finally:
        store.close()
    return StageResult("ok", metrics={"valid_to": now})


def stage_extract_graph(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """Entity + relation extraction (15 §4.2). Gated by is_core_doc.

    Implementation lives in :func:`kbapp.graph.extract.run_extract` (Task 9).
    This wrapper centralizes store lifecycle + error-class conversion.
    """
    from kbapp.core.registry import get_file
    from kbapp.graph.extract import run_extract

    with ctx.registry.read_only() as conn:
        row = get_file(conn, doc_id)
    if row is None:
        return StageResult("skip", detail=f"doc_id={doc_id} not in files")
    if not is_core_doc(
        ctx.cfg,
        topic=row.topic,
        doc_type=row.doc_type,
        doc_id=doc_id,
    ):
        return StageResult(
            "skip",
            detail=f"not is_core (topic={row.topic} doc_type={row.doc_type})",
        )
    store = _open_store(ctx)
    try:
        metrics = run_extract(
            store=store,
            registry=ctx.registry,
            paths=ctx.paths,
            doc_id=doc_id,
            row=row,
            llm=ctx.llm,
            cfg=ctx.cfg,
        )
    except GraphError as e:
        raise TerminalError(f"图库不可用：{e}") from e
    finally:
        store.close()
    return StageResult("ok", metrics=metrics)


__all__ = [
    "stage_extract_graph",
    "stage_index_graph",
    "stage_tombstone_graph",
]
