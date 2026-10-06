import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
"""Composition, density and an upper-bound site density for the shortlisted ODAC23 frameworks (from the CIFs that the
ODAC23 authors published for their 'promising' list), plus the survival rate of unverified energies."""
import collections, json, math, os, re, zipfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
MASS = dict(H=1.008, C=12.011, N=14.007, O=15.999, F=18.998, S=32.06, Cl=35.45, Br=79.904, P=30.974, Si=28.086, Li=6.94, B=10.81,
            Na=22.990, Mg=24.305, Al=26.982, K=39.098, Ca=40.078, Sc=44.956, Ti=47.867, V=50.942, Cr=51.996, Mn=54.938, Fe=55.845,
            Co=58.933, Ni=58.693, Cu=63.546, Zn=65.38, Ga=69.723, Ge=72.63, Zr=91.224, Nb=92.906, Mo=95.95, Cd=112.414, In=114.818,
            Sb=121.760, La=138.905, Pr=140.908, Gd=157.25, W=183.84, I=126.904, Sn=118.71, Ag=107.868, Ba=137.327, Sr=87.62,
            Y=88.906, Ce=140.116, Nd=144.242, Sm=150.36, Eu=151.964, Tb=158.925, Dy=162.5, Er=167.259, Yb=173.045, Pb=207.2, Bi=208.98)
METALS = set(MASS) - set("H C N O F S Cl Br P B I".split())


def read_cif(text):
    cell = {}
    for k in ("a", "b", "c"):
        cell[k] = float(re.search(rf"_cell_length_{k}\s+([\d.]+)", text).group(1))
    for k in ("alpha", "beta", "gamma"):
        cell[k] = math.radians(float(re.search(rf"_cell_angle_{k}\s+([\d.]+)", text).group(1)))
    ca, cb, cg = (math.cos(cell[k]) for k in ("alpha", "beta", "gamma"))
    vol = cell["a"] * cell["b"] * cell["c"] * math.sqrt(1 - ca * ca - cb * cb - cg * cg + 2 * ca * cb * cg)
    lines = text.splitlines()
    i = next(n for n, l in enumerate(lines) if l.strip().startswith("_atom_site_"))
    hdr = []
    while lines[i].strip().startswith("_atom_site_"):
        hdr.append(lines[i].strip()); i += 1
    col = hdr.index("_atom_site_type_symbol") if "_atom_site_type_symbol" in hdr else hdr.index("_atom_site_label")
    cnt = collections.Counter()
    for l in lines[i:]:
        p = l.split()
        if len(p) < len(hdr) or l.strip().startswith(("_", "loop_", "#")):
            if cnt: break
            continue
        el = re.match(r"[A-Z][a-z]?", p[col]).group(0)
        cnt[el] += 1
    return vol, cnt


def describe(host, text):
    vol, cnt = read_cif(text)
    mass = sum(MASS[e] * n for e, n in cnt.items())                       # g per mol of cells
    rho = mass / (vol * 1e-24 * 6.02214076e23)                              # g/cm3
    nmet = sum(n for e, n in cnt.items() if e in METALS)
    formula = " ".join(f"{e}{cnt[e]}" for e in sorted(cnt, key=lambda e: (e not in METALS, e)))
    return dict(host=host, formula=formula, natoms=sum(cnt.values()), vol=vol, density=rho,
                mol_metal_per_kg=nmet / mass * 1e3, N_per_metal=cnt.get("N", 0) / max(nmet, 1), F_per_metal=cnt.get("F", 0) / max(nmet, 1))


res = json.load(open(os.path.join(HERE, "odac23_screen_results.json")))
want = [r["host"] for r in res["tierA_primary"]] + [r["host"] for r in res["tierB_primary"]]
found = {}
for z in ("promising_pristine.zip", "promising_defective.zip"):
    with zipfile.ZipFile(os.path.join(HERE, z)) as zf:
        for n in zf.namelist():
            if n.startswith("__MACOSX") or not n.endswith(".cif"): continue
            h = os.path.basename(n)[:-4]
            if h in want:
                found[h] = describe(h, zf.read(n).decode("utf-8", "replace"))
print(f"{'host':<26}{'cell formula':<46}{'atoms':>6}{'rho g/cm3':>10}{'mol metal/kg':>13}{'N/metal':>8}")
for h in want:
    d = found.get(h)
    if d: print(f"{h:<26}{d['formula']:<46}{d['natoms']:>6}{d['density']:>10.2f}{d['mol_metal_per_kg']:>13.2f}{d['N_per_metal']:>8.1f}")
    else: print(f"{h:<26}(no CIF in the ODAC23 promising archives)")
json.dump(found, open(os.path.join(HERE, "odac23_candidate_formulas.json"), "w"), indent=1)

# verifier cycle for the two best-ranked entries, taking one CO2 site per metal atom as an UPPER bound on q_max
print("\nVerifier TVSA cycle (100 C, 1 kPa CO2, no water) with q_max = one site per metal atom (upper bound), dS from calibration:")
for r in (res["tierA_primary"][:4] + res["tierB_primary"][:4]):
    d = found.get(r["host"])
    if not d: continue
    c = TVSACycle(dH=r["dH"] * 1e3, dS=res["DS_PHYS"], q_max=d["mol_metal_per_kg"], T_des=373.15, p_des=1.0e3)
    if c.working_capacity > 0:
        print(f"  {r['host']:<26} tier {r['tier']} q_max<= {d['mol_metal_per_kg']:.2f} mol/kg -> wc {c.working_capacity:.2f} mol/kg, heat {c.heat_gj_per_t:.2f} GJ/t "
              f"(reaction {gj_per_tonne(c.reaction_heat):.2f}, sensible {gj_per_tonne(c.sensible_heat):.2f}), work-eq {c.work_equivalent_gj_per_t:.2f} GJ/t, "
              f"sorbent cost at $20/kg, 2,000 cycles ${sorbent_cost_per_tonne(20, c.working_capacity, 2000):.0f}/t")
