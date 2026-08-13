"""SHA-256 + mtime fingerprint helpers.

设计依据：05 §2.1 (files.sha256 / files.mtime) + 04 §2.1 (FR-4.1)。
SHA-256 是内容指纹的唯一权威（碰撞概率可忽略）；mtime 用于快速比对
"是否可能变化"（SHA 比对是真相，mtime 只是缓存命中优化）。

实现说明：
- ``fingerprint(path)`` 返回 ``(sha256, mtime_ns)``；mtime 用纳秒精度，
  避免秒级精度的回写/克隆造成假命中。
- ``sha256_only(path)`` 用于回填场景（已有文件、无缓存）。
- 一切 IO 失败抛 :class:`FingerprintError`；CLI 层负责捕获并打
  ``extract_status=failed``（M2 落地）。
"""

from __future__ import annotations

import hashlib
from pathlib import Path

CHUNK_SIZE = 1 << 16  # 64 KiB — 经验值，对大 PDF 友好


class FingerprintError(OSError):
    """Raised when a file cannot be fingerprinted."""


def sha256_of(path: Path) -> str:
    """Compute the SHA-256 hex digest of ``path``."""
    p = Path(path).expanduser()
    if not p.is_file():
        raise FingerprintError(f"不是文件或不存在：{p}")
    h = hashlib.sha256()
    try:
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                h.update(chunk)
    except OSError as e:
        raise FingerprintError(f"读取失败：{p} ({e})") from e
    return h.hexdigest()


def mtime_ns(path: Path) -> int:
    """Return ``st_mtime_ns`` for ``path``; 0 if the file is missing."""
    p = Path(path).expanduser()
    try:
        return p.stat().st_mtime_ns
    except FileNotFoundError:
        return 0


def fingerprint(path: Path) -> tuple[str, int]:
    """Compute ``(sha256, mtime_ns)`` for ``path``.

    Both values are needed by the registry: ``sha256`` is the dedupe key
    and the stale-detection source of truth; ``mtime`` is a cheap hint
    used by the scan loop to skip unchanged files (M2).
    """
    return sha256_of(path), mtime_ns(path)


def sha256_text(text: str, *, encoding: str = "utf-8") -> str:
    """SHA-256 of a *string*. Used for ``cache/extracted/<sha256>.json`` lookups."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


__all__ = [
    "CHUNK_SIZE",
    "FingerprintError",
    "fingerprint",
    "mtime_ns",
    "sha256_of",
    "sha256_text",
]
