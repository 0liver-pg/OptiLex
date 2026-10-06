"""Step 4: inspect the raw low-pressure points behind the top-ranked adsorbents, and list extrapolation-only leads."""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import json
import os
import pickle
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "screen_rows.json")))
D = pickle.load(open(os.path.join(HERE, "co2_h2o_isotherms.pkl"), "rb"))
ISO, BIB = D["isotherms"], D["bib"]
P_AIR_BAR = P_CO2_AIR / 1e5

print("RAW POINTS (bar, native units) of the representative 288-308 K isotherm for the top 40 by score")
for i, r in enumerate(rows[:40], 1):
    cands = [k for k in ISO if k["gas"] == "CO2" and k["hashkey"] == r["hashkey"] and k["doi"] == r["doi"]
             and isinstance(k["T"], (int, float)) and abs(k["T"] - r["T_a"]) < 0.6]
    for k in cands[:2]:
        pts = sorted((p, q) for p, q in k["pts"] if p > 0)
        near = [(float(f"{p:.3g}"), float(f"{q:.4g}")) for p, q in pts[:9]]
        print(f"{i:>2} {r['name'][:30]:30} {k['T']:.0f} K [{k['q_units']}] n={len(pts)} p_top={max(p for p, q in pts):.3g} bar"
              f" tab={k['tabular']} cat={k['category'] or '-'} file={k['file']}\n     {near}")

print("\nTemperatures available per (paper, adsorbent) for selected names")
for nm in ("TRI-PE-MCM-41", "PEI-MonoSil", "[CoIICoIII(OH)Cl2(bbta)]", "CPO-27-Mg-c", "Zeolite KX@KA core-shell",
           "Zeolite FAU-I", "Zeolite 4A", "CD-MOF-2", "Zeolite LS-Sr-KFI", "NJU-BAi7", "SIFSIX-3-Zn",
           "NIST RGTM-10257 (Zeolite 13X)", "Aluminum formate", "mmen-Mg2(dobpdc)"):
    seen = {}
    for k in ISO:
        if k["gas"] == "CO2" and k["name"] == nm:
            seen.setdefault(k["doi"], []).append(k["T"])
    for doi, Ts in seen.items():
        print(f"  {nm}: {doi} ({(BIB.get(doi) or {}).get('year')}): T = {sorted(set(Ts))} ({len(Ts)} isotherms)")

print("\nNIST 2026 interlaboratory 13X reference: lowest pressures and loadings")
ref = [k for k in ISO if k["gas"] == "CO2" and (k["name"] or "").startswith("NIST RGTM-10257")]
print("  isotherms:", len(ref), "| temperatures:", sorted({k["T"] for k in ref}), "| units:", {k["q_units"] for k in ref},
      "| categories:", {k["category"] for k in ref})
pm = sorted(min(p for p, q in k["pts"] if p > 0) for k in ref if any(p > 0 for p, q in k["pts"]))
if pm:
    print(f"  lowest pressure per isotherm: min {pm[0]:.3g} bar, median {statistics.median(pm):.3g} bar, max {pm[-1]:.3g} bar "
          f"(42.56 Pa = {P_AIR_BAR:.3g} bar)")
for k in ref[:3]:
    print("   ", k["file"], sorted((float(f'{p:.3g}'), float(f'{q:.4g}')) for p, q in k["pts"] if p > 0)[:6])

print("\nEXTRAPOLATION-ONLY LEADS: adsorbents whose first resolved point is > 25 x 42.56 Pa, ranked by Langmuir central estimate")
print("  (not measured near 420 ppm; the central value is a model extrapolation and can be badly wrong in either direction)")
ext = [r for r in rows if r["extrap"] > 25 and not r["pscale_suspect"]
       and not (r["sim_suspect"] and r["category"] != "exp")]
ext.sort(key=lambda r: -r["central_med"])
print(f"{'#':>2} {'adsorbent':34.34} {'T_a':>4} {'lo':>6} {'q_c':>6} {'q_hi':>6} {'xtrap':>6} {'nDOI':>4} {'dH':>6} {'T80':>5} {'H2O50':>5} doi (year)")
for i, r in enumerate(ext[:40], 1):
    dH = "-" if r["dH"] is None else f"{r['dH'] / 1e3:.1f}"
    t80 = "-" if r.get("T80_C") is None or r.get("T80_C") != r.get("T80_C") else f"{r['T80_C']:.0f}"
    w = "-" if r["h2o_50rh"] is None else f"{r['h2o_50rh']:.1f}"
    print(f"{i:>2} {r['name'][:34]:34} {r['T_a']:>4.0f} {r['score']:>6.3f} {r['central_med']:>6.3f} {r['hi']:>6.3f} "
          f"{r['extrap']:>6.0f} {r['n_doi']:>4d} {dH:>6} {t80:>5} {w:>5} {r['doi']} ({r['year']}) {str(r['title'])[:60]}")
