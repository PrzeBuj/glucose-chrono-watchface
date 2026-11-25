"""Podgląd tarczy „Glukoza Sport” (preview.png do Google Play / edytora), rysowany jak na zegarku o 10:09:22."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
S = 2
B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
ACC, ORA, WHITE, GREY, GREEN, RED = (85, 200, 242), (255, 138, 61), (232, 240, 244), (141, 151, 163), (52, 216, 106), (255, 59, 59)


def font(p, size):
    return ImageFont.truetype(p, int(size * S))


def main(out):
    img = Image.open(R / "bg_sport.png").convert("RGBA").resize((450 * S, 450 * S))
    d = ImageDraw.Draw(img)
    C = 225 * S
    for k in range(60):
        a = math.radians(k * 6)
        r1, col, w = (204, ORA, 4) if k % 15 == 0 else (206, ACC, 3.4) if k % 5 == 0 else (213, ACC, 1.6)
        d.line([(C + r1 * S * math.sin(a), C - r1 * S * math.cos(a)), (C + 220 * S * math.sin(a), C - 220 * S * math.cos(a))], fill=col, width=int(w * S))

    def t(x, y, w, h, s, size, col, f=B, align="c"):
        fo = font(f, size)
        bb = d.textbbox((0, 0), s, font=fo)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        X = x * S + {"c": (w * S - tw) / 2, "r": w * S - tw, "l": 0}[align] - bb[0]
        d.text((X, y * S + (h * S - th) / 2 - bb[1]), s, font=fo, fill=col)
    t(120, 52, 210, 24, "ŚR 25", 19, ACC)
    t(100, 72, 250, 70, "10:09", 64, WHITE)
    t(196, 136, 70, 22, "♥ 72", 16, (195, 200, 207), f=M)
    # lewe koło
    cx, cy, r = 108 * S, 226 * S, 55 * S
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(42, 50, 60), width=7 * S)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 302, fill=ACC, width=7 * S)
    t(46, 190, 124, 36, "84%", 30, WHITE)
    t(56, 226, 104, 20, "BAT", 15, GREY, f=M)
    # prawe koło
    cx = 342 * S
    r = 55 * S
    d.arc([cx - r, cy - r, cx + r, cy + r], 110, 250, fill=ORA, width=5 * S)
    d.arc([cx - r, cy - r, cx + r, cy + r], -70, 70, fill=ACC, width=5 * S)
    t(290, 204, 104, 40, "14°", 34, WHITE)
    t(302, 244, 80, 20, "POGODA", 13, GREY, f=M)
    # glukoza
    t(90, 300, 176, 66, "118", 64, WHITE, align="r")
    ax, ay = 272 * S, 333 * S
    d.line([(ax, ay + 16 * S), (ax + 26 * S, ay - 12 * S)], fill=GREEN, width=6 * S)
    d.line([(ax + 6 * S, ay - 13 * S), (ax + 27 * S, ay - 13 * S), (ax + 27 * S, ay + 8 * S)], fill=GREEN, width=6 * S, joint="curve")
    t(120, 364, 104, 20, "mg/dL", 15, GREY, f=M, align="r")
    t(232, 364, 110, 20, "+3  2 min", 15, (195, 200, 207), align="l")
    # wykres
    gx, gy, gw, gh = 137 * S, 388 * S, 176 * S, 42 * S
    d.rounded_rectangle([gx, gy, gx + gw, gy + gh], radius=8 * S, fill=(38, 47, 54))
    d.rectangle([gx + 4 * S, gy + 12 * S, gx + gw - 4 * S, gy + 32 * S], fill=(22, 90, 45))
    pts = [(gx + (6 + k * 6) * S, gy + (28 - 10 * math.sin(k / 4) - k * 0.25) * S) for k in range(28)]
    for p in pts:
        d.ellipse([p[0] - 1.6 * S, p[1] - 1.6 * S, p[0] + 1.6 * S, p[1] + 1.6 * S], fill=(230, 240, 235))
    # wskazówki
    def hand(name, w, h, pivot, ang, tint=None):
        hi = Image.open(R / name).convert("RGBA").resize((w * S, h * S))
        if tint:
            a = hi.getchannel("A"); hi = Image.new("RGBA", hi.size, tint + (255,)); hi.putalpha(a)
        py = h * pivot * S
        pad = Image.new("RGBA", (w * S, int(2 * py) + 2), (0, 0, 0, 0))
        pad.paste(hi, (0, 0))
        rot = pad.rotate(-ang, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(rot, (int(C - rot.width / 2), int(C - rot.height / 2)))
    hand("hand_hour_o.png", 28, 138, 0.8551, (10 + 9 / 60) * 30)
    hand("hand_minute_o.png", 26, 206, 0.8932, 9.37 * 6)
    hand("hand_second_o.png", 8, 232, 0.8448, 22 * 6, RED)
    d = ImageDraw.Draw(img)
    d.ellipse([C - 12 * S, C - 12 * S, C + 12 * S, C + 12 * S], fill=(180, 186, 192))
    d.ellipse([C - 8 * S, C - 8 * S, C + 8 * S, C + 8 * S], fill=RED)
    d.ellipse([C - 3 * S, C - 3 * S, C + 3 * S, C + 3 * S], fill=(58, 12, 12))
    circ = Image.new("L", img.size, 0)
    ImageDraw.Draw(circ).ellipse([0, 0, img.width - 1, img.height - 1], fill=255)
    outimg = Image.new("RGBA", img.size, (0, 0, 0, 0))
    outimg.paste(img, (0, 0), circ)
    outimg.save(out)


if __name__ == "__main__":
    main(R / "preview.png")
