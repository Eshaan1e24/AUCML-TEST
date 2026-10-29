# Viva guide: questions you may get, and plain answers

The viva is marked for each person on their own (3 marks). The coordinator wrote that **every team member must know the whole
project**: the problem, the data, the methods, the algorithms, the results, the limits and the future scope, not only their own slides.
So read all of this, say the answers in your own words, and do the swap test at the end.

The numbers below come from the notebook outputs (`outputs/`). If you do not know an answer, say what you do know and say you would check it
in the notebook. Never guess a number.

## The project in one minute

We took poor households from a survey done in 2004-05. The same households were visited again in 2011-12. We asked: using only what was
known in 2004-05, can we predict which poor households were no longer poor seven years later? About 69 in every 100 had escaped.
Our best model (XGBoost) ranks households better than chance (ROC-AUC 0.72, against 0.49 for a dummy) and its probabilities are reasonably well
calibrated. The 20% of households it ranks highest-risk stayed poor 57% of the time, against 31% on average. It is a tool for ranking and
screening, not for deciding about one family.

## 1. Problem and use case

**What is the problem and why does it matter?** Welfare budgets are limited. If a programme can tell which poor households are least likely to
improve on their own, it can reach them first.

**What is the application domain?** Social welfare and poverty targeting (public policy). The machine learning task is classification:
escaped or stayed poor.

**Who would use it?** Welfare departments (rank households), NGOs and microfinance institutions (choose villages and families), and researchers
(see which conditions go with leaving poverty).

**Which SDGs?** SDG 1 (no poverty, target 1.2) and SDG 10 (reduced inequalities, target 10.2). We measure only the money side of poverty
(household spending). Caste, religion and state are inputs so differences between groups can be seen.

**Your registered idea mentioned propensity matching. Where is it?** The registered idea was to predict escape with three models, rank factors
with SHAP, and optionally add a small propensity-score analysis. All of it is delivered. The optional part became the education analysis, which
compares similar households using weights built from propensity scores. We kept it small and say clearly that it shows association, not cause.

**Which studies are closest to yours?** Krishna (2004): 35 villages in Rajasthan, 11.1% of households escaped poverty and 7.9% fell into it, with poverty defined by the communities.
Thorat and co-authors (2017): the same IHDS panel with Tendulkar lines, about 65% of the households poor in 2005 had escaped by 2012, and Adivasi and Dalit households escaped less. Their work
describes, it does not predict. Narendranath and co-authors (2018): machine learning on the same panel, but we could not access its results. McBride and Nichols (2018): testing on data the model has
not seen, and ensembles, improve poverty targeting tools. Aiken and co-authors (2022): machine learning trained on survey data was used to target cash aid in Togo and cut errors of exclusion by 4 to 21%
compared with geographic targeting. Jean and co-authors (2016): satellite images explain up to 75% of the variation in local consumption and wealth.

**What is your contribution?** We found no accessible study that predicts household poverty transitions in India, explains the predictions, and tests on villages the model has never seen.

**What is the difference from predicting who is poor?** Most poverty studies describe one year. We follow the same households over seven years and
predict a change, which is harder.

**Why seven years and why only poor households?** The two survey rounds are 2004-05 and 2011-12, so that is the gap the data allow. We ask about
escape, so we start from poor households. (For interest, 9.9% of households that were not poor in 2004-05 were poor in 2011-12.)

## 2. Data

**What is IHDS?** The India Human Development Survey, run by the University of Maryland and NCAER. It visited about 41,000 households in 2004-05
and went back to them in 2011-12. We got it from ICPSR as Stata files.

**What is panel data?** The same units (here households) measured more than once.

**How many households do you use?** 41,554 were surveyed in 2004-05. 12,482 were poor on the Tendulkar line. Of these, 11,146 could be followed to
2011-12 with a valid poverty flag. Those are the households we model. 7,731 escaped (69.4%).

