"""Step 5: cross-checks. (a) reproducibility from the NIST 2026 13X interlaboratory set; (b) how the DAC window
moves with adsorption entropy; (c) literature validation of the bracket method; (d) CO2 vs water; (e) hot-isotherm checks."""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import importlib.util
import io
import contextlib
import json
import math
import os
import statistics

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("s3", os.path.join(HERE, "s3_screen.py"))
s3 = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(s3)
P_AIR = P_CO2_AIR
rows = json.load(open(os.path.join(HERE, "screen_rows.json")))
by_name = {r["name"]: r for r in rows}


def pct(xs, p):
    return float(np.percentile(xs, p))


print("(a) NIST/VAMAS 2026 interlaboratory zeolite 13X set, 25 C: uptake at 42.56 Pa per adsorption isotherm")
ref = [k for k in s3.amb if k["doi"] == "10.1007/s10450-026-00701-3"]
A = [k["u"]["central"] for k in ref if k["u"]["kind"] == "A"]
B = [k for k in ref if k["u"]["kind"] == "B"]
print(f"  isotherms with a bracket: {len(ref)}; class A: {len(A)}; class B: {len(B)}")
print(f"  class A uptake at 420 ppm, mol/kg: median {statistics.median(A):.3f}, 10th-90th percentile {pct(A, 10):.3f}-{pct(A, 90):.3f}, "
      f"min {min(A):.3f}, max {max(A):.3f}, relative spread (p90-p10)/median = {(pct(A, 90) - pct(A, 10)) / statistics.median(A):.0%}")
# how good is the class-B bracket and the Langmuir central estimate? Blind the same isotherms below 1 kPa and 2 kPa.
for cut in (425.0, 1000.0, 2000.0):
    ratios, inside, lo_ratio = [], 0, []
    for k in ref:
        if k["u"]["kind"] != "A":
            continue
        m = k["ps"] >= cut
        if m.sum() < 3:
            continue
        u = s3.uptake_at_air(k["ps"][m], k["qs"][m])
        if u is None:
            continue
        truth = k["u"]["central"]
        ratios.append(u["central"] / truth)
        lo_ratio.append(u["lo"] / truth)
        inside += (u["lo"] <= truth * 1.0001 <= u["hi"] * 1.0002)
    print(f"  blinded below {cut:.0f} Pa (n={len(ratios)}): Langmuir central / measured: median {statistics.median(ratios):.2f}, "
          f"range {min(ratios):.2f}-{max(ratios):.2f}; lower bound / measured: median {statistics.median(lo_ratio):.2f}; "
          f"bracket contains the measured value in {inside}/{len(ratios)}")

print("\n(a2) Other multi-paper adsorbents: spread of the 420 ppm central estimate across papers (288-308 K)")
for nm in ("Zeolite 13X", "Mg-MOF-74", "Zeolite 5A", "Zeolite 4A", "CuBTC", "UiO-66"):
    hk = [r for r in rows if r["name"] == nm]
    if not hk:
        continue
    r = hk[0]
    reps = []
    for doi, ks in s3.by_ads[r["hashkey"]].items():
        k = min(ks, key=lambda k: (abs(k["T"] - 298.15), k["u"]["extrap"]))
        reps.append(k)
    good = [k for k in reps if k["u"]["extrap"] <= 25]
    for label, sel in (("first point <= 25x", good), ("all papers", reps)):
        if len(sel) >= 2:
            c = [k["u"]["central"] for k in sel]
            l = [k["u"]["lo"] for k in sel]
            print(f"  {nm:12} {label:18} n={len(sel):2d} central median {statistics.median(c):.3f} (min {min(c):.3f}, max {max(c):.3f}); "
                  f"lower bound median {statistics.median(l):.3f}")

print("\n(b) Verifier window versus adsorption entropy (Langmuir site, 25 C adsorption at 42.56 Pa, desorb at 1 kPa or 0.1 kPa CO2)")
print(f"  {'dS J/mol/K':>10} {'dH for 50% fill':>16} {'T80 at 1 kPa':>13} {'T80 at 0.1 kPa':>15}   (T80 = unload 80% of the ambient loading)")
for dS in (-80.0, -100.0, -110.0, -130.0, -165.0, -186.0):
    dH = dG_for_half_loading() + T0 * dS
    th = loading(P_AIR, T0, dH, dS, 1.0)
    print(f"  {dS:>10.0f} {dH / 1e3:>16.1f} {s3.t_unload80(dH, dS, th, 1e3):>13.0f} {s3.t_unload80(dH, dS, th, 100.0):>15.0f}")
