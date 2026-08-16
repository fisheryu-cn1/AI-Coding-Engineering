#!/usr/bin/env python3
"""Generate architecture.svg for the kb-app user guide (Style 1 flat icon)."""

OUT = "code/kb-app/docs/diagrams/architecture.svg"

lines = []
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 720" width="960" height="720">')
lines.append('  <style>')
lines.append("    text { font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }")
lines.append('  </style>')
lines.append('  <defs>')
for mid, color in (("arrow-blue", "#2563eb"), ("arrow-green", "#16a34a"), ("arrow-purple", "#9333ea")):
    lines.append(f'    <marker id="{mid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    lines.append(f'      <polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
    lines.append('    </marker>')
lines.append('  </defs>')
lines.append('  <rect width="960" height="720" fill="#ffffff"/>')
lines.append('  <text x="480" y="34" text-anchor="middle" font-size="17" font-weight="600" fill="#111827">GraphIt-KB 总体架构</text>')


def box(x, y, w, h, title, subs, fill="#ffffff", stroke="#d1d5db", tsize=13.5):
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    ty = y + 22
    lines.append(f'  <text x="{x + w/2}" y="{ty}" text-anchor="middle" font-size="{tsize}" font-weight="600" fill="#111827">{title}</text>')
    for i, s in enumerate(subs):
        lines.append(f'  <text x="{x + w/2}" y="{ty + 16 * (i + 1)}" text-anchor="middle" font-size="11" fill="#6b7280">{s}</text>')


def path(d, color, marker, dash=None, width=1.5):
    dashattr = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{d}" stroke="{color}" stroke-width="{width}" fill="none"{dashattr} marker-end="url(#{marker})"/>')


def label(x, y, text, anchor="middle"):
    lines.append(f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" fill="#6b7280">{text}</text>')


# ---- arrows (drawn before nodes) ----
# users -> entries
path("M 240 108 L 220 160", "#2563eb", "arrow-blue")
path("M 720 108 L 740 160", "#2563eb", "arrow-blue")
# kb CLI -> pipeline / retrieval
path("M 170 216 L 170 280", "#2563eb", "arrow-blue")
path("M 290 216 L 290 248 L 480 248 L 480 280", "#2563eb", "arrow-blue")
# MCP -> retrieval / assemble
path("M 700 216 L 700 262 L 560 262 L 560 280", "#2563eb", "arrow-blue")
path("M 780 216 L 780 280", "#2563eb", "arrow-blue")
# core -> data dir container
path("M 170 344 L 170 420", "#16a34a", "arrow-green", dash="5,3")
path("M 480 344 L 480 420", "#16a34a", "arrow-green")
path("M 780 344 L 780 420", "#16a34a", "arrow-green")
# corpus -> pipeline (read-only scan, routed outside left edge)
path("M 40 588 L 24 588 L 24 312 L 40 312", "#16a34a", "arrow-green")
# retrieval -> LLM (optional, right corridor outside the container)
path("M 600 344 L 600 372 L 915 372 L 915 588 L 900 588", "#9333ea", "arrow-purple", dash="4,2")

# ---- nodes ----
# users
box(140, 60, 200, 48, "研究者（人）", [], fill="#eff6ff", stroke="#bfdbfe")
box(620, 60, 200, 48, "AI Agent", ["Kimi Code / Claude Code 等"], fill="#eff6ff", stroke="#bfdbfe")
# entries
box(60, 160, 240, 56, "kb CLI（Typer 命令行）", ["init / index / search / show / status …"])
box(620, 160, 240, 56, "MCP 服务（stdio）", ["kb serve mcp · 四只读工具"])
# core
box(60, 280, 260, 64, "索引流水线", ["scan → parse → chunk", "→ classify → summarize"])
box(350, 280, 260, 64, "检索引擎", ["FTS5 + 结构导航两路召回", "加权 RRF · 可选 LLM 重排"])
box(640, 280, 260, 64, "上下文组装", ["assemble_for_task", "按 token 预算截断 + 溯源锚点"])
# data dir container
lines.append('  <rect x="60" y="420" width="840" height="88" rx="8" ry="8" fill="#f9fafb" stroke="#d1d5db" stroke-width="1.5" stroke-dasharray="6,4"/>')
lines.append('  <text x="480" y="441" text-anchor="middle" font-size="12.5" font-weight="600" fill="#374151">数据目录（默认 ~/.graphit-kb/）</text>')
box(80, 450, 250, 46, "registry.sqlite（WAL）", ["files / tasks / topics / fts_chunks"], tsize=12)
box(350, 450, 250, 46, "文件产物", ["cache/extracted/ · auto_summaries/"], tsize=12)
box(620, 450, 260, 46, "config.yaml · reports/", ["graph/ · vectors/（M5/M3+ 预留）"], tsize=12)
# external
box(40, 560, 260, 56, "语料目录（只读）", ["references/ · research/ · design/"])
box(660, 560, 240, 56, "LLM API（可选）", ["摘要 · 分类兜底 · 扩展 · 重排"])

# arrow labels
label(30, 450, "只读扫描", anchor="start")
label(770, 366, "LLM 调用（可选）")
label(325, 405, "读 / 写")

# legend
lines.append('  <g transform="translate(20, 648)">')
legend = [
    ("#2563eb", None, "命令 / 工具调用"),
    ("#16a34a", None, "读"),
    ("#16a34a", "5,3", "写"),
    ("#9333ea", "4,2", "LLM 调用（可选）"),
]
for i, (c, d, t) in enumerate(legend):
    y = i * 18
    dashattr = f' stroke-dasharray="{d}"' if d else ''
    marker = {"#2563eb": "arrow-blue", "#16a34a": "arrow-green", "#9333ea": "arrow-purple"}[c]
    lines.append(f'    <line x1="0" y1="{y + 6}" x2="30" y2="{y + 6}" stroke="{c}" stroke-width="1.5"{dashattr} marker-end="url(#{marker})"/>')
    lines.append(f'    <text x="38" y="{y + 10}" font-size="11.5" fill="#6b7280">{t}</text>')
lines.append('  </g>')

lines.append('</svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written", OUT)
