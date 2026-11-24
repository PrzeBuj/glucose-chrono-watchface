# Chronograf z glukozą (Wear OS)

Tarcza zegarka w Watch Face Format v2 (Wear OS 5+): wskazówki z płynnym sekundnikiem, cyfrowa godzina,
temperatura, bateria zegarka, puls, a na dole poziom cukru ze strzałką trendu i wykres z GlucoDataHandler.

## Skąd biorą się dane
- Cukier: CamAPS FX → GlucoDataHandler (telefon, Notification Reader) → GlucoDataHandler (zegarek) → komplikacje tarczy.
- Temperatura, bateria, puls: wbudowane źródła Wear OS, bez dodatkowych aplikacji.

## Budowanie
Każdy push uruchamia GitHub Actions (`.github/workflows/build.yml`), który buduje APK.
Gotowy plik jest w zakładce **Actions → ostatni build → Artifacts → tarcza-glukoza-apk**.

Grafiki i `watchface.xml` są generowane skryptami:
```
python3 tools/make_assets.py     # wskazówki, ikony
python3 tools/make_watchface.py  # res/raw/watchface.xml
```

## Ustawienie po instalacji
Przytrzymaj tarczę → Edytuj:
- **Kolory**: 5 motywów (akcent + sekundnik), **Tło tarczy**: 4 kolory.
- **Komplikacje** (każdą można zmienić na dowolne dane GlucoDataHandler lub inne):
  - Glukoza → GlucoDataHandler „Glukoza i trend”,
  - Delta i czas odczytu → „Delta i znacznik czasu”,
  - Wykres glukozy → „Wykres 3x1”,
  - Lewa tarczka → „IOB/COB”,
  - Prawa tarczka → „Poziom baterii telefonu” (domyślnie bateria zegarka),
  - Pole pod wykresem → „Czas działania sensora”.

Temperatura, bateria zegarka i puls (rząd pod godziną) pochodzą z Wear OS.
