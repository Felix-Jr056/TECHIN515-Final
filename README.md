# Posiano

TECHIN 515 — Hardware Software Lab II, Spring 2026, UW GIX

A countertop device that monitors beginner pianists using a side-view camera for hand posture classification and a microphone for note/rhythm accuracy assessment.

## Architecture

- **XIAO ESP32S3** — Audio DSP, BLE, Wi-Fi
- **Grove Vision AI V2** — Posture ML (Edge Impulse CNN, I2C)
- **INMP441 I2S Mic** — Piano audio capture
- **Web App** — Chrome, Web Bluetooth, MIDI parsing, real-time feedback
- **Cloud** — MQTT session logging

## Directory Structure

```
Piano/
├── CLAUDE.md              # Claude Code project context
├── .claude/agents/        # Specialised sub-agents per role
├── firmware/              # Arduino C++ for XIAO ESP32S3 (PlatformIO)
├── prototyping/           # Python prototypes (audio DSP, vision data prep)
├── webapp/                # Web app (HTML/CSS/JS, BLE, MIDI)
├── hardware/              # KiCad PCB, enclosure CAD, cloud backend
└── docs/                  # Deadlines, references
```

## Quick Start

```bash
# Prototyping (Python)
cd prototyping && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Web App
cd webapp/src && python -m http.server 8080

# Firmware (requires PlatformIO)
cd firmware && pio run
```

## Milestone 1 — Real-Time Audio Demo

**Hardware required:** XIAO ESP32S3 + INMP441 mic wired (SCK→D1, WS→D2, SD→D3), USB connected to laptop.

### 1. Flash firmware

```bash
cd firmware
pio run -t upload
pio device monitor   # expect: "Posiano online, BLE advertising"
```

### 2. Start web app

```bash
cd webapp/src
python -m http.server 8080
```

Open **Chrome** at `http://localhost:8080`.

### 3. Connect and play

1. Click **Connect BLE** in the app.
2. Select **Posiano-01** in the Chrome pairing dialog.
3. Play notes on the piano — the matching key lights green and an onset flash fires on each strike.

**Fallback:** If BLE pairing fails, the firmware still prints `MIDI:60 NOTE:C4 ONSET:1 CONF:0.87` to serial — project `pio device monitor` output for the demo.

### Audio DSP validation (Python prototype)

```bash
cd prototyping/audio
python pitch_detect.py --eval test_samples/   # confusion matrix on 87 sliced WAVs
python onset_detect.py scale_recording.wav --plot
```

Expected: ≥90% pitch accuracy across C3–C5 range.

## Team

| Member | Role | Domain |
|--------|------|--------|
| A | Audio DSP Lead | `firmware/`, `prototyping/audio/` |
| B | Vision ML Lead | `prototyping/vision/` |
| C | Web App + Comms | `webapp/` |
| D | Hardware + Systems | `hardware/` |
