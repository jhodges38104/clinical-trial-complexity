# -*- coding: utf-8 -*-
"""
Committee decisions for the 14 protocols reviewed 20 Aug - 1 Oct 2025.

12 protocols were OPENED. IDBLEED was CLOSED TO ACCRUAL. VINGT was TABLED.
All confirmed by JH on 2026-09-09. Nothing here is inferred.

IDBLEED was opened at review and subsequently closed to accrual. Its decision is
recorded as a reversal, not as a refusal to open -- 14 patients had already been
enrolled, so "Declined" would misstate what happened.

The `follow_up` and `risk` fields are different in kind from the decision: they
record concerns raised in the review documents that were NOT resolved at the time
the protocol opened. Because these studies are now open, those concerns are live
accrual and delivery risks rather than gating questions -- which is what makes
them worth tracking.

risk grades the documented threat to successful accrual/completion:
  High         opened despite an explicit feasibility problem
  Medium-High  material unresolved funding or accrual concern
  Medium       methodological or operational concern, accrual plausible
  Low          no substantive unresolved concern
"""

# (key, decision, confirmed_by, basis_quote, source, follow_up, owner, risk)
DECISIONS = [
 ("X4WARDXP", "Opened", "JH 2026-09-09",
  "Feasibility: 1  /  Feasible? 0-1 potential patients at St Jude",
  "4WARDXP Manorixafor review.docx",
  "HOLD CLOSED by JH 2026-09-09. The workbook records \"BM: I have ethical questions about "
  "this protocol. Hold this until a patient is identified.\" - that hold is now closed on the "
  "Director's authority; the original note is retained. RISK REMAINS HIGH ON SEPARATE "
  "GROUNDS: closing the hold does not change the accrual problem. The single review estimated "
  "0-1 eligible patients at St. Jude, scored Feasibility 1, and no second reviewer ever "
  "assessed this protocol. It also carries a GCSF-resistance requirement and a full year "
  "before open label. Accrual should be monitored explicitly.",
  "Wlodarski", "High"),

 ("LIVBX", "Opened", "JH 2026-09-09",
  "CTFO is reviewing for cost analysis  /  No patient reimbursement built in - so "
  "recruitment is difficult",
  "SCORING LIVBX DM 10.1.docx",
  "8 eligible patients at SJ, reviewers expected 1-2 to enrol. Biopsies performed at "
  "Methodist; hemophilia patients must fly in with no patient reimbursement built in. "
  "Confirm the CTFO cost analysis closed before accrual is expected. Reviewers questioned "
  "whether 1-2 patients would be informative at all.",
  "Reiss", "High"),

 ("LTFAGTHB", "Opened", "JH 2026-09-09",
  "Important study but logistically challenging and no funding  /  I don't see full "
  "protocol, just the intake form",
  "SCORING LTFUAGT4HB DM 9.24.docx",
  "Scored 30/30 by both reviewers - but both scored from the intake form, not a full "
  "protocol. 15-year follow-up of 14 patients across many sites with no funding "
  "identified. Obtain the full protocol and settle the funding route.",
  "Reiss", "Medium-High"),

 ("CHITIN", "Opened", "JH 2026-09-09",
  "Mission: Can we do these studies here in Mitch's lab and not send to Phil?  /  Need "
  "justification for the coagulation testing",
  "SCORING CHITIN-1.docx; CHITIN review.docx",
  "Four clarifications were requested and none is recorded as resolved: (1) justify the "
  "coagulation testing, which has no statistical plan and no power at n=4/group; (2) can "
  "the assays run in Mitch's lab at SJ rather than shipping all samples out; (3) define "
  "'severe' ACU; (4) justify the 3-year stable HbF requirement.",
  "Jesudas", "Medium"),

 ("MIPICS", "Opened", "JH 2026-09-09",
  "Mission - 0/5> 5/5 We will collect same samples for our biobank to make it worthwhile",
  "SCORING MiPICS DM 9.9.docx",
  "CONDITION AGREED IN REVIEW: the same samples are drawn for the St. Jude SCD biobank, "
  "which resolved the conflict that scored Mission 0/5 and that the assessment workbook "
  "records as \"DM: ? Conflict with internal research objectives; BM: Conflict\". That "
  "conflict does appear resolved. Still unresolved: no statistical plan provided, minimal "
  "funding, and sample-fatigue risk to other SJ studies.",
  "Takemoto", "Medium"),

 ("RHEMEDY", "Opened", "JH 2026-09-09",
  "Feasibility; 3 but only agreed to do one patient",
  "SCORING RHEMEDY.docx",
  "LIMITED TO ONE PATIENT per the review document. Inpatient research support model still "
  "to be settled: CRN coverage (Oncology/BMT model), hospitalist buy-in, inpatient Heme "
  "APPs. Drug must be given <12h of first IV opioid, so patients require pre-consent in "
  "clinic - a coordination burden that was flagged but not resolved.",
  "Persaud", "Medium"),

 ("PNHIPTA", "Opened", "JH 2026-09-09",
  "Will Marcin treat as per the protocol? He has reportedly said that he will take "
  "patients to transplant in 6 months regardless of the protocol (protocol is 1 year)",
  "PNHITPA review.docx",
  "Open question recorded but not resolved: PI commitment to the 1-year protocol window "
  "rather than proceeding to transplant at 6 months. 2 eligible patients identified. NOTE "
  "two reviewer documents score this 100% and 76% - resolve which is canonical.",
  "Wlodarski", "Medium"),

 ("AG348_C28 AND C29", "Opened", "JH 2026-09-09",
  "Feasibility - 5/5 but need to confirm eligible and interested subjects",
  "SCORING AG 348 028 and 029 DM 10.1.docx",
  "Confirm eligible AND interested subjects. Two separate protocols - C-028 "
  "(non-transfusion-dependent) and C-029 (transfusion-dependent) - tracked as one row. "
  "Pharma-funded. Sibling of AGPKD: same drug (mitapivat/AG-348), same PI, different "
  "indication.",
  "Rai", "Low-Medium"),

 ("LEAP", "Opened", "JH 2026-09-09",
  "Open. Have enrolled one patient  /  can we change data collection by making it single use?",
  "SCORING LEAP DM 10.1.docx",
  "Already open with 1 patient enrolled since May 2024, so this confirms a continuation. "
  "Both reviewers independently asked whether data collection can be converted to "
  "single-use given there is no funding. That conversion is still open.",
  "Jesudas", "Low-Medium"),

 ("IXTEND3004", "Opened", "JH 2026-09-09",
  "DM: agree  /  Feasibility: 3 - have not asked patients yet",
  "IXTEND3004 review.docx",
  "HOLD CLOSED by JH 2026-09-09. The workbook records \"BM: Would hold until participants are "
  "confirmed in January 2026\" - that hold is now closed on the Director's authority; the "
  "original note is retained. No substantive concern remains: two potential patients were "
  "identified at review and the reviewer endorsed the protocol (\"DM: agree\"). Recorded as "
  "HEMGENIX in the assessment workbook.",
  "Jesudas", "Low"),

 ("MYPERS", "Opened", "JH 2026-09-09",
  "16 enrolled/ 40, 3 patients, 13 controls  /  the study is now accruing well",
  "SCORING MYPERS DM 9.9 .docx; MYPERS Protocol score sheet.docx",
  "Already accruing since 2023; confirms a continuation. Midpoint analysis planned at "
  "5:5:10. Non-blocking questions raised: age-range generalisability, high IND monitoring "
  "burden.",
  "Rai", "Low"),

 ("SCDSTEMM", "Opened", "JH 2026-09-09",
  "Important study  /  Feasibility - 3/5 adult study",
  "SCORING SCD STEMM DM 10.1.docx",
  "Internally funded. Only feasibility was discounted, solely because it is an adult "
  "study. No unresolved conditions.",
  "Leonard", "Low"),
]

