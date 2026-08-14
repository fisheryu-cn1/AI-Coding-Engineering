"""CLI helpers shared by all subcommands."""

from __future__ import annotations

from pathlib import Path

import typer

#: Common flag for skipping confirmation prompts (used by ``kb config set``).
YesOpt = typer.Option(False, "--yes", "-y", help="跳过确认提示")


def resolve_data_dir(value: Path | None) -> Path:
    """Resolve a user-supplied data dir, expanding ``~``.

    Note: this is a pure path resolver — it does **not** create the
    directory. Side-effect-free so that read-only commands (``kb config
    get`` / ``kb status`` / ``kb search query`` 等) don't accidentally
    populate ``~/.graphit-kb``. Write commands that need the directory
    must call :meth:`kbapp.core.paths.DataPaths.ensure_dirs` themselves.
    """
    if value is None:
        value = Path("~/.graphit-kb")
    return Path(value).expanduser().resolve()
