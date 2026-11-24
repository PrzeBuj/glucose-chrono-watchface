#!/bin/bash
# Instaluje kolejne warianty tarczy na emulatorze Wear OS, próbuje je ustawić, zapisuje wynik, zrzut i logi.
PKG=com.glucosechrono.watchface
mkdir -p shots
adb wait-for-device
adb shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
sleep 60
for apk in apks/*.apk; do
  n=$(basename $apk .apk)
  adb logcat -c
  adb uninstall $PKG >/dev/null 2>&1
  adb install -r "$apk"
  sleep 25
  RES=FAIL
  for i in 1 2 3; do
    OUT=$(adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId "$PKG")
    if echo "$OUT" | grep -q "failed"; then sleep 10; else RES=OK; break; fi
  done
  echo "RESULT $n: $RES"
  echo "$n: $RES" >> shots/results.txt
  sleep 15
  adb exec-out screencap -p > shots/$n.png
  adb logcat -d > shots/$n.log
  grep -E "DWF|FavoriteOperation|DebugSurface|AndroidRuntime" shots/$n.log | grep -vE "bounds|supported types|s\.a@|####" | tail -25
done
cat shots/results.txt
exit 0
