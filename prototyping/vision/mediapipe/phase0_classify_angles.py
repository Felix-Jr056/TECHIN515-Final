"""
Phase 0 — Feature-engineered keypoint classifier.

Reads landmarks.json from phase0_landmark_check.py, computes geometric
features that directly encode hand posture (finger joint angles, knuckle
plane elevation, wrist-knuckle vector), then refits the same logistic
regression and compares to the raw-coordinate baseline.

Rationale: the 63-dim raw-coord baseline confused fingers_flat with
collapsed_nuckles because both share similar wrist/fingertip positions
at side view. Joint angles separate finger curl from finger position.
"""

import os, json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (confusion_matrix, classification_report,
                             ConfusionMatrixDisplay)
from sklearn.decomposition import PCA

JSON_PATH   = os.path.join(os.path.dirname(__file__), "results/phase0/landmarks.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results/phase0")

# MediaPipe hand topology: 21 keypoints
# 0=wrist, 1-4=thumb, 5-8=index, 9-12=middle, 13-16=ring, 17-20=pinky
FINGERS = {
    "thumb":  [1, 2, 3, 4],
    "index":  [5, 6, 7, 8],
    "middle": [9, 10, 11, 12],
    "ring":   [13, 14, 15, 16],
    "pinky":  [17, 18, 19, 20],
}
MCP_IDS = [5, 9, 13, 17]   # index, middle, ring, pinky MCPs (palm knuckles)


def angle(a, b, c):
    """Angle at vertex b formed by points a-b-c, in radians."""
    ba = a - b
    bc = c - b
    nba = np.linalg.norm(ba) + 1e-8
    nbc = np.linalg.norm(bc) + 1e-8
    cos = np.clip(np.dot(ba, bc) / (nba * nbc), -1.0, 1.0)
    return float(np.arccos(cos))


def featurize(lms_list):
    """Compute geometric features from one set of 21 hand keypoints."""
    pts = np.array(lms_list, dtype=np.float32)        # 21×3
    wrist = pts[0]

    # Normalize: center on wrist, scale by palm size (wrist→middle MCP)
    palm_scale = np.linalg.norm(pts[9] - wrist) + 1e-8
    pts_n = (pts - wrist) / palm_scale

    feats = []

    # 1. Finger joint angles (3 per finger × 5 fingers = 15)
    #    For each finger: MCP angle, PIP angle, DIP angle
    #    Smaller MCP angle = curled at base; smaller PIP/DIP = curled mid/tip
    for joints in FINGERS.values():
        mcp, pip, dip, tip = joints
        feats.append(angle(pts[0],   pts[mcp], pts[pip]))   # wrist-MCP-PIP
        feats.append(angle(pts[mcp], pts[pip], pts[dip]))   # MCP-PIP-DIP
        feats.append(angle(pts[pip], pts[dip], pts[tip]))   # PIP-DIP-TIP

    # 2. Palm plane fit: estimate normal from 3 MCPs + wrist, project all MCPs.
    #    Knuckle elevation above the plane discriminates "collapsed knuckles"
    #    (knuckles drop into the plane) from "fingers flat" (knuckles stay up).
    palm_pts = np.stack([pts_n[0], pts_n[5], pts_n[17]])  # wrist, index-MCP, pinky-MCP
    v1 = palm_pts[1] - palm_pts[0]
    v2 = palm_pts[2] - palm_pts[0]
    normal = np.cross(v1, v2)
    normal = normal / (np.linalg.norm(normal) + 1e-8)
    for mcp in MCP_IDS:
        feats.append(float(np.dot(pts_n[mcp] - palm_pts[0], normal)))

    # 3. Wrist-to-middle-MCP vector direction (wrist_dropped indicator):
    #    angle of palm vector relative to vertical (image-y) axis.
    palm_vec = pts_n[9] - pts_n[0]
    feats.append(float(np.arctan2(palm_vec[1], palm_vec[0])))   # in-plane tilt
    feats.append(float(np.arctan2(palm_vec[2], np.linalg.norm(palm_vec[:2]) + 1e-8)))  # out-of-plane

    # 4. Fingertip-to-palm-plane distances (5): how much each finger extends
    for joints in FINGERS.values():
        tip = joints[-1]
        feats.append(float(np.dot(pts_n[tip] - palm_pts[0], normal)))

    return np.array(feats, dtype=np.float32)


# ── load + featurize ──────────────────────────────────────────────────────────
with open(JSON_PATH) as f:
    records = json.load(f)

print(f"Loaded {len(records)} detected samples")

X, y_raw = [], []
for r in records:
    X.append(featurize(r["landmarks"]))
    y_raw.append(r["class"])

X = np.array(X)
le = LabelEncoder()
y = le.fit_transform(y_raw)
classes = le.classes_

print(f"Feature dim: {X.shape[1]}")
print(f"Classes: {list(classes)}")
print(f"Samples per class: { {c: int((y==i).sum()) for i,c in enumerate(classes)} }")
print()

# ── cross-validated logistic regression ───────────────────────────────────────
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0))
y_pred = cross_val_predict(clf, X, y, cv=cv)

print("=== Cross-validated classification report (engineered features) ===")
print(classification_report(y, y_pred, target_names=classes))

# ── confusion matrix + PCA ────────────────────────────────────────────────────
cm = confusion_matrix(y, y_pred)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

disp = ConfusionMatrixDisplay(cm, display_labels=classes)
disp.plot(ax=axes[0], colorbar=False)
axes[0].set_title(f"Confusion matrix (5-fold CV)\n"
                  f"Engineered {X.shape[1]}-dim features")

pca = PCA(n_components=2)
X2 = pca.fit_transform(StandardScaler().fit_transform(X))
colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
for i, cls in enumerate(classes):
    mask = y == i
    axes[1].scatter(X2[mask, 0], X2[mask, 1],
                    label=cls, alpha=0.8, s=50,
                    color=colors[i % len(colors)],
                    edgecolors="white", linewidths=0.5)
axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
axes[1].set_title("PCA of engineered features")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
out_path = os.path.join(RESULTS_DIR, "phase0_results_engineered.png")
plt.savefig(out_path, dpi=150)
print(f"Plot saved to: {out_path}")

acc = (y == y_pred).mean()
print(f"\n=== Verdict ===")
print(f"  CV accuracy: {acc*100:.1f}%  (raw-coord baseline was 69.5%)")
if acc >= 0.85:
    print("  ✅ Above 85% — proceed to Phase 1 (Model Maker training)")
elif acc >= 0.75:
    print("  ☑️  Above raw baseline; close to gate. Try more samples or tune.")
else:
    print("  ⚠️  No major gain; image-CNN (Edge Impulse) likely needed.")
