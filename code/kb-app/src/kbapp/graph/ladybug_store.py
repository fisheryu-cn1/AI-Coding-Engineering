"""LadybugDB-backed :class:`GraphStore` (15 §3.1 single backend).

Schema DDL is generated from :mod:`kbapp.graph.schema` (GRAPH_NODES /
GRAPH_RELS) — adding a new node/edge label is a one-place change in
schema.py. The DDL is idempotent (``CREATE … IF NOT EXISTS``) so calls
to :meth:`open` with ``mode='rw'`` re-apply the schema every time.

The store uses the **portable Cypher subset** declared by 15 §3.1
(match / where / return / order / limit / merge / set). Parameter
binding is mandatory — callers never concatenate strings.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, Literal

import ladybug

from kbapp.graph.schema import GRAPH_NODES, GRAPH_RELS, NodeDef, RelDef

_logger = logging.getLogger(__name__)


class LadybugStore:
    """LadybugDB-backed GraphStore."""

    def __init__(self, cfg) -> None:
        self._cfg = cfg
        self._db: Any = None
        self._conn: Any = None
        self._mode: Literal["rw", "ro"] | None = None
        self._path: str | None = None

    # -- lifecycle --------------------------------------------------------

    def open(self, path: str, mode: Literal["rw", "ro"]) -> None:
        if self._db is not None:
            raise RuntimeError("LadybugStore already open")
        self._path = path
        self._mode = mode
        # Ladybug takes a *directory* path; create its parent if missing so
        # the first write doesn't crash. read_only drives write rejection.
        if mode == "rw":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        elif mode == "ro":
            if not Path(path).exists():
                raise FileNotFoundError(f"graph store not found: {path}")
        self._db = ladybug.Database(path, read_only=(mode == "ro"))
        self._conn = ladybug.Connection(self._db)
        if mode == "rw":
            self._ensure_schema()

    def close(self) -> None:
        try:
            if self._conn is not None:
                self._conn.close()
        except Exception:  # pragma: no cover - defensive
            _logger.warning("close Connection raised", exc_info=True)
        self._conn = None
        self._db = None
        self._mode = None
        self._path = None

    # -- schema -----------------------------------------------------------

    def _ensure_schema(self) -> None:
        for node in GRAPH_NODES:
            self._conn.execute(self._ddl_node(node))
        for rel in GRAPH_RELS:
            self._conn.execute(self._ddl_rel(rel))

    @staticmethod
    def _ddl_node(node: NodeDef) -> str:
        cols = [f"{node.pk} STRING"] + [
            f"{k} {v}" for k, v in node.props.items()
        ]
        return f"CREATE NODE TABLE IF NOT EXISTS {node.label}({', '.join(cols)}, PRIMARY KEY({node.pk}))"

    @staticmethod
    def _ddl_rel(rel: RelDef) -> str:
        cols = [f"{k} {v}" for k, v in rel.props.items()]
        cols_part = f", {', '.join(cols)}" if cols else ""
        return (
            f"CREATE REL TABLE IF NOT EXISTS {rel.label}("
            f"FROM {rel.src} TO {rel.dst}{cols_part})"
        )

    # -- mutations --------------------------------------------------------

    def upsert_nodes(self, label: str, rows: list[dict]) -> None:
        self._require_rw()
        if not rows:
            return
        node = _node_by_label(label)
        for row in rows:
            props = {k: row.get(k, "") for k in node.props}
            params = {"pk": row.get(node.pk, ""), **props}
            # LadybugDB Binder 禁止在 MERGE…SET 中再次赋值主键（不允许重写 PK），
            # 故 SET 只列非 PK 属性，自有 MERGE 复合决定 PK。
            set_clause = ", ".join(f"n.{k} = ${k}" for k in node.props)
            self._run(
                f"MERGE (n:{label} {{{node.pk}: $pk}}) SET {set_clause}",
                params,
            )

    def upsert_edges(self, rel: str, rows: list[dict]) -> None:
        self._require_rw()
        if not rows:
            return
        rel_def = _rel_by_label(rel)
        for row in rows:
            src, dst = row.get("src", ""), row.get("dst", "")
            src_label = rel_def.src
            dst_label = rel_def.dst
            src_pk = _pk_for(src_label)
            dst_pk = _pk_for(dst_label)
            props = {k: row.get(k, "") for k in rel_def.props}
            params = {"src": src, "dst": dst, **props}
            set_clause = ", ".join(f"r.{k} = ${k}" for k in rel_def.props)
            self._run(
                f"MATCH (a:{src_label} {{{src_pk}: $src}}) "
                f"MATCH (b:{dst_label} {{{dst_pk}: $dst}}) "
                f"MERGE (a)-[r:{rel}]->(b) SET {set_clause}",
                params,
            )

    # -- queries ----------------------------------------------------------

    def query(self, cypher: str, params: dict | None = None) -> list[dict]:
        self._require_open()
        result = self._conn.execute(cypher, params or {})
        cols = result.get_column_names()
        rows: list[dict] = []
        while result.has_next():
            raw = result.get_next()
            rows.append(dict(zip(cols, raw)))
        return rows

    def shortest_path(
        self,
        src: tuple[str, str],
        dst: tuple[str, str],
        max_hops: int = 3,
    ) -> list[dict]:
        self._require_open()
        src_label, src_value = src
        dst_label, dst_value = dst
        src_pk = _pk_for(src_label)
        dst_pk = _pk_for(dst_label)
        max_hops = max(1, int(max_hops))
        # LadybugDB 不支持 Cypher shortest() 与 list comprehension；用变长路径
        # + ORDER BY length LIMIT 1 折中，仅返回 length 计数。UI 需要 highlights
        # 时再走 store.query 单独 fetch 路径节点。
        cypher = (
            f"MATCH (a:{src_label} {{{src_pk}: $src_v}}), "
            f"      (b:{dst_label} {{{dst_pk}: $dst_v}}) "
            f"MATCH p = (a)-[*..{max_hops}]-(b) "
            f"RETURN length(p) AS length "
            f"ORDER BY length(p) ASC LIMIT 1"
        )
        rows = self.query(cypher, {"src_v": src_value, "dst_v": dst_value})
        if not rows:
            return []
        return [
            {
                "length": int(r["length"]),
            }
            for r in rows
        ]

    # -- helpers ----------------------------------------------------------

    def _run(self, cypher: str, params: dict) -> None:
        self._require_open()
        self._conn.execute(cypher, params)

    def _require_open(self) -> None:
        if self._conn is None:
            raise RuntimeError("LadybugStore not open")

    def _require_rw(self) -> None:
        self._require_open()
        if self._mode != "rw":
            raise PermissionError("LadybugStore opened in read-only mode")


def _node_by_label(label: str) -> NodeDef:
    for n in GRAPH_NODES:
        if n.label == label:
            return n
    raise KeyError(f"未知节点类型：{label!r}")


def _rel_by_label(label: str) -> RelDef:
    for r in GRAPH_RELS:
        if r.label == label:
            return r
    raise KeyError(f"未知关系类型：{label!r}")


def _pk_for(label: str) -> str:
    return _node_by_label(label).pk


def safe_rmtree(path: str | Path) -> None:
    """Public alias exposing shutil.rmtree for :mod:`kbapp.graph.reset`."""
    shutil.rmtree(path, ignore_errors=True)


__all__ = ["LadybugStore", "safe_rmtree"]
