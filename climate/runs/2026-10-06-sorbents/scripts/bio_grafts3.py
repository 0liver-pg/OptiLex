import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq
GJ = gj_per_tonne
floor_j = min_separation_work(X_AIR, 0.75, 0.99, T0)
print("=== IDEA (allosteric #2). Non-volatile oligomer of the TriH phase-change triamine: cooperative (Hill) switch in humid air")
def hill(p, T, dH, dS, n):
    bp = langmuir_b(dH, dS, T) * p
    return bp**n / (1 + bp**n)
dS = -165.0
for n in (1, 3, 6):
    dH = brentq(lambda x: hill(P_CO2_AIR, T0, x, dS, n) - 0.9, -120e3, -40e3)
    for p_des in (1e3, 1e4):
        Td = brentq(lambda T: hill(p_des, T, dH, dS, n) - 0.1, 250, 700)
        for qmax, w in ((6.0, 1.0), (6.0, 2.0)):
            wc = 0.8 * qmax
            sens = 1500 * (Td - T0) / wc
            heat = -dH + sens + w * DH_VAP_WATER
            print(f"  n={n}, dH {dH/1e3:.0f} kJ/mol, q_max {qmax} mol/kg, {w:.0f} H2O/CO2: unload 90->10% at {p_des/1e3:.0f} kPa needs {Td-273.15:.0f} C; "
                  f"heat {GJ(heat):.2f} GJ/t (rxn {GJ(-dH):.2f}, sens {GJ(sens):.2f}, water {GJ(w*DH_VAP_WATER):.2f}); exergy {GJ(heat*(1-T0/Td)):.2f}; 2nd-law {GJ(floor_j)/(GJ(heat*(1-T0/Td))+0.29):.0%}")
print("  sorbent cost at 4.8 mol/kg working capacity:", ", ".join(f"${sorbent_cost_per_tonne(p, 4.8, c):.0f}/t at ${p}/kg, {c} cycles" for p, c in ((20, 1000), (20, 10000), (50, 10000))))
kg_cycles_per_t = 1000.0 / (4.8 * M_CO2)      # kg-cycles of sorbent per tonne CO2 at 4.8 mol/kg
allowed = 5.0 / 20.0 / kg_cycles_per_t        # kg lost per kg sorbent per cycle for <= $5/t make-up at $20/kg
print(f"  volatility budget: <= $5/t make-up at $20/kg = 0.25 kg sorbent per t CO2 = {allowed*100:.4f}% of the sorbent mass per cycle "
      f"({allowed*100*10000:.0f}% over 10,000 cycles) -> isothermal TGA loss at T_des must be < {allowed*100:.3f}% per cycle")
print(f"  TriH molecule 165 g/mol, 3 NH2 -> 18.2 mmol N/g; a biphenyl-linked dimer (~2 x TAMB minus H2, ~330 g/mol, 6 NH2) keeps 18 mmol N/g; at 1 CO2 per 2 NH2 -> 9 mmol/g ceiling; at 1:1 (water-assisted) 18")
