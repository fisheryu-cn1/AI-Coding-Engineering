# 按文件分组核验清单（2026-08-18-f62f287-run7-clean.md × 2026-08-18-f62f287-run8-clean.md）
A 13 条 / B 26 条 / 共 55 个文件组

> 用法：组内判定『哪些意见指向同一缺陷』；候选对仅按签名重叠系数提示（≥0.3），不作结论。宽意见（涉及多文件）会出现在多个组，判定后全局去重。

## cli/serve.py（A×1，B×2）
- A4 [P0] `kb serve viz` 启动入口可选依赖兜底不完备：`code/kb-app/src/kbapp/web/__init__.py` 在评审锚点 f62f287 中不存在，`cli/serve.py:viz_cmd` 内 `from kbapp.web import create_app` 无 try/except，启动直接 ImportError（RR-7a serve 入口兜底完备性）
- B10 [P1] cli/serve.py `viz_cmd` 可选依赖兜底不完备（仅捕获 uvicorn ImportError，fastapi/starlette 缺失崩）
- B11 [P1] cli/serve.py `--port` 无上界校验（用户输入透传）
  - 候选: A4 ↔ B10（重叠系数 1.00）
  - 候选: A4 ↔ B11（重叠系数 0.50）

## graph/extract.py（A×1，B×3）
- A5 [P1] `RELATES_TO` 边 MERGE 模式缺 `kind` 区分键，同 (src, dst) 不同 kind 关系互相覆盖（RR-4 #3 合并键完整 + RR-5 幂等性）
- B5 [P1] `extract.py` LLM 输出未做代码围栏/控制标记清洗，碰围栏直接 JSONDecodeError 跳过整文档
- B18 [P2] extract.py `text.count(name)` 无 word boundary，子串误匹配（"RAG" → "RAGged"）
- B23 [P3] 二次抽取覆盖 entity.description/aliases（隐式语义，未登记）
  - 候选: A5 ↔ B5（重叠系数 0.50）
  - 候选: A5 ↔ B18（重叠系数 0.50）
  - 候选: A5 ↔ B23（重叠系数 0.50）

## graph/ladybug_store.py（A×4，B×3）
- A1 [P0] `stage_tombstone_graph` 通过 `upsert_nodes` 全行 SET 把 Document 14 个字段（含 13 个非 PK 属性）覆盖为空串（RR-4 #1 属性保留）
- A2 [P0] 11 处读路径全部缺失 `valid_to` 过滤，墓碑文档的 Section / Entity / Topic / 邻域 / 路径仍出现在所有图查询（RR-4 #2 读路径过滤）
- A5 [P1] `RELATES_TO` 边 MERGE 模式缺 `kind` 区分键，同 (src, dst) 不同 kind 关系互相覆盖（RR-4 #3 合并键完整 + RR-5 幂等性）
- A12 [P3] `test_ladybug_store.py::test_shortest_path` 文档与实现不一致（RR-1 / RR-2 文档同步）
- B2 [P0] `LadybugStore.upsert_nodes` 在 tombstone 路径上清空 Document 全部非 PK 属性
- B9 [P1] `shortest_path` 因 LadybugDB 限制仅返回 length，前端契约 `/api/graph/path` 无法做节点级高亮
- B19 [P2] `LadybugStore.upsert_nodes` 中 `props = {k: row.get(k, "") for k in node.props}`——空字符串混淆"未传"与"显式空"
  - 候选: A1 ↔ B2（重叠系数 1.00）
  - 候选: A1 ↔ B19（重叠系数 0.50）
  - 候选: A2 ↔ B2（重叠系数 1.00）
  - 候选: A2 ↔ B9（重叠系数 0.50）
  - 候选: A2 ↔ B19（重叠系数 0.50）
  - 候选: A5 ↔ B2（重叠系数 0.67）
  - 候选: A5 ↔ B19（重叠系数 0.50）
  - 候选: A12 ↔ B2（重叠系数 0.33）
  - 候选: A12 ↔ B9（重叠系数 0.75）
  - 候选: A12 ↔ B19（重叠系数 1.00）

