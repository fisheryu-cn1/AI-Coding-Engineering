# 复核应答卡：f62f287 状态（针对意见卡 reviews/2026-08-19-f62f287-run9-skill.md）

- 日期：2026-08-19 / 应答者：实现方（A 角色）
- 评审锚点：f62f2878e7d2ebed21c5c9fa1136e0697cd83793
- 锚点核对方式：`git show f62f287:<path>` 逐文件核对；未读取 3ffebf0 及其后任何提交
- 范围：run9 意见卡 14 条意见（P0×2 / P1×7 / P2×3 / P3×2）+ "未发现问题的检查项"对照

---

## 意见（按级别逐条应答）

### [P0] web/__init__.py — Python 包入口缺失，`kb serve viz` 启动即 ImportError

- 应答：□ 接受
- 依据：`git show f62f287:code/kb-app/src/kbapp/web/ --name-only` 仅返 `api.py / server.py / static/`，无 `__init__.py`；`cli/serve.py:46` `from kbapp.web import create_app` 走子包导入路径，Python 找不到 `__init__.py` 时不识别为 package，必抛 `ModuleNotFoundError`；与 15 §6.1 "kb serve viz 启动 FastAPI 只读服务" 交付项 C2 矛盾。
- 修复承诺：补 `code/kb-app/src/kbapp/web/__init__.py` 仅 `from kbapp.web.server import create_app` 并在 `__all__ = ["create_app"]`；同时在 `tests/unit/test_web_server.py` 加 `test_serve_viz_imports_web`（`import kbapp.web` 不抛 ImportError）。

### [P0] graph/sync.py::sync_document_structure — Document.valid_to 无条件写空串，墓碑被 reindex 复活

- 应答：□ 接受
- 依据：`graph/sync.py:67-75` 构造 `document_node` 时 `"valid_to": ""` 硬编码；`graph/sync.py:33-46` `row is None` 早退后**无 status 过滤**直接走 `upsert_nodes`；`cli/index.py:627-630` `reindex --full` 跳过 `status in ("deleted","duplicate")` 入队 parse，触发 `runner.parse→chunk→classify→enqueue(index)`（`pipeline/runner.py:217-237`），index 任务调 `sync_document_structure`（`pipeline/graph_stages.py:42-58`）把墓碑 `valid_to` 清空。`tests/unit/test_graph_sync.py:153-181` 仅测单次 tombstone→valid_to 非空+边保留，未测"tombstone 后再 sync"复活路径。设计 15 §4.1 / RR-4 #4 不可复活未达成。
- 修复承诺：改 `graph/sync.py:sync_document_structure` 入口在 `get_file` 后前置 `MATCH (d:Document) WHERE d.doc_id=$i RETURN d.valid_to AS v`（写路径走 `store.query` 读旧值），若 v 非空则**仅**同步 Section/Topic/ABOUT_TOPIC，不动 Document 节点；或前置 `if row.status == "deleted": return {"sections":0,"topic":0,"skipped":1}` 早退；补 `tests/unit/test_graph_sync.py:test_tombstone_survives_reindex` 断言。涉及文件：`code/kb-app/src/kbapp/graph/sync.py`、`code/kb-app/tests/unit/test_graph_sync.py`。

### [P1] retrieve/graph_search.py::graph_compare — doc_ids 形参定义但 Cypher/params 完全未引用

- 应答：□ 接受
- 依据：`graph_search.py:55-78` 函数签名收 `doc_ids: list[str] | None = None`，但 `params: dict = {"concept": ..., "limit": ...}`（line 65）不含 `doc_ids`；Cypher `MATCH (a:Entity {entity_id: $concept})-[r:RELATES_TO]-(b:Entity) RETURN ...` 全部不消费。代码内自注 `graph_search.py:67-69` "lbug 暂不支持 EXISTS 子查询 + 多 MATCH 联合；先按 concept 宽查，前端按 doc_ids 过滤显示（Task 19 词云/侧栏回填时拉具体 doc_id 范围）" 是延迟技术债描述，与"doc_ids 入形参"是契约声明-实现走样。设计 15 §5.1/05 §6 明确 kb_compare 契约收 `doc_ids`。
- 修复承诺：两路径二选一——(a) Cypher 扩 `MATCH (a)-[:MENTIONS]-(s:Section)<-[:CONTAINS_SECTION]-(d:Document) WHERE d.doc_id IN $doc_ids` 过滤（在 `LadybugStore` 增 `query_in` 帮助类把 list 拆成多个 MATCH 链）；或 (b) Python 层 fetch 宽结果后按 `doc_ids` 集合二次过滤；补 `tests/unit/test_graph_search.py:test_graph_compare_filters_by_doc_ids` 断言（传 `doc_ids=[d1]` 与 `None` 结果不同）。涉及文件：`code/kb-app/src/kbapp/retrieve/graph_search.py`、`code/kb-app/src/kbapp/graph/ladybug_store.py`、`code/kb-app/tests/unit/test_graph_search.py`。

### [P1] graph/ladybug_store.py::LadybugStore.shortest_path — 仅返 length 不返 path 节点/边，违反 §6.2 "路径高亮"契约

- 应答：□ 部分接受
- 依据：`ladybug_store.py:140-167` 实现 `RETURN length(p) AS length ORDER BY length(p) ASC LIMIT 1`，返回 `[{"length": int(...)}]`，注释 `ladybug_store.py:147-149` 自承认"LadybugDB 不支持 Cypher shortest() 与 list comprehension；用变长路径 + ORDER BY length LIMIT 1 折中，仅返回 length 计数。UI 需要 highlights 时再走 store.query 单独 fetch 路径节点"——承认契约兑现延迟。设计 15 §6.2 "GET /api/graph/path?src=&dst= 路径高亮（max_hops=3）" + 15 §6.3 "图谱页 G6 v5 vendored…路径高亮" + DoD D2 路径高亮三项声明；web 前端 `graph.js:107` `banner.textContent = `路径：${p.length} 跳`` 仅消费 length，**未**触发图上节点高亮。`tests/unit/test_graph_contract.py:127-141` 与实现同步缩水同源。**保留部分**：LadybugDB 当前不支持 `nodes(p)` / `relationships(p)` 提取（事实约束，run9 评审也未在文中提供反证能力是否已具备）；**接受部分**：契约侧未声明"先 length → 再二次 fetch"是 approved 偏离，且 web 图谱前端 P1-3 路径高亮未落实是综合断链。
- 修复承诺：路径 (a) LadybugStore 增 `fetch_path_nodes(src, dst, length)`（基于已知 length 走 `MATCH p = (a)-[*L]-(b) RETURN nodes(p), relationships(p)`），在 `entity_path` 后置调用，前端 `graph.js` 改 `setElementState` 高亮节点；路径 (b) 回写 15 §6.2 / §6.3 把"路径高亮"降级为"路径长度显示"并回填 milestone-log 登记偏离。倾向 (a)。涉及文件：`code/kb-app/src/kbapp/graph/ladybug_store.py`、`code/kb-app/src/kbapp/graph/queries.py`（`entity_path`）、`code/kb-app/src/kbapp/web/api.py:graph_path`、`code/kb-app/src/kbapp/web/static/graph.js`、`code/kb-app/tests/unit/test_graph_contract.py`。

### [P1] graph/queries.py::topic_subgraph — 用 Python `repr()` 拼接 Cypher IN 列表，违反 store/ladybug_store 头注"Parameter binding is mandatory"

- 应答：□ 接受
- 依据：`graph/queries.py:38` `docs_csv = ",".join(repr(d) for d in docs)`、`:46` `secs_csv = ",".join(repr(s) for s in section_ids)`、`:54` `ents_csv = ",".join(repr(e) for e in entity_ids)`、`:81` `ids_csv = ",".join(repr(n) for n in new_seen)`，四处均 `f"...IN [{csv}]..."` 拼 Cypher，第二参数实参 `{}` 空字典不参与绑定；`ladybug_store.py:14-19` 头注 "Parameter binding is mandatory — callers never concatenate strings"、设计 15 §3.1 "调用方不得拼接字符串构造查询，一律参数绑定"直接冲突。检查项 RR-7c 用户输入消毒（doc_id 虽受控 `D%04d` 注入风险低，但契约违规是事实）。
- 修复承诺：`LadybugStore` 加 `_query_in(cypher_template, params, in_clause_field, values)` helper（lbug 当前不支持 `IN $param` 的标准 Cypher 语义，需在 store 层把 list 拆为多段 `MATCH` 链或 `UNWIND` 表达），`topic_subgraph` 五处 Cypher 全部改走参数绑定；补 `tests/unit/test_graph_queries.py::test_topic_subgraph_no_string_concat` 断言（mock `store.query` 检参数绑定）。涉及文件：`code/kb-app/src/kbapp/graph/queries.py`、`code/kb-app/src/kbapp/graph/ladybug_store.py`、`code/kb-app/tests/unit/test_graph_queries.py`。

### [P1] web/api.py::_aggregate_entities — 同样用 repr() 拼接 Cypher IN 列表，且 doc_ids 无上界

- 应答：□ 接受
- 依据：`web/api.py:55` `docs_csv = ",".join(repr(d) for d in doc_ids)`；`web/api.py:60-67` `f"MATCH (s:Section)-[m:MENTIONS]->(e:Entity) WHERE s.doc_id IN [{docs_csv}] RETURN ..."` 而 `store.query` 第二参数空字典；`doc_ids` 来自 `/api/search` 端点的 `_state(request)[2]` + `result.hits`（`web/api.py:46`），与上游 `/api/search?limit=` 同源——`run9 RR-7c` 标"无硬上限"；`store.query` 路径上 `repr()` 对 `D%04d` 受控 doc_id 注入风险低，但契约违规 + 上界缺失双重缺陷。
- 修复承诺：复用 P1-3 修复中 `_query_in` helper，`_aggregate_entities` 改参数绑定；`/api/search` 端点 limit 硬上界 `min(int(limit), int(cfg.raw["viz"]["max_docs"]))`（新增配置 `viz.max_docs` 默认 50），`_aggregate_entities` 入口 `if len(doc_ids) > max_docs: doc_ids = doc_ids[:max_docs]` 二次截断；补 `tests/unit/test_web_server.py::test_search_aggregates_entities_with_param_binding` 断言。涉及文件：`code/kb-app/src/kbapp/web/api.py`、`code/kb-app/src/kbapp/graph/ladybug_store.py`、`code/kb-app/src/kbapp/core/config.py`（新增 `viz.max_docs`）、`code/kb-app/tests/unit/test_web_server.py`。

### [P1] graph/extract.py::run_extract — Entity.aliases 列表被 ",".join() 扁平化为字符串，存储与语义不一致

- 应答：□ 接受
- 依据：`graph/schema.py:74-80` `Entity.props` 声明 `aliases: _S`（STRING）；`graph/extract.py:170-172` `entity_nodes[eid] = {... "aliases": ",".join(str(a) for a in (e.get("aliases") or []) if a) ...}` 把 LLM 输出的 list 扁平化为以逗号分隔的字符串；任何 alias 含 `,` 即被切碎（无 escape）。设计 15 §4.2 "LLM 输出的 `aliases` 落 Entity 字段仅作记录，MVP 不用于消歧"——明确"仅记录"但未限定序列化为 string 与读端空缺。RR-7a LLM 输出未做 schema 校验。
- 修复承诺：写入侧 `json.dumps(..., ensure_ascii=False)` 替换 `",".join(...)`；`schema.py` 注释 "String-encoded JSON list"；读端 `kbapp.web.api._aggregate_entities` / `graph.queries` 取 `Entity.aliases` 时 `json.loads`（容错 default `[]`）；补 `tests/unit/test_extract.py::test_extract_aliases_round_trip` 断言（输入 `["a,b","c"]` 读出同样两个元素）。涉及文件：`code/kb-app/src/kbapp/graph/extract.py`、`code/kb-app/src/kbapp/graph/schema.py`、`code/kb-app/src/kbapp/web/api.py`、`code/kb-app/tests/unit/test_extract.py`。

### [P1] pipeline/stages.py::stage_summarize — Document.summary_l1/l2 字段从未填充，schema 漂移

