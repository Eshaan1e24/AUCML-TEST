// Builds the written report (Word) from report_data.json. Every number comes from the notebook outputs.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType,
  BorderStyle, ShadingType, ImageRun, LevelFormat, PageBreak, Footer, PageNumber, TableOfContents,
} = require("docx");

const R = JSON.parse(fs.readFileSync(path.join(__dirname, "report_data.json"), "utf8").replace(/"([+-]\d\.\d+)"/g, (m, v) => `"${v.replace("-", "−")}"`));
const FIG = R.run_dir + "/outputs/figures_ppt/";
const FONT = "Calibri";
const TEAL = "0F766E";

let figCount = 0, tabCount = 0;
const children = [];
const figList = [], tabList = [];

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 22, bold: o.bold, italics: o.italics, color: o.color });
const P = (text, o = {}) => new Paragraph({ spacing: { after: o.after ?? 120, line: 300 }, alignment: o.align || AlignmentType.LEFT, keepNext: o.keepNext, children: Array.isArray(text) ? text : [run(text, o)] });
const H1 = (t) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true, spacing: { before: 360, after: 160 }, children: [new TextRun({ text: t, font: FONT, size: 32, bold: true, color: TEAL })] }));
const H2 = (t) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 100 }, keepNext: true, children: [new TextRun({ text: t, font: FONT, size: 26, bold: true, color: "1F2937" })] }));
const para = (t) => children.push(P(t));
const bullets = (items) => items.forEach((t) => children.push(new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 80, line: 300 }, children: [run(t)] })));
const numbered = (items, ref) => items.forEach((t) => children.push(new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 80, line: 300 }, children: [run(t)] })));
const code = (lines) => lines.forEach((l, i) => children.push(new Paragraph({ spacing: { after: 0, line: 240 }, keepNext: i < lines.length - 1, shading: { type: ShadingType.CLEAR, fill: "F3F4F6", color: "auto" },
  children: [new TextRun({ text: l === "" ? " " : l, font: "Consolas", size: 17 })] })));

function figure(name, widthIn, caption) {
  if (!R.figs[name]) { console.log("skipping missing figure", name); return; }
  figCount += 1;
  figList.push(`Figure ${figCount}. ${caption}`);
  const [w, h] = R.figs[name];
  const wpx = Math.round(widthIn * 96), hpx = Math.round((wpx * h) / w);
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
    children: [new ImageRun({ type: "png", data: fs.readFileSync(FIG + name + ".png"), transformation: { width: wpx, height: hpx }, altText: { title: caption, description: caption, name } })] }));
  children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [run(`Figure ${figCount}. ${caption}`, { italics: true, size: 20, color: "4B5563" })] }));
}

function table(caption, header, rows, widths, opts = {}) {
  tabCount += 1;
  tabList.push(`Table ${tabCount}. ${caption}`);
  children.push(new Paragraph({ spacing: { before: 160, after: 80 }, keepNext: true, children: [run(`Table ${tabCount}. ${caption}`, { italics: true, size: 20, color: "4B5563" })] }));
  const border = { style: BorderStyle.SINGLE, size: 4, color: "BFC5CC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const total = widths.reduce((a, b) => a + b, 0);
  const keep = opts.keepTogether !== false;
  const cell = (text, i, head, hl, last) => new TableCell({
    borders, width: { size: widths[i], type: WidthType.DXA },
    shading: head ? { fill: TEAL, type: ShadingType.CLEAR, color: "auto" } : hl ? { fill: "FFF1E6", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: opts.tight ? 30 : 60, bottom: opts.tight ? 30 : 60, left: 100, right: 100 },
    children: [new Paragraph({ keepNext: keep && !last, children: [new TextRun({ text: String(text), font: FONT, size: opts.size || 20, bold: head || (i === 0 && opts.boldFirst), color: head ? "FFFFFF" : undefined })] })],
  });
  children.push(new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true, false, false)) }),
      ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false, opts.highlight === ri, ri === rows.length - 1)) }))] }));
  children.push(P("", { after: 120 }));
}

// ------------------------------------------------------------------------------------------------- title page
const front = [];
front.push(new Paragraph({ spacing: { before: 1000, after: 200 }, children: [run("Applications and Use Cases of Machine Learning (TE7483)", { size: 26, color: "4B5563" })] }));
front.push(new Paragraph({ spacing: { after: 500 }, children: [run("ESE Case Study Project Report", { size: 26, color: "4B5563" })] }));
front.push(new Paragraph({ spacing: { after: 240 }, children: [run("Predicting Household Escape from Poverty in India", { size: 56, bold: true, color: TEAL })] }));
front.push(new Paragraph({ spacing: { after: 600 }, children: [run("A Machine Learning Analysis of Longitudinal Socio-Economic Factors", { size: 30 })] }));
front.push(new Paragraph({ spacing: { after: 200 }, children: [run("India Human Development Survey, 2004-05 and 2011-12", { size: 24, color: "4B5563" })] }));
front.push(new Paragraph({ spacing: { after: 600 }, children: [run("Sustainable Development Goals: SDG 1 (No Poverty) and SDG 10 (Reduced Inequalities)", { size: 24, color: "4B5563" })] }));
const tb = { style: BorderStyle.SINGLE, size: 4, color: "BFC5CC" };
const tbs = { top: tb, bottom: tb, left: tb, right: tb };
const teamRows = [["1", "Anhad Mahajan", "24070126031"], ["2", "Aman Sumeet Saxena", "24070126030"], ["3", "Eshaan Sumesh", "24070126058"], ["4", "Gokul Sethumadhavan", "24070126061"]];
const tw = [900, 4100, 2000];
front.push(new Table({ width: { size: 7000, type: WidthType.DXA }, columnWidths: tw,
  rows: [new TableRow({ children: ["No.", "Full name", "PRN"].map((t, i) => new TableCell({ borders: tbs, width: { size: tw[i], type: WidthType.DXA }, shading: { fill: TEAL, type: ShadingType.CLEAR, color: "auto" }, margins: { top: 80, bottom: 80, left: 100, right: 100 }, children: [new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 22, bold: true, color: "FFFFFF" })] })] })) }),
    ...teamRows.map((r) => new TableRow({ children: r.map((t, i) => new TableCell({ borders: tbs, width: { size: tw[i], type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 100, right: 100 }, children: [new Paragraph({ children: [run(t, { size: 22 })] })] })) }))] }));
