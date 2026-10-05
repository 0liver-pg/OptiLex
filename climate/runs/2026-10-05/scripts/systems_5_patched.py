"""Verifier for systems_5_patched: hooded tailrace/weir degassing at OLD tropical reservoirs + VAM RTO.

Checks: (A) thermodynamic floor of moving dissolved CH4 into a 0.25-1.5% sweep (Henry's law),
(B) the hood's back-pressure suppression of degassing (missing from the idea's model),
(C) net abatement vs counterfactual (the idea's (1-f_ox) haircut), (D) energy GJ/t CO2e,
(E) $/t CO2e low/base/high with capex annuity, O&M, MRV, electricity, (F) reproduction of the
idea's own table, (G) measured anchors (Balbina, Petit Saut, NT2), (H) scale and resources.
"""
import sys, math, itertools
sys.path.insert(0, 'climate')
from physics import *

GWP = GWP100["CH4_biogenic"]          # 27, AR6
GWP20b = GWP20["CH4_biogenic"]        # 79.7
T = 301.15                            # 28 C tropical water
RHO_CH4 = P0 * M_CH4 / (R * 293.15)   # kg/m3 of pure CH4 at 20 C, 1 atm
SEC_YR = 3.1536e7

def crf(r, n): return r * (1 + r) ** n / ((1 + r) ** n - 1)

# ---------------- (A) Henry's law and thermodynamic floor ----------------
# Sander (2015) compilation: CH4 Hcp ~1.4e-5 mol/(m3 Pa) at 298.15 K, d ln H / d(1/T) ~1600 K.
def henry(Tk): return 1.4e-5 * math.exp(1600 * (1 / Tk - 1 / 298.15))   # mol/(m3 Pa)
def c_eq_mgL(y, Tk=T): return henry(Tk) * y * P0 * M_CH4 * 1e3           # mol/m3 -> kg/m3 -> g/m3 = mg/L
print("=== (A) Henry's law: dissolved CH4 in equilibrium with a sweep of mole fraction y (28 C) ===")
for y in (1.93e-6, 0.0025, 0.005, 0.01, 0.015):
    print(f"  y = {y*100:7.4f}%  ->  c_eq = {c_eq_mgL(y):.4f} mg/L")
print("  Free energy per mol CH4 moved from water at c into sweep at y (negative = spontaneous, floor = 0 work):")
for c in (0.2, 0.5, 1.0, 2.0):
    for y in (0.0025, 0.01):
        dG = R * T * math.log(c_eq_mgL(y) / c)
        print(f"    c = {c} mg/L, y = {y*100:.2f}%: dG = {dG/1e3:+.2f} kJ/mol CH4 "
              f"= {gj_per_tonne(dG, M_CH4)/GWP:+.4f} GJ/t CO2e")
print("  => separation floor is 0 GJ/t whenever c > c_eq(y): the water is supersaturated ~"
      f"{1.0/c_eq_mgL(1.93e-6):,.0f}x vs ambient air at 1 mg/L; the turbulence that already exists does the work.")
print(f"  Verifier reference: ambient-air CH4 removal fan work = "
      f"{fan_work_gj_per_tonne(1.93e-6,0.5,100,molar_mass=M_CH4)/GWP100['CH4_fossil']:.2f} GJ/t CO2e")
for dp in (500, 3000):
    fw = fan_work_gj_per_tonne(0.01, 1.0, dp, 0.7, molar_mass=M_CH4)
    print(f"  Fan work for a 1% sweep at {dp} Pa, 70% fan: {fw:.3f} GJ/t CH4 = {fw/GWP:.4f} GJ/t CO2e")

