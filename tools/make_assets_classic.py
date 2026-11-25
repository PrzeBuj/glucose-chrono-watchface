"""Grafiki stylu „Klasyczny” (wzór Przemka): włókno węglowe, wypukła szara tarcza ze szczotkowaniem
słonecznym, polerowane srebrne pierścienie i indeksy z połyskiem 3D, wskazówki fasetowane z lumą.

Uruchom: python3 tools/make_assets_classic.py
Światło pada z lewej góry (kąt 315°).
"""
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
X, SS, N = 2, 3, 450
P = X * SS                      # pikseli na jednostkę tarczy
W = N * P
LIGHT = math.radians(315)       # kierunek światła (0 = góra, zgodnie z zegarem)


def u(v):
    return int(round(v * P))


def save(img, w, h, name):
    img.resize((w * X, h * X), Image.LANCZOS).save(OUT / name, optimize=True)


yy, xx = np.mgrid[0:W, 0:W].astype(np.float32) / P
DX, DY = xx - 225, yy - 225
RAD = np.hypot(DX, DY)
ANG = np.arctan2(DX, -DY)       # 0 = góra


def to_img(rgb, alpha):
    a = np.clip(alpha, 0, 1)[..., None]
    arr = np.concatenate([np.clip(rgb, 0, 255), a * 255], axis=-1).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def gray(v):
    return np.stack([v, v * 1.02 + 1, v * 1.06 + 3], axis=-1)


def carbon():
    """Splot twill 2x2: skośne pasma, każde z połyskiem wzdłuż włókna."""
    cell = 5.0
    gx, gy = np.floor(xx / cell), np.floor(yy / cell)
    fx, fy = (xx / cell) % 1, (yy / cell) % 1
    horiz = ((gx + gy) % 4) < 2
    t = np.where(horiz, fy, fx)
    shine = np.sin(t * math.pi) ** 1.5
    v = np.where(horiz, 12 + 40 * shine, 8 + 22 * shine)
    return gray(v)


def sunburst(r_dial):
    """Szara tarcza: szczotkowanie promieniste + wypukłe cieniowanie (jaśniej od strony światła)."""
    rng = np.random.default_rng(3)
    k = 1440
    lines = rng.normal(0, 1, k).astype(np.float32)
    lines = np.convolve(np.concatenate([lines, lines[:8]]), np.ones(3) / 3, "same")[:k]
    idx = ((ANG / (2 * math.pi)) % 1 * k).astype(np.int32)
    brush = lines[idx] * 5
    light = np.cos(ANG - LIGHT)
    dome = (1 - (RAD / r_dial) ** 2).clip(0, 1)
    v = 44 + brush + 14 * light * (RAD / r_dial) + 8 * dome
    # błysk w kształcie klina, jak na szczotkowanym metalu
    v += 22 * np.exp(-((((ANG - LIGHT + math.pi) % (2 * math.pi)) - math.pi) / 0.35) ** 2) * (RAD / r_dial) ** 0.7
    v += 12 * np.exp(-((((ANG - LIGHT) % (2 * math.pi)) - math.pi) / 0.35) ** 2) * (RAD / r_dial) ** 0.7
    return gray(v)


def polished_ring(cx, cy, r_mid, width, base=150, amp=100):
    """Wypukły polerowany pierścień: jasny od strony światła, z grzbietem na środku szerokości."""
    dx, dy = xx - cx, yy - cy
    rr = np.hypot(dx, dy)
    ang = np.arctan2(dx, -dy)
    t = (rr - (r_mid - width / 2)) / width
    inside = (t >= 0) & (t <= 1)
    profile = np.cos((t - 0.5) * math.pi)              # 0 na krawędziach, 1 na grzbiecie
    facet = np.where(t < 0.5, 1.0, -0.6)               # wewnętrzna połowa łapie światło od drugiej strony
    lit = np.cos(ang - LIGHT) * facet
    v = base + amp * lit * 0.8 + 70 * profile ** 6 - 40 * (1 - profile)
    v += 60 * np.exp(-(((ang - LIGHT + math.pi) % (2 * math.pi) - math.pi) / 0.5) ** 2) * profile ** 3
    edge_aa = np.clip(np.minimum(t, 1 - t) * width * P, 0, 1)
    return gray(v), inside * edge_aa


def composite(base_img, rgb, alpha):
    return Image.alpha_composite(base_img, to_img(rgb, alpha))


def shadow(mask_img, blur, dx=1.5, dy=2.5, strength=0.8):
    m = mask_img.filter(ImageFilter.GaussianBlur(u(blur)))
    sh = Image.new("RGBA", m.size, (0, 0, 0, 0))
    sh.putalpha(m.point(lambda p: int(p * strength)))
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    out.paste(sh, (u(dx), u(dy)))
    return out


