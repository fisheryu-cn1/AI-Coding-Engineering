"""``kb init`` — idempotent data-directory bootstrap (09 §11).

行为（09 §11）：

1. :meth:`DataPaths.ensure_dirs` 建目录树（含 ``cache/extracted/`` 等）；
2. ``config.yaml`` 不存在 → 写默认值（含 §9 新参数）；存在则跳过并提示相对默认
   值的 diff；``--force`` 强制重写（已登记 09 §11）；
3. ``sources.yaml`` 不存在 → 写注释占位模板；存在则跳过；
4. 初始化 registry（DDL + ``SCHEMA_VERSION=2``）并从 ``config.core_topics``
   播种 ``topics`` 表（§7.2）；
5. 环境校验：Python ≥ 3.11；数据目录所在盘剩余 ≥ 2GB；Tesseract 缺失仅警告
   （OCR 默认关闭，§1）；
6. **不下载模型**（bge-m3 下载引导随 M3，05 §11.6）；
7. 输出下一步指引（编辑 ``config.yaml`` → ``kb index scan`` → ``kb index run``）。

幂等性要求：跑两遍无副作用；不覆盖任何既有文件（仅播种缺的 topic）。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console

from kbapp.core.config import ConfigError, diff_defaults, dump_config, load_config, merge_defaults
from kbapp.core.paths import SOURCES_FILE, DataPaths
from kbapp.core.registry import Registry, seed_topics

console = Console()
err_console = Console(stderr=True)

# Minimum free disk space in bytes (09 §11: ≥ 2GB recommended).
_MIN_FREE_BYTES = 2 * 1024 * 1024 * 1024


def init_cmd(
    ctx: typer.Context,
    force: bool = typer.Option(  # noqa: B008
        False,
        "--force",
        help="即便 config.yaml 已存在也重写（仍不覆盖 sources.yaml 之外的注释模板）",
    ),
) -> None:
    """幂等初始化数据目录：建目录、写默认配置、初始化 registry、播种 topics。"""
    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)

    # 1. Directory tree (idempotent: mkdir -p).
    paths.ensure_dirs()

    # 5. Environment check (early — surface failures before doing work).
    _check_python_version()
    free_bytes = _check_free_disk(paths.data_dir)
    tesseract_ok = _check_tesseract()

    # 2. config.yaml — write defaults if missing.
    config_existed = paths.config_path.exists()
    if not config_existed or force:
        cfg = load_config(None)  # defaults only
        try:
            dump_config(cfg, paths.config_path)
        except OSError as e:
            err_console.print(f"[red]无法写入 config.yaml[/red] {e}")
            raise typer.Exit(code=2) from None
        action = "重写" if force and config_existed else "写入"
        console.print(f"[green]{action}默认配置[/green] {paths.config_path}")
    else:
        console.print("[dim]config.yaml 已存在[/dim] [跳过]")
        # Re-load user config to seed topics from their list.
        cfg = load_config(paths.config_path)
        _print_config_diff(cfg)

    # 3. sources.yaml — write a placeholder if missing.
    if not paths.sources_path.exists():
        _write_sources_template(paths.sources_path)
        console.print(f"[green]写入来源模板[/green] {paths.sources_path}")
    else:
        console.print("[dim]sources.yaml 已存在[/dim] [跳过]")

    # 4. Initialize registry + seed topics.
    registry = Registry(paths.registry_db)
    try:
        registry.initialize()
    except Exception as e:  # pragma: no cover - defensive
        err_console.print(f"[red]无法初始化注册库[/red] {e}")
        raise typer.Exit(code=2) from None

    topics = list(cfg.raw.get("core_topics") or [])
    inserted = 0
    if topics:
        with registry.transaction() as conn:
            inserted = seed_topics(conn, topics)
    if inserted:
        console.print(f"[green]播种 {inserted} 个主题[/green]（{len(topics) - inserted} 已存在）")
    else:
        console.print(f"[dim]topics 已就绪[/dim]（{len(topics)} 个）")

    # Final summary + next steps.
    schema_version = registry.schema_version()
    _print_summary(
        data_dir=paths.data_dir,
        free_bytes=free_bytes,
        tesseract_ok=tesseract_ok,
        schema_version=schema_version,
        topics_total=len(topics),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_python_version() -> None:
    """Python ≥ 3.11（设计 02 §1）。"""
    if sys.version_info < (3, 11):  # noqa: UP036
        err_console.print(f"[red]Python 版本过低[/red] 当前 {sys.version.split()[0]}，需要 ≥ 3.11")
        raise typer.Exit(code=2)


def _check_free_disk(data_dir: Path) -> int:
    """剩余空间 ≥ 2GB；不足仅警告（M2 不阻塞，doc_count 小于 2GB 暂时够用）。"""
    try:
        usage = shutil.disk_usage(data_dir)
    except OSError as e:
        err_console.print(f"[yellow]无法获取磁盘使用[/yellow] {e}")
        return 0
    if usage.free < _MIN_FREE_BYTES:
        err_console.print(
            f"[yellow]磁盘空间不足[/yellow] {data_dir} 仅剩 "
            f"{usage.free / (1024**3):.1f} GB（建议 ≥ 2 GB）"
        )
    return usage.free


def _check_tesseract() -> bool:
    """Tesseract 仅 OCR 用；M2 默认关闭，缺失仅警告（09 §1）。"""
    ok = shutil.which("tesseract") is not None
    if not ok:
        err_console.print(
            "[yellow]未检测到 tesseract[/yellow]（OCR 默认关闭，不影响 M2；如需 PDF OCR 请"
            "安装并设置 parse.ocr_enabled=true）"
        )
    return ok


def _print_config_diff(cfg) -> None:
    """Print the user's config changes vs defaults (09 §11「跳过并提示 diff」)."""
    from kbapp.core.config import _MISSING

    diffs = diff_defaults(cfg)
    if not diffs:
        console.print("[dim]  （与默认值一致，无改动）[/dim]")
        return
    console.print("[dim]  （相对默认值的改动：）[/dim]")
    for key in sorted(diffs):
        default, current = diffs[key]
        d = "<missing>" if default is _MISSING else repr(default)
        c = "<missing>" if current is _MISSING else repr(current)
        console.print(f"    [dim]{key}:[/dim] {d} → {c}")


