# Updated Research (2026-09)

Documents generated from the September 2026 scoring exercise, in which the complexity rubric was applied at scale to the HEM CTM portfolio (40 protocols) and cross-checked against an independent workload instrument.

These **supplement** the documents in `research/` rather than replacing them. The earlier documents describe the instrument's design and its original 34-item validation; these describe what happened when it was applied to a real portfolio.

## Contents

| Document | Question it answers |
|---|---|
| [`opal-concordance-study.md`](opal-concordance-study.md) | Does the rubric measure something real? Cross-instrument comparison against OPAL acuity scores (n=30, r=0.867). |
| [`d4-9-procedural-intensity-addendum.md`](d4-9-procedural-intensity-addendum.md) | Specification and evaluation of new Item 4.9, added to Dimension 4. Includes the alternatives tested and rejected. |
| [`automated-scoring-methods.md`](automated-scoring-methods.md) | How 40 protocols were scored, what went wrong with the inputs, and how reproducible the results are. |

Suggested reading order: concordance study → addendum → methods.

## Key findings

1. **The rubric shows strong concordance with an independently-developed workload instrument** — r = 0.867, 80% exact band agreement, 100% within one band, no ≥2-band errors across 30 shared protocols.

2. **Its residual disagreements are a construct difference, not calibration error.** The rubric measures protocol and scientific complexity; OPAL measures coordinator workload. They diverge predictably on low-enrollment/high-touch studies (rubric reads lower) and design-heavy/low-visit studies (rubric reads higher).

3. **A normalized weighted-average score cannot be shifted by adding or reweighting criteria.** Item 4.9 was added specifically to correct the first divergence pattern; it scores the target studies at maximum and moves their overall score by ≤1 point, because adding an item raises numerator and denominator together. Reweighting Dimension 4 up to 4.0× was likewise ineffective and degraded portfolio-wide agreement.

4. **Input quality is the dominant risk in automated scoring, and it fails silently.** Viewer stubs, unmappable PDF font encodings, and filename collisions all produce complete, plausible, wrong scores rather than errors. One protocol's score moved 15 points and gained two red flags after its text was recovered by OCR.

## Status of the instrument

| | |
|---|---|
| Live rubric | 44 items, `TOTAL_MAX_WT` 136.8 (`index.html`, `offline-bundle/index.html`) |
| Excel workbook | **Out of parity** — still 43-item / 132.9; see `research/validation-report.md` |
| Portfolio scored | 40 protocols, uniform 44-item basis |
| Extraction cap | 80,000 characters (inherited; see `automated-scoring-methods.md` §5) |

## Open items

- **Excel/web revalidation.** `data/complexity-scoring-engine.xlsx` needs updating to the 44-item / 136.8 basis before the three-scenario concordance methodology in `research/validation-report.md` can be re-run.
- **Extraction cap.** A four-protocol experiment favours raising it from 80,000, but the effect size overlaps test-retest variance; a larger experiment is needed before re-baselining.
- **Band boundary validation.** The Moderate/High and High/Very High cutoffs rest on a regression fitted to 30 points with only 4 OPAL-High and 3 Very-High cases.
- **Inter-rater comparison.** No human-vs-model scoring of the same protocols has been performed.
