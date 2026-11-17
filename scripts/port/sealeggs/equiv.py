"""Equivalence test: original Seal Eggs page vs the BRIBERY port in new and classic mode."""
import hashlib, os, json
from playwright.sync_api import sync_playwright
BIN = os.path.expanduser("~/Downloads/Sealegs.1.3.5.0.bin")
DL = os.environ.get("EQUIV_DL", "/tmp/sealeggs-equiv-downloads")
os.makedirs(DL, exist_ok=True)
ORDER_OFF = ["seal_micro", "seal_beads", "reverse", "digi_doppler", "char", "tape_pickup", "bbd_light", "tape_bright"]
ALL = set(ORDER_OFF)
COMBOS = [
    ("all-off", set()),
    ("all-on", ALL),
    ("page default", None),
    ("Seal Beads alone", {"seal_beads"}),
    ("Seal Microloops alone", {"seal_micro"}),
    ("character only", {"char"}),
    ("Digi doppler only", {"digi_doppler"}),
    ("reverse only", {"reverse"}),
    ("tape pickup + BBD light + tape bright", {"tape_pickup", "bbd_light", "tape_bright"}),
    ("Seal Beads + character + tape bright", {"seal_beads", "char", "tape_bright"}),
]
TARGETS = [("orig", "http://127.0.0.1:8781/", None),
           ("new", "http://127.0.0.1:8791/sealeggs/", "new"),
           ("classic", "http://127.0.0.1:8791/sealeggs/", "classic")]

SET_JS = """([off, want]) => {
  const cb = k => document.querySelector(`input[data-k="${k}"]`);
  for (const k of off) { const c = cb(k); if (!want.includes(k) && c.checked && !c.disabled) { c.checked = false; c.dispatchEvent(new Event('change')); } }
  for (const k of off.slice().reverse()) { const c = cb(k); if (want.includes(k) && !c.checked && !c.disabled) { c.checked = true; c.dispatchEvent(new Event('change')); } }
  return off.filter(k => cb(k).checked);
}"""

