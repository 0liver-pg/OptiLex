"""Verifier for idea incumbent_assets_3: dissolve gas-plant (AGRU) CO2 into Permian
produced water going down saltwater-disposal (SWD) wells, Carbfix-style.

Checks: separation floor, compression floor (real gas), CO2 solubility in brine
(Spycher et al. 2003 + Sechenov salting-out), tubing hydraulics, water needed per
tonne, pore-volume added per tonne, Permian and global scale, energy share, and a
low/base/high techno-economic model versus a simple baseline (dedicated free-phase
injection well, the way Permian acid-gas-injection (AGI) / Class VI wells work).
"""
import math
import sys

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

RB = 83.1447  # bar cm3 / (mol K)
BBL = 0.158987  # m3
YR = 365.0

# ---------------------------------------------------------------- 1. separation floor
print("=" * 78)
print("1. SEPARATION FLOOR (AGRU off-gas is already >95% CO2)")
w = min_separation_work(0.96, 0.99, 0.999)
print(f"   Upgrading 96% CO2 -> 99.9%, 99% recovery: {w/1e3:.3f} kJ/mol = {gj_per_tonne(w):.4f} GJ/t")
print(f"   (vs DAC floor {gj_per_tonne(min_separation_work(420e-6, 0.75)):.3f} GJ/t). "
      "Separation energy is already spent in the AGRU; marginal ~0.")
print("   NOTE: no step in the idea is claimed below a floor; the floor that binds is compression.")


# ---------------------------------------------------------------- 2. RK fugacity, compression floor
def rk_pure_co2(P_bar, T_K):
    """Redlich-Kwong (Spycher et al. 2003 parameters) for pure CO2: returns (Z, phi) of stable root."""
    a = 7.54e7 - 4.13e4 * T_K
    b = 27.80
    A = a * P_bar / (RB ** 2 * T_K ** 2.5)
    B = b * P_bar / (RB * T_K)
    # Z^3 - Z^2 + (A - B - B^2) Z - A B = 0  -> solve numerically
    coeffs = [1.0, -1.0, A - B - B * B, -A * B]
    roots = _cubic_real_roots(*coeffs)
    best = None
    for Z in roots:
        if Z <= B:
            continue
        lnphi = Z - 1 - math.log(Z - B) - (A / B) * math.log(1 + B / Z)
        if best is None or lnphi < best[1]:
            best = (Z, lnphi)
    return best[0], math.exp(best[1])


def _cubic_real_roots(a, b, c, d):
    # Cardano / trigonometric for real roots
    b, c, d = b / a, c / a, d / a
    p = c - b * b / 3
    q = 2 * b ** 3 / 27 - b * c / 3 + d
    disc = (q / 2) ** 2 + (p / 3) ** 3
    if disc > 0:
        u = -q / 2 + math.sqrt(disc)
        v = -q / 2 - math.sqrt(disc)
        t = math.copysign(abs(u) ** (1 / 3), u) + math.copysign(abs(v) ** (1 / 3), v)
        return [t - b / 3]
    r = math.sqrt(-p / 3)
    phi = math.acos(max(-1, min(1, -q / (2 * r ** 3))))
    return [2 * r * math.cos((phi - 2 * math.pi * k) / 3) - b / 3 for k in range(3)]


def co2_density(P_bar, T_K):
    Z, _ = rk_pure_co2(P_bar, T_K)
    return P_bar * 1e5 * M_CO2 / (Z * R * T_K)  # kg/m3


print("\n" + "=" * 78)
print("2. COMPRESSION FLOOR (isothermal reversible, real gas via RK fugacity; AGRU off-gas at ~1.5 bar)")
T_c = 308.15  # 35 C, above CO2 critical temp, so a single-phase path exists
P_in = 1.5
_, phi_in = rk_pure_co2(P_in, T_c)
comp_floor = {}
for P_out in (35, 60, 100, 150):
    _, phi_out = rk_pure_co2(P_out, T_c)
    w_real = R * T_c * math.log((phi_out * P_out) / (phi_in * P_in))
    w_ideal_from1 = R * T0 * math.log(P_out / 1.0)
    comp_floor[P_out] = gj_per_tonne(w_real)
    print(f"   1.5 -> {P_out:>3} bar: real-gas floor {gj_per_tonne(w_real):.3f} GJ/t "
          f"({gj_per_tonne(w_real)/0.0036:.0f} kWh/t); idea's ideal-gas-from-1-bar figure "
          f"{gj_per_tonne(w_ideal_from1):.3f} GJ/t; CO2 density {co2_density(P_out, T_c):.0f} kg/m3")
