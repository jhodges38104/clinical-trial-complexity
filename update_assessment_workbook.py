# -*- coding: utf-8 -*-
"""
Update Hematology_Protocol_Assessment_Workbook_Updated.xlsx from the review record.

Writes a NEW file; the original is never modified.

WHAT IT CHANGES
  1. Adds "Reviewed - Decision Pending" to the Review Status dropdown (G2:G100).
     The original vocabulary had no value meaning "review happened, decision not
     yet confirmed", which is the true state of most reviewed rows.
     Approved by JH 2026-09-09.
  2. Updates Review Status on the 11 rows that were reviewed but still read
     Pending/Under Review.
  3. Appends the review facts to the Notes column, following the existing
     "; "-separated convention.
  4. Adds the 4 protocol rows that were reviewed but absent from the workbook.
  5. Relabels Dashboard A3 "Total Protocols Reviewed" -> "Total Protocols Entered"
     (the formula is COUNTA of the ID column, so it counts entries, not reviews).

WHAT IT DELIBERATELY DOES NOT CHANGE
  - Design / Population Benefit / Resource scores (H, I, J) stay empty. Those are
    a 63-criterion /100 rubric; the review used a 6-criterion /30 sheet. Mapping
    one onto the other would be fabrication.
  - The Decision column (M) stays empty. Per the workbook's own Instructions the
    decision is derived from the /100 thresholds, which were never scored. Where
    a decision IS known it is carried by Review Status instead.

USAGE  python3 update_assessment_workbook.py [review_folder] [date]
"""
import os, sys, shutil, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

ROOT = sys.argv[1] if len(sys.argv) > 1 else (
    "/Users/jhodges/Library/CloudStorage/"
    "OneDrive-St.JudeChildren'sResearchHospital/HEM Protocol Reviews")
TODAY = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
os.chdir(ROOT)

SRC = "Hematology_Protocol_Assessment_Workbook_Updated.xlsx"
REC = "CumulativeReviewtracking_reconciled_%s.xlsx" % TODAY
OUT = "Hematology_Protocol_Assessment_Workbook_reconciled_%s.xlsx" % TODAY
NEW_STATUS = "Reviewed - Decision Pending"
CLOSED_STATUS = "Closed to Accrual"

for f in (SRC, REC):
    if not os.path.exists(f): sys.exit("Missing required file: %s" % f)

# ---------- read the review record (single source of truth) ----------
rec = openpyxl.load_workbook(REC)["Reconciled Tracker"]
H = [c.value for c in rec[1]]
def col(name): return H.index(name)
review = {}
for r in rec.iter_rows(min_row=2, values_only=True):
    review[r[0]] = dict(
        pi=r[col("PI")], batches=r[col("Review date(s)")],
        rpct=r[col("Reviewer %")], dpct=r[col("DM %")],
        decision=r[col("DECISION")], confirmed_by=r[col("Confirmed by")],
        follow_up=r[col("Open follow-up / unresolved")], risk=r[col("Risk")])

# tracker key -> assessment-workbook Protocol ID
LINK = {"CHITIN":"CHITIN", "PNHIPTA":"PNHIPTA", "X4WARDXP":"4WARDXP", "IDBLEED":"IDBLEED",
        "IXTEND3004":"HEMGENIX", "RHEMEDY":"RHEMEDY", "MIPICS":"miPICs", "MYPERS":"MYPERS",
        "LEAP":"LEAP", "LIVBX":"LIVBX", "SCDSTEMM":"SCDSTEMM"}

# 12 opened, IDBLEED closed to accrual, VINGT tabled -- confirmed by JH 2026-09-09.
# "Open - Standard" rather than "High Priority": JH confirmed the opening, not a priority.
# IDBLEED is NOT "Declined" -- it was opened and enrolled 14 patients before closing.
STATUS_FOR   = {"OPENED": "Approved", "TABLED": "Deferred",
                "CLOSED TO ACCRUAL": CLOSED_STATUS}
DECISION_FOR = {"OPENED": "Open - Standard", "TABLED": "Further Review Needed",
                "CLOSED TO ACCRUAL": None}

