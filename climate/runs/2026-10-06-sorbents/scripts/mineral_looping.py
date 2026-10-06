import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math

# ---------------------------------------------------------------------------------------------
# Mineral / oxide looping for DAC: thermodynamic over-binding, kiln energy, diffusion-limited
# flux at 420 ppm, sorbent make-up cost. Thermochemical data: standard formation values
# (Robie & Hemingway / NIST-JANAF / CRC, 298 K, kJ/mol). Treat as +-2 kJ/mol.
# ---------------------------------------------------------------------------------------------
Hf = dict(CaCO3=-1207.6, CaO=-634.9, CaOH2=-985.2, CO2=-393.5, H2Og=-241.8, H2Ol=-285.8,
          MgCO3=-1095.8, MgO=-601.6, MgOH2=-924.5, hydromag=-6514.9,   # Mg5(CO3)4(OH)2.4H2O
          Na2CO3=-1130.7, NaHCO3=-950.8, K2CO3=-1151.0, KHCO3=-963.2)
Gf = dict(CaCO3=-1128.8, CaO=-603.3, CaOH2=-897.5, CO2=-394.4, H2Og=-228.6, H2Ol=-237.1,
          MgCO3=-1012.1, MgO=-569.3, MgOH2=-833.5, hydromag=-5864.2,
          Na2CO3=-1044.4, NaHCO3=-851.0, K2CO3=-1063.5, KHCO3=-863.5)

def rxn(prod, reac, table):
    return sum(n * table[s] for s, n in prod.items()) - sum(n * table[s] for s, n in reac.items())

floor = gj_per_tonne(min_separation_work(X_AIR, 0.75, 0.99))
dG_half = dG_for_half_loading() / 1e3
print(f"Reference: separation floor {floor:.2f} GJ/t; half-loading dG at 420 ppm = {dG_half:.1f} kJ/mol\n")

print("1) CAPTURE-STEP FREE ENERGY at 25 C (per mol CO2, CO2 at 1 bar std state) and equilibrium pCO2")
p_h2o = 0.5 * 3169.0 / 1e5   # 50% RH at 25 C, bar
caps = {
 "Ca(OH)2 + CO2 -> CaCO3 + H2O(g)":   (dict(CaCO3=1, H2Og=1), dict(CaOH2=1, CO2=1), +1),
 "CaO + CO2 -> CaCO3":                (dict(CaCO3=1), dict(CaO=1, CO2=1), 0),
 "Mg(OH)2 + CO2 -> MgCO3 + H2O(g)":   (dict(MgCO3=1, H2Og=1), dict(MgOH2=1, CO2=1), +1),
 "MgO + CO2 -> MgCO3":                (dict(MgCO3=1), dict(MgO=1, CO2=1), 0),
 "Na2CO3 + CO2 + H2O(g) -> 2NaHCO3":  (dict(NaHCO3=2), dict(Na2CO3=1, CO2=1, H2Og=1), -1),
 "K2CO3 + CO2 + H2O(g) -> 2KHCO3":    (dict(KHCO3=2), dict(K2CO3=1, CO2=1, H2Og=1), -1),
}
for name, (pr, re, nu_w) in caps.items():
    dH = rxn(pr, re, Hf); dG = rxn(pr, re, Gf)
    # effective dG at ambient humidity: products' water at p_h2o (nu_w=+1) or reactant water at p_h2o (nu_w=-1)
    dG_eff = dG + nu_w * R * T0 * math.log(p_h2o) / 1e3
    p_eq_ppm = math.exp(dG_eff * 1e3 / (R * T0)) * 1e6     # bar -> ppm of 1 bar
    print(f"  {name:<36} dH {dH:7.1f}  dG {dG:7.1f}  dG_eff(50%RH) {dG_eff:7.1f} kJ/mol  "
          f"eq pCO2 {p_eq_ppm:9.2e} ppm  over-binding vs {dG_half:.1f}: {dG_eff - dG_half:6.1f} kJ/mol")

print("\n2) REGENERATION (calcination) reaction heat and minimum work")
regs = {
 "CaCO3 -> CaO + CO2":                 (dict(CaO=1, CO2=1), dict(CaCO3=1), 1),
 "MgCO3 -> MgO + CO2":                 (dict(MgO=1, CO2=1), dict(MgCO3=1), 1),
 "hydromagnesite -> 5MgO+4CO2+5H2O(g)":(dict(MgO=5, CO2=4, H2Og=5), dict(hydromag=1), 4),
 "2NaHCO3 -> Na2CO3 + CO2 + H2O(g)":   (dict(Na2CO3=1, CO2=1, H2Og=1), dict(NaHCO3=2), 1),
 "2KHCO3 -> K2CO3 + CO2 + H2O(g)":     (dict(K2CO3=1, CO2=1, H2Og=1), dict(KHCO3=2), 1),
}
for name, (pr, re, nco2) in regs.items():
    dH = rxn(pr, re, Hf) / nco2; dG = rxn(pr, re, Gf) / nco2
    dS = (dH - dG) / T0 * 1e3
    T_eq = dH * 1e3 / dS    # T where dG=0 (all gases at 1 bar), crude (constant dH, dS)
    print(f"  {name:<38} dH {dH:6.1f} kJ/mol = {gj_per_tonne(dH*1e3):.2f} GJ/t | dG298 {dG:6.1f} kJ/mol = "
          f"{gj_per_tonne(dG*1e3):.2f} GJ/t ({dG*1e3/min_separation_work(X_AIR,0.75,0.99):.1f}x floor) | T(dG=0) ~{T_eq-273.15:4.0f} C")

