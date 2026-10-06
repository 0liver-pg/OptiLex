import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math, dataclasses
import numpy as np
M = M_CO2; C = 273.15

def hdr(s): print("\n" + "="*8 + " " + s + " " + "="*8)

hdr("0. Reference cycle (verifier)")
ref = reference_amine_cycle()
print(f"wc {ref.working_capacity:.2f} mol/kg | heat {ref.heat_gj_per_t:.2f} GJ/t (rxn {gj_per_tonne(ref.reaction_heat):.2f} sens {gj_per_tonne(ref.sensible_heat):.2f} water {gj_per_tonne(ref.water_heat):.2f}) | work-eq {ref.work_equivalent_gj_per_t:.2f} | eff {ref.second_law_efficiency:.0%}")
for cyc in (2000, 5000, 20000, 100000):
    print(f"  $20/kg, wc {ref.working_capacity:.2f}: {cyc:>6} cycles -> ${sorbent_cost_per_tonne(20, ref.working_capacity, cyc):6.1f}/t")

hdr("1. Fade budget: per-cycle and per-hour loss rates that lifetimes imply")
for target in (2000, 5000, 20000, 100000):
    k = 1 - 0.8**(1/target)
    print(f"  20% fade at {target:>6} cycles -> {k*100:.2e} %/cycle ; per year at 30-min cycles (90% duty): {k*100*15768:.1f} %/yr")
print("  calendar (storage) losses expressed per 30-min cycle (15,768 cycles/yr at 90% duty):")
for name, loss, days in (("PEI/Al2O3 23 C ambient air, 12 months (Guta 2026): <13%", 0.13, 365),
                         ("PEI/Al2O3 40 C air or N2, 2 months (Guta 2026): 62-66%", 0.64, 61),
                         ("TEPA/SiO2 room air, 15 months (Vu 2019): 48%", 0.48, 456)):
    kd = -math.log(1-loss)/days
    print(f"   {name}: first-order {kd:.2e}/day -> {kd/48*100:.2e} %/30-min-cycle ({kd*365*100:.0f} %/yr if uninterrupted)")

hdr("2. Oxidation rate law for warm/hot air contact (piecewise, from measured points)")
# first-order k (1/h) from single-exposure data, unprotected PEI on alumina/silica, 21% O2, 0.04% CO2 where stated
pts = [(55, 0.02, 18, "Li 2024 dry 0.04%CO2-air 18 h"), (60, 0.15, 18, "Li 2024 dry 0.04%CO2-air 18 h"),
       (70, 0.17, 3, "Guta 2023 dry 0.04%CO2-air 3 h (initial)"), (70, 0.80, 168, "Guta 2023 dry 0.04%CO2-air 7 d (long-run)"),
       (80, 0.33, 24, "Thakkar 2024 PEI/SiO2 air 24 h"), (100, 0.86, 24, "Thakkar 2024 air 24 h"),
       (120, 0.92, 24, "Thakkar 2024 air 24 h"), (120, 0.35, 4.5, "Guta 2025 dry CO2-free air 4.5 h")]
ks = {}
for T, loss, h, src in pts:
    k = -math.log(1-loss)/h; ks.setdefault(T, []).append(k)
    print(f"  {T:>4} C: {loss*100:4.0f}% in {h:5.1f} h -> k = {k:.3e} /h = {k/3600:.2e} /s   [{src}]")
# a crude envelope: k_hot ~ 0.06-0.1 /h for T >= 70 C; k(60 C) ~ 9e-3; k(55 C) ~ 1.1e-3 ; below 50 C ~ calendar rates
def k_T(Tc):   # /h, upper-envelope interpolation on log scale
    xs = [23, 40, 55, 60, 70, 80, 100, 120]; ys = [-math.log(1-0.13)/(365*24), -math.log(1-0.64)/(61*24), 1.1e-3, 9.0e-3, 6.2e-2, 1.7e-2*4, 8.2e-2, 1.05e-1]
    return math.exp(np.interp(Tc, xs, np.log(ys)))
budget = (1 - 0.8**(1/20000))   # fraction per cycle
print(f"  per-cycle budget for 20,000 cycles = {budget:.2e} (fraction)")
print("  damage per cycle from AIR contact while hot (unprotected PEI rate law):")
for Tc, secs in ((100, 1), (100, 2), (100, 10), (80, 10), (70, 60), (60, 60), (60, 600), (55, 600), (55, 1800)):
    d = k_T(Tc)/3600*secs
    print(f"    {Tc:>3} C for {secs:>5} s: {d:.2e} per cycle = {d/budget:6.1f} x budget")
