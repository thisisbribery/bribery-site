/* BRIBERY shared shell: config, classic/new mode, top bar, footer, beta tester form.
   Load it in <head> AFTER the page's <style> blocks:  <script src="/assets/site.js"></script>
   Two-mode pages mark their stylesheets with data-bx="classic" and data-bx="new". */
(function () {
  "use strict";

  /* ---------------- config: edit these ---------------- */
  var CONFIG = {
    // Web3Forms access key for the beta tester form (web3forms.com, sent to thisisbribery@gmail.com).
    web3formsKey: "4e024aad-8c40-4732-9a2e-40663e62af45",
    // Buy Me a Coffee / Ko-fi page. Leave empty to hide every Support button.
    supportUrl: "https://ko-fi.com/thisisbribery",
    links: {
      instagram: "https://www.instagram.com/thisisbribery/",
      youtube: "https://www.youtube.com/@briberysproductionhouse",
      spotify: "https://open.spotify.com/artist/2icKus0gqgPVjAtHFM0e7N",
      github: "https://github.com/thisisbribery"
    }
  };
  var NAV = [
    ["Bribeluge", "/bribeluge/", "bribeluge"],
    ["Companion", "/companion/", "companion"],
    ["Seal Eggs", "/sealeggs/", "sealeggs"],
    ["Stolperbeats", "/stolperbeats/", "stolperbeats"],
    ["Bribestages", "/bribestages/", "stages"],
    ["Kali Smash", "/kali/", "kali"],
    ["Music", "/#music", "music"],
    ["Learn", "/#learn", "learn"]
  ];

  /* ---------------- one-time import from the old github.io tools ----------------
     The old thisisbribery.github.io pages redirect here with their saved browser data in the URL
     fragment (#bx-import=...). Fragments never reach the server. Only the tools' own keys are
     accepted, and nothing already saved on this site is overwritten. */
  (function importOld() {
    var m = /^#bx-import=([A-Za-z0-9_-]+)/.exec(location.hash);
    if (!m) return;
    try {
      var b64 = m[1].replace(/-/g, "+").replace(/_/g, "/");
      while (b64.length % 4) b64 += "=";
      var bin = atob(b64), bytes = new Uint8Array(bin.length);
      for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      var data = JSON.parse(new TextDecoder().decode(bytes));
      Object.keys(data).forEach(function (k) {
        if (!/^(stolperbeats-|bribeluge-|sealeggs-)/.test(k) || typeof data[k] !== "string") return;
        if (localStorage.getItem(k) === null) localStorage.setItem(k, data[k]);
      });
    } catch (e) {}
    try { history.replaceState(null, "", location.pathname + location.search); } catch (e) {}
  })();

  var root = document.documentElement;
  var KEY = "bribery-mode";
  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  /* ---------------- mode (runs immediately, before paint) ---------------- */
  function sheets(which) { return document.querySelectorAll('[data-bx="' + which + '"]'); }
  var twoMode = sheets("classic").length > 0;
  function setMode(m, save) {
    if (!twoMode) m = "new";
    root.setAttribute("data-mode", m);
    Array.prototype.forEach.call(sheets("classic"), function (s) { s.media = m === "classic" ? "all" : "not all"; });
    Array.prototype.forEach.call(sheets("new"), function (s) { s.media = m === "new" ? "all" : "not all"; });
    Array.prototype.forEach.call(document.querySelectorAll(".bx-mode button"), function (b) {
      b.setAttribute("aria-pressed", String(b.getAttribute("data-m") === m));
    });
    if (save) store(m);
    if (document.body) fitAll();
    try { window.dispatchEvent(new CustomEvent("bx-mode", { detail: m })); } catch (e) {}
  }
  setMode(stored() === "classic" ? "classic" : "new", false);

  /* ---------------- helpers ---------------- */
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in attrs) if (attrs.hasOwnProperty(k)) e.setAttribute(k, attrs[k]);
    if (html != null) e.innerHTML = html;
    return e;
  }
  var COIN = '<span class="bx-coin" aria-hidden="true"><span class="bx-coin-inner"><img src="/assets/coin-front.png" alt="">' +
    '<span class="bx-edge"></span><img class="bx-back" src="/assets/coin-back.png" alt=""></span></span>';
  function modeToggle(extraClass) {
    var cur = root.getAttribute("data-mode");
    var w = el("div", { "class": "bx-mode " + (extraClass || ""), role: "group", "aria-label": "Page style" },
      '<button type="button" data-m="new" aria-pressed="' + (cur === "new") + '">New</button>' +
      '<button type="button" data-m="classic" aria-pressed="' + (cur === "classic") + '">Classic</button>');
    w.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (b) setMode(b.getAttribute("data-m"), true);
    });
    return w;
  }

  /* ---------------- top bar + footer ---------------- */
  function buildTop(page) {
    var top = el("header", { "class": "bx-top" });
    top.appendChild(el("a", { "class": "bx-brand", href: "/" }, COIN + "<span><b>BRIBERY</b><small>@thisisbribery</small></span>"));
    var nav = el("nav", { "class": "bx-nav", "aria-label": "Site" });
    NAV.forEach(function (n) {
      var a = el("a", { href: n[1] }, n[0]);
      if (n[2] === page) a.setAttribute("aria-current", "page");
      nav.appendChild(a);
    });
    top.appendChild(nav);
    if (twoMode) top.appendChild(modeToggle(""));
    return top;
  }
  function buildFoot() {
    var L = CONFIG.links;
    var sup = CONFIG.supportUrl ? ' &middot; <a href="' + CONFIG.supportUrl + '" target="_blank" rel="noopener">Support</a>' : "";
    return el("footer", { "class": "bx-foot" },
      '<a class="bx-foot-word" href="/">BRIBERY</a><div class="bx-foot-meta">' +
      '<a href="' + L.instagram + '" target="_blank" rel="noopener">Instagram</a> &middot; ' +
      '<a href="' + L.youtube + '" target="_blank" rel="noopener">YouTube</a> &middot; ' +
      '<a href="' + L.spotify + '" target="_blank" rel="noopener">Spotify</a> &middot; ' +
      '<a href="' + L.github + '" target="_blank" rel="noopener">GitHub</a>' + sup +
      '<br>&copy; ' + new Date().getFullYear() + ' Bribery</div>');
  }

  /* ---------------- beta tester form (Web3Forms) ---------------- */
  var modal;
  function betaModal() {
    if (modal) return modal;
    modal = el("div", { "class": "bx-modal", role: "dialog", "aria-modal": "true", "aria-labelledby": "bxBetaTitle" },
      '<form class="bx-dialog" novalidate>' +
      '<button type="button" class="bx-close" aria-label="Close">&times;</button>' +
      '<h3 id="bxBetaTitle">Become a beta tester</h3>' +
      '<p>Test new Bribeluge Companion builds before they go public. Leave your details and I\'ll be in touch.</p>' +
      '<label for="bxName">Name</label><input id="bxName" name="name" autocomplete="name" required>' +
      '<label for="bxEmail">Email</label><input id="bxEmail" name="email" type="email" autocomplete="email" required>' +
      '<label for="bxDevice">Screen you\'d use</label><select id="bxDevice" name="device">' +
      '<option>Android tablet</option><option>Android phone</option><option>Laptop or desktop (Chrome / Edge)</option><option>iPhone or iPad</option><option>Other</option></select>' +
      '<label for="bxMsg">Anything else? (optional)</label><textarea id="bxMsg" name="message" placeholder="Firmware version, what you\'d like to test..."></textarea>' +
      '<input type="checkbox" name="botcheck" class="bx-hp" tabindex="-1" autocomplete="off">' +
      '<div class="bx-ctas"><button class="bx-btn bx-solid" type="submit">Send</button></div>' +
      '<div class="bx-status" role="status"></div></form>');
    document.body.appendChild(modal);
    var form = modal.querySelector("form"), status = modal.querySelector(".bx-status");
    function close() { modal.classList.remove("bx-open"); }
    modal.querySelector(".bx-close").addEventListener("click", close);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "bx-status";
      if (!form.name.value.trim() || !/^\S+@\S+\.\S+$/.test(form.email.value.trim())) {
        status.className = "bx-status bx-bad"; status.textContent = "Add your name and a valid email."; return;
      }
      if (!CONFIG.web3formsKey) {
        status.className = "bx-status bx-bad"; status.textContent = "Sign-ups open soon. Check back shortly."; return;
      }
      var data = new FormData(form);
      data.append("access_key", CONFIG.web3formsKey);
      data.append("subject", "Bribeluge Companion beta tester: " + form.name.value.trim());
      data.append("from_name", "thisisbribery.com");
      status.textContent = "Sending...";
      fetch("https://api.web3forms.com/submit", { method: "POST", body: data })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j && j.success) { status.className = "bx-status bx-ok"; status.textContent = "You're on the list. Thanks!"; form.reset(); }
          else throw new Error((j && j.message) || "failed");
        })
        .catch(function () { status.className = "bx-status bx-bad"; status.textContent = "That didn't send. Try again in a minute."; });
    });
    return modal;
  }
  function openBeta(device) {
    betaModal().classList.add("bx-open");
    if (device) { var sel = modal.querySelector("#bxDevice"); Array.prototype.forEach.call(sel.options, function (o) { if (o.text === device) sel.value = o.value; }); }
    setTimeout(function () { modal.querySelector("#bxName").focus(); }, 30);
  }

  /* ---------------- firmware sign-up form (Web3Forms), shared by every page ----------------
     One form asks name, email, optional artist and music link, and which firmware mods they want
     (any number). Entry points:
       [data-bx-download="kali"]   download buttons: after the form, that product's file downloads
       [data-bx-gate="sealeggs"]   a flasher's final button: form once per device, then the click goes ahead
       audio[data-bx-gate]         update audio: form once per device, then it plays
       [data-bx-signup="companion"] just the form, with that mod ticked (no value: nothing ticked)
     Each product's latest.json says which file is current (scripts/bribeluge_bin.py, scripts/kali_zip.py). */
  var PRODUCTS = {
    bribeluge: { name: "Bribeluge", dev: "Synthstrom Deluge", json: "/bribeluge/download/latest.json", page: "/bribeluge/", install: "/bribeluge/#install",
      ver: function (i) { return "v" + i.version; } },
    companion: { name: "Bribeluge Companion", dev: "Phone or tablet + Deluge", page: "/companion/", open: "Open the app" },
    sealeggs: { name: "Seal Eggs", dev: "Sealegs", page: "/sealeggs/", open: "Open the flasher" },
    stolperbeats: { name: "Stolperbeats Ultra", dev: "Stolperbeats", page: "/stolperbeats/", open: "Open the flasher" },
    stages: { name: "BRIBESTAGES", dev: "Mutable Instruments Stages", json: "/bribestages/firmware/latest.json", page: "/bribestages/", install: "/bribestages/#update",
      ver: function (i) { return "v" + i.version; } },
    kali: { name: "Kali Smash", dev: "dsp.coffee Kali", json: "/kali/download/latest.json", page: "/kali/", install: "/kali/#install",
      ver: function (i) { return i.version; } }
  };
  var ORDER = ["bribeluge", "companion", "sealeggs", "stolperbeats", "stages", "kali"];
  var latests = {}, gate = null, gateCtx = null;
  var DL_SAVED = "bribery-download-details", REGISTERED = "bribery-registered";
  function registered() { try { return !!localStorage.getItem(REGISTERED); } catch (e) { return false; } }
  function product(key) { return PRODUCTS[key] ? key : "bribeluge"; }
  function getLatest(key) {
    key = product(key);
    if (!PRODUCTS[key].json) return Promise.reject(new Error("no file"));
    if (!latests[key]) latests[key] = fetch(PRODUCTS[key].json, { cache: "no-cache" }).then(function (r) { return r.json(); });
    return latests[key];
  }
  function filesOf(info) { return info.files || [{ label: "", file: info.file, name: info.name }]; }
  function startDownload(f) {
    var a = document.createElement("a");
    a.href = f.file; a.download = f.name || f.file.split("/").pop(); a.rel = "noopener";
    document.body.appendChild(a); a.click(); a.remove();
  }
  function esc2(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function buildGate() {
    if (gate) return gate;
    var checks = ORDER.map(function (k) {
      return '<label class="bx-mod-opt"><input type="checkbox" name="mods" value="' + k + '"><span><b>' + PRODUCTS[k].name + '</b><small>' + PRODUCTS[k].dev + '</small></span></label>';
    }).join("");
    gate = el("div", { "class": "bx-modal", role: "dialog", "aria-modal": "true", "aria-labelledby": "bxGateTitle" },
      '<form class="bx-dialog" novalidate>' +
      '<button type="button" class="bx-close" aria-label="Close">&times;</button>' +
      '<h3 id="bxGateTitle">Get the firmware</h3>' +
      '<p class="bx-gate-lede">Free. Tell me who you are and which mods you\'re after.</p>' +
      '<label for="bxGName">Name</label><input id="bxGName" name="name" autocomplete="name" required>' +
      '<label for="bxGEmail">Email</label><input id="bxGEmail" name="email" type="email" autocomplete="email" required>' +
      '<label for="bxGArtist">Artist name (optional)</label><input id="bxGArtist" name="artist_name" autocomplete="off">' +
      '<label for="bxGMusic">Link to your music (optional, so I can check it out)</label><input id="bxGMusic" name="music_link" type="url" inputmode="url" placeholder="Spotify, SoundCloud, Bandcamp, YouTube, Instagram...">' +
      '<fieldset class="bx-mods"><legend>Which firmware mods do you want? Pick as many as you like</legend>' + checks + '</fieldset>' +
      '<input type="checkbox" name="botcheck" class="bx-hp" tabindex="-1" autocomplete="off">' +
      '<p class="bx-dl-promise">I\'ll only ever contact you about updates to these mods and other creative projects or tech builds.</p>' +
      '<p class="bx-dl-note">Unofficial firmware: use it at your own risk and back up first.</p>' +
      '<div class="bx-ctas"><button class="bx-btn bx-solid" type="submit">Continue</button></div>' +
      '<div class="bx-status" role="status"></div></form>');
    document.body.appendChild(gate);
    var form = gate.querySelector("form"), status = gate.querySelector(".bx-status"), go = form.querySelector("button[type=submit]");
    function close() { gate.classList.remove("bx-open"); }
    gate.querySelector(".bx-close").addEventListener("click", close);
    gate.addEventListener("click", function (e) { if (e.target === gate) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    function chosen() { return Array.prototype.filter.call(form.querySelectorAll("input[name=mods]"), function (c) { return c.checked; }).map(function (c) { return c.value; }); }
    function done(sent, mods) {
      var ctx = gateCtx || {};
      status.className = "bx-status bx-ok";
      var rows = mods.map(function (k) {
        var P = PRODUCTS[k], id = "bxGot-" + k;
        return '<li id="' + id + '"><b>' + P.name + '</b> <span class="bx-got-act">' +
          (P.json ? "&hellip;" : (location.pathname.indexOf(P.page) === 0 ? "you're on its page" : '<a href="' + P.page + '">' + P.open + ' &rarr;</a>')) + '</span></li>';
      }).join("");
      status.innerHTML = (sent ? "Thanks, you're on the list!" : "You're in.") + (ctx.message ? " " + ctx.message : "") + '<ul class="bx-got">' + rows + '</ul>';
      mods.forEach(function (k) {
        var P = PRODUCTS[k]; if (!P.json) return;
        getLatest(k).then(function (info) {
          var links = filesOf(info).map(function (f) {
            return '<a href="' + esc2(f.file) + '" download="' + esc2(f.name || "") + '">Download ' + esc2(f.label ? f.label + " " : "") + P.ver(info) + '</a>';
          }).join(" &middot; ");
          var span = gate.querySelector("#bxGot-" + k + " .bx-got-act");
          if (span) span.innerHTML = links + ' &middot; <a href="' + P.install + '">Install &rarr;</a>';
        }).catch(function () {});
      });
      go.disabled = false;
      if (ctx.onDone) { try { ctx.onDone(); } catch (e) {} }
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "bx-status";
      var music = form.music_link.value.trim(), mods = chosen();
      if (music && !/^https?:\/\//i.test(music)) { music = "https://" + music; form.music_link.value = music; }
      if (!form.name.value.trim() || !/^\S+@\S+\.\S+$/.test(form.email.value.trim())) {
        status.className = "bx-status bx-bad"; status.textContent = "Add your name and a valid email."; return;
      }
      if (music && !/^https?:\/\/\S+\.\S+/.test(music)) {
        status.className = "bx-status bx-bad"; status.textContent = "That music link doesn't look right. Fix it or leave it blank."; return;
      }
      if (!mods.length) { status.className = "bx-status bx-bad"; status.textContent = "Pick at least one firmware mod."; return; }
      try {
        localStorage.setItem(DL_SAVED, JSON.stringify({ name: form.name.value.trim(), email: form.email.value.trim(),
          artist_name: form.artist_name.value.trim(), music_link: music, mods: mods }));
        localStorage.setItem(REGISTERED, String(Date.now()));
      } catch (e2) {}
      if (!CONFIG.web3formsKey) return done(false, mods);
      go.disabled = true; status.textContent = "Sending...";
      var names = mods.map(function (k) { return PRODUCTS[k].name; });
      var data = new FormData(form);
      data.delete("mods");
      data.append("firmware_mods", names.join(", "));
      data.append("page", location.pathname);
      data.append("access_key", CONFIG.web3formsKey);
      data.append("subject", "Firmware sign-up: " + names.join(" + ") + " (" + (form.artist_name.value.trim() || form.name.value.trim()) + ")");
      data.append("from_name", "thisisbribery.com");
      fetch("https://api.web3forms.com/submit", { method: "POST", body: data })
        .then(function (r) { return r.json(); })
        .then(function (j) { done(!!(j && j.success), mods); })
        // never hold the firmware back because the form service hiccuped
        .catch(function () { done(false, mods); });
    });
    return gate;
  }
  // ctx: { product, onDone, message, lede }
  function openGate(ctx) {
    buildGate(); gateCtx = ctx || {};
    var form = gate.querySelector("form"), saved = null;
    try { saved = JSON.parse(localStorage.getItem(DL_SAVED) || "null"); } catch (e) {}
    if (saved) ["name", "email", "artist_name", "music_link"].forEach(function (k) { if (saved[k]) form[k].value = saved[k]; });
    var pre = (saved && saved.mods) || [];
    Array.prototype.forEach.call(form.querySelectorAll("input[name=mods]"), function (c) {
      c.checked = c.value === gateCtx.product || pre.indexOf(c.value) >= 0;
    });
    gate.querySelector(".bx-gate-lede").textContent = gateCtx.lede || "Free. Tell me who you are and which mods you're after.";
    var st = gate.querySelector(".bx-status"); st.className = "bx-status"; st.textContent = "";
    gate.classList.add("bx-open");
    setTimeout(function () { form.querySelector("input[name=name]").focus(); }, 30);
  }
  // download buttons: the form, then that product's file (or the file the button points at)
  function openDownload(key, el) {
    key = product(key);
    var href = el && el.getAttribute("href");
    var direct = href && /\.(bin|zip|wav)$/i.test(href) ? { file: href, name: el.getAttribute("download") || href.split("/").pop() } : null;
    openGate({ product: key, lede: "Free. Tell me who you are and which mods you're after. Your download starts straight after.",
      onDone: function () {
        if (direct) return startDownload(direct);
        getLatest(key).then(function (info) { startDownload(filesOf(info)[0]); }).catch(function () {});
      } });
  }

  /* ---------------- fit .bx-fit text to its .bx-mega container ---------------- */
  function fitAll() {
    Array.prototype.forEach.call(document.querySelectorAll(".bx-mega[data-fit]"), function (h) {
      var f = h.querySelector(".bx-fit"); if (!f) return;
      h.style.fontSize = "100px";
      var w = f.getBoundingClientRect().width;
      if (w > 0) h.style.fontSize = (100 * h.clientWidth / w * 0.995) + "px";
    });
  }

  /* ---------------- glitch scrolling bands ([data-bx-glitch]) ---------------- */
  function glitchBands() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-bx-glitch]"), function (band) {
      var track = band.firstElementChild; if (!track || band.classList.contains("bx-glitch-band")) return;
      band.classList.add("bx-glitch-band");
      var tracks = [track];
      ["g1", "g2"].forEach(function (g) {
        var ghost = document.createElement("div");
        ghost.className = "bx-glitch-ghost " + g; ghost.setAttribute("aria-hidden", "true");
        var t = track.cloneNode(true); ghost.appendChild(t); band.appendChild(ghost); tracks.push(t);
      });
      // restart every copy of the scroll together so the ghosts sit exactly on the real text
      tracks.forEach(function (t) { t.style.animation = "none"; });
      void band.offsetWidth;
      tracks.forEach(function (t) { t.style.animation = ""; });
    });
  }

  /* ---------------- wire up after the DOM is ready ---------------- */
  function ready() {
    var body = document.body, page = body.getAttribute("data-bx-page") || "";
    if (!body.hasAttribute("data-bx-no-top")) body.insertBefore(buildTop(page), body.firstChild);
    if (twoMode) body.appendChild(modeToggle("bx-mode-float bx-classic-only"));
    if (body.hasAttribute("data-bx-foot")) body.appendChild(buildFoot());
    Array.prototype.forEach.call(document.querySelectorAll("[data-bx-link]"), function (a) {
      var u = CONFIG.links[a.getAttribute("data-bx-link")]; if (u) a.href = u;
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-bx-support]"), function (a) {
      if (CONFIG.supportUrl) a.href = CONFIG.supportUrl; else a.style.display = "none";
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-bx-bin-version]"), function (v) {
      var key = product(v.getAttribute("data-bx-bin-version"));
      getLatest(key).then(function (info) { v.textContent = PRODUCTS[key].ver(info); }).catch(function () {});
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-bx-support-block]"), function (b) {
      if (!CONFIG.supportUrl) b.style.display = "none";
    });
    // a flasher's final button: the form once per device, then the click goes ahead
    document.addEventListener("click", function (e) {
      var g = e.target.closest && e.target.closest("[data-bx-gate]");
      if (!g || g.tagName === "AUDIO" || g.disabled || g.__bxPass || registered()) return;
      e.preventDefault(); e.stopImmediatePropagation();
      var again = g.getAttribute("data-bx-gate-again");
      openGate({ product: g.getAttribute("data-bx-gate"),
        lede: "Free. Tell me who you are and which mods you're after. " + (again ? "Then flash away." : "Your firmware downloads straight after."),
        message: again ? "Now tap " + again + " again." : "",
        onDone: again ? null : function () { g.__bxPass = true; try { g.click(); } finally { g.__bxPass = false; } } });
    }, true);
    // update audio (BRIBESTAGES): the form once per device, then it plays
    Array.prototype.forEach.call(document.querySelectorAll("audio[data-bx-gate]"), function (a) {
      a.setAttribute("controlsList", "nodownload");
      a.addEventListener("play", function () {
        if (registered()) return;
        a.pause();
        openGate({ product: a.getAttribute("data-bx-gate"), lede: "Free. Tell me who you are and which mods you're after. The update audio plays straight after.",
          onDone: function () { var p = a.play(); if (p && p.catch) p.catch(function () {}); } });
      });
    });
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest("[data-bx-beta]");
      if (t) { e.preventDefault(); openBeta(t.getAttribute("data-bx-beta")); }
      var d = e.target.closest && e.target.closest("[data-bx-download]");
      if (d) { e.preventDefault(); openDownload(d.getAttribute("data-bx-download"), d); }
      var su = e.target.closest && e.target.closest("[data-bx-signup]");
      if (su) { e.preventDefault(); openGate({ product: su.getAttribute("data-bx-signup") }); }
    });
    setMode(root.getAttribute("data-mode"), false);
    fitAll();
    glitchBands();
    // fitting the big titles moves the page, so land on #section links again afterwards
    if (location.hash.length > 1 && !/^#bx-/.test(location.hash)) {
      var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target) requestAnimationFrame(function () { target.scrollIntoView({ behavior: "instant", block: "start" }); });
    }
    addEventListener("resize", fitAll);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready); else ready();

  window.BRIBERY = { config: CONFIG, setMode: function (m) { setMode(m, true); }, openBeta: openBeta, openDownload: openDownload, openGate: openGate, fit: fitAll };
})();
