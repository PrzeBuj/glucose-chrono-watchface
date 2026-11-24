"""Generuje watchface/src/main/res/raw/watchface.xml (Watch Face Format v2), wersja MAX.

Uruchom: python3 tools/make_watchface.py
Projekt rysowany jest w układzie 466x466 (jak makieta), a tutaj przeliczany na 450x450.

Co można zmieniać w edytorze tarczy na zegarku:
- motyw kolorów (akcent + sekundnik) i kolor tła tarczy,
- 6 pól (komplikacji): glukoza, delta/czas, wykres, lewa i prawa tarczka, pole pod wykresem.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "watchface/src/main/res/raw/watchface.xml"

K = 450 / 466  # skala z makiety


def s(v):
    """Współrzędne i wymiary: WFF wymaga liczb całkowitych."""
    return int(round(v * K))


def f(v):
    """Grubości linii i rozmiary czcionek mogą być ułamkowe."""
    return round(v * K, 1)


C = 233  # środek w układzie makiety

WHITE = "#FFF4F5F7"
BLACK = "#FF000000"
SUB = "#FF1A1D22"
GREY = "#FF9AA1AA"
LIGHT = "#FFC3C8CF"
TICK = "#FF7D838C"
TRACK = "#FF2E333A"

# kolory z ustawień użytkownika
ACCENT = "[CONFIGURATION.theme.0]"
HAND = "[CONFIGURATION.theme.1]"
DIAL = "[CONFIGURATION.dial.0]"

THEMES = [  # (id, nazwa w strings.xml, akcent, sekundnik)
    ("blue", "theme_blue", "#FF4DA3FF", "#FFE5484D"),
    ("teal", "theme_teal", "#FF3DD6C6", "#FFFF8A3D"),
    ("purple", "theme_purple", "#FFB38CFF", "#FFF2C94C"),
    ("green", "theme_green", "#FF5BD68A", "#FFF4F5F7"),
    ("white", "theme_white", "#FFF4F5F7", "#FFE5484D"),
]
DIALS = [
    ("graphite", "dial_graphite", "#FF101215"),
    ("black", "dial_black", "#FF000000"),
    ("navy", "dial_navy", "#FF0E1A2E"),
    ("green", "dial_green", "#FF0F1E17"),
]


def polar(angle_deg, r, cx=C, cy=C):
    a = math.radians(angle_deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def line(a, r1, r2, color, thickness, cap="BUTT", cx=C, cy=C):
    x1, y1 = polar(a, r1, cx, cy)
    x2, y2 = polar(a, r2, cx, cy)
    return (
        f'<Line startX="{s(x1)}" startY="{s(y1)}" endX="{s(x2)}" endY="{s(y2)}">'
        f'<Stroke color="{color}" thickness="{f(thickness)}" cap="{cap}"/></Line>'
    )


def ring(cx, cy, r, color, thickness):
    return (
        f'<Arc centerX="{s(cx)}" centerY="{s(cy)}" width="{s(2 * r)}" height="{s(2 * r)}" '
        f'startAngle="0" endAngle="360"><Stroke color="{color}" thickness="{f(thickness)}"/></Arc>'
    )


def disc(cx, cy, r, fill, stroke=None, thickness=0):
    st = f'<Stroke color="{stroke}" thickness="{f(thickness)}"/>' if stroke else ""
    return (
        f'<Ellipse x="{s(cx - r)}" y="{s(cy - r)}" width="{s(2 * r)}" height="{s(2 * r)}">'
        f'<Fill color="{fill}"/>{st}</Ellipse>'
    )


def text(x, y, w, h, content, size, color, weight="BOLD", align="CENTER", params=()):
    p = "".join(f'<Parameter expression="{e}"/>' for e in params)
    return (
        f'<PartText x="{s(x)}" y="{s(y)}" width="{s(w)}" height="{s(h)}">'
        f'<Text align="{align}" ellipsis="TRUE">'
        f'<Font family="SYNC_TO_DEVICE" size="{f(size)}" weight="{weight}" color="{color}">'
        + (f"<Template>{content}{p}</Template>" if params else content)
        + "</Font></Text></PartText>"
    )


def image(x, y, w, h, resource, tint=None):
    t = f' tintColor="{tint}"' if tint else ""
    return f'<PartImage x="{s(x)}" y="{s(y)}" width="{s(w)}" height="{s(h)}"{t}><Image resource="{resource}"/></PartImage>'


# ---------------------------------------------------------------- tło i skale

def background():
    return (
        '<PartDraw x="0" y="0" width="450" height="450">'
        f'<Rectangle x="0" y="0" width="450" height="450"><Fill color="{DIAL}"/></Rectangle></PartDraw>'
    )


def dial():
    d = [ring(C, C, 222, BLACK, 22)]
    for i in range(300):
        d.append(line(i * 1.2, 224, 231, TICK, 0.8))
    for i in range(60):
        d.append(line(i * 6, 221, 231, WHITE, 1.6))
    for a in (30, 60, 120, 240, 300, 330):
        d.append(line(a, 165, 187, WHITE, 6, cap="ROUND"))
    for dx in (-7, 7):
        d.append(
            f'<Line startX="{s(C + dx)}" startY="{s(40)}" endX="{s(C + dx)}" endY="{s(62)}">'
            f'<Stroke color="{WHITE}" thickness="{f(8)}" cap="ROUND"/></Line>'
        )
    # tarczki (tło pod komplikacjami)
    for cx in (128, 338):
        d.append(disc(cx, 212, 46, SUB, WHITE, 2.5))
        for i in range(40):
            d.append(line(i * 9, 35.5, 40.5, "#FF4A5058", 0.9, cx=cx, cy=212))
    # okienko z godziną cyfrową
    d.append(
        f'<RoundRectangle x="{s(160)}" y="{s(68)}" width="{s(146)}" height="{s(56)}" '
        f'cornerRadiusX="{s(10)}" cornerRadiusY="{s(10)}"><Fill color="{BLACK}"/>'
        f'<Stroke color="{WHITE}" thickness="{f(2)}"/></RoundRectangle>'
    )
    return '<PartDraw x="0" y="0" width="450" height="450">' + "".join(d) + "</PartDraw>"


def numerals():
    out = []
    for n in (5, 10, 15, 20, 40, 45, 50, 55):
        x, y = polar(n * 6, 196)
        out.append(text(x - 16, y - 11, 32, 22, f"{n:02d}", 15, WHITE))
    return "".join(out)


def digital():
    return (
        f'<DigitalClock x="{s(160)}" y="{s(70)}" width="{s(146)}" height="{s(52)}">'
        f'<TimeText format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER" x="0" y="0" '
        f'width="{s(146)}" height="{s(52)}">'
        f'<Font family="SYNC_TO_DEVICE" size="{f(42)}" weight="BOLD" color="{WHITE}"/>'
        f"</TimeText></DigitalClock>"
    )


def info_row():
    """Temperatura, bateria zegarka i puls z czujników Wear OS (bez GlucoDataHandler)."""
    temp_ok = text(132, 130, 64, 24, "%s°", 17, LIGHT, align="END", params=("[WEATHER.TEMPERATURE]",))
    temp_na = text(132, 130, 64, 24, "--°", 17, LIGHT, align="END")
    return (
        "<Condition><Expressions>"
        '<Expression name="weather"><![CDATA[[WEATHER.IS_AVAILABLE]]]></Expression>'
        "</Expressions>"
        f'<Compare expression="weather">{temp_ok}</Compare>'
        f"<Default>{temp_na}</Default></Condition>"
        + image(206, 136, 18, 14, "ic_battery", GREY)
        + text(227, 130, 48, 24, "%s%%", 17, LIGHT, align="START", params=("[BATTERY_PERCENT]",))
        + image(278, 136, 14, 14, "ic_heart", HAND)
        + text(295, 130, 44, 24, "%s", 17, LIGHT, align="START", params=("round([HEART_RATE])",))
    )


# ---------------------------------------------------------------- komplikacje

def slot(slot_id, name, x, y, w, h, types, bounding, bodies, default=("EMPTY", "EMPTY")):
    inner = "".join(f'<Complication type="{t}">{bodies[t]}</Complication>' for t in types)
    return (
        f'<ComplicationSlot slotId="{slot_id}" displayName="@string/{name}" '
        f'x="{s(x)}" y="{s(y)}" width="{s(w)}" height="{s(h)}" '
        f'supportedTypes="{" ".join(types)}" isCustomizable="TRUE">'
        f'<DefaultProviderPolicy defaultSystemProvider="{default[0]}" defaultSystemProviderType="{default[1]}"/>'
        f"{bounding}{inner}</ComplicationSlot>"
    )


def glucose_slot():
    # 260x56: duża wartość, strzałka trendu (ikona), mały podpis
    body = (
        text(0, 0, 260, 54, "%s", 48, WHITE, params=("[COMPLICATION.TEXT]",))
        + image(206, 12, 28, 28, "[COMPLICATION.MONOCHROMATIC_IMAGE]", ACCENT)
        + text(196, 40, 64, 16, "%s", 12, GREY, weight="NORMAL", params=("[COMPLICATION.TITLE]",))
    )
    return slot(
        0, "slot_glucose", 103, 252, 260, 56, ["SHORT_TEXT", "RANGED_VALUE"],
        f'<BoundingBox x="0" y="0" width="{s(260)}" height="{s(56)}"/>',
        {"SHORT_TEXT": body, "RANGED_VALUE": body},
    )


def delta_slot():
    # 200x20: np. „+4 · 2 min”
    body = text(0, 0, 200, 20, "%s  %s", 14, LIGHT, params=("[COMPLICATION.TEXT]", "[COMPLICATION.TITLE]"))
    return slot(
        1, "slot_delta", 133, 304, 200, 20, ["SHORT_TEXT"],
        f'<BoundingBox x="0" y="0" width="{s(200)}" height="{s(20)}"/>',
        {"SHORT_TEXT": body},
    )


def graph_slot():
    w, h = 180, 58
    frame = (
        f'<PartDraw x="0" y="0" width="{s(w)}" height="{s(h)}">'
        f'<RoundRectangle x="0" y="0" width="{s(w)}" height="{s(h)}" cornerRadiusX="{s(10)}" cornerRadiusY="{s(10)}">'
        f'<Fill color="{BLACK}"/><Stroke color="#FF3A3F46" thickness="{f(1.5)}"/></RoundRectangle></PartDraw>'
    )
    return slot(
        2, "slot_graph", 143, 326, w, h, ["PHOTO_IMAGE", "SMALL_IMAGE"],
        f'<BoundingRoundBox x="0" y="0" width="{s(w)}" height="{s(h)}" cornerRadius="{s(10)}"/>',
        {
            "PHOTO_IMAGE": frame + image(3, 3, w - 6, h - 6, "[COMPLICATION.PHOTO_IMAGE]"),
            "SMALL_IMAGE": frame + image(3, 3, w - 6, h - 6, "[COMPLICATION.SMALL_IMAGE]"),
        },
    )


def subdial_slot(slot_id, name, cx, default):
    d = 92  # średnica pola
    x, y = cx - 46, 212 - 46
    value = text(4, 22, d - 8, 30, "%s", 26, WHITE, params=("[COMPLICATION.TEXT]",))
    title = text(4, 52, d - 8, 18, "%s", 12, GREY, weight="NORMAL", params=("[COMPLICATION.TITLE]",))
    progress = (
        f'<PartDraw x="0" y="0" width="{s(d)}" height="{s(d)}">'
        f'<Arc centerX="{s(46)}" centerY="{s(46)}" width="{s(76)}" height="{s(76)}" startAngle="0" endAngle="360">'
        f'<Stroke color="{TRACK}" thickness="{f(5)}"/></Arc>'
        f'<Arc centerX="{s(46)}" centerY="{s(46)}" width="{s(76)}" height="{s(76)}" startAngle="0" endAngle="0">'
        f'<Stroke color="{ACCENT}" thickness="{f(5)}" cap="ROUND"/>'
        '<Transform target="endAngle" value="([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN])'
        ' / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN]) * 360"/></Arc></PartDraw>'
    )
    return slot(
        slot_id, name, x, y, d, d, ["SHORT_TEXT", "RANGED_VALUE", "MONOCHROMATIC_IMAGE"],
        f'<BoundingOval x="0" y="0" width="{s(d)}" height="{s(d)}"/>',
        {
            "SHORT_TEXT": value + title,
            "RANGED_VALUE": progress + value + title,
            "MONOCHROMATIC_IMAGE": image(26, 26, 40, 40, "[COMPLICATION.MONOCHROMATIC_IMAGE]", ACCENT),
        },
        default=default,
    )


def bottom_slot():
    # 160x18 pod wykresem, np. czas działania sensora
    body = text(0, 0, 160, 18, "%s %s", 11, GREY, params=("[COMPLICATION.TITLE]", "[COMPLICATION.TEXT]"))
    return slot(
        5, "slot_bottom", 153, 388, 160, 18, ["SHORT_TEXT"],
        f'<BoundingBox x="0" y="0" width="{s(160)}" height="{s(18)}"/>',
        {"SHORT_TEXT": body},
    )


# ---------------------------------------------------------------- wskazówki

def hands():
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        '<HourHand resource="hand_hour" x="219" y="124" width="12" height="118" pivotX="0.5" pivotY="0.8559"/>'
        '<MinuteHand resource="hand_minute" x="220" y="46" width="10" height="201" pivotX="0.5" pivotY="0.8905"/>'
        "</AnalogClock>"
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<SecondHand resource="hand_second" x="220" y="29" width="10" height="249" pivotX="0.5" pivotY="0.7871" tintColor="{HAND}">'
        '<Sweep frequency="15"/></SecondHand>'
        '<Variant mode="AMBIENT" target="alpha" value="0"/>'
        "</AnalogClock>"
        '<PartDraw x="0" y="0" width="450" height="450">'
        f"{disc(C, C, 8, HAND)}{disc(C, C, 3, BLACK)}</PartDraw>"
    )


def user_configurations():
    themes = "".join(
        f'<ColorOption id="{i}" displayName="@string/{name}" colors="{a} {h}"/>' for i, (_, name, a, h) in enumerate(THEMES)
    )
    dials = "".join(f'<ColorOption id="{i}" displayName="@string/{name}" colors="{c}"/>' for i, (_, name, c) in enumerate(DIALS))
    return (
        "<UserConfigurations>"
        f'<ColorConfiguration id="theme" displayName="@string/cfg_theme" defaultValue="0">{themes}</ColorConfiguration>'
        f'<ColorConfiguration id="dial" displayName="@string/cfg_dial" defaultValue="0">{dials}</ColorConfiguration>'
        "</UserConfigurations>"
    )


def build():
    body = (
        background() + dial() + numerals() + digital() + info_row()
        + subdial_slot(3, "slot_left", 128, ("EMPTY", "EMPTY"))
        + subdial_slot(4, "slot_right", 338, ("WATCH_BATTERY", "RANGED_VALUE"))
        + glucose_slot() + delta_slot() + graph_slot() + bottom_slot() + hands()
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<WatchFace width="450" height="450">\n'
        '<Metadata key="CLOCK_TYPE" value="ANALOG"/>\n'
        '<Metadata key="PREVIEW_TIME" value="10:09:22"/>\n'
        f"{user_configurations()}\n"
        f'<Scene backgroundColor="#FF101215">\n{body}\n</Scene>\n'
        "</WatchFace>\n"
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print("Zapisano", OUT, OUT.stat().st_size, "B")
