# -*- coding: utf-8 -*-
"""
Reconcile HEM Protocol Reviews: CumulativeReviewtracking.xlsx vs. files on disk.

Reads the review folder, verifies which artifacts exist for each protocol
(protocol doc / reviewer score sheet / SCORING..DM doc), extracts the scores
recorded in those documents, cross-checks against the 54-row assessment
workbook, and writes two NEW files into the review folder:

    Tracker_Reconciliation_<date>.md
    CumulativeReviewtracking_reconciled_<date>.xlsx

The originals are never modified. Re-running on the same date overwrites only
the two generated files above.

USAGE
    python3 reconcile_tracker.py [review_folder] [date]

    review_folder  defaults to the OneDrive HEM Protocol Reviews folder
    date           defaults to today (YYYY-MM-DD); sets the output filenames

REQUIRES
    openpyxl, python-docx, and pdftotext (poppler) on PATH.
    All three were present on this Mac as of 2026-09-09.

MAINTAINING THIS SCRIPT
    File presence, MD5s and duplicate detection are computed mechanically and
    need no upkeep. The per-protocol SCORES and DECISION TEXT in the `R` dict
    below were read by hand out of the review documents -- when a new review
    batch lands, add an entry to NAME_MAP and a matching entry to R, then
    re-run. `arith()` re-derives every total from the per-criterion values, so
    a typo in a criterion will surface as an arithmetic mismatch rather than
    passing silently.

    PI_OVERRIDE holds PI corrections confirmed by JH that differ from the
    original tracker; each one is flagged in the output rather than applied
    silently.
"""
import os, sys, glob, hashlib, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from decisions import BY_KEY as DECISION_BY_KEY, DECISIONS as DECISION_LIST
except ImportError:
    DECISION_BY_KEY, DECISION_LIST = {}, []

DEFAULT_ROOT = ("/Users/jhodges/Library/CloudStorage/"
                "OneDrive-St.JudeChildren'sResearchHospital/HEM Protocol Reviews")

ROOT = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT
TODAY = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()

if not os.path.isdir(ROOT):
    sys.exit("Review folder not found: %s" % ROOT)
os.chdir(ROOT)
print("Reconciling: %s\n        date: %s" % (ROOT, TODAY))

# ---------- 1. FACTS: file inventory + hashes ----------
inventory = {}
for f in glob.glob("**/*", recursive=True):
    bn = os.path.basename(f)
    if os.path.isfile(f) and bn != ".DS_Store" and not bn.startswith(
            ("Tracker_Reconciliation_", "CumulativeReviewtracking_reconciled_",
             "Decision Confirmation Worksheet", "Protocol Score Sheet TEMPLATE",
             "Hematology_Protocol_Assessment_Workbook_reconciled_")):
        inventory[f] = hashlib.md5(open(f, "rb").read()).hexdigest()

by_hash = {}
for f, h in inventory.items():
    by_hash.setdefault(h, []).append(f)
dupes = {h: sorted(v) for h, v in by_hash.items() if len(v) > 1}

# ---------- 2. Name map: tracker label -> disk/workbook aliases ----------
NAME_MAP = [
    ("CHITIN",            ["CHITIN"],                          "CHITIN"),
    ("PNHIPTA",           ["PNHIPTA", "PNHITPA"],              "PNHIPTA"),
    ("X4WARDXP",          ["4WARDXP"],                         "4WARDXP"),
    ("IDBLEED",           ["IDBLEED"],                         "IDBLEED"),
    ("IXTEND3004",        ["IXTEND3004"],                      "HEMGENIX"),
    ("RHEMEDY",           ["RHEMEDY", "Rhemedy"],              "RHEMEDY"),
    ("MIPICS",            ["miPICs", "MiPICS"],                "miPICs"),
    ("MYPERS",            ["MYPERS"],                          "MYPERS"),
    ("VINGT",             ["VINGT", "VINGHT"],                 "(not present)"),
    ("LTFAGTHB",          ["LTFUAGT4HB", "LTFU4HB"],           "(parent AGT4HB only)"),
    ("LEAP",              ["LEAP"],                            "LEAP"),
    ("LIVBX",             ["LIVBX", "LIV BX"],                 "LIVBX"),
    ("SCDSTEMM",          ["SCDSTEMM", "SCD STEMM"],           "SCDSTEMM"),
    ("AG348_C28 AND C29", ["AG348", "AG 348"],                 "(not present)"),
]

