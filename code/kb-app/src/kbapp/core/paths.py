"""Data directory layout (设计 03 §2 + 05 §2.5).

Canonical layout::

    <data_dir>/
    ├── config.yaml           # 全局配置
    ├── sources.yaml          # 自动收集来源（P2）
    ├── scoring_modules/      # 评分插件目录（P1）
    ├── registry.sqlite       # SQLite 注册库
    ├── graph/                # LadybugDB 数据库（M5）
    ├── vectors/              # LanceDB 表（M3）
    ├── cache/extracted/      # 解析产物缓存 <sha256>.json（M2）
    ├── inbox/                # 待审核新资料（M7）
    └── reports/              # 运行/收集/月度报告

Helpers in this module never *create* the data directory on import; layout
discovery is lazy. Functions that need the directory exist (e.g. ``mkdir``)
take care of creation themselves so callers control when side effects happen.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# 固定子目录名（避免散落在各处导致拼写漂移）
CONFIG_FILE = "config.yaml"
SOURCES_FILE = "sources.yaml"
REGISTRY_DB = "registry.sqlite"
GRAPH_DIR = "graph"
VECTORS_DIR = "vectors"
CACHE_DIR = "cache"
EXTRACTED_DIR = "extracted"
INBOX_DIR = "inbox"
REPORTS_DIR = "reports"
SCORING_MODULES_DIR = "scoring_modules"
WRITE_LOCK = ".write.lock"


@dataclass(frozen=True)
class DataPaths:
    """Resolved absolute paths inside ``data_dir``.

    Constructed via :meth:`from_data_dir` so callers cannot accidentally
    mutate the layout.
    """

    data_dir: Path
    config_path: Path
    sources_path: Path
    registry_db: Path
    graph_dir: Path
    vectors_dir: Path
    cache_dir: Path
    extracted_dir: Path
    inbox_dir: Path
    reports_dir: Path
    scoring_modules_dir: Path
    write_lock: Path

    @classmethod
    def from_data_dir(cls, data_dir: Path) -> DataPaths:
        """Resolve a layout from the given data directory.

        The directory is *not* created; callers (CLI commands, init flow) do
        that themselves so this function is side-effect free.
        """
        d = data_dir.expanduser().resolve()
        return cls(
            data_dir=d,
            config_path=d / CONFIG_FILE,
            sources_path=d / SOURCES_FILE,
            registry_db=d / REGISTRY_DB,
            graph_dir=d / GRAPH_DIR,
            vectors_dir=d / VECTORS_DIR,
            cache_dir=d / CACHE_DIR,
            extracted_dir=d / CACHE_DIR / EXTRACTED_DIR,
            inbox_dir=d / INBOX_DIR,
            reports_dir=d / REPORTS_DIR,
            scoring_modules_dir=d / SCORING_MODULES_DIR,
            write_lock=d / WRITE_LOCK,
        )

    def ensure_dirs(self) -> None:
        """Create all directories that should exist at runtime.

        Skips creation of files (``config_path``, ``sources_path``, ``registry_db``).
        """
        for d in (
            self.data_dir,
            self.graph_dir,
            self.vectors_dir,
            self.cache_dir,
            self.extracted_dir,
            self.inbox_dir,
            self.reports_dir,
            self.scoring_modules_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)


def default_data_dir() -> Path:
    """Return the default data directory path (``~/.graphit-kb``).

    The directory is not created; see :meth:`DataPaths.ensure_dirs`.
    """
    return Path("~/.graphit-kb").expanduser().resolve()
