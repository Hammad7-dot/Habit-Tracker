// ============================================================================
// Reminders — polls habits with reminder_enabled + reminder_time and fires a
// browser notification once per habit per day at that local time.
//
// Notes on scope: this runs while a tab is open (or, once installed as a
// PWA/service worker is registered, in many mobile browsers it can also fire
// shortly after reopening the app if the time already passed while closed).
// It intentionally does not require a backend push server.
// ============================================================================

const REMINDER_FIRED_KEY = "habit_tracker_reminders_fired"; // { "2026-07-16": [habitId, ...] }
const REMINDER_CHECK_INTERVAL_MS = 30 * 1000;

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.register("sw.js").catch(() => {});
}

function getFiredMap() {
  try {
    return JSON.parse(localStorage.getItem(REMINDER_FIRED_KEY)) || {};
  } catch {
    return {};
  }
}

function markFired(habitId) {
  const map = getFiredMap();
  const today = todayISO();
  map[today] = map[today] || [];
  if (!map[today].includes(habitId)) map[today].push(habitId);
  // Keep the map small — drop any days other than today.
  localStorage.setItem(REMINDER_FIRED_KEY, JSON.stringify({ [today]: map[today] }));
}

function alreadyFiredToday(habitId) {
  const map = getFiredMap();
  const today = todayISO();
  return (map[today] || []).includes(habitId);
}

function showReminderNotification(habit) {
  const title = "Habit reminder";
  const body = `Time for: ${habit.title}`;
  if ("serviceWorker" in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.ready.then((reg) => {
      reg.showNotification(title, {
        body,
        icon: "icon-192.png",
        badge: "icon-192.png",
        tag: `habit-${habit.id}`,
      });
    }).catch(() => fallbackNotify(title, body));
  } else {
    fallbackNotify(title, body);
  }
}

function fallbackNotify(title, body) {
  try {
    new Notification(title, { body, icon: "icon-192.png" });
  } catch {
    // Notification constructor can throw on some mobile browsers even when
    // permission is granted; silently no-op rather than breaking the page.
  }
}

async function checkReminders() {
  if (Notification.permission !== "granted") return;
  if (!getToken()) return;

  let habits;
  try {
    habits = await api.get("/habits");
  } catch {
    return;
  }

  const now = new Date();
  const hh = String(now.getHours()).padStart(2, "0");
  const mm = String(now.getMinutes()).padStart(2, "0");
  const nowHM = `${hh}:${mm}`;

  habits
    .filter((h) => h.reminder_enabled && h.reminder_time)
    .forEach((h) => {
      const habitHM = h.reminder_time.slice(0, 5); // "HH:MM:SS" -> "HH:MM"
      if (habitHM === nowHM && !alreadyFiredToday(h.id)) {
        markFired(h.id);
        showReminderNotification(h);
      }
    });
}

function showReminderPermissionBanner() {
  if (!("Notification" in window)) return;
  if (Notification.permission !== "default") return;
  if (sessionStorage.getItem("habit_tracker_reminder_banner_dismissed")) return;

  const bar = document.createElement("div");
  bar.className = "reminder-banner";
  bar.innerHTML = `
    <i class="fa-solid fa-bell"></i>
    <span>Turn on notifications to get habit reminders.</span>
    <button class="btn btn-primary btn-sm" id="reminder-banner-enable">Enable</button>
    <button class="btn btn-ghost btn-sm" id="reminder-banner-dismiss" aria-label="Dismiss"><i class="fa-solid fa-xmark"></i></button>
  `;
  document.body.appendChild(bar);

  document.getElementById("reminder-banner-enable").addEventListener("click", async () => {
    try {
      await Notification.requestPermission();
    } finally {
      bar.remove();
      if (Notification.permission === "granted") {
        toast("Reminders enabled.", "success");
        checkReminders();
      }
    }
  });
  document.getElementById("reminder-banner-dismiss").addEventListener("click", () => {
    sessionStorage.setItem("habit_tracker_reminder_banner_dismissed", "1");
    bar.remove();
  });
}

function startReminders() {
  if (!("Notification" in window)) return;
  registerServiceWorker();
  showReminderPermissionBanner();
  checkReminders();
  setInterval(checkReminders, REMINDER_CHECK_INTERVAL_MS);
}
