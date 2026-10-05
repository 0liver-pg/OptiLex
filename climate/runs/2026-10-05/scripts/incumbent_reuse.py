"""Incumbent-asset-reuse idea checks (oil-major generator). Run from repo root with .venv/bin/python.

All numbers labelled: [V] verifier, [A] assumption, [S] source value quoted in notes.
"""
import math, sys
sys.path.insert(0, 'climate')
from physics import *  # noqa

Rb = 83.14462618  # cm3 bar / (mol K)

# ---------------- Peng-Robinson EOS (density, fugacity) ----------------
COMP = {"CO2": (304.13, 73.773, 0.2239, 44.01), "CH4": (190.564, 45.992, 0.01142, 16.043)}

def pr(comp, T, Pbar):
    Tc, Pc, w, M = COMP[comp]
    k = 0.37464 + 1.54226 * w - 0.26992 * w * w
    alpha = (1 + k * (1 - math.sqrt(T / Tc))) ** 2
    a = 0.45724 * (Rb * Tc) ** 2 / Pc * alpha
    b = 0.07780 * Rb * Tc / Pc
    A = a * Pbar / (Rb * T) ** 2
    B = b * Pbar / (Rb * T)
    # Z^3 - (1-B) Z^2 + (A - 3B^2 - 2B) Z - (AB - B^2 - B^3) = 0
    import numpy as np
    roots = np.roots([1, -(1 - B), A - 3 * B * B - 2 * B, -(A * B - B * B - B ** 3)])
    real = sorted(r.real for r in roots if abs(r.imag) < 1e-9 and r.real > B)
    best = None
    for Z in real:  # choose min Gibbs root
        lnphi = Z - 1 - math.log(Z - B) - A / (2 * math.sqrt(2) * B) * math.log((Z + (1 + math.sqrt(2)) * B) / (Z + (1 - math.sqrt(2)) * B))
        if best is None or lnphi < best[1]:
            best = (Z, lnphi)
    Z, lnphi = best
    rho = Pbar * 1e5 * M / 1000 / (Z * 8.314462618 * T)  # kg/m3
    return rho, math.exp(lnphi)

print("=== PR EOS sanity (NIST refs from memory: CO2 50C/100bar ~384, 50C/150bar ~700; CH4 50C/100bar ~65 kg/m3)")
for comp, T, P in [("CO2", 323.15, 100), ("CO2", 323.15, 150), ("CH4", 323.15, 100), ("CO2", 393.15, 300)]:
    r, phi = pr(comp, T, P)
    print(f"  {comp} {T-273.15:.0f}C {P} bar: rho {r:6.1f} kg/m3, phi {phi:.3f}")

# compression floors [V-style ideal isothermal]
def comp_floor_gj_t(p_bar, T=T0):
    return R * T * math.log(p_bar / 1.01325) / M_CO2 / 1e6
print("\n=== Isothermal compression floors (ideal gas, GJ/t CO2)")
for p in (30, 35, 60, 100, 150):
    print(f"  1 -> {p} bar: {comp_floor_gj_t(p):.3f}")

sep = {k: gj_per_tonne(min_separation_work(x, 0.9)) for k, x in
       [("AGRU off-gas 95%", None), ("cement 25%", 0.25), ("coal 12%", 0.12), ("NGCC 4%", 0.04)] if x}
print("  separation floors 90% capture:", {k: round(v, 3) for k, v in sep.items()})

# ---------------- IDEA 1: CO2 cushion-gas swap in underground gas storage ----------------
print("\n=== IDEA 1: CO2 cushion gas swap")
CH4_HHV_GJ_T = 55.5      # GJ/t (HHV) [S standard]
MMBTU_PER_GJ = 0.9478
for Pmin, Tc_ in [(40, 40), (60, 50), (80, 50), (100, 60)]:
    T = Tc_ + 273.15
    rc, _ = pr("CO2", T, Pmin)
    rm, _ = pr("CH4", T, Pmin)
    ratio = rc / rm
    ch4_per_tco2 = 1 / ratio
    gj = ch4_per_tco2 * CH4_HHV_GJ_T
    print(f"  Pmin {Pmin} bar, {Tc_}C: rhoCO2 {rc:5.0f}, rhoCH4 {rm:4.0f} kg/m3, mass ratio {ratio:4.2f} -> "
          f"{ch4_per_tco2:.3f} t CH4 freed/t CO2 = {gj:5.1f} GJ HHV; value @$3.5 ${gj*MMBTU_PER_GJ*3.5:5.1f}, "
          f"@$11 ${gj*MMBTU_PER_GJ*11:5.1f} per t CO2; energy ratio vs 1->{Pmin+20}bar comp floor x{gj/comp_floor_gj_t(Pmin+20):.0f}")

