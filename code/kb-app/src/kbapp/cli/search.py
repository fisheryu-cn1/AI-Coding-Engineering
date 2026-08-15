"""``kb search / show / read / related / compare / topics``（M3 落地，11 §2/§6）。

六个命令均为**顶层**命令（对齐 04 §2.1），由 :mod:`kbapp.cli.main` 逐个注册。
业务逻辑下沉到 :mod:`kbapp.retrieve`，本模块只做参数解析 + 打印。
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from kbapp.core.config import load_config
from kbapp.core.paths import DataPaths
from kbapp.core.registry import Registry, get_file, list_topics
from kbapp.graph import GraphError, make_graph_store
from kbapp.llm import get_llm_or_none
from kbapp.retrieve import SearchHit, resolve_doc
from kbapp.retrieve import search as _search
from kbapp.retrieve.assembler import (
    read_section,
    read_summary,
    section_tree,
)
from kbapp.retrieve.graph_search import graph_compare, graph_related
from kbapp.retrieve.hybrid import topic_panorama
from kbapp.retrieve.query_understanding import norm

console = Console()
err_console = Console(stderr=True)

#: 检索模式（11 §2.6）。vector 为 P1 目标态，M3 显式报错。
SEARCH_MODES = ("hybrid", "graph", "topic-global", "vector")


def _bootstrap(ctx: typer.Context) -> tuple[Registry, object, DataPaths]:
    """解析 data_dir → load config → init registry，供各命令复用。

    顺带做 embedding 档启动校验（11 §5，P2-5：所有检索命令均接线）。
    """
    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()
    cfg = load_config(paths.config_path)
    registry = Registry(paths.registry_db)
    registry.initialize()
    _warn_embedding_backend(cfg)
    return registry, cfg, paths


def _vector_deps_available() -> bool:
    """探测向量档依赖（LanceDB / bge-m3 / onnxruntime）是否可导入（11 §5）。"""
    for mod in ("lancedb", "sentence_transformers", "onnxruntime"):
        try:
            __import__(mod)
        except ImportError:
            return False
    return True


def _warn_embedding_backend(cfg) -> None:
    """embedding 档启动校验（11 §5）：非 none 档且依赖缺失 → 警告按 none 运行。"""
    backend = cfg.get("embedding.backend", "none")
    if backend != "none" and not _vector_deps_available():
        err_console.print(
            f"[yellow]向量档 embedding.backend={backend!r} 但向量依赖缺失，按 none 运行[/yellow]；"
            "可 `kb config set embedding.backend none` 消除本警告"
        )


def _resolve_or_exit(registry: Registry, ref: str):
    """doc_id / 路径 / 标题片段 → FileRow；歧义/未命中打印错误并退出（13 §2.1）。"""
    res = resolve_doc(registry, ref)
    if res.row is None:
        if res.candidates:
            err_console.print(f"[red]文档引用歧义[/red] {ref!r}，候选：{', '.join(res.candidates)}")
        else:
            err_console.print(f"[red]找不到文档[/red] {ref!r}")
        raise typer.Exit(code=1)
    return res.row


def _print_search_result(query: str, hits: list[SearchHit], note: str) -> None:
    table = Table(title=f"kb search {query!r}", show_lines=False)
    table.add_column("#", justify="right", no_wrap=True)
    table.add_column("得分", style="green", no_wrap=True)
    table.add_column("路径", style="cyan")
    table.add_column("章节", style="yellow")
    table.add_column("摘要", style="dim")
    for i, h in enumerate(hits, 1):
        table.add_row(str(i), f"{h.score:.4f}", h.path, h.section_path, h.snippet)
    console.print(table)
    if note:
        console.print(f"[dim]{note}[/dim]")
    if hits:
        console.print("[dim]锚点下钻：kb show <doc_id> / kb read <doc_id> '<section>'[/dim]")


def search_cmd(
    ctx: typer.Context,
    query: str = typer.Argument(..., help="检索查询串"),
    mode: str = typer.Option("hybrid", "--mode", help="hybrid|graph|topic-global|vector"),
    topic: str | None = typer.Option(None, "--topic", help="限定主题（硬过滤）"),
    limit: int = typer.Option(10, "--limit", help="返回条数"),
) -> None:
    """三路（MVP 两路）检索 + RRF（11 §2）。"""
    if mode not in SEARCH_MODES:
        err_console.print(f"[red]未知 mode[/red] {mode!r}（允许：{SEARCH_MODES}）")
        raise typer.Exit(code=1)
    registry, cfg, _paths = _bootstrap(ctx)

    if mode == "vector":
        err_console.print("[red]vector 模式为 P1 目标态[/red]（M3 无向量档，见 11 §2.4）")
        raise typer.Exit(code=1)

    if mode == "topic-global":
        groups = topic_panorama(registry, cfg, topic=topic, limit=limit)
        _print_topic_panorama(groups)
        return

    llm = get_llm_or_none(cfg)
    result = _search(
        registry,
        cfg,
        query,
        mode=mode,
        topic=topic,
        limit=limit,
        llm=llm,
    )
    _print_search_result(query, result.hits, result.note)


def _print_topic_panorama(groups: list[dict]) -> None:
    if not groups:
        console.print("[dim]无主题数据[/dim]")
        return
    for g in groups:
        console.print(f"[bold]{g['name']}[/bold]（{g['doc_count']} 篇）")
        for d in g["docs"]:
            console.print(f"  {d['doc_id']}  {d['path']}")
            if d["snippet"]:
                console.print(f"    [dim]{d['snippet']}[/dim]")


def show_cmd(
    ctx: typer.Context,
    doc: str = typer.Argument(..., help="doc_id（Dxxxx）或路径/标题片段"),
) -> None:
    """文档元数据 + 章节树 + 摘要（11 §2 输出侧）。"""
    registry, _cfg, _paths = _bootstrap(ctx)
    row = _resolve_or_exit(registry, doc)

    console.print(f"[bold]{row.title or row.path}[/bold]  [dim]{row.doc_id}[/dim]")
    meta = Table(show_header=False, show_lines=False)
    meta.add_column(style="cyan")
    meta.add_column(style="green")
    meta.add_row("path", row.path)
    meta.add_row("corpus", row.corpus)
    meta.add_row("doc_type", row.doc_type or "-")
    meta.add_row("topic", row.topic or "-")
    meta.add_row("status", row.status)
    meta.add_row("summary_source", row.summary_source)
    console.print(meta)

    summary = read_summary(registry, row)
    if summary:
        console.print("[bold]摘要[/bold]")
        console.print(summary)

    tree = section_tree(registry, row.doc_id)
    if tree:
        console.print(f"[bold]章节树[/bold]（{len(tree)} 节）")
        for s in tree:
            console.print(f"  {s['section_path']}")


def read_cmd(
    ctx: typer.Context,
    doc: str = typer.Argument(..., help="doc_id（Dxxxx）或路径/标题片段"),
    section: str = typer.Argument(..., help="章节 section_path，如 '$summary' / '§1 引言'"),
) -> None:
    """输出章节原文（11 §3.4；$summary 读摘要产物文件）。"""
    registry, _cfg, _paths = _bootstrap(ctx)
    row = _resolve_or_exit(registry, doc)
    text = read_section(registry, row.doc_id, section)
    if text is None:
        err_console.print(f"[red]章节不存在[/red] {section!r}")
        raise typer.Exit(code=1)
    console.print(text)


def related_cmd(
    ctx: typer.Context,
    doc: str = typer.Argument(..., help="doc_id（Dxxxx）或路径/标题片段"),
    hops: int = typer.Option(1, "--hops", help="图遍历跳数（1-3）"),
    limit: int = typer.Option(10, "--limit", help="返回条数"),
) -> None:
    """图遍历语义（15 §5.1）：基于共享 Entity / Topic 1-3 跳邻域。

    行为回归（M3 → M5）：不再回退 M3 文档级 `same-topic` 实现；图库缺失
    或 schema 不符时显式报错并提示 `kb index reindex --full`。
    """
    registry, cfg, paths = _bootstrap(ctx)
    row = _resolve_or_exit(registry, doc)

    backend = cfg.raw["graph"]["backend"]
    store = make_graph_store(backend, cfg)
    try:
        store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    except (FileNotFoundError, GraphError) as e:
        err_console.print(
            f"[red]图库不可用[/red] {e}；请先 `kb index reindex --full`"
        )
        raise typer.Exit(code=2) from None

    try:
        # 推断 target_type：先用 Document 查 1 跳关系，结果可能经由 Entity / Topic
        result = graph_related(
            store,
            target=row.doc_id,
            target_type="Document",
            hops=hops,
            limit=limit,
        )
    finally:
        store.close()

    console.print(f"[bold]与 {row.doc_id} 相关（{hops} 跳邻域）[/bold]")
    if not result["related"]:
        console.print("  [dim]无邻域节点[/dim]")
        return
    for r in result["related"]:
        console.print(f"  [{r['type']}] {r['id']}")


def compare_cmd(
    ctx: typer.Context,
    docs: str = typer.Option(..., "--docs", help="逗号分隔的 doc_id，如 D0001,D0002"),
    limit: int = typer.Option(5, "--limit", help="关系条数"),
) -> None:
    """图遍历语义（15 §5.1）：基于共享 Entity / Topic 的 RELATES_TO 对照表。

    行为回归（M3 → M5）：依赖图库，不静默回退 M3 摘要对比。
    """
    registry, cfg, paths = _bootstrap(ctx)
    doc_ids = [d.strip() for d in docs.split(",") if d.strip()]
    if len(doc_ids) < 2:
        err_console.print("[red]compare 需 ≥2 个文档[/red]（--docs a,b[,c]）")
        raise typer.Exit(code=1)

    # 校验 doc_id 都存在
    with registry.read_only() as conn:
        rows = [(d, get_file(conn, d)) for d in doc_ids]
    for doc_id, row in rows:
        if row is None:
            err_console.print(f"[red]找不到文档[/red] {doc_id}")
            raise typer.Exit(code=1)

    backend = cfg.raw["graph"]["backend"]
    store = make_graph_store(backend, cfg)
    try:
        store.open(str(paths.graph_dir / "graph.lbug"), "ro")
    except (FileNotFoundError, GraphError) as e:
        err_console.print(
            f"[red]图库不可用[/red] {e}；请先 `kb index reindex --full`"
        )
        raise typer.Exit(code=2) from None

    try:
        # 以 doc_ids 第一个文档的某 Entity 为主（若 graph 不支持文档级 concept
        # 推断则取共享概念）。MVP：以 First doc 共享的 Entity 为 concept 兜底。
        # 简化：直接以 doc_ids 列表传给 graph_compare，前端按 docs 过滤显示。
        # 这里采用"概念名 = 第一个 doc_id"作为 MVP 兜底（UI 端可调整）。
        rows_data = []
        for d in doc_ids:
            # 语义：MVP 阶段直接按 doc_id 关联的 entity 聚合
            result = graph_related(
                store,
                target=d,
                target_type="Document",
                hops=1,
                limit=10,
            )
            for r in result["related"]:
                if r["type"] == "Entity":
                    cmp = graph_compare(
                        store,
                        concept=r["id"],
                        limit=limit,
                    )
                    for row in cmp["rows"]:
                        row["concept"] = r["id"]
                        row["doc_id"] = d
                        rows_data.append(row)
    finally:
        store.close()

    if not rows_data:
        console.print("[dim]（这些文档之间没有共享实体关系）[/dim]")
        return

    table = Table(title=f"compare {docs!r}", show_lines=False)
    table.add_column("concept", style="cyan")
    table.add_column("doc_id", style="green")
    table.add_column("kind", style="yellow")
    table.add_column("src", style="dim")
    table.add_column("dst", style="dim")
    table.add_column("evidence", style="dim")
    for r in rows_data:
        table.add_row(
            r.get("concept", ""),
            r.get("doc_id", ""),
            r.get("kind", ""),
            r.get("src", ""),
            r.get("dst", ""),
            r.get("evidence_section_id", ""),
        )
    console.print(table)


def topics_cmd(ctx: typer.Context) -> None:
    """主题清单与规模（11 §2.1 norm 碰撞提示）。"""
    registry, _cfg, _paths = _bootstrap(ctx)
    with registry.read_only() as conn:
        topics = list_topics(conn)
    if not topics:
        console.print("[dim]无主题[/dim]")
        return
    table = Table(title="topics", show_lines=False)
    table.add_column("name", style="cyan", no_wrap=True)
    table.add_column("doc_count", style="green")
    table.add_column("description", style="dim")
    for t in topics:
        table.add_row(t.name, str(t.doc_count), t.description or "")
    console.print(table)

    # norm 碰撞提示（11 §2.1 四轮 #3，P2-3）
    collisions = _norm_collision_groups([t.name for t in topics])
    for names in collisions:
        console.print(
            f"[yellow]主题名归一化碰撞[/yellow]：{', '.join(names)}"
            " → 建议 `kb index set-topic` 归并"
        )


def _norm_collision_groups(names: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = {}
    for n in names:
        groups.setdefault(norm(n), []).append(n)
    return [v for v in groups.values() if len(v) > 1]


__all__ = [
    "compare_cmd",
    "read_cmd",
    "related_cmd",
    "search_cmd",
    "show_cmd",
    "topics_cmd",
]
