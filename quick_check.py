"""Re-check the saved results in a few seconds (no retraining, no raw data needed).

Run from the project folder:  python quick_check.py

It loads the saved XGBoost predictions for the 2,252 test households, recomputes the headline scores and compares them with
the numbers that the notebook saved in outputs/key_numbers.json.
"""
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

import ihds_tools  # noqa: F401  (the saved models need ihds_tools.ClipOutliers)

HERE = Path(__file__).resolve().parent
bundle = joblib.load(HERE / "outputs" / "model_bundle.joblib")
saved = json.load(open(HERE / "outputs" / "key_numbers.json"))

test = bundle["test_rows"]
y_true = test["ESCAPED"].to_numpy()
p_escape = test["P_ESCAPE"].to_numpy()
threshold = bundle["thresholds"]["XGBoost"]
y_pred = (p_escape >= threshold).astype(int)

auc = roc_auc_score(y_true, p_escape)
tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
print(f"Test households: {len(y_true):,}   escaped: {y_true.sum():,} ({y_true.mean():.1%})   threshold: {threshold:.3f}")
print(f"ROC-AUC            : {auc:.3f}")
print(f"Accuracy           : {(tp + tn) / len(y_true):.3f}")
print(f"Precision / recall / F1 (escaped)    : {precision_score(y_true, y_pred):.3f} / {recall_score(y_true, y_pred):.3f} / {f1_score(y_true, y_pred):.3f}")
print(f"Precision / recall / F1 (stayed poor): {precision_score(1 - y_true, 1 - y_pred):.3f} / {recall_score(1 - y_true, 1 - y_pred):.3f} / {f1_score(1 - y_true, 1 - y_pred):.3f}")
print(f"Confusion matrix (rows = actual stayed poor / escaped, columns = predicted stayed poor / escaped):\n{np.array([[tn, fp], [fn, tp]])}")

# Compare with the numbers saved by the notebook.
saved_xgboost = [row for row in saved["results"] if row["Model"] == "XGBoost"][0]
assert abs(auc - saved_xgboost["ROC_AUC"]) < 5e-4, "ROC-AUC differs from the notebook"
assert abs(f1_score(y_true, y_pred, average="macro") - saved_xgboost["Macro_F1"]) < 5e-4, "macro-F1 differs from the notebook"
print("\nOK: these numbers match the ones saved by the notebook (outputs/key_numbers.json).")
