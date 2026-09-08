#!/usr/bin/env python3
"""
Build the distributable single-file HTML for Global Passport Series.

Reads  index.template.html  (markup with {{IMG:...}} / {{FONT:...}} placeholders)
Reads  assets/img/*         (the real image files)
Reads  assets/fonts/*       (the real woff2 files)
Writes dist/global-passport-series.html  with every asset inlined as base64.

Why a build step at all:
  The site must survive being sent over WhatsApp as ONE file that works with no
  network. That rules out linked assets in the distributed artefact. But a repo
  full of base64 blobs is unreviewable and undiffable, so the SOURCE keeps images
  and fonts as real files and this script produces the single-file artefact.

Usage:
    python3 build.py                 # -> dist/global-passport-series.html
    python3 build.py --out other.html
    python3 build.py --check         # verify every placeholder resolves, write nothing
    python3 build.py --hash "Some Venue"   # print a denylist entry (see below)
    python3 build.py --noindex       # add robots noindex (preview deploys only)
    python3 build.py --linked _site  # hosted build: linked assets, not inlined

Two output shapes, same source:

  default   ONE file, every asset base64-inlined. For WhatsApp. Works offline.
  --linked  index.html plus real asset files. For hosting.

The single file is the right answer for a file you send someone and wrong for a
web page: 4.3 MB of base64 has to arrive before anything paints, none of it can
be cached separately, none of it can be deferred, and base64 is a third larger
than the bytes it encodes. Linked, the HTML is ~60 KB, images stream in as
needed and the browser caches them across visits.
"""

import argparse
import base64
import hashlib
import mimetypes
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "index.template.html"
IMG_DIR = ROOT / "assets" / "img"
FONT_DIR = ROOT / "assets" / "fonts"
DEFAULT_OUT = ROOT / "dist" / "global-passport-series.html"

# Optional, gitignored. One forbidden term per line, '#' comments allowed.
# If present its terms are checked as plaintext as well as via the hash list.
LOCAL_TERMS = ROOT / "redactions.local.txt"

IMG_PLACEHOLDER = re.compile(r"\{\{IMG:([^}]+)\}\}")
FONT_PLACEHOLDER = re.compile(r"\{\{FONT:([^}]+)\}\}")
ANY_PLACEHOLDER = re.compile(r"\{\{(?:IMG|FONT|CSP|FONT_PRELOAD|HERO_SRCSET):[^}]*\}\}|\{\{(?:CSP|FONT_PRELOAD|HERO_SRCSET)\}\}")

# ---------------------------------------------------------------------------
# Hosted-build-only tokens. Each expands to "" in the single-file artefact.
#
# {{HERO_SRCSET}}   srcset/sizes for the hero <img>, from whichever of these
#                   width variants exist in assets/img/. The hero is the LCP
#                   element and a third of all image bytes; a phone needs ~1200px
#                   of it, not 3720. Variants come from tools/make_hero_variants.js
#                   (optional, needs Playwright) - a missing one is simply skipped,
#                   so the build never depends on that tool.
# {{FONT_PRELOAD}}  <link rel=preload> for the faces used above the fold, so
#                   text renders in the right face on first paint instead of after
#                   the stylesheet has been parsed and the fonts discovered.
#                   Pointless with data: URIs, hence linked-only.
# ---------------------------------------------------------------------------
HERO_FILE = "01-newport-cliff-walk-hero.jpg"
HERO_VARIANTS = [("01-newport-cliff-walk-hero-w1000.jpg", 1000),
                 ("01-newport-cliff-walk-hero-w1600.jpg", 1600),
                 ("01-newport-cliff-walk-hero-w2000.jpg", 2000),
                 (HERO_FILE, 2400)]
# The hero panel is 100vw on phones/tablets and 53vw of the viewport above 860px.
HERO_SIZES = "(max-width: 860px) 100vw, 53vw"
PRELOAD_FONTS = ["newsreader-latin-300.woff2", "newsreader-latin-300italic.woff2",
                 "ibm-plex-sans-latin-300.woff2", "ibm-plex-sans-latin-500.woff2"]

