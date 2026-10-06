import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import math, dataclasses
import numpy as np
M = M_CO2
def hdr(s): print("\n" + "=" * 6 + " " + s + " " + "=" * 6)

# ---------------------------------------------------------------- shared models
REF = reference_amine_cycle()

def cycle(q_scale=1.0, cp=1500.0, inert=0.0, cp_inert=900.0, water=2.0, dH=-70e3, dS=-165.0, T_des=373.15):
    return dataclasses.replace(REF, q_max=2.0 * q_scale, cp_sorbent=cp, inert_mass_ratio=inert,
                               cp_inert=cp_inert, water_coads=water, dH=dH, dS=dS, T_des=T_des)

def mean_cap_exp(n, k):
    return 1.0 if k <= 0 else (1 - (1 - k) ** n) / (n * k)

def lcod(wc, heat_gj, price=20.0, fade_pct=5e-3, cycle_min=30.0, cap_charge=274.0, frac_scaling=0.6,
         heat_usd_gj=5.6, elec_usd_mwh=50.0, extra_usd_t=0.0, extra_fan_pa=0.0, avail=1.0, mean_cap_fn=None,
         n_grid=None, sorb_cost_fn=None):
    """Levelized $/t: capital (60% scales with productivity incl. fade and availability), heat, electricity
    (vacuum + 100 Pa fan + extra pressure drop), sorbent replacement, plus consumables. Replacement interval optimised."""
    prod0 = (wc / REF.working_capacity) * (30.0 / cycle_min) * avail
    k = fade_pct / 100.0
    elec_gj = gj_per_tonne(REF.vacuum_work) + fan_work_gj_per_tonne(X_AIR, 0.75, 100.0 + extra_fan_pa)
    heat = heat_gj * heat_usd_gj
    elec = energy_cost_floor(elec_gj, elec_usd_mwh)
    best = None
    for n in (n_grid if n_grid is not None else np.logspace(2.5, 6.5, 2500)):
        mc = mean_cap_fn(n) if mean_cap_fn else mean_cap_exp(n, k)
        cap = cap_charge * ((1 - frac_scaling) + frac_scaling / (prod0 * mc))
        sorb = sorb_cost_fn(n, mc) if sorb_cost_fn else price / (wc * mc * n * M) * 1000.0
        tot = cap + heat + elec + sorb + extra_usd_t
        if best is None or tot < best["tot"]:
            best = dict(tot=tot, cap=cap, heat=heat, elec=elec, sorb=sorb, n=n, mc=mc)
    return best

def show(label, b, base=None):
    d = f" ({b['tot'] - base:+6.1f})" if base is not None else ""
    print(f"  {label:58s} ${b['tot']:6.1f}/t{d} | cap {b['cap']:5.1f} heat {b['heat']:4.1f} elec {b['elec']:4.1f} "
          f"sorbent {b['sorb']:5.1f} | replace at {b['n']:8.0f} cyc, mean cap {b['mc']:.2f}")

hdr("0. Verifier reference")
print(f"  ref wc {REF.working_capacity:.3f} mol/kg, heat {REF.heat_gj_per_t:.2f} GJ/t, work-eq {REF.work_equivalent_gj_per_t:.2f}, eff {REF.second_law_efficiency:.0%}")
for c in (2000, 5000, 20000):
    print(f"  $20/kg, {c} cycles: ${sorbent_cost_per_tonne(20, REF.working_capacity, c):.0f}/t")
budget = lambda N, loss=0.2: (1 - (1 - loss) ** (1 / N)) * 100
print(f"  fade budget %/cycle: 20% at 20k = {budget(20000):.2e}; at 100k = {budget(100000):.2e}")
BASE = lcod(REF.working_capacity, REF.heat_gj_per_t)
show("BASE: ref cycle, $20/kg, fade 5e-3 %/cycle, 30-min", BASE)
for f in (2.2e-3, 1.1e-3, 5e-4, 2e-4, 0.0):
    show(f"  same, fade {f:.1e} %/cycle", lcod(REF.working_capacity, REF.heat_gj_per_t, fade_pct=f), BASE["tot"])
