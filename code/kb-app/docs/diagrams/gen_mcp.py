#!/usr/bin/env python3
"""Generate mcp.svg — MCP interaction sequence diagram (Style 1)."""

OUT = "code/kb-app/docs/diagrams/mcp.svg"

lines = []
lines.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 620" width="960" height="620">')
lines.append('  <style>')
lines.append("    text { font-family: 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif; }")
lines.append('  </style>')
lines.append('  <defs>')
lines.append('    <marker id="arrow-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
lines.append('      <polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/>')
lines.append('    </marker>')
lines.append('    <marker id="arrow-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
lines.append('      <polygon points="0 0, 10 3.5, 0 7" fill="#16a34a"/>')
lines.append('    </marker>')
lines.append('  </defs>')
lines.append('  <rect width="960" height="620" fill="#ffffff"/>')
lines.append('  <text x="480" y="32" text-anchor="middle" font-size="17" font-weight="600" fill="#111827">Agent 经 MCP 调用知识库的典型时序</text>')

# participants
parts = [(150, "AI Agent"), (480, "MCP 服务"), (810, "registry.sqlite")]
for x, name in parts:
    lines.append(f'  <rect x="{x - 90}" y="50" width="180" height="36" rx="8" ry="8" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1.5"/>')
    lines.append(f'  <text x="{x}" y="73" text-anchor="middle" font-size="13.5" font-weight="600" fill="#111827">{name}</text>')
    lines.append(f'  <line x1="{x}" y1="86" x2="{x}" y2="520" stroke="#d1d5db" stroke-width="1.5" stroke-dasharray="4,3"/>')

# activation bar on MCP lifeline
lines.append('  <rect x="474" y="112" width="12" height="388" fill="#dbeafe" stroke="#bfdbfe"/>')


def msg(y, x1, x2, text, color="#2563eb", marker="arrow-blue", dash=None):
    dashattr = f' stroke-dasharray="{dash}"' if dash else ''
    lines.append(f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1.5"{dashattr} marker-end="url(#{marker})"/>')
    lines.append(f'  <text x="{(x1 + x2) / 2}" y="{y - 7}" text-anchor="middle" font-size="11.5" fill="#374151">{text}</text>')


# 1 kb_search
msg(120, 150, 474, 'kb_search(query, mode="hybrid")')
msg(160, 486, 810, "FTS + 结构导航检索", color="#16a34a", marker="arrow-green")
msg(200, 474, 150, "hits[ doc_id · section_path · snippet · score ]", color="#16a34a", marker="arrow-green", dash="5,3")
# 2 kb_show
msg(250, 150, 474, "kb_show(doc_id)")
msg(290, 474, 150, "元数据 + 章节树 + 摘要", color="#16a34a", marker="arrow-green", dash="5,3")
# 3 kb_read
msg(340, 150, 474, 'kb_read(doc_id, "§2 …")')
msg(380, 474, 150, "章节原文（$summary 读摘要全文）", color="#16a34a", marker="arrow-green", dash="5,3")
# 4 kb_assemble_context
msg(430, 150, 474, "kb_assemble_context(task, budget=8000)")
msg(470, 474, 150, "{ context_block, used, sources（溯源锚点）}", color="#16a34a", marker="arrow-green", dash="5,3")

# error note
lines.append('  <rect x="150" y="540" width="660" height="56" rx="8" ry="8" fill="#fff7ed" stroke="#fdba74" stroke-width="1.5"/>')
lines.append('  <text x="480" y="562" text-anchor="middle" font-size="12" font-weight="600" fill="#111827">统一错误结构（工具内捕获，不抛协议层异常）</text>')
lines.append('  <text x="480" y="582" text-anchor="middle" font-size="11.5" fill="#6b7280">{ error: { code, message, suggestion } } — DOC_NOT_FOUND / SECTION_NOT_FOUND / MODE_NOT_READY / CONFIG_INVALID / INTERNAL</text>')

lines.append('</svg>')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written", OUT)
