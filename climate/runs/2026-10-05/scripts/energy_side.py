"""Scale and cost arithmetic for energy-side, incumbent-led climate options (sourced inputs)."""
import sys
sys.path.insert(0, 'climate')
from physics import *

def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)

print("== 1. Methane: IEA GMT 2026 (2025 data) ==")
ch4_total, ch4_nnc, ch4_tech = 124.0, 35.0, 85.0       # Mt CH4
LHV_CH4 = 50.0                                          # MJ/kg
for lbl, mt in [("no-net-cost", ch4_nnc), ("existing tech", ch4_tech)]:
    print(f"{lbl}: {mt} Mt CH4 = {mt*GWP100['CH4_fossil']/1000:.2f} Gt CO2e (GWP100), "
          f"{mt*GWP20['CH4_fossil']/1000:.2f} Gt (GWP20); gas energy recovered {mt*LHV_CH4/1000:.2f} EJ")
ccs_op = 64.0  # Mtpa operational capacity, GCCSI 2025
print(f"no-net-cost CH4 (GWP100) / global operational CCS capacity = {ch4_nnc*GWP100['CH4_fossil']/ccs_op:.1f}x")
# DAC energy to remove the same CO2e
co2e = ch4_nnc * GWP100['CH4_fossil'] * 1e6  # t
floor = gj_per_tonne(min_separation_work(420e-6, 0.75, 0.99))
for gj in (floor, 6.0, 10.0):
    print(f"  DAC equivalent at {gj:.2f} GJ/t: {co2e*gj/1e9:.2f} EJ ({co2e*gj/1e9/WORLD_PRIMARY_ENERGY_EJ*100:.2f}% world PE)")

print("\n== 2. Flaring: World Bank GGFR 2025 (2024 data) ==")
flare_bcm, flare_mtco2e, flare_value = 151.0, 389.0, 63e9
HHV = 38.0  # MJ/m3, assumption for associated gas (rich); range 36-42
ej = flare_bcm * 1e9 * HHV / 1e12
twh_th = ej * 1e6 / 3600 / 1000 * 1000  # EJ -> TWh: 1 EJ = 277.8 TWh
twh_th = ej * 277.78
print(f"energy flared {ej:.2f} EJ = {twh_th:.0f} TWh_th; at 50% CCGT = {0.5*twh_th:.0f} TWh_e "
      f"= {0.5*twh_th/WORLD_ELECTRICITY_TWH*100:.1f}% of world electricity")
print(f"implied value ${flare_value/(flare_bcm*1e9):.3f}/m3 = ${flare_value/(flare_bcm*1e9)/0.0373*1.055:.1f}/MMBtu (approx)")
print(f"tCO2e per m3 flared: {flare_mtco2e*1e6/(flare_bcm*1e9):.2f} kg/m3")
crusoe_bcf = 2.5
print(f"Crusoe cumulative avoided flaring 2.5 bcf = {crusoe_bcf*0.0283:.3f} bcm = "
      f"{crusoe_bcf*0.0283/flare_bcm*100:.3f}% of ONE year of global flaring")

print("\n== 3. Geothermal LCOE (modelled, my assumptions) ==")
for capex in (7000, 5000, 3000):
    for wacc in (0.07, 0.09):
        cf, life, fom = 0.90, 30, 0.02 * capex   # FOM 2% capex/yr assumed (drilling make-up incl.)
        lcoe = (capex * crf(wacc, life) + fom) / (cf * 8.76)  # $/MWh
        print(f"capex ${capex}/kW wacc {wacc:.0%}: LCOE ~ ${lcoe:.0f}/MWh (pre-tax-credit)")
print("Fervo PPAs reported $100-130/MWh (S-1/A 2026)")

print("\n== 4. SMR (Darlington, OPG 2025) ==")
cad_usd = 0.72
tot, mw = 20.9e9, 1200
u1, mw1 = 7.7e9, 300
print(f"4-unit: C${tot/mw/1e3:,.0f}/kW = US${tot/mw/1e3*cad_usd:,.0f}/kW; first unit C${u1/mw1/1e3:,.0f}/kW")
for capex in (tot/mw/1e3*cad_usd,):
    for wacc in (0.04, 0.07):
        lcoe = (capex * crf(wacc, 60) + 0.015*capex) / (0.93 * 8.76)
        print(f"  US${capex:,.0f}/kW wacc {wacc:.0%} 60y: LCOE ~ ${lcoe:.0f}/MWh (modelled)")

print("\n== 5. Gas+CCS (NZT Power) ==")
mw, capt = 742, 2.0e6
ef = 0.35  # tCO2/MWh CCGT net before capture approx; with capture penalty ~0.40 gross
for cf in (0.5, 0.7, 0.9):
    gen = mw * 8760 * cf
    co2 = gen * 0.40  # incl ~12% energy penalty
    print(f"CF {cf:.0%}: gross CO2 {co2/1e6:.2f} Mt; 2.0 Mt design capture implies {min(capt/co2,1)*100:.0f}% of gross")
flue = gj_per_tonne(min_separation_work(0.04, 0.95, 0.99))
print(f"min work NGCC flue 4%, 95% capture: {flue:.2f} GJ/t; amine reboiler duty ~2.5-3.5 GJ/t heat "
      f"(exergy ~0.3x heat at ~120C -> ~0.8-1.1 GJ/t work-equiv; 2nd-law ~{flue/0.95:.0%})")

print("\n== 6. Gorgon (IEEFA, FY24-25) ==")
print(f"1.33 Mt = 25% of reservoir CO2 removed -> removed {1.33/0.25:.1f} Mt; 80% condition = {0.8*1.33/0.25:.1f} Mt")

print("\n== 7. US queue (LBNL Queued Up 2026) ==")
print(f"active gen+storage {1312+749} GW; with IA but not built 549 GW; median IR->COD >5 yr (2025 builds)")
print("\n== 8. CO2 storage scale vs need ==")
print(f"operational 64 Mtpa = {64/ (FOSSIL_CO2_GT*1000)*100:.2f}% of fossil CO2; +44 Mtpa construction -> {108/(FOSSIL_CO2_GT*1000)*100:.2f}%")
