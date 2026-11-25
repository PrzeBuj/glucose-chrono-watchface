package com.glucosechrono.chime;

import android.content.Context;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioTrack;
import android.os.VibrationEffect;
import android.os.Vibrator;

/** Krótki, wysoki „piik” jak w klasycznych zegarkach cyfrowych (brzęczyk ok. 4 kHz). */
final class Beeper {
    private static final int RATE = 44100;

    /** Barwy dźwięku: częstotliwość, długość „piik”, przerwa, wybrzmiewanie (0 = brak), ostrość (harmoniczne). */
    private static final double[][] TONES = {
            {4000, 70, 90, 0, 0.25},    // cyfrowy: wysoki brzęczyk, jak klasyczny zegarek cyfrowy
            {2048, 90, 110, 0, 0.08},   // niski: łagodniejszy, niższy ton
            {1568, 260, 120, 9, 0.35},  // dzwonek: krótkie „dzyń” z wybrzmieniem
            {3200, 45, 60, 0, 0.55},    // elektroniczny: krótki, ostry „tik-tik”
    };

    private Beeper() {}

    /** Odtwarza sygnał i czeka do końca (wywoływać poza wątkiem głównym). */
    static void play(Context c, boolean twice, int volume, boolean vibrate) {
        play(c, twice, volume, vibrate, Prefs.tone(c));
    }

    static void play(Context c, boolean twice, int volume, boolean vibrate, int tone) {
        if (vibrate) {
            Vibrator v = c.getSystemService(Vibrator.class);
            if (v != null && v.hasVibrator()) {
                long[] pattern = twice ? new long[]{0, 60, 100, 60} : new long[]{0, 70};
                v.vibrate(VibrationEffect.createWaveform(pattern, -1));
            }
        }
        double[] t = TONES[Math.max(0, Math.min(TONES.length - 1, tone))];
        short[] pcm = samples(t, twice, new float[]{0.25f, 0.55f, 1.0f}[Math.max(0, Math.min(2, volume))]);
        AudioTrack track = new AudioTrack.Builder()
                .setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ALARM)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build())
                .setAudioFormat(new AudioFormat.Builder()
                        .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                        .setSampleRate(RATE)
                        .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                        .build())
                .setTransferMode(AudioTrack.MODE_STATIC)
                .setBufferSizeInBytes(pcm.length * 2)
                .build();
        try {
            track.write(pcm, 0, pcm.length);
            track.play();
            Thread.sleep(pcm.length * 1000L / RATE + 150);
        } catch (InterruptedException ignored) {
        } finally {
            track.release();
        }
    }

    private static short[] samples(double[] t, boolean twice, float amp) {
        int beep = (int) (RATE * t[1] / 1000);
        int gap = (int) (RATE * t[2] / 1000);
        int total = twice ? beep * 2 + gap : beep;
        short[] out = new short[total + RATE / 50];
        writeBeep(out, 0, beep, amp, t);
        if (twice) writeBeep(out, beep + gap, beep, amp, t);
        return out;
    }

    private static void writeBeep(short[] out, int start, int len, float amp, double[] t) {
        double freq = t[0], decay = t[3], harm = t[4];
        int fade = RATE * 4 / 1000; // 4 ms, bez trzasków
        for (int i = 0; i < len; i++) {
            double env = Math.min(1.0, Math.min(i, len - 1 - i) / (double) fade);
            double time = i / (double) RATE;
            if (decay > 0) env *= Math.exp(-decay * time);
            double s = Math.sin(2 * Math.PI * freq * time) + harm * Math.sin(2 * Math.PI * 3 * freq * time);
            if (decay > 0) s += 0.4 * Math.sin(2 * Math.PI * 2.76 * freq * time) * Math.exp(-decay * 2 * time);
            out[start + i] = (short) (s / (1 + harm + 0.4) * env * amp * 30000);
        }
    }
}
