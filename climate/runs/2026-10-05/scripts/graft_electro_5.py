"""Verifier for graft_electro_5: AEC-Q100-style accelerated qualification of DAC sorbents.

The idea is a test protocol plus a procurement gate; it removes no CO2 itself. So we check:
 1. the thermodynamic floor of the DAC it gates (separation from air),
 2. the claimed sorbent-cost-per-tonne arithmetic C/(0.044 q N),
 3. the claimed Arrhenius/O2 acceleration factors, and whether the stated 'field baseline'
    (100 C regeneration in air) matches how TVSA plants actually expose sorbent,
 4. extrapolation error: how much activation-energy uncertainty blows up the prediction
    at field temperatures (why field calibration is load-bearing),
 5. the utilisation lever (0.9/u),
 6. a levelised cost of DAC (low/base/high) with capex annualisation, energy, sorbent, O&M,
    showing how much of it the sorbent-lifetime lever actually controls,
 7. the protocol's own incremental cost per tonne, and realistic scale.
All inputs are labelled MEASURED / REPORTED / LITERATURE-MODELLED / ASSUMED.
"""
import math
import sys

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

line = "-" * 78

# ---------------------------------------------------------------- 1. floor
w = min_separation_work(420e-6, 0.75, 0.99)
floor = gj_per_tonne(w)
print(line)
print("1. Thermodynamic floor of the gated process (DAC, 420 ppm, 75% capture, 99% pure)")
print(f"   min work = {w/1e3:.2f} kJ/mol = {floor:.3f} GJ/t CO2 = {floor/0.0036:.0f} kWh/t")
# Real solid-amine TVSA: ~5-10 GJ/t total (mostly ~100 C heat), LITERATURE-MODELLED / vendor-reported
for real in (5.0, 7.0, 10.0):
    print(f"   real {real:>4.1f} GJ/t -> second-law efficiency {second_law_efficiency(real, floor)*100:.1f}%")
print("   The protocol itself uses ~0 energy (lab ovens, a pilot rig); no claim goes below the floor.")

# ---------------------------------------------------------------- 2. sorbent cost per tonne
print(line)
print("2. Sorbent cost per tonne = C / (0.044 q N) x 1000   [C $/kg, q mol/kg working, N cycles]")
print("   Claim used q = 1-2 mmol/g. ASSUMED realistic cyclic working capacity under humid 400 ppm")
print("   for Lewatit-class / PEI-silica is often 0.5-1.5 mmol/g (literature range; flag).")
def sorbent_cost(C, q, N):
    return C * 1000.0 / (0.04401 * q * N)
print(f"   {'N cycles':>9} | {'claim range (q 1-2, C 20-50)':>30} | {'wider (q 0.5-2, C 10-50)':>26}")
for N in (1_000, 5_000, 20_000, 100_000):
    lo, hi = sorbent_cost(20, 2, N), sorbent_cost(50, 1, N)
    lo2, hi2 = sorbent_cost(10, 2, N), sorbent_cost(50, 0.5, N)
    print(f"   {N:>9,} | ${lo:>8.0f} - ${hi:>8.0f} /t          | ${lo2:>7.0f} - ${hi2:>7.0f} /t")
print("   -> Claimed $227-1,136 (N=1k) ... $2-11 (N=100k) reproduced. Arithmetic is correct.")
# cycles/yr for context: TVSA cycle ~ 2-6 h (ASSUMED, typical of published Climeworks-class models)
for cyc_h in (2, 4, 6):
    n_yr = 8760 * 0.9 / cyc_h
    print(f"   cycle {cyc_h} h at 90% uptime -> {n_yr:,.0f} cycles/yr; N=5,000 = {5000/n_yr:.1f} yr, "
          f"N=20,000 = {20000/n_yr:.1f} yr")

# ---------------------------------------------------------------- 3. acceleration factors
print(line)
print("3. Acceleration factors (Arrhenius x O2 power law)")
def af_T(Ea, T1, T2):
    return math.exp(Ea / R * (1 / (T1 + 273.15) - 1 / (T2 + 273.15)))
for Ea in (60e3, 90e3):
    a = af_T(Ea, 100, 120)
    print(f"   Ea {Ea/1e3:.0f} kJ/mol: 100->120 C AF = {a:.2f}; x O2 21->100% (1st order, x{100/21:.2f}) "
          f"= {a*100/21:.1f}; 1 week stress = {a*100/21/4.345:.1f} months at 100 C in air")
print("   -> Claimed 2.7-4.4x and 13-21x reproduced (given the ASSUMED Ea and 1st-order O2).")

