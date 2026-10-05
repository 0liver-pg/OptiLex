"""Verifier for idea incumbent_assets_1: CO2 cushion-gas swap in existing underground gas storage (UGS).

Run: cd . && .venv/bin/python <this file>
Labels: [V] OptiLex verifier, [CP] CoolProp reference EOS (Span-Wagner CO2, Setzmann-Wagner CH4),
[S] source value, [A] assumption (justified inline), [M] modelled literature estimate.
"""
import math, sys
sys.path.insert(0, 'climate')
sys.path.insert(0, 'climate/runs/2026-10-05/scripts/pylib')
from physics import *  # noqa
import CoolProp.CoolProp as CP

def rho(f, TC, Pbar): return CP.PropsSI('D', 'T', TC + 273.15, 'P', Pbar * 1e5, f)
def mu(f, TC, Pbar): return CP.PropsSI('V', 'T', TC + 273.15, 'P', Pbar * 1e5, f)
def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

CH4_HHV = 55.5                 # GJ/t HHV [S standard]
MMBTU_PER_GJ = 0.9478
CO2_PER_CH4 = 44.01 / 16.043   # t CO2 per t CH4 burned (stoichiometric)
KG_PER_M3_NG = 0.72            # kg/Sm3 pipeline gas [A, ~ pure CH4 at 15C]
BCF_TO_BCM = 0.0283168

# ---------------------------------------------------------------- 1. floors
print("=== 1. Thermodynamic floors [V]")
def comp_floor(p_bar, T=T0):  # ideal isothermal compression from 1 atm, GJ/t CO2
    return R * T * math.log(p_bar / 1.01325) / M_CO2 / 1e6
for name, x in [("cement kiln 25%", 0.25), ("lime kiln ~30%", 0.30), ("AGRU/fermentation ~98%", 0.98)]:
    print(f"  separation floor, {name}, 90% capture: {gj_per_tonne(min_separation_work(x, 0.9, 0.999 if x > 0.9 else 0.99)):.3f} GJ/t")
for p in (60, 90, 120):
    print(f"  isothermal compression floor 1 -> {p} bar: {comp_floor(p):.3f} GJ/t")
print("  No step of the idea claims energy below these floors (claimed 0.23-0.26 compression, 0.11 cement separation): OK")

# ---------------------------------------------------------------- 2. mass ratio
print("\n=== 2. CO2/CH4 mass ratio in the same pore volume at minimum seasonal pressure [CP]")
print("  (idea claims 3.2 at 40 bar/40C to 4.5 at 100 bar/60C, PR EOS)")
grid = [(40, 40), (40, 60), (60, 50), (80, 50), (80, 70), (100, 60), (100, 40), (120, 70)]
ratios = {}
for P, T in grid:
    rc, rm = rho('CO2', T, P), rho('CH4', T, P)
    ratios[(P, T)] = rc / rm
    print(f"  Pmin {P:3d} bar {T}C: rho CO2 {rc:6.1f}, CH4 {rm:5.1f} kg/m3, ratio {rc/rm:4.2f} -> {rm/rc:.3f} t CH4 freed/t CO2 "
          f"= {rm/rc*CH4_HHV:5.1f} GJ HHV")
print("  NB ratio rises steeply near the CO2 critical point (31C, 73.8 bar): shallow/cool fields at Pmin>~80 bar give 5-10x.")

# ---------------------------------------------------------------- 3. working-gas gain (segregated, no mixing)
print("\n=== 3. Extra working gas from CO2 compressibility (ideal segregated cushion, no mixing) [CP]")
for Pmin, Pmax, T in [(40, 90, 50), (60, 130, 60), (80, 180, 70), (50, 110, 45)]:
    rmin, rmax = rho('CH4', T, Pmin), rho('CH4', T, Pmax)
    cmin, cmax = rho('CO2', T, Pmin), rho('CO2', T, Pmax)
    # pore volume 1; gas-filled at Pmin; native case: cushion = all gas at Pmin
    wg0 = rmax - rmin
    out = []
    for f in (0.3, 0.5):
        vco2_max = f * cmin / cmax
        wg = rmax * (1 - vco2_max) - rmin * (1 - f)
        out.append(f"swap {f:.0%}: working gas +{wg/wg0-1:5.1%}, CO2 {f*cmin:5.1f} kg/m3 pore, CH4 freed {f*rmin:4.1f} kg/m3")
    print(f"  {Pmin}->{Pmax} bar {T}C: " + "; ".join(out))
