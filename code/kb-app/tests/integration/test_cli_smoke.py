"""Integration tests for the ``kb`` CLI.

These tests invoke the Typer application via ``CliRunner`` (no subprocess)
so they are fast and isolated. They cover the user-visible happy paths of
``kb config ...`` and ``kb status``.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from kbapp.cli.main import app
from kbapp.core.lock import acquire_write_lock, release_write_lock

runner = CliRunner()


def test_help_lists_all_subcommands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("index", "search", "collect", "config", "maintenance", "serve", "status"):
        assert cmd in result.stdout


def test_config_show_returns_defaults(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--data-dir", str(tmp_path), "config", "show"])
    assert result.exit_code == 0, result.stdout
    parsed = yaml.safe_load(result.stdout)
    assert parsed["llm"]["model"] == "deepseek-chat"
    assert parsed["scoring"]["thresholds"]["accept"] == 0.70


def test_config_set_then_get_roundtrip(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--data-dir",
            str(tmp_path),
            "config",
            "set",
            "scoring.thresholds.accept",
            "0.55",
            "--yes",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "已更新" in result.stdout

    result = runner.invoke(
        app,
        ["--data-dir", str(tmp_path), "config", "get", "scoring.thresholds.accept"],
    )
    assert result.exit_code == 0, result.stdout
    assert "0.55" in result.stdout


def test_config_get_missing_key_exits_with_code_1(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["--data-dir", str(tmp_path), "config", "get", "no.such.key"]
    )
    assert result.exit_code == 1


def test_config_set_missing_key_exits_with_code_1(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--data-dir",
            str(tmp_path),
            "config",
            "set",
            "no.such.key",
            "0.5",
            "--yes",
        ],
    )
    assert result.exit_code == 1


def test_config_diff_shows_overrides(tmp_path: Path) -> None:
    # First write an override
    runner.invoke(
        app,
        [
            "--data-dir",
            str(tmp_path),
            "config",
            "set",
            "scoring.thresholds.accept",
            "0.42",
            "--yes",
        ],
    )
    result = runner.invoke(app, ["--data-dir", str(tmp_path), "config", "diff"])
    assert result.exit_code == 0, result.stdout
    assert "scoring.thresholds.accept" in result.stdout
    assert "0.42" in result.stdout


def test_status_runs(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--data-dir", str(tmp_path), "status"])
    assert result.exit_code == 0, result.stdout
    assert "GraphIt-KB 状态" in result.stdout
    assert "任务总数" in result.stdout


def test_config_set_writes_audit_row(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "--data-dir",
            str(tmp_path),
            "config",
            "set",
            "scoring.thresholds.reject",
            "0.40",
            "--yes",
        ],
    )
    # Direct SQLite check
    import sqlite3

    db = tmp_path / "registry.sqlite"
    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute(
            "SELECT key, old_value, new_value, source FROM config_audit ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert row[0] == "scoring.thresholds.reject"
    assert row[2] == "0.4"
    assert row[3] == "cli"


def test_config_set_lock_held_exits_2(tmp_path: Path) -> None:
    """Hold the write lock manually; ``config set`` must exit 2."""
    lock = acquire_write_lock(tmp_path)
    assert lock is not None
    try:
        result = runner.invoke(
            app,
            [
                "--data-dir",
                str(tmp_path),
                "config",
                "set",
                "scoring.thresholds.accept",
                "0.99",
                "--yes",
            ],
        )
        assert result.exit_code == 2, result.stdout
        # Error message is printed to stderr; typer testing captures both
        # into ``result.output`` in newer versions.
        combined = (result.stdout or "") + (getattr(result, "stderr", "") or "")
        assert "锁" in combined or "lock" in combined.lower()
    finally:
        release_write_lock(lock)
