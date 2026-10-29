# Note for the team (you can paste this into the group chat)

Aman, thank you for the package. The notebook, the household link and the slides were a very good base, and most of it checked out against the
raw data. While checking everything we found one problem that changes the headline numbers, plus a few smaller ones. We built a corrected
version in a new folder and did not touch your files.

**The main problem.** The poverty flag that comes with the 2004-05 file uses an older official poverty line. The 2011-12 flag uses the Tendulkar line.
So the first version compared two different definitions of poor. The 2011-12 file also contains the Tendulkar line for 2004-05 prices, so we used it for both
years. This changes the numbers:

| | First version | Corrected version |
|---|---|---|
| Poor households modelled | 7,206 | 11,146 |
| Households that escaped | 66.1% | 69.4% |
| Best test ROC-AUC | 0.684 (ensemble) | 0.722 (XGBoost) |

**Smaller fixes.** The results changed with the scikit-learn version (now fixed and checked on two versions). Class weights had made the predicted probabilities
wrong (now calibrated). The model ranking was over-claimed, so the headline model is chosen by cross-validation. The education analysis got valid intervals.
A few slide statements were not supported.

**After the coordinator's email (7 October).** The coordinator wants a complete but not unnecessarily complex project, with feature selection, execution and
project structure clearly shown, all the standard metrics for every model, a structured report, and every member knowing the whole project. We added all of
that, and made the talk simpler: 31 main slides with speaker notes, and 8 backup slides for questions only.

**What is in the new folder.** The run notebook, the new deck, a report with appendices, a working demo app, `quick_check.py`, pinned package versions,
`PRESENTATION_PLAN.md`, `VIVA_GUIDE.md`, and `CHANGES_FROM_V2.md` with every change and the reason for it. Start with `README.md`.

**What we need from each of you.**
1. Read the report, the slides and the viva guide, not only your own part. Every one of us can be asked about any part.
2. Check slide 1 and the report cover, and the split of who presents what: Anhad slides 1 to 7 and 29 to 31; Aman 8 to 13 and 18 to 19; Eshaan 14 to 17 and 26 to 28; Gokul 20 to 25.
3. Do the swap test at the end of `VIVA_GUIDE.md` together before the viva, and time one full run of the talk.
