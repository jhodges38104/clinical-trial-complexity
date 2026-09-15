# HEM Protocol Review Tools

Local tooling for the departmental Hematology protocol review folder on OneDrive.
Kept out of OneDrive deliberately so it does not sync to colleagues.

## reconcile_tracker.py

Reconciles `CumulativeReviewtracking.xlsx` against the review documents actually
present on disk, and cross-checks both against
`Hematology_Protocol_Assessment_Workbook_Updated.xlsx`.

```sh
python3 reconcile_tracker.py                      # OneDrive folder, today's date
python3 reconcile_tracker.py "/path/to/folder"    # different folder
python3 reconcile_tracker.py "/path/to/folder" 2026-09-09   # pin the output date
```

**Writes two new files into the review folder** (never modifies the originals):

| File | Contents |
|---|---|
| `Tracker_Reconciliation_<date>.md` | Full report. FACT sections are filesystem-derived; PROPOSED sections need sign-off. |
| `CumulativeReviewtracking_reconciled_<date>.xlsx` | 4 sheets — Reconciled Tracker, Score Detail, File Inventory, Findings |

Re-running on the same date overwrites only those two files. The script prints
the original tracker's MD5 on every run so you can confirm it was untouched.

## make_score_sheet_template.py

Generates `Protocol Score Sheet TEMPLATE v2.docx` into the review folder — the
corrected score sheet, replacing the one whose header read "possible scores 5-25"
over six criteria.

```sh
python3 make_score_sheet_template.py
```

What changed from v1:

- Header states the real maximum (6 × 5 = **30**)
- **The NA rule is explicit and single**: an NA criterion is removed from the
  denominator — not scored 0, not scored 3 — with a worked example
- Total row asks for sum, n scored, denominator, **and percentage** (the only
  figure comparable between a sponsor trial scored /20 and an investigator study /30)
- **A required Committee Decision block**: recommendation, conditions, owner,
  due date, and the one-line comment that goes into the tracker. This is the
  root-cause fix for 13 of 14 protocols having no recorded decision — the old
  sheet never asked for one.
- Page 2 carries 1–5 scoring anchors for all six criteria, adapted from the
  department's own Protocol Assessment Workbook rubric

Always render before circulating (LibreOffice is installed):

```sh
/Applications/LibreOffice.app/Contents/MacOS/soffice --headless \
  --convert-to pdf --outdir /tmp "Protocol Score Sheet TEMPLATE v2.docx"
```

Note: python-docx does not update `w:tblGrid` when you set `cell.width`, so
LibreOffice ignores column widths unless the grid is rewritten too — the
`fixed()` helper does this. Without it every column comes out equal width.

## decisions.py + make_decision_worksheet.py

`decisions.py` holds the proposed committee decision for each of the 13 protocols
that had no recorded outcome. `make_decision_worksheet.py` renders them as a
mark-up document for sign-off:

```sh
python3 make_decision_worksheet.py
```

Each entry is one of three statuses, and the distinction matters:

| Status | Meaning |
|---|---|
| `RECORDED` | The review documents state the outcome; the quote is the evidence. No inference. |
| `PROPOSED` | Inferred from scores and narrative. **Needs confirmation — not a record of what the committee decided.** |
| `CANNOT` | The documents do not support any defensible proposal. |

Currently 2 RECORDED, 10 PROPOSED, 1 CANNOT (4WARDXP, which has no second reviewer).
VINGT is excluded — confirmed tabled by JH on 2026-09-09.

Entries are sorted by confidence so the fast confirmations come first. Every entry
carries the verbatim source quote and its filename, so any proposal can be checked
against the document it came from.

**These never write into `Resulting comments`.** They occupy their own columns in
the reconciled workbook (`Decision status`, `Proposed decision (NOT a record)`,
`Basis (quoted)`, `Conditions / next step`, `Confidence`). Once JH confirms a
decision, move it into `Resulting comments` and change its status.

`reconcile_tracker.py` imports `decisions.py` if present, so the two stay in sync
from one source of truth.

