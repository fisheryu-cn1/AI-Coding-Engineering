"""Integration tests: M4 MCP 服务（kb serve mcp；13 §2/§6）。

覆盖 DoD-1（stdio 握手 + 四工具）、DoD-2（契约形状：复合/剥离 title、$summary
哨兵、路径片段解析、退化 note）、DoD-3（错误结构）、DoD-4（未装 mcp 显式报错）。
e2e 用真实 MCP client 会话（stdio 子进程），非 mock 函数级。
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from kbapp.core.paths import DataPaths
from kbapp.core.registry import (
    Registry,
    insert_chunk,
    update_file_fields,
    upsert_file,
    upsert_topic,
)


def _seed(data_dir: Path) -> None:
    """播 2 篇文档（1 篇有 topic + 复合 title 章节、1 篇无 topic）+ D0001 摘要。"""
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    reg = Registry(paths.registry_db)
    reg.initialize()
    with reg.transaction() as conn:
        upsert_topic(conn, name="CodeGraph")
        upsert_file(
            conn,
            doc_id="D0001",
            path="/c/kg.md",
            sha256="s1",
            mtime=0,
            corpus="design",
            status="active",
            extract_status="ok",
            title="Knowledge Graph",
            topic="CodeGraph",
        )
        # 复合 title（R-1）：kb_search 保留复合、kb_show 剥离。
        insert_chunk(
            conn,
            chunk_id="D0001#c001",
            doc_id="D0001",
            section_path="§1 Graph",
            title="kg | Graph",
            text="A knowledge graph stores entities and relationships.",
        )
        upsert_file(
            conn,
            doc_id="D0002",
            path="/c/note.md",
            sha256="s2",
            mtime=0,
            corpus="research",
            status="active",
            extract_status="ok",
            title="Graph Notes",
            topic=None,
        )
        insert_chunk(
            conn,
            chunk_id="D0002#c001",
            doc_id="D0002",
            section_path="§1 Note",
            title="Note",
            text="unrelated note about cooking recipes.",
        )
        # D0001 摘要文件（供 kb_read $summary 哨兵）。
        summary_path = data_dir / "summaries" / "D0001.md"
        summary_path.parent.mkdir(exist_ok=True)
        summary_path.write_text("# Summary\n\nThis is the summary.\n", encoding="utf-8")
        update_file_fields(
            conn,
            "D0001",
            summary_source="auto",
            summary_path=str(summary_path),
            summary_stale=0,
        )


def _params(data_dir: Path) -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "kbapp.cli.main", "serve", "mcp"],
        env={**os.environ, "GRAPHIT_KB_DATA_DIR": str(data_dir)},
    )


def _call_json(result) -> dict:
    assert not result.isError, result
    assert result.content
    return json.loads(result.content[0].text)


def _run(coro):
    return asyncio.run(coro)


def test_mcp_handshake_and_four_tools(tmp_path: Path) -> None:
    """DoD-1：initialize → tools/list 恰含 M4 四工具 + M5 三只读图工具。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = {t.name for t in tools.tools}
                assert names == {
                    "kb_search",
                    "kb_show",
                    "kb_read",
                    "kb_assemble_context",
                    # M5 MCP 三只读图工具（15 §5.2；图库缺失时返 MODE_NOT_READY）
                    "kb_related",
                    "kb_compare",
                    "kb_topics",
                }
                out = _call_json(await session.call_tool("kb_search", {"query": "knowledge graph"}))
                assert out["hits"]
                assert out["hits"][0]["doc_id"] == "D0001"
                # kb_topics 不依赖图库——必返回空 topics（无图状态下不走图）
                topics = _call_json(await session.call_tool("kb_topics", {}))
                assert "topics" in topics

    _run(_go())


def test_mcp_graph_tools_unavailable_without_reindex(tmp_path: Path) -> None:
    """M5 MCP 工具：图库缺失时 kb_related / kb_compare 返 MODE_NOT_READY。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # 图库文件不存在 → MODE_NOT_READY
                r = await session.call_tool(
                    "kb_related", {"target": "Method:rag", "type": "Entity"}
                )
                err = json.loads(r.content[0].text)["error"]
                assert err["code"] == "MODE_NOT_READY"
                assert "reindex" in err["suggestion"]

                r = await session.call_tool(
                    "kb_compare", {"concept": "Method:rag", "doc_ids": ["D0001"]}
                )
                err = json.loads(r.content[0].text)["error"]
                assert err["code"] == "MODE_NOT_READY"

    _run(_go())


def test_mcp_contract_shapes(tmp_path: Path) -> None:
    """DoD-2：kb_search 复合 title / kb_show 剥离 title / kb_read $summary / 路径片段。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # FTS 路 kb_search.hits[].title 保留复合标签；字段集合完整（P2-5）。
                s = _call_json(await session.call_tool("kb_search", {"query": "knowledge graph"}))
                assert set(s) == {"hits", "note"}
                assert set(s["hits"][0]) == {
                    "doc_id",
                    "section_path",
                    "title",
                    "score",
                    "snippet",
                    "topic",
                }
                assert s["hits"][0]["title"] == "kg | Graph"
                # kb_show.sections[].title 剥离 stem；字段集合完整（P2-5）。
                show = _call_json(await session.call_tool("kb_show", {"doc": "kg.md"}))
                assert show["doc_id"] == "D0001"
                assert set(show) == {
                    "doc_id",
                    "path",
                    "title",
                    "corpus",
                    "doc_type",
                    "topic",
                    "status",
                    "summary_source",
                    "summary",
                    "sections",
                }
                assert show["sections"] == [{"section_path": "§1 Graph", "title": "Graph"}]
                # kb_read $summary 哨兵读摘要全文。
                read = _call_json(
                    await session.call_tool("kb_read", {"doc": "D0001", "section": "$summary"})
                )
                assert "This is the summary." in read["text"]

    _run(_go())


