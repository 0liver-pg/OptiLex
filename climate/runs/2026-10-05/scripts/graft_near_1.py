"""Verifier for graft_near_1: fenceline monitoring at HCFC-22 plants to close the HFC-23 gap.

Checks: (1) gap size; (2) thermodynamic floor (destruction at source vs removal from air);
(3) energy per t CO2e of destruction; (4) cost per t CO2e (monitoring + destruction);
(5) plume detectability at fenceline distances; (6) Monte Carlo of 2-week emission-rate
inference error with/without tracer calibration (the idea's falsifiable +-50% claim);
(7) scale and resource needs.

Primary sources fetched this run (abstracts via Europe PMC):
  Rust et al., Nature 2024, doi 10.1038/s41586-024-07833-y: EF 0.19% (0.13-0.24%) of HCFC-22,
    measured at one European HCFC-22/fluoropolymer plant with regional stations + released tracer;
    destruction could cut global HFC-23 by >=84% (69-100%), 14 (12-16) Gg/yr.
  Comms Earth & Env 2024, doi 10.1038/s43247-024-01946-y: global HFC-23 14.0 +- 0.9 Gg/yr in 2023
    (peak 17.3 +- 0.8 in 2019), "five times higher than reported in 2021".
  40 CFR 63.658 (Cornell LII text): 14-day samples, action level 9 ug/m3 benzene on annual
    average of delta-c (max minus min site), root-cause analysis within 5 days, done within 45 days.
Everything else is labelled ASSUMPTION with a justification.
"""
import math
import sys

import numpy as np

sys.path.insert(0, 'climate')
from physics import *  # noqa: F401,F403

rng = np.random.default_rng(42)
M_HFC23 = 0.07001        # kg/mol CHF3
GWP100_HFC23 = 14600.0   # IPCC AR6 (AR5: 12,400)
GWP20_HFC23 = 12400.0    # IPCC AR6 GWP20 (approx.)
line = "-" * 78

# ---------------------------------------------------------------- 1. gap size
print(line); print("1. GAP SIZE (measured 2023 vs reported)")
measured_2023 = 14.0             # Gg/yr, CEE 2024 (measured, atmospheric inversion)
measured_unc = 0.9
reported = measured_2023 / 5.0   # "five times higher than reported in 2021" -> ~2.8 Gg
gap = measured_2023 - reported
for lab, g in [("central", gap), ("low (meas -1 sigma, reported x1.2)", measured_2023 - measured_unc - reported * 1.2),
               ("high (meas +1 sigma)", measured_2023 + measured_unc - reported)]:
    print(f"  gap {lab:<36}: {g:5.2f} Gg/yr = {g*1e3*GWP100_HFC23/1e6:6.1f} Mt CO2e (GWP100 AR6) "
          f"| {g*1e3*12400/1e6:6.1f} Mt (AR5 GWP)")
# Rust et al. extrapolation: abatable = 84% (69-100%) of emissions
for f in (0.69, 0.84, 1.0):
    print(f"  Rust-style abatable at {f:.0%} of 14.0 Gg: {14.0*f:5.2f} Gg = {14.0*f*1e3*GWP100_HFC23/1e6:6.1f} Mt CO2e")
# implied global HCFC-22 production consistent with EF 0.19% residual
P_implied = (14.0 * (1 - 0.84)) / 0.0019  # Gg HCFC-22 -> residual 16% of emissions at EF 0.19%
print(f"  Implied HCFC-22 production if residual (16% of 14 Gg) = EF 0.19%: {P_implied/1e3:.2f} Mt/yr "
      "(order-of-magnitude consistency check; includes feedstock use)")
print("  Caveat: 2023 measured vs 2021 reported (different years); CEE 2024 says non-HCFC-22 sources "
      "explain only a minor, highly uncertain fraction.")

