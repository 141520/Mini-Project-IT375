// ─────────────────────────────────────────────────────────────
// Service Worker — BoardGame AI PWA
// ─────────────────────────────────────────────────────────────
const CACHE = "boardgame-ai-v1";
const ASSETS = [
  "/",
  "/static/css/app.css",
  "/static/js/app.js",
  "/static/js/local-db.js",
  "/static/manifest.json"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS).catch(() => {})));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // ไม่แคช API (ต้องการข้อมูลสด)
  if (url.pathname.startsWith("/api/")) return;

  // Stale-While-Revalidate สำหรับ static assets
  if (url.pathname.startsWith("/static/")) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const fetched = fetch(e.request).then(resp => {
          caches.open(CACHE).then(c => c.put(e.request, resp.clone()));
          return resp;
        }).catch(() => cached);
        return cached || fetched;
      })
    );
    return;
  }

  // Network-first สำหรับหน้าเว็บ
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request) || caches.match("/"))
  );
});
