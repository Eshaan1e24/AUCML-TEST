"""Step 2: draw one clean chart per file for the presentation (outputs/figures_ppt).

Reads only files written by the notebook (outputs/key_numbers.json, outputs/*.csv, outputs/chart_dump.pkl),
so every number on a chart can be traced to the notebook.

Run from the project folder:  python make_charts_v3.py
"""
import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve

ROOT = Path(__file__).resolve().parent
NUM = ROOT / "outputs"
OUT = NUM / "figures_ppt"
OUT.mkdir(parents=True, exist_ok=True)

BG, INK, MUTED, GRID = "#FAF7F0", "#1F2937", "#6B7280", "#E5E0D5"
TEAL, ORANGE, BLUE, PURPLE = "#0F766E", "#C2410C", "#2563EB", "#7C3AED"

plt.rcParams.update({
    "font.family": "Calibri", "font.size": 15, "axes.titlesize": 17,
    "axes.labelsize": 15, "xtick.labelsize": 14, "ytick.labelsize": 14,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})

d = pickle.load(open(NUM / "chart_dump.pkl", "rb"))
k = json.load(open(NUM / "key_numbers.json"))
ENSEMBLE = "Soft-vote ensemble (LR+RF+XGB)"
HEADLINE = d["best_model_name"]          # the model used for the confusion matrix, risk groups and SHAP
fonts_ok = True


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)


def pct_axis(ax, axis="y"):
    fmt = plt.FuncFormatter(lambda v, _: f"{v:.0%}")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


# 1. Poverty status in 2011-12 for households poor / not poor in 2004-05 (Tendulkar line in both rounds)
t = k["transitions"]
n_poor = t["poor05_not_poor12"] + t["poor05_poor12"]
n_not = t["notpoor05_not_poor12"] + t["notpoor05_poor12"]
rows = [(f"Poor in 2004-05\n({n_poor:,} households)", t["poor05_not_poor12"], t["poor05_poor12"]),
        (f"Not poor in 2004-05\n({n_not:,} households)", t["notpoor05_not_poor12"], t["notpoor05_poor12"])]
fig, ax = plt.subplots(figsize=(8, 3.6))
for i, (label, notpoor, poor) in enumerate(rows):
    total = notpoor + poor
    a, b = notpoor / total, poor / total
    ax.barh(i, a, color=TEAL, height=0.55)
    ax.barh(i, b, left=a, color=ORANGE, height=0.55)
    ax.text(a / 2, i, f"Not poor in 2011-12\n{a:.0%}", ha="center", va="center", color="white", fontsize=17, fontweight="bold")
    ax.text(a + b / 2, i, f"Poor\n{b:.0%}", ha="center", va="center", color="white", fontsize=17, fontweight="bold")
ax.set_yticks([0, 1], [r[0] for r in rows], fontsize=16)
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xticks([])
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", length=0)
save(fig, "c01_transitions.png")

# 2. Number of features in each factor group
groups = pd.read_csv(NUM / "shap_by_group.csv", index_col=0)["n_variables"].sort_values()
fig, ax = plt.subplots(figsize=(7.5, 5.2))
ax.barh(groups.index, groups.values, color=TEAL, height=0.65)
for i, v in enumerate(groups.values):
    ax.text(v + 0.4, i, str(v), va="center", fontsize=14)
ax.set_xlabel("Number of features")
ax.xaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c02_feature_groups.png")

cd = d["chart_data"]
avg = cd["ESCAPED"].mean()


def rate_chart(column, order, name, xlabel, figsize, horizontal=True, drop_small=0):
    stats = cd.groupby(column, observed=True)["ESCAPED"].agg(["mean", "size"]).reindex(order).dropna()
    stats = stats[stats["size"] >= drop_small]
    fig, ax = plt.subplots(figsize=figsize)
    if horizontal:
        stats = stats.sort_values("mean")
        colors = [ORANGE if m < avg else TEAL for m in stats["mean"]]
        ax.barh(stats.index, stats["mean"], color=colors, height=0.65)
        for i, (m, n) in enumerate(zip(stats["mean"], stats["size"])):
            ax.text(m + 0.01, i, f"{m:.0%}  (n = {n:,})", va="center", fontsize=13)
        ax.axvline(avg, color=INK, ls="--", lw=1.2)
        ax.text(avg, len(stats) - 0.35, f"  average {avg:.0%}", fontsize=13, color=INK)
        ax.set_xlim(0, 1.05)
        pct_axis(ax, "x")
        ax.set_xlabel("Share of households that escaped poverty")
    else:
        colors = [ORANGE if m < avg else TEAL for m in stats["mean"]]
        ax.bar(stats.index.astype(str), stats["mean"], color=colors, width=0.6)
        for i, (m, n) in enumerate(zip(stats["mean"], stats["size"])):
            ax.text(i, m + 0.015, f"{m:.0%}", ha="center", fontsize=14, fontweight="bold")
            ax.text(i, 0.03, f"n = {n:,}", ha="center", fontsize=12, color="white")
        ax.axhline(avg, color=INK, ls="--", lw=1.2)
        ax.text(-0.45, avg + 0.015, f"average {avg:.0%}", ha="left", fontsize=13)
        ax.set_ylim(0, 1)
        pct_axis(ax)
        ax.set_ylabel("Share that escaped poverty")
        ax.set_xlabel(xlabel)
    save(fig, name)


