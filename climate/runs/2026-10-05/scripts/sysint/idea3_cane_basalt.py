"""Idea 3: Indian cane-molasses distilleries on the Deccan Traps. Fermentation CO2 (pure, biogenic)
dissolved in the sugar mill's surplus cane-juice condensate and injected into deep basalt flows
(Carbfix-type in-situ mineralisation). Water by-product + CO2 by-product + rock underfoot."""
from common import *

kg_co2_per_L = 0.955 * 0.789          # stoichiometric CO2 per litre ethanol
print(f"Fermentation CO2: {kg_co2_per_L:.3f} kg per litre ethanol")
print(f"Separation floor (98% CO2 -> 99.9%): {gj_per_tonne(min_separation_work(0.98,0.9,0.999)):.4f} GJ/t")
for p in (25, 40):
    print(f"Compress 1->{p} bar for dissolution: ideal {iso_comp_gj_t(1,p):.3f} GJ/t, real ~{iso_comp_gj_t(1,p)/0.65/0.0036:.0f} kWh/t")

# Ethanol per tonne cane by route (literature ranges, from memory, unverified)
routes = {"C-molasses": (10, 12), "B-heavy molasses": (20, 25), "cane juice/syrup": (70, 80)}
cond = (0.30, 0.45)       # t surplus condensate per t cane after in-mill reuse (assumption, unverified)
water_need = (17, 27)     # t water per t CO2 for full dissolution at 25-40 bar (map: 17-27)
print("\nWater balance per tonne cane:")
for r, (lo, hi) in routes.items():
    co2 = (lo * kg_co2_per_L / 1000, hi * kg_co2_per_L / 1000)
    need = (co2[0] * water_need[0], co2[1] * water_need[1])
    print(f"  {r}: {lo}-{hi} L/t cane -> {co2[0]*1000:.0f}-{co2[1]*1000:.0f} kg CO2/t cane -> needs "
          f"{need[0]:.2f}-{need[1]:.2f} t water/t cane vs surplus condensate {cond[0]}-{cond[1]} t")

print("\nScale (ethanol volumes are order-of-magnitude, unverified this run):")
for name, bnL in [("India cane-based ethanol (~4-5 bn L/yr)", 4.5), ("Maharashtra+N. Karnataka cane ethanol (~2-3 bn L)", 2.5),
                  ("India all ethanol E20 (~10 bn L)", 10)]:
    print(f"  {name}: {bnL*1e9*kg_co2_per_L/1e9:.1f} Mt CO2/yr")

print("\nEnergy per tonne stored (my assumptions):")
comp = iso_comp_gj_t(1, 30) / 0.65
pump_water = 22 * 3e6 / 0.75 / 1e9     # 22 m3/t at 3 MPa wellhead overpressure
print(f"  compression {comp:.2f} GJ_e/t + water injection pumping {pump_water:.2f} GJ_e/t = {comp+pump_water:.2f} GJ_e/t "
      f"(= {(comp+pump_water)/0.0036:.0f} kWh/t); at India grid ~0.7 kg CO2/kWh that emits "
      f"{(comp+pump_water)/0.0036*0.7/1000:.2f} t CO2 per t stored ({(comp+pump_water)/0.0036*0.7/10:.0f}%)")
print(f"  vs DAC floor {gj_per_tonne(min_separation_work(420e-6,0.75)):.2f} GJ/t and real DAC 5-10+ GJ/t")

print("\nCost sketch per t CO2 (my assumptions):")
for well_cost, inj_kt in [(1.5e6, 20), (3e6, 10)]:
    wells = well_cost * crf(0.10, 20) / (inj_kt * 1e3)
    energy = (comp + pump_water) / 0.0036 * 90 / 1000      # $90/MWh industrial tariff
    mrv = 10
    other = 8     # mixing, water treatment, compressor capex
    print(f"  well ${well_cost/1e6:.1f}M serving {inj_kt} kt/yr -> ${wells:.0f}/t; energy ${energy:.0f}/t; MRV ${mrv}; other ${other} "
          f"-> ${wells+energy+mrv+other:.0f}/t vs Carbfix ~$25-30/t (Hellisheidi, geothermal gas) and durable CDR $150-600/t")
print("\nRock demand (stoichiometric, map: ~3.3 t basalt per t CO2):",
      "1 Mt/yr ->", 3.3, "Mt/yr basalt reacted in situ")
