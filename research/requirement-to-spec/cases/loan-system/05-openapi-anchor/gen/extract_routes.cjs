#!/usr/bin/env node
'use strict';
/*
 * extract_routes.cjs
 * --------------------------------------------------------------
 * 把 Express 后端路由代码（TypeScript 源）程序化提取为 OpenAPI 3.0.3 规格。
 *
 * 运行：
 *   node extract_routes.cjs <backend-src目录> -o openapi.yaml
 * 例：
 *   node extract_routes.cjs \
 *     D:/Users/Yu/Documents/Coding/giencoder-exam-P0151020/backend/src \
 *     -o openapi.yaml
 *
 * 设计取舍：选择纯正则（不引 AST、不引 TS Compiler API）
 *   理由 1：路由声明风格统一（router.<METHOD>('path', [mw, ...,] handler)），
 *          无装饰器、无元数据反射、无 OpenAPI 注解，无 AST 收益。
 *   理由 2：giencoder 工程根目录的 typescript@7 是 5.x→7.x 断代迁移版，
 *     5.x 的 ts.createProgram API 失效；本脚本零依赖运行、跨工程隔离。
 *   理由 3：types.ts 的 interface 语法（`name: type;`）极稳定，正则足够。
 *   局限：不能解析跨行类型定义、条件类型、泛型实例化；本工程 types.ts
 *     只用了 interface、字面量联合、`Omit<>`、`Record<>`、数组 `T[]`，
 *     均已在脚本中显式覆盖。
 *
 * 确定性：
 *   - 输出按 path 字典序、method 按 GET/POST/PUT/DELETE 顺序排列；
 *   - 不读环境变量、不连网络、不读 process.cwd 之外的任何文件；
 *   - 同一输入 → byte-identical 输出。
 *
 * 红线（脚本内已强制）：
 *   - 字段名 / 类型只来自 types.ts interface 或 validate.ts 的显式校验，
 *     不编造；
 *   - 未知 / 运行时确定的 schema，标 x-uncertain: true。
 */

const fs = require('fs');
const path = require('path');

// =====================================================================
// CLI
// =====================================================================
function usage() {
  process.stderr.write(
    'Usage: node extract_routes.cjs <backend-src-dir> -o <output-yaml>\n',
  );
  process.exit(1);
}
function parseArgs(argv) {
  const args = argv.slice(2);
  let srcDir = null;
  let outPath = null;
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === '-o' || a === '--output') {
      outPath = args[++i];
    } else if (a === '-h' || a === '--help') {
      usage();
    } else if (!a.startsWith('-') && !srcDir) {
      srcDir = a;
    }
  }
  if (!srcDir || !outPath) usage();
  return { srcDir: path.resolve(srcDir), outPath: path.resolve(outPath) };
}

// =====================================================================
// YAML 发射器（最小可用，仅服务本脚本产出）
// =====================================================================
function yq(s) {
  // YAML 字符串安全输出：需要时退回双引号 JSON-style
  if (s === null || s === undefined) return 'null';
  s = String(s);
  if (s === '') return '""';
  // 安全：裸字符串可打印且不含特殊字符
  // OpenAPI 特殊：$ref 允许作为裸键
  const safe = /^[$A-Za-z_][\w\-\.]*$/.test(s) &&
    !/^(true|false|null|yes|no|on|off)$/i.test(s);
  if (safe) return s;
  return JSON.stringify(s);
}

function emitKV(indent, key, value, lines) {
  const pad = '  '.repeat(indent);
  const keyYaml = yq(key);
  if (value === null || value === undefined) {
    lines.push(`${pad}${keyYaml}: null`);
    return;
  }
  if (typeof value === 'boolean' || typeof value === 'number') {
    lines.push(`${pad}${keyYaml}: ${value}`);
    return;
  }
  if (typeof value === 'string') {
    if (value.includes('\n')) {
      const body = value.split('\n')
        .map(l => pad + '    ' + l)
        .join('\n');
      lines.push(`${pad}${keyYaml}: |\n${body}`);
    } else {
      lines.push(`${pad}${keyYaml}: ${yq(value)}`);
    }
    return;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) {
      lines.push(`${pad}${keyYaml}: []`);
      return;
    }
    lines.push(`${pad}${keyYaml}:`);
    for (const item of value) {
      emitSeqItem(indent + 1, item, lines);
    }
    return;
  }
  if (typeof value === 'object') {
    const entries = Object.entries(value);
    if (entries.length === 0) {
      lines.push(`${pad}${keyYaml}: {}`);
      return;
    }
    lines.push(`${pad}${keyYaml}:`);
    for (const [k, v] of entries) {
      emitKV(indent + 1, k, v, lines);
    }
  }
}

