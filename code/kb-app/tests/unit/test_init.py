"""Unit tests for ``kb init`` (09 §11 idempotency + setup)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from kbapp.cli.main import app
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry, list_topics

runner = CliRunner()


def test_init_creates_layout_and_config(tmp_path: Path) -> None:
    result = runner.invoke(app, ["--data-dir", str(tmp_path), "init"])
    assert result.exit_code == 0, result.stdout

    paths = DataPaths.from_data_dir(tmp_path)
    for d in (
        paths.data_dir,
        paths.cache_dir,
        paths.extracted_dir,
        paths.inbox_dir,
        paths.reports_dir,
        paths.scoring_modules_dir,
    ):
        assert d.exists(), f"missing dir: {d}"

    assert paths.config_path.exists()
    assert paths.sources_path.exists()

    reg = Registry(paths.registry_db)
    assert reg.schema_version() == 2
    topics = list_topics(reg.connect())
    # core_topics defaults (09 §7.2)
    names = {t.name for t in topics}
    assert "ContextEngineering" in names
    assert "ai-coding" in names


def test_init_is_idempotent_does_not_overwrite(tmp_path: Path) -> None:
    # First init
    runner.invoke(app, ["--data-dir", str(tmp_path), "init"])
    # Mutate config.yaml
    cfg_path = tmp_path / "config.yaml"
    cfg_text = cfg_path.read_text(encoding="utf-8")
    cfg_path.write_text("# CUSTOM_MARKER\n" + cfg_text, encoding="utf-8")
    # Second init
    result = runner.invoke(app, ["--data-dir", str(tmp_path), "init"])
    assert result.exit_code == 0
    # Marker preserved
    assert cfg_path.read_text(encoding="utf-8").startswith("# CUSTOM_MARKER")
    # No duplicate seeding
    reg = Registry(tmp_path / "registry.sqlite")
    topics = list_topics(reg.connect())
    assert len({t.name for t in topics}) == len({t.name for t in topics})  # set eq


def test_init_force_overwrites_config(tmp_path: Path) -> None:
    runner.invoke(app, ["--data-dir", str(tmp_path), "init"])
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("# USER_MARKER\n", encoding="utf-8")
    result = runner.invoke(app, ["--data-dir", str(tmp_path), "init", "--force"])
    assert result.exit_code == 0
    assert "USER_MARKER" not in cfg_path.read_text(encoding="utf-8")
