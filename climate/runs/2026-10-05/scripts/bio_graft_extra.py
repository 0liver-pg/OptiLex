import sys, math
sys.path.insert(0, 'climate')
from physics import *
def hp_cop(ts, tk, f=0.5):
    return f*(tk+273.15)/(tk-ts)
# Idea 1: average energy cost to take a 0.85 t CO2/t clinker kiln to 90% capture
co2 = 0.85; cap = 0.9*co2
free_hi = 1.15  # GJ/t clinker >130 C (calibrated to Brevik 50% at 2.7 GJ/t)
for name, Q, free, cop in [("amine 2.7 GJ/t + HP to 130 C", 2.7, free_hi, hp_cop(45,130)),
                           ("CA-K2CO3 3.0 GJ/t + low-T heat + HP to 80 C", 3.0, free_hi+0.22, hp_cop(45,80)),
                           ("CA-K2CO3 3.0 GJ/t, generous low-T heat", 3.0, free_hi+0.45, hp_cop(45,80))]:
    short = max(cap*Q - free, 0)
    kwh = short/cop/0.0036
    print(f"{name}: shortfall {short:.2f} GJ/t clk, HP {kwh:.0f} kWh/t clk = {kwh/cap:.0f} kWh/t CO2 avg -> ${kwh/cap*0.06:.1f}/t CO2 @ $60/MWh")
short = cap*2.7 - free_hi
print(f"amine + gas boiler: {short:.2f} GJ/t clk -> ${short/0.9*10/cap:.1f}/t CO2 and {short/0.9*0.0561/cap:.3f} t CO2 extra per t captured")
# Idea 5: grid-intensity break-even for e-boiler / HP regeneration vs steam extraction replaced by a gas peaker
for label, mwh in [("e-boiler", (3.0+0.4)/3.6), ("HP COP 2.37", 3.0/hp_cop(45,130)/3.6+0.4/3.6)]:
    base = 0.37*0.45  # t CO2 per t captured: lost peak output replaced by 0.45 t/MWh gas
    print(f"{label}: {mwh:.2f} MWh/t; worse than steam extraction if off-peak marginal grid > {base/mwh:.2f} t/MWh; at 0.4 t/MWh emits {0.4*mwh:.2f} t per t captured")
# Idea 2: first-order rate constant thresholds
for RE, ebrt in [(0.5, 393), (0.5, 1180), (0.9, 393)]:
    k = -math.log(1-RE)/ebrt
    print(f"RE {RE:.0%} at EBRT {ebrt} s needs k = {k:.5f} 1/s (half-life {math.log(2)/k/60:.1f} min)")
print("net t CO2e per shaft (300 m3/s, 0.2%, 50% RE):", round(5665*(GWP100['CH4_fossil']-44.01/16.04)/1e3,1), "kt/yr")
for frac in (0.2, 0.4):
    mt = 9.5*frac*0.5
    print(f"sub-autothermal share {frac:.0%} of 9.5 Mt CH4 VAM-abatable, 50% RE: {mt:.2f} Mt CH4 = {mt*(GWP100['CH4_fossil']-44.01/16.04):.0f} Mt CO2e")
