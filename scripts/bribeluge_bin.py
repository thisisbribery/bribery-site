"""Publish the latest Bribeluge firmware and its presets to the site's download gate.

    python3 scripts/bribeluge_bin.py [path/to/deluge-bribes-v1]

Default repo: ~/research/deluge-bribes-v1 (public repo clone). Takes the single .bin in its firmware/
folder and the preset folders in presets/, and writes into bribeluge/download/:

  Bribeluge-v<version>.zip      the .bin, PRESETS/KITS and PRESETS/SYNTHS, INSTALL.txt and the GPL licence
  deluge-bribes-v<version>.bin  the firmware on its own, for updates
  latest.json                   what the gate reads: the zip first (it downloads after the form), then the .bin

Older bins and zips there are removed. Run it on every release, and whenever the presets change, then push.
The zip is built the same way each time, so a rerun with nothing changed leaves no diff.
"""
import hashlib, json, os, pathlib, re, sys, time, zipfile

SITE = pathlib.Path(__file__).resolve().parents[1]
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/research/deluge-bribes-v1"))
bins = sorted((REPO / "firmware").glob("deluge-bribes-v*.bin"))
if len(bins) != 1:
    sys.exit(f"expected exactly one bin in {REPO / 'firmware'}, found {[b.name for b in bins]}")
src = bins[0]
version = re.search(r"v(\d+(?:\.\d+)+)", src.name).group(1)
data = src.read_bytes()
sha = hashlib.sha256(data).hexdigest()

readme = (REPO / "README.md").read_text(encoding="utf-8")
if sha not in readme:
    sys.exit(f"{src.name} sha256 {sha} is not the one in the README: refusing to publish a mismatched bin")

# ---- presets: every folder under presets/KITS and presets/SYNTHS, as they sit on the SD card ----
PRESETS = REPO / "presets"
SKIP = {".DS_Store", "Thumbs.db"}
groups = {}                                   # "KITS" -> {"LXR": [files]}
for top in ("KITS", "SYNTHS"):
    groups[top] = {}
    for sub in sorted(p for p in (PRESETS / top).iterdir() if p.is_dir()):
        files = sorted(f for f in sub.rglob("*") if f.is_file() and f.name not in SKIP and not f.name.startswith("._"))
        if not any(f.suffix.upper() == ".XML" for f in files):
            sys.exit(f"no presets in {sub}")
        groups[top][sub.name] = files
loose = [f for top in ("KITS", "SYNTHS") for f in (PRESETS / top).iterdir() if f.is_file() and f.name not in SKIP]
if loose:
    sys.exit(f"files outside a preset folder, which the install steps don't cover: {[str(f) for f in loose]}")

def count(top, name):
    return sum(1 for f in groups[top][name] if f.suffix.upper() == ".XML")

def names(top):
    n = list(groups[top])
    return n[0] if len(n) == 1 else ", ".join(n[:-1]) + " and " + n[-1]

def listing(top):
    return "\n".join(f"        {n:<10}{count(top, n):>4}" for n in groups[top])

