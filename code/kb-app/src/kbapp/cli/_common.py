"""CLI helpers shared by all subcommands."""

from __future__ import annotations

from pathlib import Path

import typer

#: Common option type for the ``--data-dir`` flag.
DataDirOpt = typer.Option(
    None,
    "--data-dir",
    envvar="GRAPHIT_KB_DATA_DIR",
    help="数据目录（默认 ~/.graphit-kb；也可通过环境变量 GRAPHIT_KB_DATA_DIR 注入）",
    show_default=False,
)

#: Common flag for skipping confirmation prompts (used by ``kb config set``).
YesOpt = typer.Option(False, "--yes", "-y", help="跳过确认提示")


def resolve_data_dir(value: Path | None) -> Path:
    """Resolve a user-supplied data dir, expanding ``~`` and creating it.

    This is the *only* place where the data directory is implicitly created
    in the CLI layer; everywhere else we treat it as already-existing.
    """
    if value is None:
        value = Path("~/.graphit-kb")
    resolved = Path(value).expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved
