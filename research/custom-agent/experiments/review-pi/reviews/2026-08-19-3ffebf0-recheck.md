# 复审卡：3ffebf0 修复提交（f62f287 意见卡 × run9-respond 应答卡 闭环核验）

- 日期：2026-08-19 / 评审者：code-review skill v4（MiniMax-M3）
- 复审对象：`3ffebf0`（fix(m5m6): review R-1~R-13 — tombstone 生命周期 + 图读墓碑过滤 + 图谱页交互）
- 评审基线：`f62f287`
- 启用的复核基线：来自 `reviews/2026-08-19-f62f287-run9-skill.md` × `reviews/2026-08-19-run9-respond.md`
- 核对方法：`git show 3ffebf0:<path>` 逐文件比对（实现层 ≠ 测试层 ≠ 设计回写层）；RR-1/RR-2/RR-4/RR-6/RR-7a/RR-7c/RR-8 维度复扫

---

## 意见逐条核验

### [原 P0-1 / 复审 T1] web 包入口缺失 → ImportError
- 应答档：**接受**
- 修复评估：**已修复**（diff 实现 + 复审扫不到仅测试/注释层变更）
- 证据：
  - **新文件** `code/kb-app/src/kbapp/web/__init__.py:1-5`：
    ```
    """Web 可视化包（M6，15 §6）。"""
    from kbapp.web.server import create_app
    __all__ = ["create_app"]
    ```
  - 旧锚点 `git ls-tree -r f62f287 code/kb-app/src/kbapp/web/` 缺该文件 → 现在存在；
  - Python 子包导入 `from kbapp.web import create_app` 找到 `__init__.py` 不再 ImportError；
  - `cli/serve.py:42-44` 同步把 `from kbapp.web import create_app` 移进 `try/except ImportError` 块，并把缺失检测从单一 `uvicorn` 扩展到 `("uvicorn","fastapi","starlette")`（R-8 一并落实）。
- 结论：缺陷本体消除（ImportError 路径收敛）。✅ 已修复

---

### [原 P0-2 / 复审 T2] sync_document_structure 墓碑被 reindex 复活
- 应答档：**接受**
- 修复评估：**已修复**
- 证据：
  - **写路径修复** `code/kb-app/src/kbapp/graph/sync.py:52-57`：在 `document_node` 构造前置一行 `existing = store.query("MATCH (d:Document {doc_id: $id}) RETURN d.valid_to AS valid_to", {"id": doc_id})`；若 `existing[0]["valid_to"]` 非空则原样带回，覆盖原硬编码 `""`。`sync.py:75` `"valid_to": valid_to,` 替换 `"valid_to": ""`。
  - **任务队列层兜底** `code/kb-app/src/kbapp/pipeline/runner.py:202-208`：index 分支新增 `if row is None or row.status == "deleted": _logger.info(...); return` 早退，避免墓碑文档的 index 任务进入 `stage_index_graph` 触发新一轮 `sync_document_structure`。
  - **阶段本身补强** `code/kb-app/src/kbapp/pipeline/graph_stages.py:55-89`：`stage_tombstone_graph` 改为先读出 Document 整行、仅替换 `valid_to` 再整行写回（保留 title/path/corpus/doc_type 全属性），文档从未同步过则返回 `StageResult("skip", metrics={"reason":"document_not_in_graph"})` 不造空心节点（同时修复 run9 评审未识别的"软删抹空属性"缺陷，R-1 同型）。
  - **回归测试** `tests/unit/test_graph_sync.py:194-280` 新增 `test_tombstone_preserves_document_props` / `test_tombstone_skips_when_document_not_in_graph` / `test_sync_after_tombstone_keeps_valid_to`，后者直接断言 `sync → tombstone → 再 sync` 后 `valid_to` 仍为墓碑时间戳。
- 结论：写路径 + 任务队列双层修复 + 回归覆盖；与原建议（a/b 路径二选一）相比实采了更稳的 (b)+写路径+队列早退三层。✅ 已修复

---

