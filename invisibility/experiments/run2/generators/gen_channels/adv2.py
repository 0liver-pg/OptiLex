import numpy as np, json, sys, time
from scipy.optimize import differential_evolution, minimize
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim'); sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import cloak2d, fastcyl
pts=[(np.pi/2,1.25,6),(np.pi/2,1.5,4),(np.pi/2,1.5,6),(np.pi/2,2.0,2),(np.pi/2,2.0,4),(1.0,2.0,2),(1.0,3.0,2),(3.0,1.5,2),(0.5,3.0,2),(np.pi/2,3.0,2)]
fl={ (round(d['ka'],3),d['ba'],d['eps_max']):d['floor_ratio'] for d in json.load(open('perchannel_floor_sweep.json'))}
out=[]
for ka,ba,em in pts:
    t=time.time(); L=8; radii=list(np.linspace(1,ba,L+1)); bare=cloak2d.widths([],[1.0],ka,core='pec')[1]
    ks=np.array([ka])
    def f(e):
        n,b=fastcyl.coeffs_pec_real_tm(np.asarray(e).reshape(L,1),radii,ks); return float(4/ka*np.sum(np.abs(b)**2))
    r=differential_evolution(f,[(1,em)]*L,seed=1,maxiter=60,popsize=12,tol=1e-12,polish=True)
    best=r
    rng=np.random.default_rng(0)
    for s in range(20):
        x0=rng.choice([1.0,em],L) if s<10 else rng.uniform(1,em,L)
        rr=minimize(f,x0,bounds=[(1,em)]*L,method='L-BFGS-B')
        if rr.fun<best.fun: best=rr
    val=cloak2d.widths(list(np.sqrt(best.x)),radii,ka,core='pec')[1]
    R=val/bare; F=fl[(round(ka,3),ba,em)]
    out.append(dict(ka=ka,ba=ba,eps_max=em,best_R_cloak2d=R,floor=F,gap=(R/F if F>0 else None),eps=list(best.x),L=L))
    print(f"ka={ka:.3f} b/a={ba} em={em}: best layered R={R:.4f} floor={F:.4f} gap={R/F if F>0 else float('nan'):.3f} ({time.time()-t:.0f}s)",flush=True)
    json.dump(out,open('perchannel_gap_check.json','w'),indent=1)
