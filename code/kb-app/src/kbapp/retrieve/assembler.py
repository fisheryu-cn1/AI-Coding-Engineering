"""上下文组装（M3；设计 11 §2 输出侧 + FR-3.2/FR-3.3）。

提供：

- :func:`read_summary` — 读文档摘要全文（stale-curated 时优先 auto 临时文件）
- :func:`read_section` — 读章节原文（``$summary`` 哨兵读摘要文件，11 §3.4）
- :func:`section_tree` — 文档章节树（排除 ``$summary`` 伪 section）
- :func:`assemble_context` — 按 token 预算拼装多文档上下文（FR-3.2）

渐进展开（FR-3.3）的 L1/L2/L3 分层由摘要结构承载；组装器只按预算截取，不生成
新文本。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kbapp.core.registry import Registry, get_file
from kbapp.retrieve.hybrid import SUMMARY_SECTION, SearchHit, search, section_title

#: 预算单位近似：中英混合下 ~4 字符/token（MVP 用字符数近似 token 预算）。
_CHARS_PER_TOKEN = 4


def _auto_summary_path(registry: Registry, doc_id: str) -> Path:
    """``auto_summaries/<doc_id>.md``（数据目录下，11 §3.2）。"""
    return registry.db_path.parent / "auto_summaries" / f"{doc_id}.md"


def read_summary(registry: Registry, file_row: Any) -> str | None:
    """读文档摘要全文；stale-curated 且存在 auto 临时文件时优先 auto（11 §3.1）。"""
    p = Path(file_row.summary_path) if file_row.summary_path else None
    if file_row.summary_stale == 1 and file_row.summary_source == "curated":
        auto = _auto_summary_path(registry, file_row.doc_id)
        if auto.exists():
            p = auto
    if p is None:
        return None
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def read_section(registry: Registry, doc_id: str, section_path: str) -> str | None:
    """读章节原文（拼接该 section 的全部 chunk text）。

    ``section_path == '$summary'`` 时读摘要产物文件全文（11 §3.4）。
    """
    if section_path == SUMMARY_SECTION:
        with registry.read_only() as conn:
            row = get_file(conn, doc_id)
        if row is None:
            return None
        return read_summary(registry, row)

    with registry.read_only() as conn:
        rows = conn.execute(
            "SELECT text FROM fts_chunks WHERE doc_id = ? AND section_path = ? ORDER BY chunk_id",
            (doc_id, section_path),
        ).fetchall()
    if not rows:
        return None
    return "\n\n".join(r["text"] for r in rows)


def section_tree(registry: Registry, doc_id: str) -> list[dict[str, str]]:
    """文档章节树（``kb show`` 用）；排除 ``$summary`` 伪 section（11 §3.4）。"""
    with registry.read_only() as conn:
        rows = conn.execute(
            "SELECT section_path, title FROM fts_chunks WHERE doc_id = ? "
            "AND section_path != ? "
            "GROUP BY section_path ORDER BY MIN(chunk_id)",
            (doc_id, SUMMARY_SECTION),
        ).fetchall()
    # R-1（13 §3）：kb_show.sections[].title 剥复合标签，保持"章节标题"语义。
    return [{"section_path": r["section_path"], "title": section_title(r["title"])} for r in rows]


def assemble_context(
    registry: Registry,
    cfg: Any,
    doc_ids: list[str],
    *,
    budget: int | None = None,
) -> str:
    """按 token 预算拼装多文档上下文（FR-3.2）。

    每个文档贡献其摘要（无摘要回退首节前 200 字符），超出预算即截断；预算
    默认取 ``retrieve.context_budget``（约 token 数，按字符近似）。
    """
    if budget is None:
        budget = int(cfg.get("retrieve.context_budget", 8000))
    char_budget = budget * _CHARS_PER_TOKEN

    parts: list[str] = []
    used = 0
    with registry.read_only() as conn:
        for doc_id in doc_ids:
            row = get_file(conn, doc_id)
            if row is None:
                continue
            header = f"## {row.title or Path(row.path).stem} ({doc_id})"
            body = read_summary(registry, row) or _first_section(conn, row)
            block = f"{header}\n{body}"
            if used + len(block) > char_budget and parts:
                break
            parts.append(block)
            used += len(block)
    return "\n\n".join(parts)


def assemble_for_task(
    registry: Registry,
    cfg: Any,
    task: str,
    *,
    budget: int = 8000,
    topics: list[str] | None = None,
) -> dict[str, Any]:
    """task 驱动的"检索→组装"编排（M4；13 §4，FR-3.2/FR-3.3）。

    确定性路径：内部调 :func:`search` 不传 ``llm``（无查询扩展/重排），Agent
    侧延迟可预期（13 §4 决策 7）。``topics`` 非空时对每个 topic 各跑一次
    ``--topic`` 硬过滤检索合并去重；空则全库一次。返回
    ``{context_block, budget, used, sources}``；``sources`` 只含**实际拼入**
    context_block 的文档（被预算砍掉的尾部文档不出现，不给悬空锚点）。
    """
    hits: list[SearchHit] = []
    seen: set[tuple[str, str]] = set()
    if topics:
        for t in topics:
            result = search(registry, cfg, task, mode="hybrid", topic=t, limit=10)
            for h in result.hits:
                key = (h.doc_id, h.section_path)
                if key not in seen:
                    seen.add(key)
                    hits.append(h)
    else:
        hits = search(registry, cfg, task, mode="hybrid", limit=10).hits

    # 按命中序取文档去重；锚点取该文档首个命中的 section_path（供 kb_read 下钻）。
    doc_anchor: dict[str, str] = {}
    doc_ids: list[str] = []
    for h in hits:
        if h.doc_id not in doc_anchor:
            doc_anchor[h.doc_id] = h.section_path
            doc_ids.append(h.doc_id)

    char_budget = budget * _CHARS_PER_TOKEN
    parts: list[str] = []
    used_chars = 0
    sources: list[dict[str, str]] = []
    with registry.read_only() as conn:
        for doc_id in doc_ids:
            row = get_file(conn, doc_id)
            if row is None:
                continue
            header = f"## {row.title or Path(row.path).stem} ({doc_id})"
            body = read_summary(registry, row) or _first_section(conn, row)
            block = f"{header}\n{body}"
            if used_chars + len(block) > char_budget and parts:
                break
            parts.append(block)
            used_chars += len(block)
            sources.append({"doc_id": doc_id, "section_path": doc_anchor[doc_id]})
    context_block = "\n\n".join(parts)
    used = len(context_block) // _CHARS_PER_TOKEN
    return {
        "context_block": context_block,
        "budget": budget,
        "used": used,
        "sources": sources,
    }


def _first_section(conn: Any, row: Any) -> str:
    sec = conn.execute(
        "SELECT text FROM fts_chunks WHERE doc_id = ? AND section_path != ? "
        "ORDER BY chunk_id LIMIT 1",
        (row.doc_id, SUMMARY_SECTION),
    ).fetchone()
    if sec and sec["text"]:
        return sec["text"][:200]
    return row.title or ""


def compare_documents(
    llm: Any,
    entries: list[tuple[str, str, str]],
) -> str | None:
    """LLM 组装多文档对比表（11 §2.5 ``compare``）。

    ``entries`` = ``[(doc_id, title, summary)]``（summary 为 L1–L3 摘要全文）。
    成功返回 Markdown 对比表；LLM 不可用或失败返回 ``None``（调用方回退并排摘要）。

    purpose 复用 ``extract``（提取结构化对比；11 §7 未为 compare 单列枚举）。
    """
    if llm is None or len(entries) < 2:
        return None
    parts = [
        f"## [{i}] {doc_id} — {title}\n{summary or '(无摘要)'}"
        for i, (doc_id, title, summary) in enumerate(entries)
    ]
    prompt = (
        "Compare the following documents and produce a Markdown comparison table. "
        "Use a leading '维度' column plus one column per document. Rows should cover: "
        "一句话结论 / 适用场景 / 主要观点 / 关键差异. Reply with the table only.\n\n"
        + "\n\n".join(parts)
    )
    try:
        return llm.complete(
            [{"role": "user", "content": prompt}],
            json_mode=False,
            max_tokens=1024,
            purpose="extract",
        )
    except Exception:
        return None


__all__ = [
    "assemble_context",
    "assemble_for_task",
    "compare_documents",
    "read_section",
    "read_summary",
    "section_tree",
]
