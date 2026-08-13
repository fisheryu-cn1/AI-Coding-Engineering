"""``kb`` 入口。组装所有子命令并定义全局选项。"""

from __future__ import annotations

from pathlib import Path

import typer

from kbapp import __version__
from kbapp.cli import (
    collect as collect_cmd,
)
from kbapp.cli import (
    config as config_cmd,
)
from kbapp.cli import (
    index as index_cmd,
)
from kbapp.cli import (
    maint as maint_cmd,
)
from kbapp.cli import (
    search as search_cmd,
)
from kbapp.cli import (
    serve as serve_cmd,
)
from kbapp.cli._common import resolve_data_dir
from kbapp.core.registry import Registry
from kbapp.core.task import count_tasks, reset_stale_running

app = typer.Typer(
    name="kb",
    help="GraphIt-KB 本地知识库与上下文管理 CLI",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)

app.add_typer(index_cmd.app, name="index")
app.add_typer(search_cmd.app, name="search")
app.add_typer(collect_cmd.app, name="collect")
app.add_typer(config_cmd.app, name="config")
app.add_typer(maint_cmd.app, name="maintenance")
app.add_typer(serve_cmd.app, name="serve")


@app.callback()
def main(
    ctx: typer.Context,
    data_dir: Path | None = typer.Option(  # noqa: B008
        None,
        "--data-dir",
        envvar="GRAPHIT_KB_DATA_DIR",
        help="数据目录（默认 ~/.graphit-kb；也可通过环境变量 GRAPHIT_KB_DATA_DIR 注入）",
        show_default=False,
    ),
) -> None:
    """全局选项：``--data-dir`` 被各子命令继承。"""
    ctx.obj = {"data_dir": resolve_data_dir(data_dir)}


@app.command("status")
def status_cmd(ctx: typer.Context) -> None:
    """库状态总览（M1 仅展示基础设施统计；M2 起增加处理进度等）。"""
    from rich.console import Console
    from rich.table import Table

    data_dir: Path = ctx.obj["data_dir"]
    registry = Registry(data_dir / "registry.sqlite")
    try:
        registry.initialize()
    except Exception as e:  # pragma: no cover - defensive
        Console(stderr=True).print(f"[red]无法初始化注册库[/red] {e}")
        raise typer.Exit(code=2) from None

    reset = reset_stale_running(registry)

    table = Table(title=f"GraphIt-KB 状态 ({data_dir})", show_lines=False)
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")
    table.add_row("版本", __version__)
    table.add_row("数据目录", str(data_dir))
    table.add_row("任务总数", str(count_tasks(registry)))
    table.add_row("  · pending", str(count_tasks(registry, status="pending")))
    table.add_row("  · running", str(count_tasks(registry, status="running")))
    table.add_row("  · done", str(count_tasks(registry, status="done")))
    table.add_row("  · failed", str(count_tasks(registry, status="failed")))
    if reset:
        table.add_row("[yellow]崩溃恢复[/yellow]", f"重置 {reset} 个超时任务")
    Console().print(table)


__all__ = ["app"]


if __name__ == "__main__":  # pragma: no cover
    app()
