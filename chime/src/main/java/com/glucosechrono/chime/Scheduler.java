package com.glucosechrono.chime;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;

import java.util.Calendar;

/** Ustawia budzik systemowy na najbliższą pełną godzinę. */
final class Scheduler {
    private Scheduler() {}

    private static PendingIntent intent(Context c) {
        Intent i = new Intent(c, ChimeReceiver.class).setAction("com.glucosechrono.chime.HOUR");
        return PendingIntent.getBroadcast(c, 0, i,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static long nextFullHour() {
        Calendar cal = Calendar.getInstance();
        cal.set(Calendar.MINUTE, 0);
        cal.set(Calendar.SECOND, 0);
        cal.set(Calendar.MILLISECOND, 0);
        cal.add(Calendar.HOUR_OF_DAY, 1);
        return cal.getTimeInMillis();
    }

    static boolean canExact(Context c) {
        AlarmManager am = c.getSystemService(AlarmManager.class);
        return android.os.Build.VERSION.SDK_INT < 31 || am.canScheduleExactAlarms();
    }

    static void schedule(Context c) {
        AlarmManager am = c.getSystemService(AlarmManager.class);
        PendingIntent pi = intent(c);
        am.cancel(pi);
        if (!Prefs.enabled(c)) return;
        long at = nextFullHour();
        if (canExact(c)) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pi);
        } else {
            // Bez zgody na dokładne budziki system może opóźnić sygnał o kilka minut.
            am.setWindow(AlarmManager.RTC_WAKEUP, at, 60_000, pi);
        }
    }
}
