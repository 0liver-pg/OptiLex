"""Baselines for the lossless non-dispersive class (P1 total extinction, P2 backward-sector scattering, P4 per-channel).

Class: L equal-thickness concentric layers in a < r < b, real frequency-independent eps in [1, 6] (lossless, causal), TM,
PEC core. Usage: python run_lossless.py <metric> <B> <L> <seeds>   metric in {ext, sector, ch0, ch1, ch2}
"""
import sys, json, time
import numpy as np
from cards_common import *  # noqa

metric, B, L, seeds = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
radii = layered_radii(L)
if B > 0:
    ks, w = fastcyl.gl_band(KC, B, 21)
else:
    ks, w = np.array([KC]), np.array([1.0])
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


t = time.time()
best, x, allv = search(f, [(EPS_MIN, EPS_MAX)] * L, seeds=seeds, rng=0)
m = np.sqrt(x.astype(complex))
# exact re-scoring with cloak2d
fn = {"ext": lambda k: ext_width(m, radii, k), "sector": lambda k: sector_width_c2d(m, radii, k)}
for o in (0, 1, 2):
    fn[f"ch{o}"] = (lambda oo: (lambda k: channel_width_c2d(m, radii, k, oo)))(o)
res = dict(metric=metric, B=B, L=L, seeds=seeds, radii=radii, eps=list(map(float, x)), search_value=best,
           search_values_all=allv, seconds=round(time.time() - t, 1))
res["rescored_41pt"] = {key: band(g, B) for key, g in fn.items()}
res["rescored_41pt"]["sca"] = band(lambda k: sca_width(m, radii, k), B)
if B > 0:
    avg, mx = dense_uniform(fn[metric], B)
    res["dense201_avg"], res["dense201_max"] = avg, mx
res["lorentzian_imF"] = lorentzian_imF(lambda k: m, radii, B if B > 0 else 0.1)
out = HERE / f"lossless_{metric}_B{B}_L{L}.json"
out.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
