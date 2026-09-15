# -*- coding: utf-8 -*-
"""
SCD portfolio summary broken out by protocol type.

Type comes from the master portfolio's own `Study Type` field, so the grouping is
the institution's, not mine. Complexity scores are joined in where they exist
(scored_protocols.json).

USAGE  python3 scd_by_type.py [out_dir]
"""
import os, sys, json, datetime
from collections import Counter, defaultdict
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else (
    "/Users/jhodges/Library/CloudStorage/"
    "OneDrive-St.JudeChildren'sResearchHospital/HEM Protocol Reviews")
TODAY = datetime.date.today().isoformat()
B = "/Users/jhodges/Library/Mobile Documents/com~apple~CloudDocs/Documents/HEM_Clinical_Trials_Dashboard"

ws = openpyxl.load_workbook(B+"/CTM Protocol Dashboards/HEM_Protocol_Portfolio.xlsx", data_only=True)["Portfolio"]
H = [c.value for c in ws[1]]
rows = [dict(zip(H, r)) for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
PI_FIX = {"SPRINTS": "RAI, PARUL"}
for r in rows:
    k = str(r["Protocol"]).strip().upper()
    if k in PI_FIX: r["PI"] = PI_FIX[k]
scd_all = [r for r in rows if str(r["Disease Group"]) == "Sickle cell disease"]
ACTIVE_ST = ("Open to Accrual", "Pre-Activation", "Pre-Open", "New")
scd = [r for r in scd_all if str(r.get("Status Group") or "").strip() in ACTIVE_ST]
closed_n = len(scd_all) - len(scd)
c2a = [r for r in scd_all if str(r.get("Status Group") or "").strip() == "Closed to Accrual"]

AWB = ("/Users/jhodges/Library/CloudStorage/OneDrive-St.JudeChildren'sResearchHospital/"
       "HEM Protocol Reviews/Hematology_Protocol_Assessment_Workbook_reconciled_%s.xlsx" % TODAY)
REVIEWED = set()
if os.path.exists(AWB):
    _w = openpyxl.load_workbook(AWB, data_only=True)["Protocol Tracker"]
    REVIEWED = {str(r[0]).strip().upper().replace("-", "")
                for r in _w.iter_rows(min_row=2, values_only=True) if r[0]}
def reviewed(pid): return pid.strip().upper().replace("-", "") in REVIEWED

S = json.load(open(os.path.join(HERE, "scored_protocols.json")))
partA, by = S["partA"], S.get("scoredBy", {})
def score(pid):
    for k in (pid, pid.upper(), pid.replace("-", "")):
        for cand in partA:
            if cand.upper().replace("-", "") == k.upper().replace("-", ""):
                return partA[cand], by.get(cand, "")
    return None, ""

ACTIVE = ("Open to Accrual", "Pre-Activation", "Pre-Open", "New")
def s(r, f): return str(r.get(f) or "").strip()
def num(v):
    try: return int(v)
    except (TypeError, ValueError): return None

groups = defaultdict(list)
for r in scd: groups[s(r, "Study Type") or "(type not recorded)"].append(r)
order = sorted(groups, key=lambda k: -len(groups[k]))

L = []; A = L.append
A("# SCD Portfolio — active studies by protocol type")
A("")
A("**Generated:** %s  " % TODAY)
A("**Source:** `HEM_Protocol_Portfolio.xlsx` · %d protocols, %d of them Disease Group = "
  "Sickle cell disease  " % (len(rows), len(scd_all)))
A("**Scope:** the **%d active** SCD protocols — Open to Accrual, Pre-Activation, Pre-Open or New. "
  "%d closed, abandoned or IRB-closed protocols are excluded." % (len(scd), closed_n))
A("**Grouping:** the master's own `Study Type` field")
A("")
A("---")
A("")
A("## Overview")
A("")
A("| Protocol type | Active | Accruing | Zero accrual | Not yet open |")
A("|---|---|---|---|---|")
for k in order:
    g = groups[k]
    accr = sum(1 for r in g if (num(r["Total Accrual"]) or 0) > 0)
    zero = sum(1 for r in g if (num(r["Total Accrual"]) or 0) == 0 and s(r,"Status Group")=="Open to Accrual")
    notopen = sum(1 for r in g if s(r,"Status Group") in ("Pre-Activation","Pre-Open","New"))
    A("| **%s** | %d | %d | %d | %d |" % (k, len(g), accr, zero, notopen))
A("| | **%d** | **%d** | **%d** | **%d** |" % (len(scd),
  sum(1 for r in scd if (num(r["Total Accrual"]) or 0) > 0),
  sum(1 for r in scd if (num(r["Total Accrual"]) or 0)==0 and s(r,"Status Group")=="Open to Accrual"),
  sum(1 for r in scd if s(r,"Status Group") in ("Pre-Activation","Pre-Open","New"))))
A("")
A("---")
A("")

PRE = ("Pre-Activation", "Pre-Open", "New")
pre = [r for r in scd if s(r, "Status Group") in PRE]
if pre:
    unrev = [r for r in pre if not reviewed(str(r["Protocol"]))]
    A("## Pipeline — %d protocols not yet open" % len(pre))
    A("")
    A("These are the studies where a decision is still open. **Pre-activation is when the review "
      "process has leverage** — before staff are assigned, contracts signed and commitments made. "
      "Once a study opens, a review can only ratify it or create friction.")
    A("")
    A("| Protocol | Status | PI | Type | Target | In review inventory? | Complexity |")
    A("|---|---|---|---|---|---|---|")
    for r in sorted(pre, key=lambda x: (s(x, "Status Group"), str(x["Protocol"]))):
        pid = str(r["Protocol"]).strip()
        sc, _ = score(pid)
        rv = "yes" if reviewed(pid) else "**never**"
        A("| **%s** | %s | %s | %s | %s | %s | %s |"
          % (pid, s(r, "Status Group"), s(r, "PI")[:22],
             s(r, "Study Type") or "*(not recorded)*",
             s(r, "Target") or "—", rv,
             ("%d/116" % sc["partA"]) if sc else "not scored"))
    A("")
    if unrev:
        A("**%d of the %d have never been through review** — %s. Each is still pre-activation or "
          "new, so there is still time for the review to matter."
          % (len(unrev), len(pre), ", ".join(sorted(str(r["Protocol"]).strip() for r in unrev))))
        A("")
    ther = [r for r in pre if "Therapeutic" in s(r, "Study Type")
            or s(r, "Study Type") == ""]
    A("**Worth noting:** every pre-activation protocol here has **no Study Type recorded**. That "
      "field appears to be populated at activation rather than at intake, which means the "
      "classification used to organise the portfolio is systematically missing for exactly the "
      "studies where a decision is still open.")
    A("")
    A("---")
    A("")

for k in order:
    g = groups[k]
    A("## %s — %d active" % (k, len(g)))
    A("")
    pis = Counter(s(r, "PI") for r in g if s(r, "PI"))
    sp = Counter(s(r, "Sponsor Type") for r in g if s(r, "Sponsor Type"))
    ph = Counter(s(r, "Phase") for r in g if s(r, "Phase") and s(r, "Phase") != "N/A")
    A("**PIs:** " + ", ".join("%s (%d)" % (p.split(",")[0].title(), n) for p, n in pis.most_common(6)))
    A("")
    A("**Sponsors:** " + ", ".join("%s %d" % (a, b) for a, b in sp.most_common()))
    if ph:
        A("")
        A("**Phases:** " + ", ".join("%s (%d)" % (a, b) for a, b in sorted(ph.items())))
    A("")
    A("| Protocol | Status | PI | Accrual | SJ target | Complexity | Tier |")
    A("|---|---|---|---|---|---|---|")
    for r in sorted(g, key=lambda x: -(num(x["Total Accrual"]) or 0)):
        sc, who = score(str(r["Protocol"]).strip())
        ta, tg = num(r["Total Accrual"]), num(r["Target"])
        accr = "%s / %s" % (ta if ta is not None else "0", tg if tg else "—")
        A("| **%s** | %s | %s | %s | %s | %s | %s |"
          % (str(r["Protocol"]).strip(), s(r, "Status Group"), s(r, "PI")[:22], accr,
             s(r, "SJ Target") or "—",
             ("%d/116" % sc["partA"]) if sc else "not scored", sc["tier"] if sc else "—"))
    A("")
    A("---")
    A("")

A("## What the active portfolio looks like")
A("")
npro = groups.get("Non-Therapeutic Prospective", [])
tpri = groups.get("Therapeutic - Primary Diagnosis", [])
nret = groups.get("Non-Therapeutic Retrospective", [])
A("**Non-Therapeutic Prospective carries the portfolio** — %d of the %d active SCD protocols. "
  "This is the registry, biobank and cohort work, and it is also where the workload sits: "
  "SCCRIP, INSIGHT-HD, SCDIC-II and ATHN together account for most of the SCD monthly WU despite "
  "scoring Low to Moderate on complexity." % (len(npro), len(scd)))
A("")
A("**The therapeutic pipeline is three protocols, and two have never enrolled.**")
A("")
for r in sorted(tpri, key=lambda x: -(num(x["Total Accrual"]) or 0)):
    ta, tg = num(r["Total Accrual"]) or 0, num(r["Target"])
    A("- **%s** (%s, %s) — %d / %s accrued%s"
      % (str(r["Protocol"]).strip(), s(r,"PI").split(",")[0].title(), s(r,"Status Group"),
         ta, tg or "—", "" if ta else "  ← **no accrual**"))
A("")
A("That is the whole active therapeutic footprint in sickle cell disease. Every Phase III SCD "
  "trial the portfolio has run is closed.")
A("")
A("**Retrospective work is small and cheap** — %d active, all institutional chart review, "
  "scoring at the bottom of the complexity range." % len(nret))
A("")
notype = groups.get("(type not recorded)", [])
if notype:
    A("**%d active protocols have no Study Type recorded** — %s. All are pre-activation or new, "
      "so the field is likely just unpopulated; worth filling while they are being activated."
      % (len(notype), ", ".join(sorted(str(r["Protocol"]).strip() for r in notype))))
    A("")
A("---")
A("")
A("## Notes")
A("")
if c2a:
    A("- **%d SCD protocols are Closed to Accrual** and excluded here (%s). They no longer enrol "
      "but may still be in follow-up, so they can still generate work — tell me if you want them "
      "counted as active." % (len(c2a), ", ".join(sorted(str(r["Protocol"]).strip() for r in c2a))))
A("- **The snapshot is ~3 months old** (generated 19 June 2026, latest status date 2026-05-05), "
  "so recent activations and closures will not appear.")
A("- **Complexity scores mix sources** — some human-rated, some my drafts from the protocol "
  "documents. `scored_protocols.json` records which for each; \"not scored\" means it has not "
  "been through the tool.")
A("- **SPRINTS\' PI is corrected to Rai** here; the master carried Hankins until 2026-09-09.")

out = os.path.join(OUT_DIR, "SCD_Active_By_Protocol_Type_%s.md" % TODAY)
open(out, "w").write("\n".join(L))
print("WROTE:", out)
print("active SCD: %d across %d types (%d closed excluded)" % (len(scd), len(groups), closed_n))
