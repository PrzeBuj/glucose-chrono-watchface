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
        if (!Prefs.enabled(c) || shouldStayQuiet(c)) return;
        PendingResult pending = goAsync();
        new Thread(() -> {
            try {
                Beeper.play(c, Prefs.doubleBeep(c), Prefs.volume(c), Prefs.vibrate(c));
            } finally {
                pending.finish();
            }
        }).start();
    }

    static boolean shouldStayQuiet(Context c) {
        Calendar now = Calendar.getInstance();
        // Budzik spóźniony o więcej niż 2 minuty (np. po restarcie) nie gra o złej porze.
        if (now.get(Calendar.MINUTE) >= 2 && now.get(Calendar.MINUTE) < 58) return true;
        int hour = now.get(Calendar.HOUR_OF_DAY);
        if (now.get(Calendar.MINUTE) >= 58) hour = (hour + 1) % 24;
        if (Prefs.isNightHour(c, hour)) return true;
        if (Prefs.respectDnd(c)) {
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            int f = nm.getCurrentInterruptionFilter();
            if (f != NotificationManager.INTERRUPTION_FILTER_ALL
                    && f != NotificationManager.INTERRUPTION_FILTER_UNKNOWN) return true;
        }
        return false;
    }
}
