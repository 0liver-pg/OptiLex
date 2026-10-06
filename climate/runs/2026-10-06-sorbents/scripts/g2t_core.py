import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq

print("=== Verifier reference reproduction ===")
ref = reference_amine_cycle()
print(f"ref wc {ref.working_capacity:.3f} mol/kg heat {ref.heat_gj_per_t:.2f} GJ/t work-eq {ref.work_equivalent_gj_per_t:.2f} eff {ref.second_law_efficiency:.2%}")
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99, T0))
print(f"floor {floor:.3f} GJ/t; dG half-load {dG_for_half_loading()/1e3:.2f} kJ/mol")

# ---------- 1. Hill / univariant step vs Langmuir ----------
def hill_theta(p, T, dH, dS, n):
    lx = n * math.log(langmuir_b(dH, dS, T) * p)
    if lx > 50: return 1.0
    x = math.exp(lx)
    return x / (1 + x)

def T_for_theta(p, dH, dS, theta, n=1.0):
    # solve hill_theta = theta
    return brentq(lambda T: hill_theta(p, T, dH, dS, n) - theta, 200, 800)

class HillCycle(TVSACycle):
    n: float = 1.0
    def __init__(self, n=1.0, **kw):
        super().__init__(**kw); self.n = n
    @property
    def q_ads(self): return self.q_max * hill_theta(self.p_ads, self.T_ads, self.dH, self.dS, self.n)
    @property
    def q_des(self): return self.q_max * hill_theta(self.p_des, self.T_des, self.dH, self.dS, self.n)

print("\n=== Step sharpness: same dH -70 kJ/mol, dS -165, q_max 2; ambient fill and T to unload to 10% at 1 kPa ===")
for n in (1, 2, 4, 8, 50):
    fill = hill_theta(P_CO2_AIR, T0, -70e3, -165, n)
    Td = T_for_theta(1e3, -70e3, -165, 0.10, n)
    cyc = HillCycle(n=n, dH=-70e3, dS=-165, q_max=2.0, T_des=Td, p_des=1e3, water_coads=0.0)
    print(f"n={n:>3}: fill@420ppm {fill:5.1%}  T_des(10%@1kPa) {Td-273.15:6.1f} C  wc {cyc.working_capacity:.2f}  heat {cyc.heat_gj_per_t:.2f} GJ/t  work-eq {cyc.work_equivalent_gj_per_t:.2f}")

# ---------- 2. Entropy-steep sites at fixed ambient fill ----------
print("\n=== Entropy-steep sites: hold fill at 420 ppm/25 C = 65%; unload to 20% at 1 kPa ===")
def dH_for_fill(fill, dS, p=P_CO2_AIR, T=T0):
    bp = fill / (1 - fill); b = bp / p
    dG = -R * T * math.log(b * P_REF)
    return dG + T * dS
rows = []
for dS in (-120, -165, -200, -230, -260, -300):
    dH = dH_for_fill(0.65, dS)
    Td = desorption_temperature(dH, dS, 1e3, 0.2)
    for wat in (2.0, 6.0):
        cyc = TVSACycle(dH=dH, dS=dS, q_max=2.0, T_des=Td, p_des=1e3, water_coads=wat)
        Q = cyc.heat_gj_per_t
        lift = (Td + 5) - (T0 - 5)
        cop = 0.5 * (Td + 5) / lift
        print(f"dS {dS:5d} dH {dH/1e3:7.1f} kJ  T_des {Td-273.15:6.1f} C  water {wat:.0f}  wc {cyc.working_capacity:.2f}  "
              f"heat {Q:5.2f} GJ/t (rxn {gj_per_tonne(cyc.reaction_heat):.2f}, sens {gj_per_tonne(cyc.sensible_heat):.2f})  "
              f"work-eq {cyc.work_equivalent_gj_per_t:.2f}  HP COP {cop:.2f} -> elec {Q/cop:.2f} GJ/t = {Q/cop/3.6*1000:.0f} kWh/t")
