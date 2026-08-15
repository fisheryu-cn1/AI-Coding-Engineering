"""Unit tests for :mod:`kbapp.web` (15 §6.1, §6.2)。

测试 KB 服务骨架 + 只读 API 端点；只读模式下 POST/PUT 不应返回 200。
"""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client(registry, default_config, paths):
    from kbapp.web.server import create_app

    app = create_app(registry=registry, cfg=default_config, paths=paths)
    return TestClient(app)


def test_static_index_served(client) -> None:
    """GET / 返回首页 HTML（占位 index；Task 16 替换）。"""
    r = client.get("/")
    assert r.status_code == 200
    # 静态默认 404 或 index.html 视 FastAPI mount 顺序
    # 我们的实现 FileResponse(static/index.html) → 200 text/html


def test_no_write_endpoints(client) -> None:
    """API 全 GET：POST 返 405（写机制不实现）。"""
    assert client.post("/api/search").status_code == 405
    assert client.post("/api/status").status_code == 405


def test_status_endpoint_shape(client) -> None:
    """GET /api/status 返回 {tasks, library, graph} 三键。"""
    r = client.get("/api/status")
    assert r.status_code == 200
    data = r.json()
    assert set(data) == {"tasks", "library", "graph"}
    assert "available" in data["graph"]


def test_search_endpoint_returns_shape(client) -> None:
    """GET /api/search?q=&limit= 返回 {hits, note}。"""
    r = client.get("/api/search", params={"q": "x", "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert set(data) == {"hits", "note"}


def test_topics_endpoint_returns_list(client) -> None:
    """GET /api/topics 返回 {topics: [...]}。"""
    r = client.get("/api/topics")
    assert r.status_code == 200
    data = r.json()
    assert "topics" in data
    assert isinstance(data["topics"], list)


def test_docs_endpoint_404_for_missing(client) -> None:
    """GET /api/docs/{id} 缺文档返 404 DOC_NOT_FOUND。"""
    r = client.get("/api/docs/D0000")
    assert r.status_code == 404
    assert r.json() == {"detail": "DOC_NOT_FOUND"}
