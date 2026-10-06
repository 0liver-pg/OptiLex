import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
EV = 96.485  # kJ/mol per eV
# reported energy errors (eV) from primary sources
errs = {
 "ODAC25 exp. Henry benchmark eSEN CO2 MAE (0.0234 eV)": 0.0234,
 "ODAC25 exp. Henry benchmark UFF CO2 MAE (0.0299 eV)": 0.0299,
 "ODAC25 experimental spread CO2 (0.016 eV)": 0.016,
 "ODAC25 eSEN CO2 ads-energy MAE vs DFT (0.061 eV)": 0.061,
 "ODAC25 eSEN overall MAE (0.077 eV)": 0.077,
 "re-relaxation median shift ODAC23->25 (>0.1 eV)": 0.10,
 "best FF for deformation, CHGNet (0.124 eV)": 0.124,
 "ODAC23 EqV2-large MAE (0.155 eV)": 0.155,
 "ODAC23 k-point systematic error in 7% (>0.2 eV)": 0.20,
}
T = T0
print(f"T0={T0} K, P_CO2_AIR={P_CO2_AIR:.2f} Pa")
print(f"{'error source':58s} {'kJ/mol':>7} {'K_H factor':>11} {'fill@-70 lo..hi':>18} {'Tdes shift C':>13}")
dS = -165.0
for k, e in errs.items():
    kj = e*EV
    fac = math.exp(kj*1e3/(R*T))
    lo = loading(P_CO2_AIR, T, (-70+kj)*1e3, dS, 1.0)
    hi = loading(P_CO2_AIR, T, (-70-kj)*1e3, dS, 1.0)
    dT = desorption_temperature((-70-kj)*1e3, dS, 1e3) - desorption_temperature(-70e3, dS, 1e3)
    print(f"{k:58s} {kj:7.1f} {fac:11.1f} {lo:8.1%}..{hi:6.1%} {dT:13.0f}")
# width of the useful window: fill between 30% and 95% at 420 ppm, 298 K
def dH_for_fill(theta):
    # theta = bp/(1+bp) -> bp = theta/(1-theta)
    bp = theta/(1-theta)
    dG = -R*T*math.log(bp*P_REF/P_CO2_AIR)
    return dG + T*dS
lo, hi = dH_for_fill(0.30), dH_for_fill(0.95)
print(f"\nUseful dH window (30%..95% fill at 420 ppm, dS=-165): {lo/1e3:.1f} .. {hi/1e3:.1f} kJ/mol; width {abs(hi-lo)/1e3:.1f} kJ/mol = {abs(hi-lo)/1e3/EV:.3f} eV")
# Smit critique: ODAC23 criterion -E_bind > 50 kJ/mol vs PrISMa range -50..-10
print(f"ODAC23 criterion 0.5 eV = {0.5*EV:.1f} kJ/mol")
# hit rate arithmetic
print(f"ODAC23 hit rate 135/5079 = {135/5079:.2%}; reproduced 1/135 = {1/135:.2%}")
# water competition: site-blocking two-component Langmuir, what dH_H2O (dS -120?) not modelled; just report p_H2O/p_CO2 ratio
import math
psat25 = 3169.0
for rh in (0.2,0.5,0.8):
    print(f"RH {rh:.0%} at 25C: p_H2O={rh*psat25:.0f} Pa = {rh*psat25/P_CO2_AIR:.0f}x p_CO2; equal-occupancy needs K_CO2/K_H2O = that ratio -> dG gap {R*T*math.log(rh*psat25/P_CO2_AIR)/1e3:.1f} kJ/mol")