print("\n3) LIME-LOOP KILN HEAT per tonne CO2 (Heirloom-like: 85% carbonated Ca(OH)2 -> 900 C)")
X = 0.85
cp_caco3, cp_caoh2 = 1.13e3 * 0.1001, 1.45e3 * 0.0741   # J/mol/K mean values 25-900 C (approx.)
dT = 900 - 25
dH_calc = rxn(*regs["CaCO3 -> CaO + CO2"][:2], Hf)                       # kJ/mol
dH_dehyd = rxn(dict(CaO=1, H2Og=1), dict(CaOH2=1), Hf)                   # kJ/mol Ca(OH)2
sens = (cp_caco3 * dT + (1 - X) / X * cp_caoh2 * dT) / 1e3               # kJ per mol CO2
dehyd = (1 - X) / X * dH_dehyd
for moist in (0.0, 0.5, 1.0):   # mol free water carried into kiln per mol CO2
    for rec in (0.0, 0.5):
        tot = dH_calc + (sens) * (1 - rec) + dehyd + moist * 44.0
        print(f"  free water {moist:.1f} mol/mol, sensible-heat recovery {rec:.0%}: reaction {dH_calc:.0f} + sensible "
              f"{sens*(1-rec):.0f} + Ca(OH)2 dehydration {dehyd:.0f} + drying {moist*44:.0f} = {tot:.0f} kJ/mol = "
              f"{gj_per_tonne(tot*1e3):.2f} GJ/t ({gj_per_tonne(tot*1e3)/3.6*1000:.0f} kWh/t)")
base = gj_per_tonne((dH_calc + sens + dehyd) * 1e3)
print(f"  Slaking CaO + H2O(l) -> Ca(OH)2 releases {-rxn(dict(CaOH2=1), dict(CaO=1, H2Ol=1), Hf):.0f} kJ/mol at <=~100-500 C (low grade)")
print(f"  Electric kiln at ~{base:.1f} GJ/t(e): second-law efficiency {second_law_efficiency(base, floor):.1%}; "
      f"energy cost at $30/50/80 per MWh: ${energy_cost_floor(base,30):.0f}/${energy_cost_floor(base,50):.0f}/${energy_cost_floor(base,80):.0f} per t")
dG_loop = rxn(*regs["CaCO3 -> CaO + CO2"][:2], Gf)
print(f"  Ideal loop bound: calcination dG298 = {dG_loop:.0f} kJ/mol -> best-case second-law efficiency "
      f"{min_separation_work(X_AIR,0.75,0.99)/(dG_loop*1e3):.1%} unless hydration/carbonation heat (released at ambient) is reused")
for claim, v in (("Heirloom 2021 application (thermal 5.9 + 0.5)", 6.4), ("Keith 2018 calciner", 5.25),
                 ("Keith 2018 full plant, gas only", 8.81), ("APS 2011 calciner", 8.1),
                 ("McQueen 2020 MgO oxy-fired low", 5.89), ("McQueen 2020 MgO oxy-fired high", 7.97),
                 ("Chen & Kanan 2025 claim <1 MWh/t", 3.6)):
    print(f"    {claim:<46} {v:5.2f} GJ/t -> {v/floor:4.1f}x floor, 2nd-law (if all work) {second_law_efficiency(v, floor):.1%}")

print("\n4) DIFFUSION-LIMITED CARBONATION OF A Ca(OH)2 LAYER AT 420 ppm (shrinking front, gas-phase Fick)")
C = X_AIR * P0 / (R * T0)                 # mol CO2 / m3 air
D = 1.6e-5                                # m2/s CO2 in air
def front(t_s, rho_bulk, eps, tau, X=0.85):
    n = rho_bulk / 0.07409 * X            # mol CO2 capacity per m3 bed
    Deff = D * eps / tau
    z = math.sqrt(2 * Deff * C * t_s / n)
    flux = n * z / t_s                    # mol/m2/s cycle-average
    return z, flux, n
