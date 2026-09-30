# -*- coding: utf-8 -*-
"""
Sync assets from the OneDrive drop folder into the site.

  python scripts/sync-assets.py

Copies whatever exists in "HRN Audio Assets" into public/, then rewrites the
paths in src/data/shows.json so any show that has a cutout gets the branded
panel treatment and any show that has an mp3 gets a working player.

Files are matched by show slug. Nothing is invented — a show with no cutout
keeps its key art, a show with no demo keeps "Demo coming soon".
"""
import json, os, shutil, sys

ASSETS = r"C:\Users\debdo\OneDrive - Gen Media Partners\HRN Audio Assets"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(PROJ, "public")
DATA = os.path.join(PROJ, "src", "data", "shows.json")

SLUGS = ["echate-pa-ca", "buenas-tardes-el-patron", "la-mezcla-fuego",
         "los-40-usa", "minuto-deportivo"]

IMG_EXT = (".webp", ".png", ".jpg", ".jpeg")


def find(folder, slug, exts):
    """First file in folder whose name starts with the slug."""
    d = os.path.join(ASSETS, folder)
    if not os.path.isdir(d):
        return None
    for f in sorted(os.listdir(d)):
        base, ext = os.path.splitext(f)
        if ext.lower() in exts and base.lower().startswith(slug):
            return os.path.join(d, f)
    return None


def copy_to(src, rel_dir):
    dest_dir = os.path.join(PUB, rel_dir)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(src))
    shutil.copy2(src, dest)
    return "/" + rel_dir.replace("\\", "/") + "/" + os.path.basename(src)


def main():
    if not os.path.isdir(ASSETS):
        print(f"Drop folder not found:\n  {ASSETS}")
        sys.exit(1)

    shows = json.load(open(DATA, encoding="utf8"))
    by_id = {s["id"]: s for s in shows}
    report = []

    for slug in SLUGS:
        s = by_id.get(slug)
        if not s:
            continue
        got = []

        cut = find("cutouts", slug, IMG_EXT)
        if cut:
            s["cutout"] = copy_to(cut, "img/cutouts")
            got.append("cutout")

        logo = find("logos", slug, IMG_EXT)
        if logo:
            s["logo"] = copy_to(logo, "img/logos")
            got.append("logo")

        art = find("keyart", slug, IMG_EXT)
        if art:
            s["photo"] = copy_to(art, "img/talent")
            got.append("keyart")

        mp3 = find("demos", slug, (".mp3",))
        if mp3:
            s["audio"] = copy_to(mp3, "audio")
            s["hasDemo"] = True
            got.append("demo")
        else:
            s["hasDemo"] = bool(s.get("hasDemo"))

        treatment = "BRANDED" if s.get("cutout") else "key art"
        report.append((slug, treatment, s["hasDemo"], got))

    json.dump(shows, open(DATA, "w", encoding="utf8"),
              ensure_ascii=False, indent=2)
    open(DATA, "a", encoding="utf8").write("\n")

    print(f"Synced from {ASSETS}\n")
    for slug, treatment, demo, got in report:
        print(f"  {slug:26} {treatment:9} demo={'yes' if demo else 'NO ':3} "
              f"{'(' + ', '.join(got) + ')' if got else '(nothing new)'}")
    missing = [s for s, t, d, g in report if t != "BRANDED"]
    if missing:
        print("\n  Still needs a cutout: " + ", ".join(missing))


if __name__ == "__main__":
    main()
