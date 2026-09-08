# Global Passport Series — website

Source for the Global Passport Series site. GPS is an invitation-only summit series
for families, run by Adelphi Global LLC. Next summit: **Munich, 30 September – 2 October 2026**.

**Live:** https://fkhhb.github.io/globalpassport/ (preview — reachable by link, not indexed)

> **Before you commit anything, read [`docs/BRIEF.md`](docs/BRIEF.md) §2.**
> This repo has deliberate redactions — Munich venue names and the contact email address
> are removed on purpose, because the summits are invitation-only.
>
> **This repository is public, and git history is permanent.** The redacted strings are
> therefore not stored here in plaintext: `build.py` enforces them as salted hashes, and
> the plaintext list is gitignored (`redactions.local.txt`). Never commit the source
> PDFs, any pre-redaction file, or a venue name in a commit message or PR description —
> those are just as permanent as files and are not covered by `.gitignore`.

---

## Quick start

```bash
git clone https://github.com/fkhhb/globalpassport
cd globalpassport
python3 build.py              # → dist/global-passport-series.html  (the WhatsApp file)
python3 build.py --linked _site   # → _site/  (the hosted site)
open dist/global-passport-series.html
```

The build needs Python 3.8+ and the standard library. Nothing else — no npm, no
framework, no preprocessor. (One optional dev tool, `tools/make_hero_variants.js`,
needs Node + Playwright; the build never depends on it. See *Performance*.)

---

## Two builds from one source

The site exists in two shapes, produced from the same template and assets:

| | shape | HTML | for |
|---|---|---|---|
| `build.py` | **one self-contained file**, every image and font inlined as base64 | 4.1 MB | sending to guests over WhatsApp; works with no network |
| `build.py --linked DIR` | `index.html` + real asset files | 64 KB | hosting |

The single file is the right answer for a file you hand someone and the wrong answer
for a web page: 4.3 MB of base64 must all arrive before anything paints, none of it
caches per asset, and base64 is a third larger than the bytes it encodes. Hosted, the
HTML is 64 KB and images stream in as needed.

Both shapes keep the repository reviewable: source holds real files in `assets/`, and
the markup carries `{{IMG:filename}}` and `{{FONT:filename}}` placeholders that
`build.py` resolves.

```
index.template.html  +  assets/img/*   ──build.py──▶   dist/global-passport-series.html
     (edit this)        assets/fonts/*                  or  _site/  (--linked)
                        (edit these)                         (never edit these)
```

The build was verified to reproduce the originally distributed file byte for byte
before any change was made, so the decomposition is faithful.

### Commands

```bash
python3 build.py                  # single file → dist/
python3 build.py --linked _site   # hosted build → _site/index.html + assets/
python3 build.py --check          # validate only, write nothing, exit 1 on problems
python3 build.py --noindex        # add <meta name=robots noindex> (preview deploys)
python3 build.py --out foo.html   # single file, elsewhere
python3 build.py --hash "Name"    # print a redaction-denylist digest to paste into build.py

python3 tools/fetch_fonts.py            # re-download the woff2 faces (the only network step)
node   tools/make_hero_variants.js      # regenerate hero srcset variants (optional; needs Playwright)
```

`--check` runs in CI before every deploy. Every build is audited for the redacted
venue strings (by hash, over every 1–4-word window), for any bare email address, and
for unresolved placeholders; the single-file build also warns above 5 MB.

---

## Security

Full detail in [`SECURITY.md`](SECURITY.md). The short version:

- **Content Security Policy** in every build, `default-src 'none'`, with the page's own
  `<style>` and three `<script>` blocks allowed by **SHA-256 hash** of their exact
  contents. No `'unsafe-inline'`. Any script that is not ours is refused. The hashes are
  computed by `build.py` on the final HTML, so editing a script needs no manual step.
- Consequently **no `style=""` attributes** in the template — they would be blocked. Use a
  class.
- **No `innerHTML`.** The speaker grid is built with `createElement`/`textContent`.
- **No network requests at all.** No analytics, no third-party fonts or scripts, no
  cookies. `connect-src 'none'` makes the privacy notice's claim enforceable.
