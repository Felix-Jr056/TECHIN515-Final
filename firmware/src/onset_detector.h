#pragma once
#include <stddef.h>
#include <stdint.h>

static constexpr int   HOP                  = 256;
static constexpr int   FLUX_HISTORY         = 32;
static constexpr float THRESHOLD_DELTA      = 1.0f;
static constexpr int   MIN_ONSET_INTERVAL_MS = 100;

void onset_init();
bool onset_update(const float* magnitudes, size_t n_bins, uint32_t now_ms);
