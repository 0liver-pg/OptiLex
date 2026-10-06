"""Check the Hardy-space (Szego-kernel) inequality used by strategy M3 on real designs:
  f(k) = w(k) G(k),  G(k) = T(pi; k) e^{2 i k b}  (phase-compensated backscatter amplitude, b = 3),
  w = outer spectral factor of the Butterworth window W(k) = 1/(1 + ((k-kc)/D)^{2m}), |w|^2 = W on R.
  Claim: int_R |f|^2 dk >= v^H K^{-1} v,  v_i = f(z_i),  K_ij = i / (2 pi (z_i - conj z_j))  (Szego kernel of C+).
  Single point: int |f|^2 >= 4 pi Im(z) |f(z)|^2.
Also reports the in-band fraction of the window mass and the uniform band average of |T(pi)|^2 for comparison.
"""
import sys, json, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
from scipy.integrate import quad

kc, B, b = np.pi / 2, 0.1, 3.0
m = 6; D = 0.8 * kc * B / 2
# Butterworth poles of 1/(1+x^{2m}) in x=(k-kc)/D: x_l = exp(i pi (2l+1)/(2m)); keep lower half-plane ones for w analytic in C+
xl = np.exp(1j * np.pi * (2 * np.arange(2 * m) + 1) / (2 * m))
low = xl[xl.imag < 0]
def w(z):
    x = (z - kc) / D
    return 1.0 / np.prod([(x - p) for p in low], axis=0)
designs = {'bare': ([], [1.0]),
           'P2_sector_opt': (None, 'lossless_sector_B0.1_L8.json'),
           'P1_ext_opt': (None, 'de_ext_B0.1_L8.json')}
def load(name):
    m_, r_ = designs[name]
    if m_ is None:
        d = json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/' + r_))
        return np.sqrt(np.array(d['eps'])), np.array(d['radii'])
    return np.array(m_), np.array(r_)
def T_back(mm, rr, k):
    n, bn = fastcyl.coeffs_pec(mm, rr, k, N=40)
    return np.sum(bn * np.exp(1j * n * np.pi))
out = {}
for name in designs:
    mm, rr = load(name)
    f = lambda k: w(k) * T_back(mm, rr, k) * np.exp(2j * k * b)
    # |w(k)|^2 check
    assert abs(abs(w(kc + 0.3 * D)) ** 2 - 1 / (1 + 0.3 ** (2 * m))) < 1e-10
    lo, hi = kc - 40 * D, kc + 40 * D
    pts = np.linspace(lo, hi, 81)
    I = sum(quad(lambda k: abs(f(k)) ** 2, a_, b_, epsabs=1e-12, epsrel=1e-10, limit=200)[0] for a_, b_ in zip(pts[:-1], pts[1:]))
    res = {'int_|f|^2': I}
    for y in [0.25 * D, 0.5 * D, D]:
        z = kc + 1j * y
        res[f'single_y{y/D:.2f}D'] = 4 * np.pi * y * abs(f(z)) ** 2
    # multi-point along the band
    zs = kc + np.linspace(-0.8, 0.8, 5) * D + 0.5j * D
    v = np.array([f(z) for z in zs])
    K = 1j / (2 * np.pi * (zs[:, None] - np.conj(zs)[None, :]))
    res['multi5_y0.5D'] = float(np.real(v.conj() @ np.linalg.solve(K, v)))
    res['band_avg_|T(pi)|^2'] = quad(lambda k: abs(T_back(mm, rr, k)) ** 2, kc * (1 - B / 2), kc * (1 + B / 2))[0] / (kc * B)
    out[name] = {k_: float(np.real(v_)) for k_, v_ in res.items()}
    print(name, out[name], flush=True)
win_in = quad(lambda k: 1 / (1 + ((k - kc) / D) ** (2 * m)), kc * (1 - B / 2), kc * (1 + B / 2))[0]
win_all = quad(lambda k: 1 / (1 + ((k - kc) / D) ** (2 * m)), -np.inf, np.inf)[0]
out['window'] = dict(m=m, D=D, in_band_fraction=win_in / win_all, mass=win_all)
print(out['window'])
json.dump(out, open('szego_check.json', 'w'), indent=1)