## graph/queries.py（A×1，B×2）
- A2 [P0] 11 处读路径全部缺失 `valid_to` 过滤，墓碑文档的 Section / Entity / Topic / 邻域 / 路径仍出现在所有图查询（RR-4 #2 读路径过滤）
- B3 [P0] `topic_subgraph` 与 `_aggregate_entities` 多处用 `repr(d) + IN [csv]` 字符串拼接构造 Cypher
- B4 [P0] 软删墓碑在所有读路径均不过滤（应用层无过滤；测试代码手写 WHERE 掩盖）
  - 候选: A2 ↔ B3（重叠系数 0.50）
  - 候选: A2 ↔ B4（重叠系数 1.00）

## kbapp/mcp_server.py（A×1，B×1）
- A2 [P0] 11 处读路径全部缺失 `valid_to` 过滤，墓碑文档的 Section / Entity / Topic / 邻域 / 路径仍出现在所有图查询（RR-4 #2 读路径过滤）
- B24 [P3] `mcp_server.py` `_kb_search` `mode == "vector" or mode not in _SEARCH_MODES` 顺序未截断 None
  - 候选: A2 ↔ B24（重叠系数 0.50）

## pipeline/graph_stages.py（A×2，B×2）
- A1 [P0] `stage_tombstone_graph` 通过 `upsert_nodes` 全行 SET 把 Document 14 个字段（含 13 个非 PK 属性）覆盖为空串（RR-4 #1 属性保留）
- A2 [P0] 11 处读路径全部缺失 `valid_to` 过滤，墓碑文档的 Section / Entity / Topic / 邻域 / 路径仍出现在所有图查询（RR-4 #2 读路径过滤）
- B2 [P0] `LadybugStore.upsert_nodes` 在 tombstone 路径上清空 Document 全部非 PK 属性
- B22 [P2] `stage_tombstone_graph` 异常路径只 catch GraphError，其他异常（SQLite/IO）会被 runner 误判为 Generic Terminal
  - 候选: A1 ↔ B2（重叠系数 1.00）
  - 候选: A1 ↔ B22（重叠系数 0.50）
  - 候选: A2 ↔ B2（重叠系数 1.00）
  - 候选: A2 ↔ B22（重叠系数 0.50）

## retrieve/graph_search.py（A×3，B×3）
- A2 [P0] 11 处读路径全部缺失 `valid_to` 过滤，墓碑文档的 Section / Entity / Topic / 邻域 / 路径仍出现在所有图查询（RR-4 #2 读路径过滤）
- A10 [P2] M5 MCP 三只读图工具（`kb_related` / `kb_compare` / `kb_topics`）成功响应结构无同形断言，DoD-2 契约测试只覆盖错误结构（RR-1 弱断言）
- A13 [P3] `web/api.py:_aggregate_entities` / `_doc_mentions` / `_doc_related_docs` 把 `doc_ids` 用 `repr` 拼入 Cypher `IN [{docs_csv}]`，弱注入面（RR-7c 消毒）
- B14 [P1] `graph_related` 不输出关系 kind（design §5.1 要求"输出实体/文档清单及路径上的关系 kind"）
- B17 [P2] graph_compare doc_ids 参数被忽略（设计与实现偏离）
- B25 [P3] `graph_compare` 排序按 weight desc 但无 secondary tie-break
  - 候选: A2 ↔ B14（重叠系数 0.50）
  - 候选: A2 ↔ B17（重叠系数 0.50）
  - 候选: A2 ↔ B25（重叠系数 0.50）
  - 候选: A10 ↔ B14（重叠系数 1.00）
  - 候选: A10 ↔ B17（重叠系数 1.00）
  - 候选: A10 ↔ B25（重叠系数 0.50）
  - 候选: A13 ↔ B14（重叠系数 0.50）
  - 候选: A13 ↔ B17（重叠系数 0.50）
  - 候选: A13 ↔ B25（重叠系数 0.50）