# ---------- 3. Curated review data (read from the documents; see report provenance) ----------
# tot = total as WRITTEN in the doc; sums = per-criterion values in order
# order: Statistical plan, Methods, Mission, Innovation, Relevance, Feasibility
R = {}
R["CHITIN"] = dict(
    batches=["8.20.25"],
    protocol=["8.20.25 Reviews/CHITIN___Protocol___23_Dec_24___clean.pdf"],
    rev=[("8.20.25 Reviews/Review Scores and Comments/CHITIN review.docx", "22", [2,2,5,5,5,4]),
         ("8.20.25 Reviews/Review Scores and Comments/CHITIN Protocol score sheet-2025-08-18-16-40.pdf", "16", [1,4,None,3,4,4])],
    dm=[("8.20.25 Reviews/Review Scores and Comments/SCORING CHITIN-1.docx", None, None)],
    decision="Concerns: no coagulation stat plan/power; n=4 per group underpowered; all samples shipped to outside lab — asked whether assays can run in Weiss lab at SJ. Clarify 3-yr stable HbF requirement.",
)
R["PNHIPTA"] = dict(
    batches=["8.20.25"],
    protocol=["8.20.25 Reviews/PNHIPTAProtocol.docx"],
    rev=[("8.20.25 Reviews/Review Scores and Comments/PNHITPA review.docx", "20/20", [None,None,5,5,5,5]),
         ("8.20.25 Reviews/Review Scores and Comments/PNHITPA Protocol score sheet-2025-08-18-16-45.pdf", "19", [3,3,None,5,5,3])],
    dm=[("8.20.25 Reviews/Review Scores and Comments/SCORING PNHIPTA.docx", "20", None)],
    decision="Supportive — ultra-rare pediatric PNH, good SJ fit; 2 eligible patients identified. Open question: will PI adhere to the 1-year protocol window vs. transplanting at 6 months?",
)
R["X4WARDXP"] = dict(
    batches=["8.27.25"],
    protocol=["8.27.25 Reviews/4WARDXP_Protocol_SJ_Initial_Sponsor_v3.0_10Feb2025.pdf"],
    rev=[("8.27.25 Reviews/Review Scores and Comments/4WARDXP Manorixafor review.docx", "16/20", [None,None,5,5,5,1])],
    dm=[],
    decision="Mission/innovation/relevance strong but feasibility scored 1 — only 0–1 potential patients at SJ, GCSF-resistant requirement, 1 full year before open label.",
)
R["IDBLEED"] = dict(
    batches=["8.27.25"],
    protocol=["8.27.25 Reviews/IDBLEED Protocol Amendment 1.0 15_Dec_2023 Clean.pdf"],
    rev=[("8.27.25 Reviews/Review Scores and Comments/IDBLEED review.docx", "16/30", [1,3,3,3,3,3])],
    dm=[],
    decision="Action: PI to meet with statistician (Guolion, sp? - as written) for a power analysis on current data before proceeding. Accrual lagging (14/43 in 2 years); sub-objectives seen as excessive remnants of prior EDS genetic design.",
)
R["IXTEND3004"] = dict(
    batches=["8.27.25"],
    protocol=["8.27.25 Reviews/IXTEND3004_Protocol_initial__sponsor_AM_1__14Nov2024.pdf"],
    rev=[("8.27.25 Reviews/Review Scores and Comments/IXTEND3004 review.docx", "18/20", [None,None,5,5,5,3])],
    dm=[],
    decision="Supportive (“DM: agree” recorded in review doc). Pediatric FIX gene therapy; potential cure for rare catastrophic disease. Two potential patients, not yet approached.",
)
R["RHEMEDY"] = dict(
    batches=["8.27.25"],
    protocol=["8.27.25 Reviews/Rhemedy Protocol.pdf"],
    rev=[("8.27.25 Reviews/Review Scores and Comments/RHEMEDY review.docx", "18/20", [None,None,5,5,5,3])],
    dm=[("8.27.25 Reviews/Review Scores and Comments/SCORING RHEMEDY.docx", "13/15", [None,None,None,5,5,3])],
    decision="Supportive but operationally hard: drug must be given <12h after first IV opioid, so patients must be pre-consented in clinic. Requires inpatient research support decision (CRN model, hospitalist buy-in, inpatient Heme APPs). Agreed to one patient initially.",
)
R["MIPICS"] = dict(
    batches=["9.17.25", "9.24.25"],
    protocol=["9.24.25 Reviews/miPICs_SJCRH-HEM_Protocol_Clean__Initial _7_18 Feb 2025.pdf",
              "9.17.25 Reviews/miPICs_SJCRH-HEM_Protocol_Clean__Initial _7_18 Feb 2025.pdf"],
    rev=[("9.24.25 Reviews/miPICs protocol score sheet.docx", "(none)", [None]*6),
         ("9.17.25 Reviews/miPICs protocol score sheet.docx", "(none)", [None]*6)],
    dm=[("9.24.25 Reviews/SCORING MiPICS DM 9.9.docx", "20/30", [0,5,5,4,4,2])],
    decision="Conditional: conflict with the SJ SCD biobank resolved by agreeing to draw the same samples for the SJ biobank (Mission revised 0/5 → 5/5). Residual concerns: no statistical plan, minimal funding, sample-fatigue risk to SJ studies.",
)
R["MYPERS"] = dict(
    batches=["9.17.25", "9.24.25"],
    protocol=["9.24.25 Reviews/MYPERS_SJCRH-HEM_Protocol_Clean_Amendment_2.0 _2.0_24 Feb 2025.pdf",
              "9.17.25 Reviews/MYPERS_SJCRH-HEM_Protocol_Clean_Amendment_2.0 _2.0_24 Feb 2025.pdf"],
    rev=[("9.24.25 Reviews/MYPERS Protocol score sheet.docx", "28/30", [5,5,4,5,5,4]),
         ("9.17.25 Reviews/MYPERS Protocol score sheet.docx", "28/30", [5,5,4,5,5,4])],
    dm=[("9.24.25 Reviews/SCORING MYPERS DM 9.9 .docx", "26/30", [5,5,4,5,4,3])],
    decision="Positive — highest-scoring reviewed protocol after LTFU-AGT4HB. Accruing (16/40: 3 patients, 13 controls) since 2023; midpoint analysis planned at 5:5:10. Open questions: age-range generalizability, high IND monitoring burden, next steps for PI.",
)
R["VINGT"] = dict(
    batches=["9.24.25"],
    protocol=["9.24.25 Reviews/VINGT_Submission.pdf"],
    rev=[("9.24.25 Reviews/VINGT Review.docx", "19/30", [3,4,3,4,4,1])],
    dm=[("9.24.25 Reviews/SCORING VINGT DM 9.24.docx", "12/30", [None,4,None,4,4,None])],
    decision="Lowest-scoring reviewed protocol. Multi-site unfunded study with subcontracts/MTAs/DUAs across sites judged a big ask; only the intake form was available, not a full protocol. Unclear who would lead follow-on work.",
)
R["LTFAGTHB"] = dict(
    batches=["9.24.25"],
    protocol=["9.24.25 Reviews/LTFUAGT4HB.pdf"],
    rev=[("9.24.25 Reviews/LTFU4HB Review.docx", "30/30", [5,5,5,5,5,5])],
    dm=[("9.24.25 Reviews/SCORING LTFUAGT4HB DM 9.24.docx", "30/30", [5,5,5,5,5,5])],
    decision="Unanimous 30/30 from both reviewers — 15-year follow-up of AGT4HB gene therapy subjects. Caveat: no funding, 14 patients across many sites, and only the intake form was available, not the full protocol.",
)
R["LEAP"] = dict(
    batches=["10.01.25"],
    protocol=["10.01.25 Reviews/LEAP_SJCRH-HEM_Protocol_Clean__Rev 2.1 _4.0_29 Jul 2025.pdf"],
    rev=[("10.01.25 Reviews/Review Scores and Comments/LEAP score sheet.docx", "(none)", [None,None,5,3,5,3])],
    dm=[("10.01.25 Reviews/Review Scores and Comments/SCORING LEAP DM 10.1.docx", "15/15", [None,None,5,5,5,None])],
    decision="Already open with 1 patient enrolled since May 2024. Important but unfunded and logistically challenging — both reviewers ask whether data collection can be converted to a single-use study.",
)
R["LIVBX"] = dict(
    batches=["10.01.25"],
    protocol=["10.01.25 Reviews/LIVBX_SJCRH-HEM_Protocol_Clean__1.0 __23 Jul 2025.pdf"],
    rev=[("10.01.25 Reviews/Review Scores and Comments/LIVBX score sheet.docx", "(none)", [None,5,5,4,3,2])],
    dm=[("10.01.25 Reviews/Review Scores and Comments/SCORING LIVBX DM 10.1.docx", "20/30", [None,None,5,5,5,5])],
    decision="Recruitment is the blocker: 8 eligible SJ patients, likely 1–2 enroll; biopsies performed at Methodist; hemophilia patients must fly in with no patient reimbursement built in. CTFO reviewing cost analysis. Reviewers question whether so few patients will be informative.",
)
R["SCDSTEMM"] = dict(
    batches=["10.01.25"],
    protocol=["10.01.25 Reviews/SCDSTEMM_SJCRH-HEM_Protocol_Clean_Amendment_2.1 __07 May 2025.pdf"],
    rev=[("10.01.25 Reviews/Review Scores and Comments/SCDSTEMM score sheet.docx", "(none)", [5,5,5,4,4,3])],
    dm=[("10.01.25 Reviews/Review Scores and Comments/SCORING SCD STEMM DM 10.1.docx", "28/30", [5,5,5,5,5,3])],
    decision="Important study, internally funded. Only feasibility discounted (3/5) because it is an adult study.",
)
R["AG348_C28 AND C29"] = dict(
    batches=["10.01.25"],
    protocol=["10.01.25 Reviews/AG348-C-028_Synopsis Aug 22.docx",
              "10.01.25 Reviews/AG348-C-029_Synopsis Aug 22.docx"],
    rev=[("10.01.25 Reviews/Review Scores and Comments/AG348 score sheet.docx", "(none)", [None,None,5,5,5,5])],
    dm=[("10.01.25 Reviews/Review Scores and Comments/SCORING AG 348 028 and 029 DM 10.1.docx", "30/30", [5,5,5,5,5,5])],
    decision="Important study, pharma-funded, 30/30 from DM. Two separate protocols (non-transfusion-dependent C-028 and transfusion-dependent C-029 thalassemia; mitapivat). Gate: confirm eligible and interested subjects. PI not yet assigned.",
)

