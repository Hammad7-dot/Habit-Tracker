// ============================================================================
// Habits page — CRUD against /habits, options from /habits/options
// ============================================================================

(async function () {
  const user = await initAppPage("habits");
  if (!user) return;

  let options = { categories: [], icons: [], colors: [] };
  let habits = [];
  let selectedColor = null;
  let selectedIcon = null;
  let pendingDeleteId = null;

  const grid = document.getElementById("habits-grid");
  const modalOverlay = document.getElementById("habit-modal-overlay");
  const modalTitle = document.getElementById("modal-title");
  const modalError = document.getElementById("modal-error");
  const form = document.getElementById("habit-form");
  const submitBtn = document.getElementById("habit-submit-btn");
  const submitLabel = document.getElementById("habit-submit-label");
  const deleteOverlay = document.getElementById("delete-modal-overlay");
<<<<<<< HEAD
=======
<<<<<<< HEAD
  const reminderEnabledInput = document.getElementById("habit-reminder-enabled");
  const reminderTimeInput = document.getElementById("habit-reminder-time");

  reminderEnabledInput.addEventListener("change", () => {
    reminderTimeInput.style.display = reminderEnabledInput.checked ? "block" : "none";
    if (reminderEnabledInput.checked && Notification.permission === "default") {
      Notification.requestPermission();
    }
  });
=======
>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc

  await bootstrap();

  async function bootstrap() {
    try {
      [options, habits] = await Promise.all([api.get("/habits/options"), api.get("/habits")]);
    } catch (err) {
      toast(err.message || "Couldn't load habits.", "error");
      return;
    }
    buildCategorySelect();
    buildColorPicker();
    buildIconPicker();
    renderGrid();
  }

  function buildCategorySelect() {
    const sel = document.getElementById("habit-category");
    sel.innerHTML = options.categories.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
  }

  function buildColorPicker() {
    const wrap = document.getElementById("color-picker");
    wrap.innerHTML = options.colors.map((c) => `<div class="swatch" data-color="${c}" style="background:${c}; color:${c};"></div>`).join("");
    wrap.querySelectorAll(".swatch").forEach((sw) => {
      sw.addEventListener("click", () => {
        selectedColor = sw.dataset.color;
        wrap.querySelectorAll(".swatch").forEach((s) => s.classList.toggle("selected", s === sw));
      });
    });
  }

  function buildIconPicker() {
    const wrap = document.getElementById("icon-picker");
    wrap.innerHTML = options.icons.map((i) => `<div class="icon-swatch" data-icon="${i}" title="${i}"><i class="fa-solid ${i}"></i></div>`).join("");
    wrap.querySelectorAll(".icon-swatch").forEach((sw) => {
      sw.addEventListener("click", () => {
        selectedIcon = sw.dataset.icon;
        wrap.querySelectorAll(".icon-swatch").forEach((s) => s.classList.toggle("selected", s === sw));
      });
    });
  }

  function selectColor(color) {
    selectedColor = color;
    document.querySelectorAll("#color-picker .swatch").forEach((s) => s.classList.toggle("selected", s.dataset.color === color));
  }

  function selectIcon(icon) {
    selectedIcon = icon;
    document.querySelectorAll("#icon-picker .icon-swatch").forEach((s) => s.classList.toggle("selected", s.dataset.icon === icon));
  }

  function renderGrid() {
    if (!habits.length) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1;">
          <i class="fa-solid fa-seedling"></i>
          <h3>No habits yet</h3>
          <p>Add your first habit to start building a streak.</p>
          <button class="btn btn-primary" id="empty-add-btn"><i class="fa-solid fa-plus"></i> Add habit</button>
        </div>`;
      document.getElementById("empty-add-btn").addEventListener("click", openCreateModal);
      return;
    }

    grid.innerHTML = habits.map((h) => `
      <div class="habit-card" data-id="${h.id}">
        <div class="habit-card-top">
          <div class="habit-icon" style="background:${h.color};"><i class="fa-solid ${h.icon}"></i></div>
          <div class="info">
            <div class="title">${escapeHtml(h.title)}</div>
            <div class="cat">${escapeHtml(h.category)}</div>
          </div>
        </div>
        ${h.description ? `<div class="desc">${escapeHtml(h.description)}</div>` : ""}
        <div class="habit-card-stats">
          <div><strong>${h.goal}</strong>&nbsp;/ day goal</div>
<<<<<<< HEAD
=======
<<<<<<< HEAD
          ${h.reminder_enabled && h.reminder_time ? `<div class="reminder-pill"><i class="fa-solid fa-bell"></i> ${formatReminderTime(h.reminder_time)}</div>` : ""}
=======
>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
        </div>
        <div class="habit-card-actions">
          <button class="btn btn-secondary btn-sm edit-btn" style="flex:1;"><i class="fa-solid fa-pen"></i> Edit</button>
          <button class="btn btn-danger btn-sm delete-btn" style="flex:1;"><i class="fa-solid fa-trash"></i> Delete</button>
        </div>
      </div>
    `).join("");

    grid.querySelectorAll(".edit-btn").forEach((btn) => {
      btn.addEventListener("click", () => openEditModal(Number(btn.closest(".habit-card").dataset.id)));
    });
    grid.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", () => openDeleteModal(Number(btn.closest(".habit-card").dataset.id)));
    });
  }

  function openCreateModal() {
    modalTitle.textContent = "New habit";
    setFormError(modalError, "");
    document.getElementById("habit-id").value = "";
    document.getElementById("habit-title").value = "";
    document.getElementById("habit-description").value = "";
    document.getElementById("habit-category").value = options.categories[0];
    document.getElementById("habit-goal").value = 1;
<<<<<<< HEAD
=======
<<<<<<< HEAD
    reminderEnabledInput.checked = false;
    reminderTimeInput.value = "09:00";
    reminderTimeInput.style.display = "none";
=======
>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
    selectColor(options.colors[Math.floor(Math.random() * options.colors.length)] || options.colors[0]);
    selectIcon(options.icons[0]);
    submitLabel.textContent = "Save habit";
    modalOverlay.classList.add("open");
    document.getElementById("habit-title").focus();
  }

  function openEditModal(id) {
    const h = habits.find((x) => x.id === id);
    if (!h) return;
    modalTitle.textContent = "Edit habit";
    setFormError(modalError, "");
    document.getElementById("habit-id").value = h.id;
    document.getElementById("habit-title").value = h.title;
    document.getElementById("habit-description").value = h.description || "";
    document.getElementById("habit-category").value = h.category;
    document.getElementById("habit-goal").value = h.goal;
<<<<<<< HEAD
=======
<<<<<<< HEAD
    reminderEnabledInput.checked = !!h.reminder_enabled;
    reminderTimeInput.value = h.reminder_time ? h.reminder_time.slice(0, 5) : "09:00";
    reminderTimeInput.style.display = reminderEnabledInput.checked ? "block" : "none";
=======
>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
    selectColor(h.color);
    selectIcon(h.icon);
    submitLabel.textContent = "Save changes";
    modalOverlay.classList.add("open");
  }

<<<<<<< HEAD
=======
<<<<<<< HEAD
  function formatReminderTime(hms) {
    const [h, m] = hms.split(":").map(Number);
    const d = new Date();
    d.setHours(h, m, 0, 0);
    return d.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
  }

=======
>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
  function closeModal() {
    modalOverlay.classList.remove("open");
  }

  document.getElementById("new-habit-btn").addEventListener("click", openCreateModal);
  document.getElementById("modal-close-btn").addEventListener("click", closeModal);
  modalOverlay.addEventListener("click", (e) => { if (e.target === modalOverlay) closeModal(); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setFormError(modalError, "");

    const id = document.getElementById("habit-id").value;
    const title = document.getElementById("habit-title").value.trim();
    if (!title) { setFormError(modalError, "Title is required."); return; }
    if (!selectedColor || !selectedIcon) { setFormError(modalError, "Pick a color and icon."); return; }

    const payload = {
      title,
      description: document.getElementById("habit-description").value.trim() || null,
      category: document.getElementById("habit-category").value,
      goal: Number(document.getElementById("habit-goal").value) || 1,
      color: selectedColor,
      icon: selectedIcon,
<<<<<<< HEAD
=======
<<<<<<< HEAD
      reminder_enabled: reminderEnabledInput.checked,
      reminder_time: reminderEnabledInput.checked ? reminderTimeInput.value : null,
=======
>>>>>>> cc30b236afbf34ce26a54add4ee6a06deec9f873
>>>>>>> 67dc7449e9306e1041dd90249aae478f9d1548fc
    };

    submitBtn.disabled = true;
    submitLabel.textContent = "Saving…";

    try {
      if (id) {
        await api.put(`/habits/${id}`, payload);
        toast("Habit updated.", "success");
      } else {
        await api.post("/habits", payload);
        toast("Habit created.", "success");
      }
      habits = await api.get("/habits");
      renderGrid();
      closeModal();
    } catch (err) {
      setFormError(modalError, err.message || "Couldn't save that habit.");
    } finally {
      submitBtn.disabled = false;
      submitLabel.textContent = id ? "Save changes" : "Save habit";
    }
  });

  function openDeleteModal(id) {
    pendingDeleteId = id;
    deleteOverlay.classList.add("open");
  }
  function closeDeleteModal() {
    pendingDeleteId = null;
    deleteOverlay.classList.remove("open");
  }
  document.getElementById("delete-cancel-btn").addEventListener("click", closeDeleteModal);
  deleteOverlay.addEventListener("click", (e) => { if (e.target === deleteOverlay) closeDeleteModal(); });
  document.getElementById("delete-confirm-btn").addEventListener("click", async () => {
    if (!pendingDeleteId) return;
    const btn = document.getElementById("delete-confirm-btn");
    btn.disabled = true;
    try {
      await api.del(`/habits/${pendingDeleteId}`);
      habits = habits.filter((h) => h.id !== pendingDeleteId);
      renderGrid();
      toast("Habit deleted.", "success");
    } catch (err) {
      toast(err.message || "Couldn't delete that habit.", "error");
    } finally {
      btn.disabled = false;
      closeDeleteModal();
    }
  });
})();
