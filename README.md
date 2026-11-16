# BRIBERY

Website for Bribery ([@thisisbribery](https://www.instagram.com/thisisbribery/)): modified firmware, music and music production.

A single static page: `index.html` plus `assets/`. No build step.

## Deploy on Vercel

1. Push this repo to GitHub.
2. In Vercel, choose **Add New > Project**, import the repo, keep the framework preset on **Other**, and deploy. No build command or output directory is needed.

Every push to `main` redeploys.

## Editing

- Firmware rows: the `<ul class="rows">` list in `index.html`.
- Music links: the `<!-- Add streaming links here -->` comment in the Music section.
- Learn topics: the `<ul class="topics">` list.