# cooling in air from 100 C to 25 C, exponential approach, time constant tau: damage = int k(T(t)) dt
for tau in (30, 60, 120, 300):
    t = np.linspace(0, 6*tau, 4000); T = 25 + 75*np.exp(-t/tau)
    d = np.trapezoid([k_T(x)/3600 for x in T], t)
    print(f"    air-cool 100->25 C with tau {tau:>3} s: {d:.2e} per cycle = {d/budget:6.1f} x budget (time above 57 C: {tau*math.log(75/32):.0f} s)")
print("  => with the unprotected rate law, every second of air contact above ~60 C costs ~1x the whole 20,000-cycle budget.")
print("  => measured engineered-sorbent fade (TDA 2.2e-5/cycle, Climeworks target 1.7-3.5e-5/cycle) corresponds to ~1-2 s hot-air-equivalent per cycle.")

hdr("3. Residual-oxygen inventory per cycle (what a scavenger or purge must handle)")
# laminate/packed bed: sorbent bulk density rho_b, void fraction eps -> void volume per kg sorbent
for rho_b, eps in ((300, 0.7), (500, 0.5)):
    Vv = eps/rho_b   # m3 void per kg sorbent
    print(f"  bed rho_b {rho_b} kg/m3, void {eps}: void volume {Vv*1e3:.2f} L/kg sorbent")
    for p_res in (20e3, 5e3, 1e3, 200):
        nO2 = 0.21*p_res*Vv/(R*373.15)
        print(f"    residual total pressure {p_res/1e3:5.1f} kPa (21% O2 if air not purged): {nO2*1e3:.3f} mmol O2/kg/cycle; "
              f"if 1 O2 destroys 1 site of 8 mol N/kg: {nO2/8*100:.1e} %/cycle = {nO2/8/budget:5.1f} x budget")
print("  => an un-purged bed evacuated to 5 kPa carries ~0.5-0.7 mmol O2/kg per cycle; a 20% chain conversion to dead sites would already use the whole budget.")
print("  DEHA dosing (2 mol DEHA per mol O2, 89 g/mol, $4/kg) to consume that O2, per tonne CO2 at wc 1.04 mol/kg:")
for nO2 in (0.74e-3, 0.15e-3, 0.03e-3):
    kg_per_t = 2*nO2*0.089/(1.04*M)*1000
    print(f"    {nO2*1e3:.2f} mmol O2/kg/cycle -> {kg_per_t:5.2f} kg DEHA per t CO2 = ${kg_per_t*4:5.2f}/t")
print("  sacrificial Fe zone (Fe -> Fe2O3, 0.75 O2 per Fe) sized for 20,000 cycles:")
for nO2 in (0.74e-3, 0.15e-3):
    print(f"    {nO2*1e3:.2f} mmol O2/kg/cycle x 20,000 = {nO2*20000:.1f} mol O2/kg -> {nO2*20000/0.75*0.0558:.2f} kg Fe per kg sorbent")

hdr("4. Trace-metal ingress budget (dust and steam)")
vol_per_t = air_volume_per_tonne(X_AIR, 0.75)  # m3 air per t CO2
m3_per_kg_cycle = vol_per_t*1.04*M/1000.0       # m3 air per kg sorbent per cycle at wc 1.04 mol/kg
print(f"  air processed: {vol_per_t:,.0f} m3/t CO2 -> {m3_per_kg_cycle:.1f} m3 per kg sorbent per cycle")
for metal, conc_ng, ppm_effect in (("Fe", (50, 200, 1000), 100), ("Cu", (2, 5, 20), 4)):
    for cng in conc_ng:
        per_cycle = cng*1e-9*m3_per_kg_cycle   # g per kg sorbent per cycle
        for cap in (0.1, 1.0):
            cycles_to = ppm_effect*1e-6/(per_cycle*cap)
            print(f"   {metal} {cng:>5} ng/m3, capture fraction {cap:>3}: {per_cycle*1e6:7.3f} ug/kg/cycle -> {ppm_effect} ppm after {cycles_to:9,.0f} cycles ({cycles_to/15768:5.2f} yr at 30-min cycles)")
