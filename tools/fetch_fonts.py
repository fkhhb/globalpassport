#!/usr/bin/env python3
"""
Download the web fonts the site actually uses into assets/fonts/.

Why this exists
---------------
The distributed artefact is one HTML file sent over WhatsApp that must work with
no network. Pulling Newsreader and IBM Plex Sans from Google Fonts broke that:
offline, the typography fell back to Georgia and a system sans. See docs/BRIEF.md
"Fonts do not load offline".

So the faces are downloaded once, committed as real .woff2 files, and inlined by
build.py at build time via {{FONT:...}} placeholders. Same principle as the images:
real files in the repo, base64 only in the build output.

Only the **latin** subset is fetched. Every non-ASCII character in the template
(© · a-grave, en dash, em dash, curly quotes) falls inside Google's latin
unicode-range, so latin-ext / vietnamese would be dead weight.

Only the weights the stylesheet actually uses are fetched:

    Newsreader      normal 300, 400, 500   italic 300, 400
    IBM Plex Sans   normal 300, 400, 500

Newsreader 600, and Newsreader italic 500, were requested by the old Google Fonts
<link> and are used nowhere in the CSS; they are deliberately not fetched.

**Static instances, not the variable font.** Newsreader is a variable family and
asking for a weight *range* returns one file per style covering it — convenient,
but 129 KB and 143 KB for normal and italic. Asking for single weights returns
static instances at 21-24 KB each: 113 KB for all five faces against 272 KB for
the two variable ones. The cost is the optical-size axis, which would otherwise
retune letterforms between 16px body text and 62px headlines. At this file's
sizes that difference is very subtle, and 160 KB is not, on an artefact with a
5 MB delivery ceiling.

Both families are licensed under the SIL Open Font License 1.1, which permits
embedding. See assets/fonts/OFL.txt for the notice.

Usage:
    python3 tools/fetch_fonts.py            # download into assets/fonts/
    python3 tools/fetch_fonts.py --check    # report what is present, download nothing

Re-run only when the set of weights in the stylesheet changes. The files are
committed, so a normal build never touches the network.
"""

import argparse
import os
import re
import ssl
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# A browser UA is required: the Google Fonts CSS API serves woff2 only to clients
# it believes support it, and falls back to fat legacy formats otherwise.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# (output filename, css2 query, style to match, expected weight descriptor)
FACES = [
    ("newsreader-latin-300.woff2",
     "family=Newsreader:wght@300", "normal", "300"),
    ("newsreader-latin-400.woff2",
     "family=Newsreader:wght@400", "normal", "400"),
    ("newsreader-latin-500.woff2",
     "family=Newsreader:wght@500", "normal", "500"),
    ("newsreader-latin-300italic.woff2",
     "family=Newsreader:ital,wght@1,300", "italic", "300"),
    ("newsreader-latin-400italic.woff2",
     "family=Newsreader:ital,wght@1,400", "italic", "400"),
    ("ibm-plex-sans-latin-300.woff2",
     "family=IBM+Plex+Sans:wght@300", "normal", "300"),
    ("ibm-plex-sans-latin-400.woff2",
     "family=IBM+Plex+Sans:wght@400", "normal", "400"),
    ("ibm-plex-sans-latin-500.woff2",
     "family=IBM+Plex+Sans:wght@500", "normal", "500"),
]

API = "https://fonts.googleapis.com/css2?{q}&display=swap"

# Isolate the "/* latin */" block specifically. The API also returns latin-ext,
# vietnamese and greek blocks for these families; matching the first @font-face
# would silently grab the wrong subset.
LATIN_BLOCK = re.compile(
    r"/\*\s*latin\s*\*/\s*@font-face\s*\{(.*?)\}", re.S)
SRC_URL = re.compile(r"src:\s*url\((https://[^)]+\.woff2)\)")
STYLE = re.compile(r"font-style:\s*([a-z]+)")


def _opener():
    """urllib with the agent proxy's CA bundle when running inside the sandbox."""
    ca = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    ctx = ssl.create_default_context(cafile=ca) if Path(ca).exists() \
        else ssl.create_default_context()
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))


def fetch(url: str, opener) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with opener.open(req, timeout=30) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report which font files are present; download nothing")
    args = ap.parse_args()

    if args.check:
        missing = [n for n, *_ in FACES if not (FONT_DIR / n).exists()]
        for name, *_ in FACES:
            p = FONT_DIR / name
            state = f"{p.stat().st_size / 1024:6.1f} KB" if p.exists() else "MISSING"
            print(f"  {state}  {name}")
        sys.exit(1 if missing else 0)

    FONT_DIR.mkdir(parents=True, exist_ok=True)
    opener = _opener()
    total = 0

    for name, query, want_style, weight in FACES:
        css = fetch(API.format(q=query), opener).decode("utf-8")

        url = None
        for body in LATIN_BLOCK.findall(css):
            m_style = STYLE.search(body)
            if m_style and m_style.group(1) == want_style:
                m_url = SRC_URL.search(body)
                if m_url:
                    url = m_url.group(1)
                    break

        if not url:
            sys.exit(f"ERROR: no latin/{want_style} face found for {name}.\n"
                     f"The Google Fonts API response may have changed shape.")

        data = fetch(url, opener)
        if data[:4] != b"wOF2":
            sys.exit(f"ERROR: {name} is not a woff2 file (got {data[:4]!r}). "
                     f"The User-Agent may have been rejected.")

        (FONT_DIR / name).write_bytes(data)
        total += len(data)
        print(f"  {len(data) / 1024:6.1f} KB  {name}  (weight {weight}, {want_style})")

    print(f"\n{len(FACES)} faces, {total / 1024:.1f} KB total -> {FONT_DIR}")
    print("Now run: python3 build.py")


if __name__ == "__main__":
    main()
