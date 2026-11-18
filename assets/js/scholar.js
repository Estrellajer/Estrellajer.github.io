// Scholar radar: renders feed.json (published to the `data` branch by the
// Daily Scholar Monitor workflow) as a filterable timeline.
(function () {
  const root = document.getElementById("scholarRadar");
  if (!root) return;

  const params = new URLSearchParams(location.search);
  const SRC = params.get("data") || root.dataset.src;
  const FEED = root.dataset.feed;
  const PAGE = 80;
  const KIND = { paper: "论文", post: "博客", news: "动态", update: "主页" };
  // Literal class names so PurgeCSS keeps them.
  const KIND_CLASS = { paper: "k-paper", post: "k-post", news: "k-news", update: "k-update" };
  const DAY = 86400;

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  const state = { q: "", kind: "", area: "", aff: "", shown: PAGE };
  let data = null;
  let byName = {};

  function dateLabel(it) {
    if (it.precision === "day") return it.date.slice(5);
    if (it.precision === "month") return `${+it.date.slice(5, 7)}月`;
    return it.date || "—";
  }

  function monthKey(ts) {
    const d = new Date(ts * 1000);
    return `${d.getUTCFullYear()}年${d.getUTCMonth() + 1}月`;
  }

  function matches(it) {
    const s = byName[it.scholar] || {};
    if (state.kind && it.kind !== state.kind) return false;
    if (state.area && !(s.areas || []).includes(state.area)) return false;
    if (state.aff && s.affiliation !== state.aff) return false;
    if (state.q) {
      const hay = `${it.title} ${it.scholar} ${s.affiliation || ""} ${(s.areas || []).join(" ")}`.toLowerCase();
      if (!hay.includes(state.q)) return false;
    }
    return true;
  }

  function renderTimeline() {
    const items = data.items.filter(matches);
    const visible = items.slice(0, state.shown);
    $("srCount").textContent = `${items.length} 条`;
    $("srMore").hidden = items.length <= state.shown;

    if (!visible.length) {
      $("srTimeline").innerHTML = '<div class="sr-empty">没有符合条件的动态</div>';
      return;
    }

    const groups = [];
    for (const it of visible) {
      const key = monthKey(it.ts);
      if (!groups.length || groups[groups.length - 1].key !== key) groups.push({ key, rows: [] });
      groups[groups.length - 1].rows.push(it);
    }

    $("srTimeline").innerHTML = groups
      .map(
        (g) => `
      <section>
        <h2 class="sr-group-title">${esc(g.key)}<span>${g.rows.length}</span></h2>
        <ul class="sr-list">${g.rows
          .map((it) => {
            const s = byName[it.scholar] || {};
            const aff = s.affiliation ? ` · ${esc(s.affiliation)}` : "";
            return `<li class="sr-item">
              <span class="sr-date">${esc(dateLabel(it))}</span>
              <span class="sr-badge ${KIND_CLASS[it.kind] || "k-update"}">${KIND[it.kind] || "主页"}</span>
              <div class="sr-body">
                <a class="sr-link" href="${esc(it.link)}" target="_blank" rel="noopener">${esc(it.title)}</a>
                <div class="sr-who"><a href="${esc(s.url || it.link)}" target="_blank" rel="noopener">${esc(it.scholar)}</a>${aff}</div>
              </div>
            </li>`;
          })
          .join("")}</ul>
      </section>`
      )
      .join("");
  }

  function renderMeta() {
    const now = Date.now() / 1000;
    const week = data.items.filter((it) => it.precision === "day" && it.ts >= now - 7 * DAY).length;
    const month = data.items.filter((it) => it.precision === "day" && it.ts >= now - 30 * DAY).length;
    const updated = new Date(data.generated_at).toLocaleString("zh-CN", { hour12: false, month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
    $("srMeta").innerHTML =
      `<span>更新于 <b>${esc(updated)}</b></span>` +
      `<span><b>${data.scholars.length}</b> 位学者</span>` +
      `<span>近 7 天 <b>${week}</b> 条 · 近 30 天 <b>${month}</b> 条</span>` +
      (FEED ? `<a href="${esc(FEED)}" target="_blank" rel="noopener">Atom 订阅</a>` : "");
  }

  function renderDirectory() {
    const rows = [...data.scholars].sort((a, b) => b.last - a.last);
    const dormant = rows.filter((s) => s.dormant).length;
    $("srDirCount").textContent = `${rows.length} 位 · ${dormant} 位超过半年无动态`;
    $("srDirBody").innerHTML = rows
      .map((s) => {
        const last = s.last ? new Date(s.last * 1000).toISOString().slice(0, 10) : "—";
        return `<tr class="${s.dormant ? "is-dormant" : ""}">
          <td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a></td>
          <td>${esc(s.affiliation || "—")}</td>
          <td>${esc((s.areas || []).join(" / ") || "—")}</td>
          <td>${esc(last)}${s.dormant ? '<span class="sr-dormant">沉寂</span>' : ""}</td>
        </tr>`;
      })
      .join("");
  }

  function fillSelect(id, values) {
    $(id).insertAdjacentHTML("beforeend", values.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join(""));
  }

  function bind() {
    let t;
    $("srSearch").addEventListener("input", (e) => {
      clearTimeout(t);
      t = setTimeout(() => {
        state.q = e.target.value.trim().toLowerCase();
        state.shown = PAGE;
        renderTimeline();
      }, 120);
    });
    $("srKinds").addEventListener("click", (e) => {
      const btn = e.target.closest(".sr-kind");
      if (!btn) return;
      state.kind = btn.dataset.kind;
      state.shown = PAGE;
      $("srKinds").querySelectorAll(".sr-kind").forEach((b) => b.classList.toggle("is-on", b === btn));
      renderTimeline();
    });
    for (const [id, key] of [["srArea", "area"], ["srAff", "aff"]]) {
      $(id).addEventListener("change", (e) => {
        state[key] = e.target.value;
        state.shown = PAGE;
        renderTimeline();
      });
    }
    $("srMore").addEventListener("click", () => {
      state.shown += PAGE;
      renderTimeline();
    });
  }

  fetch(SRC, { cache: "no-cache" })
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then((d) => {
      data = d;
      byName = Object.fromEntries(d.scholars.map((s) => [s.name, s]));
      fillSelect("srArea", [...new Set(d.scholars.flatMap((s) => s.areas || []))].sort());
      fillSelect("srAff", [...new Set(d.scholars.map((s) => s.affiliation).filter(Boolean))].sort());
      renderMeta();
      renderTimeline();
      renderDirectory();
      bind();
    })
    .catch((err) => {
      $("srMeta").textContent = "";
      $("srTimeline").innerHTML = `<div class="sr-error">数据加载失败：${esc(err.message)}</div>`;
    });
})();
