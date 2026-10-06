"""Numerical check of the sub-mean-value inequality behind strategy S3, for layered designs in the P2 class:
  int_R P_z(t) V(t) dt >= V(z),  V(z) = |q(z)|^2 int_Theta e^{-2 c_phi Im z} |T(phi,z)|^2 dphi,
  q = sqrt(2 kap)/(z + i kap), c_phi = 2 b |sin(phi/2)|, b = 3, Theta = backward half-plane."""
import sys, json, glob, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import cloak2d, fastcyl
kc, b, kap = np.pi / 2, 3.0, np.pi / 2
xg, wg = np.polynomial.legendre.leggauss(160)
phis = np.pi / 2 + (xg + 1) * np.pi / 2; wph = wg * np.pi / 2
cphi = 2 * b * np.abs(np.sin(phis / 2))
base = '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/'
designs = {'bare': ([], [1.0])}
for f in ['de_ext_B0.0_L16.json', 'lossless_sector_B0.1_L8.json', 'de_sector_B0.0_L8.json']:
    d = json.load(open(base + f)); designs[f] = (list(d['eps']), list(d['radii']))
def Vreal(eps, radii, ts):
    chunks = [(0.0, 0.5), (0.5, 2), (2, 6), (6, 15), (15, 31)]
    return np.concatenate([Vreal1(eps, radii, ts[(ts > lo) & (ts <= hi)]) for lo, hi in chunks])
def Vreal1(eps, radii, ts):
    N = int(ts.max() * radii[-1] * np.sqrt(max(eps + [1])) + 15)
    if len(eps) == 0:
        n, B = fastcyl.coeffs_pec_real_tm(np.zeros((0, ts.size)), radii, ts, N=N)
    else:
        n, B = fastcyl.coeffs_pec_real_tm(np.repeat(np.array(eps)[:, None], ts.size, 1), radii, ts, N=N)
    T = np.exp(1j * np.outer(phis, n)) @ B          # (phi, t)
    q2 = 2 * kap / (ts ** 2 + kap ** 2)
    return q2 * (wph @ np.abs(T) ** 2)
def Vc(eps, radii, z):
    n, B = cloak2d.coeffs(list(np.sqrt(np.array(eps, float))), radii, z, core='pec', nmax=60)
    T = np.exp(1j * np.outer(phis, n)) @ B
    q2 = abs(np.sqrt(2 * kap) / (z + 1j * kap)) ** 2
    return q2 * np.sum(wph * np.exp(-2 * cphi * z.imag) * np.abs(T) ** 2)
ts = np.concatenate([np.linspace(2e-2, 6, 12000), np.linspace(6, 30, 6000)[1:]])
for name, (eps, radii) in designs.items():
    VV = Vreal(eps, radii, ts)
    out = []
    for eta in [0.01, 0.04, 0.16]:
        z = complex(kc, eta)
        P = lambda t: (eta / np.pi) / ((t - kc) ** 2 + eta ** 2)
        lhs = np.trapezoid((P(ts) + P(-ts)) * VV, ts) + (eta / np.pi) * VV[-1] * ts[-1] / ts[-1] ** 2  # crude tail
        rhs = Vc(eps, radii, z)
        out.append('eta=%.2f: Poisson avg=%.4g >= V(z)=%.4g  ratio=%.3f' % (eta, lhs, rhs, rhs / lhs))
    print(name, ' | '.join(out), flush=True)
