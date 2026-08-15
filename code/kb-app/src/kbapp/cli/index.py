"""``kb index ...`` — scan / run / reindex / add / set-topic (M2 落地).

设计锚点：

- ``scan``        — 扫 corpus_roots，按 09 §2 决策表判定 + manifest 绑定，
                    入队 parse 任务，输出变更报告（09 §3 / §5）。
- ``run``         — 取写锁 → 调 :func:`run_pending_tasks`，串行同步执行
                    （09 §10）。Ctrl-C 触发 task 回退 pending，退出码 130。
- ``reindex``     — 清空 ``fts_chunks``（+ 可选 ``cache/extracted/``），重
                    新入队全部非 duplicate/deleted 文档（09 §10）。
- ``add``         — 登记库外文件（``corpus='external'``，绝对路径），path
                    已存在则报错退出码 1（09 §12）。
- ``set-topic``   — 改判即时生效；维护 ``topics.doc_count``（09 §7.2）。
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from kbapp.core.config import load_config
from kbapp.core.files import (
    ACTION_DUPLICATE,
    ACTION_MODIFIED,
    ACTION_MOVED,
    ACTION_NEW,
    ACTION_UNCHANGED,
    ScanAction,
    apply_deleted,
    apply_modified,
    apply_moved,
    apply_new_or_duplicate,
    decide_action,
    detect_deleted,
)
from kbapp.core.fingerprint import fingerprint
from kbapp.core.lock import LockError, acquire_write_lock, release_write_lock
from kbapp.core.paths import DataPaths
from kbapp.core.registry import (
    CORPORA,
    EXTRACT_STATUSES,
    FILES_STATUSES,
    Registry,
    get_file_by_path,
    get_file_by_sha256,
    list_files,
)
from kbapp.core.task import (
    RetryableError,
    TerminalError,
    enqueue_task,
)
from kbapp.llm import get_llm_or_none
from kbapp.parse.manifest import (
    SummaryMeta,
    bind_summaries_to_corpus,
    parse_summary,
    summary_body_text,
)
from kbapp.parse.registry import ALLOWED_EXTENSIONS, extension_for
from kbapp.pipeline.runner import PipelineCtx, RunReport, run_pending_tasks
from kbapp.pipeline.stages import set_topic as _set_topic

console = Console()
err_console = Console(stderr=True)
_logger = logging.getLogger(__name__)

app = typer.Typer(
    help="索引管理（scan / run / reindex / add / set-topic）",
    no_args_is_help=True,
)


# ---------------------------------------------------------------------------
# Scan report (in-memory, used by tests and the CLI printer)
# ---------------------------------------------------------------------------


@dataclass
class ScanReport:
    """Summary of one ``kb index scan`` invocation."""

    new: list[str] = None  # type: ignore[assignment]
    modified: list[str] = None  # type: ignore[assignment]
    moved: list[str] = None  # type: ignore[assignment]
    duplicate: list[str] = None  # type: ignore[assignment]
    deleted: list[str] = None  # type: ignore[assignment]
    skipped_extension: int = 0
    manifest_mismatch: list[str] = None  # type: ignore[assignment]
    enqueued: int = 0

    def __post_init__(self) -> None:
        for f in (
            "new",
            "modified",
            "moved",
            "duplicate",
            "deleted",
            "manifest_mismatch",
        ):
            if getattr(self, f) is None:
                setattr(self, f, [])

    def total_changes(self) -> int:
        return (
            len(self.new)
            + len(self.modified)
            + len(self.moved)
            + len(self.duplicate)
            + len(self.deleted)
        )


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------


@app.command("scan")
def scan_cmd(
    ctx: typer.Context,
    corpus: str | None = typer.Option(  # noqa: B008
        None,
        "--corpus",
        help="仅扫描指定语料（references / research / design）",
    ),
) -> None:
    """扫描 corpus_roots，写 files 表 + 入队 parse 任务（09 §3）。"""
    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()

    cfg = load_config(paths.config_path)
    roots = cfg.corpus_roots
    if corpus:
        if corpus not in roots and corpus != "external":
            err_console.print(f"[red]未知 corpus[/red] {corpus!r}")
            raise typer.Exit(code=1)
        scan_roots = {corpus: roots.get(corpus, data_dir)} if corpus in roots else {}
        if not scan_roots:
            err_console.print(f"[red]corpus {corpus!r} 未在 corpus_roots 中配置[/red]")
            raise typer.Exit(code=1)
    else:
        scan_roots = roots

    registry = Registry(paths.registry_db)
    registry.initialize()

    report = _do_scan(registry, paths, scan_roots)

    _print_scan_report(report)
    if report.total_changes() == 0 and report.enqueued == 0:
        console.print("[dim]无变更，无需入队。[/dim]")


def _do_scan(
    registry: Registry,
    paths: DataPaths,
    scan_roots: dict[str, Path],
) -> ScanReport:
    """Run one scan pass; mutate registry + tasks; return a report."""
    report = ScanReport()

    # Pass 1: walk every corpus root, collect on-disk candidates.
    on_disk: dict[str, tuple[str, Path, int]] = {}  # path → (corpus, abs, mtime)
    for corpus_name, root in scan_roots.items():
        if not root.exists():
            err_console.print(f"[yellow]corpus 目录不存在[/yellow] {corpus_name} → {root}")
            continue
        for abs_path in _iter_candidates(root):
            on_disk[str(abs_path)] = (corpus_name, abs_path, 0)

    # Pass 2: load existing rows (path & sha lookups). One read-only pass.
    registered: list = []  # FileRow list — full table for delete detection
    with registry.read_only() as conn:
        for row in list_files(conn, limit=100_000):
            registered.append(row)

    by_path_idx = {r.path: r for r in registered}
    on_disk_paths = set(on_disk.keys())

    # Pass 3: per-file decision + persist + enqueue.
    manifest_mismatches: list[str] = []
    with registry.transaction() as conn:
        # Manifest binding (09 §5) — read summaries/* before per-file loop so
        # we can stamp files.summary_source + summary_path during upsert.
        manifest_bindings, mismatches = _load_manifest_bindings(conn, on_disk_paths, scan_roots)
        manifest_mismatches = [
            f"{s.source_pdf} ← {s.path.name if s.path else '?'}" for s in mismatches
        ]
        report.manifest_mismatch = manifest_mismatches

        for path_str, (corpus_name, abs_path, _) in on_disk.items():
            try:
                sha, mtime = fingerprint(abs_path)
            except OSError as e:
                err_console.print(f"[yellow]跳过（IO 失败）[/yellow] {abs_path} — {e}")
                continue

            by_path = by_path_idx.get(path_str)
            by_sha = get_file_by_sha256(conn, sha)

            action: ScanAction = decide_action(
                path=abs_path,
                sha256=sha,
                mtime=mtime,
                by_path=by_path,
                by_sha=by_sha,
            )

            if action.kind == ACTION_UNCHANGED:
                # Manifest binding may still be needed (e.g. new summary landed)
                if path_str in manifest_bindings:
                    _stamp_manifest(conn, paths, action.doc_id, manifest_bindings[path_str])
                continue

            if action.kind == ACTION_NEW:
                doc_id = apply_new_or_duplicate(
                    conn, action=action, corpus=corpus_name, is_duplicate=False
                )
                report.new.append(doc_id)
                _enqueue_parse_task(registry, doc_id, conn=conn)
                report.enqueued += 1

            elif action.kind == ACTION_MODIFIED:
                apply_modified(conn, action, corpus=corpus_name)
                report.modified.append(action.doc_id)
                _enqueue_parse_task(registry, action.doc_id, conn=conn)
                report.enqueued += 1

            elif action.kind == ACTION_MOVED:
                apply_moved(conn, action)
                report.moved.append(action.doc_id)
                # Zero re-extract: no enqueue (09 §2).
                # But if a new summary landed, stamp it.
                if path_str in manifest_bindings:
                    _stamp_manifest(conn, paths, action.doc_id, manifest_bindings[path_str])

            elif action.kind == ACTION_DUPLICATE:
                doc_id = apply_new_or_duplicate(
                    conn, action=action, corpus=corpus_name, is_duplicate=True
                )
                report.duplicate.append(doc_id)
                # Duplicate does NOT enqueue or fill FTS (09 §2).

            # Manifest binding for newly added files.
            if path_str in manifest_bindings:
                _stamp_manifest(conn, paths, action.doc_id or doc_id, manifest_bindings[path_str])

        # Pass 4: deletion detection. Re-read rows *within the transaction*
        # so paths already updated by apply_moved in Pass 3 are seen in their
        # new location — otherwise a moved file is tombstoned in the same
        # scan (P0-1).
        current_rows = list_files(conn, limit=100_000)
        tombstones = detect_deleted(on_disk_paths=on_disk_paths, registered_rows=current_rows)
        for row in tombstones:
            apply_deleted(conn, row.doc_id)
            report.deleted.append(row.doc_id)
            # 15 §4.1：图 tombstone 任务入队（runner 串行消费，软删 Document 节点）
            enqueue_task(
                registry,
                kind="tombstone",
                payload={"doc_id": row.doc_id},
                conn=conn,
            )

    # Persist manifest mismatches to reports/ (09 §5 / 06 §4.4).
    _write_manifest_mismatch_report(paths, manifest_mismatches)

    return report


def _iter_candidates(root: Path) -> Iterable[Path]:
    """Walk ``root`` honoring the scan rules (09 §3).

    - skip hidden files / dirs;
    - skip ``summaries/`` (manifest source, not corpus);
    - honor ``.gitignore`` via :mod:`pathspec`;
    - don't follow symlinks;
    - whitelist only the 6 allowed extensions.
    """
    try:
        import pathspec
    except ImportError:
        pathspec = None  # type: ignore[assignment]

    gi: object | None = None
    gitignore_path = root / ".gitignore"
    if pathspec is not None and gitignore_path.exists():
        try:
            with gitignore_path.open("r", encoding="utf-8") as f:
                gi = pathspec.PathSpec.from_lines("gitwildmatch", f)
        except OSError:
            gi = None

    for dirpath, dirnames, filenames in _walk_no_follow(root):
        # Drop hidden dirs in-place so os.walk skips them.
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "summaries"]
        for name in filenames:
            if name.startswith("."):
                continue
            ext = extension_for(Path(name))
            if ext not in ALLOWED_EXTENSIONS:
                continue
            p = Path(dirpath) / name
            if gi is not None and gi.match_file(str(p.relative_to(root))):
                continue
            yield p


def _walk_no_follow(root: Path):
    """``os.walk`` wrapper with ``followlinks=False`` and ``summaries/`` skipped."""
    import os

    yield from os.walk(root, followlinks=False)


def _enqueue_parse_task(
    registry: Registry,
    doc_id: str,
    conn=None,
) -> None:
    """Enqueue a parse task for ``doc_id`` (idempotent enough — duplicates don't hurt).

    If ``conn`` is provided, the INSERT happens on the caller's existing
    transaction (avoids recursive ``BEGIN IMMEDIATE`` → lock contention on
    the same SQLite file).
    """
    try:
        enqueue_task(
            registry,
            kind="parse",
            payload={"doc_id": doc_id},
            conn=conn,
        )
    except Exception as e:  # pragma: no cover - defensive
        _logger.warning("enqueue parse 失败：%s (%s)", doc_id, e)


def _load_manifest_bindings(
    conn,
    on_disk_paths: set[str],
    scan_roots: dict[str, Path],
) -> tuple[dict[str, SummaryMeta], list[SummaryMeta]]:
    """Parse every ``summaries/*.md`` under a corpus root; bind to corpus paths.

    Summaries are searched along each file's ancestor dirs **within its corpus
    root subtree only** (09 §5「各 corpus 下」) — never above the corpus root,
    so a stray ``summaries/`` outside the corpus is not picked up (P3-4).

    Returns ``(bindings, mismatches)``: ``bindings`` maps corpus path →
    ``SummaryMeta`` for matched PDFs; ``mismatches`` lists summaries whose
    ``source_pdf`` maps to no corpus file (06 §4.4 → ``reports/``).
    """
    # NOTE: callers must pass ``conn`` for read-only meta checks; this
    # implementation walks filesystem only and ignores ``conn`` arg.
    roots = {Path(r).expanduser().resolve() for r in scan_roots.values()}
    summaries: list[SummaryMeta] = []
    # Walk the *parents* of each on-disk path looking for ``summaries/``.
    seen_dirs: set[Path] = set()
    for path_str in on_disk_paths:
        p = Path(path_str).resolve()
        corpus_root = next((r for r in roots if p.is_relative_to(r)), None)
        if corpus_root is None:
            continue
        parent = p.parent
        for d in [parent, *parent.parents]:
            # Stop the moment we walk past the corpus root subtree.
            if not d.is_relative_to(corpus_root):
                break
            if d in seen_dirs:
                continue
            seen_dirs.add(d)
            sum_dir = d / "summaries"
            if not sum_dir.is_dir():
                continue
            for sp in sum_dir.glob("*.md"):
                try:
                    summaries.append(parse_summary(sp))
                except Exception as e:
                    err_console.print(f"[yellow]summary 解析失败[/yellow] {sp} — {e}")
    if not summaries:
        return {}, []
    bindings = bind_summaries_to_corpus(summaries, on_disk_paths)
    matched_sources = {s.source_pdf for s in bindings.values()}
    mismatches = [s for s in summaries if s.source_pdf and s.source_pdf not in matched_sources]
    return bindings, mismatches


def _write_manifest_mismatch_report(paths: DataPaths, mismatches: list[str]) -> Path | None:
    """Write ``reports/manifest_mismatch_<ts>.json`` when there are mismatches.

    Returns the written path, or ``None`` when there is nothing to report.
    """
    if not mismatches:
        return None
    paths.reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = paths.reports_dir / f"manifest_mismatch_{stamp}.json"
    payload = {"mismatches": mismatches}
    out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out


def _stamp_manifest(conn, paths: DataPaths, doc_id: str | None, summary: SummaryMeta) -> None:
    """Apply a curated manifest binding（09 §5 / 11 §3.1/§3.4）：

    - 更新 `summary_source='curated'` + `summary_path` + 清 `summary_stale`；
    - 删除 auto 临时摘要文件（再策展后清理，P1-6）；
    - 从策展文件构建 `$summary` 伪 chunk（P1-5，纯策展库也能进 FTS）。
    """
    from kbapp.core.registry import insert_chunk, update_file_fields
    from kbapp.retrieve.hybrid import SUMMARY_SECTION

    if doc_id is None:
        return
    update_file_fields(
        conn,
        doc_id,
        summary_source="curated",
        summary_path=str(summary.path) if summary.path else None,
        summary_stale=0,
    )
    # 再策展后清理 auto 临时摘要（P1-6）
    try:
        (paths.auto_summaries_dir / f"{doc_id}.md").unlink()
    except FileNotFoundError:
        pass
    # 从策展文件重建伪 chunk（P1-5；幂等先删后插）
    body = summary_body_text(summary.path) if summary.path else ""
    conn.execute("DELETE FROM fts_chunks WHERE chunk_id = ?", (f"{doc_id}#summary",))
    if body:
        insert_chunk(
            conn,
            chunk_id=f"{doc_id}#summary",
            doc_id=doc_id,
            section_path=SUMMARY_SECTION,
            title=summary.title or "",
            text=body[:2000],
        )


def _print_scan_report(report: ScanReport) -> None:
    table = Table(title="kb index scan 报告", show_lines=False)
    table.add_column("情形", style="cyan", no_wrap=True)
    table.add_column("doc_id", style="green")
    for _kind, label, ids in (
        ("new", "新增", report.new),
        ("modified", "修改", report.modified),
        ("moved", "移动（零重抽取）", report.moved),
        ("duplicate", "重复", report.duplicate),
        ("deleted", "删除（墓碑）", report.deleted),
    ):
        if ids:
            table.add_row(label, ", ".join(ids))
    if report.manifest_mismatch:
        table.add_row(
            "[yellow]manifest 不匹配[/yellow]",
            ", ".join(report.manifest_mismatch),
        )
    if report.enqueued:
        table.add_row("[bold]入队任务[/bold]", f"{report.enqueued} 个 parse")
    console.print(table)


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


@app.command("run")
def run_cmd(
    ctx: typer.Context,
    wait: bool = typer.Option(  # noqa: B008
        False,
        "--wait",
        help="锁被占用时阻塞轮询（最多 30 秒）",
    ),
    max_tasks: int | None = typer.Option(  # noqa: B008
        None,
        "--max-tasks",
        help="最多处理多少个任务就退出（默认：drain）",
    ),
) -> None:
    """执行待处理任务（09 §10）。Ctrl-C 退出码 130。"""
    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()

    cfg = load_config(paths.config_path)
    registry = Registry(paths.registry_db)
    registry.initialize()

    lock = None
    try:
        lock = acquire_write_lock(paths.data_dir, wait=wait)
        if lock is None:
            err_console.print("[red]写锁被占用[/red]，稍后重试（加 --wait 阻塞等待）")
            raise typer.Exit(code=2)

        llm = get_llm_or_none(cfg)
        ctx_obj = PipelineCtx(
            cfg=cfg,
            paths=paths,
            registry=registry,
            llm=llm,
            max_tasks=max_tasks,
        )

        started = time.monotonic()
        try:
            report = run_pending_tasks(ctx_obj)
        except KeyboardInterrupt:
            console.print("[yellow]Ctrl-C — 已恢复 pending，下次继续[/yellow]")
            raise typer.Exit(code=130) from None

        elapsed = time.monotonic() - started
        _print_run_report(report, elapsed)
    except LockError as e:
        err_console.print(f"[red]锁错误[/red] {e}")
        raise typer.Exit(code=2) from None
    except (RetryableError, TerminalError) as e:
        err_console.print(f"[red]任务失败[/red] {e}")
        raise typer.Exit(code=1) from None
    finally:
        if lock is not None:
            release_write_lock(lock)


def _print_run_report(report: RunReport, elapsed: float) -> None:
    table = Table(title=f"kb index run 报告（{elapsed:.1f}s）", show_lines=False)
    table.add_column("指标", style="cyan")
    table.add_column("值", style="green")
    table.add_row("done", str(report.tasks_done))
    table.add_row("failed", str(report.tasks_failed))
    table.add_row("skipped", str(report.tasks_skipped))
    if report.metrics:
        for k, v in report.metrics.items():
            table.add_row(f"  · {k}", str(v))
    console.print(table)


# ---------------------------------------------------------------------------
# reindex
# ---------------------------------------------------------------------------


@app.command("reindex")
def reindex_cmd(
    ctx: typer.Context,
    full: bool = typer.Option(  # noqa: B008
        False,
        "--full",
        help="清空 fts_chunks 与 graph/ 并重新入队所有非 duplicate/deleted 文档",
    ),
    no_cache: bool = typer.Option(  # noqa: B008
        False,
        "--no-cache",
        help="额外清空 cache/extracted/（与 --full 联用）",
    ),
    wait: bool = typer.Option(False, "--wait", help="锁被占用时阻塞轮询"),
) -> None:
    """重建索引（09 §10 + 15 §4.4 reindex 定义）。"""
    if not full:
        err_console.print("[red]reindex 必须配合 --full[/red]（09 §10）")
        raise typer.Exit(code=1)

    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)

    lock = None
    try:
        lock = acquire_write_lock(paths.data_dir, wait=wait)
        if lock is None:
            err_console.print("[red]写锁被占用[/red]")
            raise typer.Exit(code=2)

        registry = Registry(paths.registry_db)
        registry.initialize()

        # 1. Clear fts_chunks + graph/（15 §4.4：图库是衍生数据，可全量重建）
        deleted_chunks = 0
        with registry.transaction() as conn:
            cur = conn.execute("DELETE FROM fts_chunks")
            deleted_chunks = cur.rowcount

        from kbapp.graph.reset import reset_graph

        reset_graph(paths)

        # 2. Optionally clear cache/extracted.
        removed_files = 0
        if no_cache and paths.extracted_dir.exists():
            for p in paths.extracted_dir.glob("*.json"):
                try:
                    p.unlink()
                    removed_files += 1
                except OSError:
                    pass

        # 3. Re-enqueue every non-tombstoned, non-duplicate file.
        enqueued = 0
        with registry.read_only() as conn:
            rows = list_files(conn, limit=100_000)
        with registry.transaction() as conn:
            for r in rows:
                if r.status in ("deleted", "duplicate"):
                    continue
                enqueue_task(
                    registry,
                    kind="parse",
                    payload={"doc_id": r.doc_id},
                    conn=conn,
                )
                enqueued += 1

        console.print(
            f"[green]reindex 已入队[/green] {enqueued} 个任务；"
            f"清空 {deleted_chunks} 条 FTS；重置 graph/；移除 {removed_files} 个缓存文件"
        )
    except LockError as e:
        err_console.print(f"[red]锁错误[/red] {e}")
        raise typer.Exit(code=2) from None
    finally:
        if lock is not None:
            release_write_lock(lock)


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------


@app.command("add")
def add_cmd(
    ctx: typer.Context,
    path: Path = typer.Argument(  # noqa: B008
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="库外文件绝对路径（登记不拷贝）",
    ),
) -> None:
    """登记库外文件（09 §12）：corpus=external，绝对路径。"""
    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()

    abs_path = path.expanduser().resolve()
    ext = extension_for(abs_path)
    if ext not in ALLOWED_EXTENSIONS:
        err_console.print(f"[red]不支持的扩展名[/red] {ext!r}（白名单：{ALLOWED_EXTENSIONS}）")
        raise typer.Exit(code=1)

    registry = Registry(paths.registry_db)
    registry.initialize()

    # path already registered → exit 1 (09 §12).
    with registry.read_only() as conn:
        existing = get_file_by_path(conn, str(abs_path))
        if existing is not None:
            err_console.print(f"[red]路径已登记[/red] doc_id={existing.doc_id}")
            raise typer.Exit(code=1)

    try:
        sha, mtime = fingerprint(abs_path)
    except OSError as e:
        err_console.print(f"[red]无法读取文件[/red] {e}")
        raise typer.Exit(code=2) from None

    lock = None
    try:
        lock = acquire_write_lock(paths.data_dir, wait=False)
        if lock is None:
            err_console.print("[red]写锁被占用[/red]")
            raise typer.Exit(code=2)

        with registry.transaction() as conn:
            action = decide_action(
                path=abs_path,
                sha256=sha,
                mtime=mtime,
                by_path=None,  # we just checked — no existing row at this path
                by_sha=get_file_by_sha256(conn, sha),
            )
            if action.kind == ACTION_DUPLICATE:
                doc_id = apply_new_or_duplicate(
                    conn, action=action, corpus="external", is_duplicate=True
                )
                console.print(
                    f"[yellow]sha256 已存在[/yellow] doc_id={doc_id}（duplicate，不入队）"
                )
                return
            if action.kind in (ACTION_MOVED, ACTION_MODIFIED, ACTION_UNCHANGED):
                # Reached for external files only when sha matches an existing
                # row (the duplicate branch above handles that); but if the
                # external file's content was previously seen under another
                # path, treat as a duplicate rather than a move (avoids
                # poisoning the in-library row's path).
                action = ScanAction(
                    ACTION_DUPLICATE,
                    None,
                    action.path,
                    action.sha256,
                    action.mtime,
                    note=f"also_at={action.note}",
                )
                doc_id = apply_new_or_duplicate(
                    conn, action=action, corpus="external", is_duplicate=True
                )
                console.print(
                    f"[yellow]sha256 命中既有库内文件[/yellow] doc_id={doc_id}（duplicate）"
                )
                return

            # New: allocate doc_id + enqueue full pipeline.
            doc_id = apply_new_or_duplicate(
                conn, action=action, corpus="external", is_duplicate=False
            )
            enqueue_task(registry, kind="parse", payload={"doc_id": doc_id}, conn=conn)

        console.print(f"[green]已登记 external[/green] doc_id={doc_id} {abs_path}")
    except LockError as e:
        err_console.print(f"[red]锁错误[/red] {e}")
        raise typer.Exit(code=2) from None
    finally:
        if lock is not None:
            release_write_lock(lock)


# ---------------------------------------------------------------------------
# set-topic
# ---------------------------------------------------------------------------


@app.command("set-topic")
def set_topic_cmd(
    ctx: typer.Context,
    doc_id: str = typer.Argument(..., help="目标 doc_id，如 D0001"),  # noqa: B008
    topic: str = typer.Argument(  # noqa: B008
        ..., help="目标 topic；用 '-' 表示清空（needs_confirm）"
    ),
) -> None:
    """改判 topic（09 §7.2）；即时生效，维护 topics.doc_count。"""
    data_dir: Path = ctx.obj["data_dir"]
    paths = DataPaths.from_data_dir(data_dir)
    paths.ensure_dirs()

    registry = Registry(paths.registry_db)
    registry.initialize()

    new_topic: str | None = None if topic == "-" else topic
    if new_topic is not None and not new_topic.strip():
        err_console.print("[red]topic 不能为空字符串[/red]")
        raise typer.Exit(code=1)

    lock = None
    try:
        lock = acquire_write_lock(paths.data_dir, wait=False)
        if lock is None:
            err_console.print("[red]写锁被占用[/red]")
            raise typer.Exit(code=2)

        try:
            _set_topic(registry, doc_id, new_topic)
        except KeyError as e:
            err_console.print(f"[red]{e}[/red]")
            raise typer.Exit(code=1) from None

        if new_topic:
            console.print(
                f"[green]已改判[/green] {doc_id} → {new_topic}（topics.doc_count 已维护）"
            )
        else:
            console.print(f"[yellow]已清空 topic[/yellow] {doc_id} → needs_confirm")
    except LockError as e:
        err_console.print(f"[red]锁错误[/red] {e}")
        raise typer.Exit(code=2) from None
    finally:
        if lock is not None:
            release_write_lock(lock)


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------


__all__ = ["app", "scan_cmd", "run_cmd", "reindex_cmd", "add_cmd", "set_topic_cmd"]


if __name__ == "__main__":  # pragma: no cover
    app()


# Silence unused-import warnings for re-export-only names.
_ = shutil
_ = json
_ = sys
_ = FILES_STATUSES
_ = EXTRACT_STATUSES
_ = CORPORA