print("\n   Field-baseline check. In Climeworks-class TVSA, desorption is under vacuum with steam;")
print("   pO2 during the hot step is low (ASSUMED 0.5-5% of air), and the sorbent spends only a")
print("   fraction of each cycle hot (ASSUMED 15-30%). Ambient adsorption (~15 C, full air O2) is")
print("   the majority of the time. Plant-years equivalent of 4-8 weeks of stress at 120 C, 100% O2:")
for Ea in (60e3, 90e3):
    for hot_frac, o2_hot in ((0.15, 0.005), (0.30, 0.05)):
        # degradation rate relative to stress cell, per unit field time (O2 1st order, Arrhenius)
        r_hot = hot_frac * (1 / af_T(Ea, 100, 120)) * (o2_hot * 0.21) / 1.0  # O2 1st order vs 100% O2 cell
        r_amb = (1 - hot_frac) * (1 / af_T(Ea, 15, 120)) * 0.21
        r_field = r_hot + r_amb  # relative to stress-cell rate = 1
        for weeks in (4, 8):
            yrs = weeks / 52.18 / r_field
            print(f"   Ea {Ea/1e3:.0f}, hot {hot_frac:.0%}, hot-step O2 {o2_hot*0.21*100:.2f}% abs: "
                  f"{weeks} wk stress = {yrs:,.0f} plant-yr (overall AF {1/r_field:,.0f}x)")
print("   -> If the hot step is O2-starved, the field rate is tiny and the stress cell must")
print("      extrapolate across a 100-10,000x gap: the 'same mechanism' fingerprint rule then")
print("      becomes the whole test. Real plants also see air ingress at hot/cold transitions,")
print("      which dominates and is plant-specific (UNKNOWN; no public data).")

# ---------------------------------------------------------------- 4. extrapolation error
print(line)
print("4. Sensitivity of extrapolated rate to Ea uncertainty (why field calibration is essential)")
for Tf in (100, 60, 25):
    a60, a90 = af_T(60e3, Tf, 120), af_T(90e3, Tf, 120)
    print(f"   120 C -> {Tf:>3} C: AF = {a60:,.1f} (Ea 60) to {a90:,.1f} (Ea 90); spread x{a90/a60:,.1f}")
# What Ea precision is needed for +/-30% on a 120->100 C extrapolation and a 120->25 C one?
for Tf in (100, 25):
    d = 1 / (Tf + 273.15) - 1 / 393.15
    dEa = math.log(1.3) * R / d
    print(f"   +/-30% at {Tf} C needs Ea known to +/-{dEa/1e3:.1f} kJ/mol")
print("   Peck humidity term: for amines water generally SUPPRESSES urea formation and can")
print("   slow oxidation (literature, mechanism-dependent) -> a semiconductor-style positive RH")
print("   exponent may have the wrong sign. Model form must be fitted, not imported.")

# ---------------------------------------------------------------- 5. utilisation lever
print(line)
print("5. Utilisation lever: capital charge scales as 1/u (ratio vs u=0.9)")
for name, u in (("Mammoth (claimed 3.75% of nameplate, early ops, REPORTED/unverified)", 0.0375),
                ("Orca (~27%, REPORTED)", 0.27), ("design 90%", 0.90)):
    print(f"   {name:<62} 0.9/u = {0.9/u:5.2f}x")
print("   Confound: published under-delivery causes are commissioning/engineering/energy issues,")
print("   not demonstrated sorbent fade. A sorbent standard addresses only one cause.")

# ---------------------------------------------------------------- 6. LCOD model
print(line)
print("6. Levelised cost of DAC (solid-amine TVSA), $/t CO2 net-captured (gross; no LCA penalty)")
def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)
cases = {
    #           capex $/(t/yr)  r     yrs  util  heat GJ/t  heat $/GJ  elec MWh/t  elec $/MWh  C $/kg  q   N      O&M %capex
    "low":  dict(capex=1000, r=0.06, n=25, u=0.90, heat=4.5, hp=4.0, elec=0.35, ep=40, C=10, q=1.5, N=20000, om=0.03),
    "base": dict(capex=2500, r=0.08, n=20, u=0.80, heat=6.0, hp=8.0, elec=0.50, ep=70, C=30, q=1.0, N=5000, om=0.04),
    "high": dict(capex=5000, r=0.10, n=15, u=0.60, heat=8.0, hp=12.0, elec=0.80, ep=100, C=50, q=0.7, N=1000, om=0.05),
}
# Sources/justification (ASSUMED ranges spanning literature):
#  capex: NOAK modelled ~$700-1,500/(t/yr) (Fasihi 2019; Sievert 2024); FOAK plants ~$3-6k/(t/yr)
#    implied by public Climeworks/1PointFive figures (REPORTED, not audited).
#  heat 4.5-8 GJ/t at ~100 C (Climeworks-class modelled; Deutz & Bardow 2021 LCA ~ 5-7 GJ/t),
#    priced as waste/heat-pump/geothermal heat $4-12/GJ.  elec 0.35-0.8 MWh/t (fans, vacuum).
#  sorbent: section 2. O&M 3-5% capex/yr. Real 2024-25 contract prices: ~$400-1,000+/t (REPORTED).
res = {}
en_gj = {}
for k, c in cases.items():
    cap = c["capex"] * crf(c["r"], c["n"]) / c["u"]
    om = c["capex"] * c["om"] / c["u"]
    en = c["heat"] * c["hp"] + c["elec"] * c["ep"]
    sb = sorbent_cost(c["C"], c["q"], c["N"])
    tot = cap + om + en + sb
    res[k] = tot
    e_tot = c["heat"] + c["elec"] * 3.6
    en_gj[k] = e_tot
    print(f"   {k:>4}: capital {cap:6.0f} + O&M {om:5.0f} + energy {en:5.0f} + sorbent {sb:6.0f} = ${tot:6.0f}/t;"
          f" energy {e_tot:.1f} GJ/t ({e_tot/floor:.0f}x floor)")