print("  (Oldenburg 2003 [M, one simulation]: ~30% more CH4 storable; Mirzaei-Paiaman 2026 [M, volumetric, 384 US sites]: avg +28% at full replacement)")

# ---------------------------------------------------------------- 4. mixing / gravity stability (order of magnitude)
print("\n=== 4. Mixing-zone indicators (order of magnitude only; the falsifying simulation is the real test)")
D_eff = 1e-8  # m2/s, CO2-CH4 gas diffusion at 50-100 bar ~1e-7, x tortuosity/porosity ~0.1 [A]
for yrs in (1, 10):
    print(f"  diffusion length after {yrs} yr: {math.sqrt(D_eff*yrs*3.156e7):.1f} m (negligible)")
for alpha, L in [(1, 100), (5, 200), (10, 300)]:
    print(f"  cyclic dispersion, dispersivity {alpha} m, front travel {L} m/half-cycle, 20 half-cycles: zone ~{math.sqrt(2*alpha*L*20):.0f} m")
# Dietz critical Darcy velocity for gravity-stable displacement of CO2 by injected CH4 (unfavourable viscosity ratio)
for k_md, sin_th, (P, T) in [(100, 0.05, (60, 50)), (300, 0.10, (60, 50)), (500, 0.17, (100, 60))]:
    drho = rho('CO2', T, P) - rho('CH4', T, P)
    dmu = mu('CO2', T, P) - mu('CH4', T, P)
    uc = k_md * 9.869e-16 * drho * 9.81 * sin_th / dmu
    print(f"  k {k_md} mD, dip sin {sin_th}, {P} bar {T}C: drho {drho:4.0f} kg/m3, mu CO2/CH4 {mu('CO2',T,P)/mu('CH4',T,P):.2f}, "
          f"critical Darcy velocity {uc*3.156e7:6.1f} m/yr")
u_front = 200 / 0.5 * 0.2 * 0.7  # 200 m front travel in 6 months x porosity 0.2 x dS 0.7 [A]
print(f"  typical far-field seasonal Darcy velocity ~{u_front:.0f} m/yr (higher near wells) -> stability is marginal in tight/flat fields, OK in steep/high-k fields")

# ---------------------------------------------------------------- 5. energy per tonne
print("\n=== 5. Energy per tonne CO2 stored (storage-side, CO2 delivered at ~1 bar from source)")
E = {"low": 0.30, "base": 0.40, "high": 0.55}
# low: pure fermentation CO2, 1->~70 bar, multistage intercooled (~83 kWh/t); base: ~110 kWh/t to 90-120 bar incl. dehydration;
# high: ~150 kWh/t incl. booster + losses. Real compressors ~0.1 MWh/t to 110-150 bar is the commonly used planning figure [M].
fl = comp_floor(90)
for k, v in E.items():
    print(f"  {k}: {v:.2f} GJ/t ({v/0.0036:.0f} kWh/t); second-law eff vs 1->90 bar floor {second_law_efficiency(v, fl):.0%}")
print(f"  + cement capture if source is a kiln (not part of this idea): ~2.5-3.7 GJ heat/t for amine [M]; floor {gj_per_tonne(min_separation_work(0.25,0.9)):.2f}")
for (P, T) in [(40, 40), (100, 60), (100, 40)]:
    r = ratios[(P, T)]
    print(f"  freed-gas energy at {P} bar {T}C: {CH4_HHV/r:4.1f} GJ/t CO2 = {CH4_HHV/r/E['base']:.0f}x base compression energy")

# ---------------------------------------------------------------- 6. per-site capacity (the sink is small and one-off)
print("\n=== 6. Per-site one-off capacity")
us_total_base_bcf = 9319.291 - 4793.009   # EIA 2024 design capacity [S, from idea; consistent with 2026 study 'nearly half cushion' of ~9.2 Tscf]
us_dep_base_bcf = 7226.586 - 3910.866
print(f"  US base gas {us_total_base_bcf:,.0f} Bcf ({us_total_base_bcf*BCF_TO_BCM:.0f} bcm); depleted fields {us_dep_base_bcf:,.0f} Bcf "
      f"({us_dep_base_bcf*BCF_TO_BCM*KG_PER_M3_NG:.0f} Mt CH4)")
print(f"  Mirzaei-Paiaman 2026 [M]: full replacement ~330 Mt CO2 over 384 sites = {330/384:.2f} Mt/site average (range 0.002-19 Mt);"
      f" 20% replacement 67 Mt and 0.9 Tscf freed -> implied mass ratio {67/(900*BCF_TO_BCM*KG_PER_M3_NG):.2f}")
