#!/usr/bin/env python3
"""puml2xmi: PlantUML 类图子集 → XMI 2.5.1 (UML 2.5) 生成器（requirement-to-spec B' 路线）

支持语法子集：
  class X { +attr: Type ... }     属性（可见性 +-/#，类型；操作行忽略）
  abstract class X / interface X  （isAbstract="true"，最小版同 Class 处理）
  enum X { LIT1 LIT2 }            枚举
  A "1" --> "0..*" B : label      关联（多重性两端可选；-->/<--/o-- 等箭头变体按关联处理）
  X <|-- Y                        泛化（Y 子类）

类型映射（内置，对齐 model2owl ePO 默认配置的 xsd 命名）：
  String→xsd:string  Decimal→xsd:decimal  Integer→xsd:integer  Boolean→xsd:boolean
  Date→xsd:date  DateTime→xsd:dateTime  其他类型名原样保留（类引用或未知类型）
"""
import re
import sys

TYPE_MAP = {
    'String': 'xsd:string', 'string': 'xsd:string',
    'Decimal': 'xsd:decimal', 'decimal': 'xsd:decimal', 'double': 'xsd:decimal', 'float': 'xsd:decimal',
    'Integer': 'xsd:integer', 'int': 'xsd:integer', 'Long': 'xsd:integer', 'long': 'xsd:integer',
    'Boolean': 'xsd:boolean', 'bool': 'xsd:boolean',
    'Date': 'xsd:date', 'DateTime': 'xsd:dateTime',
}
ASSOC_RE = re.compile(r'^(\w+)\s*(?:"([^"]*)")?\s*(?:-+|\.+|o-|\*-)\s*(?:left|right)?\s*(?:>|\|)?\s*(?:"([^"]*)")?\s*(\w+)\s*(?::\s*(.+))?$')
GEN_RE = re.compile(r'^(\w+)\s*<\|--\s*(\w+)$')


class Elem:
    def __init__(self, eid):
        self.id = eid


def parse_puml(text):
    classes = {}      # name -> {'attrs':[(vis,name,type)], 'abstract':bool, 'parent':None}
    enums = {}        # name -> [literals]
    assoc_defs = []   # (a, mult_a, b, mult_b, label)
    generalizations = []  # (child, parent)
    lines = text.splitlines()
    i, cur, cur_type = 0, None, None
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("'") or line.startswith('@start') or line.startswith('@end'):
            continue
        m_enum_open = re.match(r'^enum\s+(\w+)\s*\{?$', line)
        m_enum_inline = re.match(r'^enum\s+(\w+)\s*\{\s*(.+)\s*\}$', line)
        m_cls_open = re.match(r'^(?:abstract\s+)?(?:class|interface)\s+(\w+)(?:\s*(<<.*?>>))?\s*\{?$', line)
        if cur is None:
            if m_enum_inline:
                enums.setdefault(m_enum_inline.group(1), [])
                enums[m_enum_inline.group(1)].extend(m_enum_inline.group(2).split())
            elif m_enum_open:
                cur, cur_type = m_enum_open.group(1), 'enum'
                enums.setdefault(cur, [])
            elif m_cls_open:
                name = m_cls_open.group(1)
                abstract = line.startswith('abstract')
                classes.setdefault(name, {'attrs': [], 'abstract': abstract, 'parent': None})
                cur, cur_type = name, 'class'
            elif line == '}':
                pass
            else:
                g = GEN_RE.match(line)
                if g:
                    generalizations.append((g.group(2), g.group(1)))  # (child, parent)
                    continue
                a = ASSOC_RE.match(line)
                if a:
                    # 组序: 1=A 2=multA 3=multB 4=B 5=label
                    assoc_defs.append((a.group(1), a.group(2), a.group(4), a.group(3), a.group(5) or ''))
                else:
                    # 单行泛化变体 A --|> B
                    m2 = re.match(r'^(\w+)\s*--\|>\s*(\w+)$', line)
                    if m2:
                        generalizations.append((m2.group(2), m2.group(1)))
        else:
            if line == '}':
                cur = None
                continue
            if cur_type == 'enum':
                for lit in line.split():
                    enums[cur].append(lit)
            else:
                am = re.match(r'^([+\-#~])?\s*([\w]+)\s*(\(\))?\s*(?::\s*(.+?))?$', line)
                if am and not am.group(3):  # 属性（操作忽略）
                    vis = {'+': 'public', '-': 'private', '#': 'protected', '~': 'package'}.get(am.group(1), 'public')
                    classes[cur]['attrs'].append((vis, am.group(2), (am.group(4) or '').strip()))
    return classes, enums, assoc_defs, generalizations