### [原 P1-1 / 复审 T3] graph_compare 不消费 doc_ids
- 应答档：**接受**（路径 a/b 二选一并增 `test_graph_compare_filters_by_doc_ids`）
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/retrieve/graph_search.py` 第 60-86 行 `graph_compare` 函数体未变：`params: dict[str, Any] = {"concept": concept, "limit": int(limit)}` 仍不含 `doc_ids`；Cypher `MATCH (a:Entity {entity_id: $concept})-[r:RELATES_TO]-(b:Entity) RETURN ...` 仍未引用 doc_ids；函数注释仍写 "doc_ids 限定：lbug 暂不支持 EXISTS 子查询 + 多 MATCH 联合；先按 concept 宽查，前端按 doc_ids 过滤显示..."——保留延迟技术债描述。
  - `tests/unit/test_graph_search.py:243-308` diff 仅新增 `test_graph_related_excludes_tombstoned_documents` / `test_graph_related_section_ids_not_collapsed_to_parent`，**未出现**应答档承诺的 `test_graph_compare_filters_by_doc_ids`。
- 残留：调用方透传 `doc_ids=[D1,D2]` 与 `doc_ids=None` 结果完全相同（与 f62f287 同源问题面，未变）。
- 结论：应答档承诺的修复路径完全未落地，仅 doc_ids 形参保留声明。❌ 未修复

---

### [原 P1-2 / 复审 T4] shortest_path 仅返 length → 路径高亮契约失守
- 应答档：**部分接受**（保留 LadybugDB 能力受限部分；接受契约断链部分，倾向路径 a）
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/graph/ladybug_store.py` 全文 `shortest_path` 方法未在 diff 范围内（唯一改动 `ladybug_store.py:118-133` 是 RELATES_TO MERGE 键补 kind，与 shortest_path 无关——见 [C2/3]）。
  - `git show 3ffebf0:code/kb-app/src/kbapp/retrieve/graph_search.py` 全文未引用 shortest_path（`graph_search.py` 只有 `graph_related` / `graph_compare` 两个公开函数，未涉及 `entity_path` 的实现细节）。
  - `git show 3ffebf0:code/kb-app/src/kbapp/graph/queries.py:140-145`（diff 末尾的 entity_path）仅导入更新 `__all__ = ["entity_path", "node_neighbors", "topic_subgraph"]`，**函数体本身未动**——`entity_path` 仍只 MATCH 实体间最短路径长度，无 nodes/edges 返回。
  - 前端 `web/static/graph.js` 重写后引入 `findVisiblePath(src, dst, serverLen)` 走客户端 BFS 在**已渲染**图内反推一条路径，回退到仅高亮端点；但源头仍是 `data.paths[0].length` 这一数字契约，没修 `ladybug_store.shortest_path` 的"只返 length"本体。
  - 路径高亮契约宣称 `nodes/relationships` 也回填未实现（web/api.py graph_path 端点契约仍是 `{"paths":[{"length":...}]}`，未扩 `nodes`/`edges` 字段）。
  - 测试侧：应答档承诺"扩展 `tests/unit/test_graph_contract.py`"未在 diff 出现（test_graph_contract.py 不在 19 个改动文件清单内）。
- 结论：应答档"倾向 (a)""涉及 graph/queries.py entity_path + ladybug_store"全部未落地；契约断链仍在，仅前端用 BFS 反推做掩耳盗铃式高亮。❌ 未修复

---

