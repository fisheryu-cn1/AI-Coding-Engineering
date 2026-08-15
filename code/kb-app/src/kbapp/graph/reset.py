"""Graph reset utility (15 §3.3).

The graph store is **derived data**: any moment we can rebuild it from
SQLite + parse caches. There is no in-graph migration tool — destructive
schema changes are recovered by deleting the graph directory and
re-running the pipeline.
"""

from __future__ import annotations

import shutil

from kbapp.core.paths import DataPaths


def reset_graph(paths: DataPaths) -> None:
    """Remove ``paths.graph_dir`` entirely; idempotent (no error if absent)."""
    shutil.rmtree(paths.graph_dir, ignore_errors=True)


__all__ = ["reset_graph"]