wave = "WAVE" in groups["SYNTHS"]
install = f"""BRIBELUGE v{version}
Custom firmware for the Synthstrom Deluge, with its presets.
Guide: https://www.thisisbribery.com/bribeluge/#install
Manual: https://www.thisisbribery.com/bribeluge/manual/

IN THIS FOLDER
  {src.name}
      The firmware.
  PRESETS/KITS
      Drum synth kits, by folder:
{listing("KITS")}
  PRESETS/SYNTHS
      Synth presets, by folder:
{listing("SYNTHS")}
  LICENSE.txt
      GPL-3.0.

Back up your SD card before you start.

1. FIRMWARE
  1. Put the Deluge's SD card in your computer.
  2. Copy {src.name} to the top level of the card (beside the KITS, SYNTHS and
     SONGS folders, not inside one).
  3. Remove any other .bin files from the top level.

2. PRESETS
  The card already has a KITS folder and a SYNTHS folder. The presets go inside those.
  1. Open KITS on the card. From PRESETS/KITS here, drag {names("KITS")} into it.
  2. Open SYNTHS on the card. From PRESETS/SYNTHS here, drag {names("SYNTHS")}
     into it.

  The card then looks like this:
    {src.name}
{chr(10).join(f"    {top}/{n}" for top in groups for n in groups[top])}

  DON'T drag this folder's KITS or SYNTHS onto the card itself. On a Mac that replaces the card's whole
  KITS or SYNTHS folder, and your own kits and synths go with it. Go one level in, as above.

  UPDATING from an older Bribeluge: delete those {sum(len(g) for g in groups.values())} folders from the card first, then copy the new
  ones. Presets get retuned and renamed between versions, and this clears the old ones out. If you saved
  presets of your own inside one of them, move them somewhere safe first and put them back after.
  If the card has SYNTHS/BRIB (from v1.26), move anything of yours into SYNTHS/BRINGS and delete BRIB.
"""
if wave:
    install += f"""
3. WAVETABLES (only for the {count("SYNTHS", "WAVE")} WAVE presets)
  The WAVE presets play the free BVKER Custom Wavetables pack, which isn't mine to include.
  1. Download it from https://bvker.com/free-serum-wavetables/
  2. Unzip it into SAMPLES/WAVETABLES on the card, so the card has
     SAMPLES/WAVETABLES/BVKER - Custom Wavetables/Analog and the other folders beside Analog.
  Skip this and everything else still works. Only the WAVE presets need it.
"""
install += f"""
{4 if wave else 3}. START IT
  1. Eject the card and put it back in the Deluge, with the Deluge off.
  2. Hold SHIFT and switch the Deluge on. Let go once it starts loading the new firmware.

FINDING THE PRESETS
  Synths: SHIFT + SYNTH, pick a type, then a category, then turn SELECT to play through them.
  Kits:   SHIFT + KIT, pick Cycles or LXR, then turn SELECT.
  The GIN and TRIBE kits and the ULTRAKIK kicks are built into the firmware: nothing to copy.

GOING BACK
  Install an official firmware file the same way. The preset folders can stay on the card.

Unofficial firmware. Use it at your own risk. Not made or supported by Synthstrom Audible.

LICENCE AND CREDIT
  Bribeluge is free software under the GPL-3.0 (LICENSE.txt), built on the Deluge community firmware
  (delugecommunity.com) and the work of its contributors. Full source of every release:
  https://github.com/thisisbribery/DelugeFirmware
  Where the presets come from, and their credits, is in the CREDITS, SOURCES and README files inside the
  preset folders and in the manual.
"""

out = SITE / "bribeluge" / "download"
out.mkdir(parents=True, exist_ok=True)
folder = f"Bribeluge-v{version}"
zname = f"{folder}.zip"
for old in list(out.glob("*.bin")) + list(out.glob("*.zip")):
    if old.name not in (src.name, zname):
        old.unlink()
(out / src.name).write_bytes(data)

# fixed timestamps (the release commit's) and a fixed order, so the same inputs give the same zip
stamp = time.localtime(src.stat().st_mtime)[:6]
with zipfile.ZipFile(out / zname, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    def add(name, blob):
        zi = zipfile.ZipInfo(f"{folder}/{name}", date_time=stamp)
        zi.external_attr = (0o100000 | 0o644) << 16
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, blob, compresslevel=9)
    add("INSTALL.txt", install.replace("\n", "\r\n"))      # CRLF so Windows Notepad shows it properly
    add(src.name, data)
    add("LICENSE.txt", (REPO / "LICENSE").read_bytes())
    for top in groups:
        for sub, files in groups[top].items():
            for f in files:
                add(f"PRESETS/{f.relative_to(PRESETS).as_posix()}", f.read_bytes())
zdata = (out / zname).read_bytes()

total = sum(count(top, n) for top in groups for n in groups[top])
(out / "latest.json").write_text(json.dumps({
    "version": version,
    "file": f"/bribeluge/download/{src.name}",
    "name": src.name,
    "bytes": len(data),
    "sha256": sha,
    "zip": {"file": f"/bribeluge/download/{zname}", "name": zname, "bytes": len(zdata),
            "sha256": hashlib.sha256(zdata).hexdigest(), "presets": total},
    "files": [
        {"label": "firmware + presets", "file": f"/bribeluge/download/{zname}", "name": zname},
        {"label": ".bin only", "file": f"/bribeluge/download/{src.name}", "name": src.name},
    ],
}, indent=2) + "\n")
print(f"bribeluge v{version}: {src.name} ({len(data)} bytes) sha256 {sha[:16]}...")
print(f"  {zname}: {len(zdata) // 1024} KB, {total} presets in "
      + ", ".join(f"{top}/{n} {count(top, n)}" for top in groups for n in groups[top]))