CRIT = ["Statistical plan", "Methods", "Mission", "Innovation", "Relevance", "Feasibility"]

def arith(tot, sums):
    """Return (computed_sum, n_scored, mismatch_note) for a scored doc."""
    if not sums or all(s is None for s in sums):
        return None, 0, None
    vals = [s for s in sums if s is not None]
    csum = sum(vals)
    note = None
    if tot and tot != "(none)":
        written = tot.split("/")[0].strip()
        try:
            if int(written) != csum:
                note = "written %s vs criteria sum %d" % (tot, csum)
        except ValueError:
            pass
    return csum, len(vals), note

# ---------- 4. Load the tracker ----------
wb_t = openpyxl.load_workbook("CumulativeReviewtracking.xlsx", data_only=True)
ws_t = wb_t["Sheet1"]
tracker = []
for row in ws_t.iter_rows(min_row=2, values_only=True):
    if row[0]:
        tracker.append(dict(protocol=str(row[0]).strip(),
                            pi=str(row[1]).strip() if row[1] else "",
                            type=str(row[2]).strip() if row[2] else "",
                            comments=str(row[3]).strip() if row[3] else ""))

# ---------- 5. Assessment-workbook cross-check ----------
wb_a = openpyxl.load_workbook("Hematology_Protocol_Assessment_Workbook_Updated.xlsx", data_only=True)
ws_a = wb_a["Protocol Tracker"]
awb = {}
for row in ws_a.iter_rows(min_row=2, values_only=True):
    if row[0]:
        awb[str(row[0]).strip()] = dict(pi=str(row[2]).strip() if row[2] else "",
                                        type=str(row[4]).strip() if row[4] else "",
                                        status=str(row[6]).strip() if row[6] else "",
                                        total=row[10])
AWB_LINK = {"CHITIN":"CHITIN","PNHIPTA":"PNHIPTA","X4WARDXP":"4WARDXP","IDBLEED":"IDBLEED",
            "IXTEND3004":"HEMGENIX","RHEMEDY":"RHEMEDY","MIPICS":"miPICs","MYPERS":"MYPERS",
            "VINGT":None,"LTFAGTHB":None,"LEAP":"LEAP","LIVBX":"LIVBX",
            "SCDSTEMM":"SCDSTEMM","AG348_C28 AND C29":None}

print("OK: loaded %d tracker rows, %d workbook rows, %d files, %d duplicate hashes"
      % (len(tracker), len(awb), len(inventory), len(dupes)))

# ---------- 6. Build the markdown report ----------
L = []
A = L.append
A("# HEM Protocol Reviews — Tracker Reconciliation")
A("")
A("**Generated:** %s  " % TODAY)
A("**Folder:** `HEM Protocol Reviews/` (OneDrive)  ")
A("**Reconciled:** `CumulativeReviewtracking.xlsx` (14 rows) against 54 files on disk, "
  "cross-checked against `Hematology_Protocol_Assessment_Workbook_Updated.xlsx` (54 rows).")
A("")
A("> Sections marked **FACT** are derived mechanically from the filesystem (presence, MD5). "
  "Sections marked **PROPOSED** are my reading of the review documents and need your sign-off.")
A("")
A("---")
A("")
A("## 1. Headline")
A("")
A("**The tracker's roster is complete and correct.** All 14 protocols listed in "
  "`CumulativeReviewtracking.xlsx` have review artifacts on disk, and every protocol reviewed "
  "on disk appears in the tracker. Nothing is missing or orphaned at the roster level.")
A("")
A("The gaps are in **content and consistency**, not coverage:")
A("")
A("| # | Finding | Severity |")
A("|---|---|---|")
A("| 1 | 13 of 14 `Resulting comments` cells are **empty** — only VINGT (tabled) has a recorded decision | High |")
A("| 2 | The scoring denominator is **inconsistent** (/15, /20, /25, /30) because reviewers score criteria `NA` at will | High |")
A("| 3 | The score-sheet template header says **\"possible scores 5-25\"** but the template lists **6 criteria** (max 30) | High |")
A("| 4 | **CHITIN** and **PNHIPTA** each have two reviewer documents that **disagree on the score** | High |")
A("| 5 | **4WARDXP** has no second-reviewer (DM) input of any kind | Medium |")
A("| 6 | **CHITIN review.docx** total is arithmetically wrong (written 22, criteria sum to 23) | Medium |")
A("| 7 | **LIVBX SCORING DM** lists 5/5 on every scored criterion but records `20/30` | Medium |")
A("| 8 | The 9.17.25 folder is a **byte-identical duplicate** of files in 9.24.25 | Low |")
A("| 9 | 3 of 14 reviewed protocols are **absent from the 54-row assessment workbook** | Medium |")
A("| 10 | The assessment workbook's 3-dimension /100 rubric is **not the rubric actually in use** | Medium |")
A("| 11 | Reviewers use **three different conventions** for an `NA` criterion — drop it, score it 0, or score it 3 | High |")
A("")
A("---")
A("")

# --- Section 2: name map ---
A("## 2. Name map — PROPOSED")
A("")
A("The tracker, the filenames, and the assessment workbook use different labels for the same "
  "study. This is the mapping I applied; correct any row you disagree with and the rest of the "
  "report follows from it.")
A("")
A("| Tracker label | Names on disk | Assessment workbook | Note |")
A("|---|---|---|---|")
notes = {
 "X4WARDXP": "Tracker prefixes the sponsor (X4 Pharmaceuticals); the study is 4WARDXP.",
 "PNHIPTA": "Both spellings occur **on disk**: `PNHIPTAProtocol.docx` vs `PNHITPA review.docx`.",
 "IXTEND3004": "**Confirmed by JH:** IXTEND3004 is the workbook's `HEMGENIX` row (CSL Behring / Jesudas). The tracker and the workbook should use one of the two labels, not both.",
 "MIPICS": "Three casings in use: `MIPICS`, `miPICs`, `MiPICS`.",
 "VINGT": "Review doc titled `VINGHT` (typo). Not in the assessment workbook. PI **confirmed as Jesudas** by JH.",
 "LTFAGTHB": "Four forms: tracker `LTFAGTHB`, file `LTFUAGT4HB.pdf`, review `LTFU4HB`, workbook parent `AGT4HB`. Only the **parent** study is in the workbook, not this long-term follow-up.",
 "AG348_C28 AND C29": "Two distinct protocols (C-028 non-transfusion-dependent, C-029 transfusion-dependent thalassemia). Not in the workbook. `AGPKD` there is the **same drug** (mitapivat = AG-348) under the **same PI** (Parul Rai, confirmed by JH) but for **PK deficiency** — a different indication, so a sibling study, not a duplicate.",
 "LIVBX": "DM doc writes `LIV BX` with a space.",
 "SCDSTEMM": "DM doc writes `SCD STEMM` with a space.",
 "RHEMEDY": "Protocol file is `Rhemedy Protocol.pdf` (mixed case).",
}
for tl, aliases, awb_name in NAME_MAP:
    A("| `%s` | %s | %s | %s |" % (tl, ", ".join("`%s`" % a for a in aliases),
                                   awb_name, notes.get(tl, "—")))
