"""Check: Prufer-phase reduction of the radial TM PEC problem reproduces cloak2d channel widths."""
import sys, json, numpy as np
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d
from scipy.integrate import solve_ivp
from scipy.special import jv, yv, jvp, yvp

d = json.load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.0_L16.json'))
radii, eps = np.array(d['radii']), np.array(d['eps'])
k = np.pi / 2; a, b = 1.0, 3.0

def epsf(r):
    j = np.searchsorted(radii, r, side='right') - 1
    return eps[min(max(j, 0), len(eps) - 1)]

def theta_b(n, epsfun, k):
    # theta' = cos^2/r + (k^2 eps r - n^2/r) sin^2, theta(a)=0  (u = rho sin, r u' = rho cos)
    th = 0.0
    for j in range(len(radii) - 1):
        e = eps[j]
        f = lambda r, t: [np.cos(t[0])**2 / r + (k*k*e*r - n*n/r) * np.sin(t[0])**2]
        th = solve_ivp(f, (radii[j], radii[j+1]), [th], rtol=1e-12, atol=1e-12).y[0, -1]
    return th

def sigma_n(n, th, k):
    x = k * b
    N = jv(n, x) * np.cos(th) - x * jvp(n, x) * np.sin(th)
    D = yv(n, x) * np.cos(th) - x * yvp(n, x) * np.sin(th)
    s2 = N**2 / (N**2 + D**2)
    return (4 / k) * s2 * (1 if n == 0 else 2)

nn, bc = cloak2d.coeffs(list(np.sqrt(eps)), list(radii), k, pol='TM', core='pec')
for n in range(4):
    th = theta_b(n, None, k)
    ref = (4 / k) * np.sum(np.abs(bc[np.abs(nn) == n])**2)
    print(n, 'theta_b=%.6f' % th, 'prufer=%.10f' % sigma_n(n, th, k), 'cloak2d=%.10f' % ref)
# bare
for n in range(3):
    nn0, b0 = cloak2d.coeffs([], [1.0], k, core='pec')
    # bare: eps=1 everywhere
    th = 0.0
    f = lambda r, t: [np.cos(t[0])**2 / r + (k*k*r - n*n/r) * np.sin(t[0])**2]
    th = solve_ivp(f, (a, b), [0.0], rtol=1e-12, atol=1e-12).y[0, -1]
    print('bare', n, sigma_n(n, th, k), (4/k)*np.sum(np.abs(b0[np.abs(nn0)==n])**2))
