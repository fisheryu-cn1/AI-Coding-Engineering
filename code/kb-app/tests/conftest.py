"""Shared fixtures.

Two key fixtures:

- ``data_dir``  — fresh temp data directory; resolves to ``DataPaths`` and
  creates the layout so tests can drop files in.
- ``registry``  — initialized SQLite registry (DDL applied) inside that
  data_dir.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from kbapp.core.config import Config
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Empty data directory with the standard layout created."""
    d = tmp_path / "graphit-kb"
    d.mkdir()
    DataPaths.from_data_dir(d).ensure_dirs()
    return d


@pytest.fixture
def paths(data_dir: Path) -> DataPaths:
    return DataPaths.from_data_dir(data_dir)


@pytest.fixture
def registry(paths: DataPaths) -> Iterator[Registry]:
    reg = Registry(paths.registry_db)
    reg.initialize()
    yield reg


@pytest.fixture
def default_config() -> Config:
    return Config.defaults()


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    """A small text file with deterministic content."""
    p = tmp_path / "sample.txt"
    p.write_text("GraphIt-KB test fixture content.\n" * 8, encoding="utf-8")
    return p
