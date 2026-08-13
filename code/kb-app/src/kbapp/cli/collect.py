"""``kb collect ...`` stub. M7 起替换为真实命令。"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="自动收集 + Inbox 审核（collect run / inbox list|accept|reject / report monthly）"
    " — M7 落地",
    no_args_is_help=True,
)


@app.command("run")
def run_cmd() -> None:
    """[M7 落地] 执行一次自动收集。"""
    typer.echo("M1 占位：collect run 将在 M7 落地（arXiv + 网页白名单 + 去重 + 评分）。")


@app.command("inbox")
def inbox_cmd() -> None:
    """[M7 落地] Inbox 待审核列表。"""
    typer.echo("M1 占位：inbox list|accept|reject 将在 M7 落地。")


@app.command("report")
def report_cmd() -> None:
    """[M7 落地] 月度报告。"""
    typer.echo("M1 占位：report monthly 将在 M7 落地。")


__all__ = ["app"]
