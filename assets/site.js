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
    ["Stages", "/stages/", "stages"],
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

  /* ---------------- firmware download gate (Web3Forms, then the file downloads) ----------------
     <a data-bx-download="kali">  opens the gate for that product (no value = bribeluge). Each product's
     latest.json says which file is current; scripts/bribeluge_bin.py and scripts/kali_zip.py write them. */
  var PRODUCTS = {
    bribeluge: { name: "Bribeluge", json: "/bribeluge/download/latest.json", install: "/bribeluge/#install",
      ver: function (i) { return "v" + i.version; }, note: "Unofficial firmware: use it at your own risk and back up your SD card first." },
    kali: { name: "KALI SMASH", json: "/kali/download/latest.json", install: "/kali/#install",
      ver: function (i) { return i.version; }, note: "Unofficial firmware: use it at your own risk. Back to stock any time with Kali's own v2.22 image." }
  };
  var dls = {}, latests = {};
  var DL_SAVED = "bribery-download-details";
  function product(key) { return PRODUCTS[key] ? key : "bribeluge"; }
  function getLatest(key) {
    key = product(key);
    if (!latests[key]) latests[key] = fetch(PRODUCTS[key].json, { cache: "no-cache" }).then(function (r) { return r.json(); });
    return latests[key];
  }
  function startDownload(info) {
    var a = document.createElement("a");
    a.href = info.file; a.download = info.name; a.rel = "noopener";
    document.body.appendChild(a); a.click(); a.remove();
  }
  function downloadModal(key) {
    key = product(key);
    if (dls[key]) return dls[key];
    var P = PRODUCTS[key], id = "bxDl" + key;
    var dl = dls[key] = el("div", { "class": "bx-modal", role: "dialog", "aria-modal": "true", "aria-labelledby": id + "Title" },
      '<form class="bx-dialog" novalidate>' +
      '<button type="button" class="bx-close" aria-label="Close">&times;</button>' +
      '<h3 id="' + id + 'Title">Download ' + P.name + '</h3>' +
      '<p>Free. Tell me who you are and the download starts straight after.</p>' +
      '<label for="' + id + 'Name">Name</label><input id="' + id + 'Name" name="name" autocomplete="name" required>' +
      '<label for="' + id + 'Email">Email</label><input id="' + id + 'Email" name="email" type="email" autocomplete="email" required>' +
      '<label for="' + id + 'Artist">Artist name (optional)</label><input id="' + id + 'Artist" name="artist_name" autocomplete="off">' +
      '<label for="' + id + 'Music">Link to your music (optional, so I can check it out)</label><input id="' + id + 'Music" name="music_link" type="url" inputmode="url" placeholder="Spotify, SoundCloud, Bandcamp, YouTube, Instagram...">' +
      '<input type="checkbox" name="botcheck" class="bx-hp" tabindex="-1" autocomplete="off">' +
      '<p class="bx-dl-promise">I\'ll only ever contact you about updates to ' + P.name + ' and other creative projects or tech builds.</p>' +
      '<p class="bx-dl-note">' + P.note + '</p>' +
      '<div class="bx-ctas"><button class="bx-btn bx-solid" type="submit">Download <span class="bx-dl-ver"></span></button></div>' +
      '<div class="bx-status" role="status"></div></form>');
    dl.setAttribute("data-product", key);
    document.body.appendChild(dl);
    var form = dl.querySelector("form"), status = dl.querySelector(".bx-status"), go = form.querySelector("button[type=submit]");
    function close() { dl.classList.remove("bx-open"); }
    dl.querySelector(".bx-close").addEventListener("click", close);
    dl.addEventListener("click", function (e) { if (e.target === dl) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    try {
      var saved = JSON.parse(localStorage.getItem(DL_SAVED) || "null");
      if (saved) ["name", "email", "artist_name", "music_link"].forEach(function (k) { if (saved[k]) form[k].value = saved[k]; });
    } catch (e) {}
    getLatest(key).then(function (info) { dl.querySelector(".bx-dl-ver").textContent = P.ver(info); }).catch(function () {});

    function done(info, sent) {
      status.className = "bx-status bx-ok";
      status.innerHTML = (sent ? "Thanks! " : "") + "Your download of " + P.name + " " + P.ver(info) + " is starting. " +
        '<a href="' + info.file + '" download="' + info.name + '">Didn\'t start? Download it here.</a>' +
        '<br><a href="' + P.install + '">How to install &rarr;</a>';
      go.disabled = false;
      startDownload(info);
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "bx-status";
      var music = form.music_link.value.trim();
      if (music && !/^https?:\/\//i.test(music)) { music = "https://" + music; form.music_link.value = music; }
      if (!form.name.value.trim() || !/^\S+@\S+\.\S+$/.test(form.email.value.trim())) {
        status.className = "bx-status bx-bad"; status.textContent = "Add your name and a valid email."; return;
      }
      if (music && !/^https?:\/\/\S+\.\S+/.test(music)) {
        status.className = "bx-status bx-bad"; status.textContent = "That music link doesn't look right. Fix it or leave it blank."; return;
      }
      try { localStorage.setItem(DL_SAVED, JSON.stringify({ name: form.name.value.trim(), email: form.email.value.trim(),
        artist_name: form.artist_name.value.trim(), music_link: music })); } catch (e2) {}
      go.disabled = true; status.textContent = "Sending...";
      getLatest(key).then(function (info) {
        if (!CONFIG.web3formsKey) return done(info, false);
        var data = new FormData(form);
        data.append("access_key", CONFIG.web3formsKey);
        data.append("subject", P.name + " download " + P.ver(info) + ": " + (form.artist_name.value.trim() || form.name.value.trim()));
        data.append("from_name", "thisisbribery.com");
        data.append("firmware", P.name + " " + P.ver(info));
        return fetch("https://api.web3forms.com/submit", { method: "POST", body: data })
          .then(function (r) { return r.json(); })
          .then(function (j) { done(info, !!(j && j.success)); })
          // never hold the firmware back because the form service hiccuped
          .catch(function () { done(info, false); });
      }).catch(function () {
        go.disabled = false; status.className = "bx-status bx-bad"; status.textContent = "Couldn't find the download. Try again in a minute.";
      });
    });
    return dl;
  }
  function openDownload(key) {
    var dl = downloadModal(key);
    dl.classList.add("bx-open");
    setTimeout(function () { dl.querySelector("input[name=name]").focus(); }, 30);
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
    document.addEventListener("click", function (e) {
      var t = e.target.closest && e.target.closest("[data-bx-beta]");
      if (t) { e.preventDefault(); openBeta(t.getAttribute("data-bx-beta")); }
      var d = e.target.closest && e.target.closest("[data-bx-download]");
      if (d) { e.preventDefault(); openDownload(d.getAttribute("data-bx-download")); }
    });
    setMode(root.getAttribute("data-mode"), false);
    fitAll();
    // fitting the big titles moves the page, so land on #section links again afterwards
    if (location.hash.length > 1 && !/^#bx-/.test(location.hash)) {
      var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (target) requestAnimationFrame(function () { target.scrollIntoView({ behavior: "instant", block: "start" }); });
    }
    addEventListener("resize", fitAll);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", ready); else ready();

  window.BRIBERY = { config: CONFIG, setMode: function (m) { setMode(m, true); }, openBeta: openBeta, openDownload: openDownload, fit: fitAll };
})();
