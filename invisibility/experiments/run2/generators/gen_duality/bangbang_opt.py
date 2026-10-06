"""Primal check of the radial channel-subset floors with bang-bang profiles (Pontryagin form): eps in {1, 6}, K switch radii."""
import numpy as np, time, json
from scipy.optimize import minimize
from fastchan import sig_chans
kc, a, b, EM = np.pi / 2, 1.0, 3.0, 6.0
def profile(x, start):
    s = np.sort(np.clip(x, a + 1e-6, b - 1e-6))
    radii = np.concatenate([[a], s, [b]])
    eps = [EM if (i % 2 == 0) == (start == 'hi') else 1.0 for i in range(len(radii) - 1)]
    keep = np.diff(radii) > 1e-9
    return list(np.array(eps)[keep]), list(np.concatenate([[a], radii[1:][keep]]))
def f(x, start, chans):
    e, r = profile(x, start)
    return float(np.sum(sig_chans(e, r, kc, chans)))
rng = np.random.default_rng(1)
res = {}
for chans in [(0, 1), (0, 1, 2), (0, 1, 2, 3)]:
    best = (np.inf, None)
    t0 = time.time()
    for K in [1, 2, 3, 4, 5]:
        for start in ['hi', 'lo']:
            for trial in range(25):
                x0 = np.sort(rng.uniform(a, b, K))
                r = minimize(f, x0, args=(start, chans), method='Nelder-Mead', options={'xatol': 1e-6, 'fatol': 1e-9, 'maxiter': 400 * K})
                if r.fun < best[0]:
                    best = (r.fun, profile(r.x, start))
    print(chans, 'best bang-bang channel-subset sum = %.5f a' % best[0], 'profile eps=', best[1][0], 'radii=', np.round(best[1][1], 4), '%.0fs' % (time.time() - t0), flush=True)
    res[str(chans)] = {'value': best[0], 'eps': best[1][0], 'radii': list(best[1][1])}
json.dump(res, open('bangbang_opt.json', 'w'), indent=1)
