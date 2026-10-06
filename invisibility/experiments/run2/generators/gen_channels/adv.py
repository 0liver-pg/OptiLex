import numpy as np, json, sys
from scipy.optimize import differential_evolution
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim'); import cloak2d
pts=[(np.pi/2,1.25,6),(np.pi/2,1.5,4),(np.pi/2,1.5,6),(np.pi/2,2.0,2),(np.pi/2,2.0,4),(1.0,2.0,2),(1.0,3.0,2),(3.0,1.5,2),(0.5,3.0,2),(np.pi/2,3.0,2)]
fl={ (round(d['ka'],3),d['ba'],d['eps_max']):d['floor_ratio'] for d in json.load(open('perchannel_floor_sweep.json'))}
out=[]
for ka,ba,em in pts:
    L=8; radii=list(np.linspace(1,ba,L+1)); bare=cloak2d.widths([],[1.0],ka,core='pec')[1]
    f=lambda e: cloak2d.widths(list(np.sqrt(e)),radii,ka,core='pec')[1]
    r=differential_evolution(f,[(1,em)]*L,seed=1,maxiter=150,popsize=15,tol=1e-10,polish=True)
    R=r.fun/bare; F=fl[(round(ka,3),ba,em)]
    out.append(dict(ka=ka,ba=ba,eps_max=em,best_R=R,floor=F,gap=R/F if F>0 else None,eps=list(r.x)))
    print(f"ka={ka:.3f} b/a={ba} em={em}: best layered R={R:.4f}  per-channel floor={F:.4f}  gap={R/F if F>0 else float('nan'):.3f}",flush=True)
json.dump(out,open('perchannel_gap_check.json','w'),indent=1)
