"""Build a gh-pages redirect bundle for each old thisisbribery.github.io tool.
Each bundle: index.html and 404.html (same redirect page), .nojekyll, README.md, and for the
Companion a sw.js that unregisters the old installed app's service worker."""
import pathlib, sys

OUT = pathlib.Path(__file__).parent / "out"
SITES = {
    "SealEggs_v1":           ("Seal Eggs", "https://www.thisisbribery.com/sealeggs/"),
    "stolperbeats-ultra-v1": ("STOLPERBEATS ULTRA", "https://www.thisisbribery.com/stolperbeats/"),
    "stolperbeats_v2":       ("Stolperbeats visualiser", "https://www.thisisbribery.com/stolperbeats/visualiser/"),
    "stolperbeats_v1":       ("Stolperbeats visualiser", "https://www.thisisbribery.com/stolperbeats/visualiser/"),
    "bribes-companion":      ("Bribeluge Companion", "https://www.thisisbribery.com/bribeluge/companion/"),
}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} has moved</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="3;url={target}">
<script>
(function () {{
  var TARGET = "{target}";
  // Carry this browser's saved tool data (custom Timings, banks, Companion settings) to the new site once.
  // It travels in the URL fragment, which is never sent to any server.
  var frag = "";
  try {{
    var data = {{}}, n = 0;
    for (var i = 0; i < localStorage.length; i++) {{
      var k = localStorage.key(i);
      if (/^(stolperbeats-|bribeluge-|sealeggs-)/.test(k)) {{ data[k] = localStorage.getItem(k); n++; }}
    }}
    if (n) {{
      var bytes = new TextEncoder().encode(JSON.stringify(data)), bin = "";
      for (var j = 0; j < bytes.length; j += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(j, j + 0x8000));
      var b64 = btoa(bin).replace(/\\+/g, "-").replace(/\\//g, "_").replace(/=+$/, "");
      if (b64.length < 1500000) frag = "#bx-import=" + b64;
    }}
  }} catch (e) {{}}
  function go() {{ location.replace(TARGET + location.search + frag); }}
  // Retire the old installed Companion app's offline copy, then go.
  var jobs = [];
  try {{
    if ("serviceWorker" in navigator) jobs.push(navigator.serviceWorker.getRegistrations().then(function (rs) {{
      return Promise.all(rs.map(function (r) {{ return r.unregister(); }}));
    }}));
    if (window.caches) jobs.push(caches.keys().then(function (ks) {{
      return Promise.all(ks.filter(function (k) {{ return k.indexOf("bribes-companion-") === 0; }}).map(function (k) {{ return caches.delete(k); }}));
    }}));
  }} catch (e) {{}}
  Promise.race([Promise.all(jobs), new Promise(function (r) {{ setTimeout(r, 800); }})]).then(go, go);
}})();
</script>
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#000;color:#f4f1ec;font:17px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;text-align:center;padding:24px;box-sizing:border-box}}
h1{{margin:0 0 10px;font-weight:900;font-size:clamp(34px,8vw,72px);line-height:.9;letter-spacing:-.04em;text-transform:uppercase;color:#ff1fd6}}
a{{color:#ff1fd6}}
</style>
</head>
<body>
<main>
  <h1>{name} has moved</h1>
  <p>It now lives at <a href="{target}">{target}</a>{extra}</p>
</main>
</body>
</html>
"""

KILL_SW = """// The Bribeluge Companion moved to https://www.thisisbribery.com/bribeluge/companion/ .
// This replaces the old app's service worker: it removes itself and its offline copy, then reloads
// open windows, which land on the redirect page.
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k.indexOf("bribes-companion-") === 0; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.registration.unregister(); })
    .then(function () { return self.clients.matchAll({ type: "window" }); })
    .then(function (cs) { cs.forEach(function (c) { c.navigate(c.url); }); }));
});
"""

for repo, (name, target) in SITES.items():
    d = OUT / repo
    d.mkdir(parents=True, exist_ok=True)
    extra = ". If you installed it as an app, open the new address and add it to your home screen again." if repo == "bribes-companion" else "."
    page = PAGE.format(name=name, target=target, extra=extra)
    (d / "index.html").write_text(page)
    (d / "404.html").write_text(page)
    (d / ".nojekyll").write_text("")
    (d / "README.md").write_text(f"# {name} has moved\n\nThis branch only serves a redirect for the old GitHub Pages address. "
                                 f"The page now lives at {target}\n\nThe source is on the `main` branch.\n")
    if repo == "bribes-companion":
        (d / "sw.js").write_text(KILL_SW)
    print(repo, "->", target)