def _write_sources_template(path: Path) -> None:
    """``sources.yaml`` 注释模板（P2 收集来源占位；M2 写一次即可）。"""
    template = """# GraphIt-KB 自动收集来源清单（M7 起生效）
#
# 每个 source 是一个抓取入口（M2 仅作占位登记）：
#   - name      内部标识
#   - kind      arxiv | rss | web | local_dir
#   - url / path 抓取入口
#   - cadence   抓取频次（cron 表达式）
#   - topic     默认主题（缺省走分类推断）
#
# sources:
#   - name: arxiv-context-engineering
#     kind: arxiv
#     url: https://export.arxiv.org/rss/cs.CL
#     cadence: "0 9 * * *"
#     topic: ContextEngineering
"""
    try:
        path.write_text(template, encoding="utf-8")
    except OSError as e:
        err_console.print(f"[yellow]无法写入 sources.yaml[/yellow] {e}")


def _print_summary(
    *,
    data_dir: Path,
    free_bytes: int,
    tesseract_ok: bool,
    schema_version: int,
    topics_total: int,
) -> None:
    console.print()
    console.print(f"[bold]GraphIt-KB 初始化完成[/bold] [dim]({data_dir})[/dim]")
    console.print(f"  • SCHEMA_VERSION = {schema_version}")
    console.print(f"  • topics 数 = {topics_total}")
    if free_bytes:
        console.print(f"  • 可用空间 = {free_bytes / (1024**3):.1f} GB")
    console.print(f"  • Tesseract = {'OK' if tesseract_ok else '缺失（仅警告）'}")
    console.print()
    console.print("[bold]下一步[/bold]")
    console.print("  1. 编辑 config.yaml（配置 corpus_roots、llm 等）")
    console.print("  2. [code]kb index scan[/code]  扫描资料目录")
    console.print("  3. [code]kb index run[/code]   执行流水线")


__all__ = ["init_cmd", "app"]


# Register as a top-level command (not a sub-group) so ``kb init`` works
# directly. ``kbapp.cli.main`` imports ``app`` and registers it via
# ``app.command("init")(init_cmd)``.
app = typer.Typer(help="GraphIt-KB CLI", add_completion=False)


# Re-export to silence unused-import warnings on ConfigError / merge_defaults.
_ = ConfigError
_ = merge_defaults
_ = SOURCES_FILE
