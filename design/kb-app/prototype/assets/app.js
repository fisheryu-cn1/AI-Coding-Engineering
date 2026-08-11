/* GraphIt-KB 原型 —— 前端逻辑（无框架，数据来自 assets/data.js） */
(function () {
  "use strict";

  var ROOT_PREFIX = "../../../"; // prototype/ → 项目根，用于“原文”链接
  var page = document.body.dataset.page;

  /* ---------- 工具 ---------- */
  function $(sel, root) { return (root || document).querySelector(sel); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function topicOf(id) { return KB.topics.find(function (t) { return t.id === id; }); }
  function topicColor(id) { var t = topicOf(id); return t ? t.color : "#b6bdc6"; }
  function docOf(id) { return KB.docs.find(function (d) { return d.id === id; }); }
  function entOf(id) { return KB.entities.find(function (e) { return e.id === id; }); }
  function secId(docId, secPath) { return "s-" + docId + "-" + secPath.replace("§", "").replace(/\./g, "-"); }
  function secNum(secPath) { return secPath.replace("§", ""); }
  function chip(t, extraCls) {
    return '<span class="chip chip-static ' + (extraCls || "") + '"><i class="dot" style="background:' + t.color + '"></i>' + esc(t.name) + "</span>";
  }
  function param(name) { return new URLSearchParams(location.search).get(name); }
  function hashParam(name) {
    var m = location.hash.match(new RegExp(name + "=([^&]+)"));
    return m ? decodeURIComponent(m[1]) : null;
  }

  /* 实体 → 提及它的章节列表 [{doc, sec}] */
  var entMentions = {};
  KB.docs.forEach(function (d) {
    d.sections.forEach(function (s) {
      (s.entities || []).forEach(function (e) {
        (entMentions[e] = entMentions[e] || []).push({ doc: d, sec: s });
      });
    });
  });
  /* 实体的主题色：取首个提及文档的主题 */
  function entColor(eid) {
    var ms = entMentions[eid];
    return ms && ms.length ? ms[0].doc.topic ? topicColor(ms[0].doc.topic) : "#b6bdc6" : "#b6bdc6";
  }

  /* ---------- 顶部导航 ---------- */
  function renderNav() {
    var links = [
      ["index.html", "检索", "search"],
      ["graph.html", "图谱", "graph"],
      ["inbox.html", "Inbox", "inbox"],
      ["status.html", "状态", "status"]
    ];
    var html = '<a class="logo" href="index.html">GraphIt-KB <span>本地知识库</span></a><nav class="navlinks">';
    links.forEach(function (l) {
      html += '<a href="' + l[0] + '"' + (page === l[2] ? ' class="active"' : "") + ">" + l[1] + "</a>";
    });
    html += '</nav><form class="globalsearch" action="index.html" method="get">' +
      '<input type="search" name="q" placeholder="全局搜索：概念 / 论文 / 章节…" value="' + esc(page === "search" ? (param("q") || "") : "") + '"></form>';
    $("header").innerHTML = html;
  }

  /* ================================================================
   * 检索页
   * ================================================================ */
  function initSearch() {
    var state = {
      q: param("q") || "",
      mode: "hybrid",
      topics: new Set(),
      ents: []
    };

    var modeNames = { hybrid: "混合", vector: "向量", graph: "图", topic: "主题全局" };

    /* 控件区 */
    var ctrl = $("#controls");
    var modeHtml = '<div class="moderow"><span class="muted small">模式</span>';
    Object.keys(modeNames).forEach(function (m) {
      modeHtml += '<label class="radio"><input type="radio" name="mode" value="' + m + '"' +
        (m === state.mode ? " checked" : "") + ">" + modeNames[m] + "</label>";
    });
    modeHtml += "</div>";
    var topicHtml = '<div class="topicrow"><span class="muted small" style="padding-top:2px">主题</span>';
    KB.topics.forEach(function (t) {
      topicHtml += '<span class="chip" data-topic="' + t.id + '"><i class="dot" style="background:' + t.color + '"></i>' + esc(t.name) + "</span>";
    });
    topicHtml += "</div>";
    ctrl.innerHTML = modeHtml + topicHtml;

    ctrl.addEventListener("change", function (ev) {
      if (ev.target.name === "mode") { state.mode = ev.target.value; render(); }
    });
    ctrl.addEventListener("click", function (ev) {
      var c = ev.target.closest("[data-topic]");
      if (!c) return;
      var id = c.dataset.topic;
      if (state.topics.has(id)) { state.topics.delete(id); c.classList.remove("on"); c.style.background = ""; }
      else { state.topics.add(id); c.classList.add("on"); c.style.background = topicColor(id) + "33"; }
      render();
    });

    var input = $("#q");
    input.value = state.q;
    $("#search-form").addEventListener("submit", function (ev) {
      ev.preventDefault();
      state.q = input.value.trim();
      history.replaceState(null, "", "index.html?q=" + encodeURIComponent(state.q));
      render();
    });

    /* 检索实现 */
    function search() {
      var toks = state.q.toLowerCase().split(/\s+/).filter(Boolean);
      var hits = [];
      KB.docs.forEach(function (d) {
        if (state.topics.size && !state.topics.has(d.topic)) return;
        var dTitle = d.title.toLowerCase(), dSum = d.summary.toLowerCase();
        d.sections.forEach(function (s) {
          if (state.ents.length) {
            var ok = state.ents.every(function (e) { return (s.entities || []).indexOf(e) >= 0; });
            if (!ok) return;
          }
          var score = 0;
          if (!toks.length) score = 1;
          toks.forEach(function (tk) {
            var w = { hybrid: 1, vector: 1, graph: 1 }[state.mode] || 1;
            if (dTitle.indexOf(tk) >= 0) score += 4 * w;
            if (s.title.toLowerCase().indexOf(tk) >= 0) score += 3 * w;
            if (dSum.indexOf(tk) >= 0) score += (state.mode === "vector" ? 3 : 2);
            if (s.summary.toLowerCase().indexOf(tk) >= 0) score += (state.mode === "vector" ? 3 : 2);
            if (s.text.toLowerCase().indexOf(tk) >= 0) score += 1;
            (s.entities || []).forEach(function (e) {
              if (entOf(e).name.toLowerCase().indexOf(tk) >= 0) score += state.mode === "graph" ? 5 : 3;
            });
          });
          if (score > 0) hits.push({ doc: d, sec: s, raw: score });
        });
      });
      hits.sort(function (a, b) { return b.raw - a.raw; });
      var max = hits.length ? hits[0].raw : 1;
      hits.forEach(function (h) { h.score = state.q ? Math.min(0.99, 0.45 + 0.54 * h.raw / max) : null; });
      return hits;
    }

    function renderEntFilters() {
      var box = $("#ent-filters");
      if (!state.ents.length) { box.innerHTML = ""; box.style.display = "none"; return; }
      box.style.display = "flex";
      box.innerHTML = '<span class="muted small">收窄条件：</span>' + state.ents.map(function (e) {
        return '<span class="chip on" style="background:#eef2f8">' + esc(entOf(e).name) + '<span class="x" data-x="' + e + '">✕</span></span>';
      }).join("");
    }
    $("#ent-filters").addEventListener("click", function (ev) {
      var x = ev.target.closest("[data-x]");
      if (!x) return;
      state.ents = state.ents.filter(function (e) { return e !== x.dataset.x; });
      render();
    });

    function renderCloud(hits) {
      var freq = {};
      hits.forEach(function (h) { (h.sec.entities || []).forEach(function (e) { freq[e] = (freq[e] || 0) + 1; }); });
      var list = Object.keys(freq).sort(function (a, b) { return freq[b] - freq[a]; });
      var box = $("#cloud");
      if (!list.length) { box.innerHTML = '<span class="muted small">当前结果无关联实体</span>'; return; }
      box.innerHTML = list.map(function (e) {
        var size = Math.min(24, 12 + freq[e] * 2);
        var on = state.ents.indexOf(e) >= 0 ? " on" : "";
        return '<span class="w' + on + '" data-e="' + e + '" style="font-size:' + size + 'px" title="' + freq[e] + ' 个章节提及">' + esc(entOf(e).name) + "</span>";
      }).join("");
    }
    $("#cloud").addEventListener("click", function (ev) {
      var w = ev.target.closest("[data-e]");
      if (!w) return;
      var e = w.dataset.e;
      if (state.ents.indexOf(e) >= 0) state.ents = state.ents.filter(function (x) { return x !== e; });
      else state.ents.push(e);
      render();
    });

    function renderTopicGlobal() {
      var counts = {};
      KB.docs.forEach(function (d) { counts[d.topic] = (counts[d.topic] || 0) + 1; });
      var html = '<div class="topic-grid">';
      KB.topics.forEach(function (t) {
        var n = counts[t.id] || 0;
        html += '<div class="topic-card" style="border-left-color:' + t.color + '" data-t="' + t.id + '">' +
          '<div class="t-name">' + esc(t.name) + '</div><div class="t-desc">' + esc(t.desc) + '</div>' +
          '<div class="t-count">' + n + ' 篇文档 · 点击检索该主题</div></div>';
      });
      $("#results").innerHTML = html + "</div>";
      $("#cloud").innerHTML = '<span class="muted small">主题全局模式：纵览库中各主题规模，点击主题卡片进入检索。</span>';
      $("#results").addEventListener("click", function handler(ev) {
        var c = ev.target.closest("[data-t]");
        if (!c) return;
        $("#results").removeEventListener("click", handler);
        state.topics = new Set([c.dataset.t]);
        state.mode = "hybrid";
        ctrl.querySelectorAll("input[name=mode]").forEach(function (r) { r.checked = r.value === "hybrid"; });
        ctrl.querySelectorAll("[data-topic]").forEach(function (ch) {
          var on = ch.dataset.topic === c.dataset.t;
          ch.classList.toggle("on", on);
          ch.style.background = on ? topicColor(ch.dataset.topic) + "33" : "";
        });
        render();
      });
    }

    function render() {
      renderEntFilters();
      if (state.mode === "topic") { renderTopicGlobal(); return; }
      var hits = search();
      renderCloud(hits);
      var box = $("#results");
      if (!hits.length) {
        box.innerHTML = '<div class="empty-box">没有找到与「' + esc(state.q) + '」相关的内容' +
          '<div class="suggest">建议：切换到「向量」模式放宽匹配；取消部分主题过滤；' +
          '或试试库中已有的概念，如 “GraphRAG”、“Context Rot”、“知识图谱”、“SWE-bench”。</div></div>';
        return;
      }
      var head = '<div class="muted small" style="margin-bottom:12px">共 ' + hits.length + ' 个章节命中' +
        (state.q ? "（模式：" + modeNames[state.mode] + "）" : "（输入关键词开始检索）") + "</div>";
      box.innerHTML = head + hits.map(function (h) {
        var t = topicOf(h.doc.topic);
        return '<a class="result-card" href="document.html?doc=' + h.doc.id + "#sec=" + encodeURIComponent(secNum(h.sec.path)) + '">' +
          '<div class="rc-head"><span class="rc-title">' + esc(h.doc.title) + '</span>' +
          '<span class="rc-sec">' + esc(h.sec.path) + " " + esc(h.sec.title) + "</span>" + chip(t) + "</div>" +
          '<div class="rc-summary">' + esc(h.sec.summary) + "</div>" +
          '<div class="rc-foot">' +
          (h.score != null ? '<span class="scorebar"><i style="width:' + Math.round(h.score * 100) + '%"></i></span><span class="score-num">' + h.score.toFixed(2) + "</span>" : "") +
          '<span class="rc-raw mono" data-raw="' + ROOT_PREFIX + esc(h.doc.path) + '">原文 ↗</span>' +
          "</div></a>";
      }).join("");
    }
    /* “原文”按钮：直接打开项目内真实文件 */
    $("#results").addEventListener("click", function (ev) {
      var raw = ev.target.closest("[data-raw]");
      if (raw) {
        ev.preventDefault(); ev.stopPropagation();
        window.open(raw.dataset.raw, "_blank");
      }
    });

    render();
  }

  /* ================================================================
   * 文档页
   * ================================================================ */
  function initDoc() {
    var d = docOf(param("doc")) || KB.docs[0];
    var t = topicOf(d.topic);
    var curSec = hashParam("sec");

    /* 头部与摘要 */
    $("#doc-title").textContent = d.title;
    $("#doc-meta").innerHTML =
      '<span class="chip chip-static">' + esc(d.type) + "</span>" + chip(t) +
      "<span>" + esc(d.authors) + "</span>" +
      (d.arxivId ? '<span class="mono">arXiv:' + d.arxivId + (d.version ? " " + d.version : "") + "</span>" : "") +
      '<a class="mono" href="' + ROOT_PREFIX + esc(d.path) + '" target="_blank">原文 ↗</a>';
    $("#doc-summary").innerHTML = '<span class="lbl">文档摘要（四段式简化）</span>' + esc(d.summary);

    /* 章节树（支持 §x.y 二级折叠） */
    var toc = $("#toc");
    var tocHtml = '<div class="toc-doc">' + esc(d.title.length > 22 ? d.title.slice(0, 22) + "…" : d.title) + "</div>";
    var groups = [];
    d.sections.forEach(function (s) {
      var top = secNum(s.path).split(".")[0];
      if (secNum(s.path).indexOf(".") < 0) groups.push({ sec: s, subs: [] });
      else {
        var g = groups[groups.length - 1];
        if (g && secNum(g.sec.path).split(".")[0] === top) g.subs.push(s);
        else groups.push({ sec: s, subs: [] });
      }
    });
    groups.forEach(function (g) {
      var id = secId(d.id, g.sec.path);
      var tog = g.subs.length ? '<span class="toc-toggle" data-tog="' + id + '">▾</span>' : "";
      tocHtml += '<a class="toc-item" data-sec="' + id + '" href="#sec=' + encodeURIComponent(secNum(g.sec.path)) + '">' + tog + esc(g.sec.path) + " " + esc(g.sec.title) + "</a>";
      g.subs.forEach(function (s) {
        tocHtml += '<a class="toc-item lv2" data-sec="' + secId(d.id, s.path) + '" data-parent="' + id + '" href="#sec=' + encodeURIComponent(secNum(s.path)) + '">' + esc(s.path) + " " + esc(s.title) + "</a>";
      });
    });
    toc.innerHTML = tocHtml;
    toc.addEventListener("click", function (ev) {
      var tg = ev.target.closest("[data-tog]");
      if (tg) {
        ev.preventDefault();
        var pid = tg.dataset.tog;
        var hide = tg.textContent === "▾";
        tg.textContent = hide ? "▸" : "▾";
        toc.querySelectorAll('[data-parent="' + pid + '"]').forEach(function (n) { n.style.display = hide ? "none" : ""; });
        return;
      }
      var item = ev.target.closest("[data-sec]");
      if (item) setCurrent(item.dataset.sec, true);
    });

    /* 章节卡片 */
    var main = $("#sections");
    main.innerHTML = d.sections.map(function (s) {
      var id = secId(d.id, s.path);
      var chips = (s.entities || []).map(function (e) {
        return '<span class="chip chip-static"><i class="dot" style="background:' + entColor(e) + '"></i>' + esc(entOf(e).name) + "</span>";
      }).join("");
      return '<div class="sec-card" id="' + id + '">' +
        '<div class="sec-head"><span class="sec-path">' + esc(s.path) + '</span><span class="sec-title">' + esc(s.title) + "</span>" +
        '<a class="sec-anchor" href="#sec=' + encodeURIComponent(secNum(s.path)) + '" title="复制本节锚点">锚点</a></div>' +
        '<div class="sec-summary">' + esc(s.summary) + "</div>" +
        '<div class="sec-text" style="display:none">' + esc(s.text) +
        (chips ? '<div class="sec-entities">' + chips + "</div>" : "") + "</div>" +
        '<button class="sec-toggle">展开原文</button></div>';
    }).join("");
    main.addEventListener("click", function (ev) {
      if (ev.target.classList.contains("sec-toggle")) {
        var txt = ev.target.parentNode.querySelector(".sec-text");
        var open = txt.style.display === "none";
        txt.style.display = open ? "" : "none";
        ev.target.textContent = open ? "收起原文" : "展开原文";
      }
      if (ev.target.classList.contains("sec-anchor")) {
        ev.preventDefault();
        var href = ev.target.getAttribute("href");
        history.replaceState(null, "", href);
        setCurrent(ev.target.closest(".sec-card").id, false);
      }
    });

    function setCurrent(id, scroll) {
      toc.querySelectorAll(".toc-item").forEach(function (n) { n.classList.toggle("cur", n.dataset.sec === id); });
      main.querySelectorAll(".sec-card").forEach(function (n) { n.classList.toggle("cur", n.id === id); });
      var card = document.getElementById(id);
      if (card && scroll) card.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    /* URL hash 定位：自动展开并高亮对应章节（从图谱页跳入的场景） */
    if (curSec) {
      var target = d.sections.find(function (s) { return secNum(s.path) === curSec; });
      if (target) {
        var id = secId(d.id, target.path);
        var card = document.getElementById(id);
        card.querySelector(".sec-text").style.display = "";
        card.querySelector(".sec-toggle").textContent = "收起原文";
        setCurrent(id, false);
        setTimeout(function () { card.scrollIntoView({ behavior: "smooth", block: "start" }); }, 60);
      }
    } else if (d.sections.length) {
      setCurrent(secId(d.id, d.sections[0].path), false);
    }

    /* 关联侧栏 */
    var entSet = {};
    d.sections.forEach(function (s) { (s.entities || []).forEach(function (e) { entSet[e] = true; }); });
    var rel = {};
    KB.docs.forEach(function (o) {
      if (o.id === d.id) return;
      var shared = [];
      o.sections.forEach(function (s) {
        (s.entities || []).forEach(function (e) { if (entSet[e] && shared.indexOf(e) < 0) shared.push(e); });
      });
      if (shared.length) rel[o.id] = { doc: o, why: "共享实体: " + shared.map(function (e) { return entOf(e).name; }).join("、") };
    });
    KB.docLinks.forEach(function (l) {
      if (l.from === d.id) rel[l.to] = { doc: docOf(l.to), why: l.type + " · " + l.note };
      if (l.to === d.id) rel[l.from] = { doc: docOf(l.from), why: l.type + "（被引用）· " + l.note };
    });
    var relList = Object.keys(rel).map(function (k) { return rel[k]; })
      .sort(function (a, b) { return b.why.length - a.why.length; }).slice(0, 6);
    $("#rel-list").innerHTML = relList.length ? relList.map(function (r) {
      return '<a class="rel-item" href="document.html?doc=' + r.doc.id + '"><div class="r-title">' + esc(r.doc.title) +
        '</div><div class="r-why">' + esc(r.why) + "</div></a>";
    }).join("") : '<div class="muted small">暂无关联资料</div>';

    $("#ent-chips").innerHTML = Object.keys(entSet).map(function (e) {
      return '<a class="chip" href="index.html?q=' + encodeURIComponent(entOf(e).name) + '"><i class="dot" style="background:' + entColor(e) + '"></i>' + esc(entOf(e).name) + "</a>";
    }).join("") || '<div class="muted small">本节未抽取实体</div>';

    var ver = '<div class="ver-row"><b>类型</b>　' + esc(d.type) + "</div>" +
      '<div class="ver-row"><b>主题</b>　' + esc(d.topic) + "</div>" +
      (d.arxivId ? '<div class="ver-row"><b>版本</b>　arXiv:' + esc(d.arxivId) + " " + esc(d.version || "") + "</div>" : '<div class="ver-row"><b>版本</b>　—</div>');
    KB.docLinks.forEach(function (l) {
      if (l.from === d.id || l.to === d.id) {
        var other = docOf(l.from === d.id ? l.to : l.from);
        ver += '<div class="ver-row"><b>' + l.type + '</b>　<a href="document.html?doc=' + other.id + '">' + esc(other.title) + "</a></div>";
      }
    });
    ver += '<a class="btn" style="margin-top:8px" href="' + ROOT_PREFIX + esc(d.path) + '" target="_blank">打开原文文件</a>';
    $("#ver-info").innerHTML = ver;
  }

  /* ================================================================
   * 图谱页
   * ================================================================ */
  function initGraph() {
    var docsWithTopic = {};
    KB.docs.forEach(function (d) { (docsWithTopic[d.topic] = docsWithTopic[d.topic] || []).push(d); });
    var activeTopics = Object.keys(docsWithTopic);

    /* ---- 构建全图元素 ---- */
    var allNodes = {}, allEdges = [];
    function addNode(id, data) { allNodes[id] = { group: "nodes", data: Object.assign({ id: id }, data) }; }
    function addEdge(src, tgt, label) {
      allEdges.push({ group: "edges", data: { id: src + "->" + tgt + ":" + label, source: src, target: tgt, label: label } });
    }
    activeTopics.forEach(function (tid) {
      addNode("t:" + tid, { kind: "topic", name: tid, color: topicColor(tid), desc: topicOf(tid).desc });
    });
    KB.docs.forEach(function (d) {
      addNode("d:" + d.id, { kind: "doc", name: d.title.length > 18 ? d.title.slice(0, 18) + "…" : d.title, full: d.title, color: topicColor(d.topic), docId: d.id, desc: d.summary });
      addEdge("t:" + d.topic, "d:" + d.id, "ABOUT_TOPIC");
      d.sections.forEach(function (s) {
        var sid = "s:" + secId(d.id, s.path);
        addNode(sid, { kind: "section", name: s.path + " " + (s.title.length > 10 ? s.title.slice(0, 10) + "…" : s.title), color: topicColor(d.topic), docId: d.id, sec: secNum(s.path), desc: s.summary });
        addEdge("d:" + d.id, sid, "CONTAINS_SECTION");
        (s.entities || []).forEach(function (e) { addEdge(sid, "e:" + e, "MENTIONS"); });
      });
    });
    KB.entities.forEach(function (e) {
      addNode("e:" + e.id, { kind: "entity", name: e.name, color: entColor(e.id), etype: e.type, desc: e.desc });
    });
    KB.relates.forEach(function (r) { addEdge("e:" + r.from, "e:" + r.to, "RELATES_TO:" + r.kind); });
    KB.docLinks.forEach(function (l) { addEdge("d:" + l.from, "d:" + l.to, l.type); });

    /* ---- 可见性状态 ---- */
    var state = {
      topics: new Set(["ContextEngineering"]),
      hops: 2,
      etypes: new Set(["Concept", "Method", "Tool", "Dataset"]),
      expandedDocs: new Set(),
      reveal: new Set() /* 路径查找临时揭示的节点 */
    };
    var pathMode = false, pathSel = [], pathEdges = [], lastPath = null;

    function adjacency() {
      var adj = {};
      allEdges.forEach(function (e) {
        var s = e.data.source, t = e.data.target;
        (adj[s] = adj[s] || []).push({ n: t, label: e.data.label });
        (adj[t] = adj[t] || []).push({ n: s, label: e.data.label });
      });
      return adj;
    }
    var ADJ = adjacency();

    function visibleSet() {
      var vis = new Set();
      state.topics.forEach(function (t) { if (allNodes["t:" + t]) vis.add("t:" + t); });
      var frontier = Array.from(vis);
      /* BFS：跳数 1=文档，2=章节，3=实体 */
      for (var hop = 1; hop <= state.hops; hop++) {
        var next = [];
        frontier.forEach(function (nid) {
          (ADJ[nid] || []).forEach(function (ed) {
            var nd = allNodes[ed.n];
            if (!nd || vis.has(ed.n)) return;
            var k = nd.data.kind;
            var depthOf = { topic: 0, doc: 1, section: 2, entity: 3 }[k];
            if (depthOf !== hop) return;
            if (k === "entity" && !state.etypes.has(nd.data.etype)) return;
            vis.add(ed.n); next.push(ed.n);
          });
        });
        frontier = next;
      }
      /* 手动下钻的文档：其章节与实体总是可见 */
      state.expandedDocs.forEach(function (docId) {
        var dn = "d:" + docId;
        if (!vis.has(dn)) return;
        (ADJ[dn] || []).forEach(function (ed) {
          if (allNodes[ed.n].data.kind !== "section") return;
          vis.add(ed.n);
          (ADJ[ed.n] || []).forEach(function (e2) {
            var nd = allNodes[e2.n];
            if (nd.data.kind === "entity" && state.etypes.has(nd.data.etype)) vis.add(e2.n);
          });
        });
      });
      state.reveal.forEach(function (n) { vis.add(n); });
      return vis;
    }

    /* ---- Cytoscape ---- */
    var cy = cytoscape({
      container: $("#cy"),
      elements: [],
      wheelSensitivity: 0.2,
      style: [
        { selector: "node", style: {
          "label": "data(name)", "font-size": 9, "color": "#57606a",
          "text-valign": "bottom", "text-margin-y": 4,
          "background-color": "data(color)", "border-width": 1, "border-color": "#ffffff",
          "text-wrap": "wrap", "text-max-width": "110px"
        } },
        { selector: 'node[kind="topic"]', style: { width: 64, height: 64, "font-size": 11, "font-weight": "bold", "color": "#24292f" } },
        { selector: 'node[kind="doc"]', style: { shape: "ellipse", width: 30, height: 30 } },
        { selector: 'node[kind="section"]', style: { shape: "rectangle", width: 18, height: 18 } },
        { selector: 'node[kind="entity"]', style: { shape: "diamond", width: 20, height: 20 } },
        { selector: "edge", style: {
          width: 1, "line-color": "#d4d4d4", "curve-style": "bezier",
          "target-arrow-shape": "triangle", "arrow-scale": 0.7, "target-arrow-color": "#d4d4d4",
          "label": "", "font-size": 8, "color": "#8b949e",
          "text-background-color": "#ffffff", "text-background-opacity": 0.85, "text-background-padding": "2px"
        } },
        { selector: "edge.showlabel", style: { "label": "data(label)" } },
        { selector: ".hidden", style: { "display": "none" } },
        { selector: "node.sel", style: { "border-width": 3, "border-color": "#4a6fa5" } },
        { selector: ".path", style: { "line-color": "#4a6fa5", "target-arrow-color": "#4a6fa5", width: 3, "label": "data(label)" } },
        { selector: "node.path", style: { "border-width": 3, "border-color": "#4a6fa5" } }
      ]
    });

    var firstRender = true;
    function refresh(runLayout) {
      var vis = visibleSet();
      if (firstRender) {
        var eles = [];
        Object.keys(allNodes).forEach(function (id) { eles.push(allNodes[id]); });
        allEdges.forEach(function (e) { eles.push(e); });
        cy.add(eles);
        firstRender = false;
      }
      cy.nodes().forEach(function (n) { n.toggleClass("hidden", !vis.has(n.id())); });
      cy.edges().forEach(function (e) {
        e.toggleClass("hidden", !(vis.has(e.data("source")) && vis.has(e.data("target"))));
      });
      applyPathClasses();
      if (runLayout !== false) {
        cy.elements(":visible").layout({
          name: "cose", animate: false, padding: 50,
          nodeRepulsion: 26000, idealEdgeLength: 110,
          edgeElasticity: 120, gravity: 0.4, numIter: 1500
        }).run();
        cy.fit(undefined, 50);
      }
    }

    /* 路径高亮在 refresh 后重放（refresh 只切换可见性类，不移除元素） */
    function applyPathClasses() {
      if (!lastPath) return;
      lastPath.forEach(function (step) { cy.getElementById(step.node).addClass("path"); });
      for (var i = 1; i < lastPath.length; i++) {
        (function (a, b, label) {
          cy.edges().forEach(function (e) {
            var s = e.data("source"), t = e.data("target");
            if (((s === a && t === b) || (t === a && s === b)) && e.data("label") === label) e.addClass("path");
          });
        })(lastPath[i - 1].node, lastPath[i].node, lastPath[i].edge);
      }
    }

    /* ---- 信息面板 ---- */
    function panel(html) { $("#g-info").innerHTML = html; }
    function showNode(nd) {
      var data = nd.data(), html = "";
      var kindNames = { topic: "主题", doc: "文档", section: "章节", entity: "实体" };
      html += "<h3>" + esc(data.full || data.name) + "</h3>";
      html += '<div class="g-type">' + kindNames[data.kind] +
        (data.etype ? " · " + esc(data.etype) : "") + "</div>";
      html += '<div class="g-desc">' + esc(data.desc || "") + "</div>";
      if (data.kind === "doc") {
        html += '<a class="btn btn-primary" href="document.html?doc=' + data.docId + '">在文档页打开</a>';
      } else if (data.kind === "section") {
        html += '<a class="btn btn-primary" href="document.html?doc=' + data.docId + "#sec=" + encodeURIComponent(data.sec) + '">在文档页打开</a>';
      } else if (data.kind === "entity") {
        var ms = entMentions[nd.id().slice(2)];
        if (ms && ms.length) html += '<a class="btn btn-primary" href="document.html?doc=' + ms[0].doc.id + "#sec=" + encodeURIComponent(secNum(ms[0].sec.path)) + '">在文档页打开</a>';
      } else if (data.kind === "topic") {
        html += '<a class="btn btn-primary" href="index.html">在检索页浏览</a>';
      }
      html += '<a class="btn" href="index.html?q=' + encodeURIComponent(data.full || data.name) + '">以此为起点检索</a>';
      panel(html);
    }

    /* ---- 最短路径（BFS 于全图） ---- */
    function findPath(a, b) {
      if (a === b) return null;
      var prev = {}, prevEdge = {}, q = [a], seen = {};
      seen[a] = true;
      while (q.length) {
        var cur = q.shift();
        if (cur === b) break;
        (ADJ[cur] || []).forEach(function (ed) {
          if (!seen[ed.n]) { seen[ed.n] = true; prev[ed.n] = cur; prevEdge[ed.n] = ed.label; q.push(ed.n); }
        });
      }
      if (!seen[b]) return null;
      var path = [], cur = b;
      while (cur !== a) { path.unshift({ node: cur, edge: prevEdge[cur] }); cur = prev[cur]; }
      path.unshift({ node: a, edge: null });
      return path;
    }

    function clearPath() {
      lastPath = null;
      cy.elements().removeClass("path");
      state.reveal.clear();
      pathSel = [];
      pathEdges = [];
      $("#path-out").innerHTML = "";
    }

    cy.on("tap", "node", function (ev) {
      var nd = ev.target;
      if (pathMode) {
        nd.addClass("sel");
        pathSel.push(nd.id());
        if (pathSel.length === 2) {
          var p = findPath(pathSel[0], pathSel[1]);
          cy.nodes().removeClass("sel");
          if (!p) {
            $("#path-out").innerHTML = '<div class="muted">两个节点之间没有连通路径。</div>';
          } else {
            lastPath = p;
            p.forEach(function (step) { state.reveal.add(step.node); });
            refresh(false);
            $("#path-out").innerHTML = '<div class="path-list"><b>最短路径（' + (p.length - 1) + ' 跳）</b><br>' +
              p.map(function (step, i) {
                var nm = allNodes[step.node].data.name;
                return (i === 0 ? esc(nm) : '<br><span class="edge-tag">' + esc(step.edge) + "</span> → " + esc(nm));
              }).join("") + "</div>";
          }
          pathMode = false; pathSel = [];
          $("#path-btn").textContent = "查找路径";
          $("#path-hint").textContent = "";
        } else {
          $("#path-hint").textContent = "已选第 1 个节点，请点击第 2 个节点。";
        }
        return;
      }
      showNode(nd);
    });

    cy.on("dblclick", "node", function (ev) {
      var nd = ev.target, data = nd.data();
      if (data.kind === "topic") {
        state.topics.add(nd.id().slice(2));
        syncTopicChips();
        refresh();
      } else if (data.kind === "doc") {
        state.expandedDocs.add(data.docId);
        refresh();
      }
    });
    cy.on("cxttap", "node", function (ev) {
      var nd = ev.target, data = nd.data();
      clearPath();
      if (data.kind === "doc") { state.expandedDocs.delete(data.docId); refresh(); }
      else if (data.kind === "topic" && state.topics.size > 1) {
        state.topics.delete(nd.id().slice(2)); syncTopicChips(); refresh();
      }
    });
    cy.on("mouseover", "edge", function (ev) { ev.target.addClass("showlabel"); });
    cy.on("mouseout", "edge", function (ev) { ev.target.removeClass("showlabel"); });

    /* ---- 工具条 ---- */
    var chipBox = $("#g-topics");
    chipBox.innerHTML = KB.topics.filter(function (t) { return docsWithTopic[t.id]; }).map(function (t) {
      var on = state.topics.has(t.id);
      return '<span class="chip' + (on ? " on" : "") + '" data-gt="' + t.id + '"' + (on ? ' style="background:' + t.color + '33"' : "") +
        '><i class="dot" style="background:' + t.color + '"></i>' + esc(t.name) + "</span>";
    }).join("");
    function syncTopicChips() {
      chipBox.querySelectorAll("[data-gt]").forEach(function (c) {
        var on = state.topics.has(c.dataset.gt);
        c.classList.toggle("on", on);
        c.style.background = on ? topicColor(c.dataset.gt) + "33" : "";
      });
    }
    chipBox.addEventListener("click", function (ev) {
      var c = ev.target.closest("[data-gt]");
      if (!c) return;
      var id = c.dataset.gt;
      if (state.topics.has(id)) { if (state.topics.size > 1) state.topics.delete(id); }
      else state.topics.add(id);
      syncTopicChips(); clearPath(); refresh();
    });

    var etypeSel = $("#g-etypes");
    ["Concept", "Method", "Tool", "Dataset"].forEach(function (tp) {
      var lb = document.createElement("label");
      lb.className = "radio";
      lb.innerHTML = '<input type="checkbox" checked value="' + tp + '">' + tp;
      etypeSel.appendChild(lb);
    });
    etypeSel.addEventListener("change", function () {
      state.etypes = new Set(Array.from(etypeSel.querySelectorAll("input:checked")).map(function (i) { return i.value; }));
      clearPath(); refresh();
    });

    var hops = $("#g-hops"), hopsVal = $("#g-hops-val");
    hops.addEventListener("input", function () {
      state.hops = parseInt(hops.value, 10);
      hopsVal.textContent = state.hops + " 跳";
      clearPath(); refresh();
    });

    $("#path-btn").addEventListener("click", function () {
      clearPath();
      pathMode = !pathMode;
      this.textContent = pathMode ? "取消路径查找" : "查找路径";
      $("#path-hint").textContent = pathMode ? "请依次点击两个节点。" : "";
      if (!pathMode) refresh();
    });
    $("#reset-btn").addEventListener("click", function () {
      state.topics = new Set(["ContextEngineering"]);
      state.hops = 2; hops.value = 2; hopsVal.textContent = "2 跳";
      state.expandedDocs.clear();
      clearPath(); syncTopicChips(); refresh();
      panel('<div class="muted">点击节点查看详情。<br>双击主题/文档下钻，右键收起。<br>“查找路径”模式下依次点选两个节点。</div>');
    });

    refresh();
  }

  /* ================================================================
   * Inbox 页
   * ================================================================ */
  function initInbox() {
    var r = KB.inbox.report;
    $("#run-report").innerHTML =
      '<div><span class="num">' + r.added + '</span> <span class="muted small">新增候选</span></div>' +
      '<div><span class="num">' + r.deduped + '</span> <span class="muted small">去重</span></div>' +
      '<div><span class="num">' + r.dropped + '</span> <span class="muted small">淘汰</span></div>' +
      '<div class="muted small">运行时间 ' + esc(r.runAt) + " · 来源 " + esc(r.source) + "</div>";

    var state = {}; // id -> {action, topic}
    function counters() {
      var acc = 0, rej = 0;
      Object.keys(state).forEach(function (k) { state[k].action === "accept" ? acc++ : rej++; });
      $("#counters").innerHTML = "待审 <b>" + (KB.inbox.candidates.length - acc - rej) + "</b> · " +
        "已接受 <b>" + acc + "</b> · 已拒绝 <b>" + rej + "</b>";
    }

    var list = $("#cands");
    var sorted = KB.inbox.candidates.slice().sort(function (a, b) { return b.score - a.score; });
    list.innerHTML = sorted.map(function (c) {
      var t = topicOf(c.topic);
      var opts = KB.topics.map(function (tp) {
        return '<option value="' + tp.id + '"' + (tp.id === c.topic ? " selected" : "") + ">" + esc(tp.name) + "</option>";
      }).join("");
      return '<div class="cand-card" id="cand-' + c.id + '">' +
        '<div class="cand-main"><div class="cand-title">' + esc(c.title) + "</div>" +
        '<div class="cand-source">' + esc(c.source) + "</div>" +
        '<div class="cand-summary">' + esc(c.summary) + "</div>" +
        '<div>' + chip(t) + '<span class="muted small">　建议主题（初评）</span></div>' +
        '<div class="cand-topic-edit" id="edit-' + c.id + '"><span class="muted small">改判主题：</span><select>' + opts + "</select>" +
        '<button class="btn btn-primary" data-confirm="' + c.id + '">确认入库</button></div>' +
        '<div class="cand-state" id="state-' + c.id + '"></div></div>' +
        '<div class="cand-side"><div class="cand-score">' + c.score.toFixed(2) + "</div>" +
        '<div class="muted small">初评得分</div>' +
        '<div class="cand-actions"><button class="btn btn-ok" data-acc="' + c.id + '">接受</button>' +
        '<button class="btn btn-danger" data-rej="' + c.id + '">拒绝</button></div></div></div>';
    }).join("");

    list.addEventListener("click", function (ev) {
      var acc = ev.target.closest("[data-acc]"), rej = ev.target.closest("[data-rej]"), cfm = ev.target.closest("[data-confirm]");
      if (acc) {
        var id = acc.dataset.acc;
        $("#edit-" + id).style.display = "flex";
        return;
      }
      if (cfm) {
        var id = cfm.dataset.confirm;
        var topic = $("#edit-" + id + " select").value;
        state[id] = { action: "accept", topic: topic };
        var card = $("#cand-" + id);
        card.className = "cand-card done-accept";
        card.querySelector(".cand-actions").innerHTML = "";
        $("#edit-" + id).style.display = "none";
        $("#state-" + id).innerHTML = '<span style="color:var(--ok)">✓ 已接收入库 · 主题 ' + esc(topic) + "（原型：仅前端状态）</span>";
        counters();
        return;
      }
      if (rej) {
        var id = rej.dataset.rej;
        state[id] = { action: "reject" };
        var card = $("#cand-" + id);
        card.className = "cand-card done-reject";
        card.querySelector(".cand-actions").innerHTML = "";
        $("#edit-" + id).style.display = "none";
        $("#state-" + id).innerHTML = '<span style="color:var(--danger)">✕ 已拒绝 · 同来源同主题初评将降权（原型：仅前端状态）</span>';
        counters();
      }
    });
    counters();
  }

  /* ================================================================
   * 状态页
   * ================================================================ */
  function initStatus() {
    var secCount = 0;
    KB.docs.forEach(function (d) { secCount += d.sections.length; });
    var stats = [
      [KB.docs.length, "文档"],
      [secCount, "章节"],
      [KB.entities.length, "实体"],
      [KB.status.chunks.toLocaleString(), "Chunk"],
      [KB.status.vectors.toLocaleString(), "向量"],
      [KB.status.edges.toLocaleString(), "图谱边"]
    ];
    $("#stats").innerHTML = stats.map(function (s) {
      return '<div class="stat-card"><div class="s-num">' + s[0] + '</div><div class="s-label">' + s[1] + "</div></div>";
    }).join("");

    $("#timeline").innerHTML = KB.status.timeline.map(function (e) {
      return '<div class="tl-item"><span class="badge ' + (e.ok ? "ok" : "fail") + '"></span>' +
        '<span class="t">' + esc(e.time) + "</span><span>" + esc(e.event) + "</span></div>";
    }).join("");

    $("#fail-table").innerHTML = "<thead><tr><th>任务</th><th>对象</th><th>错误</th><th>时间</th><th></th></tr></thead><tbody>" +
      KB.status.failed.map(function (f) {
        return '<tr id="row-' + f.id + '"><td>' + esc(f.task) + '</td><td class="tgt">' + esc(f.target) + "</td><td>" +
          esc(f.error) + '</td><td class="mono">' + esc(f.time) + '</td><td><button class="btn" data-retry="' + f.id + '">重试</button></td></tr>';
      }).join("") + "</tbody>";
    $("#fail-table").addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-retry]");
      if (!b || b.disabled) return;
      b.disabled = true; b.textContent = "已重试 ✓";
      $("#row-" + b.dataset.retry).style.opacity = 0.5;
    });

    var max = 0;
    KB.status.tokens.forEach(function (m) { max = Math.max(max, m.in, m.out); });
    $("#token-chart").innerHTML = KB.status.tokens.map(function (m) {
      return '<div class="bar-group">' +
        '<div><div class="bar-val">' + m.in + '</div><div class="bar in" style="height:' + Math.round(150 * m.in / max) + 'px"></div></div>' +
        '<div><div class="bar-val">' + m.out + '</div><div class="bar out" style="height:' + Math.round(150 * m.out / max) + 'px"></div></div>' +
        '<div class="bar-label">' + esc(m.month.slice(2)) + "</div></div>";
    }).join("");
  }

  /* ---------- 启动 ---------- */
  renderNav();
  if (page === "search") initSearch();
  else if (page === "doc") initDoc();
  else if (page === "graph") initGraph();
  else if (page === "inbox") initInbox();
  else if (page === "status") initStatus();
})();
