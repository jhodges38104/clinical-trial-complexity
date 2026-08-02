# HEM CTM Checklist Addendum — Draft for Review

**Status:** Draft, not yet integrated into the live tool, the Excel workbook, or `checklist-report.md`. This document proposes specific item text and scoring anchors for group review before anything is wired into the scoring engine.

**Scope:** Drafted for a non-malignant hematology CTM caseload — sickle cell disease, hemophilia, bone marrow failure syndromes, and general bleeding/clotting disorders — including non-interventional study designs (qualitative research, longitudinal EMR-based cohorts) that the current 34-item checklist wasn't built to score.

---

## Part 1 — Additions to the existing 5 core dimensions

Two of the three items discussed map cleanly onto the existing weighted framework as new items. One is a recalibration note rather than a new item (it doesn't touch the scoring math). **Adding new items to Dimensions 2 and 4 changes those dimensions' maximum possible score, which changes the master denominator the overall 0–100 complexity percentage is computed against — see "Math impact" below before adopting.**

### New Item 2.9 — Unscheduled / Event-Driven Visit Burden
*(Dimension 2: Operational Execution and Site Burden)*

**Why:** Item 2.1 ("Number of Study Visits") counts protocol-scheduled visits. In event-driven conditions — vaso-occlusive crises in SCD, bleeding episodes in hemophilia/VWD — real site burden comes from visits, dosing, and reporting triggered by the patient's clinical timeline, not the protocol's. A trial with few scheduled visits but constant unscheduled-event obligations currently scores deceptively low on this dimension.

| Item | Description | Scoring Guidance | Score (0–3) |
|------|-------------|-------------------|-------------|
| **2.9 Unscheduled/Event-Driven Visit Burden** | Frequency and predictability of non-protocol-scheduled visits or contacts triggered by clinical events | 0 = No unscheduled/event-triggered visits anticipated<br>1 = Occasional unscheduled contact (e.g., phone triage for reported symptoms), low expected frequency<br>2 = Regular unscheduled/urgent visits expected (e.g., VOC or bleeding-episode evaluation), standard business-hours capacity sufficient<br>3 = Frequent or unpredictable unscheduled visits requiring 24/7 site availability, ER-coordination, or after-hours dosing/reporting capacity | _____ |

**Revised Dimension 2 Subtotal:** _____ / 27 (was /24)
**Revised Dimension 2 Weighted Score:** Subtotal × 1.5 = _____ / 40.5 (was /36)

---

### New Item 4.8 — Long-Term Follow-Up (LTFU) Commitment
*(Dimension 4: Resource and Workforce Capacity)*

**Why:** Gene/cell therapy in this population (e.g., approved SCD and hemophilia gene therapies) typically carries FDA-mandated long-term follow-up extending 10–15 years past active treatment — a durable coordinator/site commitment none of the existing items capture, since they're implicitly scoped to the active trial period.

| Item | Description | Scoring Guidance | Score (0–3) |
|------|-------------|-------------------|-------------|
| **4.8 Long-Term Follow-Up (LTFU) Commitment** | Duration and intensity of post-treatment follow-up obligations beyond the active trial period | 0 = No extended follow-up beyond standard trial close-out (≤1 year)<br>1 = Extended follow-up 1–5 years post-treatment, low-intensity (e.g., annual survey/contact)<br>2 = Extended follow-up 5–10 years, periodic in-person visits or specialized monitoring (e.g., annual labs/imaging)<br>3 = Extended follow-up >10 years (e.g., 15-year gene therapy LTFU), sustained in-person visits, specialized long-term safety monitoring (e.g., secondary malignancy surveillance, insertional oncogenesis monitoring) | _____ |

**Revised Dimension 4 Subtotal:** _____ / 24 (was /21)
**Revised Dimension 4 Weighted Score:** Subtotal × 1.3 = _____ / 31.2 (was /27.3)

---

### Dimension 5 — Recalibration note (no new item, no math change)

**Why:** For a caseload that's predominantly rare/ultra-rare conditions (hemophilia B, Fanconi anemia, Diamond-Blackfan anemia), the generic Dimension 5 bands will classify nearly everything Medium–High, because Items 5.1 (Target Population Accessibility) and 5.3 (Competing Studies) will rarely score 0–1 for these conditions — that's expected, not a signal of elevated risk relative to your own baseline.

**Proposed addition to §8.3 Interpretation Guidance:**

> For sites whose caseload is predominantly rare/ultra-rare non-malignant hematologic conditions, the generic Dimension 5 bands (Low 0–6 / Medium 7–12 / High 13–18) will systematically skew Medium–High, since a small eligible population and competing sponsor trials for it are the norm, not the exception, in this space. This should not by itself be read as elevated risk. Per §11.1 Phase 2 (Calibration): after your pilot cohort, compute the site's own historical Dimension 5 score distribution and set Low/Medium/High bands from your own quartiles rather than the generic thresholds — this keeps Dimension 5 useful for differentiating your typical caseload instead of flattening everything to "high."

---

### Math impact if 2.9 and 4.8 are adopted

The overall complexity percentage is `ROUND((sum of 5 weighted dimension scores) / 124.5 × 100, 0)` (validation-report.md §2.2), where 124.5 is the sum of the five dimensions' weighted maximums (25.2 + 36 + 18 + 27.3 + 18). Adding 2.9 and 4.8 changes two of those maximums:

| Dimension | Old weighted max | New weighted max |
|---|---|---|
| 2 (Operational Execution) | 36 | 40.5 |
| 4 (Resource & Workforce) | 27.3 | 31.2 |
| **New denominator** | **124.5** | **132.9** |

**New formula:** `ROUND((sum of 5 weighted dimension scores) / 132.9 × 100, 0)`

This changes the overall percentage produced for *every* assessment, including historical ones, and invalidates the existing Excel-vs-web concordance validation (validation-report.md) until it's re-run against the new formula. Before this goes live: update the Excel workbook, update the web app's scoring logic (`index.html`, the DIMS/MATRIX functions referenced in validation-report.md §2.2), and re-run a validation pass with the same three-scenario (low/medium/high) methodology against the new 132.9 denominator. This is real but contained work — not a reason to avoid the change, just not a drop-in edit.

---

## Part 2 — New Dimension 6: Study Design Modality & Data/Specimen Complexity

**Kept deliberately separate from the core 0–100 score.** A large longitudinal EMR-abstraction cohort study and a Phase II drug trial aren't complex in comparable ways — forcing both onto one composite score would either dilute the drug-trial signal or produce a misleadingly low score for a cohort study that has no treatment arms or IP handling but is enormous in scope. Report Dimension 6 as its own parallel readout: **"Core Complexity: XX/100 (GO/CONDITIONAL/NO-GO)" alongside "Data & Specimen Complexity: XX/21 (Low/Medium/High)"** — two orthogonal numbers, not blended into one.

**Applicability note for Item 1.1 (Trial Phase):** its "0 = Phase IV or observational" anchor should not be read as "observational = simple." A non-interventional study will legitimately score low/N/A on several Dimension 1–4 items (treatment arms, IP handling) without that indicating true simplicity — Dimension 6 is where that study's actual complexity should surface.

### Rationale

Qualitative research and large longitudinal cohort studies built on retrospective and prospective EMR abstraction, biospecimen collection, and PRO batteries are common in non-malignant hematology (natural history studies, registries, patient-experience research) but don't fit an interventional-trial-shaped checklist. This dimension gives them the same structured, comparable scoring the other five give drug/device trials.

### Assessment Items

| Item | Description | Scoring Guidance | Score (0–3) |
|------|-------------|-------------------|-------------|
| **6.1 Study Design Modality** | Overall design type and number of concurrent data-collection modes | 0 = Simple observational/registry design, single data source, cross-sectional or short follow-up<br>1 = Observational cohort with a defined follow-up schedule, single data source<br>2 = Multi-source cohort (EMR + prospective visits + specimens), or a qualitative study with a structured protocol<br>3 = Complex multi-modal design combining retrospective EMR abstraction, prospective visits, biospecimen collection, PROs, and/or qualitative components in one protocol | _____ |
| **6.2 Qualitative Data Collection Burden** | Interviews, focus groups, or other qualitative methodology | 0 = No qualitative component<br>1 = Limited qualitative component (e.g., brief open-ended survey items), no formal coding required<br>2 = Semi-structured interviews or focus groups with a defined guide; transcription and thematic coding required; standard qualitative software (e.g., NVivo, Dedoose)<br>3 = Extensive qualitative program across multiple stakeholder groups (patients, caregivers, clinicians); iterative saturation-based sampling; multi-coder reliability process; specialized qualitative-methods staff required | _____ |
| **6.3 Retrospective EMR/Chart Abstraction Burden** | Volume and method of retrospective data abstraction from existing medical records | 0 = No retrospective chart review required<br>1 = Limited abstraction (<50 charts, or a narrow well-structured field set), primarily electronic/structured data pull<br>2 = Moderate abstraction (50–500 charts, or years of longitudinal history per patient), mix of structured EHR pull and manual review of unstructured notes/scanned documents<br>3 = Extensive manual abstraction (>500 charts, or deep multi-year/decade chart review per patient — e.g., full SCD or hemophilia treatment history), heavily reliant on manual review of scanned/unstructured records, multiple source systems, or outside-record requests | _____ |
| **6.4 Prospective & Electronic Abstraction Infrastructure** | Ongoing prospective EMR-linked or electronic data-capture requirements | 0 = No prospective EMR/electronic abstraction; data collected solely via study visit forms<br>1 = Periodic manual prospective chart review at defined intervals<br>2 = Structured electronic data feed (e.g., EHR interface, registry linkage, i2b2/OMOP extract) requiring informatics/IT setup and validation<br>3 = Continuous or near-real-time electronic data capture requiring dedicated informatics support, cross-system data-use agreements, and ongoing data-quality monitoring | _____ |
| **6.5 Biospecimen Collection & Biobanking** | Blood/tissue/other specimen collection, processing, and storage requirements | 0 = No specimen collection<br>1 = Standard specimen collection (e.g., routine blood draw), processed by local/commercial lab, no long-term storage<br>2 = Specialized processing (e.g., PBMC isolation, plasma separation, defined handling/timing windows) with short/medium-term storage<br>3 = Complex biobanking program: multiple specimen types, specialized preservation (e.g., −80 °C or liquid nitrogen), long-term storage with chain-of-custody tracking, and/or specimen sharing across sites or external biorepositories | _____ |
| **6.6 Patient-Reported Outcome (PRO) Burden** | Volume, frequency, and administration complexity of PRO instruments | 0 = No PRO collection<br>1 = Single brief PRO instrument, infrequent administration (e.g., 2–3 visits)<br>2 = Multiple PRO instruments or frequent administration (e.g., every visit), standard ePRO platform<br>3 = Extensive/complex PRO battery, high-frequency or diary-based collection (e.g., daily symptom/pain diaries), multiple platforms, or population-specific adaptation required (e.g., pediatric proxy-report versions, low-literacy accommodations) | _____ |
| **6.7 Longitudinal Duration & Cohort Scale** | Total study duration and cohort size driving sustained site commitment | 0 = ≤2 years total duration, <100 participants<br>1 = 2–5 years, 100–500 participants<br>2 = 5–10 years, 500–2,000 participants, or multi-site coordination required<br>3 = >10 years and/or >2,000 participants, requiring sustained multi-year staffing continuity, participant retention infrastructure, and long-term data/specimen stewardship | _____ |

**Dimension 6 Subtotal:** _____ / 21

### Interpretation Guidance

- **Low (0–7):** Straightforward data/specimen scope manageable within standard research-coordinator workflows.
- **Medium (8–14):** Meaningful data-management or specimen-handling burden; likely needs dedicated data-abstraction or informatics support.
- **High (15–21):** Substantial standing infrastructure required — informatics/data-management staff, biobanking capability, and/or qualitative-methods expertise — comparable in planning weight to a high-complexity interventional trial, even though it may score low on Dimensions 1–4.

### Weighting — leave unweighted (×1.0) and supplemental for now

Recommend treating Dimension 6 the same way Dimensions 3 and 5 are already weighted (×1.0) *if and when* the group decides to fold it into a blended score — but for the pilot, keep it fully separate from the 0–100 core score and report it as its own number. Folding it in later is a deliberate, visible decision the group can make once there's pilot data showing it behaves sensibly, not a default.

---

## Suggested next step

This is a review draft. Before anything moves into `checklist-report.md`, the Excel workbook, or the web app:
1. Group review of the item text/anchors above — anything to add, cut, or reword.
2. Decide whether to adopt 2.9 and 4.8 (core-dimension additions, requires the re-validation pass described above) versus holding them as assessor guidance notes only.
3. Decide Dimension 6's status: supplemental-only (recommended to start), or slated for future blending once calibrated.

Happy to wire whichever subset the group approves into the live checklist, the Excel workbook, and the web app's scoring engine — including updating the validation report with a fresh concordance pass if the core math changes.