- 应答：□ 接受
- 依据：`grep -n "summary_l1\|summary_l2" f62f287:code/kb-app/src/kbapp/` 全树核对：仅 `schema.py:53-54` 声明 + `graph/sync.py:63-64` 写空串，**无**任何真实填充路径；`pipeline/stages.py:487-563` `stage_summarize` 写 `auto_summaries/<doc_id>.md` + `$summary` 伪 chunk + `files.summary_source/path`，不写 Document 图节点。`schema.py:53-54` 字段存在 = 列级契约存在 = 读端会按 STRING 拉空串，存与读端语义一致但实际空跑，schema 漂移。
- 修复承诺：路径 (a) `stage_summarize` 完成后 `store.upsert_nodes("Document", [{"doc_id": doc_id, "summary_l1": l1, "summary_l2": l2}])`（需 store 层补"部分字段 patch"语义，避免 P0-2 同型覆写风险）；路径 (b) 回写 15 §3.2 删除 `summary_l1/l2` 列并同步 `remove_node_property` from `schema.py`。倾向 (a)——文档页 P-D 关联侧栏可消费真实摘要。涉及文件：`code/kb-app/src/kbapp/pipeline/stages.py`、`code/kb-app/src/kbapp/graph/sync.py`（补"patch 字段"分支）、`code/kb-app/src/kbapp/graph/schema.py`（注释"由 stage_summarize 填充"）、`code/kb-app/tests/unit/test_pipeline_stages.py`（新增 test）。

### [P1] graph/extract.py::_entity_type_by_name — 同名不同 type 时仅返首个，潜在错配

- 应答：□ 接受
- 依据：`graph/extract.py:223-230` 遍历 `entity_nodes.values()` 找 `e["name"] == name` 返首条 `type`；`extract.py:206-217` `relations` 解析时 `src_type = _entity_type_by_name(entity_nodes, src_name)` 找 type 后生成 `entity_id = f"{type}:{norm(name)}"`。同名不同 type（如 "RAG" 既被识别为 Method 又被识别为 Concept）时 relations 中 src="RAG" 只能映射到首个匹配，另一类边被静默丢弃。设计 15 D15-13/D15-2 暗示不同 type 应为不同 entity。
- 修复承诺：`_entity_type_by_name` 改 `name→types: list[str]` 多值映射；`relations` 解析时对 `src_name` 穷举所有 type 的 entity pair → 每条 physical edge 落到 `(src_type, dst_type, kind)` 唯一 key；或要求 LLM 输出 entity_id 而非 name（prompt 改 `relations[].src`/`dst` 字段契约）。涉及文件：`code/kb-app/src/kbapp/graph/extract.py`、`code/kb-app/src/kbapp/graph/extract.py:_extract_prompt`（若改 prompt）、`code/kb-app/tests/unit/test_extract.py`（新增"同名不同 type"用例）。

### [P2] mcp_server.py::_kb_compare / _kb_related — 目标 entity 不存在时静默返空，无 NOT_FOUND 错误码

- 应答：□ 接受
- 依据：`mcp_server.py:_kb_related:178-207` 调 `graph_related` 直接 `return graph_related(...)`，`mcp_server.py:_kb_compare:209-229` 同型；`graph_related` 与 `graph_compare` 对 `target` 不存在时静默返 `{"related": []}` / `{"rows": []}`（`graph_search.py:62-80`）。设计 13 §2.2 错误码子集 `{DOC_NOT_FOUND, SECTION_NOT_FOUND, MODE_NOT_READY, CONFIG_INVALID, INTERNAL}`（`13-M4补充设计.md:60`），无 entity/topic NOT_FOUND 条目；`tests/integration/test_mcp.py:114-135` 测 `MODE_NOT_READY` 但无 NOT_FOUND 用例。
- 修复承诺：MCP 工具前置 `MATCH (n:Type {pk: $target}) RETURN n` 探测；缺失时 `_error("TARGET_NOT_FOUND", f"找不到 {type}={target!r}", "call kb_search 找到对应 target")`；回写 13 §2.2 表加 `TARGET_NOT_FOUND`；补 `tests/integration/test_mcp.py::test_mcp_target_not_found` 两条。涉及文件：`code/kb-app/src/kbapp/mcp_server.py`、`code/kb-app/src/kbapp/retrieve/graph_search.py`（签名加 `return_exists` 或拆函数）、`design/kb-app/13-M4补充设计.md`、`code/kb-app/tests/integration/test_mcp.py`。

### [P2] web/api.py::* — 五个读端点每次请求都 open/close 图库 store，无连接复用

