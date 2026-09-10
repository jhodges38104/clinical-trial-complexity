# Automated Protocol Scoring — Methods and Failure Modes

**Status: Operational.** Describes the batch scoring pipeline used to apply the 44-item complexity rubric to 40 protocols, the input-quality failure modes encountered, and the reproducibility characteristics observed. Complements the browser tool (`index.html`), which scores one protocol at a time interactively.

**Data as of 2026-09-10.** 40 protocols scored, `claude-opus-5`, uniform 44-item rubric (`TOTAL_MAX_WT` 136.8), 80,000-character extraction cap.

## Executive Summary

The browser tool scores one protocol per session through manual upload. Applying the rubric across a portfolio required a batch pipeline. The design constraint that shaped everything else was **avoiding rubric drift**: the harness reads the item definitions, weights, decision matrix, and character cap directly out of `index.html` at runtime rather than reimplementing them, so tool and pipeline cannot diverge.

Three input-quality failure modes were encountered, all of which produce **plausible but wrong scores if undetected**: document-viewer stubs mistaken for protocols, PDFs with unmappable font encodings, and filename collisions that silently substitute one study's protocol for another's. Each is now detected and refused rather than scored. Test-retest reproducibility was measured at approximately ±4 points on the 0–100 scale, with band assignment stable.

## Table of Contents

