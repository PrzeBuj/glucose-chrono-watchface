"""Generuje watchface/src/main/res/raw/watchface.xml (Watch Face Format v2): jedna tarcza, trzy style.

Style (Edytuj › Styl): Sport, Chronograf, Klasyczny. Pola z GlucoDataHandler są wspólne dla wszystkich stylów
(te same miejsca), każdy styl ma własne tło, dodatki i wskazówki.

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
    # 210x64: wartość wyrównana do prawej, zaraz za nią duża zielona strzałka trendu
    body = (text(0, 0, 166, 64, "%s", 62, WHITE, align="END", params=("[COMPLICATION.TEXT]",))
            + image(170, 9, 44, 44, "[COMPLICATION.MONOCHROMATIC_IMAGE]", GREEN))
    return slot(0, "slot_glucose", 70, 294, 214, 64, ["SHORT_TEXT", "RANGED_VALUE"],
                '<BoundingBox x="0" y="0" width="214" height="64"/>',
                {"SHORT_TEXT": body, "RANGED_VALUE": body})


def unit_and_delta():
    # kolumna po prawej od strzałki: jednostka, pod nią delta i czas
    unit = text(288, 306, 70, 18, "mg/dL", 14, GREY, weight="NORMAL", align="START")
    delta = slot(1, "slot_delta", 288, 324, 76, 20, ["SHORT_TEXT"],
                 '<BoundingBox x="0" y="0" width="76" height="20"/>',
                 {"SHORT_TEXT": text(0, 0, 76, 20, "%s %s", 13, LIGHT, align="START", params=("[COMPLICATION.TEXT]", "[COMPLICATION.TITLE]"))})
    return unit + delta


def graph_slot():
    w, h = 156, 44
    def b(res):
        return (f'<PartDraw x="0" y="0" width="{w}" height="{h}">'
                f'<RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="8" cornerRadiusY="8">'
                f'<Fill color="#FF262F36"/></RoundRectangle></PartDraw>'
                + image(2, 2, w - 4, h - 4, res))
    return slot(2, "slot_graph", 147, 362, w, h, ["PHOTO_IMAGE", "SMALL_IMAGE"],
                f'<BoundingRoundBox x="0" y="0" width="{w}" height="{h}" cornerRadius="8"/>',
                {"PHOTO_IMAGE": b("[COMPLICATION.PHOTO_IMAGE]"), "SMALL_IMAGE": b("[COMPLICATION.SMALL_IMAGE]")})


# ------------------------------------------------------------------ wskazówki

def sport_hands():
    # rozmiary i punkty obrotu z tools/make_assets_v3.py
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<HourHand resource="hand_hour_o" x="{C - 14}" y="{C - 118}" width="28" height="138" pivotX="0.5" pivotY="0.8551"/>'
        f'<MinuteHand resource="hand_minute_o" x="{C - 13}" y="{C - 184}" width="26" height="206" pivotX="0.5" pivotY="0.8932"/>'
        "</AnalogClock>"
        + second_hand()
        + '<PartDraw x="0" y="0" width="450" height="450">'
        f'<Ellipse x="{C - 12}" y="{C - 12}" width="24" height="24"><Fill color="#FFB4BAC0"/></Ellipse>'
        f'<Ellipse x="{C - 8}" y="{C - 8}" width="16" height="16"><Fill color="{HAND}"/></Ellipse>'
        f'<Ellipse x="{C - 3}" y="{C - 3}" width="6" height="6"><Fill color="#FF3A0C0C"/></Ellipse>'
        "</PartDraw>"
    )


def second_hand():
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<SecondHand resource="hand_second_o" x="{C - 4}" y="{C - 196}" width="8" height="232" pivotX="0.5" pivotY="0.8448" tintColor="{HAND}">'
        '<Sweep frequency="15"/></SecondHand>'
        '<Variant mode="AMBIENT" target="alpha" value="0"/></AnalogClock>'
    )


def group(name, inner):
    return f'<Group name="{name}" x="0" y="0" width="450" height="450">{inner}</Group>'


# ------------------------------------------------------------------ styl: Sport

def sport_back():
    return background() + ticks() + top() + weather()


# ------------------------------------------------------------------ styl: Chronograf (poprzedni wygląd)

SUB = "#FF1A1D22"
TICK = "#FF7D838C"
DIAL = "[CONFIGURATION.dial.0]"
DIALS = [("dial_graphite", "#FF101215"), ("dial_black", "#FF000000"), ("dial_navy", "#FF0E1A2E"), ("dial_green", "#FF0F1E17")]
WID = ((108, 226), (342, 226))


def chrono_back():
    gears = (
        '<Group name="gears" x="0" y="0" width="450" height="450">'
        '<PartImage x="78" y="78" width="294" height="294" pivotX="0.5" pivotY="0.5"><Image resource="gear_big"/>'
        '<Transform target="angle" value="([SECONDS_IN_DAY] % 60) * 6"/></PartImage>'
        + "".join(
            f'<PartImage x="{cx - 64}" y="{cy - 64}" width="128" height="128" pivotX="0.5" pivotY="0.5"><Image resource="gear_small"/>'
            '<Transform target="angle" value="360 - ([SECONDS_IN_DAY] % 26) * 13.846"/></PartImage>' for cx, cy in WID)
        + '<Variant mode="AMBIENT" target="alpha" value="0"/></Group>'
    )
    d = [f'<Rectangle x="0" y="0" width="450" height="450"><Fill color="{DIAL}"/></Rectangle>']
    draw = [f'<Arc centerX="{C}" centerY="{C}" width="429" height="429" startAngle="0" endAngle="360"><Stroke color="{BLACK}" thickness="21"/></Arc>']
    for k in range(300):
        draw.append(line(k * 1.2, 216, 223, TICK, 0.8))
    for k in range(60):
        draw.append(line(k * 6, 213, 223, WHITE, 1.5))
    for a in (30, 60, 120, 240, 300, 330):
        draw.append(line(a, 159, 181, WHITE, 6, "ROUND"))
    for dx in (-7, 7):
        draw.append(f'<Line startX="{C + dx}" startY="39" endX="{C + dx}" endY="60"><Stroke color="{WHITE}" thickness="7.7" cap="ROUND"/></Line>')
    for cx, cy in WID:
        draw.append(f'<Ellipse x="{cx - 60}" y="{cy - 60}" width="120" height="120"><Fill color="{SUB}"/><Stroke color="{WHITE}" thickness="2.4"/></Ellipse>')
    draw.append(f'<RoundRectangle x="155" y="64" width="141" height="54" cornerRadiusX="10" cornerRadiusY="10"><Fill color="{BLACK}"/><Stroke color="{WHITE}" thickness="1.9"/></RoundRectangle>')
    # prawa tarczka: bateria zegarka (pole po lewej to komplikacja)
    cx, cy = WID[1]
    draw.append(f'<Arc centerX="{cx}" centerY="{cy}" width="110" height="110" startAngle="0" endAngle="360"><Stroke color="{TRACK}" thickness="7"/></Arc>')
    draw.append(f'<Arc centerX="{cx}" centerY="{cy}" width="110" height="110" startAngle="0" endAngle="0"><Stroke color="{ACCENT}" thickness="7" cap="ROUND"/>'
                '<Transform target="endAngle" value="[BATTERY_PERCENT] * 3.6"/></Arc>')
    out = ('<PartDraw x="0" y="0" width="450" height="450">' + "".join(d) + "</PartDraw>" + gears
           + '<PartDraw x="0" y="0" width="450" height="450">' + "".join(draw) + "</PartDraw>")
    for n in (5, 10, 15, 20, 40, 45, 50, 55):
        x, y = polar(n * 6, 190)
        out += text(x - 15, y - 11, 30, 22, f"{n:02d}", 14, WHITE)
    out += text(cx - 50, cy - 22, 100, 36, "%s%%", 28, WHITE, params=("[BATTERY_PERCENT]",))
    out += text(cx - 40, cy + 14, 80, 20, "BAT", 13, GREY, weight="NORMAL")
    out += ('<DigitalClock x="155" y="66" width="141" height="50">'
            '<TimeText format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER" x="0" y="0" width="141" height="50">'
            f'<Font family="SYNC_TO_DEVICE" size="40" weight="BOLD" color="{WHITE}"/></TimeText></DigitalClock>')
    temp_ok = text(130, 124, 80, 22, "%s°", 16, LIGHT, align="END", params=("[WEATHER.TEMPERATURE]",))
    temp_na = text(130, 124, 80, 22, "--°", 16, LIGHT, align="END")
    out += ("<Condition><Expressions><Expression name=\"weather\"><![CDATA[[WEATHER.IS_AVAILABLE]]]></Expression></Expressions>"
            f'<Compare expression="weather">{temp_ok}</Compare><Default>{temp_na}</Default></Condition>')
    out += image(226, 129, 14, 14, "ic_heart", HAND) + text(243, 124, 60, 22, "%s", 16, LIGHT, align="START", params=("round([HEART_RATE])",))
    return out


def chrono_hands():
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        '<HourHand resource="hand_hour" x="219" y="124" width="12" height="118" pivotX="0.5" pivotY="0.8559"/>'
        '<MinuteHand resource="hand_minute" x="220" y="46" width="10" height="201" pivotX="0.5" pivotY="0.8905"/>'
        "</AnalogClock>"
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<SecondHand resource="hand_second" x="220" y="29" width="10" height="249" pivotX="0.5" pivotY="0.7871" tintColor="{HAND}">'
        '<Sweep frequency="15"/></SecondHand><Variant mode="AMBIENT" target="alpha" value="0"/></AnalogClock>'
        f'<PartDraw x="0" y="0" width="450" height="450"><Ellipse x="{C - 7}" y="{C - 7}" width="15" height="15"><Fill color="{HAND}"/></Ellipse>'
        f'<Ellipse x="{C - 3}" y="{C - 3}" width="6" height="6"><Fill color="{BLACK}"/></Ellipse></PartDraw>'
    )


# ------------------------------------------------------------------ styl: Klasyczny (włókno węglowe, metal, luma)

def classic_back():
    out = image(0, 0, 450, 450, "bg_classic", extra='<Variant mode="AMBIENT" target="alpha" value="0"/>')
    out += image(184, 72, 18, 14, "ic_battery", LIGHT) + text(205, 68, 60, 22, "%s%%", 15, LIGHT, align="START", params=("[BATTERY_PERCENT]",))
    out += text(140, 88, 170, 22, "%s %s", 17, LIGHT, weight="NORMAL", params=("[DAY_OF_WEEK_S]", "[DAY]"))
    out += ('<DigitalClock x="110" y="106" width="230" height="58">'
            '<TimeText format="hh:mm" hourFormat="SYNC_TO_DEVICE" align="CENTER" x="0" y="0" width="230" height="58">'
            f'<Font family="SYNC_TO_DEVICE" size="54" weight="NORMAL" color="{WHITE}"/></TimeText></DigitalClock>')
    cx, cy = WID[1]
    ok = text(cx - 52, cy - 18, 104, 38, "%s°C", 28, WHITE, weight="NORMAL", params=("[WEATHER.TEMPERATURE]",))
    na = text(cx - 52, cy - 18, 104, 38, "--°C", 28, WHITE, weight="NORMAL")
    out += ("<Condition><Expressions><Expression name=\"weather\"><![CDATA[[WEATHER.IS_AVAILABLE]]]></Expression></Expressions>"
            f'<Compare expression="weather">{ok}</Compare><Default>{na}</Default></Condition>')
    out += text(cx - 40, cy - 40, 80, 20, "POGODA", 12, GREY, weight="NORMAL")
    return out


def classic_hands():
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        f'<HourHand resource="hand_hour_c" x="{C - 7}" y="{C - 108}" width="14" height="126" pivotX="0.5" pivotY="0.8571"/>'
        f'<MinuteHand resource="hand_minute_c" x="{C - 6}" y="{C - 168}" width="12" height="188" pivotX="0.5" pivotY="0.8936"/>'
        "</AnalogClock>"
        + second_hand()
        + '<PartDraw x="0" y="0" width="450" height="450">'
        f'<Ellipse x="{C - 9}" y="{C - 9}" width="18" height="18"><Fill color="#FFC8CDD2"/></Ellipse>'
        f'<Ellipse x="{C - 5}" y="{C - 5}" width="10" height="10"><Fill color="{HAND}"/></Ellipse>'
        "</PartDraw>"
    )


STYLES = [("sport", "style_sport", sport_back, sport_hands),
          ("chrono", "style_chrono", chrono_back, chrono_hands),
          ("classic", "style_classic", classic_back, classic_hands)]


def by_style():
    # Jedna lista stylów (tło i wskazówki razem): dwie listy o tym samym id nie odświeżały się na zegarku po zmianie stylu.
    opts = "".join(f'<ListOption id="{sid}">{group(sid, back() + hands())}</ListOption>' for sid, _, back, hands in STYLES)
    return f'<ListConfiguration id="style">{opts}</ListConfiguration>'


def user_configurations():
    styles = "".join(f'<ListOption id="{sid}" displayName="@string/{name}" icon="{"style_" + sid}"/>' for sid, name, _, _ in STYLES)
    opts = "".join(f'<ColorOption id="{k}" displayName="@string/{n}" colors="{a} {h}"/>' for k, (n, a, h) in enumerate(THEMES))
    dials = "".join(f'<ColorOption id="{k}" displayName="@string/{n}" colors="{c}"/>' for k, (n, c) in enumerate(DIALS))
    return ("<UserConfigurations>"
            f'<ListConfiguration id="style" displayName="@string/cfg_style" defaultValue="sport">{styles}</ListConfiguration>'
            f'<ColorConfiguration id="theme" displayName="@string/cfg_theme" defaultValue="0">{opts}</ColorConfiguration>'
            f'<ColorConfiguration id="dial" displayName="@string/cfg_dial" defaultValue="0">{dials}</ColorConfiguration>'
            "</UserConfigurations>")


def build():
    # pola danych nad wskazówkami: wartości glukozy nie zasłania żadna wskazówka
    body = (by_style() + left_slot() + glucose_slot() + unit_and_delta() + graph_slot())
    return ('<?xml version="1.0" encoding="utf-8"?>\n<WatchFace width="450" height="450">\n'
            '<Metadata key="CLOCK_TYPE" value="ANALOG"/>\n<Metadata key="PREVIEW_TIME" value="10:09:22"/>\n'
            f"{user_configurations()}\n<Scene backgroundColor=\"#FF000000\">\n{body}\n</Scene>\n</WatchFace>\n")


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("Zapisano", OUT, OUT.stat().st_size, "B")
