"""Gigatonne-scale limits: energy, land, water, materials, wells, storage lifetime, growth.
Inputs labelled SOURCE (fetched this session) or ASSUMPTION (literature-typical, not verified here)."""
import sys, math
sys.path.insert(0, 'climate')
from physics import *

GT = 1e9
print("== 1. Second-law efficiency ==")
floor_air = gj_per_tonne(min_separation_work(420e-6, 0.75))
house = gj_per_tonne(400e3)  # SOURCE House et al. 2011 PNAS abstract: >400 kJ/mol for air capture
print(f"air floor {floor_air:.3f} GJ/t; House 2011 empirical >400 kJ/mol = {house:.2f} GJ/t -> 2nd-law eff <= {floor_air/house:.1%}")
iea_dac = 30/3.3   # SOURCE IEA Net Zero Roadmap 2023: 3.3 Gt DACS ~30 EJ/yr
print(f"IEA NZR2023 implied DAC energy = {iea_dac:.1f} GJ/t -> eff {floor_air/iea_dac:.1%} (energy basis)")
# Exergy basis for solid-sorbent DAC (ASSUMPTION: 6 GJ heat at 100 C + 1.5 GJ electricity per t)
for heat, Th, el in [(6.0, 100, 1.5), (5.0, 85, 1.0), (8.0, 120, 2.0)]:
    carnot = 1 - T0/(Th+273.15)
    ex = heat*carnot + el
    print(f"  S-DAC heat {heat} GJ @{Th}C + {el} GJe: energy {heat+el:.1f} GJ/t, exergy {ex:.2f} GJ/t -> exergetic eff {floor_air/ex:.1%}")
# point-source amine (ASSUMPTION: 2.6-3.5 GJ reboiler heat at ~120 C + ~0.4 GJe compression/aux)
fl_coal = gj_per_tonne(min_separation_work(0.12, 0.9)); fl_gas = gj_per_tonne(min_separation_work(0.04, 0.9))
for heat in (2.6, 3.5):
    ex = heat*(1-T0/393.15) + 0.1  # 0.1 GJe pumps/fans excl. compression (compression is to 150 bar, separate)
    print(f"  amine reboiler {heat} GJ @120C: exergy {ex:.2f} GJ/t -> eff coal {fl_coal/ex:.0%}, gas {fl_gas/ex:.0%}")
comp = gj_per_tonne(R*T0*math.log(150/1.0))
print(f"  isothermal ideal compression 1->150 bar floor: {comp:.3f} GJ/t (same for every route; real ~0.3-0.4 GJe/t ASSUMPTION)")

print("\n== 2. Energy per Gt/yr and share of world energy ==")
for lab, gj in [("floor air", floor_air), ("6 GJ/t", 6), ("IEA-implied 9.1", iea_dac), ("House >9.1", house)]:
    s = ScaleCheck(1.0, gj)
    print(f"  1 Gt/yr DAC @ {lab}: {s.ej_per_year:.2f} EJ/yr = {s.share_of_world_primary_energy:.2%} of world primary; "
          f"10 Gt/yr: {10*s.share_of_world_primary_energy:.1%}")

print("\n== 3. Air processed (cross-check IEA '0.1% of atmosphere per year' for 3.3 Gt) ==")
atm_mol = 5.15e18/0.02897   # mass of atmosphere / molar mass of air
for gt in (1, 3.3, 10):
    mol_air = gt*GT*1e6/44.01/(420e-6*0.75)
    print(f"  {gt} Gt/yr at 75% capture: {mol_air/atm_mol:.3%} of atmosphere per year; {air_volume_per_tonne(420e-6,0.75)*gt*GT:.2e} m3")