- `<meta name="referrer" content="no-referrer">`.
- GitHub Actions pinned to **commit SHAs**, not tags. Minimal token permissions. Deploy
  gated on the redaction audit.

Two things GitHub Pages cannot do — `frame-ancestors` (clickjacking) and HSTS — need a
host that sets headers. Do that when the site moves to its real domain.

---

## Performance

Measured in Chromium on a local server (which *understates* every gap — there is no
real network):

| | requests | bytes before `load` | hero image |
|---|---|---|---|
| hosted, phone 390px @3× | 11 | **0.56 MB** | 249 KB (1600w variant) |
| hosted, laptop 1440px @2× | 10 | 0.54 MB | 249 KB (1600w variant) |
| hosted, before the srcset (previous round) | 11 | 1.31 MB | 1019 KB (full) |
| single file, any device | 1 | 4.33 MB | 1019 KB (inlined) |

What does the work:

- **Responsive hero.** The hero is the LCP element and, at 3720×2028 / 1 MB, a third of
  every image byte on the page. The hosted build emits `srcset` over four widths
  (1000 / 1600 / 2400 / 3720) with `sizes="(max-width:860px) 100vw, 53vw"`; the browser
  picks the smallest that covers its box. A 4K display still gets the full original.
  Variants come from `tools/make_hero_variants.js` (Chromium canvas resample — conventional,
  invents nothing); `build.py` emits a srcset only for variants that exist, so a checkout
  without them still builds. **Regenerate them when the hero photograph changes.**
- **Font preloads** for the four faces used above the fold, hosted build only. Text renders
  in the right face on first paint instead of after the stylesheet is parsed.
- `loading="lazy"` + `decoding="async"` on every below-the-fold image; `fetchpriority="high"`
  on the hero. Inert in the single file, where every image is already local.
- 64 KB of HTML instead of 4.3 MB, so first paint does not wait for images.

Deliberately not done: minification (GitHub Pages gzips; the gain is ~15 KB and the risk
is not worth it) and WebP (no encoder available in the build environment; JPEG at these
sizes is already within ~20% of it).

---

## Deploy

`.github/workflows/pages.yml` builds `--linked --noindex` and deploys to GitHub Pages on
every push to `main`. Nothing else: the `github-pages` environment accepts the default
branch only, so a workflow run from any other branch fails at the gate before a single
step executes.

**This is a preview deployment.** GPS is invitation-only, so the page ships with a
`noindex` meta tag and a disallow-all `robots.txt` — reachable by anyone with the link,
not discoverable by searching for the city and the dates.

**To launch for real** (client decision, not made yet):

1. Drop `--noindex` and the `robots.txt` line from the workflow.
2. Add a `CNAME` file containing `www.globalpassportseries.com` to the deploy and point
   DNS at Pages — or move to a host that can send security headers (see *Security*).
3. Set `og:url` in the template.

---

## Layout

```
index.template.html      markup + inline CSS/JS, {{IMG:}} / {{FONT:}} / {{CSP}} / {{HERO_SRCSET}} / {{FONT_PRELOAD}}
build.py                 inliner, CSP generator, redaction audit
assets/img/              48 images (45 + 3 hero srcset variants)
assets/fonts/            8 woff2 faces + OFL.txt licences
assets/manifest.json     path, dimensions, byte size for every asset
assets/fallback-silhouettes/   drawn SVG city silhouettes (Dallas, New York, Paris)
tools/fetch_fonts.py     re-download the web fonts
tools/make_hero_variants.js    hero srcset variants (optional dev tool, Node + Playwright)
tools/make_city_silhouettes.py drawn SVG city silhouettes
.github/workflows/pages.yml    build + audit + deploy to Pages, main only
redactions.local.txt     plaintext denylist — GITIGNORED, never commit
dist/                    single-file build output (gitignored)
docs/BRIEF.md            full handover: constraints, decisions, every change and why
SECURITY.md              what the page enforces, what Pages cannot, what the repo keeps out
```

---

## Editing

**Content and layout** → `index.template.html`. One file, inline `<style>` and `<script>`.
Sections in document order: `#about`, `#munich`, `#leadership`, `#calendar`, `#speakers`,
`#sponsors`, `#contact`. Backgrounds alternate paper / grey / paper / grey / paper / grey /
navy — if you move a section, re-assign the `band` classes or two of a kind end up adjacent.

