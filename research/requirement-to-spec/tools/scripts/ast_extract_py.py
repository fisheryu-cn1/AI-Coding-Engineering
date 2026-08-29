#!/usr/bin/env python3
"""ast_extract_py: Python 代码 → PlantUML 类图子集（AST 确定性提取·双通道配置的标准通道）

标准库 ast 实现，零依赖。提取：class（含方法签名与参数）、enum.Enum 子类→enum、
dataclass 装饰类、模块级函数→模块伪类（与 TS 版 ast_extract_ts.cjs 的归组约定一致）。
用途：结构骨架的标准提取（method/19 §3 提取配置决策——高频位单通道标准方法）。
用法: python ast_extract_py.py <源文件或目录> [-o out.puml] [-r]
  -r 递归目录（跳过 __pycache__/tests/node_modules/venv）
"""
import argparse, ast, os, sys


def sig(fn: ast.FunctionDef, src_lines):
    args = [a.arg for a in fn.args.posonlyargs + fn.args.args]
    if fn.args.vararg:
        args.append('*' + fn.args.vararg.arg)
    ret = ''
    if fn.returns:
        try:
            ret = ' : ' + ast.unparse(fn.returns)
        except Exception:
            ret = ''
    return f"{fn.name}({', '.join(args)}){ret}"


def extract(path):
    tree = ast.parse(open(path, encoding='utf-8').read())
    module = os.path.splitext(os.path.basename(path))[0]
    classes = {}  # name -> (kind, attrs, methods)
    order = []

    def add(name, kind):
        if name not in classes:
            classes[name] = [kind, [], []]
            order.append(name)
        return classes[name]

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases if hasattr(b, 'id') or isinstance(b, ast.Attribute)]
            is_enum = any('Enum' in b or 'enum' in b for b in bases)
            c = add(node.name, 'enum' if is_enum else 'class')
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not item.name.startswith('__') or item.name in ('__init__',):
                        c[2].append(sig(item, None))
                elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    c[1].append(item.target.id)
                elif isinstance(item, ast.Assign):
                    for t in item.targets:
                        if isinstance(t, ast.Name):
                            c[1].append(t.id)
            if is_enum:  # 枚举成员 = 类属性赋值
                c[1] = [a for a in c[1]]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add(module, 'module-fns')[2].append(sig(node, None))
    return classes, order


def emit(classes, order, sources):
    out = ['@startuml', "' ===== AST 确定性提取（Python 标准库 ast，零依赖）=====",
           f"' 来源: {len(sources)} 个文件; class/Enum 子类/模块级函数; 方法为真实签名", "' 语义摘要(@logic)属 LLM 通道，本通道不产"]
    for name in order:
        kind, attrs, methods = classes[name]
        if kind == 'enum':
            out.append(f'enum {name} {{')
            out += ['  ' + a for a in attrs]
            out.append('}')
        else:
            kw = 'class' if kind == 'class' else 'class'
            out.append(f'{kw} {name} {{')
            out += ['  +' + a for a in attrs]
            out += ['  +' + m for m in methods]
            out.append('}')
    out.append('@enduml')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('-o', default=None)
    ap.add_argument('-r', action='store_true')
    args = ap.parse_args()
    files = []
    if os.path.isdir(args.src):
        for root, dirs, fns in os.walk(args.src):
            dirs[:] = [d for d in dirs if d not in ('__pycache__', 'node_modules', 'venv', '.git', 'dist', '__tests__')]
            for f in sorted(fns):
                if f.endswith('.py'):
                    files.append(os.path.join(root, f))
    else:
        files = [args.src]
    classes, order = {}, []
    for f in files:
        try:
            cs, od = extract(f)
            for n in od:
                if n in classes:
                    for m in cs[n][2]:
                        classes[n][2].append(m)
                else:
                    classes[n] = cs[n]
                    order.append(n)
        except SyntaxError as e:
            print(f'SKIP {f}: {e}', file=sys.stderr)
    text = emit(classes, order, files)
    out = args.o or (args.src.rstrip('/\\').replace(os.sep, '_') + '_ast.puml')
    open(out, 'w', encoding='utf-8').write(text)
    print(f'OK: {out}（{len(order)} 类/模块, {len(files)} 文件）')


if __name__ == '__main__':
    main()
