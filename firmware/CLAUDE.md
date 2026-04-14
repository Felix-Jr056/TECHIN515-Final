# Firmware

Arduino C++ for XIAO ESP32S3 via PlatformIO. Owner: Member Felix Du.

## Structure

- `src/main.cpp` — entry point, setup/loop
- `src/fft_processor.h/.cpp` — FFT + Harmonic Product Spectrum pitch detection
- `src/onset_detector.h/.cpp` — spectral flux onset detection
- `src/midi_matcher.h/.cpp` — MIDI sequence comparison and scoring
- `src/ble_service.h/.cpp` — BLE GATT service definition and notifications
- `src/i2c_vision.h/.cpp` — I2C reader for Grove Vision AI V2 posture data
- `platformio.ini` — PlatformIO config

## Build

```bash
pio run              # compile
pio run -t upload    # flash to XIAO
pio device monitor   # serial monitor
```

## Pin Map (XIAO ESP32S3)

| Function | Pin | Notes |
|----------|-----|-------|
| I2S SCK | D1 | INMP441 clock |
| I2S WS | D2 | INMP441 word select |
| I2S SD | D3 | INMP441 data |
| I2C SDA | D4 | Grove connector (Vision AI) |
| I2C SCL | D5 | Grove connector (Vision AI) |
| LED Power | D6 | Green |
| LED BLE | D7 | Blue |
| LED Posture | D8 | Red |

Pin assignments are tentative — verify against XIAO ESP32S3 datasheet before PCB layout.
