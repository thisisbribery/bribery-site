# BRIBERY

Website for Bribery ([@thisisbribery](https://www.instagram.com/thisisbribery/)): modified firmware, music and music production. Live at https://thisisbribery.com

Static HTML, no build step. Vercel deploys every push to `main`.

## Pages

| Path | What |
| --- | --- |
| `/` | Home: firmware rows with device shots, music, learn |
| `/bribeluge/` | Bribeluge (Deluge firmware) feature guide |
| `/companion/` | Bribeluge Companion app (PWA, Web MIDI) |
| `/sealeggs/` | Seal Eggs flasher (Sealegs) |
| `/stolperbeats/` | STOLPERBEATS ULTRA flasher |
| `/stolperbeats/visualiser/` | Stolperbeats Timing visualiser |
| `/stages/` | Qiemem Bribery Edition (Stages) with in-page update audio |

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
