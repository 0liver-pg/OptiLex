# Adversarial (upper) values of channel-subset minima at canonical B=0: which subsets carry the joint obstruction?
import numpy as np, json, sys, time
from scipy.optimize import differential_evolution, minimize
sys.path.insert(0,'/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline'); import fastcyl
k=np.pi/2; L=16; radii=list(np.linspace(1,3,L+1)); ks=np.array([k]); em=6.0
def chan(e):
    n,b=fastcyl.coeffs_pec_real_tm(np.asarray(e).reshape(L,1),radii,ks); b=b[:,0]; N=(len(n)-1)//2
    w=4/k*np.abs(b)**2; return np.array([w[N]]+[w[N+j]+w[N-j] for j in range(1,10)])
subsets=[(0,3),(0,4),(0,3,4),(0,1,3,4),(0,1,2),(0,1,2,3),(0,1,2,3,4),(0,1,2,3,4,5,6,7,8,9)]
out=[]
for S in subsets:
    t=time.time(); f=lambda e: float(chan(e)[list(S)].sum())
    r=differential_evolution(f,[(1,em)]*L,seed=2,maxiter=80,popsize=10,tol=1e-12,polish=True)
    best=r; rng=np.random.default_rng(1)
    for s in range(15):
        rr=minimize(f,rng.choice([1.0,em],L),bounds=[(1,em)]*L,method='L-BFGS-B')
        if rr.fun<best.fun: best=rr
    c=chan(best.x)
    out.append(dict(subset=S,value=best.fun,channels=list(c),eps=list(best.x)))
    print(S, 'min found', round(best.fun,4), 'channels', np.round(c[:6],3), f'{time.time()-t:.0f}s', flush=True)
    json.dump(out,open('subset_adversary.json','w'),indent=1)