# Inventory: US EIA 2024 design capacity [S]: total 9,319,291 MMcf; working 4,793,009 MMcf
us_base_bcf = 9319.291 - 4793.009
us_dep_base_bcf = 7226.586 - 3910.866
BCF_TO_BCM = 0.0283168
KG_PER_M3_NG = 0.72  # pipeline gas at ~15C, 1 atm [A]
def bcf_to_mt(b): return b * BCF_TO_BCM * 1e9 * KG_PER_M3_NG / 1e9
print(f"  US base gas {us_base_bcf:,.0f} Bcf = {us_base_bcf*BCF_TO_BCM:.0f} bcm = {bcf_to_mt(us_base_bcf):.0f} Mt; "
      f"depleted fields {us_dep_base_bcf:,.0f} Bcf = {us_dep_base_bcf*BCF_TO_BCM:.0f} bcm = {bcf_to_mt(us_dep_base_bcf):.0f} Mt")
eu_working_bcm = 103  # [A] ~ GIE AGSI EU working gas capacity ~100-105 bcm
for label, cush_bcm in [("US depleted fields", us_dep_base_bcf * BCF_TO_BCM), ("EU (cushion/working 0.6-1.0)", None)]:
    rng = [cush_bcm] if cush_bcm else [0.6 * eu_working_bcm, 1.0 * eu_working_bcm]
    for c in rng:
        for swap in (0.3, 0.5):
            for ratio in (3.0, 5.5):
                ch4_mt = c * KG_PER_M3_NG * swap
                print(f"   {label}: cushion {c:5.0f} bcm, swap {swap:.0%}, mass ratio {ratio}: freed {c*swap:4.0f} bcm "
                      f"({ch4_mt:4.0f} Mt CH4), CO2 stored {ch4_mt*ratio:5.0f} Mt one-off")
# EU freed gas value
for bcm in (18, 52):
    twh = bcm * 10.55
    print(f"   EU freed {bcm} bcm = {twh:,.0f} TWh -> EUR {twh*35/1e3:,.1f} bn at EUR35/MWh; share of ~330 bcm EU demand {bcm/330:.0%}")

# ---------------- IDEA 2: Enhanced lithium recovery (CO2 voidage replacement of Li brine) ----------------
print("\n=== IDEA 2: CO2 as voidage-replacement fluid for Smackover lithium brine")
for T_C, P in [(110, 280), (125, 320)]:
    rc, _ = pr("CO2", T_C + 273.15, P)
    print(f"  CO2 at {T_C}C, {P} bar: {rc:.0f} kg/m3 (PR underestimates dense CO2 ~5-10%) -> {1000/rc:.2f} m3 brine displaced per t CO2")
for li_mgL in (200, 400, 550):
    for rho in (600, 750):
        brine_m3 = 1000 / rho
        li_kg = brine_m3 * li_mgL / 1000 * 0.90   # 90% DLE recovery [A]
        lce = li_kg * 5.323
        out = []
        for price in (10_000, 20_000):
            out.append(f"${lce*price/1000:5.1f}")
        net = [f"${lce*(price-cost)/1000:5.1f}" for price, cost in ((10_000, 7_000), (20_000, 7_000))]
        print(f"  Li {li_mgL} mg/L, rhoCO2 {rho}: {brine_m3:.2f} m3/t, {lce:.2f} kg LCE per t CO2; gross {out} at $10k/$20k; "
              f"net of $7k/t all-in DLE cost {net}")
# plant-scale: 22,500 tpa LCE at 450 mg/L, 90%
brine = 22_500e3 / (0.450 * 0.9 * 5.323)  # m3/yr
print(f"  22.5 ktpa LCE plant at 450 mg/L: brine {brine/1e6:.1f} Mm3/yr ({brine/365/0.159:,.0f} bbl/d); "
      f"full voidage replacement by CO2 at 600-750 kg/m3 = {brine*0.6/1e6:.1f}-{brine*0.75/1e6:.1f} Mt CO2/yr")
