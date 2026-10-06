"""Harmonic-basis (polar) volume-integral equation for a TM PEC cylinder (radius a) + annulus a<r<b.
E = E_d + k^2 int G_obj p dA,  p = chi E.  G_obj = (i/4) sum_n [J_n(kr<)H_n(kr>) - c_n H_n(kr)H_n(kr')] e^{in(phi-phi')},
c_n = J_n(ka)/H_n(ka).  Harmonic n: E_n(r) = E_d,n(r) + 2 pi k^2 int g_n(r,r') p_n(r') r' dr'.
Far field: b_n = b_n^bare + i^{-n} (i pi k^2 / 2) int psi_n(r') p_n(r') r' dr',  psi_n = J_n - c_n H_n.
Nystrom on composite Gauss-Legendre nodes in r.
"""
import sys, numpy as np
from scipy.special import jv, hankel1
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d


def nodes(a, b, nsub, q):
    x, w = np.polynomial.legendre.leggauss(q)
    edges = np.linspace(a, b, nsub + 1)
    R, W = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        R.append(0.5 * (hi - lo) * x + 0.5 * (hi + lo)); W.append(0.5 * (hi - lo) * w)
    return np.concatenate(R), np.concatenate(W)


def build(k, a, b, N, r, w):
    ns = np.arange(-N, N + 1)
    out = {}
    for n in ns:
        cn = jv(n, k * a) / hankel1(n, k * a)
        rl = np.minimum(r[:, None], r[None, :]); rg = np.maximum(r[:, None], r[None, :])
        g = 0.25j * (jv(n, k * rl) * hankel1(n, k * rg) - cn * hankel1(n, k * r[:, None]) * hankel1(n, k * r[None, :]))
        Gn = 2 * np.pi * k ** 2 * g * (r * w)[None, :]          # E_n = Ed_n + Gn @ p_n
        psi = jv(n, k * r) - cn * hankel1(n, k * r)
        Ed = (1j) ** n * psi
        bb = -cn
        Fn = (1j) ** (-n) * (1j * np.pi * k ** 2 / 2) * psi * r * w   # b_n = bb + Fn @ p_n
        out[n] = dict(G=Gn, Ed=Ed, bare=bb, F=Fn)
    return ns, out


def radial_solve(chi_r, k, a, b, N, r, w):
    ns, ops = build(k, a, b, N, r, w)
    bn = []
    for n in ns:
        o = ops[n]
        A = np.eye(len(r)) - o['G'] * chi_r[None, :]
        E = np.linalg.solve(A, o['Ed'])
        bn.append(o['bare'] + o['F'] @ (chi_r * E))
    return ns, np.array(bn)


if __name__ == '__main__':
    import json
    d = json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.0_L16.json'))
    radii, eps = np.array(d['radii']), np.array(d['eps'])
    k, a, b = np.pi / 2, 1.0, 3.0
    nref, bref = cloak2d.coeffs(np.sqrt(eps), radii, k, core='pec')
    for nsub, q in [(16, 4), (16, 8), (32, 8)]:
        r, w = nodes(a, b, nsub, q)
        idx = np.clip(np.searchsorted(radii, r) - 1, 0, len(eps) - 1)
        chi_r = eps[idx] - 1
        ns, bn = radial_solve(chi_r, k, a, b, 6, r, w)
        sel = np.isin(nref, ns)
        err = np.max(np.abs(bn - bref[sel]))
        sig = 4 / k * np.sum(np.abs(bn) ** 2)
        print(nsub, q, 'max|db|', err, 'sigma_sca', sig, 'ref', 4 / k * np.sum(np.abs(bref) ** 2))