N_PER_KG = 0.45 / 0.04307   # mol N per kg sorbent at 45 wt% PEI (repeat unit C2H5N, 43.07 g/mol)
print(f"  45 wt% PEI sorbent: {N_PER_KG:.2f} mol N/kg")

# ================================================================= IDEA 1: nanoceria
hdr("1. Nanoceria catalytic HO2*/H2O2 scavenger (3 wt% CeO2 in PEI/oxide)")
for wt in (0.01, 0.03, 0.05):
    cyc = cycle(q_scale=1 - wt, cp=(1 - wt) * 1500 + wt * 460)
    print(f"  {wt*100:.0f} wt% CeO2: wc {cyc.working_capacity:.3f} mol/kg, heat {cyc.heat_gj_per_t:.2f} GJ/t (ref {REF.heat_gj_per_t:.2f}), "
          f"work-eq {cyc.work_equivalent_gj_per_t:.2f} GJ/t")
# turnover requirement: radicals to intercept over life vs surface Ce sites
for d_nm in (3, 5, 10):
    wt = 0.03; n_ce = wt / 0.17212                      # mol Ce per kg sorbent
    surf_frac = min(1.0, 6 * 0.38 / d_nm * 0.35)          # crude: shell of ~0.38 nm (one CeO2 layer) on a sphere
    s = n_ce * surf_frac
    for k_site in (5e-3, 2.2e-3):
        lost = k_site / 100 * N_PER_KG                    # mol N lost per kg per cycle at current fade
        for nu in (1, 5):
            rad = lost / nu                                 # chain-initiating radicals to intercept per cycle
            print(f"   d {d_nm:2d} nm: surface Ce {s*1e3:5.1f} mmol/kg; fade {k_site:.1e}%/cyc, chain length {nu}: "
                  f"{rad*1e6:6.1f} umol radicals/kg/cycle -> stoichiometric capacity lasts {s/rad:7.0f} cycles; "
                  f"20,000 cycles need {rad*20000/s:6.0f} turnovers per surface Ce")
cyc1 = cycle(q_scale=0.97, cp=0.97 * 1500 + 0.03 * 460)
for fold in (1, 2, 5, 10):
    b = lcod(cyc1.working_capacity, cyc1.heat_gj_per_t, price=20.6, fade_pct=5e-3 / fold)
    show(f"3 wt% CeO2 (+$0.6/kg), fade 5e-3/{fold}", b, BASE["tot"])
for fold in (2, 5, 10):
    b = lcod(cyc1.working_capacity, cyc1.heat_gj_per_t, price=50.6, fade_pct=5e-3 / fold)
    b0 = lcod(REF.working_capacity, REF.heat_gj_per_t, price=50.0)
    show(f"  ($50/kg sorbent) fade 5e-3/{fold}", b, b0["tot"])

# ================================================================= IDEA 2: reductive reclaiming
hdr("2. In-place reductive reclaiming (NaBH4 reduces imines; base frees heat-stable salts)")
k0 = 5e-5
def repair_direct(r, c_rep, N_rep, down_days=1.0, price=20.0, k=k0, cycle_min=30.0, cap_charge=274.0, frac=0.6):
    """Damage splits into reversible (reset by each repair) and irreversible parts. Optimise number of repair blocks."""
    k_rev, k_irr = r * k, (1 - r) * k
    wc = REF.working_capacity
    heat = REF.heat_gj_per_t * 5.6
    elec = energy_cost_floor(gj_per_tonne(REF.vacuum_work) + fan_work_gj_per_tonne(X_AIR, 0.75, 100.0), 50.0)
    best = None
    for nb in range(1, 400):
        n = nb * N_rep
        mc = mean_cap_exp(N_rep, k_rev) * mean_cap_exp(n, k_irr) if r > 0 else mean_cap_exp(n, k)
        run_days = n * cycle_min / 1440
        avail = run_days / (run_days + (nb - 1) * down_days)
        cap = cap_charge * ((1 - frac) + frac / (mc * avail))
        co2_t = wc * mc * n * M / 1000
        sorb = (price + c_rep * (nb - 1)) / co2_t
        tot = cap + heat + elec + sorb
        if best is None or tot < best["tot"]:
            best = dict(tot=tot, cap=cap, heat=heat, elec=elec, sorb=sorb, n=n, mc=mc, nb=nb)
    return best