def bar_3d(img, ang_deg, r1, r2, w, lume=False):
    """Indeks nakładany: dwie fasety (jasna i ciemniejsza), obrys, cień."""
    a = math.radians(ang_deg)
    ux, uy = math.sin(a), -math.cos(a)
    px, py = -uy, ux
    # współrzędne lokalne: wzdłuż (s) i w poprzek (q)
    s = DX * ux + DY * uy
    q = DX * px + DY * py
    m = (s >= r1) & (s <= r2) & (np.abs(q) <= w / 2)
    mimg = Image.fromarray((m * 255).astype(np.uint8), "L")
    img = Image.alpha_composite(img, shadow(mimg, 2.0))
    lit = np.cos(a + math.pi / 2 - LIGHT)             # która faseta jest bliżej światła
    face_l = 230 if lit < 0 else 150
    face_r = 150 if lit < 0 else 230
    v = np.where(q < 0, face_l, face_r) + 25 * np.exp(-(q / (w * 0.12)) ** 2)
    edge = np.minimum.reduce([s - r1, r2 - s, w / 2 - np.abs(q)])
    v = np.where(edge < 0.7, 95, v)
    img = composite(img, gray(v), m.astype(np.float32))
    if lume:
        lm = (s >= r1 + 3) & (s <= r2 - 3) & (np.abs(q) <= w / 2 - 2.2)
        lv = np.stack([90 + 0 * q, 210 + 25 * np.exp(-(q / 1.5) ** 2), 140 + 0 * q], axis=-1)
        img = composite(img, lv, lm.astype(np.float32))
    return img


