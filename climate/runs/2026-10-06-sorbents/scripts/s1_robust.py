import json, re, collections, numpy as np, os
HERE=os.path.dirname(os.path.abspath(__file__)); EV=96.485
N={'CO2':1,'H2O':1,'CO2_H2O':2,'CO2_2H2O':3}
E=collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(os.path.join(HERE,'adsorption_energy.txt')):
    n,e=line.split(); e=float(e)
    m=re.match(r'(.+)_w_(CO2_2H2O|CO2_H2O|CO2|H2O)(_random)?_(\d+|new)$',n)
    if not m: continue
    h,a,r,_=m.groups()
    if abs(e/N[a])>2: continue
    E[h][a].append(e*EV)
res=json.load(open(os.path.join(HERE,'s1_results.json')))
def robust(h, tol=5.0):
    d=E[h]; w=sorted(d['H2O']); cw=sorted(d['CO2_H2O'])
    # require the water minimum to be found at least twice within tol, and the CO2+H2O minimum likewise
    return len(w)>=2 and w[1]-w[0]<=tol and len(cw)>=2 and cw[1]-cw[0]<=tol
for key in ('as113','as165','hum113','hum165'):
    L=res[key]; R=[r for r in L if robust(r['host'])]
    print(f"{key}: {len(L)} -> {len(R)} with water and CO2+H2O minima each reproduced by a 2nd placement within 5 kJ/mol")
    for r in sorted(R,key=lambda r:r['coop'])[:8]:
        print(f"    {r['host']:<18} E_CO2 {r['E_CO2']:6.1f} E_H2O {r['E_H2O']:6.1f} CO2|H2O {r['cond']:6.1f} coop {r['coop']:6.1f}")
# controls: do duplicates agree after robustness filter?
for h in ['FIQCEN','XAMDUM','XAMDUM02','XAMDUM04','XAMDUM05','XAMDUM06','XAMDUM07','VOGTIV_clean_h']:
    print(h, 'robust' if robust(h) else 'NOT robust', [round(x,1) for x in sorted(E[h]['H2O'])[:3]], [round(x,1) for x in sorted(E[h]['CO2_H2O'])[:3]])
