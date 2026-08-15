"""Config loading, atomic write, dotted-path get/set, and audit log helper.

设计依据：05 §2.5（config.yaml schema）+ 06（无）+ 02 D8（YAML）。
本模块是 M1 的核心契约之一：CLI / MCP / Web 三个入口共享同一份 Config。

要点：
- 加载失败时打印 schema 期望，不抛裸 stack（M1 UX 友好）
- 原子写：tmp 文件 + os.replace（同一文件系统下保证）
- 点路径读写：``scoring.thresholds.accept`` 一类
- 缺键自动填默认；多余键保留
- ``set_value`` 返回 ``(old, new)`` 给 audit 表使用
"""

from __future__ import annotations

import copy
import os
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

#: Sentinel for "this leaf is missing from the user / default side" in
#: :func:`diff_defaults`. Kept as a private singleton so the CLI can
#: distinguish it from a real ``None`` value (e.g. ``llm.api_base`` defaults
#: to ``None`` — the diff must not render that as "<missing>").
_MISSING = object()

DEFAULT_DATA_DIR = "~/.graphit-kb"


def _default_data_dir_str() -> str:
    return DEFAULT_DATA_DIR


def _now_iso() -> str:
    """ISO-8601 UTC, second precision."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Default schema (设计 05 §2.5)
# ---------------------------------------------------------------------------

DEFAULTS: dict[str, Any] = {
    "data_dir": _default_data_dir_str(),
    "corpus_roots": {
        "references": "~/research/references",
        "research": "~/research/research",
        "design": "~/research/design",
    },
    "core_topics": [
        "ContextEngineering",
        "context-engineering",
        "ai-coding",
        "CodeGraph",
    ],
    "llm": {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "api_base": None,
        "api_key_env": "DEEPSEEK_API_KEY",
        "json_mode": True,
        "fallback": [],
        "retry": {
            "max_attempts": 4,
            "base_delay_seconds": 1,
            "backoff_factor": 2,
            "max_delay_seconds": 30,
        },
        "fallback_max_switches": 1,
        "summary_max_tokens": 800,  # 11 §3.3：自动摘要 L1–L3 输出预算
        "summary_input_budget": 12000,  # 11 §3.1：摘要 LLM 输入（章节树+各章首段）预算
    },
    "embedding": {
        "backend": "none",  # 11 §5：无向量 MVP 默认 none（local/api 为 P1 目标态）
        "model": "BAAI/bge-m3",
        "api_model": None,
    },
    "retrieve": {
        "default_mode": "hybrid",
        "default_limit": 10,
        "context_budget": 8000,
        "rrf_k": 60,
    },
    "search": {
        # 11 §2.4：LLM 重排；max_tokens 需覆盖推理模型 think 开销
        "rerank": {"enabled": True, "top_k": 20, "max_tokens": 1024},
        "query_expansion": True,  # 11 §2.3：LLM 查询扩展（离线自动关）
        "query_expansion_max_tokens": 1024,  # 同上：推理模型 think 会吃预算
        "synonyms": {},  # 11 §2.2/§2.3：用户自定义同义/缩写表（dict，YAML 容器口径）
        "exact_boost": 1.3,  # 13 §3 R-2：原查询语义命中倍率（扩展只增召回、不压精确命中）
        "graph": {"max_docs": 20, "max_sections": 40, "weight": 0.5},  # 11 §2.1：图路有界化+权重
    },
    "parse": {
        "pdf_fast_min_coverage": 0.85,
        "pdf_fast_min_headers": 3,
        "chunk_size": 2048,
        "chunk_overlap": 200,
        "page_char_norm": 1500,  # 09 §4：分母（每页经验字符数）
        "ocr_enabled": False,  # 09 §1：Tesseract OCR 默认关闭
    },
    "classify": {
        "gap_threshold": 0.05,
        "confirm_threshold": 0.70,
        "topic_keywords": {},  # 09 §7.1：{topic: [关键词...]}；默认空
        "min_keyword_score": 2,  # 09 §7.1：top1 命中门槛
        "top_ratio": 1.5,  # 09 §7.1：top1/top2 比值门槛
    },
    "scoring": {
        "default_module": "default",
        "thresholds": {
            "accept": 0.70,
            "reject": 0.50,
            "cross_topic_bonus": 0.05,
            "min_centroid_samples": 5,
            "rejection_damp": {
                "factor": 0.8,
                "window_days": 90,
                "min_count": 3,
            },
        },
        "topic_keywords": {},
        "topic_bindings": [],
    },
    "mcp": {
        "transport": "stdio",
        "http_host": "127.0.0.1",
        "http_token": None,
        "enable_write_tools": False,
    },
    # M5/M6 新增（15 §7）：图库单一选型 ladybug（D15-10），extract 门控含
    # 单独标记入口 extract.extra_docs（D15-12），viz 服务绑定 127.0.0.1。
    "graph": {"backend": "ladybug", "dir": "graph"},
    "extract": {"doc_types": ["paper", "design"], "extra_docs": []},
    "viz": {"port": 8371, "max_nodes": 500},
}


# ---------------------------------------------------------------------------
# Config dataclass (top-level shape; values are arbitrary dicts so we can
# extend without bumping the schema every time)
# ---------------------------------------------------------------------------


@dataclass
class Config:
    """Top-level config object exposed by ``kbapp.core.config``.

    Fields are loose ``Any`` because the YAML schema evolves; consumers
    should access them through helpers (``get_value`` / ``set_value``) or
    the typed substructures inside ``llm`` / ``scoring`` / etc.
    """

    raw: dict[str, Any] = field(default_factory=dict)

    # ---- typed accessors -------------------------------------------------

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Read a value by dotted path; return ``default`` if missing.

        Convenience wrapper around :func:`get_value` that swallows
        :class:`ConfigError` (missing leaf) and returns ``default``. Used by
        pipeline stages where a missing key is a soft fallback, not an
        error.
        """
        try:
            return get_value(self, dotted_key)
        except ConfigError:
            return default

    @property
    def data_dir(self) -> Path:
        # GRAPHIT_KB_DATA_DIR 环境变量优先（与 CLI --data-dir 的 envvar 注入口径
        # 一致）：否则 llm_usage 记账等按 cfg.data_dir 寻址的写入会落到配置文件
        # 里的默认目录而非实际数据目录（M3 DoD 复核修复）。
        env = os.environ.get("GRAPHIT_KB_DATA_DIR")
        if env:
            return Path(env).expanduser()
        return Path(self.raw["data_dir"]).expanduser()

    @property
    def corpus_roots(self) -> dict[str, Path]:
        return {k: Path(v).expanduser() for k, v in self.raw["corpus_roots"].items()}

    # ---- factories -------------------------------------------------------

    @classmethod
    def defaults(cls) -> Config:
        return cls(raw=copy.deepcopy(DEFAULTS))

    # ---- repr ------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Config(data_dir={self.data_dir})"


