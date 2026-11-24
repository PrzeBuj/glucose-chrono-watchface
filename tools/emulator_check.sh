#!/bin/bash
# Instaluje tarczę na emulatorze Wear OS, ustawia ją i zapisuje zrzut ekranu oraz logi.
set -x
APK=glucose-chrono-watchface.apk
PKG=com.glucosechrono.watchface
mkdir -p shots
adb wait-for-device
adb shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
sleep 60
adb logcat -c
adb install -r "$APK"
sleep 30
for i in 1 2 3 4 5; do
  OUT=$(adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId "$PKG")
  echo "$OUT"
  echo "$OUT" | grep -q "failed" || break
  sleep 20
done
sleep 20
adb exec-out screencap -p > shots/face.png
adb shell dumpsys activity services com.google.wear.watchface.runtime > shots/runtime_services.txt 2>&1
adb shell input keyevent KEYCODE_SLEEP
sleep 8
adb exec-out screencap -p > shots/ambient.png
adb logcat -d > shots/logcat.txt
grep -E "DWF|tchface.runtime|DebugSurface|FavoriteOperation|AndroidRuntime" shots/logcat.txt | grep -v nativeloader | tail -200
exit 0
