# What changed from Aman's version (v2), and why

Every item below was checked against the raw survey files or the official IHDS documents, and the new numbers were
re-checked by an independent review. Things that were already correct in v2 are listed at the end.

## Problems found in v2 and what v3 does

| # | Problem in v2 | Why it matters | What v3 does |
|---|---|---|---|
| 1 | **The two survey rounds used different poverty lines.** The flag in the 2004-05 file (`POOR`) uses the old Planning Commission line; the 2011-12 flag uses the Tendulkar line. The notebook and slides said both were Tendulkar. | "Poor in 2005" was a much poorer group than "poor in 2012" (7,206 households instead of 11,146), and 30% of the "newly poor" were already below the Tendulkar line in 2005. | Wave-1 poverty is recomputed as spending per person < `POVLINE2005` (the Tendulkar 2004-05 line, stored in the 2011-12 file). Person-weighted poverty in 2004-05 becomes 37.4%, matching the published 37%. The old flag gives 24.8%. |
| 2 | **Results changed with the scikit-learn version.** `GroupKFold` breaks ties differently in different versions, so the folds, the tuned settings and the model ranking changed. "Exactly the same numbers" was not true. | A teammate running the notebook could get a different winner. | Folds come from our own deterministic function `stable_group_folds` and are saved (`outputs/cv_folds.csv`). Pinned `requirements.txt`. Identical tables on two different scikit-learn versions. |
| 3 | **Class weights made the probabilities wrong** (average predicted escape about 55% when 68% escaped). | The demo "probability" would mislead. | No class weights. Calibration is reported (slope, Brier skill score, calibration chart). |
| 4 | **The model ranking was over-claimed.** The ensemble was called best from one split; it was not significantly better than Logistic Regression or XGBoost. | Examiners ask "is it really better?". | Headline model chosen by cross-validated AUC before looking at the test set (XGBoost). Paired tests, and 20 repeated village splits to show how stable the ranking is. |
| 5 | **The matching analysis was fragile.** Its confidence interval used a bootstrap that is not valid for matching with replacement, and the effect fell from 5.9 to 3.2 points when baseline poverty depth was added. | The education claim was not reliable. | Three estimators with valid village-bootstrap intervals (regression, weighting, doubly robust), with and without baseline poverty depth, plus the E-value. Result: about 5 to 6 points. |
| 6 | **Survey weights were ignored without a check.** | Results describe the sample, not India. | Weighted escape rate and weighted AUC reported as a sensitivity check. |
| 7 | **SHAP importance overstated categorical variables** (state) by summing absolute values over one-hot columns. | The ranking of top features was wrong. | Contributions of one-hot columns are summed per household first. "Children aged 0-5" is now first, state second. |
| 8 | **The health feature was mislabelled.** `health_observed` meant "has a diagnosed illness", not "covered by the module", and the illness counts were dropped. | A real feature was lost and the label was wrong. | Replaced by `n_major_illness` and `any_major_illness`. Caveat: in 261 of 2,474 villages nobody was listed (about 59 expected by chance), so a 0 may mean "not recorded". |
| 9 | **Wrong statements on slides.** "Refinement since Phase I" (there was no Phase I); "matched on all other features" (it used 11); "Dalit households escaped less" (65.3% vs 66.3%, no difference); "over three quarters of the model's decisions"; SDG 10.2 wording; "few studies use machine learning..." (Narendranath et al. 2018 did, on the same panel); "47 vs 52 items makes mobility look larger" (no source says this). | These are the first things a careful examiner catches. | All rewritten from the new outputs. The deck is built by a script that reads its numbers from the notebook outputs. |
| 10 | **Other:** hard-coded `D:/` path and a `pip install` inside the notebook, no requirements file, the old leaky notebook shipped next to the new one, Streamlit listed but no app, placeholders. | Hurts "Implementation" and "Viva". | Fixed. A working demo app is included (`app.py`). |

## Already correct in v2 (checked and kept)

- The household counts (41,554, 42,152, the 83.4% re-interview rate) and the rebuilt household link (it agrees with the
  official tracking sheet; following the 2005 head of household gives the same outcome for 99.9% of tracked households).
- No wave-2 information in the inputs; spending and income left out; village-based split; preprocessing inside the pipeline.
- The exploratory numbers by caste, education and area (they change slightly because the sample changed).

Note on item 3: the 55% was measured on the first version's saved test predictions (its ensemble's average predicted chance of escaping was 0.545, against a real escape rate of 0.676 in its test villages). The first version is not part of this folder.

## Numbers that changed because of fix 1

