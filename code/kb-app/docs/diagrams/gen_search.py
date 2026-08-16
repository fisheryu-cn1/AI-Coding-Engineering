#!/usr/bin/env python3
"""Generate search.svg — hybrid retrieval + context assembly data flow (Style 1)."""

OUT = "code/kb-app/docs/diagrams/search.svg"

lines = []
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 660" width="1200" height="660">')
lines.append('  <style>')
lines.append("    text { font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }")
lines.append('  </style>')
lines.append('  <defs>')
for mid, color in (("arrow-blue", "#2563eb"), ("arrow-purple", "#9333ea")):
    lines.append(f'    <marker id="{mid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    lines.append(f'      <polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
    lines.append('    </marker>')
lines.append('  </defs>')
lines.append('  <rect width="1200" height="660" fill="#ffffff"/>')
lines.append('  <text x="600" y="32" text-anchor="middle" font-size="17" font-weight="600" fill="#111827">检索与上下文组装数据流</text>')


def box(x, y, w, h, title, subs, fill="#ffffff", stroke="#d1d5db", tsize=13):
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    ty = y + (22 if subs else h / 2 + 5)
    lines.append(f'  <text x="{x + w/2}" y="{ty}" text-anchor="middle" font-size="{tsize}" font-weight="600" fill="#111827">{title}</text>')
    for i, s in enumerate(subs):
        lines.append(f'  <text x="{x + w/2}" y="{ty + 16 * (i + 1)}" text-anchor="middle" font-size="11" fill="#6b7280">{s}</text>')


def path(d, color="#2563eb", marker="arrow-blue", dash=None, width=1.5):
    dashattr = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{d}" stroke="{color}" stroke-width="{width}" fill="none"{dashattr} marker-end="url(#{marker})"/>')


def label(x, y, text, anchor="middle"):
    lines.append(f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" fill="#6b7280">{text}</text>')


# ---- arrows ----
path("M 180 300 L 240 300", width=2)                              # query -> understanding
path("M 440 285 L 480 200")                                       # understanding -> FTS
path("M 440 315 L 480 430")                                       # understanding -> graph
path("M 720 170 L 800 170 L 800 270 L 820 270", width=2)          # FTS -> RRF
path("M 720 468 L 800 468 L 800 330 L 820 330", width=2)          # graph -> RRF
path("M 990 300 L 1030 300", width=2)                             # RRF -> rerank
path("M 1105 330 L 1105 400")                                     # rerank -> hits
# assemble strip arrows
path("M 320 584 L 360 584")
path("M 600 584 L 640 584")
path("M 880 584 L 920 584")

# ---- nodes ----
box(40, 270, 140, 60, "查询 query", ["自然语言 / 关键词"], fill="#eff6ff", stroke="#bfdbfe")
box(240, 262, 200, 76, "查询理解", ["norm 归一化 · 主题词匹配", "内置+用户同义词表", "LLM 查询扩展（可选）"])
box(480, 130, 240, 76, "全文路（FTS5 trigram）", ["BM25 chunk 召回", "→ section 聚合", "短查询 LIKE 兜底 + 分档"])
box(480, 430, 240, 76, "图路（结构导航）", ["topic 匹配 → 文档清单", "→ 章节清单", "topic 稀疏时退化 corpus 导航"])
box(820, 270, 170, 60, "加权 RRF 融合", ["w_fts 1.0 · w_graph 0.5", "rrf_k = 60"], fill="#fff7ed", stroke="#fdba74")
box(1030, 270, 150, 60, "LLM 重排", ["可选 · top-20", "失败回退 RRF 序"])
box(1030, 400, 150, 76, "SearchHit 列表", ["锚点", "doc_id#section_path"], fill="#f0fdf4", stroke="#bbf7d0")

label(600, 118, "--topic 硬过滤：前置下推 SQL，不进 RRF")

# ---- assemble strip ----
lines.append('  <rect x="40" y="530" width="1120" height="104" rx="8" ry="8" fill="#f9fafb" stroke="#d1d5db" stroke-width="1.5" stroke-dasharray="6,4"/>')
lines.append('  <text x="600" y="552" text-anchor="middle" font-size="12.5" font-weight="600" fill="#374151">kb_assemble_context（MCP 工具 · 确定性路径，全程不调 LLM）</text>')
box(80, 562, 240, 56, "检索命中", ["search() 不传 llm", "--topics 逐个硬过滤合并"], tsize=12)
box(360, 562, 240, 56, "按文档去重", ["保留首个命中章节为锚点"], tsize=12)
box(640, 562, 240, 56, "读摘要拼装", ["无摘要回退首节前 200 字"], tsize=12)
box(920, 562, 240, 56, "预算截断输出", ["budget×4 字符 ≈ token", "{context_block, sources}"], tsize=12)

# legend
lines.append('  <g transform="translate(20, 40)">')
lines.append('    <line x1="0" y1="6" x2="30" y2="6" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>')
lines.append('    <text x="38" y="10" font-size="11.5" fill="#6b7280">主数据流</text>')
lines.append('  </g>')

lines.append('</svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written", OUT)
