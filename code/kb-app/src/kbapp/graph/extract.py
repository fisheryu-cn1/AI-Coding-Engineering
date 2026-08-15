"""Entity extraction (15 §4.2 / D15-13).

MVP-simplified disambiguation: ``entity_id = f"{type}:{norm(name)}"`` —
same type + same normalized name MERGE onto the same node. No embedding,
no SAME_AS, no merge/redirect logic.

LLM 调用一次产出 entities + relations；MENTIONS 用实体名在 Section 文本
中的 ``str.count`` 计算 weight。未知 kind 丢弃并计数进 metrics。同对同
kind 冲突取 weight 高者。
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from kbapp.graph.schema import ENTITY_TYPES, REL_KINDS

if TYPE_CHECKING:
    from kbapp.core.paths import DataPaths
    from kbapp.core.registry import FileRow, Registry


_logger = logging.getLogger(__name__)


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
    或 doc_id ∈ extract.extra_docs（D15-12 单独标记入口，独立通道绕开双检）。
    """
    from kbapp.retrieve.query_understanding import norm as _norm

    # 单独标记入口：doc_id 命中独立通过（D15-12），不走 topic∩doc_type 交集。
    extra = cfg.raw.get("extract", {}).get("extra_docs", []) or []
    if doc_id in extra:
        return True

    cfg_topic = _norm(topic) if topic else ""
    core_topics = {(_norm(t) if isinstance(t, str) else "") for t in cfg.raw.get("core_topics", [])}
    if not cfg_topic or cfg_topic not in core_topics:
        return False
    return _doc_type_allowed(cfg, doc_type)


def _doc_type_allowed(cfg, doc_type: str | None) -> bool:
    allowed = set(cfg.raw.get("extract", {}).get("doc_types", []) or [])
    return doc_type is not None and doc_type in allowed


def entity_id(entity_type: str, name: str) -> str:
    """Compute ``entity_id`` from type + name (15 D15-13)."""
    return f"{entity_type}:{norm(name)}"


#: 抽取输入预算（字符）：单次 LLM 调用 body 上限。超长 prompt 会让推理模型
#: （think 吃预算）直接返回空——实测 150KB prompt 下 minimax-m2.7 返回空串。
_EXTRACT_INPUT_BUDGET = 12000


def _extract_prompt(title: str, sections: list[dict]) -> str:
    """LLM 抽取 prompt（15 §4.2：单次调用同时产实体 + 关系）。

    输入有界：每 Section 正文截 1500 字符，总 body 上限 :data:`_EXTRACT_INPUT_BUDGET`。
    """
    parts: list[str] = []
    used = 0
    for s in sections:
        line = (
            f"## {s.get('section_path', '?')} {s.get('title', '')}\n"
            f"{s.get('text', '')[:1500]}"
        )
        if used + len(line) > _EXTRACT_INPUT_BUDGET and parts:
            break
        parts.append(line)
        used += len(line)
    body = "\n".join(parts)
    return (
        "Extract entities and relations from the document. Reply with JSON only.\n"
        "Schema: "
        '{"entities":[{"name":"...","type":"Concept|Method|Tool|Dataset|Person|Organization",'
        '"aliases":[],"description":"..."}],'
        '"relations":[{"src":"<entity name>","dst":"<entity name>",'
        '"kind":"extends|contradicts|applies|evaluates|improves-on|part-of|instance-of|uses|compares",'
        '"weight":1.0,"evidence_section_id":"<section path>"}]}\n\n'
        f"# {title}\n\n{body}"
    )


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _section_text_by_id(paths: DataPaths, sha: str) -> dict[str, str]:
    """读 parse cache JSON，返回 {section_path: text}。"""
    cache = paths.extracted_dir / f"{sha}.json"
    if not cache.exists():
        return {}
    try:
        cached = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {s.get("section_path", ""): s.get("text", "") for s in cached.get("sections", [])}


