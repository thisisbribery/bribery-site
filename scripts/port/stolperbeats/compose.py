import sys, pathlib
SP = pathlib.Path(sys.argv[1])
src = pathlib.Path.home()/"dev/stolperbeats-ultra-v1/index.html"
dst = pathlib.Path.home()/"dev/bribery-site/stolperbeats/index.html"
h = src.read_text()
newcss = (SP/"new.css").read_text().rstrip("\n")

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, (old[:80], n)
    h = h.replace(old, new)

VIS_OLD = "https://thisisbribery.github.io/stolperbeats_v2/"
VIS_NEW = "/stolperbeats/visualiser/"

# ---- head ----
rep('<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">\n<link rel="icon" type="image/png" sizes="64x64" href="assets/favicon-64.png">\n<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">',
    '<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">\n<link rel="icon" type="image/png" sizes="64x64" href="/assets/favicon-64.png">\n<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">')
rep('<style>\n:root{\n  --bg:#f6f4ef;',
    '<meta name="theme-color" content="#000000">\n'
    '<!-- builder.js and mods.js in this folder are copied unchanged from the stolperbeats-ultra-v1 repo\n'
    '     (github.com/thisisbribery/stolperbeats-ultra-v1). Re-copy them, and re-apply any page changes, whenever the flasher is updated. -->\n'
    '<link rel="stylesheet" href="/assets/site.css">\n'
    '<!-- Classic look: the original flasher CSS, verbatim. -->\n'
    '<style data-bx="classic">\n:root{\n  --bg:#f6f4ef;')
rep('</style>\n</head>',
    '</style>\n<!-- New look (BRIBERY site style). -->\n<style data-bx="new">\n' + newcss + '\n</style>\n<script src="/assets/site.js"></script>\n</head>')
rep('<body>\n<div class="wrap">', '<body data-bx-page="stolperbeats" data-bx-foot>\n<div class="wrap">\n' + (SP/"hero.html").read_text().rstrip("\n"))

# ---- shared assets ----
rep('src="assets/coin-front.png"', 'src="/assets/coin-front.png"')
rep('src="assets/coin-back.png"', 'src="/assets/coin-back.png"')

# ---- visualiser now lives on the same origin ----
rep(VIS_OLD, VIS_NEW, 4)

# ---- step titles get a wrapper span for the new layout ----
for n, t in [(1,"Load your official firmware"),(2,"Swing tables on the Timing buttons"),(3,"Choose your mods"),(4,"Build and download"),(5,"Flash it over USB")]:
    rep(f'<h2><span class="num">{n}</span>{t}</h2>', f'<h2><span class="num">{n}</span><span class="bxs-h">{t}</span></h2>')

# ---- refit the big title when the mode changes (site.js only fits on load and resize) ----
rep('</script>\n</body>',
    '</script>\n<script>\n// The STOLPERBEATS / ULTRA title is hidden in classic mode, so refit it when the page switches to new.\n'
    'addEventListener("bx-mode", function(){ if (window.BRIBERY) window.BRIBERY.fit(); });\n</script>\n</body>')

assert "—" not in h
dst.write_text(h)
print("wrote", dst, len(h))
