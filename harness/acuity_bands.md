# CX Acuity bands

Derived 2026-09-09 from the 24 protocols scored by BOTH the complexity harness
and HEM_OPAL_scores.xlsx.

    OPAL = 0.1022 x CX - 0.368        r = 0.854, r2 = 0.730, n = 24

OPAL's own band boundaries (midpoints of its observed ranges, 86-study set)
mapped back through that fit:

    OPAL 3.25 -> CX 35     Low / Moderate
    OPAL 5.75 -> CX 60     Moderate / High
    OPAL 7.75 -> CX 79     High / Very High

    Low  < 35 | Moderate 35-59 | High 60-78 | Very High >= 79

Agreement with OPAL bands on the 24 overlaps: 19/24 exact (79%), 24/24 within
one band (100%).

CAVEAT: the overlap contains only ONE OPAL-High study (BDSTEM), so the
Moderate/High and High/Very High boundaries rest on the regression, not on
observed High-band cases. Refit once more High-band protocols are scored.
