"""MCP 服务（M4；13 §2）：stdio + 四只读工具，薄封装 :mod:`kbapp.retrieve`。

四工具 ``kb_search`` / ``kb_show`` / ``kb_read`` / ``kb_assemble_context`` 只做
参数校验 → 调 retrieve 既有能力 → 装配 JSON 返回，**不含业务逻辑**（13 §2.1）。
工具出错不抛异常到协议层，返回统一错误结构 ``{error:{code,message,suggestion}}``。

M4 错误码子集（13 §2.2）：``DOC_NOT_FOUND``（含歧义）/ ``SECTION_NOT_FOUND`` /
``MODE_NOT_READY``（vector 与非法 mode）/ ``CONFIG_INVALID`` / ``INTERNAL``
（兜底，message 不含堆栈；只读路径 SQLite busy 归此码）。``LOCK_HELD`` 留 P1
写工具，本进程只读、永不取应用级写锁。

依赖 ``mcp>=1.29,<2``（官方 v1 稳定线，``uv.lock`` 钉版）；未安装时由
:mod:`kbapp.cli.serve` 在 ``kb serve mcp`` 入口显式报错。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from kbapp.core.config import Config, ConfigError, load_config
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry
from kbapp.llm import get_llm_or_none
from kbapp.retrieve import assemble_for_task, resolve_doc, search
from kbapp.retrieve.assembler import read_section, read_summary, section_tree
from kbapp.retrieve.hybrid import topic_panorama

mcp = FastMCP("graphit-kb")

#: 合法检索模式（13 §2.2；vector 为 P1 目标态，M4 显式 MODE_NOT_READY）。
_SEARCH_MODES = ("hybrid", "graph", "topic-global")


def _error(code: str, message: str, suggestion: str | None = None) -> dict[str, Any]:
    """统一错误结构（04 §4.3 / 05 §6），恒产出 ``{code,message,suggestion}`` 三键。

    ``suggestion`` 缺省为空串（非省略键），保证契约形状稳定、DoD-3 可断言
    三键集合（13 §2.2 评审 P2-3）。
    """
    return {"error": {"code": code, "message": message, "suggestion": suggestion or ""}}


# ---------------------------------------------------------------------------
# 只读状态（懒初始化，进程内缓存）
# ---------------------------------------------------------------------------

_state_cache: tuple[Registry, Config] | None = None


def _state() -> tuple[Registry, Config]:
    """懒加载 registry + config（数据目录经 env 或默认 ~/.graphit-kb 寻址）。"""
    global _state_cache
    if _state_cache is None:
        data_dir = os.environ.get("GRAPHIT_KB_DATA_DIR") or "~/.graphit-kb"
        paths = DataPaths.from_data_dir(Path(data_dir).expanduser())
        paths.ensure_dirs()
        cfg = load_config(paths.config_path)
        registry = Registry(paths.registry_db)
        registry.initialize()
        _state_cache = (registry, cfg)
    return _state_cache


# ---------------------------------------------------------------------------
# 工具实现（薄封装 retrieve）
# ---------------------------------------------------------------------------


def _kb_search(query: str, mode: str, topic: str | None, limit: int) -> dict[str, Any]:
    registry, cfg = _state()
    if mode == "vector" or mode not in _SEARCH_MODES:
        return _error(
            "MODE_NOT_READY",
            f"mode={mode!r} 未就绪（允许 {'|'.join(_SEARCH_MODES)}；vector 为 P1 目标态）",
        )
    if mode == "topic-global":
        groups = topic_panorama(registry, cfg, topic=topic, limit=limit)
        return {"topics": groups, "note": ""}
    llm = get_llm_or_none(cfg)
    result = search(registry, cfg, query, mode=mode, topic=topic, limit=limit, llm=llm)
    return {
        "hits": [
            {
                "doc_id": h.doc_id,
                "section_path": h.section_path,
                "title": h.title,
                "score": h.score,
                "snippet": h.snippet,
                "topic": h.topic,
            }
            for h in result.hits
        ],
        "note": result.note,
    }


def _kb_show(doc: str) -> dict[str, Any]:
    registry, _cfg = _state()
    res = resolve_doc(registry, doc)
    if res.row is None:
        if res.candidates:
            return _error(
                "DOC_NOT_FOUND",
                f"文档引用歧义：{doc!r} 命中多篇：{', '.join(res.candidates)}",
                "call kb_search to resolve title to doc_id 或补全路径消歧",
            )
        return _error(
            "DOC_NOT_FOUND",
            f"找不到文档 {doc!r}",
            "call kb_search to resolve title to doc_id",
        )
    row = res.row
    return {
        "doc_id": row.doc_id,
        "path": row.path,
        "title": row.title,
        "corpus": row.corpus,
        "doc_type": row.doc_type,
        "topic": row.topic,
        "status": row.status,
        "summary_source": row.summary_source,
        "summary": read_summary(registry, row),
        "sections": section_tree(registry, row.doc_id),
    }


def _kb_read(doc: str, section: str) -> dict[str, Any]:
    registry, _cfg = _state()
    res = resolve_doc(registry, doc)
    if res.row is None:
        if res.candidates:
            return _error(
                "DOC_NOT_FOUND",
                f"文档引用歧义：{doc!r} 命中多篇：{', '.join(res.candidates)}",
                "call kb_search to resolve title to doc_id 或补全路径消歧",
            )
        return _error(
            "DOC_NOT_FOUND",
            f"找不到文档 {doc!r}",
            "call kb_search to resolve title to doc_id",
        )
    text = read_section(registry, res.row.doc_id, section)
    if text is None:
        return _error(
            "SECTION_NOT_FOUND",
            f"章节不存在 {section!r}",
            "call kb_show to list sections",
        )
    return {"doc_id": res.row.doc_id, "section_path": section, "text": text}


def _kb_assemble_context(task: str, budget: int, topics: list[str] | None) -> dict[str, Any]:
    registry, cfg = _state()
    return assemble_for_task(registry, cfg, task, budget=budget, topics=topics)


# ---------------------------------------------------------------------------
# FastMCP 声明
# ---------------------------------------------------------------------------


@mcp.tool()
def kb_search(
    query: str,
    mode: str = "hybrid",
    topic: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """检索知识库，返回章节级命中（锚点 + 得分 + 摘要片段）。

    mode：hybrid（默认，FTS + 结构导航加权融合）｜graph（结构导航清单）｜
    topic-global（主题全景）。vector 与非法 mode 返回 MODE_NOT_READY。
    """
    try:
        return _kb_search(query, mode, topic, limit)
    except ConfigError:
        return _error("CONFIG_INVALID", "配置无效，请检查 config.yaml")
    except Exception:
        return _error("INTERNAL", "检索内部错误，请稍后重试")


@mcp.tool()
def kb_show(doc: str) -> dict[str, Any]:
    """查看一篇资料的元数据 + 章节树 + 摘要。

    ``doc`` 可为 doc_id（Dxxxx）、路径或标题片段（歧义命中返回 DOC_NOT_FOUND 带候选）。
    """
    try:
        return _kb_show(doc)
    except ConfigError:
        return _error("CONFIG_INVALID", "配置无效，请检查 config.yaml")
    except Exception:
        return _error("INTERNAL", "查阅内部错误，请稍后重试")


@mcp.tool()
def kb_read(doc: str, section: str) -> dict[str, Any]:
    """读取章节原文。

    ``section`` 为 section_path（如 ``§1 引言``），``$summary`` 哨兵读摘要产物全文。
    """
    try:
        return _kb_read(doc, section)
    except ConfigError:
        return _error("CONFIG_INVALID", "配置无效，请检查 config.yaml")
    except Exception:
        return _error("INTERNAL", "读取内部错误，请稍后重试")


@mcp.tool()
def kb_assemble_context(
    task: str,
    budget: int = 8000,
    topics: list[str] | None = None,
) -> dict[str, Any]:
    """按任务检索并组装提示词上下文块（预算 + 溯源锚点，确定性路径无 LLM）。"""
    try:
        return _kb_assemble_context(task, budget, topics)
    except ConfigError:
        return _error("CONFIG_INVALID", "配置无效，请检查 config.yaml")
    except Exception:
        return _error("INTERNAL", "组装内部错误，请稍后重试")


__all__ = ["mcp"]
