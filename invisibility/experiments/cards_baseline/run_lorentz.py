"""P3 baseline: causal Lorentz-oscillator layers with a total electron (f-sum) budget around the TM PEC cylinder.

Class: L equal-thickness layers, eps_j(w) = 1 + wp_j^2 / (w0_j^2 - w^2 - i*gam*w), gam = GAM*w_c (fixed = minimum damping),
w0_j >= 0 free, budget (1/A_ann) sum_j A_j wp_j^2 <= W * w_c^2  (c = 1, so w == k).
Metric: uniform band-averaged extinction width (lossy class, so scattering and absorption are reported separately).
Usage: python run_lorentz.py <W> <L> <seeds> [GAM] [seed_result.json ...]
Seed results (from smaller budgets) are converted to this budget's parameters with the same absolute wp^2 (rest unused),
so the reported value is monotone non-increasing in W as it must be (a larger budget contains the smaller class).
"""
import sys, json, time
import numpy as np
from cards_common import *  # noqa

W, L, seeds = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
GAM = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
SEEDFILES = sys.argv[5:]
radii = layered_radii(L)
areas = np.pi * np.diff(np.square(radii))
A_ann = np.pi * (BOUT ** 2 - A ** 2)
ks, w = fastcyl.gl_band(KC, BW, 21)


def unpack(p):
    q, s = p[: L + 1], p[L + 1:]
    sh = np.exp(q - q.max()); sh /= sh.sum()          # last entry = unused share
    kp2 = W * KC ** 2 * A_ann * sh[:L] / areas
    k0 = KC * np.exp(s)
    return kp2, k0


def eps_of(p, k):
    kp2, k0 = unpack(p)
    k = np.asarray(k)
    return 1 + kp2[:, None] / (k0[:, None] ** 2 - k[None, :] ** 2 - 1j * GAM * KC * k[None, :])


def f(p):
    m = np.sqrt(eps_of(p, ks))
    _, b = fastcyl.coeffs_pec_multi(m, radii, ks, N=24)   # search-only truncation; final scores use cloak2d
    return float(np.sum(w * (-4 / ks * np.sum(b.real, 0))))


bounds = [(-6, 6)] * (L + 1) + [(-3, 3)] * L


def params_from(res):
    kp2 = np.array(res["kp2_over_kc2"]) * KC ** 2
    sh = kp2 * areas / (W * KC ** 2 * A_ann)
    sh = np.append(sh, max(1 - sh.sum(), 1e-12))
    sh = np.maximum(sh, 1e-30)
    q = np.clip(np.log(sh) - np.log(sh.max()) + 6, -6, 6)
    s = np.clip(np.log(np.array(res["k0_over_kc"])), -3, 3)
    return np.concatenate([q, s])


x0s = []
for sf in SEEDFILES:
    r0 = json.load(open(sf))
    if r0["W"] <= W and r0["L"] == L:
        x0s.append(params_from(r0))
t = time.time()
best, x, allv = search(f, bounds, seeds=seeds, rng=1, maxiter=200, x0s=x0s)
seed_vals = [f(p) for p in x0s]
kp2, k0 = unpack(x)
mk = lambda k: np.sqrt(eps_of(x, [k])[:, 0])
res = dict(W=W, L=L, gam_over_wc=GAM, seeds=seeds, radii=radii, kp2_over_kc2=list(map(float, kp2 / KC ** 2)),
           k0_over_kc=list(map(float, k0 / KC)), budget_used=float(np.sum(areas * kp2) / (A_ann * KC ** 2)),
           eps_at_kc=[str(complex(e)) for e in eps_of(x, [KC])[:, 0]], search_value=best, search_values_all=allv, seed_files=SEEDFILES, seed_values=seed_vals,
           seconds=round(time.time() - t, 1))
res["rescored_41pt"] = dict(ext=band(lambda k: ext_width(mk(k), radii, k)), sca=band(lambda k: sca_width(mk(k), radii, k)))
res["rescored_41pt"]["abs"] = res["rescored_41pt"]["ext"] - res["rescored_41pt"]["sca"]
avg, mx = dense_uniform(lambda k: ext_width(mk(k), radii, k))
res["dense201_avg_ext"], res["dense201_max_ext"] = avg, mx
# Lorentzian (complex-frequency) value with the exact analytic continuation of the Lorentz model
res["lorentzian_imF"] = lorentzian_imF(lambda kt: np.sqrt(eps_of(x, [kt])[:, 0]), radii, BW)
out = HERE / (f"lorentz_W{W}_L{L}_g{GAM}" + ("_seeded" if SEEDFILES else "") + ".json")
out.write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
