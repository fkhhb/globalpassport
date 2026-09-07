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
"""

import argparse
import base64
import hashlib
import mimetypes
import re
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
ANY_PLACEHOLDER = re.compile(r"\{\{(?:IMG|FONT):[^}]+\}\}")

# Anything above this in the finished file is a problem for WhatsApp / email.
SIZE_WARN_MB = 5.0

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


def inline(template_text: str) -> str:
    missing = []

    def make_sub(directory, kind):
        def sub(match):
            name = match.group(1)
            path = directory / name
            if not path.exists():
                missing.append(f"{directory.relative_to(ROOT)}/{name}")
                return match.group(0)
            if kind == "font":
                mime = "font/woff2"
            else:
                mime, _ = mimetypes.guess_type(name)
                mime = mime or "application/octet-stream"
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{data}"
        return sub

    result = IMG_PLACEHOLDER.sub(make_sub(IMG_DIR, "img"), template_text)
    result = FONT_PLACEHOLDER.sub(make_sub(FONT_DIR, "font"), result)

    if missing:
        print(f"ERROR: {len(missing)} asset(s) referenced but not found:", file=sys.stderr)
        for name in missing:
            print(f"  {name}", file=sys.stderr)
        sys.exit(1)

    return result


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

    html = inline(TEMPLATE.read_text(encoding="utf-8"))
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

    print(f"built {args.out}  ({size_mb:.2f} MB, {n_img} images + {n_font} fonts inlined)")
    if size_mb > SIZE_WARN_MB:
        print(f"WARNING: {size_mb:.2f} MB exceeds the {SIZE_WARN_MB} MB comfort limit "
              f"for sending as a single file. See docs/BRIEF.md section 7.1.")
    if problems:
        print(f"WARNING: {problems} audit problem(s) above — do not distribute this build.")
        sys.exit(1)


if __name__ == "__main__":
    main()
