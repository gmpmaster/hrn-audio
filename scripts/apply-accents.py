# -*- coding: utf-8 -*-
"""Apply the requested per-show accents.

Where a requested colour clears 4.5:1 on white it is used verbatim for text.
Where it does not, it still drives the fills (play button, rules) and a
minimally-darkened sibling of the same hue carries text, so nothing is
illegible and nothing drifts off-brand.
"""
import json, io, os, colorsys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJ, "src", "data", "shows.json")

# requested fill colours, per show
REQUESTED = {
    "echate-pa-ca":            "#00C5DC",   # Debbie, 2026-10-04: fill AND text, white play icon
    "buenas-tardes-el-patron": "#5B37CF",   # Debbie, 2026-10-04
    "la-mezcla-fuego":         "#FF224D",   # Debbie, 2026-10-04
    "los-40-usa":              "#007DFF",   # Debbie, 2026-10-07 (was #009FFF, read too teal)
    "minuto-deportivo":        "#0148D4",   # matches the new blue card art
}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return "#%02X%02X%02X" % tuple(round(max(0, min(1, c)) * 255) for c in (r, g, b))


def luminance(h):
    r, g, b = hex_to_rgb(h)
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b="#FFFFFF"):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def darken_until(h, target=4.5):
    r, g, b = hex_to_rgb(h)
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    for _ in range(100):
        cand = rgb_to_hex(*colorsys.hls_to_rgb(hh, l, s))
        if contrast(cand) >= target:
            return cand
        l -= 0.01
        if l <= 0:
            break
    return "#1A1A1A"


shows = json.load(open(DATA, encoding="utf8"))
print(f"{'show':26} {'fill':9} {'on white':>9}  {'text':9} {'on white':>9}  note")
print("-" * 86)

for s in shows:
    fill = REQUESTED[s["id"]]
    cr = contrast(fill)
    if s.get("textOverride"):
        # brand colour kept for text by explicit request, contrast notwithstanding
        text, note = s["accentText"], f"override, kept at {contrast(s['accentText']):.2f}"
    elif cr >= 4.5:
        text, note = fill, "used verbatim"
    else:
        text = darken_until(fill)
        note = f"darkened for text ({cr:.2f} -> {contrast(text):.2f})"

    s["accent"] = fill
    s["accentText"] = text
    # white on the fill is weak for these, so the play glyph goes dark instead,
    # unless a show asks for a specific glyph colour (playInkOverride)
    s["playInk"] = s.get("playInkOverride") or ("#0E1A20" if contrast("#FFFFFF", fill) < 3.0 else "#FFFFFF")

    print(f"{s['id']:26} {fill}  {cr:>7.2f}:1  {text}  {contrast(text):>7.2f}:1  {note}")

io.open(DATA, "w", encoding="utf8", newline="\n").write(
    json.dumps(shows, ensure_ascii=False, indent=2) + "\n")
print("\nshows.json updated")