rate_chart("Caste/religion", ["Brahmin", "High caste", "OBC", "Dalit", "Adivasi", "Muslim", "Sikh/Jain", "Christian"],
           "c03_escape_by_caste.png", "", (8.5, 4.8), True, drop_small=50)
rate_chart("Adult education", ["None", "1-4 yrs", "5-9 yrs", "10-12 yrs", "13+ yrs"],
           "c04_escape_by_education.png", "Years of schooling of the most educated adult", (8.5, 4.8), False)

# 5. ROC curves on the test villages
y, probs = d["y_test"], d["test_probs"]
colors = {"Logistic Regression": BLUE, "Random Forest": PURPLE, "XGBoost": ORANGE, ENSEMBLE: TEAL}
fig, ax = plt.subplots(figsize=(6.6, 5.6))
for name, col in colors.items():
    fpr, tpr, _ = roc_curve(y, probs[name])
    short = "Ensemble" if name == ENSEMBLE else name
    ax.plot(fpr, tpr, color=col, lw=3 if name == ENSEMBLE else 2, label=f"{short}  (AUC {roc_auc_score(y, probs[name]):.3f})")
ax.plot([0, 1], [0, 1], color=MUTED, ls="--", lw=1.2, label="Random guessing  (AUC 0.500)")
ax.set_xlabel("False positive rate")
ax.set_ylabel("True positive rate")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1.01)
ax.legend(loc="lower right", fontsize=12.5)
ax.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c05_roc_curves.png")

# 6. Confusion matrix of the headline model
pred = (probs[HEADLINE] >= d["thresholds"][HEADLINE]).astype(int)
cm = confusion_matrix(y, pred, labels=[0, 1])
fig, ax = plt.subplots(figsize=(6.2, 5.2))
shade = np.array([[TEAL, "#F3D9CC"], ["#F3D9CC", TEAL]])
for i in range(2):
    for j in range(2):
        ax.add_patch(plt.Rectangle((j, i), 0.97, 0.97, color=shade[i, j]))
        col = "white" if i == j else INK
        ax.text(j + 0.485, i + 0.42, f"{cm[i, j]:,}", ha="center", va="center", fontsize=26, fontweight="bold", color=col)
        ax.text(j + 0.485, i + 0.65, f"{cm[i, j] / cm[i].sum():.0%} of row", ha="center", va="center", fontsize=13, color=col)
ax.set_xlim(0, 2)
ax.set_ylim(2, 0)
ax.set_xticks([0.485, 1.485], ["Predicted:\nstayed poor", "Predicted:\nescaped"])
ax.set_yticks([0.485, 1.485], ["Actual:\nstayed poor", "Actual:\nescaped"])
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
save(fig, "c06_confusion_matrix.png")

# 7. Risk quintiles of the headline model
lift = pd.read_csv(NUM / "risk_quintile_lift.csv")
labels = ["Lowest\nrisk 20%", "2nd", "3rd", "4th", "Highest\nrisk 20%"]
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.bar(labels, lift["stayed_poor_rate"], color=[TEAL, TEAL, TEAL, ORANGE, ORANGE], width=0.6)
for i, v in enumerate(lift["stayed_poor_rate"]):
    ax.text(i, v + 0.012, f"{v:.0%}", ha="center", fontsize=15, fontweight="bold")
base = 1 - np.mean(y)
ax.axhline(base, color=INK, ls="--", lw=1.2)
ax.text(-0.35, base + 0.015, f"average {base:.0%}", fontsize=13)
ax.set_ylim(0, 0.7)
pct_axis(ax)
ax.set_ylabel("Share that actually stayed poor")
ax.set_xlabel("Test households grouped by predicted risk of staying poor")
save(fig, "c07_risk_groups.png")

