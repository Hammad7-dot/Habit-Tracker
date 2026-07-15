// ============================================================================
// Dashboard page
// ============================================================================

(async function () {
  const user = await initAppPage("dashboard");
  if (!user) return;

  document.getElementById("today-date").textContent = new Date().toLocaleDateString(undefined, {
    weekday: "long", month: "long", day: "numeric",
  });

  const hour = new Date().getHours();
  const greetingWord = hour < 5 ? "Still up" : hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  document.getElementById("greeting").textContent = `${greetingWord}, ${user.username}`;

  let calendarCursor = new Date(); // month currently being viewed

  document.getElementById("calendar-prev-month").addEventListener("click", () => {
    calendarCursor.setMonth(calendarCursor.getMonth() - 1);
    loadCalendar();
  });
  document.getElementById("calendar-next-month").addEventListener("click", () => {
    calendarCursor.setMonth(calendarCursor.getMonth() + 1);
    loadCalendar();
  });
  document.getElementById("calendar-today-btn").addEventListener("click", () => {
    calendarCursor = new Date();
    loadCalendar();
  });

  await loadDashboard();
  await loadCalendar();

  async function loadCalendar() {
    const year = calendarCursor.getFullYear();
    let data;
    try {
      data = await api.get(`/analytics/heatmap?year=${year}`);
    } catch (err) {
      toast(err.message || "Couldn't load the calendar.", "error");
      return;
    }
    renderMonthCalendar(data.days, calendarCursor);
  }

  function renderMonthCalendar(days, cursor) {
    const month = cursor.getMonth();
    const year = cursor.getFullYear();
    const label = cursor.toLocaleDateString(undefined, { month: "long", year: "numeric" });
    document.getElementById("calendar-month-label").textContent = label;

    const byDate = {};
    days.forEach((d) => { byDate[d.date] = d; });

    const firstOfMonth = new Date(year, month, 1);
    const leadingBlanks = firstOfMonth.getDay(); // 0=Sun
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const todayStr = new Date().toISOString().slice(0, 10);

    let html = "";
    for (let i = 0; i < leadingBlanks; i++) {
      html += `<div class="month-cal-cell empty"></div>`;
    }
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      const entry = byDate[dateStr];
      const level = entry ? entry.level : 0;
      const count = entry ? entry.count : 0;
      const isToday = dateStr === todayStr;
      const tip = `${count} completion${count === 1 ? "" : "s"} — ${cursor.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
      html += `<div class="month-cal-cell ${isToday ? "today" : ""}" data-level="${level}" data-tip="${escapeHtml(tip)}"><span>${day}</span></div>`;
    }

    document.getElementById("month-cal-grid").innerHTML = html;
  }

  async function loadDashboard() {
    let data;
    try {
      data = await api.get("/dashboard");
    } catch (err) {
      toast(err.message || "Couldn't load your dashboard.", "error");
      return;
    }
    renderStats(data);
    renderHabitList(data.today_habits);
  }

  function renderStats(data) {
    const grid = document.getElementById("stat-grid");
    grid.innerHTML = `
      <div class="stat-card">
        <i class="fa-solid fa-circle-check stat-icon"></i>
        <div class="stat-label">Today</div>
        <div class="stat-value">${data.completed_today}<span class="unit">/ ${data.total_habits}</span></div>
      </div>
      <div class="stat-card ember">
        <i class="fa-solid fa-fire stat-icon"></i>
        <div class="stat-label">Current streak</div>
        <div class="stat-value">${data.current_streak}<span class="unit">days</span></div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-trophy stat-icon"></i>
        <div class="stat-label">Longest streak</div>
        <div class="stat-value">${data.longest_streak}<span class="unit">days</span></div>
      </div>
      <div class="stat-card">
        <i class="fa-solid fa-layer-group stat-icon"></i>
        <div class="stat-label">Completion</div>
        <div class="stat-value">${data.completion_percentage}<span class="unit">%</span></div>
      </div>
    `;
  }

  function renderHabitList(habits) {
    const list = document.getElementById("habit-list");

    if (!habits.length) {
      list.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-seedling"></i>
          <h3>No habits yet</h3>
          <p>Create your first habit to start tracking your streaks.</p>
          <a href="habits.html" class="btn btn-primary"><i class="fa-solid fa-plus"></i> Add habit</a>
        </div>`;
      return;
    }

    list.innerHTML = habits.map((h) => `
      <div class="habit-row" data-habit-id="${h.id}">
        <button class="habit-check ${h.completed_today ? "checked" : ""}" aria-label="Toggle completion for ${escapeHtml(h.title)}">
          <i class="fa-solid fa-check"></i>
        </button>
        <div class="habit-icon" style="background:${h.color}"><i class="fa-solid ${h.icon}"></i></div>
        <div class="habit-info">
          <div class="title">${escapeHtml(h.title)}</div>
          <div class="meta">
            <span class="badge">${escapeHtml(h.category)}</span>
            ${h.current_streak > 0 ? `<span class="badge badge-streak"><i class="fa-solid fa-fire"></i> ${h.current_streak}d</span>` : ""}
          </div>
        </div>
      </div>
    `).join("");

    list.querySelectorAll(".habit-check").forEach((btn) => {
      btn.addEventListener("click", () => toggleCompletion(btn));
    });
  }

  async function toggleCompletion(btn) {
    const row = btn.closest(".habit-row");
    const habitId = row.dataset.habitId;
    btn.disabled = true;
    try {
      const result = await api.post(`/complete/${habitId}`);
      showUnlockedAchievements(result.newly_unlocked);
      await loadDashboard();
    } catch (err) {
      toast(err.message || "Couldn't update that habit.", "error");
      btn.disabled = false;
    }
  }
})();