# IDBLEED opened, then closed to accrual.
CLOSED = ("IDBLEED", "Closed to accrual", "JH 2026-09-09",
          "BM: slow accrual - enrollment plan? Interim Power analysis? would put this on hold "
          "until a power analysis is done and an enrollment strategy implemented",
          "Assessment workbook Notes (pre-existing); IDBLEED review.docx",
          "CLOSED TO ACCRUAL. Opened at review, since closed. Accrual reached 14 of a planned "
          "43 in two years, and only 1 of those 14 had even a partial positive ED score. The "
          "power analysis requested from Guolion (sp?) and the enrollment strategy asked for "
          "in the workbook were never recorded as delivered; closure supersedes both. The "
          "reviewer who recommended holding this protocol pending exactly those two items was "
          "borne out. OPEN QUESTION: what happens to the data on the 14 patients already "
          "enrolled - analysis, publication, or archive?",
          "Jesudas", "n/a")

# VINGT was never opened.
TABLED = ("VINGT", "Tabled", "JH 2026-09-09",
          "Score: 12/30  /  Multiple site subcontracts of an unfunded study seems like a big ask",
          "SCORING VINGT DM 9.24.docx",
          "Lowest-scoring protocol of the 14. Multi-site subcontracts, MTAs and DUAs for an "
          "unfunded study; only the intake form was reviewed, not a full protocol. No revisit "
          "date set.",
          "Jesudas", "n/a")

RISK_ORDER = {"High": 0, "Medium-High": 1, "Medium": 2, "Low-Medium": 3, "Low": 4, "n/a": 5}
DECISIONS.sort(key=lambda d: (RISK_ORDER[d[7]], d[0]))
NOT_OPEN = [CLOSED, TABLED]
BY_KEY = {d[0]: d for d in DECISIONS}
for _d in NOT_OPEN: BY_KEY[_d[0]] = _d
ALL = DECISIONS + NOT_OPEN
