"""
midi_compare.py -- MIDI reference parsing and note/rhythm comparison

Purpose:
    Load a MIDI reference file, extract note events with timestamps, and
    compare them against the detected note/onset data produced by
    onset_detect.py and pitch_detect.py.

    Typical workflow:
        reference = load_midi("reference.mid")       # [(note_name, time_s), ...]
        note_metrics = compare_notes(detected, reference)
        rhythm_metrics = compare_rhythm(detected_onsets, reference_onsets)

[audio] Member A -- pre-hardware prototype
"""

import argparse
import os
import sys

import mido
import numpy as np


# ---------------------------------------------------------------------------
# MIDI loading
# ---------------------------------------------------------------------------

def load_midi(path: str) -> list[tuple[str, float]]:
    """Load a MIDI file and extract note-on events with absolute timestamps.

    Converts MIDI tick times to seconds using the file's tempo map.
    Note numbers are mapped to note names matching the pitch_detect.py
    convention (e.g. 60 -> 'C4', 61 -> 'Cs4').

    Args:
        path: Path to the MIDI file (.mid / .midi).

    Returns:
        List of (note_name, onset_time_sec) tuples, sorted by onset time.
        Returns an empty list if the file has no note-on events.
    """
    pass


# ---------------------------------------------------------------------------
# Note comparison
# ---------------------------------------------------------------------------

def compare_notes(
    detected: list[tuple[str, float]],
    reference: list[tuple[str, float]],
    timing_tolerance_ms: float = 100.0,
) -> dict:
    """Compare a detected note sequence against a MIDI reference.

    A detection is a true positive if its note name matches a reference note
    AND its onset falls within timing_tolerance_ms of that reference onset.
    Each reference note may only be matched once (greedy, nearest-first).

    Args:
        detected:             List of (note_name, onset_time_sec) from the
                              audio pipeline.
        reference:            List of (note_name, onset_time_sec) from
                              load_midi().
        timing_tolerance_ms:  Maximum allowed onset offset for a match (ms).

    Returns:
        Dict with keys:
            tp         -- true positives (correct note + timing)
            fp         -- false positives (detected but not in reference)
            fn         -- false negatives (reference note not detected)
            precision  -- tp / (tp + fp)
            recall     -- tp / (tp + fn)
            f1         -- harmonic mean of precision and recall
    """
    pass


# ---------------------------------------------------------------------------
# Rhythm comparison
# ---------------------------------------------------------------------------

def compare_rhythm(
    detected_onsets: np.ndarray,
    reference_onsets: np.ndarray,
    tolerance_ms: float = 100.0,
) -> dict:
    """Compare onset timing against a reference rhythm.

    Matches each detected onset to the nearest reference onset within
    tolerance_ms.  Computes timing error statistics for matched pairs.

    Args:
        detected_onsets:   1-D array of detected onset times (seconds).
        reference_onsets:  1-D array of reference onset times (seconds).
        tolerance_ms:      Match window in milliseconds (default 100).

    Returns:
        Dict with keys:
            matched        -- number of matched onset pairs
            missed         -- reference onsets with no detection match
            extra          -- detected onsets with no reference match
            mean_error_ms  -- mean absolute timing error for matched pairs (ms)
            std_error_ms   -- std of timing error for matched pairs (ms)
            max_error_ms   -- worst-case timing error among matched pairs (ms)
    """
    pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare detected notes/onsets against a MIDI reference"
    )
    parser.add_argument("midi_file", help="Reference MIDI file (.mid)")
    parser.add_argument(
        "results_json",
        help="JSON file of detected notes (output from onset_detect.py --slice)",
    )
    parser.add_argument(
        "--tolerance", type=float, default=100.0,
        help="Onset match tolerance in ms (default 100)",
    )
    parser.add_argument(
        "--results",
        metavar="RESULTS_DIR",
        default=os.path.join(os.path.dirname(__file__), "results"),
        help="Directory for output reports (default: ./results/)",
    )
    args = parser.parse_args()

    # TODO: load results_json, call load_midi(), compare_notes(), compare_rhythm()
    print("[midi_compare] stub — not yet implemented")
    sys.exit(0)


if __name__ == "__main__":
    main()
