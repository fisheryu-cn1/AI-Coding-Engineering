"""Stub for entity extraction helpers — Task 9 充实。"""

from __future__ import annotations

import re


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


__all__ = ["is_core_doc", "norm"]
