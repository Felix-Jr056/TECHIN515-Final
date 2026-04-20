#pragma once
#include <stddef.h>

static constexpr int    FFT_SIZE     = 2048;
static constexpr int    ZERO_PAD     = 4096;
static constexpr float  SAMPLE_RATE  = 16000.0f;
static constexpr int    N_HARMONICS  = 5;
static constexpr float  FREQ_LO      = 130.0f;
static constexpr float  FREQ_HI      = 1100.0f;
static constexpr int    MIDI_C3      = 48;
static constexpr int    MIDI_C6      = 84;
static constexpr float  A4_FREQ      = 440.0f;

void        fft_init();
int         fft_detect_midi(const float* frame, float* out_confidence);
const char* midi_to_name(int midi);
const float* fft_get_magnitudes();
size_t      fft_get_n_bins();
