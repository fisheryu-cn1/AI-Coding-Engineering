"""Unit tests for :mod:`kbapp.core.lock` (S7).

Covers:
- Basic acquire / release happy path
- Concurrent acquire returns None when ``wait=False``
- ``wait=True`` blocks then succeeds once the lock is released
- Stale PID (process does not exist) → reclaim
- Stale mtime (file untouched too long) → reclaim
- Corrupt lock file (no PID) → reclaim
- ``force_release`` always removes the lock
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

from kbapp.core.lock import (
    LockHeld,
    acquire_write_lock,
    force_release,
    lock_holder,
    release_write_lock,
)


def _make_lock(data_dir: Path, *, wait: bool = False):
    lock = acquire_write_lock(data_dir, wait=wait)
    assert lock is not None
    return lock


def test_acquire_release_roundtrip(data_dir: Path) -> None:
    lock = _make_lock(data_dir)
    assert lock.path.exists()
    release_write_lock(lock)
    assert not lock.path.exists()


def test_second_acquire_returns_none_when_held(data_dir: Path) -> None:
    a = _make_lock(data_dir)
    try:
        b = acquire_write_lock(data_dir, wait=False)
        assert b is None
    finally:
        release_write_lock(a)


def test_lock_holder_returns_current_pid(data_dir: Path) -> None:
    a = _make_lock(data_dir)
    try:
        assert lock_holder(data_dir) == os.getpid()
    finally:
        release_write_lock(a)


def test_lock_holder_none_when_no_lock(data_dir: Path) -> None:
    assert lock_holder(data_dir) is None


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="lock 模块声明 POSIX-only（lock.py docstring），Windows 死 PID 探测失效",
)
def test_stale_pid_is_reclaimed(data_dir: Path) -> None:
    """A lock file pointing at a dead PID should be reaped on next acquire.

    用 PID 99_999_999 作"确定不存在"哨兵——Linux 默认 ``/proc/sys/kernel/pid_max``
    默认 4194304（部分发行版 32768 ~ 2^22），99_999_999 远超上限；macOS 默认
    99999。若未来该 PID 撞上容器/嵌入式系统上的真 PID，理论上本测试会偶发
    失败——届时改用 ``os.fork`` + 子进程退出 + ``waitpid`` 制造确定死 PID。
    """
    lock_path = data_dir / ".write.lock"
    lock_path.write_text("99999999\n", encoding="utf-8")  # likely-dead PID

    lock = acquire_write_lock(data_dir, wait=False)
    assert lock is not None
    assert lock_holder(data_dir) == os.getpid()
    release_write_lock(lock)


def test_stale_mtime_is_reclaimed(data_dir: Path) -> None:
    """A lock file with a live PID but old mtime → reclaimed."""
    lock_path = data_dir / ".write.lock"
    lock_path.write_text(f"{os.getpid()}\n", encoding="utf-8")
    # Backdate the file so the staleness check triggers
    old = time.time() - 7200  # 2h ago
    os.utime(lock_path, (old, old))

    lock = acquire_write_lock(data_dir, wait=False, stale_after=60.0)
    assert lock is not None
    release_write_lock(lock)


def test_corrupt_lock_file_is_reclaimed(data_dir: Path) -> None:
    """A lock file with no parseable PID is treated as stale."""
    lock_path = data_dir / ".write.lock"
    lock_path.write_text("not-a-pid\n", encoding="utf-8")

    lock = acquire_write_lock(data_dir, wait=False)
    assert lock is not None
    release_write_lock(lock)


def test_wait_mode_blocks_until_released(data_dir: Path) -> None:
    a = _make_lock(data_dir)
    try:
        # Schedule release in a moment; wait mode should pick it up.
        import threading

        def releaser() -> None:
            time.sleep(0.2)
            release_write_lock(a)

        t = threading.Thread(target=releaser)
        t.start()
        b = acquire_write_lock(data_dir, wait=True, timeout=5.0)
        assert b is not None
        release_write_lock(b)
        t.join()
    finally:
        # Best-effort: a was released inside the thread; if the assertion
        # above failed, ensure we don't leak.
        try:
            release_write_lock(a)
        except Exception:
            pass


def test_wait_mode_raises_lock_held_on_timeout(data_dir: Path) -> None:
    a = _make_lock(data_dir)
    try:
        with pytest.raises(LockHeld):
            acquire_write_lock(data_dir, wait=True, timeout=0.3)
    finally:
        release_write_lock(a)


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="lock 模块声明 POSIX-only（lock.py docstring）：Windows 不允许 unlink 被占用的文件",
)
def test_force_release_removes_lock_even_when_held(data_dir: Path) -> None:
    a = _make_lock(data_dir)
    assert force_release(data_dir) is True
    assert not a.path.exists()
    # fd is closed; nothing more to do.
    try:
        os.close(a.fd)
    except OSError:
        pass


def test_force_release_returns_false_when_absent(data_dir: Path) -> None:
    assert force_release(data_dir) is False
