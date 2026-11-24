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


def gear(name, r_out, teeth, spokes, r_hub=None, alpha=34):
    """Koło zębate jak w mechanizmie zegarka: obręcz z zębami, szprychy i piasta (białe, półprzezroczyste)."""
    import math
    size = int(2 * r_out + 4)
    img = canvas(size, size)
    d = ImageDraw.Draw(img)
    c = size * SS / 2
    col = (255, 255, 255, alpha)
    tooth = r_out * 0.10
    r_root = r_out - tooth
    pts = []
    for i in range(teeth):
        a0 = 2 * math.pi * i / teeth
        step = 2 * math.pi / teeth
        for frac, r in ((0.0, r_root), (0.15, r_out), (0.45, r_out), (0.6, r_root)):
            a = a0 + step * frac
            pts.append((c + r * SS * math.sin(a), c - r * SS * math.cos(a)))
    d.polygon(pts, fill=col)
    # wycięcie środka obręczy, zostawiamy obręcz o grubości ~12% promienia
    r_in = r_root * 0.86
    hole = Image.new("L", img.size, 0)
    hd = ImageDraw.Draw(hole)
    hd.ellipse([c - r_in * SS, c - r_in * SS, c + r_in * SS, c + r_in * SS], fill=255)
    # szprychy i piasta zostają
    w = r_out * 0.09 * SS
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        dx, dy = math.sin(a), -math.cos(a)
        px, py = -dy * w / 2, dx * w / 2
        hd.polygon([(c + px, c + py), (c - px, c - py),
                    (c - px + dx * r_in * SS, c - py + dy * r_in * SS),
                    (c + px + dx * r_in * SS, c + py + dy * r_in * SS)], fill=0)
    rh = (r_hub or r_out * 0.18) * SS
    hd.ellipse([c - rh, c - rh, c + rh, c + rh], fill=0)
    clear = Image.new("RGBA", img.size, (0, 0, 0, 0))
    img = Image.composite(clear, img, hole)
    d = ImageDraw.Draw(img)
    rp = rh * 0.35
    d.ellipse([c - rp, c - rp, c + rp, c + rp], fill=(0, 0, 0, 0))
    save(img, size, size, name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    hour_hand()
    minute_hand()
    second_hand()
    heart()
    battery()
    gear("gear_big.png", 150, 60, 6)
    gear("gear_small.png", 64, 26, 5)
    print("Zapisano do", OUT)
