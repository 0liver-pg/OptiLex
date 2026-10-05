import sys; sys.path.insert(0,'climate')
from physics import *
# relative cost per tonne after reload scheme: ((1-a)/N + a + o)/r ; baseline = 1
def rel(a,N,o,r): return ((1-a)/N + a + o)/r
print("saving % (a, N, o=0.12) vs recovered capacity r")
for a in (0.04,0.25,0.40):
  for N in (3,5,10):
    row=[f"{100*(1-rel(a,N,0.12,r)):5.1f}" for r in (1.0,0.9,0.85,0.8,0.7)]
    print(f"a={a:.2f} N={N:2d} breakeven r={rel(a,N,0.12,1):.2f} :", row)
# $/t: base replacement cost 69-1038 $/t
for base in (69,1038):
  for N,r in ((5,1.0),(5,0.85),(3,0.85),(3,0.8)):
    s=1-rel(0.25,N,0.12,r); print(f"base ${base}/t N={N} r={r}: saving ${base*s:.0f}/t ({100*s:.0f}%)")
