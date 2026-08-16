/* GraphIt-KB 图谱页（15 §6.3 / Task 18 DoD D2；R-5 复核修复）
* 主题下钻（下拉加载 2 跳子图）/ 节点下钻（单击展开 1 跳邻域）/ 双击折叠 /
* Shift+拖拽框选（自实现橡皮筋）/ 实体间路径高亮（两次单击选源宿）。
*/
(function () {
  const sel = document.getElementById("topic");
  const btn = document.getElementById("btn");
  const canvas = document.getElementById("canvas");
  const banner = document.getElementById("truncated-banner");

  let graph = null;
  let lastData = null;
  let collapsed = new Set();
  let pathSrc = null; // 路径查询起点（实体 id；两次单击选源/宿）
  let highlighted = []; // 当前高亮元素 id（清除用）
  let lastRender = Promise.resolve(); // 最近一次 graph.render() 的 Promise（G6 v5 渲染为异步）
  // Shift+拖拽框选（自实现橡皮筋；G6 brush-select 的选态会被松开后的 click 清空，不可用）
  let brushStart = null; // 框选起点（相对 canvas 容器）
  let brushRectEl = null; // 橡皮筋矩形 DOM
  let brushSelected = []; // 当前框选选中的节点 id
  let skipClickClear = false; // 框选收尾的 canvas:click 不清选态

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
        pathSrc = null;
        highlighted = [];
        brushSelected = [];
        if (data.truncated) {
          banner.classList.remove("hidden");
          banner.textContent = `子图已截断到 ${data.nodes.length} 节点（cap=${data.max_nodes}）`;
        } else {
          banner.classList.add("hidden");
        }
        renderGraph(lastData);
      })
      .catch((e) => (canvas.innerHTML = "<p>错误：" + e.message + "</p>"));
  }

  function visibleData(data) {
    return {
      nodes: (data.nodes || []).filter((n) => !collapsed.has(n.id)),
      edges: (data.edges || []).filter((e) => !collapsed.has(e.src) && !collapsed.has(e.dst)),
    };
  }

  function renderGraph(data) {
    canvas.innerHTML = "";
    if (typeof G6 === "undefined") {
      canvas.innerHTML = "<p>G6 v5 未加载</p>";
      return;
    }
    // 重渲染前记住视口，渲染后恢复（下钻/路径高亮不应把用户视角重置）
    const prevZoom = graph ? graph.getZoom() : null;
    const prevPos = graph ? graph.getPosition() : null;
    const filtered = visibleData(data);
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
          // 密集层级上长标签会互相覆盖，截断保可读性（完整名见悬停/下钻后邻域）
          labelText: (d) => {
            const s = String(d.data.label ?? "");
            return s.length > 10 ? s.slice(0, 10) + "…" : s;
          },
          fill: (d) => colorByType(d.data.type),
          stroke: "#333",
          lineWidth: 1,
        },
        state: {
          selected: { stroke: "#1d7afc", lineWidth: 3 },
          highlight: { stroke: "#e63946", lineWidth: 4 },
        },
      },
      edge: {
        style: {
          labelText: (d) => d.data.rel,
          endArrow: true,
          stroke: "#888",
        },
        state: {
          selected: { stroke: "#1d7afc", lineWidth: 2 },
          highlight: { stroke: "#e63946", lineWidth: 3 },
        },
      },
      // 分层布局：Topic→Document→Section→Entity 是有向分层结构，用 dagre 自上而下铺开
      layout: { type: "antv-dagre", rankdir: "TB", nodesep: 30, ranksep: 60 },
      // 图幅宽于画布时不缩放（缩放会让标签不可读），仅居中，由用户自行缩放/平移
      autoFit: "center",
      // Shift 期间 drag-canvas 让位给自实现框选
      behaviors: [
        { type: "drag-canvas", enable: (e) => !e.shiftKey },
        "zoom-canvas",
        "drag-element",
      ],
    });
    lastRender = graph.render();
    // 供自动化测试/调试定位元素（playwright 等），不影响交互
    window.__kbGraph = graph;
    if (prevZoom !== null && prevPos) {
      lastRender.then(() => {
        if (!graph) return;
        graph.zoomTo(prevZoom, false);
        graph.translateTo(prevPos, false);
      });
    }

    // 双击节点 → 折叠/展开
    graph.on("node:dblclick", (e) => {
      const id = e.target.id;
      if (collapsed.has(id)) collapsed.delete(id);
      else collapsed.add(id);
      renderGraph(lastData);
    });

    // 单击节点 → 下钻 1 跳邻域；实体节点同时参与路径源/宿选择
    graph.on("node:click", (e) => {
      const id = e.target.id;
      drillDown(id).then(() => onPathPick(id));
    });

    // 点击空白 → 清除路径高亮、源点选择与框选选态（框选收尾的那次 click 除外）
    graph.on("canvas:click", () => {
      pathSrc = null;
      clearHighlight();
      if (skipClickClear) {
        skipClickClear = false;
        return;
      }
      clearBrushSelection();
    });
  }

  // ---- 节点下钻：/api/graph/neighbors 合并 1 跳邻域 --------------------

  function drillDown(id) {
    const node = (lastData.nodes || []).find((n) => n.id === id);
    if (!node) return Promise.resolve();
    return fetchJson(
      `/api/graph/neighbors?id=${encodeURIComponent(id)}&type=${encodeURIComponent(node.type)}`
    )
      .then((data) => {
        mergeGraph(data);
        renderGraph(lastData);
      })
      .catch((e) => {
        banner.classList.remove("hidden");
        banner.textContent = "邻域加载失败：" + e.message;
      });
  }

  function mergeGraph(data) {
    const nodeIds = new Set(lastData.nodes.map((n) => n.id));
    const edgeIds = new Set(lastData.edges.map((e) => e.src + "→" + e.dst));
    (data.nodes || []).forEach((n) => {
      if (!nodeIds.has(n.id)) {
        lastData.nodes.push(n); // 已存在节点按 id 去重
        nodeIds.add(n.id);
      }
    });
    (data.edges || []).forEach((e) => {
      const eid = e.src + "→" + e.dst;
      if (!edgeIds.has(eid) && nodeIds.has(e.src) && nodeIds.has(e.dst)) {
        lastData.edges.push(e);
        edgeIds.add(eid);
      }
    });
  }

  // ---- 路径高亮：两次单击实体选源/宿 -----------------------------------

  function onPathPick(id) {
    const node = (lastData.nodes || []).find((n) => n.id === id);
    if (!node || node.type !== "Entity") return; // 路径端点仅限实体（/api/graph/path 契约）
    if (pathSrc === null) {
      pathSrc = id;
      clearHighlight();
      setNodeState(id, "highlight");
      banner.classList.remove("hidden");
      banner.textContent = `路径起点：${node.label}（再单击另一实体查询路径）`;
      return;
    }
    if (pathSrc === id) {
      pathSrc = null; // 再点同一实体 → 取消选择
      clearHighlight();
      return;
    }
    const src = pathSrc;
    pathSrc = null;
    fetchJson(
      `/api/graph/path?src=${encodeURIComponent(src)}&dst=${encodeURIComponent(id)}&max_hops=3`
    )
      .then((data) => {
        clearHighlight();
        if (data.paths && data.paths.length) {
          const len = data.paths[0].length;
          const found = findVisiblePath(src, id, len);
          if (found) {
            found.forEach((eid) => setNodeState(eid, "highlight"));
            banner.textContent = `路径：${len} 跳（已高亮；点空白清除）`;
          } else {
            setNodeState(src, "highlight");
            setNodeState(id, "highlight");
            banner.textContent = `路径：${len} 跳（经未展开节点，仅高亮端点）`;
          }
        } else {
          banner.textContent = "无路径（>3 跳或不可达）";
        }
        banner.classList.remove("hidden");
      })
      .catch((e) => {
        banner.classList.remove("hidden");
        banner.textContent = "路径错误：" + e.message;
      });
  }

  // 当前可见图内 BFS 最短路径（无向）；长度与服务端一致才采纳，返回节点+边 id 列表
  function findVisiblePath(src, dst, serverLen) {
    const { nodes, edges } = visibleData(lastData);
    if (!nodes.some((n) => n.id === src) || !nodes.some((n) => n.id === dst)) return null;
    const adj = new Map();
    edges.forEach((e) => {
      const eid = e.src + "→" + e.dst;
      (adj.get(e.src) || adj.set(e.src, []).get(e.src)).push([e.dst, eid]);
      (adj.get(e.dst) || adj.set(e.dst, []).get(e.dst)).push([e.src, eid]);
    });
    const prev = new Map([[src, null]]);
    const queue = [src];
    while (queue.length) {
      const cur = queue.shift();
      if (cur === dst) break;
      (adj.get(cur) || []).forEach(([next, eid]) => {
        if (!prev.has(next)) {
          prev.set(next, [cur, eid]);
          queue.push(next);
        }
      });
    }
    if (!prev.has(dst)) return null;
    const out = [dst];
    let cur = dst;
    let hops = 0;
    while (cur !== src) {
      const [p, eid] = prev.get(cur);
      out.push(eid, p);
      cur = p;
      hops += 1;
    }
    return hops === serverLen ? out : null;
  }

  function setNodeState(id, state) {
    if (!graph) return;
    // G6 v5 render 为异步，元素未上屏时 setElementState 会抛 TypeError；等渲染完成后再设置
    Promise.resolve(lastRender).then(() => {
      if (!graph) return;
      try {
        graph.setElementState({ [id]: [state] });
        if (!highlighted.includes(id)) highlighted.push(id);
      } catch (_e) {
        /* 元素不在当前渲染树（如被折叠）时忽略 */
      }
    });
  }

  function clearHighlight() {
    if (graph && highlighted.length) {
      const reset = {};
      highlighted.forEach((id) => {
        reset[id] = [];
      });
      // 同 setNodeState：等渲染完成后再重置状态
      Promise.resolve(lastRender).then(() => {
        if (!graph) return;
        try {
          graph.setElementState(reset);
        } catch (_e) {
          /* 图已重建时忽略 */
        }
      });
    }
    highlighted = [];
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
    pathSrc = null;
    highlighted = [];
    brushSelected = [];
    if (lastData) renderGraph(lastData);
  });

  function clearBrushSelection() {
    if (!graph || !brushSelected.length) {
      brushSelected = [];
      return;
    }
    const reset = {};
    brushSelected.forEach((id) => {
      reset[id] = [];
    });
    try {
      graph.setElementState(reset);
    } catch (_e) {
      /* 图已重建时忽略 */
    }
    brushSelected = [];
  }

  // ---- Shift+拖拽框选：自实现橡皮筋 ----------------------------------
  canvas.style.position = "relative";

  canvas.addEventListener("pointerdown", (e) => {
    if (!graph || !e.shiftKey) return;
    const r = canvas.getBoundingClientRect();
    brushStart = { x: e.clientX - r.left, y: e.clientY - r.top };
    brushRectEl = document.createElement("div");
    brushRectEl.style.cssText =
      "position:absolute;border:1px solid #1677ff;background:rgba(22,119,255,.1);pointer-events:none;z-index:2;";
    canvas.appendChild(brushRectEl);
  });

  window.addEventListener("pointermove", (e) => {
    if (!brushStart || !brushRectEl) return;
    const r = canvas.getBoundingClientRect();
    const cx = e.clientX - r.left;
    const cy = e.clientY - r.top;
    brushRectEl.style.left = Math.min(cx, brushStart.x) + "px";
    brushRectEl.style.top = Math.min(cy, brushStart.y) + "px";
    brushRectEl.style.width = Math.abs(cx - brushStart.x) + "px";
    brushRectEl.style.height = Math.abs(cy - brushStart.y) + "px";
  });

  window.addEventListener("pointerup", (e) => {
    if (!brushStart) return;
    const r = canvas.getBoundingClientRect();
    const box = {
      x1: Math.min(e.clientX, brushStart.x + r.left),
      y1: Math.min(e.clientY, brushStart.y + r.top),
      x2: Math.max(e.clientX, brushStart.x + r.left),
      y2: Math.max(e.clientY, brushStart.y + r.top),
    };
    brushStart = null;
    if (brushRectEl) {
      brushRectEl.remove();
      brushRectEl = null;
    }
    if (!graph) return;
    // 命中检测：节点中心（client 坐标）落入框内
    const ids = [];
    graph.getNodeData().forEach((n) => {
      const [cx, cy] = graph.getClientByCanvas(graph.getElementPosition(n.id));
      if (cx >= box.x1 && cx <= box.x2 && cy >= box.y1 && cy <= box.y2) ids.push(n.id);
    });
    const update = {};
    brushSelected.forEach((id) => {
      update[id] = [];
    });
    ids.forEach((id) => {
      update[id] = ["selected"];
    });
    try {
      graph.setElementState(update);
    } catch (_e) {
      /* 元素已消失时忽略 */
    }
    brushSelected = ids;
    skipClickClear = true; // 紧随的 canvas:click 是框选收尾，不清选态
  });
})();