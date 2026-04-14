# Audio Test Samples

WAV files for validating pitch and onset detection algorithms.

## Filename Convention

```
{NoteName}_{index}.wav
```

Examples:
- `C4_01.wav` — middle C, sample 1
- `Fs5_02.wav` — F-sharp 5, sample 2
- `As3_01.wav` — A-sharp 3 (B-flat), sample 1

### Note name encoding

Sharps-only convention — matches `NOTE_NAMES` in `pitch_detect.py` exactly.

| Symbol | Meaning | Enharmonic |
|--------|---------|------------|
| `Cs`   | C-sharp | D-flat     |
| `Ds`   | D-sharp | E-flat     |
| `Fs`   | F-sharp | G-flat     |
| `Gs`   | G-sharp | A-flat     |
| `As`   | A-sharp | B-flat     |

**Do not use flat names** (`Bb`, `Eb`, etc.) in filenames — the evaluator will score them as wrong.

Target range: **C3 through C6** (MIDI 48-84).

## Recommended Sources

- University of Iowa Electronic Music Studios piano samples (public domain)
- Freesound.org — search "piano single note"
- Generate synthetically: `fluidsynth -F {note}.wav FluidR3_GM.sf2 note.mid`

## What is gitignored

WAV and MP3 files in this directory are excluded from git (see root `.gitignore`).
Only this README is tracked.

## Evaluation

```bash
cd prototyping/audio
python pitch_detect.py --eval test_samples/
# Outputs results/pitch_confusion_matrix.png
```

Target: >=90% accuracy across C3-C6 on 50+ samples.
