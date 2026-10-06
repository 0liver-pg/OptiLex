"""Step 2: explore low-pressure coverage of the CO2 isotherms near ambient temperature."""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import collections
import os
import pickle

HERE = os.path.dirname(os.path.abspath(__file__))
D = pickle.load(open(os.path.join(HERE, "co2_h2o_isotherms.pkl"), "rb"))
iso = D["isotherms"]
p_air_bar = P_CO2_AIR / 1e5
print("P_CO2_AIR =", P_CO2_AIR, "Pa =", p_air_bar, "bar")

MASS_UNITS = {"mmol/g", "mol/kg", "cm3(STP)/g", "mg/g", "mol/g", "mmol/kg", "g/g", "wt%", "ml/g", "ml(STP)/g"}
co2 = [k for k in iso if k["gas"] == "CO2"]
amb = [k for k in co2 if isinstance(k["T"], (int, float)) and 288 <= k["T"] <= 308]
print("CO2 isotherms:", len(co2), "| 288-308 K:", len(amb))
ok = [k for k in amb if k["q_units"] in MASS_UNITS and len(k["pts"]) >= 3]
print("  mass-based units and >=3 points:", len(ok))
print("  category:", collections.Counter(k["category"] for k in ok))
for thr in (p_air_bar, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1):
    n = 0
    hk = set()
    for k in ok:
        ps = [p for p, q in k["pts"] if p > 0 and q > 0]
        if ps and min(ps) <= thr:
            n += 1
            hk.add(k["hashkey"])
    print(f"  lowest positive pressure <= {thr:.5g} bar: {n} isotherms, {len(hk)} adsorbents")
# multi-temperature sets (same DOI, same adsorbent)
sets = collections.defaultdict(set)
for k in co2:
    if isinstance(k["T"], (int, float)) and 250 <= k["T"] <= 400 and k["q_units"] in MASS_UNITS:
        sets[(k["doi"], k["hashkey"])].add(round(k["T"]))
multi = {s: t for s, t in sets.items() if max(t) - min(t) >= 10}
print("DOI x adsorbent sets:", len(sets), "| with temperature span >= 10 K:", len(multi))
# the isotherms with the most low-pressure information
rows = []
for k in ok:
    ps = sorted(p for p, q in k["pts"] if p > 0 and q > 0)
    if ps and ps[0] <= 1e-3:
        rows.append((ps[0], k["name"], k["T"], k["q_units"], k["category"], k["doi"], len(ps)))
rows.sort()
for r in rows[:60]:
    print(r)
