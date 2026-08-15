"""Web server factory (M6; 15 §6.1).

FastAPI 只读服务，绑定 127.0.0.1:8371（15 §6.1）。
所有 GET 路由；写操作在 API 层不存在（15 D15-4）。
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from kbapp.core.config import Config
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry


def create_app(*, registry: Registry, cfg: Config, paths: DataPaths) -> FastAPI:
    """Return a FastAPI app bound to the given state.

    ``state`` is stored on ``app.state`` so the API endpoints can grab
    registry/cfg/paths without module-level globals. The static dir is
    mounted at ``/static``; the four pages are served from ``/``.
    """
    static_dir = Path(__file__).parent / "static"

    app = FastAPI(title="GraphIt-KB Web", version="0.1.0")
    app.state.registry = registry
    app.state.cfg = cfg
    app.state.paths = paths

    @app.get("/")
    def index() -> FileResponse:
        from fastapi.responses import FileResponse

        return FileResponse(static_dir / "index.html")

    @app.get("/document")
    def document_page() -> FileResponse:
        from fastapi.responses import FileResponse

        return FileResponse(static_dir / "document.html")

    @app.get("/status")
    def status_page() -> FileResponse:
        from fastapi.responses import FileResponse

        return FileResponse(static_dir / "status.html")

    @app.get("/graph")
    def graph_page() -> FileResponse:
        from fastapi.responses import FileResponse

        return FileResponse(static_dir / "graph.html")

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # API endpoints registered
    from kbapp.web.api import router as api_router

    app.include_router(api_router)

    return app


__all__ = ["create_app"]
