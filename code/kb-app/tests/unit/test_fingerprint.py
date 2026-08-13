"""Unit tests for :mod:`kbapp.core.fingerprint`."""

from __future__ import annotations

from pathlib import Path

import pytest

from kbapp.core.fingerprint import (
    FingerprintError,
    fingerprint,
    mtime_ns,
    sha256_of,
    sha256_text,
)


def test_sha256_of_known_content(sample_file: Path) -> None:
    """Same content → same digest."""
    assert sha256_of(sample_file) == sha256_of(sample_file)
    assert len(sha256_of(sample_file)) == 64


def test_sha256_of_changes_when_content_changes(sample_file: Path, tmp_path: Path) -> None:
    other = tmp_path / "other.txt"
    other.write_text("different content", encoding="utf-8")
    assert sha256_of(sample_file) != sha256_of(other)


def test_sha256_of_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FingerprintError):
        sha256_of(tmp_path / "nope.txt")


def test_sha256_of_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FingerprintError):
        sha256_of(tmp_path)


def test_mtime_ns_present(sample_file: Path) -> None:
    assert mtime_ns(sample_file) > 0


def test_mtime_ns_missing_returns_zero(tmp_path: Path) -> None:
    assert mtime_ns(tmp_path / "nope.txt") == 0


def test_fingerprint_returns_pair(sample_file: Path) -> None:
    sha, mt = fingerprint(sample_file)
    assert sha == sha256_of(sample_file)
    assert mt == mtime_ns(sample_file)


def test_sha256_text_matches_hashlib() -> None:
    text = "GraphIt-KB 中文测试" * 5
    assert sha256_text(text) == sha256_text(text)
    assert len(sha256_text(text)) == 64
