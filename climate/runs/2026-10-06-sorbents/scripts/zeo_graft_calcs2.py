import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
ref = reference_amine_cycle(); wc = ref.working_capacity
print("=== IDEA 2: METAL INGRESS MASS BALANCE ===")
V = air_volume_per_tonne(X_AIR, 0.75)   # m3 air per t CO2
kg_co2_per_kg_cycle = wc*M_CO2
print(f"air per t CO2 (75% capture): {V:,.0f} m3; sorbent throughput {kg_co2_per_kg_cycle*1000:.1f} g CO2 per kg-cycle")
for cycles in (10000, 20000):
    co2_per_kg_life = kg_co2_per_kg_cycle*cycles/1000   # t CO2 per kg sorbent over life
    air_per_kg = V*co2_per_kg_life                       # m3 air per kg sorbent over life
    print(f" life {cycles} cycles: {co2_per_kg_life:.2f} t CO2 and {air_per_kg:,.0f} m3 air per kg sorbent")
    for metal, ngm3 in (("Cu rural", 1), ("Cu urban", 10), ("Fe rural PM2.5", 50), ("Fe dusty PM10", 500)):
        for f in (0.03, 0.3):
            ppm = ngm3*1e-9*air_per_kg*f/1e-6/1.0   # g metal per kg -> ppm = mg/kg
            ppm = ngm3*1e-9*air_per_kg*f*1e3        # mg per kg
            print(f"   {metal:<15} {ngm3:>4} ng/m3, deposited fraction {f}: {ppm:7.1f} ppm")
# steam-borne metals with direct steam condensing on the bed
heat_per_kg_cycle = ref.heat*wc            # J per kg sorbent per cycle
steam = heat_per_kg_cycle/2.257e6          # kg steam condensed per kg sorbent per cycle
print(f"direct-steam condensate on bed: {steam:.3f} kg per kg sorbent per cycle (all heat by condensing steam, ref cycle)")
for metal, ppb in (("Fe", 10), ("Fe", 50), ("Cu", 2), ("Cu", 10)):
    for cycles in (10000, 20000):
        ppm = steam*ppb*1e-9*cycles*1e6  # mg/kg
        print(f"   steam {metal} {ppb} ppb, {cycles} cycles: {ppm:.1f} ppm on sorbent (if non-volatile and retained)")
# chelator stoichiometry: 0.5 wt% sodium phytate (~923 g/mol for Na12-phytate? use phytic acid 660 g/mol, 6 phosphate) vs 20 ppm Cu (0.31 mmol/kg)
cu_mol = 20e-3/63.5   # mol per kg at 20 ppm
print(f"20 ppm Cu = {cu_mol*1e3:.2f} mmol/kg; 0.1 wt% phytic acid = {1.0/660*1e3:.2f} mmol/kg (6 phosphate groups each)\n")

print("=== IDEA 5: REDUCTIVE (IMINE) REJUVENATION ===")
# value: if each treatment recovers fraction r of lost capacity, effective fade -> (1-r) x fade
for fade in (3.5e-3, 2.2e-3):
    base = sorbent_cost_per_tonne(20, wc, 20/fade)
    for r in (0.3, 0.5, 0.7):
        eff = sorbent_cost_per_tonne(20, wc, 20/(fade*(1-r)))
        print(f"  fade {fade:.1e} %/cycle: replace at 20% loss ${base:.0f}/t; with reduction recovering {r:.0%} of loss each time ${eff:.0f}/t (+ reagent)")
# NaBH4 dose: restore 1 mol imine per kg needs 0.25 mol NaBH4 (4 hydrides) -> 9.5 g; with 3x excess ~28 g; at $15/kg
for imine in (0.5, 1.0, 2.0):
    g = imine/4*37.83*3
    print(f"  {imine} mol imine/kg -> {g:.0f} g NaBH4 per kg sorbent (3x excess) = ${g/1000*15:.2f}/kg at $15/kg; per t CO2 over a 5,000-cycle interval: ${g/1000*15/(wc*M_CO2*5000)*1000:.2f}/t")
