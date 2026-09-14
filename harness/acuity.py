"""CX -> acuity band. Single source for the cutoffs; see acuity_bands.md.

Imported wherever CX Acuity is written to the portfolio so the code and the
documentation cannot drift, the same way rubric.py single-sources the rubric.
"""
# Refit 2026-09-10 on the 31 protocols scored by BOTH the harness and OPAL.
FIT    = dict(slope=0.1074, intercept=-0.422, r=0.874, r2=0.764, n=31, date='2026-09-10')
CUTS   = (34, 57, 76)          # Low/Moderate, Moderate/High, High/Very High
LABELS = ('Low', 'Moderate', 'High', 'Very High')

def band(cx):
    """CX score (0-100) -> one of LABELS."""
    if cx is None or cx == '': return ''
    cx = float(cx)
    lo, mid, hi = CUTS
    return LABELS[0] if cx < lo else LABELS[1] if cx < mid else \
           LABELS[2] if cx < hi else LABELS[3]

if __name__ == '__main__':
    for s in (0, 33, 34, 56, 57, 75, 76, 100):
        print(f'  CX {s:>3} -> {band(s)}')
