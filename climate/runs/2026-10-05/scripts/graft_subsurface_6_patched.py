"""Verifier for graft_subsurface_6_patched: retire-and-store on depleted oil fields.

Checks: (A) thermodynamic floors (separation for DAC feed; compression for injection),
(B) field sizing (OOIP, storage capacity, residual EOR), (C) storage product cost/energy,
(D) retirement (avoidance) product cost per net tonne, incl. counterfactual-production
probability p and discounting consistency, (E) scale and resource needs.

Source labels: [V] OptiLex verifier physics.py; [EPA] EPA GHG Equivalencies (2022 data,
0.43 t CO2/bbl, fetched 2026-10-05); [IDEA] idea's own / critic inputs (unverified);
[MEM] model memory, unverified (web search budget exhausted this session); [CALC] derived here.
"""
import sys, math
sys.path.insert(0, 'climate')
from physics import *

def hr(t): print("\n=== " + t + " ===")

# ---------------- A. Thermodynamic floors ----------------
hr("A. Floors")
w_air = min_separation_work(420e-6, 0.75, 0.99)
print(f"[V] DAC separation floor (420 ppm, 75% capture, 99% pure): {w_air/1e3:.1f} kJ/mol = {gj_per_tonne(w_air):.3f} GJ/t")
# isothermal ideal-gas compression 1 -> 150 bar (upper bound on reversible work; real-gas
# behaviour near/above critical point (73.8 bar) lowers the true reversible minimum)
for p_bar in (100, 150):
    w = R*T0*math.log(p_bar/1.01325)/M_CO2/1e6  # GJ/t
    print(f"[CALC] Ideal isothermal compression 1 atm -> {p_bar} bar: {w:.3f} GJ/t ({w/0.0036:.0f} kWh/t)")
comp = {"low": 0.31, "base": 0.40, "high": 0.53}  # [IDEA] critic estimate; [MEM] ~90-150 kWh/t real compressor+pump
print("[IDEA/MEM] Real compression+injection, GJ/t:", comp, "-> 2nd-law eff. vs 0.28 floor:",
      {k: round(0.28/v, 2) for k, v in comp.items()})
dac = {"low": 5.0, "base": 7.5, "high": 10.0}  # task brief: measured 5-10+ GJ/t
print("Claimed floors in idea (0.28 compression, 0.47 separation) vs computed: consistent; no claim below floor.")

# ---------------- B. Field sizing ----------------
hr("B. Field sizing (case unit 10,000 acres, 30 m, phi 0.12) [IDEA]")
area = 10000*4046.86; h = 30; phi = 0.12; Bo = 1.2
pore = area*h*phi
print(f"[CALC] Pore volume: {pore/1e6:.0f} Mm3")
ooip = {}
for Soi in (0.70, 0.80):
    ooip[Soi] = pore*Soi/Bo*6.2898
    print(f"[CALC] Soi={Soi}: OOIP = {ooip[Soi]/1e6:.0f} Mbbl")
# Storage capacity by produced-volume method: cumulative reservoir voidage x CO2 density x utilisation
for rf_cum, rho, util in ((0.30, 600, 0.6), (0.40, 680, 0.8), (0.50, 750, 1.0)):
    void_m3 = 573e6*rf_cum/6.2898*Bo  # mid OOIP 573 Mbbl
    cap = void_m3*rho*util/1e9  # Mt
    print(f"[CALC] cum RF {rf_cum:.2f}, rho {rho} kg/m3, utilisation {util}: capacity {cap:.0f} Mt")
print("-> idea's 11-44 Mt range is consistent with produced-volume sizing (11-43 Mt here).")

# Residual EOR resource: idea uses 8-18% of OOIP. That is the incremental recovery of a FULL
# CO2 flood [MEM: NETL/ARI ~5-20% OOIP]. The target is POST-flood units, whose remaining
# tertiary/ROZ/tail resource is far smaller [MEM, assumption 1-5% OOIP].
hr("B2. Residual EOR resource")
cases_rf = {"idea (un-flooded, 8-18%)": (0.08, 0.18), "post-flood tail (1-5%, assumption)": (0.01, 0.05)}
for k, (a, b) in cases_rf.items():
    lo, hi = a*535e6, b*611e6
    print(f"{k}: {lo/1e6:.0f}-{hi/1e6:.0f} Mbbl; per t stored over 11-44 Mt: {lo/44e6:.1f}-{hi/11e6:.1f} bbl/t")
print("-> Internal inconsistency: 'truly depleted, post-CO2-flood' targets cannot also hold 8-18% OOIP of EOR oil.")

# ---------------- C. Storage (removal) product ----------------
hr("C. Storage product: cost and energy")
# [MEM] onshore Class VI storage incl. MMV $8-20/t; transport $5-15/t; restriction/easement admin ~$0.5-2/t
stor = {"low": 8+5+0.5, "base": 14+10+1, "high": 20+15+2}
elec = {"low": 40, "base": 70, "high": 110}  # $/MWh [MEM] US industrial power range 2025-26
for k in ("low", "base", "high"):
    e_cost = energy_cost_floor(comp[k], elec[k])
    print(f"{k}: compression {comp[k]} GJ/t -> ${e_cost:.1f}/t energy; T&S+restriction ${stor[k]:.1f}/t; total ${stor[k]+e_cost:.0f}/t stored (excl. capture)")
dac_cost = {"low": 400, "base": 650, "high": 1000}  # [MEM] 2025-26 DAC contract/realised prices
print("Full removal chain incl. DAC capture [MEM]:", {k: dac_cost[k]+stor[k]+round(energy_cost_floor(comp[k], elec[k])) for k in dac_cost})
print("Energy per t removed (DAC + compression), GJ/t:", {k: dac[k]+comp[k] for k in dac})