## static/app.js（A×1，B×1）
- A6 [P1] `graph.html` 漏引 `app.js`，`graph.js` 顶层调用 `app.js` 声明的 `fetchJson` 全局函数 → 加载时 `ReferenceError: fetchJson is not defined`（RR-8 反向依赖）
- B1 [P0] graph.html 缺 `app.js` 引入，graph.js 调用未定义函数 `fetchJson` 即报 ReferenceError
  - 候选: A6 ↔ B1（重叠系数 1.00）

## static/graph.html（A×1，B×1）
- A6 [P1] `graph.html` 漏引 `app.js`，`graph.js` 顶层调用 `app.js` 声明的 `fetchJson` 全局函数 → 加载时 `ReferenceError: fetchJson is not defined`（RR-8 反向依赖）
- B1 [P0] graph.html 缺 `app.js` 引入，graph.js 调用未定义函数 `fetchJson` 即报 ReferenceError
  - 候选: A6 ↔ B1（重叠系数 1.00）

## static/graph.js（A×3，B×4）
- A6 [P1] `graph.html` 漏引 `app.js`，`graph.js` 顶层调用 `app.js` 声明的 `fetchJson` 全局函数 → 加载时 `ReferenceError: fetchJson is not defined`（RR-8 反向依赖）
- A7 [P1] `new G6.Graph({…})` 缺 `layout` 配置（RR-8 v3 必需项，G6 v5 文档要求）
- A8 [P1] `graph.js` 缺 `brush-canvas` 行为，commit 289d973 声称 "brush" 但实现未落地（RR-8 行为声明偏离）
- B1 [P0] graph.html 缺 `app.js` 引入，graph.js 调用未定义函数 `fetchJson` 即报 ReferenceError
- B6 [P1] graph.js `new G6.Graph` 缺 `layout` 配置（RR-8 必需项），节点默认 force 抖动致路径高亮无法稳定
- B7 [P1] graph.js 路径高亮未在图上实现——API 返回后仅显示 banner 文字
- B8 [P1] graph.js 缺 `brush-select` 行为（DoD D2 要求"框选=Shift+拖拽"）
  - 候选: A6 ↔ B1（重叠系数 1.00）
  - 候选: A6 ↔ B6（重叠系数 1.00）
  - 候选: A6 ↔ B7（重叠系数 1.00）
  - 候选: A6 ↔ B8（重叠系数 1.00）
  - 候选: A7 ↔ B1（重叠系数 0.67）
  - 候选: A7 ↔ B6（重叠系数 1.00）
  - 候选: A7 ↔ B7（重叠系数 1.00）
  - 候选: A7 ↔ B8（重叠系数 1.00）
  - 候选: A8 ↔ B1（重叠系数 0.50）
  - 候选: A8 ↔ B6（重叠系数 1.00）
  - 候选: A8 ↔ B7（重叠系数 1.00）
  - 候选: A8 ↔ B8（重叠系数 1.00）

## unit/test_extract.py（A×2，B×1）
- A5 [P1] `RELATES_TO` 边 MERGE 模式缺 `kind` 区分键，同 (src, dst) 不同 kind 关系互相覆盖（RR-4 #3 合并键完整 + RR-5 幂等性）
- A11 [P2] `test_tombstone_soft_deletes_document` 与 `test_run_extract_idempotent_replay` 测试覆盖盲点，掩盖 P0-1 / P0 复活 / P1 RELATES_TO 三个生产 bug（RR-1 / RR-3）
- B16 [P2] test_extract.py 幂等测试只验实体去重，不验 description/aliases 重写
  - 候选: A5 ↔ B16（重叠系数 1.00）
  - 候选: A11 ↔ B16（重叠系数 0.50）

