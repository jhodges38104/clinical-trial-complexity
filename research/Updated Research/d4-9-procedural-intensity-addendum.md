# Dimension 4 Addendum — Per-Participant Procedural Intensity (Item 4.9)

**Status: Adopted into the live tool.** Item 4.9 is live in `index.html` and `offline-bundle/index.html` as of 2026-09-10. Dimension 4 max raw 24→27, max weighted 31.2→35.1, red-flag threshold 17→19, and **`TOTAL_MAX_WT` 132.9 → 136.8**. **Not yet updated:** the Excel workbook (`data/complexity-scoring-engine.xlsx`), which remains on the 43-item / 132.9 basis — Excel and web are out of parity for Item 4.9, extending the parity gap already documented at the top of `research/validation-report.md`.

**Scope:** Drafted against a non-malignant hematology CTM caseload after 40 protocols were scored and cross-checked against an independent workload instrument (`HEM_OPAL_scores.xlsx`). See the companion `opal-concordance-study.md` for the cross-instrument evidence this addendum rests on.

> **Headline finding, stated up front:** Item 4.9 measures something real that no other item captured, but it **did not improve** agreement with the OPAL workload instrument (83% → 80% exact band agreement, n=30). Section 4 explains why this outcome was arithmetically inevitable and why the item is nonetheless worth keeping.

## Table of Contents