1. [Architecture](#1-architecture)
2. [Scoring Procedure](#2-scoring-procedure)
3. [Text Extraction](#3-text-extraction)
4. [Input-Quality Failure Modes](#4-input-quality-failure-modes)
5. [Truncation](#5-truncation)
6. [Reproducibility](#6-reproducibility)
7. [Provenance](#7-provenance)
8. [Limitations](#8-limitations)

---

## 1. Architecture

```
index.html ──► rubric.py ──► score.py ──► results/<MNEMONIC>.json ──► portfolio workbook
 (rubric)      (extract)     (score)        (per-protocol)              (CX columns)
```

`rubric.py` parses the JavaScript object literals in `index.html` by bracket-matching — `DIMS`, `DIM6`, `MATRIX`, `TOTAL_MAX_WT`, `MAX_CHARS` — and converts them to Python structures. It validates on load that every item carries a 0–3 anchor set and that the declared `TOTAL_MAX_WT` equals the sum of dimension maxima.

**This single-sourcing is the load-bearing design decision.** When Item 4.9 was added to the tool, the harness picked it up with no code change. A reimplemented rubric would have required a parallel edit and would drift the first time one was missed.

---

## 2. Scoring Procedure

Each protocol is scored in one request:

1. Locate the document (§3.1) and extract text (§3.2)
2. Truncate to `MAX_CHARS` (§5)
3. Build a prompt enumerating all 44 criteria with their anchors, mirroring the tool's own prompt construction
4. Request a JSON object of `{item_id: {score, rationale}}`
5. Compute dimension raws, weighted total, overall percentage, red flags, and decision cell using the tool's own math
6. Write a per-protocol JSON result immediately

Scoring math is the tool's, not a reimplementation: `overall = round(Σ(raw × weight) / TOTAL_MAX_WT × 100)`, red flags where `raw > rfThresh`, decision from the 3×3 matrix on overall × Dimension-5 raw.

**Results are written per protocol, not accumulated.** This makes batches resumable — an already-scored protocol is skipped unless forced — and means an interruption at protocol 20 of 21 preserves 19 results.

### 2.1 Model behaviour requiring handling

Three response-level failure modes were observed and are now retried automatically:

| Failure | Frequency | Handling |
|---|---|---|
| Prose instead of JSON | 3 of ~60 requests, all on long protocols | Re-ask, up to 3 attempts |
| Response truncated at `max_tokens` mid-JSON | 1 | Raise cap; 32,000 was insufficient for the densest protocol |
| Request timeout | 2 | Retry with backoff; 900s ceiling |

A 400-class error (credit exhaustion, authentication) **aborts the entire batch** rather than failing per protocol. This was learned the hard way: a mid-batch credit lapse produced 21 consecutive identical failures before the run ended.

---

## 3. Text Extraction

### 3.1 Document resolution

Protocol files follow no single naming convention across the two source directories. Candidates are ranked:

| Rank | Rule | Example |
|---:|---|---|
| 1 | Filename stem equals the mnemonic | `ATHN.pdf` → ATHN |
| 2 | Stem before `_SJCRH` equals the mnemonic | `SCDIC-II_SJCRH-HEM_Protocol_…` |
| 3 | An explicit alias appears as a whole token | `ATHNdataset_Registry_Protocol_…` |
| 4 | The mnemonic appears as a whole token | `Study_Document_TOPMed_SCD_Protocol_…` |
| 5 | A token begins with the mnemonic | fallback |

Rank 3 outranking rank 4 is deliberate and non-obvious — see §4.3.

Candidates are tried in rank order, and each must pass validation (§4) before use; a rejected candidate falls through to the next.

### 3.2 Extraction and normalization

PDFs are extracted with `pdftotext -layout`; all other formats (`.docx`, `.doc`, `.rtf`, `.html`, `.txt`) via `textutil`. Extracted text is then normalized identically to the browser tool:

```
collapse [ \t ]+ → single space
trim leading/trailing space on each line
cap runs of ≥3 newlines at 2
```

This removes 18–25% of characters from PDF-derived text, which is column padding rather than content. The trade-off is real: `-layout` *creates* that padding deliberately to reconstruct table columns, so collapsing it loses alignment in schedule-of-events grids. Coverage was judged the better bargain — a schedule table that survives truncation in degraded form beats one that is cut off entirely — and consistency with the browser tool required matching its behaviour.

---

## 4. Input-Quality Failure Modes

All three below share a property that makes them dangerous: **they produce complete, well-formed, plausible scores.** None raises an error. Each is now detected and refused.

### 4.1 Document-viewer stubs

Five protocol "documents" were single-page export artefacts — a viewer cover sheet beginning with the word "Close", or in one case an HTML placeholder reading *"Please Wait … The Document is being generated into a PDF file."* These extract 100–3,562 characters.

Scored, such a stub yields a full 43-item result in which most items read "no evidence in the protocol" and default to 0 — producing a **low complexity score indistinguishable from a genuinely simple study**.

Detection: a minimum-length floor (8,000 characters, overridable) plus signature matching on the known placeholder strings. Real protocols in this portfolio range from 16,694 to 432,802 normalized characters; the largest stub was 3,562, so the floor separates cleanly.

### 4.2 Unmappable font encodings

One protocol (4WARDXP) extracted 1.55 million characters of mojibake — `01ÿ34567589 85ÿ8ÿÿ`. `pdffonts` identified the cause: Type 3 fonts with custom encoding and no ToUnicode CMap (`uni: no`), leaving no glyph-to-Unicode mapping.

Two diagnostics distinguish this from ordinary text:

| Metric | Corrupt | Clean |
|---|---:|---:|
| Readable-character ratio | 0.841 | 0.996 |
| Common-English word share | 1.9% | 18.9% |

The character count was itself misleading — mojibake **inflates** it, so "1.5 million characters" was never 1.5 million characters of content. After `ocrmypdf --force-ocr`, the same document yielded 298,221 characters and 25,283 real words, up from 1,132.

**`--force-ocr` is required, not optional.** Standard OCR skips pages that already contain text, and these pages do contain text — just unmappable text. An initial OCR pass without the flag left the readable ratio unchanged at 0.835.

The corrected score moved from 50 (Moderate, 0 red flags) to 65 (High, 2 red flags), matching the OPAL band it had previously disagreed with.

### 4.3 Filename collisions

When a stub is rejected and the resolver falls through to the next candidate, it can land on **a different study's protocol**. Observed: `ATHN.pdf` (a 320-character stub) was rejected, and the fallback matched `ATHN TRANSCENDS_SJCRH-HEM_Protocol_…pdf` — a real, complete, 186,667-character protocol belonging to a different study. It would have scored cleanly and attributed ATHN TRANSCENDS's complexity to ATHN.

This is the most dangerous of the three failure modes, because falling back to *something valid* looks like success. The fix is the rank-3-above-rank-4 ordering in §3.1: an explicit alias token outranks a bare mnemonic token, so `ATHN` resolves to `ATHNdataset_Registry_Protocol_…` rather than stealing a longer mnemonic's file.

---

## 5. Truncation

The 80,000-character cap is inherited from the browser tool, where it was sized for a different model's context window. For the eight longest protocols it admits a mean of **36%** of the document:

| Cap | Mean coverage (8 longest) |
|---:|---:|
| 80,000 | 36% |
| 150,000 | 65% |
| 250,000 | 88% |
| 400,000 | 99% |

A four-protocol experiment at 250,000 characters produced consistent upward movement:

| | 80k | 250k | Δ | OPAL band | Outcome |
|---|---:|---:|---:|---|---|
| SAGES1 | 82 | 89 | +7 | Very High | agrees both |
| TOPMED | 14 | 20 | +6 | — | control |
| IXTEND3004 | 74 | 79 | +5 | Very High | **disagreement resolved** |
| HIBISCUS2 | 64 | 65 | +1 | High | agrees both |

One band agreement gained, none lost. **But the effect size overlaps test-retest variance** (§6), so at n=4 only the direction is informative: four of four moving the same way has roughly a 12% probability under noise alone.

A fifth protocol (CITUSCD, 18% → 58% coverage) moved the *other* way, 86 → 79. It has no OPAL score to arbitrate. The current reading is that the back portion of a protocol carries burden the synopsis does not advertise — appendix-level lab schedules, safety monitoring, sub-studies — and the rubric under-reads when it cannot see them.

**The cap remains at 80,000 pending a larger experiment.** A `--max-chars` override exists for selective use on the worst-covered protocols. Re-baselining the full portfolio at 250,000 would cost roughly 3.3× the input tokens.

---

## 6. Reproducibility

Sampling parameters (`temperature`, `top_p`) are not available on the current model generation, so identical inputs do not guarantee identical outputs. Two protocols were re-scored against unchanged documents:

| | Original | Re-run | Δ | Band |
|---|---:|---:|---:|---|
| BDSTEM | 50 | 50 | 0 | Moderate → Moderate |
| MYPERS | 50 | 46 | −4 | Moderate → Moderate |

Individual dimension raws drifted up to ±2 (BDSTEM D1 9→11, D2 16→15, D4 10→9) while the overall remained stable, consistent with independent per-item noise partially cancelling in aggregate.

**Practical implication: differences of ≤4 points on the 0–100 scale should not be interpreted.** This bounds what any rubric modification can be shown to achieve at this sample size and is the basis for treating the 43-item vs 44-item agreement difference (83% vs 80%) as noise.

---

## 7. Provenance

Every result carries the basis on which it was produced, so scores from different sources are never silently compared:

| `CX Basis` value | n | Meaning |
|---|---:|---|
| `full_protocol` | 39 | Protocol text, clean extraction |
| `full_protocol (OCR)` | 1 | Text recovered via forced OCR |
| `n/a — <reason>` | 6 | Not scored by design (exempt, QI, sample-only, basic science, closed) |

Results also record the model ID, scoring date, token usage, truncation flag, and the resolved document filename.

The `n/a` category matters as much as the scored ones: it distinguishes *not applicable* from *pending*, so a blank score is not read as an outstanding gap. Exempt, quality-improvement, sample-only, and basic-science studies are excluded by study type rather than by score — they would score near the floor and compress the portfolio distribution without conveying information, since they have no visit schedule or coordinator workload of the kind Dimensions 2 and 4 measure.

---

## 8. Limitations

1. **Single-rater.** Each protocol is scored once by one model. No inter-rater comparison against human scoring of the same protocols has been performed.
2. **No gold standard.** Concordance with OPAL (`opal-concordance-study.md`) is the only external check, and OPAL is itself an unvalidated human instrument.
3. **Truncated evidence.** See §5. Scores reflect a mean 36% of document length for the longest protocols.
4. **Table structure is degraded** by normalization (§3.2), which may affect items keyed to visit schedules.
5. **Extraction quality is uneven** and only partly measurable. The readable-ratio and word-share diagnostics in §4.2 catch gross corruption; subtler degradation would not be detected.
6. **Model-version dependent.** Scores are tied to `claude-opus-5`; a different model would require re-baselining, which is why `CX Model` is recorded per result.
