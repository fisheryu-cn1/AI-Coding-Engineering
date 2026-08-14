"""``kb`` 入口。组装所有子命令并定义全局选项。"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

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
    serve as serve_cmd,
)
from kbapp.cli._common import resolve_data_dir
from kbapp.cli.init import init_cmd
from kbapp.cli.search import (
    compare_cmd,
    read_cmd,
    related_cmd,
    search_cmd,
    show_cmd,
    topics_cmd,
)
from kbapp.core.registry import (
    Registry,
    count_chunks,
    count_files_by_extract_status,
    count_files_by_status,
    list_files_needing_confirm,
    list_topics,
)
from kbapp.core.task import count_tasks, reset_stale_running

app = typer.Typer(
    name="kb",
    help="GraphIt-KB 本地知识库与上下文管理 CLI",
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode="rich",
)

app.add_typer(index_cmd.app, name="index")
app.add_typer(collect_cmd.app, name="collect")
app.add_typer(config_cmd.app, name="config")
app.add_typer(maint_cmd.app, name="maintenance")
app.add_typer(serve_cmd.app, name="serve")
app.command("init")(init_cmd)
# 检索六命令顶层化（11 §6.1，对齐 04 §2.1；M2 的 `kb search` 占位子组已移除）。
app.command("search")(search_cmd)
app.command("show")(show_cmd)
app.command("read")(read_cmd)
app.command("related")(related_cmd)
app.command("compare")(compare_cmd)
app.command("topics")(topics_cmd)


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
    """库状态总览（M2：files 分状态 + topics + needs_confirm + FTS）。"""
    data_dir: Path = ctx.obj["data_dir"]
    registry = Registry(data_dir / "registry.sqlite")
    try:
        registry.initialize()
    except Exception as e:  # pragma: no cover - defensive
        Console(stderr=True).print(f"[red]无法初始化注册库[/red] {e}")
        raise typer.Exit(code=2) from None

    reset = reset_stale_running(registry)
    with registry.read_only() as conn:
        by_status = count_files_by_status(conn)
        by_extract = count_files_by_extract_status(conn)
        chunks = count_chunks(conn)
        topics = list_topics(conn)
        needs_confirm = list_files_needing_confirm(conn, limit=20)

    # ----- Top: overview table ------------------------------------------
    overview = Table(title=f"GraphIt-KB 状态 ({data_dir})", show_lines=False)
    overview.add_column("指标", style="cyan")
    overview.add_column("值", style="green")
    overview.add_row("版本", __version__)
    overview.add_row("数据目录", str(data_dir))
    overview.add_row("SCHEMA_VERSION", str(registry.schema_version()))
    overview.add_row("任务 pending", str(count_tasks(registry, status="pending")))
    overview.add_row("任务 running", str(count_tasks(registry, status="running")))
    overview.add_row("任务 done", str(count_tasks(registry, status="done")))
    overview.add_row("任务 failed", str(count_tasks(registry, status="failed")))
    overview.add_row("FTS chunk 总数", str(chunks))
    if reset:
        overview.add_row("[yellow]崩溃恢复[/yellow]", f"重置 {reset} 个超时任务")
    Console().print(overview)

    # ----- Files by status ----------------------------------------------
    if by_status or by_extract:
        files_table = Table(title="files 分状态", show_lines=False)
        files_table.add_column("status", style="cyan")
        files_table.add_column("n", style="green")
        for k in ("new", "active", "needs_confirm", "duplicate", "deleted"):
            files_table.add_row(k, str(by_status.get(k, 0)))
        Console().print(files_table)

        ext_table = Table(title="extract_status", show_lines=False)
        ext_table.add_column("extract_status", style="cyan")
        ext_table.add_column("n", style="green")
        for k in ("pending", "ok", "flat", "no_text", "failed"):
            ext_table.add_row(k, str(by_extract.get(k, 0)))
        Console().print(ext_table)

    # ----- Topics --------------------------------------------------------
    if topics:
        topic_table = Table(title="topics", show_lines=False)
        topic_table.add_column("name", style="cyan", no_wrap=True)
        topic_table.add_column("doc_count", style="green")
        topic_table.add_column("description", style="dim")
        for t in topics:
            topic_table.add_row(t.name, str(t.doc_count), t.description or "")
        Console().print(topic_table)

    # ----- needs_confirm queue -------------------------------------------
    if needs_confirm:
        nc_table = Table(title="needs_confirm 待确认", show_lines=False)
        nc_table.add_column("doc_id", style="cyan", no_wrap=True)
        nc_table.add_column("path", style="green")
        nc_table.add_column("corpus", style="yellow")
        nc_table.add_column("extract_status", style="red")
        for r in needs_confirm:
            nc_table.add_row(r.doc_id, r.path, r.corpus, r.extract_status)
        Console().print(nc_table)
        console = Console()
        console.print(
            "[dim]用 [code]kb index set-topic Dxxxx TopicName[/code] 改判；"
            "或 [code]kb index set-topic Dxxxx -[/code] 留待人工[/dim]"
        )


__all__ = ["app"]


if __name__ == "__main__":  # pragma: no cover
    app()