1. [Motivation](#1-motivation)
2. [Item Specification](#2-item-specification)
3. [Math Impact](#3-math-impact)
4. [Empirical Evaluation](#4-empirical-evaluation)
5. [Alternatives Tested and Rejected](#5-alternatives-tested-and-rejected)
6. [Recommendation](#6-recommendation)

---

## 1. Motivation

Dimension 4 (Resource & Workforce Capacity) contained eight items before this addendum: coordinator FTE, specialized expertise, space and equipment, pharmacy, laboratory, budget adequacy, current site workload, and long-term follow-up commitment. None of these captures **per-visit procedural burden** — how demanding an individual participant encounter is, independent of how many participants there are.

The gap surfaced empirically. Cross-checking 30 protocols against OPAL acuity scores showed a directional pattern: **both apheresis-based mobilization studies in the portfolio (BDSTEM, SCDSTEMM) scored lower on the rubric than on OPAL**, and inspection of the item-level rationales identified the mechanism. For BDSTEM the model scored Item 4.1 (Coordinator Time Required) at 1, reasoning explicitly from enrollment volume — *"Small sample (12 enrollees)"* — while simultaneously scoring Item 2.2 at 3 (*"plerixafor dosing, serial CD34+ blood draws over 4–6 hours, and a single-blood-volume apheresis"*) and Items 4.2/4.3 at 2 each (experienced apheresis staff, procedural sedation, continuous telemetry).

The rubric was therefore describing an intensive study correctly at the item level while aggregating it as moderate effort. In a rare-disease portfolio — where low enrollment and high per-participant intensity co-occur as the norm rather than the exception — this is a systematic under-read of the dominant study pattern.

---

## 2. Item Specification

### New Item 4.9 — Per-Participant Procedural Intensity

*(Dimension 4: Resource & Workforce Capacity)*

| Score | Anchor |
|---:|---|
| 0 | Routine visits — labs, questionnaires, standard imaging |
| 1 | Extended visits or minor procedures — infusion, serial PK sampling |
| 2 | Invasive or multi-hour procedures — biopsy, apheresis, sedation, telemetry |
| 3 | Multi-day inpatient or chained procedures — mobilization + apheresis, conditioning |

The anchors deliberately describe **the participant encounter**, not the site's capacity to deliver it (Item 4.2), the physical infrastructure required (Item 4.3), or the number of encounters (Items 2.1/2.9). Those remain separately scored; 4.9 is orthogonal to all of them.

### Observed scoring behaviour

Across the 40 protocols scored on the updated rubric, Item 4.9 distributed as follows:

| Score | n | Representative studies |
|---:|---:|---|
| 0 | 17 | Retrospective chart reviews, registries, survey studies |
| 1 | 10 | Standard infusion or PK-sampling trials |
| 2 | 9 | Imaging with pharmacologic stress, biopsy sub-studies |
| 3 | 4 | Apheresis + mobilization, gene-therapy conditioning |

The item discriminates cleanly across the full 0–3 range with no floor or ceiling clustering, and the assigned scores are defensible on inspection. Representative rationales:

- **BDSTEM (3)** — *"Chained procedures per participant: 5 days of G-CSF mobilization, plerixafor, catheter placement…"*
- **SCDSTEMM (3)** — *"Chained procedures: hydroxyurea hold, exchange transfusion, possible central line placement…"*
- **MYPERS (2)** — *"Participants undergo a multi-hour PET session with IV radiotracer injections, pharmacologic vasodilator…"*

---

## 3. Math Impact

Adding a ninth item to Dimension 4 changes the dimension maximum and therefore the master denominator:

| Quantity | Before | After |
|---|---:|---:|
| D4 items | 8 | 9 |
| D4 max raw | 24 | 27 |
| D4 max weighted (× 1.3) | 31.2 | 35.1 |
| D4 red-flag threshold | 17 | 19 |
| **`TOTAL_MAX_WT`** | **132.9** | **136.8** |
| Total scored items (incl. supplemental D6) | 43 | 44 |

The red-flag threshold was moved to preserve its proportion of the dimension maximum (17/24 = 0.708; 19/27 = 0.704) rather than its absolute value.

**Scores computed before and after this change are not directly comparable.** All 40 portfolio protocols were re-scored on the 44-item basis; the prior 43-item result set is retained separately for comparison.

---

## 4. Empirical Evaluation

### 4.1 Effect on agreement with OPAL

The same 30 protocols carrying both a rubric score and an OPAL acuity score were compared under each rubric version:

| Rubric | Exact band agreement | Pearson r |
|---|---|---:|
| 43-item (132.9) | 25/30 (**83%**) | 0.870 |
| 44-item (136.8) | 24/30 (80%) | 0.867 |

Adding Item 4.9 produced a **marginal decrease** in concordance. At n=30 a one-protocol difference is well within sampling variation, so the honest reading is that the change is concordance-neutral, not that it harmed the instrument.

### 4.2 Why the motivating cases did not move

The item failed to shift the two studies that motivated it:

| | D4 raw before | D4 raw after | Overall before | Overall after |
|---|---:|---:|---:|---:|
| BDSTEM | 9/24 | 14/27 | 50 | **51** |
| SCDSTEMM | 14/24 | 18/27 | 64 | **64** |

Both scored the maximum 3 on Item 4.9. Both moved by ≤1 point overall.

This is arithmetic, not a scoring failure. **The overall score is a percentage of the maximum, so adding an item raises the numerator and the denominator together.** A study scoring the full 3 gains 3 × 1.3 = 3.9 weighted points against a denominator that grew by 27 × 1.3 − 24 × 1.3 = 3.9. The net effect on a study already scoring near the portfolio mean is approximately zero.

The general principle: **a normalized weighted-average score cannot be shifted by adding criteria to it.** Adding items makes a rubric more descriptive without making it more discriminating.

### 4.3 Which studies did move

Four protocols rose against the ~3% downward drift the larger denominator imposes on everything else:

| | Before | After | Δ | Item 4.9 |
|---|---:|---:|---:|---:|
| LIVBX | 52 | 56 | +4 | 2 |
| INSIGHT-HD | 48 | 52 | +4 | 2 |
| 4WARDXP | 65 | 68 | +3 | 2 |
| HIBISCUS2 | 61 | 64 | +3 | 1 |

These are studies scoring **moderately** on 4.9 while scoring **low** on the rest of Dimension 4. For them the new item raised D4 relative to their own baseline, which is exactly the leverage the score's normalization denies to studies already scoring high across the dimension.

---

## 5. Alternatives Tested and Rejected

### 5.1 Increasing the Dimension 4 weight

Simulated across all 40 scored protocols at weights 1.3 through 4.0, recomputing band agreement at each:

| D4 weight | Exact agreement | BDSTEM |
|---:|---|---|
| 1.3 (current) | **25/30 (83%)** | 51 Moderate |
| 1.6 | 25/30 (83%) | 51 Moderate |
| 2.0 | 24/30 (80%) | 51 Moderate |
| 3.0 | 22/30 (73%) | 51 Moderate |
| 4.0 | 21/30 (70%) | 52 Moderate |

Reweighting was **rejected**: at triple the current weight the target study moved one point, and portfolio-wide agreement degraded from 83% to 70%.

The reason is structural. Up-weighting a dimension pulls the overall score toward *that dimension's own percentage*. BDSTEM scores D4 at 14/27 = 52% against an overall of 51%; SCDSTEMM 67% vs 64%; MYPERS 48% vs 47%. Where a dimension's percentage already equals the overall, no weighting scheme creates leverage. Reweighting only moves scores for studies whose profile is sharply uneven — and the motivating cases are uniformly middling on every axis.

### 5.2 An additive modifier outside the normalized score

The OPAL instrument itself uses a `Base + Modifiers` architecture (e.g. `base=8, mods=M1M2M3M4M5`), where modifiers are additive rather than averaged in. Applying `CX + 4 × (4.9 score)` was modelled and **rejected**: it corrects BDSTEM (51 → 63, entering the High band and matching OPAL) but pushes MYPERS from 47 to 55, moving it *further* from OPAL's Low band. It trades one disagreement for another.

---

## 6. Recommendation

**Keep Item 4.9 as a descriptive field; do not expect it to move bands.**

1. It records a real construct — per-participant procedural intensity — that no other item in the instrument captures, and it discriminates cleanly across all four anchor levels.
2. Its concordance cost is one protocol out of thirty, within noise.
3. Its `CX D4.9` value is independently useful for a rare-disease portfolio, where the low-enrollment / high-intensity pattern is common and is otherwise invisible in the aggregate score.

**Do not** attempt further reconciliation with OPAL through the weighted score. Section 5 and the companion concordance study together establish that the residual divergence is a construct difference — protocol complexity versus coordinator workload — not a calibration gap that item or weight changes can close.

**Outstanding:** the Excel workbook requires updating to the 44-item / 136.8 basis before Excel and web can be revalidated against each other. Until then, treat the web application as authoritative and see `research/validation-report.md` for the standing parity caveat.
