/* GraphIt-KB 图谱页（15 §6.3 / Task 18 DoD D2）
* 主题下钻 / 双击折叠 / 框选 / 路径高亮 — G6 v5 内置交互。
*/
(function () {
  const sel = document.getElementById("topic");
  const btn = document.getElementById("btn");
  const canvas = document.getElementById("canvas");
  const banner = document.getElementById("truncated-banner");

  let graph = null;
  let lastData = null;
  let collapsed = new Set();

  fetchJson("/api/topics")
    .then((data) => {
      (data.topics || []).forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t.name;
        opt.textContent = `${t.name} (${t.doc_count})`;
        sel.appendChild(opt);
      });
    })
    .catch((e) => {
      canvas.innerHTML = "<p>载入主题失败：" + e.message + "</p>";
    });

  btn.addEventListener("click", () => loadSubgraph());

  function loadSubgraph() {
    const topic = sel.value;
    if (!topic) return;
    canvas.innerHTML = "加载中…";
    fetchJson("/api/graph/subgraph?topic=" + encodeURIComponent(topic) + "&hops=2")
      .then((data) => {
        lastData = data;
        if (data.truncated) {
          banner.classList.remove("hidden");
          banner.textContent = `子图已截断到 ${data.nodes.length} 节点（cap=${data.max_nodes}）`;
        } else {
          banner.classList.add("hidden");
        }
        renderGraph(data);
      })
      .catch((e) => (canvas.innerHTML = "<p>错误：" + e.message + "</p>"));
  }

  function renderGraph(data) {
    canvas.innerHTML = "";
    if (typeof G6 === "undefined") {
      canvas.innerHTML = "<p>G6 v5 未加载</p>";
      return;
    }
    const filtered = {
      nodes: (data.nodes || []).filter((n) => !collapsed.has(n.id)),
      edges: (data.edges || []).filter((e) => !collapsed.has(e.src) && !collapsed.has(e.dst)),
    };
    graph = new G6.Graph({
      container: canvas,
      data: {
        nodes: filtered.nodes.map((n) => ({
          id: n.id,
          data: { label: n.label, type: n.type, dist: n.dist },
        })),
        edges: filtered.edges.map((e) => ({
          id: e.src + "→" + e.dst,
          source: e.src,
          target: e.dst,
          data: { rel: e.rel },
        })),
      },
      node: {
        style: {
          size: 24,
          labelText: (d) => d.data.label,
          fill: (d) => colorByType(d.data.type),
          stroke: "#333",
          lineWidth: 1,
        },
      },
      edge: {
        style: {
          labelText: (d) => d.data.rel,
          endArrow: true,
          stroke: "#888",
        },
      },
      behaviors: ["drag-canvas", "zoom-canvas", "drag-element"],
    });
    graph.render();

    // 双击节点 → 折叠/展开
    graph.on("node:dblclick", (e) => {
      const id = e.target.id;
      if (collapsed.has(id)) collapsed.delete(id);
      else collapsed.add(id);
      renderGraph(lastData);
    });

    // 点击节点 → 查找路径（与 Topic 起点对比）
    graph.on("node:click", (e) => {
      const topic = sel.value;
      if (!topic || e.target.id === topic) return;
      fetchJson(`/api/graph/path?src=${encodeURIComponent(topic)}&dst=${encodeURIComponent(e.target.id)}&max_hops=3`)
        .then((data) => {
          if (data.paths && data.paths.length) {
            const p = data.paths[0];
            banner.classList.remove("hidden");
            banner.textContent = `路径：${p.length} 跳`;
          } else {
            banner.classList.remove("hidden");
            banner.textContent = "无路径（>3 跳或不可达）";
          }
        })
        .catch((e) => {
          banner.classList.remove("hidden");
          banner.textContent = "路径错误：" + e.message;
        });
    });
  }

  function colorByType(t) {
    return {
      Document: "#a8d5ba",
      Section: "#cce5ff",
      Entity: "#ffe6a8",
      Topic: "#f5b6c5",
    }[t] || "#ddd";
  }

  document.getElementById("reset").addEventListener("click", () => {
    collapsed = new Set();
    if (lastData) renderGraph(lastData);
  });
})();
