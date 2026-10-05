"""Stakeholder-impact arithmetic for coalition_4 (clinker process-CO2 phasedown).
All prices are ASSUMPTIONS (order-of-magnitude, flagged) - not verified this session."""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa
proc = 0.65*44.01/56.08 + 0.015*44.01/40.30   # t CO2 / t clinker (same as coalition_ideas.py)
print(f"process CO2 {proc:.3f} t/t clinker")
# Cost per t cement at clinker ratio 0.71, abatement EUR100-150/t
for cost in (100, 150):
    c = cost*proc*0.71
    # ASSUMED ex-works cement prices: EU ~EUR110-130/t; India ~USD 85-95/t (~EUR 80-88)
    print(f"EUR{cost}/t: {c:.0f} EUR/t cement = {c/130:.0%}-{c/110:.0%} of EU price (ASSUMED 110-130), "
          f"{c/88:.0%}-{c/80:.0%} of Indian price (ASSUMED EUR80-88)")
    for build, label in ((2000, 'EU EUR2000/m2'), (250, 'S8 low-cost housing EUR250/m2 (ASSUMED)')):
        for ci in (0.15, 0.30):
            print(f"   {label}, {ci} t cem/m2: {c*ci/build:.1%} of build cost")
# Effect of a 30% cut by 2035 if met by capture alone vs by clinker ratio 0.71 -> 0.50
print(f"Clinker ratio 0.71->0.50 cuts process CO2/t cement by {1-0.50/0.71:.0%} (meets the 2035 -30% step without CCS)")
# EU: process CO2 already under ETS. Incremental burden vs ETS at ASSUMED EUA EUR70-80
for eua in (70, 80):
    for cost in (100, 150):
        print(f"EU incremental over ETS (EUA {eua}): EUR{max(cost-eua,0)}/t CO2 -> {max(cost-eua,0)*proc*0.71:.0f} EUR/t cement")
