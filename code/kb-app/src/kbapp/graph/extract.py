"""Entity extraction helpers (15 §4.2 / D15-13).

MVP-simplified disambiguation: ``entity_id = f"{type}:{norm(name)}"`` — same
type + same normalized name MERGE onto the same node. No embedding, no
SAME_AS, no merge/redirect logic.

This module also exposes :func:`run_extract` (Task 9 will fill in the LLM
call) and the placeholder used by :func:`stage_extract_graph` when the
extractor is not yet wired.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kbapp.core.registry import FileRow


def norm(name: str) -> str:
    """Entity name 归一化（15 D15-13）：小写 + 连字符/下划线/空白归一。

    实体消歧=entity_id 碰撞（15 D15-13）。``entity_id = f"{type}:{norm(name)}"``，
    同名同型实体 MERGE 到同一节点。
    """
    s = name.lower()
    s = re.sub(r"[\s_\-]+", "-", s)
    s = re.sub(r"[^\w\-]", "", s)
    return s.strip("-")


def is_core_doc(cfg, *, topic: str | None, doc_type: str | None, doc_id: str) -> bool:
    """15 §4.1 gate: 命中 core_topics ∩ doc_type ∈ extract.doc_types，
    或 doc_id ∈ extract.extra_docs（D15-12 单独标记入口）。
    """
    from kbapp.retrieve.query_understanding import norm as _norm

    cfg_topic = _norm(topic) if topic else ""
    core_topics = {(_norm(t) if isinstance(t, str) else "") for t in cfg.raw.get("core_topics", [])}
    if not cfg_topic or cfg_topic not in core_topics:
        extra = cfg.raw.get("extract", {}).get("extra_docs", []) or []
        if doc_id in extra:
            return _doc_type_allowed(cfg, doc_type)
        return False
    return _doc_type_allowed(cfg, doc_type)


def _doc_type_allowed(cfg, doc_type: str | None) -> bool:
    allowed = set(cfg.raw.get("extract", {}).get("doc_types", []) or [])
    return doc_type is not None and doc_type in allowed


def entity_id(entity_type: str, name: str) -> str:
    """Compute ``entity_id`` from type + name (15 D15-13)."""
    return f"{entity_type}:{norm(name)}"


def run_extract(
    *,
    store: Any,
    registry: Any,
    paths: Any,
    doc_id: str,
    row: "FileRow",
    llm: Any,
    cfg: Any,
) -> dict[str, int]:
    """Run entity extraction; return metrics dict.

    Task 9 落地前为空实现（无 LLM 调用/无 MENTIONS/RELATES_TO 写入），仅
    返回空 metrics 以便 runner 串行链路跑通——后续任务直接替换本函数体。
    """
    return {"entities": 0, "mentions": 0, "relates_to": 0, "dropped_kind": 0}


__all__ = ["entity_id", "is_core_doc", "norm", "run_extract"]