print("\n== 4. Land per Gt/yr ==")
beccs_mha_per_gt = 135/2   # SOURCE IEA NZR2023: 2 Gt BECCS ~ 135 Mha feedstock land
dac_pv_mha_per_gt = 4.5/3.3  # SOURCE IEA NZR2023: 3.3 Gt DACS on solar PV ~4.5 Mha
cropland = 1570  # ASSUMPTION FAO global cropland ~1.57 Gha
print(f"  BECCS {beccs_mha_per_gt:.0f} Mha/Gt ({beccs_mha_per_gt/cropland:.1%} of world cropland per Gt); DAC+PV {dac_pv_mha_per_gt:.2f} Mha/Gt; ratio {beccs_mha_per_gt/dac_pv_mha_per_gt:.0f}x")

print("\n== 5. Water: dissolved-CO2 mineral injection (Carbfix-type) ==")
kH = 0.034  # mol/(L atm) at 25C ASSUMPTION (Sander compilation); ideal Henry's law, overestimates at high P
for p_bar in (25, 40):
    c = kH*p_bar/1.01325*44.01  # g/L
    print(f"  CO2 solubility ~{c:.0f} g/L at {p_bar} bar -> {1e3/c:.0f} t water per t CO2 -> {1e3/c:.0f} km3 per Gt")
global_withdrawal = 4000  # km3/yr ASSUMPTION (FAO AQUASTAT ~4,000 km3/yr)
print(f"  25 km3/Gt = {25/global_withdrawal:.1%} of global freshwater withdrawal (seawater usable per Carbfix pilots)")

print("\n== 6. Materials ==")
# Ex-situ mineralisation stoichiometry
ol = 140.69/(2*44.01); serp = 277.11/(3*44.01); basalt = 1/0.3  # basalt ~0.3 t CO2/t theoretical ASSUMPTION
print(f"  olivine {ol:.2f} t/t CO2, serpentine {serp:.2f} t/t, basalt ~{basalt:.1f} t/t -> per Gt: {ol:.1f}-{basalt:.1f} Gt rock")
coal_mined = 8.7  # Gt/yr 2023 ASSUMPTION (IEA Coal 2023 ~8.7 Gt)
print(f"  i.e. {ol/coal_mined:.0%}-{basalt/coal_mined:.0%} of global coal tonnage mined, per Gt CO2 stored")
# Sorbent replacement for S-DAC (ASSUMPTION: working capacity 1 mmol/g, 2-4 cycles/day, life 0.5-2 yr)
for wc, cyc, life in [(1.0, 3, 1.0), (0.5, 2, 0.5), (2.0, 4, 2.0)]:
    t_co2_per_t_sorb_life = wc*1e-3*44.01*cyc*365*life
    print(f"  sorbent wc={wc} mmol/g, {cyc} cyc/d, life {life} yr: {GT/t_co2_per_t_sorb_life/1e6:.1f} Mt sorbent/yr per Gt")

print("\n== 7. Injection wells and storage lifetime ==")
well = 0.7  # SOURCE Ringrose & Meckel 2019: P50 0.7 Mt/yr/well (P90 0.33, P10 1.06)
for gt in (1, 6.04, 8.7, 15):
    print(f"  {gt} Gt/yr: {gt*1e3/well:,.0f} wells (P50), {gt*1e3/0.33:,.0f} (P90) ")
prudent = 1460  # SOURCE Gidden et al. 2025 Nature
for rate in (8.7, 15):
    print(f"  prudent limit {prudent} Gt at {rate} Gt/yr -> {prudent/rate:.0f} years")
print(f"  prudent limit / fossil CO2 2024 ({FOSSIL_CO2_GT} Gt): {prudent/FOSSIL_CO2_GT:.0f} years of today's fossil emissions")

print("\n== 8. Growth rates ==")
c22 = 0.045  # SOURCE IEA NZR2023 table, 2022 captured 45 Mt
for target, yr in [(1.024, 2030), (6.04, 2050)]:
    print(f"  45 Mt (2022) -> {target} Gt ({yr}): CAGR {(target/c22)**(1/(yr-2022))-1:.0%}")
print(f"  Kazlou 2024 feasible 0.37 Gt by 2030 -> CAGR from 2022 {(0.37/c22)**(1/8)-1:.0%}")
print(f"  Sleipner 1996 (~1 Mt) -> 45 Mt 2022: historical CAGR {(45/1)**(1/26)-1:.0%}")
