"""Bundle the latest KALI SMASH release for the site's download gate.

    python3 scripts/kali_zip.py [path/to/kaliv1]

Default repo: ~/dev/kaliv1. Takes the single KaliSmash-*.bin in release/, plus the Daisy bootloader, its
MIT licence, the KALI SMASH and libDaisy licences and tools/flash-kali.sh (and copies LICENSE.md to kali/LICENSE.txt), and writes kali/download/KaliSmash-<version>.zip and latest.json.
Older zips are removed. Run it on every KALI SMASH release, then push the site.
"""
import hashlib, json, os, pathlib, re, sys, zipfile, time

SITE = pathlib.Path(__file__).resolve().parents[1]
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/dev/kaliv1"))
rel = REPO / "release"
bins = sorted(rel.glob("KaliSmash-*.bin"))
if len(bins) != 1:
    sys.exit(f"expected one KaliSmash-*.bin in {rel}, found {[b.name for b in bins]}")
app = bins[0]
boot = rel / "dsy_bootloader_v6_4-intdfu-2000ms.bin"
lic = rel / "LICENSE-DaisyBootloader.txt"
script = REPO / "tools" / "flash-kali.sh"
kali_lic = REPO / "LICENSE.md"
daisy_lic = rel / "LICENSE-libDaisy.txt"
for f in (boot, lic, script, kali_lic, daisy_lic):
    if not f.exists():
        sys.exit(f"missing {f}")
tag = app.stem.replace("KaliSmash-", "")                     # e.g. phase4-test4
m = re.match(r"phase(\d+)-test(\d+)", tag)
label = f"beta {m.group(1)}.{m.group(2)}" if m else tag      # e.g. beta 4.4

install = f"""KALI SMASH {label} ({app.name})
Alternative firmware for the dsp.coffee Kali. Full guide: https://www.thisisbribery.com/kali/

KALI SMASH runs under the Daisy bootloader (v6.4, built-in USB, 2000 ms), included here.
Use a USB DATA cable, plugged straight into the computer (no hub).

MAC: FIRST INSTALL (from stock Kali or anything older)
  1. Install dfu-util once:  brew install dfu-util
  2. In Terminal, in this folder:  ./flash-kali.sh --first {app.name}
  3. When it asks: hold BOOT, press and release RESET, release BOOT.
     It installs the bootloader, catches it as it starts and installs KALI SMASH.

MAC: UPDATES
  ./flash-kali.sh {app.name}
  While it waits, press RESET on the Daisy board (no BOOT), or on the module: SYSTEM > UPDATE, turn to GO.

ANY COMPUTER, IN THE BROWSER (updates, once KALI SMASH or the Daisy bootloader is installed)
  1. On the module: SYSTEM > UPDATE, turn to GO. It waits for an upload.
  2. In Chrome, open https://flash.daisy.audio and choose File Upload.
  3. Pick {app.name} and the "Daisy Bootloader" device (not "DFU in FS Mode").

BACK TO STOCK
  Flash Kali's v2.22 image the factory way (hold BOOT, tap RESET, File Upload, "DFU in FS Mode").
  That also removes the Daisy bootloader.

Unofficial firmware. Use it at your own risk. Not made or supported by dsp.coffee or Electrosmith.
The Daisy bootloader is Electrosmith's, MIT licensed (LICENSE-DaisyBootloader.txt).

LICENCE
  KALI SMASH is licensed under the PolyForm Noncommercial License 1.0.0 plus additional permissions
  (LICENSE.txt, also at https://www.thisisbribery.com/kali/LICENSE.txt). Free for noncommercial use and
  for making and selling music; selling the firmware or pre-flashed modules isn't allowed.
  Required Notice: Copyright 2026 Bribery (https://thisisbribery.com)
  The firmware includes libDaisy, ST and Arm code under their own licences (LICENSE-libDaisy.txt).
  Keep these files with every copy.
"""

out = SITE / "kali" / "download"
out.mkdir(parents=True, exist_ok=True)
zname = f"KaliSmash-{tag}.zip"
for old in out.glob("*.zip"):
    if old.name != zname:
        old.unlink()
folder = f"KaliSmash-{tag}"
stamp = time.localtime(app.stat().st_mtime)[:6]
with zipfile.ZipFile(out / zname, "w", zipfile.ZIP_DEFLATED) as z:
    def add(name, data, mode=0o644):
        zi = zipfile.ZipInfo(f"{folder}/{name}", date_time=stamp)
        zi.external_attr = (0o100000 | mode) << 16
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, data)
    add(app.name, app.read_bytes())
    add(boot.name, boot.read_bytes())
    add(lic.name, lic.read_bytes())
    add("LICENSE.txt", kali_lic.read_bytes())
    add(daisy_lic.name, daisy_lic.read_bytes())
    add("flash-kali.sh", script.read_bytes(), 0o755)
    add("INSTALL.txt", install)
(SITE / "kali" / "LICENSE.txt").write_bytes(kali_lic.read_bytes())
data = (out / zname).read_bytes()
(out / "latest.json").write_text(json.dumps({
    "version": label,
    "file": f"/kali/download/{zname}",
    "name": zname,
    "bytes": len(data),
    "sha256": hashlib.sha256(data).hexdigest(),
    "app": app.name,
    "app_sha256": hashlib.sha256(app.read_bytes()).hexdigest(),
}, indent=2) + "\n")
print(f"KALI SMASH {label}: {zname} ({len(data)//1024} KB), app {app.name}")