front.push(new Paragraph({ spacing: { before: 400, after: 60 }, children: [run("Guide: Dr. Shrikrishna Kolhar", { size: 22, color: "4B5563" })] }));
front.push(new Paragraph({ spacing: { after: 60 }, children: [run("AIML-A, B.Tech 2024-28, academic year 2026-27", { size: 22, color: "4B5563" })] }));
front.push(new Paragraph({ spacing: { after: 60 }, children: [run("Department of AIML, Symbiosis Institute of Technology, Pune", { size: 22, color: "4B5563" })] }));
front.push(new Paragraph({ children: [new PageBreak()] }));
front.push(new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Contents", font: FONT, size: 32, bold: true, color: TEAL })] }));
front.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-2" }));
front.push(new Paragraph({ children: [new PageBreak()] }));

// ------------------------------------------------------------------------------------------------- abstract
H1("Abstract");
para(`Many households in India move out of poverty over time, while others stay poor for years. We use the India Human Development Survey, which interviewed the same households in 2004-05 and again in 2011-12, to ask which households that were poor in 2004-05 had escaped poverty by 2011-12. After linking the two survey rounds and measuring poverty with the same (Tendulkar) line in both rounds, we study ${R.n_kept} poor households, of which ${R.escape} escaped. We use ${R.n_features} features that describe each household in 2004-05 only.`);
para(`Logistic Regression, Random Forest, XGBoost and an ensemble of the three were compared on villages that were never used for training. All of them reach a ROC-AUC between 0.70 and 0.72, and XGBoost, our headline model, scores ${R.head_res.ROC_AUC}. The 20% of test households with the highest predicted risk stayed poor ${R.q5} of the time, which is ${R.q5lift} times the average. SHAP explanations show that the number of young children, the state, household assets, the ration card type and the caste and religion group matter most. Households where an adult has 10 or more years of schooling escaped about 5 to 6 percentage points more often after adjusting for starting differences, although this is an association and not proof of cause. The models rank households better than chance but make many individual errors, so they are suitable for screening and not for decisions about a single household.`);

// ------------------------------------------------------------------------------------------------- 1 Introduction
H1("1. Introduction and Problem Statement");
H2("1.1 Background");
para("Poverty statistics usually describe one year at a time. They say how many people are poor, but not whether the same families stay poor or move out of poverty. Surveys that visit the same families again make it possible to follow households over time, and they show that poverty is not a fixed state. Some poor households improve their situation within a few years, while others remain poor for a long time.");
H2("1.2 Problem statement");
para("Welfare programmes in India have limited budgets. They need a way to tell in advance which poor households are least likely to move out of poverty on their own, so that help can reach those households first. We therefore ask a practical question. Given what we know about a household when it is poor, can we predict whether it will still be poor seven years later, and which household conditions are most closely linked to getting out of poverty?");
H2("1.3 Objectives");
numbered([
  "Predict whether a household that was poor in 2004-05 is no longer poor in 2011-12, using only information collected in 2004-05.",
  "Compare Logistic Regression, Random Forest, XGBoost and an ensemble of the three on the same held-out villages, using metrics that suit this problem.",
  "Find the household factors that the models rely on most, using SHAP.",
  "Check whether adult education is linked to escape after adjusting for the starting differences between households.",
  "Build a small demonstration application that shows the estimated risk and the reasons behind it.",
], "num1");
H2("1.4 Application domain, intended users and real-world relevance");
para("The application domain is social welfare and poverty targeting, which is part of public policy and development economics. The machine learning task is binary classification (escaped or stayed poor) on panel survey data.");
para("A government welfare department could rank poor households by their risk of staying poor and reach the highest-risk households first. An NGO or a microfinance institution could use the same ranking to choose villages and families for livelihood and training programmes. Policy researchers could use the explanations to study which household conditions are linked to leaving poverty.");
para("The need is real. Budgets are limited, so programmes must choose whom to help first, and machine learning is already used to target aid. In Togo, for example, a machine learning approach reduced the number of poor people left out of a cash transfer programme by 4 to 21% compared with the geographic targeting options considered (Aiken et al., 2022).");
H2("1.5 Sustainable development goals");
para("The project supports SDG 1 (No Poverty), mainly target 1.2, which aims to reduce at least by half the share of people living in poverty in all its dimensions, according to national definitions. We measure only the money side of poverty, through household spending. It also supports SDG 10 (Reduced Inequalities), mainly target 10.2, which aims to promote the social, economic and political inclusion of all, whatever their age, sex, disability, race, ethnicity, origin, religion or economic or other status. Caste, religion, sex and state are used as inputs so that differences between groups can be examined directly.");
H2("1.6 From the registered idea to this project");
table("The idea we registered and what the project delivers.", ["Registered idea", "What the project delivers"], [
  ["Take households that were poor in the first survey round and predict whether they crossed the poverty line by the second round.", `Done for ${R.n_kept} households, with one poverty line (Tendulkar) in both rounds.`],
  ["Compare Logistic Regression, Random Forest and XGBoost.", "These three plus an ensemble, compared with accuracy, precision, recall, F1, confusion matrices and ROC-AUC."],
  ["Use SHAP to rank the factors.", "SHAP ranking of the features and the factor groups."],
  ["Optionally add a small propensity-score analysis.", "An education analysis that compares similar households using propensity-score weights, kept as a clearly marked extension."],
  ["Handle the data properly (missing values, class balance).", "Missing values, outliers and encoding handled inside a pipeline, validation by village, and a feature selection check."],
], [4400, 4626], { size: 19 });
H2("1.7 Scope");
para("The project covers poor households across India in 2004-05 that could be followed up in 2011-12. It predicts risk and explains associations. It does not prove what causes a household to escape poverty.");

// ------------------------------------------------------------------------------------------------- 2 Literature
H1("2. Literature Review");
para("Five studies are closest to our work. Krishna (2004) followed 6,376 households in 35 villages of Rajasthan over 25 years, with poverty defined by the communities themselves. He found that 11.1% of all households escaped poverty and 7.9% fell into it, and that the reasons for escaping were different from the reasons for falling. This supports studying escape as an outcome of its own.");
para(`Thorat, Vanneman, Desai and Dubey (2017) used the same India Human Development Survey panel that we use, with Tendulkar poverty lines. They report that about 65% of the households that were poor in 2005 had escaped by 2012, and that Adivasi and Dalit households escaped less often. Our escape rate of ${R.escape} is close to theirs, and Adivasi households have the lowest escape rate in our sample as well. The two are not exactly comparable: their figure is weighted to the whole population, while ours is a household rate in our sample. Their work is descriptive and does not build a prediction model.`);
para("Narendranath, Khare, Gupta and Jyotishi (2018) applied machine learning to the same survey panel to study escaping and falling into poverty. We could not access their full results, so we cannot compare scores.");
para("Two further studies show why prediction matters for welfare programmes. McBride and Nichols (2018) show that choosing poverty targeting tools by their out-of-sample error, with cross-validation and ensemble methods, improves how well they pick out the poor. This is why we test on villages that the models have never seen. Aiken and co-authors (2022) used machine learning to target emergency cash aid in Togo. Jean and co-authors (2016) showed that machine learning on satellite images can explain up to 75% of the variation in the average consumption and wealth of local areas, which points to a future extension.");
para("We found no accessible study that pairs household-level prediction of poverty transitions in India with explanations of the predictions and a careful test on villages that the model has never seen. This project does that.");

// ------------------------------------------------------------------------------------------------- 3 Dataset
H1("3. Dataset and Preprocessing");
H2("3.1 Source and size");
para(`The India Human Development Survey (IHDS) is run by researchers at the University of Maryland and the National Council of Applied Economic Research (NCAER) in New Delhi. We downloaded the data from ICPSR as Stata files. The first round (IHDS-I, 2004-05) covers ${R.n_w1} households and ${R.n_persons} people. The second round (IHDS-II, 2011-12) covers ${R.n_w2} households. The same households were interviewed again, so the data form a panel. We used the household and person files of the first round, the household file of the second round, the village file of the first round (for one robustness check) and the tracking sheet of the second round (to check our household link). Person records were summarised to one row per household. The data are shared under the ICPSR terms of use, so they are kept inside the team and are not part of the submission files.`);
H2("3.2 Linking the two survey rounds");
para(`The second-round file does not include the number of the household in 2004-05, so we rebuilt the link from the state, district, village, household and split-household codes. About ${R.link.share} of the households from 2004-05 (${R.link.found} of ${R.link.of}) were found again, which agrees with the figure of about 83% in the IHDS user guide. Households that split in the meantime were handled by following the continuing household (split number 1), and households added in 2011-12 as replacements were dropped. We checked the link against the official tracking sheet that comes with the data, which lists where each 2005 household member went. Following the household of the 2005 head of household instead gives the same outcome for ${R.head_same} of the ${R.head_tracked} of households where the head can be tracked.`);
H2("3.3 Measuring poverty the same way in both rounds");
para(`Poverty is defined from spending. A household is poor when its monthly spending per person is below the poverty line of its state and of its rural or urban area. The two survey files do not use the same line. The poverty flag supplied with the 2004-05 file uses an older official line, while the flag in the 2011-12 file uses the Tendulkar line. Comparing the two would not be fair, because a household would count as poor in 2004-05 only if it was much poorer than the line used in 2011-12.`);
para(`The 2011-12 file also stores the Tendulkar line in 2004-05 prices. We use it to recompute who was poor in 2004-05, so that both rounds use the same method. With this line, ${R.pov_new_pw} of people were poor in 2004-05, which is close to the published estimate of about 37% (Planning Commission, 2009). The older line gives ${R.pov_old_pw}. For 2011-12 we kept the survey's own flag, which agrees with a recomputation from yearly spending and the Tendulkar line for ${R.w2agree} of households.`);
figure("c13_poverty_line", 4.6, "Share of households and of people that were poor in 2004-05 under the older line and under the Tendulkar line.");
H2("3.4 Target variable");
para(`The target is called ESCAPED. It is 1 if a household was poor in 2004-05 and not poor in 2011-12, and 0 if it was poor in both rounds. ${R.n_poor_w1} households were poor in 2004-05. Of these, ${R.n_kept} (${R.retention}) were found again as the same continuing household with a valid poverty flag in 2011-12. Among them ${R.n_escaped} escaped (${R.escape}) and ${R.n_stayed} stayed poor. Among the households that were not poor in 2004-05, ${R.fell} were poor in 2011-12.`);
figure("c01_transitions", 4.8, "Poverty status in 2011-12 for households that were poor and not poor in 2004-05.");
H2("3.5 Attributes and features");
para(`We use ${R.n_features} features, ${R.n_numeric} numeric and ${R.n_nominal} categorical, that describe the household in 2004-05. They fall into ten groups, shown in Table ${tabCount + 1}. Every feature comes from the 2004-05 household or person file, so the model only uses information that was available before the outcome. The full list, with the meaning, type and share of missing values of every feature, is in Appendix A.`);
const examples = {
  "Assets & housing": "household assets index, rooms, ownership of cycle, TV, phone, fridge; house type",
  "Occupation & employment": "members in farm work, wage work or salaried jobs; main source of income",
  "Household structure": "household size, children aged 0 to 5, age of head, share of dependants",
  "Access to services": "ration card type, water source, electricity, cooking fuel",
  "Social capital": "membership of village groups and social networks",
  "Education": "schooling of head and of adults, literacy, children in school",
  "Finance & social protection": "bank account, loans, insurance, government support",
  "Geography & social group": "state, rural or urban area, caste and religion group",
  "Women's status (gender)": "freedom to move, cash in hand, bank account",
  "Health": "deaths in household, woman's health rating, diagnosed illnesses",
};
table("The ten feature groups, with the number of numeric and categorical features.", ["Factor group", "Features", "Numeric", "Categories", "Examples"],
  R.groups_table.map((r) => [r[0], r[1], r[2], r[3], examples[r[0]] || ""]), [2000, 800, 800, 900, 4526], { size: 18 });
para("Some features are built by us from the person records and the household file. They include assets per person, rooms per person, the age and sex of the household head, the share of dependants, the number of children aged 0 to 5, the average schooling of adults, the share of working adults and the number of diagnosed major illnesses.");
figure("c02_feature_groups", 4.4, "Number of features in each factor group.");
H2("3.6 Feature selection");
para(`Feature selection happened in two steps. First, from the 945 columns of the 2004-05 household file we chose ${R.n_features} features by domain knowledge, in the ten groups above, and by simple rules: no spending or income (poverty is defined from spending), no identifiers, survey weights or interviewer codes, and no feature with more than 40% missing values.`);
para(`Second, we checked whether we really need all of them. We ranked the features by their importance in an XGBoost model trained on the training villages only, kept the top 10, 20, 40 or 80, refit the model with the same settings and compared the scores (Table ${tabCount + 1} and Figure ${figCount + 1}).`);
table("Score of XGBoost with only the most important features.", ["Features kept", "Cross-validated ROC-AUC", "Test ROC-AUC"], R.fsel, [2600, 3213, 3213], { size: 19 });
figure("c16_feature_selection", 4.2, "ROC-AUC against the number of features kept.");
H2("3.7 Missing values, outliers and encoding");
para("The survey codes missing answers as negative numbers such as -1 to -9. Left alone, these would look like real values, so they were turned into missing values. One feature (the education of the head's father) had more than 40% missing values and was dropped. The features with the most gaps among those we kept are shown in Table " + (tabCount + 1) + ".");
table("The features with the largest share of missing values.", ["Feature", "Share missing"], R.miss, [6400, 2626], { size: 19 });
para("The remaining gaps in numeric features were filled with the median, which is the middle value. Blank answers in category columns got their own 'missing' category. Numeric values were capped at the 0.5th and 99.5th percentiles of the training data, because a few cells contain typing errors.");
para("Categorical features were one-hot encoded, which means that each category becomes its own yes or no column, with categories below 1% grouped together. Numeric features were scaled for Logistic Regression only.");
para("Filling, capping, encoding and scaling are all learned from the training data only, inside a scikit-learn pipeline, so no information leaks from the test villages. The rule that drops features with more than 40% missing values used all households, but it never used the outcome.");
H2("3.8 Inputs left out on purpose");
para("Poverty is defined from spending, so household spending and income were not used as inputs. Identifiers, survey weights and interviewer codes were also left out. The ration card type is kept, because it is 2004-05 information, but it is a government poverty label and should not be read as a risk factor. A robustness check in Appendix C adds spending and income back and shows that this changes the score by less than 0.01, which is why leaving them out costs very little.");
H2("3.9 Exploratory analysis");
para(`The share of poor households that escaped differs clearly between groups. Adivasi households escaped least often (${R.caste.Adivasi[0]}), while Brahmin and other high caste households escaped about ${R.bh_combined} of the time. Dalit households (${R.caste.Dalit[0]}) were close to the average of ${R.escape.split(".")[0]}%. Sikh and Jain households are not shown in the chart because only ${R.caste["Sikh/Jain"][1]} were in the sample. These are raw differences and do not account for education, assets or location.`);
figure("c03_escape_by_caste", 5.0, "Share of poor households that escaped, by caste and religion group.");
para(`The escape rate also rises with education. It is ${R.educ.None[0]} when no adult in the household had any schooling and ${R.educ["13+ yrs"][0]} when an adult had 13 or more years. Urban households escaped more often than rural ones (${R.area.Urban} against ${R.area.Rural}), and households with more assets escaped more often (${R.assets.Low} in the lowest asset group and ${R.assets.High} in the highest).`);
figure("c04_escape_by_education", 4.8, "Share of poor households that escaped, by the highest schooling of any adult.");

// ------------------------------------------------------------------------------------------------- 4 Methodology
H1("4. Methodology and Machine Learning Pipeline");
H2("4.1 Validation strategy");
para(`Households in the same village share roads, jobs, prices and weather. If neighbours appear in both the training and the test data, the test score looks better than it really is. We therefore split by village: 80% of the villages were used for training (${R.n_train} households in ${R.n_train_vill} villages) and 20% for testing (${R.n_test} households in ${R.n_test_vill} villages). A village here also means an urban neighbourhood, which is the sampling unit of the survey.`);
para(`Model tuning used five-fold cross-validation, which means that the training villages are cut into five groups, the model is trained on four of them and checked on the fifth, and this is repeated so that each group is used once for checking. The groups also keep villages together. The folds are built by our own function and saved, so they are the same on every computer. The test villages are never used to choose models, settings or the decision threshold.`);
para(`To see what the village split changes, we repeated both kinds of split 20 times with the same XGBoost settings. A random split of households gives an average ROC-AUC of ${R.rv.random}, and a split by village gives ${R.rv.village}.`);
H2("4.2 Pipeline");
figure("c17_workflow", 6.2, "The workflow of the project, from the survey files to the slides, report and app.");
numbered([
  "Load the survey files (2004-05 and 2011-12) and check their size and checksum.",
  "Check, clean and link the two rounds.",
  "Use one poverty line in both rounds and create the target.",
  `Build the ${R.n_features} features from 2004-05 and check the feature selection.`,
  "Split by village into training and test data.",
  "Train and tune the four models on the training villages: preprocessing inside the pipeline (fill missing values, cap outliers, encode, scale), a random search with five-fold village cross-validation, and a decision threshold chosen on out-of-fold predictions.",
  "Test on the villages never seen, with 95% confidence intervals from a bootstrap of whole villages.",
  "Explain the model with SHAP, run the robustness checks and the education analysis, and save the outputs.",
  "Slides, report and demo app all read the saved outputs.",
], "num2");
H2("4.3 Models and why we chose them");
para("We compare four models and a dummy baseline. The dummy classifier always predicts the overall escape rate and shows what no skill looks like. Logistic Regression is simple, fast and easy to explain through odds ratios, so it is the natural baseline. Random Forest (Breiman, 2001) averages many decision trees and can capture curved relationships and interactions. XGBoost (Chen and Guestrin, 2016) builds trees one after another, each correcting the errors of the last, and often works well on tabular data. The soft-voting ensemble averages the probabilities of the other three models.");
para("We did not use a neural network or a support vector machine. We have about 9,000 training rows of mixed survey data, where tree models are the usual strong choice, and they are easier to explain to the people who would use the results.");
H2("4.4 Training strategy");
para(`The random search tried 11 settings for Logistic Regression, 20 for Random Forest and 30 for XGBoost and kept the setting with the highest cross-validated ROC-AUC. About ${R.escape} of the households escaped, so the classes are mildly unbalanced. We did not use class weights, because weights distort the predicted probabilities. The decision threshold for turning a probability into a prediction was chosen for each model to give the best macro-F1 (the average F1 score of both classes) on out-of-fold training predictions, never on the test set. The headline model was chosen before looking at the test set, as the single model with the best cross-validated ROC-AUC. This is XGBoost.`);
H2("4.5 Evaluation measures");
para("We report accuracy, precision, recall and F1-score for both classes, the confusion matrix and ROC-AUC for every model. Precision is the share of households called 'escaped' that really escaped, recall is the share of households that really escaped that we found, and F1 balances the two. ROC-AUC is the chance that the model gives a random household that escaped a higher score than a random household that stayed poor, and it does not depend on the threshold. We also report macro-F1 and the Matthews correlation coefficient (MCC, Chicco and Jurman, 2020), which stay honest when classes are unbalanced. Accuracy is reported but not used to choose models, because a model that always predicts 'escaped' already reaches about 69%.");
H2("4.6 Explaining the model");
para("SHAP (Lundberg and Lee, 2017) splits each prediction into the contribution of each feature, a little like splitting a bill between items. Averaging the size of these contributions over many households shows which features the model relies on most. SHAP shows what the model uses. It does not show that changing a feature would cause escape.");

// ------------------------------------------------------------------------------------------------- 5 Implementation
H1("5. Implementation");
H2("5.1 Tools");
para("The work is done in Python 3.11 with pandas and NumPy for the data, pyreadstat to read the Stata files, scikit-learn for pipelines, Logistic Regression, Random Forest and cross-validation, XGBoost for gradient boosting, SHAP for explanations and matplotlib for charts. The demonstration application uses Streamlit.");
H2("5.2 Project structure");
para("The notebook is the heart of the project. You run it from top to bottom, and it writes tables, charts and the saved models into the outputs folder. The charts, slides, report and app all read from that folder.");
code([
  "AUCML project folder",
  "|-- IHDS_poverty_escape_v3.ipynb   main notebook (run top to bottom)",
  "|-- ihds_tools.py                  helper class shared with the app",
  "|-- requirements.txt               exact package versions",
  "|-- quick_check.py                 re-checks the saved results in seconds",
  "|-- app.py, app_labels.json        Streamlit demo",
  "|-- make_charts_v3.py              rebuilds the charts",
  "|-- build_deck_v4.py               rebuilds the slides",
  "|-- outputs/",
  "|     |-- *.csv, key_numbers.json  tables and numbers",
  "|     |-- figures/, figures_ppt/   charts",
  "|     |-- model_bundle.joblib      saved models",
  "|-- AUCML_Project_Report.docx      this report",
  "|-- ICPSR_22626-V12/, ICPSR_36151-V6/   raw survey data (not shared)",
]);
H2("5.3 A look at the code");
para("The next lines show how the XGBoost model is set up and tuned. The same pattern is used for the other two models.");
code([
  'xgboost_pipeline = Pipeline([("prep", make_preprocessor(scale=False)),',
  '                             ("clf", XGBClassifier(eval_metric="logloss", tree_method="hist",',
  '                                                   random_state=SEED, n_jobs=1))])',
  'xgboost_grid = {"clf__n_estimators": [200, 400, 600], "clf__learning_rate": [0.02, 0.05, 0.1],',
  '                "clf__max_depth": [2, 3, 4, 5, 6], "clf__min_child_weight": [1, 3, 5, 10], ...}',
  'search = RandomizedSearchCV(pipeline, grid, n_iter=30, scoring="roc_auc",',
  '                            cv=cv, random_state=SEED, n_jobs=-1, refit=True)',
  'search.fit(X_train, y_train, groups=groups_train)   # cv = folds that keep villages together',
]);
H2("5.4 Execution evidence");
para("Figure " + (figCount + 1) + " shows the output of the executed notebook, with the time taken to tune each model. The script quick_check.py recomputes the headline scores from the saved predictions in a few seconds, so the results can also be checked live.");
figure("exec_evidence", 6.0, "Output of the executed notebook: the time taken to tune each model and the settings chosen.");
code(R.quick_check);
H2("5.5 Reproducibility");
para("Seeds are fixed and the cross-validation folds are saved. Running the whole notebook again with the same packages gave identical tables, and running it with a different version of scikit-learn (1.6.1 with XGBoost 2.1.4) also gave identical results for the result tables. A full run takes about 30 minutes on our laptop. A requirements file lists the exact package versions.");
H2("5.6 Demonstration application");
para("The application lets a user enter a household's 2004-05 details, or start from a real household of the test villages. It shows the estimated chance of escaping, the risk group with how often households in that group really stayed poor, and a SHAP chart of what raised or lowered the estimate. Inputs that the user does not fill in are set to the typical household of the study sample. A warning on the screen says that the tool is for screening and not for decisions about one household.");
figure("app_screenshot", 5.6, "The demonstration application.");

// ------------------------------------------------------------------------------------------------- 6 Results
H1("6. Results");
H2("6.1 Comparison of the models");
para(`Table ${tabCount + 1} and Table ${tabCount + 2} show the scores on the ${R.n_test} test households. XGBoost and the ensemble have the highest ROC-AUC. The ensemble is ${R.pair_ens_xgb_abs} below XGBoost, and the 95% interval of that difference runs from ${R.pair_ens_xgb[1]} to ${R.pair_ens_xgb[2]}, so the two cannot be told apart. XGBoost is better than Logistic Regression by ${R.pair_xgb_lr.replace("+", "")} and better than Random Forest by ${R.pair_xgb_rf.replace("+", "")}, and the intervals of both differences stay above zero. The ensemble is also ahead of both, by ${R.pair_ens_lr.replace("+", "")} and ${R.pair_ens_rf.replace("+", "")}.`);
para("All models are far better than the dummy classifier, whose ROC-AUC is shown as 0.487. The dummy gives every household the same score, so its true ROC-AUC is 0.5, and the 0.487 comes from tiny random noise that breaks ties.");
table("Main scores on the test villages.", ["Model", "ROC-AUC (95% CI)", "Accuracy", "Macro-F1", "MCC", "Brier"], R.models, [1900, 2926, 1000, 1000, 800, 800], { highlight: 0, size: 19 });
table("Accuracy, precision, recall and F1 for both classes, for every model.", ["Model", "Accuracy", "Prec. escaped", "Recall escaped", "F1 escaped", "Prec. stayed", "Recall stayed", "F1 stayed"],
  R.perclass, [1750, 900, 1000, 1050, 900, 1000, 1050, 900], { highlight: 2, size: 18 });
para("The scores are modest. A ROC-AUC of about 0.70 to 0.72 means that the models rank households better than chance but make many individual errors. The dummy classifier has an accuracy that is almost as high as the models, but it never finds a household that stays poor, which is why accuracy alone cannot be used here. All models find escaped households better than stayed-poor households.");
figure("c05_roc_curves", 4.4, "ROC curves of all models on the test villages.");
para(`The mean ROC-AUC over the five validation folds of the training villages was ${R.cv["Logistic Regression"]} for Logistic Regression, ${R.cv["Random Forest"]} for Random Forest and ${R.cv.XGBoost} for XGBoost. XGBoost has the best cross-validated score, which is why it is our headline model.`);
H2("6.2 Confusion matrices");
para(`Figure ${figCount + 1} shows the confusion matrix of every model. With a decision threshold of ${R.thr}, the XGBoost model correctly predicted ${R.cm[1][1].toLocaleString("en-US")} of the ${(R.cm[1][0] + R.cm[1][1]).toLocaleString("en-US")} households that escaped and ${R.cm[0][0]} of the ${R.cm[0][0] + R.cm[0][1]} households that stayed poor. Finding the households that stay poor is the harder task. The model finds a little over half of them, compared with none for the baseline. Because many individual predictions are wrong, the model is meant for ranking and not for decisions about one household.`);
figure("c18_confusion_all_models", 6.2, "Confusion matrices of all four models on the test villages (rows are the true outcome).");
H2("6.3 Checks on overfitting and on the village split");
para(`Table ${tabCount + 1} compares the score on the households a model learned from with the cross-validated score and the test score. Random Forest fits its training households almost perfectly (a training score of 0.988), which is why we judge models only on cross-validation and on test villages. The scores of the other two models do not drop much from training to test.`);
table("ROC-AUC on the training households, in cross-validation and on the test villages.", ["Model", "Train", "Cross-validated", "Test"], R.over, [3000, 1900, 2200, 1926], { size: 19 });
H2("6.4 Practical value: ranking households by risk");
para(`We sorted the test households by predicted risk of staying poor and split them into five equal groups. In the highest-risk group, ${R.q5} really stayed poor, which is ${R.q5lift} times the average of ${R.avg_stay}. In the lowest-risk group, only ${R.q1} stayed poor. The highest-risk 40% of the ranking contains ${R.top40} of all households that stayed poor, so a programme with a limited budget can focus on fewer households and still reach more than half of those in need.`);
table("Households grouped by predicted risk of staying poor (test villages).", ["Risk group", "Households", "Stayed poor", "Times the average", "Share of all who stayed poor"], R.lift, [2300, 1500, 1500, 1800, 1926]);
figure("c07_risk_groups", 4.6, "Share that actually stayed poor in each predicted-risk group.");
para("Appendix C adds three further checks: how stable the ranking of the models is over 20 different splits, whether the predicted probabilities can be trusted, and how the results change under other choices.");

// ------------------------------------------------------------------------------------------------- 7 Interpretation
H1("7. Interpretation of the Model");
H2("7.1 Most important features");
para(`Table ${tabCount + 1} and Figure ${figCount + 1} show the ten features with the largest average impact on the XGBoost predictions. The number of children aged 0 to 5, the state, the household asset index (in two related forms), the ration card type and the caste and religion group are the strongest. Households with no child under six are pushed towards escape, while households with two or more are pushed towards staying poor. More assets per household member generally push the prediction towards escape. These are patterns that the model uses, and they do not show that a feature causes escape. In particular, the ration card type is a government label for poor households and should not be read as a risk factor.`);
table("The ten features with the largest average SHAP impact.", ["Variable", "Meaning", "Mean |SHAP|", "Group"], R.shap_top, [1500, 3700, 1300, 2526], { size: 19 });
figure("c08_shap_top10", 4.8, "Average impact of the ten most important features on the XGBoost predictions.");
figure("c10_shap_children", 3.8, "SHAP value against the number of children aged 0 to 5.");
figure("c11_shap_assets", 3.8, "SHAP value against assets per household member.");
H2("7.2 Is education linked to escape?");
const E = R.edu;
para(`Among poor households, ${E.n_treated} had an adult with 10 or more years of schooling, and ${E.n_control} did not (14 households have no education value). The raw difference in escape rate is ${E.A.raw[0]} percentage points. We then compared similar households, with the same state, caste, religion, urban or rural area, household size, age and sex of the head and land, using weights built from propensity scores (the estimated chance of having an educated adult given the other traits). The gap shrinks to about ${E.A.doubly_robust[0]} percentage points (95% interval ${E.A.doubly_robust[1]} to ${E.A.doubly_robust[2]}). If we also adjust for how poor the household was in 2004-05, it is ${E.B.doubly_robust[0]} points. So the gap is real in this data, about 5 to 6 points, but it is an association and not proof that education causes escape. All results are for households that were already poor in 2004-05. Appendix C gives the details of the three estimators and the E-value.`);
figure("c19_education_simple", 4.8, "Difference in escape rate between households with 10 or more years of adult schooling and others, with 95% intervals.");

// ------------------------------------------------------------------------------------------------- 8-10
H1("8. Limitations, Fairness and Ethics");
bullets([
  "The models are modest. A ROC-AUC of about 0.7 is good enough to rank households by risk, but not to decide about a single household.",
  `Escaping is partly a noisy crossing of a line. About one in five poor households (${R.near.all}) were within 10% of the poverty line, and spending was collected with different item lists in the two rounds (47 and 52 items), which may add measurement noise. A different poverty line would change which households count as poor.`,
  `About 11% of poor households could not be followed, for example because the household moved away. They differ from the others (for example, they are more often urban and own less land), and re-weighting changes the escape rate only slightly (${R.rob.ipw[0]} to ${R.rob.ipw[1]}).`,
  "The survey covers 2004 to 2012. A model for real use would have to be retrained on newer panel data.",
  `SHAP and group differences describe patterns, and the education analysis cannot rule out hidden factors. The illness feature may contain zeros that mean 'not recorded' in some villages (in ${R.ill.none} of ${R.ill.vill} villages and urban neighbourhoods nobody was listed, against about ${R.ill.exp} expected by chance). Health is only about 1% of the SHAP importance, so this cannot change the results much.`,
  "State and caste are strong predictors. A risk score must be used to support groups and never to exclude them, and fairness checks for each social group are needed before any real use.",
  "The data are personal survey data under the ICPSR terms of use. They are not shared outside the team.",
]);
H1("9. Conclusion");
numbered([
  `About seven out of ten households that were poor in 2004-05 had escaped poverty by 2011-12 (${R.escape}), when poverty is measured in the same way in both rounds.`,
  `The models reach a ROC-AUC of about 0.70 to 0.72 on villages they have never seen. XGBoost (${R.head_res.ROC_AUC}) and the ensemble are the best and cannot be told apart.`,
  "Young children, state, assets, the caste and religion group and the ration card type were the strongest predictors.",
  `Adivasi households escaped least often (${R.caste.Adivasi[0]}), in line with Thorat and co-authors (2017).`,
  `The highest-risk 20% of households stayed poor ${R.q5lift} times as often as the average, which makes the model useful for ranking households for programmes under SDG 1 and SDG 10.`,
  `Adult education is linked to an escape rate about 5 to 6 percentage points higher after adjustment (the 95% intervals of the two adjusted estimates together run from ${R.edu_int[0]} to ${R.edu_int[1]}), but this is an association and not proof of cause.`,
], "num3");
H1("10. Future Scope");
numbered([
  "Retrain the model on newer panel survey data, and test it on a later period.",
  "Add satellite or village-level data, following Jean and co-authors (2016).",
  "Predict falling into poverty as a separate outcome.",
  "Run fairness checks for each social group before any real use.",
  "Extend the Streamlit application for field workers.",
], "num4");

// ------------------------------------------------------------------------------------------------- References
H1("References");
const refs = [
  "Krishna, A. (2004). Escaping poverty and becoming poor: Who gains, who loses, and why? World Development, 32(1), 121-136. https://doi.org/10.1016/j.worlddev.2003.08.002",
  "Thorat, A., Vanneman, R., Desai, S., and Dubey, A. (2017). Escaping and falling into poverty in India today. World Development, 93, 413-426. https://doi.org/10.1016/j.worlddev.2017.01.004",
  "Narendranath, S., Khare, S., Gupta, D., and Jyotishi, A. (2018). Characteristics of Escaping and Falling into Poverty in India: An Analysis of IHDS Panel Data using machine learning approach. ICACCI 2018, 1391-1397. https://doi.org/10.1109/ICACCI.2018.8554571",
  "McBride, L., and Nichols, A. (2018). Retooling poverty targeting using out-of-sample validation and machine learning. World Bank Economic Review, 32(3), 531-550. https://doi.org/10.1093/wber/lhw056",
  "Aiken, E., Bellue, S., Karlan, D., Udry, C., and Blumenstock, J. E. (2022). Machine learning and phone data can improve targeting of humanitarian aid. Nature, 603, 864-870. https://doi.org/10.1038/s41586-022-04484-9",
  "Jean, N., Burke, M., Xie, M., Davis, W. M., Lobell, D. B., and Ermon, S. (2016). Combining satellite imagery and machine learning to predict poverty. Science, 353(6301), 790-794. https://doi.org/10.1126/science.aaf7894",
  "Breiman, L. (2001). Random forests. Machine Learning, 45, 5-32. https://doi.org/10.1023/A:1010933404324",
  "Chen, T., and Guestrin, C. (2016). XGBoost: A scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD Conference, 785-794. https://doi.org/10.1145/2939672.2939785",
  "Lundberg, S. M., and Lee, S.-I. (2017). A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems 30. https://arxiv.org/abs/1705.07874",
  "VanderWeele, T. J., and Ding, P. (2017). Sensitivity analysis in observational research: introducing the E-value. Annals of Internal Medicine, 167(4), 268-274. https://doi.org/10.7326/M16-2607",
  "Chicco, D., and Jurman, G. (2020). The advantages of the Matthews correlation coefficient (MCC) over F1 score and accuracy in binary classification evaluation. BMC Genomics, 21, 6. https://doi.org/10.1186/s12864-019-6413-7",
  "Planning Commission (2009). Report of the Expert Group to Review the Methodology for Estimation of Poverty (Tendulkar Committee). Government of India.",
  "Desai, S., Vanneman, R., and NCAER. India Human Development Survey (IHDS), ICPSR 22626 (2004-05) and IHDS-II, ICPSR 36151 (2011-12). https://ihds.umd.edu",
  "United Nations. Sustainable Development Goals 1 and 10. https://sdgs.un.org/goals/goal1 and https://sdgs.un.org/goals/goal10",
];
refs.forEach((t, i) => children.push(new Paragraph({ spacing: { after: 100, line: 280 }, indent: { left: 360, hanging: 360 }, children: [run(`${i + 1}. ${t}`, { size: 20 })] })));

// ------------------------------------------------------------------------------------------------- Appendices
children.push(new Paragraph({ children: [new PageBreak()] }));
H1("Appendix A. Feature Dictionary");
para(`All ${R.n_features} features used by the models. 'Number' means a numeric feature and 'category' means a categorical feature that is one-hot encoded.`);
table("The features used in the models, with their group, type and share of missing values.", ["Variable", "Meaning", "Group", "Type", "Missing"], R.dictionary_rows, [1300, 3700, 2300, 900, 826], { size: 16, tight: true, keepTogether: false });
H1("Appendix B. How to Reproduce the Results");
numbered([
  "Use Python 3.11 and install the packages in requirements.txt.",
  "Place the two ICPSR data folders next to the notebook, or set the environment variable IHDS_DATA_DIR.",
  "Open IHDS_poverty_escape_v3.ipynb and run all cells. All tables, charts and the model file are written to the outputs folder.",
  "Run quick_check.py to re-check the headline results in seconds.",
  "Run make_charts_v3.py and then build_deck_v4.py to rebuild the charts and the slides.",
  "Run streamlit run app.py to start the demonstration application.",
], "num5");
H1("Appendix C. Additional Analyses");
para("These checks are not needed to follow the project. They show that the main results are stable.");
H2("C.1 How stable is the ranking of the models?");
para(`We repeated the train and test step on 20 different village splits. The test ROC-AUC moved with a standard deviation of about ${R.rep.XGBoost[1]}. On average the ensemble (${R.rep["Soft-vote ensemble (LR+RF+XGB)"][0]}) and XGBoost (${R.rep.XGBoost[0]}) were ahead of Logistic Regression (${R.rep["Logistic Regression"][0]}) and Random Forest (${R.rep["Random Forest"][0]}). The ensemble had the highest score in ${R.rep["Soft-vote ensemble (LR+RF+XGB)"][4]} of the 20 splits and XGBoost in ${R.rep.XGBoost[4]}, but the difference between them is only about 0.001. The tuned settings were kept fixed and the test sets overlap, so this shows how stable the ranking is. It is not a new unbiased score.`);
figure("c15_repeated_splits", 4.4, "Test ROC-AUC of each model over 20 different village splits.");
H2("C.2 Can the predicted probabilities be trusted?");
para(`For the XGBoost model, the average predicted chance of escaping (${R.cal.XGBoost[0]}) matches the real escape rate (${R.cal.XGBoost[1]}). The calibration slope is ${R.cal.XGBoost[3]}, where 1 is perfect, and the Brier score (the average squared error of the probabilities, lower is better) is ${R.cal.XGBoost[2]}, which is ${(parseFloat(R.cal.XGBoost[4]) * 100).toFixed(0)}% better than always predicting the average. A predicted 70% can be read as roughly 7 in 10 similar households. We did not use class weights because they pull the predicted chances away from the real rates, and we wanted probabilities that can be read as real chances.`);
figure("c14_calibration", 3.8, "Predicted chance of escaping against the share that really escaped (test villages).");
H2("C.3 Robustness checks");
const fsRows = R.rob.fs.map((r) => [r[0].replace("Final feature set (structural, no consumption/income)", "Final feature set").replace("ABLATION: + consumption gap, income, village poverty rate", "Add spending gap, income and village poverty rate"), r[1], r[2], r[3], r[4], r[5]]);
table("Does more information help? Cross-validated (CV) and test ROC-AUC. CV values pool the out-of-fold predictions of three shuffles, so they differ slightly from the fold averages in Section 6.1.", ["Feature set", "Features", "LR CV", "LR test", "XGB CV", "XGB test"], fsRows, [3600, 1000, 1100, 1100, 1100, 1126], { size: 19 });
table("Other robustness checks.", ["Check", "Result"], [
  ["Count escape only if all split-off families are non-poor", `Escape rate ${R.rob.all[0]}, ROC-AUC ${R.rob.all[1]}`],
  ["Count escape if any split-off family is non-poor", `Escape rate ${R.rob.any[0]}, ROC-AUC ${R.rob.any[1]}`],
  ["Re-weight for households lost between the rounds", `Escape rate ${R.rob.ipw[1]} instead of ${R.rob.ipw[0]}`],
  ["Only households that were also poor on the older line", `${R.rob.old[0]} households, escape rate ${R.rob.old[1]}, ROC-AUC ${R.rob.old[2]} (XGBoost) and ${R.rob.old[3]} (Logistic Regression)`],
  ["Survey weights (SWEIGHT)", `Weighted escape rate ${R.rob.sw[0]}, effective sample size ${R.rob.sw[1]}, weighted ROC-AUC ${R.rob.sw[2]} (XGBoost)`],
  ["Without the ration card variables", `ROC-AUC (XGBoost) ${R.ration.XGBoost[1]} instead of ${R.ration.XGBoost[0]}; (Logistic Regression) ${R.ration["Logistic Regression"][1]} instead of ${R.ration["Logistic Regression"][0]}`],
], [4300, 4726], { size: 19 });
para(`Adding village infrastructure data, the average traits of neighbouring households, or even spending and income changes the test ROC-AUC of XGBoost by less than 0.01. Spending alone, expressed as a ratio to the poverty line, reaches only ${R.rob.gap_alone}. This supports the view that the limit on accuracy comes from the data and not from the choice of model.`);
H2("C.4 The education analysis in detail");
para(`The estimates of the gap between households with and without an adult with 10 or more years of schooling are very similar for three methods: ${E.A.regression[0]} points by regression adjustment, ${E.A.ipw[0]} points by weighting with propensity scores and ${E.A.doubly_robust[0]} points by a doubly robust estimator that combines the two (95% intervals from re-drawing whole villages). The largest standardised difference between the two groups falls from ${E.smd_before} before weighting to ${E.smd_after} after, which shows that the weighting balances the groups well. A nearest-neighbour matching estimate gives ${E.matchA} points. The E-value (VanderWeele and Ding, 2017) of the first estimate is ${E.evalA} (${E.evalA_ci} for the confidence limit nearest to no effect): a hidden factor that raised both education and escape by a risk ratio of about ${E.evalA} could explain the gap away. This is a fairly weak shield, so the result is suggestive and not proof of cause.`);
figure("c12_education_effect", 5.4, "The education gap under each estimator and specification, with 95% village-bootstrap intervals.");
H2("C.5 SHAP importance by factor group");
const g = R.shap_grp;
para(`Household structure (${g["Household structure"]}) and assets and housing (${g["Assets & housing"]}) account for the largest shares of the total SHAP importance, followed by geography and social group (${g["Geography & social group"]}) and access to services (${g["Access to services"]}). Education accounts for ${g.Education} and health for ${g.Health}. A group with many features collects more total importance, and features that move together share credit between them, so a small share does not mean that a factor is unimportant.`);
figure("c09_shap_groups", 4.6, "Share of the total SHAP importance by factor group.");
H1("Appendix D. Glossary");
table("Terms used in this report.", ["Term", "Plain meaning"], [
  ["Panel data", "The same households measured more than once."],
  ["Tendulkar line", "The official poverty line: monthly spending per person, set by state and by rural or urban area."],
  ["One-hot encoding", "A category such as state becomes one yes or no column for each value."],
  ["Out-of-fold prediction", "A prediction made while the household's village was hidden from the model."],
  ["Threshold (cut-off)", "The probability above which a household is predicted to escape."],
  ["ROC-AUC", "The chance that the model scores a random household that escaped above a random household that stayed poor."],
  ["Macro-F1", "The F1 score averaged over both classes."],
  ["SHAP", "A way to split a prediction into the push from each feature."],
  ["Bootstrap 95% interval", "Redraw villages 1,000 times and take the middle 95% of the scores."],
  ["Propensity score", "The estimated chance of a household having a trait (here an educated adult) given its other traits."],
  ["Data leakage", "Giving the model the answer, or information it would not have in real use."],
], [2700, 6326], { size: 19, boldFirst: true });

// ------------------------------------------------------------------------------------------------- list of figures and tables (after the contents)
const listParas = [new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "List of Figures and Tables", font: FONT, size: 32, bold: true, color: TEAL })] })];
figList.forEach((t) => listParas.push(new Paragraph({ spacing: { after: 40 }, children: [run(t, { size: 19 })] })));
listParas.push(new Paragraph({ spacing: { after: 100 }, children: [run("", { size: 10 })] }));
tabList.forEach((t) => listParas.push(new Paragraph({ spacing: { after: 40 }, children: [run(t, { size: 19 })] })));
listParas.push(new Paragraph({ children: [new PageBreak()] }));

const numCfg = (ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] });
const doc = new Document({
  creator: "AUCML team", title: "Predicting Household Escape from Poverty in India",
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    numCfg("num1"), numCfg("num2"), numCfg("num3"), numCfg("num4"), numCfg("num5")] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT], font: FONT, size: 18, color: "6B7280" })] })] }) },
    children: [...front, ...listParas, ...children],
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(path.join(R.run_dir, "AUCML_Project_Report.docx"), buf); console.log("report written, figures:", figCount, "tables:", tabCount); });
