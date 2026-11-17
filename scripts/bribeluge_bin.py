"""Copy the latest Bribeluge firmware into the site and describe it in latest.json.

    python3 scripts/bribeluge_bin.py [path/to/deluge-bribes-v1]

Default repo: ~/research/deluge-bribes-v1 (public repo clone). Takes the single .bin in its firmware/
folder, copies it to bribeluge/download/, removes older bins there, and writes
bribeluge/download/latest.json, which the site's download gate reads. Run it on every release.
"""
import hashlib, json, os, pathlib, re, sys

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

out = SITE / "bribeluge" / "download"
out.mkdir(parents=True, exist_ok=True)
for old in out.glob("*.bin"):
    if old.name != src.name:
        old.unlink()
(out / src.name).write_bytes(data)
(out / "latest.json").write_text(json.dumps({
    "version": version,
    "file": f"/bribeluge/download/{src.name}",
    "name": src.name,
    "bytes": len(data),
    "sha256": sha,
}, indent=2) + "\n")
print(f"bribeluge v{version}: {src.name} ({len(data)} bytes) sha256 {sha[:16]}...")
