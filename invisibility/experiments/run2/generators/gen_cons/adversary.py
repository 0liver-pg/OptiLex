import sys, json, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d as c
from scipy.optimize import differential_evolution, minimize
pts = [(np.pi/2, 1.5, 2), (0.5, 3.0, 2), (0.5, 1.5, 6), (0.5, 1.5, 20)]
L = 8; out = {}
for k, b, em in pts:
    radii = list(np.linspace(1, b, L+1))
    f = lambda e: c.widths(np.sqrt(np.asarray(e, complex)), radii, k, pol='TM', core='pec')[1]
    bare = c.widths([], [1.0], k, pol='TM', core='pec')[1]
    r = differential_evolution(f, [(1, em)]*L, seed=0, maxiter=60, popsize=12, tol=1e-8, polish=True)
    best = r.fun; x = r.x
    for e0 in [[em]*L, [1]*L, [em]*(L//2)+[1]*(L//2)]:
        rr = minimize(f, e0, method='L-BFGS-B', bounds=[(1, em)]*L)
        if rr.fun < best: best, x = rr.fun, rr.x
    print(f"ka={k:.3f} b/a={b} eps_max={em}: bare={bare:.4f} best layered={best:.4f} ratio={best/bare:.4f} eps={np.round(x,2)}", flush=True)
    out[f"{k:.4f}_{b}_{em}"] = dict(bare=bare, best=float(best), ratio=float(best/bare), eps=list(map(float, x)))
json.dump(out, open('adversary.json', 'w'), indent=1)