for swap in (0.3, 0.5):
    print(f"   -> {swap:.0%} swap of the average US site: {330/384*swap:.2f} Mt CO2; over 10 yr = {330/384*swap/10*1000:.0f} kt/yr")
eu_dep_working = (103 * 0.55, 103 * 0.70)   # [A] depleted fields ~55-70% of ~103 bcm EU working gas (rest caverns/aquifers); unverified
eu_sites_dep = (50, 70)                      # [A] number of EU depleted-field UGS sites
for wg, n in zip(eu_dep_working, eu_sites_dep):
    for cw in (0.6, 1.0):
        ch4_mt = wg * cw * KG_PER_M3_NG
        lo, hi = ch4_mt * 0.3 * 3.2, ch4_mt * 0.5 * 4.5
        print(f"  EU depleted working {wg:.0f} bcm, cushion/working {cw}: CO2 one-off {lo:.0f}-{hi:.0f} Mt; per site ({n} sites) {lo/n:.1f}-{hi/n:.1f} Mt")
print("  Typical cement plant: 0.5-1.0 Mt CO2/yr for 25+ yr [A]; one average site absorbs ~1-3 years of one plant.")

# idea's own inventory numbers re-run with the idea's own ratio range (3.2-4.5) instead of 3.0-5.5
us_ch4 = us_dep_base_bcf * BCF_TO_BCM * KG_PER_M3_NG
print(f"  Idea US 61-186 Mt used ratio 3.0-5.5; with its own 3.2-4.5: {us_ch4*0.3*3.2:.0f}-{us_ch4*0.5*4.5:.0f} Mt")
eu_ch4_lo, eu_ch4_hi = 103 * 0.6 * KG_PER_M3_NG, 103 * 1.0 * KG_PER_M3_NG
print(f"  Idea EU 40-204 Mt (all storage types); with 3.2-4.5 and depleted-only 55-70%: "
      f"{eu_ch4_lo*0.55*0.3*3.2:.0f}-{eu_ch4_hi*0.70*0.5*4.5:.0f} Mt")

# ---------------------------------------------------------------- 7. cost per tonne (storage side)
print("\n=== 7. Storage-side cost per tonne CO2 stored, from source fence (capture excluded)")
r = 0.08
cases = {
    #        site Mt, fill yr, pipe km, $M/km, new wells, $M/well, fixed $M (permit, baseline MMV, well CO2-proofing), var MMV $/t, compressor $M, GJ/t, $/MWh
    "low":  dict(M=8.0, yrs=10, km=30,  pkm=1.0, nw=2, cw=8,  fix=10, mmv=1, comp=25, gj=0.30, pe=60),
    "base": dict(M=3.0, yrs=10, km=75,  pkm=1.5, nw=3, cw=12, fix=20, mmv=2, comp=20, gj=0.40, pe=90),
    "high": dict(M=1.0, yrs=10, km=100, pkm=2.0, nw=2, cw=15, fix=20, mmv=3, comp=12, gj=0.55, pe=130),
}
# Justification [A]: onshore European CO2 pipeline $1-2.5M/km for 8-16 in (ZEP/IEAGHG-type planning ranges, modelled);
# flank injectors must be NEW (existing UGS wells sit on the crest and are not CO2-rated): onshore 1.5-3 km wells $8-15M;
# capex amortised over the FILL period because the sink is one-off; O&M 3%/yr of capex.
cost = {}
for k, c in cases.items():
    rate = c["M"] / c["yrs"]
    capex = c["km"] * c["pkm"] + c["nw"] * c["cw"] + c["fix"] + c["comp"]
    ann = capex * crf(r, c["yrs"]) + 0.03 * capex
    energy = c["gj"] / 3.6 * c["pe"]
    tot = ann / rate + energy + c["mmv"]
    cost[k] = tot
    print(f"  {k}: site {c['M']} Mt at {rate:.2f} Mt/yr, capex ${capex:.0f}M (pipe {c['km']*c['pkm']:.0f}, wells {c['nw']*c['cw']}, fixed {c['fix']}, comp {c['comp']}) "
          f"-> capital+O&M ${ann/rate:5.1f}/t + energy ${energy:4.1f}/t + MMV ${c['mmv']}/t = ${tot:5.1f}/t")