print("   Idea's floors (0.20 / 0.26 / 0.28 GJ/t) are ideal-gas from 1 bar: slightly HIGH (conservative), not below floor.")


# ---------------------------------------------------------------- 3. solubility
def logK(T_C):
    kco2 = 1.189 + 1.304e-2 * T_C - 5.446e-5 * T_C ** 2
    kh2o = -2.209 + 3.097e-2 * T_C - 1.098e-4 * T_C ** 2 + 2.048e-7 * T_C ** 3
    return 10 ** kco2, 10 ** kh2o


def co2_molality_pure_water(P_bar, T_C):
    """Spycher, Pruess & Ennis-King (2003) non-iterative form, pure-CO2 gas fugacity approx."""
    T_K = T_C + 273.15
    Kc, Kw = logK(T_C)
    _, phi_c = rk_pure_co2(P_bar, T_K)
    phi_w = 1.0  # approximation; y_H2O is < 1% here so effect on x_CO2 is small
    A = Kw / (phi_w * P_bar) * math.exp((P_bar - 1) * 18.1 / (RB * T_K))
    B = phi_c * P_bar / (55.508 * Kc) * math.exp(-(P_bar - 1) * 32.6 / (RB * T_K))
    y_w = (1 - B) / (1 / A - B)
    x = B * (1 - y_w)
    return 55.508 * x / (1 - x)


def co2_molality_brine(P_bar, T_C, m_nacl, ks):
    return co2_molality_pure_water(P_bar, T_C) * 10 ** (-ks * m_nacl)


def kg_co2_per_m3_brine(m_co2, m_nacl):
    rho_brine = 1000 + 37.0 * m_nacl       # kg/m3, NaCl brine approx at ~30C
    kg_water = rho_brine / (1 + 0.05844 * m_nacl)
    return m_co2 * 0.04401 * kg_water


print("\n" + "=" * 78)
print("3. CO2 SOLUBILITY (Spycher 2003 + RK; Sechenov ks 0.10-0.12 log10 kg/mol)")
checks = [(25, 50.7, 1.25, "~1.2-1.3 (Wiebe & Gaddy 1940 / Spycher 2003 compilation)"),
          (50, 101.3, 1.07, "~1.0-1.1 (Bamberger et al. 2000)"),
          (31, 35.0, None, "")]
for T_C, P, lit, src in checks:
    m = co2_molality_pure_water(P, T_C)
    print(f"   pure water {T_C}C {P} bar: {m:.3f} mol/kg" + (f"  vs literature {src}" if lit else ""))

cases = [("shallow release, 30C/35 bar", 30, 35), ("mid release, 40C/60 bar", 40, 60),
         ("deep release, 45C/100 bar", 45, 100)]
sat_table = {}
for label, T_C, P in cases:
    row = []
    for m_nacl in (1.5, 2.5, 4.0):
        for ks in (0.10, 0.12):
            mb = co2_molality_brine(P, T_C, m_nacl, ks)
            row.append(kg_co2_per_m3_brine(mb, m_nacl))
    sat_table[label] = (min(row), max(row))
    print(f"   {label}: saturation {min(row):.1f}-{max(row):.1f} kg CO2/m3 brine (1.5-4 molal NaCl)")

print("   Design loading at 75% of saturation and water needed per tonne:")
for label, (lo, hi) in sat_table.items():
    print(f"     {label}: {0.75*lo:.1f}-{0.75*hi:.1f} kg/m3 -> {1000/(0.75*hi):.0f}-{1000/(0.75*lo):.0f} m3 water per t CO2")
print("   Carbfix reference: ~25 t water per t CO2 (Matter et al. 2016; fresh water, ~25-30 bar release).")