## web/api.py（A×5，B×6）
- A2 [P0] 11 处读路径全部缺失 `valid_to` 过滤，墓碑文档的 Section / Entity / Topic / 邻域 / 路径仍出现在所有图查询（RR-4 #2 读路径过滤）
- A4 [P0] `kb serve viz` 启动入口可选依赖兜底不完备：`code/kb-app/src/kbapp/web/__init__.py` 在评审锚点 f62f287 中不存在，`cli/serve.py:viz_cmd` 内 `from kbapp.web import create_app` 无 try/except，启动直接 ImportError（RR-7a serve 入口兜底完备性）
- A9 [P2] `web/api.py:search` 等 7 个端点 `limit` 参数无上限校验（RR-7c 上界缺失）
- A12 [P3] `test_ladybug_store.py::test_shortest_path` 文档与实现不一致（RR-1 / RR-2 文档同步）
- A13 [P3] `web/api.py:_aggregate_entities` / `_doc_mentions` / `_doc_related_docs` 把 `doc_ids` 用 `repr` 拼入 Cypher `IN [{docs_csv}]`，弱注入面（RR-7c 消毒）
- B3 [P0] `topic_subgraph` 与 `_aggregate_entities` 多处用 `repr(d) + IN [csv]` 字符串拼接构造 Cypher
- B4 [P0] 软删墓碑在所有读路径均不过滤（应用层无过滤；测试代码手写 WHERE 掩盖）
- B9 [P1] `shortest_path` 因 LadybugDB 限制仅返回 length，前端契约 `/api/graph/path` 无法做节点级高亮
- B12 [P1] `/api/graph/path` 的 src/dst 无格式校验，且类型未校验（与 MCP kb_related 不一致）
- B21 [P2] `web/api.py` 多处 `make_graph_store + open + try/finally close` 重复模板
- B26 [P3] `_aggregate_entities` 中 `cur["count"] += int(r["w"])` 累加多 Section 同 entity 出现次数
  - 候选: A2 ↔ B3（重叠系数 0.50）
  - 候选: A2 ↔ B4（重叠系数 1.00）
  - 候选: A2 ↔ B9（重叠系数 0.50）
  - 候选: A2 ↔ B12（重叠系数 0.33）
  - 候选: A2 ↔ B21（重叠系数 0.50）
  - 候选: A2 ↔ B26（重叠系数 0.50）
  - 候选: A4 ↔ B4（重叠系数 0.33）
  - 候选: A4 ↔ B12（重叠系数 0.33）
  - 候选: A4 ↔ B21（重叠系数 0.50）
  - 候选: A4 ↔ B26（重叠系数 0.50）
  - 候选: A9 ↔ B3（重叠系数 1.00）
  - 候选: A9 ↔ B4（重叠系数 0.50）
  - 候选: A9 ↔ B9（重叠系数 0.50）
  - 候选: A9 ↔ B12（重叠系数 1.00）
  - 候选: A9 ↔ B21（重叠系数 0.50）
  - 候选: A9 ↔ B26（重叠系数 0.50）
  - 候选: A12 ↔ B3（重叠系数 0.50）
  - 候选: A12 ↔ B4（重叠系数 0.33）
  - 候选: A12 ↔ B9（重叠系数 0.75）
  - 候选: A12 ↔ B12（重叠系数 0.67）
  - 候选: A12 ↔ B21（重叠系数 0.50）
  - 候选: A12 ↔ B26（重叠系数 1.00）
  - 候选: A13 ↔ B3（重叠系数 0.50）
  - 候选: A13 ↔ B4（重叠系数 0.33）
  - 候选: A13 ↔ B12（重叠系数 0.67）
  - 候选: A13 ↔ B21（重叠系数 0.50）
  - 候选: A13 ↔ B26（重叠系数 0.50）

## 仅 A 侧出现的文件组（40）：05-详细设计.md、__init__.py、api.py、app.js、cli/index.py、core/registry.py、docs/milestone-log.md、document.html、extract.py、graph.html、graph.js、graph/schema.py、graph/sync.py、graph_search.py、index.html、integration/test_m5m6_e2e.py、integration/test_mcp.py、kb-app/03-技术概要设计.md、kb-app/15-m5m6合并补充设计.md、ladybug_store.py、mcp_server.py、pyproject.toml、r.js、schema.py、server.py、static/...js、static/common.js、status.html、test_graph_contract.py、test_graph_search.py、test_graph_sync.py、test_mcp.py、test_web_server.py、unit/test_graph_contract.py、unit/test_graph_sync.py、unit/test_ladybug_store.py、vendor/g6.min.js、vendor/smoke.html、web/__init__.py、web/server.py
## 仅 B 侧出现的文件组（3）：cli/search.py、kb-app/pyproject.toml、unit/test_web_server.py
