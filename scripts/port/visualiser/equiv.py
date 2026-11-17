"""Drive the same interaction script on the original and on the ported page (new and classic mode), then compare
localStorage, downloaded files and the serialized SVGs."""
import hashlib, io, json, sys, zipfile
from playwright.sync_api import sync_playwright

ORIG = "http://127.0.0.1:8783/"
SITE = "http://127.0.0.1:8793/stolperbeats/visualiser/"
OLD_URL = b"https://thisisbribery.github.io/stolperbeats-ultra-v1/"
NEW_URL = b"https://thisisbribery.com/stolperbeats/"

def svg_click(pg, sel, x, y, drag_to=None):
    """Click (or drag) at viewBox coordinates, so the result doesn't depend on how wide the SVG is drawn."""
    pg.locator(sel).scroll_into_view_if_needed()
    def pt(px, py):
        return pg.evaluate("""([sel,x,y])=>{ const s=document.querySelector(sel), p=s.createSVGPoint(); p.x=x; p.y=y;
            const q=p.matrixTransform(s.getScreenCTM()); return [q.x,q.y]; }""", [sel, px, py])
    a = pt(x, y)
    pg.mouse.move(*a); pg.mouse.down()
    if drag_to:
        for i in range(1, 9):
            b = pt(x + (drag_to[0] - x) * i / 8, y + (drag_to[1] - y) * i / 8)
            pg.mouse.move(*b)
    pg.mouse.up()
    pg.mouse.move(1, 1)

