"""Screen 1 (gen-2 computational): CO2 binding on the HYDRATED framework from ODAC23 co-adsorption energies.

Descriptor (reference-error-free): E_CO2|H2O = min E_ads(CO2+H2O) - min E_ads(H2O)
  = E(MOF+CO2+H2O) - E(MOF+H2O) - E(CO2); the empty-MOF energy (ODAC23's known flaw) cancels.
Cooperativity: dE_coop = min E(CO2+H2O) - min E(CO2) - min E(H2O) (gas-phase CO2-H2O dimer is about -12 kJ/mol).
Rules fixed before reading results:
  - pristine only (no _x.xx_y missing-linker suffix, no 'charged' tag); >=2 placements each for CO2, H2O, CO2+H2O
  - drop placements with |E/n_molecules| > 2 eV (ODAC23's own artifact cut) and hosts whose min per-molecule E < -1.0 eV (reactive/artifact)
  - water present at 50% RH, 25 C: E_H2O <= -45 kJ/mol (half-fill with dS_H2O -119 J/mol/K needs dH about -45.7)
  - humid window: dH = E_CO2|H2O + 1.3 kJ/mol inside the verifier window for dS = -113 (physisorption-calibrated)
    or dS = -165 (amine-like), i.e. >=20% fill at 420 ppm/25 C and <=20% residual at 1 kPa CO2 by 120 C
"""
import sys; sys.path.insert(0, 'climate'); from physics import *; from sorbent import *
import re, collections, csv, json, math, os
import numpy as np
from scipy.optimize import brentq
HERE = os.path.dirname(os.path.abspath(__file__))
EV = 96.485  # kJ/mol per eV
N_MOL = {'CO2': 1, 'H2O': 1, 'CO2_H2O': 2, 'CO2_2H2O': 3}

E = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(os.path.join(HERE, 'adsorption_energy.txt')):
    n, e = line.split(); e = float(e)
    m = re.match(r'(.+)_w_(CO2_2H2O|CO2_H2O|CO2|H2O)(?:_random)?_(\d+|new)$', n)
    if not m: continue
    h, a, _ = m.groups()
    if abs(e / N_MOL[a]) > 2.0: continue
    E[h][a].append(e)

def pristine(h): return not re.search(r'_\d\.\d+_\d+$', h) and 'charged' not in h

def window(dS, Tdes=393.15, pdes=1e3):
    lo = brentq(lambda dH: loading(P_CO2_AIR, T0, dH, dS, 1) - 0.2, -150e3, -1e3)   # weakest allowed
    hi = brentq(lambda dH: loading(pdes, Tdes, dH, dS, 1) - 0.2, -150e3, -1e3)      # strongest allowed
    return hi / 1e3, lo / 1e3   # (strong end, weak end) in kJ/mol
W113, W165 = window(-113.0), window(-165.0)
print(f"verifier windows (dH, kJ/mol): dS=-113 {W113[0]:.1f}..{W113[1]:.1f}; dS=-165 {W165[0]:.1f}..{W165[1]:.1f}")

rows = []
for h, d in E.items():
    if not all(len(d[a]) >= 2 for a in ('CO2', 'H2O', 'CO2_H2O')): continue
    eco2, eh2o, eco = min(d['CO2']) * EV, min(d['H2O']) * EV, min(d['CO2_H2O']) * EV
    e2 = min(d['CO2_2H2O']) * EV if d['CO2_2H2O'] else None
    permol_min = min(eco2, eh2o, eco / 2, (e2 / 3) if e2 else 0)
    rows.append(dict(host=h, pristine=pristine(h), E_CO2=eco2, E_H2O=eh2o, E_CO2H2O=eco, E_CO22H2O=e2,
                     cond=eco - eh2o, coop=eco - eco2 - eh2o,
                     cond2=(e2 - eco) if e2 is not None else None,   # 2nd water given CO2+H2O present
                     artifact=permol_min < -1.0 * EV, nplace=(len(d['CO2']), len(d['H2O']), len(d['CO2_H2O']))))
pr = [r for r in rows if r['pristine'] and not r['artifact']]
print(f"hosts with >=2 placements each: {len(rows)}; pristine {sum(r['pristine'] for r in rows)}; pristine non-artifact {len(pr)}")

coop = np.array([r['coop'] for r in pr])
print(f"cooperativity dE_coop (kJ/mol), pristine: median {np.median(coop):+.1f}, 10th pct {np.percentile(coop,10):+.1f}, "
      f"90th {np.percentile(coop,90):+.1f}; < -12 (beyond gas dimer): {(coop<-12).sum()}; < -25: {(coop<-25).sum()}")

def inwin(dH, w): return w[0] <= dH <= w[1]
def report(label, w):
    dry = [r for r in pr if inwin(r['E_CO2'] + 1.3, w)]
    wet_present = [r for r in pr if r['E_H2O'] <= -45.0]
    hum = [r for r in wet_present if inwin(r['cond'] + 1.3, w)]
    assisted = [r for r in hum if not inwin(r['E_CO2'] + 1.3, w) and r['E_CO2'] + 1.3 > w[1]]  # too weak dry, in window wet
    print(f"\n[{label}] window dH {w[0]:.1f}..{w[1]:.1f}: dry raw in-window {len(dry)}; water present at 50% RH (E_H2O<=-45): {len(wet_present)}; "
          f"humid (CO2 on hydrated site) in-window {len(hum)}; of these too weak when dry (water-ASSISTED): {len(assisted)}")
    return hum, assisted
hum113, as113 = report('dS=-113', W113)
hum165, as165 = report('dS=-165', W165)

# join CoRE metadata
meta = {}
with open(os.path.join(HERE, '..', 'core2019_asr_public.csv')) as f:
    for r in csv.DictReader(f):
        key = r['filename'].replace('_clean', '').split('_')[0] if r['filename'] else ''
        meta.setdefault(key, r); meta.setdefault(r['filename'].replace('_clean',''), r)
def md(h):
    r = meta.get(h) or meta.get(h.split('_')[0]) or {}
    return r.get('All_Metals', '?'), r.get('PLD', '?'), r.get('Has_OMS', '?')

def show(lst, title, n=25):
    print(f"\n{title} (sorted by cooperativity)")
    print(f"{'host':<34}{'metals':<10}{'PLD':>6}{'OMS':>5}{'E_CO2':>8}{'E_H2O':>8}{'CO2|H2O':>9}{'coop':>7}{'2ndH2O|CO2+H2O':>16}  placements")
    for r in sorted(lst, key=lambda r: r['coop'])[:n]:
        m, p, o = md(r['host'])
        c2 = f"{r['cond2']:.1f}" if r['cond2'] is not None else '-'
        try: p = f"{float(p):.1f}"
        except: pass
        print(f"{r['host']:<34}{m:<10}{p:>6}{o:>5}{r['E_CO2']:8.1f}{r['E_H2O']:8.1f}{r['cond']:9.1f}{r['coop']:7.1f}{c2:>16}  {r['nplace']}")
show(as113, 'WATER-ASSISTED, physisorption window dS=-113')
show(as165, 'WATER-ASSISTED, amine-like window dS=-165')
json.dump(dict(pr=pr, as113=as113, as165=as165, hum113=hum113, hum165=hum165), open(os.path.join(HERE, 's1_results.json'), 'w'), default=str)