# 8. SHAP top 10 variables (labels come from the feature dictionary written by the notebook)
dictionary = pd.read_csv(NUM / "feature_dictionary.csv").set_index("variable")["label"].to_dict()
nice = {"STATEID2": "State", "n_children_0_5": "Number of children aged 0-5", "assets_per_capita": "Assets per household member",
        "HHASSETS": "Household assets index", "RC1A": "Ration card type", "GROUPS8": "Caste / religion group",
        "head_age": "Age of household head", "has_school_age_kids": "Has children aged 6-14", "ID13": "Caste category",
        "FU4": "Type of cooking stove", "ID15": "Main income source", "share_female": "Share of members who are female",
        "HQ1": "House type", "WA1": "Main water source"}
top = pd.read_csv(NUM / "shap_top_variables.csv", index_col=0).head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(8.2, 5.2))
ax.barh([nice.get(v, dictionary.get(v, v)) for v in top.index], top["mean_abs_SHAP"], color=TEAL, height=0.65)
for i, v in enumerate(top["mean_abs_SHAP"]):
    ax.text(v + 0.004, i, f"{v:.3f}", va="center", fontsize=13)
ax.set_xlabel("Average impact on the prediction (mean |SHAP value|)")
ax.xaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c08_shap_top10.png")

# 9. SHAP share by factor group
g = pd.read_csv(NUM / "shap_by_group.csv", index_col=0)["share_of_total_SHAP"].sort_values()
fig, ax = plt.subplots(figsize=(8.2, 5.2))
ax.barh(g.index, g.values, color=[TEAL if v >= 0.1 else "#5EA9A3" for v in g.values], height=0.65)
for i, v in enumerate(g.values):
    ax.text(v + 0.004, i, f"{v:.1%}", va="center", fontsize=13)
pct_axis(ax, "x")
ax.set_xlim(0, 0.3)
ax.set_xlabel("Share of total SHAP importance")
save(fig, "c09_shap_groups.png")

# 10-11. SHAP dependence: young children, assets per person
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(6.2, 4.6))
xc = d["x_children"]
ok = ~np.isnan(xc)
ax.scatter(xc[ok] + rng.uniform(-0.18, 0.18, ok.sum()), d["shap_children"][ok], s=9, alpha=0.5, color=TEAL)
ax.axhline(0, color=INK, lw=1)
ax.set_xlabel("Number of children aged 0-5 in 2004-05")
ax.set_ylabel("SHAP value\n(+ = towards escape)")
ax.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c10_shap_children.png")

fig, ax = plt.subplots(figsize=(6.2, 4.6))
xa = d["x_assets"]
ok = ~np.isnan(xa)
ax.scatter(xa[ok], d["shap_assets"][ok], s=9, alpha=0.5, color=TEAL)
ax.axhline(0, color=INK, lw=1)
ax.set_xlabel("Assets per household member in 2004-05")
ax.set_ylabel("SHAP value\n(+ = towards escape)")
ax.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c11_shap_assets.png")

# 12. Education: difference in escape rate under each estimator (dots with 95% village-bootstrap intervals)
e = k["education"]
spec_a, spec_b = e["A: baseline characteristics"], e["B: A + baseline poverty gap"]
items = [("Raw difference", spec_a["raw"], MUTED),
         ("Adjusted for starting traits (regression)", spec_a["regression"], TEAL),
         ("Adjusted for starting traits (weighting)", spec_a["ipw"], TEAL),
         ("Adjusted for starting traits (doubly robust)", spec_a["doubly_robust"], TEAL),
         ("Also adjusted for baseline poverty depth (doubly robust)", spec_b["doubly_robust"], ORANGE)]
fig, ax = plt.subplots(figsize=(9.2, 4.6))
for i, (label, r, col) in enumerate(items[::-1]):
    ax.errorbar(r["estimate"] * 100, i, xerr=[[(r["estimate"] - r["ci_low"]) * 100], [(r["ci_high"] - r["estimate"]) * 100]],
                fmt="o", color=col, capsize=6, lw=2, ms=9)
    ax.text(r["ci_high"] * 100 + 0.5, i, f"{r['estimate'] * 100:+.1f}", va="center", fontsize=14, fontweight="bold", color=col)
ax.set_yticks(range(len(items)), [it[0] for it in items[::-1]], fontsize=13)
ax.axvline(0, color=INK, lw=1)
ax.set_xlim(0, 17)
ax.set_xlabel("Difference in escape rate (percentage points)")
ax.xaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c12_education_effect.png")

