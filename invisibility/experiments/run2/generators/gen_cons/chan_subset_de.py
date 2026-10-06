# Design-side estimate: min over layered eps in [1,6] (L=16) of sum_{|n|<=Nc} sigma_|n| at k_c (B=0), Nc = 1, 2.
import numpy as np, sys, json, time
from scipy.optimize import differential_evolution, minimize
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
k = np.pi/2; L = 16; radii = list(np.linspace(1, 3, L + 1))
def sig(eps, Nc):
    n, b = fastcyl.coeffs_pec_real_tm(np.asarray(eps)[:, None], radii, np.array([k]))
    b = b[:, 0]; s = 0.0
    for nn in range(Nc + 1):
        s += (4/k)*(1 if nn == 0 else 2)*abs(b[n == nn][0])**2
    return s
out = {}
for Nc in (0, 1, 2):
    t0 = time.time()
    r = differential_evolution(lambda e: sig(e, Nc), [(1, 6)]*L, seed=1, maxiter=300, popsize=20, tol=1e-10, polish=True)
    out[Nc] = dict(val=float(r.fun), eps=np.round(r.x, 3).tolist(), sec=round(time.time() - t0, 1))
    print(Nc, out[Nc], flush=True)
json.dump(out, open('chan_subset_de.json', 'w'), indent=1)