### [原 P1-3 / 复审 T5] queries.py:topic_subgraph 用 `repr()` 拼 Cypher IN
- 应答档：**接受**（路径 (a) LadybugStore 加 `_query_in` helper；topic_subgraph 五处 Cypher 全部改走参数绑定）
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/graph/queries.py:104-119`（修复后的边装配段）：
    ```
    for rel in ["CONTAINS_SECTION", "MENTIONS", "ABOUT_TOPIC", "RELATES_TO"]:
        ids_csv = ",".join(repr(n) for n in new_seen)
        cypher_edges = (
            f"MATCH (a)-[r:{rel}]->(b) "
            f"WHERE coalesce(a.entity_id, a.section_id, a.doc_id, a.name) IN [{ids_csv}] "
            f"AND coalesce(b.entity_id, b.section_id, b.doc_id, a.name) IN [{ids_csv}] "
            ...
        )
        for r in store.query(cypher_edges, {}):
    ```
    `ids_csv = ",".join(repr(n) for n in new_seen)` 仍在；`f"...IN [{ids_csv}]..."` 字符串拼接仍在；`store.query` 第二参数仍 `{}` 空字典不绑定——与 f62f287 同源问题面未消除。
  - 注意 diff 注释行 `queries.py:99-103` 自承认这是 R-10 修复（key 顺序），但**未触及** P1-3 字符串拼接。
  - `ladybug_store.py` 不在本次 diff 变更范围内（仅 RELATES_TO MERGE 键一处），未引入 `_query_in` helper。
  - 测试侧：应答档承诺的 `test_graph_queries.py::test_topic_subgraph_no_string_concat` 未在 diff 出现（test_graph_queries.py 新增的 329 行全部围绕 R-2 墓碑过滤 + R-5 node_neighbors + R-10 键序）。
- 结论：缺陷本体（拼接 IN 列表）一行未改；应答档承诺的 helper 与回归测试均未落地。❌ 未修复

---

### [原 P1-4 / 复审 T6] web/api.py:_aggregate_entities 同样 `repr()` 拼 Cypher + doc_ids 无上界
- 应答档：**接受**（参数绑定 + `viz.max_docs` 上界 + 50 配置默认值；新增配置 + `/api/search` limit 上界）
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/web/api.py:52-69`：
    ```
    docs_csv = ",".join(repr(d) for d in doc_ids)
    ...
    for r in store.query(
        f"MATCH (d:Document)-[:CONTAINS_SECTION]->(s:Section)-[m:MENTIONS]->(e:Entity) "
        f"WHERE s.doc_id IN [{docs_csv}] AND d.valid_to = '' "
        ...
    ):
    ```
    `docs_csv = ",".join(repr(d) for d in doc_ids)` 仍在；`f"...IN [{docs_csv}]..."` 字符串拼接仍在；`store.query` 第二参数实参与 run9 行 67 相比无新增（diff 仅改 WHERE 条件增量补墓碑过滤）。
  - `web/api.py:24` `def search(q: str, limit: int = 10, request: Request = None)` 仍无 `Query(..., ge=1, le=...)` 边界或 `min(int(limit), int(cfg.raw["viz"]["max_docs"]))` 截断。
  - `code/kb-app/src/kbapp/core/config.py` 不在 diff 范围，`viz.max_docs` 配置键未新增。
  - `tests/unit/test_web_api.py` 新增文件存在但只覆盖 R-2/R-5/R-7（墓碑过滤/neighbors 端点/deleted 404），无 `test_search_aggregates_entities_with_param_binding` 与"limit 上界"断言。
- 结论：契约违规（拼接）与上界缺失（无界）双缺陷一行未改；应答档承诺全数未落地。❌ 未修复

---

### [原 P1-5 / 复审 T7] run_extract 把 Entity.aliases 列表 `",".join()` 扁平化为串
- 应答档：**接受**（`json.dumps` 序列化 + 读端 `json.loads` 反序列化；补 `test_extract_aliases_round_trip`）
- 修复评估：**未修复**
- 证据：
  - `code/kb-app/src/kbapp/graph/extract.py` 不在 19 个改动文件清单内（与 f62f287 同源问题面未变）。
  - `tests/unit/test_extract.py` 也不在 19 个改动文件清单内，应答档承诺的 `test_extract_aliases_round_trip` 未落地。
- 结论：应答档承诺完全未涉及修复文件，无可观测 diff。❌ 未修复

---

