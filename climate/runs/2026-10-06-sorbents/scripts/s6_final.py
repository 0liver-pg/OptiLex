"""Step 6: final candidate table from the ISODB screen, with documented exclusions and conditional regeneration numbers."""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import contextlib
import importlib.util
import io
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("s3", os.path.join(HERE, "s3_screen.py"))
s3 = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(s3)
rows = json.load(open(os.path.join(HERE, "screen_rows.json")))
P_AIR = P_CO2_AIR

# ---- documented exclusions (automatic flags; reasons checked against the raw points and the source titles) ----
excluded, kept = [], []
for r in rows:
    why = None
    if r["sim_suspect"]:
        why = "simulation (journal/title), not a measurement"
    elif r["pscale_suspect"]:
        why = "pressure scale suspect: whole isotherm lies below 5 mbar"
    elif r["noisy_low"] and r["flag_units"]:
        why = "non-monotone low-pressure points and ambiguous unit"
    (excluded if why else kept).append((r, why))
print("EXCLUDED among the top 30 by score")
for r, why in excluded:
    if rows.index(r) < 30:
        print(f"  {r['name'][:30]:30} score {r['score']:.3f}  {r['doi']}: {why}")

# merge the two zeolite 13X entries (literature set and the NIST/VAMAS 2026 interlaboratory set)
nist = [k["u"]["central"] for k in s3.amb if k["doi"] == "10.1007/s10450-026-00701-3" and k["u"]["kind"] == "A"]
final = [r for r, _ in kept if not r["name"].startswith("NIST RGTM")]
final.sort(key=lambda r: -r["score"])
top = final[:15]

DS_ZEOLITE = next(r for r in rows if r["name"] == "Zeolite 13X")["dS"]
DS_AMINE = next(r for r in rows if r["name"] == "PEI-MonoSil")["dS"]
DS_MOF = 0.5 * (next(r for r in rows if r["name"] == "SIFSIX-3-Zn")["dS"] + next(r for r in rows if r["name"] == "Mg-MOF-74")["dS"])
print(f"\nEntropies measured in this screen and used for the conditional column (J/mol/K): zeolite 13X {DS_ZEOLITE:.0f}; "
      f"physisorbent MOF (mean of SIFSIX-3-Zn and Mg-MOF-74) {DS_MOF:.0f}; amine chemisorbent (PEI-MonoSil) {DS_AMINE:.0f}")

AMINE = ("PEI", "TRI-PE", "CPO-27-Mg-c", "mmen")
HYDROXIDE = ("(OH)", "CD-MOF")


def conditional_T80(r, dS):
    dH = r["dG"] + r["T_a"] * dS
    th = loading(P_AIR, T0, dH, dS, 1.0)
    return dH, s3.t_unload80(dH, dS, th, 1.0e3), s3.t_unload80(dH, dS, th, 100.0)


print("\nFINAL: top 15 adsorbents by guaranteed 420 ppm uptake (288-308 K, dry, single-component CO2), ISODB")
print(f"{'#':>2} {'adsorbent':28.28} {'cls':>3} {'T_a':>4} {'score':>6} {'central':>7} {'upper':>6} {'p1/p':>5} {'nDOI':>4} "
      f"{'dH':>6} {'dS':>5} {'T80@1kPa':>8} {'T80@0.1kPa':>10} {'basis':>10} {'wc100':>5} {'heat100':>7} {'H2O50':>5}  window")
out = []
f = lambda x, s="{:.2f}": "-" if x is None or (isinstance(x, float) and math.isnan(x)) else s.format(x)
for i, r in enumerate(top, 1):
    dH = dS = t1 = t01 = None
    if r["dH"] is not None and r["dS"] <= -50.0:
        dH, dS, t1, t01, basis = r["dH"], r["dS"], r["T80_C"], r["T80_100Pa_C"], "measured"
    elif r["dH"] is not None:
        basis = "weak-site"          # mapped dS > -50 J/mol/K: the isosteric heat was taken on weaker sites
    elif any(h in r["name"] for h in HYDROXIDE):
        basis = "none"
    else:
        dS = DS_AMINE if any(a in r["name"] for a in AMINE) else (DS_ZEOLITE if ("eolite" in r["name"] or "Chabazite" in r["name"]) else DS_MOF)
        dH, t1, t01 = conditional_T80(r, dS)
        basis = "assumed dS"
    wc = r.get("wc_100C") if basis == "measured" else None
    heat = r.get("heat_100C") if basis == "measured" else None
    if r["score"] < 0.1:
        window = "below 0.1 mol/kg"
    elif basis == "measured":
        window = "IN (1 kPa, <=120 C)" if t1 <= 120 else ("only with 0.1 kPa CO2" if t01 <= 120 else "OUT")
    elif basis == "weak-site":
        window = "indeterminate (dH from weaker sites)"
    else:
        window = "regeneration unmeasured"
    print(f"{i:>2} {r['name'][:28]:28} {r['kind']:>3} {r['T_a']:>4.0f} {r['score']:>6.3f} {r['central_med']:>7.3f} {r['hi']:>6.3f} "
          f"{r['extrap']:>5.1f} {r['n_doi']:>4d} {f(dH / 1e3 if dH else None, '{:.1f}'):>6} {f(dS, '{:.0f}'):>5} {f(t1, '{:.0f}'):>8} "
          f"{f(t01, '{:.0f}'):>10} {basis:>10} {f(wc):>5} {f(heat, '{:.1f}'):>7} {f(r['h2o_50rh'], '{:.1f}'):>5}  {window}")
    out.append(dict(name=r["name"], cls=r["kind"], T_a=r["T_a"], score=r["score"], central=r["central_med"], upper=r["hi"],
                    extrap=r["extrap"], n_doi=r["n_doi"], dH=dH, dS=dS, T80_1kPa=t1, T80_01kPa=t01, basis=basis,
                    wc100=wc, heat100=heat, h2o50=r["h2o_50rh"], doi=r["doi"], year=r["year"], window=window,
                    dH_raw=r["dH"], dS_raw=r.get("dS")))