# shared cluster trunk: base site but pipeline shared by 4 sites / two-phase hub
c = cases["base"]; capex = c["km"] * c["pkm"] / 4 + c["nw"] * c["cw"] + c["fix"] + c["comp"]
print(f"  base with pipeline shared 4 ways: ${(capex*(crf(r,10)+0.03))/0.3 + c['gj']/3.6*c['pe'] + c['mmv']:.1f}/t")
print("  Claim '<$30/t incremental' holds only for large sites (>~5 Mt) within ~30 km of the source.")

# ---------------------------------------------------------------- 8. climate accounting variants
print("\n=== 8. Net CO2e per gross tonne stored, and cost per NET tonne")
grid_int = 0.30          # t CO2/MWh grid electricity for compression [A, EU 2025-26 average ~0.25-0.35]
leak = 0.01              # fraction of freed CH4 leaked downstream [A]
for (P, T) in [(40, 40), (100, 60)]:
    ch4 = 1 / ratios[(P, T)]
    comp_em = E["base"] / 3.6 * grid_int
    burn = ch4 * CO2_PER_CH4
    leak_e = ch4 * leak * GWP100["CH4_fossil"]
    reserve = 1 - comp_em
    sale_add = 1 - comp_em - burn - leak_e
    print(f"  {P} bar {T}C: freed {ch4:.3f} t CH4/t CO2; burn {burn:.2f}, leak {leak_e:.3f}, compression {comp_em:.3f} t CO2e")
    for lam in (1.0, 0.5, 0.0):
        net = 1 - comp_em - lam * (burn + leak_e)
        print(f"     sale, market leakage {lam:.0%} (share of freed gas that adds to consumption): net {net:.2f} t/t gross")
    for label, price in [("US $3.5/MMBtu", 3.5), ("EU $11/MMBtu", 11.0)]:
        credit = ch4 * CH4_HHV * MMBTU_PER_GJ * price * 0.85   # 15% for production, processing, royalty/tax [A]
        for k in ("low", "base", "high"):
            pass
        print(f"     {label}: net gas credit ${credit:5.1f}/t gross; cost/net t (base site): "
              f"reserve ${cost['base']/reserve:6.1f}; sale+100% leakage ${(cost['base']-credit)/sale_add:7.1f}; "
              f"sale+50% leakage ${(cost['base']-credit)/(1-comp_em-0.5*(burn+leak_e)):7.1f}")
print("  Reserve variant: low/base/high cost per net t = " +
      ", ".join(f"${cost[k]/(1-E[k]/3.6*grid_int):.0f}" for k in ("low", "base", "high")))

# ---------------------------------------------------------------- 9. scale and resources
print("\n=== 9. Scale and resources")
glob_working = 425  # bcm, global UGS working capacity ~2023 [A, IGU/Cedigaz order of magnitude]
dep_share = 0.75    # [A] depleted fields share of global working capacity
for cw, swap, ratio in [(0.6, 0.3, 3.2), (1.0, 0.5, 4.5)]:
    mt = glob_working * dep_share * cw * KG_PER_M3_NG * swap * ratio
    print(f"  global one-off (cushion/working {cw}, swap {swap:.0%}, ratio {ratio}): {mt:.0f} Mt CO2 -> over 10-20 yr {mt/20/1000:.3f}-{mt/10/1000:.3f} Gt/yr")
for gt in (0.005, 0.02, 0.05):
    s = ScaleCheck(gt, E["base"])
    print(f"  {gt} Gt/yr at {E['base']} GJ/t: {s.ej_per_year*1000:.1f} PJ/yr = {s.share_of_world_primary_energy:.4%} of world primary, "
          f"{s.share_of_world_electricity_if_electric:.4%} of world electricity; = {gt/FOSSIL_CO2_GT:.2%} of fossil CO2")
eu_cement_process = 65  # Mt/yr EU process CO2 from clinker [A, ~2/3 of ~100 Mt EU ETS cement]
print(f"  EU swap 4-20 Mt/yr (idea) vs EU cement process CO2 ~{eu_cement_process} Mt/yr: {4/eu_cement_process:.0%}-{20/eu_cement_process:.0%}; "
      f"vs NZIA 50 Mt/yr injection target: {4/50:.0%}-{20/50:.0%}")
steel_t_km = 200  # t steel per km for ~12-16 in line [A]
print(f"  materials: base site pipeline 75 km x {steel_t_km} t/km = {75*steel_t_km/1000:.0f} kt steel for 3 Mt stored "
      f"({75*steel_t_km/3e6*1000:.1f} kg steel/t CO2); land: pipeline easement only; water: none beyond dehydration knock-out")