print("  steam-borne metals, 2 mol H2O steam per mol CO2 (36 g steam per 1.04 mol CO2 per kg sorbent per cycle):")
for ppb in (1, 10, 50):
    g_per_cycle = 2*1.04*0.018*ppb*1e-9
    print(f"   {ppb:>3} ppb metal in steam, all deposited: {g_per_cycle*1e6:.3f} ug/kg/cycle -> 4 ppm (Cu threshold) after {4e-6/g_per_cycle:9,.0f} cycles; 20,000 cycles deposit {g_per_cycle*20000*1e6:.1f} ppm")
print("  chelator sizing: 1 wt% tethered iminodiacetate/phosphonate (~0.05 mol sites/kg) binds up to", f"{0.05*55.8:.1f} g Fe/kg = {0.05*55.8/1e-6/1e3:.0f} ppm-equivalent Fe -> >>  ingress; capacity penalty ~1% of mass")

hdr("5. Refurbishment (strip-and-reload) economics")
def cost_per_t(price, wc, cycles): return sorbent_cost_per_tonne(price, wc, cycles)
wc = 1.04
for support_price, support_life, amine_price, amine_frac, amine_life, refurb_cost in (
        (20, 20000, 4, 0.4, 3000, 2.0), (20, 20000, 4, 0.4, 5000, 2.0), (20, 60000, 4, 0.4, 5000, 2.0), (50, 20000, 4, 0.4, 5000, 3.0)):
    sup = cost_per_t(support_price, wc, support_life)
    am = cost_per_t(amine_price*amine_frac + refurb_cost, wc, amine_life)
    rep = cost_per_t(support_price, wc, amine_life)
    print(f"  support ${support_price}/kg life {support_life} cyc; amine ${amine_price}/kg x {amine_frac:.0%} + refurb ${refurb_cost}/kg every {amine_life} cyc: "
          f"support {sup:5.1f} + reload {am:5.1f} = ${sup+am:5.1f}/t  vs replace whole sorbent every {amine_life} cyc: ${rep:5.1f}/t")

hdr("6. Cool-down under CO2 blanket vs water flash (verifier Langmuir site -70 kJ/mol, dS -165)")
q_ads = loading(P_CO2_AIR, T0, -70e3, -165, 2.0)
print(f"  q_ads (25 C, 420 ppm) = {q_ads:.2f} mol/kg; reference q_des (100 C, 1 kPa) = {ref.q_des:.2f} -> wc {ref.working_capacity:.2f}")
for Tc in (55, 40):
    for p in (1000, 300, 100, 30):
        q = loading(p, C+Tc, -70e3, -165, 2.0)
        print(f"   cooled to {Tc} C under {p:>5} Pa CO2: loading {q:.2f} mol/kg -> working capacity left {max(0, q_ads-q):.2f} mol/kg ({max(0,q_ads-q)/ref.working_capacity:.0%} of reference)")
print("  water flash: heat to remove cooling 1 kg sorbent (+inert) from T_des to 55 C, as mol H2O evaporated (44 kJ/mol):")
for Tdes in (100, 90, 80):
    for inert in (0.0, 1.0, 3.0):
        Q = (1500 + inert*900)*(Tdes-55)
        print(f"   T_des {Tdes} C, inert {inert} kg/kg: {Q/1e3:5.0f} kJ/kg -> {Q/44000:.2f} mol H2O per kg = {Q/44000/wc:.2f} mol H2O per mol CO2 (sorbent holds ~3-4 mol/kg at 40-50% RH)")
print(f"  vapour pressure of water at 55 C ~15.7 kPa: flash only needs p_total < 15.7 kPa; isothermal pump work from 15.7 kPa to 1 atm = {R*328*math.log(P0/15.7e3)/0.7/1e3:.2f} kJ/mol gas")
print(f"  for comparison vacuum work in the reference cycle (1 kPa): {ref.vacuum_work/1e3:.1f} kJ/mol CO2")
# residual CO2 pressure during the flash: CO2 left in the bed re-adsorbs; at 55 C the bed is at steam partial pressure ~15 kPa, CO2 partial pressure set by pump-down
print("  => blanket must be water vapour or O2-free gas, not CO2: >=300 Pa CO2 during cool-down to 55 C wipes out the working capacity.")

