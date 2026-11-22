import re, pathlib, sys
SRC = pathlib.Path.home()/"dev/stolper-re/stolperbeats_v2/index.html"
OUT = pathlib.Path.home()/"dev/bribery-site/stolperbeats/visualiser/index.html"
HERE = pathlib.Path(__file__).parent
src = SRC.read_text()

def rep(s, old, new, count=1):
    n = s.count(old)
    assert n == count, (old[:80], n)
    return s.replace(old, new)

head_end = src.index("<style>")
style_start = head_end + len("<style>")
style_end = src.index("</style>")
orig_css = src[style_start:style_end]
head = src[:head_end]
body = src[src.index("</head>"):]

# ---- head: absolute shared assets ----
head = rep(head, 'href="assets/favicon-32.png"', 'href="/assets/favicon-32.png"')
head = rep(head, 'href="assets/favicon-64.png"', 'href="/assets/favicon-64.png"')
head = rep(head, 'href="assets/apple-touch-icon.png"', 'href="/assets/apple-touch-icon.png"')
head = rep(head, '<meta name="description"', '<meta name="theme-color" content="#000000">\n<meta name="description"')

# ---- new sheet part A: the original's structural CSS without its colour themes ----
base = orig_css
a = base.index(":root{\n  --bg:#f5f4f0")
b = base.index("*{box-sizing:border-box}")
base = base[:a] + base[b:]
base = rep(base, ':root{--mine:#2bb5ae;--amber:#e09a1c} :root[data-theme="dark"]{--mine:#3fd0c9;--amber:#ffb627}\n', '')
base = rep(base, '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--mine:#3fd0c9;--amber:#ffb627}}\n', '')
new_css = (HERE/"new.css").read_text()

styles = ('<link rel="stylesheet" href="/assets/site.css">\n'
          '<style data-bx="classic">' + orig_css + '</style>\n'
          '<style data-bx="new">\n/* ===== new mode: the original layout rules, re-themed below ===== */\n' + base +
          '\n/* ===== new mode: BRIBERY look ===== */\n' + new_css + '</style>\n'
          '<script src="/assets/site.js"></script>\n'
          '<script>/* refit the mega title when the page style changes */addEventListener("bx-mode",function(){ if(window.BRIBERY) window.BRIBERY.fit(); });</script>\n')

# ---- body ----
body = rep(body, "<body>", '<body data-bx-page="stolperbeats" data-bx-foot>')
body = rep(body, 'src="assets/coin-front.png"', 'src="/assets/coin-front.png"')
body = rep(body, 'src="assets/coin-back.png"', 'src="/assets/coin-back.png"')
ULTRA = "https://thisisbribery.github.io/stolperbeats-ultra-v1/"
# hrefs -> same-origin flasher (3 of them), exported text -> full site URL (1)
assert body.count(ULTRA) == 4, body.count(ULTRA)
body = body.replace('href="' + ULTRA + '"', 'href="/stolperbeats/"')
body = rep(body, "flasher (" + ULTRA + ")", "flasher (https://thisisbribery.com/stolperbeats/)")
assert ULTRA not in body

# hero for new mode
body = rep(body, '<div class="headtext">\n      <h1>',
  '<div class="headtext">\n'
  '      <p class="bx-kicker bx-new-only sbx-kick">MSM Stolperbeats <span>/</span> Swing visualiser <span>/</span> Emulator</p>\n'
  '      <div class="bx-mega bx-new-only sbx-mega" data-fit role="heading" aria-level="1" aria-label="Stolperbeats Visualiser"><span class="bx-fit">STOLPERBEATS</span></div>\n'
  '      <div class="bx-mega bx-new-only sbx-mega2" data-fit aria-hidden="true"><span class="bx-fit sbx-swap"><span class="sbx-v">VISUALISER</span><span class="sbx-c">CREATOR</span></span></div>\n'
  '      <h1>')
# section labels (attributes only)
body = rep(body, '<section class="card">\n    <div class="barhead"><h2 id="barTitle">', '<section class="card" data-bx-label="Grid">\n    <div class="barhead"><h2 id="barTitle">')
body = rep(body, '<details class="card sources" id="bankCard">\n    <summary>', '<details class="card sources" id="bankCard">\n    <summary data-bx-label="Banks">')
body = rep(body, '<section class="card" id="halfCard">', '<section class="card" id="halfCard" data-bx-label="Close-up">')
body = rep(body, '<section class="card fwlink" id="fwCard">', '<section class="card fwlink" id="fwCard" data-bx-label="Firmware">')
body = rep(body, '<details class="card sources about">\n    <summary>', '<details class="card sources about">\n    <summary data-bx-label="About">')
body = rep(body, '<details class="card sources">\n    <summary><span class="chev" aria-hidden="true"></span><span><b>Sources</b>', '<details class="card sources">\n    <summary data-bx-label="Sources"><span class="chev" aria-hidden="true"></span><span><b>Sources</b>')

OUT.write_text(head + styles + body)
print("wrote", OUT, len(head + styles + body))