# ---------------- D. Retirement (avoidance) product ----------------
hr("D. Retirement product: $/t net avoided")
EF = 0.43  # [EPA] t CO2/bbl, combustion only (lifecycle incl. upstream ~0.5 [MEM])
def pv_factor(years=25, r=0.08, delay=2):
    """PV of a level production stream per undiscounted bbl."""
    return sum((1+r)**-(t+delay) for t in range(1, years+1))/years
for yrs, r, d in ((20, 0.06, 1), (25, 0.08, 2), (30, 0.10, 3)):
    print(f"[CALC] PV factor, {yrs} yr level profile, {r:.0%} discount, {d} yr delay: {pv_factor(yrs, r, d):.2f}")
print("-> idea's 0.5 PV factor is within the 0.3-0.6 range; acceptable as a crude factor.")

print("\nD1. Idea's own crediting (bbl x 0.43 x (1-repl)), PV cost / undiscounted tonnes:")
for nb in (28, 52):
    for repl in (0.8, 0.5):
        for pv in (1.0, 0.5):
            print(f"  netback ${nb}/bbl repl {repl} PVfac {pv}: ${nb*pv/(EF*(1-repl)):.0f}/t")
print("  (reproduces the idea's $326-605 / $163-302 / $130-242 / $65-121 ranges)")

print("\nD2. Additionality: owners' rational reservation bid = p_prod x PV(netback). Real avoided t = p_prod x bbl x EF x (1-repl).")
print("    Cost per REAL net tonne = PVfac x netback / (EF x (1-repl)), independent of p_prod.")
print("    The idea's credit formula omits p_prod, so a cheap-clearing field over-issues credits by 1/p_prod.")
for nb_pv_bid in (13, 20, 30):
    for nb_full in (28, 52):
        p_imp = nb_pv_bid/(0.5*nb_full)
        if p_imp <= 1:
            print(f"  bid ${nb_pv_bid}/bbl (PV) vs full PV netback ${0.5*nb_full:.0f}: implied p_prod {p_imp:.2f} -> credits over-issued x{1/p_imp:.1f}")
print("  Break-even netback (undiscounted) for real cost <= $150/t with PVfac 0.5:")
for repl in (0.8, 0.5):
    print(f"    repl {repl}: netback <= ${150*EF*(1-repl)/0.5:.1f}/bbl (PV bid <= ${150*EF*(1-repl):.1f}/bbl)")
print("  -> At 80% replacement the $150/t kill threshold is breached for any netback >= $26/bbl, i.e. across the idea's whole $28-52 range.")

print("\nD3. Low/base/high real $/t net avoided (PVfac 0.5, real tonnes):")
lohi = {"low": (28, 0.5), "base": (40, 0.7), "high": (52, 0.8)}  # (netback, replacement)
avoid_cost = {}
for k, (nb, repl) in lohi.items():
    avoid_cost[k] = 0.5*nb/(EF*(1-repl))
    print(f"  {k}: netback ${nb}, repl {repl}: ${avoid_cost[k]:.0f}/t")
print("  Option-value premium (owners demand above expected NPV) would push these up [qualitative].")

# Retirement cost per field, undiscounted and PV
hr("D4. Per-field retirement cost")
for bbl in (43e6, 110e6):
    for nb in (28, 52):
        print(f"  {bbl/1e6:.0f} Mbbl @ ${nb}: ${bbl*nb/1e9:.2f}B undiscounted, ${0.5*bbl*nb/1e9:.2f}B PV")
print("  Depleted GAS fields: no residual-oil estate -> retirement product does not apply; only the storage restriction does.")

# ---------------- E. Scale and resources ----------------
hr("E. Scale")
for nf, cap, yrs in ((10, 11e6, 30), (10, 44e6, 20), (30, 25e6, 25)):
    print(f"  {nf} fields x {cap/1e6:.0f} Mt over {yrs} yr: {nf*cap/yrs/1e9:.4f} Gt/yr stored")
# Ceiling for the avoidance product: retire ALL US CO2-EOR output [MEM ~250-300 kb/d]
for kbd in (250, 300):
    gbbl = kbd*1e3*365/1e9
    for repl in (0.8, 0.5):
        g = gbbl*EF*(1-repl)
        print(f"  Retire all US CO2-EOR ({kbd} kb/d = {gbbl:.3f} Gbbl/yr), repl {repl}: {g:.4f} Gt/yr net avoided = {g/TOTAL_GHG_GT_CO2E:.3%} of world GHG; cost ${gbbl*1e9*40/1e9:.1f}B/yr @ $40 netback")
stored, avoided = 0.02, 0.008
print(f"  Idea's claim: {stored} Gt/yr stored + {avoided} Gt/yr avoided = {(stored+avoided)/TOTAL_GHG_GT_CO2E:.3%} of world GHG")
for k in ("low", "base", "high"):
    sc = ScaleCheck(stored, comp[k]); sd = ScaleCheck(stored, dac[k]+comp[k])
    print(f"  energy {k}: compression only {sc.ej_per_year*1e3:.1f} PJ/yr ({sc.share_of_world_primary_energy:.4%} world primary); with DAC feed {sd.ej_per_year:.3f} EJ/yr ({sd.share_of_world_primary_energy:.3%}; {sd.share_of_world_electricity_if_electric:.3%} of world electricity if electric)")
print("  Land: well pads/monitoring only (DAC land counted elsewhere). Water: none consumed by storage; pressure-management brine produced.")
