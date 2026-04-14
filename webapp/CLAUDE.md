# Web App

Vanilla HTML/CSS/JS web app served in Chrome. Owner: Member Sonia Chen.

## Structure

- `src/index.html` — main page
- `src/css/style.css` — styles
- `src/js/app.js` — entry point, UI state management
- `src/js/ble.js` — Web Bluetooth connection, GATT service handling
- `src/js/midi-parser.js` — MIDI file upload and parsing
- `src/js/feedback.js` — real-time note/rhythm/posture rendering
- `src/js/session.js` — session history and scoring
- `src/assets/` — icons, fonts

## Dev Server

```bash
cd webapp/src
python -m http.server 8080
# Open Chrome at http://localhost:8080
```

## Notes

- Web Bluetooth only works over HTTPS or localhost — never deploy on plain HTTP
- Mobile-first layout — primary use is phone/tablet beside piano
- No build step, no bundler, no npm — keep it simple
- Test BLE with nRF Connect app as mock peripheral before hardware arrives
