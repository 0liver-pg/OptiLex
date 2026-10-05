"""Verifier for idea non_co2_6: HFC-23 + CH4 co-pyrolysis to vinylidene fluoride (VDF).

Checks: reaction thermochemistry (dH, dS, dG, equilibrium onset), separation floor for
HFC-23 capture from HCFC-22 vent streams, process energy per t HFC-23 and per t CO2e,
techno-economics (capex annualisation, energy, methane, disposal, VDF and HF credits),
comparison with incineration cost derived from Zhao et al. 2023, perverse-incentive ratio
vs CDM-era credits, realistic scale, and resource needs.

Sources / labels:
  [M]  measured / realized outcome     [E] expert/agency estimate
  [Mod] modelled estimate              [A] assumption (justified inline)
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *  # noqa

# ---------------------------------------------------------------- constants
M_HFC23, M_VDF, M_HF, M_CH4_ = 70.014, 64.035, 20.006, 16.043   # g/mol
GWP100_HFC23 = 14_600   # IPCC AR6 (Adam et al. 2024 use 14,700, WMO 2022)
GWP20_HFC23 = 12_400    # IPCC AR6
GWP100_HCFC142b = 2_300 # IPCC AR6 (approx.)
USD_PER_CNY = 0.14

print("=" * 78)
print("1. Reaction thermochemistry: CHF3 + CH4 -> CH2=CF2 + HF + H2")
# Standard-state gas values at 298 K, NIST Chemistry WebBook / JANAF (rounded) [M]
dHf = {"CHF3": -697.0, "CH4": -74.87, "VDF": -345.2, "HF": -273.3, "H2": 0.0}   # kJ/mol
S0 = {"CHF3": 259.7, "CH4": 186.3, "VDF": 266.1, "HF": 173.8, "H2": 130.7}      # J/mol/K
dH = dHf["VDF"] + dHf["HF"] + dHf["H2"] - dHf["CHF3"] - dHf["CH4"]
dS = S0["VDF"] + S0["HF"] + S0["H2"] - S0["CHF3"] - S0["CH4"]
T_eq = dH * 1e3 / dS
print(f"  dH298 = {dH:+.1f} kJ/mol ; dS298 = {dS:+.1f} J/mol/K ; dG=0 at ~{T_eq:.0f} K "
      "(constant dH,dS approximation)")
for T in (873, 1073, 1173, 1273):
    dG = dH - T * dS / 1e3
    K = math.exp(-dG * 1e3 / (R * T))
    print(f"  T={T} K: dG ~ {dG:+.1f} kJ/mol, Kp ~ {K:.3g} (bar)")
dH_GJ_per_t = dH / M_HFC23   # kJ/g = GJ/t
print(f"  reaction enthalpy = {dH_GJ_per_t:.2f} GJ per t HFC-23 "
      f"= {dH_GJ_per_t*1e3/GWP100_HFC23*1e3:.0f} kJ per t CO2e (GWP100)")
vdf_stoich = M_VDF / M_HFC23
hf_stoich = M_HF / M_HFC23
ch4_stoich = M_CH4_ / M_HFC23
print(f"  stoichiometry per t HFC-23: VDF {vdf_stoich:.3f} t, HF {hf_stoich:.3f} t, "
      f"CH4 consumed {ch4_stoich:.3f} t")

print("=" * 78)
print("2. Separation floor: HFC-23 recovery from HCFC-22 plant streams")
# HFC-23 is the light end of the HCFC-22 distillation train; vent is mostly HFC-23 [E].
for x, f, label in [(0.90, 0.99, "column vent, 90% HFC-23"),
                    (0.30, 0.95, "dilute vent, 30% HFC-23"),
                    (0.01, 0.90, "very dilute fugitive stream, 1%")]:
    w = min_separation_work(x, f, purity=0.999)
    gjt = gj_per_tonne(w, M_HFC23 / 1e3)
    print(f"  {label:<36} floor {w/1e3:6.2f} kJ/mol = {gjt:.3f} GJ/t HFC-23 "
          f"= {gjt*1e9/GWP100_HFC23/1e3:.2f} kJ/t CO2e")

print("=" * 78)
print("3. Process energy per t HFC-23 (low / base / high)")
# Sensible heat to reaction T, with per-pass conversion and heat recovery [A].
Cp_avg = {"CHF3": 70.0, "CH4": 60.0}  # J/mol/K, mean 298-1100 K (JANAF-order values) [A]
cases = {
    #        T_K, CH4:CHF3 ratio, per-pass conv, heat recovery, purification GJ/t VDF
    "low":  (1073, 1.0, 0.6, 0.7, 3.0),
    "base": (1123, 2.0, 0.4, 0.5, 6.0),
    "high": (1173, 4.0, 0.25, 0.3, 12.0),
}
sel = {"low": 0.70, "base": 0.50, "high": 0.30}  # VDF selectivity: unverified [A]
E = {}
for k, (T, ratio, conv, rec, purif) in cases.items():
    sens_kJ_per_mol_fed = (T - 298) * (Cp_avg["CHF3"] + ratio * Cp_avg["CH4"]) / 1e3
    sens_kJ_per_mol_conv = sens_kJ_per_mol_fed / conv * (1 - rec)
    sens_GJ_t = sens_kJ_per_mol_conv / M_HFC23
    rxn = dH_GJ_per_t                                # all converted HFC-23 at overall dH
    purif_GJ_t = purif * vdf_stoich * sel[k]
    tot = sens_GJ_t + rxn + purif_GJ_t
    E[k] = tot
    print(f"  {k:<5} T={T} K, CH4:CHF3={ratio}, conv/pass={conv}, recovery={rec}: "
          f"sensible {sens_GJ_t:.2f} + reaction {rxn:.2f} + purification {purif_GJ_t:.2f} "
          f"= {tot:.2f} GJ/t HFC-23 -> {tot*1e3/GWP100_HFC23:.3f} MJ/t CO2e")
co2_heat = {k: v * 0.0561 for k, v in E.items()}  # t CO2 per t HFC-23 if gas-fired
print(f"  process CO2 if gas-fired (base): {co2_heat['base']:.2f} t CO2 per t HFC-23 vs "
      f"{GWP100_HFC23} t CO2e abated -> {co2_heat['base']/GWP100_HFC23*100:.4f}% penalty")

print("=" * 78)
print("4. Incineration benchmark from Zhao et al. 2023 (Adv. Clim. Change Res. 14:136) [Mod]")
# Cumulative 2021-2060 net abatement cost (2021 CNY) and abatement mass, from abstract.
for scen, cost_bn, kt in [("KA baseline (destruction)", 5.0, 683),
                          ("Less Emission", 2.9, 694),
                          ("Resource Utilization", -2.7, 702)]:
    cny_per_kg = cost_bn * 1e9 / (kt * 1e6)
    usd_per_t23 = cny_per_kg * 1e3 * USD_PER_CNY
    print(f"  {scen:<28} {cny_per_kg:+.2f} CNY/kg HFC-23 = {usd_per_t23:+.0f} USD/t HFC-23 "
          f"= {usd_per_t23/GWP100_HFC23:+.3f} USD/t CO2e")
incin_usd_t23 = 5.0e9 / 683e6 * 1e3 * USD_PER_CNY

print("=" * 78)
print("5. Conversion-plant techno-economics, per t HFC-23 fed (low / base / high cost)")
CRF = lambda r, n: r * (1 + r) ** n / ((1 + r) ** n - 1)
# Plant sized to one large HCFC-22 site: 2 kt/yr HFC-23 [A: 100 kt/yr HCFC-22 x 2%].
tea = {
    # capex $M, scale kt/yr, r, n, O&M %capex, energy $/GJ, CH4 $/GJ, disposal $/t, VDF $/t, HF $/t
    "low":  (15, 2.0, 0.08, 20, 0.04, 5, 4, 200, 6000, 2000),
    "base": (30, 2.0, 0.10, 15, 0.05, 8, 8, 500, 3500, 1500),
    "high": (60, 1.0, 0.12, 10, 0.06, 15, 12, 1500, 2000, 1000),
}
order = {"low": "low", "base": "base", "high": "high"}
net = {}
for k, (capex, kt, r, n, om, pE, pCH4, disp, pVDF, pHF) in tea.items():
    capex_t = capex * 1e6 * CRF(r, n) / (kt * 1e3)
    om_t = capex * 1e6 * om / (kt * 1e3)
    energy_t = E[k] * pE
    # methane: stoichiometric use / selectivity (non-selective carbon lost), 55.5 GJ/t CH4
    ch4_t = ch4_stoich / max(sel[k], 0.2) * 55.5 * pCH4
    disp_t = disp
    cost = capex_t + om_t + energy_t + ch4_t + disp_t
    rev_vdf = vdf_stoich * sel[k] * pVDF
    rev_hf = hf_stoich * pHF       # F not in VDF assumed recovered as HF (optimistic for low sel)
    netc = cost - rev_vdf - rev_hf
    net[k] = netc
    print(f"  {k:<5} capex {capex_t:6.0f} + O&M {om_t:5.0f} + energy {energy_t:4.0f} + CH4 {ch4_t:4.0f}"
          f" + disposal {disp_t:5.0f} = {cost:6.0f} $/t;  VDF credit {rev_vdf:5.0f}, HF credit {rev_hf:4.0f}"
          f" -> NET {netc:+6.0f} $/t HFC-23 = {netc/GWP100_HFC23:+.3f} $/t CO2e (GWP100), "
          f"{netc/GWP20_HFC23:+.3f} (GWP20)")
print(f"  incineration benchmark (Zhao 2023 KA): {incin_usd_t23:+.0f} $/t HFC-23 = "
      f"{incin_usd_t23/GWP100_HFC23:+.3f} $/t CO2e")
for k in net:
    print(f"  {k}: conversion minus incineration (positive = conversion costs more) = {net[k]-incin_usd_t23:+.0f} $/t HFC-23 "
          f"(= {(net[k]-incin_usd_t23)/1e3:+.2f} $/kg)")

# The idea's own revenue claim: 40-80% selectivity x $3,000-7,000/t VDF
lo = vdf_stoich * 0.40 * 3000; hi = vdf_stoich * 0.80 * 7000
print(f"  idea's gross-revenue claim reproduced: {lo:.0f}-{hi:.0f} $/t HFC-23 = "
      f"{lo/GWP100_HFC23:.3f}-{hi/GWP100_HFC23:.3f} $/t CO2e (gross, before capex/opex)")

print("=" * 78)
print("6. Incentive size vs the HCFC-22 business and vs CDM-era credits")
for byp in (0.015, 0.03, 0.04):
    for k in ("low", "base"):
        gain_per_t22 = -(net[k] - incin_usd_t23) * byp   # $ per t HCFC-22 swing vs incineration
        print(f"  by-product {byp*100:.1f}%: {k} swing vs incineration {gain_per_t22:+.0f} $/t HCFC-22 "
              f"({gain_per_t22/2500*100:+.1f}% of an ASSUMED $2,500/t HCFC-22 price)")
cdm_credit = 10 * GWP100_HFC23 * (11700 / 14600)  # CDM used GWP 11,700; ~$10/CER [E]
print(f"  CDM-era credit value ~ {cdm_credit:,.0f} $/t HFC-23 vs base conversion swing "
      f"{-(net['base']-incin_usd_t23):,.0f} $/t -> ratio {cdm_credit/abs(net['base']-incin_usd_t23+1e-9):,.0f}x")

print("=" * 78)
print("7. Scale and resource needs")
meas_kt = 14.0   # Adam et al. 2024, 2023 global emissions 14.0 +/- 0.9 Gg/yr [M]
reported_kt = meas_kt / 5
gap_kt = meas_kt - reported_kt
eChina_gap = (3.5, 4.3)  # Gg/yr above China's reported total, 2021/2022 [M]
print(f"  measured 2023 emissions {meas_kt} kt = {meas_kt*GWP100_HFC23/1e3:.0f} Mt CO2e (GWP100); "
      f"reported ~{reported_kt:.1f} kt; gap ~{gap_kt:.1f} kt = {gap_kt*GWP100_HFC23/1e3:.0f} Mt CO2e")
print(f"  eastern-China excess over China's report: {eChina_gap[0]}-{eChina_gap[1]} kt = "
      f"{eChina_gap[0]*GWP100_HFC23/1e3:.0f}-{eChina_gap[1]*GWP100_HFC23/1e3:.0f} Mt CO2e (~1/3 of gap)")
scen = {"low": 0.25 * eChina_gap[0], "base": 0.5 * gap_kt, "high": 0.9 * meas_kt}
for k, kt in scen.items():
    gt = kt * GWP100_HFC23 / 1e6
    sc = ScaleCheck(gt_per_year=kt * 1e3 / 1e9, gj_per_tonne=E[k])  # mass of HFC-23 processed
    vdf_kt = kt * vdf_stoich * sel[k]
    ch4_kt = kt * ch4_stoich / max(sel[k], 0.2)
    print(f"  {k:<5}: {kt:5.1f} kt HFC-23/yr abated -> {gt:.3f} Gt CO2e/yr (GWP100); "
          f"energy {sc.ej_per_year*1e3:.4f} PJ/yr = {sc.share_of_world_primary_energy:.2e} of world primary; "
          f"VDF {vdf_kt:.1f} kt/yr; CH4 {ch4_kt:.1f} kt/yr")
print(f"  share of fossil CO2 (base): {scen['base']*GWP100_HFC23/1e6/FOSSIL_CO2_GT*100:.2f}%  "
      f"of total GHG: {scen['base']*GWP100_HFC23/1e6/TOTAL_GHG_GT_CO2E*100:.2f}%")

# Co-benefit: displaced HCFC-142b feedstock leakage
for leak in (0.005, 0.02):
    r142b_per_vdf = 100.49 / M_VDF   # CH3CClF2 -> CH2=CF2 + HCl
    co2e = r142b_per_vdf * leak * GWP100_HCFC142b
    vdf = scen["base"] * vdf_stoich * sel["base"]
    print(f"  142b-route displacement at {leak*100:.1f}% feedstock leak: {co2e:.0f} t CO2e/t VDF "
          f"-> {co2e*vdf/1e3:.2f} Mt CO2e/yr on {vdf:.1f} kt VDF (ODS co-benefit)")

print("=" * 78)
print("8. Marginal abatement attributable to the VDF graft (vs simply enforcing incineration)")
print("  Climate benefit comes from COLLECTION; incineration and conversion abate the same kg.")
print("  Graft adds value only if the plant-level swing (section 6) changes operator behaviour.")
