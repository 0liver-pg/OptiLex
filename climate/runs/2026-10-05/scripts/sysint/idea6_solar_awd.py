"""Idea 6: groundwater-irrigated rice. Grid-connected solar irrigation pumps that are paid for exported
power make every unpumped m3 a sale, so alternate wetting and drying (AWD) pays the farmer in kWh;
pump telemetry (run-hours, kWh) plus Sentinel-1 flood detection gives field-level MRV."""
from common import *

EF = 1.19         # kg CH4/ha/day, IPCC 2019 default continuously flooded (from memory)
SF_awd = (0.52, 0.60)   # scaling factor, multiple drainage (IPCC 2006/2019 ~0.52-0.55; use up to 0.6 conservative)
days = (100, 120)
for d in days:
    base = EF * d
    for sf in SF_awd:
        cut = base * (1 - sf)
        print(f"{d} d season: baseline {base:.0f} kg CH4/ha -> AWD saves {cut:.0f} kg CH4/ha = "
              f"{cut*GWP100['CH4_biogenic']/1000:.2f} t CO2e/ha (GWP100), {cut*GWP20['CH4_biogenic']/1000:.2f} (GWP20)")
n2o_penalty = (0.1, 0.4)   # t CO2e/ha extra N2O under AWD (assumption from literature ranges, unverified)
print(f"N2O penalty assumed {n2o_penalty} t CO2e/ha")

print("\nPumping energy saved by AWD and its value as exported solar power:")
for water_mm, save, lift, eff in [(1200, 0.20, 15, 0.40), (1400, 0.25, 30, 0.40), (1500, 0.30, 40, 0.35)]:
    m3_saved = water_mm / 1000 * 1e4 * save
    kwh = m3_saved * 1000 * 9.81 * lift / eff / 3.6e6
    for tariff_inr in (3.0,):
        inr = kwh * tariff_inr
        print(f"  {water_mm} mm, {save:.0%} saved = {m3_saved:.0f} m3/ha, lift {lift} m -> {kwh:.0f} kWh/ha "
              f"-> INR {inr:,.0f}/ha (~${inr/84:.0f}) at INR {tariff_inr}/kWh feed-in")
        diesel_l = kwh / 3.0     # ~3 kWh shaft per litre in small diesel pumpsets
        print(f"     if diesel pumpset instead: ~{diesel_l:.0f} L/ha saved = {diesel_l*2.68/1000:.2f} t CO2/ha")

print("\nCarbon value per ha (methane only, GWP100) at $10-20/t:",
      [round(1.19*110*0.45*27/1000*p, 0) for p in (10, 20)], "$/ha/season")
print("\nScale envelope (areas are order-of-magnitude, unverified): groundwater-irrigated dry-season/kharif rice")
for name, mha in [("Bangladesh boro (~4.8 Mha)", 4.8), ("India Punjab+Haryana kharif (~4.5 Mha)", 4.5), ("10% of those adopting", 0.93)]:
    t = mha * 1e6 * 1.19 * 110 * 0.45 * 27 / 1e9
    print(f"  {name}: {t:.1f} Mt CO2e/yr methane cut at full AWD (before N2O offset)")
