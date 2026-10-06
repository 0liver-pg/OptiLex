import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math
import numpy as np

M = 0.04401  # kg/mol CO2

print("=== 1. Sorbent replacement cost, no fade (verifier function) ===")
for price in (5, 20, 50):
    for cyc in (2000, 5000, 15000, 50000, 100000):
        print(f"  ${price}/kg, wc 1.04 mol/kg, {cyc:>6} cycles -> ${sorbent_cost_per_tonne(price, 1.04, cyc):7.1f}/t")

print("\n=== 2. Cycles per calendar period at given cycle time (100% uptime) ===")
for cyc_min in (20, 30, 60, 120, 240):
    per_yr = 365*24*60/cyc_min
    print(f"  {cyc_min:>3} min cycle: {per_yr:8.0f} cycles/yr; 3 months = {per_yr/4:7.0f}; 2 yr = {2*per_yr:8.0f}")

print("\n=== 3. Hunter-Sellars 2026 Table 1 consistency check ===")
# stated: kdegrad 5.1e-3 %/cycle, replacement at 30% fade, cycles_rep = 15363, 20 min cycle
k = 5.1e-5
n_exp = math.log(0.7)/math.log(1-k)
print(f"  exponential fade (1-k)^n=0.7 with k=5.1e-3 %/cycle -> n = {n_exp:.0f} cycles")
k_imp = 1 - 0.7**(1/15363)
print(f"  k implied by 15363 cycles to 30% fade = {k_imp*100:.2e} %/cycle")
# alternative reading: average capacity over life is 70%?? solve mean((1-k)^i) = 0.7
def mean_cap(n, k): return (1-(1-k)**n)/(n*k)
lo, hi = 1, 1e6
for _ in range(100):
    mid = 0.5*(lo+hi)
    if mean_cap(mid, k) > 0.7: lo = mid
    else: hi = mid
print(f"  cycles at which MEAN capacity = 70% (k=5.1e-3 %/cycle): {lo:.0f}")
print(f"  15363 cycles x 20 min = {15363*20/60/24:.0f} days = {15363*20/60/24/365:.2f} yr at 100% duty")

print("\n=== 4. NETL 2022 sorbent-price sensitivity -> implied sorbent consumption ===")
# COC 702 at $0.20/kg; 1030 at $15/kg; 2910 at $100/kg ; lifetime 0.5 yr
s1 = (1030-702)/(15-0.2); s2 = (2910-702)/(100-0.2)
print(f"  slope = {s1:.1f} and {s2:.1f} $/t per $/kg  => {s1:.0f} kg sorbent consumed per t CO2 at 0.5 yr life")
print(f"  => lifetime CO2 per kg sorbent = {1000/s1:.0f} kg CO2/kg = {1000/s1/M/1.0:.0f} mol/kg total")
print(f"  if wc = 1.0 mol/kg that is only {1000/s1/M/1.0:.0f} cycles in 0.5 yr (~{0.5*365*24/(1000/s1/M/1.0):.1f} h per cycle)")

print("\n=== 5. Optimal replacement with exponential fade: plant-level trade-off ===")
# Cost per tonne = (fixed capital+O&M charge per kg-sorbent-slot per cycle)/(CO2 per cycle) + sorbent price/(cumulative CO2)
# fixed charge expressed as $/t at fresh capacity: C_fix0. With fade, fixed cost per t scales as 1/mean_capacity.
def lcod(n, k, price, wc0, C_fix0, C_energy):
    mean = mean_cap(n, k)
    co2_per_kg = wc0*mean*n*M/1000.0   # t CO2 per kg sorbent over life
    return C_fix0/mean + C_energy + price/co2_per_kg, C_fix0/mean, price/co2_per_kg
C_fix0, C_energy, wc0 = 274.0, 100.0, 1.04   # $/t capital charge (OptiLex Stratos-like), energy placeholder
print(f"  assumptions: fixed charge ${C_fix0}/t at fresh capacity, energy ${C_energy}/t, wc0 {wc0} mol/kg")
for price in (5, 20, 50):
    for kpct in (1e-1, 2e-2, 5.1e-3, 1e-3, 2e-4):
        k = kpct/100
        ns = np.logspace(2, 6, 4000)
        vals = [lcod(n, k, price, wc0, C_fix0, C_energy)[0] for n in ns]
        i = int(np.argmin(vals)); n = ns[i]
        tot, fx, sb = lcod(n, k, price, wc0, C_fix0, C_energy)
        print(f"  ${price:>2}/kg, fade {kpct:.0e} %/cycle: optimum replace at {n:8.0f} cycles (fade {100*(1-(1-k)**n):4.1f}%), "
              f"total ${tot:6.0f}/t = fixed {fx:5.0f} + energy {C_energy:.0f} + sorbent {sb:5.0f}")

print("\n=== 6. Holmes-type claim check: 3-month vs 1-year replacement ===")
# at 30-min cycles: 3 months = 4380 cycles, 1 yr = 17520. Sorbent cost alone, no fade:
for price in (15, 50, 100):
    a = sorbent_cost_per_tonne(price, 1.04, 4380); b = sorbent_cost_per_tonne(price, 1.04, 17520)
    print(f"  ${price}/kg: 3-month life ${a:.0f}/t vs 1-yr life ${b:.0f}/t  (saving ${a-b:.0f}/t)")

print("\n=== 7. Degradation-rate budget: what per-cycle and per-hour loss rates do lifetimes imply? ===")
for target_cycles in (2000, 20000, 100000):
    k = 1 - 0.8**(1/target_cycles)
    print(f"  20% fade at {target_cycles:>6} cycles -> {k*100:.2e} %/cycle = {k*1e6:.1f} ppm of amine sites lost per cycle")
# per-hour first order rate at hot dwell: if 5 min per cycle spent hot with O2 ingress
for target_cycles in (2000, 20000, 100000):
    hot_h = target_cycles*5/60
    kh = -math.log(0.8)/hot_h
    print(f"  {target_cycles:>6} cycles x 5 min hot = {hot_h:6.0f} h hot exposure -> first-order k must be < {kh:.2e} 1/h ({kh*24:.2e} 1/day)")
print("  Min et al. 2018 (110 C, 3% O2, 15% CO2, 10% H2O): PEI/SiO2 k=0.123/day; EB-PEI+TSP k=0.00258/day")
for name, kd in (("PEI/SiO2", 0.123), ("EB-PEI/SiO2+2%TSP", 0.00258)):
    t20 = -math.log(0.8)/kd  # days of continuous hot exposure to 20% fade
    print(f"   {name}: 20% fade after {t20:.1f} days hot = {t20*24*60/5:.0f} cycles at 5 min hot/cycle (if rate applied only while hot)")
