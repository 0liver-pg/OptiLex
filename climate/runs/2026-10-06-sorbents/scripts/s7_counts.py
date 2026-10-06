"""Step 7: coverage counts quoted in the report."""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import contextlib, importlib.util, io, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("s3", os.path.join(HERE, "s3_screen.py"))
s3 = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(s3)
rows = json.load(open(os.path.join(HERE, "screen_rows.json")))
near = {k["hashkey"] for k in s3.amb if k["u"]["extrap"] <= 25}
nearA = {k["hashkey"] for k in s3.amb if k["u"]["kind"] == "A"}
print("adsorbents with a 420 ppm bracket:", len(rows))
print("adsorbents with at least one isotherm resolved within one decade either side of 42.56 Pa (class A):", len(nearA))
print("adsorbents with a first resolved point within 25x of 42.56 Pa (class A or B):", len(near), f"= {len(near) / len(rows):.1%}")
nonnist = [k for k in s3.amb if k["doi"] != "10.1007/s10450-026-00701-3"]
print("class A isotherms outside the NIST 2026 13X set:", sum(1 for k in nonnist if k["u"]["kind"] == "A"), "of", len(nonnist))
with_dH = sum(1 for r in rows if r["dH"] is not None)
print("adsorbents with a bracket and a Clausius-Clapeyron dH:", with_dH)
real = [r for r in rows if not r["sim_suspect"] and not r["pscale_suspect"] and not (r["noisy_low"] and r["flag_units"]) and not r["name"].startswith("NIST RGTM")]
for thr in (0.1, 0.2, 0.5, 1.0):
    print(f"after exclusions: adsorbents with guaranteed uptake >= {thr} mol/kg: {sum(1 for r in real if r['score'] >= thr)}; "
          f"with upper bound >= {thr}: {sum(1 for r in real if r['hi'] >= thr)}")
med = sorted(r["dS"] for r in rows if r.get("dS") is not None and r["dH_same_paper"] and -250 < r["dS"] < -50)
print(f"mapped adsorption entropies (same-paper dH, -250 < dS < -50), n={len(med)}: median {med[len(med)//2]:.0f} J/mol/K, "
      f"10th-90th percentile {med[int(0.1*len(med))]:.0f} to {med[int(0.9*len(med))]:.0f}")
