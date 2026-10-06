import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math, dataclasses
import numpy as np
M = 0.04401

def mean_cap(n, k):
    return 1.0 if k <= 0 else (1-(1-k)**n)/(n*k)

def cost(q_max=2.0, dH=-70e3, cycle_min=30.0, price=20.0, fade_pct=5e-3, calendar_fade_per_yr=0.0,
         cap_charge=274.0, frac_cap_scaling=0.6, heat_usd_gj=5.6, elec_usd_mwh=50.0, heat_recovery=0.0,
         water=2.0, verbose=False):
    """Simple levelized-cost model. cap_charge: $/t at the reference productivity (ref cycle, 30 min, no fade).
    frac_cap_scaling: share of capital that scales inversely with sorbent productivity (contactor, sorbent housing)."""
    ref = reference_amine_cycle()
    cyc = dataclasses.replace(ref, q_max=q_max, dH=dH, heat_recovery=heat_recovery, water_coads=water)
    wc = cyc.working_capacity
    prod_ratio0 = (wc/ref.working_capacity) * (30.0/cycle_min)   # fresh productivity relative to reference
    k = fade_pct/100.0
    cycles_per_yr = 365*24*60/cycle_min*0.9
    # per-cycle fade plus calendar (time-based) fade expressed per cycle
    k_tot = k + calendar_fade_per_yr/cycles_per_yr
    heat = cyc.heat_gj_per_t * heat_usd_gj
    elec_gj = gj_per_tonne(cyc.vacuum_work) + fan_work_gj_per_tonne(X_AIR, 0.75, 100.0)
    elec = energy_cost_floor(elec_gj, elec_usd_mwh)
    best = None
    for n in np.logspace(2, 6.3, 3000):
        mc = mean_cap(n, k_tot)
        cap = cap_charge*((1-frac_cap_scaling) + frac_cap_scaling/(prod_ratio0*mc))
        sorb = price/(wc*mc*n*M)*1000.0
        tot = cap + heat + elec + sorb
        if best is None or tot < best[0]:
            best = (tot, cap, heat, elec, sorb, n, 1-(1-k_tot)**n, n/cycles_per_yr)
    if verbose:
        tot, cap, heat, elec, sorb, n, fade, yrs = best
        print(f"   total ${tot:5.0f}/t = capital {cap:4.0f} + heat {heat:3.0f} + elec {elec:3.0f} + sorbent {sorb:4.0f}; "
              f"replace at {n:7.0f} cycles ({yrs:4.2f} yr, {fade*100:4.1f}% fade); wc {wc:.2f} mol/kg; heat {cyc.heat_gj_per_t:.2f} GJ/t")
    return best[0]

print("BASE (ref amine cycle, 30 min cycle, $20/kg, fade 5e-3 %/cycle, heat $5.6/GJ, elec $50/MWh, capital $274/t of which 60% scales with productivity)")
base = cost(verbose=True)
print("\nTORNADO: change one material/process property at a time; delta vs base")
cases = [
 ("fade 5e-3 -> 1e-3 %/cycle (5x more durable)", dict(fade_pct=1e-3)),
 ("fade 5e-3 -> 2e-4 %/cycle (25x more durable)", dict(fade_pct=2e-4)),
 ("fade 5e-3 -> 2e-2 %/cycle (4x less durable)", dict(fade_pct=2e-2)),
 ("fade 5e-3 -> 1e-1 %/cycle (20x less durable)", dict(fade_pct=1e-1)),
 ("sorbent price $20 -> $5/kg", dict(price=5.0)),
 ("sorbent price $20 -> $50/kg", dict(price=50.0)),
 ("capacity q_max 2 -> 4 mol/kg (2x working capacity)", dict(q_max=4.0)),
 ("kinetics: cycle 30 -> 15 min, same per-cycle fade", dict(cycle_min=15.0)),
 ("kinetics: cycle 30 -> 15 min, fade purely time-based (same %/yr)", dict(cycle_min=15.0, fade_pct=0.0, calendar_fade_per_yr=5e-5*365*24*2*0.9)),
 ("binding dH -70 -> -65 kJ/mol", dict(dH=-65e3)),
 ("binding dH -70 -> -75 kJ/mol", dict(dH=-75e3)),
 ("no co-desorbed water (2 -> 0 mol/mol)", dict(water=0.0)),
 ("50% sensible heat recovery", dict(heat_recovery=0.5)),
 ("heat price $5.6 -> $2/GJ (waste heat)", dict(heat_usd_gj=2.0)),
]
for name, kw in cases:
    v = cost(**kw)
    print(f"  {name:66s} ${v:5.0f}/t  ({v-base:+5.0f})")
    cost(verbose=True, **kw)

print("\nMEASURED/ASSUMED FADE RATES converted to cost (30 min cycle, $20/kg and $50/kg):")
rates = [
 ("Guta 2023 lab, unprotected PEI/Al2O3, 30 cycles humid: 52% loss", 1-(1-0.52)**(1/30)),
 ("Guta 2023 lab, unprotected PEI/Al2O3, 30 cycles dry: 29% loss", 1-(1-0.29)**(1/30)),
 ("Orca 2-yr filter: 1900/2500 run-rate, assume 3000 cycles/yr (upper bound)", 1-(1900/2500)**(1/6000)),
 ("Hunter-Sellars 2026 TEA assumption", 5.1e-5),
 ("Climeworks/Svante Gen2 target: 10% per ~3000 cycles", 1-0.9**(1/3000)),
 ("TDA/GE 2026 measured: 11% over 5000 cycles", 1-0.89**(1/5000)),
 ("Climeworks/Svante Gen3 target: 5% per ~3000 cycles", 1-0.95**(1/3000)),
 ("Needed for 20% fade at 20,000 cycles", 1-0.8**(1/20000)),
 ("Needed for 20% fade at 100,000 cycles", 1-0.8**(1/100000)),
]
for name, k in rates:
    a = cost(fade_pct=k*100, price=20.0); b = cost(fade_pct=k*100, price=50.0); c0 = cost(fade_pct=0.0, price=0.0)
    print(f"  {name:72s} {k*100:8.2e} %/cycle -> ${a:5.0f}/t (@$20/kg), ${b:5.0f}/t (@$50/kg); degradation penalty vs ideal ${a-c0:4.0f} / ${b-c0:4.0f}")

print("\nTDA/GE: 2.2%/1000 cycles extrapolated to assumed 4-year sorbent life")
for cyc_min in (10, 44):
    n = 4*365*24*60/cyc_min
    print(f"  {cyc_min} min cycles: {n:8.0f} cycles in 4 yr -> capacity remaining {0.978**(n/1000)*100:5.1f}% (exponential), linear loss {2.2*n/1000:5.0f}%")