# rows to add: (ID, Title, PI, Sponsor, Type, SubmissionDate, Status, Notes)
ADD = [
 ("VINGT",
  "Longitudinal evaluation of vector-mediated cellular immunity in bleeding disorder "
  "gene therapy patients",
  "Rohith Jesudas", "American Thrombosis and Hemostasis Network", "Observational", None,
  "Deferred",
  "Reviewed 9.24.25: reviewer 63%, DM 80%; TABLED - confirmed JH 2026-09-09; "
  "20 patients over 6 years across multiple ATHN sites; unfunded, multi-site subcontracts/"
  "MTAs/DUAs; only intake form reviewed, not full protocol"),
 ("LTFUAGT4HB",
  "Long Term Follow-Up for subjects treated in the AGT4HB study (15 year follow-up)",
  "Ulrike Reiss", "St. Jude Children's Research Hospital", "Natural History", None,
  "Approved",
  "Reviewed 9.24.25: reviewer 100%, DM 100% - highest of any reviewed protocol; "
  "OPENED - confirmed JH 2026-09-09; RISK Medium-High - no funding identified and both "
  "reviewers scored from the intake form only, not a full protocol; parent study AGT4HB "
  "is a separate row"),
 ("AG348-C-028",
  "Mitapivat in non-transfusion-dependent alpha- or beta-thalassemia (AG348-C-028)",
  "Parul Rai", "Agios Pharmaceuticals", "Interventional", None,
  "Approved",
  "Reviewed 10.01.25: reviewer 100%, DM 100%; OPENED - confirmed JH 2026-09-09; "
  "follow-up: confirm eligible AND interested subjects; sibling of AGPKD "
  "(same drug mitapivat/AG-348, same PI, different indication)"),
 ("AG348-C-029",
  "Mitapivat in transfusion-dependent alpha- or beta-thalassemia (AG348-C-029)",
  "Parul Rai", "Agios Pharmaceuticals", "Interventional", None,
  "Approved",
  "Reviewed 10.01.25: reviewer 100%, DM 100%; OPENED - confirmed JH 2026-09-09; "
  "follow-up: confirm eligible AND interested subjects; tracked jointly with "
  "AG348-C-028 in CumulativeReviewtracking but is a separate protocol"),
]

# ---------- load and edit ----------
shutil.copyfile(SRC, OUT)          # start from a byte copy, then edit the copy
wb = openpyxl.load_workbook(OUT)
wt = wb["Protocol Tracker"]

# 1. widen the Review Status dropdown
changed_dv = False
for dv in wt.data_validations.dataValidation:
    if dv.type == "list" and "G2" in str(dv.sqref):
        vals = str(dv.formula1).strip('"').split(",")
        if NEW_STATUS not in vals:
            vals.insert(vals.index("Under Review") + 1, NEW_STATUS)
            changed_dv = True
        if CLOSED_STATUS not in vals:
            vals.append(CLOSED_STATUS)   # a post-opening state, so it sits last
            changed_dv = True
        if changed_dv:
            dv.formula1 = '"%s"' % ",".join(vals)
            status_vocab = vals
print("dropdown extended:", changed_dv)
if changed_dv:
    print("  Review Status vocabulary now:", ", ".join(status_vocab))

# Portfolio rows that are NOT among the 14 reviewed protocols but whose status changed.
# PROSPECT: the workbook already carried "DM: CLOSE THIS STUDY" as an unactioned directive.
PORTFOLIO_UPDATES = {
 "PROSPECT": dict(
     status=CLOSED_STATUS, decision=None,
     note="STUDY CLOSED, confirmed JH 2026-09-09. Actions the pre-existing directive "
          "\"DM: CLOSE THIS STUDY\" above, which had been sitting unexecuted against an "
          "Under Review row. PROSPECT is the Oxbryta (voxelotor) product registry; voxelotor "
          "was withdrawn from the market in September 2024."),
}

