"""Heavy-industry green-premium and energy arithmetic (illustrative; inputs labelled)."""
import sys
sys.path.insert(0, 'climate')
from physics import *

print("== 1. Green premium per end product ==")
# Steel per car: ETC 2018 used ~0.9 t; GEI 2024 premium $167-231/t; Fastmarkets EU flat premium EUR150-200/t (2026, assessed)
for label, prem in [("GEI modelled $186/t (EU, H2 $5/kg)", 186), ("Fastmarkets EU market EUR150-200/t (~$175-235)", 205)]:
    for steel_t in (0.9, 1.2):
        per_car = prem * steel_t
        print(f"  steel {steel_t} t/car x {label}: ${per_car:,.0f}/car = {per_car/30000:.2%} of $30k car; "
              f"{per_car/(30000*0.06):.1%} of a 6% EBIT margin")
# Cement CCS: Brevik estimated abatement cost ~EUR100/t CO2 (modelled, Longship); cement ~0.6 t CO2/t cement (clinker 0.71)
for cost in (100, 150):
    co2_per_t_cement = 0.6
    prem_cement = cost * co2_per_t_cement * 0.9
    for cement_per_m2 in (0.15, 0.3):  # t cement per m2 floor area (assumed range, mid-rise concrete frame)
        per_m2 = prem_cement * cement_per_m2
        print(f"  cement CCS at EUR{cost}/tCO2 -> +EUR{prem_cement:.0f}/t cement; {cement_per_m2} t/m2 -> "
              f"EUR{per_m2:.1f}/m2 = {per_m2/2000:.2%} of EUR2,000/m2 build cost")
# SAF: IATA 2025 SAF ~2x jet (up to 5x in mandated markets). Jet ~$750/t assumed (2025 pre-conflict)
jet = 750
for mult in (2, 3):
    prem_t = jet * (mult - 1)
    fuel_per_pax = 5500 * 0.025  # kg fuel per pax one-way, ~5,500 km transatlantic, ~25 g fuel/pkm (assumed)
    for share in (0.02, 0.06, 0.20, 1.0):
        print(f"  SAF {mult}x jet, {share:.0%} blend: +${prem_t*share*fuel_per_pax/1000:,.0f} per one-way transatlantic seat "
              f"({fuel_per_pax:.0f} kg fuel/pax)")
# Shipping: green methanol $600-850/t (bio) vs VLSFO ~$600/t; energy basis
vlsfo_usd_t, vlsfo_gj_t = 600, 41.0
meoh_gj_t = 19.9
for meoh in (700, 1000):  # $/t green methanol
    prem_gj = meoh / meoh_gj_t - vlsfo_usd_t / vlsfo_gj_t
    fuel_gj_per_teu = 0.375 * vlsfo_gj_t  # ~0.375 t VLSFO per TEU Asia-Europe one-way (assumed: 15k TEU ship, 150 t/d, 30 d, 80% load)
    print(f"  green methanol ${meoh}/t: premium ${prem_gj:.1f}/GJ -> ${prem_gj*fuel_gj_per_teu:,.0f}/TEU Asia-Europe "
          f"= {prem_gj*fuel_gj_per_teu/100000:.2%} of $100k cargo value")

print("\n== 2. H2-DRI energy and H2 price sensitivity ==")
h2_kg_per_t = 55     # kg H2/t steel (literature ~50-60)
kwh_per_kg = 52      # electrolyser system
mwh = h2_kg_per_t * kwh_per_kg / 1000
print(f"  electrolysis: {mwh:.2f} MWh/t steel; +~0.7 MWh EAF/other -> ~{mwh+0.7:.1f} MWh/t")
print(f"  each $1/kg H2 = ${h2_kg_per_t:.0f}/t steel; $5 vs $1.5/kg gap = ${h2_kg_per_t*3.5:.0f}/t")
# Thermodynamic floor of Fe2O3 + 3H2 -> 2Fe + 3H2O(g): need H2 at 3 mol per mol Fe2O3 = 1.5 mol H2/mol Fe
kg_h2_stoich = 1.5 * 2.016 / 55.845 * 1000
print(f"  stoichiometric H2: {kg_h2_stoich:.0f} kg/t Fe -> real plants use ~{h2_kg_per_t/kg_h2_stoich:.1f}x stoich (incl. heating H2)")
# Reduction enthalpy Fe2O3 -> 2Fe + 1.5 O2: 824 kJ/mol Fe2O3
print(f"  Fe2O3 dissociation enthalpy floor: {824e3/2/0.055845/1e9:.2f} GJ/t Fe = {824e3/2/0.055845/3.6e9:.2f} MWh/t "
      f"(electrolytic routes like MOE/Electra are bounded below by ~this, plus heat/overpotential)")
eu_bf_mt = 70  # Mt/yr EU hot metal via BF (approx, ~55% of ~130 Mt crude steel)
twh = eu_bf_mt * (mwh + 0.7)
print(f"  EU BF->H2-DRI ({eu_bf_mt} Mt): ~{twh:.0f} TWh/yr = {twh/2700:.0%} of EU electricity (~2,700 TWh)")
print(f"  global BF-BOF (~1,350 Mt): {1350*(mwh+0.7):,.0f} TWh = {1350*(mwh+0.7)/WORLD_ELECTRICITY_TWH:.0%} of world electricity")

print("\n== 3. Cement point-source capture vs thermodynamic floor ==")
for frac in (0.5, 0.9):
    w = gj_per_tonne(min_separation_work(0.25, frac))
    print(f"  kiln flue 25% CO2, {frac:.0%} capture: floor {w:.3f} GJ/t")
amine_heat, T_regen = 3.0, 393.15
ex = amine_heat * (1 - T0 / T_regen)
fl = gj_per_tonne(min_separation_work(0.25, 0.9))
print(f"  amine reboiler {amine_heat} GJ/t at {T_regen-273.15:.0f} C = {ex:.2f} GJ/t exergy -> 2nd-law eff {fl/ex:.0%} "
      f"(vs DAC ~5-10%); waste heat is the binding constraint, not separation work")
# Gas-DRI off-gas: CO2 removal already integral (Energiron); concentrations ~ high
print(f"  DRI process-gas CO2 (e.g. ~ 30-90%): floor {gj_per_tonne(min_separation_work(0.3,0.9)):.3f}-"
      f"{gj_per_tonne(min_separation_work(0.9,0.9,0.999)):.3f} GJ/t")

print("\n== 4. Steel cost of carbon at EU ETS ==")
for eua in (70, 100):
    print(f"  BF-BOF ~2.0 tCO2/t vs gas-DRI ~1.1 vs H2-DRI ~0.3: at EUR{eua}/t, carbon cost {2.0*eua:.0f} / {1.1*eua:.0f} / {0.3*eua:.0f} EUR/t steel "
          f"(but CBAM phase-in 2.5% in 2026 -> effective ~{2.0*eua*0.025:.0f} EUR/t on BF-BOF)")