- 应答：□ 接受
- 依据：`web/api.py:56-73`（`_aggregate_entities`）、`:110-131`（`_doc_mentions`）、`:133-156`（`_doc_related_docs`）、`:206-228`（`graph_subgraph`）、`:230-253`（`graph_path`）五处均 `make_graph_store → open(ro) → try/finally close`；`web/server.py:create_app` 无 `lifespan` handler，未在 `app.state` 缓存 `GraphStore` 单例。LadybugDB `open()` 含 `ladybug.Database(path, read_only=True)` 初始化（约 1–10ms 级别），每次请求新建连接是显著浪费；设计 15 §6.1 仅约束"绑定 127.0.0.1" 未约束资源生命周期。
- 修复承诺：`web/server.py:create_app` 改用 `asynccontextmanager` `lifespan` 启动时 `app.state.graph_store = make_graph_store(...)` + `open(ro)` 单例，关闭时 `close()`；5 个端点改 `request.app.state.graph_store` 复用；LadybugStore 需补 `is_open()` 守卫；补 `tests/unit/test_web_server.py::test_state_graph_store_singleton` 断言同一请求多次访问 `app.state.graph_store` 是同一对象。涉及文件：`code/kb-app/src/kbapp/web/server.py`、`code/kb-app/src/kbapp/web/api.py`、`code/kb-app/src/kbapp/graph/ladybug_store.py`、`code/kb-app/tests/unit/test_web_server.py`。

### [P2] graph/extract.py::is_core_doc — doc_type=None 静默被踢出抽取，无 metric/log

- 应答：□ 接受
- 依据：`graph/extract.py:46-58` `is_core_doc` → `_doc_type_allowed` 返回 `doc_type is not None and doc_type in allowed`——`doc_type=None` 直接 `False`；`pipeline/graph_stages.py:78-99` `stage_extract_graph` 命中 `is_core=False` 时 `return StageResult("skip", detail=...)` 但 `metrics` 字段空（`StageResult` 默认 `field(default_factory=dict)`），运维无法统计"被规则剔除"的样本。`tests/unit/test_extract.py:39-49` 测试覆盖了 `doc_type in allowed / not allowed` 路径，未覆盖 `doc_type=None`。
- 修复承诺：`_doc_type_allowed` 增加分支 `doc_type is None → False` 并 `extract_module._logger.info("doc_type None 跳过: doc_id=%s", doc_id)`；`stage_extract_graph` 把 `skipped_no_doc_type` / `skipped_doc_type_not_allowed` 计入 `metrics`（包含 `doc_id` 列表或计数）；补 `tests/unit/test_extract.py::test_is_core_doc_skipped_no_doc_type_metrics` 断言。涉及文件：`code/kb-app/src/kbapp/graph/extract.py`、`code/kb-app/src/kbapp/pipeline/graph_stages.py`、`code/kb-app/tests/unit/test_extract.py`。

### [P3] tests/unit/test_graph_queries.py::test_topic_subgraph_truncates — 条件断言，truncated 未触发时被默默跳过

- 应答：□ 接受
- 依据：`tests/unit/test_graph_queries.py:115-118` 完整段为 `if len(result["nodes"]) >= 500: assert result["truncated"] is True; assert len(result["nodes"]) <= 500`——若 hops=2 实际遍历未达 500 节点（LadybugDB 变长路径遍历受 Cypher 复杂度限制，`_seed_full_graph` 造 1 文档 + 2 section + 1 entity + 600 dummy entity + 600 边，单主题拉 2 跳子图实际可能只命中部分），整个 if 块被跳过、断言不触发。RR-3 登记真实性失守。
- 修复承诺：先断言 `assert len(result["nodes"]) >= 600` 强制触发 truncation（条件前置必触发），再断言 `result["truncated"] is True` + `len(result["nodes"]) <= 500`；考虑补充更直接路径如制造 `2 文档 × 600 实体 × 全连` 必达 500 节点。涉及文件：`code/kb-app/tests/unit/test_graph_queries.py`。

### [P3] web/static/graph.html — 不引用 app.js（设计选择但缺注释）

- 应答：□ 接受
- 依据：`graph.html:7` `<script src="/static/vendor/g6.min.js" defer></script>` + `graph.html:29` `<script src="/static/graph.js" defer></script>`；`index.html:13` / `document.html:13` / `status.html:12` 全部 `<script src="/static/app.js" defer></script>` 范式；`app.js:5-7` `data-page` 分派仅处理 `search/document/status` 三页。`graph.js` 走 IIFE 自管理（`fetchJson` 定义于 `app.js`，但 graph.js 内部以 `function fetchJson() {...}` 自定义同名函数，已自洽）—— run8 P0-1 提的 `fetchJson` ReferenceError 在 run9 评审口径下不再断言；但 graph.html 完全不走 `data-page` 分派范式，缺注释说明意图。
- 修复承诺：`graph.html:7` 后加注释 `<!-- 不走 app.js 分派：graph.js 直接绑定 G6，依赖 g6.min.js 单 vendored 脚本 -->`；或补一行 `<!-- fetchJson: graph.js 内部定义（与 app.js 同名同语义，避免引入 app.js 触发其他 init* 副作用） -->`。涉及文件：`code/kb-app/src/kbapp/web/static/graph.html`。

