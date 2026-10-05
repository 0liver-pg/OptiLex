"""Bottleneck-first thermodynamic checks for six capture ideas (OptiLex idea engine, 2026-10-05).

All floors come from the OptiLex verifier (climate/physics.py). Every other input is an
explicit ASSUMPTION (labelled) so a reviewer can change it.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *

MOL_PER_T = 1e6 / 44.01          # mol CO2 per tonne
def gj_t(kj_per_mol):            # kJ/mol CO2 -> GJ/t CO2
    return kj_per_mol * 1e3 / M_CO2 / 1e9 * 1e3 / 1e3  # = kJ/mol / 44.01 g/mol -> GJ/t
def gj_t(kj_per_mol):
    return kj_per_mol / 44.01   # kJ/mol / (g/mol) = kJ/g = GJ/t

print("=" * 90)
print("0. REFERENCE FLOORS (verifier)")
dac_floor = gj_per_tonne(min_separation_work(420e-6, 0.75))
comp_floor = gj_per_tonne(R * T0 * math.log(150 / 1.0))   # isothermal ideal 1->150 bar, GJ/t
print(f"DAC floor 420 ppm, 75% capture: {dac_floor:.3f} GJ/t")
print(f"Isothermal compression 1->150 bar floor: {comp_floor:.3f} GJ/t")
for x, f in [(0.25, 0.50), (0.25, 0.90), (0.25, 0.95), (0.25, 0.99)]:
    print(f"Cement flue {x:.0%} CO2 at {f:.0%} capture: {gj_per_tonne(min_separation_work(x, f)):.3f} GJ/t")

print("=" * 90)
print("1. SOLAR COLLECTOR-ADSORBER, one passive cycle per day")
# ASSUMPTIONS: desert site, 6.5 kWh/m2/day on tilted aperture; batch-heating daily collector efficiency.
for label, insol, eta in [("low", 5.5, 0.35), ("mid", 6.5, 0.42), ("high", 7.0, 0.50)]:
    q = insol * 3.6 * eta  # MJ/m2/day
    print(f"  solar heat delivered ({label}): {insol} kWh/m2/d x {eta:.0%} = {q:.1f} MJ/m2/day")
Q_SOLAR = 6.5 * 3.6 * 0.42   # MJ/m2/day, mid case

def tsa_heat(w_mmolg, dH_ads, n_h2o, dT, struct_kg_per_kg_sorb=0.0, cp_s=1.2, cp_struct=0.8, recov=0.0):
    """kJ per mol CO2 for one temperature-swing cycle.
    w: working capacity mmol/g; dH_ads kJ/mol; n_h2o mol H2O desorbed per mol CO2 (44 kJ/mol);
    dT heating span K; structure mass per kg sorbent; recov = fraction of sensible heat recovered."""
    g_per_mol = 1000.0 / w_mmolg
    sens = g_per_mol * (cp_s + struct_kg_per_kg_sorb * cp_struct) * dT / 1000.0   # kJ/mol
    return sens * (1 - recov) + dH_ads + n_h2o * 44.0, sens

cases = {
    # name: (w mmol/g, dH kJ/mol, H2O mol/mol, dT K, struct kg/kg sorbent, sorbent $/kg)
    "A amine/silica, glazed panel 90C + vacuum": (1.2, 75.0, 1.5, 70, 0.5, 20.0),
    "B K2CO3-on-carbon, 140C self-pressurised":  (0.8, 140.0, 1.0, 120, 0.5, 3.0),
}
for name, (w, dH, nw, dT, st, price) in cases.items():
    q_mol, sens = tsa_heat(w, dH, nw, dT, st)
    q_t = gj_t(q_mol)
    max_kg_m2_day = Q_SOLAR * 1e3 / q_mol * 44.01 / 1000   # kg CO2 per m2 per day if heat-limited
    print(f"\n  Variant {name}")
    print(f"    heat per mol: {q_mol:.0f} kJ/mol (sensible {sens:.0f}) = {q_t:.1f} GJ_th/t (all free solar)")
    print(f"    heat-limited ceiling: {max_kg_m2_day:.2f} kg CO2/m2/day")
    for kg_day in (0.3, 0.6):
        sorb_kg_m2 = kg_day * 1000 / 44.01 / w   # kg sorbent per m2 needed for that daily uptake
        days = 300
        t_per_m2_yr = kg_day * days / 1000
        m2_per_tpy = 1 / t_per_m2_yr
        sorb_per_tpy = sorb_kg_m2 * m2_per_tpy
        air_m3 = air_volume_per_tonne(420e-6, 0.75) * kg_day / 1000      # m3 air per m2 per night at 75% capture
        v_face = air_m3 / (12 * 3600)                                     # m/s through 1 m2 face over 12 h
        print(f"    design {kg_day} kg/m2/day: sorbent {sorb_kg_m2:.1f} kg/m2, {m2_per_tpy:.1f} m2 per t/yr, "
              f"sorbent {sorb_per_tpy:.0f} kg per t/yr (${sorb_per_tpy*price:,.0f} per t/yr at ${price}/kg), "
              f"night air {air_m3:.0f} m3/m2 -> {v_face*100:.1f} cm/s face velocity; heat used {kg_day/max_kg_m2_day:.0%} of supply")
        for panel_cost in (100, 200):
            capex = panel_cost * m2_per_tpy + sorb_per_tpy * price
            print(f"      panel ${panel_cost}/m2 -> capex ~${capex:,.0f} per t/yr (vs Stratos ~$2,600); "
                  f"capital charge at CRF 0.10: ${capex*0.10:,.0f}/t; land at 2x aperture: {2*m2_per_tpy:.0f} m2/t/yr "
                  f"= {2*m2_per_tpy*1e6/1e6:.0f} km2 per Mt/yr")
for name, (w, dH, nw, dT, st, price) in cases.items():
    for ncyc in (3000, 6000):
        t_per_kg = w * 44.01e-3 * ncyc / 1000
        print(f"  sorbent cost per tonne, {name[:9]}: ${price}/kg over {ncyc} cycles ({ncyc/300:.0f} yr at 1/day) = ${price/t_per_kg:.0f}/t")
# electricity: variant A vacuum 0.15 -> 1 bar (30% eff) + compression (65% eff); fan at 10 Pa
vac_A = gj_per_tonne(R * T0 * math.log(1 / 0.15)) / 0.30
comp_real = comp_floor / 0.65
fan10 = fan_work_gj_per_tonne(420e-6, 0.75, 10)
print(f"\n  Electricity A: vacuum {vac_A:.2f} + compression {comp_real:.2f} + fan(10 Pa) {fan10:.3f} = "
      f"{vac_A+comp_real+fan10:.2f} GJe/t ({(vac_A+comp_real+fan10)/0.0036:.0f} kWh/t); Climeworks Gen2 stated 2.34 GJe/t")
print(f"  Electricity B (self-pressurised to ~1 atm, no vacuum pump): compression {comp_real:.2f} GJe/t "
      f"({comp_real/0.0036:.0f} kWh/t)")
# KHCO3 decomposition temperature (thermochemistry, NBS standard values)
dH, dS = 140.1, 0.3271   # kJ/mol, kJ/molK for 2KHCO3 -> K2CO3 + CO2 + H2O(g)
for ptot in (0.2, 1.0):
    p = ptot / 2
    T = dH / (dS - R / 1000 * math.log(p * p))
    print(f"  KHCO3 decomposition with pCO2=pH2O={p} bar needs T >= {T-273.15:.0f} C")
K298 = math.exp(-(dH - 298.15 * dS) / (R / 1000 * 298.15))
print(f"  Night loading driving force: eq. pCO2 over K2CO3 at 25C, pH2O 0.01 bar = {K298/0.01:.1e} bar (vs 4.2e-4 ambient)")
# exergy view of variant A
ex_A = gj_t(tsa_heat(1.2, 75, 1.5, 70, 0.5)[0]) * (1 - T0 / 363) + vac_A + comp_real
print(f"  Exergy input variant A ~{ex_A:.2f} GJ/t -> second-law eff (sep+comp floor {dac_floor+comp_floor:.2f}) "
      f"{(dac_floor+comp_floor)/ex_A:.0%}; PURCHASED energy only {vac_A+comp_real+fan10:.2f} GJe/t")
s = ScaleCheck(1.0, vac_A + comp_real + fan10)
print(f"  1 Gt/yr purchased electricity: {s.ej_per_year:.2f} EJ = {s.share_of_world_electricity_if_electric:.1%} of world electricity")

print("=" * 90)
print("2. THERMAL-WAVE BED-TO-BED SENSIBLE HEAT RECOVERY (sorbent-coated heat exchangers)")
print("   case (w, dHads, H2O/CO2, dT, structure kg/kg) -> GJ_th/t at heat recovery r")
tw_cases = {"best": (2.0, 75, 1.0, 75, 1.0), "mid": (1.0, 75, 2.5, 75, 1.5), "worst": (0.5, 75, 5.0, 75, 2.0)}
for name, (w, dHa, nw, dT, st) in tw_cases.items():
    row = []
    for r in (0.0, 0.4, 0.6, 0.75):
        row.append(gj_t(tsa_heat(w, dHa, nw, dT, st, recov=r)[0]))
    base = row[0]
    print(f"   {name:5s}: " + ", ".join(f"r={r:.2f}: {v:.1f}" for r, v in zip((0, .4, .6, .75), row))
          + f" | tonnes per MW_th of waste heat x{base/row[2]:.2f} at r=0.6")
mw_tonnes = lambda gjt: 31536.0 / gjt   # t/yr per MW_th (31,536 GJ/yr)
q_mid0 = gj_t(tsa_heat(1.0, 75, 2.5, 75, 1.5)[0]); q_mid6 = gj_t(tsa_heat(1.0, 75, 2.5, 75, 1.5, recov=0.6)[0])
print(f"   mid case: {mw_tonnes(q_mid0):,.0f} -> {mw_tonnes(q_mid6):,.0f} t/yr per MW_th; heat $ saved at $20/MWh_th: "
      f"${(q_mid0-q_mid6)/3.6*20:.0f}/t; at $60/MWh_th (e-boiler): ${(q_mid0-q_mid6)/3.6*60:.0f}/t")
s0, s6 = ScaleCheck(1, q_mid0), ScaleCheck(1, q_mid6)
print(f"   1 Gt/yr heat: {s0.ej_per_year:.1f} -> {s6.ej_per_year:.1f} EJ/yr ({s0.share_of_world_primary_energy:.2%} -> {s6.share_of_world_primary_energy:.2%} of primary)")
# extra cycle time: heat recovery step adds a phase; productivity penalty assumption 15-25%

print("=" * 90)
print("3. STORE HEAT, NOT THE LOADED SORBENT (power-to-heat + pressurised hot-water TES)")
plant_tpy = 100_000; q_heat = 7.2   # GJ_th/t (Climeworks Gen2 nominal 2,000 kWh_th/t)
mw_th = plant_tpy * q_heat * 1e9 / 3.1536e7 / 1e6
hours = 16
mwh_store = mw_th * hours
tank_m3 = mwh_store * 3.6e6 / (4.18 * 50 * 1000)  # kJ: MWh*3.6e6 kJ / (cp*dT kJ/m3... ) use 4.18e3 kJ/m3K
tank_m3 = mwh_store * 3.6e6 / (4180 * 50)
for c_m3 in (150, 400):
    print(f"   {plant_tpy:,} t/yr plant: {mw_th:.1f} MW_th; {hours} h store = {mwh_store:.0f} MWh_th = {tank_m3:,.0f} m3 water at dT 50K;"
          f" at ${c_m3}/m3 -> ${tank_m3*c_m3/1e6:.1f}M = ${tank_m3*c_m3/plant_tpy:.0f} per t/yr")
co2_buffer = plant_tpy / 8760 * hours
for w, price in ((1.5, 20), (1.0, 40)):
    sorb_t = co2_buffer / (w * 44.01e-3)
    print(f"   storing {hours} h of LOADED sorbent instead: {co2_buffer:.0f} t CO2 -> {sorb_t:,.0f} t sorbent (w={w}) "
          f"at ${price}/kg = ${sorb_t*price*1e3/1e6:.0f}M = ${sorb_t*price*1e3/plant_tpy:,.0f} per t/yr")
# electricity price arbitrage (ASSUMPTION: avg $60/MWh; cheapest 8 h/day avg $20/MWh in a high-renewables grid)
for cop, lab in ((1.0, "e-boiler"), (2.2, "air-source heat pump to 100 C")):
    mwh_e = q_heat / 3.6 / cop
    print(f"   {lab} COP {cop}: {mwh_e:.2f} MWh_e/t -> ${mwh_e*60:.0f}/t at $60 avg vs ${mwh_e*20:.0f}/t at $20 cheap hours "
          f"(saving ${mwh_e*40:.0f}/t); charge rating {mw_th/cop*24/8:.0f} MW_e for 8 h/day charging")
crf = 0.10
for cf in (0.95, 0.33):
    print(f"   capital charge at $2,600 per t/yr, CRF 0.10, CF {cf:.0%}: ${2600*crf/cf:,.0f}/t")

print("=" * 90)
print("4. HEAT-PUMP-LIFTED CAPTURE FRACTION AT A WASTE-HEAT-LIMITED CEMENT PLANT (Brevik-type)")
cap50 = 400_000; total = cap50 / 0.5
for frac in (0.90, 0.95):
    extra = total * frac - cap50
    for reb in (2.6, 3.2):
        heat_pj = extra * reb / 1e6
        mw = extra * reb * 1e9 / 3.1536e7 / 0.9 / 1e6   # MW_th at 90% availability
        print(f"   to {frac:.0%}: +{extra/1e3:.0f} kt/yr, reboiler {reb} GJ/t -> {heat_pj:.2f} PJ/yr = {mw:.0f} MW_th")
def cop(t_src_c, t_sink_c, frac=0.5):
    return frac * (t_sink_c + 273.15) / (t_sink_c - t_src_c)
print("   heat-pump COPs (50% of Carnot), sink 135 C:")
srcs = {"stripper overhead vapour ~90 C": 90, "lean-amine/absorber cooling ~55 C": 55, "seawater/ambient ~10 C": 10}
for k, t in srcs.items():
    print(f"     {k}: COP {cop(t,135):.1f}")
# blended: 1/3 of duty from overhead (90C), 2/3 from absorber/lean cooler (55C)
reb = 2.9
e_hp = reb * (1/3) / cop(90, 135) + reb * (2/3) / cop(55, 135)
print(f"   blended self-heating (1/3 at 90C, 2/3 at 55C), reboiler {reb} GJ/t: {e_hp:.2f} GJe/t = {e_hp/0.0036:.0f} kWh/t")
for p in (40, 60, 80):
    print(f"     energy cost at ${p}/MWh: ${e_hp/3.6*p:.0f}/t ; e-boiler: ${reb/3.6*p:.0f}/t")
gas_gj = reb / 0.9
print(f"   gas boiler: {gas_gj:.2f} GJ gas/t = ${gas_gj*10:.0f}/t at $10/GJ + {gas_gj*0.0561:.3f} t CO2/t captured "
      f"(= {gas_gj*0.0561*90:.0f} EUR/t at 90 EUR ETS if uncaptured)")
ex_reb = reb * (1 - T0 / (130 + 273.15))
print(f"   exergy of {reb} GJ/t at 130 C = {ex_reb:.2f} GJ/t; heat-pump electricity {e_hp:.2f} -> regen exergy efficiency {ex_reb/e_hp:.0%}")
for capex_kw in (600, 1200):
    extra = total * 0.90 - cap50
    mw = extra * reb * 1e9 / 3.1536e7 / 0.9 / 1e6
    print(f"   HP capex ${capex_kw}/kW_th x {mw:.0f} MW = ${mw*capex_kw/1e3:.0f}M -> ${mw*capex_kw*1e3*crf/extra:.0f}/t (CRF 0.10)")

print("=" * 90)
print("5. LIME-LOOPING DAC HOSTED AT INDIRECT-CALCINER CEMENT/LIME PLANTS")
dH_calc = 178.0  # kJ/mol CaCO3 -> CaO + CO2 (approx, 25 C basis)
floor_calc = gj_t(dH_calc)
for X in (0.4, 0.6, 0.8):
    solids_g = 56.08 / X + 44.01          # g solids (CaO + captured CO2) per mol CO2 cycled
    sens = solids_g * 1.0 * 875 / 1000    # kJ/mol, cp ~1.0 J/gK, 25->900 C
    for rec in (0.0, 0.75):
        tot = floor_calc + gj_t(sens * (1 - rec))
        print(f"   carbonation conversion {X:.0%}, sensible recovery {rec:.0%}: {tot:.2f} GJ_th/t "
              f"= {tot/3.6:.2f} MWh/t -> ${tot/3.6*60:.0f}/t electric at $60/MWh")
ex_calc = floor_calc * (1 - T0 / 1173)
print(f"   calcination floor {floor_calc:.2f} GJ/t at 900 C carries {ex_calc:.2f} GJ/t exergy -> best-case eta_II "
      f"{dac_floor/ex_calc:.0%} (separation floor / calcination exergy)")
# fuel-fired calciner: fuel CO2 per t DAC CO2 (coal 95 kg/GJ, gas 56 kg/GJ) at 4.7 GJ/t
for fuel, ef in (("gas", 0.0561), ("coal/petcoke", 0.095)):
    fco2 = 4.7 * ef
    print(f"   fuel-fired ({fuel}) at 4.7 GJ/t: +{fco2:.2f} t fuel CO2 per t DAC CO2 -> net removal at 90% capture "
          f"of fuel CO2: {1 - fco2*0.10:.2f} t; at 50% (Brevik-type): {1 - fco2*0.5:.2f} t")
# tray footprint (ASSUMPTIONS): 1.5 cm CaO layer, bulk 0.9 t/m3, 60% conversion in 3 days, 20 stacked levels
layer_kg = 0.015 * 900
co2_cycle = layer_kg * 0.6 * 44.01 / 56.08
per_level_yr = co2_cycle * 365 / 3 / 1000
print(f"   trays: {co2_cycle:.1f} kg CO2/m2 per 3-day cycle -> {per_level_yr:.2f} t/m2/yr per level; "
      f"20 levels -> {per_level_yr*20:.0f} t/m2 footprint/yr -> {1e6/(per_level_yr*20)/1e4:.0f} ha per Mt/yr")
ca_per_t = 56.08 / 44.01 / 0.6
print(f"   CaO cycled: {ca_per_t:.2f} t CaO per t CO2 (X=0.6); 100 kt/yr DAC = {ca_per_t*1e5/1e3:.0f} kt/yr CaO "
      f"through the calciner (a 1 Mt/yr clinker kiln calcines ~1.2-1.3 Mt CaCO3/yr)")

print("=" * 90)
print("6. STEAM-SWEPT TVSA WITH MECHANICAL VAPOUR RECOMPRESSION (MVR) OF CO-DESORBED WATER")
L = 2330.0   # kJ/kg latent heat near 70 C
def mvr(p1_bar, p2_bar, T1_c=70, eta=0.70, x_co2=0.3):
    # ideal-gas isentropic compression of steam/CO2 mixture, cp/k approx for steam (k=1.33) and CO2 (k=1.29)
    k = 1.31; cp_mix = (1 - x_co2) * 1.9 * 18.015 + x_co2 * 0.85 * 44.01   # J/molK approx
    T1 = T1_c + 273.15
    w = cp_mix * T1 * ((p2_bar / p1_bar) ** ((k - 1) / k) - 1) / eta / 1000   # kJ per mol mixture
    return w
for nw in (1.0, 2.5, 5.0):
    x_co2 = 1 / (1 + nw)
    for (p1, p2) in ((0.3, 1.2), (0.2, 1.2)):
        w_mix = mvr(p1, p2, x_co2=x_co2)                 # kJ per mol of mixture
        w_per_co2 = w_mix * (1 + nw)                      # kJ per mol CO2
        latent = nw * 18.015 * L / 1000                   # kJ per mol CO2 recovered (if fully condensed)
        vac_baseline = R * T0 * math.log(1 / p1) / 1000 / 0.30 * (1 + nw * 0)   # vacuum pump on CO2 only, after condensing water
        print(f"   H2O/CO2={nw}: {p1}->{p2} bar: MVR work {gj_t(w_per_co2):.2f} GJe/t recovers {gj_t(latent):.2f} GJ_th/t "
              f"(COP {latent/w_per_co2:.1f}); replaces vacuum pump {gj_t(vac_baseline):.2f} GJe/t; "
              f"net extra elec {gj_t(w_per_co2 - vac_baseline):.2f} GJe/t")

print("   --- dew-point-constrained MVR: compress to p2 where steam dew point = 100 C; heat recoverable above 80 C")
def psat_bar(Tc):  # Antoine for water, 1-100 C (mmHg) -> bar
    return 10 ** (8.07131 - 1730.63 / (233.426 + Tc)) / 750.06
p100, p80 = psat_bar(100), psat_bar(80)
for nw in (1.0, 2.5, 5.0):
    p2 = p100 * (1 + nw) / nw
    n_rem = p80 / (p2 - p80)                     # mol H2O left uncondensed at 80 C per mol CO2
    frac = max(0.0, (nw - n_rem) / nw)
    for p1 in (0.3, 0.2):
        w = mvr(p1, p2, x_co2=1/(1+nw)) * (1 + nw)
        rec = nw * frac * 18.015 * L / 1000
        vac = gj_per_tonne(R * T0 * math.log(1 / p1) * 1000) / 1000 / 0.30
        print(f"   H2O/CO2={nw}: p2={p2:.2f} bar; {frac:.0%} of latent condenses above 80 C = {gj_t(rec):.2f} GJ_th/t; "
              f"MVR {p1}->{p2:.2f} bar = {gj_t(w):.2f} GJe/t (COP {rec/w:.1f}); vacuum pump it replaces {vac:.2f} GJe/t; "
              f"net extra {gj_t(w)-vac:.2f} GJe/t -> marginal COP {gj_t(rec)/(gj_t(w)-vac):.1f}")