print(f"  CO2 concentration in air: {C*1e3:.1f} mmol/m3")
z, f, n = front(182.5 * 86400, 2240 * 0.5, 0.5, 1.5)
print(f"  Check vs Abanades 2020 (3 cm plate, porosity 0.5, both faces, 'about 6 months'): model front after 6 months = {z*1e3:.1f} mm (need 15 mm)")
for label, rho, eps, tau in (("loose hydrated-lime powder (500 kg/m3)", 500, 0.78, 1.3),
                             ("compacted plate (1120 kg/m3, eps 0.5)", 1120, 0.5, 1.5)):
    for days in (1, 3, 14, 180):
        z, f, n = front(days * 86400, rho, eps, tau)
        kg_m2_yr = f * M_CO2 * 365 * 86400
        print(f"  {label:<40} {days:>4} d: depth {z*1e3:5.1f} mm, loading {z*rho:6.2f} kg/m2, "
              f"avg flux {kg_m2_yr:6.0f} kg CO2/m2/yr -> {1000/kg_m2_yr:6.1f} m2 per t/yr, {1e6/kg_m2_yr/1e6*1e0:6.3f} km2 per kt/yr x1000 = {1e9/kg_m2_yr/1e6:5.1f} km2 exposed area per Mt/yr")
print("  External gas-film ceiling N = k_g * C:")
for kg in (0.002, 0.005, 0.02):
    print(f"    k_g = {kg*1e3:.0f} mm/s -> {kg*C*M_CO2*365*86400:5.0f} kg CO2/m2/yr")
print("  Measured for comparison: Dostie 2025 CaO 0.5-1.5 cm, 85-95% RH, 24 d: 12-117 kg/m2/yr; Hawrot & Renforth 2025 lime <10 mm: >2 t/ha/d "
      f"= {2000/1e4*365:.0f} kg/m2/yr; Rausis 2022 MgO 10 cm tilled: 2.2-12.5 kg/m2/yr")
# MgO: implied land for 1 Gt at measured flux
for fl in (2.2, 12.5, 73, 117):
    print(f"    flux {fl:6.1f} kg/m2/yr -> {1e12/fl/1e6:9,.0f} km2 per Gt CO2/yr")
# McQueen assumption: 0.1 m layer, 90% in a year
mgo_load = 21500e3 / 11e4       # kg MgO per m2 (21,500 t on 11 ha)
flux_mcq = mgo_load / 0.0403 * 0.9 * M_CO2
print(f"  McQueen 2020 assumption: {mgo_load:.0f} kg MgO/m2, 90%/yr -> {flux_mcq:.0f} kg CO2/m2/yr, i.e. {flux_mcq/12.5:.0f}x-{flux_mcq/2.2:.0f}x the measured 12.5-2.2")

print("\n5) SORBENT MAKE-UP COST (lime ~$0.10-0.20/kg vs amine sorbent $20/kg)")
wc_lime = 0.85 / 0.07409        # mol CO2 per kg Ca(OH)2 per cycle
print(f"  Ca(OH)2 at 85% conversion: {wc_lime:.1f} mol/kg/cycle = {wc_lime*M_CO2:.3f} kg CO2/kg; "
      f"productivity at 3-day cycle {productivity(wc_lime, 1/3):.3f} kg/kg/day vs amine 1.04 mol/kg x 24 cycles/day = {productivity(1.04, 24):.2f} kg/kg/day")
for price in (0.10, 0.20):
    for cyc in (1, 8, 10, 100):
        print(f"    ${price:.2f}/kg, {cyc:>3} cycles: ${sorbent_cost_per_tonne(price, wc_lime, cyc):6.1f}/t CO2")
print(f"  Amine reference: $20/kg, 1.04 mol/kg, 2,000 / 20,000 cycles: ${sorbent_cost_per_tonne(20,1.04,2000):.0f} / ${sorbent_cost_per_tonne(20,1.04,20000):.0f} per t")
print("  Single-use (no kiln) lime is NOT net-negative: making 1 t CaO from limestone emits 0.785 t process CO2 that the lime merely re-absorbs.")

print("\n6) ALKALI CARBONATE/BICARBONATE on a support: heat of a 150 C swing (verifier cycle, optimistic)")
# K2CO3 route treated as a Langmuir site with dH = reaction enthalpy incl. water; effective dS fitted so that dG_eff matches
dH_K = rxn(dict(KHCO3=2), dict(K2CO3=1, CO2=1, H2Og=1), Hf) * 1e3
dG_K_eff = (rxn(dict(KHCO3=2), dict(K2CO3=1, CO2=1, H2Og=1), Gf) - R * T0 * math.log(p_h2o) / 1e3) * 1e3
dS_K = (dH_K - dG_K_eff) / T0
for wt in (0.06, 0.20, 0.40):      # K2CO3 mass fraction on the support
    qmax = wt / 0.1382             # mol CO2 per kg composite
    for Tdes in (423.15,):
        cyc = TVSACycle(dH=dH_K, dS=dS_K, q_max=qmax, T_des=Tdes, p_des=1.0e4, cp_sorbent=1000.0, water_coads=0.0)
        print(f"  K2CO3 {wt:.0%} on support: q_max {qmax:.2f} mol/kg, working cap {cyc.working_capacity:.2f} mol/kg, heat {cyc.heat_gj_per_t:.1f} GJ/t "
              f"(reaction {gj_per_tonne(cyc.reaction_heat):.2f} incl. 1 mol water vapour, sensible {gj_per_tonne(cyc.sensible_heat):.2f}), work-eq {cyc.work_equivalent_gj_per_t:.2f} GJ/t")
