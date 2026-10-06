"""Context only: single-frequency (B=0) radial optimum with non-dispersive eps in [-10, 10] (acausal over a band, but a
legitimate single-frequency material). Tests whether the radial single-frequency floor is a 'positive-phase-only' (eps>=1)
effect. DE + L-BFGS-B polish; final value re-scored with cloak2d."""
import json, time
import numpy as np
from scipy.optimize import differential_evolution, minimize
from cards_common import *  # noqa
L = 8; radii = layered_radii(L); k = np.array([KC])
def f(eps):
    m = np.sqrt(np.asarray(eps, float).astype(complex))
    _, b = fastcyl.coeffs_pec_multi(m[:, None], radii, k, N=24)
    return float(-4 / KC * np.sum(b.real))
t = time.time()
init = np.random.default_rng(5).uniform(-10, 10, (120, L)); init[0] = json.load(open("de_ext_B0.0_L8.json"))["eps"]
r = differential_evolution(f, [(-10, 10)] * L, init=init, maxiter=200, tol=1e-8, polish=False, seed=5, updating="immediate")
p = minimize(f, r.x, method="L-BFGS-B", bounds=[(-10, 10)] * L)
x = p.x if p.fun < r.fun else r.x
m = np.sqrt(x.astype(complex))
out = dict(note="single-frequency radial optimum, eps in [-10,10] non-dispersive (valid at one frequency only)", L=L,
           eps=list(map(float, x)), search_value=float(min(p.fun, r.fun)), ext_cloak2d=ext_width(m, radii, KC),
           channels={o: channel_width_c2d(m, radii, KC, o) for o in (0, 1, 2, 3)}, seconds=round(time.time() - t, 1))
json.dump(out, open("acausal_de_B0_L8.json", "w"), indent=1); print(json.dumps(out))