# Titles corrected at source. The workbook held a truncated or superseded string.
TITLE_FIXES = {
 "BHEEM": ("A Phase 1/2 Study Evaluating the Safety and Efficacy of a Single Dose of "
           "Autologous CD34+ Base Edited Hematopoietic Stem Cells (BEAM-101) in Patients "
           "with Sickle Cell Disease and Severe Vaso-Occlusive Crises",
           "the stored title was truncated and carried a superseded \"to Increase Fetal "
           "Hemoglobin (HbF) Production\" clause; replaced with the full title supplied by JH"),
 "HEMGENIX": ("Phase 3, Open-label, Single-dose, Multicenter Study Investigating Efficacy, "
              "Safety, and Tolerability of CSL222 (Etranacogene Dezaparvovec) Administered to "
              "Adolescent Male Subjects (>= 12 to < 18 Years of Age) with Severe or Moderately "
              "Severe Hemophilia B",
              "the stored title was truncated at \"(>= 12 to < 18 Years\"; full title taken from "
              "HEM_Protocol_Portfolio.xlsx, where this protocol is filed under its institutional "
              "ID IXTEND3004 - 'HEMGENIX' is not a protocol ID in the master portfolio"),
 "RESESTX": ("A Randomized, Double-Blind, Controlled, Parallel Group Study with the INTERCEPT "
             "Blood System for Red Blood Cells in Regions at Potential Risk for Zika Virus "
             "Transfusion-Transmitted Infections (RedeS Study) and Treatment Use Open-Label "
             "Extension Study",
             "the stored title was truncated mid-word at \"(RedeS\"; full title taken from "
             "HEM_Protocol_Portfolio.xlsx"),
 "CDCCCR": ("CDC Community Counts Registry for bleeding disorders",
           "the title cell was EMPTY; supplied by JH. This is a descriptive name rather than "
           "a formal protocol title. NOT present in HEM_Protocol_Portfolio.xlsx - replace "
           "if a registered title exists"),
}

# PI corrections confirmed by JH 2026-09-09, protocol by protocol.
# Three match the master portfolio; SPRINTS does NOT -- there the assessment
# workbook was already right and it is the MASTER that needs correcting.
AWB_PI_FIXES = {
 "SCCRIP":   ("Deepa Manwani",  "confirmed JH 2026-09-09; matches master portfolio"),
 "SCDIC-II": ("Alexis Leonard", "confirmed JH 2026-09-09; matches master portfolio"),
 "SPRINTS":  ("Parul Rai",      "confirmed JH 2026-09-09; assessment workbook was already "
                                "correct - the MASTER PORTFOLIO says Hankins and needs fixing"),
 "SCDSTEMM": ("Alexis Leonard", "confirmed JH 2026-09-09; matches master portfolio. NOTE the "
                                "protocol document (Amendment 2.1, May 2025) names Akshay Sharma "
                                "as PI with Leonard as sub-investigator - consistent with a PI "
                                "change after that amendment"),
}

# index existing rows
row_of = {}
for i, r in enumerate(wt.iter_rows(min_row=2, values_only=True), 2):
    if r[0]: row_of[str(r[0]).strip()] = i

# Holds closed on the Director's authority. The original note text is never removed --
# the closure is appended so the audit trail stays intact.
HOLDS_CLOSED = {
 "4WARDXP":  "HOLD CLOSED by JH 2026-09-09 (BM hold above: ethical questions / hold until a "
             "patient is identified). Accrual risk remains HIGH on separate grounds: "
             "Feasibility 1, 0-1 eligible patients, no second reviewer.",
 "HEMGENIX": "HOLD CLOSED by JH 2026-09-09 (BM hold above: hold until participants confirmed "
             "January 2026).",
 "IDBLEED":  "STUDY CLOSED TO ACCRUAL, confirmed JH 2026-09-09. Opened at review, since "
             "closed; reached 14 of a planned 43 patients in two years. The BM hold above is "
             "superseded rather than satisfied - the power analysis and enrollment strategy "
             "it asked for were never delivered, and slow accrual is what the study was "
             "ultimately closed for. OPEN: disposition of data on the 14 enrolled patients.",
}

def append_note(cell, addition):
    cur = (cell.value or "").strip()
    cell.value = (cur + "; " + addition) if cur else addition

# 2 + 3. update the 11 reviewed rows
updated = []
for key, awb_id in LINK.items():
    if awb_id not in row_of:
        print("  WARN: %s not found in workbook" % awb_id); continue
    r = row_of[awb_id]
    v = review[key]
    old = wt.cell(row=r, column=7).value
    new = STATUS_FOR.get(v["decision"], NEW_STATUS)
    wt.cell(row=r, column=7).value = new
    wt.cell(row=r, column=13).value = DECISION_FOR.get(v["decision"], None)
    parts = ["Reviewed %s" % v["batches"]]
    sc = []
    if v["rpct"]: sc.append("reviewer %s" % v["rpct"])
    if v["dpct"]: sc.append("DM %s" % v["dpct"])
    if sc: parts[0] += ": " + ", ".join(sc)
    parts.append("%s - confirmed %s" % (v["decision"], v["confirmed_by"]))
    if v["risk"] and v["risk"] not in ("Low", "n/a"):
        parts.append("RISK %s - %s" % (v["risk"], v["follow_up"]))
    if awb_id in HOLDS_CLOSED: parts.append(HOLDS_CLOSED[awb_id])
    append_note(wt.cell(row=r, column=14), "; ".join(parts))
    updated.append((awb_id, r, old, new))

