"""Format → parser dispatch (设计 05 §3.2 + 09 §3/§4).

The single entry point is :func:`parse_path`. It looks up the extension in
the table below, calls the appropriate parser, and returns
``(ParseResult, ExtractMeta)``. Unknown extensions raise :class:`ParseError`
so the scan loop can skip them — extensions outside the whitelist are not
indexed at all (09 §3 白名单).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kbapp.parse.base import ExtractMeta, ParseError, ParseResult

#: Allowed scan extensions (lower-case, no dot). 09 §3 whitelist.
ALLOWED_EXTENSIONS: tuple[str, ...] = ("pdf", "html", "htm", "md", "docx", "txt")

#: extension → parser module name (lazy import to avoid loading all deps).
_FORMAT_TO_PARSER: dict[str, str] = {
    "pdf": "kbapp.parse.pdf_fast",
    "html": "kbapp.parse.html",
    "htm": "kbapp.parse.html",
    "md": "kbapp.parse.md",
    "docx": "kbapp.parse.docx",
    "txt": "kbapp.parse.txt",
}


def extension_for(path: Path) -> str:
    """Return the lowercased extension (no dot); empty string if none."""
    return path.suffix.lower().lstrip(".")


def parse_path(path: Path, *, cfg: Any | None = None) -> tuple[ParseResult, ExtractMeta]:
    """Dispatch by extension and parse ``path``.

    ``cfg`` (optional) is threaded to parsers that read tunables from
    ``parse.*`` config keys (the PDF fast path, 09 §4). Parsers ignore it
    otherwise.

    Raises :class:`ParseError` for unknown extensions or parser failures.
    """
    ext = extension_for(path)
    if not ext or ext not in _FORMAT_TO_PARSER:
        raise ParseError(f"不支持的扩展名：{ext!r}（白名单：{ALLOWED_EXTENSIONS}）")

    module_name = _FORMAT_TO_PARSER[ext]
    try:
        module = __import__(module_name, fromlist=["parse_" + ext])
    except ImportError as e:
        raise ParseError(f"解析器 {module_name} 未安装（pip install 'kbapp[parse]'）: {e}") from e

    fn_name = "parse_" + ext
    fn = getattr(module, fn_name, None)
    if fn is None:
        raise ParseError(f"解析器 {module_name} 未暴露 {fn_name}()")

    if ext == "pdf":
        return fn(path, **_pdf_kwargs(cfg))
    return fn(path)


def _pdf_kwargs(cfg: Any | None) -> dict[str, Any]:
    """Read ``parse.*`` tunables for the PDF fast path (09 §4).

    ``parse.ocr_enabled`` is deliberately not consumed here: M2 ships no OCR
    path (09 §1 default off) — the key is a config placeholder for M3.
    """
    if cfg is None:
        return {}

    def get(key: str, default: Any) -> Any:
        return cfg.get(key, default) if hasattr(cfg, "get") else default

    return {
        "page_char_norm": int(get("parse.page_char_norm", 1500)),
        "min_coverage": float(get("parse.pdf_fast_min_coverage", 0.85)),
        "min_headers": int(get("parse.pdf_fast_min_headers", 3)),
    }


def extract_meta_for_path(path: Path) -> ExtractMeta:
    """Same dispatch but only return the meta (lighter; used by scan probe).

    Calls the same parser as :func:`parse_path` and discards the result.
    """
    result, meta = parse_path(path)
    return meta


__all__ = [
    "ALLOWED_EXTENSIONS",
    "extract_meta_for_path",
    "extension_for",
    "parse_path",
]
