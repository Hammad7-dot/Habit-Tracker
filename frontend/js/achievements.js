// ============================================================================
// Achievements page — /achievements + /achievements/evaluate
// ============================================================================

(async function () {
  const user = await initAppPage("achievements");
  if (!user) return;

  await loadAchievements();

  document.getElementById("recheck-btn").addEventListener("click", async (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    const icon = btn.querySelector("i");
    icon.classList.add("fa-spin");
    try {
      const newlyUnlocked = await api.post("/achievements/evaluate");
      if (newlyUnlocked.length) {
        showUnlockedAchievements(newlyUnlocked);
      } else {
        toast("Nothing new yet — keep going.", "success");
      }
      await loadAchievements();
    } catch (err) {
      toast(err.message || "Couldn't re-check achievements.", "error");
    } finally {
      btn.disabled = false;
      icon.classList.remove("fa-spin");
    }
  });

  async function loadAchievements() {
    let data;
    try {
      data = await api.get("/achievements");
    } catch (err) {
      toast(err.message || "Couldn't load achievements.", "error");
      return;
    }
    renderSummary(data);
    renderGrid(data.achievements);
  }

  function renderSummary(data) {
    const pct = data.total_count > 0 ? Math.round((data.unlocked_count / data.total_count) * 100) : 0;
    const ring = document.getElementById("achievements-ring");
    ring.style.setProperty("--pct", pct);
    document.getElementById("ring-label").textContent = `${pct}%`;
    document.getElementById("summary-count").textContent = `${data.unlocked_count} / ${data.total_count}`;
  }

  function renderGrid(achievements) {
    const grid = document.getElementById("achievements-grid");
    // unlocked first, then in-progress by descending progress
    const sorted = achievements.slice().sort((a, b) => {
      if (a.unlocked !== b.unlocked) return a.unlocked ? -1 : 1;
      return b.progress_percentage - a.progress_percentage;
    });

    grid.innerHTML = sorted.map((a) => `
      <div class="achievement-card ${a.unlocked ? "unlocked" : ""}">
        <div class="achievement-icon"><i class="fa-solid ${a.unlocked ? "fa-trophy" : "fa-lock"}"></i></div>
        <div class="achievement-body">
          <div class="name">${escapeHtml(a.name)}</div>
          <div class="desc">${escapeHtml(a.description)}</div>
          ${a.unlocked
            ? `<span class="badge badge-streak"><i class="fa-solid fa-check"></i> Unlocked${a.unlocked_at ? " " + formatDate(a.unlocked_at) : ""}</span>`
            : `<div class="bar-track"><div class="bar-fill" style="width:${a.progress_percentage}%; background:var(--gradient-ember, var(--ember-hot));"></div></div>
               <div class="sub" style="font-size:0.72rem; margin-top:0.35rem;">${a.current_value} / ${a.threshold}</div>`
          }
        </div>
      </div>
    `).join("");
  }
})();