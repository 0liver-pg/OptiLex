import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
"""Follow-up checks on the ODAC23 shortlist:
 (1) measured CO2 loadings quoted in the ODAC23 paper (Table 2) vs the DFT energies, through the verifier's Langmuir site;
 (2) pristine parents of the Tier-A defective structures;
 (3) structural sanity of shortlisted CIFs (carbon present but no hydrogen = broken model)."""
import collections, json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
EV = 96.48533
res = json.load(open(os.path.join(HERE, "odac23_screen_results.json")))
DS = res["DS_PHYS"]; DELTA = res["DELTA_CO2"]; lo, hi = res["window_primary_kJ"]

# ---- raw data again (small) ----
hosts = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(os.path.join(HERE, "odac23_adsorption_energy.txt")):
    name, e = line.split(); e = float(e)
    host, ads = name.rsplit("_w_", 1)
    kind = re.fullmatch(r"(CO2_2H2O|CO2_H2O|CO2|H2O)(?:_(random|new))?(?:_(\d+))?", ads).group(1)
    n = {"CO2": 1, "H2O": 1, "CO2_H2O": 2, "CO2_2H2O": 3}[kind]
    if abs(e / n) < 2.0:
        hosts[host][kind].append((e, name))
import csv
eint = {r["name"]: float(r["E_int_eV"]) for r in csv.DictReader(open(os.path.join(HERE, "odac23_eint_compact.csv")))}


def corrected(host, kind):
    out = []
    for e, name in hosts[host].get(kind, []):
        if name not in eint: out.append((e, "unverified"))
        elif e - eint[name] < -0.05: out.append((eint[name], "refcorr"))
        elif e - eint[name] > 0.05: out.append((e, "distort"))
        else: out.append((e, "ok"))
    return min(out) if out else (None, None)


print("=" * 100)
print("1. MEASURED LOADINGS (ODAC23 paper Table 2; pure CO2, dry) vs DFT, via a two-point Langmuir fit and the calibrated entropy")
print(f"   (dS = {DS:.0f} J/mol/K; window dH {lo:.1f} .. {hi:.1f} kJ/mol)")
# host, name, T (K), q at 150 mbar, q at 1 bar (mmol/g)
MEAS = [("QEFNAQ", "Cu(2-pymo)2 sodalite (Navarro 2006)", 293.15, 0.4, 1.0),
        ("QOVSOL", "Cd mixed-ligand polymer (Hua 2022)", 298.15, 0.1, 0.2),
        ("FECXES", "Cu MOF, flexible linker (Xue 2012)", 273.15, 1.6, 6.3)]
for host, nm, T, q15, q100 in MEAS:
    p1, p2 = 0.15e5, 1.0e5
    # q = qm b p / (1 + b p) through both points
    b = (q100 / p2 - q15 / p1) / (q15 - q100)            # 1/Pa
    qm = q100 * (1 + b * p2) / (b * p2)
    dG = -R * T * math.log(b * P_REF)
    dH_meas = (dG + T * DS) / 1e3
    q420 = qm * loading(P_CO2_AIR, T0, dH_meas * 1e3, DS, 1.0)
    raw = min(hosts[host]["CO2"])[0] * EV
    ec, st = corrected(host, "CO2")
    print(f"   {host:<7} {nm:<38} T {T:.0f} K: fit q_max {qm:.2f} mmol/g, b {b*1e5:.2f} /bar -> implied dH {dH_meas:6.1f} kJ/mol; "
          f"extrapolated uptake at 420 ppm, 25 C: {q420:.4f} mmol/g")
    print(f"           DFT raw {raw + DELTA:6.1f}, reference-corrected {ec*EV + DELTA:6.1f} [{st}] kJ/mol (as dH); "
          f"measured-implied value is {'INSIDE' if lo <= dH_meas <= hi else 'OUTSIDE'} the window")

