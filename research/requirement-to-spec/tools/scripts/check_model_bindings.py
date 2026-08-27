#!/usr/bin/env python3
"""check_model_bindings: 需求登记 ↔ 模型绑定清单的引用闭包检查（R2 首件"ID 引用闭包"的模型侧原型）

三个方向（回填实验 A 的结论=缺失类缺陷对 OWL/SHACL 层不可见，唯本检查兜底）：
  A 覆盖闭包  —— 每个非豁免的已接受需求 ID 至少 1 条绑定行或 [暂缓] 行；
  B 解析闭包  —— 每条绑定的元素定位符必须能在其工件中解析（防清单与模型漂移）；
  C 反向闭包  —— 绑定行的 ID 必须存在于需求登记表（防私造，对照三方评估 K×4 DEL 私造缺陷）。
用法: check_model_bindings.py <case_dir> [--bindings PATH] [--register PATH]
退出码: 0=PASS, 1=FAIL。
"""
import argparse, os, re, sys
from html import unescape

REG_ID_RE = re.compile(r'\b(BR|FUNC|RULE|FLOW|FIELD|UI|NFR|DEL)-(\d{3})\b')
SPLIT_ID_RE = re.compile(r'^\s*((?:BR|FUNC|RULE|FLOW|FIELD|UI|NFR|DEL)-\d{3})\s*$')


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def table_rows(text, header):
    """提取 header 之后表格的数据行（二维列表），止于下一个 ## 或文件尾。"""
    out = []
    idx = text.find(header)
    if idx < 0:
        return out
    for line in text[idx:].splitlines()[1:]:
        if line.startswith('## '):
            break
        if line.startswith('|') and not re.match(r'^\|[\s:-]+\|', line):
            cells = [unescape(c.strip()) for c in line.strip('|').split('|')]
            if len(cells) >= 3:
                out.append(cells)
    return out


def parse_register_ids(text):
    ids = []
    for m in REG_ID_RE.finditer(text):
        i = f'{m.group(1)}-{m.group(2)}'
        if i not in ids:
            ids.append(i)
    return ids


def base_id(cell):
    return SPLIT_ID_RE.match(re.sub(r'[（(].*$', '', cell).strip())


# ---- 定位符解析（在工件文本中查证元素仍存在）----

def resolve(locator, artifact_text):
    loc = unescape(locator).strip()
    kind, _, key = loc.partition(':')
    if kind == 'class':
        return bool(re.search(rf'^\s*class\s+{re.escape(key)}\s*\{{', artifact_text, re.M))
    if kind == 'enum':
        return bool(re.search(rf'^\s*enum\s+{re.escape(key)}\s*\{{', artifact_text, re.M))
    if kind == 'attr':
        cname, _, aname = key.partition('.')
        blk = re.search(rf'class\s+{re.escape(cname)}\s*\{{(.*?)\}}', artifact_text, re.S)
        return bool(blk and re.search(rf'\b{re.escape(aname)}\s*:', blk.group(1)))
    if kind == 'assoc':
        return bool(re.search(rf':\s*{re.escape(key)}\s*$', artifact_text, re.M))
    if kind == 'disjoint':
        pre = re.escape(key.rstrip('_'))
        return bool(re.search(rf"^'?\s*@disjoint:.*\b{pre}_\w+", artifact_text, re.M))
    if kind == 'decision':
        return bool(re.search(rf"@decision:.*{re.escape(key)}", artifact_text))
    if kind == 'z3tag':
        return bool(re.search(rf"assert_and_track\(.*?['\"]{re.escape(key)}", artifact_text, re.S))
    if kind == 'trans':
        a, _, b = key.partition('>')
        if b == '__END__':
            pat = rf'^\s*\[?\*?\]?\s*{re.escape(a)}\s*-->\s*\[\*\]'
        else:
            pat = rf'^\s*\[?\*?\]?\s*{re.escape(a)}\s*-->\s*{re.escape(b)}\b'
        return bool(re.search(pat, artifact_text, re.M))
    return None  # 未知语法按失败处理


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case_dir')
    ap.add_argument('--bindings', default=None)
    ap.add_argument('--register', default=None)
    args = ap.parse_args()

    reg_path = args.register or os.path.join(args.case_dir, 'raw', 'requirements-register.md')
    bind_path = args.bindings or os.path.join(args.case_dir, 'formal', 'model-bindings.md')
    reg_text, bind_text = read(reg_path), read(bind_path)

    reg_ids = parse_register_ids(reg_text)
    # 登记表只统计"已接受"的行内的首个 ID 归属；简化：出现即视为已接受（本项目登记表当前全为已接受）
    policy_rows = [r for r in table_rows(bind_text, '## 豁免政策') if r[0].startswith(('BR-', 'FUNC-', 'RULE-', 'FLOW-', 'FIELD-', 'UI-', 'NFR-', 'DEL-')) or r[0].endswith('-*')]
    bind_rows = [r for r in table_rows(bind_text, '## 绑定表') if REG_ID_RE.search(r[0])]

    exempt_prefixes = set()
    exempt_ids = set()
    for r in policy_rows:
        scope = r[0]
        if scope.endswith('-*'):
            exempt_prefixes.add(scope[:-2])
        else:
            m = base_id(scope)
            if m:
                exempt_ids.add(m.group(1))

    findings, deferred, resolved_ok = [], [], 0

    # B+C: 每条绑定解析 + 反向存在
    bound_bases = {}
    for cid_cell, artifact, locator, note in [(r + [''] * 4)[:4] for r in bind_rows]:
        m = base_id(cid_cell)
        if not m:
            findings.append(f'BADROW 绑定行 ID 无法解析: "{cid_cell}"')
            continue
        bid = m.group(1)
        bound_bases.setdefault(bid, 0)
        bound_bases[bid] += 1
        if bid not in reg_ids:
            findings.append(f'C 私造/失效引用: {bid} 不在需求登记表')
        if '[暂缓]' in note or '[暂缓]' in locator:
            deferred.append(f'{bid} ({cid_cell})')
            continue
        # 工件路径按 case_dir 相对解释
        apath = os.path.join(args.case_dir, artifact)
        if not os.path.exists(apath):
            findings.append(f'B 工件不存在: {bid} -> {artifact}')
            continue
        r = resolve(locator, read(apath))
        if r:
            resolved_ok += 1
        else:
            findings.append(f'B 定位符无法解析(模型漂移?): {bid} -> {locator}')

    # A: 覆盖闭包
    need = [i for i in reg_ids
            if i.split('-')[0] not in exempt_prefixes and i not in exempt_ids]
    for i in need:
        if i not in bound_bases:
            findings.append(f'A 未承接: {i} 无绑定且无 [暂缓] 行')

    print(f'== check_model_bindings: {os.path.basename(args.case_dir)} ==')
    print(f'登记 ID {len(reg_ids)} 个 | 豁免前缀 {sorted(exempt_prefixes)} | 豁免单条 {len(exempt_ids)} | 绑定行 {len(bind_rows)}')
    print(f'覆盖闭包 OK={len(need) - sum(1 for f in findings if f.startswith("A "))}/{len(need)} | '
          f'解析闭包 OK={resolved_ok} | 反向闭包 FINDING={sum(1 for f in findings if f.startswith("C "))}')
    for d in sorted(set(deferred)):
        print(f'DEFERRED: {d}')
    for f in findings:
        print(f'FINDING[{f[0]}]: {f[2:].strip()}')
    print('VERDICT:', 'PASS' if not findings else f'FAIL({len(findings)})')
    sys.exit(0 if not findings else 1)


if __name__ == '__main__':
    main()
