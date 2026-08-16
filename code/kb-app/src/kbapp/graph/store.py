"""GraphStore 协议与工厂（05 §3.1 / 15 §3.1；单一选型 ladybug，15 D15-10）。

The protocol is implemented by backend-specific stores (LadybugStore). The
factory is the only entry point: callers ask for``make_graph_store("ladybug",
cfg)`` and never instantiate a backend directly. This means swapping the
backend (e.g. if LadybugDB upstream breaks) is a matter of rewriting one
file — see 15 §3.3 for the "single backend, contract-test set" insurance.
"""

from __future__ import annotations

from typing import Literal, Protocol


class GraphError(Exception):
    """图库不可用 / 不支持的后端 / 缺依赖。"""


class GraphStore(Protocol):
    """Thin Cypher-facing protocol. Backends translate to native DDL."""

    def open(self, path: str, mode: Literal["rw", "ro"]) -> None: ...
    def close(self) -> None: ...
    def upsert_nodes(self, label: str, rows: list[dict]) -> None: ...
    def upsert_edges(self, rel: str, rows: list[dict]) -> None: ...
    def query(self, cypher: str, params: dict | None = None) -> list[dict]: ...
    def shortest_path(
        self,
        src: tuple[str, str],
        dst: tuple[str, str],
        max_hops: int = 3,
    ) -> list[dict]: ...


def make_graph_store(backend: str, cfg) -> GraphStore:
    """Factory: only ``"ladybug"`` is accepted (15 D15-10 单一选型）。"""
    if backend == "ladybug":
        try:
            from kbapp.graph.ladybug_store import LadybugStore
        except ImportError as e:
            raise GraphError("ladybug 依赖缺失：uv sync --extra graph-ladybug") from e
        return LadybugStore(cfg)
    raise GraphError(f"不支持的后端 {backend!r}（单一选型 ladybug，15 D15-10）")


__all__ = ["GraphError", "GraphStore", "make_graph_store"]
