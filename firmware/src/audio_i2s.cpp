#include "audio_i2s.h"
#include <driver/i2s.h>
#include <Arduino.h>

#define I2S_PORT        I2S_NUM_0
#define I2S_DMA_BUFS    4
#define I2S_DMA_BUF_LEN 512

// INMP441 L/R pin: GND -> LEFT channel, VDD -> RIGHT channel.
// Toggle this to 1 if L/R is tied to VDD (or as a diagnostic fallback).
#define I2S_USE_RIGHT 0

void audio_i2s_init() {
    i2s_config_t cfg = {
        .mode                 = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate          = 16000,
        .bits_per_sample      = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format       = I2S_USE_RIGHT ? I2S_CHANNEL_FMT_ONLY_RIGHT : I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags     = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count        = I2S_DMA_BUFS,
        .dma_buf_len          = I2S_DMA_BUF_LEN,
        .use_apll             = false,
        .tx_desc_auto_clear   = false,
        .fixed_mclk           = 0
    };
    i2s_driver_install(I2S_PORT, &cfg, 0, nullptr);

    i2s_pin_config_t pins = {
        .bck_io_num    = D1,
        .ws_io_num     = D2,
        .data_out_num  = I2S_PIN_NO_CHANGE,
        .data_in_num   = D3
    };
    i2s_set_pin(I2S_PORT, &pins);
}

// INMP441: 24-bit audio left-justified in 32-bit I2S frame (bits [31:8]).
// `raw[i] >> 8` arithmetic-shifts to a signed 24-bit value; divide by 2^23 to normalize to [-1, 1].
// Alternative form: `(int32_t)(raw[i] & 0xFFFFFF00) >> 8` is equivalent on two's-complement (ESP32).
size_t audio_i2s_read(float* dst, size_t n_samples) {
    static int32_t raw[512];
    static uint32_t dbg_count = 0;
    size_t to_read = (n_samples <= 512) ? n_samples : 512;
    size_t bytes_read = 0;
    i2s_read(I2S_PORT, raw, to_read * sizeof(int32_t), &bytes_read, portMAX_DELAY);
    size_t got = bytes_read / sizeof(int32_t);
    if (got > 0 && ++dbg_count % 50 == 0) {
        int32_t mn = raw[0], mx = raw[0];
        for (size_t i = 1; i < got; i++) {
            if (raw[i] < mn) mn = raw[i];
            if (raw[i] > mx) mx = raw[i];
        }
        Serial.printf("RAW min=%ld max=%ld range=%ld\n", (long)mn, (long)mx, (long)(mx - mn));
    }
    for (size_t i = 0; i < got; i++) {
        dst[i] = (float)(raw[i] >> 8) / 8388608.0f;
    }
    return got;
}