hdr("7. Hindered-amine (TMP) sorbent window: capacity ceiling and binding needed")
for N_mmol in (2.0, 3.0, 4.0):
    print(f"  {N_mmol} mmol N/g grafted: carbamate ceiling (0.5/N) {N_mmol*0.5:.1f} mmol/g; bicarbonate 1:1 ceiling {N_mmol:.1f} mmol/g")
for dS in (-165, -140, -120):
    for dH in (-55e3, -60e3, -65e3, -70e3):
        th = loading(P_CO2_AIR, T0, dH, dS, 1.0); Td = desorption_temperature(dH, dS, 1e3) - C
        print(f"   dS {dS}: dH {dH/1e3:.0f} -> fill at 420 ppm {th:5.1%}, unload to 20% at 1 kPa needs {Td:5.0f} C")
print("  TAD grafted via glycidyl silane (~0.3 kg amine per kg): if 1:1 bicarbonate at 60% site use on 3 mmol N/g -> 1.8 mmol/g; test threshold set at >=0.8 mmol/g humid")

hdr("8. Stabiliser package capacity penalty and cost")
for molpct in (1, 2, 4):
    # additive per amine N: at 8 mol N/kg, molpct% of N replaced by stabiliser groups of ~300 g/mol
    n_add = 8*molpct/100; mass_add = n_add*0.3
    print(f"  {molpct} mol% additive on 8 mol N/kg: {n_add:.2f} mol/kg = {mass_add*100:.0f} wt% added mass -> capacity per kg down ~{mass_add/(1+mass_add):.0%} + lost N {molpct}% ; additive cost at $15/kg: ${mass_add*15:.2f}/kg sorbent (+{mass_add*15/20:.0%} on a $20/kg sorbent)")
# value of durability (reuse tornado model logic)
def mean_cap(n, k): return 1.0 if k <= 0 else (1-(1-k)**n)/(n*k)
def cost(price=20.0, fade_pct=5e-3, cap_charge=274.0, frac=0.6, heat_usd_gj=5.6, elec_usd_mwh=50.0, wc=1.04, cycle_min=30.0, q_pen=0.0):
    k = fade_pct/100.0; wc_eff = wc*(1-q_pen)
    heat = ref.heat_gj_per_t*heat_usd_gj; elec = energy_cost_floor(gj_per_tonne(ref.vacuum_work)+fan_work_gj_per_tonne(X_AIR,0.75,100.0), elec_usd_mwh)
    best = None
    for n in np.logspace(2, 6.3, 2000):
        mc = mean_cap(n, k); prod = (wc_eff/1.04)*mc
        cap = cap_charge*((1-frac)+frac/prod); sorb = price/(wc_eff*mc*n*M)*1000.0
        tot = cap+heat+elec+sorb
        if best is None or tot < best[0]: best = (tot, cap, heat, elec, sorb, n)
    return best
print("  levelized $/t (model of deg_tornado.py): base fade 5e-3 %/cycle, $20/kg")
b = cost(); print(f"   base: ${b[0]:.0f}/t (cap {b[1]:.0f} heat {b[2]:.0f} elec {b[3]:.0f} sorbent {b[4]:.0f}; replace at {b[5]:.0f} cycles)")
for name, kw in (("fade 5e-3 -> 1e-3, 5% capacity penalty, +$2/kg (stabiliser package)", dict(fade_pct=1e-3, q_pen=0.05, price=22.0)),
                 ("fade 5e-3 -> 2e-4, 10% capacity penalty, +$4/kg", dict(fade_pct=2e-4, q_pen=0.10, price=24.0)),
                 ("fade 5e-3 -> 1e-3, no penalty (process fix: O2-free cool-down)", dict(fade_pct=1e-3)),
                 ("fade 5e-3 -> 1e-3, +$12/t DEHA consumable", dict(fade_pct=1e-3)),
                 ("fade unchanged 5e-3 but sorbent price $20 -> $3.6/kg (refurbish: amine+labour only)", dict(price=3.6)),
                 ("fade 2.2e-3 (TDA measured), $20/kg", dict(fade_pct=2.2e-3)),
                 ("fade 2.2e-3, hot-climate calendar loss added (+7e-3 %/cycle)", dict(fade_pct=9.2e-3))):
    v = cost(**kw); extra = 12.0 if "DEHA" in name else 0.0
    print(f"   {name:75s} ${v[0]+extra:5.0f}/t ({v[0]+extra-b[0]:+5.0f}); sorbent term {v[4]:5.0f}, replace at {v[5]:7.0f} cycles")
