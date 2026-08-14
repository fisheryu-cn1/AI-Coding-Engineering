"""Pipeline stages (M2; 设计 05 §4.0 + 09 §6/§7/§10).

Each stage is a small pure-ish function over :class:`PipelineCtx` plus a
``doc_id``. They write to the registry + cache and return a
:class:`StageResult` so the runner can summarise metrics. The stages are
**idempotent** — re-running on the same doc_id produces the same DB state
(``upsert`` semantics + ``delete-then-insert`` for FTS rows).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from kbapp.core.fingerprint import fingerprint
from kbapp.core.registry import (
    CLEAR,
    get_file,
    insert_chunk,
    update_file_fields,
)
from kbapp.core.task import TerminalError, enqueue_task
from kbapp.parse import parse_path
from kbapp.parse.chunk import chunk_document, write_cache_payload
from kbapp.pipeline.classify import (
    decide_doc_type,
    decide_topic,
    llm_arbitrate_doc_type,
    score_topics,
)
from kbapp.retrieve.hybrid import SUMMARY_SECTION, TITLE_SEP, section_title

if TYPE_CHECKING:
    from kbapp.pipeline.runner import PipelineCtx

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# StageResult
# ---------------------------------------------------------------------------


@dataclass
class StageResult:
    """What every stage returns (09 §10)."""

    status: Literal["ok", "skip"]
    detail: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# stage_parse — read the file, write cache payload, update extract_status.
# ---------------------------------------------------------------------------


def stage_parse(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """Parse the source file, write ``cache/extracted/<sha256>.json``.

    On failure (missing file / unreadable / no_text PDF) the stage sets
    ``extract_status='failed'`` (or ``'no_text'`` for PDFs without a text
    layer) and ``status='needs_confirm'`` so the file surfaces in
    ``kb status``. The function then returns ``StageResult(skip, …)`` so
    downstream stages are short-circuited.
    """
    with ctx.registry.read_only() as conn:
        file_row = get_file(conn, doc_id)
    if file_row is None:
        return StageResult("skip", detail=f"doc_id={doc_id} 不在 files 表")

    path = Path(file_row.path)
    if not path.exists():
        with ctx.registry.transaction() as conn:
            update_file_fields(
                conn,
                doc_id,
                extract_status="failed",
                status="needs_confirm",
            )
        return StageResult("skip", detail=f"文件不存在：{path}")

    # Re-fingerprint in case the disk sha256 drifted since scan.
    try:
        sha, mtime = fingerprint(path)
    except OSError as e:
        with ctx.registry.transaction() as conn:
            update_file_fields(
                conn,
                doc_id,
                extract_status="failed",
                status="needs_confirm",
            )
        return StageResult("skip", detail=f"指纹失败：{e}")

    cache_path = ctx.paths.extracted_dir / f"{sha}.json"
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = None
    else:
        cached = None

    if cached is not None:
        parse_result = _parse_result_from_cache(cached)
        meta = {
            "parser": cached.get("parser", "unknown"),
            "format": cached.get("format", path.suffix.lstrip(".")),
            "page_count": cached.get("page_count"),
            "header_count": cached.get("header_count"),
            "coverage": cached.get("coverage"),
        }
    else:
        try:
            parse_result, meta_obj = parse_path(path, cfg=ctx.cfg)
        except Exception as e:
            # Distinguish "no text layer" (PDF scans) from other failures.
            low = str(e).lower()
            ext_status = "no_text" if "no_text" in low or "扫描" in str(e) else "failed"
            with ctx.registry.transaction() as conn:
                update_file_fields(
                    conn,
                    doc_id,
                    extract_status=ext_status,
                    status="needs_confirm",
                )
            return StageResult("skip", detail=f"解析失败：{e}")
        meta = {
            "parser": meta_obj.parser,
            "format": meta_obj.format,
            "page_count": meta_obj.page_count,
            "header_count": meta_obj.header_count,
            "coverage": meta_obj.coverage,
        }
        # Write cache; chunk stage will populate the chunks section.
        write_cache_payload(
            sha256=sha,
            path=path,
            format=meta["format"],
            parse=parse_result,
            chunks=[],  # chunk stage fills this in
            cache_dir=ctx.paths.extracted_dir,
            page_count=meta.get("page_count"),
            header_count=meta.get("header_count"),
            coverage=meta.get("coverage"),
        )

    extract_status = (
        "ok"
        if parse_result.structure == "tree"
        else ("flat" if parse_result.structure == "flat" else "failed")
    )
    title = _derive_title(parse_result, path)
    with ctx.registry.transaction() as conn:
        update_file_fields(
            conn,
            doc_id,
            extract_status=extract_status,
            pages=meta.get("page_count"),
            title=title,
        )
    return StageResult(
        "ok",
        detail=meta["parser"],
        metrics={
            "parser": meta["parser"],
            "format": meta["format"],
            "page_count": meta.get("page_count"),
            "header_count": meta.get("header_count"),
            "coverage": meta.get("coverage"),
            "structure": parse_result.structure,
            "sections": len(parse_result.sections),
            "warnings": list(parse_result.warnings),
        },
    )


def _parse_result_from_cache(cached: dict[str, Any]):
    """Rehydrate a :class:`kbapp.parse.ParseResult` from a cache payload.

    The chunks section is loaded too — chunk stage needs it to upsert FTS
    rows in the same transaction.
    """
    from kbapp.parse.base import ParseResult, Section

    sections = [
        Section(
            section_path=s["section_path"],
            level=s["level"],
            title=s["title"],
            page_range=s.get("page_range"),
            text=s["text"],
        )
        for s in cached.get("sections", [])
    ]
    return ParseResult(
        full_text=cached.get("full_text", ""),
        sections=sections,
        structure=cached.get("structure", "flat"),
        parser=cached.get("parser", "unknown"),
        warnings=list(cached.get("warnings", [])),
    )


def _derive_title(parse_result: Any, path: Path) -> str:
    """Pick a display title for ``files.title`` (FR-1.5).

    Tree-structured docs use the first heading; flat docs fall back to the
    filename stem. Placeholders (``全文`` / ``第 N 页``) never become titles.
    """
    if parse_result.structure == "tree" and parse_result.sections:
        t = (parse_result.sections[0].title or "").strip()
        if t and t != "(无标题)":
            return t
    return path.stem.replace("_", " ").replace("-", " ")


# ---------------------------------------------------------------------------
# stage_chunk — split sections into fts_chunks + cache.
# ---------------------------------------------------------------------------


def stage_chunk(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """Chunk the cached parse, upsert into ``fts_chunks`` + cache payload.

    Idempotent: old FTS rows for the doc are deleted before new ones are
    inserted, so reparse-without-content-change is a no-op (09 §6).
    """
    with ctx.registry.read_only() as conn:
        file_row = get_file(conn, doc_id)
    if file_row is None:
        return StageResult("skip", detail=f"doc_id={doc_id} 不在 files 表")
    if file_row.extract_status in ("failed", "no_text"):
        return StageResult("skip", detail=f"上游解析失败（{file_row.extract_status}）")

    sha = file_row.sha256
    cache_path = ctx.paths.extracted_dir / f"{sha}.json"
    if not cache_path.exists():
        return StageResult("skip", detail=f"缓存缺失：{cache_path}")
    try:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return StageResult("skip", detail=f"缓存损坏：{e}")

    parse_result = _parse_result_from_cache(cached)

    chunk_size = int(ctx.cfg.get("parse.chunk_size", 2048))
    chunk_overlap = int(ctx.cfg.get("parse.chunk_overlap", 200))
    chunked = chunk_document(
        doc_id=doc_id,
        parse=parse_result,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # R-1 复合 title 的 stem 部分消毒：文件名 stem 若含 " | " 会破坏 section_title
    # 的 split 剥离（评审 P3-4），写侧替换为空格根除歧义。
    stem = Path(file_row.path).stem.replace(TITLE_SEP, " ")

    # FTS upsert: delete-then-insert per doc (09 §6 idempotency)。
    # 排除 $summary 伪 chunk（摘要由 stage_summarize 管理，重解析不删，P1-4）。
    with ctx.registry.transaction() as conn:
        conn.execute(
            "DELETE FROM fts_chunks WHERE doc_id = ? AND section_path != ?",
            (doc_id, SUMMARY_SECTION),
        )
        for c in chunked.chunks:
            insert_chunk(
                conn,
                chunk_id=c.chunk_id,
                doc_id=doc_id,
                section_path=c.section_path,
                title=f"{stem}{TITLE_SEP}{c.title}",
                text=c.text,
            )

    # Refresh cache payload with the chunk section (preserving parse metrics).
    write_cache_payload(
        sha256=sha,
        path=Path(cached.get("path", file_row.path)),
        format=cached.get("format", ""),
        parse=parse_result,
        chunks=chunked.chunks,
        cache_dir=ctx.paths.extracted_dir,
        page_count=cached.get("page_count"),
        header_count=cached.get("header_count"),
        coverage=cached.get("coverage"),
    )

    return StageResult(
        "ok",
        metrics={
            "chunks": len(chunked.chunks),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        },
    )


# ---------------------------------------------------------------------------
# stage_classify — keyword topic scoring + doc_type decision.
# ---------------------------------------------------------------------------


def stage_classify(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """Decide topic + doc_type via keyword scoring; mark ``needs_confirm`` if unsure."""
    with ctx.registry.read_only() as conn:
        file_row = get_file(conn, doc_id)
    if file_row is None:
        return StageResult("skip", detail=f"doc_id={doc_id} 不在 files 表")
    if file_row.extract_status in ("failed", "no_text"):
        return StageResult("skip", detail=f"上游解析失败（{file_row.extract_status}）")
    if file_row.status == "duplicate":
        return StageResult("skip", detail="duplicate 不入分类")

    # Title from cache payload (preferred) — falls back to filename stem.
    title = ""
    sha = file_row.sha256
    cache_path = ctx.paths.extracted_dir / f"{sha}.json"
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = None
        if cached:
            sections = cached.get("sections") or []
            title = (sections[0].get("title") if sections else "") or ""
            body = cached.get("full_text", "") or ""
        else:
            body = ""
    else:
        body = ""
    if not title:
        title = Path(file_row.path).stem.replace("_", " ").replace("-", " ")

    keywords: dict[str, list[str]] = ctx.cfg.get("classify.topic_keywords", {}) or {}
    min_score = int(ctx.cfg.get("classify.min_keyword_score", 2))
    top_ratio = float(ctx.cfg.get("classify.top_ratio", 1.5))
    scores = score_topics(
        title=title,
        body=body,
        keywords=keywords,
        body_limit=4000,
    )
    topic, needs_confirm = decide_topic(
        scores=scores,
        min_keyword_score=min_score,
        top_ratio=top_ratio,
    )
    doc_type = decide_doc_type(
        path=Path(file_row.path),
        corpus=file_row.corpus,
        summary_source=file_row.summary_source,
    )
    # Rule ⑤ LLM fallback (09 §7.3): only when we fell through to "other"
    # and a client is available.
    if doc_type == "other" and ctx.llm is not None:
        doc_type = llm_arbitrate_doc_type(
            llm=ctx.llm,
            title=title,
            body=body,
            doc_id=doc_id,
        )

    if needs_confirm:
        # Topic left NULL (09 §7.1); clear any stale topic from a prior run
        # and rebalance the old topic's doc_count (P2-3).
        _swap_topic_counts(
            registry=ctx.registry,
            old_topic=file_row.topic,
            new_topic=None,
        )
        with ctx.registry.transaction() as conn:
            update_file_fields(
                conn,
                doc_id,
                topic=CLEAR,
                doc_type=doc_type,
                status="needs_confirm",
            )
    else:
        # Decrement old topic's doc_count (if any), increment new one.
        _swap_topic_counts(
            registry=ctx.registry,
            old_topic=file_row.topic,
            new_topic=topic,
        )
        with ctx.registry.transaction() as conn:
            update_file_fields(
                conn,
                doc_id,
                topic=topic,
                doc_type=doc_type,
                status="active",
            )

    # 摘要触发（11 §3.1）：非 curated（none 需生成 / auto 需重生）或 curated+stale，
    # 且 LLM 可用时入队 summarize 任务（LLM 不可用则不入队，检索回退 title）。
    if ctx.llm is not None and (
        file_row.summary_source != "curated" or file_row.summary_stale == 1
    ):
        enqueue_task(
            ctx.registry,
            kind="summarize",
            payload={"doc_id": doc_id},
        )

    return StageResult(
        "ok",
        metrics={
            "topic": topic,
            "doc_type": doc_type,
            "needs_confirm": needs_confirm,
            "score_top1": scores[0].score if scores else 0,
            "score_top2": scores[1].score if len(scores) > 1 else 0,
        },
    )


def _swap_topic_counts(
    *,
    registry: Any,
    old_topic: str | None,
    new_topic: str | None,
) -> None:
    """Atomically rebalance ``topics.doc_count`` when a file changes topic.

    Same-topic changes are a no-op.
    """
    if old_topic == new_topic:
        return
    from kbapp.core.registry import adjust_topic_doc_count

    with registry.transaction() as conn:
        if old_topic is not None:
            adjust_topic_doc_count(conn, old_topic, -1)
        if new_topic is not None:
            adjust_topic_doc_count(conn, new_topic, +1)


def set_topic(
    registry: Any,
    doc_id: str,
    new_topic: str | None,
) -> None:
    """Manually override a file's topic. Updates ``topics.doc_count``.

    Used by the CLI's ``kb index set-topic <doc_id> <topic>`` command.
    """
    from kbapp.core.registry import (
        adjust_topic_doc_count,
        get_file,
        update_file_fields,
        upsert_topic,
    )

    with registry.read_only() as conn:
        row = get_file(conn, doc_id)
    if row is None:
        raise KeyError(f"doc_id={doc_id} 不在 files 表")
    old = row.topic
    if new_topic is not None:
        with registry.transaction() as conn:
            upsert_topic(conn, name=new_topic)
    with registry.transaction() as conn:
        if old is not None:
            adjust_topic_doc_count(conn, old, -1)
        if new_topic is not None:
            adjust_topic_doc_count(conn, new_topic, +1)
        update_file_fields(
            conn,
            doc_id,
            topic=new_topic if new_topic is not None else CLEAR,
            status="active" if new_topic is not None else "needs_confirm",
        )


# ---------------------------------------------------------------------------
# stage_summarize — 自动摘要（11 §3）
# ---------------------------------------------------------------------------


def stage_summarize(doc_id: str, ctx: PipelineCtx) -> StageResult:
    """生成自动摘要（L1–L3），写 ``auto_summaries/<doc_id>.md`` + ``$summary`` 伪 chunk。

    stale-curated（11 §3.1 四轮 #1）时生成临时 auto 摘要但不改 ``summary_source``
    /``summary_path``/``summary_stale``（provenance 不丢）。LLM 调用失败抛
    ``LLMUnavailable``（继承 ``RetryableError``）由 runner 退避。
    """
    with ctx.registry.read_only() as conn:
        file_row = get_file(conn, doc_id)
    if file_row is None:
        return StageResult("skip", detail=f"doc_id={doc_id} 不在 files 表")
    if ctx.llm is None:
        return StageResult("skip", detail="LLM 不可用，跳过摘要")
    if file_row.extract_status in ("failed", "no_text"):
        return StageResult("skip", detail=f"上游解析失败（{file_row.extract_status}）")

    summary_max_tokens = int(ctx.cfg.get("llm.summary_max_tokens", 800))
    input_budget = int(ctx.cfg.get("llm.summary_input_budget", 12000))

    with ctx.registry.read_only() as conn:
        input_text = _summary_input(conn, doc_id, input_budget)

    title = file_row.title or Path(file_row.path).stem
    try:
        raw = ctx.llm.complete(
            [{"role": "user", "content": _summary_prompt(title, input_text)}],
            json_mode=True,
            max_tokens=summary_max_tokens,
            purpose="summarize",
            doc_id=doc_id,
        )
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError(f"摘要响应不是 dict：{type(data).__name__}")
        l1 = str(data.get("l1", "")).strip()
        l2 = str(data.get("l2", "")).strip()
        l3 = str(data.get("l3", "")).strip()
    except ValueError as e:
        raise TerminalError(f"摘要结果解析失败：{e}") from e

    if not l1:
        raise TerminalError("摘要生成结果为空（l1 缺失）")

    auto_dir = ctx.paths.auto_summaries_dir
    auto_dir.mkdir(parents=True, exist_ok=True)
    auto_path = auto_dir / f"{doc_id}.md"
    auto_path.write_text(_render_summary_md(title, l1, l2, l3), encoding="utf-8")

    is_stale_curated = file_row.summary_source == "curated" and file_row.summary_stale == 1
    with ctx.registry.transaction() as conn:
        if not is_stale_curated:
            update_file_fields(
                conn,
                doc_id,
                summary_source="auto",
                summary_path=str(auto_path),
            )
        # $summary 伪 chunk 幂等 upsert（先删后插，11 §3.4）。
        conn.execute("DELETE FROM fts_chunks WHERE chunk_id = ?", (f"{doc_id}#summary",))
        insert_chunk(
            conn,
            chunk_id=f"{doc_id}#summary",
            doc_id=doc_id,
            section_path=SUMMARY_SECTION,
            title=title,
            text=f"{l1}\n{l2}",
        )

    return StageResult(
        "ok",
        detail="summary",
        metrics={"summary_chars": len(l1) + len(l2) + len(l3)},
    )


def _summary_input(conn, doc_id: str, budget: int) -> str:
    """章节树 + 各章首段（11 §3.1 LLM 输入），按 budget 截断。"""
    rows = conn.execute(
        "SELECT section_path, title, text FROM fts_chunks "
        "WHERE doc_id = ? AND section_path != ? ORDER BY chunk_id",
        (doc_id, SUMMARY_SECTION),
    ).fetchall()
    parts: list[str] = []
    used = 0
    seen: set[str] = set()
    for r in rows:
        sp = r["section_path"]
        if sp in seen:
            continue
        seen.add(sp)
        line = f"## {section_title(r['title']) or sp}\n{(r['text'] or '')[:200]}"
        if used + len(line) > budget and parts:
            break
        parts.append(line)
        used += len(line)
    return "\n\n".join(parts)


def _summary_prompt(title: str, input_text: str) -> str:
    return (
        "Write a structured summary for the document. Reply with JSON only: "
        '{"l1": "...", "l2": "...", "l3": "..."}.\n'
        "- l1: one-sentence index (~100-200 tokens)\n"
        "- l2: applicable scenarios and main viewpoints\n"
        "- l3: key details\n\n"
        f"# {title}\n\n{input_text}"
    )


def _render_summary_md(title: str, l1: str, l2: str, l3: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "## 一句话索引",
            l1,
            "",
            "## 适用场景与主要观点",
            l2,
            "",
            "## 要点细节",
            l3,
            "",
        ]
    )


__all__ = [
    "StageResult",
    "set_topic",
    "stage_chunk",
    "stage_classify",
    "stage_parse",
    "stage_summarize",
]
