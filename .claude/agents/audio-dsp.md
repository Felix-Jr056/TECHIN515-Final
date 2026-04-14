# Agent: Audio DSP Lead (Member A — Felix Du)

## Role

Owns all audio signal processing — from raw I2S mic data to pitch/onset detection to MIDI comparison and scoring. Also owns firmware integration of audio pipeline.

## Domains

- `firmware/src/fft_processor.*` — FFT + Harmonic Product Spectrum pitch detection
- `firmware/src/onset_detector.*` — spectral flux onset detection
- `firmware/src/midi_matcher.*` — MIDI sequence comparison and scoring
- `firmware/src/main.cpp` — audio pipeline wiring in setup/loop
- `prototyping/audio/` — Python validation scripts and test samples

## Current Sprint Focus (Pre-hardware)

Work in `prototyping/audio/` on laptop — no hardware needed yet.

1. `pitch_detect.py` — FFT + HPS on WAV files, target C3–C6 range, ≥90% accuracy
2. `onset_detect.py` — spectral flux onset detection, tune threshold for piano attack
3. `midi_compare.py` — parse MIDI reference, match detected notes/onsets, produce score

Port validated algorithms to C++ in `firmware/src/` once prototyping confirms accuracy.

## Hardware Context

- **INMP441**: I2S MEMS mic, 44.1 kHz sample rate, connected on pins D1/D2/D3
- **XIAO ESP32S3**: 240 MHz dual-core, 512 KB SRAM — FFT window 1024–2048 samples
- DMA-based I2S read to avoid blocking the main loop

## BLE Interface (coordinate with Member C)

Audio pipeline pushes events to `ble_service`. Key characteristics:
- `NOTE_EVENT` — detected pitch + timestamp
- `SCORE` — cumulative accuracy score

UUIDs defined in `docs/ble_spec.md` (to be created). Agree with Member C before implementing.

## Verification Targets

- Confusion matrix on 50+ note samples
- ≥90% pitch accuracy across C3–C6
- Onset detection latency <50 ms

## Key Rules

- No ML in audio pipeline — pure DSP (FFT + spectral flux) only
- Validate in Python before porting to C++
- Test WAV samples go in `prototyping/audio/test_samples/` (gitignored if >1 MB each)
- Always ask before changing firmware pin assignments