**How did you link the two surveys?** The second survey does not store the old household number, so we rebuilt it from the state, district, village,
household and split codes. We checked it against the official tracking sheet that comes with the data. About 83% of the first-round households were
found again, which matches the 83% in the IHDS user guide.

**What about households that split or were added?** If a household split, we follow the continuing household (split number 1). Households added in
2011-12 as replacements are dropped. If we follow the household of the 2005 head instead, the outcome is the same for 99.9% of the households where the
head can be tracked.

**Attrition?** About 11% of poor households could not be followed, often because they moved. They are not a random group (more often urban, less land).
Re-weighting for this moves the escape rate only from 69.4% to 69.7%.

**Are the results representative of India?** Not exactly. The survey gives each household a weight for national estimates, and our models are trained
without weights. As a check, with the weights the escape rate is 68.2% (against 69.4%) and the weighted ROC-AUC of XGBoost is 0.701 (against 0.722).
The story is the same, but the numbers describe our sample. The IHDS guide also cautions users against relying only on the smaller state samples.

## 3. The poverty line and the target

**Why did you recompute the 2004-05 poverty flag?** The flag that comes with the 2004-05 file uses an older official line. The 2011-12 flag uses the
Tendulkar line. Comparing them would be unfair. The 2011-12 file also stores the Tendulkar line in 2004-05 prices, so we used it for both rounds. One
sentence: "We measured poverty with the same ruler in both years." With it, 37% of people were poor in 2004-05, matching the published 37%. The older
line gives 25%.

**What is the Tendulkar line and what are its criticisms?** It is the official poverty line from the 2009 expert group: monthly spending per person,
set by state and by rural or urban area. Some experts say it is too low, and a later committee (Rangarajan, 2014) proposed a higher line. A different
line would change who counts as poor. We chose Tendulkar because IHDS provides it for both rounds.

**What is the target?** ESCAPED = 1 if the household was poor in 2004-05 and not poor in 2011-12, otherwise 0.

## 4. Features, selection and missing values

**What features do you use?** 137 features from 2004-05 in ten groups: assets and housing, jobs, household structure (children, dependants), services
(ration card, water, fuel), social capital, education, finance, geography and social group (state, caste, religion), women's status and health.
118 are numbers and 19 are categories. The full list is in Appendix A of the report.

**How did you select features from 945 columns? Is there feature selection?** Two steps. First by domain knowledge and simple rules: ten groups, no
spending or income, no IDs or weights, nothing with more than 40% missing values. Second, a data-driven check: we ranked the features by importance in a
model trained on training villages only and refit XGBoost with the top 10, 20, 40, 80 or all 137. The test ROC-AUC was 0.693, 0.708, 0.717, 0.721 and
0.722. So about 40 features already give almost the same score. We kept all 137 for the main model.

**Why keep all 137 features if 40 give almost the same score?** The top 40 reach a test ROC-AUC of 0.717 against 0.722 with all of them. We keep all 137 because nothing is lost and the explanations then cover every group of factors, and we show the smaller set to prove the model does not depend on a long tail of features.

**Which features did you engineer?** From the person records we built household features: age and sex of the head, share of dependants, number of children aged 0 to 5, average schooling of adults, share of working adults, and the number of diagnosed illnesses. From the household file we added ratios such as assets per person and rooms per person. Assets per person is the fourth strongest feature in SHAP.

