"""Streamlit demo: risk of staying poor for a household that was poor in 2004-05.

Run:  streamlit run app.py
Needs:  outputs/model_bundle.joblib (written by the notebook) and app_labels.json (next to this file).

The tool ranks households by risk. It is a screening aid, not a basis for decisions about one household.
"""
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import streamlit as st

import ihds_tools  # noqa: F401  (the saved models need ihds_tools.ClipOutliers)

HERE = Path(__file__).resolve().parent
BUNDLE_PATH = HERE / "outputs" / "model_bundle.joblib"
LABELS = json.load(open(HERE / "app_labels.json", encoding="utf8"))

st.set_page_config(page_title="Poverty escape risk (demo)", layout="wide")


@st.cache_resource
def load_bundle():
    """Load the trained models, the typical-household defaults and the held-out test households."""
    return joblib.load(BUNDLE_PATH)


@st.cache_resource
def make_explainer(_booster):
    """Create the SHAP explainer once (it is slow to build)."""
    return shap.TreeExplainer(_booster)


bundle = load_bundle()
models = bundle["models"]
test_rows = bundle["test_rows"]
feature_info = bundle["feature_info"]
nominal = bundle["nominal"]
features = bundle["features"]

# Risk bands from the held-out test households: five equal groups of predicted risk of staying poor.
risk_test = 1 - test_rows["P_ESCAPE"].to_numpy()
band_edges = np.quantile(risk_test, [0.2, 0.4, 0.6, 0.8])
band_names = ["lowest 20%", "20-40%", "40-60%", "60-80%", "highest 20%"]
band_index = np.digitize(risk_test, band_edges)
stay_poor_by_band = [float(1 - test_rows["ESCAPED"].to_numpy()[band_index == b].mean()) for b in range(5)]


def predict_risk(row):
    """Return the XGBoost probability of ESCAPING (the headline model, also explained by SHAP) and all single-model probabilities."""
    probs = {name: float(model.predict_proba(row)[:, 1][0]) for name, model in models.items()}
    return probs["XGBoost"], probs


def original_variable(encoded_name):
    """Map an encoded column name (for example GROUPS8_5) back to the survey variable (GROUPS8)."""
    for name in sorted(nominal, key=len, reverse=True):
        if encoded_name == name or encoded_name.startswith(name + "_"):
            return name
    return encoded_name


def labelled(options):
    """Turn a {code: label} dictionary into a list of labels plus a lookup back to the code."""
    return list(options.values()), {label: code for code, label in options.items()}


st.title("Risk of staying poor: demo for households that were poor in 2004-05")
st.warning("Screening and ranking tool built on India Human Development Survey data (2004-05 to 2011-12). "
           "It is **not** for deciding about an individual household. The model's ROC-AUC is about 0.7: "
           "it ranks households better than chance, but many individual predictions are wrong.")

