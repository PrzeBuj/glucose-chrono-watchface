package com.glucosechrono.chime;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Po restarcie, aktualizacji lub zmianie czasu ustawia sygnał na nowo. */
public class RescheduleReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        Scheduler.schedule(context.getApplicationContext());
    }
}
