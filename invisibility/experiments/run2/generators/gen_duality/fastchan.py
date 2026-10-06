"""Lean evaluator: channel widths sigma_n (n in chans) at one real k for a radially layered lossless TM PEC-core cylinder."""
import numpy as np
from scipy.special import jv, yv, jvp, yvp
def sig_chans(eps, radii, k, chans):
    eps = np.asarray(eps, float); radii = np.asarray(radii, float); ch = np.asarray(chans)
    L = len(eps); m = np.sqrt(eps)
    out = []
    # inner (layer j) side at r_{j+1} and outer side (layer j+1 or vacuum)
    mi = m; mo = np.concatenate([m[1:], [1.0]]); r = radii[1:]
    xi = np.outer(k * mi * r, np.ones(len(ch))); xo = np.outer(k * mo * r, np.ones(len(ch)))
    n = ch[None, :]
    Ji, Yi, Jpi, Ypi = jv(n, xi), yv(n, xi), jvp(n, xi), yvp(n, xi)
    Jo, Yo, Jpo, Ypo = jv(n, xo), yv(n, xo), jvp(n, xo), yvp(n, xo)
    x0 = k * m[0] * radii[0] * np.ones(len(ch))
    # real solution u = A J + B Y in layer 0 with u(a) = 0
    A = -yv(ch, x0); B = jv(ch, x0)
    for j in range(L):
        u = A * Ji[j] + B * Yi[j]; du = mi[j] * (A * Jpi[j] + B * Ypi[j])
        det = mo[j] * (Jo[j] * Ypo[j] - Yo[j] * Jpo[j])
        A, B = (u * mo[j] * Ypo[j] - Yo[j] * du) / det, (Jo[j] * du - u * mo[j] * Jpo[j]) / det
        s = np.maximum(np.abs(A), np.abs(B)); A, B = A / s, B / s
    # outside: u = A J + B Y = C (cos d J - sin d Y) -> tan d = -B/A ; sin^2 d = B^2/(A^2+B^2)
    s2 = B ** 2 / (A ** 2 + B ** 2)
    return (4 / k) * s2 * np.where(ch == 0, 1, 2)
if __name__ == '__main__':
    import sys, json
    sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim'); import cloak2d, time
    d = json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.0_L16.json'))
    print(sig_chans(d['eps'], d['radii'], np.pi/2, [0, 1, 2, 3]), 'expect 2.4908 0.16815 0.34310 0.03469')
    t = time.time(); [sig_chans(d['eps'], d['radii'], np.pi/2, [0, 1, 2]) for _ in range(1000)]; print('ms', (time.time()-t))
