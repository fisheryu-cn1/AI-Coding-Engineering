#!/usr/bin/env python3
"""check_env: 环境检测 + 全组件冒烟（p2s-kit v0，plan/02 §3.2）

把当初手工完成的五件套冒烟（tools/env/README 的踩坑验证）变成一条命令：
  python check_env.py            # 只检测（版本/可用性）
  python check_env.py --smoke    # 检测 + 最小功能冒烟（Z3 求解/OWL+HermiT 推理/pySHACL 校验/puml2owl 转换）
退出码: 0=全部通过, 1=有缺失（冒烟失败也计入）, 2=可选组件缺失（仅警告）。
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

ok, warn, fail = [], [], []


def report(name, good, detail, optional=False):
    (ok if good else (warn if optional else fail)).append(f'{name}: {"OK" if good else "MISSING"} {detail}')


# --- 检测 ---
import importlib.util
for pkg, minv in [('owlready2', '0.5'), ('pyshacl', '0.2'), ('rdflib', '6'), ('z3', None)]:
    spec = importlib.util.find_spec(pkg)
    if spec is None:
        report(f'pip:{pkg}', False, '(pip install)', optional=False)
    else:
        try:
            mod = __import__(pkg)
            v = getattr(mod, '__version__', '?')
            report(f'pip:{pkg}', True, f'v{v}')
        except Exception as e:
            report(f'pip:{pkg}', False, str(e)[:60])

try:
    v = sys.version_info
    report('python', v >= (3, 10), f'{v.major}.{v.minor}.{v.micro}')
except Exception:
    pass

jr = subprocess.run(['java', '-version'], capture_output=True, text=True)
report('java(系统 PATH)', jr.returncode == 0,
       (jr.stderr or jr.stdout).splitlines()[0][:60] if jr.returncode == 0 else 'HermiT 需要 JVM——安装 Temurin 17+')

jar = os.path.join(ROOT, 'tools', 'env', 'jars', 'plantuml.jar')
report('plantuml.jar(可选,仅渲染)', os.path.exists(jar), jar if os.path.exists(jar) else 'SVG 渲染不可用', optional=True)

# --- 冒烟 ---
if '--smoke' in sys.argv and not fail:
    from z3 import Solver, Int
    s = Solver(); x = Int('x'); s.add(x > 1, x < 3)
    report('smoke:Z3', s.check() is not None and str(s.check()) == 'sat', '求解 sat/unsat')

    from owlready2 import get_ontology, sync_reasoner_hermit
    import owlready2
    onto = get_ontology('http://t/smoke#')
    with onto:
        import types as pytypes
        A = pytypes.new_class('SmA', (owlready2.Thing,))
        B = pytypes.new_class('SmB', (owlready2.Thing,))
        owlready2.AllDisjoint([A, B])
        i = A('i1')
        try:
            sync_reasoner_hermit()
            report('smoke:HermiT(经owlready2)', True, '一致性推理可执行')
        except owlready2.OwlReadyInconsistentOntologyError:
            report('smoke:HermiT', False, '意外不一致（最小本体不应触发）')

    from rdflib import Graph
    from pyshacl import validate
    g = Graph(); g.parse(data='@prefix ex: <http://t/s#> .\nex:a ex:p "v" .', format='turtle')
    sh = Graph(); sh.parse(data='''@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://t/s#> .
ex:AShape a sh:NodeShape ; sh:targetSubjectsOf ex:p ;
  sh:property [ sh:path ex:p ; sh:minCount 1 ; sh:pattern "^v$" ] .''', format='turtle')
    c, _, _ = validate(data_graph=g, shacl_graph=sh)
    report('smoke:pySHACL', c, f'Conforms={c}')

    # puml2owl 冒烟：内联最小 puml 写临时文件转换
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), 'p2s_smoke.puml')
    open(tmp, 'w', encoding='utf-8').write(
        "@startuml\nclass T {\n  +a : String\n}\nenum E {\n  x\n}\n' @required: T.a\n@enduml\n")
    out = os.path.join(tempfile.gettempdir(), 'p2s_smoke')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'puml2owl.py'), tmp, out],
                       capture_output=True, text=True)
    good = r.returncode == 0 and os.path.exists(out + '.shacl.ttl') and 'minCount' in open(out + '.shacl.ttl', encoding='utf-8').read()
    report('smoke:puml2owl(@required→sh:minCount)', good, r.stdout.strip()[:60] or r.stderr.strip()[-80:])

print('== p2s 环境自检 ==')
for line in ok:
    print('  [OK] ', line)
for line in warn:
    print('  [WARN]', line)
for line in fail:
    print('  [FAIL]', line)
verdict = 'ALL_PASS' if not fail and not warn else ('PASS_WITH_WARNINGS' if not fail else 'INCOMPLETE')
print('VERDICT:', verdict)
sys.exit(0 if not fail else 1)
