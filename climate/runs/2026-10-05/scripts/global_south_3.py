"""Verifier for idea global_south_3: swap carbonate aglime for silicate fines on tropical
estates, credit avoided carbonate CO2 and (only if detectable) silicate CDR.

All inputs are labelled: [P] primary source checked this session, [R] recalled literature
value (verify before quoting), [A] engineering assumption.
"""
import sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

M_CACO3, M_MGCA = 100.09, 184.40
print("=== 1. Thermodynamic floor ===")
air_floor = gj_per_tonne(min_separation_work(420e-6, 0.75))
print(f"No gas separation step. Avoided-emission part: floor = 0 GJ/t (an emission not made).")
print(f"Silicate weathering is spontaneous (exergonic mineral dissolution); floor for its CDR = 0 beyond "
      f"rock handling. Air-capture floor for comparison: {air_floor:.2f} GJ/t.")

print("\n=== 2. Emission factors (IPCC 2006 Tier 1 check) ===")
ef_ls = 44.01 / M_CACO3                  # all carbonate C emitted
ef_dol = 2 * 44.01 / M_MGCA
print(f"Limestone Tier 1: {ef_ls:.3f} t CO2/t (claim 0.44)   Dolomite Tier 1: {ef_dol:.3f} t CO2/t (claim 0.48)")
ef_blend = 0.5 * ef_ls + 0.5 * ef_dol    # [A] Brazilian aglime is largely dolomitic/magnesian
# Net emission depends on the strong-acid (nitric) share f_s of lime dissolution. Carbonic-acid
# dissolution consumes one atmospheric CO2 per carbonate (sink); strong-acid releases the carbonate C.
# E = EF * (f_s - (1 - f_s)) = EF * (2 f_s - 1). f_s=0.75 reproduces West & McBride's ~49% of Tier 1 [R].
def net_ef(f_s, ef=ef_blend):
    return ef * (2 * f_s - 1)
for f_s in (0.5, 0.6, 0.75, 0.9, 1.0):
    print(f"  f_strong={f_s:.2f}: net lime emission {net_ef(f_s):+.3f} t CO2/t lime ({net_ef(f_s)/ef_blend:.0%} of Tier 1)")

print("\n=== 3. Substitution logistics per t lime replaced ===")
def bond_kwh(wi, p80, f80):
    return 10 * wi * (1 / p80 ** 0.5 - 1 / f80 ** 0.5)
print(f"Bond grinding Wi=20, F80=10 mm: P80 100 um {bond_kwh(20,100,10000):.1f} kWh/t, "
      f"P80 50 um {bond_kwh(20,50,10000):.1f} kWh/t (claim 18-26)")
print(f"  Typical quarry 'fines' (P80 ~1-2 mm [R]) are NOT 100 um powder: P80 1500->100 um costs "
      f"{bond_kwh(20,100,1500):.1f} kWh/t if regrinding is needed.")

cases = {
    #            CCE   haul km  truck kgCO2/tkm  lime haul km  f_s   grind kWh/t  grid kg/kWh
    "low":  dict(cce=0.30, d=30,  tk=0.06, d_lime=200, f_s=0.90, grind=0.0,  grid=0.10),
    "base": dict(cce=0.20, d=50,  tk=0.08, d_lime=150, f_s=0.75, grind=13.0, grid=0.30),
    "high": dict(cce=0.10, d=100, tk=0.10, d_lime=100, f_s=0.65, grind=26.0, grid=0.60),
}
# CCE: calcium-carbonate equivalence of basalt/andesite fines over the agronomic horizon [A, R: 10-30%].
# Truck 0.06-0.10 kg CO2/t-km heavy truck incl. empty return [R, GLEC-order]. Spreading 0.5 L diesel/t
# = 1.35 kg CO2/t [A]. Lime quarry+grind 8 kg CO2/t [A]. grid: Brazil ~0.1, Malaysia ~0.6 kg/kWh [R].
SPREAD = 1.35
DIESEL_MJ_PER_TKM = 0.9   # [R] heavy truck ~0.025 L/t-km x 36 MJ/L incl. return
res = {}
for k, c in cases.items():
    n_rock = 1 / c["cce"]
    haul = n_rock * c["d"] * c["tk"]
    spread_extra = (n_rock - 1) * SPREAD
    grind = n_rock * c["grind"] * c["grid"]
    lime_upstream = 8 + c["d_lime"] * c["tk"]            # avoided lime production + haul
    gross = net_ef(c["f_s"]) * 1000                       # kg CO2 avoided per t lime
    net = gross - haul - spread_extra - grind + lime_upstream
    energy_mj = (n_rock * c["d"] * DIESEL_MJ_PER_TKM + (n_rock - 1) * 0.5 * 36
                 + n_rock * c["grind"] * 3.6 / 0.4)        # grinding electricity as primary (40% eff.)
    res[k] = dict(c, n_rock=n_rock, net=net, energy=energy_mj)
    print(f"[{k}] rock {n_rock:.1f} t/t lime | gross avoided {gross:.0f} kg | haul {haul:.0f} | "
          f"extra spreading {spread_extra:.0f} | grinding {grind:.0f} | avoided lime upstream {lime_upstream:.0f} "
          f"| NET {net:.0f} kg CO2/t lime replaced")
    print(f"       process energy {energy_mj:.0f} MJ/t lime = "
          f"{energy_mj/1000/(net/1000) if net > 0 else float('nan'):.2f} GJ/t CO2e avoided")

