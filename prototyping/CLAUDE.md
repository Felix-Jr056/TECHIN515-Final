# Prototyping

Python prototypes for algorithm validation before porting to firmware. These run on laptop, no hardware needed.

## Structure

- `audio/pitch_detect.py` — FFT + HPS pitch detection on WAV files
- `audio/onset_detect.py` — spectral flux onset detection
- `audio/midi_compare.py` — MIDI file parsing + matching logic
- `audio/test_samples/` — WAV files for testing (gitignored if large)
- `audio/results/` — confusion matrices, plots
- `vision/preprocess.py` — image resize/grayscale conversion for Edge Impulse
- `vision/data_collection_log.md` — log of every data collection session
- `vision/datasets/` — gitignored, metadata only tracked

## Setup

```bash
cd prototyping
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Dependencies (requirements.txt)

```
numpy
scipy
librosa
matplotlib
mido
python-rtmidi
Pillow
opencv-python
```
