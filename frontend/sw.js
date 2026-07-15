// Minimal service worker: enables installability + lets Notification API
// show reminders reliably (some mobile browsers require an active SW
// registration for notifications to appear consistently).

const CACHE = "habit-tracker-shell-v1";
const SHELL_ASSETS = [
  "css/main.css",
  "js/app.js",
  "js/config.js",
  "js/reminders.js",
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {})
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first for API/HTML, cache-first for static shell assets.
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || !SHELL_ASSETS.some((a) => url.pathname.endsWith(a))) {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});

// Clicking a reminder notification focuses/opens the habits page.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if ("focus" in client) return client.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow("habits.html");
    })
  );
});