# 3a-pre. PI corrections
for pid,(newpi,why) in AWB_PI_FIXES.items():
    if pid not in row_of:
        print("  WARN: %s not found" % pid); continue
    r=row_of[pid]; oldpi=str(wt.cell(row=r,column=3).value or "")
    if oldpi.strip()!=newpi:
        wt.cell(row=r,column=3).value=newpi
        append_note(wt.cell(row=r,column=14),
                    "PI CORRECTED %s from '%s' to '%s' - %s" % (TODAY,oldpi.strip(),newpi,why))
        print("  PI fixed: %-10s %-18s -> %s" % (pid,oldpi.strip(),newpi))
    else:
        append_note(wt.cell(row=r,column=14), "PI CONFIRMED %s as '%s' - %s" % (TODAY,newpi,why))
        print("  PI confirmed (no change): %-10s %s" % (pid,newpi))

# 3a. title corrections
for pid, (newtitle, why) in TITLE_FIXES.items():
    if pid not in row_of:
        print("  WARN: %s not found in workbook" % pid); continue
    r = row_of[pid]
    oldtitle = str(wt.cell(row=r, column=2).value or "")
    if oldtitle.strip() != newtitle:
        wt.cell(row=r, column=2).value = newtitle
        append_note(wt.cell(row=r, column=14),
                    "TITLE CORRECTED %s - %s" % (TODAY, why))
        print("  title fixed: %-8s (row %2d)  was: %s"
              % (pid, r, (oldtitle.strip()[:40] + "...") if oldtitle.strip() else "(EMPTY)"))

# 3b. portfolio rows closed outside the reviewed set
for pid, upd in PORTFOLIO_UPDATES.items():
    if pid not in row_of:
        print("  WARN: %s not found in workbook" % pid); continue
    r = row_of[pid]
    old_status = wt.cell(row=r, column=7).value
    wt.cell(row=r, column=7).value = upd["status"]
    wt.cell(row=r, column=13).value = upd["decision"]
    append_note(wt.cell(row=r, column=14), upd["note"])
    updated.append((pid, r, old_status, upd["status"]))

# 4. add the missing protocols
start = max(row_of.values()) + 1
for i, (pid, title, pi, sponsor, typ, sub, status, notes) in enumerate(ADD):
    r = start + i
    mdec = {"Approved": "Open - Standard", "Deferred": "Further Review Needed"}.get(status)
    for c, val in ((1, pid), (2, title), (3, pi), (4, sponsor), (5, typ),
                   (6, sub), (7, status), (13, mdec), (14, notes)):
        wt.cell(row=r, column=c).value = val
print("\nadded rows %d-%d" % (start, start + len(ADD) - 1))

# 5. relabel the Dashboard metric
db = wb["Dashboard"]
if db["A3"].value and "Reviewed" in str(db["A3"].value):
    db["A3"].value = "Total Protocols Entered:"
# surface the new status, otherwise the largest category change is invisible
db["A8"] = "Reviewed - Decision Pending:"
db["B8"] = '=COUNTIF(\'Protocol Tracker\'!G2:G100,"Reviewed - Decision Pending")'
db["A8"].font = Font(bold=True)
db["A9"] = ("Note: 'Entered' counts rows via COUNTA, not reviews completed. Approved/Declined "
            "count the Decision column, which is intentionally empty - see Notes per row.")
db["A9"].font = Font(italic=True, size=9, color="595959")

wb.save(OUT)

print("\n--- status changes ---")
for awb_id, r, old, new in sorted(updated, key=lambda x: x[1]):
    print("  row %-3d %-12s %-15s -> %s" % (r, awb_id, old, new))
print("\nWROTE:", os.path.join(ROOT, OUT))