# ---------------------------------------------------------------- inputs
presets = {"(enter details by hand)": None}
ordered = test_rows.sort_values("P_ESCAPE").reset_index(drop=True)
for label, position in [("Real test household: lowest predicted escape chance", 5),
                        ("Real test household: about average", len(ordered) // 2),
                        ("Real test household: highest predicted escape chance", len(ordered) - 6)]:
    presets[label] = ordered.iloc[position]
preset_name = st.sidebar.selectbox("Start from", list(presets), index=0)
preset = presets[preset_name]


def start_value(name, fallback):
    """Value of an input: from the chosen real household if one is selected, otherwise the typical household."""
    if preset is not None and name in preset.index and pd.notna(preset[name]):
        return preset[name]
    return fallback


defaults = bundle["default_household"]
st.sidebar.header("Household details (2004-05)")
state_labels, state_lookup = labelled(LABELS["STATEID2"])
state_default = str(int(float(start_value("STATEID2", defaults["STATEID2"])))) if str(start_value("STATEID2", defaults["STATEID2"])).replace(".0", "").isdigit() else None
state_choice = st.sidebar.selectbox("State", state_labels,
                                    index=state_labels.index(LABELS["STATEID2"].get(state_default, state_labels[0])) if state_default in LABELS["STATEID2"] else 0)
group_labels, group_lookup = labelled(LABELS["GROUPS8"])
group_default = str(int(float(start_value("GROUPS8", defaults["GROUPS8"])))) if str(start_value("GROUPS8", defaults["GROUPS8"])).replace(".0", "").isdigit() else "3"
group_choice = st.sidebar.selectbox("Caste / religion group", group_labels,
                                    index=group_labels.index(LABELS["GROUPS8"].get(group_default, group_labels[0])))
urban = st.sidebar.radio("Area", ["Rural", "Urban"], index=int(float(start_value("URBAN", defaults["URBAN"]))), horizontal=True)
persons = st.sidebar.slider("Household size (people)", 1, 20, int(round(float(start_value("NPERSONS", defaults["NPERSONS"])))))
children_0_5 = st.sidebar.slider("Children aged 0-5", 0, 8, int(round(float(start_value("n_children_0_5", defaults["n_children_0_5"])))))
children_6_14 = st.sidebar.slider("Children aged 6-14", 0, 8, int(max(0, round(float(start_value("NCHILD", defaults["NCHILD"])) - float(start_value("n_children_0_5", defaults["n_children_0_5"]))))))
head_age = st.sidebar.slider("Age of household head", 15, 90, int(round(float(start_value("head_age", defaults["head_age"])))))
head_female = st.sidebar.radio("Head of household", ["Male", "Female"], index=int(round(float(start_value("head_female", defaults["head_female"])))), horizontal=True)
education = st.sidebar.slider("Years of schooling of the most educated adult (21+)", 0, 18, int(round(float(start_value("HHED5ADULT", defaults["HHED5ADULT"])))))
assets = st.sidebar.slider("Household assets index (0-30: goods and housing items owned)", 0, 30, int(round(float(start_value("HHASSETS", defaults["HHASSETS"])))))
ration_labels, ration_lookup = labelled(LABELS["RC1A"])
ration_default = str(int(float(start_value("RC1A", defaults["RC1A"])))) if str(start_value("RC1A", defaults["RC1A"])).replace(".0", "").isdigit() else "2"
ration_choice = st.sidebar.selectbox("Ration card type", ration_labels,
                                     index=ration_labels.index(LABELS["RC1A"].get(ration_default, ration_labels[1])))
land = st.sidebar.radio("Owns or cultivates land", ["No", "Yes"], index=int(round(float(start_value("FM3", defaults["FM3"])))), horizontal=True)
st.sidebar.caption("The other inputs of the model (about 120 survey answers) are set to the typical household of the study sample, "
                   "or kept from the chosen real household.")

# ---------------------------------------------------------------- build the model input row
row = {name: (start_value(name, defaults[name])) for name in features}
for name in nominal:
    value = row[name]
    row[name] = str(int(float(value))) if str(value).replace(".0", "").lstrip("-").isdigit() else str(value)
caste_code = int(group_lookup[group_choice])
religion_code = {6: "2", 7: "4", 8: "3"}.get(caste_code, "1")           # Muslim, Sikh/Jain, Christian, otherwise Hindu
row.update({
    "STATEID2": state_lookup[state_choice], "GROUPS8": str(caste_code), "ID14": religion_code,
    "ID13": str(caste_code) if caste_code <= 5 else row["ID13"],
    "URBAN": float(urban == "Urban"), "NPERSONS": float(persons), "n_children_0_5": float(children_0_5),
    "NCHILD": float(children_0_5 + children_6_14), "head_age": float(head_age), "head_female": float(head_female == "Female"),
    "HHED5ADULT": float(education), "HHASSETS": float(assets), "RC1A": ration_lookup[ration_choice], "FM3": float(land == "Yes"),
    "assets_per_capita": assets / persons, "children_share": (children_0_5 + children_6_14) / persons,
    "has_school_age_kids": float(children_6_14 > 0),
})
row_frame = pd.DataFrame([row])[features]

# ---------------------------------------------------------------- results
escape_probability, single_models = predict_risk(row_frame)
risk = 1 - escape_probability
band = int(np.digitize(risk, band_edges))
left, right = st.columns([1, 1])
with left:
    st.subheader("Result")
    st.metric("Estimated chance of escaping poverty by 2011-12", f"{escape_probability:.0%}")
    st.metric("Risk of staying poor", f"{risk:.0%}")
    st.write(f"This household is in the **{band_names[band]}** group of predicted risk among the {len(test_rows):,} held-out test households. "
             f"In that group, **{stay_poor_by_band[band]:.0%}** of households really stayed poor "
             f"(average over all groups: {float(1 - test_rows['ESCAPED'].mean()):.0%}).")
    st.caption("Estimate from the XGBoost model. For comparison: " + " | ".join(f"{name} {p:.0%}" for name, p in single_models.items()))
    if preset is not None:
        st.info(f"This is a real household from the held-out test villages. It did "
                f"{'escape' if int(preset['ESCAPED']) == 1 else 'stay poor'} by 2011-12.")
with right:
    st.subheader("What pushed the estimate up or down (SHAP, XGBoost model)")
    xgboost_pipeline = models["XGBoost"]
    preprocessor, booster = xgboost_pipeline.named_steps["prep"], xgboost_pipeline.named_steps["clf"]
    encoded = preprocessor.transform(row_frame)
    encoded = encoded.toarray() if hasattr(encoded, "toarray") else np.asarray(encoded)
    encoded_names = [n.split("__", 1)[1] for n in preprocessor.get_feature_names_out()]
    contributions = pd.Series(make_explainer(booster).shap_values(encoded)[0], index=encoded_names)
    by_variable = contributions.groupby(original_variable).sum()
    top = by_variable.reindex(by_variable.abs().sort_values(ascending=False).index)[:10][::-1]
    names = [feature_info[v]["label"][:44] for v in top.index]
    fig, axis = plt.subplots(figsize=(6.2, 4.2))
    axis.barh(names, top.values, color=["#0F766E" if v > 0 else "#C2410C" for v in top.values])
    axis.axvline(0, color="k", lw=0.8)
    axis.set_xlabel("pushes toward escaping (right) or staying poor (left), log-odds")
    axis.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig)
    st.caption("SHAP shows what the model uses. It does not show that changing a factor would cause escape.")
