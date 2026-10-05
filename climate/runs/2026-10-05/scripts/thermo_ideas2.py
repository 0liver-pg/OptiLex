"""Refinements: idea 1 (atmospheric steam-swept collector-adsorber), idea 6 (LWR steam bleed for DAC),
cost roll-ups. ASSUMPTIONS are labelled; floors from the OptiLex verifier."""
import sys, math
sys.path.insert(0, 'climate')
from physics import *
gj_t = lambda kj_mol: kj_mol / 44.01
dac_floor = gj_per_tonne(min_separation_work(420e-6, 0.75))
comp_floor = gj_per_tonne(R * T0 * math.log(150))
comp_real = comp_floor / 0.65
fan10 = fan_work_gj_per_tonne(420e-6, 0.75, 10)

print("1'. ATMOSPHERIC-PRESSURE, STEAM-SWEPT SOLAR COLLECTOR-ADSORBER")
def collector_eta(dT, G=800, kind="flat"):
    # EN 12975-style quadratic; ASSUMED coefficients: selective flat plate / evacuated tube
    if kind == "flat":
        return 0.78 - 3.5 * dT / G - 0.015 * dT**2 / G
    return 0.65 - 1.2 * dT / G - 0.008 * dT**2 / G
for kind, Tm in (("flat", 105), ("evac", 140)):
    for dT_avg in (Tm - 25 - 30, Tm - 25):     # morning warm-up lowers average dT; bracket
        print(f"  {kind} collector, mean dT {dT_avg} K: eta {collector_eta(dT_avg, kind=kind):.2f}")
insol = 6.5  # kWh/m2/day ASSUMED desert tilted aperture
variants = {
    # name: (w mmol/g, dH, H2O co-desorbed, extra sweep steam mol/mol, dT bed, struct kg/kg, eta_daily, $/kg sorbent)
    "A amine/silica, steam-swept 105C, flat glazed": (1.2, 75, 1.5, 1.5, 80, 0.5, 0.38, 20.0),
    "B K2CO3/carbon, 140C, evacuated-tube class":   (0.8, 140, 1.0, 0.0, 120, 0.5, 0.40, 3.0),
}
for name, (w, dH, nw, nsw, dT, st, eta, price) in variants.items():
    sens = 1000 / w * (1.2 + 0.8 * st) * dT / 1000
    q = sens + dH + (nw + nsw) * 44
    qday = insol * 3.6 * eta * 1e3   # kJ/m2/day
    ceil = qday / q * 44.01 / 1000
    print(f"\n  {name}: heat {q:.0f} kJ/mol = {gj_t(q):.1f} GJ_th/t solar; ceiling {ceil:.2f} kg/m2/day")
    for kg_day in (0.3, 0.6):
        if kg_day > ceil:
            print(f"    {kg_day} kg/m2/day exceeds heat ceiling"); continue
        t_m2_yr = kg_day * 300 / 1000               # ASSUMED 300 effective sunny days
        m2 = 1 / t_m2_yr
        sorb = kg_day * 1000 / 44.01 / w * m2      # kg sorbent per t/yr
        for panel in (100, 200):                    # $/m2 ASSUMED installed panel incl. valves, manifold
            capex = panel * m2 + sorb * price
            # LCOD: CRF 0.10 on capex (sorbent assumed to last plant life, ~10 yr/3,000 cycles; else add),
            # O&M 4%/yr of capex, electricity (compression + 10 Pa fan) at $60/MWh, transport+storage $25/t
            elec = (comp_real + fan10) / 3.6 * 60
            lcod = capex * 0.10 + capex * 0.04 + elec + 25
            print(f"    {kg_day} kg/m2/d, panel ${panel}/m2: {m2:.1f} m2 & {sorb:.0f} kg sorbent per t/yr -> capex ${capex:,.0f}/(t/yr); "
                  f"LCOD ~${lcod:,.0f}/t (elec ${elec:.0f}, heat used {kg_day/ceil:.0%})")
print(f"\n  purchased electricity (compression + 10 Pa fan): {comp_real+fan10:.2f} GJe/t = {(comp_real+fan10)/0.0036:.0f} kWh/t "
      f"vs Climeworks Gen2 stated 650 kWh/t; at 1 Gt/yr = {ScaleCheck(1, comp_real+fan10).share_of_world_electricity_if_electric:.1%} of world electricity")
print(f"  land at 2x aperture: 0.6 kg/m2/d -> {2/0.18:.0f} m2 per t/yr -> {2/0.18*1e9/1e6:,.0f} km2 per Gt/yr; 0.3 -> {2/0.09*1e9/1e6:,.0f} km2 per Gt/yr")

print("\n6. LWR TURBINE STEAM BLEED AS DAC REGENERATION HEAT")
T_cond = 273.15 + 38    # ASSUMED condenser saturation
for T_ext_c in (110, 125):
    z = 0.85 * (1 - T_cond / (T_ext_c + 273.15))   # lost MWe per MWth extracted (Carnot x turbine eff.)
    print(f"  steam bled at {T_ext_c} C: lost electricity {z:.2f} MWe per MWth")
z = 0.85 * (1 - T_cond / (273.15 + 120))
q_dac, e_dac = 7.2, 2.34   # GJ_th/t and GJe/t, Climeworks Gen2 nominal (company-stated)
for label, cop in (("LWR steam bleed", 1 / z), ("air-source heat pump", 2.2), ("electric boiler", 1.0)):
    e_eq = q_dac / cop + e_dac
    print(f"  {label:22s}: heat costs {q_dac/cop:.2f} GJe/t; total {e_eq:.2f} GJe-eq/t; eta_II {(dac_floor+comp_floor)/e_eq:.0%}; "
          f"energy ${e_eq/3.6*35:.0f}/t at $35/MWh, ${e_eq/3.6*60:.0f}/t at $60/MWh")
for price in (30, 40):
    print(f"  LWR steam heat price at ${price}/MWh_e opportunity cost: ${z*price:.1f}/MWh_th "
          f"(Geissler 2026 LCOH: geothermal >=$16, CSP >=$31, heat pump >=$39/MWh_th)")
for per_gw in (100, 300):
    t = per_gw * 31536 / q_dac
    print(f"  {per_gw} MW_th bled per GWe: {t/1e6:.2f} Mt/yr DAC per GWe; derate {per_gw*z:.0f} MWe ({per_gw*z/10:.1f}%); "
          f"US fleet 97 GWe -> {t*97/1e6:.0f} Mt/yr; world ~380 GWe -> {t*380/1e9:.2f} Gt/yr")

print("\n4'. CEMENT MARGINAL CAPTURE: capex-dominated?")
capex_eur, cap = 421e6, 400e3
for share in (0.6, 0.8):
    cc = capex_eur / cap * share * 0.10
    print(f"  marginal capex at {share:.0%} of Brevik unit capex (EUR{capex_eur/cap:,.0f} per t/yr): EUR{cc:.0f}/t capital charge (CRF 0.10)")
print("  + heat via heat pump ~$17-34/t (energy $11-22 + capex $6-12) + O&M + transport/storage -> marginal ~EUR100-160/t")
