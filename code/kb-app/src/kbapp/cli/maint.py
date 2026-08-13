"""``kb maintenance ...`` stub. M3 起替换为 LanceDB 维护等。"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="维护（cleanup / compaction / 依赖漂移检查）— M3 起逐步落地",
    no_args_is_help=True,
)


@app.command("cleanup")
def cleanup_cmd() -> None:
    """[M3 落地] 清理 LanceDB 旧版本。"""
    typer.echo("M1 占位：maintenance cleanup 将在 M3 落地。")


@app.command("deps")
def deps_cmd() -> None:
    """[M2 落地] 依赖版本与漂移检查。"""
    typer.echo("M1 占位：maintenance deps 将在 M2 落地。")


__all__ = ["app"]
