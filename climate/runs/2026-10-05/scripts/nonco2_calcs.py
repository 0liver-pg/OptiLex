"""Non-CO2 GHG calculations for the OptiLex climate idea engine map (methane, N2O, AMR)."""
import sys
sys.path.insert(0, 'climate')
from physics import *

G100F, G100B, G20F, G20B = GWP100["CH4_fossil"], GWP100["CH4_biogenic"], GWP20["CH4_fossil"], GWP20["CH4_biogenic"]

print("=== 1. Value of recovered gas per t CH4 and per t CO2e ===")
HHV_MJ_PER_KG = 55.5          # methane HHV
MMBTU_PER_T = HHV_MJ_PER_KG * 1000 / 1055.06
print(f"1 t CH4 = {MMBTU_PER_T:.1f} MMBtu (HHV)")
for label, p in [("US Henry Hub ~$3.5", 3.5), ("EU TTF/Asia LNG ~$11", 11.0)]:
    v = MMBTU_PER_T * p
    print(f"  {label}: ${v:.0f}/t CH4 = ${v/G100F:.1f}/t CO2e (GWP100) = ${v/G20F:.1f}/t CO2e (GWP20)")
# 100 bcm recovered
DENS = 0.678  # kg/m3 CH4 at 15 C, 1 atm
mt_per_bcm = DENS  # 1e9 m3 * kg/m3 / 1e9 = Mt
print(f"100 bcm = {100*mt_per_bcm:.0f} Mt CH4; value at $3.5 = ${100*mt_per_bcm*1e6*MMBTU_PER_T*3.5/1e9:.0f} bn, at $11 = ${100*mt_per_bcm*1e6*MMBTU_PER_T*11/1e9:.0f} bn")
nnc = 35e6
print(f"35 Mt CH4 no-net-cost = {nnc*G100F/1e9:.2f} Gt CO2e (GWP100) = {nnc*G20F/1e9:.2f} Gt CO2e (GWP20); "
      f"= {nnc*G100F/1e9/FOSSIL_CO2_GT*100:.1f}% of fossil CO2 (GWP100)")
s = ScaleCheck(nnc*G100F/1e9, 6.0)
print(f"  removing the same GWP100 CO2e by DAC at 6 GJ/t would need {s.ej_per_year:.1f} EJ/yr = {s.share_of_world_primary_energy*100:.1f}% world primary energy")
s0 = ScaleCheck(nnc*G100F/1e9, gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99)))
print(f"  ...even at the DAC thermodynamic floor: {s0.ej_per_year:.2f} EJ/yr")

print("\n=== 2. Coal mine ventilation air methane (VAM) RTO cost ===")
capex, opex, tch4 = 9.52e6, 0.87e6, 7236.0   # EUR, EUR/yr, t CH4/yr (MATEC 2025 design case, 0.326% CH4)
for r, n in [(0.08, 20), (0.10, 15)]:
    crf = r * (1 + r) ** n / ((1 + r) ** n - 1)
    ann = capex * crf + opex
    print(f"  r={r:.0%}, n={n}: EUR {ann/1e6:.2f}M/yr -> EUR {ann/tch4:.0f}/t CH4 = EUR {ann/(tch4*G100F):.1f}/t CO2e GWP100, EUR {ann/(tch4*G20F):.1f}/t CO2e GWP20")
print(f"  MATEC capex intensity: EUR {capex/tch4:.0f} per (t CH4/yr)")
print(f"  IEA/Ember: $2.5bn for 9.5 Mt CH4/yr -> ${2.5e9/9.5e6:.0f} per (t CH4/yr)  (ratio {capex/tch4/(2.5e9/9.5e6):.1f}x lower than MATEC case)")

print("\n=== 3. Autothermal threshold for catalytic/thermal oxidation vs CH4 concentration ===")
DH = 802e3   # J/mol CH4 (LHV)
CP = 29.1    # J/mol/K air
T_op = 1000 + 273.15  # thermal oxidiser bed ~1000 C ; catalytic ~ 450-600 C
for T_bed_C in (1000, 500):
    dT_needed = T_bed_C - 25
    for eff in (0.95, 0.97, 0.99, 0.999):
        x_min = CP * dT_needed * (1 - eff) / DH
        print(f"  bed {T_bed_C} C, regenerator eff {eff}: autothermal needs CH4 >= {x_min*1e6:,.0f} ppm ({x_min*100:.3f}%)")
