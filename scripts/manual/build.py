"""Build bribeluge/manual/index.html from the Bribeluge firmware README.

    python3 scripts/manual/build.py [path/to/README.md]

Default README: ~/research/deluge-bribes-v1/README.md (the public repo clone).
Rendering uses GitHub's own Markdown API (`gh api markdown`), so the manual reads exactly like
the README on GitHub. Heading ids use GitHub's slug rules, so links like #6-drum-synth match.
Re-run after every README change, then push the site.
"""
import html, json, os, re, subprocess, sys, pathlib

SITE = pathlib.Path(__file__).resolve().parents[2]
README = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/research/deluge-bribes-v1/README.md"))
REPO = "thisisbribery/deluge-bribes-v1"
OUT = SITE / "bribeluge" / "manual" / "index.html"
# old GitHub Pages tools now live on this site
OLD_PAGES = {
    "https://thisisbribery.github.io/bribes-companion": "/companion/",
    "https://thisisbribery.github.io/SealEggs_v1": "/sealeggs/",
    "https://thisisbribery.github.io/stolperbeats-ultra-v1": "/stolperbeats/",
    "https://thisisbribery.github.io/stolperbeats_v2": "/stolperbeats/visualiser/",
    "https://thisisbribery.github.io/stolperbeats_v1": "/stolperbeats/visualiser/",
    "https://www.thisisbribery.com/": "/",
    "https://thisisbribery.com/": "/",
}

md = README.read_text(encoding="utf-8")
body = subprocess.run(["gh", "api", "markdown", "-f", "mode=gfm", "-f", f"context={REPO}", "-f", f"text={md}"],
                      check=True, capture_output=True, text=True).stdout

# ---- headings: GitHub slugs (lowercase, drop punctuation, spaces to hyphens, -1/-2 for repeats) ----
seen = {}
def slug(text):
    s = html.unescape(re.sub(r"<[^>]+>", "", text)).strip().lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE).replace(" ", "-")
    n = seen.get(s, 0); seen[s] = n + 1
    return s if n == 0 else f"{s}-{n}"

title = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S).group(1)
version = (re.search(r"v\d+(?:\.\d+)+", title) or [""])[0]
body = re.sub(r"<h1[^>]*>.*?</h1>\s*", "", body, count=1, flags=re.S)
body = re.sub(r'<p dir="auto"><a id="user-content-readme-top"></a></p>\s*', "", body)

toc = []
def head(m):
    lvl, inner = m.group(1), m.group(2)
    sid = slug(inner)
    if lvl == "2":
        text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        num = re.match(r"(\d+)\.\s+(.*)", text)
        toc.append((sid, num.group(1) if num else "", num.group(2) if num else text))
    return f'<h{lvl} id="{sid}"><a class="m-anchor" href="#{sid}" aria-hidden="true" tabindex="-1">#</a>{inner}</h{lvl}>'
body = re.sub(r'<h([2-6]) dir="auto">(.*?)</h\1>', head, body, flags=re.S)

# ---- links ----
def link(m):
    href = html.unescape(m.group(1))
    if href.startswith("#readme-top"):
        return 'href="#top"'
    self_link = re.match(r"https://github\.com/" + re.escape(REPO) + r"/?(#.*)$", href)
    if self_link:
        return f'href="{self_link.group(1)}"'
    for old, new in OLD_PAGES.items():
        if href.startswith(old):
            return f'href="{new}"' if new != "/" else f'href="/{html.escape(href[len(old):])}"'
    if href.startswith(("http://", "https://", "mailto:")):
        return f'href="{html.escape(href)}" target="_blank" rel="noopener"'
    if href.startswith("#"):
        return f'href="{html.escape(href)}"'
    # a file or folder in the firmware repo
    kind = "raw" if re.search(r"\.(bin|zip|wav|syx)$", href, re.I) else "blob"
    return f'href="https://github.com/{REPO}/{kind}/main/{html.escape(href)}" target="_blank" rel="noopener"'
body = body.replace(' rel="nofollow"', "")
body = re.sub(r'href="([^"]*)"', link, body)

# "Back to top" lines become small right-aligned links
body = re.sub(r'<p dir="auto"><a href="#top">Back to top</a></p>', '<p class="m-top"><a href="#top">Back to top &#8593;</a></p>', body)
# wide tables and code scroll inside their own box on phones
body = re.sub(r"<table role=\"table\">", '<div class="m-table"><table>', body).replace("</table>", "</table></div>")
body = body.replace(' dir="auto"', "").replace(' class="notranslate"', "")

toc_html = "\n".join(
    f'<li><a href="#{sid}"><span>{num}</span>{html.escape(name)}</a></li>' for sid, num, name in toc)

page = (SITE / "scripts" / "manual" / "template.html").read_text(encoding="utf-8")
page = (page.replace("{{VERSION}}", version or "")
            .replace("{{TOC}}", toc_html)
            .replace("{{BODY}}", body)
            .replace("{{SOURCE}}", json.dumps(f"{README.name} @ {REPO}")))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT.relative_to(SITE)}: {len(toc)} sections, {len(page)//1024} KB, version {version}")
