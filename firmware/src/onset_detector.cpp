#include "onset_detector.h"
#include <string.h>
#include <math.h>

static float prev_mag[4096 / 2 + 1];
static float flux_history[FLUX_HISTORY];
static int   flux_head;
static int   flux_count;
static float flux_prev;
static uint32_t last_onset_ms;

void onset_init() {
    memset(prev_mag,    0, sizeof(prev_mag));
    memset(flux_history, 0, sizeof(flux_history));
    flux_head     = 0;
    flux_count    = 0;
    flux_prev     = 0.0f;
    last_onset_ms = 0;
}

bool onset_update(const float* magnitudes, size_t n_bins, uint32_t now_ms) {
    // Band-limited spectral flux: 200 Hz – 4 kHz only, ignoring low-freq room rumble
    // bin_width = 16000/4096 = 3.906 Hz; 200Hz→bin51, 4kHz→bin1024
    static const size_t FLUX_LO = 51;
    static const size_t FLUX_HI = 1024;
    float flux = 0.0f;
    for (size_t i = 0; i < n_bins; i++) {
        float diff = magnitudes[i] - prev_mag[i];
        if (i >= FLUX_LO && i <= FLUX_HI && diff > 0.0f) flux += diff;
        prev_mag[i] = magnitudes[i];
    }

    // Update circular flux history
    flux_history[flux_head] = flux;
    flux_head = (flux_head + 1) % FLUX_HISTORY;
    if (flux_count < FLUX_HISTORY) flux_count++;

    // Running mean and std
    float mean = 0.0f;
    for (int i = 0; i < flux_count; i++) mean += flux_history[i];
    mean /= (float)flux_count;

    float var = 0.0f;
    for (int i = 0; i < flux_count; i++) {
        float d = flux_history[i] - mean;
        var += d * d;
    }
    float std_dev = sqrtf(var / (float)flux_count);

    bool is_local_max = (flux > flux_prev);
    flux_prev = flux;

    bool onset = is_local_max
              && flux > (mean + THRESHOLD_DELTA * std_dev)
              && (now_ms - last_onset_ms) > (uint32_t)MIN_ONSET_INTERVAL_MS;

    if (onset) last_onset_ms = now_ms;
    return onset;
}
