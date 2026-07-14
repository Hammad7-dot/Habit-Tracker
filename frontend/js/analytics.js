// ============================================================================
// Analytics page — /analytics + /analytics/heatmap
// ============================================================================

(async function () {
  const user = await initAppPage("analytics");
  if (!user) return;

  const styles = getComputedStyle(document.documentElement);
  const cVar = (name) => styles.getPropertyValue(name).trim();
  const colors = {
    violet: cVar("--violet"),
    cyan: cVar("--cyan"),
    text: cVar("--text-dim"),
    grid: cVar("--border"),
  };
  Chart.defaults.color = colors.text;
  Chart.defaults.font.family = "Inter, system-ui, sans-serif";

  let dailyChart = null;
  let categoryChart = null;
  let currentDays = 30;
  let currentYear = new Date().getFullYear();

  const rangeToggle = document.getElementById("range-toggle");
  rangeToggle.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    rangeToggle.querySelectorAll("button").forEach((b) => b.classList.toggle("active", b === btn));
    currentDays = Number(btn.dataset.days);
    loadAnalytics();
  });

  buildYearToggle();
  await Promise.all([loadAnalytics(), loadHeatmap()]);

  function buildYearToggle() {
    const wrap = document.getElementById("year-toggle");
    const thisYear = new Date().getFullYear();
    const years = [thisYear - 1, thisYear];
    wrap.innerHTML = years.map((y) => `<button data-year="${y}" class="${y === currentYear ? "active" : ""}">${y}</button>`).join("");
    wrap.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      wrap.querySelectorAll("button").forEach((b) => b.classList.toggle("active", b === btn));
      currentYear = Number(btn.dataset.year);
      loadHeatmap();
    });
  }

  async function loadAnalytics() {
    let data;
    try {
      data = await api.get(`/analytics?days=${currentDays}`);
    } catch (err) {
      toast(err.message || "Couldn't load analytics.", "error");
      return;
    }
    renderDailyChart(data.daily_completions);
    renderCategoryChart(data.category_breakdown);
    renderPerHabit(data.per_habit);
  }

  function renderDailyChart(daily) {
    const ctx = document.getElementById("daily-chart");
    const labels = daily.map((d) => formatDate(d.date));
    const values = daily.map((d) => d.count);

    const gradient = ctx.getContext("2d").createLinearGradient(0, 0, 0, 260);
    gradient.addColorStop(0, "rgba(139, 92, 246, 0.35)");
    gradient.addColorStop(1, "rgba(139, 92, 246, 0)");

    if (dailyChart) dailyChart.destroy();
    dailyChart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Completions",
          data: values,
          borderColor: colors.violet,
          backgroundColor: gradient,
          fill: true,
          tension: 0.35,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
          y: { beginAtZero: true, grid: { color: colors.grid }, ticks: { precision: 0 } },
        },
      },
    });
  }

  function renderCategoryChart(breakdown) {
    const ctx = document.getElementById("category-chart");
    const palette = ["#8b5cf6", "#22d3ee", "#fb923c", "#34d399", "#f87171", "#fbbf24", "#a855f7", "#0ea5e9", "#ec4899", "#84cc16"];

    if (categoryChart) categoryChart.destroy();

    if (!breakdown.length) {
      categoryChart = null;
      ctx.getContext("2d").clearRect(0, 0, ctx.width, ctx.height);
      const wrap = ctx.closest(".chart-wrap");
      if (!wrap.querySelector(".empty-note")) {
        const note = document.createElement("div");
        note.className = "empty-note";
        note.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--text-faint);font-size:0.85rem;";
        note.textContent = "No completions in this period yet.";
        wrap.appendChild(note);
      }
      return;
    }
    const existingNote = ctx.closest(".chart-wrap").querySelector(".empty-note");
    if (existingNote) existingNote.remove();

    categoryChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: breakdown.map((b) => b.category),
        datasets: [{
          data: breakdown.map((b) => b.count),
          backgroundColor: breakdown.map((_, i) => palette[i % palette.length]),
          borderColor: cVar("--bg-elevated") || "#12121f",
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "62%",
        plugins: { legend: { position: "bottom", labels: { boxWidth: 10, padding: 12, font: { size: 11 } } } },
      },
    });
  }

  function renderPerHabit(perHabit) {
    const list = document.getElementById("per-habit-list");
    if (!perHabit.length) {
      list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-chart-simple"></i><p>No habits to show yet.</p></div>`;
      return;
    }
    list.innerHTML = perHabit
      .slice()
      .sort((a, b) => b.completion_rate - a.completion_rate)
      .map((h) => `
        <div class="per-habit-row">
          <div class="top"><span class="name">${escapeHtml(h.title)}</span><span class="pct">${h.completion_rate}%</span></div>
          <div class="bar-track"><div class="bar-fill" style="width:${Math.min(h.completion_rate, 100)}%; background:${h.color};"></div></div>
        </div>
      `).join("");
  }

  async function loadHeatmap() {
    let data;
    try {
      data = await api.get(`/analytics/heatmap?year=${currentYear}`);
    } catch (err) {
      toast(err.message || "Couldn't load the heatmap.", "error");
      return;
    }
    renderHeatmap(data);
  }

  function renderHeatmap(data) {
    const grid = document.getElementById("heatmap-grid");
    const firstDate = new Date(`${data.days[0].date}T00:00:00`);
    const leadingBlanks = firstDate.getDay(); // 0=Sun

    let html = "";
    for (let i = 0; i < leadingBlanks; i++) {
      html += `<div class="heatmap-cell" data-level="0" style="visibility:hidden;"></div>`;
    }
    data.days.forEach((d) => {
      const label = formatDate(d.date, { month: "short", day: "numeric", year: "numeric" });
      html += `<div class="heatmap-cell" data-level="${d.level}" data-tip="${d.count} completion${d.count === 1 ? "" : "s"} — ${label}"></div>`;
    });
    grid.innerHTML = html;
  }
})();
