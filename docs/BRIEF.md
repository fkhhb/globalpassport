# Global Passport Series — Handover Brief

**Last updated:** 7 September 2026
**Audience:** whoever picks this up next (human or AI session)
**Read this before touching anything.** Several decisions in this repo look
arbitrary and are not. The ones that matter most are in §2.

---

## 1. What this is

Global Passport Series (GPS) is an **invitation-only summit series for families** —
not an investment-banking or commercial conference. It is run by Adelphi Global LLC.
The tagline is *For families by families*.

Summits to date and planned:

| When | Where | Status |
|---|---|---|
| 18–19 June 2025 | London | past |
| 17–19 February 2026 | Palm Beach | past |
| **30 September – 2 October 2026** | **Munich** | **next** |
| November 2026 | United Arab Emirates | upcoming |
| 2027 | Salzburg | upcoming |

The current artefact is a **single self-contained HTML file** with every image
embedded as base64. It is distributed by sending that one file over WhatsApp to
prospective guests. It must keep working with no network connection.

The goal of this repo is to grow that into a **full website** while preserving the
single-file artefact as a build output. Both matter. Do not discard one for the other.

**Related organisation:** [newportglobalsummit.com](https://newportglobalsummit.com) is a
sibling, not a competitor — John Royall appears on both, and NGS runs its own
"NGS Passport Series" events through Adelphi Global. Its information architecture is the
agreed reference for the full site (see §8). One thing on it must **not** be copied: see §2.

---

## 2. Hard constraints — read this section twice

These are not style preferences. Breaking them causes real-world harm to the client.

### 2.1 Venue names are redacted on purpose

GPS is invitation-only and the organisers do not want uninvited people turning up.
Every Munich venue name was deliberately removed. The build script fails if any of
them reappears.

**The names are not written down in this repository.** There are eight of them,
the longest three words. They are enforced as salted SHA-256 digests in
`build.py` (`FORBIDDEN_HASHES`), and the build audit hashes every 1–4 word window
of the finished markup to find them. A name that comes back fails the build,
without the repo ever carrying the list — see §2.3 for why that matters here.

The plaintext list lives with the client, and locally in `redactions.local.txt`,
which is gitignored. If you have that file, `build.py` also does a plain
substring check against it. If you do not, the hash audit still protects you.

To register a further term: `python3 build.py --hash "The Name"` and paste the
printed line into `FORBIDDEN_HASHES`. Do not paste the name itself.

What stays: the city, the dates, session times, and dress codes. Those are useful to
real invitees and useless without an address. The programme says
*"Venue shared with confirmed guests"*.

Three consequences that are easy to get wrong:

- **The venue photo grid was deleted, not hidden.** Four photographs of the actual rooms
  were removed entirely. Photographs identify a venue as surely as text: one of them
  carried the venue's own name in illuminated signage across the facade, and another had
  distinctive painted murals that fall to a reverse image search in seconds. If you
  re-add venue imagery, you have undone the redaction regardless of what the captions say.
- **CSS hiding is not redaction.** This file is handed directly to people. `display:none`,
  a JS gate, or a comment leaves the string in the source for anyone who opens it in a
  text editor. Strings must be *removed*.
- **Do not add a Travel or Hotels section.** Newport Global Summit has one and it is the
  single riskiest thing on that site to borrow. Recommending Munich hotels narrows the
  venue down sharply — especially since one of the venues *is* a hotel. The client already
  ruled Travel out. Keep it out.

### 2.2 The contact address must not appear in the source

A single mailbox on the project domain. It is never written literally anywhere in
the markup, and deliberately not written out in this document either. It is stored as
two base64 fragments in `data-` attributes and assembled at runtime; the `@` itself is
built with `String.fromCharCode(64)` so no `@`-next-to-domain pattern exists in the
file at all. Links read **"Email us"** and **"Email us about
sponsorship"**, and carry `data-s` subject lines so enquiries can be triaged.

The build script greps for a bare address pattern and fails if one appears. That
regex catches *any* address, which is why the audit does not need to — and no longer
does — carry the real one in a denylist.

This stops bots that scrape raw HTML, which is the common case. It does **not** stop a
human reading the source, nor a headless-browser scraper. Do not oversell it.

### 2.3 Git history is forever — and this repository is public

**This is the biggest risk in moving to GitHub.** Both redactions above are defeated
completely if any commit, at any point, contains the venue names or the plain address.
Deleting them in a later commit does not remove them; `git log -p` and GitHub's API
still serve the old blob.

`github.com/fkhhb/globalpassport` **is public.** That was checked, not assumed. An
earlier draft of this brief recommended making it private; the repo went public
instead, so the protection had to move into the files themselves rather than rely on
the repo's visibility.

What that changed, concretely:

1. **The denylist is hashed, not written out.** The first version of `build.py` held
   all eight venue strings in plaintext, and §2.1 of this document listed them again.
   Between them, the two files whose job is to enforce the redaction would have
   published exactly what it removes, permanently, on the first push. They are now
   salted digests (§2.1).
2. **The plain address is gone from the audit.** It used to sit in the same denylist.
   The generic bare-address regex is strictly stronger and carries nothing.
3. **`redactions.local.txt` is gitignored** and holds the plaintext for local builds.

Still true, and still on you:

4. Never commit the original source PDFs, the pre-redaction HTML, or notes containing
   venue names. `.gitignore` covers the obvious paths; it cannot cover carelessness.
5. **Watch commit messages and PR descriptions as closely as files.** They are just as
   permanent and are not covered by `.gitignore` or by the build audit.
6. If the page was ever hosted publicly with the venue names or plain `mailto:` in
   place, assume both are already in Google's cache, the Wayback Machine, and harvester
   lists. Worth checking. Redacting now closes the door after the fact.

**Be clear about what the hashing does and does not buy.** It stops the list being
read straight out of a public repo by someone who had no idea. It does not stop
someone who already suspects a particular venue from hashing their guess and
confirming it. If the venue names are genuinely sensitive rather than merely
inconvenient, making the repository private is still the stronger control, and
nothing here replaces it.

### 2.4 Speaker and team portraits — do not run these through a generative upscaler

Twenty named, identifiable public figures. This was tested and the test is the reason for
the rule; see §7.3 for the evidence. Short version: a generative upscaler at these
resolutions does not produce a sharper version of the person, it produces a confident,
plausible, *different* person — and the failure is invisible unless you have the original
side by side. A conventional Lanczos resample has already been applied; that is safe
because it invents nothing.

---

## 3. Current state

```
dist/global-passport-series.html   4.32 MB   45 embedded images   8 embedded fonts
```

(The 3.56 MB / 42 image figure in earlier drafts of this brief was stale before the
fonts were added; the build was already 4.08 MB with 45 images.)

Single page, anchor navigation, no dependencies, no framework, no build tooling beyond
`build.py`. Sections in document order:

| id | class | contents |
|---|---|---|
| — | `nav` | inline SVG logo + tagline, anchor links, mobile toggle |
| — | `hero` | full-bleed Munich photo, headline, date stamp |
| `about` | — | creed, pillars, facts |
| `leadership` | `band` | founder quote + candid, six team members |
| `munich` | — | three-day programme, venues redacted |
| `speakers` | `dark` | 20-portrait grid, click to expand bio |
| `calendar` | `band` | eight city cards in a 4-column grid, past/next/upcoming |
| `sponsors` | — | seven sponsor marks, partnership CTA |
| `contact` | `footer` | "Email us", event meta, colophon |

Two `<script>` blocks: the speakers data array plus grid interaction, and the email
assembly. One inline `<svg>`: the GPS mark in the nav.

---

## 4. Repo layout and how to build

```
.
├── index.template.html      markup with {{IMG:filename}} placeholders — EDIT THIS
├── build.py                 inlines assets → dist/, runs redaction audit
├── assets/
│   ├── img/                 45 real image files
│   ├── fonts/               8 woff2 faces + OFL.txt (see §7.2)
│   └── manifest.json        path, dimensions, byte size (48 entries: img + silhouettes)
├── dist/
│   └── global-passport-series.html    build output — DO NOT EDIT BY HAND
├── docs/
│   └── BRIEF.md             this file
└── README.md
```

```bash
python3 build.py             # → dist/global-passport-series.html
python3 build.py --check     # validate only, exit non-zero on problems
python3 build.py --hash STR  # print a denylist digest for STR (§2.1)

python3 tools/fetch_fonts.py         # re-download the woff2 faces
python3 tools/fetch_fonts.py --check # report which are present
```

`fetch_fonts.py` is the only thing here that touches the network, and the files it
writes are committed, so an ordinary build never does.

**Edit `index.template.html`, never `dist/`.** The dist file is generated. A hand edit
there is silently destroyed on the next build.

The build has been verified to reproduce the current distributed file **byte for byte**,
so the template + assets are a faithful decomposition, not an approximation.

`build.py` also audits every build for the §2.1 venue strings (by hash) and any bare
email address, and warns if the output exceeds 5 MB. It handles two placeholder kinds:
`{{IMG:name}}` from `assets/img/` and `{{FONT:name}}` from `assets/fonts/`.

---

## 5. Design system

Everything lives in `:root`. There is no CSS framework and no preprocessor.

```css
--ink:      #132339   /* body text, dark section backgrounds */
--ink-deep: #0C1727   /* mobile nav drawer */
--crimson:  #AD2625   /* primary accent — GPS Red, picked from the logo file */
--navy:     #203D6A   /* secondary accent — GPS Navy, picked from the logo file */
--paper:    #FCFBFA   /* page background */
--grey:     #E7EAEE   /* .band section background */
--slate:    #5B6879   /* secondary text */
--brass:    #A9853F   /* small ornaments */
--line:     rgba(19,35,57,.16)
--serif:    "Newsreader", Georgia, "Times New Roman", serif
--sans:     "IBM Plex Sans", -apple-system, ..., Arial, sans-serif
```

**Typography is fixed by the client:** Newsreader for headlines, IBM Plex Sans for
everything else. Five alternatives were presented and this pairing was chosen. Do not
change it without being asked.

**Colour rules learned the hard way:**

- **The navbar is now white** (`--nav:#FCFBFA`), superseding the earlier `#0E162B`.
  That hex had been specified by the client and is why the bar is opaque rather than
  the original `rgba(12,23,39,.97)` with a backdrop blur — at 97% the scrolling
  content behind tints it, so "exact" is only achievable opaque. That reasoning still
  holds if a dark bar ever comes back. See §14 for why it changed.

  One good side effect: `nav .mark svg path{fill:#fff}` is gone. The mark now renders
  in the fills it actually carries, so the logo's red and navy are visible in the
  navbar for the first time.
- **Navy only works on light backgrounds** — still true, and the page is now built
  around it rather than around the exception. `#273D68` on `--paper` is **10.40:1**, so
  navy is the headline colour throughout: hero, speaker names, bio headings. The old
  warning that navy in the hero, speakers or footer would need a lightened variant only
  applied while those sections were dark. The footer inverts it — navy as the
  *background*, white text at 10.75:1.
- **Crimson on dark is decorative only.** That barely binds any more, because almost
  nothing sits on dark. All crimson *text* is on light at 5.8:1–6.8:1, comfortably above
  the 4.5:1 AA threshold. Measured across the rebuilt page, every foreground/background
  pair passes AA; the lowest is 5.49:1, slate on paper.
- **The palette is derived from the logo, not from a brand manual, and has now been
  corrected three times.** Round one: the client specified `#8B1A1A` red and `#1E3A6E`
  navy as "read from the original". Round two: measuring the artwork then available gave
  `#A0322D` and `#273D68` — the stated red was noticeably darker than the real one.
  Round three, current: the client supplied the logo lockups with a colour-picker reading
  off the files themselves — **`#AD2625` red and `#203D6A` navy** — and those are the
  values in use.

  The nav SVG carries the same fills, so logo and accents are identical by construction.
  **They must move together.** Changing the palette without the mark, or the reverse,
  destroys the one property this exercise exists to produce.

  The pattern across all three rounds is worth internalising: every value that came from
  memory, from a description, or from looking at a screenshot was wrong, and every
  correction came from sampling the actual file. If a designer supplies an official SVG,
  sample it before dropping it in — do not trust the accompanying hex values.

  Current contrast: crimson text on paper 6.60:1, navy on paper 10.49:1, white on the
  navy bar 10.84:1.

**Breakpoints: 1080px, 860px, 480px.** Note 860, not 900. Layout shifts:

- ≤1080 — speakers 4 columns, calendar 3, sponsors 3, pillars 2, team 2
- ≤860 — mobile nav drawer, hero stacks with photo on top, most two-column grids collapse
- ≤480 — pillars 1 column, **calendar 1 column** (see §7.1, this one matters)

**The logo is an inline SVG.** It was traced from the supplied raster artwork: the red and
navy regions separated into two masks, contours traced and simplified into two paths with
`fill-rule="evenodd"`. 10 KB, sharp at any size, fills controlled by CSS. This replaced a
PNG that needed a `filter:brightness(0) invert(1)` hack to go white in the navbar — that
hack is gone. The nav shows the mark alone plus the tagline as text; the full lockup with
wordmark was illegible at 26px and duplicated the text beside it.

Curves are traced polygons. Invisible at nav size; at poster scale you would see faceting
on the G. For print, get a real vector file from a designer.

---

## 6. Assets — inventory and provenance

All 42 images were originally **extracted from two PDFs**, which explains most of their
quirks. `assets/manifest.json` has exact dimensions and byte sizes.

| Group | Count | State |
|---|---|---|
| Hero (Munich) | 1 | 3720×2028, generatively upscaled |
| Calendar cards | 5 | ~780×440, upscaled, white frames trimmed |
| Speaker portraits | 20 | 276×396 to 476×573, Lanczos only |
| Team portraits | 6 | 252×301, untouched — adequate at 78px |
| Founder candid | 1 | 1098×969, Lanczos |
| Logos and sponsor marks | 7 | untouched vector-style PNGs |
| City silhouettes | 3 | drawn SVG, see §8 |
| Favicon | 1 | untouched |

**Upscaling history.** Nine city and venue photos went through Higgsfield
(`upscale_image`, provider `bytedance`, the only provider it offers) at 2 credits each.
22 credits were spent in total across the session. Four of those upscales were venue
photos that were subsequently deleted under §2.1 — spent, not recoverable, noted so
nobody re-runs them looking for the results.

**The white frame problem.** London, Palm Beach and the UAE cards each carried a
photo-card frame baked into the pixels from the PDF extraction: a thin dark shadow line
on the outer edge, then roughly 5% of the height in flat white, then the photograph.
Munich and Salzburg were clean.

This is worth knowing because naive detection fails on it in two different ways, and both
were tried before the right approach was found:

- Scanning inward from each edge stops immediately — the outermost pixels are the *dark*
  shadow line, not white.
- Thresholding on brightness alone misclassifies London's sunset sky and Palm Beach's
  pale facades as frame.

What works: **bright AND colourless together.** The frame is achromatic (median
saturation near zero); sky and water are not. Skip 3px for the shadow, then scan while
`median(brightness) > 235 and median(saturation) < 8`. Verify visually against a grey
background — white frames are invisible against the white of most image viewers.

If more assets ever arrive from those PDFs, check them for this before use.

---

## 7. Known issues

### 7.1 Calendar images are undersized on small phones

At ≤480px the calendar collapses to **one column**, so each card image renders about
436 CSS px wide. The cards are ~780×440.

| Device | Needed | Have | Ratio |
|---|---|---|---|
| 480px @2x | 872×654 | 780×440 | 0.67 |
| 480px @3x | 1308×981 | 780×440 | 0.45 |

They were sized for the two-column layout and the third breakpoint was missed. Fine at
2x, soft on 3x flagship phones. **Fixable without spending credits** — the 4K upscales
still exist and can be re-encoded larger. The cost is roughly +1.2 MB, pushing the file
to ~4.8 MB.

The right fix is not to pick a number. It is `srcset`, which the multi-page build makes
possible: serve small files to small screens and large ones to large screens, and the
whole trade-off disappears. Deferred deliberately.

### 7.2 Fonts do not load offline — FIXED

*Was:* the single file embedded every image but pulled Newsreader and IBM Plex Sans
from Google Fonts, so opening it with no network gave perfect layout and images and
**typography falling back** to Georgia and a system sans — on an artefact whose entire
purpose is offline WhatsApp delivery.

*Now:* eight woff2 faces live in `assets/fonts/` and are inlined by `build.py` through
`{{FONT:...}}` placeholders, exactly as images are. The Google Fonts `<link>` and both
`preconnect` hints are gone, so the page makes no network requests at all.

- **Latin subset only.** Every non-ASCII character in the template (`©· à – — “ ”`)
  falls inside Google's latin unicode-range; latin-ext and vietnamese would be dead weight.
- **Only the weights the CSS uses:** Newsreader 300/400/500 normal and 300/400 italic,
  IBM Plex Sans 300/400/500. The old `<link>` also requested Newsreader 600 and italic
  500, which appear nowhere in the stylesheet.
- **Static instances, not the variable font.** Newsreader is variable, and asking for a
  weight *range* returns 129 KB + 143 KB for normal and italic. Single weights return
  static instances at 21–24 KB each — 113 KB for all five against 272 KB for the two.
  The cost is the optical-size axis, which is very subtle at these sizes; 160 KB is not.
- **Cost:** +244 KB, taking the build from 4.08 MB to 4.32 MB. Still under the 5 MB limit.
- Regenerate with `python3 tools/fetch_fonts.py`. Both families are OFL-1.1, which
  permits embedding; the licences are bundled in `assets/fonts/OFL.txt`.

Verified in a headless browser with **every non-`file://` request aborted**:
`document.fonts.status` is `loaded`, all 8 faces resolve, and both families pass
`document.fonts.check()`.

### 7.3 Speaker portrait resolution — and why it stays as it is

Every speaker portrait is below 1× of even its desktop requirement; the worst are at 0.43×.
This is the most undersized set on the page. A free Lanczos resample with light sharpening
has been applied, capped at 2× native so small sources are not merely inflated.

Generative upscaling was **tested and rejected**, on two images, 4 credits, at the client's
request. The results:

- **David Malpass** (300×408, the best source in the set): much sharper, but the hairline
  visibly receded, the hair thinned, skin was smoothed to a beauty-filter finish, eyebrows
  changed shape, and the architectural background flattened to plain grey.
- **David Shedd** (138×198, the worst source): looks genuinely good in isolation — which is
  the problem. **The spectacle frames were redrawn** into a different shape, hair became
  fuller and whiter with a different part, the mouth expression changed, the face broadened,
  the background was wholly invented.

The client considered applying it only to the greyscale rest state, keeping the original as
the colour hover. That is worse: the CSS transitions `filter`, not `src`, so hovering would
hard-pop between two structurally different faces — building the A/B comparison into the
page for every visitor. Greyscale hides the skin smoothing; it does nothing for hairlines,
spectacle frames or jaw width, none of which depend on colour.

**The real fix is source files.** These are prominent people whose organisations hold
high-resolution press photographs — the World Bank, Fortress, Stephens, Gladstone,
Harvard/MGH, ARK. One email per person. Free, better than any upscaler, no likeness risk.
This is the single highest-value outstanding task.

### 7.4 Two portraits are genuinely greyscale, and one is a visible bug

`.spk .ph img` is `filter:grayscale(1)` at rest and `grayscale(0)` on hover, so the grid
desaturates and blooms into colour. The files themselves are colour — except two:

- **Gregg Hill** — a greyscale file. On hover his tile stays grey while all nineteen others
  turn colour. Noticeable to anyone running a mouse along the row.
- **Brenda Exline** (team) — greyscale, and the team section has no grayscale filter, so she
  sits black-and-white among five colour portraits.

Neither is fixable by upscaling. Both need a colour photograph. Colourising a real person
would be fabrication and is not an option.

### 7.5 The hero photograph is a Christmas market

The Munich hero shows Marienplatz in December — stalls across the square, lit tree beside
the Rathaus. The summit is 30 September – 2 October. At the original 889px this was hard
to see; at 3720px it is unmistakable. An autumn Marienplatz shot would sit better against
the dates. Flagged, not changed — it is an editorial call.

---

### 7.6 Privacy notice — what it does and does not claim

The footer carries a **Privacy and cookies** notice. Read this before changing its copy,
because the wording is load-bearing.

The site sets **no cookies**, and since §7.2 it makes **no network requests at all** —
no fonts, no analytics, no embeds, nothing third-party. So there is nothing to consent
to, and a conventional "we use cookies to improve your experience" banner would be a
false statement on a page handed to guests who were invited personally.

What is there instead is an acknowledgement, built so it stays correct if that changes:

- **Nothing is stored before a choice is made.** Verified: 0 cookies, 0 localStorage,
  0 sessionStorage on first paint.
- **Declining persists nothing.** It writes a `sessionStorage` key so the bar does not
  nag for the rest of the tab, and explicitly clears `localStorage`. A refusal that
  left a permanent marker would be the opposite of a refusal.
- **Accepting is not a precondition for anything.** No content is gated.
- **The choice can be reopened** from the footer link, which clears both stores.
  Withdrawal has to be as easy as consent.
- **It never appears on `file://`.** The WhatsApp leave-behind is a local file with no
  server, no cookies and no data controller; a notice there would be theatre, and
  storage on `file://` is unreliable anyway. Hosted builds show it, the artefact does not.
- **Every storage access is wrapped in try/catch.** Private mode and `file://` can
  *throw* on access rather than return null, and the privacy notice must never be the
  thing that breaks the page.

`window.gpsPrivacyChoice` is left as `'accepted'`, `'declined'` or `null` for any future
script to gate on. **If analytics are ever added, they must check it** — and at that
point the copy above stops being true and must be rewritten to describe what is actually
collected.

### 7.8 Two build shapes, and why

`build.py` emits two things from the same source:

| | shape | html | use |
|---|---|---|---|
| default | one self-contained file | 4.33 MB | WhatsApp, offline |
| `--linked DIR` | index.html + real asset files | 64 KB | hosting |

The single file is right for a file you send someone and wrong for a web page.
Inlined, 4.3 MB of base64 has to arrive before anything paints, no asset can be
cached separately or deferred, and base64 is a third larger than the bytes it
encodes. Measured on a throttle-free local server at 390px, which *understates*
the gap because there is no real network in play:

```
hosted   (linked)  11 requests   1.31 MB before load   LCP 108 ms
artefact (single)   1 request    4.33 MB before load   LCP 128 ms
```

The rest of the images arrive as you scroll rather than never being needed at
all. Over a phone connection the 3 MB that no longer blocks first paint is the
whole story.

Both shapes share one template. `loading="lazy"` and `decoding="async"` sit on
every below-the-fold image and are inert in the single-file build, where the data
URI is already local. The hero carries `fetchpriority="high"` and is never lazy —
it is the LCP element.

### 7.7 What was deliberately not added

- **JSON-LD `Event` structured data.** Standard practice for an events site, and wrong
  here: it exists to make an event more discoverable in search, and GPS is
  invitation-only with venues redacted under §2.1. Better search placement for "summit
  in Munich" is the opposite of the goal. Revisit only if the client says the summit
  should be publicly promoted.
- **A Travel or Hotels section.** §2.1. Still out.
- **FAQ / Letter from the Founder / News copy.** §8 — the structure could be built, but
  the words are factual claims about GPS and must come from the client.
- **Dropdown nav.** §8 option 1 is the recommended architecture, but the target menu is
  mostly the three sections above, which do not exist yet. Dropdowns to nowhere are
  worse than the current flat anchor nav. Build it when the copy arrives.

## 8. Roadmap — from one page to a full site

The agreed reference is Newport Global Summit's information architecture, **minus Travel
and Donate** (Travel for the §2.1 reason; Donate because GPS is not a 501(c)(3) soliciting
tax-deductible gifts).

Target menu:

- **About** — About · FAQ · Board of Directors · Letter from the Founder · News
- **Events** — Munich 2026 · All Events · Sponsor
- **Contact**

Mapped against what exists: About, leadership (= Board of Directors), Munich 2026 (= their
NGS26), the calendar (= All Events), Sponsors and Contact are all built. Speakers is an
extra GPS has and they do not.

**Three sections need to be created: FAQ, Letter from the Founder, News.** Structure can be
built now; **the copy must come from the client** — these are factual claims about GPS and
must not be invented. The existing founder quote is a starting point for the Letter.

**Architecture decision to make first.** Newport is genuinely multi-page. GPS is one file
with anchors. Two options:

1. **Keep one page, group the nav visually into dropdowns that jump to anchors.** Newport's
   look, WhatsApp distribution survives. Lower risk. *Recommended.*
2. **Go genuinely multi-page.** Better for SEO and for a growing News section, but the
   single-file artefact can no longer be the whole site — it becomes a separate "leave-behind"
   build of the landing page only.

Do not start option 2 without an explicit decision from the client. The single-file property
has been protected through every change in this project and is not incidental.

### Open threads not yet started

- **Silhouette slideshow.** The client wants a slideshow of city silhouettes for the summit
  locations, partly to fill the hole left by the deleted venue grid. Deriving silhouettes
  automatically from the photos was tried and looks bad — scratchy edge-detection line art,
  not silhouettes. Drawn SVG is the way, and `tools/make_city_silhouettes.py` now holds
  three (Dallas, New York, Paris) that establish the house style: 4:3, `--ink` field,
  `--navy` far skyline, light landmarks, thin horizon. Extending it to London, Palm Beach,
  Munich, the UAE and Salzburg is mechanical. **Still blocked on one thing:** the client
  referred to silhouettes "as already done" somewhere — find that reference before drawing
  more, in case a set already exists.
- **Frame.io video embed.** The client wants a video embedded. Frame.io is a review tool,
  not a video host: share links are access-controlled, revocable, block automated access,
  and almost certainly block iframing. More fundamentally an embed needs the network, which
  breaks offline. Options: get the MP4 and inline it (15–30s muted loop ≈ 2–4 MB, taking the
  file to 5–7 MB), or host unlisted on Vimeo/YouTube for the hosted build only, or a poster
  image linking out. **Blocked:** needs a decision on offline vs hosted, and the MP4.
- **Willkie Farr & Gallagher logo.** Added as the eighth sponsor at the client's request,
  but no logo file was supplied and willkie.com is outside the sandbox network allowlist,
  so the cell currently carries the firm name typeset in the serif face instead of a mark.
  It reads deliberately rather than broken, but it is a placeholder. Ask for a PNG or SVG.
- **Dates for Dallas, New York and Paris — resolved by dropping the line.** These were
  added as past summits on request and their dates were never supplied. They read
  "Date to confirm", which is placeholder text and reads as unfinished on a page handed
  to guests. The client's position is that the exact dates do not matter for events that
  have already happened, so the `.when` line was removed from those three cards rather
  than filled in with anything invented.

  The cards now read tag + city, and all eight tiles still render at identical height.
  Five of the eight carry a date and three do not, which reads as deliberate in a way
  that three "Date to confirm" labels did not. If years ever surface, add them back as
  a plain `<div class="when">` and the layout absorbs it with no other change.

  **This was the blocker on sending the file to guests. It is now clear.**
- **The Dallas, New York and Paris card images are AI-generated, not photographs.**
  Record this; it is not obvious from looking at them. No usable photographs of these
  cities existed in the asset set and none could be fetched (the sandbox network allowlist
  blocks image sources), so they were generated with Higgsfield `kling_omni_image` at
  0.5 credits each, 4 credits including retries. Every candidate was reviewed for landmark
  accuracy before selection: the first two Dallas attempts were **rejected because Reunion
  Tower was missing**, which is the one structure that makes a Dallas skyline identifiable,
  and a re-prompt naming the tower explicitly fixed it. The chosen frames show Reunion
  Tower and Fountain Place for Dallas, the Empire State Building for New York, and the
  Eiffel Tower over Haussmann rooftops with the Seine for Paris.
  Two consequences worth carrying forward. First, if GPS ever needs to state that its
  imagery is photographic, these three do not qualify — replace them with real photographs.
  Second, generated cityscapes get landmarks wrong by default rather than by exception;
  any future generation must be reviewed against the real skyline, not accepted because it
  looks plausible. Drawn SVG silhouettes of all three are kept in
  `assets/fallback-silhouettes/` (generator: `tools/make_city_silhouettes.py`) as a
  non-generated fallback if the client would rather not use AI imagery.
- **Press photographs** for the twenty speakers — see §7.3.
- **Colour photographs** of Gregg Hill and Brenda Exline — see §7.4.
- **Autumn Munich hero** — see §7.5.

---

## 9. Pitfalls — things that cost time, so they do not cost it twice

1. **Verify image problems against a grey background.** White frames, white borders and
   letterboxing are invisible in viewers that render on white. The user spotted the Dubai
   frame; London and Palm Beach had the same defect and nobody had noticed.
2. **Check whether a visual effect is in the pixels or in the CSS before fixing it.** The
   speaker portraits look black-and-white; they are colour files with a `grayscale(1)`
   filter. Two rounds of measurement were spent before checking the stylesheet.
3. **Measure against the box an image actually renders into, at every breakpoint.** An early
   assessment declared four images "already fine" based on desktop only, and missed that
   venue photos go full-width on phones. §7.1 is the same mistake surviving into the current
   build. Always check the *largest* box an image can occupy.
4. **Images appearing twice need two sizes.** The Munich photo is both the hero and a
   calendar card. Encoding the hero version into the card would have wasted ~1.2 MB.
5. **`upscale_image` needs explicit `width`/`height`** — the server does not infer them from
   the image. And it takes a flat 2 credits regardless of 2k or 4k, so choose the *smallest*
   resolution that meets the need: a smaller jump means less invented detail.
6. **Preflight with `get_cost` before spending.** It submits nothing.
7. **Higgsfield presigned upload URLs are on `*.s3.amazonaws.com`** and outputs on
   `*.cloudfront.net`. Both are in the sandbox allowlist. A 403 from `test.s3.amazonaws.com`
   with `server: AmazonS3` and no `x-deny-reason` header is S3 refusing anonymous listing,
   **not** a blocked domain — check for the header before concluding the allowlist is wrong.
8. **The `[third_party_mcp_app]` connectors need per-call approval.** If a call returns
   "No approval received", the connector is fine — the permission prompt is what needs
   granting. Retrying identically will not help.

---

## 10. Changelog — 7 September 2026

Verified before starting: `build.py` reproduced the previously distributed
`global-passport-series.html` **byte for byte** (md5 `90cadee0…`), so the template and
assets are a faithful decomposition of it.

**Redaction hardening (§2.1, §2.3)** — the repository was confirmed **public**, which
inverted the assumption the previous draft of this brief was written under. `build.py`
had all eight venue names and the plain contact address in a plaintext `FORBIDDEN` list;
§2.1 of this document listed the names again; §2.2 spelled out the address's local part.
On the first push, the two files whose purpose is to enforce the redaction would have
published exactly what it removes — permanently. Replaced with salted SHA-256 digests
and an n-gram scan. The plaintext moved to a gitignored `redactions.local.txt`.

The new audit is *stricter* than the old one, not just quieter: the old check was a
case-sensitive substring test, so any of the names typed in lowercase would have
sailed through it.
Tested against 10 reintroduction attempts — single word, two words, three words,
umlaut, NFD-decomposed umlaut, lowercase, irregular whitespace, inside an `alt`
attribute, inside an HTML comment, and a bare address — all 10 caught, with no false
positive on innocent text that shares a word with a denylisted phrase.

**Fonts embedded (§7.2)** — closed. Verified with every non-`file://` request aborted.
+244 KB, build now 4.32 MB.

**Anchor targets cleared the sticky navbar.** Every nav link scrolled the section's top
edge to y=0, behind the 66px sticky nav. On desktop the 96px section padding mostly
absorbed it (29px of visible gap above the eyebrow). At ≤860px, where padding drops to
70px, the gap was **3px** — the eyebrow sat jammed against the navbar on every phone
and tablet, which is the primary delivery channel. Added `scroll-margin-top:66px`;
measured 3px → 69px at 390px and 800px, 29px → 95px at 1440px.

**Privacy notice added (§7.6).**

**Smaller things:** `--nav` variable (the §5 tidy-up candidate); `lang="en-GB"`, since
the copy is British throughout; Open Graph and `theme-color` meta; a skip link;
`aria-controls` / `aria-labelledby` wiring between speaker tiles and the bio panel.

**Verified across 1440 / 1080 / 860 / 480 / 390 px:** no horizontal overflow at any
width, all 20 speaker tiles render, bios open and close, the mobile drawer opens and
closes on navigation, the address still assembles at runtime and its `data-` attributes
are wiped after use, and there are no console errors.

**Not changed, and why:** see §7.7. The portraits, the three "Date to confirm" cards,
the Willkie logo, the greyscale Gregg Hill and Brenda Exline files and the Christmas
market hero are all blocked on client-supplied assets — none of them can be invented,
and §2.4 rules out the one shortcut that looks like a fix.

---

## 11. Changelog — client review round

Three voice notes and a WhatsApp message from the client. What each asked for
and what happened:

**Already done before the request landed** — worth recording so nobody redoes them:

- *"Add Willkie Farr & Gallagher as a sponsor."* Present as the eighth cell since
  the previous round. Still typeset text rather than a mark (§8) — willkie.com is
  outside the sandbox network allowlist, confirmed again this round, so the logo
  still cannot be fetched here.
- *"Replace 'Partner with us in Munich' with 'Partner with us'."* The string was
  already just "Partner with us"; no "in Munich" variant existed.
- *"Remove 80 seats per Summit, three days together, five cities."* These were the
  three `.facts` stat tiles, already removed from the markup earlier. The dead
  `.facts` CSS is now gone too, along with the `.venues` rules left behind by the
  §2.1 venue-grid deletion.
- *"Add Dallas, New York and Paris to past events."* Already in the calendar.

**Changed this round:**

- **Section order.** *"Bring the Munich 2026 programme up and move the speakers
  further down."* Was about → leadership → munich → speakers → calendar. Now
  **about → munich → leadership → calendar → speakers**. The nav follows the same
  order, or the anchors read as jumbled.

  The `band` classes were reassigned rather than moved with their sections: the
  page alternates paper / grey / paper / grey / dark, and simply relocating the
  sections would have put two paper sections and then two grey ones back to back.
  `munich` gains `band`, `leadership` loses it.

- **The contact address is now visible** under "Partner with us", as asked. It is
  still absent from the HTML source: a `data-show` attribute tells the existing
  runtime assembler to write the address into the link's own text. Verified — the
  link reads as the address, and a regex for a bare address over the served source
  finds nothing. This costs no privacy that the `mailto:` href did not already
  give away to anything running JavaScript. §2.2 holds.

- **Hosted build shape** (§7.8) and the GitHub Pages preview deploy.

**Explicitly retracted by the client mid-sentence:** using the logo instead of the
Munich hero image — *"although no, I think you can leave that."* Not changed.

**Still blocked:**

- **Logo colours.** *"Make the Global Passport Series logo congruent with the
  colours of the logo I sent, and adjust the colours."* The referenced logo file
  has not reached this repo. Note that §5 already describes this exercise being
  done once: the palette was measured off the supplied artwork, giving `#A0322D`
  and `#273D68`, and the nav SVG carries the same fills, so mark and accents are
  identical by construction. Either a different logo file is meant, or the earlier
  work was not seen. **Get the file before changing any colour** — the current
  palette is measured, not guessed, and replacing it blind would undo §5.

---

## 12. Changelog — second client review round

**Done:**

- **The speakers section is now "Past participants and speakers."** The client asked
  for these people to be described as previous participants and speakers rather than
  as a speaker line-up. The old framing ("Speakers" / "the faculty from Palm Beach")
  read as a promise that the same faculty returns for Munich. Nav item is
  "Participants" — checked at 1440/1200/1080/900/870px, the menu still clears the
  logo by 24px at its tightest, just above the 860px drawer breakpoint.

**Client decisions recorded, no code change needed:**

- **The AI-generated Dallas, New York and Paris cards stay** ("so lassen passt").
  §8's note still applies: if GPS ever has to claim its imagery is photographic,
  these three do not qualify.
- **Domain is `globalpassportseries.com`**, but it is not being pointed at the site
  yet. When it is: add a `CNAME` file to the Pages deploy, and set `og:url`.
- **FAQ and News stay as placeholders for now** — read as "leave them for later",
  so no empty sections were added to a live page. Worth confirming, since the
  German could also be read as "add them as placeholders".

**Blocked, and specifically why:**

- **Logo colours.** The logo was shown in chat as a pasted image rather than an
  attached file, so its pixels cannot be sampled here. This matters more than it
  sounds. §5 records that the client's own stated values (`#8B1A1A` red,
  `#1E3A6E` navy, "read from the original") were both wrong when the artwork was
  actually measured, which is how the palette became `#A0322D` / `#273D68`. Judging
  a colour by eye off a recompressed screenshot is the same mistake with extra
  steps. The supplied logo does confirm the *structure* is right: red G and S,
  navy P, which is exactly what the traced SVG carries. **Get the PNG or SVG as a
  file, measure it, then change `--crimson`, `--navy` and both SVG fills together**
  — they are one system, and moving the palette without the mark breaks §5's
  congruence-by-construction.
