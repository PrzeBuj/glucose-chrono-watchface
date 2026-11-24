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
    private static final double FREQ = 4000;
    private static final int BEEP_MS = 70;
    private static final int GAP_MS = 90;

    private Beeper() {}

    /** Odtwarza sygnał i czeka do końca (wywoływać poza wątkiem głównym). */
    static void play(Context c, boolean twice, int volume, boolean vibrate) {
        if (vibrate) {
            Vibrator v = c.getSystemService(Vibrator.class);
            if (v != null && v.hasVibrator()) {
                long[] pattern = twice ? new long[]{0, 60, 100, 60} : new long[]{0, 70};
                v.vibrate(VibrationEffect.createWaveform(pattern, -1));
            }
        }
        short[] pcm = samples(twice, new float[]{0.25f, 0.55f, 1.0f}[Math.max(0, Math.min(2, volume))]);
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

    private static short[] samples(boolean twice, float amp) {
        int beep = RATE * BEEP_MS / 1000;
        int gap = RATE * GAP_MS / 1000;
        int total = twice ? beep * 2 + gap : beep;
        short[] out = new short[total + RATE / 50];
        writeBeep(out, 0, beep, amp);
        if (twice) writeBeep(out, beep + gap, beep, amp);
        return out;
    }

    private static void writeBeep(short[] out, int start, int len, float amp) {
        int fade = RATE * 4 / 1000; // 4 ms, bez trzasków
        for (int i = 0; i < len; i++) {
            double env = Math.min(1.0, Math.min(i, len - 1 - i) / (double) fade);
            double t = i / (double) RATE;
            // fala zbliżona do prostokątnej, jak brzęczyk piezo, ale łagodniejsza dla ucha
            double s = Math.sin(2 * Math.PI * FREQ * t) + 0.25 * Math.sin(2 * Math.PI * 3 * FREQ * t);
            out[start + i] = (short) (s / 1.25 * env * amp * 30000);
        }
    }
}