### [原 P1-6 / 复审 T8] Document.summary_l1/l2 字段从未填充（schema 漂移）
- 应答档：**接受**（倾向路径 (a) `stage_summarize` 完成后写 summary_l1/l2 + store.upsert_nodes 部分字段 patch）
- 修复评估：**未修复**
- 证据：
  - `code/kb-app/src/kbapp/pipeline/stages.py` 不在 diff 范围——`stage_summarize` 函数体未改写，仍仅写 `files.summary_source/path` + `$summary` 伪 chunk。
  - `code/kb-app/src/kbapp/graph/schema.py` 不在 diff 范围——`summary_l1/l2` 字段仍声明；`15-M5M6合并补充设计.md` 也未回写删除该字段。
  - 在 `code/kb-app/src/kbapp/graph/sync.py:70-71` 反而新写入：`"summary_l1": "", "summary_l2": ""`（被现有 valid_to 保留逻辑一并原样带回了空串，与 P0-2 修复兼容但漂移面仍未修）。
- 结论：应答档路径 (a)/(b) 均未走通；空串仍写入图节点。❌ 未修复

---

### [原 P1-7 / 复审 T9] graph/extract.py::_entity_type_by_name 同名不同 type 错配
- 应答档：**接受**（`name→types: list[str]` 多值映射；relations 解析时穷举；或要求 LLM 输出 entity_id）
- 修复评估：**未修复**
- 证据：
  - `code/kb-app/src/kbapp/graph/extract.py` 不在 diff 范围；`_entity_type_by_name:223-230` 与 `entity_id = f"{type}:{norm(name)}"` 构造逻辑均未改。
  - `_extract_prompt`（prompt 契约变更路径）也不在 diff 范围。
- 结论：缺陷本体未触及。❌ 未修复

---

### [原 P2-1 / 复审 T10] mcp_server 目标 entity 不存在时静默返空，无 NOT_FOUND
- 应答档：**接受**（前置 MATCH 探测 + `_error("TARGET_NOT_FOUND", ...)` + 回写 13 §2.2 表 + 补 `test_mcp_target_not_found`）
- 修复评估：**未修复**
- 证据：
  - `code/kb-app/src/kbapp/mcp_server.py` 不在 19 个改动文件清单内；`_kb_compare` / `_kb_related` 透传 `graph_related` / `graph_compare` 未补探测分支。
  - `design/kb-app/13-M4补充设计.md` 不在 diff 范围。
  - `tests/integration/test_mcp.py` 不在 diff 范围。
- 结论：缺陷本体 + 测试 + 设计回写三项均未动。❌ 未修复

---

### [原 P2-2 / 复审 T11] web/api.py 五个读端点每次新建图库 store，无 lifespan 单例
- 应答档：**接受**（`web/server.py:create_app` 改 `asynccontextmanager` lifespan 启停 + 5 端点改 `request.app.state.graph_store`；LadybugStore 补 `is_open()` 守卫）
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/web/server.py`：`create_app` 函数体未引入 `lifespan` / `asynccontextmanager`；`app.state` 仅存 `registry/cfg/paths`；5 个 endpoint 仍走 `make_graph_store → open(ro) → try/finally close` 老路径。
  - diff 仅删除 4 处冗余局部 `from fastapi.responses import FileResponse` 改至文件头 — 顺手清理 import，**不触及连接生命周期**。
  - `code/kb-app/src/kbapp/web/api.py:60-75/121-140/146-160/200-215/230-245`（修复后）每个端点仍各自 `make_graph_store + open + try/finally close`——单例未建。
  - `ladybug_store.py` 未新增 `is_open()` 守卫或类似连接管理 API。
  - 测试侧 `test_web_server.py::test_state_graph_store_singleton` 未在 diff 出现。
- 结论：缺陷本体（每次 open/close）一行未改；应答档的 lifespan 改写与回归测试均未落地。❌ 未修复

---

### [原 P2-3 / 复审 T12] is_core_doc 对 doc_type=None 静默剔除，无 metric/log
- 应答档：**接受**（`doc_type is None → False` 分支显化 + `_logger.info` 日志；`stage_extract_graph` 把 `skipped_no_doc_type` / `skipped_doc_type_not_allowed` 计入 metrics；补 `test_is_core_doc_skipped_no_doc_type_metrics`）
- 修复评估：**未修复**
- 证据：
  - `code/kb-app/src/kbapp/graph/extract.py` 不在 diff 范围；`_doc_type_allowed` 三态分支未改（`doc_type is None → False` 已隐含在 `is not None and doc_type in allowed` 但**未显化日志**）。
  - `code/kb-app/src/kbapp/pipeline/graph_stages.py:78-87` diff 仅改 `stage_tombstone_graph`；`stage_extract_graph` 未变（仍 `StageResult("skip", detail=...)` + metrics 字典空）。
  - `tests/unit/test_extract.py` 不在 diff 范围。
- 结论：缺陷本体（静默剔除）未变更；可观测性缺失未补。❌ 未修复

---

### [原 P3-1 / 复审 T13] test_topic_subgraph_truncates 条件断言
- 应答档：**接受**（前置必触发 `assert len(result["nodes"]) >= 600` + truncated is True + ≤ max_nodes）
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/tests/unit/test_graph_queries.py:130-140`：
    ```
    if len(result["nodes"]) >= 500:
        assert result["truncated"] is True
        assert len(result["nodes"]) <= 500
    ```
    与 f62f287 run9 P3-1 锚点（`if len(result["nodes"]) >= 500: ...`）完全相同；条件断言未被前置必触发改动。
  - 同一文件新增 329 行均为 R-2 / R-5 / R-10 测试，未触 P3-1。