# Break-even strong-acid share (base logistics)
c = res["base"]
burden = c["n_rock"]*c["d"]*c["tk"] + (c["n_rock"]-1)*SPREAD + c["n_rock"]*c["grind"]*c["grid"] - (8 + c["d_lime"]*c["tk"])
f_be = (burden / 1000 / ef_blend + 1) / 2
print(f"Break-even strong-acid share (base logistics): f_s = {f_be:.2f}; below it the swap emits more than it saves.")

print("\n=== 4. Silicate CDR detectability at swap rates ===")
lime_rate = 1.5      # t lime/ha/yr on limed tropical estates [A]
swap = 0.30
for k in ("low", "base", "high"):
    rock_ha = lime_rate * swap * res[k]["n_rock"]
    for r in (0.05, 0.02):    # t CO2/t rock: Illinois-type optimistic [R, Beerling 2024 order], pessimistic
        print(f"[{k}] rock {rock_ha:.1f} t/ha/yr x {r} t CO2/t = {rock_ha*r:.3f} t CO2/ha/yr")
larkin_noise = (0.8**2 + 0.6**2) ** 0.5   # [P] Larkin 2022 treated 3.8+-0.8, control 3.7+-0.6 t/ha
print(f"Larkin 2022 [P]: 50 t/ha/yr x3 yr andesite, difference 0.1 t/ha with combined 1-sigma {larkin_noise:.1f} t/ha "
      f"(per-ha cumulative). Swap-rate signal is ~{0.075/ (50*0.05):.1%}-{0.75/(50*0.05):.0%} of a 50 t/ha "
      f"application at the same per-rock rate; apportionment must cut uncertainty >10x to detect it.")

print("\n=== 5. Cost per t CO2e avoided (avoided-emission credit only) ===")
cost = {
    #          rock $/t  haul $/tkm spread $/t lime delivered $/t  elec $/MWh  MRV $/yr  lime replaced t/yr per estate
    "low":  dict(rock=2,  hk=0.04, sp=3, lime=50, el=60,  mrv=50e3,  t=20000),
    "base": dict(rock=6,  hk=0.06, sp=4, lime=35, el=80,  mrv=100e3, t=6000),
    "high": dict(rock=15, hk=0.10, sp=6, lime=25, el=120, mrv=200e3, t=2000),
}
# Rock fines price, freight, spreading, delivered lime: [R/A] Brazil order-of-magnitude (R$ to $ at ~5.4).
# MRV: lysimeters/drain sampling + Sr isotopes (~$150-300/sample) + d13C-DIC + labour per estate [A].
# Capex: none new (existing quarries, trucks, spreaders); no annualisation term beyond freight rates.
usd = {}
for k in ("low", "base", "high"):
    c, p = res[k], cost[k]
    rock_cost = c["n_rock"] * (p["rock"] + p["hk"] * c["d"] + p["sp"] + c["grind"] / 1000 * p["el"])
    lime_cost = p["lime"] + p["sp"]
    mrv = p["mrv"] / p["t"]
    delta = rock_cost - lime_cost + mrv
    per_t = delta / (c["net"] / 1000) if c["net"] > 0 else float("inf")
    usd[k] = per_t
    print(f"[{k}] rock delivered+spread {rock_cost:.0f} $/t lime-eq vs lime {lime_cost:.0f} | MRV {mrv:.0f} | "
          f"delta {delta:+.0f} $/t lime | net avoided {c['net']/1000:.3f} t | {per_t:,.0f} $/t CO2e")

