import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
GJ = gj_per_tonne
print("=== A. Purge-gas confound: temperature to unload a Langmuir site to 20% vs CO2 partial pressure in the desorption gas")
for dH in (-60e3, -70e3, -80e3):
    row = []
    for p in (50, 100, 1e3, 1e4, 1e5):
        row.append(f"{p:>7.0f} Pa: {desorption_temperature(dH, -165.0, p) - 273.15:5.0f} C")
    print(f"  dH {dH/1e3:.0f} kJ/mol ->", " | ".join(row))
print("  (N2/Ar purge keeps p_CO2 at ~50-1000 Pa, so 'regenerates at 60-80 C under N2' does not mean pure CO2 at 60-80 C)")

print("\n=== B. Is 0.94 GJ/t regeneration heat (reported for a biphasic IL, ES&T 2026) compatible with DAC-strength binding?")
q = 0.94e9 / 1e3 * M_CO2  # J/mol
print(f"  0.94 GJ/t = {q/1e3:.1f} kJ/mol CO2 total heat")
dG = dG_for_half_loading()
for dS in (-165.0, -120.0, -80.0):
    print(f"  dS {dS:.0f} J/mol/K: binding enthalpy for half loading at 420 ppm = {(dG + T0*dS)/1e3:.1f} kJ/mol "
          f"= {GJ(-(dG + T0*dS)):.2f} GJ/t reaction heat alone")
print(f"  entropy that would make 41 kJ/mol sufficient for half loading: {(-q - dG)/T0:.0f} J/mol/K")
print(f"  second-law check: heat at 100 C carries exergy {q*(1-T0/373.15)/1e3:.1f} kJ/mol vs floor "
      f"{min_separation_work(X_AIR, 0.75, 0.99, T0)/1e3:.1f} kJ/mol (99% pure); 41 kJ/mol heat below ~{T0/(1-min_separation_work(X_AIR,0.75,0.99,T0)/q)-273.15:.0f} C cannot reach the floor")

print("\n=== C. High capacity as the lever on sensible heat (N5-dGA-like vs reference), T_des 80 C, cp 1500 J/kg/K")
for wc in (0.5, 1.04, 2.0, 4.0, 6.2):
    sens = 1500.0 * (353.15 - T0) / wc
    print(f"  working capacity {wc:4.2f} mol/kg: sensible {GJ(sens):.2f} GJ/t; + reaction 70 kJ/mol {GJ(70e3):.2f} -> {GJ(sens+70e3):.2f} GJ/t before water")
print(f"  water co-desorption: each mol H2O per mol CO2 adds {GJ(DH_VAP_WATER):.2f} GJ/t; 3.4 GJ/t total leaves room for "
      f"{(3.4 - GJ(1500*55/6.2 + 70e3))/GJ(DH_VAP_WATER):.1f} mol H2O/mol CO2 at wc 6.2 and dH -70")

print("\n=== D. Water burden of a hydrophilic framework (mmen-Mg2(dobpdc): 1.5 mol CO2/kg at 400 ppm, water up to 40 mol/kg at 90% RH)")
for w in (3.0, 10.0, 40.0):
    print(f"  {w:4.0f} mol H2O/kg co-desorbed with 1.5 mol CO2/kg: {w/1.5:.1f} mol/mol -> water heat {GJ(w/1.5*DH_VAP_WATER):.1f} GJ/t")

print("\n=== E. Charged-sorbent: reported 0.14 -> 0.08 mol/kg (RH 11 -> 38%), sensible heat at dT = 65 K, cp 620 J/kg/K (reported)")
for wc in (0.14, 0.08):
    print(f"  wc {wc}: sensible {GJ(620*65/wc):.1f} GJ/t (reported totals 6.5 and 11.4 GJ/t)")
