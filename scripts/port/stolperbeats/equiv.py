import sys, asyncio, hashlib, json, os
from playwright.async_api import async_playwright
SP = sys.argv[1]; BIN = sys.argv[2]
DL = os.path.join(SP, "dl"); os.makedirs(DL, exist_ok=True)
PAGES = {"original": ("http://127.0.0.1:8782/", None),
         "site-new": ("http://127.0.0.1:8792/stolperbeats/", "new"),
         "site-classic": ("http://127.0.0.1:8792/stolperbeats/", "classic")}

# uploaded .timing.json (creator export shape: style + 7 stolperbeatsRows, 16 step lengths each)
half = [(16,[4]*8),(20,[6,4,6,4,6,4,6,4]),(24,[7,5,6,6,7,5,6,6]),(28,[9,5,8,6,9,5,8,6]),(32,[10,6,9,7,10,6,9,7]),(36,[12,6,10,8,12,6,10,8]),(16,[5,3,4,4,5,3,4,4])]
TIMING = os.path.join(SP, "wobl.timing.json")
json.dump({"style":"WOBL","stolperbeatsRows":[{"ticksPerBeat":n,"stepLengths":l+l} for n,l in half]}, open(TIMING,"w"))
# a visualiser CREATOR Timing saved in localStorage (same origin as the visualiser)
MINE = [{"key":"MYSW","levels":[{"N":36,"pos":[0,10,18,28,36,46,54,64]},{"N":32,"pos":[0,9,16,25,32,41,48,57]},{"N":24,"pos":[0,7,12,19,24,31,36,43]},
         {"N":28,"pos":[0,10,14,24,28,38,42,52]},{"N":20,"pos":[0,7,10,17,20,27,30,37]},{"N":36,"pos":[0,13,21,28,36,49,57,64]}]}]

ALL = dict(ratchets=True, pitch=True, fill=True, fillcv=True)
COMBOS = [
 ("1 factory tables, all 4 mods", dict(picks={}, mods=ALL)),
 ("2 factory tables, ratchets only", dict(picks={}, mods=dict(ratchets=True,pitch=False,fill=False,fillcv=False))),
 ("3 alt on every button, pitch+fill", dict(picks={"Trip":"HOPP","Shake":"DEEP","Push":"SQEZ","Clave":"CLSTR"}, mods=dict(ratchets=False,pitch=True,fill=True,fillcv=False), recipe=True)),
 ("4 FOLD/Factory Clave/DEEP/SQEZ, all mods", dict(picks={"Trip":"FOLD","Shake":"Factory Clave","Push":"DEEP","Clave":"SQEZ"}, mods=ALL)),
 ("5 uploaded .timing.json on Clave, Trip=Factory Push, no mods", dict(upload=True, picks={"Trip":"Factory Push","Clave":"WOBL"}, mods=dict(ratchets=False,pitch=False,fill=False,fillcv=False))),
 ("6 visualiser Timing (localStorage) on Shake, fill+fillcv", dict(mine=True, picks={"Shake":"MYSW","Push":"Factory Trip"}, mods=dict(ratchets=False,pitch=False,fill=True,fillcv=True))),
 ("7 fillcv picked but fill off (locked), ratchets+pitch, Push=FOLD", dict(picks={"Push":"FOLD"}, mods=dict(ratchets=True,pitch=True,fill=False,fillcv=True))),
 ("8 recipe from #3 opened, then build", dict(open_recipe=True)),
]
SLOTS = ["Trip","Shake","Push","Clave"]
H = lambda b: hashlib.sha256(b).hexdigest()