lift = [1200 * 9.81 * h / 0.5 / 1e6 for h in (1000, 2500)]  # MJ/m3, 50% pump eff [A]
print(f"  brine lift work {lift[0]:.0f}-{lift[1]:.0f} MJ/m3 -> {lift[0]*1.33/1000:.3f}-{lift[1]*1.67/1000:.3f} GJ/t CO2; "
      f"compression floor 1->150 bar {comp_floor_gj_t(150):.2f} GJ/t")

# ---------------- IDEA 3: dissolved-CO2 co-injection in produced-water disposal ----------------
print("\n=== IDEA 3: dissolve CO2 into produced water already going down SWD wells")
def logK(tC):  # Spycher et al. 2003, CO2(g) <-> CO2(aq), valid 12-100C, bar per mol fraction*55.508
    return 1.189 + 1.304e-2 * tC - 5.446e-5 * tC * tC
def sol_pure(tC, P):
    T = tC + 273.15
    _, phi = pr("CO2", T, P)
    K = 10 ** logK(tC)
    poy = math.exp((P - 1) * 32.6 / (Rb * T))
    x = phi * P / (55.508 * K * poy)
    return 55.508 * x / (1 - x)
for tC, P in [(25, 50), (50, 100)]:
    print(f"  pure water {tC}C {P} bar: {sol_pure(tC, P):.2f} mol/kg (lit ~1.25 @25C/50bar, ~1.05-1.1 @50C/100bar)")
ks = (0.10, 0.12)  # Sechenov log10 coefficient, kg/mol [A]
for tC, P in [(30, 35), (40, 60), (45, 100)]:
    m0 = sol_pure(tC, P)
    for mNaCl in (1.5, 4.0):
        vals = [m0 * 10 ** (-k * mNaCl) * 44.01 for k in ks]
        print(f"  {tC}C {P} bar, {mNaCl} m NaCl: saturation {min(vals):.0f}-{max(vals):.0f} kg CO2/t water")
design_kg_m3 = (15, 30)  # design loading incl. undersaturation margin [A]
for mmbbl_d in (12, 20):
    m3_yr = mmbbl_d * 1e6 * 0.159 * 365
    print(f"  Permian SWD {mmbbl_d} MMbbl/d = {m3_yr/1e9:.2f} km3/yr -> {m3_yr*design_kg_m3[0]/1e9:.0f}-{m3_yr*design_kg_m3[1]/1e9:.0f} Mt CO2/yr at {design_kg_m3} kg/m3")
# Permian AGRU vented CO2 rough
for bcfd, xco2 in [(27, 0.015), (27, 0.03)]:
    co2_mt = bcfd * xco2 * 28.3168e6 * 1.87 * 365 / 1e9
    print(f"  Permian raw gas {bcfd} Bcf/d at {xco2:.1%} CO2 -> {co2_mt:.1f} Mt CO2/yr removed at processing plants")
print(f"  compression floor to 35 bar (in-well dissolution, Carbfix-style) {comp_floor_gj_t(35):.2f} vs supercritical 150 bar {comp_floor_gj_t(150):.2f} GJ/t")
# velocity check in tubing
q = 20_000 * 0.159 / 86400; A = math.pi * (0.0889 / 2) ** 2
print(f"  downward water velocity, 20k bbl/d in 3.5in ID tubing: {q/A:.1f} m/s (bubble rise ~0.2-0.3 m/s)")
# volume added by dissolved CO2: partial molar volume ~ 35 cm3/mol
print(f"  added volume per t CO2 dissolved: {1e6/44.01*35e-6:.2f} m3 vs {1000/30:.0f}-{1000/15:.0f} m3 brine carrier")