- 结论：弱断言本体未改。❌ 未修复

---

### [原 P3-2 / 复审 T14] graph.html 不引用 app.js 缺注释
- 应答档：**接受**（在 graph.html:7 后加注释 `<!-- 不走 app.js 分派 -->`）
- 修复评估：**已修复**（修复手段优于应答档建议）
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/web/static/graph.html` 改为：
    ```html
    <main>
      ...
      <p class="hint">单击节点展开 1 跳邻域；双击折叠/展开；Shift+拖拽框选；依次单击两个实体查询并高亮最短路径；点空白清除高亮。</p>
    </main>
    <script src="/static/app.js" defer></script>
    <script src="/static/graph.js" defer></script>
    ```
    两个 script 都用 `defer`，按文档顺序执行——`fetchJson` 在 app.js 中先定义，graph.js 后引用，与 index/document/status 三页范式统一。
  - 应答档倾向"加注释说明设计选择"，实现方反而**采纳了 app.js 分派范式**——把 graph.html 的 page 范式与其它三页对齐（RR-8 一致性彻底满足），同时让 graph.js 可复用 fetchJson。这正是 run8 P0-1 暴露的"graph.js 自定义 fetchJson"技术债的根因——一致比注记更强。
- 结论：缺陷消解；修复手段比建议更彻底。✅ 已修复

---

## 矛盾项（应答档独立提出的 P0/P1 面）逐项核验

### [C1] RR-4 #2 读路径 valid_to 过滤 6/7 处（独立问题面）
- 应答档：**待确认**（归类 ①，建议与 P0-2 合并 P0）
- 修复评估：**部分修复**（6 处中 5 处落实，1 处残留）
- 落实证据：
  | # | 路径 | diff 后位置 | 过滤形态 | 状态 |
  |---|---|---|---|---|
  | 1 | `graph_search.py:graph_related` | graph_search.py:37-43 + :61-63 | Python 层 "tombstoned" 集合 fetch + 端点级 `if rid in tombstoned or r["parent_doc"] in tombstoned: continue` | ✅ |
  | 2 | `graph_search.py:graph_compare` | graph_search.py:65-86 | **未补 valid_to 过滤** | ❌ 残留 |
  | 3 | `web/api.py:_aggregate_entities` | web/api.py:63-69 | `AND d.valid_to = ''` | ✅ |
  | 4 | `web/api.py:_doc_mentions` | web/api.py:124-129 | `AND d.valid_to = ''` | ✅ |
  | 5 | `web/api.py:_doc_related_docs` | web/api.py:150-159 | `AND d2.valid_to = ''` | ✅ |
  | 6 | `web/api.py:graph_subgraph` → `topic_subgraph` | queries.py:33-38 | `WHERE d.valid_to = ''` | ✅ |
  | 7 | `web/api.py:graph_path` → `entity_path` | queries.py:140-145（函数体未动） | **未补 valid_to 过滤**（entity 之间最短路径间接经过墓碑文档仍可见） | ❌ 残留 |
  | 8 | `mcp_server:_kb_related / _kb_compare` | （mcp_server.py 未在 diff）→ 走 graph_search 内部过滤 | mcp 端调 graph_related 已自带；调 graph_compare 不带 | △ 半覆盖 |
- 残留：graph_compare（实体图对照，间接经墓碑文档的实体仍出现）+ entity_path（实体路径，端点为墓碑文档关联的实体仍出现）。
- 结论：**部分修复**（5/6 核心读路径补全；新发现 [N1]/[N2] 为残留路径）。

### [C2/3] RR-4 #3 + RR-5 RELATES_TO upsert_edges 主键缺 kind
- 修复评估：**已修复**
- 证据：
  - `code/kb-app/src/kbapp/graph/ladybug_store.py:121-130` 新增 `merge_clause` 分支：
    ```
    merge_clause = (
        f"MERGE (a)-[r:{rel} {{kind: $kind}}]->(b)"
        if rel == "RELATES_TO"
        else f"MERGE (a)-[r:{rel}]->(b)"
    )
    ```
    配合 `params = {"src": src, "dst": dst, **props}`（`props` 含 `kind` 因 `RELATES_TO.props` 含 `kind` 字段）。
  - 回归测试 `tests/unit/test_ladybug_store.py:91-139` 新增 `test_relates_to_multi_kind_coexists` / `test_relates_to_same_kind_idempotent`，断言同 `(src,dst)` 两不同 kind 边并存 + 同 kind 重复 upsert 幂等。
- 结论：MERGE 主键补 `{kind}`；冲突消解（run9 P1-3 同型）+ 幂等（RR-5）双口径同时满足。✅ 已修复

### [C4] RR-7c `/api/search?limit=` 无硬上限
- 修复评估：**未修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/web/api.py:21` `def search(q: str, limit: int = 10, request: Request = None)`（注解签名未变）；
  - diff 中 web/api.py 仅改 `_aggregate_entities` / `get_doc` / `_doc_mentions` / `_doc_related_docs` 四处，`search` 端点整体未动；
  - `tests/unit/test_web_api.py` 新增 234 行全部围绕 R-2/R-5/R-7，无 limit 上界断言。
  - 应答档承诺的 `min(int(limit), int(cfg.raw["viz"]["max_docs"]))` 与 `viz.max_docs` 配置均未落地。