---

## 未发现问题的检查项 — 与已知缺陷矛盾项（按 review-respond.md §3 单独列出）

意见卡"未发现问题的检查项"中以下条目与应答者已知事实矛盾；标记入待确认问题流程（`A-B评审闭环工作流.md` §4 + `evals/待确认问题卡-模板.md`）：

### 矛盾项 1 — RR-4 #2 读路径过滤 6 处失守被标"→ 与 P0-2 同源问题面"
- 意见卡原文：RR-4 段落
  > **`mcp_server.py:_kb_related:179` graph_related Cypher 无 `valid_to` 过滤（**缺**）→ 与 P0-2 同源问题面**
  > **`mcp_server.py:_kb_compare:198` graph_compare 无 valid_to 过滤（**缺**）→ 同上**
  > **`web/api.py:search` `_aggregate_entities:60-67` 无 valid_to 过滤（**缺**）→ 同上**
  > **`web/api.py:_doc_mentions:107-114` 无 valid_to 过滤（**缺**）→ 同上**
  > **`web/api.py:_doc_related_docs:130-138` 无 valid_to 过滤（**缺**）→ 同上**
  > **`web/api.py:graph_subgraph` `topic_subgraph` 无 valid_to 过滤（**缺**）→ 同上**
  > **`web/api.py:graph_path` `entity_path` 无 valid_to 过滤（**缺**）→ 同上**
- 矛盾论证：P0-2 是**写路径** tombstone 文档被 `sync_document_structure` 复活（`graph/sync.py:67-75`）；RR-4 #2 是**读路径** 6 处 Cypher 不带 `WHERE d.valid_to = ''` 过滤（`web/api.py:60-67` / `:107-114` / `:130-138` / 透传 `topic_subgraph` / `entity_path` / `mcp_server.py:179` / `:198`），二者**非同源**——即使 P0-2 修复使墓碑的 `valid_to` 不被覆盖，读路径仍会原样返回软删文档及其 Section/Entity。意见卡把这些条目归入"未发现问题的检查项"清单（"缺"），未作为独立 P0/P1 立项。
- 独立性问题面（建议作为 P0 单独立项）：
  1. `mcp_server.py:_kb_related:179` graph_related 无 valid_to 过滤
  2. `mcp_server.py:_kb_compare:198` graph_compare 无 valid_to 过滤
  3. `web/api.py:_aggregate_entities:60-67` 无 valid_to 过滤
  4. `web/api.py:_doc_mentions:107-114` 无 valid_to 过滤
  5. `web/api.py:_doc_related_docs:130-138` 无 valid_to 过滤
  6. `web/api.py:graph_subgraph` 透传 `topic_subgraph` 无 valid_to 过滤
  7. `web/api.py:graph_path` 透传 `entity_path` 无 valid_to 过滤
- 设计口径核对：`design/kb-app/15-M5M6合并补充设计.md:137` 明确"tombstone | 既有文件清理之上，追加图侧 Document 置 `valid_to` 软删（**不物理删边，查询层过滤**）"；`design/kb-app/03-技术概要设计.md:100` / `05-详细设计.md:261` 同口径——读路径过滤是显式设计要求，与 P0-2 写路径修复并列。
- 处置建议：待确认问题卡（归类 ①"前一次缺陷标注识别错了"——评审本应在 P0/P1 立项读路径过滤而非合并到 P0-2 旁注）。

### 矛盾项 2 — RR-4 #3 合并键完整 — RELATES_TO upsert_edges 主键缺 kind 维度
- 意见卡原文：RR-4 段
  > RELATES_TO upsert_edges 主键为 src+dst 但 MERGE 复合键 `(a)-[r:RELATES_TO]->(b)` 无 kind 维度（**缺**）→ 同 kind 不同 src/dst 多边共存：每条边 SET 覆盖前一条，**冲突**
