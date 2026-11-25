package com.glucosechrono.chime;

import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import java.util.Calendar;

/** Budzik o pełnej godzinie: ustawia następny i gra sygnał. */
public class ChimeReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Context c = context.getApplicationContext();
        Scheduler.schedule(c);
        if (!Prefs.enabled(c)) return;
        String why = quietReason(c);
        if (why != null) {
            Prefs.log(c, "pominięty: " + why);
            return;
        }
        PendingResult pending = goAsync();
        new Thread(() -> {
            try {
                Beeper.play(c, Prefs.doubleBeep(c), Prefs.volume(c), Prefs.vibrate(c));
                android.media.AudioManager am = c.getSystemService(android.media.AudioManager.class);
                boolean mute = am != null && am.getStreamVolume(android.media.AudioManager.STREAM_ALARM) == 0;
                Prefs.log(c, mute ? "zagrał, ale głośność alarmów zegarka jest na zero" : "zagrał");
            } catch (RuntimeException e) {
                Prefs.log(c, "błąd dźwięku: " + e.getClass().getSimpleName());
            } finally {
                pending.finish();
            }
        }).start();
    }

    /** Powód ciszy albo null, gdy sygnał ma zagrać. */
    static String quietReason(Context c) {
        Calendar now = Calendar.getInstance();
        int min = now.get(Calendar.MINUTE);
        // Budzik spóźniony o więcej niż 5 minut (np. po restarcie) nie gra o złej porze.
        if (min >= 5 && min < 58) return "spóźniony budzik (" + min + " min po pełnej godzinie)";
        int hour = now.get(Calendar.HOUR_OF_DAY);
        if (min >= 58) hour = (hour + 1) % 24;
        if (Prefs.isNightHour(c, hour)) return "cisza nocna";
        if (Prefs.respectDnd(c)) {
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            int f = nm.getCurrentInterruptionFilter();
            if (f != NotificationManager.INTERRUPTION_FILTER_ALL
                    && f != NotificationManager.INTERRUPTION_FILTER_UNKNOWN) return "tryb Nie przeszkadzać";
        }
        return null;
    }
}