def repair_case(r, c_rep, N_rep, down_days=1.0, price=20.0):
    return repair_direct(r, c_rep, N_rep, down_days=down_days, price=price)
print("  NaBH4 need: imine sites per 10% capacity loss ~0.1-0.3 mol/kg; at 3x excess, 0.1-0.25 mol NaBH4/kg = "
      f"{0.1*37.83:.1f}-{0.25*37.83:.1f} g/kg; at $30/kg = ${0.1*37.83*0.03:.2f}-{0.25*37.83*0.03:.2f}/kg per repair")
for r in (0.0, 0.25, 0.5, 0.75):
    best = None
    for N_rep in (1000, 2000, 3000, 5000, 8000, 12000):
        b = repair_case(r, 1.0, N_rep)
        if best is None or b["tot"] < best[0]["tot"]:
            best = (b, N_rep)
    b, N_rep = best
    show(f"reversible fraction {r:.2f}, $1/kg/repair, 1 day down, repair every {N_rep}", b, BASE["tot"])
for r, c in ((0.5, 3.0), (0.5, 0.3)):
    best = min((repair_case(r, c, N), N) for N in (2000, 3000, 5000, 8000) if True) if False else None
    bs = [(repair_case(r, c, N), N) for N in (2000, 3000, 5000, 8000, 12000)]
    b, N = min(bs, key=lambda x: x[0]["tot"])
    show(f"reversible 0.50, ${c}/kg/repair, repair every {N}", b, BASE["tot"])
bs = [(repair_case(0.5, 1.0, N, price=50.0), N) for N in (2000, 3000, 5000, 8000, 12000)]
b, N = min(bs, key=lambda x: x[0]["tot"]); b0 = lcod(REF.working_capacity, REF.heat_gj_per_t, price=50.0)
show(f"  ($50/kg sorbent) reversible 0.50, $1/kg, every {N}", b, b0["tot"])
# drying energy after an aqueous wash
for N_rep in (3000, 5000):
    co2_kg = REF.working_capacity * M * N_rep
    print(f"  drying 1 kg water/kg sorbent after wash every {N_rep} cycles: {2.44/co2_kg:.4f} GJ/t CO2 (negligible)")

# ================================================================= IDEA 3: deuterium isotope reinforcement
hdr("3. Site-specific isotope reinforcement (alpha C-D) of the amine")
d2o_min = 2 * 20.03 / 43.07
print(f"  min D2O for full alpha-C deuteration of PEI: {d2o_min:.2f} kg D2O per kg PEI (4 C-H per C2H5N unit); D mass fraction {4*1.006/(43.07+4*1.006):.1%}")
print("  kinetic picture: rate ~ kp(effective) if propagation (alpha-H abstraction by HO2*/ROO*) is rate-limiting;")
print("  linear mixing for partial deuteration x: kp_eff/kp_H = (1-x) + x/KIE")
for KIE in (3, 6, 12.8):
    print("   KIE", KIE, ":", ", ".join(f"x={x:.1f}: {((1-x)+x/KIE):.2f}" for x in (0.2, 0.5, 0.9, 0.98)))
classes = [("PEI/silica laminate", 20.0, 0.40, 1.0), ("COF/MOF-tethered amine", 100.0, 0.30, 1.25),
           ("COF/MOF-tethered amine", 200.0, 0.30, 1.25)]