- 结论：硬上限缺失原样保留。❌ 未修复

### [C5] RR-8 graph.js G6 初始化缺 `layout`
- 修复评估：**已修复**
- 证据：
  - `git show 3ffebf0:code/kb-app/src/kbapp/web/static/graph.js:111-115`（renderGraph 内 G6 初始化）：
    ```javascript
    layout: { type: "antv-dagre", rankdir: "TB", nodesep: 30, ranksep: 60 },
    autoFit: "center",
    behaviors: [
      { type: "drag-canvas", enable: (e) => !e.shiftKey },
      "zoom-canvas",
      "drag-element",
    ],
    ```
    dagre 自上而下分层布局补齐，DoD D2 "下钻/折叠/路径高亮" 视觉效果不再因节点堆左上角失效；同时 `autoFit: "center"` 保图幅居中。
- 结论：声明-实现一致性缺口闭合。✅ 已修复

---

## 回归检查（修复 diff 本身）

按 code-review skill v4 的 RR-1/RR-2/RR-4/RR-5/RR-6/RR-7a/RR-7c/RR-8 维度对 3ffebf0 修复 diff 本身过一遍——发现如下新问题：

### [N1] mcp_server 侧 valid_to 过滤覆盖不完整
- 类型：范围缺口（修读路径未与调用面同步核查）
- 证据：`code/kb-app/src/kbapp/mcp_server.py` 未在 diff 范围；其 `_kb_related` 调 `graph_search.graph_related`（已带 Python 层 tombstoned 集合过滤），但若改为走 `topic_subgraph` 或新 `node_neighbors` 端点（MCP 端未声明调用，但 web 端已用）需另查；`mcp_server._kb_compare` 调 `graph_search.graph_compare`（**仍无** valid_to 过滤）—— 与 [T3] / [C1] 同源残留。
- 维度：RR-1 / RR-4 / 契约一致性
- 处置建议：mcp_server.py 修复 / 测试两件并补，与 web 侧同步。

