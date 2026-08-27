#!/usr/bin/env python3
"""puml2owl: PlantUML 类图子集 → OWL 本体 + SHACL shapes（B 方案直映射）

复用 puml2xmi 的解析器；映射规则按备忘 §9.3 语义差异表：
- 泛化 → subClassOf（不默认补 disjoint；枚举字面量间自动 disjoint——OWL Individuals 语义）
- 关联 → ObjectProperty + domain/range + 多重性 → cardinality 限定（仅非默认端生成）
- 属性类型 → xsd datatype；指向枚举/类的属性 → 对应类关联
输出：<out_prefix>.owl.ttl（本体）与 <out_prefix>.shacl.ttl（shapes）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from puml2xmi import parse_puml, TYPE_MAP


def build(puml_path, ns="http://example.org/loan#", prefix="loan"):
    from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty, AllDisjoint
    import types as pytypes
    text = open(puml_path, encoding='utf-8').read()
    classes, enums, assoc_defs, gens = parse_puml(text)
    # 决策注解提取（method/13 词表）：' @disjoint: A, B
    import re as _re
    disjoint_groups = [[x.strip() for x in m.group(1).split(',')]
                       for m in _re.finditer(r"^'\s*@disjoint:\s*(.+)$", text, _re.M)]
    onto = get_ontology(ns)
    with onto:
        # 枚举：类 + 字面量个体 + 字面量间互斥
        enum_classes, enum_inds = {}, {}
        for ename, lits in enums.items():
            ec = pytypes.new_class(ename, (Thing,))
            enum_classes[ename] = ec
            lit_classes = []
            for l in lits:
                lc = pytypes.new_class(f'{ename}_{l}', (ec,))
                lit_classes.append(lc)
                lc(f'lit_{ename}_{l}')
            enum_inds[ename] = [lc[0] for lc in [(c,) for c in lit_classes]]
            if len(lit_classes) > 1:
                AllDisjoint(lit_classes)
        # 类
        cls_map = {}
        for cname, info in classes.items():
            cls_map[cname] = pytypes.new_class(cname, (Thing,))
        for child, parent in set(gens):
            if child in cls_map and parent in cls_map:
                cls_map[child].is_a.append(cls_map[parent])
        onto.disjoint_groups_resolved = []
        for grp in disjoint_groups:
            members = []
            for c in grp:
                if c in enum_classes or c in cls_map:
                    members.append(enum_classes.get(c) or cls_map.get(c))
                else:  # Enum_Literal 子类形式
                    members.append(onto.search_one(iri=f'{onto.base_iri}{c}'))
            members = [m for m in members if m]
            if len(members) >= 2:
                AllDisjoint(members)
                onto.disjoint_groups_resolved.append(grp)
        # 关联
        prop_map = {}
        for a, ma, b, mb, label in assoc_defs:
            pname = label if (label and label.replace('_', '').isalnum()) else f'has{b}'
            if pname in prop_map:
                continue
            p = pytypes.new_class(pname, (ObjectProperty,))
            p.domain = [cls_map[a]]
            p.range = [enum_classes.get(b, cls_map.get(b, Thing))]
            prop_map[pname] = (p, a, b)
            # 属性：datatype 属性或指向枚举的对象属性
        for cname, info in classes.items():
            for vis, aname, atype in info['attrs']:
                if atype and atype in enums:
                    p = pytypes.new_class(f'has{atype}', (ObjectProperty,))
                    p.domain = [cls_map[cname]]
                    p.range = [enum_classes[atype]]
                elif atype and atype in classes:
                    p = pytypes.new_class(f'has{atype}', (ObjectProperty,))
                    p.domain = [cls_map[cname]]
                    p.range = [cls_map[atype]]
                else:
                    p = pytypes.new_class(f'attr{aname.capitalize()}', (DataProperty,))
                    p.domain = [cls_map[cname]]
                    p.range = [_xsd(atype)]
    return onto, classes, enums, cls_map, enum_classes, prop_map


def _xsd(t):
    from owlready2 import Restriction
    import owlready2
    m = {'xsd:string': str, 'xsd:decimal': float, 'xsd:integer': int, 'xsd:boolean': bool,
         'xsd:date': str, 'xsd:dateTime': str}
    return m.get(TYPE_MAP.get(t, t), str)


def _parse_mult(m):
    if not m:
        return None, None
    m = m.strip()
    if m == '*':
        return '0', '*'
    if '..' in m:
        lo, hi = m.split('..', 1)
        return lo.strip(), hi.strip()
    return m, m


def gen_shacl(onto, classes, enums, cls_map, enum_classes, out_path, ns, prefix, src_text):
    lines = [f'@prefix {prefix}: <{ns}> .', '@prefix sh: <http://www.w3.org/ns/shacl#> .',
             '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .', '']
    for cname in classes:
        lines.append(f'{prefix}:{cname}Shape a sh:NodeShape ;')
        lines.append(f'  sh:targetClass {prefix}:{cname} .')
    for ename, lits in enums.items():
        lit_list = ' '.join(f'{prefix}:lit_{ename}_{l}' for l in lits)
        lines.append(f'{prefix}:{ename}Shape a sh:NodeShape ;')
        lines.append(f'  sh:targetClass {prefix}:{ename} ;')
        lines.append(f'  sh:property [ sh:path [ sh:inversePath {prefix}:has{ename} ] ] .')
    # 约束注解（method/13 §3）：@required → sh:minCount；@pattern → sh:pattern
    import re as _re
    src = src_text
    prop_lines = []
    for m in _re.finditer(r"^'\s*@required:\s*(.+)$", src, _re.M):
        for spec in m.group(1).split(','):
            cname, _, pname = spec.strip().partition('.')
            if cname in classes:
                prop_lines.append(f'{prefix}:{cname}Shape sh:property [ sh:path {prefix}:attr{pname.strip().capitalize()} ; sh:minCount 1 ] .')
    for m in _re.finditer(r"^'\s*@pattern:\s*(.+?)\s*=\s*(.+)$", src, _re.M):
        spec, pat = m.group(1).strip(), m.group(2).strip()
        cname, _, pname = spec.partition('.')
        if cname in classes:
            prop_lines.append(f'{prefix}:{cname}Shape sh:property [ sh:path {prefix}:attr{pname.strip().capitalize()} ; sh:pattern "{pat}" ] .')
    lines.extend(prop_lines)
    open(out_path, 'w', encoding='utf-8').write('\n'.join(lines))


if __name__ == '__main__':
    src, out_prefix = sys.argv[1], sys.argv[2]
    ns = sys.argv[3] if len(sys.argv) > 3 else 'http://example.org/loan#'
    prefix = sys.argv[4] if len(sys.argv) > 4 else 'loan'
    onto, classes, enums, cls_map, enum_classes, prop_map = build(src, ns, prefix)
    onto.save(file=out_prefix + '.owl.rdf', format='rdfxml')
    src_text = open(src, encoding='utf-8').read()
    gen_shacl(onto, classes, enums, cls_map, enum_classes, out_prefix + '.shacl.ttl', ns, prefix, src_text)
    n_cls = len(classes) + len(enums)
    print(f'OK: {out_prefix}.owl.rdf（{n_cls} 类/枚举, {len(prop_map)} 关联）+ .shacl.ttl')
