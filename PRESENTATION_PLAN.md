# Presentation plan

The deck has **31 main slides, a references slide and 8 backup slides**. The speaker notes on every slide hold what to say, in plain words.
The time slot is not announced yet, so here are three versions. In PowerPoint, hide a slide with Slide Show > Hide Slide.

## Who presents what

| Presenter | Sections | Slides | Time (speaking only) |
|---|---|---|---|
| Anhad | 1 Problem and use case, 2 Literature, 8 Conclusion (plus slides 1 to 3) | 1 to 7 and 29 to 31 | about 4 minutes |
| Aman | 3 Dataset, 5 Implementation | 8 to 13 and 18 to 19 | about 3.5 minutes |
| Eshaan | 4 Methodology, 7 Interpretation | 14 to 17 and 26 to 28 | about 3 minutes |
| Gokul | 6 Results | 20 to 25 | about 2.5 minutes |

Add about 15 seconds for each slide with a chart, because the audience needs time to look at it.

The speaker notes are written as a script in plain words. Read them to practise, and then say them in your own words. The first slide of each person's turn (slides 8, 14, 18, 20, 26 and 29) starts with a thank-you to the previous speaker, so the talk flows in every version, even when some slides are hidden.

## Three versions

| Version | Slides to show | Time |
|---|---|---|
| **Full** | 1 to 31 (all) | about 15 to 17 minutes |
| **12 minutes** | 1, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 28, 29, 30, 31 (hide 2, 7, 13, 23, 27) | about 12 to 13 minutes |
| **10 minutes** | 1, 4, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 19, 20, 21, 24, 25, 26, 28, 29, 30, 31 (hide the rest) | about 11 minutes |

The backup slides (33 to 40) are never presented. They are for questions.

The 10-minute version leaves out three slides that the coordinator's email asks about: missing values (12), training strategy (17) and the precision, recall and F1 table (22). They stay in the report, in the speaker notes and in the viva guide, so be ready to answer questions on them. If the slot allows 12 minutes, use the 12-minute version.

## What the examiners must see (from the coordinator's email)

| Requirement in the email | Where it is shown |
|---|---|
| Problem statement, objective, scope | Slides 4 and 6 |
| Application domain, users, real-world relevance | Slide 5 |
| Refined version of the registered idea | Slide 6 |
| Data source, attributes, target, validation | Slides 8, 9, 10, 14 |
| Missing values, feature selection and engineering | Slides 10, 11, 12 |
| Pipeline with justification, training strategy | Slides 15, 16, 17 |
| Implementation, workflow, outputs, project structure | Slides 15, 18, 19 |
| Execution (the code really runs) | Slide 19 and the live demo on slide 31 |
| Accuracy, precision, recall, F1, confusion matrix, ROC-AUC, comparison | Slides 20 to 25 |
| Conclusion, limitations, future scope | Slides 29 and 30 |

## Live demo (about 1 minute, slide 31)

1. Before the talk, open a terminal in the project folder and run `streamlit run app.py`. Keep the browser tab ready.
2. Show the default household, then choose "Real test household: lowest predicted escape chance". Read the chance of escaping and the risk group.
3. Change the number of assets and show that the estimate moves.
4. Say once: it is a screening aid, not a decision about one family.
5. If the demo fails, the screenshot on the slide shows the same thing. You can also run `python quick_check.py` to show the results are re-checked in seconds.

## Rehearsal checklist

- [ ] Each person reads the whole report and `VIVA_GUIDE.md`.
- [ ] Do the swap test at the end of the viva guide (each person answers two questions about someone else's part).
- [ ] Run the talk once with a timer, in the version that matches the slot.
- [ ] Check that `streamlit run app.py` and `python quick_check.py` work on the laptop you will use.
- [ ] Fill in anything the faculty ask for that we do not know yet (submission format, time slot).
