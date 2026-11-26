"""Podglądy trzech stylów tarczy (10:09:22, przykładowe dane). Zapisuje preview.png (Sport)
oraz ikony stylów style_*.png do edytora, a duże podglądy do katalogu podanego jako argument.

Uruchom: python3 tools/render_styles.py [katalog_na_podglady]
"""
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent.parent / "watchface/src/main/res/drawable-nodpi"
S = 2
B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
L = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
ACC, ORA, WHITE, GREY, GREEN, RED, LIGHT = (85, 200, 242), (255, 138, 61), (232, 240, 244), (141, 151, 163), (52, 216, 106), (255, 59, 59), (195, 200, 207)
C = 225


class Face:
    def __init__(self, bg=None, fill=(16, 18, 21)):
        self.img = Image.new("RGBA", (450 * S, 450 * S), fill + (255,))
        if bg:
            self.img = Image.open(R / bg).convert("RGBA").resize((450 * S, 450 * S))
        self.d = ImageDraw.Draw(self.img)

    def t(self, x, y, w, h, s, size, col, f=B, align="c"):
        fo = ImageFont.truetype(f, int(size * S))
        bb = self.d.textbbox((0, 0), s, font=fo)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        X = x * S + {"c": (w * S - tw) / 2, "r": w * S - tw, "l": 0}[align] - bb[0]
        self.d.text((X, y * S + (h * S - th) / 2 - bb[1]), s, font=fo, fill=col)

    def line(self, a, r1, r2, col, w):
        a = math.radians(a)
        self.d.line([((C + r1 * math.sin(a)) * S, (C - r1 * math.cos(a)) * S), ((C + r2 * math.sin(a)) * S, (C - r2 * math.cos(a)) * S)], fill=col, width=max(1, int(w * S)))

    def arc(self, cx, cy, r, a0, a1, col, w):
        self.d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], a0 - 90, a1 - 90, fill=col, width=int(w * S))

    def disc(self, cx, cy, r, fill, outline=None, w=0):
        self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill, outline=outline, width=int(w * S))

    def paste(self, name, x, y, w, h, tint=None):
        im = Image.open(R / name).convert("RGBA").resize((w * S, h * S))
        if tint:
            a = im.getchannel("A"); im = Image.new("RGBA", im.size, tint + (255,)); im.putalpha(a)
        self.img.alpha_composite(im, (x * S, y * S))

    def hand(self, name, w, h, pivot, ang, tint=None):
        hi = Image.open(R / name).convert("RGBA").resize((w * S, h * S))
        if tint:
            a = hi.getchannel("A"); hi = Image.new("RGBA", hi.size, tint + (255,)); hi.putalpha(a)
        py = h * pivot * S
        pad = Image.new("RGBA", (w * S, int(2 * py) + 2), (0, 0, 0, 0))
        pad.paste(hi, (0, 0))
        rot = pad.rotate(-ang, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(rot, (int(C * S - rot.width / 2), int(C * S - rot.height / 2)))
        self.d = ImageDraw.Draw(self.img)

    def shared(self, value_font=B, old=False):
        # lewe pole: bateria z łukiem
        self.arc(108, 226, 55, 0, 360, (42, 50, 60), 7)
        self.arc(108, 226, 55, 0, 302, ACC, 7)
        self.t(52, 192, 112, 36, "84%", 30, WHITE)
        self.t(56, 228, 104, 20, "BAT", 15, GREY, f=M)
        # glukoza
        if old:  # Sport 1: wartość wyżej na środku, jednostka i delta pod spodem, wykres niżej
            self.t(90, 300, 176, 66, "118", 64, WHITE, align="r", f=value_font)
            ax, ay = 278 * S, 333 * S
        else:
            self.t(70, 294, 166, 64, "118", 62, WHITE, align="r", f=value_font)
            ax, ay = 246 * S, 326 * S
        self.d.line([(ax, ay + 16 * S), (ax + 26 * S, ay - 12 * S)], fill=GREEN, width=6 * S)
        self.d.line([(ax + 6 * S, ay - 13 * S), (ax + 27 * S, ay - 13 * S), (ax + 27 * S, ay + 8 * S)], fill=GREEN, width=6 * S, joint="curve")
        if old:
            self.t(120, 364, 104, 20, "mg/dL", 15, GREY, f=M, align="r")
            self.t(232, 364, 110, 20, "+3 2 min", 15, LIGHT, align="l")
            gx, gy, gw, gh = 137 * S, 388 * S, 176 * S, 42 * S
        else:
            self.t(288, 306, 70, 18, "mg/dL", 14, GREY, f=M, align="l")
            self.t(288, 324, 76, 20, "+3 2 min", 13, LIGHT, align="l")
            gx, gy, gw, gh = 147 * S, 362 * S, 156 * S, 44 * S
        self.d.rounded_rectangle([gx, gy, gx + gw, gy + gh], radius=8 * S, fill=(20, 24, 28))
        self.d.line([(gx + 4 * S, gy + 14 * S), (gx + gw - 4 * S, gy + 14 * S)], fill=(230, 150, 40), width=S)
        self.d.line([(gx + 4 * S, gy + 34 * S), (gx + gw - 4 * S, gy + 34 * S)], fill=(220, 50, 50), width=S)
        pts = [(gx + (5 + k * 5) * S, gy + (27 - 7 * math.sin(k / 4) - k * 0.2) * S) for k in range(30)]
        self.d.line(pts, fill=(60, 220, 110), width=2 * S)

    def done(self, out):
        circ = Image.new("L", self.img.size, 0)
        ImageDraw.Draw(circ).ellipse([0, 0, self.img.width - 1, self.img.height - 1], fill=255)
        o = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        o.paste(self.img, (0, 0), circ)
        return o


def sport(bg="bg_sport.png", old=False):
    f = Face(bg)
    for k in range(60):
        if k % 15 == 0: f.line(k * 6, 204, 220, ORA, 4)
        elif k % 5 == 0: f.line(k * 6, 206, 220, ACC, 3.4)
        else: f.line(k * 6, 213, 220, ACC, 1.6)
    f.t(120, 52, 210, 24, "ŚR 25", 19, ACC)
    f.t(100, 72, 250, 70, "10:09", 64, WHITE)
    f.paste("ic_heart.png", 196, 141, 14, 14, RED)
    f.t(213, 136, 50, 22, "72", 16, LIGHT, f=M, align="l")
    f.arc(342, 226, 55, 200, 340, ORA, 5)
    f.arc(342, 226, 55, 20, 160, ACC, 5)
    f.t(290, 204, 104, 40, "14°", 34, WHITE)
    f.t(302, 244, 80, 20, "POGODA", 13, GREY, f=M)
    f.shared(old=old)
    f.hand("hand_hour_o.png", 28, 138, 0.8551, (10 + 9 / 60) * 30)
    f.hand("hand_minute_o.png", 26, 206, 0.8932, 9.37 * 6)
    f.hand("hand_second_o.png", 8, 232, 0.8448, 22 * 6, RED)
    f.disc(C, C, 12, (180, 186, 192)); f.disc(C, C, 8, RED); f.disc(C, C, 3, (58, 12, 12))
    return f.done(None)


def chrono():
    f = Face(fill=(16, 18, 21))
    f.img.alpha_composite(Image.open(R / "gear_big.png").convert("RGBA").resize((294 * S, 294 * S)), (78 * S, 78 * S))
    for cx, cy in ((108, 226), (342, 226)):
        f.img.alpha_composite(Image.open(R / "gear_small.png").convert("RGBA").resize((128 * S, 128 * S)), ((cx - 64) * S, (cy - 64) * S))
    f.d = ImageDraw.Draw(f.img)
    f.arc(C, C, 214, 0, 360, (0, 0, 0), 21)
    for k in range(300): f.line(k * 1.2, 216, 223, (125, 131, 140), 0.8)
    for k in range(60): f.line(k * 6, 213, 223, WHITE, 1.5)
    for a in (30, 60, 120, 240, 300, 330): f.line(a, 159, 181, WHITE, 6)
    for dx in (-7, 7): f.d.line([((C + dx) * S, 39 * S), ((C + dx) * S, 60 * S)], fill=WHITE, width=8 * S)
    for cx, cy in ((108, 226), (342, 226)): f.disc(cx, cy, 60, (26, 29, 34), WHITE, 2.4)
    f.d.rounded_rectangle([155 * S, 64 * S, 296 * S, 118 * S], radius=10 * S, fill=(0, 0, 0), outline=WHITE, width=2 * S)
    f.t(290, 204, 104, 40, "14°", 34, WHITE); f.t(302, 244, 80, 20, "POGODA", 13, GREY, f=M)
    for n in (5, 10, 15, 20, 40, 45, 50, 55):
        a = math.radians(n * 6); x, y = C + 190 * math.sin(a), C - 190 * math.cos(a)
        f.t(x - 15, y - 11, 30, 22, f"{n:02d}", 14, WHITE)
    f.t(155, 66, 141, 50, "10:09", 40, WHITE)
    f.t(130, 124, 80, 22, "78%", 16, LIGHT, align="r")
    f.paste("ic_heart.png", 226, 129, 14, 14, (229, 72, 77)); f.t(243, 124, 60, 22, "72", 16, LIGHT, align="l")
    f.shared()
    f.hand("hand_hour.png", 12, 118, 0.8559, (10 + 9 / 60) * 30)
    f.hand("hand_minute.png", 10, 201, 0.8905, 9.37 * 6)
    f.hand("hand_second.png", 10, 249, 0.7871, 22 * 6, (229, 72, 77))
    f.disc(C, C, 7.5, (229, 72, 77)); f.disc(C, C, 3, (0, 0, 0))
    return f.done(None)


def classic():
    f = Face("bg_classic.png")
    f.paste("ic_battery.png", 184, 72, 18, 14, LIGHT); f.t(205, 68, 60, 22, "84%", 15, LIGHT, f=M, align="l")
    f.t(140, 88, 170, 22, "ŚR 25", 17, LIGHT, f=L)
    f.t(110, 106, 230, 58, "10:09", 54, WHITE, f=L)
    f.t(290, 204, 104, 40, "14°", 34, WHITE); f.t(302, 244, 80, 20, "POGODA", 13, GREY, f=M)
    f.shared()
    f.hand("hand_hour_c.png", 14, 126, 0.8571, (10 + 9 / 60) * 30)
    f.hand("hand_minute_c.png", 12, 188, 0.8936, 9.37 * 6)
    f.hand("hand_second_o.png", 8, 232, 0.8448, 22 * 6, RED)
    f.disc(C, C, 9, (200, 205, 210)); f.disc(C, C, 5, RED)
    return f.done(None)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    sport1 = lambda: sport("bg_sport1.png")
    for name, fn in (("sport", sport), ("sport1", sport1), ("chrono", chrono), ("classic", classic)):
        img = fn()
        img.resize((160, 160), Image.LANCZOS).save(R / f"style_{name}.png")
        if name == "sport":
            img.save(R / "preview.png")
        if out:
            out.mkdir(parents=True, exist_ok=True)
            img.save(out / f"styl-{name}.png")
    print("ok")
