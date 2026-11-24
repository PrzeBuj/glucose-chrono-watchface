"""Generuje obrazy wskazówek i ikon tarczy (PNG) do watchface/src/main/res/drawable-nodpi.

Uruchom: python3 tools/make_assets.py
Wymiary są w jednostkach tarczy 450x450 (tak jak w watchface.xml).
"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
SS = 8  # supersampling, żeby krawędzie były gładkie

WHITE = (244, 245, 247, 255)
DIAL = (16, 18, 21, 255)
RED = (229, 72, 77, 255)


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def save(img, w, h, name):
    img.resize((w * 2, h * 2), Image.LANCZOS).save(OUT / name)


def hour_hand():
    w, h = 12, 118
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=3 * SS, fill=WHITE)
    d.rounded_rectangle([4 * SS, 10 * SS, 8 * SS, 78 * SS], radius=2 * SS, fill=DIAL)
    save(img, w, h, "hand_hour.png")


def minute_hand():
    w, h = 9, 201
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=3 * SS, fill=WHITE)
    d.rounded_rectangle([3 * SS, 10 * SS, 6 * SS, 135 * SS], radius=1.5 * SS, fill=DIAL)
    save(img, w, h, "hand_minute.png")


def second_hand():
    w, h = 10, 249
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    cx = w * SS / 2
    # biały: kolor nadaje motyw tarczy (tintColor)
    d.rounded_rectangle([cx - 1.1 * SS, 0, cx + 1.1 * SS, h * SS - 1], radius=1.1 * SS, fill=WHITE)
    # przeciwwaga
    d.rounded_rectangle([1 * SS, 221 * SS, 9 * SS, 248 * SS], radius=3 * SS, fill=WHITE)
    save(img, w, h, "hand_second.png")


def heart():
    w = h = 14
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    s = SS * w / 24
    pts = [(12, 21), (4.2, 13.4), (3.2, 12.4), (2.4, 9), (3.2, 5.6), (6, 3.6), (9, 3.6), (12, 6)]
    pts += [(15, 3.6), (18, 3.6), (20.8, 5.6), (21.6, 9), (20.8, 12.4), (19.8, 13.4)]
    d.polygon([(x * s, y * s) for x, y in pts], fill=WHITE)
    save(img, w, h, "ic_heart.png")


def battery():
    w, h = 18, 14
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1 * SS, 2 * SS, 15 * SS, 12 * SS], radius=2 * SS, outline=WHITE, width=int(1.8 * SS))
    d.rectangle([15.5 * SS, 5 * SS, 17 * SS, 9 * SS], fill=WHITE)
    save(img, w, h, "ic_battery.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    hour_hand()
    minute_hand()
    second_hand()
    heart()
    battery()
    print("Zapisano do", OUT)
