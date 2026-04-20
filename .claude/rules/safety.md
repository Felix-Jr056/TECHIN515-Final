# Safety Rules — Posiano

These rules apply to all members and all Claude Code sessions in this project.

## Decision-Making

- **Always ask before deciding** on architecture, sensor choices, scope changes, or anything that affects another member's domain.
- **No autonomous decisions** — if in doubt, surface it to the team before acting.
- Cross-domain changes (e.g., changing a pin assignment that affects both PCB and firmware) require explicit sign-off from both domain owners.

## Code Quality

- No committing broken builds — run `pio run` before committing firmware changes.
- No committing untested prototyping scripts — run on at least one WAV sample or image before committing.
- No dead code — remove commented-out blocks before committing.
- Commit message format: `[area] short description` (e.g., `[audio] add HPS stage to pitch_detect.py`).

## Security

- Never commit credentials, API keys, or MQTT passwords — use `.env` files (gitignored).
- Never commit raw image datasets — add to `.gitignore`.
- `config.env.example` is the only credentials file allowed in git (no real values).

## Budget

- Total budget: $350. Current BOM estimate: ~$130–165.
- Do not order any component without checking remaining budget in `docs/budget.md`.
- All purchases require team awareness before ordering.

## Deadlines

All deadlines are firm — late = zero.

- PCB Gerbers must be uploaded to Google Drive by 9am on the deadline date.
- Milestone demos must be functional — plan buffer time for hardware bring-up issues.
- See `docs/syllabus_deadlines.md` for the full schedule.

## Verification Before Milestone

| Member | Verification |
|--------|-------------|
| A | Confusion matrix ≥90% on 50+ note samples (C3–C6) |
| B | Edge Impulse validation ≥80% on 3-class holdout set |
| C | BLE latency <200ms, ≥95% delivery over 5 min |
| D | I2C zero packet loss over 5 min; PCB powers up |

## Inter-member Interfaces

Changes to shared interfaces require both owners to agree first:

| Interface | Owners |
|-----------|--------|
| BLE GATT characteristics | A + C |
| I2C packet format (Vision AI → XIAO) | B + A |
| MQTT session payload schema | D + C |
| Pin assignments | A + D |
