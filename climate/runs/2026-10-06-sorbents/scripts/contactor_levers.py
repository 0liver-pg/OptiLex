import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
"""Contactor / cycle / process-integration levers for sorbent DAC, using OptiLex verifiers.

All cases start from the reference solid-amine-like cycle (dH -70 kJ/mol, q_max 2 mol/kg, 100 C,
1 kPa CO2). Each block changes ONE lever so the size of each lever is visible.
"""
import math
from dataclasses import replace

ref = reference_amine_cycle()
wc = ref.working_capacity


def show(label, c):
    print(f"{label:<58} heat {c.heat_gj_per_t:6.2f} GJ/t = rxn {gj_per_tonne(c.reaction_heat):.2f} "
          f"+ sens {gj_per_tonne(c.sensible_heat):.2f} + water {gj_per_tonne(c.water_heat):.2f} | "
          f"work-eq {c.work_equivalent_gj_per_t:.2f}")


print("== 1. Reference ==")
show("reference (2 mol H2O/mol CO2, no inert mass)", ref)

print("\n== 2. Water co-desorption (mol H2O per mol CO2) ==")
for w in (0, 1, 2, 3.8, 8, 15):
    show(f"water_coads = {w}", replace(ref, water_coads=w))

print("\n== 3. Parasitic thermal mass (kg structure/housing heated per kg sorbent, cp 900 J/kg/K) ==")
for m in (0, 1, 3, 5, 10, 14):
    show(f"inert_mass_ratio = {m}", replace(ref, inert_mass_ratio=m))
# washcoated monolith with 6.9 wt% active material (Stampi-Bombelli 2024): 13.5 kg inert per kg active
show("6.9 wt% washcoat monolith (13.5 kg inert/kg)", replace(ref, inert_mass_ratio=13.5))

print("\n== 4. Sensible heat recovery between beds ==")
for hr in (0, 0.3, 0.5, 0.7):
    show(f"heat_recovery = {hr} (inert ratio 3)", replace(ref, inert_mass_ratio=3, heat_recovery=hr))

print("\n== 5. Working capacity actually used per cycle (short cycles use a fraction of equilibrium wc) ==")
# The verifier's sensible term scales as 1/wc. Emulate partial use by scaling q_max.
for frac in (1.0, 0.6, 0.35, 0.2):
    c = replace(ref, q_max=ref.q_max * frac, inert_mass_ratio=3)
    print(f"  used fraction {frac:4.2f}: wc {c.working_capacity:.2f} mol/kg, heat {c.heat_gj_per_t:6.2f} GJ/t "
          f"(sens {gj_per_tonne(c.sensible_heat):.2f})")

print("\n== 6. Heat pump: electricity needed if regeneration heat is delivered by a heat pump ==")
for label, c in (("ideal-ish cycle (ref)", ref),
                 ("realistic (inert 3, water 4)", replace(ref, inert_mass_ratio=3, water_coads=4)),):
    for cop in (1.0, 2.0, 3.0):
        el = c.heat_gj_per_t / cop
        print(f"  {label:<30} COP {cop:.0f}: {el:5.2f} GJ_e/t = {el/3.6*1000:5.0f} kWh/t "
              f"-> ${energy_cost_floor(el, 50):.0f}/t at $50/MWh, ${energy_cost_floor(el, 30):.0f}/t at $30/MWh")
T_h, T_c = 373.15, 288.15
print(f"  Carnot COP for 15 C -> 100 C lift: {T_h/(T_h-T_c):.2f}; with latent-heat recovery from condensing "
      f"product steam at ~60 C: {T_h/(T_h-333.15):.2f}")

print("\n== 7. Air supply: face-area productivity and fan work ==")
mol_m3 = P0 / (R * T0) * X_AIR
for v in (1.0, 2.0, 3.0, 5.0):
    for cf in (0.5, 0.75):
        kg_day = mol_m3 * v * cf * M_CO2 * 86400
        print(f"  v {v:.0f} m/s, capture {cf:.0%}: {kg_day:6.1f} kg CO2/m2-face/day = {kg_day*365/1000:5.1f} t/m2/yr")
