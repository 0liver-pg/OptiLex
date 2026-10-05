"""Verifier for graft_bio_2: N2O-respiring (NosZ) bacteria enriched in livestock slurry before spreading.

Checks: thermodynamics (no separation; N2O -> N2 + 1/2 O2 is exergonic), per-hectare abatement,
enrichment (aeration) energy, bottom-up cost per t CO2e incl. capex annualisation, NH3-stripping
debit from aerating raw slurry, and realistic global scale when the vector is limited to slurry.

Sources / justifications (measured vs modelled flagged):
- Hiis et al., Nature 630 (2024), doi 10.1038/s41586-024-07464-3, abstract (Europe PMC): CB-01 at ~6e9 cells/mL
  in digestate; N2O cut 50-95% depending on soil type (MEASURED, mostly soil incubations + field trial);
  Europe-scale 5-20% of national anthropogenic N2O (MODELLED), "more if including other organic wastes"
  -> the authors themselves anticipate the slurry/organic-waste extension.
- IPCC 2019 Refinement EF1 (direct N2O): aggregated 1.0%; wet-climate synthetic 1.6%, wet-climate organic 0.6%,
  dry climate 0.5%. EF4 (volatilised N -> N2O) 1.0% (wet). GWP100 N2O = 273 (AR6, verifier constant).
- Slurry N content: cattle ~2.5-4 kg N/m3, pig ~3.5-6 kg N/m3 (typical EU/UK fertiliser manuals, e.g. RB209).
- Cell dry mass ~0.3 pg (typical for ~1 um rods); aerobic heterotrophic yield ~0.4 g cells/g COD;
  cell COD 1.42 g/g (standard activated-sludge stoichiometry).
- Field aeration efficiency 1-2 kg O2/kWh (surface/diffused aerators in viscous slurry, lower end of wastewater range).
- Aeration-driven NH3 stripping of slurry: low-rate aeration studies report a few % to >20% of N lost (ASSUMED 2/5/12%).
- Global inputs: synthetic N ~110 Mt N/yr (IFA ~2022), manure N applied to soils ~28-35 Mt N/yr (FAOSTAT).
  Liquid-slurry share of applied manure N (housed pigs/dairy, EU/NA/China) ASSUMED 35-60%.
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

N2O_PER_N = 44.013 / 28.014
GWP = GWP100["N2O"]

print("=== 1. Thermodynamics ===")
dGf_N2O = 104.2  # kJ/mol, standard Gibbs energy of formation of N2O(g) (NIST/CRC)
print(f"N2O(g) -> N2 + 1/2 O2: dG0 = {-dGf_N2O:.1f} kJ/mol (exergonic). No separation step; "
      f"thermodynamic floor for the conversion = 0 GJ/t CO2e (it releases energy).")
print("Only real energy cost: aerating/stirring slurry to grow the inoculum, plus handling.")

print("\n=== 2. Per-hectare abatement (field receiving slurry) ===")
cases = {
    #        N kg/ha, EF,    realised cut
    "low":  (150, 0.006, 0.30),   # IPCC wet-climate organic EF, low realised cut
    "base": (150, 0.010, 0.45),
    "high": (200, 0.016, 0.60),   # slurry + mineral top-up on wet fine soil
}
emis, saved = {}, {}
for k, (n, ef, cut) in cases.items():
    e = n * ef * N2O_PER_N * GWP / 1000  # t CO2e/ha/yr
    emis[k], saved[k] = e, e * cut
    print(f"{k:4s}: {n} kg N/ha x EF {ef*100:.1f}% -> {n*ef*N2O_PER_N:.2f} kg N2O = {e:.3f} t CO2e/ha; "
          f"cut {cut*100:.0f}% -> saves {e*cut:.3f} t CO2e/ha/yr")
# check claimant's own arithmetic
e_claim = 150 * 0.01 * N2O_PER_N * GWP / 1000
print(f"Claim check: 150 kg N, EF 1% -> {150*0.01*N2O_PER_N:.2f} kg N2O = {e_claim:.3f} t CO2e/ha (claimed 2.36 kg, 0.64 t)")

print("\n=== 3. Enrichment energy (aeration to grow ~6e9 cells/mL) ===")
cells_per_ml = 6e9
cell_dry_g = 0.3e-12
X = cells_per_ml * cell_dry_g * 1000  # g/L biomass
yield_ = 0.4
cod_used = X / yield_
o2 = cod_used - 1.42 * X  # g O2/L = kg/m3
print(f"Biomass {X:.2f} g/L; COD consumed {cod_used:.2f} g/L; O2 demand {o2:.2f} kg/m3 slurry")
energy_kwh_m3 = {}
for k, ae, mix in (("low", 2.0, 0.2), ("base", 1.5, 0.4), ("high", 1.0, 0.8)):
    # mixing of viscous slurry over 24-48 h batch added (kWh/m3)
    energy_kwh_m3[k] = o2 / ae + mix
    print(f"{k:4s}: aeration eff {ae} kg O2/kWh + mixing {mix} kWh/m3 -> {energy_kwh_m3[k]:.2f} kWh/m3")

print("\n=== 4. Slurry volume per ha and energy per t CO2e ===")
vol = {"low": 150/5.0, "base": 150/3.5, "high": 200/3.0}  # m3/ha (N content kg/m3)
gj_t = {}
for k in ("low", "base", "high"):
    kwh_ha = vol[k] * energy_kwh_m3[k]
    gj_t[k] = kwh_ha * 3.6e-3 / saved[k]
    print(f"{k:4s}: {vol[k]:.0f} m3/ha x {energy_kwh_m3[k]:.2f} kWh/m3 = {kwh_ha:.0f} kWh/ha -> "
          f"{gj_t[k]:.2f} GJ(el)/t CO2e abated")
# pairing for energy range: low energy uses low kWh with high savings; high uses high kWh with low savings
e_lo = vol["low"] * energy_kwh_m3["low"] * 3.6e-3 / saved["high"]
e_hi = vol["high"] * energy_kwh_m3["high"] * 3.6e-3 / saved["low"]
print(f"Energy range (best/worst pairing): {e_lo:.2f} - {e_hi:.2f} GJ/t CO2e; base {gj_t['base']:.2f}")
print(f"Compare DAC floor 0.47 GJ/t, real DAC 5-10 GJ/t: energy is not the binding constraint.")

print("\n=== 5. NH3-stripping debit from aerating raw slurry ===")
debit = {}
for k, loss in (("low", 0.02), ("base", 0.05), ("high", 0.12)):
    n_lost = 150 * loss  # kg N/ha
    ind = n_lost * 0.01 * N2O_PER_N * GWP / 1000         # indirect N2O, EF4 1%
    repl = n_lost * 2.5 / 1000                            # replace lost N with mineral N, ~2.5 kg CO2e/kg N (gas-based NH3 + AN, assumed)
    debit[k] = ind + repl
    print(f"{k:4s}: {loss*100:.0f}% NH3-N loss = {n_lost:.1f} kg N/ha -> indirect N2O {ind:.3f} + replacement N {repl:.3f}"
          f" = {debit[k]:.3f} t CO2e/ha (plus PM2.5 harm, unpriced)")
net = {"low": saved["low"] - debit["high"], "base": saved["base"] - debit["base"], "high": saved["high"] - debit["low"]}
for k in net:
    print(f"Net saving {k}: {net[k]:.3f} t CO2e/ha/yr")

print("\n=== 6. Cost per t CO2e (bottom-up, contractor/farm batch reactor) ===")
def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)
cost_m3 = {}
for k, capex, thru, price, cons in (
        ("low",  30_000, 12_000, 0.12, 0.15),   # 100 m3 aerated tank reused, long spreading season
        ("base", 45_000, 7_000,  0.20, 0.35),   # 60 batches/yr x ~120 m3 in spring/autumn windows
        ("high", 70_000, 4_000,  0.30, 0.80)):  # inoculum production + qPCR QA per batch
    ann = capex * crf(0.08, 10) + 0.03 * capex  # 8%, 10 yr, 3% O&M
    cap_m3 = ann / thru
    en = energy_kwh_m3[k] * price
    cost_m3[k] = cap_m3 + en + cons
    print(f"{k:4s}: capex ${capex:,} -> ${ann:,.0f}/yr over {thru:,} m3 = ${cap_m3:.2f}/m3; energy ${en:.2f}/m3 "
          f"(${price}/kWh); inoculum+QA ${cons:.2f}/m3 -> ${cost_m3[k]:.2f}/m3")
cost_ha = {k: cost_m3[k] * vol[k] for k in cost_m3}
for k in cost_ha:
    print(f"{k:4s}: ${cost_ha[k]:.0f}/ha (claimant assumed $10-30/ha)")
c_lo = cost_ha["low"] / net["high"]
c_base = cost_ha["base"] / net["base"]
if net["low"] <= 0:
    print(f"Worst case: net saving {net['low']:.3f} t CO2e/ha is <= 0 -> cost per tonne UNDEFINED "
          f"(the NH3-stripping debit erases the abatement). Using the gross-saving denominator instead "
          f"as a floor on the high estimate.")
    c_hi = cost_ha["high"] / saved["low"]
else:
    c_hi = cost_ha["high"] / net["low"]
print(f"Cost per t CO2e (net of NH3 debit): low ${c_lo:.0f}, base ${c_base:.0f}, high ${c_hi:.0f}")
print(f"Same cost on gross savings (no NH3 debit): low ${cost_ha['low']/saved['high']:.0f}, "
      f"base ${cost_ha['base']/saved['base']:.0f}, high ${cost_ha['high']/saved['low']:.0f}")
# claimant check
for c in (10, 30):
    print(f"Claimant check: ${c}/ha at EF 1%, cut 30-60% -> ${c/(e_claim*0.6):.0f}-{c/(e_claim*0.3):.0f}/t")
print("MRV not included: field N2O flux measurement is ~$ thousands/site; payers will need modelled MRV.")

print("\n=== 7. Global scale ===")
synth, manure = 110.0, 31.0
for ef in (0.008, 0.012):
    g = (synth + manure) * 1e6 * ef * N2O_PER_N * GWP / 1e12  # Gt? Mt N *1e6 t * ...
    # (Mt N -> t N) * EF -> t N2O-N * 44/28 -> t N2O * 273 -> t CO2e ; /1e9 for Gt
    g = (synth + manure) * 1e6 * ef * N2O_PER_N * GWP / 1e9
    print(f"All applied N {synth+manure:.0f} Mt N x EF {ef*100:.1f}% -> {g:.2f} Gt CO2e/yr direct soil N2O")
g_claim = (0.48, 0.72)
claim_reach = (0.48*0.5*0.2*0.3, 0.72*0.6*0.4*0.5)
print(f"Claimant reach (all soils): {claim_reach[0]*1000:.0f}-{claim_reach[1]*1000:.0f} Mt CO2e/yr")
# Vector-limited: only land receiving liquid slurry. Persistence means mineral N on same fields also covered.
res = []
for k, slurry_share, n_ha_total, ef, dd_share, adopt, cut in (
        ("low",  0.35, 150, 0.008, 0.55, 0.20, 0.30),
        ("base", 0.50, 180, 0.010, 0.65, 0.30, 0.45),
        ("high", 0.60, 220, 0.012, 0.75, 0.40, 0.60)):
    slurry_n = manure * slurry_share  # Mt N
    area_mha = slurry_n / 0.150  # Mt N / (0.150 t N per ha) = Mha at ~150 kg slurry-N/ha
    emis_gt = area_mha * 1e6 * n_ha_total * ef * N2O_PER_N * GWP / 1e3 / 1e9  # Mha->ha, kg N/ha, ->t CO2e, ->Gt
    abate = emis_gt * dd_share * adopt * cut
    res.append(abate)
    print(f"{k:4s}: slurry N {slurry_n:.1f} Mt -> {area_mha:.0f} Mha; N2O there {emis_gt*1000:.0f} Mt CO2e; "
          f"x denitrif.-dominated {dd_share} x adoption {adopt} x cut {cut} = {abate*1000:.1f} Mt CO2e/yr")
print(f"Vector-limited realistic scale: {res[0]*1000:.1f} / {res[1]*1000:.1f} / {res[2]*1000:.1f} Mt CO2e/yr "
      f"= {res[1]/TOTAL_GHG_GT_CO2E*100:.3f}% of global GHG (base)")

print("\n=== 8. Resource needs ===")
slurry_m3 = manure * 0.5 * 1e6 * 1000 / 3.5  # m3/yr, base slurry share
el_twh = slurry_m3 * energy_kwh_m3["base"] / 1e9
print(f"Treating all base-case slurry ({slurry_m3/1e9:.1f} bn m3/yr) at {energy_kwh_m3['base']:.2f} kWh/m3: "
      f"{el_twh:.1f} TWh/yr = {el_twh/WORLD_ELECTRICITY_TWH*100:.3f}% of world electricity")
print("Land: none additional. Water: none (slurry is the medium). Materials: aerated batch tanks "
      "(~1 per 4-12k m3/yr; ~0.4-1.1 million tanks if global slurry treated), inoculum starter cultures.")
