"""Step 1: read the NIST ISODB tarball in place, keep single-component CO2 and H2O isotherms, cache compactly.

The 18.3 MB tarball was deleted after extraction (disk limit); the cache co2_h2o_isotherms.pkl is what the later
steps read. To rebuild the cache, re-download first:
    curl -sSL -o isodb.tar.gz https://codeload.github.com/NIST-ISODB/isodb-library/tar.gz/refs/heads/master
Pipeline order: s1_extract.py -> s3_screen.py (writes screen_rows.json) -> s5_checks.py, s6_final.py, s7_counts.py.
"""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import collections
import json
import os
import pickle
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
TAR = os.path.join(HERE, "isodb.tar.gz")
CO2 = "CURLTUGMZLYLDI-UHFFFAOYSA-N"
H2O = "XLYOFNOQVPJJNP-UHFFFAOYSA-N"

n_iso = 0
keep = []
adsorbents = {}
bib = {}
counts = collections.Counter()
with tarfile.open(TAR, "r:gz") as tf:
    for m in tf:
        if not (m.isfile() and m.name.endswith(".json") and "/Library/" in m.name):
            continue
        try:
            d = json.load(tf.extractfile(m))
        except Exception:
            counts["json decode error"] += 1
            continue
        if "/Library/Adsorbents/" in m.name:
            adsorbents[d.get("hashkey")] = dict(name=d.get("name"), formula=d.get("formula"),
                                                synonyms=d.get("synonyms"))
            continue
        if "/Library/Bibliography/" in m.name:
            bib[d.get("DOI")] = dict(title=d.get("title"), year=d.get("year"), journal=d.get("journal"),
                                     authors=d.get("authors"), categories=d.get("categories"))
            continue
        if "isotherm_data" not in d:
            continue
        n_iso += 1
        ads = d.get("adsorbates") or []
        if len(ads) != 1:
            counts["multi-component or none"] += 1
            continue
        key = ads[0].get("InChIKey")
        if key not in (CO2, H2O):
            continue
        gas = "CO2" if key == CO2 else "H2O"
        counts[gas] += 1
        pts = []
        for row in d["isotherm_data"]:
            try:
                p = float(row["pressure"])
                q = float(row.get("total_adsorption", row["species_data"][0]["adsorption"]))
            except Exception:
                continue
            pts.append((p, q))
        keep.append(dict(
            gas=gas, file=d.get("filename"), doi=d.get("DOI"),
            name=(d.get("adsorbent") or {}).get("name"), hashkey=(d.get("adsorbent") or {}).get("hashkey"),
            T=d.get("temperature"), p_units=d.get("pressureUnits"), q_units=d.get("adsorptionUnits"),
            category=d.get("category"), iso_type=d.get("isotherm_type"), tabular=d.get("tabular_data"),
            pts=pts))

print("isotherm files read:", n_iso, "| adsorbent records:", len(adsorbents), "| bibliography records:", len(bib))
print("counts:", dict(counts))
for gas in ("CO2", "H2O"):
    sub = [k for k in keep if k["gas"] == gas]
    print(f"\n== {gas}: {len(sub)} single-component isotherms")
    print(" pressure units:", collections.Counter(k["p_units"] for k in sub).most_common(8))
    print(" adsorption units:", collections.Counter(k["q_units"] for k in sub).most_common(12))
    print(" category:", collections.Counter(k["category"] for k in sub).most_common(8))
    print(" distinct adsorbent hashkeys:", len({k["hashkey"] for k in sub}))
    print(" distinct DOIs:", len({k["doi"] for k in sub}))

with open(os.path.join(HERE, "co2_h2o_isotherms.pkl"), "wb") as f:
    pickle.dump(dict(isotherms=keep, adsorbents=adsorbents, bib=bib), f)
print("\ncache written:", round(os.path.getsize(os.path.join(HERE, "co2_h2o_isotherms.pkl")) / 1e6, 2), "MB")
yrs = collections.Counter()
for k in keep:
    if k["gas"] == "CO2":
        y = (bib.get(k["doi"]) or {}).get("year")
        yrs[y] += 1
print("CO2 isotherms by publication year:", sorted(yrs.items(), key=lambda kv: (kv[0] is None, kv[0])))
