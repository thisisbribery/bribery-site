"""Turn gear photos into the site's device images.

    python3 scripts/photos/process.py [name ...]

Reads scripts/photos/originals/<name>.(webp|jpg|png), crops to 16:10 keeping the most of the device,
fades the edges to pure black so it blends into the page, and writes assets/devices/<name>.webp
(1600x1000) and <name>-sm.webp (800x500). Names: deluge, companion, sealegs, stolperbeats, stages, kali.
"""
import pathlib, sys
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE.parents[1]
OUT = SITE / "assets" / "devices"

def best_crop(im, ratio=1.6):
    w, h = im.size
    if w / h > ratio:                      # too wide: crop sides
        cw, ch = round(h * ratio), h
    else:                                  # too tall: crop top/bottom
        cw, ch = w, round(w / ratio)
    g = np.asarray(im.convert("L")).astype(np.float32)
    rows, cols = g.mean(axis=1), g.mean(axis=0)
    # slide the window to keep the most brightness (the device), not the empty backdrop
    def pick(profile, size):
        if len(profile) == size: return 0
        c = np.concatenate([[0], np.cumsum(profile)])
        sums = c[size:] - c[:-size]
        return int(np.argmax(sums))
    top, left = pick(rows, ch), pick(cols, cw)
    return im.crop((left, top, left + cw, top + ch))

def fade(im):
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[:2]
    x = (np.arange(w) + 0.5) / w; y = (np.arange(h) + 0.5) / h
    ss = lambda e0, e1, t: (lambda u: u * u * (3 - 2 * u))(np.clip((t - e0) / (e1 - e0), 0, 1))
    m = ss(0, 0.05, np.minimum(y, 1 - y))[:, None] * ss(0, 0.04, np.minimum(x, 1 - x))[None, :]
    a = a * m[..., None]
    a = np.clip((a - 5) * (255 / 250), 0, 255)   # lift the near-black backdrop to true black
    return Image.fromarray((a + 0.5).astype(np.uint8))

names = sys.argv[1:] or sorted(p.stem for p in (HERE / "originals").iterdir() if not p.stem.endswith("-alt"))
for n in names:
    src = next((HERE / "originals").glob(n + ".*"))
    im = fade(best_crop(Image.open(src).convert("RGB")))
    big = im.resize((1600, 1000), Image.LANCZOS); big.save(OUT / f"{n}.webp", "WEBP", quality=84, method=6)
    sm = im.resize((800, 500), Image.LANCZOS); sm.save(OUT / f"{n}-sm.webp", "WEBP", quality=82, method=6)
    print(f"{n}: {src.name} -> {n}.webp {(OUT / f'{n}.webp').stat().st_size // 1024} KB, {n}-sm.webp {(OUT / f'{n}-sm.webp').stat().st_size // 1024} KB")
