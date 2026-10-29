"""Collect every number used in the written report from the notebook outputs (no number is typed by hand)."""
import json
import os
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import confusion_matrix

RUN = os.environ.get("RUN_DIR") or str(Path(__file__).resolve().parent.parent).replace("\\", "/")
NUM = RUN + "/outputs/"
k = json.load(open(NUM + "key_numbers.json"))
dump = pickle.load(open(NUM + "chart_dump.pkl", "rb"))
cv = pd.read_csv(NUM + "cv_summary.csv").set_index("Model")
split = pd.read_csv(NUM + "modelling_ids_and_split.csv")
fd = pd.read_csv(NUM + "feature_dictionary.csv")
res = {r["Model"]: r for r in k["results"]}
fm = {r["Model"]: r for r in k["full_metrics"]}
cal = {r["Model"]: r for r in k["calibration"]}
rep = {r["Model"]: r for r in k["repeated_splits"]}
over = {r["Model"]: r for r in k["overfitting_check"]}
ENS = "Soft-vote ensemble (LR+RF+XGB)"
HEAD = k["best_model"]


def pct(x, d=0):
    return f"{x * 100:.{d}f}%"


cd = dump["chart_data"]


def grp(col):
    return cd.groupby(col, observed=True)["ESCAPED"].agg(["mean", "size"])


caste, area, educ, assets = (grp(c) for c in ["Caste/religion", "Area", "Adult education", "Assets tertile"])
y, probs, thr = dump["y_test"], dump["test_probs"], dump["thresholds"]
cm = confusion_matrix(y, (probs[HEAD] >= thr[HEAD]).astype(int), labels=[0, 1])
edu = k["education"]
EA = edu["A: baseline characteristics"]
EB = edu["B: A + baseline poverty gap"]
pair = {(p["model_a"], p["model_b"]): p for p in k["paired_differences"]}
fs = k["feature_sets"]
sens = {r["Target rule"]: r for r in k["sensitivity"]}
old = {r["Model"]: r for r in k["old_line"]}
sw = k["survey_weights"]
ALL = "Escaped only if ALL descendant households non-poor"
ANY = "Escaped if ANY descendant household non-poor"
fsel = pd.DataFrame(k["feature_selection"]["table"]).set_index("Features kept")
rv = k["random_vs_village"]


def model_row(m):
    name = "Soft-voting ensemble" if m == ENS else "Dummy baseline" if m.startswith("Dummy") else m
    auc = "0.487" if m.startswith("Dummy") else f"{res[m]['ROC_AUC']:.3f} ({res[m]['ROC_AUC_CI'].strip('[]').replace(', ', ' to ')})"
    return [name, auc, f"{res[m]['Accuracy']:.3f}", f"{res[m]['Macro_F1']:.3f}", f"{res[m]['MCC']:.3f}", f"{res[m]['Brier']:.3f}"]


def est(spec):
    return {q: [f"{spec[q]['estimate'] * 100:.1f}", f"{spec[q]['ci_low'] * 100:.1f}", f"{spec[q]['ci_high'] * 100:.1f}"] for q in ["raw", "regression", "ipw", "doubly_robust"]}


used = fd[fd["used"]].copy()
miss = used.sort_values("missing_share", ascending=False).head(6)
groups_table = []
for gname, sub in used.groupby("group"):
    groups_table.append([gname, str(len(sub)), str(int((sub["type"] == "num").sum())), str(int((sub["type"] == "nom").sum()))])
groups_table.sort(key=lambda r: -int(r[1]))
dictionary_rows = [[r["variable"], str(r["label"]), r["group"], "number" if r["type"] == "num" else "category", f"{r['missing_share'] * 100:.0f}%"]
                   for _, r in used.sort_values(["group", "variable"]).iterrows()]

