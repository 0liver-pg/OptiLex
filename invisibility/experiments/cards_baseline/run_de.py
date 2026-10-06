"""Global adversary for the lossless non-dispersive class: differential evolution (+ L-BFGS-B polish), seeded with
known designs. Same class/metrics as run_lossless.py. Usage: python run_de.py <metric> <B> <L> <maxiter> [seedfiles...]
metric in {ext, sector, ch0, ch1, ch2}. Seed files are JSONs with 'eps' and 'radii' (resampled onto L equal layers).
"""
import sys, json, time
import numpy as np
from scipy.optimize import differential_evolution, minimize
from cards_common import *  # noqa

metric, B, L, maxiter = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
seedfiles = sys.argv[5:]
radii = layered_radii(L)
ks, w = (fastcyl.gl_band(KC, B, 21) if B > 0 else (np.array([KC]), np.array([1.0])))
N = int(np.ceil(ks.max() * BOUT * np.sqrt(EPS_MAX) + 4 * (ks.max() * BOUT) ** (1 / 3) + 12))
nvec = np.arange(-N, N + 1)
Ksec = fastcyl.sector_kernel(nvec, SECTOR_CENTER, SECTOR_HALF)


def per_k(b):
    if metric == "ext":
        return -4 / ks * np.sum(b.real, 0)
    if metric == "sector":
        return 2 / (np.pi * ks) * np.real(np.einsum("nk,nm,mk->k", np.conj(b), Ksec, b))
    o = int(metric[2:])
    return 4 / ks * np.sum(np.abs(b[np.abs(nvec) == o]) ** 2, 0)


def f(eps):
    _, b = fastcyl.coeffs_pec_real_tm(np.repeat(np.asarray(eps)[:, None], ks.size, 1), radii, ks, N=N)
    return float(np.sum(w * per_k(b)))


def resample(eps_src, radii_src):
    mids = 0.5 * (np.array(radii[:-1]) + np.array(radii[1:]))
    idx = np.searchsorted(np.array(radii_src[1:]), mids)
    return np.clip(np.array(eps_src)[np.minimum(idx, len(eps_src) - 1)], EPS_MIN, EPS_MAX)


seeds = []
for sf in seedfiles:
    d = json.load(open(sf))
    if "L4" in d:
        d = d["L4"]
    seeds.append(resample(d["eps"], d["radii"]))
t = time.time()
gen = np.random.default_rng(3)
popsize = 15
init = gen.uniform(EPS_MIN, EPS_MAX, (popsize * L, L))
for i, s in enumerate(seeds):
    init[i] = s
bounds = [(EPS_MIN, EPS_MAX)] * L
r = differential_evolution(f, bounds, init=init, maxiter=maxiter, tol=1e-8, polish=False, seed=3, updating="immediate")
best_x, best = r.x, r.fun
for x0 in [r.x] + seeds:
    p = minimize(f, x0, method="L-BFGS-B", bounds=bounds)
    if p.fun < best:
        best_x, best = p.x, float(p.fun)
seed_vals = [f(s) for s in seeds]
m = np.sqrt(best_x.astype(complex))
fn = {"ext": lambda k: ext_width(m, radii, k), "sector": lambda k: sector_width_c2d(m, radii, k)}
for o in (0, 1, 2):
    fn[f"ch{o}"] = (lambda oo: (lambda k: channel_width_c2d(m, radii, k, oo)))(o)
res = dict(adversary="differential_evolution+LBFGSB", eps_max=EPS_MAX, metric=metric, B=B, L=L, maxiter=maxiter, nfev=int(r.nfev),
           radii=radii, eps=list(map(float, best_x)), search_value=float(best), seed_files=seedfiles,
           seed_values=seed_vals, seconds=round(time.time() - t, 1))
res["rescored_41pt"] = {key: band(g, B) for key, g in fn.items()}
res["rescored_41pt"]["sca"] = band(lambda k: sca_width(m, radii, k), B)
if B > 0:
    res["dense201_avg"], res["dense201_max"] = dense_uniform(fn[metric], B)
res["lorentzian_imF"] = lorentzian_imF(lambda k: m, radii, B if B > 0 else 0.1)
(HERE / (f"de_{metric}_B{B}_L{L}" + (f"_epsmax{EPS_MAX:g}" if EPS_MAX != 6.0 else "") + ".json")).write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