def background():
    img = to_img(carbon(), np.ones_like(RAD))
    R_DIAL = 175
    # szara tarcza: cień na włóknie, wypukła powierzchnia, ciemny rant
    dial_m = Image.fromarray(((RAD <= R_DIAL) * 255).astype(np.uint8), "L")
    img = Image.alpha_composite(img, shadow(dial_m, 4, 2, 3, 0.9))
    img = composite(img, sunburst(R_DIAL), np.clip((R_DIAL - RAD) * P, 0, 1))
    rim = np.clip(1 - np.abs(RAD - R_DIAL + 0.8) / 1.2, 0, 1)
    img = composite(img, gray(20 + 0 * RAD), rim * 0.9)
    hl = np.clip(1 - np.abs(RAD - R_DIAL + 2.2) / 0.8, 0, 1) * np.clip(np.cos(ANG - LIGHT), 0, 1)
    img = composite(img, gray(200 + 0 * RAD), hl * 0.5)

    # kreski minutowe na obrzeżu
    d = ImageDraw.Draw(img)
    for k in range(60):
        if k % 5 == 0 or k in (1, 59, 14, 16, 29, 31, 44, 46):
            continue  # przy cyfrach bez kresek
        a = math.radians(k * 6)
        d.line([(u(225 + 203 * math.sin(a)), u(225 - 203 * math.cos(a))), (u(225 + 211 * math.sin(a)), u(225 - 211 * math.cos(a)))],
               fill=(205, 210, 214, 255), width=u(1.3))
    # indeksy godzinowe 3D
    for h in range(12):
        ang = h * 30
        if h in (0, 3, 6, 9):
            continue  # tu są cyfry
        else:
            img = bar_3d(img, ang, 176, 205, 9, lume=h in (4, 8))

    # cyfry 12, 3, 6, 9: polerowany metal (gradient), ciemny obrys i cień
    from PIL import ImageFont
    fo = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", u(27))
    for txt, ang, r in (("12", 0, 199), ("3", 90, 200), ("6", 180, 199), ("9", 270, 200)):
        a = math.radians(ang)
        cx, cy = 225 + r * math.sin(a), 225 - r * math.cos(a)
        m = Image.new("L", img.size, 0)
        md = ImageDraw.Draw(m)
        bb = md.textbbox((0, 0), txt, font=fo)
        md.text((u(cx) - (bb[2] - bb[0]) / 2 - bb[0], u(cy) - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=fo, fill=255)
        img = Image.alpha_composite(img, shadow(m, 1.6, 1.2, 2.0, 0.9))
        outline = m.filter(ImageFilter.MaxFilter(u(1.2) // 2 * 2 + 1))
        img = composite(img, gray(70 + 0 * RAD), np.array(outline, dtype=np.float32) / 255)
        top, bot = cy - 13, cy + 13
        t = np.clip((yy - top) / (bot - top), 0, 1)
        v = 245 - 110 * t + 30 * np.exp(-((t - 0.45) / 0.08) ** 2) - 40 * np.exp(-((t - 0.55) / 0.06) ** 2)
        img = composite(img, gray(v), np.array(m, dtype=np.float32) / 255)

    # bezel: niebieskie szkło szafirowe i biała linia
    ring_rgb = np.stack([30 + 40 * np.cos(ANG - LIGHT), 70 + 60 * np.cos(ANG - LIGHT), 110 + 70 * np.cos(ANG - LIGHT)], axis=-1) + 30
    img = composite(img, ring_rgb, np.clip((RAD - 216) * P, 0, 1) * np.clip((226 - RAD) * P, 0, 1))
    img = composite(img, gray(225 + 0 * RAD), np.clip(1 - np.abs(RAD - 215) / 1.0, 0, 1) * (0.55 + 0.45 * np.cos(ANG - LIGHT)))

    # koła widżetów: wypukły polerowany pierścień, środek z koncentrycznym szlifem
    for cx, cy in ((108, 226), (342, 226)):
        m = Image.fromarray(((np.hypot(xx - cx, yy - cy) <= 64) * 255).astype(np.uint8), "L")
        img = Image.alpha_composite(img, shadow(m, 3, 2, 3, 0.9))
        rr = np.hypot(xx - cx, yy - cy)
        conc = 24 + 5 * np.sin(rr * 7.0) + 4 * np.cos(np.arctan2(xx - cx, -(yy - cy)) - LIGHT) * rr / 60
        img = composite(img, gray(conc), np.clip((58.5 - rr) * P, 0, 1))
        rgb, a = polished_ring(cx, cy, 61.5, 7)
        img = composite(img, rgb, a)
        d = ImageDraw.Draw(img)
        for k in range(12):
            t = math.radians(k * 30)
            d.line([(u(cx + 47 * math.sin(t)), u(cy - 47 * math.cos(t))), (u(cx + 53 * math.sin(t)), u(cy - 53 * math.cos(t)))],
                   fill=(200, 204, 208, 255), width=u(1.6))

    # okienko wykresu: wpuszczone, polerowana ramka
    d = ImageDraw.Draw(img)
    fr = Image.new("L", img.size, 0)
    ImageDraw.Draw(fr).rounded_rectangle([u(141), u(356), u(309), u(410)], radius=u(12), fill=255)
    img = Image.alpha_composite(img, shadow(fr, 3, 1.5, 2.5, 0.9))
    frame_v = 120 + 90 * np.clip((380 - yy) / 26, -1, 1)
    frame = np.array(fr, dtype=np.float32) / 255
    img = composite(img, gray(frame_v), frame)
    inner = Image.new("L", img.size, 0)
    ImageDraw.Draw(inner).rounded_rectangle([u(145), u(360), u(305), u(406)], radius=u(9), fill=255)
    img = composite(img, gray(9 + 6 * np.clip((yy - 360) / 46, 0, 1)), np.array(inner, dtype=np.float32) / 255)

    circ = Image.new("L", img.size, 0)
    ImageDraw.Draw(circ).ellipse([0, 0, W - 1, W - 1], fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 255))
    out.paste(img, (0, 0), circ)
    save(out, N, N, "bg_classic.png")


def bar_3d_offset(img, ang_deg, r1, r2, w, off):
    """Indeks przesunięty w poprzek (podwójne indeksy na 12 i 6)."""
    global DX, DY
    a = math.radians(ang_deg)
    px, py = math.cos(a), math.sin(a)
    sx, sy = DX, DY
    DX, DY = sx - off * px, sy - off * py
    try:
        return bar_3d(img, ang_deg, r1, r2, w)
    finally:
        DX, DY = sx, sy


def faceted_hand(name, w, length, tail):
    """Wskazówka fasetowana: jasna lewa i ciemniejsza prawa połowa, wstawka z lumą; oś w (w/2, length)."""
    h = length + tail
    S = 8
    Wd, Hd = w * X * S, h * X * S
    img = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    k = X * S
    c = w / 2
    outer = [(c, 0), (w, w * 1.3), (w * 0.8, h - 5), (c, h), (w * 0.2, h - 5), (0, w * 1.3)]
    left = [(c, 0), (c, h), (w * 0.2, h - 5), (0, w * 1.3)]
    right = [(c, 0), (w, w * 1.3), (w * 0.8, h - 5), (c, h)]
    d = ImageDraw.Draw(img)
    d.polygon([(x * k, y * k) for x, y in left], fill=(236, 238, 240, 255))
    d.polygon([(x * k, y * k) for x, y in right], fill=(150, 155, 160, 255))
    d.line([(x * k, y * k) for x, y in outer + [outer[0]]], fill=(90, 94, 98, 255), width=k // 2)
    lume = [(c, 7), (w - 3, w * 1.5), (w * 0.7, length * 0.72), (c, length * 0.75), (w * 0.3, length * 0.72), (3, w * 1.5)]
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).polygon([(x * k, y * k) for x, y in lume], fill=(170, 255, 190, 140))
    glow = glow.filter(ImageFilter.GaussianBlur(k * 0.8))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    d.polygon([(x * k, y * k) for x, y in lume], fill=(212, 240, 218, 255))
    img.resize((w * X, h * X), Image.LANCZOS).save(OUT / name, optimize=True)
    return w, h, round(length / h, 4)


if __name__ == "__main__":
    background()
    print("hour", faceted_hand("hand_hour_c.png", 14, 108, 18))
    print("minute", faceted_hand("hand_minute_c.png", 12, 168, 20))