def gen_xmi(text, model_name='Model', prefix=None):
    classes, enums, assoc_defs, gens = parse_puml(text)
    q = (lambda n: f'{prefix}:{n}') if prefix else (lambda n: n)
    ids = {}
    counter = [0]

    def nid(prefix):
        counter[0] += 1
        return f'{prefix}{counter[0]:04d}'

    datatypes_needed = {}
    for c in classes.values():
        for _, _, t in c['attrs']:
            if t:
                qt = TYPE_MAP.get(t, t if (':' in t or t[0:1].islower() and t not in classes and t not in enums) else None)
                if qt is None:
                    qt = t  # 保留原样（可能是类引用）
                if qt.startswith(('xsd:', 'rdfs:', 'epo:')):
                    datatypes_needed[qt] = None
    for qt in datatypes_needed:
        ids[('dt', qt)] = nid('DT_')

    for n in list(classes) + list(enums):
        ids[('el', n)] = nid('CL_')
    gen_pairs = set(gens)
    for child, parent in gen_pairs:
        if child in classes:
            classes[child]['parent'] = parent

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<xmi:XMI xmi:version="2.5.1" xmlns:xmi="http://www.omg.org/spec/XMI/20131001" xmlns:uml="http://www.omg.org/spec/UML/20131001">',
           f'\t<uml:Model xmi:type="uml:Model" xmi:id="{nid("MD_")}" name="{model_name}">',
           '\t\t<packagedElement xmi:type="uml:Package" xmi:id="%s" name="ConceptualModel">' % nid('PK_')]
    for qt, did in datatypes_needed.items():
        out.append(f'\t\t\t<packagedElement xmi:type="uml:DataType" xmi:id="{did}" name="{qt}"/>')
    for name, lits in enums.items():
        out.append(f'\t\t\t<packagedElement xmi:type="uml:Enumeration" xmi:id="{ids[("el",name)]}" name="{q(name)}">')
        for lit in lits:
            out.append(f'\t\t\t\t<ownedLiteral xmi:type="uml:EnumerationLiteral" xmi:id="{nid("LT_")}" name="{lit}"/>')
        out.append('\t\t\t</packagedElement>')
    # 预生成关联端属性 id
    assoc_ends = {}
    for a, ma, b, mb, label in assoc_defs:
        assoc_ends[(a, b, label)] = (nid('AE_'), nid('AE_'))
    for name, info in classes.items():
        abstract_attr = ' isAbstract="true"' if info['abstract'] else ''
        out.append(f'\t\t\t<packagedElement xmi:type="uml:Class" xmi:id="{ids[("el",name)]}" name="{q(name)}"{abstract_attr}>')
        for vis, aname, atype in info['attrs']:
            # 跳过本类中由关联端生成的同名属性（多重性端优先走关联）
            pid = nid('AT_')
            if atype:
                qt = TYPE_MAP.get(atype, atype)
                tid = ids.get(('dt', qt)) or ids.get(('el', qt))
                type_xml = f'<type xmi:idref="{tid}"/>' if tid else f'<!-- 未识别类型: {atype} -->'
            else:
                type_xml = ''
            out.append(f'\t\t\t\t<ownedAttribute xmi:type="uml:Property" xmi:id="{pid}" name="{q(aname)}" visibility="{vis}">{type_xml}</ownedAttribute>')
        if info['parent'] and info['parent'] in ids:
            pid = nid('GE_')
            out.append(f'\t\t\t\t<generalization xmi:type="uml:Generalization" xmi:id="{pid}" general="{ids[("el",info["parent"])]}"/>')
        out.append('\t\t\t</packagedElement>')
    for (a, b, label), (ea, eb) in assoc_ends.items():
        ma = next((x[1] for x in assoc_defs if x[0] == a and x[2] == b and x[4] == label), None)
        mb = next((x[3] for x in assoc_defs if x[0] == a and x[2] == b and x[4] == label), None)
        aid = nid('AS_')
        out.append(f'\t\t\t<packagedElement xmi:type="uml:Association" xmi:id="{aid}" name="{q(label or a+"2"+b)}">')
        out.append(f'\t\t\t\t<memberEnd xmi:idref="{ea}"/>')
        out.append(f'\t\t\t\t<memberEnd xmi:idref="{eb}"/>')
        # 端属性以 ownedEnd 形式挂在关联上（自包含，两端类型+多重性显式）
        for endid, cls, mult in ((ea, a, ma), (eb, b, mb)):
            lower, upper = parse_mult(mult)
            mult_xml = ''
            if lower is not None:
                mult_xml += f'<lowerValue xmi:type="uml:LiteralInteger" xmi:id="{nid("LI_")}" value="{lower}"/>'
            if upper is not None:
                mult_xml += f'<upperValue xmi:type="uml:LiteralUnlimitedNatural" xmi:id="{nid("LU_")}" value="{upper}"/>'
            out.append(f'\t\t\t\t<ownedEnd xmi:type="uml:Property" xmi:id="{endid}" name="{q(cls.lower())}" association="{aid}">'
                       f'<type xmi:idref="{ids[("el",cls)]}"/>{mult_xml}</ownedEnd>')
        out.append('\t\t\t</packagedElement>')
    out.append('\t\t</packagedElement>')
    out.append('\t</uml:Model>')
    out.append('</xmi:XMI>')
    return '\n'.join(out)


def parse_mult(m):
    if not m:
        return None, None
    m = m.strip()
    if m == '*':
        return '0', '*'
    if '..' in m:
        lo, hi = m.split('..', 1)
        return lo.strip(), hi.strip()
    return m, m


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else None
    text = open(src, encoding='utf-8').read()
    name = src.replace('\\', '/').split('/')[-1].rsplit('.', 1)[0]
    xml = gen_xmi(text, model_name=name, prefix=prefix)
    open(dst, 'w', encoding='utf-8').write(xml)
    print(f'OK: {dst} ({len(xml)} bytes)')
