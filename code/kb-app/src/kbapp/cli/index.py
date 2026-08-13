"""``kb index ...`` stub. M2 起替换为真实命令。"""

from __future__ import annotations

import typer

app = typer.Typer(
    help="索引管理（scan / index run / reindex / add）— M2 落地",
    no_args_is_help=True,
)


@app.command("scan")
def scan_cmd() -> None:
    """[M2 落地] 扫描资料目录，报告变更。"""
    typer.echo("M1 占位：scan 将在 M2 落地（指纹比对 + 任务入队）。")


@app.command("run")
def run_cmd() -> None:
    """[M2 落地] 执行待处理任务。"""
    typer.echo("M1 占位：index run 将在 M2 落地（P1→P5 流水线）。")


@app.command("reindex")
def reindex_cmd() -> None:
    """[M2 落地] 全量重建索引。"""
    typer.echo("M1 占位：reindex 将在 M2 落地（保留/丢弃缓存两种模式）。")


@app.command("add")
def add_cmd() -> None:
    """[M2 落地] 手动纳入库外文件。"""
    typer.echo("M1 占位：add 将在 M2 落地（路径登记 + 入队完整流水线）。")


__all__ = ["app"]
