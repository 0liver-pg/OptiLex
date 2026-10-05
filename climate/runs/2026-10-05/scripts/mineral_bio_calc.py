"""Back-of-envelope checks for mineralization / ERW / biochar / BECCS / soils.
All inputs are labelled with source or 'ASSUMPTION'."""
import sys
sys.path.insert(0, 'climate')
from physics import *

GJ_PER_KWH = 0.0036
print("== Reference floor from verifier ==")
for name, x in [("air 420ppm", 420e-6), ("fermentation ~99%", 0.99)]:
    try:
        w = min_separation_work(x, capture_fraction=0.75 if x < 0.5 else 0.9)
        print(f"{name}: {w/1000:.2f} kJ/mol, {gj_per_tonne(w):.3f} GJ/t")
    except Exception as e:
        print(name, "err", e)

print("\n== 1. ERW: rock mass and grinding energy per tonne CO2 ==")
# Beerling et al. 2024 PNAS: 50 t/ha/yr x 4 yr basalt -> 10.5 +/- 3.8 t CO2/ha (time-integrated, soil-based, 'potential')
rock = 50 * 4
for cdr in (10.5 - 3.8, 10.5, 10.5 + 3.8):
    print(f"  realised CDR potential per t rock (4 yr) = {cdr/rock:.4f} t CO2/t rock (CDR {cdr} t/ha)")
real = 10.5 / rock
theo = 0.3  # literature theoretical max for basalt (~0.3 t CO2/t)
print(f"  fraction of theoretical basalt potential realised in 4 yr: {real/theo:.1%}")
# Expert elicitation 2026 (Buma et al., Commun Earth Environ): field->ocean durable efficiency ~27-39% (~1/3)
for eff in (0.27, 0.33, 0.39):
    print(f"  durable after downstream losses (eff {eff:.0%}): {real*eff:.4f} t CO2/t rock -> rock per Gt CO2 = {1/(real*eff):.0f} Gt")
print(f"  rock per Gt CO2 at field-level (no downstream loss): {1/real:.0f} Gt")
# Bond's law grinding energy, basalt Bond work index ~20 kWh/t (ASSUMPTION, typical literature value)
Wi = 20.0
F80 = 10000.0  # um, ~1 cm quarry product (ASSUMPTION)
for P80 in (1000, 100, 50, 10):
    W = 10 * Wi * (1 / P80 ** 0.5 - 1 / F80 ** 0.5)
    gj_per_t_co2_field = W * GJ_PER_KWH / real
    gj_durable = gj_per_t_co2_field / 0.33
    emis = W * 0.4 / 1000  # t CO2 per t rock at 0.4 kg/kWh grid (ASSUMPTION)
    print(f"  grind to P80={P80:>5} um: {W:5.1f} kWh/t rock -> {gj_per_t_co2_field:5.2f} GJ_e/t CO2 (field), "
          f"{gj_durable:5.2f} GJ_e/t (durable, eff 0.33); grid emissions = {emis/real:.1%} of field CDR")
# trucking penalty
for km in (50, 200, 500):
    e = km * 0.1 / 1000  # 0.1 kg CO2 / t-km truck (ASSUMPTION)
    print(f"  truck {km} km: {e*1000:.0f} kg CO2/t rock = {e/real:.1%} of field CDR")

print("\n== 2. Carbfix water demand ==")
w_per_t = 25  # t water per t CO2 (Carbfix 2016 Science paper / Carbfix materials)
for gt in (0.003, 0.1, 1.0):
    print(f"  {gt} Gt CO2/yr -> {w_per_t*gt:.3f} Gt water/yr = {w_per_t*gt*1e9/1e9:.3f} km3/yr")

print("\n== 3. Biochar mass balance ==")
for cfrac in (0.7, 0.8, 0.9):
    print(f"  biochar C content {cfrac:.0%}: {cfrac*44/12:.2f} t CO2 per t biochar (before permanence factor)")
bio_C = 0.5  # dry biomass C fraction (ASSUMPTION)
for retained in (0.4, 0.5):
    for perm in (0.75, 0.9):
        tco2 = bio_C * 44 / 12 * retained * perm
        print(f"  C retained {retained:.0%}, permanence {perm:.0%}: {tco2:.2f} t CO2/t dry biomass -> {1/tco2:.2f} Gt biomass per Gt CO2")

print("\n== 4. Ethanol fermentation BECCS ==")
# C6H12O6 -> 2 C2H5OH + 2 CO2
ratio = (2 * 44.01) / (2 * 46.07)
print(f"  {ratio:.3f} t CO2 per t ethanol (stoichiometric)")
for bgal in (15.0, 16.0):  # US production ~15-16 bn gal/yr (ASSUMPTION; EIA order of magnitude)
    mt_eth = bgal * 1e9 * 3.785 * 0.789 / 1e9  # Mt
    print(f"  US {bgal} bn gal -> {mt_eth:.1f} Mt ethanol -> {mt_eth*ratio:.1f} Mt CO2/yr; at 45Q $85/t = ${mt_eth*ratio*85/1000:.2f} bn/yr")
# compression work, 1 -> 150 bar isothermal ideal, 3 stages efficiency 70% (ASSUMPTION)
import math
R, T = 8.314, 313
w_iso = R * T * math.log(150 / 1)  # J/mol
print(f"  isothermal compression 1->150 bar: {w_iso/1000:.1f} kJ/mol = {gj_per_tonne(w_iso):.3f} GJ/t; /0.7 eff = {gj_per_tonne(w_iso)/0.7:.3f} GJ/t "
      f"({gj_per_tonne(w_iso)/0.7/GJ_PER_KWH:.0f} kWh/t)")

print("\n== 5. Soil carbon detectability ==")
mdc = 3 / 10  # Mg C/ha/yr detectable over 10 yr (Bradford et al 2023 Geoderma)
print(f"  Bradford 2023 detectable 3 Mg C/ha/10yr = {mdc*44/12:.2f} t CO2/ha/yr")
for rate in (0.1, 0.3, 0.5):  # typical practice-change accrual Mg C/ha/yr (ASSUMPTION, literature range)
    print(f"  practice rate {rate} Mg C/ha/yr = {rate*44/12:.2f} t CO2/ha/yr; years to accumulate 3 Mg C/ha: {3/rate:.0f}")

print("\n== 6. Mine tailings (Mt Keith) ==")
print(f"  39,800 t/yr passive = 11% of mine emissions -> mine emissions ~ {39800/0.11/1000:.0f} kt CO2/yr")
