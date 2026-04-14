# Agent: Hardware + Systems Lead (Member D — Fish Shao)

## Role

Owns PCB design, enclosure, and cloud backend. Responsible for getting Gerbers to JLCPCB on time and producing a professional-quality enclosure.

## Domains

- `hardware/kicad/` — KiCad schematic + PCB layout
- `hardware/enclosure/` — Fusion 360 source and STL exports
- `hardware/cloud/mqtt_subscriber.py` — MQTT session data logger
- `hardware/cloud/config.env.example` — credentials template (never commit real creds)

## PCB Run Deadlines (FIRM — late = zero)

| Run | Deadline | Action |
|-----|----------|--------|
| 1st | Apr 6, 9am | Upload zipped Gerbers to course Google Drive |
| 2nd | Apr 20, 9am | Upload zipped Gerbers to course Google Drive |
| 3rd | May 4, 9am | Upload zipped Gerbers to course Google Drive |
| 4th | May 11, 9am | Upload zipped Gerbers to course Google Drive |

## Schematic Reference

Key connections:

| Net | From | To | Notes |
|-----|------|----|-------|
| I2S_SCK | XIAO D1 | INMP441 SCK | |
| I2S_WS | XIAO D2 | INMP441 WS | |
| I2S_SD | XIAO D3 | INMP441 SD | |
| I2C_SDA | XIAO D4 | Grove Vision AI SDA | Via Grove connector |
| I2C_SCL | XIAO D5 | Grove Vision AI SCL | Via Grove connector |
| CSI | OV5647 | Grove Vision AI CSI | Ribbon cable, not on PCB |

Verify pin assignments against XIAO ESP32S3 datasheet before finalising PCB layout.

## Enclosure Requirements

- High-fidelity finish: painted, labelled, professional
- Camera window for OV5647 (side-view angle, positioned for right-hand view)
- Mic port opening aligned with INMP441
- USB-C access for XIAO charging/programming
- Stable on piano surface (rubber feet or weighted base)
- Designed for 3D printing (PLA or PETG)

## Cloud Backend

- **Protocol**: MQTT (e.g., HiveMQ Cloud free tier or local Mosquitto)
- **Script**: `cloud/mqtt_subscriber.py` subscribes and logs session data to CSV/JSON
- **Credentials**: stored in `.env` (gitignored), template in `config.env.example`
- Session payload: `{ session_id, timestamp, score, posture_events[] }`

## Key Rules

- Never commit real MQTT credentials — use `.env` + `.gitignore`
- Always verify pin assignments with Member A before PCB layout
- Export Gerbers as ZIP for JLCPCB — use standard layer naming
- Ask before ordering any component not on the approved BOM
