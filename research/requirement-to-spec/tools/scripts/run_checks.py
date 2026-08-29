#!/usr/bin/env python3
"""run_checks: 案例目录的统一检查入口（最佳审核方法 v1 的常规轻检查链, method/19 §2）

自动发现案例结构并依次执行（全部确定性、零 LLM）：
  1. 转换验证   formal/*.puml 全部经 puml2owl 转换（语法面）
  2. 状态机     文件名含 flow 的 .puml 跑 fsm_check 五性质
  3. 规则集     formal/rules*.py 逐个执行（退出码 0 视为 PASS）
  4. 绑定闭包   formal/model-bindings.md 存在时跑 check_model_bindings（FR 体系自动探测）
  5. 执行队列   review/ 存在时重生成 G90
  6. HermiT     --heavy 时对每张类图跑 owlready2+HermiT 一致性（需 Java）
文档级五项检查（check_doc_closure）需按案例参数手跑（见 method/14）。
用法: python run_checks.py <case_dir> [--heavy]
退出码: 0=无 FAIL; 1=有 FAIL。
"""
import glob, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else ''


def main():
    case = sys.argv[1] if len(sys.argv) > 1 else '.'
    heavy = '--heavy' in sys.argv
    results = []

    def rec(name, ok, detail):
        results.append((name, 'PASS' if ok else 'FAIL', detail))

    # 1 转换验证（仅概念类图——状态图与 OWL 无对应, method/13 §2, 不做转换）
    pumls = sorted(glob.glob(os.path.join(case, 'formal', '*.puml')))
    for p in [x for x in pumls if 'flow' not in os.path.basename(x)]:
        out = os.path.join(os.environ.get('TEMP', '/tmp'), 'p2s_rc_' + os.path.basename(p)[:-4])
        rc, last = run([sys.executable, os.path.join(HERE, 'puml2owl.py'), p, out])
        rec(f'转换 {os.path.basename(p)}', rc == 0, last[:80])

    # 2 状态机
    for p in [p for p in pumls if 'flow' in os.path.basename(p)]:
        rc, last = run([sys.executable, os.path.join(HERE, 'fsm_check.py'), p])
        rec(f'状态机 {os.path.basename(p)}', rc == 0, last[:80])

    # 3 规则集
    for r in sorted(glob.glob(os.path.join(case, 'formal', 'rules*.py'))):
        rc, last = run([sys.executable, r])
        rec(f'规则 {os.path.basename(r)}', rc == 0, last[:80])

    # 4 绑定闭包
    bind = os.path.join(case, 'formal', 'model-bindings.md')
    if os.path.exists(bind):
        raw = os.path.join(case, 'raw')
        reg = next(iter(sorted(glob.glob(os.path.join(raw, '*requirements-register*.md'))
                               + glob.glob(os.path.join(raw, '*功能需求*.md')) + glob.glob(os.path.join(raw, '*登记*.md')))), None)
        cmd = [sys.executable, os.path.join(HERE, 'check_model_bindings.py'), case]
        if reg:
            txt = open(reg, encoding='utf-8').read()
            if re.search(r'\bFR-\d', txt):
                cmd += ['--id-regex', r'FR-\d+(?:\.\d+)?[ab]?', '--register', reg]
            else:
                cmd += ['--register', reg]
        rc, last = run(cmd)
        rec('绑定闭包', rc == 0, last[:80])
    else:
        results.append(('绑定闭包', 'SKIP', '无 model-bindings.md'))

    # 5 执行队列
    if os.path.isdir(os.path.join(case, 'review')):
        rc, last = run([sys.executable, os.path.join(HERE, 'collect_review_actions.py'), case])
        rec('执行队列', rc == 0, last[:80])

    # 6 HermiT（可选重检查）
    if heavy:
        rc, last = run([sys.executable, '-c', f'''
import os; os.chdir(r'{os.path.join(HERE, "..", "env", "sandbox")}')
from owlready2 import get_ontology, sync_reasoner_hermit
for p in {pumls!r}:
    onto = get_ontology(p.replace('.puml', '.owl.rdf') if os.path.exists(p.replace('.puml', '.owl.rdf')) else p).load()
    try:
        sync_reasoner_hermit(); print(p, 'consistent')
    except Exception as e:
        print(p, 'FAIL', e); raise SystemExit(1)
'''])
        rec('HermiT(heavy)', rc == 0, last[:80])
    else:
        results.append(('HermiT', 'SKIP', '加 --heavy 启用（需 Java）'))

    print(f'== run_checks: {case} ==')
    for name, st, d in results:
        print(f'[{st:4}] {name:28} {d}')
    fails = [r for r in results if r[1] == 'FAIL']
    print('VERDICT:', 'ALL_GREEN' if not fails else f'{len(fails)} FAIL')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