**Speakers** → the `const speakers = [...]` array near the bottom. Each entry is
`{name, role, img, bio}`; `img` is an `{{IMG:...}}` placeholder. Write `&`, not `&amp;` —
the text goes through `textContent`, so entities would render literally.

**Colours** → the `:root` block. `--crimson` **#AD2625** and `--navy` **#203D6A** are picked
from the logo files. The nav SVG carries the same two values as inline fills — **change
them together** or the mark and the accents drift apart. The navbar is white so the mark
can show those colours: on a navy bar the logo's own navy `P` measures 1.6:1 and vanishes,
so a coloured mark and a dark bar cannot coexist (BRIEF §18–19). Navy headlines on paper measure
10.5:1, crimson text 6.6:1, white on the navy bar 10.8:1. See BRIEF §5 for how these were
arrived at (three corrections; every eyeballed value was wrong).

**Type** → Newsreader for headlines, IBM Plex Sans for everything else. Client-chosen from
five options. Do not change unasked. Weights are embedded, not linked — add a weight to the
CSS and you must add it to `FACES` in `tools/fetch_fonts.py` and re-run, or it synthesises.

**Images** → drop the file in `assets/img/`, reference it as `{{IMG:filename}}`, add it to
`assets/manifest.json`. Check BRIEF §6 if it came from the original PDFs — several carry a
white frame baked into the pixels. **If you replace the hero, re-run
`tools/make_hero_variants.js`** or the srcset will point at the old picture.

**Styles** → in the `<style>` block, as a class. Never a `style=""` attribute: the CSP
allows the stylesheet by hash and refuses inline styles.

---

## Things that will bite you

- Editing `dist/` or `_site/`. Both are regenerated and your change disappears.
- Re-adding venue names or venue photographs. See BRIEF §2.1 — photographs identify a
  venue as surely as text does.
- Adding a Travel or Hotels section. Deliberately excluded (BRIEF §2.1).
- Writing the email address literally anywhere. See BRIEF §2.2.
- Putting a venue name in a commit message. `.gitignore` cannot help you and the build
  audit does not read commit messages.
- Adding any external `<script>`, `<link>`, font or image. Two things break at once: the
  CSP refuses it, and the offline WhatsApp file has no network to fetch it with.
- Adding a `style=""` attribute. Blocked by the CSP. Use a class.
- Using `innerHTML`. There is no reason to; use the `el()` helper.
- Running speaker portraits through a generative upscaler. Tested, rejected, evidence in
  BRIEF §7.3. A conventional resample (Lanczos, canvas) is fine.
- Trusting a colour value you did not sample from the artwork. Three times wrong so far.
- Assuming an image is big enough because it looks fine on desktop. Check every
  breakpoint — 1080, 860 and 480 — and size for the largest box the image can occupy.

---

## Status

Working, deployed, and passing every check it has: redaction audit, zero CSP violations
on both builds, 20 colour pairs all AA, no horizontal overflow or console errors at
1440 / 1080 / 860 / 480 / 390 px.

**Blocked on files from the client:**

1. **Autumn Munich hero.** The client has chosen a photograph (a real one — better than
   any generated candidate). It has been shown, not yet supplied as a file. Once it is:
   drop it into `assets/img/`, point the hero `{{IMG:}}` at it, re-run
   `make_hero_variants.js`, update `HERO_FILE` in `build.py`.
2. **Logo files.** Colour values were extracted; the PNG/SVG files themselves have not
   arrived. `favicon.png` is a 480×295 rectangle being used as a square icon.
3. Willkie Farr & Gallagher logo — the cell is typeset text as a placeholder.
4. Press photographs for the twenty speakers (BRIEF §7.3), colour photographs of Gregg
   Hill and Brenda Exline (§7.4), the video, the city silhouettes (§8).

**Decisions the client owes:** FAQ / News (left out for now, not as empty sections);
launching publicly vs staying a noindexed preview; single-page vs multi-page (BRIEF §8);
whether the venue names warrant a private repo after all (§2.3).

Every change and the reasoning behind it is in `docs/BRIEF.md`, §10 onward.
