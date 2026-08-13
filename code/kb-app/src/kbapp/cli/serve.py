"""``kb serve ...`` stub. M4 (mcp) / M6 (viz) 起替换为真实命令。"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="服务（MCP stdio/HTTP + Web UI）— M4 / M6 落地",
    no_args_is_help=True,
)


@app.command("mcp")
def mcp_cmd() -> None:
    """[M4 落地] 启动 MCP 服务（stdio/HTTP）。"""
    typer.echo("M1 占位：serve mcp 将在 M4 落地（mcp>=1.29,<2 钉版）。")


@app.command("viz")
def viz_cmd() -> None:
    """[M6 落地] 启动 Web UI（FastAPI + G6 v5）。"""
    typer.echo("M1 占位：serve viz 将在 M6 落地。")


__all__ = ["app"]
