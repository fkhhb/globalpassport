# Working on this repository

**Read [`docs/BRIEF.md`](docs/BRIEF.md) before you change anything. §2 is non-negotiable.**
It is the full handover: constraints, every decision and why, and a changelog of each round
of client feedback. `README.md` covers the build; `SECURITY.md` covers what the page
enforces.

This is the website for Global Passport Series, an invitation-only summit series run by
Adelphi Global LLC. It is **live at https://www.globalpassportseries.com** and currently
`noindex` — reachable by link, not discoverable by search. That is deliberate.

## The two things that must never land in this repository

The repository is **public** and git history is **permanent**. Two pieces of information
are kept out of the site *and* out of the repo, because the summits are invitation-only:

1. **The Munich venue names.** Enforced by `build.py` as salted SHA-256 digests checked
   against every 1–4-word window of the built page. The plaintext list lives in
   `redactions.local.txt`, which is **gitignored and must stay that way**.
2. **The contact email address.** Never written literally. Stored as two base64 fragments
   and assembled at runtime; the build fails on any bare address pattern.

Photographs identify a venue as surely as text does — see BRIEF §2.1 before adding an
image. And `.gitignore` does not cover commit messages or PR descriptions: **keep venue
names out of those too.** The audit does not read them.

## Build

```bash
python3 build.py                  # → dist/global-passport-series.html   (one self-contained file)
python3 build.py --linked _site   # → _site/   (the hosted site)
python3 build.py --check          # audit only, write nothing, exit 1 on problems
```

Python 3.8+, standard library only. No npm, no framework.

**Edit `index.template.html` and `assets/`. Never hand-edit `dist/` or `_site/`** — both
are generated and your change disappears.

Run `python3 build.py --check` before every commit. CI gates the deploy on it.

## Things that will bite you

- Adding an external `<script>`, `<link>`, font or image. Two things break at once: the CSP
  refuses it, and the offline single-file build has no network to fetch it with.
- A `style=""` attribute. Blocked by the CSP — it allows the stylesheet by hash only. Use a
  class.
- `innerHTML`. Use the `el()` helper; the speaker grid is built with `textContent`.
- Dropping an image into `assets/img/` and expecting it to appear. It also needs an
  `{{IMG:filename}}` reference in the template and an entry in `assets/manifest.json`.
- Replacing the hero without re-running `tools/make_hero_variants.js` — the `srcset` would
  keep pointing at the old picture. Also update `HERO_FILE` in `build.py`.
- Running speaker portraits through a generative upscaler. Tested and rejected, evidence in
  BRIEF §7.3. A conventional resample (Lanczos, canvas) is fine.
- Trusting a colour you did not sample from the artwork. Wrong three times so far.
- Assuming an image is large enough because it looks fine on desktop. Check 1080, 860 and
  480 too.

## Deploy

Push to `main` → `.github/workflows/pages.yml` builds, audits and deploys. The
`github-pages` environment accepts the default branch only, so a run from any other branch
fails at the gate before a single step executes.

Two **repository variables** control posture (Settings → Secrets and variables → Actions):
`CUSTOM_DOMAIN` is set to `www.globalpassportseries.com`; `PUBLIC_LAUNCH` is **unset**, so
the site ships `noindex` plus a disallow-all `robots.txt`. Setting it to `true` is the
client's call, not ours. See README → *Deploy*.

## Style

Match the surrounding code. The template is one file with an inline `<style>` and
`<script>`; comments in it explain *why*, not *what*. Keep that.
