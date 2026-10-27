# sofiakgomes.com

Static re-creation of Sofia Gomes' art-director portfolio. Plain HTML/CSS/JS, no framework, no runtime build. Hosted on GitHub Pages (`origin` = `git@github.com:sofiakgomes/portfolio-v3.git`, custom domain in `CNAME` = `www.sofiakgomes.com`); DNS is at Porkbun.

## Layout

- `index.html` – splash (black screen, logo fades in, auto-advances to `/work/` after 5s or on click).
- `work/index.html` – the "home" grid; `work/<slug>/index.html` – six project pages; `about/index.html`; `404.html`.
- `css/style.css`, `js/main.js` – the only stylesheet and script (edit directly).
- `assets/img/<project>/<name>.webp` full-size images, `.../thumb/<name>.webp` 1000px grid/lightbox placeholders, `assets/img/work/` Work-grid tiles, `assets/img/site/` logo/splash/portrait, `assets/img/og.jpg` social preview; `assets/video/<name>.mp4` + `<name>.webp` poster; `assets/fonts/oswald-latin.woff2`; `assets/Sofia-Gomes-Resume.pdf`.
- Site root: `favicon.ico`, `apple-touch-icon.png`, `CNAME`, `.nojekyll`, `robots.txt`, `sitemap.xml` (the last three plus `404.html` are generated).
- `tools/build.py` + `tools/images.txt` – page generator (see below).

## Workflow

- **All HTML is generated.** Shared header/footer/head, the project copy, video names and the project list live in `tools/build.py` (`PROJECTS` holds one entry per project page: title, description, text, stats, credits, hero video, extra blocks). Edit that, run `python3 tools/build.py`, commit the regenerated files. Do not hand-edit the `.html`, `sitemap.xml` or `robots.txt` files; they are overwritten. `DOMAIN` in `build.py` must match `CNAME`.
- `tools/images.txt` lists `<folder> <name>` per gallery image in display order (`<name>.webp` full size + `thumb/<name>.webp`). The first Anthems image is that page's hero and has no thumbnail.
- Preview: `python3 -m http.server 8000 --bind 127.0.0.1` from the repo root. Pages use root-absolute paths (`/css/style.css`), so they must be served from `/`; they only look right at the custom domain's root (not at `username.github.io/portfolio-v3/`).
- No test suite. Layout was verified by measuring against the live original with headless Chrome driven over the DevTools protocol (ad hoc scripts, not committed): dump every element's rect at ~11 widths before and after a change and diff. In the VNC Chrome the window-resize tool does not change the viewport; use device-metrics emulation instead.

## Media pipeline (derived assets; originals are not kept in the repo)

- Full-size images: WebP q80 (`cwebp -q 80 -metadata icc`; keep the ICC profile, the Anthems photos are Display P3 and ffmpeg's WebP encoder drops it). Thumbnails: `cwebp -q 80 -sharp_yuv -metadata icc -resize 1000 0 full.webp -o thumb/<name>.webp`.
- Logo 480px wide WebP with alpha, splash 546px (shown at 182px), favicon 32x32 `.ico` + 180px apple-touch icon, `og.jpg` 1200x630.
- Videos are H.264/AAC with `+faststart`. The three 1080p heroes (`buldak-hero`, `heroes-hero`, `merry-hero`) are untouched; `duomiles-hero` is 1080p CRF 24; the 9:16 clips are 720x1280 and the artist intros 1280x720, both CRF 26 (`-preset slow -profile:v high -pix_fmt yuv420p -c:a copy -movflags +faststart`). Posters are the frames the original site showed (about 7s in), as WebP.

## Design rules worth knowing

- Sizes are fluid and were measured from the original: body text is `clamp(9.8px, 15.7px - 0.23vw, 12.8px)` (it shrinks on wide screens), header height is `51px + 3.18vw`, project/about content is centred and capped once the window passes ~1490px.
- Breakpoints: `<800px` mobile layout (burger menu with fading overlay, stacked project layouts, 2-column galleries); `<900px` Work grid becomes one column. The Work grid has no max size: edge to edge up to 1400px, then a growing side margin and gaps.
- Fonts: Oswald (self-hosted woff2, latin subset, variable 200-700) for headings, system Helvetica/Arial for everything else. Social icons are hand-drawn inline SVGs in `build.py`.
- Footer contains only the social icons (header and mobile menu have WORK/ABOUT).
- `main.js` adds `js` to `<html>` just before observing; `.reveal` elements are hidden until an IntersectionObserver adds `.in`. The lightbox crossfades between slides (one `<img>` per slide, old one removed after fading), shows the cached thumbnail first and swaps in the full file, and preloads neighbours. The picture's displayed width comes from its shape (`--ar`, set by the script) through `--w` in the CSS, which also places the arrows, so thumbnail and full file occupy the same box. Reduced-motion users get no fades.
- Videos load on first click (`data-src`), then use native controls.

## Provenance and legal

- No code, templates, fonts, icons or scripts from any site builder are used; everything was written from scratch. Keep it that way. The images/videos are the owner's own work files.
- The portfolio shows client campaign work (Walmart, Sam's Club, American Express, Duolingo/Delta, Buldak); permission to publish it is the owner's responsibility.
- Everything in the repo root is published by GitHub Pages, including `tools/` and this file.

## Git

- Identity for this repo only: `sofiakgomes` / `sofiakfourigomes@gmail.com` (local config, nothing global).
- Pushes use the key `~/.ssh/id_ed25519_sofia` via the repo-local `core.sshCommand`. The default `~/.ssh/id_ed25519` belongs to another GitHub account, so never rely on it here.
- Do not push, tag or change the remote unless asked. End commit messages with the attribution line from the session.

## Open items

- Accessibility items from the review were deliberately postponed: a single `<h1>` per page (project titles are `h2`), meaningful alt text on gallery links, `role="dialog"`/focus handling for the lightbox, `aria-controls`/Escape for the menu.
- The resume PDF's Author metadata is "Pontes, Rodrigo D"; re-export it with the right author before publishing.
- DNS still needs pointing at GitHub Pages (4 `A` records for `@` to `185.199.108-111.153`, `CNAME www` -> `sofiakgomes.github.io`, remove any wildcard record), then enable Enforce HTTPS in the Pages settings.