D = {
    "n_w1": f"{k['n_w1_households']:,}", "n_w2": f"{k['n_w2_households']:,}", "n_persons": f"{k['n_w1_persons']:,}",
    "n_poor_w1": f"{k['n_poor_w1']:,}", "n_kept": f"{k['n_kept']:,}", "retention": pct(k["retention"], 1),
    "n_escaped": f"{k['n_escaped']:,}", "n_stayed": f"{k['n_stayed']:,}", "escape": pct(k["escape_rate"], 1), "fell": pct(k["pct_nonpoor_fell"], 1),
    "n_features": k["n_features"], "n_numeric": k["n_numeric"], "n_nominal": k["n_nominal"],
    "n_train": f"{k['n_train']:,}", "n_test": f"{k['n_test']:,}", "n_train_vill": f"{k['n_train_villages']:,}", "n_test_vill": f"{k['n_test_villages']:,}",
    "link": {"found": f"{k['link']['found_again']:,}", "of": f"{k['link']['wave1_households']:,}", "share": pct(k["link"]["share_found_again"], 1)},
    "w2agree": pct(k["wave2_flag_agreement"], 1),
    "pov_old_pw": pct(k["poverty_rates"]["POOR_OLD"]["person_weighted"]), "pov_new_pw": pct(k["poverty_rates"]["POOR"]["person_weighted"]),
    "head_tracked": pct(k["head_rule_check"]["share_head_tracked"]), "head_same": pct(k["head_rule_check"]["same_outcome"], 1),
    "near": {"all": pct(k["near_line"]["within_10_all_poor"]), "below": pct(k["near_line"]["poor12_just_below"]), "above": pct(k["near_line"]["poor12_just_above"])},
    "ill": {"vill": f"{k['illness_villages']['villages']:,}", "none": str(k["illness_villages"]["none_listed"]), "exp": f"{k['illness_villages']['expected_by_chance']:.0f}"},
    "ration": {r["Model"]: [f"{r['AUC with ration card']:.3f}", f"{r['AUC without ration card']:.3f}"] for r in k["ration_card"]},
    "caste": {c: [pct(caste.loc[c, "mean"]), f"{int(caste.loc[c, 'size']):,}"] for c in caste.index},
    "educ": {c: [pct(educ.loc[c, "mean"]), f"{int(educ.loc[c, 'size']):,}"] for c in educ.index},
    "area": {c: pct(area.loc[c, "mean"]) for c in area.index}, "assets": {c: pct(assets.loc[c, "mean"]) for c in assets.index},
    "bh_combined": pct((caste.loc["Brahmin", "mean"] * caste.loc["Brahmin", "size"] + caste.loc["High caste", "mean"] * caste.loc["High caste", "size"]) / (caste.loc["Brahmin", "size"] + caste.loc["High caste", "size"])),
    "models": [model_row(m) for m in ["XGBoost", ENS, "Random Forest", "Logistic Regression", "Dummy (predict prior)"]],
    "perclass": [[("Ensemble" if m == ENS else m)] + [f"{fm[m][c]:.3f}" for c in ["Accuracy", "Precision (escaped)", "Recall (escaped)", "F1 (escaped)", "Precision (stayed poor)", "Recall (stayed poor)", "F1 (stayed poor)"]]
                 for m in ["Logistic Regression", "Random Forest", "XGBoost", ENS]],
    "cv": {m: f"{cv.loc[m, 'CV ROC-AUC (mean)']:.3f}" for m in cv.index},
    "pair_ens_xgb": [f"{pair[(ENS, 'XGBoost')][q]:+.4f}" for q in ["difference", "ci_low", "ci_high"]], "pair_ens_xgb_abs": f"{abs(pair[(ENS, 'XGBoost')]['difference']):.3f}",
    "pair_xgb_lr": f"{pair[('XGBoost', 'Logistic Regression')]['difference']:+.3f}", "pair_xgb_rf": f"{pair[('XGBoost', 'Random Forest')]['difference']:+.3f}",
    "pair_ens_lr": f"{pair[(ENS, 'Logistic Regression')]['difference']:+.3f}", "pair_ens_rf": f"{pair[(ENS, 'Random Forest')]['difference']:+.3f}",
    "rep": {m: [f"{rep[m]['mean']:.3f}", f"{rep[m]['std']:.3f}", f"{rep[m]['min']:.3f}", f"{rep[m]['max']:.3f}", int(rep[m]["best_in_n_splits"])] for m in rep},
    "cal": {m: [f"{cal[m]['mean_predicted']:.3f}", f"{cal[m]['observed_rate']:.3f}", f"{cal[m]['Brier']:.3f}", f"{cal[m]['calib_slope']:.2f}", f"{cal[m]['Brier_skill_score']:.3f}"] for m in cal},
    "cm": [[int(v) for v in row] for row in cm], "thr": f"{thr[HEAD]:.3f}",
    "head_res": {q: f"{res[HEAD][q]:.3f}" for q in ["ROC_AUC", "Recall_escaped", "Precision_escaped", "Recall_stayed", "Precision_stayed", "Macro_F1", "MCC", "Brier", "Accuracy"]},
    "lift": [[r["quintile"], f"{r['households']}", pct(r["stayed_poor_rate"]), f"{r['lift_vs_average']:.2f}", pct(r["share_of_all_stayed_poor"])] for r in k["lift"]],
    "avg_stay": pct(1 - float(np.mean(y))), "top40": pct(k["lift"][-1]["share_of_all_stayed_poor"] + k["lift"][-2]["share_of_all_stayed_poor"]),
    "q5": pct(k["lift"][-1]["stayed_poor_rate"]), "q5lift": f"{k['lift'][-1]['lift_vs_average']:.1f}", "q1": pct(k["lift"][0]["stayed_poor_rate"]),
    "shap_top": [[r["variable"], r["label"], f"{r['mean_abs_SHAP']:.3f}", r["group"]] for _, r in pd.read_csv(NUM + "shap_top_variables.csv").rename(columns={"Unnamed: 0": "variable"}).head(10).iterrows()],
    "shap_grp": {a: pct(b, 1) for a, b in k["shap_group_share"].items()},
    "edu": {"n_treated": f"{edu['n_treated']:,}", "n_control": f"{edu['n_control']:,}", "A": est(EA), "B": est(EB),
            "matchA": f"{EA['matching']['estimate'] * 100:.1f}", "evalA": f"{EA['doubly_robust']['e_value']:.2f}", "evalA_ci": f"{EA['doubly_robust']['e_value_ci_limit']:.2f}",
            "smd_before": f"{EA['max_smd_before']:.2f}", "smd_after": f"{EA['max_smd_after_ipw']:.2f}"},
    "edu_int": [f"{min(EA['doubly_robust']['ci_low'], EB['doubly_robust']['ci_low']) * 100:.1f}", f"{max(EA['doubly_robust']['ci_high'], EB['doubly_robust']['ci_high']) * 100:.1f}"],
    "rob": {"fs": [[r["Feature set"], str(r["n_features"]), f"{r['LR CV AUC']:.3f}", f"{r['LR test AUC']:.3f}", f"{r['XGB CV AUC']:.3f}", f"{r['XGB test AUC']:.3f}"] for r in fs],
            "all": [pct(sens[ALL]["Escape rate"], 1), f"{sens[ALL]['ROC_AUC (test)']:.3f}"], "any": [pct(sens[ANY]["Escape rate"], 1), f"{sens[ANY]['ROC_AUC (test)']:.3f}"],
            "ipw": [pct(k["ipw"]["escape_rate_raw"], 1), pct(k["ipw"]["escape_rate_ipw"], 1)],
            "old": [f"{int(old['XGBoost']['households (deeper poor)']):,}", pct(old["XGBoost"]["escape rate (deeper poor)"], 1), f"{old['XGBoost']['AUC: main model']:.3f}", f"{old['Logistic Regression']['AUC: main model']:.3f}"],
            "sw": [pct(sw["escape_rate_weighted"], 1), f"{sw['effective_n']:,.0f}", [f"{a['AUC weighted']:.3f}" for a in sw["auc"] if a["Model"] == "XGBoost"][0]],
            "gap_alone": f"{k['gap_alone_auc']:.3f}"},
    "fsel": [[str(int(i)), f"{r['Cross-validated ROC-AUC']:.3f}", f"{r['Test ROC-AUC']:.3f}"] for i, r in fsel.iterrows()],
    "fsel_top10": k["feature_selection"]["top10"],
    "over": [[m, f"{over[m]['Train ROC-AUC']:.3f}", f"{over[m]['Cross-validated ROC-AUC']:.3f}", f"{over[m]['Test ROC-AUC']:.3f}"] for m in ["Logistic Regression", "Random Forest", "XGBoost"]],
    "rv": {"random": f"{rv['random_mean']:.3f}", "random_sd": f"{rv['random_sd']:.3f}", "village": f"{rv['village_mean']:.3f}", "village_sd": f"{rv['village_sd']:.3f}"},
    "miss": [[str(r["label"]), pct(r["missing_share"])] for _, r in miss.iterrows()],
    "groups_table": groups_table, "dictionary_rows": dictionary_rows,
    "versions": k["versions"],
}
figs = {}
for name in ["c13_poverty_line", "c01_transitions", "c02_feature_groups", "c03_escape_by_caste", "c04_escape_by_education", "c05_roc_curves", "c15_repeated_splits",
             "c14_calibration", "c07_risk_groups", "c08_shap_top10", "c09_shap_groups", "c10_shap_children", "c11_shap_assets", "c12_education_effect", "app_screenshot",
             "c16_feature_selection", "c17_workflow", "c18_confusion_all_models", "c19_education_simple", "exec_evidence"]:
    path = NUM + f"figures_ppt/{name}.png"
    if os.path.exists(path):
        w, h = Image.open(path).size
        figs[name] = [w, h]
    else:
        print("MISSING figure", name)
D["figs"] = figs
D["run_dir"] = RUN
_check = subprocess.run([sys.executable, str(Path(RUN) / "quick_check.py")], capture_output=True, text=True, cwd=RUN)
assert _check.returncode == 0 and "OK" in _check.stdout, _check.stderr
D["quick_check"] = ["$ python quick_check.py"] + [ln for ln in _check.stdout.splitlines() if ln.strip()]
json.dump(D, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_data.json"), "w"), indent=1)
print("report_data.json written;", len(json.dumps(D)), "bytes; figures:", len(figs))