# ---------------------------------------------------------------------------
# Content Security Policy, delivered as a <meta> because GitHub Pages cannot
# set response headers. Everything the page needs is itself or a data: URI, so
# default-src can be 'none'. The three inline <script> blocks and the one
# <style> block are allowed by SHA-256 hash of their exact contents, computed
# on the FINAL html after every placeholder is resolved - which is also why
# there are no inline style= attributes left in the template: a hash-only
# style-src forbids them, and 'unsafe-inline' would defeat the point.
#
# Not expressible in a <meta> CSP and therefore absent, not forgotten:
# frame-ancestors (clickjacking) and report-uri. Both need a real header, which
# means a host that can send one; GitHub Pages cannot. See README.
# ---------------------------------------------------------------------------
INLINE_BLOCK = re.compile(r"<(script|style)>(.*?)</\1>", re.S)

# Anything above this in the finished file is a problem for WhatsApp / email.
SIZE_WARN_MB = 5.0

# Injected by --noindex. GPS is invitation-only, so a publicly *reachable* preview
# should still not be a publicly *discoverable* one: a review link that turns up in
# a search for "summit Munich" is the thing §2.1 exists to prevent, one step removed.
# Deliberately not in index.template.html — baking it into the source would risk
# shipping a launched site that quietly tells search engines to ignore it.
NOINDEX_TAG = '<meta name="robots" content="noindex, nofollow">'

# ---------------------------------------------------------------------------
# Redaction audit
#
# The Munich venue names are redacted from the site on purpose: GPS is
# invitation-only and the organisers do not want uninvited arrivals. See
# docs/BRIEF.md section 2.
#
# Those names are NOT stored here in plaintext, because this repository is
# public and git history is permanent — a denylist of the exact strings would
# hand over precisely what the redaction removes, in the file whose job is to
# protect it. They are stored as salted SHA-256 digests instead. The audit
# hashes every 1-4 word window of the built markup and looks for a match, so it
# still fails the build if a name is reintroduced, while the repo itself
# discloses nothing.
#
# Honest about the limits: a digest confirms a guess, it does not prevent one.
# Someone who already suspects a specific venue can hash it and check. What this
# stops is the far more likely case — the list being read straight out of a
# public repo by someone who had no idea. The salt only defeats generic
# precomputed tables.
#
# To add a term:  python3 build.py --hash "The Venue Name"  and paste the line.
# The plaintext list lives with the client, and optionally in the gitignored
# redactions.local.txt for local builds.
# ---------------------------------------------------------------------------
SALT = b"gps-redaction-v1"

# Eight venue strings, longest three words. Listed in digest order so that even
# the ordering says nothing about them.
FORBIDDEN_HASHES = {
    "13f7c0ea54eb039afd6e4bdc12128e7541e5f9c24dd9a130713c881f49e7b35b",
    "16b496a3515d7e2e7901390e112ffed8a0fe16d93e16a098214ee77b3484747f",
    "37350d01e23b2d93582a6f98c4f001a9f453cafe0df8241dbcb53a97258c93fd",
    "47faa97e684245ef11927e4217f1749f383d79bd7b9272b3e71f855786d2b874",
    "a6bbc9f47d010963a1641ade6db738b925468d62d197fbc532436d806c97a9ce",
    "c9bf95a5ba6d7cd20228677106b1dc74a61d6b9a88c879d872343319a62bbf65",
    "ebe2ad38a035d9322ca890fd81c28afa7666c3b0777ceb495d247417f6cf8849",
    "f574ef7e0b1346556a4cdb633d15033b7a24f2d9d25947730e52bd89e3defcce",
}

MAX_NGRAM = 4


def norm(term: str) -> str:
    """Casefold + collapse whitespace so 'Foo  Bar' == 'foo bar'."""
    term = unicodedata.normalize("NFC", term)
    return " ".join(term.split()).casefold()


def digest(term: str) -> str:
    return hashlib.sha256(SALT + norm(term).encode("utf-8")).hexdigest()


