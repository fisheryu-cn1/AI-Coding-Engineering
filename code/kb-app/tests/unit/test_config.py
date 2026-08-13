"""Unit tests for :mod:`kbapp.core.config`."""

from __future__ import annotations

from pathlib import Path

import pytest

from kbapp.core.config import (
    Config,
    ConfigError,
    diff_defaults,
    dump_config,
    get_value,
    load_config,
    merge_defaults,
    set_value,
)


def test_defaults_is_deep_copy_safe() -> None:
    """Mutating a defaults() Config must not mutate the module-level DEFAULTS."""
    cfg = Config.defaults()
    cfg.raw["llm"]["provider"] = "mutated"
    # Reload and confirm
    fresh = Config.defaults()
    assert fresh.raw["llm"]["provider"] == "deepseek"


def test_load_config_returns_defaults_when_path_is_none() -> None:
    cfg = load_config(None)
    assert cfg.raw["llm"]["model"] == "deepseek-chat"


def test_load_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "does-not-exist.yaml")
    assert cfg.raw["scoring"]["thresholds"]["accept"] == 0.70


def test_load_config_merges_user_over_defaults(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    p.write_text(
        "scoring:\n  thresholds:\n    accept: 0.55\n", encoding="utf-8"
    )
    cfg = load_config(p)
    assert cfg.raw["scoring"]["thresholds"]["accept"] == 0.55
    # Defaults preserved for non-overridden leaves
    assert cfg.raw["scoring"]["thresholds"]["reject"] == 0.50
    assert cfg.raw["llm"]["model"] == "deepseek-chat"


def test_load_config_raises_on_garbage(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    p.write_text(": not a mapping at top\n[1, 2]\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(p)


def test_dump_config_is_atomic(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    cfg = Config.defaults()
    cfg.raw["llm"]["model"] = "gpt-test"
    dump_config(cfg, p)
    assert p.exists()
    # No leftover temp file
    leftovers = list(tmp_path.glob(".config.yaml.*.tmp"))
    assert not leftovers


def test_dump_then_load_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "config.yaml"
    cfg = Config.defaults()
    cfg.raw["scoring"]["thresholds"]["accept"] = 0.42
    dump_config(cfg, p)
    reloaded = load_config(p)
    assert reloaded.raw["scoring"]["thresholds"]["accept"] == 0.42


def test_get_value_returns_scalar() -> None:
    cfg = Config.defaults()
    assert get_value(cfg, "llm.model") == "deepseek-chat"
    assert get_value(cfg, "scoring.thresholds.accept") == 0.70


def test_get_value_missing_raises() -> None:
    cfg = Config.defaults()
    with pytest.raises(ConfigError):
        get_value(cfg, "no.such.key")


def test_set_value_returns_old_new_pair() -> None:
    cfg = Config.defaults()
    old, new = set_value(cfg, "scoring.thresholds.accept", "0.42")
    assert old == 0.70
    assert new == 0.42
    assert cfg.raw["scoring"]["thresholds"]["accept"] == 0.42


def test_set_value_coerces_bool() -> None:
    cfg = Config.defaults()
    cfg.raw["mcp"]["enable_write_tools"] = False
    old, new = set_value(cfg, "mcp.enable_write_tools", "true")
    assert old is False
    assert new is True


def test_set_value_coerces_int() -> None:
    cfg = Config.defaults()
    cfg.raw["retrieve"]["default_limit"] = 10
    old, new = set_value(cfg, "retrieve.default_limit", "42")
    assert old == 10
    assert new == 42


def test_set_value_coerces_float() -> None:
    cfg = Config.defaults()
    old, new = set_value(cfg, "parse.pdf_fast_min_coverage", "0.9")
    assert old == 0.85
    assert new == 0.9


def test_set_value_int_field_rejects_float_string() -> None:
    """Int fields reject float-shaped strings (type safety)."""
    cfg = Config.defaults()
    with pytest.raises(ConfigError):
        set_value(cfg, "retrieve.rrf_k", "12.5")


def test_set_value_missing_leaf_raises() -> None:
    cfg = Config.defaults()
    with pytest.raises(ConfigError):
        set_value(cfg, "no.such.key", "x")


def test_set_value_intermediate_not_dict_raises() -> None:
    cfg = Config.defaults()
    with pytest.raises(ConfigError):
        # ``llm.model`` is a string, so traversing past it must fail
        set_value(cfg, "llm.model.nope", "x")


def test_set_value_rejects_non_bool_for_bool() -> None:
    cfg = Config.defaults()
    cfg.raw["mcp"]["enable_write_tools"] = False
    with pytest.raises(ConfigError):
        set_value(cfg, "mcp.enable_write_tools", "notabool")


def test_diff_defaults_empty_when_no_overrides() -> None:
    cfg = Config.defaults()
    assert diff_defaults(cfg) == {}


def test_diff_defaults_lists_changed_leaves() -> None:
    cfg = Config.defaults()
    cfg.raw["scoring"]["thresholds"]["accept"] = 0.65
    cfg.raw["llm"]["model"] = "gpt-x"
    diffs = diff_defaults(cfg)
    assert diffs["scoring.thresholds.accept"] == (0.70, 0.65)
    assert diffs["llm.model"] == ("deepseek-chat", "gpt-x")


def test_merge_defaults_does_not_mutate_DEFAULTS() -> None:
    user = {"scoring": {"thresholds": {"accept": 0.1}}}
    merged = merge_defaults(user)
    assert merged["scoring"]["thresholds"]["accept"] == 0.1
    # Reload defaults and verify untouched
    fresh = Config.defaults()
    assert fresh.raw["scoring"]["thresholds"]["accept"] == 0.70
