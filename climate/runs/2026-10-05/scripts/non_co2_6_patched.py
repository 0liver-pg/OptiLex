"""Verifier for non_co2_6_patched: HFC-23 input-side balance + per-kg penalty, VDF as optional offset.

Labels: [M] measured/realized  [E] expert/agency estimate  [Mod] modelled  [A] assumption (justified)
        [K] domain knowledge not re-verified in this session (web-search budget exhausted)
Key primary source: Adam et al. 2024 (Nat. Commun., AGAGE + FLEXINVERT+), cached as adam2024.xml.
"""
import sys, math
import numpy as np
sys.path.insert(0, 'climate')
from physics import *  # noqa

M = {'CHCl3': 119.377, 'HF': 20.006, 'CHClF2': 86.468, 'HCl': 36.461, 'CHF3': 70.014,
     'CH4': 16.043, 'VDF': 64.035, 'CaF2': 78.07, 'CaOH2': 74.09}
GWP100, GWP20 = 14_600, 12_400        # AR6 HFC-23
USD_PER_CNY = 0.14
rng = np.random.default_rng(7)
line = lambda t: print("=" * 80 + f"\n{t}")

# --------------------------------------------------------------------------- 1
line("1. Thermodynamic floor (separation of HFC-23 from HCFC-22 plant streams)")
for x, f, lab in [(0.90, 0.99, "column vent 90% HFC-23"), (0.30, 0.95, "dilute vent 30%"),
                  (0.01, 0.90, "fugitive 1%")]:
    w = min_separation_work(x, f, purity=0.999)
    g = gj_per_tonne(w, M['CHF3'] / 1e3)
    print(f"  {lab:<24} floor {w/1e3:5.2f} kJ/mol = {g:.3f} GJ/t HFC-23 = {g*1e6/GWP100:.2f} kJ/t CO2e")
print("  -> floor is ~1e-5 of DAC's 0.47 GJ/t CO2; no claim can be below it. Energy is not a constraint.")

# --------------------------------------------------------------------------- 2
line("2. Input-side stoichiometry (CHCl3 + 2HF -> CHClF2 + 2HCl; CHCl3 + 3HF -> CHF3 + 3HCl)")
cl_per = M['CHCl3'] / M['CHClF2']; hf_per = 2 * M['HF'] / M['CHClF2']; hcl_per = 2 * M['HCl'] / M['CHClF2']
print(f"  per t HCFC-22: CHCl3 {cl_per:.3f} t, HF {hf_per:.3f} t, HCl {hcl_per:.3f} t  (claim 1.381/0.463/0.843: OK)")
for r in (0.015, 0.02, 0.03, 0.04):
    hf23 = r * 3 * M['HF'] / M['CHF3']; cl23 = r * M['CHCl3'] / M['CHF3']
    print(f"  by-product r={r:.3f} t/t: extra HF {hf23:.4f} t, extra CHCl3 {cl23:.4f} t per t HCFC-22; "
          f"HFC-23 per t HF = {r/(hf_per+hf23)*1e3:.1f} kg; per t CHCl3 = {r/(cl_per+cl23)*1e3:.1f} kg")
print("  claim 'HFC-23 adds ~0.005-0.03 t HF per t HCFC-22': executed range is 0.013-0.034 t -> low end understated (minor)")
print("  Signal size: the HFC-23 route changes HF use by only 2.7-6.9% and CHCl3 by 1.8-4.6%, so venting is")
print("  NOT visible in inputs; the balance can only infer HCFC-22 output and multiply by a ratio r_c.")

# --------------------------------------------------------------------------- 3
line("3. Detection power of the input balance at one plant-year (Monte Carlo, 20k draws) [Mod]")
# Uncertainties [A]: r year-mean variability CV_r (catalyst age, HF:CHCl3, T); input-implied output
# CV_P (CHCl3 yield 97-99%, inventory change, CHCl3 diverted to other uses); flowmeter CV_m 2%.
# Commissioning bias b: operator sets r_c during a fresh-catalyst / low-over-fluorination test, so r_c = (1-b) r_true.
def detect(v, cv_r, cv_p, b, cv_m=0.02, n=20000):
    r_true = 0.025 * (1 + cv_r * rng.standard_normal(n))
    P = 100_000.0                                   # t HCFC-22/yr, one large plant [A]
    G = r_true * P
    A = (1 - v) * G * (1 + cv_m * rng.standard_normal(n))
    E = 0.025 * (1 - b) * P * (1 + cv_p * rng.standard_normal(n))
    sig = E * math.sqrt(cv_r**2 + cv_p**2 + cv_m**2)
    return np.mean(E - A > 1.645 * sig)             # one-sided 5% false-positive threshold
