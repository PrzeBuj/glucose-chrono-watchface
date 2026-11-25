"""Grafiki tarczy „Glukoza Sport” (wzór: heksagonalne tło, panele, wskazówki konturowe).

Uruchom: python3 tools/make_assets_v3.py   (zapis do watchface/src/main/res/drawable-nodpi)
Układ 450x450 jak w watchface.xml, obrazy zapisywane w 2x dla ostrości.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
X = 2          # skala zapisu
SS = 4         # nadpróbkowanie przy rysowaniu
N = 450


def big(w, h):
    return Image.new("RGBA", (w * X * SS, h * X * SS), (0, 0, 0, 0))


def save(img, w, h, name):
    img.resize((w * X, h * X), Image.LANCZOS).save(OUT / name, optimize=True)


def u(v):
    return int(round(v * X * SS))


def background():
    img = Image.new("RGBA", (u(N), u(N)), (12, 15, 19, 255))
    d = ImageDraw.Draw(img)
    # delikatna poświata w środku
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(30):
        r = u(225) * (1 - i / 30)
        a = int(2 + i * 0.9)
        gd.ellipse([u(225) - r, u(225) - r, u(225) + r, u(225) + r], fill=(40, 52, 66, a))
    img = Image.alpha_composite(img, glow)
    # heksagonalna siatka
    hexl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hexl)
    r = 7.0
    w = math.sqrt(3) * r
    row = 0
    y = -r
    while y < N + r:
        x = (w / 2 if row % 2 else 0) - w
        while x < N + w:
            pts = [(u(x + r * 0.92 * math.cos(math.radians(60 * k + 30))), u(y + r * 0.92 * math.sin(math.radians(60 * k + 30)))) for k in range(6)]
            hd.polygon(pts, fill=(18, 22, 28, 255), outline=(40, 49, 60, 255))
            x += w
        y += r * 1.5
        row += 1
    # siatka mocniejsza w środku, zanika ku brzegom
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    for i in range(40):
        rr = u(225) * (1 - i / 40)
        md.ellipse([u(225) - rr, u(225) - rr, u(225) + rr, u(225) + rr], fill=int(110 + i * 3.6))
    hexl.putalpha(Image.composite(hexl.getchannel("A"), Image.new("L", img.size, 0), mask).point(lambda p: p))
    img = Image.alpha_composite(img, hexl)

    # panele (jak szkło na tarczy)
    pan = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(pan)
    fill = (26, 32, 40, 215)
    edge = (58, 68, 80, 255)
    lw = int(u(1.4))
    pd.rounded_rectangle([u(92), u(46), u(358), u(162)], radius=u(34), fill=fill, outline=edge, width=lw)
    for cx in (108, 342):
        pd.ellipse([u(cx - 62), u(226 - 62), u(cx + 62), u(226 + 62)], fill=fill, outline=edge, width=lw)
    pd.rounded_rectangle([u(58), u(296), u(392), u(480)], radius=u(40), fill=fill, outline=edge, width=lw)
    shadow = pan.filter(ImageFilter.GaussianBlur(u(5)))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(shadow.getchannel("A").point(lambda p: int(p * 0.7)))
    img = Image.alpha_composite(img, sh)
    img = Image.alpha_composite(img, pan)
    # górna krawędź paneli lekko jaśniejsza
    hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(hl)
    ld.arc([u(92), u(46), u(358), u(162)], 0, 0, fill=(0, 0, 0, 0))
    img = Image.alpha_composite(img, hl)
    # przycięcie do koła
    circ = Image.new("L", img.size, 0)
    ImageDraw.Draw(circ).ellipse([0, 0, u(N) - 1, u(N) - 1], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 255))
    out.paste(img, (0, 0), circ)
    save(out.convert("RGB").convert("RGBA"), N, N, "bg_sport.png")


def outlined_hand(name, w, length, tail, color, fill=(22, 27, 34, 235)):
    """Wskazówka konturowa ze spiczastym końcem; oś obrotu w punkcie (w/2, length)."""
    h = length + tail
    img = big(w, h)
    d = ImageDraw.Draw(img)
    c = w / 2
    pts = [(c, 0), (w - 1, w * 0.9), (w - 1, h - 4), (c, h), (1, h - 4), (1, w * 0.9)]
    pts = [(u(x), u(y)) for x, y in pts]
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=color, width=int(u(2.4)), joint="curve")
    # środkowa jasna kreska w części końcowej
    d.rounded_rectangle([u(c - 1.1), u(w * 1.4), u(c + 1.1), u(length * 0.62)], radius=u(1.1), fill=color[:3] + (200,))
    save(img, w, h, name)
    return h, length / h


def second_hand(name, length, tail):
    w = 8
    h = length + tail
    img = big(w, h)
    d = ImageDraw.Draw(img)
    c = w / 2
    d.rounded_rectangle([u(c - 1.0), 0, u(c + 1.0), u(h)], radius=u(1), fill=(255, 255, 255, 255))
    d.rounded_rectangle([u(c - 2.6), u(length + 8), u(c + 2.6), u(h)], radius=u(2.6), fill=(255, 255, 255, 255))
    save(img, w, h, name)
    return h, length / h


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    background()
    print("hour", outlined_hand("hand_hour_o.png", 16, 112, 14, (244, 245, 247, 255)))
    print("minute", outlined_hand("hand_minute_o.png", 14, 178, 16, (255, 138, 61, 255)))
    print("second", second_hand("hand_second_o.png", 196, 36))
