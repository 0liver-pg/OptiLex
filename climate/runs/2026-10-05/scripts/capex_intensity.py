import sys
sys.path.insert(0, 'climate')
from physics import *
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
CRF = crf(0.08, 25)
print(f"CRF 8%/25y = {CRF:.4f}")
projects = {
 # name: (capex USD, design t/yr, actual t/yr)
 "Petra Nova (2017, $1.0bn incl. CHP, 1.4 Mt/yr design; ~1.15 Mt/yr actual 2017-19)": (1.0e9, 1.4e6, 3.8e6*0.9072/3),
 "Boundary Dam 3 (2014, ~C$1.5bn total retrofit ~US$1.1bn, 1 Mt/yr; 0.72 Mt in 2025)": (1.1e9, 1.0e6, 0.721e6),
 "Klemetsrud WtE (2029, NOK 9.5bn ~US$0.9bn, ~0.35-0.4 Mt/yr)": (0.9e9, 0.4e6, 0.4e6*0.9),
}
for k,(capex, design, actual) in projects.items():
    print(f"{k}\n   capex/(t/yr) design ${capex/design:,.0f}; annualised capex per t: design ${capex*CRF/design:.0f}, actual ${capex*CRF/actual:.0f}")
# Capacity-factor sensitivity of NETL NGCC $61/t (2018$, 85% CF); assume capex+fixed O&M share s
for s in (0.5, 0.6, 0.7):
    for cf in (0.85, 0.6, 0.4, 0.25):
        cost = 61*(s*0.85/cf + (1-s))
        print(f"fixed share {s:.0%} CF {cf:.0%}: ${cost:.0f}/t", end="; ")
    print()
# Longship rough per tonne: NOK 34bn incl 10y operation; Brevik 0.4 Mt/yr x 10 y; NL phase 1 1.5 Mt/yr capacity
nok_usd = 0.095
for tonnes in (4e6, 8e6, 15e6):
    print(f"Longship NOK 34bn / {tonnes/1e6:.0f} Mt over 10y = ${34e9*nok_usd/tonnes:,.0f}/t (undiscounted)")