async def run(b, page_key, combo_key, spec, errs_all, recipe_path):
    url, mode = PAGES[page_key]
    ctx = await b.new_context(viewport={"width":1280,"height":900}, accept_downloads=True)
    init = ""
    if mode: init += f"localStorage.setItem('bribery-mode','{mode}');"
    if spec.get("mine"): init += f"localStorage.setItem('stolperbeats-shuffle-map:mine', {json.dumps(json.dumps(MINE))});"
    if init: await ctx.add_init_script("try{" + init + "}catch(e){}")
    pg = await ctx.new_page(); errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror " + str(e)))
    await pg.goto(url); await pg.wait_for_load_state("load")
    if mode: assert await pg.evaluate("document.documentElement.dataset.mode") == mode
    await pg.set_input_files("#file", BIN); await pg.wait_for_selector("#status.ok")
    if spec.get("upload"):
        await pg.set_input_files("#timingFile", TIMING); await pg.wait_for_selector("#tableStatus.ok")
    if spec.get("open_recipe"):
        await pg.set_input_files("#recipeFile", recipe_path); await pg.wait_for_selector("#tableStatus.ok")
    for slot, v in spec.get("picks", {}).items():
        i = SLOTS.index(slot)
        await pg.locator("#slots select").nth(i).select_option(v)
    if "mods" in spec:
        want = spec["mods"]
        async def setm(k, on):
            cur = await pg.evaluate(f"window.__ultra.sel.{k}")
            if bool(cur) != on: await pg.locator(f".mod:has(input[data-k={k}]) h3").click()
        await setm("fill", True)
        for k in ["ratchets","pitch","fillcv"]: await setm(k, want[k])
        await setm("fill", want["fill"])
    await pg.click("#buildBtn"); await pg.click("#riskAccept")
    await pg.wait_for_selector("#resultStatus.ok", timeout=20000)
    out = {}
    async with pg.expect_download() as d: await pg.click("#dlBtn")
    dl = await d.value; p = os.path.join(DL, f"{page_key}-{combo_key[0]}-{dl.suggested_filename}"); await dl.save_as(p)
    out["name"] = dl.suggested_filename; out["sha"] = H(open(p,"rb").read())
    async with pg.expect_download() as d: await pg.click("#notesBtn")
    n = await d.value; np_ = os.path.join(DL, f"{page_key}-{combo_key[0]}-notes.txt"); await n.save_as(np_); out["notes"] = H(open(np_,"rb").read())
    async with pg.expect_download() as d: await pg.click("#recipeBtn")
    r = await d.value; rp = os.path.join(DL, f"{page_key}-{combo_key[0]}-recipe.json"); await r.save_as(rp); out["recipe"] = H(open(rp,"rb").read()); out["recipe_path"] = rp
    out["status"] = await pg.inner_text("#resultStatus")
    out["mods_state"] = await pg.evaluate("JSON.stringify([window.__ultra.sel, window.__ultra.picks])")
    errs_all[(page_key, combo_key)] = errs
    await ctx.close()
    return out

async def main():
    res = {}; errs = {}; recipe3 = None
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for ck, spec in COMBOS:
            for pk in PAGES:
                res[(pk, ck)] = await run(b, pk, ck, spec, errs, recipe3)
            if spec.get("recipe"): recipe3 = res[("original", ck)]["recipe_path"]
        await b.close()
    allok = True
    print("| Combination | Output file | original sha256 | site new | site classic | notes+recipe+status match |")
    print("|---|---|---|---|---|---|")
    for ck, _ in COMBOS:
        o = res[("original", ck)]; n = res[("site-new", ck)]; c = res[("site-classic", ck)]
        same = lambda f: o[f] == n[f] == c[f]
        okb = same("sha") and same("name")
        extra = same("notes") and same("recipe") and same("status") and same("mods_state")
        allok &= okb and extra
        print(f"| {ck} | {o['name']} | {o['sha'][:16]}... | {'MATCH' if n['sha']==o['sha'] else 'DIFF '+n['sha'][:12]} | {'MATCH' if c['sha']==o['sha'] else 'DIFF '+c['sha'][:12]} | {'yes' if extra else 'NO'} |")
    print("\nfull sha256:"); [print(" ", ck[:2], res[("original",ck)]["sha"]) for ck,_ in COMBOS]
    print("distinct outputs:", len({res[("original",ck)]["sha"] for ck,_ in COMBOS}))
    print("console errors:", {f"{k[0]}/{k[1][:2]}": v for k, v in errs.items() if v} or "none")
    print("ALL MATCH" if allok else "MISMATCH")
asyncio.run(main())