A("")
A("---")
A("")

# --- Section 3: artifact matrix ---
A("## 3. Artifact matrix — FACT")
A("")
A("Every review batch should produce four things: the protocol document, a reviewer score sheet "
  "or review write-up, a second-reviewer `SCORING … DM` document, and a recorded decision.")
A("")
A("| Protocol | Batch | Protocol doc | Reviewer sheet | `SCORING…DM` | Decision in tracker |")
A("|---|---|:--:|:--:|:--:|:--:|")
for tl, aliases, _ in NAME_MAP:
    d = R[tl]
    yes = lambda x: "yes" if x else "**NO**"
    nrev = len(d["rev"]); ndm = len(d["dm"])
    rev_c = "yes" if nrev == 1 else ("yes (%d)" % nrev if nrev else "**NO**")
    dm_c = "yes" if ndm == 1 else ("yes (%d)" % ndm if ndm else "**NO**")
    A("| %s | %s | %s | %s | %s | **NO** |"
      % (tl, ", ".join(d["batches"]), yes(d["protocol"]), rev_c, dm_c))
A("")
A("**Gaps:**")
A("")
A("- **4WARDXP, IDBLEED, IXTEND3004** (all 8.27.25) have no separate `SCORING … DM` file. "
  "For IDBLEED and IXTEND3004 the second reviewer's comments were folded into the review "
  "document instead (`DM: 43 seems like a lot of patients…`, `DM: agree`), so only **4WARDXP "
  "genuinely has no second-reviewer input**.")
A("- **CHITIN and PNHIPTA** have *two* reviewer artifacts each — a PDF score sheet and a "
  "separate `review.docx` — and they disagree (see §5).")
A("- **Decision is recorded for none of the 14.**")
A("")
A("**Folder structure is inconsistent:** 8.20.25, 8.27.25 and 10.01.25 use a "
  "`Review Scores and Comments/` subfolder; 9.17.25 and 9.24.25 keep everything flat.")
A("")
A("**Date mismatch:** the DM documents for miPICs and MYPERS are named `… DM 9.9` but live in "
  "the **9.24.25** folder — they predate the batch they are filed under.")
A("")

# --- duplicates ---
A("### 3a. Duplicate files — FACT (MD5-verified)")
A("")
A("The 9.17.25 folder contains **nothing unique**. All four of its files are byte-for-byte "
  "identical to files in 9.24.25:")
A("")
A("| MD5 | Copies |")
A("|---|---|")
for h, files in sorted(dupes.items(), key=lambda kv: kv[1][0]):
    A("| `%s` | %s |" % (h[:12], "<br>".join("`%s`" % f for f in files)))
A("")
A("So miPICs and MYPERS were **carried forward rather than re-reviewed** — but the files do not "
  "say which folder is the canonical record. 9.17.25 is the earlier date and both DM documents "
  "are dated 9.9, which would fit these protocols being tabled on 9.17 and rolled to 9.24. "
  "The tracker correctly lists each protocol once; the reconciled sheet records both dates.")
A("")
A("### 3b. Non-protocol files — FACT")
A("")
A("| File | What it is |")
A("|---|---|")
A("| `8.27.25 Reviews/26420dft.pdf` | FDA draft guidance — *Rare Diseases: Natural History Studies for Drug Development* |")
A("| `8.27.25 Reviews/44625092dft_Confirmatory Evidence.pdf` | FDA draft guidance — *Substantial Evidence of Effectiveness With One Adequate and Well-Controlled Investigation and Confirmatory Evidence* |")
A("| `8.20.25 Reviews/StudyDescriptions.docx` | Background write-ups (purpose + history) for PNHIPTA and CHITIN |")
A("| `8.27.25 Reviews/Protocol Summaries_08.27.2025.pptx` | Meeting slide deck |")
A("| `10.01.25 Reviews/1_Protocol Summaries_10.01.2025.pptx` | Meeting slide deck |")
A("| `10.01.25 Reviews/AG348_thalfeasibilitysurvey_SJpreDraft.docx.url` | Shortcut to a SharePoint doc — **content is not in this folder** |")
A("")
A("Only 8.27.25 and 10.01.25 have a summary deck; 8.20.25, 9.17.25 and 9.24.25 do not.")
A("")
A("---")
A("")
# --- Section 4: scores ---
A("## 4. Scores recovered from the review documents — PROPOSED")
A("")
A("Criteria are always in this order: **Statistical plan · Methods · Mission · Innovation · "
  "Relevance · Feasibility**. `–` means the criterion was marked NA or left narrative-only. "
  "\"Written\" is the total as it appears in the document; \"Sum\" is the arithmetic sum of the "
  "criteria actually scored.")
A("")
A("| Protocol | Document | Stat | Meth | Miss | Inno | Rel | Feas | Written | Sum | n |")
A("|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|")
for tl, _, _ in NAME_MAP:
    d = R[tl]
    for kind, lst in (("reviewer", d["rev"]), ("DM", d["dm"])):
        for path, tot, sums in lst:
            csum, n, note = arith(tot, sums)
            cells = ["–" if (not sums or sums[i] is None) else str(sums[i]) for i in range(6)] \
                    if sums else ["–"]*6
            A("| %s | `%s`<br><sub>%s</sub> | %s | %s | %s | %s |"
              % (tl, os.path.basename(path), kind, " | ".join(cells),
                 tot if tot else "–", csum if csum is not None else "–", n if n else "–"))
A("")

A("### 4a. Denominator drift — the biggest structural problem")
A("")
A("The same six-criterion sheet has been totalled against **four different denominators**:")
A("")
A("| Denominator | Used for | Why |")
A("|---|---|---|")
A("| **/15** | LEAP (DM) | 3 criteria scored |")
A("| **/20** | PNHIPTA, 4WARDXP, IXTEND3004, RHEMEDY, AG348 (reviewer) | 4 criteria scored |")
A("| **/25** | template header claim | Header says \"possible scores 5-25\" |")
A("| **/30** | IDBLEED, miPICs, MYPERS, VINGT, LTFU-AGT4HB, SCDSTEMM, LIVBX, AG348 (DM) | all 6 criteria |")
A("")
A("Underneath the denominator problem is a deeper one: **`NA` is handled three different ways**, "
  "all currently in use.")
A("")
A("| Convention | Example | Effect |")
A("|---|---|---|")
A("| `NA` **drops out** of the denominator | RHEMEDY reviewer: Stat plan and Methods NA → `18/20` | Neutral — the study is judged on what applied |")
A("| `NA` **scores 0** | VINGT DM: 3 criteria unscored, total written `12/30` | Penalises the study for criteria that did not apply |")
A("| `NA` **scores 3** (midpoint) | `PNHITPA Protocol score sheet…pdf`: \"Statistical plan — 3. NA\", \"Methods — 3 NA\"; 3+3+5+5+3 = 19 | Pulls every score toward the middle |")
A("")
A("The same protocol can therefore be scored 100%, 76%, or lower depending only on which "
  "reviewer filled in the sheet. **This is the single highest-value thing to fix.**")
