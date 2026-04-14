"""
preprocess.py -- Image preprocessing for Edge Impulse (96x96 grayscale)

Usage:
    python preprocess.py datasets/raw/ datasets/processed/
    python preprocess.py datasets/raw/ datasets/processed/ --augment
    python preprocess.py --single input.jpg output.png     # preview single image

Input directory structure:
    datasets/raw/
        correct/
        wrist_dropped/
        fingers_flat/

Output mirrors the structure under the output directory.

[vision] Member B -- pre-hardware prototype
"""

import argparse
import os
import sys

import cv2
import numpy as np

TARGET_SIZE = (96, 96)
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


# ---------------------------------------------------------------------------
# Single-image operations
# ---------------------------------------------------------------------------

def _center_crop(img: np.ndarray) -> np.ndarray:
    """Crop to square using the shorter side, centred."""
    h, w = img.shape[:2]
    side = min(h, w)
    y0 = (h - side) // 2
    x0 = (w - side) // 2
    return img[y0 : y0 + side, x0 : x0 + side]


def preprocess_image(
    input_path: str,
    output_path: str,
    size: tuple = TARGET_SIZE,
) -> None:
    """Load an image, center-crop to square, convert to grayscale, resize, save.

    Args:
        input_path:  Source image (any OpenCV-supported format).
        output_path: Destination path (PNG recommended).
        size:        Output (width, height) in pixels.
    """
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not read image: {input_path}")

    img = _center_crop(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, resized)


# ---------------------------------------------------------------------------
# Augmentation
# ---------------------------------------------------------------------------

def augment_image(img: np.ndarray) -> list:
    """Return augmented variants of a grayscale image (original not included).

    Augmentations: horizontal flip, +-5 deg rotation, +-15% brightness.
    """
    h, w = img.shape
    variants = []

    # Horizontal flip
    variants.append(cv2.flip(img, 1))

    # Rotations
    for angle in (-5, 5):
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        variants.append(rotated)

    # Brightness variation
    for delta in (-0.15, 0.15):
        bright = np.clip(img.astype(np.float32) * (1.0 + delta), 0, 255).astype(np.uint8)
        variants.append(bright)

    return variants


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def batch_preprocess(
    input_dir: str,
    output_dir: str,
    size: tuple = TARGET_SIZE,
    augment: bool = False,
) -> int:
    """Process all images under input_dir, save preprocessed versions to output_dir.

    Preserves subdirectory structure (correct/, wrist_dropped/, fingers_flat/).
    Augmented images are saved with suffixes _flip, _rot-5, _rot5, _bright-15, _bright15.

    Args:
        input_dir:  Root of raw dataset (contains class subdirectories).
        output_dir: Root of processed dataset (created if absent).
        size:       Output image size.
        augment:    If True, also save augmented variants.

    Returns:
        Total number of output images written.
    """
    count = 0
    skipped = 0

    for root, _, files in os.walk(input_dir):
        rel = os.path.relpath(root, input_dir)
        out_root = os.path.join(output_dir, rel)

        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in IMG_EXTS:
                continue

            in_path = os.path.join(root, fname)
            stem = os.path.splitext(fname)[0]

            img = cv2.imread(in_path)
            if img is None:
                print(f"  [skip] cannot read {in_path}", file=sys.stderr)
                skipped += 1
                continue

            img = _center_crop(img)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)

            os.makedirs(out_root, exist_ok=True)
            cv2.imwrite(os.path.join(out_root, f"{stem}.png"), resized)
            count += 1

            if augment:
                suffixes = ["_flip", "_rot-5", "_rot5", "_bright-15", "_bright15"]
                for variant, suffix in zip(augment_image(resized), suffixes):
                    cv2.imwrite(os.path.join(out_root, f"{stem}{suffix}.png"), variant)
                    count += 1

    print(f"Done. {count} images written, {skipped} skipped.")
    return count


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess hand posture images to 96x96 grayscale for Edge Impulse"
    )
    parser.add_argument(
        "input_dir", nargs="?",
        help="Root directory of raw images (with class subdirectories)"
    )
    parser.add_argument(
        "output_dir", nargs="?",
        help="Root directory for processed output"
    )
    parser.add_argument(
        "--augment", action="store_true",
        help="Also save augmented variants (flip, rotate, brightness)"
    )
    parser.add_argument(
        "--single", nargs=2, metavar=("IN", "OUT"),
        help="Process a single image: --single input.jpg output.png"
    )
    args = parser.parse_args()

    if args.single:
        preprocess_image(args.single[0], args.single[1])
        print(f"Saved {args.single[1]}")
    elif args.input_dir and args.output_dir:
        batch_preprocess(args.input_dir, args.output_dir, augment=args.augment)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
