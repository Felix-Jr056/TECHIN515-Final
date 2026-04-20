#include "fft_processor.h"
#include <arduinoFFT.h>
#include <Arduino.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

static float vReal[ZERO_PAD];
static float vImag[ZERO_PAD];
static float magnitudes[ZERO_PAD / 2 + 1];
static float hps_buf[ZERO_PAD / 2 + 1];

static const char* NOTE_NAMES[] = {"C","Cs","D","Ds","E","F","Fs","G","Gs","A","As","B"};

void fft_init() {
    memset(vReal, 0, sizeof(vReal));
    memset(vImag, 0, sizeof(vImag));
}

int fft_detect_midi(const float* frame, float* out_confidence) {
    // Remove DC before windowing to avoid spectral leakage at bin 0 biasing HPS
    float dc = 0.0f;
    for (int i = 0; i < FFT_SIZE; i++) dc += frame[i];
    dc /= FFT_SIZE;

    // Apply Hann window to FFT_SIZE samples, then zero-pad to ZERO_PAD
    for (int i = 0; i < FFT_SIZE; i++) {
        float w = 0.5f * (1.0f - cosf(2.0f * M_PI * i / (FFT_SIZE - 1)));
        vReal[i] = (frame[i] - dc) * w;
    }
    for (int i = FFT_SIZE; i < ZERO_PAD; i++) vReal[i] = 0.0f;
    memset(vImag, 0, sizeof(vImag));

    ArduinoFFT<float> fft(vReal, vImag, ZERO_PAD, SAMPLE_RATE);
    fft.compute(FFTDirection::Forward);
    fft.complexToMagnitude();

    int n_bins = ZERO_PAD / 2 + 1;
    for (int i = 0; i < n_bins; i++) magnitudes[i] = vReal[i];

    // Harmonic Product Spectrum over valid range
    float bin_width = SAMPLE_RATE / (float)ZERO_PAD;
    int lo_bin = (int)(FREQ_LO / bin_width);
    int hi_bin = (int)(FREQ_HI / bin_width);
    int max_k  = n_bins / N_HARMONICS;
    if (hi_bin >= max_k) hi_bin = max_k - 1;
    if (lo_bin >= hi_bin) { *out_confidence = 0.0f; return -1; }

    for (int k = lo_bin; k <= hi_bin; k++) {
        hps_buf[k] = magnitudes[k];
        for (int h = 2; h <= N_HARMONICS; h++) hps_buf[k] *= magnitudes[k * h];
    }

    // Find peak and compute confidence as peak / total HPS energy
    int   peak_bin = lo_bin;
    float peak_val = hps_buf[lo_bin];
    float total    = hps_buf[lo_bin];
    for (int k = lo_bin + 1; k <= hi_bin; k++) {
        total += hps_buf[k];
        if (hps_buf[k] > peak_val) {
            peak_val = hps_buf[k];
            peak_bin = k;
        }
    }
    *out_confidence = (total > 0.0f) ? fminf(1.0f, peak_val / total) : 0.0f;

    // Print top 5 raw magnitude bins (before HPS) to verify FFT spectrum
    static uint32_t dbg_fft = 0;
    if (++dbg_fft % 10 == 0) {
        int top5[5] = {0}; float top5v[5] = {0};
        for (int k = lo_bin; k <= hi_bin; k++) {
            if (magnitudes[k] > top5v[4]) {
                top5v[4] = magnitudes[k]; top5[4] = k;
                for (int j = 3; j >= 0 && top5v[j+1] > top5v[j]; j--) {
                    float tv = top5v[j]; top5v[j] = top5v[j+1]; top5v[j+1] = tv;
                    int ti = top5[j]; top5[j] = top5[j+1]; top5[j+1] = ti;
                }
            }
        }
        Serial.printf("SPEC top5: %d(%.4f) %d(%.4f) %d(%.4f) %d(%.4f) %d(%.4f)\n",
            top5[0],(double)top5v[0], top5[1],(double)top5v[1], top5[2],(double)top5v[2],
            top5[3],(double)top5v[3], top5[4],(double)top5v[4]);
    }

    float peak_freq = (float)peak_bin * bin_width;
    if (peak_freq <= 0.0f) { *out_confidence = 0.0f; return -1; }

    Serial.printf("DBG peak_bin=%d freq=%.1f\n", peak_bin, peak_freq);

    int midi = (int)roundf(12.0f * log2f(peak_freq / A4_FREQ) + 69.0f);
    if (midi < MIDI_C3 || midi > MIDI_C6) { *out_confidence = 0.0f; return -1; }
    return midi;
}

const char* midi_to_name(int midi) {
    if (midi < 0) return "???";
    static char buf[8];
    int octave = (midi / 12) - 1;
    snprintf(buf, sizeof(buf), "%s%d", NOTE_NAMES[midi % 12], octave);
    return buf;
}

const float* fft_get_magnitudes() { return magnitudes; }
size_t       fft_get_n_bins()     { return ZERO_PAD / 2 + 1; }
