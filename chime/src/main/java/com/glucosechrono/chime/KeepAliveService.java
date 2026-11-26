package com.glucosechrono.chime;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.IBinder;

/**
 * Usługa na pierwszym planie: utrzymuje proces aplikacji przy życiu, żeby system zegarka
 * (np. OnePlus) nie blokował budzika pełnej godziny. Sama nic nie liczy, procesor śpi do budzika.
 */
public class KeepAliveService extends Service {
    private static final String CHANNEL = "chime_active";
    private static boolean logged;

    static void start(Context c) {
        Intent i = new Intent(c, KeepAliveService.class);
        try {
            if (Prefs.enabled(c)) c.startForegroundService(i);
            else c.stopService(i);
        } catch (RuntimeException e) {
            Prefs.log(c, "nie udało się uruchomić usługi: " + e.getClass().getSimpleName());
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        NotificationManager nm = getSystemService(NotificationManager.class);
        nm.createNotificationChannel(new NotificationChannel(CHANNEL, "Sygnał godzinowy aktywny",
                NotificationManager.IMPORTANCE_MIN));
        PendingIntent open = PendingIntent.getActivity(this, 2, new Intent(this, MainActivity.class),
                PendingIntent.FLAG_IMMUTABLE);
        Notification n = new Notification.Builder(this, CHANNEL)
                .setSmallIcon(R.drawable.ic_launcher)
                .setContentTitle("Sygnał godzinowy")
                .setContentText("Aktywny")
                .setContentIntent(open)
                .setOngoing(true)
                .build();
        startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        if (!logged) {
            logged = true;
            Prefs.log(this, "działa w tle");
        }
        Scheduler.schedule(this);
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
