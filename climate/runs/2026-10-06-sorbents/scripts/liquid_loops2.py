import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99)); kWh=3.6e-3
print("--- membrane-free acid/base (Nat Commun 2025) applied to carbonate release ---")
for Eab in (0.060, 0.066, 0.073, 0.145):
    for n in (1, 2):
        e = Eab*3.6e6*n
        print(f"  E_ab {Eab} kWh/mol, {n} H+/CO2: {e/1e3:.0f} kJ/mol = {gj_per_tonne(e):.1f} GJ/t(e)")
print("--- PNAS 2026 two-stage ---")
for gj in (4.5, 2.4, 2.1, 10.0):
    print(f"  {gj} GJ/t = {gj*M_CO2*1e3:.0f} kJ/mol = {gj/kWh:.0f} kWh/t ; 2nd-law {floor/gj:.1%}")
# their liquid: 0.32 M KOH + 1.34 M K2CO3 -> H+ per CO2
print(f"  H+ per CO2 for 0.32 M KOH + 1.34 M K2CO3: {(0.32+2*1.34)/1.34:.2f}")
V=lambda dpH: R*T0*math.log(10)*dpH/FARADAY
# staged Nernst: OH- neutralisation at pH13.5->~12 etc. crude: stage1 2.24-1 = 1.24 H+/CO2 at dpH~ (13.5-9), stage2 1 H+ at dpH ~ (9-~4)?
e1 = electrochemical_work((0.32+1.34)/1.34, V(14-9.0)); e2 = electrochemical_work(1.0, V(14-6.0))
print(f"  crude Nernst floor two-stage (catholyte pH14): stage1 {(0.32+1.34)/1.34:.2f} H+ x dpH5 = {e1/1e3:.0f} kJ/mol; stage2 1 H+ x dpH8 = {e2/1e3:.0f} kJ/mol; total {gj_per_tonne(e1+e2):.2f} GJ/t")
print(f"  AQDS dual electrolyser 257 kJ/mol = {gj_per_tonne(257e3):.2f} GJ/t")
print("--- direct ocean capture seawater volume ---")
dic = 2.2  # mol/m3
for frac in (1.0, 0.6):
    v = 1e6/44.01/(dic*frac)
    print(f"  extract {frac:.0%} of DIC: {v:.0f} m3 seawater per t CO2; pumping at 0.5-2 kWh/m3 would be {v*0.5/1000:.1f}-{v*2/1000:.1f} MWh/t if not shared")
    print(f"    vs air: {air_volume_per_tonne(X_AIR,0.75):.2e} m3 air/t; mass ratio water/air = {v*1025/(air_volume_per_tonne(X_AIR,0.75)*1.18):.1f}")
print("--- Ca(OH)2 passive flux vs KOH packing ---")
for f in (12, 117):
    print(f"  Dostie flux {f} kg/m2/yr -> 1 Mt/yr needs {1e9/f/1e4:.0f} ha tray area; 1 kt/yr needs {1e6/f:.0f} m2")
print(f"  lime layers 2 t/ha/day = {2000*365/1e4:.0f} kg/m2/yr")
print(f"  KOH packing (KL 1.3 mm/s): 17-31 kg/m2 wetted/yr; CE inlet-area basis 22 t/m2/yr")
print("--- K-sarcosinate contactor (ORNL 2025): fan energy at measured capture efficiency ---")
for eff, dp, lab in [(0.339, 60, '3M K-SAR 20C'), (0.203, 69.2, '3M K-SAR -5C'), (0.421, 52.5, '3M K-SAR 35C')]:
    print(f"  {lab}: capture {eff:.1%}, dP {dp} Pa -> fan {fan_work_gj_per_tonne(X_AIR, eff, dp, 0.6)/kWh:.0f} kWh/t; air {air_volume_per_tonne(X_AIR, eff):.2e} m3/t")
print("--- water loss in K-SAR test ---")
print("  6.5 L of 20 L lost in 10 h (1 M K-SAR), ~20% in 8 h (3 M)")
print("--- sarcosine thermal loss ---")
# 21% amine loss after 700 h at 120C -> first-order k
k = -math.log(1-0.21)/700
print(f"  k = {k:.2e} /h at 120C; half-life {math.log(2)/k:.0f} h; if solvent spends 5% of time hot: effective half-life {math.log(2)/k/0.05/8760:.1f} yr")
print("--- BIG regeneration 7.0-10.2 kJ/g ---")
for x in (7.0, 10.2): print(f"  {x} kJ/g = {x} GJ/t = {x*44.01:.0f} kJ/mol; 2nd-law at 120C heat: {floor/(x*(1-T0/393.15)):.1%}")
print(f"  CaCO3 loop for comparison: solubility-driven; calcination 178 kJ/mol")