# ---------------------------------------------------------------- 2. thermodynamic floor
print(line); print("2. THERMODYNAMIC FLOOR")
# Destruction: CHF3 + 1/2 O2 + H2O -> CO2 + 3 HF (gas phase), standard enthalpies of formation (kJ/mol)
dHf = {"CHF3": -697.0, "H2O": -241.8, "CO2": -393.5, "HF": -273.3, "O2": 0.0}
dH = dHf["CO2"] + 3 * dHf["HF"] - (dHf["CHF3"] + dHf["H2O"])
print(f"  Hydrolytic oxidation of CHF3: dH = {dH:.0f} kJ/mol (exothermic) -> no work floor; "
      "support fuel is a kinetic need (>1100 C), not a thermodynamic one.")
# separation of HFC-23 from a concentrated vent (assume 50-95% HFC-23; the vent is HFC-23-rich after condensation)
for x in (0.5, 0.95):
    w = min_separation_work(x, 0.999 if x < 0.95 else 0.99, 0.9999)
    print(f"  Min work to concentrate HFC-23 from {x:.0%} vent: {w/1e3:.2f} kJ/mol = "
          f"{gj_per_tonne(w, M_HFC23):.4f} GJ/t HFC-23 = {gj_per_tonne(w, M_HFC23)/GWP100_HFC23*1e6:.2f} kJ/t CO2e")
# contrast: removing HFC-23 from ambient air after release (37 ppt background assumed)
x_air = 37e-12
w_air = min_separation_work(x_air, 0.5, 0.99)
fan_air = fan_work_gj_per_tonne(x_air, 0.5, 100, 0.6, M_HFC23)
print(f"  Contrast: removal from air at 37 ppt, 50% capture: floor {w_air/1e3:.1f} kJ/mol = "
      f"{gj_per_tonne(w_air, M_HFC23):.2f} GJ/t HFC-23 = {gj_per_tonne(w_air, M_HFC23)/GWP100_HFC23:.4f} GJ/t CO2e;"
      f" fan work alone {fan_air:.3e} GJ/t HFC-23 = {fan_air/GWP100_HFC23:.1f} GJ/t CO2e  -> prevention at source only.")
floor_gj_per_t_co2e = 0.0

# ---------------------------------------------------------------- 3. energy per t CO2e
print(line); print("3. ENERGY PER t CO2e ABATED (destruction + monitoring)")
# ASSUMPTION: support fuel for thermal oxidiser / plasma, 20/60/150 GJ per t HFC-23 destroyed
# (vent is non-flammable, must be held >1100 C with dilution air/steam; plasma arc ~ similar order).
fuel = {"low": 20.0, "base": 60.0, "high": 150.0}
mon_energy_gj_per_plant = 50.0  # ASSUMPTION: shipping canisters, GC-MS, cryogen ~ 50 GJ/plant/yr (negligible)
e = {}
for k, v in fuel.items():
    e[k] = v / GWP100_HFC23
    print(f"  {k:<5}: {v:5.0f} GJ/t HFC-23 -> {e[k]:.5f} GJ/t CO2e ({e[k]*1e3:.2f} MJ/t CO2e); CO2 from fuel {v*0.0561/GWP100_HFC23*100:.3f}% of abated CO2e")
print(f"  Direct CO2 from CHF3 carbon: {44.01/70.01:.3f} t CO2 per t HFC-23 = {44.01/70.01/GWP100_HFC23*100:.4f}% of abated")

# ---------------------------------------------------------------- 4. cost per t CO2e
print(line); print("4. COST PER t CO2e")
def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)
# Monitoring network (the graft). ASSUMPTIONS: 10-14 samplers + 2 upwind blanks, 26 two-week periods;
# preconcentration GC-MS (Medusa-class) at $400-1500/sample (specialist, not commodity TO-15);
# annual tracer release $50-150k; staff/QA/reporting $50-150k; capex samplers $50-150k annualised.
mon = {}
for k, (n_s, c_s, tracer, staff, capex) in {
        "low": (12, 400, 50e3, 50e3, 50e3), "base": (14, 800, 100e3, 100e3, 100e3),
        "high": (16, 1500, 150e3, 150e3, 150e3)}.items():
    mon[k] = n_s * 26 * c_s + tracer + staff + capex * crf(0.08, 10)
    print(f"  monitoring per plant {k:<5}: ${mon[k]/1e6:.2f}M/yr")
