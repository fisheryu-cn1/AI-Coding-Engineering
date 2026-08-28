#!/usr/bin/env python3
"""check_doc_closure: 文档级闭包检查器（评审模式·三层防线的追溯层适配到 NL 文档）

被评审 md 文档 vs 参照登记表，五项确定性检查（零 LLM）：
  A 反向闭包  —— 文档中出现的条目 ID 必须存在于登记表（抓私造前缀/悬挂引用）
  B 覆盖闭包  —— 登记表已接受 ID 在文档中的出现计数（0=未承接；1=弱承接线索）
  C 验收映射  —— 非豁免 ID 必须出现在验收节（--accept 节标题）的关联列（抓"规则表有、验收标准无"断点）
  D 受控词表  —— 文档中疑似状态字面量必须属于 --vocab 闭集（抓 rejection 式拼写漂移/私造状态）
  E 验收行 ID —— 验收节表格是否有行级 ID 列（可被下游精确引用的结构前提）
用法:
  check_doc_closure.py <doc.md> <register.md> --accept "验收标准" \
      [--vocab draft,pending,...] [--exempt BR-001,BR-002]
退出码: 0=PASS, 1=FINDINGS。
"""
import argparse, re, sys

ID_RE = re.compile(r'\b(BR|FUNC|RULE|FLOW|FIELD|UI|NFR|DEL)-\d{3}\b')


def read(p):
    return open(p, encoding='utf-8').read()


def register_ids(reg_text):
    ids = []
    for m in ID_RE.finditer(reg_text):
        if m.group(0) not in ids:
            ids.append(m.group(0))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('doc'); ap.add_argument('register')
    ap.add_argument('--accept', required=True, help='验收节标题（含该标题起、至下一同级标题止）')
    ap.add_argument('--vocab', default='', help='受控词表（逗号分隔，如状态字面量闭集）')
    ap.add_argument('--exempt', default='', help='C 检查豁免 ID（逗号分隔）')
    ap.add_argument('--term', default='', help='D 检查的上下文锚词（默认自动=vocab 首词所在表格行）')
    args = ap.parse_args()

    doc, reg = read(args.doc), read(args.register)
    reg_ids = register_ids(reg)
    doc_ids = sorted({m.group(0) for m in ID_RE.finditer(doc)})
    findings = []

    # A 反向闭包
    bogus = [i for i in doc_ids if i not in reg_ids]
    for i in bogus:
        findings.append(f'A 私造/悬挂引用: {i} 不在登记表')

    # 验收节切片
    idx = doc.find(args.accept)
    if idx < 0:
        sys.exit(f'ERR: 验收节标题 "{args.accept}" 未找到')
    nxt = re.search(r'^## ', doc[idx + 1:], re.M)
    accept_sec = doc[idx: idx + 1 + nxt.start()] if nxt else doc[idx:]

    # B 覆盖闭包
    counts = {i: len(re.findall(rf'\b{i}\b', doc)) for i in reg_ids}
    for i, c in counts.items():
        if c == 0:
            findings.append(f'B 未承接: {i} 在文档中零出现')
        elif c == 1:
            findings.append(f'B 弱承接(线索): {i} 仅出现 1 次')

    # C 验收映射
    exempt = {x.strip() for x in args.exempt.split(',') if x.strip()}
    for i in reg_ids:
        if i in exempt:
            continue
        if not re.search(rf'\b{i}\b', accept_sec):
            findings.append(f'C 验收断点: {i} 在验收节零出现（规则/范围有承接但无验收行）')

    # D 受控词表（状态字面量）：找文档中 ID-FLOW 或状态语境附近的英文 token
    vocab = [v.strip() for v in args.vocab.split(',') if v.strip()]
    if vocab:
        # 候选：与 vocab 词形近似的 token（编辑距离≤3 且首字母相同）或出现在状态枚举列表语境的英文词
        tokens = set(re.findall(r'\b[a-z][a-z_]{3,}\b', doc))
        near = []
        for t in tokens:
            if t in vocab:
                continue
            for v in vocab:
                if abs(len(t) - len(v)) <= 2 and t[0] == v[0] and _lev(t, v) <= 3:
                    near.append((t, v))
        for t, v in sorted(set(near)):
            findings.append(f'D 词表漂移: "{t}" 不在受控词表（最近 "{v}"，出现 {doc.count(t)} 次）')

    # E 验收行 ID 列
    first_table = None
    for line in accept_sec.splitlines():
        if line.startswith('|'):
            first_table = line
            break
    has_row_id = bool(first_table) and bool(re.match(r'^\|\s*(ID|编号|AC)', first_table))
    if not has_row_id:
        findings.append('E 验收行无 ID 列: 验收节表首列不是 ID/编号/AC——验收行无法被下游精确引用')

    print(f'== check_doc_closure: {args.doc} ==')
    print(f'登记 ID {len(reg_ids)} | 文档引用 ID {len(doc_ids)} | 豁免 {sorted(exempt) or "无"}')
    print(f'A 私造/悬挂: {len([f for f in findings if f[0] == "A"])} | '
          f'B 未承接 {[f for f in findings if f.startswith("B 未")].__len__()} / 弱承接线索 {len([f for f in findings if f.startswith("B 弱")])} | '
          f'C 验收断点: {len([f for f in findings if f[0] == "C"])} | '
          f'D 词表漂移: {len([f for f in findings if f[0] == "D"])} | E: {"触发" if any(f[0]=="E" for f in findings) else "未触发"}')
    for f in findings:
        print(f'FINDING[{f[0]}]: {f[2:]}')
    print('VERDICT:', 'PASS' if not findings else f'FINDINGS({len(findings)})')
    sys.exit(0 if not findings else 1)


def _lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


if __name__ == '__main__':
    main()