- **Autumn hero photograph.** Client prefers autumn over the Christmas market
  (§7.5) — agreed, but no such photo exists in the asset set and every image
  source is outside the sandbox network allowlist, re-confirmed this round
  (unsplash, pexels, wikimedia and willkie.com all fail at the proxy).
- **City silhouettes.** The client has none and asked whether images can be pulled
  from the internet. Two separate problems with that: the sandbox cannot reach
  image hosts, and more importantly a photograph found online is not licensed for
  a commercial site just because it is reachable. The safe answers are properly
  licensed stock, or extending the drawn SVGs already in
  `assets/fallback-silhouettes/` via `tools/make_city_silhouettes.py`, which owe
  nobody a licence. See §8.

---

## 13. Changelog — monochrome calendar, and the autumn hero attempt

**Calendar cards are now all greyscale.** Client's request. Previously only
`.ev.past` was desaturated, so past summits were monochrome and Munich, the UAE
and Salzburg were in colour. Now every card image is `grayscale(1)` and the past
ones keep the extra `opacity:.72`.

Worth knowing why the opacity step stayed: colour was doing the past/upcoming
separation, and removing it without a replacement would have flattened the row
into eight equal tiles. The fade now carries that hierarchy, and the crimson
`.ev.next` bar and "Next summit" tag read *louder* against a fully monochrome
field than they did against seven colour photographs.

