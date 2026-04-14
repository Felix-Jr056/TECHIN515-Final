"""
plot_pitch_onsets.py -- Combined pitch + onset visualization

Usage:
    python plot_pitch_onsets.py <wav_file> [--output path] [--clip SECONDS]

Generates a waveform plot with onset markers (red lines) and pitch labels
(e.g. "C4") annotated above each onset.

[audio] Member A -- pre-hardware prototype
"""

import argparse
import os
import sys

import librosa
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np

from onset_detect import detect_onsets
from pitch_detect import _find_sustained_frame, freq_to_note, hps_pitch


def plot_pitch_onsets(
    y: np.ndarray,
    sr: int,
    onsets: np.ndarray,
    labels: list[str],
    output_path: str,
    clip_end: float,
) -> None:
    """Save waveform plot with onset markers and pitch labels."""
    clip_samples = int(clip_end * sr)
    t_axis = np.linspace(0, clip_end, clip_samples)
    y_clip = y[:clip_samples]

    fig, ax = plt.subplots(figsize=(18, 5))
    ax.plot(t_axis, y_clip, color="steelblue", linewidth=0.4, alpha=0.75,
            label="Waveform")

    amp_peak = np.max(np.abs(y_clip)) * 1.05

    for i, (t, label) in enumerate(zip(onsets, labels)):
        ax.axvline(t, color="red", linewidth=0.9, alpha=0.7,
                   label="Onset" if i == 0 else None)
        # Alternate label height to reduce overlap on closely-spaced onsets
        y_text = amp_peak * (1.05 if i % 2 == 0 else 1.25)
        txt = ax.text(
            t, y_text, label,
            fontsize=7, ha="center", va="bottom",
            color="crimson", fontweight="bold", clip_on=False,
        )
        txt.set_path_effects([pe.withStroke(linewidth=2, foreground="white")])

    ax.set_xlim(0, clip_end)
    ax.set_ylim(-amp_peak * 1.1, amp_peak * 1.6)
    ax.set_xlabel("Time (s)", fontsize=11)
    ax.set_ylabel("Amplitude", fontsize=11)
    ax.set_title(
        f"Pitch + Onset Detection — first {clip_end:.0f}s  "
        f"({len(onsets)} onsets labeled)",
        fontsize=12,
    )
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="x", linestyle=":", alpha=0.4)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combined pitch + onset visualization for piano audio"
    )
    parser.add_argument("wav_file", help="Input WAV file")
    parser.add_argument(
        "--output",
        metavar="PATH",
        default=os.path.join(os.path.dirname(__file__), "results",
                             "pitch_onset_visualization.png"),
        help="Output PNG path (default: results/pitch_onset_visualization.png)",
    )
    parser.add_argument(
        "--clip", type=float, default=20.0,
        help="Only visualize the first N seconds (default: 20.0)",
    )
    parser.add_argument(
        "--delta", type=float, default=1.5,
        help="Onset threshold delta (default 1.5)",
    )
    parser.add_argument(
        "--min-interval", type=float, default=50.0,
        help="Minimum inter-onset interval in ms (default 50)",
    )
    args = parser.parse_args()

    try:
        y, sr = librosa.load(args.wav_file, sr=None, mono=True)
    except Exception as exc:
        print(f"Error loading {args.wav_file}: {exc}", file=sys.stderr)
        sys.exit(1)

    duration = len(y) / sr
    clip_end = min(args.clip, duration)

    onsets = detect_onsets(y, sr, threshold_delta=args.delta,
                           min_interval_ms=args.min_interval)
    onsets_clip = onsets[onsets <= clip_end]

    print(f"File:     {args.wav_file}")
    print(f"SR:       {sr} Hz  |  Duration: {duration:.2f}s  |  Clipped to: {clip_end:.1f}s")
    print(f"Onsets:   {len(onsets)} total, {len(onsets_clip)} in first {clip_end:.1f}s")

    # Detect pitch at each onset using a 700ms window
    n_fft = 4096
    labels = []
    for t in onsets_clip:
        start = int(t * sr)
        end = min(int((t + 0.7) * sr), len(y))
        segment = y[start:end]
        if len(segment) >= n_fft:
            frame = _find_sustained_frame(segment, sr, n_fft)
        else:
            frame = np.pad(segment, (0, max(0, n_fft - len(segment))))
        freq = hps_pitch(frame, sr, n_fft=n_fft)
        note = freq_to_note(freq)
        labels.append(note)
        print(f"  {t:.3f}s  ->  {note}")

    plot_pitch_onsets(y, sr, onsets_clip, labels, args.output, clip_end)


if __name__ == "__main__":
    main()
