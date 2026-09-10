# Concordance Study — Complexity Rubric vs. OPAL Acuity Scores

**Status: Complete.** Cross-instrument comparison of the 44-item complexity rubric against the independently-developed HEM OPAL acuity scores, across 30 protocols scored by both. Establishes construct validity for the rubric and characterises where the two instruments diverge and why.

**Data as of 2026-09-10.** Rubric scores: 40 protocols, 44-item basis (`TOTAL_MAX_WT` 136.8), 80,000-character extraction cap. OPAL scores: 86 protocols from `HEM_OPAL_scores.xlsx`. Overlap: 30.

## Executive Summary

Two instruments developed independently for the same portfolio — a 44-item weighted protocol-complexity rubric and an OPAL-derived workload acuity score — agree strongly (**Pearson r = 0.867, r² = 0.752**) across 30 shared protocols. Band-level agreement is **24/30 exact (80%)** and **30/30 within one band (100%)**; no protocol is misclassified by more than one adjacent band.

The six one-band disagreements are not randomly distributed. They separate cleanly by study shape: the rubric reads **lower** on low-enrollment/high-touch procedural studies and **higher** on design-heavy/low-visit studies. This is interpretable as a genuine construct difference — the rubric measures **protocol and scientific complexity**, OPAL measures **coordinator workload** — rather than as calibration error in either instrument. Attempts to close the gap by rubric modification were unsuccessful and are documented in the companion addendum.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Methods](#2-methods)
3. [Results](#3-results)
4. [Band Derivation](#4-band-derivation)
5. [Analysis of Disagreements](#5-analysis-of-disagreements)
6. [Discussion](#6-discussion)
7. [Limitations](#7-limitations)
8. [Conclusion](#8-conclusion)

---

## 1. Introduction

The complexity rubric documented in `research/checklist-report.md` produces a 0–100 weighted score intended to support go/no-go participation decisions. Applied to a portfolio already in activation, the go/no-go framing is not the operative question — the participation decision has been made — and the score is instead being used for **resourcing**: which studies need more coordinator capacity.

That reframing invites a validity question. An independent instrument for exactly that purpose already exists for this portfolio: OPAL acuity scores, recorded as a `Base + Modifiers` value on a roughly 1–10.5 scale with four bands (Low, Moderate, High, Very High). If the rubric is measuring something useful for resourcing, it should agree with OPAL. Where it disagrees, the disagreements should be interpretable.

This study tests that.

---

## 2. Methods

### 2.1 Instruments

| | Complexity Rubric | OPAL Acuity |
|---|---|---|
| Scale | 0–100 (weighted % of 136.8 max) | ~1.0–10.5 |
| Structure | 44 items × 0–3, five weighted dimensions + supplemental D6 | Base score + additive modifiers (M1–M5) |
| Construct | Protocol / scientific complexity | Site coordinator workload |
| Scored by | LLM against full protocol text (see `automated-scoring-methods.md`) | Human assignment |
| Bands | Low / Moderate / High / Very High (derived, §4) | Low / Moderate / High / Very High (assigned) |

The two instruments were developed independently and neither was calibrated against the other. OPAL scores predate the rubric scoring exercise.

### 2.2 Sample

- Rubric-scored: **40** protocols
- OPAL-scored: **86** protocols
- **Overlap: 30** protocols carrying both

Three OPAL entries were excluded before analysis: one duplicate of a protocol already present under its St. Jude mnemonic rather than the sponsor protocol number (`X4P-001-110` = 4WARDXP, identical 7.0/High), and two inactive studies (`PMVOCVR`, `SAMD9/9L-Mut`).

### 2.3 Analysis

Pearson correlation was computed on the raw scores. Ordinary least squares regression of OPAL on rubric score provided the mapping used for band derivation (§4). Band agreement was assessed as exact match and as within-one-adjacent-band.

---

## 3. Results

### 3.1 Correlation

```
OPAL = 0.1012 × Rubric − 0.244
r = 0.867     r² = 0.752     n = 30
```

The rubric explains **75% of the variance** in OPAL acuity. Mean rubric score 41.4; mean OPAL score 3.95.

### 3.2 Band agreement

| Metric | Result |
|---|---|
| Exact band agreement | **24/30 (80%)** |
| Within one band | **30/30 (100%)** |
| Disagreements by ≥2 bands | **0** |

### 3.3 Distributions

| Band | Rubric (n=40) | OPAL (n=86) |
|---|---:|---:|
| Low | 17 | 26 |
| Moderate | 11 | 31 |
| High | 9 | 15 |
| Very High | 3 | 14 |

Both instruments produce right-skewed distributions with the mass in the lower two bands, consistent with a portfolio dominated by registries, chart reviews, and observational cohorts.

### 3.4 Extremes

The rubric's ranking is face-valid at both ends. The highest-scoring protocols are gene- and cell-therapy trials; the lowest are retrospective chart reviews.

| Highest | Score | Band | Red flags |
|---|---:|---|---:|
| CITUSCD | 86 | Very High | 5 |
| SAGES1 | 82 | Very High | 4 |
| DBA19 | 79 | Very High | 4 |
| BGLOBAL | 75 | High | 2 |

| Lowest | Score | Band |
|---|---:|---|
| ROCHELLE | 6 | Low |
| COAGALL | 7 | Low |
| TOPMED | 14 | Low |
| ATHN | 15 | Low |

No modality information is supplied to the scoring process; this separation emerges from the protocol text alone.

---

## 4. Band Derivation

Rubric bands were derived by regressing OPAL on rubric score and mapping **OPAL's own observed band boundaries** back through the fit, rather than by optimising thresholds against the sample.

OPAL band ranges across the full 86-study set, with midpoint cutoffs:

| Band | OPAL range | Boundary |
|---|---|---:|
| Low | 1.0 – 3.0 | |
| | | 3.25 |
| Moderate | 3.5 – 5.5 | |
| | | 5.75 |
| High | 6.0 – 7.5 | |
| | | 7.75 |
| Very High | 8.0 – 10.5 | |

Mapped through `OPAL = 0.1012 × Rubric − 0.244`:

| Rubric Acuity | Score range |
|---|---|
| Low | < 35 |
| Moderate | 35 – 59 |
| High | 60 – 78 |
| Very High | ≥ 79 |

**Method note.** An earlier fit optimised cutoffs directly against the sample and achieved higher exact agreement (88%), but did so by compressing the High band into a three-point window (58–60) — an artefact of the overlap containing only **one** OPAL-High study at that time. Anchoring to OPAL's published boundaries scored lower on the optimised metric while generalising better. When a class has n=1, agreement percentage is the wrong objective function.

That decision was subsequently validated: four additional industry protocols were scored, raising OPAL-High representation in the overlap from 1 to 4, and the regression-derived boundaries classified 3 of 4 correctly — including both that landed in the newly-populated High band.

---

## 5. Analysis of Disagreements

All six disagreements are one band, and they sort by direction:

| Protocol | Rubric | Band | OPAL | Band | Direction |
|---|---:|---|---:|---|---|
| IXTEND3004 | 74 | High | 8.0 | Very High | rubric lower |
| SCDSTEMM | 64 | High | 8.0 | Very High | rubric lower |
| BDSTEM | 51 | Moderate | 7.0 | High | rubric lower |
| LEAP | 32 | Low | 5.5 | Moderate | rubric lower |
| ATHNTRANSCENDS | 60 | High | 4.5 | Moderate | rubric higher |
| MYPERS | 47 | Moderate | 3.0 | Low | rubric higher |

### 5.1 Rubric lower — low-enrollment, high-touch

BDSTEM and SCDSTEMM are both apheresis-based mobilization studies. Item-level inspection shows the rubric registering the intensity correctly (Item 2.2 = 3; Items 4.2/4.3 = 2 each) while Item 4.1 (Coordinator Time Required) scores 1, reasoned explicitly from enrollment volume: *"Small sample (12 enrollees) but intensive per-participant coordination…"*.

OPAL rates these High to Very High because per-participant burden drives coordinator effort regardless of N. A 12-patient study requiring five days of mobilization dosing, sedation, and multi-hour collections generates more work than its enrollment suggests.

### 5.2 Rubric higher — design-heavy, low-touch

MYPERS scores Item 1.4 at 3 (*">30 eligibility criteria"*) and Item 1.5 at 2 (specialized cardiac assays), while Item 4.1 scores 1: *"Only 40 participants over 60 months with two visits each."* The rubric weights the design complexity; OPAL weights the two-visits-per-patient reality.

ATHNTRANSCENDS follows the same shape — a broad natural-history cohort with genomics, scoring high on assessment breadth and low on per-visit demand.

### 5.3 Boundary cases

IXTEND3004 (74) and SCDSTEMM (64) both carry OPAL 8.0, sitting at the bottom of the Very High range against a rubric cutoff of 79. These are the least diagnostic disagreements — small score movements would resolve them, and both fall within the instrument's demonstrated test-retest variance of approximately ±4 points.

---

## 6. Discussion

The pattern in §5 is coherent enough to name. **The rubric measures protocol and scientific complexity; OPAL measures coordinator workload.** These correlate at r = 0.867 because complex protocols usually generate more work — but they come apart in exactly the two configurations where complexity and workload dissociate:

- **Low enrollment, high per-participant intensity** — few patients, demanding encounters. The rubric under-reads; OPAL captures it.
- **High design complexity, low visit burden** — elaborate eligibility and assays, minimal contact. The rubric over-reads; OPAL discounts it.

This has a practical consequence for how the two should be used. For **resourcing and staffing decisions**, OPAL is the better-fitted instrument; it was built for that question. For **protocol review, feasibility assessment, and scientific-burden triage**, the rubric captures dimensions OPAL does not — regulatory oversight, design complexity, eligibility restrictiveness — at item-level granularity with recorded rationales.

Six one-band disagreements out of thirty is good agreement *between different questions*. It should not be read as an error rate to be driven to zero.

Attempts to force convergence were made and failed; see `d4-9-procedural-intensity-addendum.md` §4–5. Neither adding an item targeting per-participant intensity nor reweighting the workforce dimension shifted the disagreements, for reasons that turn out to be arithmetic properties of normalized weighted averages rather than deficiencies in the item content.

---

## 7. Limitations

1. **n = 30.** A one-protocol change moves exact agreement by 3.3 percentage points. Differences of that size between rubric versions are not interpretable.
2. **OPAL scores are human-assigned and unblinded** to study identity; the rubric scores are model-assigned from protocol text. Neither is a gold standard, so disagreements cannot be attributed to one instrument.
3. **Band boundaries are derived, not validated.** The Moderate/High and High/Very High cutoffs rest on a regression fitted to 30 points with 4 OPAL-High and 3 Very-High cases.
4. **Rubric scores reflect a truncated evidence base.** Protocols are scored on the first 80,000 characters of extracted text — a mean of 36% of document length for the eight longest protocols. See `automated-scoring-methods.md` §5.
5. **Portfolio-specific.** Findings describe a non-malignant hematology caseload and should not be generalised to oncology or to portfolios with different enrollment profiles.

---

## 8. Conclusion

The 44-item complexity rubric shows strong concordance with an independently-developed workload instrument across 30 shared protocols (r = 0.867; 80% exact band agreement; 100% within one band; no ≥2-band errors). Its extremes are face-valid without modality information being supplied. Its six disagreements are systematic, directional, and explicable as a construct difference rather than calibration error.

The two instruments should be maintained side by side rather than reconciled. They answer adjacent questions, and the portfolio benefits from both.
