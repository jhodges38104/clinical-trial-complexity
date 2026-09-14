# CX Acuity bands

Refit **2026-09-10** from the 31 protocols scored by BOTH the complexity harness
and HEM_OPAL_scores.xlsx. Cutoffs are defined in code in `acuity.py` — import
`band()` rather than re-deriving them.

    OPAL = 0.1074 x CX - 0.422        r = 0.874, r2 = 0.764, n = 31

OPAL's own band boundaries (midpoints of its observed ranges, 86-study set)
mapped back through that fit:

    OPAL 3.25 -> CX 34.2   Low / Moderate
    OPAL 5.75 -> CX 57.5   Moderate / High
    OPAL 7.75 -> CX 76.1   High / Very High

    Low  < 34 | Moderate 34-56 | High 57-75 | Very High >= 76

Agreement with OPAL bands on the 31 overlaps: 24/31 exact (77%), 31/31 within
one band (100%).

## What changed from the 2026-09-09 fit (n = 24)

| | 2026-09-09 | 2026-09-10 |
|---|---|---|
| n | 24 | 31 |
| slope / intercept | 0.1022 / -0.368 | 0.1074 / -0.422 |
| r / r2 | 0.854 / 0.730 | 0.874 / 0.764 |
| cutoffs | 35 / 60 / 79 | 34 / 57 / 76 |
| exact agreement | 19/24 (79%) | 24/31 (77%) |
| within one band | 24/24 (100%) | 31/31 (100%) |

**The previous CAVEAT is resolved.** The 24-protocol overlap contained only one
OPAL-High study (BDSTEM), so the upper two boundaries rested on the regression
rather than observed cases. The 31-protocol overlap contains 4 High and 4 Very
High, so both boundaries are now supported by data.

**The refit reclassifies nothing.** No CX score in the 42-protocol scored set
falls between the old and new cutoffs, so every protocol keeps its existing
acuity label. Exact agreement moves 79% -> 77% only because the denominator grew
from 24 to 31; the same protocols agree. This is a better-grounded fit, not a
better-performing one.
