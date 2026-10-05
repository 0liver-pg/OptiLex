"""Patch checks for bottleneck_thermo_1 (amine-only solar collector-adsorber panel). All modelled; Wang 2024 values measured (bench/prototype)."""
import sys
sys.path.insert(0, 'climate')
from physics import *
MW = 44.01e-3
crf = lambda i, n: i*(1+i)**n/((1+i)**n-1)
Q_WANG = 10.3            # MJ/kg CO2, measured solar VPD heat (Wang et al. 2024 Nat Commun)
heat = (6.9, 12.6)       # MJ/m2/day collected (assumed, from original idea)
print("Heat-limited ceiling at Wang's measured 10.3 MJ/kg:", [round(h/Q_WANG,2) for h in heat], "kg/m2/day")
print("Max regen heat allowing 0.6 kg/m2/day at low irradiance:", round(heat[0]/0.6,1), "MJ/kg; at 0.35:", round(heat[0]/0.35,1))
fan = fan_work_gj_per_tonne(420e-6, 0.75, 10, 0.6)
print("fan 10 Pa GJ/t:", round(fan,3))
# Sorbent charge vs lifetime cycles: amine 0.9 mmol/g (Wang working capacity 0.9-1.0), $20/kg
def sorb(cycles, w=0.9, price=20, mean_frac=0.9):
    return price/(w*MW*mean_frac*cycles)*1000
for n in (1500, 3000, 4500, 6000): print(f"sorbent charge {n} cycles: ${sorb(n):.0f}/t")
# fade threshold -> cycles to 20% loss (replacement point)
for f in (5, 10): print(f"fade {f}%/1000 cycles -> 20% loss at {20/f*1000:.0f} cycles, charge ${sorb(20/f*1000):.0f}/t")
# Levelised cost, amine only. Two capex stacks.
E_kwh = 129; elec = E_kwh*60/1000; ts = 25
def lcod(L, panel, bos, i, n, om, cycles, shade=0):
    m2 = 1/(L*300/1000)
    capex = (panel+shade)*m2 + bos
    return capex*(crf(i,n)+om) + elec + ts + sorb(cycles), capex
print("\nLCOD amine ($/t): L kg/m2/day, stack, life cycles")
for L in (0.35, 0.6):
    for (lab, panel, bos, i, n, om) in (("orig-low", 100, 0, .10, 20, .04), ("orig-high", 200, 0, .10, 20, .04), ("critic", 200, 350, .08, 20, .03)):
        for cyc in (1500, 4500):
            c, cap = lcod(L, panel, bos, i, n, om, cyc)
            print(f"  L={L} {lab:9s} cycles={cyc}: capex ${cap:,.0f}/(t/yr), LCOD ${c:,.0f}/t")
# Multi-cycle mode (calendar-limited life): inventory per t/yr and sorbent charge at 5-yr calendar life
print("\nInventory & calendar-limited sorbent charge, L=0.6")
for k in (1, 3, 4):
    inv = 0.6/(0.9*MW)/k * 1/(0.6*300/1000)   # kg sorbent per t/yr
    print(f"  {k} cycles/day: {inv:.0f} kg per t/yr, charge (5-yr calendar life, $20/kg, 8%) ${inv*20*crf(.08,5):.0f}/t, + shading $30/m2 adds ${30/(0.6*.3)*(crf(.10,20)+.04) if k>1 else 0:.0f}/t")
