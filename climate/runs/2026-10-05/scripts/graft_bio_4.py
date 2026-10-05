"""Verifier for graft_bio_4: in-place wash-out and re-impregnation of oxidised amine on
solid-sorbent DAC supports (PSII D1-repair analogy).

Checks: thermodynamic floor (air capture), reload energy, sorbent cost per tonne with and
without reload, full DAC cost per tonne (low/base/high), material flows, scale and resource
share. All assumptions are labelled. Values marked [mem] are literature values recalled
from memory and NOT re-verified in this run (web-search budget exhausted); [idea] are
the idea's own inputs; [verifier] come from climate/physics.py; [assume] are judgement.
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

M = 0.04401  # kg/mol CO2

print("=" * 78)
print("1. THERMODYNAMIC FLOOR (separation is from air; reload itself is not a separation)")
w = min_separation_work(420e-6, 0.75, 0.99)
floor = gj_per_tonne(w)
print(f"  Air 420 ppm, 75% capture, 99% purity: {w/1e3:.2f} kJ/mol = {floor:.3f} GJ/t "
      f"= {floor/0.0036:.0f} kWh/t   [verifier]")
for real in (5.0, 7.0, 10.0):
    print(f"  Real solid-sorbent DAC {real:>4.1f} GJ/t -> second-law eff "
          f"{second_law_efficiency(real, floor)*100:.1f}%")
print("  Real solid-sorbent DAC energy 5-10+ GJ/t: [mem] McQueen et al. 2021 review range "
      "~5.4-11.9 GJ/t (modelled + pilot), heat-dominated at 80-100 C.")

print("=" * 78)
print("2. SORBENT LIFETIME PRODUCTIVITY (reproduces idea claim 1 inputs)")
def kg_co2_per_kg_sorbent(cap_mol_kg, cycles_day, years, cf=1.0):
    return cap_mol_kg * M * cycles_day * 365 * years * cf

cases = {
    #           cap mol/kg, cycles/d, life yr, $/kg structured sorbent
    "pessimistic": (1.0, 3, 1.0, 50.0),
    "base":        (1.25, 4, 1.5, 35.0),
    "optimistic":  (1.5, 6, 2.0, 20.0),
}
prod = {}
for k, (c, n, y, p) in cases.items():
    q = kg_co2_per_kg_sorbent(c, n, y)
    prod[k] = q
    cyc = n * 365 * y
    print(f"  {k:<12} cap {c} mol/kg, {n} cyc/d, {y} yr ({cyc:.0f} cycles) -> "
          f"{q:6.1f} kg CO2/kg sorbent; replacement ${p/q*1000:7.0f}/t CO2 at ${p}/kg")
lo_q = kg_co2_per_kg_sorbent(1.0, 3, 1.0); hi_q = kg_co2_per_kg_sorbent(1.5, 6, 2.0)
print(f"  Idea's extremes: {lo_q:.0f}-{hi_q:.0f} kg/kg; $20/kg at best = ${20/hi_q*1000:.0f}/t, "
      f"$50/kg at worst = ${50/lo_q*1000:.0f}/t  (idea claims $69-1,038/t: CHECK)")
print("  Note: 1e4 cycles at 3-6 cyc/d = "
      f"{1e4/6/365:.1f}-{1e4/3/365:.1f} yr; 1e5 cycles = {1e5/6/365:.0f}-{1e5/3/365:.0f} yr. "
      "The idea's 1-2 yr life = 1,095-4,380 cycles, i.e. below the TEA target.")
print("  Working capacity at 400 ppm of PEI/silica in humid TVSA: [mem] ~0.5-1.5 mol/kg "
      "(lab); 1.0-1.5 is optimistic-to-mid for field laminates.")

print("=" * 78)
print("3. RELOAD ECONOMICS (support reused N times; amine + process cost per reload)")
# per-life cost as fraction of new sorbent price:
#   f = a*(1+o_amine) + (1-a)/N + proc
# a = amine share of sorbent cost [idea 0.2-0.3]; N = support reuses [idea 5-10];
# proc = reload process cost as fraction of sorbent price (solvent loss, labour,
#        downtime, waste disposal) [idea 10-15%, applied here to the sorbent price].
def reload_fraction(a, N, proc):
    return a + (1 - a) / N + proc

scen = {
    "idea-optimistic": (0.20, 10, 0.10),
    "idea-pessimistic": (0.30, 5, 0.15),
    "stress: amine-dominated cost": (0.50, 5, 0.15),
    "stress: support degrades (N=2)": (0.30, 2, 0.15),
    "stress: amine 70%, N=3": (0.70, 3, 0.20),
}
for k, (a, N, proc) in scen.items():
    f = reload_fraction(a, N, proc)
    print(f"  {k:<32} a={a:.2f} N={N:<2} proc={proc:.2f} -> reload costs {f*100:5.1f}% "
          f"of new sorbent (saving {100*(1-f):5.1f}%)")
print("  Idea claims 46-54% saving. Under its own inputs the formula above gives "
      f"{100*(1-reload_fraction(0.30,5,0.15)):.0f}-{100*(1-reload_fraction(0.20,10,0.10)):.0f}% "
      "(i.e. the idea's range is conservative relative to its inputs, not inflated).")
print("  The structural risk: amine share 'a'. Bulk branched PEI [mem] ~$3-10/kg; amine at")
print("  40 wt% of sorbent -> $1.2-4/kg sorbent, i.e. 2.4-20% of a $20-50/kg structured")
print("  sorbent. So a=0.2-0.3 is plausible IF the expensive part is the structure. If")
print("  instead the support is cheap precipitated silica [mem ~$1-3/kg] in a cheap")
print("  laminate, 'a' is high and the saving collapses (see stress rows).")

# $/t sorbent component with and without reload
print("  Sorbent cost $/t CO2 (no reload -> with reload):")
for k in cases:
    c, n, y, p = cases[k]
    base_cost = p / prod[k] * 1000
    for lab, (a, N, proc) in (("idea-opt", scen["idea-optimistic"]),
                               ("idea-pess", scen["idea-pessimistic"])):
        print(f"    {k:<12} {lab:<9}: ${base_cost:7.0f} -> ${base_cost*reload_fraction(a,N,proc):7.0f}"
              f"  (saves ${base_cost*(1-reload_fraction(a,N,proc)):6.0f}/t)")

print("=" * 78)
print("4. RELOAD ENERGY (solvent evaporation/recovery)")
L_MEOH = 1.10   # MJ/kg latent heat methanol at bp [handbook ~1.1 MJ/kg]
L_H2O = 2.26    # MJ/kg water
for solvent, L in (("methanol", L_MEOH), ("water", L_H2O)):
    for kg_solv in (2.0, 4.0):   # 2 = wash only [idea]; 4 = wash + impregnation solution [assume]
        for k in ("pessimistic", "optimistic"):
            e_mj_per_kg_sorb = kg_solv * L * 1.3   # +30% sensible heat / recovery losses [assume]
            gj_t = e_mj_per_kg_sorb / prod[k]      # MJ/kg sorbent / (t CO2 / kg... ) see below
            # prod in kg CO2/kg sorbent -> MJ per kg CO2 = e/prod; GJ/t = MJ/kg
            gj_t = e_mj_per_kg_sorb / prod[k]
            print(f"  {solvent:<8} {kg_solv:.0f} kg/kg sorbent, {k:<11}: {gj_t:.3f} GJ/t CO2 "
                  f"= {gj_t/7.0*100:.2f}% of 7 GJ/t DAC, {gj_t/floor*100:.1f}% of floor")
print("  Idea claim 0.008-0.046 GJ/t (methanol, 2 kg/kg, latent only): consistent; even")
print("  water wash + re-impregnation stays <~0.25 GJ/t. Energy is NOT the binding issue.")

print("=" * 78)
print("5. FULL SOLID-SORBENT DAC COST $/t CO2 (gross captured), WITH vs WITHOUT reload")
def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)
# capex per (t/yr) capacity: [mem] FOAK solid DAC ~$1,500-3,000+/(t/yr); NOAK targets ~$500.
# heat GJ/t [mem McQueen]; elec GJ/t [mem]; prices [assume, 2026 indicative].
full = {
    "low":  dict(capex=500,  r=0.06, n=25, om=0.03, heat=4.0, elec=1.0, p_heat=4.0,
                 p_el=40, sorb_case="optimistic", rl=scen["idea-optimistic"], ts=10),
    "base": dict(capex=1500, r=0.08, n=20, om=0.04, heat=5.5, elec=1.5, p_heat=8.0,
                 p_el=60, sorb_case="base", rl=scen["idea-pessimistic"], ts=20),
    "high": dict(capex=3000, r=0.10, n=15, om=0.05, heat=8.0, elec=2.5, p_heat=15.0,
                 p_el=100, sorb_case="pessimistic", rl=scen["stress: support degrades (N=2)"], ts=40),
}
results = {}
for k, d in full.items():
    cap = d["capex"] * crf(d["r"], d["n"])
    om = d["capex"] * d["om"]
    en = d["heat"] * d["p_heat"] + d["elec"] / 3.6 * d["p_el"]
    c, n, y, p = cases[d["sorb_case"]]
    s0 = p / prod[d["sorb_case"]] * 1000
    s1 = s0 * reload_fraction(*d["rl"])
    # downtime for reload: ~2 days per reload per module [assume]
    downtime = 2 / (365 * y)
    tot0 = cap + om + en + s0 + d["ts"]
    tot1 = (cap + om) / (1 - downtime) + en + s1 + d["ts"]
    results[k] = (tot0, tot1)
    print(f"  {k:<4}: capex ${cap:5.0f} + O&M ${om:4.0f} + energy ${en:4.0f} + sorbent ${s0:5.0f}"
          f" + T&S ${d['ts']} = ${tot0:5.0f}/t")
    print(f"        with reload: sorbent ${s1:5.0f}, downtime {downtime*100:.2f}% -> ${tot1:5.0f}/t"
          f"  (cut {100*(1-tot1/tot0):4.1f}%; sorbent share was {100*s0/tot0:4.1f}%)")
print("  Context: [mem] Young et al. 2023 (One Earth) put current solid DAC ~$400-1,000+/t,")
print("  2050 ~$200-500/t; realized 2024-25 CDR purchase prices for DAC ~$400-1,000/t (Frontier,")
print("  Microsoft offtakes; Climeworks' public price ~$1,000/t). Model is in that band.")

print("=" * 78)
print("6. MATERIAL FLOWS per Gt CO2/yr")
for k in ("pessimistic", "base", "optimistic"):
    sorb_mt = 1e9 / prod[k] / 1e9 * 1000  # Mt sorbent per Gt CO2  (1e9 t CO2 / (kg/kg) -> kg? )
    # 1 Gt = 1e12 kg CO2; sorbent kg = 1e12/prod; Mt = /1e9
    sorb_mt = 1e12 / prod[k] / 1e9
    amine_mt = 0.40 * sorb_mt
    print(f"  {k:<11}: sorbent {sorb_mt:5.1f} Mt/yr (no reload) ; amine {amine_mt:4.1f} Mt/yr "
          f"(reload: support make-up {0.6*sorb_mt/5:4.1f}-{0.6*sorb_mt/10:4.1f} Mt/yr at N=5-10)")
ETHYLENEAMINES_MT = 0.6   # [mem] global ethyleneamines production ~0.5-0.7 Mt/yr; PEI much smaller
print(f"  Global ethyleneamines market [mem] ~{ETHYLENEAMINES_MT} Mt/yr -> 1 Gt DAC needs "
      f"{1e12/hi_q/1e9*0.4/ETHYLENEAMINES_MT:.0f}-{1e12/lo_q/1e9*0.4/ETHYLENEAMINES_MT:.0f}x today's market"
      " in amine. Reload does not reduce amine demand (idea concedes).")
EMB = (2.0, 4.0)  # kg CO2e per kg amine [assume; petrochemical amine, cradle-to-gate]
for k in ("pessimistic", "optimistic"):
    am = 0.4 * 1e12 / prod[k] / 1e9
    print(f"  Embodied CO2 of amine make-up ({k}): {am*EMB[0]:.1f}-{am*EMB[1]:.1f} Mt per Gt "
          f"= {am*EMB[0]/10:.2f}-{am*EMB[1]/10:.2f}% of captured")
print("  Spent amine waste: same Mt/yr as amine make-up, now a liquid solvent stream on site")
print("  rather than a solid module returned to the factory (S11 handling issue).")
solvent_loss = (0.01, 0.05)  # fraction of solvent lost per reload [assume]
for k in ("pessimistic", "optimistic"):
    sorb = 1e12 / prod[k]  # kg sorbent reloaded per Gt
    v = [sorb * 4.0 * f / 1e9 for f in solvent_loss]
    print(f"  Methanol VOC loss per Gt ({k}), 4 kg/kg, 1-5% loss: {v[0]:.2f}-{v[1]:.2f} Mt/yr")

print("=" * 78)
print("7. SCALE AND ENERGY SHARE")
for gt, gj in ((0.1, 7.0), (0.5, 7.0), (1.0, 7.0), (1.0, 10.0)):
    s = ScaleCheck(gt, gj)
    print(f"  {gt:>4} Gt/yr at {gj:>4.1f} GJ/t: {s.ej_per_year:5.1f} EJ = "
          f"{s.share_of_world_primary_energy*100:4.2f}% world primary")
print("  Scale is that of solid-sorbent DAC (the idea is a cost lever, not a new removal")
print("  pathway). [mem] IEA NZE ~1 Gt/yr DAC by 2050; 2025 operating DAC ~0.01-0.02 Mt/yr realized.")
print("  Land: [mem] solid DAC plant footprint small (~0.1-1 km2/Mt excl. energy supply);")
print("  water: TVSA with steam can be net water-consuming or producing depending on climate.")

print("=" * 78)
print("8. FLAGS")
print("  - Nothing claimed below the thermodynamic floor: reload energy is additive, not a")
print("    separation-energy claim. Not physically_impossible.")
print("  - Mechanism precondition: amine must be PHYSICALLY impregnated. Climeworks' original")
print("    sorbent is aminosilane grafted on cellulose [mem, Gebald et al.] -> wash-out does")
print("    not apply. Fits PEI-impregnated monoliths/laminates (Global Thermostat-type) better.")
print("  - Oxidised PEI may crosslink or bind to silica (amides/imines/carboxylates); if not")
print("    removable by solvent, the support is fouled -> N small -> savings shrink (stress rows).")
print("  - Silica supports also age hydrothermally under steam regeneration; N=5-10 unproven.")
print("  - Claim (4) 94% loss in 24 h at 120 C/21% O2 [idea, Thakkar 2024] not re-verified here;")
print("    120 C accelerated aging may not reproduce 80-100 C humid field degradation chemistry.")
