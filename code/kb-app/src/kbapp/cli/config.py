"""``kb config ...`` subcommand group.

M1 唯一完整实现的子命令：

- ``show``   —— 打印当前配置（含默认值）
- ``get``    —— 按点路径读
- ``set``    —— 按点路径写（带 audit；写锁）
- ``diff``   —— 与默认值对比，标出用户改动

退出码（设计 05 §9 + 04 §2.2）：

- ``0`` —— 成功
- ``1`` —— 配置校验失败（键不存在、类型不匹配）
- ``2`` —— 锁冲突 / 其他 IO 错误

数据目录来源：父命令 ``main`` 的 callback 把 ``--data-dir`` 解析后写入
``ctx.obj["data_dir"]``；本模块的子命令从 ``ctx.obj`` 取。这样保证全局
``--data-dir`` 选项只声明一次（typer 不会向子命令自动转发父 callback 的
选项值）。
"""

from __future__ import annotations

import typer
import yaml
from rich.console import Console
from rich.table import Table

from kbapp.cli._common import YesOpt
from kbapp.core.config import (
    Config,
    ConfigError,
    diff_defaults,
    dump_config,
    get_value,
    load_config,
    set_value,
)
from kbapp.core.lock import LockError, acquire_write_lock, release_write_lock
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry, config_audit

app = typer.Typer(help="查看 / 修改配置（含默认值对比与审计）", no_args_is_help=True)

console = Console()
err_console = Console(stderr=True)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


@app.command("show")
def show_cmd(
    ctx: typer.Context,
    defaults: bool = typer.Option(
        False, "--defaults", help="仅显示默认配置，忽略用户配置"
    ),
) -> None:
    """打印当前生效配置（含默认值合并结果）。"""
    paths = DataPaths.from_data_dir(ctx.obj["data_dir"])
    cfg = Config.defaults() if defaults else load_config(paths.config_path)
    text = yaml.safe_dump(
        cfg.raw,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    console.print(text.rstrip())


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


@app.command("get")
def get_cmd(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="点路径，如 scoring.thresholds.accept"),
) -> None:
    """按点路径读单个值。"""
    paths = DataPaths.from_data_dir(ctx.obj["data_dir"])
    cfg = load_config(paths.config_path)
    try:
        value = get_value(cfg, key)
    except ConfigError as e:
        err_console.print(f"[red]错误[/red] {e}")
        raise typer.Exit(code=1) from None

    # Render bools / ints / floats as plain literals, otherwise yaml-quote
    if isinstance(value, bool):
        console.print("true" if value else "false")
    elif isinstance(value, (int, float)):
        console.print(repr(value))
    else:
        console.print(yaml.safe_dump(value, allow_unicode=True).rstrip())


# ---------------------------------------------------------------------------
# set
# ---------------------------------------------------------------------------


@app.command("set")
def set_cmd(
    ctx: typer.Context,
    key: str = typer.Argument(..., help="点路径，如 scoring.thresholds.accept"),
    value: str = typer.Argument(..., help="新值（按现有类型自动转换）"),
    yes: bool = YesOpt,
) -> None:
    """按点路径写单个值；写 config_audit 表。

    取写锁 → 读旧值 → 校验/转换 → 写 yaml（原子）+ 写 audit → 释放锁。
    """
    paths = DataPaths.from_data_dir(ctx.obj["data_dir"])

    if not yes:
        err_console.print(
            f"[yellow]将修改[/yellow] {key}（当前值由 kb config get {key} 查看）"
        )
        if not typer.confirm("确认?", default=False):
            raise typer.Abort()

    lock = None
    try:
        lock = acquire_write_lock(paths.data_dir, wait=False)
        if lock is None:
            err_console.print("[red]写锁被占用[/red]，稍后重试")
            raise typer.Exit(code=2)

        # Initialize registry first so we can audit
        paths.ensure_dirs()
        registry = Registry(paths.registry_db)
        registry.initialize()

        cfg = load_config(paths.config_path)
        try:
            old, new = set_value(cfg, key, value)
        except ConfigError as e:
            err_console.print(f"[red]错误[/red] {e}")
            raise typer.Exit(code=1) from None

        dump_config(cfg, paths.config_path)
        with registry.transaction() as conn:
            config_audit(
                conn,
                key=key,
                old_value=old,
                new_value=new,
                source="cli",
            )

        console.print(f"[green]已更新[/green] {key}: {old!r} → {new!r}")
    except LockError as e:
        err_console.print(f"[red]锁错误[/red] {e}")
        raise typer.Exit(code=2) from None
    finally:
        if lock is not None:
            release_write_lock(lock)


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------


@app.command("diff")
def diff_cmd(ctx: typer.Context) -> None:
    """显示用户配置相对默认值的差异。"""
    paths = DataPaths.from_data_dir(ctx.obj["data_dir"])
    cfg = load_config(paths.config_path)
    diffs = diff_defaults(cfg)

    if not diffs:
        console.print("[dim]当前配置与默认值一致，无修改项。[/dim]")
        return

    table = Table(title="用户配置 vs 默认值", show_lines=False)
    table.add_column("配置键", style="cyan", no_wrap=True)
    table.add_column("默认值", style="yellow")
    table.add_column("当前值", style="green")

    for k in sorted(diffs):
        old, new = diffs[k]
        table.add_row(k, _render(old), _render(new))

    console.print(table)


def _render(value: object) -> str:
    if value is None:
        return "<missing>"
    if isinstance(value, str):
        return value
    return repr(value)


__all__ = ["app"]
