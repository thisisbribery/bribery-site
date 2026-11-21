#!/bin/sh
# Re-copy the flashers' generated data files from their source repos after a flasher update.
# The page markup in this site is restyled, so only data/logic files are copied; if a flasher's
# index.html changes, port that change by hand into the matching sub-page.
set -e
SITE="$(cd "$(dirname "$0")/.." && pwd)"
cp ~/dev/sealegs_v1/mods.js                "$SITE/sealeggs/mods.js"
cp ~/dev/sealegs_v1/LICENSE.md             "$SITE/sealeggs/LICENSE.txt"
cp ~/dev/stolperbeats-ultra-v1/mods.js     "$SITE/stolperbeats/mods.js"
cp ~/dev/stolperbeats-ultra-v1/builder.js  "$SITE/stolperbeats/builder.js"
# BRIBESTAGES: replace the update wavs and rewrite the list the sign-up form reads
python3 - "$SITE" <<'PY'
import json, pathlib, re, shutil, sys
site = pathlib.Path(sys.argv[1]); src = pathlib.Path.home() / "dev/qiemem-bribery-edition/firmware"; dst = site / "bribestages/firmware"
wavs = sorted(src.glob("*.wav"), key=lambda p: ("flipped" in p.name, p.name))
if not wavs: sys.exit("no BRIBESTAGES wavs in " + str(src))
for old in dst.glob("*.wav"):
    if old.name not in [w.name for w in wavs]: old.unlink()
for w in wavs: shutil.copy2(w, dst / w.name)
ver = re.search(r"v(\d+(?:\.\d+)+)", wavs[0].name).group(1)
files = [{"label": "flipped" if "flipped" in w.name else "normal", "file": "/bribestages/firmware/" + w.name, "name": w.name} for w in wavs]
(dst / "latest.json").write_text(json.dumps({"version": ver, "files": files}, indent=2) + "\n")
print("BRIBESTAGES v" + ver + ":", ", ".join(w.name for w in wavs))
PY
python3 "$SITE/scripts/bribeluge_bin.py"
python3 "$SITE/scripts/manual/build.py"
echo "Synced. Check git diff, then test the flashers before pushing."
