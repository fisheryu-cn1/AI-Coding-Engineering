# -*- coding: utf-8 -*-
"""适配器：把无 skill 对照组（run10）的自创格式意见卡转换为意见卡模板 v5 契约格式。
格式契约原则（notes/06）：历史/非契约产出物经适配器转换后进入评分，而非修改工具解析。
转换规则（对应 run10 的实际偏差）：
  1. 删除自创分节头 `## P0 — …` / `## P1 — …` 等（评分器按 `## 意见` 节解析意见块）；
  2. 在首个 `### [P0-3]` 前插入 `## 意见（适配后）`；
  3. 字段行 `类型 / X` → `- 类型：X`（溯源/证据/维度/建议同理）。
"""
import io, re, sys

src, dst = sys.argv[1], sys.argv[2]
text = io.open(src, encoding="utf-8").read()
lines = text.split("\n")
out, inserted = [], False
for ln in lines:
    if re.match(r"^## P[0-3][ \u2014-]", ln):
        continue  # 自创分节头
    if not inserted and ln.startswith("### [P"):
        out.append("## 意见（适配后，原卡为无 skill 对照组的自创格式）")
        out.append("")
        inserted = True
    m = re.match(r"^(类型|溯源|证据|维度|建议) / (.*)$", ln)
    if m:
        out.append(f"- {m.group(1)}：{m.group(2)}")
    else:
        out.append(ln)
io.open(dst, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print(f"适配完成：{dst}（插入意见节：{inserted}）")
