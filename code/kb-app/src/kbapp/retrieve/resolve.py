"""Doc 引用解析（M4；13 §2.1）：doc_id / 路径 / 标题片段 → FileRow。

CLI 与 MCP 共用，避免分层倒挂（原 ``cli/search.py:_resolve_doc`` 提升而来，
13 §2.1 P2-1）。解析优先级：doc_id 精确 → path 精确 → path 后缀 / title
子串（须唯一）；多文档歧义命中不回"首个"，返回候选路径供上层构造
``DOC_NOT_FOUND``（带候选，suggestion 引导 ``kb_search`` 或补全路径消歧）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kbapp.core.registry import FileRow, Registry, get_file, get_file_by_path, list_files


@dataclass
class ResolveResult:
    """doc 引用解析结果：命中返回 ``row``；歧义时 ``row=None`` 且带候选 path。"""

    row: FileRow | None = None
    candidates: list[str] = field(default_factory=list)


def resolve_doc(registry: Registry, ref: str) -> ResolveResult:
    """按优先级解析 ``ref``；歧义/未命中时 ``row`` 为 ``None``。

    - doc_id 精确（``get_file``）
    - path 精确（``get_file_by_path``）
    - path 后缀 / title 子串（须唯一命中；多命中回 ``candidates``）
    """
    ref = (ref or "").strip()
    if not ref:
        return ResolveResult()
    with registry.read_only() as conn:
        row = get_file(conn, ref)
        if row is not None:
            return ResolveResult(row=row)
        exact = get_file_by_path(conn, ref)
        if exact is not None:
            return ResolveResult(row=exact)
        hits = [
            r
            for r in list_files(conn, limit=100_000)
            if r.status not in ("deleted", "duplicate")
            and (r.path.endswith(ref) or (r.title and ref in r.title))
        ]
        if len(hits) == 1:
            return ResolveResult(row=hits[0])
        if len(hits) > 1:
            return ResolveResult(candidates=[r.path for r in hits])
        return ResolveResult()


__all__ = ["ResolveResult", "resolve_doc"]
