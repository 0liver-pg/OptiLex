import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
V = air_volume_per_tonne(X_AIR, 0.75)
print("=== B: exhaust concentration of the steam-dosed radical trap if all of it leaves with the air ===")
for g_per_t in (2.2, 22.3, 222.8):
    print(f"  {g_per_t} g per t CO2 over {V:,.0f} m3 -> {g_per_t/V*1e6:.2f} ug/m3 average in exhaust")
print("=== B/C value: halving or thirding fade from 2.2e-3 %/cycle, $20 and $50/kg, wc 1.04 ===")
def cost(f, price):
    cyc = 20 / f
    return sorbent_cost_per_tonne(price, 1.04 * 0.9, cyc)
for price in (20, 50):
    print(f"  ${price}/kg: 2.2e-3 ${cost(2.2e-3,price):.0f}/t; /2 ${cost(1.1e-3,price):.0f}/t; /3 ${cost(2.2e-3/3,price):.0f}/t")
print("=== D: kinetics-limited cycle for a 100 um resin sheet (measured half-time 31.8 min at 400 ppm, 30% RH; Shi 2017) ===")
t_half = 31.8
for n_half, rel in ((1, 15), (2, 15), (2, 30)):
    load = 1 - 0.5 ** n_half
    cyc_min = n_half * t_half + rel
    cpd = 1440 / cyc_min
    for wc in (0.73, 0.9):
        print(f"  load {n_half} half-times ({load:.0%}) + {rel} min wet release: {cpd:.1f} cycles/day -> {productivity(wc*load, cpd):.2f} kg/kg/day at wc {wc}")
print("  measured beads/packets 0.19-0.27 kg/kg/day (map); ASU drying alone 30 min before any uptake, 2 h day / 4 h night cycles")
print("=== E: low NH3 yield cases (pilot autopsy found oxidation without loss of N) ===")
lod = 0.01e-3 / 18.04 * 0.010 * 1e9
for Y in (0.01, 0.03, 0.1):
    for m in (1, 10):
        nmol = 1e-3 / 100 * 1.04 * 1e-3 * m * Y * 1e9
        print(f"  Y {Y}, {m} g, fade 1e-3 %/cycle: {nmol:.2f} nmol/cycle -> {math.ceil(3*lod/nmol)} cycles to 3x IC LOD ({lod:.1f} nmol in 10 mL)")
print("=== A: accelerated outdoor-equivalent exposure for the falsifying test ===")
air_per_g_cycle = 1.04e-3 / (X_AIR * P0 / (R * T0) * 0.75)
print(f"  air per g sorbent per cycle (wc 1.04, 75% capture): {air_per_g_cycle:.3f} m3")
for cycles in (10000, 20000):
    ppbm3 = cycles * air_per_g_cycle * 1.0
    for spike, flow in ((100, 1.0), (500, 1.0)):
        days = ppbm3 / (spike * flow * 1.44)
        print(f"  {cycles:,} cycles at 1 ppb-eq = {ppbm3:.0f} ppb*m3 per g -> {days:.1f} days at {spike} ppb SO2 spike, {flow} L/min per g")
print("=== D: air-flow-limited (passive/low-fan) contactor: drying then loading are sequential ===")
Tamb = 293.15
psat = lambda T: 610.94 * math.exp(17.625 * (T - 273.15) / (T - 273.15 + 243.04))
dw = 0.40 * psat(Tamb) / (R * Tamb)
co2 = X_AIR * P0 / (R * Tamb) * 0.5
for air_per_kg in (0.1, 0.02):
    for label, g in (("immersion packet 3.3 g/g", 3.3), ("metered 0.6 g/g", 0.6), ("metered 0.4 g/g", 0.4)):
        W = g / 0.018 / 0.9
        t_dry = W * 0.9 / (dw * air_per_kg) / 60
        t_load = 0.9 / (co2 * air_per_kg) / 60
        cyc = t_dry + max(t_load, 2 * 31.8) + 15
        print(f"  air {air_per_kg} m3/s per kg, {label}: W {W:.0f} mol/mol, drying {t_dry:.0f} min + loading {max(t_load, 63.6):.0f} min + 15 -> "
              f"{1440/cyc:.1f} cycles/day -> {productivity(0.9*0.75 if t_load < 63.6 else 0.9, 1440/cyc):.2f} kg/kg/day")
