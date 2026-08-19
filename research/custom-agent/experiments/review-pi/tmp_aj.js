/* GraphIt-KB 前端逻辑（15 §6.3 vanilla + data-page 分派） */
(function () {
  const page = document.body.dataset.page;
  if (page === "search") initSearch();
  else if (page === "document") initDocument();
  else if (page === "status") initStatus();
})();

function fetchJson(url) {
  return fetch(url).then((r) => {
    if (!r.ok) throw new Error(r.status + " " + r.statusText);
    return r.json();
  });
}

function el(tag, attrs, children) {
  const e = document.createElement(tag);
  if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (children) (children || []).forEach((c) => e.appendChild(c));
  return e;
}

function renderHits(hits) {
  if (!hits || !hits.length) {
    return el("p", { class: "empty" }, [document.createTextNode("无命中")]);
  }
  const tbl = el("table");
  const thead = el("thead");
  const trh = el("tr");
  ["#", "doc_id", "section", "title", "score", "snippet"].forEach((h) => {
    trh.appendChild(el("th", null, [document.createTextNode(h)]));
  });
  thead.appendChild(trh);
  tbl.appendChild(thead);
  const tbody = el("tbody");
  hits.forEach((h, i) => {
    const tr = el("tr");
    [String(i + 1), h.doc_id, h.section_path, h.title || "", h.score.toFixed(4), h.snippet || ""].forEach((v) => {
      tr.appendChild(el("td", null, [document.createTextNode(v)]));
    });
    tbody.appendChild(tr);
  });
  tbl.appendChild(tbody);
  return tbl;
}

function initSearch() {
  const q = document.getElementById("q");
  const btn = document.getElementById("btn");
  const out = document.getElementById("results");
  const cloud = document.getElementById("entity-cloud");
  function go() {
    const v = q.value.trim();
    if (!v) return;
    out.innerHTML = "查询中…";
    fetchJson("/api/search?q=" + encodeURIComponent(v) + "&limit=20")
      .then((data) => {
        out.innerHTML = "";
        const head = el("h2", null, [document.createTextNode(`${(data.hits || []).length} 条命中`)]);
        out.appendChild(head);
        out.appendChild(renderHits(data.hits || []));
        if (data.note) out.appendChild(el("p", { class: "note" }, [document.createTextNode(data.note)]));
        // 实体词云（Task 19 占位；从 search 响应读 entities 字段）
        if (data.entities && data.entities.length) {
          cloud.innerHTML = "<h3>命中实体</h3>";
          data.entities.forEach((e) => {
            const span = el("span", { class: "pill" }, [document.createTextNode(`${e.name} (${e.count})`)]);
            cloud.appendChild(span);
          });
        }
      })
      .catch((e) => (out.innerHTML = "<p>Error: " + e.message + "</p>"));
  }
  btn.addEventListener("click", go);
  q.addEventListener("keydown", (e) => {
    if (e.key === "Enter") go();
  });
}

function initDocument() {
  const docInput = document.getElementById("doc");
  const btn = document.getElementById("btn");
  function go() {
    const v = docInput.value.trim();
    if (!v) return;
    document.getElementById("meta").innerHTML = "载入中…";
    fetchJson("/api/docs/" + encodeURIComponent(v))
      .then((data) => {
        document.getElementById("meta").innerHTML = "<h2>元数据</h2><pre>" + JSON.stringify(data.doc, null, 2) + "</pre>";
        document.getElementById("summary").innerHTML = "<h2>摘要</h2><pre>" + (data.summary || "(无)") + "</pre>";
        document.getElementById("sections").innerHTML = "<h2>章节树</h2><pre>" + JSON.stringify(data.sections, null, 2) + "</pre>";
        // 关联侧栏（Task 19 占位）
        if (data.related_docs) {
          document.getElementById("related").innerHTML = "<h3>关联文档</h3><pre>" + JSON.stringify(data.related_docs, null, 2) + "</pre>";
        }
        if (data.mentioned_entities) {
          document.getElementById("mentions").innerHTML = "<h3>提及实体</h3><pre>" + JSON.stringify(data.mentioned_entities, null, 2) + "</pre>";
        }
      })
      .catch((e) => (document.getElementById("meta").innerHTML = "<p>Error: " + e.message + "</p>"));
  }
  btn.addEventListener("click", go);
  docInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") go();
  });
}

function initStatus() {
  fetchJson("/api/status")
    .then((data) => {
      document.getElementById("status").innerHTML = "<h2>库状态</h2><pre>" + JSON.stringify(data, null, 2) + "</pre>";
    })
    .catch((e) => (document.getElementById("status").innerHTML = "<p>Error: " + e.message + "</p>"));
}
