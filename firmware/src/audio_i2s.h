#pragma once
#include <stddef.h>

void audio_i2s_init();
size_t audio_i2s_read(float* dst, size_t n_samples);