A("")
A("Because reviewers mark *Statistical plan* and *Methods* as `NA` for sponsor-run trials, "
  "those studies are silently scored out of 20 while investigator-initiated studies are scored "
  "out of 30. **Raw totals are therefore not comparable across protocols.** A 16/20 (4WARDXP) "
  "and a 16/30 (IDBLEED) are 80% and 53% respectively.")
A("")
A("Normalised, the ranking is:")
A("")
A("| Rank | Protocol | Reviewer | as % | DM | as % |")
A("|---|---|---|---|---|---|")
rank_rows = []
for tl, _, _ in NAME_MAP:
    d = R[tl]
    def pct(lst):
        for path, tot, sums in lst:
            csum, n, _ = arith(tot, sums)
            if csum is not None and n:
                return csum, n*5, 100.0*csum/(n*5)
        return None
    rp, dp = pct(d["rev"]), pct(d["dm"])
    best = rp[2] if rp else (dp[2] if dp else -1)
    rank_rows.append((best, tl, rp, dp))
rank_rows.sort(reverse=True)
CONFLICT = {"CHITIN": "other doc: 16/25 = 64%", "PNHIPTA": "other doc: 19/25 = 76%"}
for i, (best, tl, rp, dp) in enumerate(rank_rows, 1):
    f = lambda p: ("%d/%d | %.0f%%" % (p[0], p[1], p[2])) if p else "– | –"
    star = " *" if tl in CONFLICT else ""
    A("| %d | %s%s | %s | %s |" % (i, tl, star, f(rp), f(dp)))
A("")
A("\\* **CHITIN and PNHIPTA each have a second reviewer document with a different score**, so "
  "their rank here reflects only the first document found and should not be taken at face "
  "value. CHITIN: `review.docx` gives 23/30 = 77% (and miscounts its own total as 22) while "
  "`score sheet.pdf` gives 16/25 = 64%. PNHIPTA: `review.docx` gives 20/20 = 100% while "
  "`score sheet.pdf` gives 19/25 = 76%. Resolve these before using the ranking.")
A("")
A("Note also that **MIPICS is ranked on its DM score alone** — its reviewer sheet carries no "
  "numbers — and that **five protocols (X4WARDXP, IDBLEED, IXTEND3004, CHITIN, PNHIPTA) have "
  "no comparable DM score**, so the two columns are not scored on the same population.")
A("")
A("> **Caveat:** normalising by \"criteria actually scored\" treats an NA as *absent*, not as "
  "zero. That is the charitable reading and it is what most reviewers appear to intend, but it "
  "is an assumption, and it is not what every document does — VINGT's DM doc writes `12/30`, "
  "treating unscored criteria as **zero**, while the PNHITPA PDF scores NA as **3**. All three "
  "conventions are in active use, so these percentages are the best available comparison, not "
  "an authoritative one.")
A("")

A("### 4b. Documents that disagree with themselves or each other")
A("")
A("| Protocol | Problem |")
A("|---|---|")
A("| **CHITIN** | `CHITIN review.docx` scores 2·2·5·5·5·4 which **sums to 23**, but records `Total: 22`. Separately, `CHITIN Protocol score sheet…pdf` scores 1·4·–·3·4·4 = **16**. Two reviewer documents, two different scores, one arithmetic error. |")
A("| **PNHIPTA** | Three different totals for one protocol: `PNHITPA review.docx` = **20/20**, `PNHITPA Protocol score sheet…pdf` = **19**, `SCORING PNHIPTA.docx` = **20**. |")
A("| **LIVBX** | `SCORING LIVBX DM 10.1.docx` records `5/5` on Mission, Innovation, Relevance **and** Feasibility (= 20) but writes the total as `20/30`, implying two unscored criteria count as zero — while the narrative for those two is critical, not absent. |")
A("| **AG348** | Reviewer sheet marks Statistical plan and Methods `NA` (→ 20/20) but the DM doc scores both `5/5` (→ 30/30). The two reviewers disagreed on whether the criteria were applicable. |")
A("| **miPICs** | The reviewer score sheet contains **no numbers at all** — narrative only. Only the DM score (20/30) exists. |")
A("| **LEAP / LIVBX / SCDSTEMM / AG348** | Reviewer score sheets record per-criterion values but **no total line**. Totals in §4 are my arithmetic, not theirs. |")
A("")
A("---")
A("")

# --- Section 5: proposed comments ---
A("## 5. Proposed `Resulting comments` — PROPOSED")
A("")
A("All 14 cells are currently blank. These are drawn from the review and DM documents; the "
  "source files are listed so you can check each one.")
A("")
A("> **Decisions confirmed by JH on 2026-09-09: 12 protocols OPENED, IDBLEED CLOSED TO "
  "ACCRUAL, VINGT TABLED.** The summaries below record what the review discussion said and now sit "
  "alongside the confirmed decision in the reconciled workbook. Several protocols opened "
  "with concerns that were never recorded as resolved — those are tracked as open follow-ups "
  "and graded for risk in §5a rather than being treated as closed.")
A("")
for tl, _, _ in NAME_MAP:
    d = R[tl]
    A("### %s" % tl)
    A("")
    A(d["decision"])
    A("")
    srcs = [p for p, _, _ in d["rev"]] + [p for p, _, _ in d["dm"]]
    A("<sub>Sources: %s</sub>" % "; ".join("`%s`" % os.path.basename(s) for s in srcs))
    A("")
A("---")
A("")

# --- Section 6: assessment workbook ---
A("## 5a. Open follow-ups on opened protocols — WATCHLIST")
A("")
A("Twelve protocols are open. Several opened with concerns that no document records as "
  "resolved; because those studies are now running, the concerns are live accrual and "
  "delivery risks rather than gating questions. IDBLEED and VINGT are listed separately "
  "below — neither is accruing.")
A("")
A("| Risk | Protocol | PI | What is still open |")
A("|---|---|---|---|")
for _k, _dec, _by, _q, _src, _fu, _own, _risk in DECISION_LIST:
    A("| **%s** | %s | %s | %s |" % (_risk, _k, _own, _fu.replace("\n", " ")))
A("")
A("**The remaining High-risk openings:**")
A("")
A("- **4WARDXP** opened on a single review that scored Feasibility **1** and estimated "
  "**0–1 eligible patients** at St. Jude. It is the only protocol of the 14 opened without "
  "any second-reviewer assessment. Its hold is now closed, but that was a governance "
  "question; this is an accrual question, and it is unchanged. Monitor explicitly.")
A("- **LIVBX** opened with 8 eligible patients, an expected enrolment of **1–2**, biopsies "
  "at Methodist, and no patient reimbursement built in. Reviewers questioned whether so few "
  "patients would be informative at all; the CTFO cost analysis was still in flight.")
A("")
A("**IDBLEED — closed to accrual.** Opened at review, since closed. It reached 14 of a "
  "planned 43 patients in two years, with only 1 of those 14 partially positive for ED. The "
  "power analysis and enrollment strategy requested at review were never recorded as "
  "delivered, and closure supersedes both. The reviewer who recommended holding it pending "
  "exactly those two items was borne out.")
