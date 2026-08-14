"""``kb serve ...`` stub. M4 (mcp) / M6 (viz) 起替换为真实命令。"""

from __future__ import annotations

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
        # 仅当缺的是 mcp 本体（或其子模块）时才报"未装 extra"；传递依赖导入
        # 失败应原样上抛，避免误报（13 §2.1 评审 P3-3）。
        name = e.name or ""
        if name != "mcp" and not name.startswith("mcp."):
            raise
        typer.echo("未安装 mcp extra：请先 `uv sync --extra mcp` 后重试。")
        raise typer.Exit(code=1) from None
    mcp.run(transport="stdio")


@app.command("viz")
def viz_cmd() -> None:
    """[M6 落地] 启动 Web UI（FastAPI + G6 v5）。"""
    typer.echo("M1 占位：serve viz 将在 M6 落地。")


__all__ = ["app"]
