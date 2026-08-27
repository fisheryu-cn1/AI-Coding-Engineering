#!/usr/bin/env python3
"""collect_review_actions: 聚合 review/ 填写件中的执行标记 → G90-执行队列.md（method/16 §6）

确定性脚本（零 LLM）。只扫 E 前缀填写件（V 只读/G 生成物不扫）。两类来源：
  1) 评审表（E3x- 前缀）：表格行执行标记列（匹配 [待执行:…]/[裁决后执行:…]），
     行锚点 = 第 1 列行 ID（如 TA1-03）；
  2) 决策记录（E4x- 前缀）：`## 决策ID` 节的 `- 机器执行:` 行，锚点 = 决策 ID，
     并带出 `- 状态:` 行。
输出分两组：待执行（可立即执行，含已解锁）/ 裁决后执行（等待决策状态变更，含退回重议）。
用法: collect_review_actions.py <case_dir> [--expand]
退出码: 0=正常生成（含零队列）。
"""
import argparse, os, re, sys

MARK_RE = re.compile(r'\[(待执行|裁决后执行|驳回执行)[:：]?\s*([^\]]*)\]')
ROWID_RE = re.compile(r'^[A-Z]{1,4}\d+-\d+$')          # TA1-03 / SC3-12
SECTION_RE = re.compile(r'^##\s+(.+)$')                # 决策记录一决策一节（16 号规约 §4）


def parse_mark(cell):
    m = MARK_RE.search(cell)
    return (m.group(1), m.group(2).strip()) if m else None


def collect_tables(path):
    """评审表：返回 [(行ID, 条目ID, 执行标记元组, 整行文本)]。"""
    rows = []
    for line in open(path, encoding='utf-8').read().splitlines():
        if not line.startswith('|') or re.match(r'^\|[\s:-]+\|', line):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 7 or not ROWID_RE.match(cells[0]):
            continue
        mk = parse_mark(cells[-2])  # 倒数第 2 列 = 执行标记（末列为签注）
        if mk:
            rows.append((cells[0], cells[1] if len(cells) > 1 else '', mk, line.strip()))
    return rows


def collect_decisions(path):
    """决策记录：返回 [(决策ID+名, 状态, 执行标记元组, 节文本摘要)]。"""
    out, cur_id, cur_status, buf = [], None, None, []
    def flush():
        if cur_id and buf:
            for line in buf:
                mk = parse_mark(line)
                if mk:
                    out.append((cur_id, cur_status, mk, '\n'.join(buf).strip()))
    for line in open(path, encoding='utf-8').read().splitlines():
        m = SECTION_RE.match(line)
        if m:
            flush()
            cur_id, cur_status, buf = m.group(1).strip(), '', [line]
        elif cur_id:
            buf.append(line)
            sm = re.match(r'-\s*状态[:：]\s*(.+)', line)
            if sm:
                cur_status = sm.group(1).strip()
    flush()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case_dir')
    ap.add_argument('--expand', action='store_true', help='队列条目嵌入来源行/节原文')
    args = ap.parse_args()
    rdir = os.path.join(args.case_dir, 'review')
    if not os.path.isdir(rdir):
        sys.exit(f'ERR: {rdir} 不存在')

    ready, gated = [], []   # 待执行(含已解锁) / 裁决后执行(含退回重议)
    for fn in sorted(os.listdir(rdir)):
        if not fn.endswith('.md') or not fn.startswith('E'):
            continue        # 只扫 E 前缀人工填写件（V 只读 / G 生成物 / 其他不扫）
        p = os.path.join(rdir, fn)
        if fn.startswith('E4'):   # 决策记录（S4 阶段）
            for did, status, mk, text in collect_decisions(p):
                # 解锁规则（16 号规约 §4）：裁决后执行 + 状态已裁决/已消解 → 决策已完成，动作转入待执行组
                unlocked = mk[0] == '裁决后执行' and ('已裁决' in status or '已消解' in status)
                (ready if (mk[0] == '待执行' or unlocked) else gated).append((did, status, mk, fn, text))
        else:
            for rid, cid, mk, line in collect_tables(p):
                (ready if mk[0] == '待执行' else gated).append((rid, '', mk, fn, line))

    L = ['# 执行队列（G90-）', '',
         '> 生成物：collect_review_actions.py 从 review/ 填写件聚合，勿手改；重生成命令见文末。',
         '> 下游 LLM 调用纪律（method/16 §6）：以本队列为调用上下文，按锚点拉取最小行级上下文，禁止整读填写件全表。', '']

    for title, items in (('待执行（可立即执行）', ready), ('裁决后执行（等待对应决策/输入状态变更）', gated)):
        L += [f'## {title}（{len(items)} 条）', '']
        if args.expand:
            for aid, status, mk, fn, text in items:
                L += [f'### [{aid}]', '',
                      f'- 动作: {mk[1] or mk[0]}', f'- 来源: {fn}（锚点检索: `{aid.split("（")[0].strip()}`）',
                      f'- 等待状态: {status or "—"}', '', '```', text, '```', '']
        else:
            L += ['| 锚点 | 动作 | 来源 | 等待状态 |', '|---|---|---|---|']
            for aid, status, mk, fn, text in items:
                act = mk[1].replace('|', '\\|') or mk[0]
                L.append(f'| {aid} | {act} | {fn} | {status or "—"} |')
            L.append('')

    L += ['## 生成记录', '',
          f'- 命令: python tools/scripts/collect_review_actions.py <case_dir>' + (' --expand' if args.expand else ''),
          f'- 待执行 {len(ready)} 条 / 裁决后执行 {len(gated)} 条']
    out = os.path.join(rdir, 'G90-执行队列.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'OK: {out}（待执行 {len(ready)} / 裁决后执行 {len(gated)}）')


if __name__ == '__main__':
    main()