print("\n" + "=" * 100)
print("2. PRISTINE PARENTS OF THE TIER-A DEFECTIVE STRUCTURES (kJ/mol, corrected CO2 energy and raw H2O margin)")
for r in res["tierA_primary"]:
    par = re.sub(r"_0\.\d+_\d$", "", r["host"])
    if par not in hosts or not hosts[par].get("CO2"):
        print(f"   {r['host']:<26} parent {par}: no CO2 data"); continue
    ec, st = corrected(par, "CO2")
    raw = min(hosts[par]["CO2"])[0]
    w = min(hosts[par]["H2O"])[0] if hosts[par].get("H2O") else None
    dH = ec * EV + DELTA
    verdict = "IN WINDOW" if lo <= dH <= hi else ("too strong" if dH < lo else "too weak")
    fill = loading(P_CO2_AIR, T0, dH * 1e3, DS, 1.0)
    sibs = sorted(h for h in hosts if h != r["host"] and re.sub(r"_0\.\d+_\d$", "", h) == par and h != par)
    sib_txt = "; ".join(f"{h.replace(par, '')}: {corrected(h, 'CO2')[0]*EV:.1f}[{corrected(h, 'CO2')[1][:3]}]" for h in sibs if hosts[h].get("CO2"))
    print(f"   {r['host']:<26} defective corrected {r['Ec_CO2']*EV:6.1f} | parent {par}: raw {raw*EV:6.1f}, corrected {ec*EV:6.1f} [{st}], "
          f"E_H2O {w*EV if w is not None else float('nan'):6.1f}, dH {dH:6.1f}, fill at 420 ppm {fill:.3f} -> {verdict}"
          + (f" | other defect variants: {sib_txt}" if sib_txt else ""))

print("\n" + "=" * 100)
print("3. STRUCTURE SANITY OF SHORTLISTED CIFs (from the ODAC23 promising-MOF archives)")
forms = json.load(open(os.path.join(HERE, "odac23_candidate_formulas.json")))
for r in res["tierA_primary"] + res["tierB_primary"]:
    f = forms.get(r["host"])
    if not f:
        print(f"   {r['host']:<26} tier {r['tier']}: no CIF available here"); continue
    has_c = re.search(r"\bC\d+", f["formula"]) is not None
    has_h = re.search(r"\bH\d+", f["formula"]) is not None
    flag = "CARBON BUT NO HYDROGEN -> suspect/broken model" if (has_c and not has_h) else ("inorganic (no carbon)" if not has_c else "ok")
    print(f"   {r['host']:<26} tier {r['tier']}: {f['formula']:<44} density {f['density']:.2f} g/cm3 -> {flag}")

print("\n" + "=" * 100)
print("4. VERIFIER CYCLE IF THE STRONG SITE EXISTS ONLY AT THE DEFECT (1 or 2 sites per simulation cell), 100 C, 1 kPa CO2, no water")
MASS = dict(H=1.008, C=12.011, N=14.007, O=15.999, F=18.998, S=32.06, P=30.974, Si=28.086, Li=6.94, Fe=55.845, Cu=63.546, Zn=65.38, Ga=69.723, Ti=47.867)
ref = reference_amine_cycle()
print(f"   amine reference: wc {ref.working_capacity:.2f} mol/kg, heat {ref.heat_gj_per_t:.2f} GJ/t, sorbent ${sorbent_cost_per_tonne(20, ref.working_capacity, 2000):.0f}/t at $20/kg and 2,000 cycles")
for r in res["tierA_primary"]:
    f = forms[r["host"]]
    m = sum(MASS[e] * int(n) for e, n in re.findall(r"([A-Z][a-z]?)(\d+)", f["formula"]))   # g per mol of cells
    for nsite in (1, 2):
        qmax = nsite / m * 1e3
        c = TVSACycle(dH=r["dH"] * 1e3, dS=DS, q_max=qmax, T_des=373.15, p_des=1.0e3)
        print(f"   {r['host']:<26} cell mass {m:6.0f} g/mol, {nsite} site(s)/cell -> q_max {qmax:.2f} mol/kg, wc {c.working_capacity:.3f} mol/kg, "
              f"heat {c.heat_gj_per_t:6.1f} GJ/t (sensible {gj_per_tonne(c.sensible_heat):6.1f}), sorbent ${sorbent_cost_per_tonne(20, c.working_capacity, 2000):,.0f}/t at $20/kg, 2,000 cycles")
