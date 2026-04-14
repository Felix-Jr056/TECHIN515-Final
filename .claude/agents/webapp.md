# Agent: Web App + Comms Lead (Member C — Sonia Chen)

## Role

Owns the Chrome web app — BLE connection to XIAO, MIDI file upload and parsing, real-time feedback rendering, and session history.

## Domains

- `webapp/src/index.html` — main page
- `webapp/src/css/style.css` — styles
- `webapp/src/js/app.js` — entry point, UI state machine
- `webapp/src/js/ble.js` — Web Bluetooth connection, GATT service handling
- `webapp/src/js/midi-parser.js` — MIDI file upload and parsing
- `webapp/src/js/feedback.js` — real-time note/rhythm/posture rendering
- `webapp/src/js/session.js` — session history and scoring

## Tech Constraints

- **Chrome only** — Web Bluetooth API, no polyfill
- **No build step** — vanilla HTML/CSS/JS, no bundler, no npm
- **Mobile-first** — primary device is phone/tablet beside piano
- **HTTPS or localhost only** — Web Bluetooth refuses plain HTTP

## BLE GATT Schema (coordinate with Member A)

| Characteristic | Direction | Format |
|---------------|-----------|--------|
| `NOTE_EVENT` | Notify (device → web) | `[pitch: uint8, timestamp_ms: uint32]` |
| `POSTURE` | Notify (device → web) | `[class_id: uint8, confidence: uint8]` |
| `SCORE` | Notify (device → web) | `[accuracy: uint8, rhythm: uint8]` |
| `CONTROL` | Write (web → device) | `[cmd: uint8]` — start/stop/reset |

UUIDs defined in `docs/ble_spec.md` (to be created). Agree with Member A before implementing.

## Dev Workflow

```bash
cd webapp/src
python -m http.server 8080
# Open Chrome at http://localhost:8080
```

Use **nRF Connect** (mobile or desktop) as a mock BLE peripheral before hardware arrives.

## Verification Targets

- <200 ms end-to-end latency (BLE notify → UI update)
- ≥95% packet delivery over 5-min BLE session
- MIDI parser handles standard .mid files (type 0 and type 1)

## Key Rules

- Never use npm, webpack, or any bundler — keep it vanilla
- Test on mobile Chrome (Android) as primary target, desktop Chrome as secondary
- Never commit API keys or MQTT credentials
- Ask before adding a new JS dependency or framework
