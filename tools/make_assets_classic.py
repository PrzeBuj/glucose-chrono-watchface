"""Grafiki stylu „Klasyczny”: włókno węglowe, szczotkowany środek, metalowe indeksy, wskazówki z lumą.

Uruchom: python3 tools/make_assets_classic.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
X, SS, N = 2, 3, 450


def u(v):
    return int(round(v * X * SS))


def save(img, w, h, name):
    img.resize((w * X, h * X), Image.LANCZOS).save(OUT / name, optimize=True)


def carbon(size):
    """Splot włókna węglowego: naprzemienne skośne pola."""
    img = Image.new("RGBA", size, (14, 16, 18, 255))
    d = ImageDraw.Draw(img)
    cell = u(6)
    for gy in range(0, size[1] + cell, cell):
        for gx in range(0, size[0] + cell, cell):
            odd = ((gx // cell) + (gy // cell)) % 2
            if odd:
                for k in range(0, cell, max(1, u(1.0))):
                    t = k / cell
                    c = int(24 + 34 * (1 - abs(t - 0.5) * 2))
                    d.line([(gx, gy + k), (gx + cell, gy + k)], fill=(c, c + 2, c + 5, 255))
            else:
                for k in range(0, cell, max(1, u(1.0))):
                    t = k / cell
                    c = int(12 + 16 * (1 - abs(t - 0.5) * 2))
                    d.line([(gx + k, gy), (gx + k, gy + cell)], fill=(c, c + 1, c + 3, 255))
    return img


def brushed(size, r):
    """Szczotkowany metal (promieniście), ciemnografitowy."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size[0] / 2
    import random
    rnd = random.Random(7)
    d.ellipse([c - r, c - r, c + r, c + r], fill=(30, 33, 37, 255))
    for k in range(2400):
        a = rnd.random() * 2 * math.pi
        l1 = rnd.random() * r * 0.15
        v = rnd.randint(22, 70)
        d.line([(c + l1 * math.cos(a), c + l1 * math.sin(a)), (c + r * math.cos(a), c + r * math.sin(a))],
               fill=(v, v + 2, v + 5, 70), width=1)
    # połysk: jaśniej u góry po prawej
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for k in range(20):
        rr = r * (1 - k / 22)
        gd.ellipse([c - rr + r * 0.25, c - rr - r * 0.3, c + rr + r * 0.25, c + rr - r * 0.3], fill=(255, 255, 255, 3))
    img = Image.alpha_composite(img, glow)
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse([c - r, c - r, c + r, c + r], fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def bar(d, cx, cy, ang, r1, r2, w, fill, edge):
    """Prostokątny nakładany indeks między promieniami r1 i r2."""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    px, py = -uy, ux
    pts = []
    for (r, s) in ((r1, -1), (r2, -1), (r2, 1), (r1, 1)):
        pts.append((u(cx + ux * r + px * s * w / 2), u(cy + uy * r + py * s * w / 2)))
    d.polygon(pts, fill=fill, outline=edge, width=u(1.2))


def background():
    size = (u(N), u(N))
    img = carbon(size)
    C = 225
    # środek: szczotkowana tarcza
    img = Image.alpha_composite(img, brushed(size, u(150)))
    d = ImageDraw.Draw(img)
    # pierścień rehaut i jasna obwódka (szkło/bezel)
    d.ellipse([u(C - 222), u(C - 222), u(C + 222), u(C + 222)], outline=(150, 200, 225, 255), width=u(3))
    d.ellipse([u(C - 217), u(C - 217), u(C + 217), u(C + 217)], outline=(30, 60, 85, 255), width=u(3))
    # minutowe kreski
    for k in range(60):
        a = math.radians(k * 6)
        r1 = 200 if k % 5 else 196
        d.line([(u(C + r1 * math.sin(a)), u(C - r1 * math.cos(a))), (u(C + 210 * math.sin(a)), u(C - 210 * math.cos(a)))],
               fill=(190, 195, 200, 255), width=u(1.4 if k % 5 else 2.4))
    # indeksy godzinowe (metal), przy 4 i 8 zielona luma
    silver, edge = (214, 218, 222, 255), (110, 115, 120, 255)
    for h in range(12):
        ang = h * 30
        if h == 0:
            for dx in (-6, 6):
                a = math.radians(0)
                d.rounded_rectangle([u(C + dx - 4), u(C - 192), u(C + dx + 4), u(C - 160)], radius=u(1.5), fill=silver, outline=edge, width=u(1.2))
        elif h == 6:
            for dx in (-4, 4):
                d.rounded_rectangle([u(C + dx - 2.5), u(C + 192), u(C + dx + 2.5), u(C + 208)], radius=u(1.2), fill=silver, outline=edge, width=u(1))
        elif h in (3, 9):
            continue
        elif h in (4, 8):
            bar(d, C, C, ang, 166, 194, 10, (60, 190, 120, 255), (30, 90, 60, 255))
            bar(d, C, C, ang, 170, 190, 4, (150, 240, 190, 255), (150, 240, 190, 255))
        else:
            bar(d, C, C, ang, 172 if h in (5, 7) else 168, 194, 9, silver, edge)
    # koła widżetów: srebrny pierścień, drobna skala
    for cx in (108, 342):
        cy = 226
        d.ellipse([u(cx - 62), u(cy - 62), u(cx + 62), u(cy + 62)], fill=(22, 24, 27, 255))
        d.ellipse([u(cx - 62), u(cy - 62), u(cx + 62), u(cy + 62)], outline=(205, 210, 215, 255), width=u(3))
        d.ellipse([u(cx - 58), u(cy - 58), u(cx + 58), u(cy + 58)], outline=(70, 74, 79, 255), width=u(1))
        for k in range(48):
            a = math.radians(k * 7.5)
            d.line([(u(cx + 52 * math.sin(a)), u(cy - 52 * math.cos(a))), (u(cx + 56 * math.sin(a)), u(cy - 56 * math.cos(a)))],
                   fill=(120, 125, 130, 255), width=u(0.8))
    # okienko wykresu: wpuszczone, srebrna krawędź
    d.rounded_rectangle([u(143), u(358), u(307), u(408)], radius=u(10), fill=(10, 11, 12, 255), outline=(170, 175, 180, 255), width=u(2))
    circ = Image.new("L", size, 0)
    ImageDraw.Draw(circ).ellipse([0, 0, u(N) - 1, u(N) - 1], fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 255))
    out.paste(img, (0, 0), circ)
    save(out, N, N, "bg_classic.png")


def lume_hand(name, w, length, tail):
    """Wskazówka typu „miecz”: srebrna ramka, wypełnienie lumą; oś w (w/2, length)."""
    h = length + tail
    img = Image.new("RGBA", (u(w), u(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = w / 2
    outer = [(c, 0), (w, w * 1.2), (w * 0.82, h - 6), (c, h), (w * 0.18, h - 6), (0, w * 1.2)]
    d.polygon([(u(x), u(y)) for x, y in outer], fill=(200, 205, 210, 255), outline=(120, 125, 130, 255))
    inner = [(c, 6), (w - 3, w * 1.4), (w * 0.72, length * 0.7), (c, length * 0.72), (w * 0.28, length * 0.7), (3, w * 1.4)]
    d.polygon([(u(x), u(y)) for x, y in inner], fill=(205, 235, 215, 255))
    d.line([(u(c), u(length * 0.74)), (u(c), u(h - 4))], fill=(150, 155, 160, 255), width=u(1.2))
    save(img, w, h, name)
    return w, h, round(length / h, 4)


if __name__ == "__main__":
    background()
    print("hour", lume_hand("hand_hour_c.png", 14, 108, 18))
    print("minute", lume_hand("hand_minute_c.png", 12, 168, 20))