# downstream: does pressure+temperature rise along the well keep it dissolved?
print("   Downstream check (loading = 75% sat at 30C/35 bar, 2.5 molal, ks 0.11):")
load = 0.75 * co2_molality_brine(35, 30, 2.5, 0.11)
for depth, T_C, P in [(1500, 55, 150), (3000, 80, 320), (4000, 100, 430)]:
    s = co2_molality_brine(P, T_C, 2.5, 0.11)
    print(f"     {depth} m (~{T_C}C, ~{P} bar): saturation {s:.2f} mol/kg vs loading {load:.2f} -> "
          f"{'stays dissolved' if s > load else 'EXSOLVES'}")
print("   Upward-migration check (same loading) if brine leaks to shallower depth:")
for depth, T_C, P in [(250, 25, 27), (150, 22, 16), (50, 20, 6)]:
    s = co2_molality_brine(P, T_C, 2.5, 0.11)
    print(f"     {depth} m (~{T_C}C, ~{P} bar): saturation {s:.2f} vs loading {load:.2f} -> "
          f"{'stays dissolved' if s > load else 'EXSOLVES (degassing hazard)'}")

# pore volume added per tonne
v_dissolved = 1e6 / 44.01 * 33e-6  # partial molar volume ~33 cm3/mol
rho_sc = co2_density(250, 333.15)
print(f"\n   Added fluid volume per t CO2: dissolved {v_dissolved:.2f} m3 vs free-phase at 250 bar/60C "
      f"{1000/rho_sc:.2f} m3 (rho {rho_sc:.0f} kg/m3)")
print("   -> dissolved route adds ~half the pore volume per tonne of free-phase injection; "
      "but disposal-zone overpressure is driven by the water itself, which is unchanged.")

# ---------------------------------------------------------------- 4. tubing hydraulics
print("\n" + "=" * 78)
print("4. TUBING HYDRAULICS at 20,000 bbl/d (bubble slip ~0.2-0.35 m/s must be exceeded)")
q = 20000 * BBL / 86400
for name, d_in in [("3.5in (2.992in ID)", 2.992), ("4.5in (3.958in ID)", 3.958), ("5.5in (4.892in ID)", 4.892),
                   ("7in (6.276in ID)", 6.276)]:
    D = d_in * 0.0254
    v = q / (math.pi * D * D / 4)
    Re = 1100 * v * D / 1e-3
    f = 0.25 / (math.log10(4.6e-5 / D / 3.7 + 5.74 / Re ** 0.9)) ** 2  # Swamee-Jain, commercial steel
    dp = f * 3000 / D * 1100 * v * v / 2 / 1e5
    print(f"   {name}: v = {v:.2f} m/s, friction over 3,000 m = {dp:.0f} bar")
print("   -> idea's '6 m/s in 3.5in tubing at 20k bbl/d' implies ~hundreds of bar friction: real wells at that rate")
print("      use 4.5-7in tubing (1-3 m/s), which still beats bubble slip. Mechanism survives; that detail is wrong.")
for P_rel in (35, 60, 100):
    print(f"   release depth below the liquid level for {P_rel} bar (brine 1,100 kg/m3): "
          f"{P_rel*1e5/(1100*9.81):.0f} m  (many deep Permian SWDs take water on vacuum -> liquid level may be deep)")

# ---------------------------------------------------------------- 5. scale
print("\n" + "=" * 78)
print("5. SCALE")
# Source CO2: Permian gas ~27 Bcf/d (2025, EIA order of magnitude), CO2 content 1.5-3% (assumed)
mol_per_scf = 101325 * 0.0283168 / (R * 288.7)
for co2frac in (0.015, 0.02, 0.03):
    t = 27e9 * co2frac * mol_per_scf * M_CO2 / 1000 * YR / 1e6
    print(f"   Raw-gas CO2 at {co2frac:.1%} of 27 Bcf/d: {t:.1f} Mt/yr")
src = {}
for case, cf, rem, vent in [("low", 0.015, 0.5, 0.4), ("base", 0.02, 0.7, 0.6), ("high", 0.03, 0.9, 0.8)]:
    raw = 27e9 * cf * mol_per_scf * M_CO2 / 1000 * YR / 1e6
    src[case] = raw * rem * vent
    print(f"   {case}: removed by AGRU {rem:.0%} (only CO2 above pipeline/cryo spec is removed), "
          f"vented (not AGI/EOR) {vent:.0%} -> {src[case]:.1f} Mt/yr ventable AGRU CO2")