**Autumn hero (§7.5) — generated, not yet landed.** Four candidates at
5056x3392, `nano_banana_pro` 4K 3:2, 4 credits total, preflighted with
`get_cost` first. The prompt names the Neues Rathaus, the Frauenkirche's green
copper onion domes and the Mariensaeule explicitly, per §8's lesson that naming
the landmark is what fixed Dallas.

**They cannot be pulled into the repo from this sandbox.** `*.cloudfront.net`,
where Higgsfield serves its outputs, is denied by this environment's network
policy (403 on CONNECT, confirmed against the proxy's own status endpoint).
§9.7 records CloudFront as being *inside* the allowlist — that was a previous
sandbox and is no longer true. So the loop is now: generate here, client reviews
in the widget, client sends the chosen PNG back as a file attachment, and only
then can it be committed.

**Whoever picks the frame must check it against the real square**, not against
whether it looks plausible — §8, and the two Dallas attempts that were rejected
for missing Reunion Tower. For Marienplatz the three tells are: the Neues
Rathaus tower (neo-Gothic openwork stone spire, not a plain steeple), the
Frauenkirche's two *onion* domes (green copper, rounded — not pointed spires),
and the Mariensaeule column standing free in the square. A Munich audience will
catch any of the three being wrong, and this client's guests are Munich-based.

Note also that replacing the hero with a generated frame makes it the **fourth**
AI image on the page and by far the most prominent. §8's consequence stands and
grows: if GPS ever has to state that its imagery is photographic, the hero would
be the first thing to fail that claim.

---

## 14. Changelog — white, red and blue

The client sent a page from their own GPS document and asked whether the site could
work "mit weiss und rot und blau wie hier". That document is white-led: navy serif
headline, red italic tagline, letterspaced caps eyebrow. The site was the opposite —
near-black navbar, dark hero panel, dark speakers section, near-black footer, white
text on all of them.

| | was | now |
|---|---|---|
| navbar | `#0E162B` | `--nav:#FCFBFA`, navy links, crimson hover rule |
| nav mark | forced white | its own red and navy fills |
| hero panel | `--ink`, white text | `--paper`, navy headline, crimson italic |
| speakers | `.dark` | light, navy names, grey bio panel |
| sponsors | paper | `.band`, to keep the alternation |
| footer | `--ink-deep` near-black | `--navy` |

**The band rhythm had to be re-cut, not just recoloured.** Sections alternate paper
and grey. Turning speakers light without touching sponsors would have left two paper
sections adjacent, so sponsors took the `band` class. The page now runs paper, grey,
paper, grey, paper, grey, navy from About to the footer.

**Added the client's own eyebrow line**, "An invitation-only circuit for global
families", above the hero headline. Their copy, lifted from the document they sent,
and it says what GPS *is* before the headline says what it does.

**This is an accessibility improvement, not only a cosmetic one.** §5 used to warn
that navy was unusable outside light sections at 1.61:1 on `--ink`. Navy is now the
headline colour on paper at 10.40:1. Every pair on the rebuilt page was measured in
the browser against its real computed background: 20 checks, no failures, lowest
5.49:1. Verified at 1440, 860 and 390px — no horizontal overflow, no console errors.

Two things that would have broken silently and were caught by checking rather than
assuming: the mobile drawer needed a shadow it never needed while dark, and the
privacy bar and skip link had to be moved off `--nav` onto `--navy` explicitly —
both were relying on that variable being dark and would have gone white on white.

---

## 15. Changelog — logo-sampled palette, navy header

**The palette now comes from the logo files** — red `#AD2625`, navy `#203D6A`,
replacing `#A0322D` / `#273D68`. Both inline `fill=` attributes on the nav SVG changed
in the same commit; see §5 on why they cannot drift apart.

**The header is navy again**, at the client's request ("I feel like the header menu
could be blue"). It is `--navy`, the brand colour shared with the footer, rather than
the old near-black `#0E162B` or the white it briefly carried. Navy bookends the page
top and bottom with white content between, closer to the client's own document than an
all-white treatment.

**The mark goes back to white fills in the navbar, and that is forced rather than
chosen:** on its own brand navy, the logo's navy `P` measures 1.6:1 against the bar and
disappears. A coloured mark cannot sit on one of its own colours. The inline fills still
carry the real values for every other context.

Re-audited after both changes: 20 pairs measured in-browser against real computed
backgrounds, no AA failures, lowest 5.49:1. No overflow or console errors at 1440, 1080,
860 or 390px. The mobile drawer follows `--nav`, so it returned to navy with the bar.

**Which lockup goes where** (three were supplied):

| lockup | use |
|---|---|
| mark only | the navbar — already correct, the traced SVG is this one |
| mark + wordmark | the footer colophon (`logo-footer.png`, reversed to white) |
| mark + wordmark + tagline | the full lockup |

The site sets "For families by families" as **live text** beside the navbar mark rather
than baking it into an image. Worth keeping: it stays selectable, translatable and sharp
at any size, and it means the tagline is not a 480px raster.

**Still not landed:** the logo files themselves never reached the repo — they were
pasted into chat as images, which renders them visible but writes no file, so only the
colour values crossed over. `assets/img/favicon.png` and `logo-footer.png` are both
still the original 480x295 extractions, and the favicon in particular is a 480x295
rectangle being used as a square icon.

---

## 16. Note — the Pages workflow is main-only

`.github/workflows/pages.yml` triggers on pushes to `main` and on
`workflow_dispatch`, and deliberately not on any other branch.

The `github-pages` environment accepts deployments from the default branch only.
A run started by a feature branch fails at the environment gate *before any step
executes* — no checkout, no build, no audit — so it produces a red X that can
never go green no matter what the branch contains. Listing a feature branch under
`on.push.branches` only manufactures noise.

This was learnt twice: once when the site still lived on the working branch and
the deploy would not run at all (which is why it was merged to `main`), and again
when fast-forwarding that branch to `main` produced an immediately-failing run for
a commit that had already deployed successfully from `main` seconds earlier.

To redeploy without a code change, use the workflow's **Run workflow** button on
`main`, or `workflow_dispatch` via the API.
