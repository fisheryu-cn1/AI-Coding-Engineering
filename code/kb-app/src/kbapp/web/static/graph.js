/* GraphIt-KB 图谱页（Task 18 充实） */
(function () {
  const sel = document.getElementById("topic");
  const btn = document.getElementById("btn");
  const canvas = document.getElementById("canvas");

  fetchJson("/api/topics")
    .then((data) => {
      (data.topics || []).forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t.name;
        opt.textContent = `${t.name} (${t.doc_count})`;
        sel.appendChild(opt);
      });
    })
    .catch((e) => (canvas.innerHTML = "<p>Error: " + e.message + "</p>"));

  btn.addEventListener("click", () => {
    const topic = sel.value;
    if (!topic) return;
    fetchJson("/api/graph/subgraph?topic=" + encodeURIComponent(topic) + "&hops=2")
      .then((data) => renderGraph(data))
      .catch((e) => (canvas.innerHTML = "<p>Error: " + e.message + "</p>"));
  });
})();

function renderGraph(data) {
  const canvas = document.getElementById("canvas");
  canvas.innerHTML = "";
  if (data.truncated) {
    const banner = document.createElement("div");
    banner.className = "truncated";
    banner.textContent = `子图已截断到 ${data.nodes.length} 节点（cap=${data.max_nodes}）`;
    canvas.parentNode.insertBefore(banner, canvas);
  }
  if (typeof G6 === "undefined") {
    canvas.innerHTML = "<p>G6 未加载</p>";
    return;
  }
  const graph = new G6.Graph({
    container: canvas,
    data: { nodes: data.nodes, edges: data.edges },
    node: { style: { labelText: (d) => d.label } },
    edge: { style: { endArrow: true } },
  });
  graph.render();
}
