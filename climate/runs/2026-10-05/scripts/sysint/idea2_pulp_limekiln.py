"""Idea 2: Kraft pulp mill. Replace the fossil-fired rotary lime kiln with an electrically heated,
indirectly heated calciner (Leilac-type graft from cement) powered by the mill's own surplus
biomass electricity. Lime-mud CO2 (biogenic: its carbon came from black liquor) leaves pure."""
from common import *

CaO_per_ADt = (0.25, 0.30)          # t CaO per air-dry tonne pulp (literature range, from memory)
kiln_fuel_GJ_tCaO = (5.5, 7.0)      # rotary lime kiln specific fuel (literature range, from memory)
ef = {"natural gas": 0.056, "fuel oil": 0.074}   # t CO2/GJ
dH_calc = 178e3 / 0.05608 * 1000 / 1e9     # GJ/t CaO, standard enthalpy (verifier-style hand calc)
print(f"Calcination enthalpy floor: {dH_calc:.2f} GJ/t CaO = {dH_calc/0.785:.2f} GJ/t CO2")
for cao in CaO_per_ADt:
    co2_proc = cao * 44.01 / 56.08
    print(f"\nCaO {cao} t/ADt -> biogenic process CO2 {co2_proc:.3f} t/ADt")
    for fuel in kiln_fuel_GJ_tCaO:
        for k, e in ef.items():
            print(f"  fossil kiln fuel {fuel} GJ/tCaO ({k}): {cao*fuel*e:.3f} t fossil CO2/ADt")
    for elec in (4.0, 4.5):     # GJ_e/t CaO for electric indirect calciner with heat recovery (assumption)
        mwh = cao * elec / 3.6
        print(f"  electric calciner {elec} GJ/tCaO -> {mwh:.2f} MWh/ADt; 1 Mt/yr mill -> {mwh*1e6/8000:.0f} MW avg")

# Lime mud drying: 25-30% moisture -> use mill LP steam/flue heat (not electricity)
for moist in (0.25, 0.30):
    w = moist / (1 - moist) / 0.892      # t water per t CaO (CaCO3->CaO mass 1/0.56; per t CaCO3 water=moist/(1-moist))
    w = moist / (1 - moist) * (100.09 / 56.08)
    print(f"lime mud moisture {moist:.0%}: {w:.2f} t water per t CaO -> {w*2.6:.1f} GJ/t CaO drying heat (LP steam)")

print("\n== Separation/compression floors (OptiLex verifier) ==")
print(f"rotary lime kiln flue ~20% CO2, 90% capture: {gj_per_tonne(min_separation_work(0.20,0.9)):.3f} GJ/t")
print(f"recovery boiler flue ~13% CO2, 90% capture: {gj_per_tonne(min_separation_work(0.13,0.9)):.3f} GJ/t")
print(f"indirect calciner off-gas ~95% CO2 (after steam condensation): {gj_per_tonne(min_separation_work(0.95,0.9,0.99)):.4f} GJ/t")
print(f"liquefaction for ship (1->~15 bar ideal isothermal + refrigeration not counted): {iso_comp_gj_t(1,15):.3f} GJ/t")

print("\n== Energy economics per ADt (my assumptions) ==")
for cao, fuel, p_el, p_fuel, eua in [(0.25, 5.5, 40, 8, 70), (0.28, 6.5, 60, 10, 75), (0.30, 7.0, 80, 12, 80)]:
    lost_sales = cao * 4.25 / 3.6 * p_el
    saved_fuel = cao * fuel * p_fuel
    saved_ets = cao * fuel * 0.056 * eua * 1.08   # EUR->USD ~1.08
    net = lost_sales - saved_fuel - saved_ets
    co2 = cao * 0.785
    print(f"CaO {cao}, fuel {fuel} GJ, power ${p_el}/MWh, gas ${p_fuel}/GJ, EUA EUR{eua}: lost power sales ${lost_sales:.1f}/ADt, "
          f"saved fuel ${saved_fuel:.1f}, saved ETS ${saved_ets:.1f} -> net ${net:+.1f}/ADt = ${net/co2:+.0f} per t biogenic CO2")

print("\n== Global scale ==")
for kraft_mt in (120, 140):   # kraft/sulfate pulp, Mt/yr (order of magnitude, unverified)
    for cao in CaO_per_ADt:
        print(f"kraft {kraft_mt} Mt/yr x {cao} tCaO/ADt -> {kraft_mt*cao*0.785:.0f} Mt/yr pure biogenic CO2; "
              f"fossil kiln CO2 avoided ~{kraft_mt*cao*6.25*0.06:.0f} Mt/yr")
# chain cost per t biogenic CO2 (assumptions): calciner capex premium, liquefaction, ship+store
for capex_prem, ts in [(150, 35), (300, 60)]:   # $ per t/yr CO2 capacity premium over a rotary kiln rebuild; T&S $/t
    cap = capex_prem * crf(0.08, 25)
    liq = 120 * 50 / 1000 + 8   # 120 kWh/t at $50/MWh + $8/t liquefaction capex
    print(f"calciner premium ${capex_prem}/(t/yr) -> ${cap:.0f}/t; liquefaction ${liq:.0f}/t; T&S ${ts}/t -> total ${cap+liq+ts:.0f}/t "
          f"vs durable BECCS offtake prices ~$200-600/t (map) and Swedish BECCS auction")
