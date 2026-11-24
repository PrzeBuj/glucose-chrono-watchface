#!/bin/bash
# Instaluje tarczę na emulatorze Wear OS, ustawia ją i zapisuje zrzut ekranu oraz logi.
set -x
APK=glucose-chrono-watchface.apk
PKG=com.glucosechrono.watchface
mkdir -p shots
adb wait-for-device
adb shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
sleep 20
adb logcat -c
adb install -r "$APK"
sleep 5
adb shell am broadcast -a com.google.android.wearable.app.DEBUG_SURFACE --es operation set-watchface --es watchFaceId "$PKG"
sleep 20
adb exec-out screencap -p > shots/face.png
adb shell input keyevent KEYCODE_SLEEP
sleep 8
adb exec-out screencap -p > shots/ambient.png
adb logcat -d > shots/logcat.txt
grep -iE "wff|watchface|watch face|dwf|runtime|validat|exception|error" shots/logcat.txt | grep -iv "chatty" | tail -150
exit 0