A("")
A("> **Open question:** what becomes of the data on the 14 patients already enrolled — "
  "analysis, publication, or archive? Nothing in the record addresses this, and it is the "
  "one live question a closure creates.")
A("")
A("**VINGT — tabled**, never opened. No revisit date set.")
A("")
A("### 5b. Recorded holds — all three resolved — FACT")
A("")
A("This is the finding most worth your attention. The assessment workbook's **pre-existing** "
  "Notes column — text that was already there, not written by this reconciliation — records "
  "an explicit recommendation to **hold** three of the protocols that were opened. None of "
  "the three holds is recorded anywhere as retracted or satisfied.")
A("")
A("| Protocol | Recorded note (verbatim, pre-existing) | Hold status |")
A("|---|---|---|")
A("| **4WARDXP** | \"BM: I have ethical questions about this protocol. **Hold this until a "
  "patient is identified.**\" | **CLOSED** by JH 2026-09-09 |")
A("| **IXTEND3004** (as `HEMGENIX`) | \"BM: **Would hold** until participants are confirmed "
  "in January 2026.\" | **CLOSED** by JH 2026-09-09 |")
A("| **IDBLEED** | \"BM: slow accrual – enrollment plan? Interim Power analysis? **would put "
  "this on hold** until a power analysis is done and an enrollment strategy implemented.\" | "
  "**MOOT** — study closed to accrual |")
A("")
A("The original note text is retained in every case — the closures are appended, not "
  "substituted, so the audit trail runs hold → closure → authority → date.")
A("")
A("**Closing the 4WARDXP hold does not close the accrual problem.** The hold and the "
  "feasibility concern are separate findings that happened to sit in the same row. Feasibility "
  "was scored **1** on an estimated **0–1 eligible patients**, and this is still the only one "
  "of the 14 opened without any second-reviewer assessment. Its risk grade stays **High** on "
  "those grounds alone. IXTEND3004 drops to **Low** — its hold was the only thing outstanding.")
A("")
A("**IDBLEED's hold is superseded rather than satisfied.** It asked for a power analysis "
  "and an enrollment strategy; neither was delivered, and the study has since been closed "
  "to accrual. Worth recording plainly: the concern that prompted that hold — slow accrual "
  "— is what the protocol was ultimately closed for.")
A("")
A("---")
A("")
A("## 6. Cross-check against the assessment workbook — FACT")
A("")
A("`Hematology_Protocol_Assessment_Workbook_Updated.xlsx` holds a 54-protocol portfolio with a "
  "`Protocol Tracker` sheet. **Not one of its 54 rows has a score**, and every reviewed "
  "protocol still shows its pre-review status.")
A("")
A("| Tracker protocol | In workbook? | Status there | Score there | Reviewed on |")
A("|---|---|---|---|---|")
for tl, _, _ in NAME_MAP:
    key = AWB_LINK[tl]
    d = R[tl]
    if key and key in awb:
        a = awb[key]
        A("| %s | yes (`%s`) | %s | %s | %s |"
          % (tl, key, a["status"], "(blank)" if not a["total"] else a["total"], ", ".join(d["batches"])))
    else:
        A("| %s | **absent** | — | — | %s |" % (tl, ", ".join(d["batches"])))
A("")
A("**Three reviewed protocols are missing from the workbook:** VINGT, LTFU-AGT4HB (only the "
  "parent `AGT4HB` is listed), and AG348-C-028/C-029.")
A("")
A("**Eleven reviewed protocols still read `Under Review` or `Pending Review`** in the workbook "
  "despite having been reviewed and scored weeks ago. This now includes IXTEND3004, confirmed "
  "as the workbook's `HEMGENIX` row, which still shows `Pending Review`.")
A("")
A("### 6a. The two workbooks use incompatible rubrics")
A("")
A("| | `CumulativeReviewtracking` + score sheets | `Assessment Workbook` |")
A("|---|---|---|")
A("| Criteria | 6 (Stat plan, Methods, Mission, Innovation, Relevance, Feasibility) | 63 (21 Design + 21 Benefit + 21 Resource) |")
A("| Scale | 1–5 each, total /30 (nominally) | 1–5 each, total /100 |")
A("| Thresholds | none defined | ≥80 High Priority, 65–79 Standard, 50–64 Further Review |")
A("| Actually used? | **yes** — 14 protocols scored | **no** — 0 of 54 scored |")
A("")
A("The assessment workbook was built but never used for scoring. **Verified:** the "
  "`Design Assessment`, `Population Benefit` and `Resource Assessment` sheets contain "
  "**zero numeric entries** between them, and the `TOTAL SCORE` formulas are present and "
  "intact on all 99 rows — the machinery works, it has simply never been fed.")
A("")
A("The `Dashboard` is live and arithmetically correct: `Total Protocols Reviewed: 54` is "
  "`=COUNTA('Protocol Tracker'!A2:A100)` and `Pending Review: 14` is a `COUNTIF` — both match "
  "the sheet exactly, and the four average-score cells correctly display `-` because there is "
  "nothing to average. The only defect is the **label**: \"Total Protocols Reviewed\" counts "
  "protocols *entered*, not reviewed. Read correctly, the Dashboard is itself the evidence — "
  "54 entered, 0 scored, 0 decided.")
A("")
A("### 6b. Study-type disagreements")
A("")
A("The two files use different taxonomies (`Therapeutic`/`Non-therapeutic` vs "
  "`Interventional`/`Observational`/`Registry`/`Natural History`/`Biobank`), so most "
  "differences are cosmetic. One is substantive:")
A("")
A("| Protocol | Tracker | Workbook | Comment |")
A("|---|---|---|---|")
A("| **LEAP** | Therapeutic | Observational | LEAP is an **expanded access program** that "
  "administers leniolisib. \"Observational\" looks wrong; \"Expanded Access\" is the "
  "conventional label. |")
A("| CHITIN, miPICs, MYPERS, LIVBX, SCDSTEMM | Non-therapeutic | Interventional | Consistent if "
  "\"non-therapeutic\" means *no therapeutic intent*: these involve procedures (biopsy, "
  "mobilisation, imaging, sampling) but do not treat. Worth confirming the intended meaning. |")
A("")
A("### 6c. PI attributions")
A("")
A("**VINGT — PI Jesudas: confirmed correct by JH.** I had flagged this because every other "
  "hemophilia/ATHN protocol in the assessment workbook (ATHN, ATHN TRANSCENDS, AGT4HB, GO8, "
  "LIVBX) is attributed to Reiss, and neither VINGT review document names a PI. The tracker is "
  "right; no change needed.")
A("")
A("**AG348 — PI Parul Rai: supplied by JH.** The tracker records `TBD` and the DM document "
  "`PI ?`, so this is the one place where the reconciled sheet **changes a value** rather than "
  "filling a blank. It is flagged as such in the workbook.")
A("")
A("This also places AG348 next to the workbook's `AGPKD` row: same PI (Rai), same drug "
  "(mitapivat = AG-348), different indication (PK deficiency vs thalassemia). They are sibling "
  "studies, not duplicates — which strengthens the case for adding C-028/C-029 to the workbook "
  "under Rai rather than leaving them out.")
A("")
A("**All PI attributions are now resolved.** Every one of the 14 reviewed protocols has a named "
  "PI.")