# ---------------------------------------------------------------------------
# Load / dump
# ---------------------------------------------------------------------------


def load_config(path: Path | None) -> Config:
    """Load config from ``path``, merging user values over defaults.

    ``path`` may be ``None`` (returns defaults only). Missing parent directory
    is *not* created. A non-existent file returns defaults; a malformed file
    raises :class:`ConfigError` with a helpful message.
    """
    if path is None:
        return Config.defaults()

    p = Path(path).expanduser()
    if not p.exists():
        return Config.defaults()

    try:
        with p.open("r", encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"config.yaml 解析失败 ({p}): {e}") from e

    if not isinstance(user, dict):
        raise ConfigError(f"config.yaml 顶层必须是 mapping，得到 {type(user).__name__} ({p})")

    merged = merge_defaults(user)
    return Config(raw=merged)


def dump_config(cfg: Config, path: Path) -> None:
    """Atomically write config to ``path``.

    Uses ``tempfile.NamedTemporaryFile(dir=path.parent)`` + ``os.replace`` so
    concurrent readers either see the old file or the fully-written new one,
    never a partial.
    """
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)

    payload = yaml.safe_dump(
        cfg.raw,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    fd, tmp_name = tempfile.mkstemp(prefix=f".{p.name}.", suffix=".tmp", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, p)
    except Exception:
        # best-effort cleanup; if rename succeeded this is a no-op
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def merge_defaults(user: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge ``user`` over :data:`DEFAULTS`; lists/scalars in user win."""
    return _deep_merge(copy.deepcopy(DEFAULTS), user)


# ---------------------------------------------------------------------------
# Dotted-path get / set
# ---------------------------------------------------------------------------


def get_value(cfg: Config, dotted_key: str) -> Any:
    """Read a value by dotted path; raise :class:`ConfigError` if missing."""
    cur: Any = cfg.raw
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ConfigError(f"配置键不存在：{dotted_key!r}")
        cur = cur[part]
    return cur


def set_value(cfg: Config, dotted_key: str, value: Any) -> tuple[Any, Any]:
    """Set a value by dotted path; return ``(old, new)``.

    The dict is mutated in place. Intermediate nodes must already exist
    (we are not in the business of inventing schema via this API).
    Coerces scalars via :func:`_coerce_scalar`.
    """
    parts = dotted_key.split(".")
    if not parts:
        raise ConfigError("配置键不能为空")

    cur = cfg.raw
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            raise ConfigError(f"配置路径中间节点不存在或不是 dict：{dotted_key!r}")
        cur = cur[part]

    leaf = parts[-1]
    if leaf not in cur:
        raise ConfigError(f"配置键不存在：{dotted_key!r}")

    old = cur[leaf]
    new = _coerce_scalar(old, value)
    cur[leaf] = new
    return old, new


def diff_defaults(cfg: Config) -> dict[str, tuple[Any, Any]]:
    """Return ``{dotted_key: (default, current)}`` for every user-modified leaf.

    Used by ``kb config diff`` to highlight what the user has changed.
    """
    diffs: dict[str, tuple[Any, Any]] = {}
    _walk_diff("", DEFAULTS, cfg.raw, diffs)
    return diffs


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ConfigError(ValueError):
    """Raised for any user-facing config problem."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursive dict merge; lists/scalars in ``override`` replace base."""
    out = copy.deepcopy(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _coerce_scalar(existing: Any, new: Any) -> Any:
    """Best-effort scalar coercion to match the type of ``existing``.

    Used when CLI receives a string but the underlying value is bool / int /
    float. We never coerce *away* from a string.
    """
    if isinstance(existing, bool):
        if isinstance(new, bool):
            return new
        if isinstance(new, str):
            low = new.strip().lower()
            if low in ("true", "yes", "1", "on"):
                return True
            if low in ("false", "no", "0", "off"):
                return False
        raise ConfigError(f"无法把 {new!r} 解析为 bool")
    if isinstance(existing, int) and not isinstance(existing, bool):
        if isinstance(new, bool):
            # bool is subclass of int — explicit, not implicit
            raise ConfigError(f"无法把 {new!r} 解析为 int")
        if isinstance(new, int):
            return new
        if isinstance(new, str):
            try:
                return int(new.strip(), base=10)
            except ValueError as e:
                raise ConfigError(f"无法把 {new!r} 解析为 int") from e
        raise ConfigError(f"无法把 {type(new).__name__} 解析为 int")
    if isinstance(existing, float):
        if isinstance(new, (int, float)) and not isinstance(new, bool):
            return float(new)
        if isinstance(new, str):
            try:
                return float(new.strip())
            except ValueError as e:
                raise ConfigError(f"无法把 {new!r} 解析为 float") from e
        raise ConfigError(f"无法把 {type(new).__name__} 解析为 float")
    if isinstance(existing, (list, dict)):
        # The CLI delivers a string; parse it back into the container type so
        # `kb config set llm.fallback [...]` and
        # `kb config set classify.topic_keywords '{...}'` actually work (09 §9
        # 「全部参数可修改」；P3-5).
        if isinstance(new, type(existing)):
            return new
        if isinstance(new, str):
            try:
                parsed = yaml.safe_load(new)
            except yaml.YAMLError as e:
                raise ConfigError(f"无法把 {new!r} 解析为 {type(existing).__name__}: {e}") from e
            if isinstance(parsed, type(existing)):
                return parsed
            raise ConfigError(f"无法把 {new!r} 解析为 {type(existing).__name__}")
        raise ConfigError(f"无法把 {type(new).__name__} 解析为 {type(existing).__name__}")
    # str / None — pass through; deeper validation is not the job of this module
    return new


def _walk_diff(prefix: str, base: Any, current: Any, out: dict[str, tuple[Any, Any]]) -> None:
    if isinstance(base, dict) and isinstance(current, dict):
        for k, v in base.items():
            sub_prefix = f"{prefix}.{k}" if prefix else k
            if k not in current:
                out[sub_prefix] = (v, _MISSING)
                continue
            _walk_diff(sub_prefix, v, current[k], out)
        for k in current:
            if k not in base:
                sub_prefix = f"{prefix}.{k}" if prefix else k
                out[sub_prefix] = (_MISSING, current[k])
        return
    if base != current:
        out[prefix] = (base, current)


__all__ = [
    "Config",
    "ConfigError",
    "DEFAULTS",
    "diff_defaults",
    "dump_config",
    "get_value",
    "load_config",
    "merge_defaults",
    "set_value",
]
