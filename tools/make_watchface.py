"""Generuje watchface/src/main/res/raw/watchface.xml (Watch Face Format v2).

Uruchom: python3 tools/make_watchface.py
Projekt rysowany jest w układzie 466x466 (jak makieta), a tutaj przeliczany na 450x450.
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
DIAL = "#FF101215"
SUB = "#FF1A1D22"
GREY = "#FF9AA1AA"
TICK = "#FF7D838C"
TRACK = "#FF2E333A"
ACCENT = "#FF4DA3FF"  # kolor zakresu / baterii
HAND = "#FFE5484D"  # czerwony sekundnik


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


def ring(cx, cy, r, color, thickness, extra=""):
    return (
        f'<Arc centerX="{s(cx)}" centerY="{s(cy)}" width="{s(2 * r)}" height="{s(2 * r)}" '
        f'startAngle="0" endAngle="360"><Stroke color="{color}" thickness="{f(thickness)}"/>{extra}</Arc>'
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
        f"<Template>{content}{p}</Template></Font></Text></PartText>"
    )


def dial():
    d = []
    # czarny kołnierz i skale minutowe
    d.append(ring(C, C, 222, BLACK, 22))
    for i in range(300):
        d.append(line(i * 1.2, 224, 231, TICK, 0.8))
    for i in range(60):
        d.append(line(i * 6, 221, 231, WHITE, 1.6))
    # indeksy godzinowe
    for a in (30, 60, 120, 240, 300, 330):
        d.append(line(a, 165, 187, WHITE, 6, cap="ROUND"))
    for dx in (-7, 7):
        d.append(
            f'<Line startX="{s(C + dx)}" startY="{s(40)}" endX="{s(C + dx)}" endY="{s(62)}">'
            f'<Stroke color="{WHITE}" thickness="{f(8)}" cap="ROUND"/></Line>'
        )
    # lewa tarczka (temperatura)
    d.append(disc(128, 212, 46, SUB, WHITE, 2.5))
    for i in range(40):
        d.append(line(i * 9, 35.5, 40.5, "#FF6F7680", 0.9, cx=128, cy=212))
    # prawa tarczka (bateria)
    d.append(disc(338, 212, 46, SUB, WHITE, 2.5))
    d.append(ring(338, 212, 38, TRACK, 5))
    d.append(
        f'<Arc centerX="{s(338)}" centerY="{s(212)}" width="{s(76)}" height="{s(76)}" startAngle="0" endAngle="0">'
        f'<Stroke color="{ACCENT}" thickness="{f(5)}" cap="ROUND"/>'
        f'<Transform target="endAngle" value="[BATTERY_PERCENT] * 3.6"/></Arc>'
    )
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


def heart_rate():
    return (
        f'<PartImage x="{s(190)}" y="{s(135)}" width="{s(15)}" height="{s(15)}">'
        f'<Image resource="ic_heart"/></PartImage>'
        + text(209, 130, 90, 24, "%s BPM", 17, "#FFC3C8CF", align="START", params=("round([HEART_RATE])",))
    )


def temperature():
    value_ok = text(88, 186, 80, 36, "%s°", 32, WHITE, params=("[WEATHER.TEMPERATURE]",))
    value_na = text(88, 186, 80, 36, "--", 32, WHITE)
    label = text(88, 222, 80, 16, "TEMP", 12, GREY)
    return (
        "<Condition><Expressions>"
        '<Expression name="weather"><![CDATA[[WEATHER.IS_AVAILABLE]]]></Expression>'
        "</Expressions>"
        f'<Compare expression="weather">{value_ok}</Compare>'
        f"<Default>{value_na}</Default></Condition>" + label
    )


def battery():
    return text(298, 186, 80, 36, "%s", 32, WHITE, params=("[BATTERY_PERCENT]",)) + text(
        298, 222, 80, 16, "BAT %", 12, GREY
    )


def glucose_parts():
    # współrzędne względem slotu (260x70): wartość z GlucoDataHandler, strzałka trendu jako ikona, mały podpis (np. delta)
    return (
        text(0, 2, 260, 50, "%s", 46, WHITE, params=("[COMPLICATION.TEXT]",))
        + f'<PartImage x="{s(200)}" y="{s(14)}" width="{s(28)}" height="{s(28)}" tintColor="{ACCENT}">'
        f'<Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/></PartImage>'
        + text(0, 50, 260, 18, "%s", 13, GREY, weight="NORMAL", params=("[COMPLICATION.TITLE]",))
    )


def glucose_slot():
    return (
        f'<ComplicationSlot slotId="0" displayName="@string/slot_glucose" '
        f'x="{s(103)}" y="{s(248)}" width="{s(260)}" height="{s(70)}" '
        f'supportedTypes="SHORT_TEXT RANGED_VALUE" isCustomizable="TRUE">'
        f'<DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY"/>'
        f'<BoundingBox x="0" y="0" width="{s(260)}" height="{s(70)}"/>'
        f'<Complication type="SHORT_TEXT">{glucose_parts()}</Complication>'
        f'<Complication type="RANGED_VALUE">{glucose_parts()}</Complication>'
        f"</ComplicationSlot>"
    )


def graph_slot():
    w, h = 180, 62
    frame = (
        f'<PartDraw x="0" y="0" width="{s(w)}" height="{s(h)}">'
        f'<RoundRectangle x="0" y="0" width="{s(w)}" height="{s(h)}" cornerRadiusX="{s(10)}" cornerRadiusY="{s(10)}">'
        f'<Fill color="{BLACK}"/><Stroke color="#FF3A3F46" thickness="{f(1.5)}"/></RoundRectangle></PartDraw>'
    )

    def img(expr):
        return (
            f'<PartImage x="{s(3)}" y="{s(3)}" width="{s(w - 6)}" height="{s(h - 6)}">'
            f'<Image resource="{expr}"/></PartImage>'
        )

    return (
        f'<ComplicationSlot slotId="1" displayName="@string/slot_graph" '
        f'x="{s(143)}" y="{s(320)}" width="{s(w)}" height="{s(h)}" '
        f'supportedTypes="PHOTO_IMAGE SMALL_IMAGE" isCustomizable="TRUE">'
        f'<DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY"/>'
        f'<BoundingRoundBox x="0" y="0" width="{s(w)}" height="{s(h)}" cornerRadius="{s(10)}"/>'
        f'<Complication type="PHOTO_IMAGE">{frame}{img("[COMPLICATION.PHOTO_IMAGE]")}</Complication>'
        f'<Complication type="SMALL_IMAGE">{frame}{img("[COMPLICATION.SMALL_IMAGE]")}</Complication>'
        f"</ComplicationSlot>"
    )


def hands():
    # wymiary obrazów w jednostkach 450 (patrz tools/make_assets.py)
    return (
        '<AnalogClock x="0" y="0" width="450" height="450">'
        '<HourHand resource="hand_hour" x="219" y="124" width="12" height="118" pivotX="0.5" pivotY="0.8559"/>'
        '<MinuteHand resource="hand_minute" x="220" y="46" width="10" height="201" pivotX="0.5" pivotY="0.8905"/>'
        "</AnalogClock>"
        '<AnalogClock x="0" y="0" width="450" height="450">'
        '<SecondHand resource="hand_second" x="220" y="29" width="10" height="249" pivotX="0.5" pivotY="0.7871">'
        '<Sweep frequency="15"/></SecondHand>'
        '<Variant mode="AMBIENT" target="alpha" value="0"/>'
        "</AnalogClock>"
        '<PartDraw x="0" y="0" width="450" height="450">'
        f"{disc(C, C, 8, HAND)}{disc(C, C, 3, DIAL)}</PartDraw>"
    )


def build():
    body = (
        dial() + numerals() + digital() + heart_rate() + temperature() + battery()
        + glucose_slot() + graph_slot() + hands()
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<WatchFace width="450" height="450">\n'
        '<Metadata key="CLOCK_TYPE" value="ANALOG"/>\n'
        '<Metadata key="PREVIEW_TIME" value="10:09:22"/>\n'
        f'<Scene backgroundColor="{DIAL}">\n{body}\n</Scene>\n'
        "</WatchFace>\n"
    )


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print("Zapisano", OUT, OUT.stat().st_size, "B")