- 矛盾论证：意见卡已自承认"缺"且"每条边 SET 覆盖前一条，冲突"——典型实现偏离（`graph/ladybug_store.py:121-141` `upsert_edges` 用 `MATCH (a)-[:RELATES_TO]->(b)` 复合主键不含 `kind`），但未作为独立 P1/P2 立项；以"未发现问题的检查项"清单呈现。
- 独立性问题面：同 src/dst 不同 kind 边冲突——仅靠 `extract.py:223-230` 端 Python 层 `(src_eid, dst_eid, kind)` dedup（应用层），迁移到 graph 后被 SET 覆盖；类型"实现偏离"。
- 处置建议：待确认问题卡（归类 ①"前一次缺陷标注识别错了"——评审应独立列 P1）。

### 矛盾项 3 — RR-5 幂等与重放 — RELATES_TO upsert_edges 主键缺 kind
- 意见卡原文：RR-5 段
  > RELATES_TO upsert_edges 主键缺 kind 维度，同 src/dst 不同 kind 边冲突（extract.py 端按 `(src_eid, dst_eid, kind)` 去重，但 graph 端 MERGE 仅靠端点）
- 矛盾论证：与矛盾项 2 同根问题，意见卡用"发现"标记，但未独立列项。
- 处置建议：与矛盾项 2 合并为单一致命点。

### 矛盾项 4 — RR-7c 用户输入 — `/api/search?limit=` 无硬上限
- 意见卡原文：RR-7c 段
  > web `/api/search?limit=` 无硬上限（仅 Python int 默认）—— 取决于 FastAPI/Pydantic 解析
- 矛盾论证：`web/api.py:21-23` `search(q: str, limit: int = 10, request: Request = None)` Python 类型注解仅 `int`，无 `Query(..., ge=1, le=...)` 边界；Pydantic 自动转 int 但**无范围校验**——用户传 `?limit=1000000` 全部命中 → FTS 大查询 → 内存压力 + 延迟；与 P1-4 `_aggregate_entities` 的 `doc_ids` 无上界同一类问题面，但被归入"未发现问题的检查项"清单未独立列项。
- 处置建议：待确认问题卡（归类 ①），与 P1-4 修复承诺合并（`min(int(limit), int(cfg.raw["viz"]["max_docs"]))`）。

### 矛盾项 5 — RR-8 前端 — graph.js G6 初始化缺 `layout`
- 意见卡原文：RR-8 段
  > graph.js G6 初始化：`new G6.Graph({container:canvas, data, node:{style}, edge:{style}, behaviors:["drag-canvas", "zoom-canvas", "drag-element"]})` —— **缺 layout**（§6.3 "选中主题下钻/折叠" 应有 dagre layout；DoD D2）
- 矛盾论证：意见卡自承认"缺 layout"但归入"未发现问题的检查项"清单，仅"标注即可（不立项 P0/P1/P2）"——与"声明-实现对照表"必须逐项对照的 RR-8 规则集要求不符（声明 `data-page` 范式 / 行为 commands / 配置项 与 实际不符 应列为 P3 一致性问题）。`graph.js:52-76` 实际 G6 初始化无 `layout` 字段，DoD D2 "路径高亮" + 15 §6.3 "选中主题下钻/折叠"在 force 默认布局下节点持续抖动，路径高亮将被抵消。
- 处置建议：待确认问题卡（归类 ①），独立列 P3。

---

## 摘要

- 接受：13（P0×2 + P1×6 + P2×3 + P3×2）
- 部分接受：1（P1-2 shortest_path — 保留 LadybugDB 能力受限部分；接受契约断链部分）
- 驳回：0
- 矛盾项：5（RR-4 #2 读路径过滤 6/7 处 / RR-4 #3 RELATES_TO kind 维度 / RR-5 同根 / RR-7c `/api/search?limit=` 上界 / RR-8 graph.js `layout` 缺）

**承接动作**：5 条矛盾项按 `A-B评审闭环工作流.md` §4 触发待确认问题卡（`evals/待确认问题卡-模板.md`），由人工归类四况之一后按处置路由执行；接受项进入修复提交（每条意见的修复可追溯，参见 review-respond.md §3 修复承诺字段）。

**签名**：实现方 A 已按 review-respond.md §1 核对锚点状态（`git show f62f287:<path>` 全部 14 条意见 + 5 条矛盾项的证据文件均已读），未读取 3ffebf0 及其后任何提交。

**摘要行**：接受 13 / 部分 1 / 驳回 0 / 矛盾项 5。
