# -*- coding: utf-8 -*-
"""
Compute Part B (Monthly Workload Units) with the registry-track convention.

REGISTRY TRACK (adopted 2026-09-09, see Registry_Track_Proposal_2026-09-09.md)
  A protocol is registry track when Domain 4 (Investigational Product) == 0 AND
  Domain 8 lifetime_horizon >= 2 -- no study intervention, open-ended collection.
  Membership is derived from scores already recorded, not judged.

  For those protocols two OnCore statuses map differently:
    ON STUDY     -> ltfu       (not follow_up) -- a dormant cohort member between
                                annual contacts is what the LTFU row describes
    ON TREATMENT -> follow_up  (not active)    -- the `active` row is definitionally
                                unreachable: Domain 4 == 0 means there is no study
                                intervention, so OnCore's ON TREATMENT there is the
                                patient's own background therapy

  This changes no weights, rates or tier boundaries. It is a mapping convention.

USAGE  python3 compute_partb.py [out_dir]
"""
import os, sys, json, subprocess, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else (
    "/Users/jhodges/Library/CloudStorage/"
    "OneDrive-St.JudeChildren'sResearchHospital/HEM Protocol Reviews")
TODAY = datetime.date.today().isoformat()
REPO = ("/Users/jhodges/Library/Mobile Documents/com~apple~CloudDocs/Documents/"
        "GitHub/hem-protocol-scoring-tool")
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"

D = json.load(open(os.path.join(HERE, "scored_protocols.json")))
items, partA, counts = D["itemScores"], D["partA"], D["participantCounts"]

def is_registry(pid):
    it = items.get(pid, {})
    d4 = partA.get(pid, {}).get("domains", {}).get("d4")
    return d4 == 0 and it.get("lifetime_horizon", 0) >= 2

MAP_TRIAL = {"CONSENTED":"screening","ELIGIBILITY":"screening","ON TREATMENT":"active",
             "ON FOLLOW UP":"follow_up","OFF TREATMENT":"follow_up","ON STUDY":"follow_up"}
MAP_REG   = {"CONSENTED":"screening","ELIGIBILITY":"screening","ON TREATMENT":"follow_up",
             "ON FOLLOW UP":"follow_up","OFF TREATMENT":"ltfu","ON STUDY":"ltfu"}
NOT_COUNTED = {"OFF STUDY","EXPIRED","WITHDRAWN","CONSENT REFUSED","CONSENT WAIVED","UNKNOWN"}

batch, meta = [], {}
for pid, v in counts.items():
    if pid not in items: continue
    reg = is_registry(pid)
    M = MAP_REG if reg else MAP_TRIAL
    rows = {"screening":0,"active":0,"follow_up":0,"ltfu":0,"closeout":0}
    unmapped = []
    for st, n in v["raw"].items():
        u = st.upper()
        if u in NOT_COUNTED: continue
        t = M.get(u)
        if t: rows[t] += n
        else: unmapped.append(st)
    if sum(rows.values()) == 0: continue
    batch.append({"id": pid, "items": items[pid], "participants": rows})
    meta[pid] = {"registry": reg, "rows": rows, "unmapped": unmapped, "raw": v["raw"]}

# sanity: no registry-track protocol may populate the `active` row
bad = [p for p, m in meta.items() if m["registry"] and m["rows"]["active"] > 0]
assert not bad, "registry-track protocols populating `active`: %s" % bad

inp = os.path.join(HERE, "_partb_in.json"); outp = os.path.join(HERE, "_partb_out.json")
json.dump({"protocols": batch}, open(inp, "w"))
r = subprocess.run([JSC, os.path.join(HERE, "batch_score.js"), "--", REPO, inp, outp],
                   capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
res = {x["id"]: x for x in json.load(open(outp))["results"]}

wb = openpyxl.Workbook()
HDR = Font(bold=True, color="FFFFFF"); FILL = PatternFill("solid", fgColor="1F4E79")
GREEN = PatternFill("solid", fgColor="E8F5E9")

ws = wb.active; ws.title = "Part B results"
ws.append(["Protocol","Track","Part A","Tier","Participants","Static WU",
           "Monthly WU","screening","active","follow_up","ltfu"])
for pid in sorted(res, key=lambda x: -(res[x]["partB"]["monthlyWU"] or 0)):
    m, b = meta[pid], res[pid]["partB"]
    ws.append([pid, "REGISTRY" if m["registry"] else "trial", res[pid]["partA"], res[pid]["tier"],
               b["participantTotal"], b["staticWU"], round(b["monthlyWU"], 1),
               m["rows"]["screening"], m["rows"]["active"], m["rows"]["follow_up"], m["rows"]["ltfu"]])
for row in ws.iter_rows(min_row=2):
    if row[1].value == "REGISTRY":
        for c in row: c.fill = GREEN

ws2 = wb.create_sheet("Mapping")
ws2.append(["OnCore status","Trial track","Registry track","Note"])
for a,b,c,d in [
 ("CONSENTED","screening","screening",""),("ELIGIBILITY","screening","screening",""),
 ("ON TREATMENT","active","follow_up","Registry: the `active` row is definitionally unreachable when Domain 4 == 0 - there is no study intervention, so OnCore's ON TREATMENT reflects the patient's own background therapy."),
 ("ON FOLLOW UP","follow_up","follow_up",""),
 ("OFF TREATMENT","follow_up","ltfu",""),
 ("ON STUDY","follow_up","ltfu","Confirmed by JH 2026-09-09 for the trial track. Registry: a dormant cohort member between annual contacts is what the LTFU row describes."),
 ("OFF STUDY / EXPIRED / WITHDRAWN / CONSENT REFUSED / CONSENT WAIVED","not counted","not counted","No longer generating per-participant workload.")]:
    ws2.append([a,b,c,d])

ws3 = wb.create_sheet("Registry track")
ws3.append(["Rule","Domain 4 (Investigational Product) == 0  AND  Domain 8 lifetime_horizon >= 2"])
ws3.append(["Meaning","No study intervention, open-ended data collection. Derived from scores already recorded - no new rater judgement."])
ws3.append(["Adopted","2026-09-09 (JH). See Registry_Track_Proposal_2026-09-09.md"])
ws3.append([])
ws3.append(["Protocol","Registry track?","Domain 4","lifetime_horizon"])
for pid in sorted(meta):
    ws3.append([pid, "yes" if meta[pid]["registry"] else "no",
                partA.get(pid,{}).get("domains",{}).get("d4"), items[pid].get("lifetime_horizon")])

for sh, w in (("Part B results",[16,10,8,11,13,10,12,10,8,11,8]),
              ("Mapping",[52,14,15,92]),("Registry track",[18,16,10,18])):
    s = wb[sh]
    for i, x in enumerate(w, 1): s.column_dimensions[get_column_letter(i)].width = x
    for c in s[1]: c.font = HDR; c.fill = FILL; c.alignment = Alignment(wrap_text=True, vertical="center")
    s.freeze_panes = "A2"
    for row in s.iter_rows(min_row=2):
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")

out = os.path.join(OUT_DIR, "Participant_Counts_and_PartB_%s.xlsx" % TODAY)
wb.save(out)
os.remove(inp); os.remove(outp)
nreg = sum(1 for m in meta.values() if m["registry"])
print("WROTE:", out)
print("Part B computed for %d protocols (%d registry track, %d trial track)"
      % (len(res), nreg, len(res)-nreg))
