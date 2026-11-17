"""Assemble ~/dev/bribery-site/sealeggs/index.html from the SealEggs_v1 page plus new.css.
The original CSS and the flasher <script> are copied verbatim."""
import os, re, sys
HOME = os.path.expanduser("~")
SRC = os.path.join(HOME, "dev/sealegs_v1/index.html")
OUT = os.path.join(HOME, "dev/bribery-site/sealeggs/index.html")
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(SRC, encoding="utf-8").read()
new_css = open(os.path.join(HERE, "new.css"), encoding="utf-8").read()

m = re.search(r"<style>\n(.*?)</style>", src, re.S)
classic_css = m.group(1)
body = src[src.index("<body>") + len("<body>"):src.index("</body>")]

def rep(s, old, new, count=1):
    assert s.count(old) == count, (old, s.count(old))
    return s.replace(old, new)

# shared assets by absolute path
body = rep(body, 'src="assets/coin-front.png"', 'src="/assets/coin-front.png"')
body = rep(body, 'src="assets/coin-back.png"', 'src="/assets/coin-back.png"')

# hero: kicker + huge fitted title (new style only), CTA
body = rep(body, "<header>\n  <svg class=\"logo\"",
  "<header>\n"
  "  <p class=\"bx-kicker bx-new-only\">Sealegs delay <span>/</span> Firmware 1.3.5.0 <span>/</span> Browser flasher</p>\n"
  "  <div class=\"bx-mega bx-glitch bx-new-only\" data-fit data-text=\"SEAL EGGS\" aria-hidden=\"true\"><span class=\"bx-fit\">SEAL EGGS</span></div>\n"
  "  <svg class=\"logo\"")
body = rep(body, "this site hosts none.</span></div>\n  </div>\n</header>",
  "this site hosts none.</span></div>\n"
  "    <div class=\"se-ctas bx-new-only\"><a class=\"bx-btn bx-solid\" href=\"#step1\">Start</a><a class=\"bx-btn\" href=\"#notes\">Read before you flash</a></div>\n"
  "  </div>\n</header>\n\n"
  "<div class=\"se-marquee bx-new-only\" aria-hidden=\"true\"><div class=\"se-marquee-track\">"
  + "<span>Live reverse<i>/</i>Digi doppler<i>/</i>Tape grunge<i>/</i>BBD chip decay<i>/</i>Data corruption<i>/</i>Seal Beads<i>/</i>Seal Microloops<i>/</i></span>" * 2
  + "</div></div>")

# step heads: wrap the h2 + hint so they can sit side by side
body, n = re.subn(r'(  <h2><span class="num">\d</span>[^<]*</h2>\n  <p class="hint">.*?</p>)\n',
                  lambda mm: '  <div class="step-head">\n' + "\n".join("  " + l for l in mm.group(1).split("\n")) + "\n  </div>\n",
                  body, flags=re.S)
assert n == 3, n

# notes: group each h3 with its paragraphs
foot_start = body.index("<footer>")
foot_end = body.index("</footer>") + len("</footer>")
foot = body[foot_start:foot_end]
parts = re.split(r"(?=  <h3>)", foot[len("<footer>\n"):-len("</footer>")])
groups = ['  <div class="fgrp">\n' + "\n".join("  " + l for l in p.rstrip("\n").split("\n")) + "\n  </div>\n" for p in parts if p.strip()]
assert len(groups) == 3
foot = ('<footer id="notes">\n  <h2 class="se-notes-head bx-new-only">Read this</h2>\n' + "".join(groups) + "</footer>")
body = body[:foot_start] + foot + body[foot_end:]

# mods.js note
body = rep(body, '<script src="mods.js"></script>',
  '<!-- mods.js is copied unchanged from the SealEggs_v1 repo (github.com/thisisbribery/SealEggs_v1).\n'
  '     Re-copy it (and this page\'s flasher script) whenever the flasher is updated there. -->\n'
  '<script src="mods.js"></script>')

body = body.rstrip("\n") + """
<script>
// Site shell: refit the SEAL EGGS title when the page switches into the new style.
addEventListener("bx-mode", function () { requestAnimationFrame(function () { if (window.BRIBERY) window.BRIBERY.fit(); }); });
</script>
"""

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seal Eggs Firmware Flasher</title>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="/assets/favicon-64.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="description" content="Build a modded Sealegs 1.3.5.0 firmware in your browser from your own copy of the official firmware.">
<meta name="theme-color" content="#000000">
<meta property="og:title" content="Seal Eggs Firmware Flasher">
<meta property="og:description" content="Build a modded Sealegs 1.3.5.0 firmware in your browser from your own copy of the official firmware.">
<meta property="og:image" content="/assets/apple-touch-icon.png">
<!-- Ported from github.com/thisisbribery/SealEggs_v1. Classic style = that page's CSS, verbatim. -->
<link rel="stylesheet" href="/assets/site.css">
<style data-bx="classic">
{classic_css}</style>
<style data-bx="new">
{new_css}</style>
<script src="/assets/site.js"></script>
</head>
<body data-bx-page="sealeggs" data-bx-foot>"""

out = head + body + "</body>\n</html>\n"
open(OUT, "w", encoding="utf-8").write(out)

# self-check: flasher script and classic CSS are byte-identical to the source
js = lambda s: re.search(r'<script src="mods.js"></script>\n<script>\n(.*?)</script>', s, re.S).group(1)
assert js(src) == js(out), "flasher JS changed"
assert re.search(r'<style data-bx="classic">\n(.*?)</style>', out, re.S).group(1) == classic_css
print("wrote", OUT, len(out), "bytes")