| | v2 | v3 |
|---|---|---|
| Poor households modelled | 7,206 | 11,146 |
| Escape rate | 66.1% | 69.4% |
| Non-poor households that became poor | 12.1% | 9.9% |
| Test ROC-AUC (best model) | 0.684 (ensemble) | 0.722 (XGBoost) |
| Test households | 1,408 | 2,252 |

The higher AUC is partly because the group is larger and partly because it is now defined consistently; it is still a modest
result, and the notebook says so.

## Known limits that remain (also in the notebook and slides)

- Escaping is partly a noisy crossing of a poverty line; one in five poor households were within 10% of the line.
- About 11% of poor households could not be followed (attrition); it is not random, and re-weighting changes little.
- The illness feature may contain "not recorded" zeros; the education result is an association, not proof of cause.
- 20 repeated splits use tuned settings from the original training set, so they show stability, not unbiased scores.
- A different poverty line would change who counts as poor.

## Second round (7 October 2026): after the coordinator's email

The coordinator asked for a refined, complete, understandable and properly implemented project, with feature selection, model execution and project
structure clearly shown, all the standard metrics for the compared models, a structured report and every member knowing the whole project.
Two independent reviews (an examiner simulation and a student-readability audit) were run against the finished work. What changed:

| Gap found | What was done |
|---|---|
| Application domain never stated | Stated on slide 5, in report 1.4 and in the notebook introduction. |
| No link back to the registered idea | New slide 6 and report 1.6 (registered idea against what was delivered). |
| Feature selection not shown | Notebook check (top 10, 20, 40, 80 or all 137 features), slide 11, report 3.6. The 40 most important features reach 0.717 against 0.722. |
| No feature list or missing-value table | Feature dictionary (Appendix A), missing-value table (report 3.7, slide 12), group table (report 3.5). |
| Precision, recall, F1 and confusion matrix for the headline model only | Full per-class table and confusion matrices for all four models (notebook, slides 22 and 24, report 6.1 and 6.2). |
| Project structure and execution not demonstrated | Workflow diagram (slide 15), folder tree (slide 18), real notebook output and quick check output (slide 19), and a code excerpt (report 5.3). |
| Justification of models thin | One line per model and "why not a neural network" (slide 16, report 4.3). |
| Overfitting and village-split questions unanswered | Train, cross-validated and test scores, and random split against village split (notebook, report 6.3, 4.1). |
| Slides too dense (26 of 33 slides over 90 words, about 40 minutes of reading) | New lean deck: plain text, large type, speaker notes. Heavy material (calibration, 20 splits, robustness, education details, SHAP by group, glossary) moved to 8 clearly marked backup slides. |
| Report too technical in the main chapters | Advanced analyses moved to Appendix C. The education result is explained simply in the main text. |
| Viva guide missed 21 of 40 likely questions | Rewritten to cover all of them, plus a swap test between members. |
| Literature thin on real use of machine learning for targeting | Two verified references added (McBride and Nichols 2018, Aiken et al. 2022). |
| "Leakage" wording for the spending and income choice | Now "left out on purpose" (spending is 2004-05 information; it is left out so that the model shows the main starting conditions). |

## Plain-language pass (7 October, evening)

After the coordinator's email we read every piece of text again for three things: technically correct, easy to read, and not written in a stiff or machine-like voice. What changed:

| What we found | What we changed |
|---|---|
| Slide titles named a topic and not the point | Most titles now state the point (for example "XGBoost scores highest, but all four models are close"). The small section tag at the top of each slide still shows which part of the marking scheme it belongs to. |
| Short label-and-fragment lines and repeated slogans ("a screening aid, not a decision about one family" appeared about six times) | Full plain sentences. The caution is said clearly where it matters (limits, conclusion, demo) and not on every slide. |
| A "Source" line under 23 slides | Removed. The data source is named on the dataset slide and in the references. |
| Speaker notes had no hand-overs | Each person's first slide starts with a thank-you and a one-line preview, and the notes read like speech. |
| The notebook introduction listed changes from an earlier draft that an examiner has never seen | It now explains what the notebook does. The history stays in this file. |
| The report and slides gave a figure (55% predicted against 68% real) for a draft that is not part of this folder | Replaced with the plain reason: class weights pull the predicted chances away from the real rates. |
| The State row of the SHAP table in the report showed 0.184 while the chart showed 0.185 | The report now reads the unrounded value from the saved table: the value is 0.1845, which rounds to 0.185. |
| Long paragraphs in the report (missing values, validation, model comparison) | Split into shorter paragraphs, and cross-validation is explained in one sentence where it first appears. |
| Duplicate and misplaced questions in the viva guide | Duplicate removed, and added questions moved next to their topic. |

No result, table or chart value changed in this pass, except the one rounding fix above.
