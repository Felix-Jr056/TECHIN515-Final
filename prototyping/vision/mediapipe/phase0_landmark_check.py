"""
Phase 0 — Landmark feasibility check.
Runs MediaPipe HandLandmarker over the existing dataset and reports:
  - Detection rate per class
  - Saves annotated overlay images for visual inspection
"""

import os, urllib.request, json
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

DATASET_DIR = os.path.join(os.path.dirname(__file__), "../datasets/frames")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results/phase0/overlays")
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
MODEL_URL   = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

CLASSES = ["correct", "fingers_flat", "wrist_dropped", "collapsed_nuckles"]
MAX_PER_CLASS = 50  # smoke test cap; set to 0 for no limit

# ── download model if missing ──────────────────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print("Downloading hand_landmarker.task …")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("  done.")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ── build detector ─────────────────────────────────────────────────────────────
base_opts = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
opts = mp_vision.HandLandmarkerOptions(
    base_options=base_opts,
    num_hands=1,
    min_hand_detection_confidence=0.3,   # lenient — side-view is harder
    min_hand_presence_confidence=0.3,
    min_tracking_confidence=0.3,
)
detector = mp_vision.HandLandmarker.create_from_options(opts)

# ── helpers ────────────────────────────────────────────────────────────────────
# Hand connections from MediaPipe hand topology (21 keypoints)
CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),          # thumb
    (0,5),(5,6),(6,7),(7,8),          # index
    (0,9),(9,10),(10,11),(11,12),     # middle
    (0,13),(13,14),(14,15),(15,16),   # ring
    (0,17),(17,18),(18,19),(19,20),   # pinky
    (5,9),(9,13),(13,17),             # palm
]

def draw_landmarks(img_bgr, landmarks):
    h, w = img_bgr.shape[:2]
    out = img_bgr.copy()
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in CONNECTIONS:
        cv2.line(out, pts[a], pts[b], (0, 255, 0), 1)
    for p in pts:
        cv2.circle(out, p, 3, (0, 0, 255), -1)
    return out

# ── run per class ──────────────────────────────────────────────────────────────
summary = {}
all_results = []   # [(class, filename, detected, landmarks_or_None)]

for cls in CLASSES:
    cls_dir = os.path.join(DATASET_DIR, cls)
    if not os.path.isdir(cls_dir):
        print(f"[WARN] {cls_dir} not found, skipping")
        continue

    files = sorted(f for f in os.listdir(cls_dir) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if MAX_PER_CLASS > 0:
        # Evenly spaced subsample across the sorted list (better coverage than first N)
        step = max(1, len(files) // MAX_PER_CLASS)
        files = files[::step][:MAX_PER_CLASS]
    detected = 0
    os.makedirs(os.path.join(RESULTS_DIR, cls), exist_ok=True)

    for fname in files:
        path = os.path.join(cls_dir, fname)
        img_bgr = cv2.imread(path)
        if img_bgr is None:
            continue
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_img  = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        result  = detector.detect(mp_img)

        if result.hand_landmarks:
            detected += 1
            lms = result.hand_landmarks[0]
            overlay = draw_landmarks(img_bgr, lms)
            all_results.append((cls, fname, True, lms))
        else:
            overlay = img_bgr.copy()
            cv2.putText(overlay, "NO HAND", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            all_results.append((cls, fname, False, None))

        out_path = os.path.join(RESULTS_DIR, cls, fname.replace(".jpg", ".png"))
        cv2.imwrite(out_path, overlay)

    summary[cls] = (detected, len(files))
    print(f"  {cls:15s}  {detected:2d}/{len(files)} detected  "
          f"({100*detected/len(files):.0f}%)")

# ── save JSON for phase0_classify_quick.py ────────────────────────────────────
json_path = os.path.join(os.path.dirname(__file__), "results/phase0/landmarks.json")
os.makedirs(os.path.dirname(json_path), exist_ok=True)
records = []
for cls, fname, ok, lms in all_results:
    if ok:
        records.append({
            "class": cls,
            "file":  fname,
            "landmarks": [[lm.x, lm.y, lm.z] for lm in lms],
        })
with open(json_path, "w") as f:
    json.dump(records, f)

# ── final report ───────────────────────────────────────────────────────────────
print("\n=== Phase 0 detection summary ===")
total_det = total_img = 0
for cls, (det, tot) in summary.items():
    bar = "█" * det + "░" * (tot - det)
    print(f"  {cls:15s} [{bar}] {det}/{tot}")
    total_det += det; total_img += tot

overall = 100 * total_det / total_img if total_img else 0
print(f"\n  Overall: {total_det}/{total_img} ({overall:.0f}%)")
if overall >= 80:
    print("  ✅ Detection rate OK — proceed to classify check")
elif overall >= 50:
    print("  ⚠️  Partial detection — inspect overlays, may need camera angle tweak")
else:
    print("  ❌ Low detection — MediaPipe struggles at this camera angle")

print(f"\n  Overlay images saved to: results/phase0/overlays/")
print(f"  Landmark JSON saved to:  results/phase0/landmarks.json")
