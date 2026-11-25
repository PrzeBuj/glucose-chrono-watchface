"""Generuje watchface/src/main/res/raw/watchface.xml (Watch Face Format v2), wygląd „Glukoza Sport”.

Uruchom: python3 tools/make_assets_v3.py && python3 tools/make_watchface.py
Układ 450x450. Poprzedni wygląd (chronograf MAX) jest w tools/legacy_racing_max.py.

Na tarczy:
- u góry data, duża godzina cyfrowa i puls,
- lewe koło: pole (domyślnie bateria zegarka, z łukiem postępu),
- prawe koło: temperatura z pogody Wear OS,
- na dole panel glukozy: duża wartość, strzałka trendu tuż obok, delta, wykres GlucoDataHandler,
- wskazówki konturowe, płynny sekundnik.
Ustawienia: motyw kolorów (podziałki i łuki + sekundnik).
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "watchface/src/main/res/raw/watchface.xml"
C = 225

WHITE = "#FFE8F0F4"
BLACK = "#FF000000"
GREY = "#FF8D97A3"
LIGHT = "#FFC3C8CF"
TRACK = "#FF2A323C"
ORANGE = "#FFFF8A3D"
GREEN = "#FF34D86A"
RED = "#FFFF3B3B"

ACCENT = "[CONFIGURATION.theme.0]"
HAND = "[CONFIGURATION.theme.1]"

THEMES = [  # (nazwa w strings.xml, podziałki i łuki, sekundnik)
    ("theme_blue", "#FF55C8F2", "#FFFF3B3B"),
    ("theme_teal", "#FF3DD6C6", "#FFFF8A3D"),
    ("theme_purple", "#FFB38CFF", "#FFF2C94C"),
    ("theme_green", "#FF5BD68A", "#FFFF3B3B"),
    ("theme_white", "#FFE8ECF0", "#FFFF3B3B"),
]


def i(v):
    return int(round(v))


def polar(a, r, cx=C, cy=C):
    t = math.radians(a)
    return cx + r * math.sin(t), cy - r * math.cos(t)


def line(a, r1, r2, color, th, cap="BUTT"):
    x1, y1 = polar(a, r1)
    x2, y2 = polar(a, r2)
    return (f'<Line startX="{i(x1)}" startY="{i(y1)}" endX="{i(x2)}" endY="{i(y2)}">'
            f'<Stroke color="{color}" thickness="{th}" cap="{cap}"/></Line>')


def text(x, y, w, h, content, size, color, weight="BOLD", align="CENTER", params=()):
    p = "".join(f'<Parameter expression="{e}"/>' for e in params)
    return (f'<PartText x="{i(x)}" y="{i(y)}" width="{i(w)}" height="{i(h)}">'
            f'<Text align="{align}" ellipsis="TRUE">'
            f'<Font family="SYNC_TO_DEVICE" size="{size}" weight="{weight}" color="{color}">'
            + (f"<Template>{content}{p}</Template>" if params else content)
            + "</Font></Text></PartText>")


def image(x, y, w, h, res, tint=None, extra=""):
    t = f' tintColor="{tint}"' if tint else ""
    return f'<PartImage x="{i(x)}" y="{i(y)}" width="{i(w)}" height="{i(h)}"{t}><Image resource="{res}"/>{extra}</PartImage>'


def slot(sid, name, x, y, w, h, types, bounding, bodies, default=("EMPTY", None)):
    inner = "".join(f'<Complication type="{t}">{bodies[t]}</Complication>' for t in types)
    dtype = default[1] or types[0]  # typ EMPTY blokuje ustawienie tarczy na zegarku
    return (f'<ComplicationSlot slotId="{sid}" displayName="@string/{name}" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'supportedTypes="{" ".join(types)}" isCustomizable="TRUE">'
            f'<DefaultProviderPolicy defaultSystemProvider="{default[0]}" defaultSystemProviderType="{dtype}"/>'
            f"{bounding}{inner}</ComplicationSlot>")


# ------------------------------------------------------------------ tło, podziałki

def background():
    # tło z panelami (PNG); w trybie Always-On ukryte, zostaje czerń
    return image(0, 0, 450, 450, "bg_sport", extra='<Variant mode="AMBIENT" target="alpha" value="0"/>')


def ticks():
    d = []
    for k in range(60):
        a = k * 6
        if k % 15 == 0:
            d.append(line(a, 204, 220, ORANGE, 4.0, "ROUND"))
        elif k % 5 == 0:
            d.append(line(a, 206, 220, ACCENT, 3.4, "ROUND"))
        else:
            d.append(line(a, 213, 220, ACCENT, 1.6, "ROUND"))
    return '<PartDraw x="0" y="0" width="450" height="450">' + "".join(d) + "</PartDraw>"


# ------------------------------------------------------------------ góra: data, godzina, puls

def top():
    date = text(120, 52, 210, 24, "%s %s", 19, ACCENT, params=("[DAY_OF_WEEK_S]", "[DAY]"))
    clock = (
        '<DigitalClock x="100" y="72" width="250" height="70">'
        '<TimeText format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER" x="0" y="0" width="250" height="70">'
        f'<Font family="SYNC_TO_DEVICE" size="64" weight="BOLD" color="{WHITE}"/></TimeText></DigitalClock>'
    )
    heart = (image(196, 141, 14, 14, "ic_heart", RED)
             + text(213, 136, 50, 22, "%s", 16, LIGHT, align="START", params=("round([HEART_RATE])",)))
    return date + clock + heart


# ------------------------------------------------------------------ lewe koło: pole z łukiem

def left_slot():
    d = 124  # pole 124x124 wokół (108, 226)
    x, y = 108 - d // 2, 226 - d // 2
    icon = image(48, 20, 28, 28, "[COMPLICATION.MONOCHROMATIC_IMAGE]", ACCENT)
    value = text(6, 46, d - 12, 36, "%s", 30, WHITE, params=("[COMPLICATION.TEXT]",))
    title = text(10, 82, d - 20, 20, "%s", 15, GREY, weight="NORMAL", params=("[COMPLICATION.TITLE]",))
    arc = (
        f'<PartDraw x="0" y="0" width="{d}" height="{d}">'
        f'<Arc centerX="{d // 2}" centerY="{d // 2}" width="{d - 14}" height="{d - 14}" startAngle="0" endAngle="360">'
        f'<Stroke color="{TRACK}" thickness="7"/></Arc>'
        f'<Arc centerX="{d // 2}" centerY="{d // 2}" width="{d - 14}" height="{d - 14}" startAngle="0" endAngle="0">'
        f'<Stroke color="{ACCENT}" thickness="7" cap="ROUND"/>'
        '<Transform target="endAngle" value="([COMPLICATION.RANGED_VALUE_VALUE] - [COMPLICATION.RANGED_VALUE_MIN])'
        ' / ([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN]) * 360"/></Arc></PartDraw>'
    )
    return slot(
        3, "slot_left", x, y, d, d, ["RANGED_VALUE", "SHORT_TEXT", "MONOCHROMATIC_IMAGE"],
        f'<BoundingOval x="0" y="0" width="{d}" height="{d}"/>',
        {
            "RANGED_VALUE": arc + icon + value + title,
            "SHORT_TEXT": icon + value + title,
            "MONOCHROMATIC_IMAGE": image(37, 37, 50, 50, "[COMPLICATION.MONOCHROMATIC_IMAGE]", ACCENT),
        },
        default=("WATCH_BATTERY", "RANGED_VALUE"),
    )


# ------------------------------------------------------------------ prawe koło: pogoda

def weather():
    cx, cy = 342, 226
    ring = (f'<PartDraw x="0" y="0" width="450" height="450">'
            f'<Arc centerX="{cx}" centerY="{cy}" width="110" height="110" startAngle="200" endAngle="340">'
            f'<Stroke color="{ORANGE}" thickness="5" cap="ROUND"/></Arc>'
            f'<Arc centerX="{cx}" centerY="{cy}" width="110" height="110" startAngle="20" endAngle="160">'
            f'<Stroke color="{ACCENT}" thickness="5" cap="ROUND"/></Arc></PartDraw>')
    ok = text(cx - 52, cy - 22, 104, 40, "%s°", 34, WHITE, params=("[WEATHER.TEMPERATURE]",))
    na = text(cx - 52, cy - 22, 104, 40, "--°", 34, WHITE)
    label = text(cx - 40, cy + 18, 80, 20, "POGODA", 13, GREY, weight="NORMAL")
    return (ring + "<Condition><Expressions>"
            '<Expression name="weather"><![CDATA[[WEATHER.IS_AVAILABLE]]]></Expression></Expressions>'
            f'<Compare expression="weather">{ok}</Compare><Default>{na}</Default></Condition>' + label)


# ------------------------------------------------------------------ dół: glukoza, delta, wykres

def glucose_slot():
    # 270x66: wartość wyrównana do prawej, zaraz za nią duża zielona strzałka trendu
    body = (text(0, 0, 176, 66, "%s", 64, WHITE, align="END", params=("[COMPLICATION.TEXT]",))
            + image(182, 10, 46, 46, "[COMPLICATION.MONOCHROMATIC_IMAGE]", GREEN)
            + text(230, 22, 40, 20, "%s", 13, GREY, weight="NORMAL", align="START", params=("[COMPLICATION.TITLE]",)))
    return slot(0, "slot_glucose", 90, 300, 270, 66, ["SHORT_TEXT", "RANGED_VALUE"],
                '<BoundingBox x="0" y="0" width="270" height="66"/>',
                {"SHORT_TEXT": body, "RANGED_VALUE": body})


def unit_and_delta():
    unit = text(120, 364, 104, 20, "mg/dL", 15, GREY, weight="NORMAL", align="END")
    body = text(0, 0, 110, 20, "%s %s", 15, LIGHT, align="START", params=("[COMPLICATION.TEXT]", "[COMPLICATION.TITLE]"))
    delta = slot(1, "slot_delta", 232, 364, 110, 20, ["SHORT_TEXT"],
                 '<BoundingBox x="0" y="0" width="110" height="20"/>', {"SHORT_TEXT": body})
    return unit + delta


def graph_slot():
    w, h = 176, 42
    def b(res):
        return (f'<PartDraw x="0" y="0" width="{w}" height="{h}">'
                f'<RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="8" cornerRadiusY="8">'
                f'<Fill color="#FF262F36"/></RoundRectangle></PartDraw>'
                + image(2, 2, w - 4, h - 4, res))
    return slot(2, "slot_graph", 137, 388, w, h, ["PHOTO_IMAGE", "SMALL_IMAGE"],
                f'<BoundingRoundBox x="0" y="0" width="{w}" height="{h}" cornerRadius="8"/>',
                {"PHOTO_IMAGE": b("[COMPLICATION.PHOTO_IMAGE]"), "SMALL_IMAGE": b("[COMPLICATION.SMALL_IMAGE]")})


# ------------------------------------------------------------------ wskazówki

def hands():
    # rozmiary i punkty obrotu z tools/make_assets_v3.py
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<HourHand resource="hand_hour_o" x="{C - 14}" y="{C - 118}" width="28" height="138" pivotX="0.5" pivotY="0.8551"/>'
        f'<MinuteHand resource="hand_minute_o" x="{C - 13}" y="{C - 184}" width="26" height="206" pivotX="0.5" pivotY="0.8932"/>'
        "</AnalogClock>"
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<SecondHand resource="hand_second_o" x="{C - 4}" y="{C - 196}" width="8" height="232" pivotX="0.5" pivotY="0.8448" tintColor="{HAND}">'
        '<Sweep frequency="15"/></SecondHand>'
        '<Variant mode="AMBIENT" target="alpha" value="0"/></AnalogClock>'
        '<PartDraw x="0" y="0" width="450" height="450">'
        f'<Ellipse x="{C - 12}" y="{C - 12}" width="24" height="24"><Fill color="#FFB4BAC0"/></Ellipse>'
        f'<Ellipse x="{C - 8}" y="{C - 8}" width="16" height="16"><Fill color="{HAND}"/></Ellipse>'
        f'<Ellipse x="{C - 3}" y="{C - 3}" width="6" height="6"><Fill color="#FF3A0C0C"/></Ellipse>'
        "</PartDraw>"
    )


def user_configurations():
    opts = "".join(f'<ColorOption id="{k}" displayName="@string/{n}" colors="{a} {h}"/>' for k, (n, a, h) in enumerate(THEMES))
    return f'<UserConfigurations><ColorConfiguration id="theme" displayName="@string/cfg_theme" defaultValue="0">{opts}</ColorConfiguration></UserConfigurations>'


def build():
    body = (background() + ticks() + top() + left_slot() + weather()
            + glucose_slot() + unit_and_delta() + graph_slot() + hands())
    return ('<?xml version="1.0" encoding="utf-8"?>\n<WatchFace width="450" height="450">\n'
            '<Metadata key="CLOCK_TYPE" value="ANALOG"/>\n<Metadata key="PREVIEW_TIME" value="10:09:22"/>\n'
            f"{user_configurations()}\n<Scene backgroundColor=\"#FF000000\">\n{body}\n</Scene>\n</WatchFace>\n")


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("Zapisano", OUT, OUT.stat().st_size, "B")
