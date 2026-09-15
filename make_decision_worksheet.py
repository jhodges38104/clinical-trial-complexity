# -*- coding: utf-8 -*-
"""
Generate the decision record.

One page per few protocols; each block carries the PROPOSED decision pre-ticked,
the verbatim source quote it rests on, and a blank line for what the committee
actually decided. Sorted by confidence so the fast confirmations come first and
the one protocol that cannot be inferred sits last.

USAGE  python3 make_decision_worksheet.py [output_folder]
"""
import docx, os, sys, datetime
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from decisions import DECISIONS, NOT_OPEN

ROOT = sys.argv[1] if len(sys.argv) > 1 else (
    "/Users/jhodges/Library/CloudStorage/"
    "OneDrive-St.JudeChildren'sResearchHospital/HEM Protocol Reviews")
TODAY = datetime.date.today().isoformat()

NAVY  = RGBColor(0x1F, 0x4E, 0x79)
GREY  = RGBColor(0x59, 0x59, 0x59)
GREEN = RGBColor(0x1B, 0x5E, 0x20)
RED   = RGBColor(0x9B, 0x1C, 0x1C)

d = docx.Document()
for s in d.sections:
    s.top_margin = s.bottom_margin = Inches(0.5)
    s.left_margin = s.right_margin = Inches(0.65)
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)

def fixed(table, widths):
    table.autofit = False
    tbl = table._tbl; tblPr = tbl.tblPr
    for el in tblPr.findall(qn("w:tblLayout")): tblPr.remove(el)
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
    for g in tbl.findall(qn("w:tblGrid")): tbl.remove(g)
    grid = OxmlElement("w:tblGrid")
    for w in widths:
        gc = OxmlElement("w:gridCol"); gc.set(qn("w:w"), str(int(w*1440))); grid.append(gc)
    tblPr.addnext(grid)
    for row in table.rows:
        for i, w in enumerate(widths):
            if i < len(row.cells): row.cells[i].width = Inches(w)

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    el = OxmlElement("w:shd"); el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), hexcolor); tcPr.append(el)

def para(text="", size=10, bold=False, color=None, after=4, italic=False):
    p = d.add_paragraph(); r = p.add_run(text)
    r.font.size = Pt(size); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = color
    p.paragraph_format.space_after = Pt(after)
    return p

# ---------------- header ----------------
para("PROTOCOL REVIEW — DECISION RECORD", 15, True, NAVY, after=1)
para("Department of Hematology · reviews of 20 Aug – 1 Oct 2025 · recorded %s" % TODAY,
     9, False, GREY, after=7)

box = d.add_table(rows=1, cols=1); box.style = "Table Grid"; fixed(box, [7.2])
bc = box.cell(0, 0); shade(bc, "E8F5E9"); bc.text = ""
p = bc.paragraphs[0]
r = p.add_run("Outcome  "); r.bold = True; r.font.size = Pt(10); r.font.color.rgb = GREEN
r = p.add_run("12 protocols OPENED. IDBLEED CLOSED TO ACCRUAL. VINGT TABLED. Confirmed by "
              "JH on 2026-09-09. Nothing in this document is inferred.")
r.font.size = Pt(9)
p2 = bc.add_paragraph()
r = p2.add_run("Why the follow-ups matter  "); r.bold = True; r.font.size = Pt(10); r.font.color.rgb = RED
r = p2.add_run("Several protocols opened with concerns that no document records as resolved. "
               "Because these studies are now open, those concerns are live accrual and "
               "delivery risks rather than gating questions. Entries are ordered by risk.")
r.font.size = Pt(9)
for p in bc.paragraphs: p.paragraph_format.space_after = Pt(3)

d.add_paragraph().paragraph_format.space_after = Pt(3)

RISKFILL = {"High": "FDECEA", "Medium-High": "FFF4E5", "Medium": "FFFDE7",
            "Low-Medium": "F1F8E9", "Low": "E8F5E9", "n/a": "EDF2F7"}
RISKCOL  = {"High": RED, "Medium-High": RED, "Medium": NAVY,
            "Low-Medium": GREEN, "Low": GREEN, "n/a": GREY}