### [N2] graph_compare 仍无 valid_to 过滤（与 [T3] 不同问题面）
- 类型：实现偏离（修复范围遗漏）
- 证据：`git show 3ffebf0:code/kb-app/src/kbapp/retrieve/graph_search.py:64-86` `graph_compare` 函数：MATCH `(a:Entity)-[r:RELATES_TO]-(b:Entity)` 不经 Document/Section，但（a/b）的 entity_id 由 Section 通过 MENTIONS 关联进来——若 Section 在墓碑文档下，entity 仍出现在对照表里。05 §6 显式列出 "经 `[:MENTIONS]` 过滤 doc_ids"；valid_to 过滤是 doc_ids 过滤的简化版（"墓碑 doc_ids 一律剔除"），二者同样缺位。
- 维度：RR-4 #2 / RR-1
- 处置建议：在 RELATES_TO 模式上加 `MATCH (a)<-[:MENTIONS]-(s:Section)<-[:CONTAINS_SECTION]-(d:Document) WHERE d.valid_to = ''` 或在 Python 层 fetch 后过滤 evidence_section_id 对应父 Document。

### [N3] graph_related 每次调用 fetch 全量墓碑集合（性能伸缩性）
- 类型：性能回归（为修 tomestone 过滤引入，但非测试覆盖点）
- 证据：graph_search.py:37-43 每次进入 graph_related 即执行 `MATCH (d:Document) WHERE d.valid_to <> '' RETURN d.doc_id AS doc_id`——拉全图所有软删文档。在百万级 Document 库下每次 MCP / Web 请求都跑一次全表扫，且结果不缓存。
- 维度：RR-6 / 性能契约
- 处置建议：lbug 层面加 `valid_to <> ''` 上的 secondary index（如果 backend 支持）或在 GraphStore 层维护进程内墓碑集合 TTL 缓存；至少补规模上限断言。

### [N4] graph.js::clearHighlight 传 `[]` 给 setElementState 语义未明
- 类型：API 调用风险（被 try/except 吞，潜在静默失败）
- 证据：graph.js:230-243（修复后）：
  ```javascript
  function clearHighlight() {
    ...
    const reset = {};
    highlighted.forEach((id) => { reset[id] = []; });
    Promise.resolve(lastRender).then(() => {
      try { graph.setElementState(reset); } catch (_e) { /* 图已重建时忽略 */ }
    });
    ...
  }
  ```
  G6 v5 `setElementState({id: []})` 中空数组的语义官方文档未明（一般 `null`/`"default"` 表示清空）；try/except 把任何异常吞掉不记录——后续若 G6 版本更新解除宽容，会以"高亮清不掉"的视觉 bug 形式回返。
- 维度：RR-8 一致性 / 可观测性
- 处置建议：替换为 `setElementState({[id]: "default"})`（G6 官方 reset 语义）或先在 dev 环境去掉 try/except 跑一遍自验。

---

## 复审摘要

### 接受条目 14 条核验结果

