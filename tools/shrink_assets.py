"""Zmniejsza duże grafiki tarczy do rozdzielczości ekranu (466 px), żeby tarcza zajmowała mniej pamięci.
Uruchom po make_assets*.py: python3 tools/shrink_assets.py"""
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
K = 466 / 900
for name in ("bg_classic", "bg_sport", "bg_sport1", "gear_big", "gear_small", "preview"):
    p = R / f"{name}.png"
    im = Image.open(p)
    if im.width < {"gear_big": 400, "gear_small": 200}.get(name, 600):
        continue  # już zmniejszona
    w = round(im.width * K)
    im.resize((w, w), Image.LANCZOS).save(p, optimize=True)
    print(name, im.width, "->", w)