# ---------------- IDEA 4: measure-first buy-and-plug of marginal wells ----------------
print("\n=== IDEA 4: measure-first buy-and-plug of high-emitting low-production well sites")
sites = 565_000; tg = 4.0  # Omara 2022 [S]
print(f"  mean per site {tg*1e6/sites:.1f} t CH4/yr = {tg*1e9/sites/8760:.2f} kg/h (paper: 0.8 kg/h)")
us_boed = 29e6  # [A] ~2019 US O&G ~29 Mboe/d
print(f"  mean production per site {0.056*us_boed/sites:.1f} boe/d (5.6% share)")
for E in (0.8, 2.0, 5.0):
    t_ch4_yr = E * 8.76
    for L in (10, 20):
        for C in (75_000, 200_000):
            tco2e = t_ch4_yr * L * GWP100['CH4_fossil']
            print(f"  E {E} kg/h, {L} yr avoided, cost ${C/1e3:.0f}k: {tco2e:6,.0f} t CO2e -> ${C/tco2e:5.1f}/t (GWP100), ${C/(t_ch4_yr*L*GWP20['CH4_fossil']):4.1f}/t GWP20")
# lost gas value of plugged emitters: ~2.9 boe/d
# heavy tail assumption: top 10% of sites emit 50% -> 2 Tg from 56,500 sites
top = 0.5 * tg * 1e6 / (0.1 * sites)
print(f"  if top 10% of sites emit 50%: {top:.0f} t CH4/yr per site = {top/8.76:.1f} kg/h; program 56.5k sites x $150k = ${56500*150e3/1e9:.1f} bn"
      f" for {0.5*tg:.0f} Tg/yr = {0.5*tg*GWP100['CH4_fossil']:.0f} Mt CO2e/yr (GWP100)")

# ---------------- IDEA 5: store vented reservoir CO2 at existing LNG trains ----------------
print("\n=== IDEA 5: reservoir CO2 from LNG feed gas")
LNG_MT = 411  # IGU 2024 [S, from memory]
for x in (0.02, 0.04, 0.06, 0.10, 0.14):
    co2_t_per_t = (1000 / 16.043) * x / (1 - x) * 44.01 / 1000
    print(f"  feed {x:.0%} CO2: {co2_t_per_t*1000:4.0f} kg CO2/t LNG; global at this avg {LNG_MT*co2_t_per_t:5.0f} Mt/yr; "
          f"cost at $25-45/t = ${co2_t_per_t*25/51.5:.2f}-{co2_t_per_t*45/51.5:.2f}/MMBtu; share of ~3.4 t CO2e/t LNG lifecycle {co2_t_per_t/3.4:.0%}")
print(f"  energy: dehydrate+compress to 150 bar floor {comp_floor_gj_t(150):.2f} GJ/t, separation ~0 (already done for spec)")

# ---------------- IDEA 6: throughput royalty to CO2-pipeline landowners ----------------
print("\n=== IDEA 6: per-tonne throughput royalty to pipeline landowners")
mtpa, miles = 18, 2500   # Summit design [S, from memory/map]
acres_per_mile = 50 * 5280 / 43560  # 50 ft permanent easement [A]
for roy in (1, 2, 3):
    per_mile = mtpa * 1e6 * roy / miles
    print(f"  ${roy}/t x {mtpa} Mt/yr = ${mtpa*roy}M/yr; ${per_mile:,.0f}/mile/yr; ${per_mile/acres_per_mile:,.0f}/easement-acre/yr "
          f"(Iowa cash rent ~$250/acre [A]); {roy/85:.1%} of 45Q $85")
eth_cap = 45e6  # US fermentation CO2 ceiling (map)
print(f"  full US ethanol pool {eth_cap/1e6:.0f} Mt/yr at $2/t = ${eth_cap*2/1e6:.0f}M/yr; 45Q value ${eth_cap*85/1e9:.1f}bn/yr")
print(f"  ethanol CO2 energy: separation ~0, compression floor 1->150 bar {comp_floor_gj_t(150):.2f} GJ/t")

# ---------------- scale checks ----------------
print("\n=== Scale checks (ScaleCheck from verifier)")
for name, gt, gj in [("Idea3 Permian 25 Mt/yr at 0.25 GJ/t", 0.025, 0.25), ("Idea5 50 Mt/yr at 0.4 GJ/t", 0.05, 0.4)]:
    s = ScaleCheck(gt, gj)
    print(f"  {name}: {s.ej_per_year*1000:.1f} PJ/yr, {s.share_of_world_primary_energy:.4%} of primary energy")
