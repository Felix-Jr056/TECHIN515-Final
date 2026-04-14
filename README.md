# Smart Piano Learning Device

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

## Team

| Member | Role | Domain |
|--------|------|--------|
| A | Audio DSP Lead | `firmware/`, `prototyping/audio/` |
| B | Vision ML Lead | `prototyping/vision/` |
| C | Web App + Comms | `webapp/` |
| D | Hardware + Systems | `hardware/` |
