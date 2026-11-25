"""Tło stylu „Sport 1” (pierwsza wersja Glukoza Sport: prostokątne panele). Wskazówki wspólne ze stylem Sport.

Uruchom: python3 tools/make_assets_sport1.py   (zapis do watchface/src/main/res/drawable-nodpi)
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


def lerp(c1, c2, t):
    return tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(len(c1)))


def panel_layer(size, draw_shape, top, bottom, edge, y0, y1):
    """Panel z pionowym gradientem (jaśniejszy u góry), krawędzią i cieniem."""
    mask = Image.new("L", size, 0)
    draw_shape(ImageDraw.Draw(mask), 255)
    grad = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for yy in range(u(y0), u(y1) + 1, 2):
        t = (yy - u(y0)) / max(1, u(y1) - u(y0))
        gd.line([(0, yy), (size[0], yy)], fill=lerp(top, bottom, min(1, t)) + (255,), width=2)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.paste(grad, (0, 0), mask)
    # krawędź: jaśniejsza u góry, ciemniejsza na dole
    rim = Image.new("L", size, 0)
    draw_shape(ImageDraw.Draw(rim), 255, outline=True)
    rim_col = Image.new("RGBA", size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim_col)
    for yy in range(u(y0) - u(4), u(y1) + 1, 2):
        t = (yy - u(y0)) / max(1, u(y1) - u(y0))
        rd.line([(0, yy), (size[0], yy)], fill=lerp(edge, (40, 48, 55, 255), max(0, min(1, t * 1.6))), width=2)
    layer.paste(rim_col, (0, 0), rim)
    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow.putalpha(mask.filter(ImageFilter.GaussianBlur(u(6))).point(lambda p: int(p * 0.85)))
    return shadow, layer


def background():
    size = (u(N), u(N))
    img = Image.new("RGBA", size, (10, 13, 16, 255))
    # plaster miodu: ciemne komórki, jaśniejsze grafitowe ścianki
    hexl = Image.new("RGBA", size, (52, 59, 66, 255))
    hd = ImageDraw.Draw(hexl)
    r = 8.5
    w = math.sqrt(3) * r
    row = 0
    y = -r
    while y < N + r:
        x = (w / 2 if row % 2 else 0) - w
        while x < N + w:
            pts = [(u(x + r * 0.84 * math.cos(math.radians(60 * k + 30))), u(y + r * 0.84 * math.sin(math.radians(60 * k + 30)))) for k in range(6)]
            hd.polygon(pts, fill=(17, 20, 23, 255))
            # lekki połysk górnej krawędzi komórki
            hd.line([pts[4], pts[5]], fill=(70, 79, 88, 255), width=u(0.6))
            x += w
        y += r * 1.5
        row += 1
    # siatka wyraźna w środku, ciemnieje ku brzegom (jak światło na tarczy)
    shade = Image.new("L", size, 0)
    sd = ImageDraw.Draw(shade)
    for k in range(50):
        rr = u(225) * (1 - k / 50)
        sd.ellipse([u(225) - rr, u(225) - rr, u(225) + rr, u(225) + rr], fill=int(120 + k * 2.7))
    img.paste(hexl, (0, 0), shade)

    top, bottom, edge = (70, 83, 92), (36, 45, 51), (118, 132, 142, 255)
    shapes = [
        (lambda d, c, outline=False: d.rounded_rectangle([u(92), u(46), u(358), u(162)], radius=u(34), fill=None if outline else c, outline=c if outline else None, width=u(1.4)), 46, 162),
        (lambda d, c, outline=False: d.ellipse([u(46), u(164), u(170), u(288)], fill=None if outline else c, outline=c if outline else None, width=u(1.4)), 164, 288),
        (lambda d, c, outline=False: d.ellipse([u(280), u(164), u(404), u(288)], fill=None if outline else c, outline=c if outline else None, width=u(1.4)), 164, 288),
        (lambda d, c, outline=False: d.rounded_rectangle([u(58), u(296), u(392), u(480)], radius=u(40), fill=None if outline else c, outline=c if outline else None, width=u(1.4)), 296, 450),
    ]
    for shape, y0, y1 in shapes:
        sh, layer = panel_layer(size, shape, top, bottom, edge, y0, y1)
        img = Image.alpha_composite(img, sh)
        img = Image.alpha_composite(img, layer)

    # pierścień skali: ciemniejszy, z delikatną poświatą podziałek
    ring = Image.new("RGBA", size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([0, 0, u(N), u(N)], outline=(6, 9, 12, 235), width=u(26))
    img = Image.alpha_composite(img, ring)
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for k in range(60):
        a = math.radians(k * 6)
        r1 = 204 if k % 5 == 0 else 212
        col = (255, 138, 61, 255) if k % 15 == 0 else (85, 200, 242, 255)
        gd.line([(u(225 + r1 * math.sin(a)), u(225 - r1 * math.cos(a))), (u(225 + 220 * math.sin(a)), u(225 - 220 * math.cos(a)))], fill=col, width=u(5))
    glow = glow.filter(ImageFilter.GaussianBlur(u(4)))
    glow.putalpha(glow.getchannel("A").point(lambda p: int(p * 0.55)))
    img = Image.alpha_composite(img, glow)

    circ = Image.new("L", size, 0)
    ImageDraw.Draw(circ).ellipse([0, 0, u(N) - 1, u(N) - 1], fill=255)
    out = Image.new("RGBA", size, (0, 0, 0, 255))
    out.paste(img, (0, 0), circ)
    save(out, N, N, "bg_sport1.png")


def outlined_hand(name, w, length, tail, color, pad=6):
    """Neonowa wskazówka konturowa: pusty środek (widać tło), jasny kontur z poświatą.
    Obraz ma margines `pad` na poświatę; oś obrotu w punkcie (szerokość/2, pad + length)."""
    W, H = w + 2 * pad, length + tail + 2 * pad
    img = big(W, H)
    c = W / 2
    pts = [(c, pad), (pad + w - 1, pad + w * 0.9), (pad + w - 1, pad + length + tail - 4),
           (c, pad + length + tail), (pad + 1, pad + length + tail - 4), (pad + 1, pad + w * 0.9)]
    pts = [(u(x), u(y)) for x, y in pts]
    core = big(W, H)
    cd = ImageDraw.Draw(core)
    cd.polygon(pts, fill=(14, 18, 22, 110))
    cd.line(pts + [pts[0]], fill=color, width=u(2.6), joint="curve")
    glow = big(W, H)
    ImageDraw.Draw(glow).line(pts + [pts[0]], fill=color, width=u(5))
    glow = glow.filter(ImageFilter.GaussianBlur(u(2.6)))
    img = Image.alpha_composite(img, glow)
    img = Image.alpha_composite(img, core)
    # biały środek konturu (efekt neonu)
    hi = big(W, H)
    ImageDraw.Draw(hi).line(pts + [pts[0]], fill=(255, 255, 255, 170), width=u(0.9), joint="curve")
    img = Image.alpha_composite(img, hi)
    save(img, W, H, name)
    return W, H, round((pad + length) / H, 4)


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
