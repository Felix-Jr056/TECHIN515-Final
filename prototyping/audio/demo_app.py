"""
demo_app.py -- Flask web demo for the audio analysis pipeline

Usage:
    cd prototyping/audio
    python demo_app.py
    # open http://localhost:5000

Routes:
    GET  /         — serve the HTML interface
    POST /analyze  — accept WAV upload, return JSON analysis

[audio] Member A -- pre-hardware prototype
"""

import base64
import io
import os
import sys
import tempfile

import librosa
import matplotlib
matplotlib.use("Agg")   # non-interactive backend — must come before pyplot import
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, jsonify, render_template, request

from onset_detect import detect_onsets
from pitch_detect import _find_sustained_frame, freq_to_note, hps_pitch


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB upload limit


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def _detect_pitch_in_segment(segment: np.ndarray, sr: int, n_fft: int = 4096) -> str:
    """Run HPS on a single audio segment, return note name."""
    if len(segment) >= n_fft:
        frame = _find_sustained_frame(segment, sr, n_fft)
    else:
        frame = np.pad(segment, (0, max(0, n_fft - len(segment))))
    freq = hps_pitch(frame, sr, n_fft=n_fft)
    return freq_to_note(freq)


def _build_plot_b64(
    y: np.ndarray,
    sr: int,
    onsets: np.ndarray,
    labels: list[str],
    clip_end: float,
) -> str:
    """Return a base64-encoded PNG of the waveform + onset + pitch labels."""
    import matplotlib.patheffects as pe

    clip_samples = int(clip_end * sr)
    t_axis = np.linspace(0, clip_end, clip_samples)
    y_clip = y[:clip_samples]
    onsets_clip = onsets[onsets <= clip_end]
    labels_clip = labels[: len(onsets_clip)]

    fig, ax = plt.subplots(figsize=(14, 4), facecolor="#0a0e0a")
    ax.set_facecolor("#0a0e0a")

    ax.plot(t_axis, y_clip, color="#39ff6a", linewidth=0.5, alpha=0.7)

    amp_peak = np.max(np.abs(y_clip)) * 1.05 if y_clip.size else 1.0

    for i, (t, label) in enumerate(zip(onsets_clip, labels_clip)):
        ax.axvline(t, color="#ff4444", linewidth=0.9, alpha=0.7)
        y_text = amp_peak * (1.05 if i % 2 == 0 else 1.28)
        txt = ax.text(
            t, y_text, label,
            fontsize=6.5, ha="center", va="bottom",
            color="#ff6868", fontweight="bold", clip_on=False,
            fontfamily="monospace",
        )
        txt.set_path_effects([pe.withStroke(linewidth=2, foreground="#0a0e0a")])

    ax.set_xlim(0, clip_end)
    ax.set_ylim(-amp_peak * 1.1, amp_peak * 1.7)
    ax.tick_params(colors="#4a6a4a", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1e331e")
    ax.set_xlabel("Time (s)", color="#4a6a4a", fontsize=9, fontfamily="monospace")
    ax.set_ylabel("Amplitude", color="#4a6a4a", fontsize=9, fontfamily="monospace")
    ax.set_title(
        f"Onset & Pitch Detection  —  first {clip_end:.0f}s  "
        f"({len(onsets_clip)} onsets)",
        color="#39ff6a", fontsize=10, fontfamily="monospace",
    )
    ax.grid(axis="x", color="#1e331e", linestyle=":", linewidth=0.5)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".wav"):
        return jsonify({"error": "Only .wav files are supported"}), 400

    # Save to a temp file (librosa needs a path, not a stream)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
        f.save(tmp_path)

    try:
        y, sr = librosa.load(tmp_path, sr=None, mono=True)
    except Exception as exc:
        os.unlink(tmp_path)
        return jsonify({"error": f"Could not load audio: {exc}"}), 422
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    duration = len(y) / sr

    # Onset detection
    onsets = detect_onsets(y, sr)

    # Pitch detection at each onset (700ms window per note)
    n_fft = 4096
    notes_out = []
    for t in onsets:
        start = int(t * sr)
        end = min(int((t + 0.7) * sr), len(y))
        note = _detect_pitch_in_segment(y[start:end], sr, n_fft=n_fft)
        notes_out.append({"time": round(float(t), 3), "note": note})

    labels = [n["note"] for n in notes_out]
    unique_notes = sorted(set(labels), key=lambda n: (
        int(n[-1]) if n[-1].isdigit() else 0,
        n[:-1] if n != "N/A" else "ZZ",
    ))

    # Plot — clip to first 30s or full duration, whichever is shorter
    clip_end = min(30.0, duration)
    plot_b64 = _build_plot_b64(y, sr, onsets, labels, clip_end)

    return jsonify({
        "notes": notes_out,
        "plot_b64": plot_b64,
        "total_onsets": len(onsets),
        "unique_notes": unique_notes,
    })


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