results = {}
errors = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for tname, url, mode in TARGETS:
        ctx = b.new_context(accept_downloads=True, viewport={"width": 1280, "height": 900})
        if mode:
            ctx.add_init_script(f"try{{if(!sessionStorage.getItem('seeded')){{localStorage.setItem('bribery-mode','{mode}');sessionStorage.setItem('seeded','1')}}}}catch(e){{}}")
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m, errs=errs: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e, errs=errs: errs.append(str(e)))
        pg.goto(url); pg.wait_for_load_state("networkidle")
        if mode:
            assert pg.evaluate("document.documentElement.getAttribute('data-mode')") == mode
        pg.set_input_files("#file", BIN)
        pg.wait_for_selector("#status.ok")
        # one real pointer click on a row (tape bright), then back, to prove the row layout still toggles
        pg.click(".mod:nth-child(8) h3")
        clicked = pg.evaluate("document.querySelector('input[data-k=tape_bright]').checked")
        pg.click(".mod:nth-child(8) h3")
        clicked_back = pg.evaluate("document.querySelector('input[data-k=tape_bright]').checked")
        results.setdefault("_rowclick", {})[tname] = (clicked, clicked_back)
        for name, want in COMBOS:
            if want is None:
                pg.reload(); pg.wait_for_load_state("networkidle")
                pg.set_input_files("#file", BIN); pg.wait_for_selector("#status.ok")
                state = pg.evaluate("Array.from(document.querySelectorAll('.mod input')).filter(c=>c.checked).map(c=>c.dataset.k)")
            else:
                state = pg.evaluate(SET_JS, [ORDER_OFF, sorted(want)])
            disabled = pg.is_disabled("#buildBtn")
            hint = pg.text_content("#buildHint")
            row = {"state": sorted(state), "hint": hint}
            if disabled:
                row["sha"] = "build blocked (" + hint + ")"
            else:
                pg.click("#buildBtn")
                pg.wait_for_selector("#riskDlg[open]")
                pg.click("#riskAccept")
                pg.wait_for_selector("#resultStatus.ok")
                with pg.expect_download() as d:
                    pg.click("#dlBtn")
                dl = d.value
                path = os.path.join(DL, f"{tname}-{dl.suggested_filename}")
                dl.save_as(path)
                data = open(path, "rb").read()
                row["sha"] = hashlib.sha256(data).hexdigest()
                row["size"] = len(data)
                row["file"] = dl.suggested_filename
                with pg.expect_download() as d2:
                    pg.click("#notesBtn")
                p2 = os.path.join(DL, f"{tname}-{d2.value.suggested_filename}")
                d2.value.save_as(p2)
                row["notes_sha"] = hashlib.sha256(open(p2, "rb").read()).hexdigest()
                row["ref"] = pg.evaluate("(k)=>window.SEAL_EGGS.refs[k]", "".join("1" if k in state else "0" for k in pg.evaluate("window.SEAL_EGGS.keys")))
            results.setdefault(name, {})[tname] = row
        errors[tname] = errs
        ctx.close()

    # mode toggle switches and persists across reload
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page(); errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://127.0.0.1:8791/sealeggs/"); pg.wait_for_load_state("networkidle")
    def snap():
        return pg.evaluate("""({mode: document.documentElement.dataset.mode,
          classicOn: document.querySelector('style[data-bx=classic]').media, newOn: document.querySelector('style[data-bx=new]').media,
          top: !!document.querySelector('.bx-top') && getComputedStyle(document.querySelector('.bx-top')).display,
          themeBtn: getComputedStyle(document.getElementById('themeBtn')).display,
          byline: getComputedStyle(document.querySelector('.byline')).display,
          bodyBg: getComputedStyle(document.body).backgroundColor,
          megaFont: getComputedStyle(document.querySelector('.bx-mega')).fontSize,
          float: getComputedStyle(document.querySelector('.bx-mode-float')).display})""")
    toggle = {"start": snap()}
    pg.click(".bx-top .bx-mode button[data-m=classic]"); pg.wait_for_timeout(100)
    toggle["after click Classic"] = snap()
    pg.reload(); pg.wait_for_load_state("networkidle")
    toggle["after reload"] = snap()
    pg.click("#themeBtn"); pg.wait_for_timeout(100)
    toggle["classic theme button"] = pg.evaluate("[document.documentElement.dataset.theme, getComputedStyle(document.body).backgroundColor]")
    pg.click(".bx-mode-float button[data-m=new]"); pg.wait_for_timeout(200)
    toggle["after click New (float)"] = snap()
    pg.reload(); pg.wait_for_load_state("networkidle")
    toggle["after reload 2"] = snap()
    errors["toggle"] = errs
    ctx.close()
    b.close()

json.dump({"results": results, "errors": errors, "toggle": toggle}, open(os.path.join(DL, "..", "equiv.json"), "w"), indent=1)
print("row click (on, back off):", results.pop("_rowclick"))
ok = True
print(f"{'combo':40} {'orig':16} {'new':16} {'classic':16} match ref")
for name, _ in COMBOS:
    r = results[name]
    shas = [r[t]["sha"] for t in ("orig", "new", "classic")]
    states = [r[t]["state"] for t in ("orig", "new", "classic")]
    notes = [r[t].get("notes_sha") for t in ("orig", "new", "classic")]
    same = len(set(shas)) == 1 and len(set(map(tuple, states))) == 1 and len(set(notes)) == 1
    refok = r["orig"].get("ref") in (None, r["orig"]["sha"])
    ok &= same and refok
    print(f"{name:40} {shas[0][:16]:16} {shas[1][:16]:16} {shas[2][:16]:16} {same} {refok}  mods={','.join(states[0])}")
print("ALL MATCH" if ok else "MISMATCH")
print("console errors:", errors)
for k, v in toggle.items(): print(k, v)
