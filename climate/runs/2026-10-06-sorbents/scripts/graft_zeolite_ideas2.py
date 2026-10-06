import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

FAN = fan_work_gj_per_tonne(X_AIR, 0.75, 100.0)
print("IDEA 6. Cold-operated weak (oxidation-stabilised) amine: sub-ambient adsorption moves a -58..-66 kJ/mol site into the window")
print("  Site filling at 420 ppm vs temperature (dS -165 J/mol/K):")
print(f"  {'dH kJ/mol':>10}" + "".join(f"{t:>8}C" for t in (-10, 0, 5, 10, 15, 25)))
for dHk in (-58, -60, -62, -64, -66, -70):
    print(f"{dHk:>10}" + "".join(f"{loading(P_CO2_AIR, t+273.15, dHk*1e3, -165.0, 1.0):>9.0%}" for t in (-10, 0, 5, 10, 15, 25)))
print("\n  Residual filling at desorption (T_des, p_des):")
print(f"  {'dH kJ/mol':>10}" + "".join(f"{t:>5}C/{p:>4.0f}Pa" for t, p in [(45,1000),(50,1000),(55,1000),(50,300),(55,300),(55,100)]))
for dHk in (-58, -60, -62, -64, -66, -70):
    print(f"{dHk:>10}" + "".join(f"{loading(p, t+273.15, dHk*1e3, -165.0, 1.0):>12.0%}" for t, p in [(45,1000),(50,1000),(55,1000),(50,300),(55,300),(55,100)]))

print("\n  Cycles (q_max 2.0 mol/kg, cp 1500, 3 mol H2O per mol CO2, no inert, no heat recovery):")
print(f"  {'dH':>5}{'T_ads':>7}{'T_des':>7}{'p_des':>7}{'wc':>7}{'heat GJ/t':>11}{'rxn':>6}{'sens':>6}{'water':>7}{'vac GJe/t':>11}{'work-eq':>9}{'2nd law':>9}")
best = []
for dHk in (-60, -62, -64, -66):
    for tads in (0, 5, 10):
        for tdes, pdes in [(50, 1000.0), (55, 1000.0), (55, 300.0)]:
            cyc = TVSACycle(dH=dHk*1e3, dS=-165.0, q_max=2.0, T_ads=tads+273.15, T_des=tdes+273.15, p_des=pdes, water_coads=3.0)
            if cyc.working_capacity < 0.15:
                continue
            best.append((cyc.work_equivalent_gj_per_t, dHk, tads, tdes, pdes, cyc))
            print(f"  {dHk:>5}{tads:>6}C{tdes:>6}C{pdes:>7.0f}{cyc.working_capacity:>7.2f}{cyc.heat_gj_per_t:>11.2f}"
                  f"{gj_per_tonne(cyc.reaction_heat):>6.2f}{gj_per_tonne(cyc.sensible_heat):>6.2f}{gj_per_tonne(cyc.water_heat):>7.2f}"
                  f"{gj_per_tonne(cyc.vacuum_work):>11.2f}{cyc.work_equivalent_gj_per_t:>9.2f}{cyc.second_law_efficiency:>9.0%}")
ref = reference_amine_cycle()
print(f"\n  reference amine cycle (-70, 25 C -> 100 C / 1 kPa, 2 H2O): wc {ref.working_capacity:.2f}, heat {ref.heat_gj_per_t:.2f}, work-eq {ref.work_equivalent_gj_per_t:.2f} GJ/t")
ref3 = TVSACycle(dH=-70_000.0, dS=-165.0, q_max=2.0, T_des=373.15, p_des=1.0e3, water_coads=3.0)
print(f"  same with 3 H2O: heat {ref3.heat_gj_per_t:.2f}, work-eq {ref3.work_equivalent_gj_per_t:.2f} GJ/t")
# same weak site operated at 25 C, for contrast
for dHk in (-62, -66):
    cyc = TVSACycle(dH=dHk*1e3, dS=-165.0, q_max=2.0, T_ads=298.15, T_des=373.15, p_des=1.0e3, water_coads=3.0)
    print(f"  dH {dHk} at 25 C -> 100 C/1 kPa: wc {cyc.working_capacity:.2f} mol/kg, heat {cyc.heat_gj_per_t:.1f} GJ/t (the penalty the map flags for stabilised amines)")

print("\n  Oxidation budget arithmetic (Li et al. 2024: dry 0.04% CO2 in air, 18 h: ~2% loss at 55 C, 15% at 60 C; Guta 2026 storage: <13%/12 mo at 23 C; 62-66%/2 mo at 40 C in N2 or air, 0 under CO2)")
for label, pct, hours in [("55 C in air", 2.0, 18), ("60 C in air", 15.0, 18), ("23 C storage (upper bound)", 13.0, 365*24), ("40 C storage, CO2-free", 64.0, 61*24)]:
    rate = pct / hours
    print(f"    {label:<28}: {rate:.4f} %/h -> at 48 cycles/day a 1.1e-3 %/cycle budget (0.053 %/day) allows {0.053/rate*60:6.1f} min/day at this condition")
print("    => a 50-55 C cap does not make air contact during regeneration acceptable; the hot step must still be O2-free (vacuum, steam or CO2 blanket)."
      " It removes the 55-90 C air-readmission window entirely and keeps any leak in the 7x-slower regime.")

print("\n  Seasonal capacity of a -62 kJ/mol site (q_max 2, 420 ppm) across a cool-climate year:")
for month, tc in [("Jan", -2), ("Apr", 7), ("Jul", 18), ("Oct", 9)]:
    print(f"    {month} {tc:>3} C: equilibrium loading {loading(P_CO2_AIR, tc+273.15, -62e3, -165.0, 2.0):.2f} mol/kg; working to 55 C/300 Pa: "
          f"{max(0, loading(P_CO2_AIR, tc+273.15, -62e3, -165.0, 2.0) - loading(300.0, 328.15, -62e3, -165.0, 2.0)):.2f}")

print("\nIDEA 2 addendum: water per CO2 if water per N is fixed (~1 H2O per N at 50% RH) and amine efficiency rises")
for eff in (0.15, 0.25, 0.35, 0.45):
    print(f"    efficiency {eff:.2f}: {1.0/eff:4.1f} mol H2O per mol CO2 -> water heat {gj_per_tonne(1.0/eff*DH_VAP_WATER):.1f} GJ/t")

print("\nIDEA 1 addendum: equivalent single-site check of the dual-site result and Li-X")
# Li-X (Wilson): 0.31, 0.47, 0.77, 1.3, 1.9 at 20, 1, -20, -40, -58 C; isosteric heat ~51 kJ/mol (stronger, slower to regenerate)
print("    Li-X measured 0.77 mol/kg at -20 C vs Na-X 1.1: Na-X is the better cold sorbent per Wilson's own data; Li-X's stronger site needs more heat.")