json.dump(out, open(os.path.join(HERE, "final_candidates.json"), "w"), indent=1)

print(f"\nZeolite 13X benchmark: literature papers with a point within 25x of 42.56 Pa: score {next(r for r in rows if r['name'] == 'Zeolite 13X')['score']:.3f} mol/kg "
      f"(7 papers, 293-303 K); NIST/VAMAS 2026 interlaboratory set at 25 C: median {statistics.median(nist):.3f} mol/kg over {len(nist)} isotherms")

print("\nSame-paper comparison for 10.1016/j.micromeso.2018.12.002 (binderless X microspheres), uptake at 42.56 Pa and 298 K")
for k in s3.amb:
    if k["doi"] == "10.1016/j.micromeso.2018.12.002":
        u = k["u"]
        print(f"  {k['name'][:30]:30} file {k['file'][-10:]}: class {u['kind']}, lower {u['lo']:.3f}, central {u['central']:.3f}, upper {u['hi']:.3f}, first point {u['extrap']:.1f}x")

print("\nVerifier cycle for the one adsorbent inside the strict window (PEI-MonoSil; dry, no water co-desorption):")
r = next(r for r in rows if r["name"] == "PEI-MonoSil")
for Td in (373.15, 393.15):
    for water in (0.0, 2.0):
        cyc = TVSACycle(dH=r["dH"], dS=r["dS"], q_max=r["qmax_eff"], T_des=Td, p_des=1.0e3, water_coads=water)
        print(f"  T_des {Td - 273.15:.0f} C, water co-desorbed {water:.0f} mol/mol: working capacity {cyc.working_capacity:.2f} mol/kg, "
              f"heat {cyc.heat_gj_per_t:.2f} GJ/t (reaction {gj_per_tonne(cyc.reaction_heat):.2f}, sensible {gj_per_tonne(cyc.sensible_heat):.2f}, "
              f"water {gj_per_tonne(cyc.water_heat):.2f}), work-equivalent {cyc.work_equivalent_gj_per_t:.2f} GJ/t, "
              f"second-law efficiency {cyc.second_law_efficiency:.0%}; sorbent cost at $20/kg: "
              f"${sorbent_cost_per_tonne(20, cyc.working_capacity, 2000):.0f}/t at 2,000 cycles, ${sorbent_cost_per_tonne(20, cyc.working_capacity, 20000):.0f}/t at 20,000")

print("\nPhysisorbents with measured dH: verifier swing if the desorption CO2 partial pressure is lowered to 0.1 kPa (dry)")
for nm in ("Zeolite 13X", "SIFSIX-3-Zn", "Mg-MOF-74"):
    r = next(r for r in rows if r["name"] == nm)
    for Td, pdes in ((373.15, 1.0e3), (373.15, 100.0), (353.15, 100.0)):
        cyc = TVSACycle(dH=r["dH"], dS=r["dS"], q_max=r["qmax_eff"], T_des=Td, p_des=pdes)
        if cyc.working_capacity > 1e-3:
            print(f"  {nm:12} T_des {Td - 273.15:.0f} C, p_des {pdes:.0f} Pa: working capacity {cyc.working_capacity:.3f} mol/kg, heat {cyc.heat_gj_per_t:.1f} GJ/t, "
                  f"work-equivalent {cyc.work_equivalent_gj_per_t:.1f} GJ/t; sorbent at $20/kg, 20,000 cycles: ${sorbent_cost_per_tonne(20, cyc.working_capacity, 20000):.0f}/t")
        else:
            print(f"  {nm:12} T_des {Td - 273.15:.0f} C, p_des {pdes:.0f} Pa: working capacity {cyc.working_capacity:.3f} mol/kg (no useful swing)")
