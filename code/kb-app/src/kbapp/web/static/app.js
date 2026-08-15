/* GraphIt-KB 前端逻辑（15 §6.3 vanilla + data-page 分派） */
(function () {
  const page = document.body.dataset.page;
  if (page === "search") {
    initSearch();
  } else if (page === "document") {
    initDocument();
  } else if (page === "status") {
    initStatus();
  }
})();

function fetchJson(url) {
  return fetch(url).then((r) => {
    if (!r.ok) throw new Error(r.status + " " + r.statusText);
    return r.json();
  });
}

function initSearch() {
  const q = document.getElementById("q");
  const btn = document.getElementById("btn");
  const out = document.getElementById("results");
  function go() {
    if (!q.value.trim()) return;
    fetchJson("/api/search?q=" + encodeURIComponent(q.value) + "&limit=20")
      .then((data) => {
        const rows = (data.hits || [])
          .map((h, i) => `${i + 1}. ${h.doc_id} ${h.section_path} ${h.title}<br>${h.snippet || ""}`)
          .join("<br>");
        out.innerHTML = `<p>${(data.hits || []).length} hits</p><div>${rows}</div>`;
      })
      .catch((e) => (out.innerHTML = "<p>Error: " + e.message + "</p>"));
  }
  btn.addEventListener("click", go);
  q.addEventListener("keydown", (e) => {
    if (e.key === "Enter") go();
  });
}

function initDocument() {
  const doc = document.getElementById("doc");
  const btn = document.getElementById("btn");
  btn.addEventListener("click", () => {
    if (!doc.value.trim()) return;
    fetchJson("/api/docs/" + doc.value)
      .then((data) => {
        document.getElementById("meta").innerHTML = `<pre>${JSON.stringify(data.doc, null, 2)}</pre>`;
        document.getElementById("summary").innerHTML = `<h2>摘要</h2><pre>${data.summary || ""}</pre>`;
        document.getElementById("sections").innerHTML = `<h2>章节</h2><pre>${JSON.stringify(data.sections, null, 2)}</pre>`;
      })
      .catch((e) => (document.getElementById("meta").innerHTML = "<p>Error: " + e.message + "</p>"));
  });
}

function initStatus() {
  fetchJson("/api/status")
    .then((data) => {
      document.getElementById("status").innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    })
    .catch((e) => (document.getElementById("status").innerHTML = "<p>Error: " + e.message + "</p>"));
}
