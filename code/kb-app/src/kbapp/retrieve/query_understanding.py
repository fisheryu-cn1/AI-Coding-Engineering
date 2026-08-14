"""查询理解（M3；设计 11 §2.1/§2.2/§2.3）。

职责：查询串归一化、主题词匹配、同义/缩写确定性扩展，以及可选的 LLM 查询
扩展。全部纯函数（除 :func:`llm_expand_query`）便于单测。

关键口径（11 §2.1/§2.2/§2.3）：

- ``norm()`` 双向应用（查询串与 ``topics.name``）：小写 → CamelCase 拆词 →
  连字符/下划线/空白归一为单空格 → 去标点 → trim。
- 主题匹配：``norm(topic)`` 作为词序列出现于 ``norm(query)``；ASCII 片段要求
  词边界（防 ``AI`` 误中 ``contain`` 类）、CJK 片段允许子串。
- 短查询（< 3 字符）ASCII 缩写走确定性扩展表（内置 + 用户配置合并），禁用裸
  ``LIKE '%AI%'``。
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any

#: CamelCase 拆词（``ContextEngineering`` → ``context engineering``）。
_CAMEL_SPLIT_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")

#: 本域高频缩写/中英同义内置表（11 §2.2/§2.3，随版本迭代）。查询期与 config
#: ``search.synonyms`` 合并，同名键用户配置覆盖内置。
BUILTIN_SYNONYMS: dict[str, list[str]] = {
    "ai": ["artificial intelligence", "人工智能"],
    "kg": ["knowledge graph", "知识图谱"],
    "rag": ["retrieval augmented generation", "检索增强生成"],
    "llm": ["large language model", "大语言模型"],
    "mcp": ["model context protocol"],
    "rl": ["reinforcement learning", "强化学习"],
    "nlp": ["natural language processing", "自然语言处理"],
    "ir": ["information retrieval", "信息检索"],
    "ml": ["machine learning", "机器学习"],
}

#: CJK 判断区间（简中 + 日文假名，足够覆盖本域语料）。
_CJK_MIN, _CJK_MAX = "一", "鿿"


def norm(s: str) -> str:
    """统一归一化（11 §2.1）：小写 → CamelCase 拆词 → 符号归一 → 单空格 → trim。"""
    s = _CAMEL_SPLIT_RE.sub(" ", s).lower()
    s = re.sub(r"[\s_\-]+", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def is_cjk(s: str) -> bool:
    """True if any character falls in the CJK range."""
    return any(_CJK_MIN <= ch <= _CJK_MAX for ch in s)


def split_terms(query: str) -> list[str]:
    """把查询串按空白拆成词元（CJK 无空白则整串为单词元）。"""
    return [t for t in re.split(r"\s+", query.strip()) if t]


def merged_synonyms(cfg_synonyms: dict[str, Any] | None) -> dict[str, list[str]]:
    """内置同义表 + 用户 config 合并；键统一小写，用户覆盖内置（11 §2.2）。"""
    out: dict[str, list[str]] = {k: list(v) for k, v in BUILTIN_SYNONYMS.items()}
    for key, vals in (cfg_synonyms or {}).items():
        k = str(key).strip().lower()
        if not k:
            continue
        if isinstance(vals, str):
            vals = [vals]
        out[k] = [str(v) for v in vals] if vals else []
    return out


def match_topics(query: str, topic_names: Iterable[str]) -> list[str]:
    """返回查询串命中的主题名（norm 等价，含碰撞组，11 §2.1/四轮 #3）。

    ASCII 主题要求词边界；CJK 主题允许子串。
    """
    q = norm(query)
    return [name for name in topic_names if _match_topic(norm(name), q)]


def _match_topic(norm_topic: str, norm_query: str) -> bool:
    if not norm_topic:
        return False
    if is_cjk(norm_topic):
        return norm_topic in norm_query
    return re.search(rf"\b{re.escape(norm_topic)}\b", norm_query) is not None


def llm_expand_query(
    llm: Any,
    query: str,
    *,
    max_tokens: int = 1024,
    doc_id: str | None = None,
) -> list[str]:
    """LLM 查询扩展（11 §2.3）：返回同义/中英互译候选词；失败返回空列表。

    ``json_mode=True``，``purpose='query_expand'``；任何异常（LLM 不可用 / 解析
    失败）静默回退空列表，检索继续用原始查询。``max_tokens`` 默认 1024——推理
    模型（MiniMax-M3 等）的 think 开销计入 completion 预算，128 会被吃光导致
    静默零扩展（M3 DoD 复核修复）。
    """
    if llm is None:
        return []
    prompt = (
        "Expand the query into search keywords (synonyms and Chinese/English "
        "translations) to improve recall. Reply with JSON only: "
        '{"terms": ["...", "..."]}.\n\nQuery: ' + query
    )
    try:
        raw = llm.complete(
            [{"role": "user", "content": prompt}],
            json_mode=True,
            max_tokens=max_tokens,
            purpose="query_expand",
            doc_id=doc_id,
        )
        data = json.loads(raw)
        terms = data.get("terms", [])
        return [t for t in terms if isinstance(t, str) and t.strip()]
    except Exception:
        return []


__all__ = [
    "BUILTIN_SYNONYMS",
    "is_cjk",
    "llm_expand_query",
    "match_topics",
    "merged_synonyms",
    "norm",
    "split_terms",
]