print("  min vented fraction detected with >=80% probability (and detection prob. at 20% venting):")
res = {}
for b in (0.0, 0.2):
    for cv_r in (0.05, 0.10, 0.15, 0.25):
        for cv_p in (0.02, 0.05):
            vs = np.linspace(0, 0.9, 91)
            pdet = [detect(v, cv_r, cv_p, b, n=4000) for v in vs]
            vmin = next((v for v, p in zip(vs, pdet) if p >= 0.8), float('nan'))
            p20 = detect(0.20, cv_r, cv_p, b)
            res[(b, cv_r, cv_p)] = (vmin, p20)
            print(f"   bias b={b:.1f} CV_r={cv_r:.2f} CV_P={cv_p:.2f}: v_min(80%) = {vmin:.2f}; P(detect | 20% vented) = {p20:.2f}")
print("  -> with CV_r <= 0.10 and no commissioning bias, venting >~20-27% is caught; at the idea's own")
print("     CV 0.15 threshold the 80%-power floor is ~33-36%, so the claimed '20% shortfall' test is too tight.")
print("     A 20% commissioning bias lets the operator vent ~20% with near-zero penalty risk (structural, not noise).")

# --------------------------------------------------------------------------- 4
line("4. Penalty vs avoided destruction cost (does the per-kg penalty make venting irrational?)")
zhao = 5.0e9 / 683e6 * USD_PER_CNY                 # $/kg lifecycle, Zhao et al. 2023 KA scenario [Mod]
avoid = {"low (opex only, unit already built)": 0.3, "base (Zhao 2023 lifecycle)": zhao,
         "high (small plant, new unit)": 3.0}       # [A] bracket around Zhao
for p in (1, 2, 5, 10):
    print(f"  penalty ${p}/kg = ${p*1e3/GWP100:.3f}/t CO2e (GWP100), ${p*1e3/GWP20:.3f}/t CO2e (GWP20)")
for pdet in (0.3, 0.6, 0.9):
    req = {k: v / pdet for k, v in avoid.items()}
    print(f"  detection prob {pdet:.1f}: penalty needed > " +
          ", ".join(f"{k.split(' ')[0]} ${v:.2f}/kg" for k, v in req.items()))
print(f"  CDM comparison: $10-20/t CO2e at CDM GWP 11,700 = ${10*11.7:.0f}-{20*11.7:.0f}/kg "
      f"(idea quotes $146-292/kg at AR6 GWP; same order, 50-200x the penalty) -> no over-production incentive: OK")
print("  -> $1-2/kg is BELOW the needed level when detection prob <0.5 (base); $5-10/kg is robust and still <$0.7/t CO2e.")

# --------------------------------------------------------------------------- 5
line("5. Scale: what share of the measured-minus-reported gap is reachable? (Adam et al. 2024) [M]")
meas, rep21 = 14.0, 2.8                            # Gg 2023 measured; 2021 reported total [M]
gap = meas - meas / 5
print(f"  idea's gap (14.0 - 14.0/5) = {gap:.1f} kt = {gap*GWP100/1e3:.0f} Mt CO2e; 2021 reported-based gap was 12.7 Gg [M]")
outside_EA = 8.3                                    # Gg 2023 outside eastern Asia, +/-1.7 [M]
eChina_excess = (3.5, 4.3)                          # Gg above China's report, 2021/2022 [M]
nonHCFC = (0.4, 1.5)                                # Gg global, HFC-32/125/TFE-HFP production [Mod]
print(f"  outside eastern Asia 2023: {outside_EA} +/-1.7 Gg = {outside_EA/meas:.0%} of global emissions -> the idea's")
print("  'eastern China dominates the gap' is CONTRADICTED: eastern-China excess is ~1/3 of the gap (paper's own words).")
print(f"  non-HCFC-22 sources {nonHCFC} Gg are a GLOBAL estimate, not specific to eastern China (claim mis-attributes it).")
print("  Outside eastern Asia (Russia, India, etc.) current networks cannot verify (paper); the cross-check step is absent there.")
scen = {
    # kt recovered: share of eastern-China excess (monitored, input data plausible) + share of remainder (unmonitored)
    "low":  0.5 * eChina_excess[0] + 0.0 * (gap - eChina_excess[0]),
    "base": 0.75 * np.mean(eChina_excess) + 0.25 * (gap - np.mean(eChina_excess)),
    "high": 0.9 * eChina_excess[1] + 0.6 * (gap - eChina_excess[1]),
}
for k, kt in scen.items():
    print(f"  {k:<4}: {kt:4.1f} kt HFC-23/yr = {kt*GWP100/1e6:.3f} Gt CO2e/yr GWP100 ({kt*GWP20/1e6:.3f} GWP20)"
          f" = {kt*GWP100/1e6/FOSSIL_CO2_GT*100:.2f}% of fossil CO2")
