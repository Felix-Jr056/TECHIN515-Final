"""
onset_detect.py -- Spectral flux onset detection for piano sequences

Usage:
    python onset_detect.py <wav_file>                    # detect and print onsets
    python onset_detect.py <wav_file> --ref onsets.csv   # evaluate against ground truth
    python onset_detect.py <wav_file> --plot             # save waveform+onset plot

Ground truth CSV format (one onset per line):
    onset_time_s
    0.123
    0.456

[audio] Member A -- pre-hardware prototype
"""

import argparse
import csv
import os
import sys

import librosa
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Spectral flux
# ---------------------------------------------------------------------------

def spectral_flux(
    y: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """Compute half-wave rectified spectral flux envelope.

    Args:
        y:          Mono audio signal.
        sr:         Sample rate (Hz).
        n_fft:      FFT window size.
        hop_length: Hop between frames.

    Returns:
        1-D array of flux values, one per frame.
    """
    stft = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    # Half-wave rectified difference: only positive increases in energy
    diff = np.diff(stft, axis=1, prepend=stft[:, :1])
    flux = np.sum(np.maximum(0.0, diff), axis=0)
    return flux


# ---------------------------------------------------------------------------
# Onset detection
# ---------------------------------------------------------------------------

def detect_onsets(
    y: np.ndarray,
    sr: int,
    n_fft: int = 2048,
    hop_length: int = 512,
    threshold_delta: float = 1.5,
    min_interval_ms: float = 50.0,
) -> np.ndarray:
    """Detect onset times using spectral flux + adaptive threshold.

    Args:
        y:                Mono audio signal.
        sr:               Sample rate (Hz).
        n_fft:            FFT window size.
        hop_length:       Hop between frames.
        threshold_delta:  Threshold = mean + delta * std of flux.
        min_interval_ms:  Minimum gap between onsets (ms).

    Returns:
        Array of onset times in seconds.
    """
    flux = spectral_flux(y, sr, n_fft=n_fft, hop_length=hop_length)

    threshold = flux.mean() + threshold_delta * flux.std()
    min_frames = int((min_interval_ms / 1000.0) * sr / hop_length)

    # Peak picking: local maxima above threshold, respecting min interval
    onsets = []
    last_frame = -min_frames
    for i in range(1, len(flux) - 1):
        if (
            flux[i] > threshold
            and flux[i] >= flux[i - 1]
            and flux[i] >= flux[i + 1]
            and (i - last_frame) >= min_frames
        ):
            onsets.append(i)
            last_frame = i

    times = librosa.frames_to_time(np.array(onsets), sr=sr, hop_length=hop_length)
    return times


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_onsets(
    detected: np.ndarray,
    reference: np.ndarray,
    tolerance_ms: float = 50.0,
) -> dict:
    """Compare detected onsets against reference times.

    An onset is a true positive if it falls within tolerance_ms of a reference.
    Each reference onset can only be matched once (greedy, nearest-first).

    Args:
        detected:      Array of detected onset times (seconds).
        reference:     Array of reference onset times (seconds).
        tolerance_ms:  Match window in milliseconds.

    Returns:
        Dict with keys: tp, fp, fn, precision, recall, f1.
    """
    tol = tolerance_ms / 1000.0
    matched_ref = set()
    tp = 0

    for d in sorted(detected):
        best_dist = tol + 1.0
        best_idx = -1
        for i, r in enumerate(reference):
            if i in matched_ref:
                continue
            dist = abs(d - r)
            if dist <= tol and dist < best_dist:
                best_dist = dist
                best_idx = i
        if best_idx >= 0:
            tp += 1
            matched_ref.add(best_idx)

    fp = len(detected) - tp
    fn = len(reference) - tp
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {"tp": tp, "fp": fp, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1}


def load_reference_csv(path: str) -> np.ndarray:
    """Load reference onset times from a CSV with header 'onset_time_s'."""
    times = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row["onset_time_s"]))
    return np.array(sorted(times))


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_onset_analysis(
    y: np.ndarray,
    sr: int,
    onsets: np.ndarray,
    output_path: str,
    reference: np.ndarray = None,
) -> None:
    """Save a waveform plot with detected (and optional reference) onset markers."""
    times = np.linspace(0, len(y) / sr, len(y))
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(times, y, color="steelblue", linewidth=0.5, alpha=0.8, label="Waveform")

    for i, t in enumerate(onsets):
        ax.axvline(t, color="red", linewidth=1.0, alpha=0.8,
                   label="Detected" if i == 0 else None)

    if reference is not None:
        for i, t in enumerate(reference):
            ax.axvline(t, color="green", linewidth=1.0, linestyle="--", alpha=0.7,
                       label="Reference" if i == 0 else None)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Onset Detection -- {len(onsets)} onsets found")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Plot saved to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Spectral flux onset detection for piano audio"
    )
    parser.add_argument("wav_file", help="Input WAV file")
    parser.add_argument(
        "--ref", metavar="CSV", help="Reference onset CSV (column: onset_time_s)"
    )
    parser.add_argument(
        "--plot", action="store_true", help="Save waveform + onset plot"
    )
    parser.add_argument(
        "--results",
        metavar="RESULTS_DIR",
        default=os.path.join(os.path.dirname(__file__), "results"),
        help="Output directory for plots (default: ./results/)",
    )
    parser.add_argument(
        "--delta", type=float, default=1.5,
        help="Threshold = mean + delta*std of spectral flux (default 1.5)"
    )
    parser.add_argument(
        "--min-interval", type=float, default=50.0,
        help="Minimum inter-onset interval in ms (default 50)"
    )
    parser.add_argument(
        "--tolerance", type=float, default=50.0,
        help="Evaluation match tolerance in ms (default 50)"
    )
    args = parser.parse_args()

    try:
        y, sr = librosa.load(args.wav_file, sr=None, mono=True)
    except Exception as exc:
        print(f"Error loading {args.wav_file}: {exc}", file=sys.stderr)
        sys.exit(1)

    onsets = detect_onsets(y, sr, threshold_delta=args.delta,
                           min_interval_ms=args.min_interval)

    print(f"File:    {args.wav_file}")
    print(f"SR:      {sr} Hz  |  Duration: {len(y)/sr:.2f}s")
    print(f"Onsets:  {len(onsets)} detected")
    for i, t in enumerate(onsets):
        print(f"  [{i+1:3d}]  {t:.3f}s")

    reference = None
    if args.ref:
        reference = load_reference_csv(args.ref)
        metrics = evaluate_onsets(onsets, reference, tolerance_ms=args.tolerance)
        print(f"\nEvaluation (tolerance={args.tolerance}ms):")
        print(f"  TP={metrics['tp']}  FP={metrics['fp']}  FN={metrics['fn']}")
        print(f"  Precision={metrics['precision']:.3f}  "
              f"Recall={metrics['recall']:.3f}  "
              f"F1={metrics['f1']:.3f}")

    if args.plot:
        out = os.path.join(args.results, "onset_analysis.png")
        plot_onset_analysis(y, sr, onsets, out, reference=reference)


if __name__ == "__main__":
    main()
