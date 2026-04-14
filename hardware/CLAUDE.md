# Hardware

PCB design, enclosure, and cloud backend. Owner: Member Fish Shao.

## Structure

- `kicad/piano-device.kicad_pro` — KiCad project
- `kicad/piano-device.kicad_sch` — schematic
- `kicad/piano-device.kicad_pcb` — PCB layout
- `kicad/gerbers/` — exported Gerber files for JLCPCB
- `enclosure/piano-device.f3d` — Fusion 360 source (or .step export)
- `enclosure/stl/` — STL files for 3D printing
- `cloud/mqtt_subscriber.py` — MQTT listener and data logger
- `cloud/config.env.example` — MQTT broker credentials template (never commit real creds)

## PCB Run Deadlines

| Run | Deadline | Google Drive |
|-----|----------|-------------|
| 1st | Apr 6, 9am | Course folder |
| 2nd | Apr 20, 9am | Course folder |
| 3rd | May 4, 9am | Course folder |
| 4th | May 11, 9am | Course folder |

Upload zipped Gerber files to the course Google Drive folder before deadline.

## Enclosure Requirements

- High-fidelity finish: painted, labelled, professional
- Camera window for OV5647 side-view
- Mic port opening
- USB-C access for charging
- Stable on piano surface (rubber feet or weighted base)
