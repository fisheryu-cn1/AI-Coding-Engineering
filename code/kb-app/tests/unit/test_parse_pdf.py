"""``parse/pdf_fast`` 单测（pymupdf4llm 打桩，不依赖真实 PDF）。

回归场景（M3 DoD 复核发现）：pymupdf4llm 部分版本 ``metadata.page`` 为
``None``，TOC 分节若依赖该字段取页码会导致全部 section 正文为空（主语料
80 篇文件零 chunk）。修复后页码一律取自枚举序号（1-based，与 TOC 同基）。
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from kbapp.parse.pdf_fast import parse_pdf

TOC = [[1, "Introduction", 1], [1, "Method", 3], [1, "Conclusion", 5]]


def _fake_chunks(n_pages: int, toc: list[list]) -> list[dict]:
    """构造 pymupdf4llm page_chunks 返回值：metadata.page 为 None、每页带全量 TOC。"""
    return [
        {
            "text": f"page {i + 1} body text. " * 30,
            "metadata": {"format": "pdf", "page": None},
            "toc_items": toc,
        }
        for i in range(n_pages)
    ]


@pytest.fixture()
def fake_pymupdf4llm(monkeypatch: pytest.MonkeyPatch):
    mod = types.ModuleType("pymupdf4llm")

    def to_markdown(_path: str, page_chunks: bool = False):
        assert page_chunks
        return _fake_chunks(6, TOC)

    mod.to_markdown = to_markdown
    monkeypatch.setitem(sys.modules, "pymupdf4llm", mod)
    return mod


def test_toc_sections_get_text_when_metadata_page_missing(fake_pymupdf4llm, tmp_path: Path) -> None:
    result, meta = parse_pdf(tmp_path / "fake.pdf")
    assert meta.page_count == 6
    assert result.structure == "tree"
    assert len(result.sections) == 3
    # 每个 section 必须带正文（修复前全空）。
    for sec in result.sections:
        assert sec.text.strip(), f"{sec.section_path} 正文为空"
    # 页归属正确：Introduction ∈ 页1-2，Method ∈ 页3-4，Conclusion ∈ 页5-6。
    intro, method, concl = result.sections
    assert "page 1 body" in intro.text and "page 2 body" in intro.text
    assert "page 3 body" in method.text and "page 4 body" in method.text
    assert "page 5 body" in concl.text and "page 6 body" in concl.text
    assert intro.page_range == "1-2"
    assert concl.page_range == "5-6"


def test_toc_page_out_of_range_yields_empty_section(
    fake_pymupdf4llm, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # TOC 页码超出实际页数：越界 section 正文为空但不崩（防御性）。
    mod = sys.modules["pymupdf4llm"]

    def to_markdown(_path: str, page_chunks: bool = False):
        return _fake_chunks(2, [[1, "Only", 1], [1, "Ghost", 5]])

    monkeypatch.setattr(mod, "to_markdown", to_markdown)
    result, _ = parse_pdf(tmp_path / "fake.pdf")
    assert len(result.sections) == 2
    assert result.sections[0].text.strip()
    assert result.sections[1].text == ""
