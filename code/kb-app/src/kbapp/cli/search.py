"""``kb search ...`` stub. M3 起替换为真实命令。"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="检索与查阅（search / show / read / related / compare / topics）— M3 落地",
    no_args_is_help=True,
)


@app.command("query")
def query_cmd() -> None:
    """[M3 落地] 三路混合检索 + RRF。"""
    typer.echo("M1 占位：search query 将在 M3 落地（FTS5 + LanceDB + RRF）。")


@app.command("show")
def show_cmd() -> None:
    """[M3 落地] 文档元数据 + 章节树 + 摘要。"""
    typer.echo("M1 占位：search show 将在 M3 落地。")


@app.command("read")
def read_cmd() -> None:
    """[M3 落地] 输出章节原文。"""
    typer.echo("M1 占位：search read 将在 M3 落地。")


@app.command("related")
def related_cmd() -> None:
    """[M5 落地] 关联资料 + 原因标注。"""
    typer.echo("M1 占位：search related 将在 M5 落地（实体图谱）。")


@app.command("compare")
def compare_cmd() -> None:
    """[M5 落地] 多文档观点并排。"""
    typer.echo("M1 占位：search compare 将在 M5 落地。")


@app.command("topics")
def topics_cmd() -> None:
    """[M3 落地] 主题清单与规模。"""
    typer.echo("M1 占位：search topics 将在 M3 落地。")


__all__ = ["app"]