# 13. Why the poverty line matters: poverty rate in 2004-05 under the old wave-1 line and the Tendulkar line
pr = k["poverty_rates"]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
x = np.arange(2)
w = 0.34
old = [pr["POOR_OLD"]["unweighted"], pr["POOR_OLD"]["person_weighted"]]
new = [pr["POOR"]["unweighted"], pr["POOR"]["person_weighted"]]
ax.bar(x - w / 2, old, w, color=MUTED, label="Old line (wave-1 flag)")
ax.bar(x + w / 2, new, w, color=TEAL, label="Tendulkar line (used here)")
for xi, (a_, b_) in enumerate(zip(old, new)):
    ax.text(xi - w / 2, a_ + 0.008, f"{a_:.0%}", ha="center", fontsize=15, fontweight="bold")
    ax.text(xi + w / 2, b_ + 0.008, f"{b_:.0%}", ha="center", fontsize=15, fontweight="bold")
ax.axhline(0.372, color=ORANGE, ls="--", lw=1.4)
ax.text(1.62, 0.381, "published estimate\nabout 37%", color=ORANGE, fontsize=12, ha="right")
ax.set_xticks(x, ["Share of households\n(unweighted)", "Share of people\n(survey weighted)"])
ax.set_ylim(0, 0.5)
pct_axis(ax)
ax.set_ylabel("Poor in 2004-05")
ax.legend(loc="upper left", fontsize=12.5)
save(fig, "c13_poverty_line.png")

# 14. Calibration of the headline model and logistic regression on the test villages
fig, ax = plt.subplots(figsize=(6.2, 5.0))
for name, col in [("Logistic Regression", BLUE), (HEADLINE, ORANGE)]:
    observed, predicted = calibration_curve(y, probs[name], n_bins=10, strategy="quantile")
    ax.plot(predicted, observed, "o-", color=col, lw=2, label=name)
ax.plot([0, 1], [0, 1], color=MUTED, ls="--", lw=1.2, label="Perfect calibration")
ax.set_xlabel("Predicted chance of escaping")
ax.set_ylabel("Share that really escaped")
ax.set_xlim(0.2, 1.0)
ax.set_ylim(0.2, 1.0)
ax.legend(loc="upper left", fontsize=12.5)
ax.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c14_calibration.png")

# 15. Repeated village splits: test ROC-AUC of each model over 20 different splits
rep = pd.read_csv(NUM / "repeated_split_auc.csv")
order = ["Logistic Regression", "Random Forest", "XGBoost", ENSEMBLE]
fig, ax = plt.subplots(figsize=(8.2, 4.8))
box = ax.boxplot([rep[c] for c in order], tick_labels=["Logistic\nRegression", "Random\nForest", "XGBoost", "Ensemble"],
                 patch_artist=True, widths=0.55, medianprops={"color": INK, "lw": 2})
for patch, col in zip(box["boxes"], [BLUE, PURPLE, ORANGE, TEAL]):
    patch.set_facecolor(col)
    patch.set_alpha(0.75)
ax.set_ylabel("Test ROC-AUC")
ax.yaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c15_repeated_splits.png")

# 16. Feature selection check: score against the number of features kept
fsel = pd.DataFrame(k["feature_selection"]["table"])
fig, ax = plt.subplots(figsize=(7.4, 4.6))
labels_x = [str(int(v)) for v in fsel["Features kept"]]
ax.plot(labels_x, fsel["Test ROC-AUC"], "o-", color=ORANGE, lw=2.5, ms=9, label="test villages")
ax.plot(labels_x, fsel["Cross-validated ROC-AUC"], "s-", color=TEAL, lw=2.5, ms=8, label="cross-validation (training villages)")
for xv, yv in zip(labels_x, fsel["Test ROC-AUC"]):
    ax.text(xv, yv + 0.004, f"{yv:.3f}", ha="center", fontsize=13, color=ORANGE, fontweight="bold")
ax.set_xlabel("Number of features kept (most important first)")
ax.set_ylabel("ROC-AUC")
ax.set_ylim(min(fsel["Cross-validated ROC-AUC"].min(), fsel["Test ROC-AUC"].min()) - 0.02, max(fsel["Test ROC-AUC"].max(), fsel["Cross-validated ROC-AUC"].max()) + 0.02)
ax.legend(loc="lower right", fontsize=13)
ax.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c16_feature_selection.png")

# 17. Workflow diagram (boxes and arrows)
steps = ["Survey files\n(2004-05, 2011-12)", "Check, clean and\nlink the two rounds", "One poverty line\nand the target", "Build 137 features,\ncheck selection", "Split by village\n(train / test)",
         "Train and tune\n4 models", "Test on villages\nnever seen", "Explain with SHAP,\nsave outputs", "Slides, report\nand demo app"]
