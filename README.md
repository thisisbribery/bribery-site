# BRIBERY

Website for Bribery ([@thisisbribery](https://www.instagram.com/thisisbribery/)): modified firmware, music and music production. Live at https://thisisbribery.com

Static HTML, no build step. Vercel deploys every push to `main`.

## Pages

| Path | What |
| --- | --- |
| `/` | Home: firmware rows with device shots, music, learn |
| `/bribeluge/` | Bribeluge (Deluge firmware) feature guide |
| `/bribeluge/manual/` | Full Bribeluge manual, generated from the firmware README |
| `/companion/` | Bribeluge Companion app (PWA, Web MIDI) |
| `/sealeggs/` | Seal Eggs flasher (Sealegs) |
| `/stolperbeats/` | STOLPERBEATS ULTRA flasher |
| `/stolperbeats/visualiser/` | Stolperbeats Timing visualiser |
| `/stages/` | Qiemem Bribery Edition (Stages) with in-page update audio |
| `/kali/` | KALI SMASH (dsp.coffee Kali) with a gated zip download |

Ported tools keep their original look as **Classic** mode (toggle in the top bar, remembered per browser). Their original CSS sits in `<style data-bx="classic">`, the new look in `<style data-bx="new">`.

## Settings (`assets/site.js`, top of file)

- `web3formsKey`: access key from web3forms.com for the beta tester form (delivers to the address you register it with). Empty = the form says sign-ups open soon and sends nothing.
- `supportUrl`: Buy Me a Coffee / Ko-fi link. Empty = every Support button stays hidden.
- `links`: Instagram, YouTube, Spotify, GitHub.

## Shared files

- `assets/site.css`, `assets/site.js`: top bar, footer, New/Classic toggle, beta form. Everything is prefixed `bx-`.
- `assets/pages.css`: layout for the info pages (Bribeluge, Stages).
- `assets/devices/*.webp`: device shots (`<name>.webp` 1600x1000, `<name>-sm.webp` 800x500). Replace with real photos at the same names and sizes.

## Updating a flasher

The flasher logic and data files are copies of the source repos. After a flasher update run `scripts/sync-tools.sh`, test the page, then push. If a flasher's `index.html` changed, rebuild its sub-page from the source page with the generator in `scripts/port/` (each folder holds the generator and the page's new-mode `new.css`; Stolperbeats: `python3 scripts/port/stolperbeats/compose.py scripts/port/stolperbeats`), then check the result with that folder's `equiv.py`, which compares built firmware against the original page. `scripts/` is not deployed (`.vercelignore`).

`vercel.json` sets `trailingSlash: true` so `/sealeggs` redirects to `/sealeggs/` and relative script paths resolve.

## Old addresses

The old GitHub Pages tools (SealEggs_v1, stolperbeats-ultra-v1, stolperbeats_v1, stolperbeats_v2, bribes-companion) redirect here. Each of those repos serves a `gh-pages` branch built by `scripts/redirects/make.py` (their `main` branches are unchanged). The redirect carries the visitor's saved tool data (custom Timings, banks, Companion settings) in a `#bx-import=` URL fragment; `assets/site.js` imports it once without overwriting anything already saved here. Pushing to those repos' `main` no longer publishes anything: update the matching sub-page here instead.

## Bribeluge manual

`bribeluge/manual/index.html` is generated from the firmware README by `scripts/manual/build.py` (layout in `scripts/manual/template.html`), using GitHub's Markdown renderer via `gh api markdown`, so it reads exactly like the README and keeps GitHub's heading anchors (`#6-drum-synth` and so on). After every README change: `python3 scripts/manual/build.py ~/research/deluge-bribes-v1/README.md`, then push. Don't edit the generated page by hand.

## Bribeluge download

The firmware downloads from the site through a gate on `/bribeluge/` (pink Download band, hero and install buttons, and the manual's Download button): name, email, optional artist name and a music link go to Web3Forms, then the bin downloads. The file lives in `bribeluge/download/` with `latest.json`, written by `scripts/bribeluge_bin.py`, which refuses a bin whose sha256 isn't in the firmware README. On every release run it (or `scripts/sync-tools.sh`) and push. If Web3Forms fails, the download still goes ahead.

## KALI SMASH download

`kali/download/` holds a zip (firmware, Daisy bootloader + MIT licence, `flash-kali.sh`, INSTALL.txt) and `latest.json`, built by `scripts/kali_zip.py` from `~/dev/kaliv1/release`. Run it on every KALI SMASH release, then push. The page's Download buttons use the same gate as Bribeluge (`data-bx-download="kali"`). Device render: `scripts/renders` (`python3 render.py kali --final`).
