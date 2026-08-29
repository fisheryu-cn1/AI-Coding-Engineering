// ast_extract_ts: TypeScript 代码 → PlantUML 类图子集（AST 确定性提取·双通道配置的标准通道）
// 依赖 typescript@5.x（须锁 5.x——7.x 原生重构版 API 断代, method/19 §3）; 用法: node ast_extract_ts.cjs <根目录> <输出.puml>
// 双通道提取实验的通道一（对照 pi 的 LLM 通道 code-concept.puml）
let ts;
try { ts = require('typescript'); } catch { ts = require(process.env.P2S_TYPESCRIPT); } // 5.x 路径可经 P2S_TYPESCRIPT 注入
const fs = require('fs'), path = require('path');
const ROOT = process.argv[2];
const FILES = [
  'backend/src/types.ts', 'backend/src/store.ts', 'backend/src/rules/scoring.ts',
  'backend/src/rules/rates.ts', 'backend/src/services/borrowerService.ts',
  'backend/src/services/loanOrderService.ts', 'backend/src/services/configService.ts',
  'backend/src/services/orderFlowService.ts', 'frontend/src/api/index.ts', 'frontend/src/api/http.ts',
];
const typeTxt = n => n ? n.getText(sf).replace(/\n\s*/g, ' ').slice(0, 40) : '';
let sf; // 当前 SourceFile（getText 锚定）
const classes = {}; // name -> {attrs:[], methods:[], kind}
function add(name, kind) { if (!classes[name]) classes[name] = { kind, attrs: [], methods: [] }; return classes[name]; }

function walk(n) {
  const bn = d => d.name ? d.name.text : null;
  if (ts.isInterfaceDeclaration(n)) {
    const c = add(bn(n), 'interface');
    for (const m of n.members) if (m.name) c.attrs.push(m.name.getText(sf));
  } else if (ts.isEnumDeclaration(n)) {
    const c = add(bn(n), 'enum');
    for (const m of n.members) if (m.name) c.attrs.push(m.name.getText(sf));
  } else if (ts.isTypeAliasDeclaration(n)) {
    const lits = [];
    (function collect(x){ if (ts.isUnionTypeNode(x)) x.types.forEach(collect);
      else if (ts.isLiteralTypeNode(x)) lits.push(x.getText(sf).replace(/['"]/g,''));
      else lits.push(null); })(n.type);
    if (lits.length && lits.every(x=>x!==null)) { const c = add(bn(n),'enum'); lits.forEach(l=>c.attrs.push(l)); }
    else add(bn(n),'typealias').attrs.push(typeTxt(n.type));
  } else if (ts.isClassDeclaration(n) && bn(n)) {
    const c = add(bn(n), 'class');
    for (const m of n.members) {
      if (m.name && ts.isMethodDeclaration(m)) c.methods.push(sig(m));
      else if (m.name && ts.isPropertyDeclaration(m)) c.attrs.push(m.name.getText(sf));
    }
  } else if ((ts.isFunctionDeclaration(n) || ts.isArrowFunction(n)) && n.parent && ts.isSourceFile(n.parent)) {
    // 模块级导出函数 → 归入「文件名对应的伪类」（与 pi 的服务类建模对齐）
    const fn = n.name ? n.name.text : (n.parent.statements.find(s => ts.isVariableStatement(s) && s.declarationList.declarations[0].initializer === n) || {}).name?.escapedText;
    if (fn) { const holder = add(curModule, 'module-fns'); holder.methods.push(sig(n)); }
  } else if (ts.isVariableStatement(n) && n.parent && ts.isSourceFile(n.parent)) {
    for (const d of n.declarationList.declarations)
      if (ts.isArrowFunction(d.initializer) || ts.isFunctionExpression(d.initializer))
        add(curModule, 'module-fns').methods.push(d.name.escapedText + sigTail(d.initializer));
  }
  ts.forEachChild(n, walk);
}
const sigTail = f => '(' + f.parameters.map(p => p.name.getText(sf)).join(', ') + ')' + (f.type ? ' : ' + typeTxt(f.type).replace(/[^\w.<>\[\]| ]/g,'') : '');
const sig = m => (m.name ? m.name.getText(sf) : '') + (ts.isFunctionDeclaration(m) || ts.isMethodDeclaration(m) ? sigTail(m) : '');

let curModule = '';
for (const rel of FILES) {
  const full = path.join(ROOT, rel);
  const src = fs.readFileSync(full, 'utf8');
  curModule = path.basename(rel, '.ts');
  sf = ts.createSourceFile(full, src, ts.ScriptTarget.ES2022, true);
  walk(sf);
}
const P = s => s.replace(/[^#\w\u4e00-\u9fa5]/g, '_');
const out = ["@startuml", "' ===== AST 确定性提取（typescript@5.9 Compiler API，双通道实验通道一）=====",
  "' 来源文件: " + FILES.length + ' 个（backend 8 + frontend 2）; 提取: interface/enum/typealias/class/模块级函数',
  "' 注: 方法参数为真实签名; 类型别名/枚举字面量全量; 无语义摘要(@logic 属 LLM 通道)"];
for (const [name, c] of Object.entries(classes)) {
  if (c.kind === 'enum') {
    out.push(`enum ${P(name)} {`); c.attrs.forEach(a => out.push('  ' + P(a))); out.push('}');
  } else {
    out.push(`${c.kind === 'interface' ? 'interface' : 'class'} ${P(name)} {`);
    c.attrs.forEach(a => out.push('  +' + P(a)));
    c.methods.forEach(m => out.push('  +' + m)); // 签名原文(参数/返回类型为合法标识符)
    out.push('}');
  }
}
out.push('@enduml');
fs.writeFileSync(process.argv[3] || 'code-ast-concept.puml', out.join('\n'));
console.log('OK:', Object.keys(classes).length, '个类型/模块 →', out.length, '行');