print(f"  air to process per tonne at 75% capture: {air_volume_per_tonne(X_AIR, 0.75):,.0f} m3")
for dp in (100, 220, 300, 895, 1000, 1935, 3200):
    print(f"  dP {dp:>5} Pa: fan {fan_work_gj_per_tonne(X_AIR, 0.75, dp):5.2f} GJ_e/t at 75% capture, "
          f"{fan_work_gj_per_tonne(X_AIR, 0.6, dp):5.2f} at 60% capture "
          f"(${energy_cost_floor(fan_work_gj_per_tonne(X_AIR, 0.6, dp), 50):.0f}/t at $50/MWh)")

print("\n== 8. Productivity (kg CO2/kg sorbent/day) vs cycle time and used capacity ==")
for used_wc, t_cycle_min, tag in ((0.6, 40, "Climeworks/Svante laminate field KPI (0.5-0.7 mol/kg, ~30+10 min)"),
                                  (0.72, 48, "GT hollow fibre hot-water 2026 (33+13+2 min)"),
                                  (0.8, 20, "Hunter-Sellars 2026 TEA assumption (0.8 mol/kg, 20 min)"),
                                  (0.8, 66.6, "NETL Rev1 base (0.8 mol/kg, 1 h + 0.11 h)"),
                                  (1.2, 198, "NETL 2022 base (1.2 mol/kg, 3 h + 0.3 h)"),
                                  (1.04, 240, "packed bed, 4 h cycle, full ref wc")):
    p = productivity(used_wc, 1440 / t_cycle_min)
    print(f"  {tag:<66} {p:5.2f} kg/kg/day")
for meas, tag in ((0.27, "Schellevis & Brilman 2024 kg-scale S-TVSA pilot (measured)"),
                  (0.235, "Wu 2026 rotary wheel low (measured)"), (0.352, "Wu 2026 rotary wheel high (measured)"),
                  (0.90 * 24 * M_CO2, "Campbell 2026 fibre 0.90 mmol/g/h (measured, lab module)"),
                  (0.032 * 24, "TDA/GE coated HX 32 g/kg/h, 500 ppm (measured, sub-bench)")):
    print(f"  {tag:<66} {meas:5.2f} kg/kg/day")

print("\n== 9. What productivity buys: sorbent inventory and sorbent-linked capital per t/yr ==")
for p in (0.27, 0.5, 1.0, 1.5, 3.0):
    inv = 1000 / (p * 365 * 0.9)   # kg sorbent per (t CO2/yr), 90% utilisation
    print(f"  {p:4.2f} kg/kg/day -> {inv:6.1f} kg sorbent per t/yr; "
          f"initial fill at $20/kg = ${inv*20:,.0f} per t/yr; at $50/kg-structured = ${inv*50:,.0f}")

print("\n== 10. Sorbent replacement: cycles per year vs lifetime ==")
for t_cycle_min in (240, 60, 20):
    cpy = 0.9 * 365 * 1440 / t_cycle_min
    for used_wc in (0.6, 1.04):
        for life_yr in (1, 3):
            cost = sorbent_cost_per_tonne(20, used_wc, cpy * life_yr)
            print(f"  cycle {t_cycle_min:>3} min ({cpy:,.0f} cycles/yr), wc {used_wc}, life {life_yr} yr: ${cost:6.1f}/t at $20/kg")

print("\n== 11. Measured pilot heat vs ideal: implied second-law efficiency ==")
floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99))
for q, tdes, tag in ((14.5, 373.15, "Schellevis & Brilman pilot 14.5 MJ/kg heat"),
                     (22.0, 376.45, "Wu rotary prototype >22 MJ/kg heat"),
                     (11.9, 373.15, "Climeworks-derived 11.9 GJ/t (Deutz & Bardow via Hunter-Sellars)"),
                     (6.04, 373.15, "OptiLex reference ideal cycle 6.04 GJ/t")):
    ex = q * (1 - T0 / tdes)
    print(f"  {tag:<62} exergy of heat {ex:5.2f} GJ/t -> 2nd-law eff (heat only) {floor/ex:5.1%}")
