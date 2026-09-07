#!/usr/bin/env python3
"""
Draw 4:3 city silhouette panels as SVG for calendar cards that have no photograph.

Deliberately illustration, not a simulated photograph: these cities have no usable
image, and a generated "photo" of a real skyline gets landmarks subtly wrong.
A drawn silhouette is honest about being a graphic.

Palette comes from the site tokens. Output lands in assets/img/.
"""
from pathlib import Path

W, H = 800, 600
GROUND = 508
INK = "#132339"      # --ink, panel background
NAVY = "#273D68"     # --navy, far skyline
LIGHT = "#7C8CA8"    # near skyline / landmark
HAZE = "#1B2C46"     # sky band


def rect(x, y, w, h, fill):
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{fill}"/>'


def blocks(spec, fill):
    """spec: list of (x, width, height-above-ground)"""
    return "".join(rect(x, GROUND - h, w, h, fill) for x, w, h in spec)


def frame(body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
        f'<rect width="{W}" height="{H}" fill="{INK}"/>'
        f'<rect x="0" y="{GROUND-210}" width="{W}" height="210" fill="{HAZE}"/>'
        f'{body}'
        f'<rect x="0" y="{GROUND}" width="{W}" height="{H-GROUND}" fill="{INK}"/>'
        f'<rect x="0" y="{GROUND}" width="{W}" height="2" fill="{LIGHT}" opacity=".35"/>'
        f'</svg>'
    )


# ---------------------------------------------------------------- Paris
def paris():
    cx, base = 470, GROUND
    p1, p2, top = 340, 245, 90          # platform and spire heights (y)
    s = []
    s.append(blocks([(20,110,74),(140,90,58),(240,120,86),
                     (620,120,80),(750,50,60)], NAVY))
    # Sacre-Coeur suggestion
    s.append(f'<path d="M96 {GROUND-74} q30-58 60 0 z" fill="{NAVY}"/>')
    s.append(rect(122, GROUND - 98, 8, 28, NAVY))

    # Eiffel Tower — one silhouette, wide splayed base, arch punched out
    s.append(f'<path d="M{cx-95} {base} C{cx-72} {base-78} {cx-54} {p1+50} {cx-46} {p1} '
             f'L{cx-26} {p2} L{cx-9} {top+30} L{cx-4} {top} L{cx+4} {top} L{cx+9} {top+30} '
             f'L{cx+26} {p2} L{cx+46} {p1} C{cx+54} {p1+50} {cx+72} {base-78} {cx+95} {base} Z" '
             f'fill="{LIGHT}"/>')
    s.append(f'<path d="M{cx-64} {base} C{cx-60} {base-64} {cx-32} {base-104} {cx} {base-104} '
             f'C{cx+32} {base-104} {cx+60} {base-64} {cx+64} {base} Z" fill="{HAZE}"/>')
    s.append(rect(cx - 52, p1 - 10, 104, 12, LIGHT))
    s.append(rect(cx - 31, p2 - 9, 62, 11, LIGHT))
    return frame("".join(s))


# ---------------------------------------------------------------- New York
def newyork():
    s = []
    s.append(blocks([(16,80,96),(104,64,140),(176,54,104),(628,74,150),
                     (712,54,104),(766,34,140)], NAVY))
    # Empire State — continuous stacked setbacks, all rising from the ground
    cx = 402
    for hw, h in [(78, 214), (56, 316), (38, 396), (22, 436)]:
        s.append(rect(cx - hw, GROUND - h, hw * 2, h, LIGHT))
    s.append(rect(cx - 5, GROUND - 486, 10, 56, LIGHT))   # mast
    # Chrysler — tiered arched crown
    cx2 = 258
    s.append(rect(cx2 - 34, GROUND - 250, 68, 250, LIGHT))
    for i, w in enumerate([64, 50, 36, 22]):
        y = GROUND - 250 - i * 17
        s.append(f'<path d="M{cx2-w/2:.0f} {y} q{w/2:.0f} -20 {w} 0 z" fill="{LIGHT}"/>')
    s.append(rect(cx2 - 3, GROUND - 366, 6, 50, LIGHT))
    # slim neighbour
    s.append(blocks([(520, 46, 300), (566, 30, 246)], LIGHT))
    return frame("".join(s))


# ---------------------------------------------------------------- Dallas
def dallas():
    s = []
    s.append(blocks([(20,90,88),(120,70,120),(206,60,96),(560,80,132),
                     (656,58,92),(724,64,150)], NAVY))
    # Bank of America Plaza — tall slab
    s.append(blocks([(300,76,306)], LIGHT))
    s.append(rect(330, GROUND - 350, 16, 46, LIGHT))
    # a stepped neighbour
    s.append(blocks([(392,62,214),(404,38,252)], LIGHT))
    # Reunion Tower — stalk with the sphere
    cx, ball = 500, GROUND - 300
    s.append(rect(cx - 11, ball, 22, 300, LIGHT))
    s.append(f'<circle cx="{cx}" cy="{ball}" r="42" fill="{LIGHT}"/>')
    s.append(f'<circle cx="{cx}" cy="{ball}" r="42" fill="none" stroke="{HAZE}" '
             f'stroke-width="3" opacity=".55"/>')
    s.append(f'<path d="M{cx-42} {ball} h84" stroke="{HAZE}" stroke-width="3" opacity=".55"/>')
    s.append(rect(cx - 3, ball - 76, 6, 36, LIGHT))
    return frame("".join(s))


if __name__ == "__main__":
    out = Path(__file__).parent / "assets" / "img"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("42-dallas.svg", dallas),
                     ("43-new-york.svg", newyork),
                     ("44-paris.svg", paris)]:
        svg = fn()
        (out / name).write_text(svg, encoding="utf-8")
        print(f"{name:<18}{len(svg)/1024:5.1f} KB")
