"""Warianty watchface.xml do szukania błędu na emulatorze (tools/variants/*.xml)."""
import re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
src = (R / "watchface/src/main/res/raw/watchface.xml").read_text()
out = R / "tools/variants"
out.mkdir(exist_ok=True)
for f in out.glob("*.xml"):
    f.unlink()

def w(name, s):
    (out / f"{name}.xml").write_text(s)

w("a_full", src)

def fix_types(m):
    tag = m.group(0)
    first = re.search(r'supportedTypes="(\S+)', tag).group(1)
    return tag
b = re.sub(r'(<ComplicationSlot [^>]*supportedTypes="([A-Z_]+)[^"]*"[^>]*>\s*)<DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY"/>',
           lambda m: m.group(1) + f'<DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="{m.group(2)}"/>', src)
# w("b_types", b)

# w("c_noslots", re.sub(r'<ComplicationSlot .*?</ComplicationSlot>', '', src, flags=re.S))

d = re.sub(r'<BooleanConfiguration id="gears"><BooleanOption id="TRUE">(.*?)</BooleanOption></BooleanConfiguration>', r'\1', src, flags=re.S)
d = re.sub(r'<BooleanConfiguration [^>]*/>', '', d)
# w("d_noboolcfg", d)

e = re.sub(r'<UserConfigurations>.*?</UserConfigurations>', '', src, flags=re.S)
e = e.replace('[CONFIGURATION.dial.0]', '#FF101215').replace('[CONFIGURATION.theme.0]', '#FF4DA3FF').replace('[CONFIGURATION.theme.1]', '#FFE5484D')
e = re.sub(r'<BooleanConfiguration id="gears"><BooleanOption id="TRUE">(.*?)</BooleanOption></BooleanConfiguration>', r'\1', e, flags=re.S)
# w("e_nouserconfig", e)

m = re.search(r'<AnalogClock .*?</AnalogClock>', src, flags=re.S).group(0)
f = re.sub(r'<Scene ([^>]*)>.*</Scene>', lambda x: f'<Scene {x.group(1)}><PartDraw x="0" y="0" width="450" height="450"><Rectangle x="0" y="0" width="450" height="450"><Fill color="#FF203040"/></Rectangle></PartDraw>{m}</Scene>', e, flags=re.S)
# w("f_minimal", f)
for p in sorted(out.glob("*.xml")):
    print(p.name, len(p.read_text()))
