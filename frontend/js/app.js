// ============================================================================
// Habit Tracker — shared core (API client, auth, sidebar, toasts, helpers)
// Loaded on every page before the page-specific script.
// ============================================================================

const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : (window.HABIT_TRACKER_CONFIG && window.HABIT_TRACKER_CONFIG.PROD_API_BASE_URL) || "";

if (!API_BASE_URL && window.location.hostname !== "localhost") {
  console.error("HABIT_TRACKER_CONFIG.PROD_API_BASE_URL is not set — edit frontend/js/config.js with your deployed backend URL.");
}

// ---- Token storage -------------------------------------------------------

function getToken() {
  return localStorage.getItem("habit_tracker_token");
}

function setToken(token) {
  localStorage.setItem("habit_tracker_token", token);
}

function clearToken() {
  localStorage.removeItem("habit_tracker_token");
  localStorage.removeItem("habit_tracker_user");
}

function getCachedUser() {
  try {
    const raw = localStorage.getItem("habit_tracker_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setCachedUser(user) {
  localStorage.setItem("habit_tracker_user", JSON.stringify(user));
}

// ---- API client ------------------------------------------------------------

async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  let res;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (networkErr) {
    throw new Error("Can't reach the server. Check your connection and try again.");
  }

  if (res.status === 401) {
    clearToken();
    if (!location.pathname.endsWith("login.html") && !location.pathname.endsWith("register.html") && !location.pathname.endsWith("index.html") && location.pathname !== "/") {
      location.href = "login.html";
    }
    throw new Error("Your session expired. Please log in again.");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const detail = err.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join(" ")
      : (detail || res.statusText || "Request failed");
    throw new Error(message);
  }

  if (res.status === 204) return null;
  return res.json();
}

const api = {
  get: (path) => apiRequest(path, { method: "GET" }),
  post: (path, body) => apiRequest(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: (path, body) => apiRequest(path, { method: "PUT", body: JSON.stringify(body) }),
  del: (path) => apiRequest(path, { method: "DELETE" }),
};

// ---- Auth guards ------------------------------------------------------------

async function requireAuth() {
  const token = getToken();
  if (!token) {
    location.href = "login.html";
    return null;
  }
  try {
    const user = await api.get("/auth/me");
    setCachedUser(user);
    return user;
  } catch (e) {
    location.href = "login.html";
    return null;
  }
}

function redirectIfAuthed() {
  if (getToken()) {
    location.href = "dashboard.html";
  }
}

function logout() {
  clearToken();
  location.href = "login.html";
}

// ---- Toasts ------------------------------------------------------------

function ensureToastStack() {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    document.body.appendChild(stack);
  }
  return stack;
}

function toast(message, type = "success", timeout = 4200) {
  const stack = ensureToastStack();
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  const icon = type === "error" ? "fa-circle-exclamation" : type === "unlock" ? "fa-trophy" : "fa-circle-check";
  el.innerHTML = `<i class="fa-solid ${icon}"></i><span></span>`;
  el.querySelector("span").textContent = message;
  stack.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transition = "opacity 0.25s ease";
    setTimeout(() => el.remove(), 260);
  }, timeout);
}

function showUnlockedAchievements(newlyUnlocked) {
  if (!newlyUnlocked || !newlyUnlocked.length) return;
  newlyUnlocked.forEach((a, i) => {
    setTimeout(() => toast(`Achievement unlocked: ${a.name}`, "unlock", 5500), i * 350);
  });
}

// ---- Sidebar / app shell ------------------------------------------------------------

const NAV_ITEMS = [
  { page: "dashboard", href: "dashboard.html", icon: "fa-house", label: "Dashboard" },
  { page: "habits", href: "habits.html", icon: "fa-list-check", label: "Habits" },
  { page: "analytics", href: "analytics.html", icon: "fa-chart-line", label: "Analytics" },
  { page: "achievements", href: "achievements.html", icon: "fa-trophy", label: "Achievements" },
  { page: "profile", href: "profile.html", icon: "fa-user-gear", label: "Profile" },
];

function renderShell(activePage, user) {
  const root = document.getElementById("app-shell-root");
  if (!root) return;

  const navHtml = NAV_ITEMS.map(
    (item) => `
      <a href="${item.href}" class="nav-link ${item.page === activePage ? "active" : ""}">
        <i class="fa-solid ${item.icon}"></i><span>${item.label}</span>
      </a>`
  ).join("");

  const initials = (user?.username || "?").slice(0, 2).toUpperCase();
  const avatarInner = user?.avatar_url
    ? `<img src="${escapeHtml(user.avatar_url)}" alt="">`
    : initials;

  root.innerHTML = `
    <div class="sidebar-backdrop" id="sidebar-backdrop"></div>
    <div class="mobile-topbar">
      <button class="btn btn-icon btn-ghost" id="mobile-menu-btn" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button>
      <a href="dashboard.html" class="brand"><i class="fa-solid fa-bolt"></i> Habit Tracker</a>
      <div style="width:2.25rem"></div>
    </div>
    <aside class="sidebar" id="app-sidebar">
      <a href="dashboard.html" class="brand"><i class="fa-solid fa-bolt"></i> Habit Tracker</a>
      <nav>${navHtml}</nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="avatar">${avatarInner}</div>
          <div class="who">
            <div class="name">${escapeHtml(user?.username || "")}</div>
            <div class="email">${escapeHtml(user?.email || "")}</div>
          </div>
        </div>
        <button class="btn btn-ghost btn-block" id="logout-btn" style="justify-content:flex-start;"><i class="fa-solid fa-arrow-right-from-bracket"></i> Log out</button>
      </div>
    </aside>
  `;

  document.getElementById("logout-btn").addEventListener("click", logout);

  const menuBtn = document.getElementById("mobile-menu-btn");
  const sidebar = document.getElementById("app-sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  const closeMenu = () => { sidebar.classList.remove("open"); backdrop.classList.remove("open"); };
  if (menuBtn) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      backdrop.classList.toggle("open");
    });
  }
  backdrop.addEventListener("click", closeMenu);
  sidebar.querySelectorAll(".nav-link").forEach((a) => a.addEventListener("click", closeMenu));
}

async function initAppPage(activePage) {
  const user = await requireAuth();
  if (!user) return null;
  renderShell(activePage, user);
  if (typeof startReminders === "function") startReminders();
  if (typeof startReminders === "function") startReminders();
  return user;
}

// ---- Formatting helpers ------------------------------------------------------------

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDate(isoDate, opts = { month: "short", day: "numeric" }) {
  if (!isoDate) return "";
  const d = new Date(isoDate.length <= 10 ? `${isoDate}T00:00:00` : isoDate);
  return d.toLocaleDateString(undefined, opts);
}

function todayISO() {
  const d = new Date();
  const off = d.getTimezoneOffset();
  return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10);
}

function debounce(fn, wait = 250) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function setFormError(el, message) {
  if (!el) return;
  if (message) {
    el.textContent = message;
    el.classList.add("visible");
  } else {
    el.textContent = "";
    el.classList.remove("visible");
  }
}

