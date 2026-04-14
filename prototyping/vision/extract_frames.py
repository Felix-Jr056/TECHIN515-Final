"""
extract_frames.py -- Extract frames from a posture recording video

Film 30 seconds of each hand posture on a phone or webcam, then run this
script to extract frames at a fixed interval. Feed the output directly into
preprocess.py for Edge Impulse upload.

Usage:
    python extract_frames.py <video.mp4> <output_dir/> [--interval 500]
    python extract_frames.py piano_correct.mp4 datasets/raw/correct/ --interval 500
    python extract_frames.py piano_wrist.mp4 datasets/raw/wrist_dropped/ --prefix s02

Output filenames: {prefix}_{sample_index:04d}.jpg
  e.g. s01_0000.jpg, s01_0001.jpg, ...
  (sample_index is sequential count of saved frames, not the video frame index)

[vision] Member B -- pre-hardware prototype
"""

import argparse
import glob
import math
import os
import sys

import cv2


def extract_frames(
    video_path: str,
    output_dir: str,
    interval_ms: int = 500,
    prefix: str = "s01",
    max_frames: int = 0,
) -> int:
    """Extract frames from a video at a fixed time interval using sequential read.

    Uses sequential frame reading (not seek) for reliable extraction from
    compressed video formats (H.264/MP4) as produced by phones and webcams.

    Args:
        video_path:  Path to input video file (MP4, MOV, AVI, etc.).
        output_dir:  Directory to save extracted JPEG frames.
        interval_ms: Time between extracted frames in milliseconds.
        prefix:      Filename prefix / session ID (e.g. 's01').
        max_frames:  Stop after this many frames (0 = no limit).

    Returns:
        Number of frames written.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Guard against NaN/0 fps from some codecs
    if not math.isfinite(fps) or fps <= 0:
        print(f"  [warn] Could not read FPS from video; assuming 30 fps", file=sys.stderr)
        fps = 30.0

    duration_s = total_frames / fps if fps > 0 else 0

    print(f"Video:    {video_path}")
    print(f"FPS:      {fps:.1f}  |  Frames: {total_frames}  |  Duration: {duration_s:.1f}s")
    print(f"Interval: {interval_ms}ms  |  Prefix: {prefix}")

    os.makedirs(output_dir, exist_ok=True)

    # Warn if existing files with this prefix will be overwritten
    existing = glob.glob(os.path.join(output_dir, f"{prefix}_*.jpg"))
    if existing:
        print(f"  [warn] {len(existing)} existing file(s) with prefix '{prefix}' "
              f"in {output_dir}/ will be overwritten.", file=sys.stderr)

    frame_step = max(1, int(fps * interval_ms / 1000.0))
    count = 0      # sequential index of saved samples
    read_idx = 0   # video frame index (every frame read sequentially)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if read_idx % frame_step == 0:
            out_path = os.path.join(output_dir, f"{prefix}_{count:04d}.jpg")
            cv2.imwrite(out_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            count += 1

            if max_frames > 0 and count >= max_frames:
                break

        read_idx += 1

    cap.release()
    print(f"Extracted {count} frames to {output_dir}/")
    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract frames from a posture video at fixed intervals"
    )
    parser.add_argument("video", help="Input video file (MP4, MOV, AVI)")
    parser.add_argument("output_dir", help="Directory to save extracted frames")
    parser.add_argument(
        "--interval", type=int, default=500, metavar="MS",
        help="Time between frames in milliseconds (default 500 = ~2 samples/s)"
    )
    parser.add_argument(
        "--prefix", type=str, default="s01",
        help="Filename prefix / session ID (default 's01')"
    )
    parser.add_argument(
        "--max-frames", type=int, default=0, metavar="N",
        help="Stop after N frames (default 0 = no limit)"
    )
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval must be a positive number of milliseconds")

    try:
        extract_frames(
            args.video,
            args.output_dir,
            interval_ms=args.interval,
            prefix=args.prefix,
            max_frames=args.max_frames,
        )
    except IOError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    parent = os.path.dirname(os.path.abspath(args.output_dir))
    print(f"\nNext step:")
    print(f"  python preprocess.py {parent}/ datasets/processed/")


if __name__ == "__main__":
    main()
