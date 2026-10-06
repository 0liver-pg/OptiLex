import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
from scipy.optimize import brentq
GJ = gj_per_tonne
exec(open('climate/runs/2026-10-06-sorbents/scripts/g2t_polymer_conf.py').read().split('print("=== 1.')[0])
# re-define frumkin from polymer script
src = open('climate/runs/2026-10-06-sorbents/scripts/g2t_polymer_conf.py').read()
start = src.index('def theta_frumkin'); end = src.index('print(f"{\'J kJ/mol\'')
exec(src[start:end])

print("=== Anti-cooperativity (Frumkin J) from diamine pKa splits (CRC values) ===")
diam = {'ethylene (PEI-like)': (9.93, 6.85), 'propylene (PPI-like)': (10.55, 8.88), 'butylene': (10.80, 9.35), 'hexylene': (11.02, 10.24)}
for k, (p1, p2) in diam.items():
    w = (p1 - p2 - math.log10(4))*2.303*R*T0
    print(f"  {k:22s}: pKa split {p1-p2:.2f} -> pair repulsion {w/1e3:.1f} kJ/mol (after statistical log4)")
print("  fixed intrinsic site dH -75 kJ/mol, dS -165: ambient fill and T to unload to 10% at 1 kPa vs J")
for J in (-14e3, -6e3, -4.9e3, -1.2e3, 0.0):
    f = theta_frumkin(P_CO2_AIR, T0, -75e3, -165, J)
    Td = T_for(1e3, -75e3, -165, J, 0.10)
    print(f"   J {J/1e3:6.1f}: fill@420ppm {f:.2f}  T(10%@1kPa) {Td-273.15:.0f} C")
print("  same ambient fill (65%) by adjusting dH: see g2t_polymer_conf.py table (J -15 -> 150 C, 7.67 GJ/t; J 0 -> 105 C, 6.07; J +10 -> 77 C, 5.05)")
for J in (-14e3, -6e3, -1.2e3):
    dH = brentq(lambda h: theta_frumkin(P_CO2_AIR, T0, h, -165, J) - 0.65, -120e3, -40e3)
    Td = T_for(1e3, dH, -165, J, 0.10)
    wc = 2*(0.65 - theta_frumkin(1e3, Td, dH, -165, J)); sens = 1500*(Td-T0)/wc; heat = -dH + sens + 2*44e3
    print(f"   J {J/1e3:6.1f} at 65% fill: dH {dH/1e3:.1f}, T(10%@1kPa) {Td-273.15:.0f} C, heat {GJ(heat):.2f} GJ/t (2 H2O/CO2)")

print("\n=== Purge-free predictions for published low-T claims (verifier Langmuir, dS -165 unless stated) ===")
# epoxide-PEI: dH -66 (Min 2018 calorimetry, flue gas)
for name, dH in (("epoxybutane-PEI (dH -66)", -66e3), ("COF-999-like (Qst 53, dS fitted)", -53e3)):
    dS = -165.0 if 'PEI' in name else None
    if dS is None:
        # fit dS so that 0.91 mmol/g at 40 Pa with q_max 2.5 (assumed) at 25 C
        th = 0.91/2.5; bp = th/(1-th); b = bp/40
        dS = (dH + R*T0*math.log(b*P_REF))/T0
    for Td_c in (45, 60, 80):
        cyc = TVSACycle(dH=dH, dS=dS, q_max=2.0 if 'PEI' in name else 2.5, T_des=Td_c+273.15, p_des=1e3)
        cyc5 = TVSACycle(dH=dH, dS=dS, q_max=2.0 if 'PEI' in name else 2.5, T_des=Td_c+273.15, p_des=100.0)
        print(f"  {name}: dS {dS:.0f}; fill@420ppm {cyc.q_ads/cyc.q_max:.2f}; T_des {Td_c} C: wc into 1 kPa {cyc.working_capacity:.2f} mol/kg, into 0.1 kPa {cyc5.working_capacity:.2f}")
print("  TriH (from dry 400 ppm isobar holding CO2 to ~87-95 C): purge-free 1 kPa release 131-147 C (g2t_polymer_conf.py) vs fast volatilisation at 120 C")
print("  Kanoh NaCH (Na2CO3/nanocarbon): two-gas release; 80 C with p_w pinned at 1 kPa gives 25 kPa CO2; at 0.26 kPa gives 96 kPa (g2t_windows.py) -> survives a purge-free test")

print("\n=== Sorbent cost checks (verifier) ===")
print(f"  Na2CO3/carbon $2/kg, wc 3.0, 2,000 cycles: ${sorbent_cost_per_tonne(2,3.0,2000):.1f}/t; wc 1.5: ${sorbent_cost_per_tonne(2,1.5,2000):.1f}/t; $5/kg wc 1.5 1,000 cycles: ${sorbent_cost_per_tonne(5,1.5,1000):.1f}/t")
print(f"  TriH@silica (assume $50/kg, wc 2.0): 1,000 cycles ${sorbent_cost_per_tonne(50,2.0,1000):.0f}/t, 10,000 ${sorbent_cost_per_tonne(50,2.0,10000):.0f}/t")
print(f"  LCST microgel film ($30/kg, wc 1.35-2.0): 2,000 cycles ${sorbent_cost_per_tonne(30,1.35,2000):.0f}-{sorbent_cost_per_tonne(30,2.0,2000):.0f}/t; 10,000 ${sorbent_cost_per_tonne(30,1.35,10000):.0f}-{sorbent_cost_per_tonne(30,2.0,10000):.0f}/t")
print(f"  spaced polyamine/silica ($20/kg): wc 1.04 (ref) vs 1.4: 5,000 cycles ${sorbent_cost_per_tonne(20,1.04,5000):.0f} vs ${sorbent_cost_per_tonne(20,1.4,5000):.0f}/t")
print(f"  productivity Na x0.8 wc 3.0 at 6 cycles/day: {productivity(3.0,6):.2f} kg/kg/day; at 2 cycles/day {productivity(3.0,2):.2f}")