for name, price, amine_frac, qs in classes:
    cyc = cycle(q_scale=qs)
    b0 = lcod(cyc.working_capacity, cyc.heat_gj_per_t, price=price)
    print(f"  {name} ${price:.0f}/kg (amine {amine_frac:.0%}, wc {cyc.working_capacity:.2f}): base ${b0['tot']:.0f}/t (sorbent ${b0['sorb']:.0f})")
    for d2o_price, use in ((300, 1.2), (600, 1.5), (1000, 2.0)):
        prem = amine_frac * d2o_min * use * d2o_price
        row = []
        for x in (0.98,):
            for KIE in (1.5, 3, 6, 12.8):
                fade = 5e-3 * ((1 - x) + x / KIE)
                b = lcod(cyc.working_capacity, cyc.heat_gj_per_t, price=price + prem, fade_pct=fade)
                row.append(f"KIE {KIE}: {b['tot']-b0['tot']:+6.0f}")
        print(f"    D2O ${d2o_price}/kg x{use} use -> premium ${prem:6.0f}/kg sorbent | " + " | ".join(row))
# scale: D2O demand
for gt in (0.001, 0.1, 1.0):
    life_t_per_kg = REF.working_capacity * M * 20000 / 1000   # t CO2 per kg sorbent over 20k cycles
    sorb_kg = gt * 1e9 / life_t_per_kg
    d2o = sorb_kg * 0.40 * d2o_min * 1.5
    print(f"  {gt*1000:6.0f} Mt/yr DAC at 20k-cycle life: sorbent {sorb_kg/1e6:8.2f} kt/yr -> D2O {d2o/1e6:8.2f} kt/yr (fully deuterated PEI, 40 wt%)")

# ================================================================= IDEA 4: metal deactivator
hdr("4. Polymer-bound salicylaldimine (DMD-type) / tolyltriazole Cu deactivator")
V = air_volume_per_tonne(X_AIR, 0.75)
air_per_kg_cycle = V * (REF.working_capacity * M / 1000)      # m3 air per kg sorbent per cycle
print(f"  air processed: {V:,.0f} m3/t -> {air_per_kg_cycle:.1f} m3 per kg sorbent per cycle")
for cu_ng in (2, 5, 20):
    for cf in (0.01, 0.1, 1.0):
        dep = cu_ng * air_per_kg_cycle * cf * 1e-9 * 1e3   # mg per kg per cycle -> ppm (mg/kg)
        n4 = 4 / dep
        print(f"   Cu {cu_ng:2d} ng/m3, retained fraction {cf:4.2f}: {dep*1e3:7.3f} ug/kg/cycle -> 4 ppm after {n4:9,.0f} cycles "
              f"({n4/17520:6.2f} yr at 30-min); 20,000 cycles -> {dep*20000:7.1f} ppm")
for fe_ng, sol in ((200, 0.01), (1000, 0.01), (1000, 0.05)):
    dep = fe_ng * air_per_kg_cycle * sol * 1e-9 * 1e3
    print(f"   Fe {fe_ng} ng/m3 x soluble/available fraction {sol} (all particles retained): {dep*20000:6.1f} ppm available Fe over 20,000 cycles")
for ppb, steam_mult in ((2, 1), (10, 1), (10, 5), (50, 5)):
    steam_g = 2 * 18.015 * REF.working_capacity * steam_mult      # g steam contacting 1 kg sorbent per cycle
    dep = ppb * 1e-9 * steam_g * 1e-3 * 1e6                       # mg per kg per cycle
    print(f"   steam {ppb:2d} ppb Cu, {steam_mult}x the co-desorbed water ({steam_g:.0f} g/kg/cycle), all deposited: {dep*20000:6.1f} ppm over 20,000 cycles")
# Kuspangaliyeva 2026 retention -> relative first-order rate
ctrl = -math.log(0.72)
for lab, ret in (("4 ppm Cu (10,000:1)", 0.63), ("~40 ppm Cu/Fe (1000:1), 50% kept", 0.50), ("~40 ppm, 25% kept", 0.25)):
    print(f"   {lab}: rate multiplier vs metal-free control = {-math.log(ret)/ctrl:.2f} (120 C, 4.5 h, dry air)")