print("\n=== 6. Scale ===")
br_lime = (35, 45, 50)       # Mt/yr Brazil aglime [R, ABRACAL-order; not verified this session]
prox = (0.2, 0.35, 0.5)      # share of use within ~50 km of basalt/andesite quarry fines [A]
sea_lime = (2, 5, 10)        # Mt/yr GML/dolomite on Malaysian+Indonesian palm [A, low confidence]
glob_lime = (100, 200, 300)  # Mt/yr global aglime [A, order of magnitude]
for i, k in enumerate(("low", "base", "high")):
    n = res[k]["net"] / 1000
    br = br_lime[i] * swap * prox[i] * n
    sea = sea_lime[i] * swap * prox[i] * n
    gl = glob_lime[i] * 0.5 * 1.0 * max(net_ef(1.0), 0)   # absolute ceiling: half of all aglime, Tier 1
    print(f"[{k}] Brazil {br:.2f} Mt + SE Asia {sea:.2f} Mt = {(br+sea)/1000:.4f} Gt CO2e/yr; "
          f"global ceiling (50% of aglime, Tier 1, zero logistics) {gl/1000:.3f} Gt")
tier1_brazil = [x * ef_blend for x in br_lime]
print(f"Brazil aglime at Tier 1: {tier1_brazil[0]:.0f}-{tier1_brazil[2]:.0f} Mt CO2/yr (claim 15-22); "
      f"net (f_s 0.75): {br_lime[0]*net_ef(0.75):.0f}-{br_lime[2]*net_ef(0.75):.0f} (claim 8-11)")
print(f"Claim '30% swap = 2.5-7 Mt/yr' vs computed Brazil-wide 30% swap with NO proximity limit and "
      f"base net factor: {br_lime[1]*swap*res['base']['net']/1000:.1f} Mt/yr")

print("\n=== 7. Resource needs (base) ===")
c = res["base"]
br_rep = br_lime[1] * swap * prox[1]
rock_mt = br_rep * c["n_rock"]
e_ej = br_rep * 1e6 * c["energy"] / 1e12
print(f"Lime replaced {br_rep:.1f} Mt/yr -> rock {rock_mt:.0f} Mt/yr (Brazil aggregates output ~500-700 Mt/yr [R])")
print(f"Process energy {e_ej*1000:.1f} PJ/yr = {e_ej/WORLD_PRIMARY_ENERGY_EJ:.2e} of world primary energy")
print("Land: zero new (existing estates). Water: none beyond rainfall.")

print("\n=== 8. Base-case sensitivities ($/t CO2e) ===")
def base_cost(**ov):
    c = dict(res["base"]); p = dict(cost["base"]); c.update({k: v for k, v in ov.items() if k in c}); p.update({k: v for k, v in ov.items() if k in p})
    n_rock = 1 / c["cce"]
    net = (net_ef(c["f_s"]) * 1000 - n_rock*c["d"]*c["tk"] - (n_rock-1)*SPREAD - n_rock*c["grind"]*c["grid"] + 8 + c["d_lime"]*c["tk"]) / 1000
    delta = n_rock*(p["rock"] + p["hk"]*c["d"] + p["sp"] + c["grind"]/1000*p["el"]) - (p["lime"] + p["sp"]) + p["mrv"]/p["t"]
    return delta / net if net > 0 else float("inf"), net
for label, ov in [("base", {}), ("no regrind (fines already <100 um)", dict(grind=0.0)),
                  ("no regrind + rock free at quarry", dict(grind=0.0, rock=0)),
                  ("no regrind + CCE 0.30", dict(grind=0.0, cce=0.30)),
                  ("f_s=0.60 (more carbonic-acid dissolution)", dict(f_s=0.60)),
                  ("f_s=0.95 (heavy urea, acid Oxisol)", dict(f_s=0.95)),
                  ("large estate 30k t lime/yr (MRV dilution)", dict(t=30000))]:
    v, n = base_cost(**ov)
    print(f"  {label:<45} {v:>8,.0f} $/t  (net {n:.3f} t CO2/t lime)")
