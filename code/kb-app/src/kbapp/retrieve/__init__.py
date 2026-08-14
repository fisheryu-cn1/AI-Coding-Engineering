"""检索（M3；设计 11 §2）。

无向量 MVP 两路召回：FTS5 全文路 + SQLite 结构导航图路，section 粒度加权
RRF 融合，可选 LLM 查询扩展与重排。模块划分：

- :mod:`kbapp.retrieve.query_understanding` — 查询归一化 / 同义扩展 / 主题匹配
- :mod:`kbapp.retrieve.hybrid` — 两路召回 + RRF 融合
- :mod:`kbapp.retrieve.assembler` — 上下文组装（token 预算）+ 渐进展开
"""

from kbapp.retrieve.assembler import assemble_context, assemble_for_task
from kbapp.retrieve.hybrid import SearchHit, search
from kbapp.retrieve.resolve import ResolveResult, resolve_doc

__all__ = [
    "ResolveResult",
    "SearchHit",
    "assemble_context",
    "assemble_for_task",
    "resolve_doc",
    "search",
]