print("\n   Sorbent-lifetime lever inside the base case (other inputs held at base):")
b = cases["base"]
for N in (1000, 5000, 20000, 100000):
    sb = sorbent_cost(b["C"], b["q"], N)
    cap = b["capex"] * crf(b["r"], b["n"]) / b["u"]
    om = b["capex"] * b["om"] / b["u"]
    en = b["heat"] * b["hp"] + b["elec"] * b["ep"]
    print(f"   N={N:>7,}: sorbent ${sb:5.0f}/t -> total ${cap+om+en+sb:5.0f}/t (sorbent share {sb/(cap+om+en+sb):.0%})")
print("   Utilisation lever inside the base case:")
for u in (0.0375, 0.27, 0.5, 0.8, 0.9):
    cap = b["capex"] * crf(b["r"], b["n"]) / u
    om = b["capex"] * b["om"] / u
    print(f"   u={u:5.3f}: capital+O&M ${cap+om:6.0f}/t")

# ---------------------------------------------------------------- 7. protocol cost and scale
print(line)
print("7. The protocol's own cost per tonne (incremental, amortised over a vendor's deliveries)")
# per-sorbent qualification $0.1-0.3M (claim) + $50-150k field rig; plus standards body ~$2-5M/yr (ASSUMED)
for qual, tonnes in ((0.15e6, 1e6), (0.4e6, 1e5), (0.6e6, 1e4)):
    print(f"   qual ${qual/1e6:.2f}M over {tonnes:>9,.0f} t delivered -> ${qual/tonnes:7.2f}/t")
for body, market in ((2e6, 10e6), (5e6, 1e6), (5e6, 0.1e6)):
    print(f"   standards body ${body/1e6:.0f}M/yr over {market/1e6:.1f} Mt/yr DAC -> ${body/market:6.2f}/t")
print("   DAC delivered worldwide 2025 is ~kt/yr scale (REPORTED); contracted pipeline ~ few Mt total.")

print("\n   Scale: the idea removes 0 t itself; it de-risks DAC. Plausible DAC 2035 (ASSUMED):")
for gt, gj in ((0.001, 6.0), (0.01, 6.0), (0.05, 6.0), (1.0, 6.0)):
    s = ScaleCheck(gt, gj)
    print(f"   {gt:6.3f} Gt/yr at {gj} GJ/t: {s.ej_per_year:6.3f} EJ/yr = "
          f"{s.share_of_world_primary_energy*100:6.3f}% of world primary energy")
# sorbent mass flow at scale
for gt, N, q in ((0.01, 5000, 1.0), (1.0, 5000, 1.0), (1.0, 20000, 1.0)):
    kg = gt * 1e12 / (0.04401 * q * N)
    print(f"   {gt} Gt/yr, N={N:,}, q={q}: sorbent replacement {kg/1e9:,.2f} Mt/yr")
print("   Land: contactor footprint small (~0.1-1 km2 per Mt/yr incl. spacing, literature-modelled);")
print("   water: humid TVSA can be net water producer or consumer, site-dependent (UNKNOWN).")

print(line)
print(f"SUMMARY: floor {floor:.3f} GJ/t; gated DAC energy low/base/high {en_gj['low']:.1f}/{en_gj['base']:.1f}/{en_gj['high']:.1f} GJ/t;")
print(f"LCOD low/base/high ${res['low']:.0f}/${res['base']:.0f}/${res['high']:.0f} per t;")
print("protocol incremental cost ~$0.2-60/t depending on deliveries; no physics violations.")