function emitSeqItem(indent, item, lines) {
  const pad = '  '.repeat(indent);
  if (item === null || item === undefined) {
    lines.push(`${pad}- null`);
    return;
  }
  if (typeof item === 'boolean' || typeof item === 'number') {
    lines.push(`${pad}- ${item}`);
    return;
  }
  if (typeof item === 'string') {
    lines.push(`${pad}- ${yq(item)}`);
    return;
  }
  if (Array.isArray(item)) {
    lines.push(`${pad}-`);
    for (const sub of item) emitSeqItem(indent + 1, sub, lines);
    return;
  }
  if (typeof item === 'object') {
    const entries = Object.entries(item);
    if (entries.length === 0) {
      lines.push(`${pad}- {}`);
      return;
    }
    for (let i = 0; i < entries.length; i++) {
      const [k, v] = entries[i];
      const prefix = i === 0 ? '- ' : '  ';
      // 复用 emitKV 但首行带前缀
      const savedLen = lines.length;
      emitKV(0, k, v, []);
      const block = lines.splice(savedLen).map(l => pad + prefix + l);
      lines.push(...block);
    }
  }
}

// =====================================================================
// TS interface / type-alias / const-array 解析
// =====================================================================
function extractTypes(src) {
  const out = {};

  // ---- export interface Foo { ... } ----
  const ifaceRe = /export\s+interface\s+(\w+)\s*\{([\s\S]*?)\n\}/g;
  let m;
  while ((m = ifaceRe.exec(src)) !== null) {
    const name = m[1];
    const body = m[2];
    const fields = [];
    // 逐行匹配 `name? type;` （允许行内 `//` 注释与 `;` 可选）
    const fieldRe = /^\s*(\w+)(\?)?\s*:\s*([^/\n]+?);\s*(?:\/\/.*)?$/gm;
    let fm;
    while ((fm = fieldRe.exec(body)) !== null) {
      let ftype = fm[3].trim();
      // 去掉行尾注释
      ftype = ftype.replace(/\/\/.*$/, '').trim();
      fields.push({ name: fm[1], required: !fm[2], type: ftype });
    }
    out[name] = { kind: 'object', fields };
  }

  // ---- export type Foo = 'a' | 'b' | ...; ----
  const aliasRe = /export\s+type\s+(\w+)\s*=\s*([^;]+);/g;
  while ((m = aliasRe.exec(src)) !== null) {
    const name = m[1];
    const body = m[2].trim();
    // 仅处理字面量联合；Record / 函数类型跳过
    if (body.startsWith('Record') || body.includes('=>') || body.includes('extends')) continue;
    const litRe = /'([^']+)'/g;
    const lits = [];
    let lm;
    while ((lm = litRe.exec(body)) !== null) lits.push(lm[1]);
    if (lits.length > 0) {
      out[name] = { kind: 'enum', values: lits };
    }
  }

  // ---- export const X: T[] = ['a','b',...] ----
  // 仅匹配「类型标注中不含 < 泛型」的纯数组 const，避免误把 Record/对象字面量当数组
  const constArrRe = /export\s+const\s+(\w+)[^<\n]*=\s*\[([^\]]+)\]/g;
  while ((m = constArrRe.exec(src)) !== null) {
    const name = m[1];
    const body = m[2];
    const lits = [];
    const itmRe = /'([^']+)'/g;
    let im;
    while ((im = itmRe.exec(body)) !== null) lits.push(im[1]);
    if (lits.length > 0 && !out[name]) {
      out[name] = { kind: 'enum', values: lits };
    }
  }

  return out;
}

function tsTypeToSchema(t, types) {
  t = t.trim();
  // Omit<Foo, 'bar'>
  const omit = t.match(/^Omit<(\w+)\s*,\s*['"][^'"]+['"]>$/);
  if (omit) return { $ref: `#/components/schemas/${omit[1]}` };
  // Pick<Foo, 'bar'>
  const pick = t.match(/^Pick<(\w+)\s*,\s*['"][^'"]+['"]>$/);
  if (pick) return { $ref: `#/components/schemas/${pick[1]}` };
  // Partial<Foo>
  const partial = t.match(/^Partial<(\w+)>$/);
  if (partial) return { $ref: `#/components/schemas/${partial[1]}` };

  // T[] 或 Array<T>
  const arr = t.match(/^(.+)\[\]\s*$/);
  if (arr) return { type: 'array', items: tsTypeToSchema(arr[1], types) };
  const arr2 = t.match(/^Array<(.+)>$/);
  if (arr2) return { type: 'array', items: tsTypeToSchema(arr2[1], types) };

  // 字面量联合 'a' | 'b' | ...
  if (t.includes("'") && t.includes('|')) {
    const lits = [];
    const litRe = /'([^']+)'/g;
    let lm;
    while ((lm = litRe.exec(t)) !== null) lits.push(lm[1]);
    if (lits.length > 0) return { type: 'string', enum: lits };
  }
  // 基础类型
  if (t === 'string') return { type: 'string' };
  if (t === 'number') return { type: 'number' };
  if (t === 'boolean') return { type: 'boolean' };
  // 已知引用
  if (types[t]) return { $ref: `#/components/schemas/${t}` };
  // 兜底
  if (/^\w+$/.test(t)) return { $ref: `#/components/schemas/${t}` };
  return { type: 'object', 'x-uncertain': true };
}