def inline(template_text: str, link_dir: Path = None) -> str:
    """Resolve placeholders. Inlines as base64, or rewrites to relative paths
    and copies the files when link_dir is given."""
    missing = []
    used = []

    def make_sub(directory, kind, rel):
        def sub(match):
            name = match.group(1)
            path = directory / name
            if not path.exists():
                missing.append(f"{directory.relative_to(ROOT)}/{name}")
                return match.group(0)
            if link_dir is not None:
                used.append((path, rel + "/" + name))
                return rel + "/" + name
            if kind == "font":
                mime = "font/woff2"
            else:
                mime, _ = mimetypes.guess_type(name)
                mime = mime or "application/octet-stream"
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{data}"
        return sub

    result = IMG_PLACEHOLDER.sub(make_sub(IMG_DIR, "img", "assets/img"), template_text)
    result = FONT_PLACEHOLDER.sub(make_sub(FONT_DIR, "font", "assets/fonts"), result)

    if missing:
        print(f"ERROR: {len(missing)} asset(s) referenced but not found:", file=sys.stderr)
        for name in missing:
            print(f"  {name}", file=sys.stderr)
        sys.exit(1)

    for src, rel in used:
        dst = link_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    return result


def hero_srcset(link_dir: Path) -> str:
    """srcset attribute for whichever hero variants exist; copies them alongside."""
    parts = []
    for name, w in HERO_VARIANTS:
        src = IMG_DIR / name
        if not src.exists():
            continue
        dst = link_dir / "assets" / "img" / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copyfile(src, dst)
        parts.append(f"assets/img/{name} {w}w")
    if len(parts) < 2:          # only the original: a srcset would say nothing
        return ""
    return f' srcset="{", ".join(parts)}" sizes="{HERO_SIZES}"'


def font_preload() -> str:
    links = []
    for name in PRELOAD_FONTS:
        if (FONT_DIR / name).exists():
            # crossorigin is required on font preloads even same-origin, or the
            # browser fetches the file twice with mismatched credentials modes.
            links.append(f'<link rel="preload" href="assets/fonts/{name}" '
                         f'as="font" type="font/woff2" crossorigin>')
    return "\n".join(links)


def csp_for(html: str) -> str:
    """Build the CSP meta tag from hashes of the page's own inline blocks."""
    scripts, styles = [], []
    for kind, body in INLINE_BLOCK.findall(html):
        h = base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()
        (scripts if kind == "script" else styles).append(f"'sha256-{h}'")
    policy = "; ".join([
        "default-src 'none'",
        "img-src 'self' data:",
        "font-src 'self' data:",
        "style-src " + " ".join(styles),
        "script-src " + " ".join(scripts),
        "connect-src 'none'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
    ])
    return f'<meta http-equiv="Content-Security-Policy" content="{policy}">'


def strip_payloads(html: str) -> str:
    """Drop base64 payloads before text scanning — they are megabytes of noise."""
    return re.sub(r"base64,[A-Za-z0-9+/=]+", "base64,", html)


def words_of(text: str) -> list:
    """
    Tokenise for the n-gram scan.

    NFC first, and this is load-bearing rather than tidiness. A combining
    diaeresis is not alphanumeric, so a decomposed 'ö' splits its word in two
    ('schön' -> 'scho' + 'n') and any denylisted term carrying an umlaut
    walks straight past the scan. One of them does. macOS filesystems and paste
    buffers hand you decomposed text as a matter of course, so this is the
    normal case, not the exotic one.
    """
    text = unicodedata.normalize("NFC", text)
    return re.findall(r"[^\W_]+", text, flags=re.UNICODE)