# ---------------- (B) hood with back-pressure suppression ----------------
def hood(Q, c, phi_open, y, months, f_ds):
    """Q m3/s, c mg/L entering hooded zone, phi_open = fraction that would degas there in open air.
    Well-mixed hood gas at mole fraction y; water leaving: c_out = c_eq + (c - c_eq)(1 - phi_open).
    Returns captured t CH4/yr, net t CO2e/yr (vs counterfactual), sweep m3/s, ideal-model (no suppression)."""
    ce = c_eq_mgL(y)
    cap_kg_s = max(Q * (c - ce) * phi_open / 1000, 0.0)
    ideal_kg_s = Q * c * phi_open / 1000
    frac = months / 12
    cap_t = cap_kg_s * SEC_YR * frac / 1000
    # counterfactual: open-air degassing Q c phi + downstream (1-f_ds) of remainder.
    # with hood: captured, extra CH4 left in water = Q*ce*phi goes downstream, (1-f_ds) of it emitted.
    extra_ds_t = Q * ce * phi_open / 1000 * SEC_YR * frac / 1000 * (1 - f_ds) if c > ce else 0
    open_t = ideal_kg_s * SEC_YR * frac / 1000
    net_t = (open_t - extra_ds_t) if c > ce else 0.0
    G = cap_kg_s / RHO_CH4 / y if cap_kg_s > 0 else 0.0
    return cap_t, net_t * GWP, G, open_t

print("\n=== (B) Suppression: captured / open-air degassing at hood fraction y ===")
for c in (0.5, 1.0, 2.0):
    row = []
    for y in (0.0025, 0.005, 0.01, 0.015):
        cap, net, G, ideal = hood(600, c, 0.3, y, 12, 0.4)
        row.append(f"y {y*100:.2f}%: {cap/ideal:.2f}")
    print(f"  c = {c} mg/L: " + " | ".join(row))

# ---------------- (C,D,E) costs ----------------
CAPEX = {  # (low, base, high)
    "rto_usd_per_m3s": (70e3, 103e3, 300e3),   # base: MATEC claim EUR 9.5M / 100 m3/s * 1.08 (unverified);
                                               # high: installed VAM projects incl. ducting/controls (judgement)
    "rto_min_usd":     (3e6, 5e6, 8e6),        # smallest practical unit
    "hood_usd":        (5e6, 15e6, 40e6),      # ~5,000 m2 flood-rated corrosion-proof enclosure over moving water
}
OPEX = {
    "om_frac": (0.02, 0.03, 0.05),             # of capex per yr
    "mrv_usd": (0.2e6, 0.5e6, 1.0e6),          # continuous CH4, flow, f_ds and phi verification
    "elec": (40.0, 60.0, 90.0),                # $/MWh
    "dp_total": (1500, 3000, 5000),            # Pa: hood+duct ~500 + RTO beds 1000-4500
    "eta_fan": 0.7,
    "rate": (0.06, 0.08, 0.10), "life": 20,
}
def cost(Q, c, phi, y, months, f_ds, k):
    """k = 0 low, 1 base, 2 high cost assumptions."""
    cap_t, net_co2e, G, ideal = hood(Q, c, phi, y, months, f_ds)
    if net_co2e <= 0: return net_co2e, float('inf'), 0, 0, G
    capex = max(G * CAPEX["rto_usd_per_m3s"][k], CAPEX["rto_min_usd"][k]) + CAPEX["hood_usd"][k]
    fan_MW = G * OPEX["dp_total"][k] / OPEX["eta_fan"] / 1e6
    mwh = fan_MW * 8760 * months / 12
    annual = capex * crf(OPEX["rate"][k], OPEX["life"]) + capex * OPEX["om_frac"][k] + OPEX["mrv_usd"][k] + mwh * OPEX["elec"][k]
    gj_per_t = mwh * 3.6 / net_co2e
    return net_co2e, annual / net_co2e, gj_per_t, capex, G

print("\n=== (F) Reproduce the idea's table (its model: no suppression, net = captured*(1-0.4), its capex, no O&M/MRV) ===")
def idea_model(c, phi, months, fox=0.4, Q=600):
    ch4 = Q * c / 1000 * phi; t = ch4 * SEC_YR * months / 12 / 1000; net = t * GWP * (1 - fox)
    G = ch4 / 0.668 / 0.01; fan = G * 500 / 0.6 / 1e6
    capex = max(G / 100, 0.5) * 9.5e6 * 1.08 + 15e6
    return net, (fan * 8760 * months / 12 * 60 + capex * crf(0.08, 20)) / net
