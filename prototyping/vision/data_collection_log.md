# Data Collection Log

Record every data collection session here.

---

## Data Collection Protocol

### Camera Setup

- **View**: Side view, camera perpendicular to the piano keys, capturing the right hand
- **Distance**: 30–50 cm from the hand
- **Height**: At keyboard level — not looking down from above
- **Camera**: Phone camera or laptop webcam (Phase 1); Grove Vision AI OV5647 (Phase 2+)

### Lighting

- Consistent overhead or natural daylight
- Avoid backlighting (no window directly behind the hand)
- Avoid harsh shadows across fingers

### Class Definitions

| Class | Description |
|-------|-------------|
| `correct` | Proper arch, wrist level with forearm, curved fingers, thumb on side of key |
| `wrist_dropped` | Wrist visibly below keyboard surface level |
| `fingers_flat` | Fingers extended/straight rather than curved |

### Labelling Convention

- Directory name IS the label: `datasets/raw/correct/`, `datasets/raw/wrist_dropped/`, `datasets/raw/fingers_flat/`
- Filename: `{session_id}_{sample_index:04d}.jpg` — e.g. `s01_0042.jpg`
  (`sample_index` is the sequential count of saved frames, not the raw video frame number)
- Generate from video: `python extract_frames.py <video.mp4> datasets/raw/<class>/ --prefix s01`

### Capture Tips

- Film ~30 s of each posture per session; extract frames at 500 ms interval (~60 frames)
- Vary finger positions within each class (play different notes, not just one)
- Keep background consistent (same piano, same surface)
- Target: **150–200 images per class** for Phase 1 (1 person)
- Phase 2: recruit 2–3 more hands for diversity

---

## Session Template

| Field | Value |
|-------|-------|
| Date | |
| Person | (hand size: S/M/L) |
| Camera | (phone/webcam/Grove Vision AI) |
| Distance | (e.g. 30cm) |
| Angle | (side view, perpendicular to keys) |
| Lighting | (daylight/overhead lamp/dim) |
| Images per class | |
| Total images | |
| Notes | |

---

## Sessions

(Add entries below as you collect data)
