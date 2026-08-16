#!/usr/bin/env python3
"""Generate pipeline.svg — indexing pipeline flowchart (Style 1)."""

OUT = "code/kb-app/docs/diagrams/pipeline.svg"

lines = []
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 800" width="960" height="800">')
lines.append('  <style>')
lines.append("    text { font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }")
lines.append('  </style>')
lines.append('  <defs>')
for mid, color in (("arrow-blue", "#2563eb"), ("arrow-gray", "#6b7280")):
    lines.append(f'    <marker id="{mid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    lines.append(f'      <polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
    lines.append('    </marker>')
lines.append('  </defs>')
lines.append('  <rect width="960" height="800" fill="#ffffff"/>')
lines.append('  <text x="480" y="32" text-anchor="middle" font-size="17" font-weight="600" fill="#111827">索引流水线与日常维护流程</text>')


def box(x, y, w, h, title, subs, fill="#ffffff", stroke="#d1d5db"):
    lines.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    ty = y + (22 if subs else h / 2 + 5)
    lines.append(f'  <text x="{x + w/2}" y="{ty}" text-anchor="middle" font-size="13" font-weight="600" fill="#111827">{title}</text>')
    for i, s in enumerate(subs):
        lines.append(f'  <text x="{x + w/2}" y="{ty + 16 * (i + 1)}" text-anchor="middle" font-size="11" fill="#6b7280">{s}</text>')


def diamond(cx, cy, w, h, title):
    pts = f"{cx},{cy - h/2} {cx + w/2},{cy} {cx},{cy + h/2} {cx - w/2},{cy}"
    lines.append(f'  <polygon points="{pts}" fill="#fff7ed" stroke="#fdba74" stroke-width="1.5"/>')
    lines.append(f'  <text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="12.5" font-weight="600" fill="#111827">{title}</text>')


def path(d, color="#2563eb", marker="arrow-blue", dash=None):
    dashattr = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <path d="{d}" stroke="{color}" stroke-width="1.5" fill="none"{dashattr} marker-end="url(#{marker})"/>')


def label(x, y, text, anchor="middle"):
    lines.append(f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="11" fill="#6b7280">{text}</text>')


# ---- arrows ----
path("M 220 108 L 220 140")                       # init -> edit config
path("M 220 188 L 220 220")                       # edit config -> scan
path("M 220 268 L 220 296")                       # scan -> diamond
path("M 340 340 L 460 340 L 460 322 L 520 322")   # diamond -> moved
path("M 340 340 L 480 340 L 480 382 L 520 382")   # diamond -> duplicate
path("M 340 340 L 500 340 L 500 442 L 520 442")   # diamond -> deleted
path("M 220 384 L 220 440")                       # diamond -> run (new/modified)
path("M 220 488 L 220 530")                       # run -> stages
path("M 220 606 L 220 650")                       # stages -> status
path("M 360 672 L 435 672")                       # status -> needs_confirm?
path("M 605 672 L 680 672")                       # yes -> set-topic
path("M 920 672 L 945 672 L 945 244 L 360 244", color="#6b7280", marker="arrow-gray", dash="4,2")  # loop back to scan
path("M 680 762 L 640 762 L 640 540 L 380 540 L 380 464 L 360 464", color="#6b7280", marker="arrow-gray", dash="4,2")  # reindex -> run

# ---- nodes ----
box(80, 60, 280, 48, "kb init", ["一次性：建目录 · 默认配置 · 播种 topics"], fill="#eff6ff", stroke="#bfdbfe")
box(80, 140, 280, 48, "编辑 config.yaml", ["corpus_roots · core_topics · 关键词 · llm"], fill="#eff6ff", stroke="#bfdbfe")
box(80, 220, 280, 48, "kb index scan", ["白名单扫描 + SHA-256 指纹比对"], fill="#eff6ff", stroke="#bfdbfe")
diamond(220, 340, 240, 88, "逐文件变更判定")

box(520, 300, 340, 44, "moved：仅更新路径", ["零重抽取，保留 doc_id"])
box(520, 360, 340, 44, "duplicate：仅登记", ["SHA-256 重复，不入队、不入 FTS"])
box(520, 420, 340, 44, "deleted：墓碑标记", ["保留身份字段，文件回归可复活"])

box(80, 440, 280, 48, "kb index run", ["取写锁，串行执行任务队列"], fill="#eff6ff", stroke="#bfdbfe")
box(80, 530, 280, 76, "四阶段流水线", ["parse → chunk → classify → summarize", "分块写 FTS5 + 解析缓存；摘要需 LLM"], fill="#eff6ff", stroke="#bfdbfe")
box(80, 650, 280, 44, "kb status", ["查看状态 / topics / 待确认队列"], fill="#eff6ff", stroke="#bfdbfe")
diamond(520, 672, 170, 70, "needs_confirm?")
box(680, 640, 240, 64, "kb index set-topic", ["Dxxxx Topic 改判，即时生效", "'-' 清空留待人工"])
box(680, 740, 240, 44, "kb index reindex --full", ["清空 FTS，全量重建"])

# labels
label(430, 314, "moved")
label(440, 356, "duplicate")
label(508, 436, "deleted", anchor="start")
label(232, 416, "new / modified → 入队 parse", anchor="start")
label(573, 664, "是")
label(520, 730, "否：库已可检索（kb search …）")
label(650, 236, "资料变动后再次扫描（增量）")
label(510, 534, "全量重建")

# legend
lines.append('  <g transform="translate(20, 760)">')
lines.append('    <line x1="0" y1="6" x2="30" y2="6" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arrow-blue)"/>')
lines.append('    <text x="38" y="10" font-size="11.5" fill="#6b7280">主流程</text>')
lines.append('    <line x1="110" y1="6" x2="140" y2="6" stroke="#6b7280" stroke-width="1.5" stroke-dasharray="4,2" marker-end="url(#arrow-gray)"/>')
lines.append('    <text x="148" y="10" font-size="11.5" fill="#6b7280">循环 / 重建</text>')
lines.append('  </g>')

lines.append('</svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written", OUT)
