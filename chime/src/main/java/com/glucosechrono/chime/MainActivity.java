package com.glucosechrono.chime;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
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
    private Button exactButton;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        build();
        Scheduler.schedule(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        refreshExact();
        Scheduler.schedule(this);
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

        TextView title = new TextView(this);
        title.setText(R.string.app_name);
        title.setTextSize(16);
        title.setTextColor(Color.WHITE);
        title.setGravity(Gravity.CENTER);
        list.addView(title);

        toggle("Włączony", Prefs.ENABLED, Prefs.enabled(this));
        cycle(new String[]{"Pojedynczy: piik", "Podwójny: piik-piik"}, Prefs.doubleBeep(this) ? 1 : 0,
                i -> Prefs.get(this).edit().putBoolean(Prefs.DOUBLE, i == 1).apply());
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
        exactButton = button("Zezwól na dokładny czas");
        exactButton.setOnClickListener(v -> {
            try {
                startActivity(new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM,
                        Uri.parse("package:" + getPackageName())));
            } catch (ActivityNotFoundException e) {
                startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                        Uri.parse("package:" + getPackageName())));
            }
        });
        list.addView(exactButton);
    }

    private void refreshExact() {
        boolean ok = Scheduler.canExact(this);
        exactInfo.setText(ok ? "Sygnał co do sekundy o pełnej godzinie."
                : "Bez tej zgody sygnał może się spóźniać o 1–2 minuty.");
        exactButton.setVisibility(ok ? View.GONE : View.VISIBLE);
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
