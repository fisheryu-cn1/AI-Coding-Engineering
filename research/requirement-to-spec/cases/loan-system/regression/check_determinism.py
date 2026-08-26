#!/usr/bin/env python3
"""决定性回归：同输入重跑 puml2owl，比对产物 sha256 与基准（路径自锚定）"""
import hashlib, subprocess, sys, os
REG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(REG, '..', '..', '..'))
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
out = os.path.join(REG, 'rerun.owl.rdf')
r = subprocess.run([sys.executable, os.path.join(ROOT,'tools','scripts','puml2owl.py'),
                os.path.join(REG,'mini.puml'), os.path.join(REG,'rerun')], capture_output=True, text=True)
if r.returncode != 0:
    print('REGEN FAILED:', r.stderr[-300:]); sys.exit(2)
base = sha(os.path.join(REG,'baseline','mini.owl.rdf'))
new = sha(out)
print(f'baseline : {base}')
print(f'rerun    : {new}')
print('DETERMINISTIC' if base == new else 'DRIFT!')
sys.exit(0 if base == new else 1)