def run_extract(
    *,
    store: Any,
    registry: Registry,
    paths: DataPaths,
    doc_id: str,
    row: FileRow,
    llm: Any,
    cfg: Any,
) -> dict[str, int]:
    """Run entity extraction; return metrics dict.

    Metrics keys: entities, mentions, relates_to, dropped_kind, skipped.
    """
    if llm is None:
        return {"entities": 0, "mentions": 0, "relates_to": 0, "dropped_kind": 0, "skipped": 1}

    sha = row.sha256
    section_text = _section_text_by_id(paths, sha)
    cache_path = paths.extracted_dir / f"{sha}.json"
    sections_payload: list[dict] = []
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            sections_payload = cached.get("sections", []) or []
        except (OSError, json.JSONDecodeError):
            sections_payload = []

    prompt = _extract_prompt(row.title or row.path, sections_payload)
    try:
        raw = llm.complete(
            [{"role": "user", "content": prompt}],
            json_mode=True,
            max_tokens=int(cfg.get("llm.extract_max_tokens", 4096)),
            purpose="extract",
            doc_id=doc_id,
        )
        data = json.loads(raw)
    except Exception as e:
        _logger.warning("extract LLM failed for %s: %s", doc_id, e)
        return {"entities": 0, "mentions": 0, "relates_to": 0, "dropped_kind": 0, "skipped": 1}

    if not isinstance(data, dict):
        return {"entities": 0, "mentions": 0, "relates_to": 0, "dropped_kind": 0, "skipped": 1}

    entities_in = data.get("entities") or []
    relations_in = data.get("relations") or []

    # 1) 收敛实体：去重（type + name 碰撞）
    entity_nodes: dict[str, dict] = {}
    for e in entities_in:
        if not isinstance(e, dict):
            continue
        t = str(e.get("type", "")).strip()
        n = str(e.get("name", "")).strip()
        if not t or not n:
            continue
        if t not in ENTITY_TYPES:
            _logger.info("drop entity with unknown type %r", t)
            continue
        eid = entity_id(t, n)
        if eid not in entity_nodes:
            entity_nodes[eid] = {
                "entity_id": eid,
                "name": n,
                "type": t,
                "aliases": ",".join(str(a) for a in (e.get("aliases") or []) if a),
                "description": str(e.get("description", ""))[:500],
            }
    if entity_nodes:
        store.upsert_nodes("Entity", list(entity_nodes.values()))

    # 2) MENTIONS：实体名在 Section 文本中 count(name) 计算 weight
    mentions_count = 0
    for eid, entity in entity_nodes.items():
        name = entity["name"]
        # 简化全文扫描：每篇 Section 独立计数；evidence_section_id 缺失则全 doc
        for sp, text in section_text.items():
            if not text:
                continue
            cnt = text.count(name)
            if cnt <= 0:
                continue
            sid = f"{doc_id}#{sp}"
            store.upsert_edges(
                "MENTIONS",
                [{"src": sid, "dst": eid, "weight": int(cnt)}],
            )
            mentions_count += 1

    # 3) RELATES_TO：去重（src/dst/kind 唯一），未知 kind 丢弃并计数
    dropped_kind = 0
    rel_edges: dict[tuple[str, str, str], dict] = {}
    for r in relations_in:
        if not isinstance(r, dict):
            continue
        src_name = str(r.get("src", "")).strip()
        dst_name = str(r.get("dst", "")).strip()
        src_type = _entity_type_by_name(entity_nodes, src_name)
        dst_type = _entity_type_by_name(entity_nodes, dst_name)
        if not src_type or not dst_type:
            continue
        kind = str(r.get("kind", "")).strip()
        if kind not in REL_KINDS:
            dropped_kind += 1
            continue
        weight = float(r.get("weight", 1.0) or 1.0)
        evid = str(r.get("evidence_section_id", "")).strip()
        src_eid = entity_id(src_type, src_name)
        dst_eid = entity_id(dst_type, dst_name)
        key = (src_eid, dst_eid, kind)
        existing = rel_edges.get(key)
        if existing is None or existing["weight"] < weight:
            rel_edges[key] = {
                "src": src_eid,
                "dst": dst_eid,
                "kind": kind,
                "weight": weight,
                "evidence_section_id": evid,
            }
    if rel_edges:
        store.upsert_edges("RELATES_TO", list(rel_edges.values()))

    return {
        "entities": len(entity_nodes),
        "mentions": mentions_count,
        "relates_to": len(rel_edges),
        "dropped_kind": dropped_kind,
        "skipped": 0,
    }


def _entity_type_by_name(entity_nodes: dict[str, dict], name: str) -> str | None:
    """通过 name 查 entity 的 type（关系里的 src/dst 是 name）。"""
    if not name:
        return None
    for e in entity_nodes.values():
        if e["name"] == name:
            return e["type"]
    return None


__all__ = ["entity_id", "is_core_doc", "norm", "run_extract"]
