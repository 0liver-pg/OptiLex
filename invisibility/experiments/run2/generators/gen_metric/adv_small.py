import sys, json, numpy as np
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
from scipy.optimize import minimize
k=np.pi/2; L=8; radii=np.linspace(1,3,L+1)
_,bb=fastcyl.coeffs_pec([],[1.0],k); bare=4/k*np.sum(abs(bb)**2)
n0=None
out={}
for em in [1.5,2.0,6.0]:
    best=np.inf
    rng=np.random.default_rng(0)
    for s in range(24):
        f=lambda e: fastcyl.widths_pec(np.sqrt(e),radii,k)[0]
        r=minimize(f, rng.uniform(1,em,L), method='L-BFGS-B', bounds=[(1,em)]*L)
        best=min(best,r.fun)
    # sector
    bests=np.inf
    for s in range(24):
        def fs(e):
            n,b=fastcyl.coeffs_pec(np.sqrt(e),radii,k); return fastcyl.sector_width(b,n,k,np.pi,np.pi/2)
        r=minimize(fs, rng.uniform(1,em,L), method='L-BFGS-B', bounds=[(1,em)]*L)
        bests=min(bests,r.fun)
    nb_,b_=fastcyl.coeffs_pec([],[1.0],k); bs=fastcyl.sector_width(b_,nb_,k,np.pi,np.pi/2)
    out[em]=dict(R_ext=best/bare, R_sector=bests/bs)
    print(em,out[em],flush=True)
json.dump(out,open('adv_small.json','w'),indent=1)
