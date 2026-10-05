"""Idea 4: duct coal-mine ventilation air (VAM) into the combustion-air intake of a nearby
(mine-mouth) coal or gas-fired boiler, which destroys the methane with no oxidiser capex."""
from common import *

rho_ch4 = 0.668   # kg/m3 at 20 C, 1 atm
# Boiler combustion air: 600 MWe coal unit at 40% net LHV
for mwe, eff in ((300, 0.38), (600, 0.40), (1000, 0.43)):
    fuel_mw = mwe / eff
    air_kg_s = fuel_mw * 0.34 * 1.2          # 0.34 kg stoich air per MJ coal, 20% excess
    air_m3_h = air_kg_s / 1.2 * 3600
    print(f"{mwe} MWe coal unit: fuel {fuel_mw:.0f} MWth, combustion air ~{air_m3_h/1e6:.2f} Mm3/h")

print("\nPer VAM shaft:")
for q_mm3h in (0.5, 1.0, 1.5):
    for y in (0.002, 0.004, 0.007):
        ch4_kg_s = q_mm3h * 1e6 / 3600 * y * rho_ch4
        th = ch4_kg_s * 50e6 / 1e6                  # MWth
        for cf in (0.55, 0.85):
            t_yr = ch4_kg_s * 8760 * 3600 / 1000 * cf
            if y == 0.004 and cf == 0.55 or (q_mm3h == 1.0 and cf == 0.85 and y == 0.004):
                print(f"  {q_mm3h} Mm3/h at {y:.1%} CH4: {th:.0f} MWth of fuel; boiler CF {cf}: {t_yr/1e3:.1f} kt CH4/yr "
                      f"= {t_yr*GWP100['CH4_fossil']/1e6:.2f} Mt CO2e (GWP100), {t_yr*GWP20['CH4_fossil']/1e6:.2f} Mt (GWP20)")

print("\nDuct + fan cost per t CO2e (assumptions: 1.0 Mm3/h, 0.4% CH4, boiler CF 0.55, duct $4-10M per km, 2-5 km):")
q = 1.0e6 / 3600
ch4_t = q * 0.004 * rho_ch4 * 8760 * 3600 / 1000 * 0.55
co2e = ch4_t * GWP100['CH4_fossil']
for km, capex_km, dp_pa_per_km in ((2, 4e6, 300), (5, 10e6, 400)):
    capex = km * capex_km + 3e6      # + intake tie-in, dampers, controls
    ann = capex * crf(0.08, 15)
    fan_mw = q * (dp_pa_per_km * km + 500) / 0.7 / 1e6
    fan_cost = fan_mw * 8760 * 60      # $/yr at $60/MWh, runs whole year
    fuel_credit = ch4_t * 50 * 6       # GJ x $6/GJ coal-equivalent displaced heat
    net = ann + fan_cost - fuel_credit
    print(f"  {km} km: capex ${capex/1e6:.0f}M -> ${ann/co2e:.2f}/t; fan {fan_mw:.2f} MW -> ${fan_cost/co2e:.2f}/t; "
          f"fuel credit -${fuel_credit/co2e:.2f}/t -> net ${net/co2e:.2f}/t CO2e")
print("  Reference: RTO (MATEC 2025 design case) EUR 8.5-9.8/t CO2e GWP100 (map)")
print(f"  Fan-work to push VAM 3 km vs CH4 destroyed: {q*(400*3+500)/0.7*8760*3600/1e9/ (ch4_t):.2f} GJ per t CH4 "
      f"(cf. verifier fan floor for air methane removal ~263 GJ/t CH4 at 1.93 ppm)")

print("\nAutothermal threshold reminder: an RTO needs >= ~0.18% CH4 at 95% regenerator effectiveness (map);")
print("a boiler needs no threshold because its own fuel holds flame temperature, so 0.1-0.2% VAM shafts also qualify.")

print("\nGlobal envelope: coal methane 43 Mt (IEA 2025); underground share ~0.85 x VAM share 0.7-0.8 (map)")
for share in (0.05, 0.10, 0.20):
    vam = 43 * 0.85 * 0.75
    print(f"  {share:.0%} of VAM within duct reach of a boiler x CF 0.55: {vam*share*0.55:.2f} Mt CH4/yr "
          f"= {vam*share*0.55*GWP100['CH4_fossil']:.0f} Mt CO2e GWP100")
