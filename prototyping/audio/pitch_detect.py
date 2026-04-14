"""
pitch_detect.py — FFT + Harmonic Product Spectrum pitch detection

Usage:
    python pitch_detect.py <wav_file>              # single file
    python pitch_detect.py --eval test_samples/    # batch evaluation + confusion matrix

Test sample filename convention: {NoteName}_{index}.wav
  e.g. C4_01.wav, Fs5_02.wav (Fs = F-sharp, Bb = B-flat)

[audio] Member A — pre-hardware prototype
"""

import argparse
import os
import sys

import librosa
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix


# ---------------------------------------------------------------------------
# Note mapping helpers
# ---------------------------------------------------------------------------

NOTE_NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]
# Cs = C-sharp, Ds = D-sharp, etc.  Match filename convention.

C3_MIDI = 48   # C3 = MIDI 48
C6_MIDI = 84   # C6 = MIDI 84 (inclusive)


def midi_to_note(midi: int) -> str:
    """Return note name string for a MIDI number (e.g. 60 → 'C4')."""
    octave = (midi // 12) - 1
    name = NOTE_NAMES[midi % 12]
    return f"{name}{octave}"


def freq_to_midi(freq: float) -> int:
    """Convert frequency (Hz) to nearest MIDI note number."""
    if freq <= 0:
        return -1
    return int(round(12 * np.log2(freq / 440.0) + 69))


def freq_to_note(freq: float) -> str:
    """Convert frequency (Hz) to note name.  Returns 'N/A' if outside C3-C6."""
    midi = freq_to_midi(freq)
    if midi < C3_MIDI or midi > C6_MIDI:
        return "N/A"
    return midi_to_note(midi)


def note_name_from_filename(filename: str) -> str:
    """Extract ground-truth note name from filename, e.g. 'C4_01.wav' -> 'C4'."""
    base = os.path.splitext(os.path.basename(filename))[0]
    return base.rsplit("_", 1)[0]  # everything before the last underscore


# ---------------------------------------------------------------------------
# HPS core
# ---------------------------------------------------------------------------

def hps_pitch(
    frame: np.ndarray,
    sr: int,
    n_fft: int = 4096,
    n_harmonics: int = 5,
) -> float:
    """Return the fundamental frequency (Hz) for a single audio frame via HPS.

    Args:
        frame:       1-D array of audio samples.
        sr:          Sample rate (Hz).
        n_fft:       FFT size (zero-padded to 2*n_fft for finer resolution).
        n_harmonics: Number of harmonic copies to multiply (2-5 typical).

    Returns:
        Estimated fundamental frequency in Hz, or 0.0 on failure.
    """
    pad_to = n_fft * 2  # zero-pad for finer frequency bins

    windowed = frame * np.hanning(len(frame))
    spectrum = np.abs(np.fft.rfft(windowed, n=pad_to))

    # Build HPS: downsample by h, multiply element-wise
    hps = spectrum.copy()
    for h in range(2, n_harmonics + 1):
        decimated = spectrum[::h]
        hps[: len(decimated)] *= decimated

    # Search only in piano C3-C6 range (130-1047 Hz)
    freq_resolution = sr / pad_to
    bin_lo = max(1, int(130.0 / freq_resolution))
    bin_hi = int(1100.0 / freq_resolution)
    bin_hi = min(bin_hi, len(hps) - 1)

    peak_bin = np.argmax(hps[bin_lo:bin_hi]) + bin_lo
    fundamental = peak_bin * freq_resolution
    return fundamental


# ---------------------------------------------------------------------------
# File-level detection
# ---------------------------------------------------------------------------

def _find_sustained_frame(y: np.ndarray, sr: int, n_fft: int) -> np.ndarray:
    """Return the highest-energy n_fft-length frame (captures the note body)."""
    hop = n_fft // 2
    best_energy = -1.0
    best_frame = y[:n_fft] if len(y) >= n_fft else np.pad(y, (0, n_fft - len(y)))

    for start in range(0, len(y) - n_fft + 1, hop):
        chunk = y[start : start + n_fft]
        energy = float(np.dot(chunk, chunk))
        if energy > best_energy:
            best_energy = energy
            best_frame = chunk

    return best_frame


def detect_pitch_in_file(filepath: str, sr: int = 44100, n_fft: int = 4096) -> str:
    """Load a WAV file, detect its pitch, return note name (e.g. 'C4').

    Returns 'N/A' if pitch is outside C3-C6 or file cannot be read.
    """
    try:
        y, _ = librosa.load(filepath, sr=sr, mono=True)
    except Exception as exc:
        print(f"  [warn] could not load {filepath}: {exc}", file=sys.stderr)
        return "N/A"

    frame = _find_sustained_frame(y, sr, n_fft)
    freq = hps_pitch(frame, sr, n_fft=n_fft)
    return freq_to_note(freq)


# ---------------------------------------------------------------------------
# Batch evaluation
# ---------------------------------------------------------------------------

def run_evaluation(samples_dir: str, results_dir: str) -> None:
    """Run pitch detection on all WAV files under samples_dir.

    Expects filenames like C4_01.wav (ground truth = 'C4').
    Prints a classification report and saves a confusion matrix PNG.
    """
    wav_files = [
        os.path.join(samples_dir, f)
        for f in sorted(os.listdir(samples_dir))
        if f.lower().endswith(".wav")
    ]

    if not wav_files:
        print(f"No WAV files found in {samples_dir}", file=sys.stderr)
        sys.exit(1)

    y_true, y_pred = [], []

    print(f"Evaluating {len(wav_files)} files in {samples_dir}...\n")
    for path in wav_files:
        true_note = note_name_from_filename(path)
        pred_note = detect_pitch_in_file(path)
        match = "OK" if pred_note == true_note else "XX"
        print(f"  [{match}] {os.path.basename(path):<20} true={true_note:<5} pred={pred_note}")
        y_true.append(true_note)
        y_pred.append(pred_note)

    # Summary
    correct = sum(t == p for t, p in zip(y_true, y_pred))
    accuracy = correct / len(y_true) * 100
    print(f"\nAccuracy: {correct}/{len(y_true)} = {accuracy:.1f}%")

    labels = sorted(set(y_true) | set(y_pred))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, labels=labels, zero_division=0))

    # Confusion matrix plot
    os.makedirs(results_dir, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(max(6, len(labels)), max(5, len(labels))))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Predicted note")
    ax.set_ylabel("True note")
    ax.set_title(f"Pitch Detection Confusion Matrix  ({accuracy:.1f}% accuracy)")

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if cm[i, j]:
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black", fontsize=7)

    plt.tight_layout()
    out_path = os.path.join(results_dir, "pitch_confusion_matrix.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"\nConfusion matrix saved to {out_path}")

    if accuracy < 90.0:
        print(f"[warn] Accuracy {accuracy:.1f}% is below the 90% verification target.")
    else:
        print(f"[ok]  Accuracy {accuracy:.1f}% meets the >=90% verification target.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="HPS pitch detection for piano notes (C3-C6)"
    )
    parser.add_argument(
        "wav_or_dir",
        nargs="?",
        help="WAV file to analyse, or omit when using --eval",
    )
    parser.add_argument(
        "--eval",
        metavar="SAMPLES_DIR",
        help="Batch evaluation mode: run on every WAV in SAMPLES_DIR",
    )
    parser.add_argument(
        "--results",
        metavar="RESULTS_DIR",
        default=os.path.join(os.path.dirname(__file__), "results"),
        help="Directory for output plots (default: ./results/)",
    )
    parser.add_argument("--sr", type=int, default=44100, help="Sample rate (default 44100)")
    parser.add_argument("--fft", type=int, default=4096, help="FFT window size (default 4096)")
    args = parser.parse_args()

    if args.eval:
        run_evaluation(args.eval, args.results)
    elif args.wav_or_dir:
        note = detect_pitch_in_file(args.wav_or_dir, sr=args.sr, n_fft=args.fft)
        print(f"{args.wav_or_dir} -> {note}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