## update_assessment_workbook.py

Updates `Hematology_Protocol_Assessment_Workbook_Updated.xlsx` from the review
record. Writes `Hematology_Protocol_Assessment_Workbook_reconciled_<date>.xlsx`;
the original is never modified.

```sh
python3 update_assessment_workbook.py
```

Reads scores and proposed decisions from `CumulativeReviewtracking_reconciled_<date>.xlsx`,
so the two stay consistent. Run the reconciler first.

**Changes it makes**

1. Adds `Reviewed - Decision Pending` to the Review Status dropdown (G2:G100).
   The original vocabulary had no value meaning "review happened, decision not
   yet confirmed" — the true state of most reviewed rows. *Approved by JH 2026-09-09.*
2. Updates the 11 rows that were reviewed but still read Pending/Under Review.
3. Appends review facts to Notes, following the existing `"; "` convention and
   preserving what was there.
4. Adds the 4 reviewed protocols missing from the workbook (VINGT, LTFUAGT4HB,
   AG348-C-028, AG348-C-029).
5. Relabels Dashboard `A3` to "Total Protocols **Entered**" (the formula is COUNTA
   of the ID column — it counts entries, not reviews) and adds a
   `Reviewed - Decision Pending` metric so the largest category is visible.

**What it deliberately does NOT do**

- **Does not populate Design / Benefit / Resource scores (H, I, J).** Those are a
  63-criterion /100 rubric; the reviews used a 6-criterion /30 sheet. Mapping one
  onto the other would be fabrication.
- **Does not populate the Decision column (M).** Per the workbook's own Instructions
  the decision derives from /100 thresholds that were never scored. Where a decision
  IS known it is carried by Review Status instead (`Conditionally Approved`, `Deferred`).
- **Does not write unconfirmed decisions as fact.** Notes mark each as `RECORDED`,
  `PROPOSED ... (unconfirmed)`, or `NO DECISION POSSIBLE`.

**Verify after running.** openpyxl can silently drop workbook features. Confirmed
preserved on the 2026-09-09 run: all 10 sheets, 3 list validations, 4 table parts,
`Table1` range, freeze panes, and all 99 `TOTAL SCORE` formulas. A LibreOffice
recalculation returned 58 entered / 8 pending / 12 reviewed-decision-pending with
no formula errors.

```sh
# force a recalculation to check formulas still evaluate
/Applications/LibreOffice.app/Contents/MacOS/soffice --headless \
  --convert-to xlsx --outdir /tmp/recalc "<the reconciled workbook>"
```

## Requirements

`openpyxl`, `python-docx`, and `pdftotext` (poppler) on PATH. All present under
`/opt/miniconda3/bin/python3` and `/opt/homebrew/bin` as of 2026-09-09.

## Adding a new review batch

1. Add the protocol to `NAME_MAP` (tracker label, on-disk aliases, workbook name).
2. Add a matching entry to `R` with the file paths, per-criterion scores read from
   the review documents, and the decision text.
3. Re-run.

File presence, MD5s and duplicate detection are mechanical and need no upkeep.
Scores and decision text are hand-encoded from the documents — `arith()`
re-derives every total from the per-criterion values, so a mistyped criterion
surfaces as an arithmetic mismatch in the report rather than passing silently.

`PI_OVERRIDE` holds PI corrections that differ from the original tracker (currently
AG348 → Parul Rai). Each is flagged in the output, never applied silently.

## State as of 2026-09-09

14 protocols reviewed across 5 batches (8.20.25 – 10.01.25). Roster is complete —
every tracker row has artifacts on disk and vice versa. Open items are:

- 13 of 14 protocols have **no recorded decision** (VINGT is tabled; the rest are blank)
- Three conflicting conventions for scoring a criterion `NA` (dropped / 0 / 3),
  which makes totals incomparable across protocols
- 4WARDXP has no second-reviewer input
- CHITIN and PNHIPTA each have two reviewer documents that disagree on the score
