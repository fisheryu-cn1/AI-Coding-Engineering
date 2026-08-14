"""无向量两路召回 + 加权 RRF（M3；设计 11 §2）。

- 全文路：FTS5 trigram（chunk 级召回 → 聚合到 section，§2.2；短查询兜底 §2.2）
- 图路：结构导航（topic/标题命中 → section 列表，§2.1）
- 融合：加权 RRF（``w_fts=1.0`` / ``w_graph=0.5``，§2.1），section 粒度
- 结果：``[SearchHit]``（doc_id / section_path / 得分 / 摘要片段 / 锚点，FR-3.5）

本模块所有 SQL 直接跑在 ``registry.read_only()`` 连接上，与 ``cli/index.py``
的 scan 层同风格（typed DAO 只放 registry，检索专用查询就地写）。
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Any

from kbapp.core.registry import Registry, list_files, list_topics
from kbapp.retrieve.query_understanding import (
    is_cjk,
    llm_expand_query,
    match_topics,
    merged_synonyms,
    split_terms,
)

#: section_path 哨兵：摘要伪 chunk（11 §3.4）。
SUMMARY_SECTION = "$summary"

#: R-1 复合 title 分隔符：`{文件名 stem} | {章节标题}`（13 §3）。
TITLE_SEP = " | "


def section_title(title: str) -> str:
    """剥 R-1 复合标签，取纯章节标题（13 §3 展示/匹配出口）。

    复合标签形如 ``06-Hong-Context_Rot | Introduction``；取 ``|`` 之后的纯
    章节标题。无分隔符（``$summary`` 或历史数据）原样返回，幂等安全
    （``split`` 无分隔符时返回单元素列表，``[-1]`` 即原串）。
    """
    return title.split(TITLE_SEP, 1)[-1]


#: snippet 截断长度（对齐 04 §2.1 命中表格的一行摘要）。
_SNIPPET_LEN = 120

#: topic 稀疏退化阈值（11 §2.1）：topic=NULL 占比 ≥ 此值时图路才退化（P1-1）。
_TOPIC_SPARSE_RATIO = 0.5


def _topic_null_ratio(conn: sqlite3.Connection) -> float:
    """非 deleted/duplicate 文档中 topic=NULL 的占比。"""
    row = conn.execute(
        "SELECT "
        "COALESCE(SUM(CASE WHEN topic IS NULL THEN 1 ELSE 0 END), 0) AS nulls, "
        "COUNT(*) AS total FROM files WHERE status NOT IN ('deleted','duplicate')"
    ).fetchone()
    if row is None or row["total"] == 0:
        return 0.0
    return row["nulls"] / row["total"]


@dataclass
class SearchHit:
    """一条 section 级命中（FR-3.5 输出口径）。"""

    doc_id: str
    path: str
    section_path: str
    title: str  # section 标题（$summary 时为文档标题）
    score: float
    corpus: str
    doc_type: str | None
    topic: str | None
    snippet: str

    @property
    def anchor(self) -> str:
        return f"{self.doc_id}#{self.section_path}"


@dataclass
class SearchResult:
    """一次检索的结果 + 诊断信息（图路退化提示等）。"""

    hits: list[SearchHit] = field(default_factory=list)
    mode: str = "hybrid"
    note: str = ""
    graph_degraded: bool = False


# ---------------------------------------------------------------------------
# 全文路（FTS5 trigram）
# ---------------------------------------------------------------------------


def _fts_chunk_hits(
    conn: sqlite3.Connection,
    query: str,
    synonyms: dict[str, list[str]],
    *,
    extra_terms: list[str],
    doc_ids: set[str] | None,
    limit: int,
    exact_boost: float = 1.0,
) -> list[tuple[str, str, str, str, float]]:
    """返回 chunk 级命中 ``(doc_id, section_path, title, text, score)``。

    ``score`` 取 ``-bm25()``（更高=更相关）。短查询按 §2.2 分 CJK LIKE / ASCII
    缩写扩展两路处理，与 FTS 词元结果取交集（AND）。``doc_ids`` 非空时把
    ``--topic`` 前置硬过滤下推进 SQL（P1-2）；词元引号消毒（P2-2）。

    LLM 扩展词（``extra_terms``）只做**并集增召回**（11 §2.3）：原查询按既有
    语义单独执行，扩展词另起一个 OR 组 MATCH，两结果按 (doc_id, section)
    取并集留最高分——扩展只加候选、绝不收缩原查询结果（M3 DoD 复核修复：
    此前扩展词混入 AND 组，30+ 词全合取导致 FTS 零命中）。

    R-2（13 §3）：原查询语义命中的 chunk 得分 ×``exact_boost`` 再与扩展路并集。
    先 boost 原查询路（``rows``）再 max 并集，等价于保留 provenance、不改变
    合并结构与返回 shape；扩展词缺失（``extra_terms`` 空）时直接返回不 boost，
    保持无扩展时既有相对序不变。
    """
    if doc_ids is not None and not doc_ids:
        return []
    rows = _fts_rows(conn, split_terms(query), synonyms, doc_ids=doc_ids, limit=limit)

    exp_terms = [t.replace('"', "").strip() for t in extra_terms]
    exp_terms = [t for t in exp_terms if len(t) >= 3]
    if not exp_terms:
        return rows
    match = " OR ".join(f'"{t}"' for t in exp_terms)
    rows_ext = _fts_match_query(conn, match, [], [], doc_ids=doc_ids, limit=limit)

    if exact_boost != 1.0:
        rows = [(d, sp, t, x, s * exact_boost) for (d, sp, t, x, s) in rows]

    best: dict[tuple[str, str], tuple[str, str, str, str, float]] = {}
    for r in [*rows, *rows_ext]:
        key = (r[0], r[1])
        if key not in best or r[4] > best[key][4]:
            best[key] = r
    return sorted(best.values(), key=lambda r: -r[4])


def _fts_rows(
    conn: sqlite3.Connection,
    terms: list[str],
    synonyms: dict[str, list[str]],
    *,
    doc_ids: set[str] | None,
    limit: int,
) -> list[tuple[str, str, str, str, float]]:
    """原查询语义的 FTS/LIKE 执行（AND 组合），见 :func:`_fts_chunk_hits`。"""
    fts_terms = [t for t in terms if len(t) >= 3]
    short = [t for t in terms if len(t) < 3]
    cjk_short = [t for t in short if is_cjk(t)]
    ascii_short = [t for t in short if not is_cjk(t)]

    # FTS MATCH：≥3 字符词元 AND；ASCII 缩写经同义扩展 OR 成一组。词元引号消毒。
    groups: list[str] = []
    for t in fts_terms:
        clean = t.replace('"', "").strip()
        if clean:
            groups.append(f'"{clean}"')
    for t in ascii_short:
        syns = [s.replace('"', "") for s in synonyms.get(t.lower(), []) if len(s) >= 3]
        if syns:
            groups.append("(" + " OR ".join(f'"{s}"' for s in syns) + ")")

    # LIKE 兜底（text 维度，与 FTS 结果取交集；纯 LIKE 路的 text 档也复用）。
    text_clauses: list[str] = []
    text_params: list[str] = []
    for t in cjk_short:
        text_clauses.append("text LIKE ?")
        text_params.append(f"%{t}%")
    for t in ascii_short:
        if not any(s for s in synonyms.get(t.lower(), []) if len(s) >= 3):
            text_clauses.append("' ' || text || ' ' LIKE ?")
            text_params.append(f"% {t} %")

    if groups:
        return _fts_match_query(
            conn, " AND ".join(groups), text_clauses, text_params, doc_ids=doc_ids, limit=limit
        )

    # 无 ≥3 字符词元：纯 LIKE 扫描（R-3 分档：title 1.0 / text 0.5）。
    if not text_clauses:
        return []
    return _like_ranked_rows(
        conn, cjk_short, ascii_short, synonyms, text_clauses, text_params, doc_ids, limit
    )


def _id_clause(doc_ids: set[str] | None) -> tuple[str, list[Any]]:
    if doc_ids is None:
        return "", []
    return f" AND doc_id IN ({','.join('?' for _ in doc_ids)})", list(doc_ids)


def _like_sql(
    like_clauses: list[str],
    like_params: list[str],
    doc_ids: set[str] | None,
    limit: int,
) -> tuple[str, list[Any]]:
    id_clause, id_params = _id_clause(doc_ids)
    # R-3（13 §3）确定性：LIMIT 截断前先按 (doc_id, section_path) 排序，避免
    # 大命中集下由查询计划决定截断集合、title 命中被截断降级（评审 P2-6）。
    sql = (
        "SELECT doc_id, section_path, title, text FROM fts_chunks WHERE "
        + " AND ".join(like_clauses)
        + id_clause
        + " ORDER BY doc_id, section_path LIMIT ?"
    )
    return sql, [*like_params, *id_params, limit * 4]


def _like_ranked_rows(
    conn: sqlite3.Connection,
    cjk_short: list[str],
    ascii_short: list[str],
    synonyms: dict[str, list[str]],
    text_clauses: list[str],
    text_params: list[str],
    doc_ids: set[str] | None,
    limit: int,
) -> list[tuple[str, str, str, str, float]]:
    """R-3（13 §3）：纯 LIKE 兜底分档排序。

    ``title LIKE`` 命中记 1.0、``text LIKE`` 命中记 0.5，按
    (score desc, doc_id asc, section_path asc) 确定性排序——避免纯 LIKE 路
    一律 score=0 导致"图谱"类短词在 title 命中被吞或无法稳定排序。title/text
    两个维度独立 AND 匹配后按 (doc_id, section) 取最高分并集。
    """
    title_clauses: list[str] = []
    title_params: list[str] = []
    for t in cjk_short:
        title_clauses.append("title LIKE ?")
        title_params.append(f"%{t}%")
    for t in ascii_short:
        if not any(s for s in synonyms.get(t.lower(), []) if len(s) >= 3):
            title_clauses.append("' ' || title || ' ' LIKE ?")
            title_params.append(f"% {t} %")

    best: dict[tuple[str, str], tuple[str, str, str, str, float]] = {}
    if title_clauses:
        for r in _like_rows(conn, title_clauses, title_params, doc_ids, limit, 1.0):
            key = (r[0], r[1])
            if key not in best or r[4] > best[key][4]:
                best[key] = r
    if text_clauses:
        for r in _like_rows(conn, text_clauses, text_params, doc_ids, limit, 0.5):
            key = (r[0], r[1])
            if key not in best or r[4] > best[key][4]:
                best[key] = r
    return sorted(best.values(), key=lambda r: (-r[4], r[0], r[1]))


def _like_rows(
    conn: sqlite3.Connection,
    clauses: list[str],
    params: list[str],
    doc_ids: set[str] | None,
    limit: int,
    score: float,
) -> list[tuple[str, str, str, str, float]]:
    """对单个维度（title/text）跑 AND 组合的 LIKE 查询，统一记 ``score``。"""
    sql, p = _like_sql(clauses, params, doc_ids, limit)
    rows = conn.execute(sql, p).fetchall()
    return [(r["doc_id"], r["section_path"], r["title"], r["text"], score) for r in rows]


def _fts_match_query(
    conn: sqlite3.Connection,
    match: str,
    like_clauses: list[str],
    like_params: list[str],
    *,
    doc_ids: set[str] | None,
    limit: int,
) -> list[tuple[str, str, str, str, float]]:
    """执行一条 FTS MATCH 查询（可叠加 LIKE 交集与 doc_id 硬过滤）。"""
    id_clause, id_params = _id_clause(doc_ids)
    where = ["fts_chunks MATCH ?", *like_clauses]
    sql = (
        "SELECT doc_id, section_path, title, text, bm25(fts_chunks) AS r "
        "FROM fts_chunks WHERE " + " AND ".join(where) + id_clause + " ORDER BY r LIMIT ?"
    )
    rows = conn.execute(sql, [match, *like_params, *id_params, limit * 4]).fetchall()
    return [(r["doc_id"], r["section_path"], r["title"], r["text"], -float(r["r"])) for r in rows]


def _aggregate_sections(
    chunk_hits: list[tuple[str, str, str, str, float]],
    limit: int,
) -> list[tuple[str, str, str, str, float]]:
    """chunk → section 聚合（§2.2）：同 ``doc_id + section_path`` 取最高分 chunk。"""
    best: dict[tuple[str, str], tuple[str, str, float]] = {}
    for doc_id, section_path, title, text, score in chunk_hits:
        key = (doc_id, section_path)
        if key not in best or score > best[key][2]:
            best[key] = (title, text, score)
    ranked = sorted(best.items(), key=lambda kv: -kv[1][2])
    return [
        (doc_id, section_path, title, text, score)
        for (doc_id, section_path), (title, text, score) in ranked[:limit]
    ]


# ---------------------------------------------------------------------------
# 图路（结构导航）
# ---------------------------------------------------------------------------


def _sections_for_doc(conn: sqlite3.Connection, doc_id: str) -> list[tuple[str, str]]:
    """按文档反查 section（``(section_path, title)``），按 chunk 顺序去重。"""
    rows = conn.execute(
        "SELECT section_path, title FROM fts_chunks WHERE doc_id = ? "
        "GROUP BY section_path ORDER BY MIN(chunk_id)",
        (doc_id,),
    ).fetchall()
    # R-1（13 §3）：图路展示/排序匹配剥复合标签，取纯章节标题。
    return [(r["section_path"], section_title(r["title"])) for r in rows]


def _graph_chunk_hits(
    conn: sqlite3.Connection,
    query: str,
    topic_names: list[str],
    *,
    max_docs: int,
    max_sections: int,
    topic: str | None = None,
) -> tuple[list[tuple[str, str, str, str, float]], bool]:
    """图路 → chunk 级命中（section 粒度，score 记 0，RRF 只看 rank）。

    ``topic`` 非空时直接以 T 为入口（graph --topic / --topic 硬过滤，§2.6）；
    否则按查询串匹配主题词。**无主题命中 → 空列表**（不报错）；仅当 topic 稀疏
    （NULL 占比 ≥ 阈值）才退化为 corpus/doc_type 导航（P1-1）。返回
    ``(hits, degraded)``。
    """
    matched = [topic] if topic is not None else match_topics(query, topic_names)
    degraded = False
    if matched:
        placeholders = ",".join("?" for _ in matched)
        docs = conn.execute(
            f"SELECT * FROM files WHERE topic IN ({placeholders}) "
            "AND status NOT IN ('deleted','duplicate') "
            "ORDER BY CASE summary_source WHEN 'curated' THEN 0 WHEN 'auto' THEN 1 ELSE 2 END, "
            "updated_at DESC LIMIT ?",
            (*matched, max_docs),
        ).fetchall()
    elif _topic_null_ratio(conn) >= _TOPIC_SPARSE_RATIO:
        degraded = True
        docs = conn.execute(
            "SELECT * FROM files WHERE status NOT IN ('deleted','duplicate') "
            "ORDER BY corpus, doc_type, updated_at DESC LIMIT ?",
            (max_docs,),
        ).fetchall()
    else:
        return [], False

    hits: list[tuple[str, str, str, str, float]] = []
    nq = query.strip().lower()
    for row in docs:
        sections = _sections_for_doc(conn, row["doc_id"])
        # 标题/章节名命中 query 的 section 提前（§2.1 步骤 4）。
        sections.sort(key=lambda st: nq not in st[0].lower() and nq not in st[1].lower())
        for section_path, title in sections:
            if len(hits) >= max_sections:
                return hits, degraded
            hits.append((row["doc_id"], section_path, title, "", 0.0))
    return hits, degraded


# ---------------------------------------------------------------------------
# RRF 融合
# ---------------------------------------------------------------------------


def _rrf(
    fts_ranked: list[tuple[str, str, str, str, float]],
    graph_ranked: list[tuple[str, str, str, str, float]],
    *,
    rrf_k: int,
    w_fts: float,
    w_graph: float,
) -> list[tuple[str, str, str, str, float]]:
    """加权 RRF（§2.1）：``score = Σ w_i / (rrf_k + rank_i)``。

    title/text 保留**有正文**的那一路（图路 text 为空，不覆盖全文路的摘要片段）。
    """
    scores: dict[tuple[str, str], float] = {}
    meta: dict[tuple[str, str], tuple[str, str]] = {}
    for rank, (doc_id, sp, title, text, _) in enumerate(fts_ranked):
        key = (doc_id, sp)
        scores[key] = scores.get(key, 0.0) + w_fts / (rrf_k + rank + 1)
        if key not in meta or (text and not meta[key][1]):
            meta[key] = (title, text)
    for rank, (doc_id, sp, title, text, _) in enumerate(graph_ranked):
        key = (doc_id, sp)
        scores[key] = scores.get(key, 0.0) + w_graph / (rrf_k + rank + 1)
        if key not in meta or (text and not meta[key][1]):
            meta[key] = (title, text)
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    return [(doc_id, sp, *meta[(doc_id, sp)], score) for (doc_id, sp), score in ranked]


# ---------------------------------------------------------------------------
# 结果富化 + 编排
# ---------------------------------------------------------------------------


def _enrich(
    conn: sqlite3.Connection,
    fused: list[tuple[str, str, str, str, float]],
) -> list[SearchHit]:
    """把 section 级融合结果富化为 :class:`SearchHit`（补 files 元数据 + snippet）。"""
    out: list[SearchHit] = []
    for doc_id, section_path, title, text, score in fused:
        row = conn.execute("SELECT * FROM files WHERE doc_id = ?", (doc_id,)).fetchone()
        if row is None:
            continue
        out.append(
            SearchHit(
                doc_id=doc_id,
                path=row["path"],
                section_path=section_path,
                title=title or section_path,
                score=round(score, 6),
                corpus=row["corpus"],
                doc_type=row["doc_type"],
                topic=row["topic"],
                snippet=(text or title or "")[:_SNIPPET_LEN],
            )
        )
    return out


def search(
    registry: Registry,
    cfg: Any,
    query: str,
    *,
    mode: str = "hybrid",
    topic: str | None = None,
    limit: int = 10,
    llm: Any = None,
) -> SearchResult:
    """检索编排（11 §2 / §2.6）。

    - ``hybrid``：两路加权 RRF（默认）
    - ``graph``：仅图路（结构导航清单，不融合不重排）
    - 其余 mode（``vector`` / ``topic-global``）由 CLI 层处理，这里不进入。
    """
    rrf_k = int(cfg.get("retrieve.rrf_k", 60))
    graph_cfg = cfg.get("search.graph", {}) or {}
    max_docs = int(graph_cfg.get("max_docs", 20))
    max_sections = int(graph_cfg.get("max_sections", 40))
    w_graph = float(graph_cfg.get("weight", 0.5))
    synonyms = merged_synonyms(cfg.get("search.synonyms", {}) or {})
    query_expansion = bool(cfg.get("search.query_expansion", True))

    # LLM 查询扩展（一次，供 FTS 与图路共用，P2-4）。
    extra_terms: list[str] = []
    if query_expansion and llm is not None:
        qe_max_tokens = int(cfg.get("search.query_expansion_max_tokens", 1024))
        extra_terms = [
            t for t in llm_expand_query(llm, query, max_tokens=qe_max_tokens) if t not in query
        ]
    expanded_query = (query + " " + " ".join(extra_terms)).strip() if extra_terms else query

    with registry.read_only() as conn:
        topic_names = [t.name for t in list_topics(conn)]

        # --topic T 的文档集（前置硬过滤，P1-2）。
        topic_docs: set[str] | None = None
        if topic is not None:
            topic_docs = {
                r["doc_id"]
                for r in conn.execute(
                    "SELECT doc_id FROM files WHERE topic = ? "
                    "AND status NOT IN ('deleted','duplicate')",
                    (topic,),
                ).fetchall()
            }

        graph_hits, degraded = _graph_chunk_hits(
            conn,
            expanded_query,
            topic_names,
            max_docs=max_docs,
            max_sections=max_sections,
            topic=topic,
        )
        if mode == "graph":
            return SearchResult(
                hits=_enrich(conn, graph_hits[:limit]),
                mode=mode,
                note="结构导航（图路）",
                graph_degraded=degraded,
            )

        fts_hits = _aggregate_sections(
            _fts_chunk_hits(
                conn,
                query,
                synonyms,
                extra_terms=extra_terms,
                doc_ids=topic_docs,
                limit=limit,
                exact_boost=float(cfg.get("search.exact_boost", 1.3)),
            ),
            limit=max_sections,
        )

        if topic is not None:
            fused = fts_hits[:limit]  # --topic 前置硬过滤，不进 RRF
        else:
            fused = _rrf(fts_hits, graph_hits, rrf_k=rrf_k, w_fts=1.0, w_graph=w_graph)

        hits = _enrich(conn, fused[:limit])

    # LLM 重排（11 §2.4，可选；失败静默回退 RRF 原序）。
    if mode == "hybrid" and bool(cfg.get("search.rerank.enabled", True)) and llm is not None:
        top_k = int(cfg.get("search.rerank.top_k", 20))
        rr_max_tokens = int(cfg.get("search.rerank.max_tokens", 1024))
        hits = _rerank(llm, query, hits, top_k, max_tokens=rr_max_tokens)

    note = ""
    if degraded:
        note = "主题未确认占比高，图路退化为 corpus/doc_type 导航；建议 kb index set-topic 改判。"
    return SearchResult(hits=hits, mode=mode, note=note, graph_degraded=degraded)


def _rerank(
    llm: Any,
    query: str,
    hits: list[SearchHit],
    top_k: int,
    *,
    max_tokens: int = 1024,
) -> list[SearchHit]:
    """LLM 重排（§2.4）：对 top-K 打相关性分重排，失败静默回退原序。

    ``max_tokens`` 默认 1024（推理模型 think 计入 completion 预算，256 会
    被吃光导致静默零重排——M3 DoD 复核修复）。
    """
    if not hits or len(hits) < 2:
        return hits
    candidates = hits[:top_k]
    lines = "\n".join(f"[{i}] {h.title}: {h.snippet[:80]}" for i, h in enumerate(candidates))
    prompt = (
        "Rank the following passages by relevance to the query. "
        'Reply with JSON only: {"ranking": [indices most→least relevant]}.\n\n'
        f"Query: {query}\n\n{lines}"
    )
    try:
        raw = llm.complete(
            [{"role": "user", "content": prompt}],
            json_mode=True,
            max_tokens=max_tokens,
            purpose="rerank",
        )
        data = json.loads(raw)
        order = [
            int(i)
            for i in data.get("ranking", [])
            if isinstance(i, (int, float)) and 0 <= int(i) < len(candidates)
        ]
    except Exception:
        return hits
    seen: set[int] = set()
    deduped: list[int] = []
    for i in order:
        if i not in seen:
            seen.add(i)
            deduped.append(i)
    deduped += [i for i in range(len(candidates)) if i not in seen]
    return [candidates[i] for i in deduped] + hits[top_k:]


def topic_panorama(
    registry: Registry,
    cfg: Any,
    *,
    topic: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """主题全景（11 §2.6 `topic-global`）：返回主题分组的文档清单 + L1。

    每个条目：``{name, doc_count, docs: [{doc_id, path, title, snippet}]}``。
    """
    with registry.read_only() as conn:
        topics = list_topics(conn)
        if topic is not None:
            topics = [t for t in topics if t.name == topic]
        out: list[dict[str, Any]] = []
        for t in topics:
            docs = list_files(conn, topic=t.name, limit=limit)
            entries = [
                {
                    "doc_id": f.doc_id,
                    "path": f.path,
                    "title": f.title or f.path,
                    "snippet": _l1_snippet(conn, f),
                }
                for f in docs
                if f.status not in ("deleted", "duplicate")
            ]
            out.append({"name": t.name, "doc_count": t.doc_count, "docs": entries})
        return out


def _l1_snippet(conn: sqlite3.Connection, f: Any) -> str:
    """取文档 L1 摘要片段（$summary 伪 chunk 的 text），无则 title 回退。"""
    row = conn.execute(
        "SELECT text FROM fts_chunks WHERE doc_id = ? AND section_path = ?",
        (f.doc_id, SUMMARY_SECTION),
    ).fetchone()
    if row:
        return row["text"][:_SNIPPET_LEN]
    return (f.title or f.path)[:_SNIPPET_LEN]


__all__ = [
    "SUMMARY_SECTION",
    "TITLE_SEP",
    "SearchHit",
    "SearchResult",
    "search",
    "section_title",
    "topic_panorama",
]
