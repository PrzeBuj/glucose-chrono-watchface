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
Przytrzymaj tarczę → Edytuj → Komplikacje:
- pole **Glukoza** → GlucoDataHandler → wartość glukozy z trendem,
- pole **Wykres glukozy** → GlucoDataHandler → Wykres 3x1.