plants = {"low": 25, "base": 35, "high": 60}  # ASSUMPTION: HCFC-22 production sites worldwide (China majority)
# Destruction. ASSUMPTIONS: incinerator capex $5/10/20M per plant needing new/redundant unit (high case adds
# a redundant unit to cover downtime, a known venting cause); share of plants needing new capex 30/50/80%;
# fixed O&M 4% capex; fuel $8/GJ; HF neutralisation with lime 1.6 t Ca(OH)2 per t HFC-23 at $150/t
# (low case recovers HF as product, cost 0); 15 yr at 8%.
gap_t = {"low": (measured_2023 - measured_unc - reported * 1.2) * 1e3,
         "base": gap * 1e3, "high": (measured_2023 + measured_unc - reported) * 1e3}  # t HFC-23/yr
capture_frac = {"low": 0.3, "base": 0.7, "high": 0.95}  # share of gap actually closed (compliance response)
cap = {"low": 5e6, "base": 10e6, "high": 20e6}
share_new = {"low": 0.3, "base": 0.5, "high": 0.8}
lime = {"low": 0.0, "base": 1.6 * 150, "high": 1.6 * 250}
cost = {}
abated_mt = {}
for k in ("low", "base", "high"):
    # "low" cost pairs cheap assumptions; "high" cost pairs expensive; abated tonnes use the matching
    # pessimistic tonnage for high cost (worst-case cost per tonne).
    kk_t = {"low": "high", "base": "base", "high": "low"}[k]
    t_destroyed = gap_t[kk_t] * capture_frac[{"low": "high", "base": "base", "high": "low"}[k]]
    co2e = t_destroyed * GWP100_HFC23
    capex_ann = cap[k] * share_new[k] * plants[k] * (crf(0.08, 15) + 0.04)
    fuel_cost = t_destroyed * fuel[k] * 8.0
    cons = t_destroyed * lime[k]
    mon_tot = mon[k] * plants[k]
    total = capex_ann + fuel_cost + cons + mon_tot
    cost[k] = total / co2e
    abated_mt[k] = co2e / 1e6
    print(f"  {k:<5}: abated {co2e/1e6:6.1f} Mt CO2e/yr | monitoring ${mon_tot/1e6:5.1f}M | destruction capex "
          f"${capex_ann/1e6:5.1f}M/yr | fuel ${fuel_cost/1e6:.2f}M | consumables ${cons/1e6:.2f}M | total "
          f"${total/1e6:5.1f}M/yr -> ${cost[k]:.3f}/t CO2e (monitoring alone ${mon_tot/co2e:.3f}/t)")
print("  NOTE: excludes the economic value of foregone non-compliance to violators; this is a transfer, "
      "and is small (it equals the destruction cost above).")

# ---------------------------------------------------------------- 5. plume detectability
print(line); print("5. DETECTABILITY (Gaussian plume, Briggs rural, ground-level centreline)")
BRIGGS = {  # sigma_y, sigma_z coefficients (Briggs 1973 rural)
    "B": (0.16, 0.12, 0.0),  # sigma_z = 0.12x
    "C": (0.11, 0.08, 0.0002),
    "D": (0.08, 0.06, 0.0015),
    "E": (0.06, 0.03, 0.0003),
}
def sig(x, cls):
    a, b, c = BRIGGS[cls]
    sy = a * x / math.sqrt(1 + 0.0001 * x)
    if cls == "B":
        sz = 0.12 * x
    elif cls == "E":
        sz = b * x / (1 + c * x)
    else:
        sz = b * x / math.sqrt(1 + c * x)
    return sy, sz
def conc_ppt(q_gs, x, y, u, cls, H=0.0):
    sy, sz = sig(x, cls)
    c = q_gs / (2 * math.pi * sy * sz * u) * math.exp(-y * y / (2 * sy * sy)) * 2 * math.exp(-H * H / (2 * sz * sz))
    mol_air = P0 / (R * T0)
    return (c / (M_HFC23 * 1e3)) / mol_air * 1e12  # g/m3 -> mol/m3 -> mol/mol -> ppt
