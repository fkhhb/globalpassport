# Global Passport Series — website

Source for the Global Passport Series site. GPS is an invitation-only summit series
for families, run by Adelphi Global LLC. Next summit: **Munich, 30 September – 2 October 2026**.

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
git clone <this repo>
cd global-passport-series
python3 build.py            # → dist/global-passport-series.html
open dist/global-passport-series.html
```

No dependencies. Python 3.8+ standard library only. No npm, no framework, no CSS
preprocessor.

---

## How this works

The site is distributed as **one self-contained HTML file** that is sent to prospective
guests over WhatsApp and must work with no network connection. That rules out linked
image files in the distributed artefact.

But a repository full of base64 blobs is impossible to review or diff. So:

- **Source** keeps images as real files in `assets/img/`, and the markup carries
  `{{IMG:filename}}` placeholders.
- **`build.py`** inlines them into a single file in `dist/`.

```
index.template.html  +  assets/img/*     ──build.py──▶  dist/global-passport-series.html
     (edit this)        assets/fonts/*                      (never edit this)
                        (edit these)
```

Fonts work the same way: the woff2 files are real files, `{{FONT:filename}}` in the
markup, inlined at build time. The page makes **no network requests at all** — that is
deliberate, see BRIEF §7.2.

The build was verified to reproduce the previously distributed file byte for byte
before this pass's changes, so the template + assets are a faithful decomposition
rather than an approximation.

### Commands

```bash
python3 build.py                 # build to dist/
python3 build.py --check         # validate only, write nothing, non-zero exit on problems
python3 build.py --out foo.html  # build somewhere else
python3 build.py --hash "Name"   # print a denylist digest to paste into build.py

python3 tools/fetch_fonts.py     # re-download the woff2 faces (the only network step)
```

`--check` is worth wiring into CI. Every build is audited for the redacted venue strings
(matched by hash against every 1–4 word window of the markup) and for any bare email
address, and warns if the output exceeds 5 MB (the comfort limit for sending as a single
file).

---

## Layout

```
index.template.html      markup + inline CSS/JS, with {{IMG:...}}/{{FONT:...}} placeholders
build.py                 inliner + redaction audit
assets/img/              45 images
assets/fonts/            8 woff2 faces + OFL.txt licences
assets/manifest.json     path, dimensions, byte size
tools/fetch_fonts.py     re-download the web fonts
tools/make_city_silhouettes.py   drawn SVG city silhouettes
redactions.local.txt     plaintext denylist — GITIGNORED, never commit
dist/                    build output (gitignored)
docs/BRIEF.md            full handover: constraints, decisions, known issues, roadmap
```

---

## Editing

**Content and layout** → `index.template.html`. One file, inline `<style>` and `<script>`.
Sections are `#about`, `#leadership`, `#speakers`, `#munich`, `#calendar`, `#sponsors`,
`#contact`.

**Speakers** → the `const speakers = [...]` array near the bottom. Each entry is
`{name, role, img, bio}`; `img` is an `{{IMG:...}}` placeholder.

**Colours** → the `:root` block. `--crimson` (#A0322D) and `--navy` (#273D68) are the
brand accents, both measured from the logo artwork so the mark and the accents match
exactly. Note that navy is unreadable on the dark sections — see BRIEF §5.

**Type** → Newsreader for headlines, IBM Plex Sans for everything else. Client-chosen
from five options. Do not change unasked.

**Images** → drop the file in `assets/img/` and reference it as `{{IMG:filename}}`.
Check BRIEF §6 first if it came from the original PDFs; several carry a white frame
baked into the pixels.

**Fonts** → `assets/fonts/`, referenced as `{{FONT:filename}}`. Change the weights the
CSS uses and you must update `FACES` in `tools/fetch_fonts.py` and re-run it, or the
new weight will synthesise from the nearest embedded one.

---

## Things that will bite you

- Editing `dist/` by hand. It is regenerated and your change disappears.
- Re-adding venue names or venue photographs. See BRIEF §2.1 — photographs identify a
  venue as surely as text does.
- Adding a Travel or Hotels section. Deliberately excluded.
- Writing the email address literally anywhere. See BRIEF §2.2.
- Re-adding the Google Fonts `<link>`. It would silently reintroduce a network
  dependency the offline artefact cannot rely on. See BRIEF §7.2.
- Putting a venue name in a commit message. `.gitignore` cannot help you and the
  build audit does not read commit messages.
- Running speaker portraits through a generative upscaler. Tested, rejected, evidence in
  BRIEF §7.3.
- Assuming an image is big enough because it looks fine on desktop. Check every
  breakpoint — 1080, 860 and 480 — and size for the largest box the image can occupy.

---

## Status and what's next

Working and current. The build is 4.32 MB, 45 images and 8 font faces, and makes no
network requests.

**Done in the latest pass** (BRIEF §10): the three "Date to confirm" placeholders
removed, which clears the blocker on sending the file to guests; fonts embedded so the offline file keeps its
typography; the redaction denylist moved to salted hashes so this public repo carries
no venue names; anchor targets no longer land under the sticky navbar; `--nav`
variable; skip link and ARIA wiring on the speaker grid.

**Blocked on the client — nothing here can be invented:**

1. Press photographs for the twenty speakers — the weakest assets on the page, and no
   upscaler can fix them without changing what people look like (BRIEF §7.3)
2. Willkie Farr & Gallagher logo file — the cell is typeset text as a placeholder
3. Colour photographs of Gregg Hill and Brenda Exline (BRIEF §7.4)
4. FAQ, Letter from the Founder and News copy (BRIEF §8)
5. An autumn replacement for the Christmas-market hero photograph (BRIEF §7.5)
6. The city silhouette slideshow and the Frame.io video (BRIEF §8)

**Decisions the client owes before more building:**

7. Single-page-with-dropdowns vs genuinely multi-page (BRIEF §8). Option 1 is
   recommended and preserves the single-file artefact.
8. Whether the venue names are sensitive enough to warrant making this repo private
   after all (BRIEF §2.3).

**Deferred on purpose:** re-encoding calendar images for the ≤480px single-column
layout. The right fix is `srcset`, which only the multi-page build makes possible
(BRIEF §7.1).
