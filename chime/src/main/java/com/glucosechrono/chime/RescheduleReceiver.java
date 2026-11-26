package com.glucosechrono.chime;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Po restarcie, aktualizacji lub zmianie czasu ustawia sygnał na nowo. */
public class RescheduleReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Context c = context.getApplicationContext();
        String a = String.valueOf(intent.getAction());
        String why = a.endsWith("BOOT_COMPLETED") ? "restart zegarka"
                : a.endsWith("MY_PACKAGE_REPLACED") ? "aktualizacja aplikacji"
                : a.endsWith("TIME_SET") || a.endsWith("TIMEZONE_CHANGED") ? "zmiana czasu" : "zmiana uprawnień";
        Prefs.log(c, "ustawiony ponownie (" + why + ")");
        Scheduler.schedule(c);
        KeepAliveService.start(c);
    }
}