fig, ax = plt.subplots(figsize=(13, 5.2))
ax.set_xlim(0, 13)
ax.set_ylim(0, 5.2)
ax.axis("off")
positions = [(1.3 + 2.45 * i, 3.9) for i in range(5)] + [(1.3 + 2.45 * i, 1.3) for i in range(4)]
for i, ((x, y), label) in enumerate(zip(positions, steps)):
    ax.add_patch(plt.Rectangle((x - 1.1, y - 0.6), 2.2, 1.2, color=TEAL if i < 8 else ORANGE, alpha=0.95, zorder=2))
    ax.text(x, y, label, ha="center", va="center", color="white", fontsize=13.5, fontweight="bold", zorder=3)
    ax.text(x - 0.95, y + 0.78, f"{i + 1}", ha="center", va="center", fontsize=13, color=INK, fontweight="bold")
for i in range(len(positions) - 1):
    (x1, y1), (x2, y2) = positions[i], positions[i + 1]
    if y1 == y2:
        ax.annotate("", xy=(x2 - 1.12, y2), xytext=(x1 + 1.12, y1), arrowprops={"arrowstyle": "-|>", "mutation_scale": 24, "color": INK, "lw": 2.2}, zorder=1)
    else:
        ax.annotate("", xy=(x2 + 0.0, y2 + 0.62), xytext=(x1 + 0.0, y1 - 0.62), arrowprops={"arrowstyle": "-|>", "mutation_scale": 24, "color": INK, "lw": 2.2, "connectionstyle": "angle,angleA=0,angleB=90,rad=10"}, zorder=1)
save(fig, "c17_workflow.png")

# 18. Confusion matrices of all four models
cms = k["confusion_matrices"]
order_cm = ["Logistic Regression", "Random Forest", "XGBoost", ENSEMBLE]
fig, axes = plt.subplots(1, 4, figsize=(16, 4.4))
for ax, name in zip(axes, order_cm):
    m = np.array(cms[name])
    for i in range(2):
        for j in range(2):
            good = i == j
            ax.add_patch(plt.Rectangle((j, i), 0.96, 0.96, color=TEAL if good else "#F3D9CC"))
            ax.text(j + 0.48, i + 0.42, f"{m[i, j]:,}", ha="center", va="center", fontsize=20, fontweight="bold", color="white" if good else INK)
            ax.text(j + 0.48, i + 0.68, f"{m[i, j] / m[i].sum():.0%}", ha="center", va="center", fontsize=12, color="white" if good else INK)
    ax.set_xlim(0, 2)
    ax.set_ylim(2, 0)
    ax.set_xticks([0.48, 1.48], ["pred.\nstayed poor", "pred.\nescaped"], fontsize=11)
    ax.set_yticks([0.48, 1.48], ["actual\nstayed poor", "actual\nescaped"], fontsize=11)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("Ensemble" if name == ENSEMBLE else name, fontsize=15, fontweight="bold")
save(fig, "c18_confusion_all_models.png")


# 19. Education, simple version: raw gap and adjusted gaps (dots with 95% intervals)
ed = k["education"]
bars = [("Raw gap", ed["A: baseline characteristics"]["raw"], MUTED),
        ("Adjusted: compared with\nsimilar households", ed["A: baseline characteristics"]["doubly_robust"], TEAL),
        ("Also adjusted for how poor\nthe household was", ed["B: A + baseline poverty gap"]["doubly_robust"], ORANGE)]
fig, ax = plt.subplots(figsize=(7.6, 4.6))
for i, (label, r, col) in enumerate(bars):
    ax.bar(i, r["estimate"] * 100, color=col, width=0.55)
    ax.errorbar(i, r["estimate"] * 100, yerr=[[(r["estimate"] - r["ci_low"]) * 100], [(r["ci_high"] - r["estimate"]) * 100]], color=INK, capsize=8, lw=1.6)
    ax.text(i, r["ci_high"] * 100 + 0.5, f"+{r['estimate'] * 100:.1f}", ha="center", fontsize=17, fontweight="bold", color=col)
ax.set_xticks(range(3), [b[0] for b in bars], fontsize=13)
ax.set_ylabel("Higher escape rate (percentage points)")
ax.set_ylim(0, max(b[1]["ci_high"] for b in bars) * 100 + 3)
ax.yaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
save(fig, "c19_education_simple.png")

print("charts saved to", OUT)
