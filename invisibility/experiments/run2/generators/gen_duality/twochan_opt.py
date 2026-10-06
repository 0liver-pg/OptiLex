"""Primal check for the DP: minimise sigma_0 + sigma_1 (and +sigma_2) at k_c over layered eps in [1,6]."""
import sys, numpy as np, time
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
from scipy.optimize import minimize, differential_evolution
kc = np.pi / 2
def obj(e, chans, L):
    radii = list(np.linspace(1, 3, L + 1))
    n, b = fastcyl.coeffs_pec_real_tm(np.asarray(e)[:, None], radii, np.array([kc]), N=max(chans))
    b = b[:, 0]
    return sum((4 / kc) * np.sum(np.abs(b[np.abs(n) == c]) ** 2) for c in chans)
if __name__ == '__main__':
    import time as _t
    e = np.random.uniform(1, 6, 16); t0 = _t.time(); [obj(e, (0, 1, 2), 16) for _ in range(50)]; print('ms/eval', (_t.time() - t0) / 50 * 1e3, flush=True)
    rng = np.random.default_rng(0)
    for chans in [(0, 1), (0, 1, 2)]:
        for L in [16, 32]:
            t0 = time.time(); best = np.inf; bx = None
            for s in range(40):
                x0 = rng.uniform(1, 6, L)
                rr = minimize(obj, x0, args=(chans, L), bounds=[(1, 6)] * L, method='L-BFGS-B', options={'maxiter': 300})
                if rr.fun < best: best, bx = rr.fun, rr.x
            print(chans, L, 'min=%.5f' % best, 'eps=', np.round(bx, 2), '%.0fs' % (time.time() - t0), flush=True)
