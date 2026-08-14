"""Atomic write lock (设计 05 §7.1, S7 修复).

**平台支持**：POSIX-only（Linux / macOS）。``_is_alive`` 依赖
``os.kill(pid, 0)``，Windows 下 PID 语义不同，本模块不保证可用。

S7 修复要点（评审报告 07 §S7 + 03 §6.4）：

1. ``os.open(path, O_CREAT|O_EXCL|O_WRONLY)`` —— 真正的原子获取；不依赖
   ``fcntl.flock``（跨平台不一致）也不依赖外加进程（race）。
2. 持锁进程探测失败时不能"装作没事"回收，必须：
   - 用 ``os.kill(pid, 0)`` 探测 PID 存活；
   - PID 不存在则视为崩溃，回收锁文件；
   - PID 存在但锁文件 mtime 超过阈值（默认 1 小时），同样视为死锁。
3. ``--wait`` 模式下按 100ms 步长轮询；轮询期间 PID 死了立即重新尝试。

设计取舍：
- 不依赖 ``psutil``（少依赖）；``os.kill(pid, 0)`` 在 POSIX 是
  ``ESRCH`` = 进程不存在，``EPERM`` = 进程存在但无权发信号，二者均
  视作"持锁中"（后者在单用户本机基本不会触发）。
- 锁文件内容只写 PID（行尾换行），后续可扩展为 JSON 记录持有者元数据
  （启动时间、命令名），保持向后兼容——读时按行解析首段为 int 即可。

已知限制：mtime 兜底回收后，原持有进程恢复时调用 ``release_write_lock``
会无条件 unlink，理论上可删掉新持有者的锁文件——单用户本地场景概率极
低；M2+ 若引入多用户/网络盘需改为按 PID 校验后再删。
"""

from __future__ import annotations

import errno
import os
import time
from dataclasses import dataclass
from pathlib import Path

#: Lock files older than this (seconds) are considered stale even if the
#: holding PID still appears alive (e.g. frozen process / kernel hang).
DEFAULT_STALE_AFTER_SECONDS = 3600

#: Poll interval for ``wait=True`` mode.
DEFAULT_POLL_INTERVAL_SECONDS = 0.1

#: Maximum total time to wait when ``wait=True``.
DEFAULT_WAIT_TIMEOUT_SECONDS = 30.0


class LockError(RuntimeError):
    """Base class for lock-related failures."""


class LockHeld(LockError):
    """Raised when the lock is held by another live process."""

    def __init__(self, pid: int, *, stale_after: float | None = None) -> None:
        self.pid = pid
        msg = f"写锁被进程 {pid} 持有"
        if stale_after is not None:
            msg += f"（锁文件 {stale_after:.0f}s 内未刷新）"
        super().__init__(msg)


class LockStale(LockError):
    """Internal: lock file is stale and about to be reclaimed."""


@dataclass
class Lock:
    """A held write lock. Released by :func:`release_write_lock`."""

    path: Path
    fd: int

    @property
    def pid(self) -> int:
        return os.getpid()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def acquire_write_lock(
    data_dir: Path,
    *,
    wait: bool = False,
    timeout: float = DEFAULT_WAIT_TIMEOUT_SECONDS,
    stale_after: float = DEFAULT_STALE_AFTER_SECONDS,
) -> Lock | None:
    """Acquire the write lock under ``data_dir``.

    Returns a :class:`Lock` on success, or ``None`` if ``wait=False`` and the
    lock is held. When ``wait=True``, blocks (polling) until the lock can
    be acquired or ``timeout`` seconds elapse, then raises
    :class:`LockHeld`.
    """
    lock_path = _lock_path(data_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    deadline = time.monotonic() + timeout if wait else None
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            # lock file exists — check if it's stale
            if not _is_lock_held(lock_path, stale_after=stale_after):
                # stale — try to reclaim
                _try_reclaim(lock_path)
                continue  # retry the O_EXCL acquisition
            # genuinely held
            if not wait:
                return None
            holder = _read_pid(lock_path)
            if deadline is not None and time.monotonic() >= deadline:
                raise LockHeld(holder or 0) from None
            time.sleep(DEFAULT_POLL_INTERVAL_SECONDS)
            continue

        # We won — record our PID
        payload = f"{os.getpid()}\n".encode()
        try:
            os.write(fd, payload)
            os.fsync(fd)
        except OSError:
            # extremely unlikely; release fd and bubble
            os.close(fd)
            raise
        return Lock(path=lock_path, fd=fd)


def release_write_lock(lock: Lock) -> None:
    """Release a previously acquired lock.

    Best-effort: closes the fd and unlinks the lock file. Always closes
    the fd; missing lock file at unlink time is ignored (someone else may
    have already cleaned up after a crash).
    """
    try:
        os.close(lock.fd)
    finally:
        try:
            lock.path.unlink()
        except FileNotFoundError:
            pass


def force_release(data_dir: Path) -> bool:
    """Forcibly remove the lock file regardless of holder.

    Used by ``kb status`` / recovery utilities. Returns ``True`` if a lock
    was actually removed.
    """
    lock_path = _lock_path(data_dir)
    try:
        lock_path.unlink()
        return True
    except FileNotFoundError:
        return False


def lock_holder(data_dir: Path) -> int | None:
    """Return the PID currently recorded in the lock file (or None)."""
    lock_path = _lock_path(data_dir)
    return _read_pid(lock_path) if lock_path.exists() else None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _lock_path(data_dir: Path) -> Path:
    return Path(data_dir).expanduser().resolve() / ".write.lock"


def _read_pid(lock_path: Path) -> int | None:
    try:
        raw = lock_path.read_text(encoding="utf-8", errors="replace").strip()
    except FileNotFoundError:
        return None
    if not raw:
        return None
    try:
        return int(raw.splitlines()[0])
    except ValueError:
        return None


def _is_alive(pid: int) -> bool:
    """POSIX-only: ``True`` if ``pid`` is a running process we can see."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we lack permission — treat as alive
        return True
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        # Unknown error — be conservative and treat as alive
        return True
    return True


def _age_seconds(lock_path: Path) -> float:
    try:
        st = lock_path.stat()
    except FileNotFoundError:
        return 0.0
    return time.time() - st.st_mtime


def _is_lock_held(lock_path: Path, *, stale_after: float) -> bool:
    """Decide whether the lock file at ``lock_path`` represents a live holder.

    Returns ``False`` when:

    - the file is missing (handled by caller), or
    - the recorded PID is dead, or
    - the recorded PID is alive but the file hasn't been touched in
      ``stale_after`` seconds.
    """
    pid = _read_pid(lock_path)
    if pid is None:
        # Corrupt lock file (no PID). Treat as stale so the next acquire
        # reclaims it. Caller will retry the O_EXCL after unlink.
        return False
    if not _is_alive(pid):
        return False
    if _age_seconds(lock_path) > stale_after:
        return False
    return True


def _try_reclaim(lock_path: Path) -> None:
    """Try to unlink a stale lock file.

    Tolerates races (the file may already be gone); on permission errors,
    re-raises so the caller can decide what to do.
    """
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


__all__ = [
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "DEFAULT_STALE_AFTER_SECONDS",
    "DEFAULT_WAIT_TIMEOUT_SECONDS",
    "Lock",
    "LockError",
    "LockHeld",
    "acquire_write_lock",
    "force_release",
    "lock_holder",
    "release_write_lock",
]