for x in (1.93e-6, 10e-6, 100e-6, 3e-3):
    print(f"  CH4 {x*1e6:,.2f} ppm releases adiabatic dT = {x*DH/CP:.3f} K")

print("\n=== 4. Fan work to push gas through a contactor, per t CH4 and per t CO2e (100 Pa, 60% fan, 90% conversion) ===")
for x in (1.93e-6, 10e-6, 100e-6, 1000e-6, 3e-3):
    fw = fan_work_gj_per_tonne(x, 0.9, 100, 0.6, M_CH4)
    print(f"  {x*1e6:>8,.2f} ppm: {fw:8.1f} GJ/t CH4 = {fw/G100F:6.3f} GJ/t CO2e(100) | {fw/G20F:6.3f} GJ/t CO2e(20) | elec cost @$60/MWh ${energy_cost_floor(fw,60)/G100F:,.1f}/t CO2e(100)")
# heating energy at 10 ppm with 99% heat recovery to 300 C (catalyst light-off for Cu-zeolite ~ 300-450 C)
x = 10e-6
mol_gas_per_t = 1e6 / (M_CH4 * 1e3 * x * 0.9)
for eff in (0.9, 0.99):
    q = mol_gas_per_t * CP * 275 * (1 - eff) / 1e9
    print(f"  10 ppm heated to 300 C, recovery {eff}: heat {q:,.0f} GJ/t CH4 = {q/G100F:.1f} GJ/t CO2e(100)")

print("\n=== 5. Atmospheric oxidation enhancement scale (Horowitz 2026, ACP, single model) ===")
BURDEN_TG = 1930 * 2.78   # Tg CH4 (2.78 Tg/ppb)
E_TOT = 580.0             # Tg CH4/yr total emissions (Global Methane Budget order)
FEEDBACK = 1.3            # perturbation lifetime / steady-state lifetime
for agent, mass_tg, frac, world_tg, wname in [("Cl2", 1250, 0.143, 97, "world chlorine production ~97 Mt/yr"),
                                              ("Fe (ISA)", 565, 0.025, 1300, "world pig iron ~1.3 Gt/yr")]:
    eq_cut = frac * E_TOT / FEEDBACK
    print(f"  {agent}: {mass_tg} Tg/yr -> -{frac*100:.1f}% CH4 = burden -{frac*BURDEN_TG:,.0f} Tg; ~equivalent to cutting {eq_cut:.0f} Tg CH4/yr of emissions;"
          f" {mass_tg/eq_cut:.0f} t agent per t CH4/yr equivalent; agent mass = {mass_tg/world_tg:.1f}x {wname}")
print(f"  compare: IEA no-net-cost fossil abatement = 35 Tg CH4/yr")

print("\n=== 6. Enteric: 3-NOP (Bovaer) cost per t CO2e ===")
for ch4_g_day in (350, 450):
    annual = ch4_g_day * 365 / 1e6   # t CH4/yr per cow
    for red in (0.26, 0.30):
        abated = annual * red
        for cost in (58, 105):
            print(f"  cow {ch4_g_day} g/d, -{red:.0%}, ${cost}/cow-yr: {abated*1000:.0f} kg CH4 -> ${cost/(abated*G100B):.0f}/t CO2e(100), ${cost/(abated*G20B):.0f}/t CO2e(20)")
print("  Danish livestock tax: 300 DKK/t marginal 2030 (~$46), effective 120 DKK (~$18); 750/300 DKK in 2035")

print("\n=== 7. Industrial N2O ===")
china_adipic = 76e6  # t CO2e (AR5 GWP 265), NRDC 2026 fig
for c in (0.25, 1, 4, 13):
    print(f"  China adipic acid 76 Mt CO2e at ${c}/t = ${china_adipic*c/1e6:,.0f}M/yr")
print(f"  >100 Mt CO2e unabated industrial N2O = {100/37400*100:.2f}% of fossil CO2; at $4/t = $400M/yr")
print(f"  for comparison, DAC at $400/t for 100 Mt = ${100e6*400/1e9:.0f}bn/yr; ratio {400/4:.0f}x")