def test_mcp_graph_degradation_note(tmp_path: Path) -> None:
    """DoD-2：topic 稀疏时 kb_search.note 承载图路退化提示（NULL 占比 1/2 ≥ 0.5）。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                s = _call_json(await session.call_tool("kb_search", {"query": "cooking recipes"}))
                assert "退化" in s["note"]

    _run(_go())


def test_mcp_error_structures(tmp_path: Path) -> None:
    """DoD-3：DOC_NOT_FOUND（歧义）/ SECTION_NOT_FOUND / MODE_NOT_READY（vector + 非法）。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # 歧义命中 D0001/D0002；三键形状 + message 列候选（P2-1/P2-3）。
                r = await session.call_tool("kb_show", {"doc": "Graph"})
                err = json.loads(r.content[0].text)["error"]
                assert set(err) == {"code", "message", "suggestion"}
                assert err["code"] == "DOC_NOT_FOUND"
                assert "/c/kg.md" in err["message"] and "/c/note.md" in err["message"]
                assert "kb_search" in err["suggestion"]
                # SECTION_NOT_FOUND（三键形状）。
                r = await session.call_tool("kb_read", {"doc": "D0001", "section": "§9 Nope"})
                err = json.loads(r.content[0].text)["error"]
                assert set(err) == {"code", "message", "suggestion"}
                assert err["code"] == "SECTION_NOT_FOUND"
                # vector 与非法 mode → MODE_NOT_READY（message 含合法枚举）。
                for mode in ("vector", "bogus"):
                    r = await session.call_tool("kb_search", {"query": "x", "mode": mode})
                    err = json.loads(r.content[0].text)["error"]
                    assert set(err) == {"code", "message", "suggestion"}
                    assert err["code"] == "MODE_NOT_READY"
                    assert "hybrid" in err["message"]

    _run(_go())


def test_mcp_assemble_context_session_call(tmp_path: Path) -> None:
    """DoD-1/P1-2：`kb_assemble_context` 经 MCP client 会话调用，断言返回形状。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                out = _call_json(
                    await session.call_tool(
                        "kb_assemble_context", {"task": "knowledge graph", "budget": 8000}
                    )
                )
                assert set(out) == {"context_block", "budget", "used", "sources"}
                assert "D0001" in out["context_block"]
                assert out["budget"] == 8000
                # 相关文档 D0001 必在 sources（图路退化可能额外带入 D0002）。
                assert "D0001" in {s["doc_id"] for s in out["sources"]}
                assert all(s["section_path"] for s in out["sources"])
                assert out["used"] == len(out["context_block"]) // 4

    _run(_go())


def test_mcp_topic_global_mode(tmp_path: Path) -> None:
    """P2-4：`kb_search mode=topic-global` 分派 topic_panorama，返回 `{topics,...}`。"""
    data_dir = tmp_path / "data"
    _seed(data_dir)

    async def _go():
        async with stdio_client(_params(data_dir)) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                out = _call_json(
                    await session.call_tool("kb_search", {"query": "x", "mode": "topic-global"})
                )
                assert set(out) == {"topics", "note"}
                assert any(g["name"] == "CodeGraph" for g in out["topics"])

    _run(_go())


def test_serve_mcp_errors_without_mcp_extra() -> None:
    """DoD-4：未装 mcp extra 时 `kb serve mcp` 显式报错（非 ImportError 堆栈）。"""
    import builtins

    from typer.testing import CliRunner

    from kbapp.cli.serve import app

    sys.modules.pop("kbapp.mcp_server", None)
    real_import = builtins.__import__

    def _no_mcp(name, *args, **kwargs):
        if name == "mcp" or name.startswith("mcp."):
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return real_import(name, *args, **kwargs)

    runner = CliRunner()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(builtins, "__import__", _no_mcp)
        r = runner.invoke(app, ["mcp"])
    assert r.exit_code == 1
    assert "uv sync --extra mcp" in r.stdout
