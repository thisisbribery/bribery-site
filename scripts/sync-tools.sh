#!/bin/sh
# Re-copy the flashers' generated data files from their source repos after a flasher update.
# The page markup in this site is restyled, so only data/logic files are copied; if a flasher's
# index.html changes, port that change by hand into the matching sub-page.
set -e
SITE="$(cd "$(dirname "$0")/.." && pwd)"
cp ~/dev/sealegs_v1/mods.js                "$SITE/sealeggs/mods.js"
cp ~/dev/stolperbeats-ultra-v1/mods.js     "$SITE/stolperbeats/mods.js"
cp ~/dev/stolperbeats-ultra-v1/builder.js  "$SITE/stolperbeats/builder.js"
cp ~/dev/qiemem-bribery-edition/firmware/*.wav "$SITE/stages/firmware/"
python3 "$SITE/scripts/bribeluge_bin.py"
python3 "$SITE/scripts/manual/build.py"
echo "Synced. Check git diff, then test the flashers before pushing."
