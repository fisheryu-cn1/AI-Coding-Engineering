"""Unit tests for :mod:`kbapp.core.paths`."""

from __future__ import annotations

from pathlib import Path

from kbapp.core.paths import DataPaths, default_data_dir


def test_from_data_dir_resolves_relative_paths(tmp_path: Path) -> None:
    p = DataPaths.from_data_dir(tmp_path / "sub")
    assert p.data_dir == (tmp_path / "sub").resolve()
    assert p.config_path == p.data_dir / "config.yaml"
    assert p.registry_db == p.data_dir / "registry.sqlite"
    assert p.write_lock == p.data_dir / ".write.lock"


def test_ensure_dirs_creates_layout(tmp_path: Path) -> None:
    p = DataPaths.from_data_dir(tmp_path / "fresh")
    assert not p.data_dir.exists()
    p.ensure_dirs()
    assert p.data_dir.is_dir()
    assert p.graph_dir.is_dir()
    assert p.extracted_dir.is_dir()
    assert p.inbox_dir.is_dir()
    assert p.scoring_modules_dir.is_dir()
    assert p.reports_dir.is_dir()
    # Files are NOT created
    assert not p.config_path.exists()
    assert not p.registry_db.exists()


def test_default_data_dir_under_home() -> None:
    p = default_data_dir()
    assert p.is_absolute()
    assert p.name == ".graphit-kb"
