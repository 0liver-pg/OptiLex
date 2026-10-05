import sys
sys.path.insert(0, 'climate')
from physics import *
import random
GWP=29.8; slope_co2e=30.0; slope_ch4=slope_co2e*GWP
kg_per_mmbtu=19.01
print(f"slope per t CH4: ${slope_ch4:.0f}")
# Marginal incentive per tonne of own CH4 abated, under basin-level settlement
# dRev/dE_i = slope * (P_i/P_basin) * clause_share_i
for share in [0.005,0.02,0.10]:
    for clause in [0.12,0.5,1.0]:
        print(f"basin settle: prod share {share:5.3f} clause cover {clause:4.2f} -> ${slope_co2e*share*clause:6.2f}/t CO2e")
# Patch: asset-level L5 x basin reconciliation factor F = max(1, Inv/sum L5)
for F in [1.0,1.5,2.5]:
    for clause in [0.12,0.5,1.0]:
        print(f"asset settle: F {F:3.1f} clause {clause:4.2f} -> ${slope_co2e*F*clause:6.2f}/t CO2e of reported L5 cut")
# Bias of max(A,B) vs reconciliation-factor estimator, Monte Carlo
random.seed(1)
true=1.5; n=20000
for sd in [0.3,0.5]:
    mx=sum(max(random.gauss(true,sd),random.gauss(true,sd)) for _ in range(n))/n
    print(f"max rule sd {sd}: mean {mx:.3f} bias {mx-true:+.3f} pp")
# Plume inventory detecting 50% of a 1.5% basin; max rule vs factor
print("plume-only 50% detection: L5-scope gap", 1.5*0.5, "pp; max rule always picks inversion")