lig_frac = 0.005
sites = lig_frac * N_PER_KG
print(f"  0.5 mol% of N as salicylaldimine: {sites*1e3:.1f} mmol/kg ligand -> {sites/2*1e3:.1f} mmol Cu/kg as Cu(L)2 = {sites/2*63.55*1e3:.0f} ppm Cu capacity; "
      f"salicylaldehyde {sites*122.12:.1f} g/kg (${sites*0.12212*5:.3f}/kg at $5/kg)")
cyc4 = cycle(q_scale=1 - lig_frac * 1.5)
for kint, mult in ((2.2e-3, 1.0), (2.2e-3, 1.4), (2.2e-3, 2.1), (2.2e-3, 4.2)):
    b_with_metal = lcod(REF.working_capacity, REF.heat_gj_per_t, fade_pct=kint * mult)
    b_deact = lcod(cyc4.working_capacity, cyc4.heat_gj_per_t, price=20.02, fade_pct=kint)
    print(f"   intrinsic fade {kint:.1e}, metal multiplier {mult}: no deactivator ${b_with_metal['tot']:.0f}/t -> with deactivator "
          f"${b_deact['tot']:.0f}/t (saves ${b_with_metal['tot']-b_deact['tot']:.0f}/t)")

# ================================================================= IDEA 5: graded, skimmable inlet cartridge
hdr("5. Graded bed with replaceable sacrificial inlet cartridge (refinery top-bed skimming)")
def graded(g, share, price_s=20.0, price_b=20.0, k_avg=5e-5):
    a = share / g; bfac = (1 - share) / (1 - g)
    ks, kb = a * k_avg, bfac * k_avg
    wc = REF.working_capacity
    heat = REF.heat_gj_per_t * 5.6
    elec = energy_cost_floor(gj_per_tonne(REF.vacuum_work) + fan_work_gj_per_tonne(X_AIR, 0.75, 100.0), 50.0)
    best = None
    for Ns in np.logspace(2.5, 6, 140):
        for Nb in np.logspace(2.5, 6, 140):
            mean = g * mean_cap_exp(Ns, ks) + (1 - g) * mean_cap_exp(Nb, kb)
            sorb = (g * price_s / Ns + (1 - g) * price_b / Nb) / (wc * mean * M) * 1000.0
            cap = 274.0 * (0.4 + 0.6 / mean)
            tot = cap + heat + elec + sorb
            if best is None or tot < best["tot"]:
                best = dict(tot=tot, cap=cap, heat=heat, elec=elec, sorb=sorb, n=Nb, mc=mean, Ns=Ns,
                            fs=1 - (1 - ks) ** Ns, fb=1 - (1 - kb) ** Nb)
    return best
whole = lcod(REF.working_capacity, REF.heat_gj_per_t, fade_pct=5e-3)
show("whole-bed replacement (optimised), fade 5e-3 avg", whole)
for g, share in ((0.2, 0.2), (0.2, 0.5), (0.15, 0.7), (0.1, 0.8)):
    for ps in (20.0, 8.0):
        b = graded(g, share, price_s=ps)
        print(f"  g={g:.2f} holds {share:.0%} of damage, slice ${ps:.0f}/kg: ${b['tot']:.1f}/t ({b['tot']-whole['tot']:+.1f}) | sorbent {b['sorb']:.1f} cap {b['cap']:.1f} | "
              f"slice replaced every {b['Ns']:,.0f} cyc at {b['fs']:.0%} loss, bulk every {b['n']:,.0f} cyc at {b['fb']:.0%} loss, mean cap {b['mc']:.2f}")
for pa in (20, 50, 100):
    print(f"  guard/pre-filter extra {pa} Pa: fan {fan_work_gj_per_tonne(X_AIR, 0.75, pa):.3f} GJ/t = ${energy_cost_floor(fan_work_gj_per_tonne(X_AIR, 0.75, pa), 50):.2f}/t at $50/MWh")

