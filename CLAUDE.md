# Posiano

TECHIN 515 Hardware Software Lab II — Spring 2026, UW GIX.
4-member team, $350 budget, 10-week timeline.

## What This Is

A countertop device that monitors beginner pianists using a side-view camera for hand posture classification and a microphone for note/rhythm accuracy against a MIDI reference. Real-time feedback via web app on phone/tablet. Session data logged to cloud.

## Architecture

```
INMP441 Mic --[I2S]--> XIAO ESP32S3 --[BLE GATT]--> Web App (Chrome)
                              |                            |
OV5647 Cam --[CSI]--> Grove Vision AI V2 --[I2C Grove]--^  |
                                                            |--[Wi-Fi/MQTT]--> Cloud
```

- **XIAO ESP32S3**: Main MCU — FFT pitch detection, onset/rhythm analysis, MIDI comparison, BLE, Wi-Fi
- **Grove Vision AI V2**: Posture ML — Arm Cortex-M55 + Ethos-U55 NPU, Edge Impulse CNN (INT8), 4 classes
- **INMP441**: I2S MEMS mic — digital audio, no ADC needed
- **OV5647**: CSI camera on Grove Vision AI — 96×96 grayscale for posture

## Team Roles

| Member | Role | Owns |
|--------|------|------|
| A | Audio DSP Lead | `firmware/`, `prototyping/audio/` — FFT, onset, MIDI logic |
| B | Vision ML Lead | `prototyping/vision/` — Edge Impulse, data collection, model |
| C | Web App + Comms | `webapp/` — BLE, MIDI parser, feedback UI, session history |
| D | Hardware + Systems | `hardware/` — KiCad, enclosure, cloud backend |

## Key Constraints

- **Always ask before generating** — no autonomous decisions on architecture, sensor choices, or scope
- Audio pipeline is pure DSP (FFT + spectral flux) — no ML
- Posture pipeline is ML (Edge Impulse CNN) — 4 classes: correct, wrist-dropped, fingers-flat, collapsed-knuckles
- 150–200 images per class, phased: Phase 1 one person, Phase 2 add 2–3 more hands
- Web app uses Web Bluetooth API (Chrome only) — no native app
- Budget: $350 total, current BOM estimate ~$130–165
- All deadlines are firm, late = zero. See `docs/syllabus_deadlines.md`

## Commands

- `cd prototyping/audio && python pitch_detect.py <wav_file>` — test pitch detection
- `cd prototyping/audio && python onset_detect.py <wav_file>` — test onset detection
- `cd webapp && python -m http.server 8080` — serve web app locally
- `cd firmware && pio run` — build firmware (when PlatformIO is set up)
- `cd firmware && pio run -t upload` — flash to XIAO ESP32S3

## Verification

- Audio: confusion matrix on 50+ note samples, ≥90% accuracy across C3–C6
- Posture: Edge Impulse validation ≥80% on 4-class problem
- BLE: <200ms end-to-end latency, ≥95% packet delivery over 5 min
- I2C: zero packet loss over 5-min continuous test between Grove Vision AI and XIAO