sink = {}
for case, bbl_d, deep_ok, util, load_kg in [("low", 12e6, 0.2, 0.6, 10), ("base", 16e6, 0.35, 0.75, 15),
                                            ("high", 20e6, 0.5, 0.85, 25)]:
    km3 = bbl_d * BBL * YR / 1e9
    sink[case] = km3 * 1e9 * deep_ok * util * load_kg / 1e9
    print(f"   {case}: disposal {bbl_d/1e6:.0f} MMbbl/d = {km3:.2f} km3/yr; eligible deep, contained, "
          f"outside seismic response areas {deep_ok:.0%}; uptime match {util:.0%}; {load_kg} kg/m3 "
          f"-> {sink[case]:.1f} Mt/yr capacity")
print("   (idea's unconstrained 7-29 Mt/yr assumes ALL disposal water qualifies)")
for case in ("low", "base", "high"):
    print(f"   Permian deliverable ({case}) = min(source, sink) = {min(src[case], sink[case]):.1f} Mt/yr")

# global: ~250 MMbbl/d produced water (commonly cited order of magnitude), 20-40% to disposal
for case, share, load_kg, colocate in [("low", 0.2, 10, 0.1), ("base", 0.3, 15, 0.25), ("high", 0.4, 25, 0.5)]:
    km3 = 250e6 * BBL * YR / 1e9 * share
    gt = km3 * 1e9 * load_kg * colocate / 1e12
    print(f"   Global ({case}): {km3:.1f} km3/yr disposal x {load_kg} kg/m3 x {colocate:.0%} co-located with "
          f"concentrated CO2 -> {gt*1000:.0f} Mt/yr = {gt:.3f} Gt/yr")

# ---------------------------------------------------------------- 6. energy
print("\n" + "=" * 78)
print("6. ENERGY PER TONNE (electric, compression + dehydration + CO2 booster)")
energy = {}
for case, P_out, eta, extra in [("low", 35, 0.75, 0.01), ("base", 60, 0.65, 0.02), ("high", 100, 0.55, 0.04)]:
    energy[case] = comp_floor[P_out] / eta + extra
    print(f"   {case}: floor to {P_out} bar {comp_floor[P_out]:.3f} / isothermal eff {eta} + aux {extra} "
          f"= {energy[case]:.3f} GJ/t ({energy[case]/0.0036:.0f} kWh/t)")
print("   Cross-check: NETL/IEAGHG compression to ~150 bar is ~0.3-0.45 GJ/t (~90-120 kWh/t) [order of magnitude].")
for case in ("low", "base", "high"):
    s = ScaleCheck(0.025, energy[case])
    print(f"   25 Mt/yr at {case}: {s.ej_per_year*1000:.1f} PJ/yr = {s.share_of_world_primary_energy:.5%} of "
          f"world primary energy")

# ---------------------------------------------------------------- 7. cost
print("\n" + "=" * 78)
print("7. COST PER TONNE CO2 (hub of 0.3 Mt/yr from one gas plant)")


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