# ================================================================= IDEA 6: steam-carried antioxidant top-up
hdr("6. In-service antioxidant top-up via regeneration steam (diphenylamine-class radical trap)")
dH_vap, Tb = 62e3, 575.15   # DPA: bp 302 C; dHvap ~62 kJ/mol (estimate, not verified)
pv = lambda T: 101.325e3 * math.exp(-dH_vap / R * (1 / T - 1 / Tb))
print(f"  DPA vapour pressure (Clausius-Clapeyron from bp, dHvap 62 kJ/mol assumed): 100 C {pv(373.15):.0f} Pa, 30 C {pv(303.15):.2f} Pa, 25 C {pv(298.15):.2f} Pa")
print(f"  -> saturation mole fraction in 1 atm steam at 100 C {pv(373.15)/101325:.1e}; residual in product CO2 at 30 C condenser ~{pv(303.15)/1e5*1e6:.0f} ppmv")
for kfade in (5e-3, 2.2e-3):
    lost = kfade / 100 * N_PER_KG               # mol N sites lost per kg per cycle if unprotected
    for nu in (1, 3, 10):
        n_stoich = 2.0
        dose = lost / nu / n_stoich              # mol trap per kg per cycle
        per_t = dose / REF.working_capacity / M * 1000   # mol per t CO2 (1 t = 1000/M mol... careful)
        per_t = dose / (REF.working_capacity * M / 1000)  # mol trap per t CO2
        kg_t = per_t * 0.16922
        steam_x = dose / 4.0                     # mole fraction if carried by ~4 mol steam per kg per cycle
        print(f"   fade {kfade:.1e}, chain length {nu:2d}: {dose*1e6:6.1f} umol DPA/kg/cycle = {kg_t:5.2f} kg DPA/t CO2 "
              f"(${kg_t*4:5.2f}/t at $4/kg); needed steam mole fraction {steam_x:.1e}")
for fade_after, cons in ((1e-3, 1.5), (1e-3, 3.0), (2e-3, 1.5)):
    cyc6 = cycle(q_scale=0.98)
    b = lcod(cyc6.working_capacity, cyc6.heat_gj_per_t, price=20.4, fade_pct=fade_after, extra_usd_t=cons)
    show(f"2 mol% DPA initial (+$0.4/kg), fade -> {fade_after:.0e}, top-up ${cons}/t", b, BASE["tot"])

hdr("3b. Semiclassical primary KIE bound for alpha C-H vs C-D abstraction (stretch ZPE lost at TS)")
h, c, kB, NA = 6.62607e-34, 2.99792e10, 1.380649e-23, 6.02214e23
nu_H = 2900.0; nu_D = nu_H / math.sqrt((12 * 2.014 / 14.014) / (12 * 1.008 / 13.008))
dzpe = 0.5 * h * c * (nu_H - nu_D) * NA      # J/mol
print(f"  C-H {nu_H:.0f} cm-1, C-D {nu_D:.0f} cm-1, dZPE {dzpe/1e3:.2f} kJ/mol")
for Tc in (25, 60, 70, 100):
    T = Tc + 273.15
    print(f"   {Tc:3d} C: semiclassical KIE ~ {math.exp(dzpe/(R*T)):.1f} (tunnelling can exceed this; D-PUFA propagation KIE measured 12.8 at 37 C)")
print("  verifier check: alpha-D leaves CO2 binding unchanged (secondary EIE << 1 kJ/mol); working capacity stays", f"{REF.working_capacity:.2f} mol/kg")

hdr("Summary of verifier energy numbers for the six ideas")
rows = [("ref", cycle()), ("1 ceria 3 wt%", cycle(q_scale=0.97, cp=0.97*1500+0.03*460)),
        ("4 ligand 0.5 mol% N", cycle(q_scale=1-0.0075)), ("6 DPA 2 wt%", cycle(q_scale=0.98, cp=1500))]
for name, cy in rows:
    print(f"  {name:22s} wc {cy.working_capacity:.3f} mol/kg | heat {cy.heat_gj_per_t:.2f} GJ/t | work-eq {cy.work_equivalent_gj_per_t:.2f} GJ/t | eff {cy.second_law_efficiency:.1%}")
print(f"  5 guard layer +30 Pa: +{fan_work_gj_per_tonne(X_AIR, 0.75, 30):.3f} GJ/t electricity")
