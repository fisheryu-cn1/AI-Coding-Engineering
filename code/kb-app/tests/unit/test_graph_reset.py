"""Unit tests for :mod:`kbapp.graph.reset` (15 §3.3)."""

from __future__ import annotations


def test_reset_graph_removes_dir(paths) -> None:
    """reset_graph 删除整个 graph_dir；幂等（不存在时不报错）。"""
    paths.ensure_dirs()
    (paths.graph_dir / "dummy").write_text("x", encoding="utf-8")
    assert paths.graph_dir.exists()

    from kbapp.graph.reset import reset_graph

    reset_graph(paths)
    assert not paths.graph_dir.exists()
    # 二次调用幂等
    reset_graph(paths)
    assert not paths.graph_dir.exists()
