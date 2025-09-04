// AI Solution Hub · Admin JS (dashboard + login + UX helpers)
// Works with Static/admin/css/admin.css and templates/admin/*
// No public-site impact

(function () {
  // ---------- THEME ----------
  const root = document.documentElement;
  const THEME_KEY = "ops-theme";
  function setTheme(t) { root.setAttribute("data-theme", t); localStorage.setItem(THEME_KEY, t); }
  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) { setTheme(saved); return; }
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
  }

  // ---------- CHARTS ----------
  function lineChart() {
    const el = document.getElementById("ops-line");
    if (!el) return;
    const labels = JSON.parse(el.dataset.labels || "[]");
    const a = JSON.parse(el.dataset.a || "[]");
    const b = JSON.parse(el.dataset.b || "[]");
    const svg = el.querySelector("svg");
    const W = 560, H = 170, OX = 30, OY = 190;
    const max = Math.max(1, ...a, ...b);
    const n = Math.max(a.length, b.length, 1);
    function xy(v, i) {
      const x = OX + (i * (W / (n - 1 || 1)));
      const y = OY - (v / max) * H;
      return [x, y];
    }
    function toPath(series) {
      return series.map((v, i) => {
        const [x, y] = xy(v, i);
        return (i ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1);
      }).join(" ");
    }
    const pA = toPath(a), pB = toPath(b);
    svg.querySelector(".series-a").setAttribute("d", pA);
    svg.querySelector(".series-b").setAttribute("d", pB);
    const pts = a.map((v, i) => xy(v, i).map(n => n.toFixed(1)).join(","));
    const area = ["30,190"].concat(pts).concat(["590,190"]).join(" ");
    svg.querySelector(".area-a").setAttribute("points", area);
  }

  function donut() {
    const el = document.getElementById("ops-donut");
    if (!el) return;
    const labels = JSON.parse(el.dataset.labels || "[]");
    const vals = JSON.parse(el.dataset.values || "[]");
    const sum = vals.reduce((s, v) => s + v, 0) || 1;
    const svg = el.querySelector("svg");
    const cx = 110, cy = 110, r = 70, C = 2 * Math.PI * r;
    let off = 0;
    const colors = ["#4f46e5", "#22c55e", "#f59e0b", "#ef4444", "#a78bfa", "#10b981", "#f472b6"];
    vals.forEach((v, i) => {
      const len = C * (v / sum);
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", cx); c.setAttribute("cy", cy); c.setAttribute("r", r);
      c.setAttribute("fill", "none"); c.setAttribute("stroke-width", "22");
      c.setAttribute("stroke", colors[i % colors.length]);
      c.setAttribute("stroke-dasharray", `${len} ${C - len}`);
      c.setAttribute("stroke-dashoffset", -off);
      svg.appendChild(c);
      off += len;
    });
    const legend = el.querySelector(".donut-legend");
    labels.forEach((lab, i) => {
      const s = document.createElement("span");
      s.innerHTML = `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${colors[i%colors.length]};margin-right:6px"></span>${lab}`;
      legend.appendChild(s);
    });
  }

  // ---------- PROFILE MENU ----------
  function profileMenu() {
    const btn = document.getElementById("ops-profile-toggle");
    const menu = document.getElementById("ops-profile-menu");
    if (!btn || !menu) return;
    btn.addEventListener("click", () => {
      const open = menu.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", (e) => {
      if (!menu.contains(e.target) && !btn.contains(e.target)) menu.classList.remove("open");
    });
  }

  // ---------- UX ENHANCEMENTS (your snippet merged) ----------
  function enhanceUX() {
    // Loading state for action buttons
    document.querySelectorAll(".action-btn").forEach(btn => {
      btn.addEventListener("click", function () {
        const txt = this.innerHTML;
        this.innerHTML = '<span class="loading"></span> Processing...';
        this.disabled = true;
        setTimeout(() => { this.innerHTML = txt; this.disabled = false; }, 2000);
      });
    });

    // Hover lift on stat cards
    document.querySelectorAll(".stat-card, .card[data-kpi], .card.kpi").forEach(card => {
      card.style.transition = "transform .15s ease";
      card.addEventListener("mouseenter", () => card.style.transform = "translateY(-5px)");
      card.addEventListener("mouseleave", () => card.style.transform = "translateY(0)");
    });

    // Click nudge on quick actions
    document.querySelectorAll(".quick-action-btn, .actions .btn").forEach(btn => {
      btn.style.transition = "transform .15s ease";
      btn.addEventListener("click", () => {
        btn.style.transform = "translateY(-2px)";
        setTimeout(() => btn.style.transform = "translateY(0)", 150);
      });
    });

    // Auto-refresh dashboard every 30s (only dashboard index)
    if (/^\/admin\/?$/.test(location.pathname)) {
      setInterval(() => {
        if (!document.querySelector('form:not([method="get"])')) location.reload();
      }, 30000);
    }

    // Bulk action confirm
    const bulk = document.querySelector('select[name="action"]');
    if (bulk) {
      bulk.addEventListener("change", function () {
        if (!this.value) return;
        const name = this.options[this.selectedIndex].text;
        if (!confirm(`Are you sure you want to ${name.toLowerCase()} the selected items?`)) {
          this.selectedIndex = 0;
        }
      });
    }

    // Priority tooltips
    document.querySelectorAll(".priority-indicator,[data-priority]").forEach(indicator => {
      const text = (indicator.dataset.priority || indicator.textContent || "").trim();
      let tip = "Normal Priority";
      if (text.includes("🔴")) tip = "High Priority — new within 24h";
      else if (text.includes("🟡")) tip = "Medium Priority — in progress";
      else if (text.includes("🟢")) tip = "Low Priority — contacted/closed";
      indicator.title = tip;
    });

    // Status badge click pulse
    document.querySelectorAll(".status-badge,[data-status-badge]").forEach(badge => {
      badge.style.transition = "transform .2s ease";
      badge.addEventListener("click", () => {
        badge.style.transform = "scale(1.1)";
        setTimeout(() => badge.style.transform = "scale(1)", 200);
      });
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key.toLowerCase() === "e") {
        e.preventDefault();
        const exportBtn = document.querySelector('input[value="Export to CSV"], button[value="export_csv"]');
        if (exportBtn) exportBtn.click();
      }
      if (e.ctrlKey && e.key.toLowerCase() === "n") {
        e.preventDefault();
        const add = document.querySelector('a[href*="/add/"]');
        if (add) add.click();
      }
    });

    // Search highlighting on changelist
    const q = document.querySelector('input[name="q"]');
    if (q) {
      q.addEventListener("input", function () {
        const s = this.value.toLowerCase();
        document.querySelectorAll(".results tbody tr").forEach(tr => {
          const txt = tr.textContent.toLowerCase();
          tr.style.backgroundColor = s && txt.includes(s) ? "#fff3cd" : "";
        });
      });
    }

    // Notes autosave placeholder (debounced)
    const notes = document.querySelector('textarea[name="notes"]');
    if (notes) {
      let t;
      notes.addEventListener("input", () => {
        clearTimeout(t);
        t = setTimeout(() => { console.log("Auto-saving notes…"); /* hook AJAX here if needed */ }, 2000);
      });
    }

    // Toast notifications
    function notify(msg, type = "info") {
      const map = {
        success: { bg: "#d4edda", fg: "#155724" },
        error: { bg: "#f8d7da", fg: "#721c24" },
        info: { bg: "#d1ecf1", fg: "#0c5460" }
      };
      const { bg, fg } = map[type] || map.info;
      const n = document.createElement("div");
      n.innerHTML = `<div style="
        position:fixed;top:20px;right:20px;background:${bg};color:${fg};
        padding:15px 20px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15);
        z-index:9999;font-weight:500;max-width:320px;">${msg}</div>`;
      document.body.appendChild(n);
      setTimeout(() => n.remove(), 3000);
    }

    if (/^\/admin\/?$/.test(location.pathname)) {
      setTimeout(() => notify("Welcome to AI Solution Hub Admin! 🚀", "success"), 1000);
    }
  }

  // ---------- INIT ----------
  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    const toggle = document.getElementById("ops-theme-toggle");
    if (toggle) toggle.addEventListener("click", () =>
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark")
    );

    // Mark login page for CSS layout tweaks
    if (document.querySelector(".login-wrap")) {
      const c = document.getElementById("content");
      if (c) c.classList.add("login-page");
      
      // Password toggle functionality
      const togglePass = document.getElementById("toggle-pass");
      const passwordField = document.getElementById("id_password");
      if (togglePass && passwordField) {
        togglePass.addEventListener("click", function(e) {
          e.preventDefault();
          passwordField.type = (passwordField.type === "password" ? "text" : "password");
          togglePass.textContent = (passwordField.type === "password" ? "👁" : "🙈");
        });
      }
    }

    profileMenu();
    lineChart();
    donut();
    enhanceUX();
  });
})();
