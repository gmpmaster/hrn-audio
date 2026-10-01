# -*- coding: utf-8 -*-
"""
Derive each show's palette from its own key art.

The sampled background colour becomes the show's accent. Because those range
from very light (Sebas green) to very dark (Juan navy), the text colour cannot
just be the accent — it is darkened or lightened until it clears 4.5:1 on white,
so every card is legible without anyone eyeballing it.
"""
import json, io, colorsys, os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PROJ, "src", "data", "shows.json")

SAMPLED = {
    "echate-pa-ca":            "#FC7A1C",
    "la-mezcla-fuego":         "#5F34CA",
    "buenas-tardes-el-patron": "#FC373E",
    "minuto-deportivo":        "#011665",
    "los-40-usa":              "#ABF059",
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


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def text_safe(hex_color, target=4.5, bg="#FFFFFF"):
    """Walk lightness down until the colour clears `target` on white."""
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    for _ in range(100):
        cand = rgb_to_hex(*colorsys.hls_to_rgb(h, l, s))
        if contrast(cand, bg) >= target:
            return cand, round(contrast(cand, bg), 2)
        l -= 0.01
        if l <= 0:
            break
    return "#1A1A1A", round(contrast("#1A1A1A", bg), 2)


shows = json.load(open(DATA, encoding="utf8"))
print(f"{'show':26} {'accent':9} {'on white':>9}   {'text':9} {'on white':>9}")
print("-" * 70)

for s in shows:
    accent = SAMPLED.get(s["id"])
    if not accent:
        continue
    raw = round(contrast(accent, "#FFFFFF"), 2)
    txt, txt_ratio = text_safe(accent)
    s["accent"] = accent
    s["accentText"] = txt
    s["panel"] = accent
    s.pop("accent2", None)
    # these key art files are a matched set — use them, not the cutouts
    s["photo"] = f"/img/talent/{s['id']}.jpg"
    s["cutout"] = ""
    note = "" if raw >= 4.5 else "  <- darkened for text"
    print(f"{s['id']:26} {accent}   {raw:>6}:1   {txt}   {txt_ratio:>6}:1{note}")

io.open(DATA, "w", encoding="utf8", newline="\n").write(
    json.dumps(shows, ensure_ascii=False, indent=2) + "\n")
print("\nshows.json updated")
