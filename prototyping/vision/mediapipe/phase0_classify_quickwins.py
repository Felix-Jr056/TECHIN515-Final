"""
Phase 0 — Quick-wins test: non-linear classifiers + per-video CV.

Tests whether the 69.5% raw-coord baseline holds up under:
  (a) stronger non-linear models (RandomForest, SVM-RBF)
  (b) per-video cross-validation (no frame leakage from same clip)

Per-video CV: filenames like "s01_0000.jpg" share session "s01" within a class.
Group ID = "{class}_{session}" — a single MOV's frames stay in one fold.
"""

import os, json, re
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import (StratifiedKFold, GroupKFold,
                                     cross_val_predict)
from sklearn.metrics import classification_report, confusion_matrix

JSON_PATH = os.path.join(os.path.dirname(__file__), "results/phase0/landmarks.json")


def normalize(lms):
    pts = np.array(lms, dtype=np.float32)
    wrist = pts[0].copy()
    pts -= wrist
    scale = np.linalg.norm(pts[9] - pts[0]) + 1e-6
    pts /= scale
    return pts.flatten()


# ── load ──────────────────────────────────────────────────────────────────────
with open(JSON_PATH) as f:
    records = json.load(f)

X, y_raw, groups = [], [], []
sess_re = re.compile(r"^(s\d+)_")
for r in records:
    X.append(normalize(r["landmarks"]))
    y_raw.append(r["class"])
    m = sess_re.match(r["file"])
    sess = m.group(1) if m else "unknown"
    groups.append(f"{r['class']}_{sess}")

X = np.array(X)
le = LabelEncoder()
y = le.fit_transform(y_raw)
groups = np.array(groups)
classes = le.classes_

n_groups = len(set(groups))
print(f"Samples: {len(y)}   Classes: {len(classes)}   Unique videos: {n_groups}")
print(f"Class counts: { {c: int((y==i).sum()) for i,c in enumerate(classes)} }")
print()

# ── classifiers ───────────────────────────────────────────────────────────────
clfs = {
    "LogReg (baseline)":  make_pipeline(StandardScaler(),
                                        LogisticRegression(max_iter=2000)),
    "RandomForest":       RandomForestClassifier(n_estimators=300,
                                                 random_state=42, n_jobs=-1),
    "SVM-RBF":            make_pipeline(StandardScaler(),
                                        SVC(kernel="rbf", C=5.0, gamma="scale")),
}

# ── CV schemes ────────────────────────────────────────────────────────────────
schemes = {
    "5-fold Stratified (random; allows same-video leakage)":
        ("strat", StratifiedKFold(n_splits=5, shuffle=True, random_state=42)),
    f"GroupKFold by video (no leakage; {min(5, n_groups)} folds)":
        ("group", GroupKFold(n_splits=min(5, n_groups))),
}

# ── run all combinations ──────────────────────────────────────────────────────
results = {}
for sch_name, (sch_kind, cv) in schemes.items():
    print(f"\n{'='*70}\nCV scheme: {sch_name}\n{'='*70}")
    for clf_name, clf in clfs.items():
        if sch_kind == "group":
            y_pred = cross_val_predict(clf, X, y, cv=cv, groups=groups)
        else:
            y_pred = cross_val_predict(clf, X, y, cv=cv)
        acc = (y == y_pred).mean()
        results[(sch_name, clf_name)] = acc
        print(f"\n  {clf_name}: accuracy = {acc*100:.1f}%")
        print("  " + classification_report(y, y_pred, target_names=classes,
                                            zero_division=0).replace("\n", "\n  "))

# ── summary table ─────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"{'Classifier':<22} {'Stratified (leaky)':<22} {'GroupKFold (honest)':<22}")
for clf_name in clfs:
    s_acc = results[(list(schemes.keys())[0], clf_name)]
    g_acc = results[(list(schemes.keys())[1], clf_name)]
    drop = (s_acc - g_acc) * 100
    print(f"{clf_name:<22} {s_acc*100:>6.1f}%               "
          f"{g_acc*100:>6.1f}%   (Δ {drop:+.1f}pp)")