print("  Henry-regime limit (fill << 1): T80 depends on dH only")
for dH in (-30e3, -40e3, -50e3, -60e3, -70e3, -80e3, -90e3):
    out = []
    for p_des in (1e3, 100.0):
        ratio = 0.2 * P_AIR / p_des
        T = 1.0 / (1.0 / T0 + R * math.log(ratio) / dH * -1.0 * -1.0)
        # b(T)/b(T0) = ratio -> exp(-dH/R (1/T - 1/T0)) = ratio
        T = 1.0 / (1.0 / T0 - R * math.log(ratio) / dH)
        out.append(T - 273.15)
    print(f"    dH {dH / 1e3:>5.0f} kJ/mol: T80 = {out[0]:>4.0f} C at 1 kPa, {out[1]:>4.0f} C at 0.1 kPa")

print("\n(c) Bracket method against independent literature values at about 400 ppm, 25 C (dry, single-component)")
lit = [("SIFSIX-3-Zn", 0.13, "Shekhah 2014"), ("Mg-MOF-74", 0.088, "Shekhah 2014 comparison"),
       ("TRI-PE-MCM-41", 0.98, "Belmabkhout 2010"), ("mmen-Mg2(dobpdc)", 2.0, "McDonald 2012, 0.39 mbar"),
       ("Zeolite 13X", None, "see NIST set above")]
for nm, val, src in lit:
    r = by_name.get(nm)
    if r:
        v = "-" if val is None else f"{val:.3f}"
        ok = "" if val is None else ("inside bracket" if r["score"] <= val <= r["hi"] else "OUTSIDE bracket")
        print(f"  {nm:18} literature {v:>6} ({src}); screen: lower {r['score']:.3f}, central {r['central_med']:.3f}, upper {r['hi']:.3f}, "
              f"first point at {r['extrap']:.1f}x  {ok}")

print("\n(d) CO2 at 420 ppm versus pure-water uptake (same adsorbent, 288-308 K water isotherms in ISODB)")
both = [r for r in rows if r["h2o_50rh"] is not None and r["central_med"] >= 0.02]
both.sort(key=lambda r: -r["score"])
print(f"  adsorbents with CO2 central >= 0.02 mol/kg and a water isotherm: {len(both)}")
for r in both[:14]:
    w10 = "-" if r["h2o_10rh"] is None else f"{r['h2o_10rh']:.1f}"
    print(f"  {r['name'][:28]:28} CO2 lower {r['score']:.3f} / central {r['central_med']:.3f} mol/kg; H2O at 10% RH {w10:>5}, "
          f"at 50% RH {r['h2o_50rh']:.1f} mol/kg; H2O(50% RH)/CO2(central) = {r['h2o_50rh'] / r['central_med']:.0f}")

print("\n(e) Hot-isotherm checks: measured loading at 1 kPa CO2 on the hottest isotherm versus the mapped verifier site")
for r in rows[:60]:
    d = r.get("direct")
    if not d or d.get("q_hot_1kPa") is None or r["dH"] is None:
        continue
    Th = d["T_hot_C"] + 273.15
    model = loading(1e3, Th, r["dH"], r["dS"], r["qmax_eff"])
    print(f"  {r['name'][:28]:28} {d['T_hot_C']:.0f} C: measured {d['q_hot_1kPa']:.3f} mol/kg, verifier site {model:.3f} mol/kg; "
          f"ambient 420 ppm central {r['central_med']:.3f}; measured swing {r['central_med'] - d['q_hot_1kPa']:+.3f} mol/kg")

print("\n(f) TRI-PE-MCM-41 and PEI-MonoSil isosteric heats per paper")
for (doi, hk), v in s3.cc.items():
    nm = (s3.ADS.get(hk) or {}).get("name")
    if nm in ("TRI-PE-MCM-41", "PEI-MonoSil", "mmen-Mg2(dobpdc)", "CPO-27-Mg-c", "CD-MOF-2", "SIFSIX-3-Zn", "CuBTTri-mmen"):
        print(f"  {nm:18} {doi}: dH {v['dH'] / 1e3:.1f} kJ/mol from {v['nT']} temperatures {v['Tmin']}-{v['Tmax']} K at q* = {v['qstar']:.3f} mol/kg")
grp = [k for (doi, hk), ks in s3.sets.items() for k in ks if k["name"] == "TRI-PE-MCM-41"]
for k in sorted(grp, key=lambda k: (k["doi"], k["T"], k["ps"][0]))[:40]:
    print(f"    {k['doi']} {k['T']:.0f} K file={k['file'][-14:]} p {k['ps'][0]:.3g}-{k['ps'][-1]:.3g} Pa, q {k['qs'][0]:.3f}-{k['qs'][-1]:.3f} mol/kg, n={len(k['ps'])}")
