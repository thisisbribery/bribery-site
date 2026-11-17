#!/usr/bin/env python3
"""Render the device product shots with three.js in headless Chromium.

  python3 render.py                     # all five, previews only (renders/out/<name>.png)
  python3 render.py deluge sealegs      # just these
  python3 render.py --final             # also write ~/dev/bribery-site/assets/devices/<name>.webp and <name>-sm.webp
  python3 render.py deluge --q "rim=10&exp=1.1"   # pass extra URL params to render.html (see the Q.get calls)

companion needs companion_screen.png next to render.html: run shot_companion.py first (it needs the app served
on 127.0.0.1:8796, e.g. `python3 -m http.server 8796 --bind 127.0.0.1` from ~/research/stolperbeats/deluge/companion).

Rendered at 3200 x 2000 and downsampled to 1600 x 1000 (supersampling), then the borders are faded to exact #000
so the image sits on a black page with no visible edge.
"""
import base64, functools, http.server, io, os, sys, threading
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SITE = os.path.expanduser("~/dev/bribery-site/assets/devices")
ALL = ["deluge", "companion", "sealegs", "stolperbeats", "stages", "kali"]
PORT = 8797

# Per-device URL params, tuned by eye
TUNE = {
    "deluge": "",
    "companion": "",
    "sealegs": "",
    "stolperbeats": "",
    "stages": "",
}


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    h.log_message = lambda *a, **k: None
    s = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


def edge_fade(img):
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    x = (np.arange(w) + 0.5) / w
    y = (np.arange(h) + 0.5) / h

    def ss(e0, e1, t):
        t = np.clip((t - e0) / (e1 - e0), 0, 1)
        return t * t * (3 - 2 * t)

    ex = ss(0.0, 0.06, np.minimum(x, 1 - x))
    ey = ss(0.0, 0.08, np.minimum(y, 1 - y))
    # elliptical falloff so the floor fades to black as a soft pool, never showing the frame
    r = np.sqrt(((x[None, :] - 0.5) / 0.5) ** 2 + ((y[:, None] - 0.5) / 0.5) ** 2)
    m = ey[:, None] * ex[None, :] * (1 - ss(0.78, 1.18, r))
    a = a * m[..., None]
    a = np.where(a < 2.5, 0, a)  # crush the last bits of floor glow to true black
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8))


def main():
    args = [a for a in sys.argv[1:]]
    final = "--final" in args
    extra = ""
    if "--q" in args:
        i = args.index("--q"); extra = args[i + 1]; del args[i:i + 2]
    names = [a for a in args if not a.startswith("--")] or ALL
    os.makedirs(OUT, exist_ok=True)
    srv = serve()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
        for n in names:
            pg = b.new_page(viewport={"width": 1600, "height": 1000})
            pg.on("console", lambda m: print("  [console]", m.text) if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: print("  [pageerror]", e))
            q = "&".join(x for x in [f"device={n}", TUNE.get(n, ""), extra] if x)
            pg.goto(f"http://127.0.0.1:{PORT}/render.html?{q}")
            pg.wait_for_function("window.__done === true", timeout=300000)
            err = pg.evaluate("window.__err || null")
            if err:
                print(n, "ERROR", err); pg.close(); continue
            data = pg.evaluate("window.__png")
            pg.close()
            big = Image.open(io.BytesIO(base64.b64decode(data.split(",", 1)[1]))).convert("RGB")
            img = edge_fade(big.resize((1600, 1000), Image.LANCZOS))
            img.save(os.path.join(OUT, f"{n}.png"))
            print(n, "->", os.path.join(OUT, f"{n}.png"))
            if final:
                os.makedirs(SITE, exist_ok=True)
                for suffix, size in (("", (1600, 1000)), ("-sm", (800, 500))):
                    im = img if suffix == "" else img.resize(size, Image.LANCZOS)
                    path = os.path.join(SITE, f"{n}{suffix}.webp")
                    im.save(path, "WEBP", quality=82, method=6)
                    print("  ", path, os.path.getsize(path) // 1024, "KB")
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
