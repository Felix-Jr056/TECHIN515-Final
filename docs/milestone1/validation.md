# Posiano — Milestone 1 Validation

## Component: Audio DSP (Member A)

### Python prototype — pitch accuracy

**Method:** Run `pitch_detect.py --eval` on 87 sliced WAV files in `prototyping/audio/test_samples/`. Each WAV is named `{NoteName}_{index}.wav` (ground truth). Compute per-note and overall accuracy.

```bash
cd prototyping/audio
python pitch_detect.py --eval test_samples/
```

**Expected result:** ≥90% overall accuracy, C3–C5 range.

> _Paste confusion matrix screenshot here before demo._

### Python prototype — onset detection

**Method:** Run `onset_detect.py` on the 46-second scale recording with `--plot`, verify onset count matches expected note count.

```bash
python onset_detect.py scale_recording.wav --plot --min-interval 200
```

> _Paste onset plot screenshot here (`results/onset_analysis.png`)._

### Firmware live accuracy — 60-trial test

**Method:** With firmware flashed and `pio device monitor` open, play each of the 12 notes C3–B3 five times each. Record serial output lines (`MIDI:xx NOTE:xx ONSET:x CONF:x.xx`). Compute:
- Note match rate = correct_notes / 60
- Onset detection rate = onsets_detected / 60
- Median confidence

**Pass bar:** ≥85% note accuracy, ≥95% onset detection, median confidence ≥0.6.

| Note | Expected MIDI | Detections | Matches |
|------|--------------|------------|---------|
| C3 | 48 | | |
| Cs3 | 49 | | |
| D3 | 50 | | |
| Ds3 | 51 | | |
| E3 | 52 | | |
| F3 | 53 | | |
| Fs3 | 54 | | |
| G3 | 55 | | |
| Gs3 | 56 | | |
| A3 | 57 | | |
| As3 | 58 | | |
| B3 | 59 | | |

> _Fill in after live test. Total: __/60._

### BLE end-to-end latency

**Method:** Timestamp note strike (onset serial log) and webapp `characteristicvaluechanged` event (Chrome `performance.now()`). Run 20 trials.

**Pass bar:** Median latency <200 ms, 95th percentile <400 ms, ≥95% packet delivery over 5 minutes.

> _Paste latency measurement results here._

## Component: Vision ML (Member B)

### Edge Impulse 2-class proof-of-concept

**Status:** 57 images uploaded (21 correct, 36 fingers_flat). Training in progress.

**Pass bar:** ≥80% validation accuracy on 3-class holdout set (Milestone 2 target; 2-class demo for Milestone 1).

> _Paste Edge Impulse validation screenshot here._

## Evidence of work

- [ ] Photo of cardboard enclosure with XIAO + mic mounted
- [ ] Screenshot of live webapp with piano key lit green
- [ ] `git log --oneline` output showing commits since sprint start
- [ ] Confusion matrix from Python eval
- [ ] Onset plot from scale recording