| 复审标号 | 原意见 | 应答态度 | 复审结论 | 关键证据 |
|---|---|---|---|---|
| T1 | [P0] web 包入口缺失 | 接受 | **已修复** | web/__init__.py 新建 + serve.py import 检测扩展 |
| T2 | [P0] sync 墓碑复活 | 接受 | **已修复** | sync.py 读既有 valid_to + runner 早退 + 多回归测试 |
| T3 | [P1] graph_compare doc_ids | 接受 | **未修复** | graph_search.py graph_compare 函数体未变；承诺测试未落 |
| T4 | [P1] shortest_path 缩水 | 部分接受 | **未修复** | ladybug_store.py / queries.py entity_path 函数体未动；契约仍仅 length |
| T5 | [P1] queries.py Cypher IN 拼接 | 接受 | **未修复** | ids_csv 拼接原样保留；in `[]` 原样保留 |
| T6 | [P1] api.py _aggregate_entities 拼接 + 上界 | 接受 | **未修复** | docs_csv 拼接原样保留；无 viz.max_docs |
| T7 | [P1] aliases 扁平化 | 接受 | **未修复** | extract.py 不在 diff |
| T8 | [P1] summary_l1/l2 schema 漂移 | 接受 | **未修复** | stages.py / schema.py 不在 diff |
| T9 | [P1] 同名不同 type | 接受 | **未修复** | extract.py 不在 diff |
| T10 | [P2] ENTITY_NOT_FOUND | 接受 | **未修复** | mcp_server.py 不在 diff |
| T11 | [P2] web/api lifespan | 接受 | **未修复** | server.py 仅清理 import，无 lifespan |
| T12 | [P2] is_core_doc doc_type=None | 接受 | **未修复** | extract.py 不在 diff |
| T13 | [P3] test_topic_subgraph_truncates 条件断言 | 接受 | **未修复** | 测试断言 1 字未改 |
| T14 | [P3] graph.html 不引 app.js | 接受 | **已修复**（手段更彻底） | graph.html 改为统一范式引 app.js |

### 矛盾项 5 条核验结果

| 复审标号 | 矛盾项 | 复审结论 | 关键证据 |
|---|---|---|---|
| C1 | 读路径 valid_to 过滤 6 处失守 | **部分修复** | 5/6 落实；graph_compare + entity_path 残留 |
| C2/3 | RELATES_TO kind 维度 | **已修复** | ladybug_store.py:121-130 merge_clause + 双回归 |
| C4 | /api/search?limit= 上界 | **未修复** | search 端点签名未变 |
| C5 | graph.js layout 缺 | **已修复** | graph.js:111-113 antv-dagre TB |

### 回归新发现 4 条

| 复审标号 | 新发现 | 维度 | 处置 |
|---|---|---|---|
| N1 | mcp_server 读路径过滤覆盖不全 | RR-1 / RR-4 | mcp_server.py 同步修复 |
| N2 | graph_compare 仍无 valid_to 过滤 | RR-4 #2 | queries.py / graph_search.py 补过滤 |
| N3 | graph_related 每次 fetch 全量墓碑 | RR-6 / 性能 | 缓存或索引 |
| N4 | graph.js clearHighlight `[]` 语义未明 | RR-8 / 可观测性 | 用 `"default"` 语义替代 |

---

**摘要行**：已修复 5 / 部分 1 / 未修复 12 / 驳回成立 0 / 待确认 0 / 新发现 4

**复审方结论**：3ffebf0 仅完成 P0 双缺陷 + P3-2 + 矛盾项 C2/C3/C5（5 项），其余 12 项应答档"接受"承诺的修复路径均未真正落地——diff 范围（19 文件 / +1415 行）主要集中在 tombstone 生命周期补救与图谱页 UI 重写，未触及 P1-3/4/5/6/7/8 批次的契约违规修复面。建议实现方按本卡 [T3]~[T13] + [N1]~[N2] 的 file:line 指引重启一轮修复，重点关注 (a) graph_search.graph_compare doc_ids 接入 + valid_to 过滤；(b) queries.py / api.py 两处字符串拼接彻底改为参数绑定或 _query_in helper；(c) extract.py / pipeline stages.py / mcp_server.py 三文件组的契约一致性回归。
