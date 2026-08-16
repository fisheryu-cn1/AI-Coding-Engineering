"""``kb serve ...`` stub. M4 (mcp) / M6 (viz) 起替换为真实命令。"""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(
    help="服务（MCP stdio/HTTP + Web UI）— M4 / M6 落地",
    no_args_is_help=True,
)


@app.command("mcp")
def mcp_cmd() -> None:
    """启动 MCP 服务（stdio；13 §2）。"""
    try:
        from kbapp.mcp_server import mcp
    except ImportError as e:
        name = e.name or ""
        if name != "mcp" and not name.startswith("mcp."):
            raise
        typer.echo("未安装 mcp extra：请先 `uv sync --extra mcp` 后重试。")
        raise typer.Exit(code=1) from None
    mcp.run(transport="stdio")


@app.command("viz")
def viz_cmd(
    ctx: typer.Context,
    port: int | None = typer.Option(  # noqa: B008
        None,
        "--port",
        help="覆盖 viz.port 配置（默认 8371）；host 恒为 127.0.0.1",
    ),
) -> None:
    """启动 Web UI（FastAPI + G6 v5 bound 127.0.0.1；15 §6.1）。"""
    try:
        import uvicorn

        from kbapp.web import create_app
    except ImportError as e:
        name = e.name or ""
        viz_mods = ("uvicorn", "fastapi", "starlette")
        if not any(name == m or name.startswith(f"{m}.") for m in viz_mods):
            raise
        typer.echo("未安装 viz extra：请先 `uv sync --extra viz` 后重试。")
        raise typer.Exit(code=1) from None

    from kbapp.core.config import load_config
    from kbapp.core.paths import DataPaths
    from kbapp.core.registry import Registry

    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    cfg = load_config(paths.config_path)
    registry = Registry(paths.registry_db)
    registry.initialize()

    actual_port = port if port is not None else int(cfg.raw["viz"]["port"])
    app = create_app(registry=registry, cfg=cfg, paths=paths)
    uvicorn.run(app, host="127.0.0.1", port=actual_port, log_level="info")


__all__ = ["app"]
