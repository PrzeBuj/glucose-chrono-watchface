package com.glucosechrono.chime;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.util.TypedValue;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;

import java.util.function.Consumer;

/** Jeden ekran ustawień, dopasowany do okrągłej tarczy. */
public class MainActivity extends Activity {
    private LinearLayout list;
    private TextView exactInfo;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        build();
        Scheduler.schedule(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        Scheduler.schedule(this);
        refreshExact();
    }

    private int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    private void build() {
        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.BLACK);
        list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setGravity(Gravity.CENTER_HORIZONTAL);
        int side = (int) (getResources().getDisplayMetrics().widthPixels * 0.12);
        list.setPadding(side, dp(28), side, dp(40));
        scroll.addView(list);
        setContentView(scroll);
        // pokrętło zegarka przewija listę
        scroll.setFocusableInTouchMode(true);
        scroll.requestFocus();

        TextView title = new TextView(this);
        title.setText(R.string.app_name);
        title.setTextSize(16);
        title.setTextColor(Color.WHITE);
        title.setGravity(Gravity.CENTER);
        list.addView(title);

        toggle("Włączony", Prefs.ENABLED, Prefs.enabled(this));
        cycle(new String[]{"Pojedynczy: piik", "Podwójny: piik-piik"}, Prefs.doubleBeep(this) ? 1 : 0,
                i -> Prefs.get(this).edit().putBoolean(Prefs.DOUBLE, i == 1).apply());
        cycle(new String[]{"Ton: cyfrowy", "Ton: niski", "Ton: dzwonek", "Ton: elektroniczny"}, Prefs.tone(this),
                i -> {
                    Prefs.get(this).edit().putInt(Prefs.TONE, i).apply();
                    new Thread(() -> Beeper.play(this, Prefs.doubleBeep(this), Prefs.volume(this), false, i)).start();
                });
        cycle(new String[]{"Głośność: cicho", "Głośność: średnio", "Głośność: głośno"}, Prefs.volume(this),
                i -> Prefs.get(this).edit().putInt(Prefs.VOLUME, i).apply());
        toggle("Też wibracja", Prefs.VIBRATE, Prefs.vibrate(this));
        toggle("Cisza nocna", Prefs.NIGHT, Prefs.night(this));
        cycle(hours("Od "), Prefs.nightFrom(this),
                i -> Prefs.get(this).edit().putInt(Prefs.NIGHT_FROM, i).apply());
        cycle(hours("Do "), Prefs.nightTo(this),
                i -> Prefs.get(this).edit().putInt(Prefs.NIGHT_TO, i).apply());
        toggle("Cisza w trybie Nie przeszkadzać", Prefs.RESPECT_DND, Prefs.respectDnd(this));

        Button test = button("▶ Odtwórz teraz");
        test.setOnClickListener(v -> new Thread(() ->
                Beeper.play(this, Prefs.doubleBeep(this), Prefs.volume(this), Prefs.vibrate(this))).start());
        list.addView(test);

        exactInfo = new TextView(this);
        exactInfo.setTextSize(12);
        exactInfo.setTextColor(0xFF9AA1AA);
        exactInfo.setGravity(Gravity.CENTER);
        exactInfo.setPadding(0, dp(10), 0, 0);
        list.addView(exactInfo);
    }

    private void refreshExact() {
        StringBuilder sb = new StringBuilder();
        long next = Prefs.get(this).getLong(Prefs.NEXT, 0);
        sb.append(next > 0 ? "Następny sygnał: " + new java.text.SimpleDateFormat("HH:mm", java.util.Locale.ROOT)
                .format(new java.util.Date(next)) : "Sygnał wyłączony");
        sb.append("\nOstatnio: ").append(Prefs.get(this).getString(Prefs.LAST, "jeszcze nie było"));
        android.media.AudioManager am = getSystemService(android.media.AudioManager.class);
        if (am != null && am.getStreamVolume(android.media.AudioManager.STREAM_ALARM) == 0)
            sb.append("\nGłośność alarmów zegarka jest na zero, sygnał nie będzie słyszalny.");
        if (!Scheduler.canExact(this)) sb.append("\nSystem nie pozwala na dokładny budzik, sygnał może się spóźniać.");
        exactInfo.setText(sb.toString());
    }

    private static String[] hours(String prefix) {
        String[] out = new String[24];
        for (int i = 0; i < 24; i++) out[i] = prefix + i + ":00";
        return out;
    }

    private Button button(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setAllCaps(false);
        b.setTextSize(14);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(6);
        b.setLayoutParams(lp);
        return b;
    }

    private void toggle(String label, String key, boolean value) {
        Switch s = new Switch(this);
        s.setText(label);
        s.setTextSize(14);
        s.setTextColor(Color.WHITE);
        s.setChecked(value);
        s.setPadding(dp(4), dp(10), dp(4), dp(10));
        s.setOnCheckedChangeListener((b, checked) -> {
            Prefs.get(this).edit().putBoolean(key, checked).apply();
            Scheduler.schedule(this);
            refreshExact();
        });
        list.addView(s, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT));
    }

    /** Przycisk, który po każdym dotknięciu przechodzi do następnej wartości. */
    private void cycle(String[] labels, int start, Consumer<Integer> save) {
        Button b = button(labels[start]);
        final int[] idx = {start};
        b.setOnClickListener(v -> {
            idx[0] = (idx[0] + 1) % labels.length;
            b.setText(labels[idx[0]]);
            save.accept(idx[0]);
        });
        list.addView(b);
    }
}