for c, phi, m in ((1, 0.3, 12), (1, 0.5, 12), (2, 0.5, 6), (2, 0.5, 12), (0.5, 0.15, 6)):
    n, u = idea_model(c, phi, m)
    print(f"  c {c} phi {phi} {m} mo: net {n/1e6:.3f} Mt CO2e/yr at ${u:.0f}/t")

print("\n=== (C/D/E) Corrected model, Q=600 m3/s (Balbina-like), y=1%, f_ds=0.4 ===")
print("  c mg/L | phi | mo | capt/open | net Mt CO2e/yr | GJ/t CO2e (base) | $/t low | base | high | capex base $M | sweep m3/s")
for c, phi, m in ((0.5, 0.15, 6), (0.5, 0.3, 12), (1, 0.15, 12), (1, 0.3, 12), (1, 0.5, 12),
                  (2, 0.3, 6), (2, 0.5, 6), (2, 0.5, 12), (2.75, 0.5, 12)):
    out = [cost(600, c, phi, 0.01, m, 0.4, k) for k in range(3)]
    cap, net, G, ideal = hood(600, c, phi, 0.01, m, 0.4)
    print(f"  {c:4} | {phi:.2f} | {m:2} | {cap/ideal:.2f} | {out[1][0]/1e6:.3f} | {out[1][2]:.4f} | "
          f"{out[0][1]:6.1f} | {out[1][1]:6.1f} | {out[2][1]:6.1f} | {out[1][3]/1e6:5.1f} | {out[1][4]:5.0f}")

print("\n  Optimal sweep fraction y (base costs), c=1, phi=0.3, 12 mo:")
for y in (0.0025, 0.005, 0.01, 0.0125):
    n, u, gj, cx, G = cost(600, 1.0, 0.3, y, 12, 0.4, 1)
    print(f"    y {y*100:.2f}%: net {n/1e6:.3f} Mt/yr, ${u:.1f}/t, sweep {G:.0f} m3/s")

print("\n  Counterfactual check: net / captured with f_ds = 0, 0.4, 0.8 (c=1, phi=0.3, y=1%):")
for f in (0.0, 0.4, 0.8):
    cap, net, G, ideal = hood(600, 1.0, 0.3, 0.01, 12, f)
    print(f"    f_ds {f}: captured {cap*GWP/1e6:.3f} Mt CO2e, net {net/1e6:.3f} Mt CO2e (net/captured {net/(cap*GWP):.2f})")
print("  => the idea's net = captured*(1-f_ox) haircut is wrong in direction for in-zone degassing: CH4 that degasses"
      "\n     under the hood would have degassed there anyway, so net >= captured. The real loss is suppression (B).")

# ---------------- head penalty ----------------
P1 = 1000 * 9.81 * 600 * 1.0 * 0.9 / 1e6
print(f"\n  1 m added head at Q=600: {P1:.2f} MW lost = {1/22*100:.1f}% of output at 22 m; "
      f"${P1*8760*60/1e6:.2f}M/yr at $60/MWh")

# ---------------- (G) measured anchors ----------------
print("\n=== (G) Measured anchors (dated) ===")
balbina_ds = 39e3 * 16.04 / 12.01      # Kemenes et al. 2007 GRL, downstream 39 Gg C/yr (2004-06 data)
balbina_res = 34e3 * 16.04 / 12.01
print(f"  Balbina (Kemenes 2007): downstream {balbina_ds/1e3:.0f} kt CH4/yr, reservoir surface {balbina_res/1e3:.0f} kt CH4/yr "
      f"-> total {(balbina_ds+balbina_res)/1e3:.0f} kt (idea calls 52 kt the TOTAL; it is the downstream share)")
print(f"  implied mean CH4 lost from turbined water at Q=600: {balbina_ds*1e6/(600*SEC_YR):.2f} mg/L (2004-06)")
print(f"  if hooded zone took phi=0.3 of that today at 50% decay since 2005: {0.5*0.3*balbina_ds*GWP/1e6:.2f} Mt CO2e/yr")
ps_ch4 = 0.016e6 * 16.04 / 12.01; ps_weir = 0.70 * ps_ch4    # Abril et al. 2005 GBC, 2000-03 mean
print(f"  Petit Saut (Abril 2005): CH4 {ps_ch4/1e3:.1f} kt/yr since 2000, ~70% at aerating weir = {ps_weir/1e3:.1f} kt "
      f"= {ps_weir*GWP/1e6:.2f} Mt CO2e/yr (2000-03); decayed 4.4x from 1994-96 to 2000-03")
