"""Dossier-level checks for graft_near_1 (HFC-23 fenceline + independent audit). All inputs labelled."""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa  (verifier imported per protocol; HFC-23 destruction has no separation floor)
GWP = 14600            # AR6 GWP100 (sourced)
MEAS = 14.0            # Gg/yr 2023, CEE 2024 (measured, inversion)
EF_RUST = 0.0019       # Rust et al. 2024 measured at one plant
# 1. Implied global HCFC-22 production (modelled): residual 16% of 14 Gg at EF 0.19%
P = MEAS*0.16/EF_RUST/1000  # Mt/yr
print(f"implied HCFC-22 production ~{P:.2f} Mt/yr (consistency only)")
for ef in (0.0019, 0.003, 0.005):
    allowed = P*1e3*ef  # Gg
    cut = MEAS-allowed
    print(f"  threshold EF {ef*100:.2f}%: allowed {allowed:.2f} Gg/yr -> cut {cut:.1f} Gg = {cut*GWP/1e3:.0f} Mt CO2e ({cut/MEAS:.0%} of 2023)")
# 2. Average plant size and signal scaling (plume is linear in Q)
for n in (25, 40):
    avg = P*1e3/n
    s19 = 1336*avg/100; s10 = 7030*avg/100
    print(f"  {n} plants: avg {avg:.0f} kt/yr -> 2-wk sector mean at 2 km {s19:.0f} ppt (EF .19%) vs {s10:.0f} ppt (EF 1%); bkg 37 ppt")
# 3. Threshold per plant
for kt in (30, 100):
    t = kt*1e3*0.003
    print(f"  {kt} kt/yr plant at EF 0.3%: {t:.0f} t HFC-23 = {t*GWP/1e6:.2f} Mt CO2e/yr allowed")
# 4. Split-sample random audit: P(at least one tampered period drawn)
print("split-sample detection P(>=1 tampered period drawn), 26 periods/yr")
for f in (0.10, 0.20):
    print("  f=%.2f: " % f + ", ".join(f"k={k}:{1-(1-f)**k:.0%}" for k in (2, 4, 8, 26)))
# 5. Patched monitoring cost (assumptions from fix step)
GAP = 11.2*GWP/1e3  # Mt CO2e
for lab, n, base, uplift, survey in (("low", 25, .15, .10, .05), ("high", 40, .40, .20, .10), ("critic-high", 40, .95, .20, .10)):
    tot = n*(base*(1+uplift)+survey)
    print(f"  {lab}: ${tot:.1f}M/yr -> ${tot/GAP:.3f}/t over full 163 Mt gap; ${tot/(GAP*0.3):.3f}/t if only 30% closed")
# 6. Destruction cost per t HCFC-22 (cross-check hfc23_stake.py): co-production 1.5-3%, $0.1-1/t CO2e
for cp, c in ((0.015, 0.1), (0.03, 1.0)):
    print(f"  co-prod {cp:.1%}, ${c}/tCO2e -> ${cp*GWP*c:.0f} per t HCFC-22")