def run(url, mode, log):
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        ctx = b.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True, color_scheme="dark")
        if mode:
            ctx.add_init_script(f"try{{ if(!localStorage.getItem('bribery-mode')) localStorage.setItem('bribery-mode','{mode}'); }}catch(e){{}}")
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append("console:" + m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("pageerror:" + str(e)))
        pg.on("dialog", lambda d: d.accept())
        pg.goto(url); pg.wait_for_timeout(400)
        downloads = {}
        def dl(click_sel, label):
            with pg.expect_download() as di:
                pg.click(click_sel)
            d = di.value
            data = open(d.path(), "rb").read()
            downloads[label] = (d.suggested_filename, data)
        snaps = {}
        def snap(label):
            pg.wait_for_timeout(1200)  # let the dots finish easing to their new places
            snaps[label] = pg.evaluate("""()=>({bar:document.getElementById('bar').outerHTML.replace(/<line x1="[^"]*" x2="[^"]*"( y1="24" y2="260" stroke="var\(--accent\)")/,'<line x1="PLAYHEAD" x2="PLAYHEAD"$1'), beat:document.getElementById('beat').outerHTML,
                tbl:document.getElementById('tbl').outerHTML, ro:document.querySelector('.readout').innerText,
                status:document.getElementById('status').textContent, timing:document.getElementById('timing').outerHTML,
                tabs:document.getElementById('barTabs').outerHTML, trows:document.getElementById('trows').outerHTML,
                strip:document.getElementById('modStrip').outerHTML})""")

        # 1. Timings, Shuffle, Feel, presets, kit, Linear
        pg.click('[data-timing="Shake"]'); pg.click('#detents span:nth-child(4)')
        pg.click('#feels .feel-item:nth-child(3) .lampbtn')
        pg.click('#beats .bbtn:nth-child(6)')
        snap("shake3_flam_funk")
        pg.click('[data-timing="CLSTR"]'); pg.click('#detents span:nth-child(6)')
        pg.click('#kits button:nth-child(3)')   # kit change starts audio
        pg.click('#linear button:nth-child(2)')
        snap("clstr5_linear")
        # 2. your beat: draw on the grid, bar 2, ratchet + pitch
        pg.click('#mine')
        svg_click(pg, '#bar', 300, 82)
        svg_click(pg, '#bar', 420, 120, drag_to=(760, 120))
        pg.click('#barTabs .btab:nth-child(2)')
        svg_click(pg, '#bar', 520, 82)
        pg.click('#toolSeg [data-tool="ratchet"]')
        pg.click('#barTabs .btab:nth-child(1)')
        svg_click(pg, '#bar', 300, 82)
        pg.click('#toolSeg [data-tool="pitch"]')
        svg_click(pg, '#bar', 300, 82, drag_to=(300, 60))
        pg.click('#toolSeg [data-tool="hits"]')
        pg.click('#bar .mute >> nth=2')
        snap("yourbeat")
        dl('#dlMidi', "midi")
        # 3. pattern banks: new bank, pick tiles, send sketch, MODULE mode, encoder, download
        pg.click('#bankCard > summary')
        pg.click('#bankNew')
        pg.click('#trows .trow:nth-child(1) .ptile:nth-child(3)')
        pg.click('#sendSketch')
        pg.click('#trows .trow:nth-child(3) .ptile:nth-child(5)')
        pg.click('#srcSeg [data-src="module"]')
        pg.locator('#modStrip .encw:nth-child(2) button >> nth=1').click()
        svg_click(pg, '#bar', 640, 82)
        snap("module")
        dl('#bankDl', "bank")
        pg.click('#bankNew')
        dl('#bankZip', "bankzip")
        pg.click('#srcSeg [data-src="sketch"]')
        # 4. alt table download
        pg.click('[data-timing="HOPP"]')
        dl('#dlTables', "tables")
        # 5. creator: make, save and export a Timing
        pg.click('#modeSw [data-mode="1"]')
        pg.select_option('#cFrom', 'Shake')
        pg.click('#detents span:nth-child(3)')
        snap("creator_start")
        beat_x = pg.evaluate("""()=>{ const c=[...document.querySelectorAll('#beat circle')].filter(c=>c.getAttribute('r')==='11'); return c.map(c=>+c.getAttribute('cx')); }""")
        svg_click(pg, '#beat', beat_x[1], 74, drag_to=(beat_x[1] + 60, 74))
        pg.click('#detents span:nth-child(5)')
        svg_click(pg, '#beat', pg.evaluate("""()=>[...document.querySelectorAll('#beat circle')].filter(c=>c.getAttribute('r')==='11').map(c=>+c.getAttribute('cx'))[2]"""), 74, drag_to=(500, 74))
        pg.click('#cGrid button:nth-child(4)')
        pg.fill('#cName', 'BRB1')
        pg.click('#cSave')
        snap("creator_saved")
        dl('#cExport', "timingjson")
        # import: the exported Timing back into the creator under a new name, and a bank file from the SD-card zip
        import tempfile, os
        td = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))
        tj = os.path.join(td, "BRB1.timing.json"); open(tj, "wb").write(downloads["timingjson"][1])
        pg.set_input_files('#cFile', tj)
        pg.fill('#cName', 'BRB2'); pg.click('#cSave')
        snap("creator_imported")
        z = zipfile.ZipFile(io.BytesIO(downloads["bankzip"][1])); names = [n for n in z.namelist() if n.startswith("PatternBank")]
        bf = os.path.join(td, "PatternBank007.txt"); open(bf, "wb").write(z.read(names[0]))
        pg.set_input_files('#bankFile', bf)
        snap("bank_imported")
        pg.click('#modeSw [data-mode="0"]')
        pg.click('[data-timing="BRB1"]')
        snap("mine_timing")
        # 6. play for a moment, then stop
        pg.click('#play'); pg.wait_for_timeout(700)
        audio = pg.evaluate("()=>typeof ctx!=='undefined'&&ctx?ctx.state:'none'")
        pg.click('#play'); pg.wait_for_timeout(200)
        pg.click('#ab')
        snap("end")
        ls = pg.evaluate("()=>Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
        b.close()
    ls.pop("bribery-mode", None)
    return dict(errs=errs, downloads=downloads, snaps=snaps, ls=ls, audio=audio)

def norm(data):
    return data.replace(OLD_URL, NEW_URL)

def zip_members(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    return {i.filename: z.read(i.filename) for i in z.infolist()}

def compare(a, b, name):
    ok = True
    print(f"\n=== original vs {name} ===")
    print("errors original:", a["errs"], f"| errors {name}:", b["errs"])
    print("audio state after Play:", a["audio"], "/", b["audio"])
    if b["errs"]: ok = False
    print("localStorage keys:", list(b["ls"].keys()))
    same_ls = a["ls"] == b["ls"]
    print("localStorage identical:", same_ls); ok &= same_ls
    for k in a["downloads"]:
        fa, da = a["downloads"][k]; fb, db = b["downloads"][k]
        ha, hb = hashlib.sha256(da).hexdigest(), hashlib.sha256(db).hexdigest()
        line = f"download {k:10s} {fa:40s} {len(da):6d}B sha256 {ha[:16]} vs {hb[:16]} names_equal={fa==fb}"
        if ha == hb:
            print(line, "IDENTICAL")
        else:
            nz = hashlib.sha256(norm(da)).hexdigest() == hb
            detail = ""
            if da[:2] == b"PK":
                ma, mb = zip_members(da), zip_members(db)
                diffs = [m for m in ma if ma[m] != mb.get(m)]
                normed = [m for m in diffs if norm(ma[m]) == mb.get(m)]
                detail = f" zip members differing: {diffs}; equal after URL swap: {normed}"
                nz = set(ma) == set(mb) and diffs == normed
            print(line, "DIFFERS" + (" only by the ULTRA URL" if nz else " UNEXPECTEDLY") + detail)
            ok &= nz
    for k in a["snaps"]:
        for part in a["snaps"][k]:
            eq = a["snaps"][k][part] == b["snaps"][k][part]
            if not eq:
                print(f"snapshot {k}.{part} DIFFERS"); ok = False
    print("snapshots compared:", len(a["snaps"]), "x", len(next(iter(a["snaps"].values()))), "parts")
    print("RESULT:", "MATCH" if ok else "MISMATCH")
    return ok

if __name__ == "__main__":
    o = run(ORIG, None, "orig")
    n = run(SITE, "new", "new")
    c = run(SITE, "classic", "classic")
    r1 = compare(o, n, "site NEW mode")
    r2 = compare(o, c, "site CLASSIC mode")
    # keep the bar SVG for the record
    json.dump({k: {"orig": o["snaps"][k]["bar"][:200]} for k in o["snaps"]}, open(sys.path[0] + "/snap_heads.json", "w"))
    sys.exit(0 if r1 and r2 else 1)