nt2 = (385, 1240, 756)   # Deshmukh 2016 BG: peak monthly degassing Mg CH4/month, 2010: powerhouse, reg. dam, weir
print("  NT2 peak-month degassing split (Deshmukh 2016, 2010): " +
      ", ".join(f"{n} {v/sum(nt2):.0%}" for n, v in zip(("powerhouse", "regulating dam", "weir"), nt2)))
print("  NT2 CH4 at TRC1 below turbines: 117 -> 1.55 umol/L over 30 km channel (2010 WD), i.e. most degassing is"
      "\n  distributed downstream of the boil; a hood over the boil alone captures only part of 'below powerhouse'.")

# Petit Saut-like weir case (Q~250 m3/s Sinnamary mean flow, judgement)
print("\n  Petit Saut-like aerating-weir case, Q=250, y=1%:")
for c, phi, m in ((1.0, 0.7, 12), (0.5, 0.7, 12), (0.3, 0.7, 12)):
    out = [cost(250, c, phi, 0.01, m, 0.4, k) for k in range(3)]
    print(f"    c {c} phi {phi}: net {out[1][0]/1e6:.3f} Mt/yr, $/t {out[0][1]:.1f} / {out[1][1]:.1f} / {out[2][1]:.1f}")

# ---------------- kill screen ----------------
print("\n=== Kill screen with corrected model (net >= 0.1 Mt CO2e/yr and base $/t < 30), Q=600 ===")
for m in (6, 12):
    for k in range(3):
        for cphi in [x / 100 for x in range(5, 200)]:
            n, u, *_ = cost(600, cphi / 0.3, 0.3, 0.01, m, 0.4, k)
            if n >= 0.1e6 and u < 30:
                print(f"  {m} mo, {('low','base','high')[k]} costs: need c*phi >= {cphi:.2f} mg/L (phi=0.3)"); break

# ---------------- (H) scale and resources ----------------
print("\n=== (H) Scale ===")
for nsites, per in ((5, 0.05e6), (15, 0.1e6), (30, 0.2e6)):
    tot = nsites * per
    print(f"  {nsites} sites x {per/1e6:.2f} Mt = {tot/1e9:.4f} Gt CO2e/yr GWP100 ({tot/GWP*GWP20b/1e9:.4f} Gt GWP20) "
          f"= {tot/1e9/TOTAL_GHG_GT_CO2E:.3%} of global GHG")
for tg in (1.0, 3.0):
    print(f"  ceiling: if global reservoir degassing were {tg} Tg CH4/yr (unsourced bracket) and 20% were hood-capturable "
          f"at old persistent sites: {tg*1e6*0.2*GWP/1e9:.3f} Gt CO2e/yr")
n, u, gj, cx, G = cost(600, 1.0, 0.3, 0.01, 12, 0.4, 1)
ej = gj * 0.75e6 / 1e9
print(f"  Energy at 0.75 Mt/yr fleet, base: {gj:.4f} GJ/t -> {ej*1e3:.4f} PJ/yr = {ej/WORLD_PRIMARY_ENERGY_EJ:.2e} of world primary")
print(f"  Materials per site (judgement): hood ~5,000 m2 x ~100 kg/m2 = ~500 t steel/FRP; RTO for {G:.0f} m3/s sweep; "
      "land ~0.5 ha; water 0 (no pumping)")

print("\n=== Summary case c=1 mg/L, phi=0.3, 12 mo, y=1%, Q=600: low / base / high ===")
for k in range(3):
    n, u, gj, cx, G = cost(600, 1.0, 0.3, 0.01, 12, 0.4, k)
    print(f"  {('low','base','high')[k]}: net {n/1e6:.3f} Mt CO2e/yr, {gj:.4f} GJ(e)/t CO2e, ${u:.1f}/t, capex ${cx/1e6:.1f}M")