Q = 0.3e6  # t/yr
P = {
    #            low      base     high
    "elec":     (40,      60,      90),     # $/MWh, West Texas/ERCOT industrial (assumption)
    "comp_kw":  (2000,    3000,    4500),   # $/kWe installed compression+dehy (small reciprocating)
    "trunk_km": (5,       10,      20),
    "trunk_m":  (0.6e6,   1.0e6,   1.5e6),  # $/km, 6-8in CO2 line
    "spur_km":  (1.5,     2.5,     4.0),    # per well
    "spur_m":   (0.25e6,  0.4e6,   0.7e6),  # $/km, 3-4in CRA/lined spur
    "bbl_well": (30000,   20000,   15000),  # bbl/d per SWD well
    "util":     (0.85,    0.75,    0.6),
    "load":     (25,      15,      10),     # kg CO2/m3 at 75% sat (from section 3)
    "retro":    (0.8e6,   2.0e6,   4.0e6),  # $/well: CRA tubing, dip-tube string, packer, wellhead, MIT/cement logs
    "mrv_cap":  (3e6,     10e6,    25e6),   # project permitting, AoR modelling, baseline, monitoring wells
    "mrv_opex": (0.3e6,   1.0e6,   2.5e6),  # $/yr monitoring + financial assurance
    "om_frac":  (0.025,   0.035,   0.05),
    "chem":     (0.5,     1.0,     3.0),    # $/t corrosion inhibitor etc
    "r":        (0.06,    0.08,    0.10),
    "n":        (25,      20,      12),     # 12 = 45Q credit period, conservative
}
cost = {}
for i, case in enumerate(("low", "base", "high")):
    g = {k: v[i] for k, v in P.items()}
    per_well = g["bbl_well"] * BBL * YR * g["util"] * g["load"] / 1000  # t/yr
    n_wells = math.ceil(Q / per_well)
    mw = Q * energy[case] * 1e9 / (YR * 86400) / 1e6 / 0.9  # 90% availability -> size up
    capex = {
        "compression": mw * 1000 * g["comp_kw"],
        "trunk": g["trunk_km"] * g["trunk_m"],
        "spurs": n_wells * g["spur_km"] * g["spur_m"],
        "wells": n_wells * g["retro"],
        "mrv": g["mrv_cap"],
    }
    tot = sum(capex.values())
    f = crf(g["r"], g["n"])
    ann = tot * f / Q
    elec = energy[case] / 3.6 * g["elec"]
    om = tot * g["om_frac"] / Q
    mrv = g["mrv_opex"] / Q
    cost[case] = ann + elec + om + mrv + g["chem"]
    print(f"   {case}: {per_well/1e3:.1f} kt/yr per well -> {n_wells} wells; compression {mw:.1f} MW")
    print("      capex $M: " + ", ".join(f"{k} {v/1e6:.1f}" for k, v in capex.items()) + f"; total {tot/1e6:.0f}")
    print(f"      $/t: capital {ann:.1f} (CRF {f:.3f}) + electricity {elec:.1f} + O&M {om:.1f} + MRV {mrv:.1f} "
          f"+ chemicals {g['chem']:.1f} = {cost[case]:.1f}")

print("\n   BASELINE: dedicated free-phase injection (AGI/Class VI style), same 0.3 Mt/yr, to 150 bar")
base_cost = {}
for i, case in enumerate(("low", "base", "high")):
    g = {k: v[i] for k, v in P.items()}
    e = comp_floor[150] / (0.75, 0.65, 0.55)[i] + 0.02
    n_wells = (1, 2, 3)[i]
    well_cost = (6e6, 12e6, 25e6)[i]  # new deep well incl. permitting; Permian deep well order of magnitude
    mw = Q * e * 1e9 / (YR * 86400) / 1e6 / 0.9
    capex = mw * 1000 * g["comp_kw"] + g["trunk_km"] * g["trunk_m"] + n_wells * well_cost + g["mrv_cap"]
    f = crf(g["r"], g["n"])
    c = capex * f / Q + e / 3.6 * g["elec"] + capex * g["om_frac"] / Q + g["mrv_opex"] / Q + g["chem"]
    base_cost[case] = c
    print(f"   {case}: {n_wells} new wells, {e:.2f} GJ/t, capex ${capex/1e6:.0f}M -> {c:.1f} $/t")

print("\n   SUMMARY $/t CO2: dissolved-in-SWD low/base/high = "
      + " / ".join(f"{cost[c]:.0f}" for c in ("low", "base", "high"))
      + "; dedicated-well baseline = " + " / ".join(f"{base_cost[c]:.0f}" for c in ("low", "base", "high")))
print("   45Q geologic storage: $85/t (statutory, 2025 law keeps $85 and gives EOR parity).")
print("   Idea's claim '<$35/t' holds only in the low case; base exceeds it.")
print("   Key driver: per-well CO2 throughput is capped by water flow (~10-60 kt/yr/well), so a 0.3 Mt/yr plant needs")
print("   many retrofitted wells, while one free-phase well can take 0.3-1 Mt/yr.")

print("\n" + "=" * 78)
print("8. FLAGS")
print("   physically_impossible: none (no step below a floor).")
print("   heroic assumptions: none for the physics; scale is small (Mt, not Gt).")
print("   Errors in the idea: tubing velocity/size; 'all disposal water qualifies'; '<$35/t' is the low case only.")