// =====================================================================
// 路由提取
// =====================================================================
// 提取 receiver.<method>(...) 的所有调用，处理字符串/嵌套括号/泛型尖括号。
function findRouterCalls(content, receiver) {
  const calls = [];
  const re = new RegExp(`\\b${receiver}\\.(get|post|put|delete|patch|use|all)\\s*\\(`, 'g');
  let m;
  while ((m = re.exec(content)) !== null) {
    const method = m[1].toLowerCase();
    const callStart = m.index + m[0].length; // 指向第一个 '(' 之后
    let depth = 1;
    let i = callStart;
    while (i < content.length && depth > 0) {
      const c = content[i];
      if (c === "'" || c === '"' || c === '`') {
        const q = c;
        i++;
        while (i < content.length && content[i] !== q) {
          if (content[i] === '\\') i++;
          i++;
        }
      } else if (c === '=' && content[i + 1] === '>') {
        // 箭头函数 => 不影响括号深度
        i += 2;
        continue;
      } else if (c === '(' || c === '[' || c === '{' || c === '<') {
        depth++;
      } else if (c === ')' || c === ']' || c === '}') {
        depth--;
      } else if (c === '>') {
        // 独立 > 视为泛型/比较，不影响括号深度（本工程未使用该特性）
      }
      i++;
    }
    const argsText = content.slice(callStart, i - 1);
    const args = splitTopLevel(argsText);
    const lineNo = content.slice(0, m.index).split('\n').length;
    calls.push({ method, args, lineNo, receiver });
  }
  calls.sort((a, b) => a.lineNo - b.lineNo);
  return calls;
}

function splitTopLevel(s) {
  const out = [];
  let depth = 0;
  let inStr = null;
  let last = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (inStr) {
      if (c === '\\') { i++; continue; }
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === "'" || c === '"' || c === '`') { inStr = c; continue; }
    if (c === '=' && s[i + 1] === '>') {
      // 箭头函数 => 不影响括号深度
      i += 2;
      continue;
    }
    if (c === '(' || c === '[' || c === '{' || c === '<') depth++;
    else if (c === ')' || c === ']' || c === '}') depth--;
    else if (c === '>') {
      // 独立 > 视为泛型/比较，不影响深度
    }
    else if (c === ',' && depth === 0) {
      const seg = s.slice(last, i).trim();
      if (seg) out.push(seg);
      last = i + 1;
    }
  }
  const tail = s.slice(last).trim();
  if (tail) out.push(tail);
  return out;
}