for n, (key, decision, by, quote, src, follow, owner, risk) in enumerate(DECISIONS + NOT_OPEN, 1):
    t = d.add_table(rows=4, cols=2); t.style = "Table Grid"; fixed(t, [1.35, 5.85])
    fill = RISKFILL[risk]

    c = t.cell(0, 0); shade(c, fill); c.text = ""
    p = c.paragraphs[0]; r = p.add_run("%d. %s" % (n, key))
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = NAVY
    c = t.cell(0, 1); shade(c, fill); c.text = ""
    p = c.paragraphs[0]
    r = p.add_run(decision.upper()); r.bold = True; r.font.size = Pt(9.5)
    r.font.color.rgb = GREEN if decision == "Opened" else RED
    if decision != "Opened": shade(t.cell(0, 1), "FDECEA")
    r = p.add_run("     PI: %s     Risk: " % owner); r.font.size = Pt(8.5); r.font.color.rgb = GREY
    r = p.add_run(risk); r.font.size = Pt(8.5); r.bold = True; r.font.color.rgb = RISKCOL[risk]
    r = p.add_run("     Confirmed: %s" % by); r.font.size = Pt(8.5); r.font.color.rgb = GREY

    c = t.cell(1, 0); c.text = ""
    p = c.paragraphs[0]; r = p.add_run("Open follow-up"); r.bold = True; r.font.size = Pt(8.5)
    c = t.cell(1, 1); c.text = ""
    p = c.paragraphs[0]; r = p.add_run(follow); r.font.size = Pt(8.5)

    c = t.cell(2, 0); c.text = ""
    p = c.paragraphs[0]; r = p.add_run("From review"); r.bold = True; r.font.size = Pt(8.5)
    c = t.cell(2, 1); c.text = ""
    p = c.paragraphs[0]
    r = p.add_run("\u201c%s\u201d" % quote); r.font.size = Pt(8.5); r.italic = True
    p2 = c.add_paragraph(); r = p2.add_run(src); r.font.size = Pt(7.5); r.font.color.rgb = GREY
    p2.paragraph_format.space_after = Pt(2)

    c = t.cell(3, 0); c.text = ""
    p = c.paragraphs[0]; r = p.add_run("Closed by /\ndate"); r.bold = True; r.font.size = Pt(8.5)
    c = t.cell(3, 1); c.text = ""
    p = c.paragraphs[0]
    r = p.add_run("_" * 46 + "     Date: " + "_" * 18)
    r.font.size = Pt(8.5); r.font.color.rgb = GREY

    d.add_paragraph().paragraph_format.space_after = Pt(5)

d.add_page_break()
para("RECORDED HOLDS — ALL THREE RESOLVED", 12, True, NAVY, after=3)
para("The assessment workbook's Notes column — text that was already there, not written by "
     "this reconciliation — recorded an explicit recommendation to hold three of the "
     "protocols that were opened. Two are now closed on the Director's authority. The "
     "original note text is retained in every case: closures are appended, not substituted, "
     "so the audit trail runs hold \u2192 closure \u2192 authority \u2192 date.",
     9.5, after=5)
ht = d.add_table(rows=4, cols=3); ht.style = "Table Grid"; fixed(ht, [1.25, 4.35, 1.6])
for i, h in enumerate(["Protocol", "Recorded note (verbatim, pre-existing)", "Hold status"]):
    c = ht.cell(0, i); shade(c, "1F4E79"); c.text = ""
    p = c.paragraphs[0]; r = p.add_run(h); r.bold = True; r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
HOLDS = [
 ("4WARDXP", "BM: I have ethical questions about this protocol. Hold this until a patient "
             "is identified.", "CLOSED\nJH 2026-09-09", GREEN),
 ("IXTEND3004\n(as HEMGENIX)",
             "BM: Would hold until participants are confirmed in January 2026.",
             "CLOSED\nJH 2026-09-09", GREEN),
 ("IDBLEED", "BM: slow accrual - enrollment plan? Interim Power analysis? would put this on "
             "hold until a power analysis is done and an enrollment strategy implemented.",
             "MOOT\nstudy closed", GREY),
]
for i, (k, note, stat, col) in enumerate(HOLDS, 1):
    c = ht.cell(i, 0); c.text = ""
    p = c.paragraphs[0]; r = p.add_run(k); r.bold = True; r.font.size = Pt(8.5)
    c = ht.cell(i, 1); c.text = ""
    p = c.paragraphs[0]; r = p.add_run("\u201c%s\u201d" % note)
    r.font.size = Pt(8.5); r.italic = True
    c = ht.cell(i, 2); c.text = ""
    p = c.paragraphs[0]; r = p.add_run(stat); r.bold = True; r.font.size = Pt(8.5)
    r.font.color.rgb = col

d.add_paragraph().paragraph_format.space_after = Pt(4)
para("Closing the 4WARDXP hold does not close the accrual problem", 10, True, RED, after=3)
para("The hold and the feasibility concern are separate findings that happened to share a "
     "row. Feasibility was scored 1 on an estimated 0–1 eligible patients, and 4WARDXP is "
     "still the only one of the 14 opened without any second-reviewer assessment. Its risk "
     "grade stays High on those grounds alone. IXTEND3004 drops to Low — its hold was the "
     "only thing outstanding against it.", 9.5, after=5)
para("IDBLEED's hold was superseded, not satisfied", 10, True, NAVY, after=3)
para("It asked for a power analysis and an enrollment strategy; neither was delivered, and "
     "the study has since been closed to accrual. Worth recording plainly: the concern that "
     "prompted the hold — slow accrual — is what the protocol was ultimately closed for. "
     "Open question: the disposition of data on the 14 patients already enrolled.",
     9.5, after=4)

out = os.path.join(ROOT, "Decision Record %s.docx" % TODAY)
d.save(out)
print("WROTE:", out, os.path.getsize(out), "bytes")