def local_terms() -> list:
    if not LOCAL_TERMS.exists():
        return []
    out = []
    for line in LOCAL_TERMS.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def audit(html: str) -> int:
    """Returns count of problems found."""
    problems = 0
    text = strip_payloads(html)

    # Plaintext pass, only if the optional local list is present.
    for term in local_terms():
        if norm(term) in norm(text):
            print(f"REDACTION FAILURE: a term from {LOCAL_TERMS.name} is present "
                  f"in the build.", file=sys.stderr)
            problems += 1

    # Hash pass: every 1..MAX_NGRAM word window of the visible markup.
    words = words_of(text)
    seen = set()
    for n in range(1, MAX_NGRAM + 1):
        for i in range(len(words) - n + 1):
            window = " ".join(words[i:i + n]).casefold()
            if window in seen:
                continue
            seen.add(window)
            if digest(window) in FORBIDDEN_HASHES:
                print(f"REDACTION FAILURE: a redacted venue name is present in "
                      f"the build (matched a {n}-word phrase). See docs/BRIEF.md "
                      f"section 2.1.", file=sys.stderr)
                problems += 1

    # A bare address anywhere means the mailto obfuscation has regressed.
    # This is checked against the whole file, and is strictly stronger than
    # listing the address itself would be.
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html):
        print("REDACTION FAILURE: a plain email address is present.", file=sys.stderr)
        problems += 1

    if ANY_PLACEHOLDER.search(html):
        print("ERROR: unresolved {{...}} placeholder remains.", file=sys.stderr)
        problems += 1

    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true",
                    help="validate only; do not write the output file")
    ap.add_argument("--hash", metavar="TERM",
                    help="print the denylist entry for TERM and exit; "
                         "paste it into FORBIDDEN_HASHES")
    ap.add_argument("--noindex", action="store_true",
                    help="inject a robots noindex meta tag; for preview deploys of "
                         "an invitation-only event, not for the real launch")
    ap.add_argument("--linked", metavar="DIR", type=Path,
                    help="hosted build: write DIR/index.html with linked assets "
                         "instead of one self-contained file")
    args = ap.parse_args()

    if args.hash:
        print(f'    "{digest(args.hash)}",')
        return

    if not TEMPLATE.exists():
        sys.exit(f"ERROR: {TEMPLATE} not found.")
    if not IMG_DIR.is_dir():
        sys.exit(f"ERROR: {IMG_DIR} not found.")
    if not FONT_DIR.is_dir():
        sys.exit(f"ERROR: {FONT_DIR} not found. Run: python3 tools/fetch_fonts.py")

    link_dir = args.linked
    if link_dir is not None:
        link_dir.mkdir(parents=True, exist_ok=True)
        args.out = link_dir / "index.html"

    html = inline(TEMPLATE.read_text(encoding="utf-8"), link_dir)

    # Hosted-only tokens; empty in the single file.
    html = html.replace("{{HERO_SRCSET}}", hero_srcset(link_dir) if link_dir else "")
    html = html.replace("{{FONT_PRELOAD}}", font_preload() if link_dir else "")

    # Last, once nothing else will touch the inline blocks: their hashes.
    html = html.replace("{{CSP}}", csp_for(html))

    if args.noindex:
        assert "</head>" in html, "no </head> to inject the robots tag into"
        html = html.replace("</head>", f"{NOINDEX_TAG}\n</head>", 1)

    problems = audit(html)

    n_img = len(list(IMG_DIR.glob("*")))
    n_font = len(list(FONT_DIR.glob("*.woff2")))
    size_mb = len(html.encode("utf-8")) / 1024 / 1024

    if args.check:
        print(f"check: {n_img} images + {n_font} fonts, "
              f"would produce {size_mb:.2f} MB")
        sys.exit(1 if problems else 0)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")

    shape = "linked" if args.linked else "inlined"
    print(f"built {args.out}  ({size_mb:.2f} MB html, {n_img} images + {n_font} fonts {shape})"
          + ("  [noindex]" if args.noindex else ""))
    if size_mb > SIZE_WARN_MB and not args.linked:
        print(f"WARNING: {size_mb:.2f} MB exceeds the {SIZE_WARN_MB} MB comfort limit "
              f"for sending as a single file. See docs/BRIEF.md section 7.1.")
    if problems:
        print(f"WARNING: {problems} audit problem(s) above — do not distribute this build.")
        sys.exit(1)


if __name__ == "__main__":
    main()
