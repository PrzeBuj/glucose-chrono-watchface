#!/bin/bash
# Test sygnału godzinowego: instalacja, otwarcie, przestawienie zegara na hh:59:40 i sprawdzenie, czy budzik zagrał.
P=com.glucosechrono.chime
mkdir -p shots
adb wait-for-device
adb shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'
sleep 40
adb root; sleep 5
adb shell settings put global auto_time 0
adb install -r chime.apk
adb shell am start -W -n $P/.MainActivity
sleep 6
adb shell input keyevent KEYCODE_HOME
echo "== ALARM po otwarciu"; adb shell dumpsys alarm | grep -B2 -A6 "$P" | head -30
for round in 1 2; do
  H=$(adb shell date +%H | tr -d '\r'); D=$(adb shell date +%m%d | tr -d '\r'); Y=$(adb shell date +%Y | tr -d '\r')
  adb shell date "$D$H"59"$Y.40"
  echo "== zegar: $(adb shell date)"
  sleep 3
  echo "== ALARM po zmianie czasu"; adb shell dumpsys alarm | grep -A4 "$P" | head -12
  sleep 40
  echo "== zegar po: $(adb shell date)"
  echo "== PREFS ($round)"; adb shell run-as $P cat shared_prefs/chime.xml
done
adb logcat -d > shots/chime.log
grep -E "AndroidRuntime|glucosechrono|AlarmManager.*chime" shots/chime.log | tail -40
exit 0
