# Predicting Household Escape from Poverty in India

AUCML (TE7483) ESE case study, SIT Pune. Data: India Human Development Survey, 2004-05 (IHDS-I) and 2011-12 (IHDS-II).
Team: Anhad Mahajan, Aman Sumeet Saxena, Eshaan Sumesh, Gokul Sethumadhavan. Guide: Dr. Shrikrishna Kolhar.

## What is in this folder

| File | What it is |
|---|---|
| `IHDS_poverty_escape_v3.ipynb` | The main notebook, already run (all outputs are inside). 12 sections, from the data check to saving results. Sections 1 to 9 are the core project, sections 10 and 11 are extra checks. |
| `AUCML_Project_Report.docx` and `.pdf` | The written report (problem, dataset, methodology, implementation, results, conclusion, future scope, references, appendices). |
| `IHDS_poverty_escape_presentation_v4.pptx` | The presentation: 31 main slides, references and 8 backup slides, with speaker notes on every slide. |
| `PRESENTATION_PLAN.md` | Who presents what, three timed versions (10, 12 and 15 to 17 minutes), the demo script and a rehearsal checklist. |
| `VIVA_GUIDE.md` | Plain-language questions and answers for the viva, and a swap test so that everyone can defend the whole project. |
| `app.py`, `app_labels.json`, `ihds_tools.py` | The Streamlit demo (and a helper class that the notebook and the app share). |
| `quick_check.py` | Re-checks the headline results in a few seconds from the saved predictions (good for showing live). |
| `outputs/` | Every table (CSV), `key_numbers.json`, charts (PNG) and the trained models (`model_bundle.joblib`). `outputs/figures_ppt/` has the clean single charts. |
| `make_charts_v3.py`, `make_exec_evidence.py`, `build_deck_v4.py`, `deck_helpers.py` | Rebuild the charts and the slides from `outputs/`. |
| `report_tools/` | Scripts that build the report from `outputs/` (set `RUN_DIR` to this folder, run `prep_report_data_v4.py`, then `node build_report_v4.js`; needs the Node package `docx`, and the contents table is refreshed in Word). |
| `requirements.txt` | Exact package versions used for the reported numbers. |
| `CHANGES_FROM_V2.md` | What was wrong in the first version (v2) and what changed. |
| `NOTE_FOR_TEAM.md` | A short message to send to the team. |

The raw survey data is **not** included (ICPSR terms of use: keep it inside the team). It is in Aman's archive: the folders
`ICPSR_22626-V12` and `ICPSR_36151-V6`.

## How to run

1. Python 3.11. Install the packages: `pip install -r requirements.txt`
2. Put the two ICPSR folders next to the notebook (or set the environment variable `IHDS_DATA_DIR` to the folder that contains them).
3. Open the notebook and choose Run All. It takes about 30 minutes on our laptop. The notebook checks the size and checksum of each data file first.
4. Quick re-check of the results (seconds, no data needed): `python quick_check.py`
5. Charts and slides: `python make_charts_v3.py` then `python build_deck_v4.py` (needs `python-pptx`).
6. Demo app: `streamlit run app.py` (needs `outputs/model_bundle.joblib`, which the notebook writes).

Running the notebook again gives identical result tables. We checked this twice with the same package versions and once with a different scikit-learn version
(1.6.1 with XGBoost 2.1.4): 22 of the 24 output files were byte for byte identical, and the other two only record the package versions or store the saved models.

## Headline results (test villages, 2,252 households)

- Poor households in 2004-05 followed to 2011-12: 11,146. Escaped: 7,731 (69.4%).
- ROC-AUC: XGBoost 0.722, ensemble 0.719, Random Forest 0.709, Logistic Regression 0.700 (dummy 0.487).
- XGBoost is the headline model because it has the best cross-validated AUC (chosen before looking at the test set). It is not significantly different from the ensemble.
- Feature selection check: the 40 most important of 137 features already reach a test ROC-AUC of 0.717.
- The probabilities are reasonably well calibrated (calibration slope 1.07; average predicted 69.0%, real 69.2%).
- The highest-risk 20% of households stayed poor at 57% (1.9 times the average of 31%).
- Education (10+ years in the household) goes with a 5 to 6 point higher escape rate after adjustment (not proof of cause).

## How this answers the coordinator's email (7 October 2026)

| Requirement | Where |
|---|---|
| Problem, objective, scope, application domain, users, real-world relevance | Report 1.2 to 1.7, slides 4 to 6 |
| Refined version of the registered idea | Report 1.6, slide 6 |
| Data source, features, target, missing values, feature selection and engineering, validation | Report 3 and 4.1, slides 8 to 14, Appendix A (feature dictionary) |
| Pipeline with justification, training strategy, evaluation | Report 4, slides 15 to 17 |
| Implementation, workflow, execution, outputs, project structure | Report 5, slides 15, 18, 19, the notebook, `quick_check.py`, the app |
| Accuracy, precision, recall, F1, confusion matrix, ROC-AUC, comparison | Report 6, slides 20 to 25 |
| Final report | `AUCML_Project_Report.docx` |
| Every member knows the whole project | `VIVA_GUIDE.md` and the swap test |
| Not unnecessarily complex | The talk follows one simple story. Extra checks are in backup slides and Appendix C. |

## Who presents what

| Presenter | Sections | Slides |
|---|---|---|
| Anhad | 1 Problem and Use Case, 2 Literature Review, 8 Conclusion | 1 to 7 and 29 to 31 |
| Aman | 3 Dataset and Preprocessing, 5 Implementation | 8 to 13 and 18 to 19 |
| Eshaan | 4 Methodology, 7 Interpretation | 14 to 17 and 26 to 28 |
| Gokul | 6 Results and Evaluation | 20 to 25 |

## Still to check by the team

- The submission format and the time slot are not announced yet. When they are, tell us and we adapt the files and choose the slide version in `PRESENTATION_PLAN.md`.
- Every member must read the report, the slides and `VIVA_GUIDE.md` and be able to explain them.
