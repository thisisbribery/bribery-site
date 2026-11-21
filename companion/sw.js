// The Companion moved to /bribeluge/companion/launch/ . This replaces the old /companion/ worker so installed
// copies stop serving the old page and follow the redirect. It leaves the caches alone: the new app's worker
// clears the old ones itself.
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(self.registration.unregister().then(function () {
    return self.clients.matchAll({ type: "window" });
  }).then(function (cs) {
    cs.forEach(function (c) { c.navigate(c.url); });
  }));
});