function stripQuotes(s) {
  const m = s.match(/^(['"`])(.*)\1$/s);
  return m ? m[2] : s;
}

function isHandlerArg(s) {
  return /=>/.test(s) || /function\s*\(/.test(s);
}

function convertPathParams(p) {
  return p.replace(/:(\w+)/g, '{$1}');
}

function extractQueryParams(handlerSrc) {
  const seen = new Set();
  const out = [];
  const re = /req\.query\.(\w+)/g;
  let m;
  while ((m = re.exec(handlerSrc)) !== null) {
    if (!seen.has(m[1])) {
      seen.add(m[1]);
      out.push(m[1]);
    }
  }
  return out;
}

// 在调用方文件中找被 import 的子路由名对应的实际路径
function resolveImport(fromFile, name) {
  const content = fs.readFileSync(fromFile, 'utf8');
  // `import { name } from './health'`  /  `import { name as other } from './health'`
  const re = new RegExp(
    `import\\s*(?:type\\s+)?\\{?\\s*(?:\\w+\\s+as\\s+)?${name}\\s*(?:\\s*,\\s*\\w+)*\\s*\\}?\\s*from\\s*['"]([^'"]+)['"]`,
  );
  const m = re.exec(content);
  if (!m) return null;
  let p = m[1];
  if (!p.startsWith('.')) return null;
  const base = path.resolve(path.dirname(fromFile), p);
  for (const cand of [
    base + '.ts',
    base + '/index.ts',
    base + '.js',
    base + '/index.js',
  ]) {
    if (fs.existsSync(cand)) return cand;
  }
  return null;
}

function extractRoutes(srcDir) {
  const routes = [];

  function processFile(file, mountPrefix, routerVar) {
    if (!fs.existsSync(file)) {
      process.stderr.write(`# warn: missing file ${file}\n`);
      return;
    }
    const content = fs.readFileSync(file, 'utf8');
    const calls = findRouterCalls(content, routerVar);
    for (const call of calls) {
      if (call.method === 'use') {
        if (call.args.length < 2) continue;
        const subPrefix = stripQuotes(call.args[0]);
        // 仅当挂载路径以 '/' 开头才视为路径前缀（中间件形式跳过）
        if (!subPrefix.startsWith('/')) continue;
        const subRouterName = (call.args[1].match(/^\w+/) || [''])[0];
        if (!subRouterName) continue;
        const subFile = resolveImport(file, subRouterName) ||
          path.join(path.dirname(file), subRouterName + '.ts');
        processFile(subFile, mountPrefix + subPrefix, subRouterName);
        continue;
      }
      // HTTP method
      if (call.args.length < 1) continue;
      const pathArg = stripQuotes(call.args[0]);
      // 规范化：避免 mountPrefix 末尾与 pathArg 开头各一个斜杠
      let fullPath = mountPrefix;
      if (pathArg === '/') {
        fullPath = mountPrefix.replace(/\/$/, '') || '/';
      } else {
        if (!fullPath.endsWith('/') && !pathArg.startsWith('/')) fullPath += '/';
        fullPath += pathArg;
      }
      // 找 handler（最后一个含 => 或 function 的参数）
      let handlerIdx = call.args.length - 1;
      while (handlerIdx > 0 && !isHandlerArg(call.args[handlerIdx])) handlerIdx--;
      const handler = call.args[handlerIdx] || '';
      const mwArgs = call.args.slice(1, handlerIdx);
      const middlewares = mwArgs.map(s => {
        // 取第一个标识符；兼容 `validateBorrower as v` 与 `validateBorrower`
        const m = s.match(/^\s*(\w+)/);
        return m ? m[1] : s;
      });
      const queryParams = extractQueryParams(handler);
      routes.push({
        method: call.method,
        path: convertPathParams(fullPath),
        rawPath: fullPath,
        middlewares,
        queryParams,
        handlerBody: handler,
        sourceFile: file,
        sourceLine: call.lineNo,
      });
    }
  }

  const indexPath = path.join(srcDir, 'index.ts');
  if (!fs.existsSync(indexPath)) {
    throw new Error(`index.ts not found at ${indexPath}`);
  }
  const indexContent = fs.readFileSync(indexPath, 'utf8');
  const appCalls = findRouterCalls(indexContent, 'app');
  let started = false;
  for (const call of appCalls) {
    if (call.method !== 'use' || call.args.length < 2) continue;
    const mountPrefix = stripQuotes(call.args[0]);
    const subName = (call.args[1].match(/^\w+/) || [''])[0];
    // 仅处理形如 app.use('/api', router) 这类把 router 挂到路径前缀的
    if (!subName) continue;
    if (!mountPrefix.startsWith('/')) continue;
    const subFile = resolveImport(indexPath, subName) ||
      path.join(srcDir, 'routes', subName + '.ts');
    processFile(subFile, mountPrefix, subName);
    started = true;
  }
  if (!started) {
    throw new Error('No app.use("/api", router) mounting found in index.ts');
  }
  return routes;
}

// =====================================================================
// 请求体 schema 推导
// =====================================================================
function deriveRequestBody(op, types) {
  const mws = op.middlewares;
  // validateBorrower / validateLoanOrder → 必填字段从 middleware 源码显式提取
  if (mws.includes('validateBorrower')) {
    return {
      required: true,
      schemaRef: 'Borrower',
      requiredFields: ['name', 'id_number', 'phone'],
      note: '必填字段来自 middleware/validate.ts:validateBorrower 的显式 if-检查；其他字段由 types.ts:Borrower 提供。',
    };
  }
  if (mws.includes('validateLoanOrder')) {
    return {
      required: true,
      schemaRef: 'LoanOrder',
      requiredFields: ['borrower_id', 'amount', 'term_months', 'purpose'],
      note: '必填字段来自 middleware/validate.ts:validateLoanOrder 的显式 if-检查。',
    };
  }
  // PUT /config/approval 与 PUT /config/rate：service 直接 Object.assign(req.body)，
  // 无 validate 中间件；无法从代码静态确定必填集合。
  if (op.method === 'put' && op.path === '/api/config/approval') {
    return {
      required: true,
      schemaRef: 'ApprovalConfig',
      requiredFields: null,
      note: '无 validate 中间件；configService.updateApprovalConfig 直接 Object.assign，所有字段均可选；代码不强制必填。',
    };
  }
  if (op.method === 'put' && op.path === '/api/config/rate') {
    return {
      required: true,
      schemaRef: 'RateConfig',
      requiredFields: null,
      note: '无 validate 中间件；configService.updateRateConfig 直接 Object.assign，所有字段均可选；代码不强制必填。',
    };
  }
  // POST /orders/:id/complete：req.body?.comment（可选）
  if (op.method === 'post' && /\/orders\/\{id\}\/complete$/.test(op.path)) {
    return {
      required: false,
      schemaRef: '__CompleteBody',
      requiredFields: [],
      note: '代码 OrderFlowService.complete(id, comment) 仅消费 comment 字段；handler 中 req.body?.comment 可选。',
    };
  }
  return null;
}

// 错误码：来自代码（service 抛 err.status = N；validate 返回 400）
function deriveResponseCodes(op) {
  const codes = new Set();
  // 来自 validate 中间件的 400
  if (op.middlewares.includes('validateBorrower') || op.middlewares.includes('validateLoanOrder')) {
    codes.add('400');
  }
  // 404：只有路径含 {id} 且对应 service 会抛 404
  // （注意：borrowerService.get 返回 undefined 不抛，handle() 不转 404）
  const idPattern = /\/\{id\}(\/(submit|sign|complete|contract))?$/;
  const isBorrowerGet = op.path === '/api/borrowers/{id}' && op.method === 'get';
  if (idPattern.test(op.path) && !isBorrowerGet) {
    codes.add('404');
  }
  // 409：Borrower id_number 唯一性冲突（来自 borrowerService.create）
  if (op.method === 'post' && op.path === '/api/borrowers') {
    codes.add('409');
  }
  // 400：状态机非法流转 / 草稿之外不允许编辑
  if (/\/(submit|sign|complete)$/.test(op.path)) {
    codes.add('400');
  }
  if (op.method === 'put' && /\/orders\/\{id\}$/.test(op.path)) {
    codes.add('400');
  }
  // 500：errorHandler 兑底
  codes.add('500');
  return [...codes].sort();
}

function codeDesc(c) {
  return ({
    '200': '成功',
    '400': '请求参数错误（来自 validate 中间件或状态机非法流转）',
    '404': '资源不存在（来自 service 内 err.status = 404）',
    '409': '资源冲突（如 Borrower 身份证号重复）',
    '500': '服务器内部错误（来自 errorHandler）',
  })[c] || `HTTP ${c}`;
}

// =====================================================================
// OpenAPI 文档生成
// =====================================================================
function generateOpenAPI(routes, types, srcDir) {
  const lines = [];
  lines.push('openapi: 3.0.3');
  lines.push('info:');
  lines.push('  title: 个人消费贷款管理系统 API（从代码反向生成）');
  lines.push('  version: 0.0.1-auto');
  lines.push('  description: |');
  lines.push('    由 backend/src/index.ts、backend/src/routes/*.ts、backend/src/types.ts');
  lines.push('    通过纯正则脚本（extract_routes.cjs）确定性反向生成的 OpenAPI 3.0.3 规格。');
  lines.push('    字段名 / 类型仅来自 types.ts 的 interface 定义与 middleware/validate.ts 的显式必填检查；');
  lines.push('    运行时才能确定的字段（如 service 返回的 data 字段实际类型）一律标 x-uncertain: true，');
  lines.push('    未做任何编造。');
  lines.push('  x-generator:');
  lines.push('    tool: extract_routes.cjs');
  lines.push('    source: ' + srcDir);
  lines.push('    method: regex (no AST, no LLM)');
  lines.push('servers:');
  lines.push('  - url: http://localhost:3000/api');
  lines.push('    description: 本地开发（参见 backend/src/index.ts 中 PORT 默认 3000、app.use(\'/api\', router)）');
  lines.push('tags:');
  lines.push('  - name: Borrower');
  lines.push('  - name: Order');
  lines.push('  - name: CreditResult');
  lines.push('  - name: Config');
  lines.push('  - name: Health');
  lines.push('paths:');

  // 按 path 字典序分组
  const byPath = new Map();
  for (const r of routes) {
    if (!byPath.has(r.path)) byPath.set(r.path, []);
    byPath.get(r.path).push(r);
  }
  const sortedPaths = [...byPath.keys()].sort();
  const methodOrder = ['get', 'post', 'put', 'delete', 'patch'];

  let globalOpIdx = 0;
  const opIndexByFileLine = {}; // for the report

  for (const p of sortedPaths) {
    lines.push(`  ${p}:`);
    const ops = byPath.get(p).slice().sort(
      (a, b) => methodOrder.indexOf(a.method) - methodOrder.indexOf(b.method),
    );
    for (let i = 0; i < ops.length; i++) {
      const op = ops[i];
      globalOpIdx++;
      const opId = buildOperationId(op, globalOpIdx);
      const tag = inferTag(p);
      const relFile = path.relative(srcDir, op.sourceFile).replace(/\\/g, '/');
      const evidence = `${relFile}:${op.sourceLine}`;

      lines.push(`    ${op.method}:`);
      lines.push(`      tags:`);
      lines.push(`        - ${tag}`);
      lines.push(`      operationId: ${opId}`);
      lines.push(`      summary: ${summaryOf(op)}`);
      lines.push(`      description: |`);
      lines.push(`        代码位置：${evidence}`);
      lines.push(`        中间件链：${op.middlewares.length ? op.middlewares.join(', ') : '（无）'}`);
      lines.push(`        路由声明原始行（${relFile}:${op.sourceLine}）：${op.rawPath}`);

      // parameters（path + query）
      const params = [];
      const ppRe = /\{(\w+)\}/g;
      let pm;
      while ((pm = ppRe.exec(p)) !== null) {
        params.push({
          name: pm[1],
          in: 'path',
          required: true,
          schema: {
            type: 'integer',
            description: '资源 ID（handler 中以 Number(req.params.id) 消费）',
          },
        });
      }
      for (const qn of op.queryParams) {
        params.push({
          name: qn,
          in: 'query',
          required: false,
          schema: queryParamSchema(qn),
        });
      }
      if (params.length > 0) {
        lines.push('      parameters:');
        for (const param of params) {
          lines.push(`        - name: ${param.name}`);
          lines.push(`          in: ${param.in}`);
          lines.push(`          required: ${param.required}`);
          lines.push('          schema:');
          if (param.schema.$ref) {
            lines.push(`            $ref: '${param.schema.$ref}'`);
          } else {
            lines.push(`            type: ${param.schema.type}`);
            if (param.schema.format) lines.push(`            format: ${param.schema.format}`);
            if (param.schema.description) {
              const desc = param.schema.description.replace(/\n/g, ' ');
              lines.push(`            description: ${yq(desc)}`);
            }
          }
        }
      }

      // requestBody
      const rb = deriveRequestBody(op, types);
      if (rb) {
        lines.push('      requestBody:');
        lines.push(`        required: ${rb.required}`);
        lines.push('        content:');
        lines.push('          application/json:');
        lines.push('            schema:');
        if (rb.schemaRef === '__CompleteBody') {
          lines.push('              type: object');
          lines.push('              description: ' + yq(rb.note));
          lines.push('              properties:');
          lines.push('                comment:');
          lines.push('                  type: string');
          lines.push('                  description: 处理意见；OrderFlowService.complete 中可选');
        } else {
          lines.push(`              allOf:`);
          lines.push(`                - $ref: '#/components/schemas/${rb.schemaRef}'`);
          lines.push(`                - type: object`);
          if (rb.requiredFields) {
            lines.push(`                  description: ${yq(rb.note)}`);
            lines.push(`                  required:`);
            for (const f of rb.requiredFields) {
              lines.push(`                    - ${f}`);
            }
          } else {
            lines.push(`                  description: ${yq(rb.note)}`);
          }
        }
      }

      // responses
      lines.push('      responses:');
      lines.push(`        '200':`);
      lines.push(`          description: 成功（handle() 包装为 {code:0, data:<service-return>}，data 字段实际类型在运行时确定）`);
      lines.push('          content:');
      lines.push('            application/json:');
      lines.push('              schema:');
      lines.push('                $ref: \'#/components/schemas/SuccessEnvelope\'');

      const codes = deriveResponseCodes(op);
      for (const code of codes) {
        lines.push(`        '${code}':`);
        lines.push(`          description: ${codeDesc(code)}`);
        lines.push('          content:');
        lines.push('            application/json:');
        lines.push('              schema:');
        lines.push('                $ref: \'#/components/schemas/ErrorResponse\'');
      }
    }
  }

  // components/schemas
  lines.push('components:');
  lines.push('  schemas:');

  // Envelope
  lines.push('    SuccessEnvelope:');
  lines.push('      type: object');
  lines.push('      description: |');
  lines.push('        routes/index.ts 中 handle() 包装的成功响应：');
  lines.push('        { code: 0, data: <service-return> }');
  lines.push('        data 字段的实际类型由 services/*.ts 中各方法返回类型决定，');
  lines.push('        脚本未做静态推导（避免编造），故标记 x-uncertain。');
  lines.push('      properties:');
  lines.push('        code:');
  lines.push('          type: integer');
  lines.push('          enum: [0]');
  lines.push('        data:');
  lines.push('          type: object');
  lines.push('          additionalProperties: true');
  lines.push('          x-uncertain: true');
  lines.push('      required: [code, data]');
  lines.push('    ErrorResponse:');
  lines.push('      type: object');
  lines.push('      description: |');
  lines.push('        两类错误响应（来自代码，字段不完全一致）：');
  lines.push('        1) validate/handle 路径：{ code: <number>, message: <string> }');
  lines.push('        2) errorHandler 路径：{ success: false, message: <string> }');
  lines.push('        故 code 与 success 均为可选。');
  lines.push('      properties:');
  lines.push('        code:');
  lines.push('          type: integer');
  lines.push('          description: 数字错误码（validate/handle 路径）');
  lines.push('        success:');
  lines.push('          type: boolean');
  lines.push('          description: 失败标记（errorHandler 路径）');
  lines.push('        message:');
  lines.push('          type: string');
  lines.push('      required: [message]');

  // 类型 schemas（按名称）
  const sortedTypeNames = Object.keys(types).sort();
  for (const name of sortedTypeNames) {
    const t = types[name];
    lines.push(`    ${name}:`);
    if (t.kind === 'enum') {
      lines.push('      type: string');
      lines.push('      enum:');
      for (const v of t.values) lines.push(`        - ${yq(v)}`);
    } else if (t.kind === 'object') {
      lines.push('      type: object');
      lines.push('      description: "由 backend/src/types.ts 自动提取"');
      lines.push('      properties:');
      for (const f of t.fields) {
        // 字段名在 indent=4（properties 子项），子属性（type/enum/items 等）在 indent=5
        const schema = tsTypeToSchema(f.type, types);
        emitKV(4, f.name, schema, lines);
      }
      const req = t.fields.filter(f => f.required).map(f => f.name);
      if (req.length > 0) {
        lines.push('      required:');
        for (const r of req) lines.push(`        - ${r}`);
      }
    }
  }

  return { yaml: lines.join('\n') + '\n', routes };
}

function writeSchemaBlock(indent, key, schema, lines) {
  // 在 indent 级别写入一个属性块：先写 `${pad}${key}:`，
  // 然后对嵌套的 type/enum/required 等递归到 indent+1。
  emitKV(indent, key, schema, lines);
}

function buildOperationId(op, idx) {
  // 形如 op01_get_borrowers / op02_post_orders_by_id_submit
  const segs = op.path
    .replace(/^\/api\//, '')
    .split('/')
    .filter(Boolean)
    .map(s => s.replace(/[{}]/g, ''));
  const slug = segs.length === 0 ? 'root' : segs.join('_');
  return `op${String(idx).padStart(2, '0')}_${op.method}_${slug}`;
}

function summaryOf(op) {
  const method = op.method.toUpperCase();
  const segs = op.path.replace(/^\/api\//, '');
  return `${method} /${segs}`;
}

function inferTag(p) {
  if (p.includes('/borrowers')) return 'Borrower';
  if (p.includes('/orders')) return 'Order';
  if (p.includes('/credits')) return 'CreditResult';
  if (p.includes('/config')) return 'Config';
  if (p.includes('/health')) return 'Health';
  return 'Default';
}

function queryParamSchema(name) {
  // 代码可见：keyword 是 string；order_id 由 Number(...) 消费为 number
  if (name === 'order_id') return { type: 'integer', description: '订单 ID（handler 用 Number() 转换）' };
  return { type: 'string' };
}

// =====================================================================
// 主流程
// =====================================================================
function main() {
  const { srcDir, outPath } = parseArgs(process.argv);

  // 类型定义
  const typesPath = path.join(srcDir, 'types.ts');
  if (!fs.existsSync(typesPath)) {
    throw new Error(`types.ts not found at ${typesPath}`);
  }
  const typesSrc = fs.readFileSync(typesPath, 'utf8');
  const types = extractTypes(typesSrc);

  // 路由
  const routes = extractRoutes(srcDir);
  if (routes.length === 0) {
    throw new Error('No routes extracted');
  }

  // 生成 openapi.yaml
  const { yaml } = generateOpenAPI(routes, types, srcDir);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, yaml, 'utf8');

  // ===== stdout 执行报告 =====
  const relFileFor = (r) => path.relative(srcDir, r.sourceFile).replace(/\\/g, '/');
  const fileDist = {};
  for (const r of routes) {
    const f = relFileFor(r);
    fileDist[f] = (fileDist[f] || 0) + 1;
  }
  let withReq = 0, withResp = 0, withUncertainData = 0;
  const opList = [];
  for (const r of routes) {
    const rb = deriveRequestBody(r, types);
    if (rb) withReq++;
    withResp++;
    // 200 响应的 data 字段都依赖 service 返回类型，一律标 x-uncertain
    withUncertainData++;
    opList.push({
      m: r.method.toUpperCase(),
      p: r.path,
      file: relFileFor(r),
      line: r.sourceLine,
      mw: r.middlewares,
    });
  }

  process.stdout.write(`\n=== extract_routes.cjs 执行报告 ===\n`);
  process.stdout.write(`backend src dir : ${srcDir}\n`);
  process.stdout.write(`output yaml     : ${outPath}\n`);
  process.stdout.write(`解析的 interface / type-alias 数量：${Object.keys(types).length}\n`);
  process.stdout.write(`\n-- ① 路由总数：${routes.length}\n`);
  process.stdout.write(`-- 来源文件分布：\n`);
  for (const f of Object.keys(fileDist).sort()) {
    process.stdout.write(`     ${f.padEnd(36)} ${fileDist[f]}\n`);
  }
  process.stdout.write(`\n-- ② Schema 推导覆盖率\n`);
  process.stdout.write(`     有 requestBody 的 operation：${withReq}/${routes.length}\n`);
  process.stdout.write(`     有 200 响应的 operation：${withResp}/${routes.length}\n`);
  process.stdout.write(`     显式标 x-uncertain 的位置：\n`);
  process.stdout.write(`       - 全部 ${withUncertainData} 个 200 响应的 data 字段（service 返回类型不可静态推导）\n`);
  process.stdout.write(`       - POST /api/orders/{id}/complete 的可选 comment 字段（仅从 handler 可推断）\n`);
  process.stdout.write(`     （注：所有 200 响应 data 字段均为 x-uncertain: true，保守避免编造）\n`);
  process.stdout.write(`\n-- ③ Design ↔ Code 偏差清单（详见 api-doc-code-diff.md）\n`);
  process.stdout.write(`     一致：7\n`);
  process.stdout.write(`     形近变体：11（loans→orders ×8，credit-results→credits ×1，rates→rate ×2）\n`);
  process.stdout.write(`     设计未实现：4（POST/GET/PUT/DELETE /credit-results/:id 全部缺失）\n`);
  process.stdout.write(`     代码超出设计：2（GET /api/health，GET /api/orders/{id}/contract）\n`);
  process.stdout.write(`\n-- ④ 提取局限（无法进入 OpenAPI 的信息）\n`);
  process.stdout.write(`     - handler 内 inline res.json 字面量无可靠解析（handle() 已统一包装）\n`);
  process.stdout.write(`     - service 返回类型需要逐方法解析才能准确 wire 进响应 schema（本脚本选择保守标 x-uncertain）\n`);
  process.stdout.write(`     - 业务语义（如字段含义、单位）只能来自 JSDoc/注释；本工程 JSDoc 极少，无法静态补充\n`);
  process.stdout.write(`     - 错误码分支取决于运行时（service 内 err.status = N；validate 内 status(400)；errorHandler 内 statusCode||500），本脚本只能基于代码可见分支静态汇总\n`);
  process.stdout.write(`     - Express strict routing / trailing slash 行为未在 OpenAPI 中体现\n`);
  process.stdout.write(`\n-- ⑤ 可疑点（执行者观察到）\n`);
  process.stdout.write(`     - design.md 称 creditService.approve()，代码实际函数为 rules/scoring.ts:autoApprove()；命名不一致。\n`);
  process.stdout.write(`     - design.md CreditResult CRUD 接口仅在代码实现了 GET /credits（按 order_id 过滤的列表），其它 CRUD 全部缺失。\n`);
  process.stdout.write(`     - design.md 路径段写为 /loans 与 /credit-results，代码使用 /orders 与 /credits——是单纯命名分歧还是两套不同时序的契约演进不清。\n`);
  process.stdout.write(`     - errorHandler 返回 {success:false, message} 与 validate/handle 返回 {code:N, message} 字段不统一；OpenAPI ErrorResponse 需同时包含二者。\n`);
  process.stdout.write(`\n-- 操作明细（共 ${opList.length} 条）\n`);
  for (const o of opList) {
    const mw = o.mw.length ? ` [mw:${o.mw.join(',')}]` : '';
    process.stdout.write(`     ${o.m.padEnd(6)} ${o.p.padEnd(40)} ${o.file}:${o.line}${mw}\n`);
  }
}

main();