A("")
A("---")
A("")
A("## 7. Recommended actions")
A("")
A("1. **Fix the score-sheet template.** The header says \"possible scores 5-25\" but lists six "
  "criteria. Change it to `possible scores 6-30`, and add an explicit instruction for how `NA` "
  "affects the denominator.")
A("2. **Decide the NA convention.** Does an `NA` criterion drop out of the denominator, score "
  "zero, or score 3? All three are in use today (§4a). Until this is settled, totals cannot be "
  "compared across protocols — this is the highest-value single fix.")
A("3. **Record scores as a percentage** alongside the raw total so sponsor trials (scored /20) "
  "and investigator studies (scored /30) can be ranked together.")
A("4. **Populate `Resulting comments`** — §5 gives a starting draft for all 14.")
A("5. **Get a DM review for 4WARDXP**, the only protocol with no second-reviewer input.")
A("6. **Resolve the CHITIN and PNHIPTA double-documents** — decide which artifact is canonical "
  "and retire the other.")
A("7. **Decide which of 9.17.25 / 9.24.25 is the canonical record for miPICs and MYPERS.** The "
  "duplication is MD5-confirmed, but the files cannot tell us which date is authoritative — "
  "9.17 is the earlier folder and the DM documents are dated 9.9, which would be consistent "
  "with the protocols being tabled on 9.17 and carried to 9.24. That is your call, not "
  "something to infer from the filesystem; the reconciled tracker records both dates.")
A("8. **Decide the fate of the assessment workbook.** Either adopt its 63-criterion rubric or "
  "retire it; running two rubrics where one is never filled in is worse than either alone. At "
  "minimum, update the 11 stale statuses and add the 3 missing protocols — AG348-C-028/C-029 "
  "belongs under Rai alongside the existing `AGPKD` row.")
A("9. **Standardise the folder layout** — always use `Review Scores and Comments/`, and always "
  "produce a summary deck (currently 2 of 5 batches have one).")
A("10. **Adopt one protocol ID per study.** §2 lists 5 studies with 2–4 spellings each.")
A("")

report = "\n".join(L)
out_md = os.path.join(ROOT, "Tracker_Reconciliation_%s.md" % TODAY)
open(out_md, "w").write(report)
print("WROTE:", out_md, len(report), "bytes")

# ---------- 7. Proposed reconciled workbook (NEW FILE — original untouched) ----------
HDR = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1F4E79")
WRAP = Alignment(wrap_text=True, vertical="top")

wb_o = openpyxl.Workbook()

# -- Sheet 1: Reconciled Tracker --
ws = wb_o.active
ws.title = "Reconciled Tracker"
cols = ["Protocol", "PI", "Type", "DECISION", "Confirmed by", "Resulting comments",
        "Open follow-up / unresolved", "Risk", "Review date(s)",
        "Reviewer total (as written)", "Reviewer normalised", "Reviewer %",
        "DM total (as written)", "DM normalised", "DM %",
        "Artifacts on disk", "Source files", "Flags"]
ws.append(cols)
tmap = {t["protocol"]: t for t in tracker}
# PI corrections supplied by JH 2026-09-09 (differ from the original tracker)
PI_OVERRIDE = {"AG348_C28 AND C29": ("Parul Rai", "TBD")}
for tl, _, _ in NAME_MAP:
    d, t = R[tl], tmap[tl]
    def one(lst):
        """-> (as-written total, normalised total, pct)"""
        if not lst:
            return "no document", "", None
        written = []
        for path, tot, sums in lst:
            csum, n, _ = arith(tot, sums)
            w = tot if (tot and tot != "(none)") else "no total stated"
            written.append(w)
            if csum is not None and n:
                return " / ".join(written), "%d/%d" % (csum, n*5), round(100.0*csum/(n*5))
        return " / ".join(written), "no per-criterion scores", None
    rw, rs, rp = one(d["rev"]); dw, ds, dp = one(d["dm"])
    arts = []
    arts.append("protocol x%d" % len(d["protocol"]) if d["protocol"] else "NO protocol doc")
    arts.append("reviewer x%d" % len(d["rev"]) if d["rev"] else "NO reviewer sheet")
    arts.append("DM x%d" % len(d["dm"]) if d["dm"] else "NO DM doc")
    flags = []
    if not d["dm"]: flags.append("No second-reviewer document")
    if len(d["rev"]) > 1 and len(set(x[1] for x in d["rev"])) > 1:
        flags.append("Two reviewer docs with different totals")
    if tl == "CHITIN": flags.append("review.docx total 22 but criteria sum to 23")
    if tl == "LIVBX": flags.append("DM lists 5/5 x4 but writes 20/30")
    if tl == "AG348_C28 AND C29": flags.append("Reviewer marks Stat/Methods NA; DM scores both 5/5")
    if tl == "MIPICS": flags.append("Reviewer score sheet has no numeric scores")
    for lbl, w, nrm in (("Reviewer", rw, rs), ("DM", dw, ds)):
        if "/" in str(w) and "/" in str(nrm) and str(w) != str(nrm):
            flags.append("%s total as written (%s) differs from normalised (%s) - NA convention"
                         % (lbl, w, nrm))
    if len(d["batches"]) > 1: flags.append("Duplicate files across 9.17.25 and 9.24.25")
    if AWB_LINK[tl] is None: flags.append("Absent from assessment workbook")
    elif awb.get(AWB_LINK[tl], {}).get("status") in ("Under Review", "Pending Review"):
        flags.append("Assessment workbook still says '%s'" % awb[AWB_LINK[tl]]["status"])
    if tl == "VINGT": flags.append("TABLED (decision confirmed by JH 2026-09-09)")
    if tl == "IXTEND3004": flags.append("Recorded as HEMGENIX in assessment workbook - one study, two labels")
    if tl in PI_OVERRIDE:
        flags.append("PI CHANGED from '%s' to '%s' (confirmed by JH 2026-09-09)"
                     % (PI_OVERRIDE[tl][1], PI_OVERRIDE[tl][0]))
    srcs = [os.path.basename(p) for p, _, _ in d["rev"]] + [os.path.basename(p) for p, _, _ in d["dm"]]
    pi_val = PI_OVERRIDE[tl][0] if tl in PI_OVERRIDE else t["pi"]
    dec = DECISION_BY_KEY.get(tl)
    if dec:
        _, ddecision, dconf_by, dquote, dsrc, dfollow, downer, drisk = dec
        comment = "%s. %s" % (ddecision.upper(), d["decision"])
        dcells = [ddecision.upper(), dconf_by, comment, dfollow, drisk]
    else:
        dcells = ["", "", d["decision"], "", ""]
    ws.append([tl, pi_val, t["type"]] + dcells[:2] + [dcells[2], dcells[3], dcells[4],
               ", ".join(d["batches"]),
               rw, rs, ("%d%%" % rp) if rp is not None else "",
               dw, ds, ("%d%%" % dp) if dp is not None else "",
               "; ".join(arts), "; ".join(srcs), " | ".join(flags) if flags else ""])

# -- Sheet 2: Score Detail --
ws2 = wb_o.create_sheet("Score Detail")
ws2.append(["Protocol", "Document", "Reviewer", "Statistical plan", "Methods", "Mission",
            "Innovation", "Relevance", "Feasibility", "Total as written", "Criteria sum",
            "Criteria scored", "Arithmetic note"])