**How did you handle missing values?** The survey codes missing answers as -1 to -9, so we turned those into blanks. One feature (education of the
head's father) had over 40% blanks and was dropped. The other blanks in numbers were filled with the median (the middle value), which is simple and not
bothered by extreme values. The features with the most gaps are child school enrolment (35%) and some questions asked only of women (up to 28%).

**How are blank answers in category columns handled?** They get their own category called 'missing', and then the category is one-hot encoded like the others.

**Why cap outliers and why one-hot encode?** A few cells hold typing errors (for example 100 meals a day), so values are capped at the 0.5th and 99.5th
percentile of the training data. One-hot encoding turns a category such as state into one yes or no column per state, because the models need numbers.
Numbers are scaled only for Logistic Regression, which needs it.

**What is data leakage and how did you avoid it?** Leakage means giving the model the answer, or information it would not have in real use. We use
nothing from 2011-12 as an input. We also chose to leave out spending and income, because poverty is defined from spending. All fill-in values and
limits are learned inside the training folds only. When we added spending and income back as a test, the score changed by less than 0.01.

**The ration card is a government poverty label. Is that a problem?** It is 2004-05 information, so it is not leakage. But because the government gave
that label to poor households, we do not read it as a risk factor. Dropping it lowers XGBoost's ROC-AUC from 0.722 to 0.715.

**What if you removed state?** We did not test that. State is one of the strongest features, so we would expect the score to fall.

## 5. Method

**Why split by village and not randomly?** Households in one village share roads, prices, jobs and weather. In a random split, neighbours would be in
both training and test data. We checked: with 20 random splits XGBoost scores 0.708 on average, and with 20 village splits 0.710. They are close here, so
neighbours did not inflate our scores much, but the village split is the safe design and we could not know that in advance.

**What is cross-validation?** We cut the training villages into five groups, train on four and check on the fifth, and rotate. We use it to choose
settings. The test villages are never used to choose models or settings.

**Why 80/20, and why is the threshold chosen separately?** 80/20 is a common split. The threshold (cut-off) is chosen on predictions made for the
training households while their own village was hidden (out-of-fold predictions), so the test set stays untouched.

**Why these four models and why not a neural network or SVM?** Logistic Regression is simple and easy to explain. Random Forest and XGBoost can find
curved patterns and interactions. The ensemble averages the three. The dummy shows what no skill looks like. We have about 9,000 rows of mixed survey
data, where tree models are the usual strong choice, and they are easier to explain than a neural network.

**What is the difference between Random Forest and XGBoost?** Random Forest grows many trees independently and averages them (bagging). XGBoost grows
trees one after another, each correcting the errors of the last (boosting).

**What is an odds ratio?** For Logistic Regression, exponentiating a coefficient gives how many times the odds of escaping change when a feature goes up by one unit. In our model the numbers are scaled, so the change is per one standard deviation. For a category column (such as one state) it compares that category with not being in it. Logistic Regression is also regularised, which pulls the values towards 1. We saved them in `outputs/logistic_odds_ratios.csv`.

**Why no class weights, and why not SMOTE?** About 69% escaped, which is only mildly unbalanced. Class weights pull the predicted probabilities away from the real rates, and we wanted probabilities that can be read as real chances. SMOTE (which makes synthetic extra rows of the smaller class by blending neighbouring rows) would also change the class balance the model sees, and we did not test it.

**What settings did XGBoost end up with?** 600 trees, depth 5, learning rate 0.02, subsample 0.85, minimum child weight 10, column sample 0.7 and regularisation 5, found by the random search.

**What is hyper-parameter tuning?** Settings of a model that you choose before training (for example tree depth). A random search tries many
settings and keeps the one with the best cross-validated ROC-AUC (11 tried for Logistic Regression, 20 for Random Forest, 30 for XGBoost).

**Why threshold 0.645? What if the agency wants to catch more stayed-poor households?** The cut-off turns a probability into "escaped" or "stayed
poor". 0.645 gave XGBoost the best average F1 of both classes on training predictions. Raising the cut-off flags more households as stayed poor: you
catch more of them (higher recall) but also raise more false alarms (lower precision). The agency can choose the cut-off to match its budget.

**Why did you choose XGBoost as the headline model?** It has the best cross-validated ROC-AUC (0.696), and we fixed that rule before looking at the test
set. On the test villages XGBoost (0.722) and the ensemble (0.719) are within chance of each other.

## 6. Metrics and results

**What is ROC-AUC?** Take one household that escaped and one that stayed poor at random. ROC-AUC is the chance that the model gives the escaped one the
higher score. 0.5 is guessing, 1.0 is perfect.

**What are precision, recall and F1?** Precision: of the households we call "escaped", the share that really escaped. Recall: of the households that
really escaped, the share we found. F1 balances the two. For XGBoost on the test villages: escaped households precision 0.796, recall 0.755, F1 0.775.
Stayed-poor households: precision 0.506, recall 0.564, F1 0.533.

**Read the confusion matrix.** For XGBoost: of 693 households that really stayed poor, the model found 391 (56%). Of 1,559 that escaped, it found 1,177
(75%). It misses a lot, which is why we say "ranking, not deciding".

**Why not use accuracy?** A model that always says "escaped" is right about 69% of the time and finds no household that stays poor. Our models reach
68 to 70% accuracy, so accuracy tells us almost nothing.

**Are your results good?** Moderate. 0.72 is enough to rank households, and the ranking is useful (highest-risk 20% stayed poor 57% against 31%). It is
not enough to decide about one family. Adding more data (village information, neighbours, even spending and income) does not help, so the limit comes from
the problem: escaping is partly a noisy crossing of a line, and seven years of events (illness, harvests, jobs) cannot be seen in 2004-05.

**Why is the dummy's ROC-AUC 0.487 and not 0.5?** The dummy gives every household the same score, so its true ROC-AUC is exactly 0.5. We added tiny random noise to break ties, which gives 0.487.

**What are MCC and PR-AUC?** MCC (Matthews correlation coefficient) is a correlation between the predictions and the truth, from -1 to 1, and stays honest when classes are unequal. XGBoost has an MCC of 0.310. PR-AUC is the area under the precision-recall curve. For the escaped class XGBoost has 0.844, and the dummy 0.691 (the base rate).

**Do the models really differ?** XGBoost and the ensemble are the best and cannot be told apart. Both beat Logistic Regression and Random Forest in most
comparisons. Over 20 different village splits the averages were: ensemble 0.711, XGBoost 0.710, Logistic Regression 0.701, Random Forest 0.696. One split
can move a score by about 0.015.

**Test ROC-AUC (0.722) is higher than cross-validation (0.696). Is that overfitting?** No. Cross-validation trains on only part of the training data
and its folds vary (standard deviation about 0.016). A single test split also varies by about 0.015, and across 20 splits the XGBoost average is 0.710.
So 0.722 is a normal draw. On the households it learned from, XGBoost scores 0.851, Logistic Regression 0.731 and Random Forest 0.988, so Random Forest fits its training households almost perfectly. That is why we judge models only on cross-validation and unseen villages.

**What is calibration?** Whether a predicted 70% really means about 70 in 100. Our average predicted chance of escaping is 69.0% and the real rate is
69.2%, with a calibration slope of 1.07 (1 is perfect).

**What is the Brier score?** The average squared error of the predicted probabilities (lower is better). XGBoost: 0.183, about 14% better than always
predicting the average.

**What is a bootstrap 95% interval?** We redraw whole villages 1,000 times and recompute the score each time. The middle 95% of the scores is the
interval. It shows how much a score could move by chance.

**What does the risk table show?** Test households sorted into five equal groups by predicted risk. In the highest-risk group 57% stayed poor (1.9
times the average of 31%), in the lowest only 11%. The riskiest 40% hold 63% of all households that stayed poor.

## 7. Explanation and the education analysis

**What is SHAP?** A way to split one prediction into the push from each feature, like splitting a bill among items. Averaging the size of the pushes
over many households shows which features the model uses most.

**What are the most important features?** Number of children aged 0 to 5 (more young children push towards staying poor), state, household assets
(more assets push towards escape), ration card type, and caste and religion group.

**On which households is SHAP computed?** On the test households, using the final XGBoost model. For each household we add up the pushes of the yes/no columns that belong to the same variable, then average the size of that sum over households.

**Does SHAP prove these things cause escape?** No. It shows what the model relies on. Features that move together (education, assets, jobs) share credit.

**What did you find about education?** Poor households where an adult had 10 or more years of schooling escaped 11.1 points more often. After comparing
with similar households (same state, caste, area, family structure, land) the gap is about 6 points, and about 5 if we also adjust for how poor the
household was.

**Why 6.3 and 5.4, and what about the matching result?** 6.3 compares similar households on their starting traits. 5.4 also adjusts for how poor the household was in 2004-05. That depth of poverty is measured at the same time as education, so it may itself be partly a result of education, and the second number may over-adjust. A nearest-neighbour matching version gives 8.1 points, but it comes without a valid interval, so we show it only for comparison.

**Is that causal? What is a propensity score, and the E-value?** No, it is an association. A propensity score is the estimated chance that a household
has an educated adult, given its other traits. Weighting by it makes the two groups similar. The E-value (about 1.4) says how strong a hidden cause
would have to be, with both education and escape, to explain the gap away. 1.4 is not strong, so we call the result suggestive.

## 8. Limits, ethics and the future

**What are the limits?** Accuracy is modest. Poverty is a noisy crossing of a line (one in five poor households were within 10% of it). Spending was
collected with different item lists (47 items, then 52). About 11% of poor households were lost. The data are old (2004 to 2012). The results show association, not cause. The illness
feature may contain zeros that mean "not recorded" in some villages.

**Is it ethical to use caste, religion and state as inputs?** They are inputs so that inequality can be seen, and they are strong predictors. A real
programme must never use the score to exclude a group. We did not run a group-by-group error check. That is future work.

**Would you deploy it?** Not as it is. The data are old, accuracy is modest, and a wrong prediction about one family has real consequences. It needs newer
data and fairness checks first.

**What is the future scope?** Newer panel data, satellite or village data, a model for falling into poverty, fairness checks by group, and a field
version of the app.

## 9. Implementation and the demo

**How do we know the results are not luck?** Seeds are fixed, the cross-validation folds are saved, and running the notebook again gives identical result
tables, also with a different version of scikit-learn. A full run takes about 30 minutes on our laptop. `quick_check.py` recomputes the headline scores in seconds.

**Show the project structure.** The notebook writes everything into `outputs/`. The charts, slides, report and app read from there. See the folder tree
on the implementation slide (slide 18) and in Section 5.2 of the report.

**What does the app do?** You enter a household's 2004-05 details (or start from a real test household). It shows the estimated chance of escaping, the
risk group and how often households in that group really stayed poor, and a SHAP chart. The other inputs are set to the typical household. It carries a
warning that it is a screening tool.

## 10. The swap test (do this together before the viva)

Each person answers two questions about **another** person's part. A listener checks the answer against this guide.

| Asked about | Questions to practise |
|---|---|
| Anhad's part (problem, literature, conclusion) | What is the application domain? What did you register and what changed? Which studies are closest and what is your contribution? What are the limits? |
| Aman's part (data, features, implementation) | Why did you recompute the poverty line? How did you handle missing values? How did you select features? Show the project structure. |
| Eshaan's part (methods, SHAP, education) | Why split by village? Why XGBoost and not a neural network? What does SHAP show? Is education causal? |
| Gokul's part (results) | Define precision, recall and F1 and read the confusion matrix. Why not accuracy? Is 0.72 good? What does the risk table show? |

**Short answers to keep ready**

- **Target:** "Escaped means poor in 2004-05 and not poor in 2011-12, measured with the Tendulkar line both times."
- **Split:** "We test on whole villages the model has never seen."
- **Result:** "It ranks households well enough for screening, not well enough to decide about one household."
- **Not sure:** say what you know, and that you would check it in the notebook (give the section number).