prod_kt = 100.0
bg = 37.0  # ppt background (ASSUMPTION, ~2023 NH baseline)
for ef in (0.0019, 0.01, 0.025):
    q = prod_kt * 1e9 * ef / 3.156e7  # g/s
    row = []
    for x in (300, 1000, 2000):
        row.append(f"x={x}m: {conc_ppt(q, x, 0, 4.0, 'D'):>9,.0f} (H=30m: {conc_ppt(q, x, 0, 4.0, 'D', 30):>8,.0f})")
    print(f"  EF {ef:.2%} (Q={q:.2f} g/s): " + " | ".join(row) + " ppt")
# sector-averaged two-week mean at 15% wind frequency into a 22.5 deg sector
for ef in (0.0019, 0.01):
    q = prod_kt * 1e9 * ef / 3.156e7
    x = 2000.0
    _, sz = sig(x, "D")
    c = math.sqrt(2 / math.pi) * q / (sz * 4.0 * (2 * math.pi * x / 16)) * 0.15
    print(f"  EF {ef:.2%}: sector-averaged 2-week mean at 2 km, 15% frequency: "
          f"{(c/(M_HFC23*1e3))/(P0/(R*T0))*1e12:,.0f} ppt vs background {bg:.0f} ppt")

# ---------------------------------------------------------------- 6. inference Monte Carlo
print(line); print("6. MONTE CARLO: 2-WEEK EMISSION-RATE INFERENCE FROM A FENCELINE RING")
# Truth: hourly met (wind dir from a bimodal rose, speed lognormal, stability class random by hour),
# source = cluster of 3 vents at random offsets <=150 m, heights 0-30 m, ring of N samplers at radius r.
# Inference: forward model with ONE effective point source at plant centre, class D, ground level,
# measured hourly wind; Q_hat = sum(obs)/sum(model per unit Q). Tracer: once a year a 1-week release
# at a single vent gives a multiplicative calibration factor for the model (model bias), applied to
# later periods. Additive noise: 5% analytical + 2 ppt background variability per sample.
def simulate(n_samplers=10, r=500.0, n_periods=200, tracer=True, neighbour=False):
    ratios = []
    ang = np.linspace(0, 2 * np.pi, n_samplers, endpoint=False)
    sx, sy_ = r * np.cos(ang), r * np.sin(ang)
    classes = np.array(["B", "C", "D", "E"])
    def period(Q, vents, hours=336, rose_main=None):
        main = rose_main if rose_main is not None else rng.uniform(0, 2 * np.pi)
        wd = np.where(rng.random(hours) < 0.6, rng.normal(main, 0.5, hours), rng.uniform(0, 2 * np.pi, hours))
        ws = np.clip(rng.lognormal(np.log(3.5), 0.45, hours), 0.8, 15)
        cl = rng.choice(classes, hours, p=[0.1, 0.2, 0.5, 0.2])
        obs = np.zeros(n_samplers); mod = np.zeros(n_samplers)
        for h in range(hours):
            ux, uy = np.cos(wd[h]), np.sin(wd[h])
            for i in range(n_samplers):
                for (vx, vy, H, frac) in vents:
                    dx, dy = sx[i] - vx, sy_[i] - vy
                    xd = dx * ux + dy * uy; yd = -dx * uy + dy * ux
                    if xd > 10:
                        obs[i] += conc_ppt(Q * frac, xd, yd, ws[h], cl[h], H)
                xd = sx[i] * ux + sy_[i] * uy; yd = -sx[i] * uy + sy_[i] * ux
                if xd > 10:
                    mod[i] += conc_ppt(1.0, xd, yd, ws[h], "D", 0.0)
            if neighbour:  # uncontrolled neighbour 1.5 km away emitting 1.0 g/s, not modelled
                for i in range(n_samplers):
                    dx, dy = sx[i] - 1500.0, sy_[i]
                    xd = dx * ux + dy * uy; yd = -dx * uy + dy * ux
                    if xd > 10:
                        obs[i] += conc_ppt(1.0, xd, yd, ws[h], cl[h], 10.0)
        obs /= hours; mod /= hours
        obs = obs * (1 + rng.normal(0, 0.05, n_samplers)) + rng.normal(0, 2.0, n_samplers)
        # delta-c style: subtract the minimum site as background estimate (as in 63.658)
        obs_d = obs - obs.min(); mod_d = mod - mod.min()
        return obs_d.sum() / mod_d.sum()
    for _ in range(n_periods):
        vents = [(rng.uniform(-150, 150), rng.uniform(-150, 150), rng.uniform(0, 30), f)
                 for f in rng.dirichlet([2, 2, 2])]
        Q = rng.uniform(0.5, 15.0)  # g/s (EF ~0.16%-4.7% for a 100 kt/yr plant)
        cal = 1.0
        if tracer:
            # tracer released at one vent location, known rate 1 g/s-equivalent, model bias -> cal
            v0 = vents[int(rng.integers(3))]
            cal = period(1.0, [(v0[0], v0[1], v0[2], 1.0)], hours=168)
        q_hat = period(Q, vents) / cal
        ratios.append(q_hat / Q)
    return np.array(ratios)
