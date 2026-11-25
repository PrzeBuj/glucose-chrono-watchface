package com.glucosechrono.chime;

import android.content.Context;
import android.content.SharedPreferences;

/** Ustawienia sygnału godzinowego. */
final class Prefs {
    static final String ENABLED = "enabled";
    static final String DOUBLE = "double";
    static final String VOLUME = "volume";       // 0 cicho, 1 średnio, 2 głośno
    static final String TONE = "tone";           // 0 cyfrowy, 1 niski, 2 dzwonek, 3 elektroniczny
    static final String VIBRATE = "vibrate";
    static final String NIGHT = "night";         // cisza nocna
    static final String NIGHT_FROM = "night_from";
    static final String NIGHT_TO = "night_to";
    static final String RESPECT_DND = "respect_dnd";
    static final String LAST = "last";           // ostatnie zdarzenie, np. "11:00 zagrał"
    static final String NEXT = "next";           // czas następnego budzika (ms)

    private Prefs() {}

    static SharedPreferences get(Context c) {
        return c.getSharedPreferences("chime", Context.MODE_PRIVATE);
    }

    static boolean enabled(Context c) { return get(c).getBoolean(ENABLED, true); }
    static boolean doubleBeep(Context c) { return get(c).getBoolean(DOUBLE, true); }
    static int volume(Context c) { return get(c).getInt(VOLUME, 1); }
    static int tone(Context c) { return get(c).getInt(TONE, 0); }
    static boolean vibrate(Context c) { return get(c).getBoolean(VIBRATE, false); }
    static boolean night(Context c) { return get(c).getBoolean(NIGHT, true); }
    static int nightFrom(Context c) { return get(c).getInt(NIGHT_FROM, 23); }
    static int nightTo(Context c) { return get(c).getInt(NIGHT_TO, 7); }
    static boolean respectDnd(Context c) { return get(c).getBoolean(RESPECT_DND, true); }

    static void log(Context c, String text) {
        String t = new java.text.SimpleDateFormat("HH:mm", java.util.Locale.ROOT).format(new java.util.Date());
        // ostatnie 6 zdarzeń, najnowsze na górze
        String prev = get(c).getString(LAST, "");
        String[] lines = prev.isEmpty() ? new String[0] : prev.split("\n");
        StringBuilder sb = new StringBuilder(t + " " + text);
        for (int k = 0; k < Math.min(5, lines.length); k++) sb.append('\n').append(lines[k]);
        get(c).edit().putString(LAST, sb.toString()).commit();
    }

    /** Czy o tej godzinie (0-23) obowiązuje cisza nocna. */
    static boolean isNightHour(Context c, int hour) {
        if (!night(c)) return false;
        int from = nightFrom(c), to = nightTo(c);
        if (from == to) return false;
        return from < to ? (hour >= from && hour < to) : (hour >= from || hour < to);
    }
}
