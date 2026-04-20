#include <Arduino.h>
#include <Wire.h>
#include "audio_i2s.h"
#include "fft_processor.h"
#include "onset_detector.h"
#include "ble_service.h"
#include "i2c_vision.h"

static float ring_buf[FFT_SIZE];
static int   n_filled = 0;

void setup() {
    Serial.begin(115200);

    pinMode(D6, OUTPUT); digitalWrite(D6, HIGH);
    pinMode(D7, OUTPUT); digitalWrite(D7, LOW);
    pinMode(D8, OUTPUT); digitalWrite(D8, LOW);

    Wire.begin();
    vision_init();
    audio_i2s_init();
    fft_init();
    onset_init();
    ble_init();

    Serial.println("Posiano online, BLE advertising");
}

void loop() {
    if (n_filled < FFT_SIZE) {
        int to_read = FFT_SIZE - n_filled;
        if (to_read > HOP) to_read = HOP;
        size_t got = audio_i2s_read(ring_buf + n_filled, to_read);
        n_filled += (int)got;
        return;
    }

    float dc = 0.0f;
    for (int i = 0; i < FFT_SIZE; i++) dc += ring_buf[i];
    dc /= FFT_SIZE;

    float rms = 0.0f;
    for (int i = 0; i < FFT_SIZE; i++) { float s = ring_buf[i] - dc; rms += s * s; }
    rms = sqrtf(rms / FFT_SIZE);

    static const float RMS_GATE     = 0.001f;
    static const float CONF_THRESHOLD = 0.20f;

    float conf = 0.0f;
    int midi = -1;
    bool onset = false;

    if (rms >= RMS_GATE) {
        midi = fft_detect_midi(ring_buf, &conf);
        const float* mags = fft_get_magnitudes();
        size_t n_bins = fft_get_n_bins();
        onset = onset_update(mags, n_bins, millis());
    }

    uint8_t midi_byte = (midi < 0 || conf < CONF_THRESHOLD) ? 0xFF : (uint8_t)midi;
    ble_notify(midi_byte, (uint8_t)(conf * 255.0f), onset && conf >= CONF_THRESHOLD);

    Serial.printf("RMS:%.5f MIDI:%d NOTE:%s ONSET:%d CONF:%.2f\n",
                  rms, midi, midi_to_name(midi), (int)onset, conf);

    memmove(ring_buf, ring_buf + HOP, (FFT_SIZE - HOP) * sizeof(float));
    audio_i2s_read(ring_buf + FFT_SIZE - HOP, HOP);

    static uint32_t last_vision_ms = 0;
    uint32_t now = millis();
    if (now - last_vision_ms >= 500) {
        last_vision_ms = now;
        int cls = vision_get_class();
        Serial.printf("POSTURE:%d CLASS:%s\n", cls, vision_class_name(cls));
    }
}
