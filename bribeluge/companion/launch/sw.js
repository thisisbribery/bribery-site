// Offline copy of the app. The page itself comes from the network when it's reachable (so an update shows straight
// away), falling back to the saved copy offline; other files are served from the saved copy and refreshed behind.
// Lives at /bribeluge/companion/launch/ on the BRIBERY site (scope /bribeluge/companion/launch/). The site shell it uses comes from /assets/.
var CACHE = "bribes-companion-v38";
var FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png",
  "/assets/site.css", "/assets/site.js", "/assets/coin-front.png", "/assets/coin-back.png",
  "/assets/favicon-32.png", "/assets/favicon-64.png", "/assets/apple-touch-icon.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }));
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    // Only this app's old caches: the rest of the site may keep its own
    return Promise.all(keys.filter(function (k) { return k !== CACHE && k.indexOf("bribes-companion-") === 0; }).map(function (k) { return caches.delete(k); }));
  }));
  self.clients.claim();
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  var page = e.request.mode === "navigate" || /\/(index\.html)?(\?.*)?$/.test(new URL(e.request.url).pathname);
  if (page) {
    e.respondWith(caches.open(CACHE).then(function (c) {
      return fetch(e.request, { cache: "no-store" }).then(function (res) {
        if (res && res.ok) c.put("index.html", res.clone());
        return res;
      }).catch(function () {
        return c.match("index.html").then(function (hit) { return hit || c.match("./"); });
      });
    }));
    return;
  }
  e.respondWith(caches.open(CACHE).then(function (c) {
    return c.match(e.request, { ignoreSearch: true }).then(function (hit) {
      var fresh = fetch(e.request).then(function (res) {
        if (res && res.ok) c.put(e.request, res.clone());
        return res;
      }).catch(function () { return hit; });
      return hit || fresh;
    });
  }));
});
