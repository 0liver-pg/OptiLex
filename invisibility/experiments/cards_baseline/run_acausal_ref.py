"""Context only (NOT a valid class over a band): non-dispersive real eps in [-10, 10] (cloak2d default bounds), lossless.
Frequency-independent Re eps < 1 violates Kramers-Kronig over a band, so this value is NOT a falsifier for any card; it shows
what sub-unity permittivity would be worth if it were free, which motivates the causal-dispersion card P3.
Usage: python run_acausal_ref.py <B> <L> <seeds>
"""
import sys, json, time
import numpy as np
from cards_common import *  # noqa

B, L, seeds = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
radii = layered_radii(L)
ks, w = fastcyl.gl_band(KC, B, 21)


def f(eps):
    m = np.sqrt(np.asarray(eps, float).astype(complex))
    _, b = fastcyl.coeffs_pec_multi(np.repeat(m[:, None], ks.size, 1), radii, ks, N=24)
    return float(np.sum(w * (-4 / ks * np.sum(b.real, 0))))


t = time.time()
best, x, allv = search(f, [(-10.0, 10.0)] * L, seeds=seeds, rng=2, maxiter=200)
m = np.sqrt(x.astype(complex))
res = dict(note="acausal reference (non-dispersive eps<1 allowed); not a member of any card class", B=B, L=L,
           radii=radii, eps=list(map(float, x)), search_value=best, search_values_all=allv,
           rescored_41pt_ext=band(lambda k: ext_width(m, radii, k), B),
           dense201=dense_uniform(lambda k: ext_width(m, radii, k), B), seconds=round(time.time() - t, 1))
(HERE / f"acausal_ref_B{B}_L{L}.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