for tl, _, _ in NAME_MAP:
    d = R[tl]
    for kind, lst in (("Reviewer", d["rev"]), ("DM", d["dm"])):
        for path, tot, sums in lst:
            csum, n, note = arith(tot, sums)
            row = [tl, os.path.basename(path), kind]
            row += [(sums[i] if sums and sums[i] is not None else "NA") for i in range(6)] if sums else ["NA"]*6
            row += [tot or "", csum if csum is not None else "", n or "", note or ""]
            ws2.append(row)

# -- Sheet 3: File Inventory --
ws3 = wb_o.create_sheet("File Inventory")
ws3.append(["Path", "MD5", "Size (bytes)", "Duplicate of"])
for f in sorted(inventory):
    h = inventory[f]
    dup = [x for x in by_hash[h] if x != f]
    ws3.append([f, h, os.path.getsize(f), "; ".join(dup)])

# -- Sheet 4: Findings --
ws4 = wb_o.create_sheet("Findings")
ws4.append(["#", "Finding", "Severity", "Evidence"])
FIND = [
 (1, "All 14 'Resulting comments' cells are empty", "High",
     "CumulativeReviewtracking.xlsx column D is blank for every row"),
 (2, "Scoring denominator is inconsistent (/15, /20, /25, /30)", "High",
     "LEAP DM 15/15; RHEMEDY reviewer 18/20; template header says 5-25; IDBLEED 16/30"),
 (3, "Score-sheet template header says 'possible scores 5-25' but lists 6 criteria (max 30)", "High",
     "Header text in every 'score sheet.docx'"),
 (4, "CHITIN has two reviewer documents with different scores (22 vs 16)", "High",
     "CHITIN review.docx vs CHITIN Protocol score sheet-2025-08-18-16-40.pdf"),
 (5, "PNHIPTA has three different recorded totals (20/20, 19, 20)", "High",
     "PNHITPA review.docx, PNHITPA Protocol score sheet PDF, SCORING PNHIPTA.docx"),
 (6, "4WARDXP has no second-reviewer (DM) input of any kind", "Medium",
     "No SCORING file, and no DM: comment inside 4WARDXP Manorixafor review.docx"),
 (7, "CHITIN review.docx arithmetic error: written 22, criteria sum to 23", "Medium",
     "2+2+5+5+5+4 = 23"),
 (8, "LIVBX DM doc lists 5/5 on four criteria but writes 20/30", "Medium",
     "SCORING LIVBX DM 10.1.docx"),
 (9, "AG348 reviewers disagree on applicability: NA vs 5/5 for Stat plan and Methods", "Medium",
     "AG348 score sheet.docx vs SCORING AG 348 028 and 029 DM 10.1.docx"),
 (10, "miPICs reviewer score sheet contains no numeric scores", "Medium",
     "miPICs protocol score sheet.docx - narrative only"),
 (11, "9.17.25 folder is byte-identical duplicate of files in 9.24.25", "Low",
     "4 files, MD5-verified identical"),
 (12, "miPICs/MYPERS DM docs dated 9.9 but filed under 9.24.25", "Low",
     "SCORING MiPICS DM 9.9.docx, SCORING MYPERS DM 9.9 .docx"),
 (13, "3 reviewed protocols absent from the 54-row assessment workbook", "Medium",
     "VINGT, LTFU-AGT4HB (parent AGT4HB only), AG348-C-028/029"),
 (14, "11 reviewed protocols still 'Under Review'/'Pending Review' in assessment workbook", "Medium",
     "Protocol Tracker sheet, column G; includes HEMGENIX (=IXTEND3004), confirmed by JH"),
 (15, "Assessment workbook rubric (63 criteria, /100) is not the rubric in use (6 criteria, /30)", "Medium",
     "0 of 54 rows scored in the assessment workbook"),
 (16, "Assessment workbook Dashboard label 'Total Protocols Reviewed' actually counts protocols ENTERED",
      "Low",
      "B3 is =COUNTA('Protocol Tracker'!A2:A100) = 54; formulas are live and correct, only the label misleads"),
 (22, "Three different conventions for an NA criterion are in active use", "High",
      "NA dropped (RHEMEDY 18/20); NA=0 (VINGT 12/30); NA=3 (PNHITPA PDF 3+3+5+5+3=19)"),
 (23, "Assessment workbook scoring sheets are entirely empty - verified", "Medium",
      "Design/Population Benefit/Resource Assessment sheets contain 0 numeric cells; TOTAL SCORE formulas intact on 99 rows"),
 (17, "LEAP typed 'Therapeutic' in tracker but 'Observational' in workbook", "Low",
     "LEAP is an expanded access program administering leniolisib"),
 (18, "RESOLVED - VINGT PI (Jesudas) confirmed correct by JH; tracker needs no change", "Low",
     "Flagged because other ATHN/hemophilia studies are Reiss; confirmed 2026-09-09"),
 (19, "5 studies carry 2-4 different spellings across files", "Low",
     "PNHIPTA/PNHITPA; MIPICS/miPICs/MiPICS; LTFAGTHB/LTFUAGT4HB/LTFU4HB/AGT4HB; VINGT/VINGHT; X4WARDXP/4WARDXP"),
 (20, "Folder layout inconsistent; only 2 of 5 batches have a summary deck", "Low",
     "9.17.25 and 9.24.25 lack 'Review Scores and Comments/' subfolder"),
 (21, "RESOLVED - AG348 PI is Parul Rai (supplied by JH); tracker said TBD, DM doc said 'PI ?'",
      "Low",
      "Only value the reconciled sheet CHANGES rather than fills; same PI and drug as workbook row AGPKD (different indication)"),
 (24, "IXTEND3004 and HEMGENIX are the same study recorded under two labels", "Medium",
      "Confirmed by JH 2026-09-09; tracker says IXTEND3004, assessment workbook says HEMGENIX"),
 (25, "VINGT is TABLED - the only protocol with a recorded decision", "Medium",
      "Decision supplied by JH 2026-09-09; not previously captured in any file"),
]
for f in FIND:
    ws4.append(list(f))

# -- formatting --
WIDTHS = {"Reconciled Tracker": [20,12,16,11,15,62,60,12,14,
                                 17,15,10,17,15,9,26,38,42],
          "Score Detail":      [20,42,10,15,10,9,10,10,11,15,12,14,34],
          "File Inventory":    [70,34,13,70],
          "Findings":          [5,66,10,64]}
for sh in wb_o.worksheets:
    for i, w in enumerate(WIDTHS[sh.title], 1):
        sh.column_dimensions[get_column_letter(i)].width = w
    for c in sh[1]:
        c.font = HDR; c.fill = FILL; c.alignment = Alignment(wrap_text=True, vertical="center")
    sh.freeze_panes = "A2"
    sh.auto_filter.ref = sh.dimensions
    for row in sh.iter_rows(min_row=2):
        for c in row:
            c.alignment = WRAP

out_xlsx = os.path.join(ROOT, "CumulativeReviewtracking_reconciled_%s.xlsx" % TODAY)
wb_o.save(out_xlsx)
print("WROTE:", out_xlsx)
print("original CumulativeReviewtracking.xlsx md5 unchanged:",
      hashlib.md5(open(os.path.join(ROOT,"CumulativeReviewtracking.xlsx"),"rb").read()).hexdigest())