for f in (0.25, 0.5, 0.75):
    print(f"  idea's scenario {f:.0%} of gap: {gap*f:.1f} kt = {gap*f*GWP100/1e3:.0f} Mt (requires adoption beyond China)")

# --------------------------------------------------------------------------- 6
line("6. Cost per t CO2e (social cost; penalties are transfers and excluded)")
# MRV programme [A]: ~50 HCFC-22 plants worldwide [K]; tracer/commissioning test $0.1-0.3M one-off
# (annualised 10%/10 yr); supplier reporting + audit $0.05-0.2M/plant/yr; 5-15 new tall-tower/flask sites
# at $0.3-1M/yr each (AGAGE-class station order of magnitude) [A].
CRF = lambda r, n: r * (1 + r) ** n / ((1 + r) ** n - 1)
mrv = {"low": 50 * (0.1e6 * CRF(0.1, 10) + 0.05e6) + 5 * 0.3e6,
       "base": 50 * (0.2e6 * CRF(0.1, 10) + 0.1e6) + 10 * 0.6e6,
       "high": 50 * (0.3e6 * CRF(0.1, 10) + 0.2e6) + 15 * 1.0e6}
# compliance (destruction / conversion) per t CO2e: low = VDF route full-cost low case from non_co2_6.py
# (-$3,052/t HFC-23, unverified selectivity), base = Zhao lifecycle destruction, high = $3/kg destruction.
comp = {"low": -3052 / GWP100, "base": zhao * 1e3 / GWP100, "high": 3.0e3 / GWP100}
cost = {}
for k in ("low", "base", "high"):
    t = scen[k] * 1e3 * GWP100                      # t CO2e/yr
    m = mrv[k] / t
    cost[k] = comp[k] + m
    print(f"  {k:<4}: MRV ${mrv[k]/1e6:5.1f}M/yr over {t/1e6:5.0f} Mt = ${m:.3f}/t; compliance ${comp[k]:+.3f}/t "
          f"-> TOTAL ${cost[k]:+.3f}/t CO2e")
# robust high: low abatement with high MRV and high destruction
t = scen["low"] * 1e3 * GWP100
print(f"  stress (high MRV + high destruction, LOW abatement): ${comp['high'] + mrv['high']/t:.3f}/t CO2e")

# --------------------------------------------------------------------------- 7
line("7. Energy and resources")
E_destr = {"low": 5.0, "base": 15.0, "high": 40.0}  # GJ/t HFC-23: plasma 1-3 kWh/kg ~ 4-11 GJ_e; incinerator
                                                    # support fuel; [A, order of magnitude]
for k in E_destr:
    sc = ScaleCheck(gt_per_year=scen[k] * 1e3 / 1e9, gj_per_tonne=E_destr[k])
    print(f"  {k:<4}: {E_destr[k]:4.0f} GJ/t HFC-23 = {E_destr[k]*1e3/GWP100:.2f} MJ/t CO2e; "
          f"{sc.ej_per_year*1e3:.3f} PJ/yr = {sc.share_of_world_primary_energy:.1e} of world primary energy")
caf2 = 1.5 * M['CaF2'] / M['CHF3']; lime = 1.5 * M['CaOH2'] / M['CHF3']
print(f"  destruction by-products: {caf2:.2f} t CaF2 and {lime:.2f} t Ca(OH)2 per t HFC-23 "
      f"-> base {scen['base']*caf2:.1f} kt CaF2/yr (fluorspar-grade recyclable); land/water negligible")
print(f"  VDF route (offset only): stoich {M['VDF']/M['CHF3']:.3f} t VDF/t HFC-23; base 50% sel. on half of "
      f"base volume = {scen['base']*0.5*0.5*M['VDF']/M['CHF3']:.1f} kt VDF/yr (vs global PVDF market ~10^2 kt/yr [K])")
dH = (-345.2 - 273.3) - (-697.0 - 74.87)
print(f"  reaction dH = {dH:+.1f} kJ/mol = {dH/M['CHF3']:.2f} GJ/t HFC-23 = {dH/M['CHF3']*1e6/GWP100:.0f} kJ/t CO2e (claim OK)")

line("8. Verdict inputs")
print(f"  cost $/t CO2e low/base/high: {cost['low']:+.3f} / {cost['base']:+.3f} / {cost['high']:+.3f}")
print(f"  scale Gt CO2e/yr low/base/high: {scen['low']*GWP100/1e6:.3f} / {scen['base']*GWP100/1e6:.3f} / {scen['high']*GWP100/1e6:.3f}")
print(f"  energy GJ/t CO2e low/base/high: {E_destr['low']/GWP100:.2e} / {E_destr['base']/GWP100:.2e} / {E_destr['high']/GWP100:.2e}")
print(f"  floor GJ/t CO2e (column vent): {gj_per_tonne(min_separation_work(0.9,0.99,purity=0.999), M['CHF3']/1e3)/GWP100:.2e}")
