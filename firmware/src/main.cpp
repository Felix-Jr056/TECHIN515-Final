/**
 * Smart Piano Learning Device — Main Firmware
 * XIAO ESP32S3
 * 
 * Audio DSP: FFT pitch detection + onset detection
 * Comms: BLE GATT to web app, I2C to Grove Vision AI V2, Wi-Fi/MQTT to cloud
 */

#include <Arduino.h>

// TODO: Include headers when modules are implemented
// #include "fft_processor.h"
// #include "onset_detector.h"
// #include "midi_matcher.h"
// #include "ble_service.h"
// #include "i2c_vision.h"

void setup() {
    Serial.begin(115200);
    Serial.println("Piano Learning Device — Initialising...");
    
    // TODO: Initialise I2S mic
    // TODO: Initialise BLE GATT service
    // TODO: Initialise I2C for Grove Vision AI V2
    // TODO: Initialise Wi-Fi + MQTT
    // TODO: Initialise status LEDs
}

void loop() {
    // TODO: Read I2S audio buffer
    // TODO: Run FFT pitch detection
    // TODO: Run onset detection
    // TODO: Compare against MIDI reference
    // TODO: Read posture classification from Grove Vision AI (I2C)
    // TODO: Send combined feedback via BLE notify
    // TODO: Log session data to cloud (periodic)
}
