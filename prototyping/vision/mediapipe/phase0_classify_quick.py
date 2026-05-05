"""
Phase 0 — Quick keypoint separability check.
Reads landmarks.json from phase0_landmark_check.py, fits a logistic regression,
and reports cross-validated accuracy + confusion matrix + PCA scatter plot.
"""

import os, json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (confusion_matrix, classification_report,
                             ConfusionMatrixDisplay)
from sklearn.decomposition import PCA

JSON_PATH   = os.path.join(os.path.dirname(__file__), "results/phase0/landmarks.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results/phase0")

# ── load ───────────────────────────────────────────────────────────────────────
with open(JSON_PATH) as f:
    records = json.load(f)

print(f"Loaded {len(records)} detected samples")

def normalize(lms):
    """Translate to wrist origin, scale by palm diagonal."""
    pts = np.array(lms, dtype=np.float32)        # 21×3
    wrist = pts[0].copy()
    pts -= wrist
    scale = np.linalg.norm(pts[9] - pts[0]) + 1e-6   # wrist→middle-MCP
    pts /= scale
    return pts.flatten()                          # 63-dim

X, y_raw = [], []
for r in records:
    X.append(normalize(r["landmarks"]))
    y_raw.append(r["class"])

X = np.array(X)
le = LabelEncoder()
y = le.fit_transform(y_raw)
classes = le.classes_

print(f"Classes: {list(classes)}")
print(f"Samples per class: { {c: int((y==i).sum()) for i,c in enumerate(classes)} }")
print()

if len(classes) < 2:
    print("Need at least 2 classes with detections. Exiting.")
    raise SystemExit(1)

# ── cross-validated logistic regression ───────────────────────────────────────
cv = StratifiedKFold(n_splits=min(5, len(y)), shuffle=True, random_state=42)
clf = LogisticRegression(max_iter=1000, C=1.0)
y_pred = cross_val_predict(clf, X, y, cv=cv)

print("=== Cross-validated classification report ===")
print(classification_report(y, y_pred, target_names=classes))

# ── confusion matrix ───────────────────────────────────────────────────────────
cm = confusion_matrix(y, y_pred)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

disp = ConfusionMatrixDisplay(cm, display_labels=classes)
disp.plot(ax=axes[0], colorbar=False)
axes[0].set_title("Confusion matrix (5-fold CV)\nLogistic Regression on 63-dim keypoints")

# ── PCA scatter ────────────────────────────────────────────────────────────────
pca = PCA(n_components=2)
X2  = pca.fit_transform(X)
colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]

for i, cls in enumerate(classes):
    mask = y == i
    axes[1].scatter(X2[mask, 0], X2[mask, 1],
                    label=cls, alpha=0.8, s=60,
                    color=colors[i % len(colors)], edgecolors="white", linewidths=0.5)

axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
axes[1].set_title("PCA of normalized hand keypoints\n(well-separated clusters = good signal)")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
out_path = os.path.join(RESULTS_DIR, "phase0_results.png")
plt.savefig(out_path, dpi=150)
print(f"Plot saved to: {out_path}")
plt.show()

# ── verdict ────────────────────────────────────────────────────────────────────
acc = (y == y_pred).mean()
print(f"\n=== Phase 0 verdict ===")
print(f"  CV accuracy: {acc*100:.1f}%")
if acc >= 0.75:
    print("  ✅ Classes are separable in keypoint space — MediaPipe approach looks viable")
elif acc >= 0.60:
    print("  ⚠️  Marginal separability — may improve with more data or better camera angle")
else:
    print("  ❌ Classes not separable as keypoints — posture differences may be too subtle")
    print("     Consider: different camera angle, feature engineering, or stay with image CNN")