for label, kw in [("no tracer, 10 samplers r=500m", dict(tracer=False)),
                  ("tracer-calibrated, 10 samplers r=500m", dict(tracer=True)),
                  ("tracer-calibrated, 10 samplers r=1500m", dict(tracer=True, r=1500.0)),
                  ("tracer-calibrated + unmodelled neighbour 1 g/s at 1.5 km", dict(tracer=True, neighbour=True))]:
    rr = simulate(n_periods=120, **kw)
    lr = np.log(rr)
    p5, p50, p95 = np.exp(np.percentile(lr, [5, 50, 95]))
    within = np.mean(np.abs(rr - 1) <= 0.5)
    print(f"  {label:<58}: median {p50:.2f}, 5-95% [{p5:.2f}, {p95:.2f}], within +-50%: {within:.0%}")
# discrimination EF 0.2% vs 1%: factor 5 separation; check probability of confusing
rr = simulate(n_periods=200, tracer=True)
thr = math.sqrt(5)  # geometric midpoint between 0.2% and 1%
p_mis_low = np.mean(rr * 1.0 > thr)        # true 0.2% read as >0.447%
p_mis_high = np.mean(rr * 5.0 < thr)        # true 1% read as <0.447%
print(f"  Discrimination EF 0.2% vs 1% (threshold at geometric midpoint): false alarm {p_mis_low:.1%}, "
      f"missed violation {p_mis_high:.1%}")

# ---------------------------------------------------------------- 7. scale and resources
print(line); print("7. SCALE AND RESOURCES")
for k in ("low", "base", "high"):
    gt = {"low": gap_t["low"] * capture_frac["low"], "base": gap_t["base"] * capture_frac["base"],
          "high": gap_t["high"] * capture_frac["high"]}[k] * GWP100_HFC23 / 1e9
    s = ScaleCheck(gt, e["base"])
    print(f"  scale {k:<5}: {gt:.3f} Gt CO2e/yr ({gt/TOTAL_GHG_GT_CO2E:.2%} of global GHG); energy "
          f"{s.ej_per_year*1e3:.3f} PJ/yr = {s.share_of_world_primary_energy:.2e} of world primary energy")
print(f"  GWP20 view: base scale {gap_t['base']*capture_frac['base']*GWP20_HFC23/1e9:.3f} Gt CO2e/yr "
      "(HFC-23 lifetime ~228 yr, so GWP20 < GWP100)")
print(f"  Materials: lime {gap_t['base']*capture_frac['base']*1.6/1e3:.1f} kt/yr (or HF recovered as product); "
      f"canisters ~{14*26*plants['base']:,} samples/yr; land: <1 ha/plant; water: scrubber only, negligible.")
print(f"  Lab capacity: {14*26*plants['base']:,} preconcentration GC-MS runs/yr ~ "
      f"{14*26*plants['base']/2500:.1f} instrument-years at ~2,500 runs/instrument-yr (ASSUMPTION).")
print(line)
print(f"SUMMARY: floor {floor_gj_per_t_co2e} GJ/t CO2e (exothermic destruction); energy low/base/high "
      f"{e['low']:.5f}/{e['base']:.5f}/{e['high']:.5f} GJ/t CO2e; cost low/base/high "
      f"${cost['low']:.3f}/${cost['base']:.3f}/${cost['high']:.3f} per t CO2e")
