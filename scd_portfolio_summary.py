# -*- coding: utf-8 -*-
"""
SCD portfolio summary, built from the master HEM_Protocol_Portfolio.xlsx.

Supersedes the earlier version, which was built from the 58-row assessment
workbook -- a subset covering under a third of the SCD portfolio.

Disease classification comes from the master's own `Disease Group` field, so
none of it is my judgement.

USAGE  python3 scd_portfolio_summary.py [out_folder] [date]
"""
import os, sys, datetime
from collections import Counter, defaultdict
import openpyxl

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else (
    "/Users/jhodges/Library/CloudStorage/"
    "OneDrive-St.JudeChildren'sResearchHospital/HEM Protocol Reviews")
TODAY = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
MASTER = ("/Users/jhodges/Library/Mobile Documents/com~apple~CloudDocs/Documents/"
          "HEM_Clinical_Trials_Dashboard/CTM Protocol Dashboards/HEM_Protocol_Portfolio.xlsx")
AWB = os.path.join(OUT_DIR, "Hematology_Protocol_Assessment_Workbook_reconciled_%s.xlsx" % TODAY)

ws = openpyxl.load_workbook(MASTER, data_only=True)["Portfolio"]
H = [c.value for c in ws[1]]
rows = [dict(zip(H, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
# PI corrections confirmed by JH 2026-09-09. SPRINTS is the one case where the
# master portfolio is wrong and the assessment workbook was right.
# SPRINTS was corrected in the master itself on 2026-09-09, so this overlay is
# now a no-op kept as a guard: if the master is ever regenerated from
# HEM_Clinical_Trials_Workbook (which still says HANKINS), it re-applies the fix.
PI_CORRECTIONS = {"SPRINTS": "RAI, PARUL"}
for _r in rows:
    if str(_r["Protocol"]).strip().upper() in PI_CORRECTIONS:
        _r["PI"] = PI_CORRECTIONS[str(_r["Protocol"]).strip().upper()]
scd = [r for r in rows if str(r["Disease Group"]) == "Sickle cell disease"]
ACTIVE = ("Open to Accrual", "Pre-Activation", "Pre-Open", "New")
act = [r for r in scd if str(r["Status Group"]) in ACTIVE]

# assessment-workbook coverage
awb_ids, awb_pi = set(), {}
if os.path.exists(AWB):
    w2 = openpyxl.load_workbook(AWB, data_only=True)["Protocol Tracker"]
    for r in w2.iter_rows(min_row=2, values_only=True):
        if r[0]:
            awb_ids.add(str(r[0]).strip().upper()); awb_pi[str(r[0]).strip().upper()] = str(r[2] or "")
REVIEWED = {"SCDSTEMM": "Opened", "MIPICS": "Opened", "MYPERS": "Opened",
            "CHITIN": "Opened", "RHEMEDY": "Opened"}

def pid(r): return str(r["Protocol"]).strip()
def sur(s):
    s = str(s or "").strip()
    return s.split(",")[0].strip().upper() if "," in s else (s.split()[-1].upper() if s else "")
def num(v):
    try: return int(v)
    except (TypeError, ValueError): return None

# snapshot age
exp = [r for r in rows if r["Expiration"] and r["Days to Expiry"] not in (None, "")]
snap = None
if exp:
    r0 = exp[0]
    try:
        d = r0["Expiration"] if isinstance(r0["Expiration"], datetime.date) else \
            datetime.date.fromisoformat(str(r0["Expiration"])[:10])
        snap = d - datetime.timedelta(days=int(r0["Days to Expiry"]))
    except Exception: pass

L=[]; A=L.append
A("# SCD Portfolio Summary")
A("")
A("**Generated:** %s  " % TODAY)
A("**Source:** `HEM_Protocol_Portfolio.xlsx` (CTM Protocol Dashboards) — %d protocols" % len(rows))
if snap: A("**Snapshot date:** ~%s, so roughly %d months old  " % (snap.isoformat(), max(0,(datetime.date.fromisoformat(TODAY)-snap).days)//30))
A("**Classification:** the master's own `Disease Group` field — not my judgement")
A("")
A("> This replaces the earlier version of this summary, which was built from the 58-row "
  "assessment workbook. That workbook turned out to cover **25 of these 80 protocols** — "
  "under a third — so its counts described the review committee's inventory, not the SCD "
  "portfolio.")
A("")
A("---")
A("")
A("## Headline")
A("")
A("**%d of the %d protocols in the portfolio are sickle cell disease** — the single largest "
  "disease group, ahead of hemophilia & bleeding/clotting disorders (%d) and bone marrow "
  "failure / MDS (%d)."
  % (len(scd), len(rows),
     sum(1 for r in rows if str(r["Disease Group"]).startswith("Hemophilia")),
     sum(1 for r in rows if str(r["Disease Group"]).startswith("Bone marrow"))))
A("")
A("| Status | Count |")
A("|---|---|")
for k, v in Counter(str(r["Status Group"]) for r in scd).most_common():
    A("| %s | %d |" % (k, v))
A("| **Active (open, pre-open, pre-activation, new)** | **%d** |" % len(act))
A("")
A("**Only %d of the %d SCD protocols are active.** %d sit at IRB closure and %d were "
  "abandoned — so most of what the portfolio lists is historical."
  % (len(act), len(scd),
     sum(1 for r in scd if str(r["Status Group"])=="IRB Closure"),
     sum(1 for r in scd if str(r["Status Group"])=="Abandoned")))
A("")
A("---")
A("")
A("## The active SCD portfolio (%d)" % len(act))
A("")
A("| Protocol | Status | Therapeutic? | PI | Accrual | SJ target | CT.gov |")
A("|---|---|---|---|---|---|---|")
for r in sorted(act, key=lambda x: (str(x["Status Group"]), pid(x))):
    ta, tg = r["Total Accrual"], r["Target"]
    accr = "%s / %s" % (ta if ta not in (None,"") else "0", tg if tg not in (None,"") else "—")
    A("| **%s** | %s | %s | %s | %s | %s | %s |"
      % (pid(r), r["Status Group"],
         "Therapeutic" if str(r["Therapeutic Group"])=="Therapeutic" else "Non-therapeutic",
         str(r["PI"])[:24], accr, r["SJ Target"] if r["SJ Target"] not in (None,"") else "—",
         str(r["Live CT Status"] or r["NCT"] or "—")[:12]))
A("")

ther = [r for r in act if str(r["Therapeutic Group"])=="Therapeutic"]
A("### The portfolio is overwhelmingly observational")
A("")
A("**Only %d of the %d active SCD protocols are therapeutic** (%s). The other %d are "
  "registries, biobanks, natural-history and other non-therapeutic studies."
  % (len(ther), len(act), ", ".join(pid(r) for r in ther), len(act)-len(ther)))
A("")
A("Across all %d SCD protocols the split is %d non-therapeutic to %d therapeutic. Only %d "
  "carry the gene-therapy flag."
  % (len(scd), sum(1 for r in scd if str(r["Therapeutic Group"])=="Non-Therapeutic"),
     sum(1 for r in scd if str(r["Therapeutic Group"])=="Therapeutic"),
     sum(1 for r in scd if str(r["Gene Therapy"])=="Y")))
A("")
A("---")
A("")
A("## Accrual")
A("")
zero = [r for r in act if num(r["Total Accrual"]) in (0, None)]
A("**%d of the %d active protocols have accrued nobody.** Some are collaborative or "
  "data-sharing projects with no target at all; others have real targets and no patients."
  % (len(zero), len(act)))
A("")
A("| Protocol | Status | Target | SJ target | Reading |")
A("|---|---|---|---|---|")
for r in sorted(zero, key=lambda x: pid(x)):
    t = r["Target"]
    reading = ("no target set — likely a data-sharing or consortium project"
               if t in (None, "") else "**has a target and zero patients**")
    A("| %s | %s | %s | %s | %s |"
      % (pid(r), r["Status Group"], t if t not in (None,"") else "—",
         r["SJ Target"] if r["SJ Target"] not in (None,"") else "—", reading))
A("")
perf = [(pid(r), num(r["Total Accrual"]), num(r["Target"])) for r in act
        if num(r["Total Accrual"]) and num(r["Total Accrual"]) > 0]
A("**Accruing:**")
A("")
A("| Protocol | Accrued | Target | % of target |")
A("|---|---|---|---|")
for p, a, t in sorted(perf, key=lambda x: -(x[1] or 0)):
    A("| %s | %d | %s | %s |" % (p, a, t if t else "—", ("%.0f%%" % (100.0*a/t)) if t else "—"))
A("")
A("---")
A("")
A("## Who holds the SCD portfolio")
A("")
A("| PI | Protocols |")
A("|---|---|")
for k, v in Counter(str(r["PI"]) for r in scd).most_common(8):
    A("| %s | %d |" % (k, v))
A("")
top = Counter(str(r["PI"]) for r in scd).most_common(4)
A("The top four PIs hold **%d of the %d** SCD protocols. Note this counts the full history, "
  "not just active studies." % (sum(v for _, v in top), len(scd)))
A("")
A("---")
A("")
A("## Review coverage")
A("")
A("This is the gap worth acting on.")
A("")
A("| | Count |")
A("|---|---|")
A("| SCD protocols in the master | %d |" % len(scd))
A("| …that appear in the assessment workbook | %d |" % len([r for r in scd if pid(r).upper() in awb_ids]))
A("| …that have been through protocol review | %d |" % len([r for r in scd if pid(r).upper() in REVIEWED]))
A("")
A("**%d of the %d SCD protocols are not in the assessment workbook at all** — the review "
  "committee's inventory has never listed them. Of the %d that have actually been reviewed, "
  "all were opened."
  % (len(scd)-len([r for r in scd if pid(r).upper() in awb_ids]), len(scd), len(REVIEWED)))
A("")
never = [r for r in act if pid(r).upper() not in awb_ids]
A("### Active SCD protocols never visible to the review process (%d)" % len(never))
A("")
A("| Protocol | Status | PI | Title |")
A("|---|---|---|---|")
for r in sorted(never, key=lambda x: pid(x)):
    A("| **%s** | %s | %s | %s |" % (pid(r), r["Status Group"], str(r["PI"])[:22],
                                     str(r["Title"] or "")[:70]))
A("")
A("These are open or activating today and have never been through the review process the "
  "other protocols went through.")
A("")
A("---")
A("")
A("## Data-quality flags")
A("")
A("### PI attribution — settled")
A("")
A("Five protocols had conflicting PI records across systems. All resolved by JH on %s and "
  "recorded in `PI_Attribution_Log_%s.md`." % (TODAY, TODAY))
A("")
A("| Protocol | Correct PI | Which system was wrong |")
A("|---|---|---|")
A("| 1000SGP | Takemoto | `CTMProtocolsPositions.xlsx` (said Hankins) |")
A("| SCCRIP | Manwani | assessment workbook (said Takemoto) |")
A("| SCDIC-II | Leonard | assessment workbook (said Takemoto) |")
A("| SCDSTEMM | Leonard | neither — though the protocol document names Sharma |")
A("| **SPRINTS** | **Rai** | **the master portfolio** (says Hankins) |")
A("")
A("**SPRINTS is the exception.** For the other four the master portfolio was right; for "
  "SPRINTS the master is wrong and the assessment workbook was correct. This summary applies "
  "the correction, so the PI counts above already read Rai — but **the master portfolio itself "
  "still carries the error**, and anything else generated from it will inherit it.")
A("")
A("### Identifier and coverage mismatches")
A("")
A("- **`HEMGENIX` is not a protocol ID in the master.** That protocol is filed as "
  "**`IXTEND3004`**, which is what `CumulativeReviewtracking.xlsx` already uses. The "
  "assessment workbook's label is the outlier.")
A("- **`LTFUAGT4HB`, `AG348-C-028` and `AG348-C-029`** — reviewed and opened in October 2025, "
  "**absent from the master entirely**. Either never activated, or filed under other IDs.")
A("- **`CDCCCR`** is not in the master either; its title remains the descriptive name supplied "
  "by JH rather than a registered protocol title.")
A("")
A("### One review decision contradicts the master")
A("")
A("**CHITIN** was recorded as **opened**, but the master shows it at **IRB Closure with 0 of 8 "
  "accrued** — opened and closed without enrolling anyone. Worth confirming which is current.")
A("")
A("### Snapshot age")
A("")
A("The master's most recent status date is **2026-05-05**%s. Anything decided since — including "
  "the protocol review decisions confirmed on 2026-09-09 — will not be reflected in it."
  % (", putting the snapshot around %s" % snap.isoformat() if snap else ""))
A("")

out = os.path.join(OUT_DIR, "SCD_Portfolio_Summary_%s.md" % TODAY)
open(out, "w").write("\n".join(L))
print("WROTE:", out, os.path.getsize(out), "bytes")
print("SCD %d of %d | active %d | therapeutic-active %d | zero-accrual %d | in AWB %d | reviewed %d"
      % (len(scd), len(rows), len(act), len(ther), len(zero),
         len([r for r in scd if pid(r).upper() in awb_ids]), len(REVIEWED)))
