# Radial Prufer-angle check: monotonicity in eps and in k, per-channel ranges, cancellation targets.
import numpy as np, sys
from scipy.integrate import solve_ivp
from scipy.special import jv, jvp, yv, yvp, hankel1, h1vp
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/sim')
import cloak2d

def theta_b(eps_fun, n, k, a=1.0, b=3.0):
    # (r u')' + (k^2 eps r - n^2/r) u = 0, u = rho sin th, r u' = rho cos th  => th' = cos^2/r + q sin^2
    def f(r, th):
        q = k**2*eps_fun(r)*r - n**2/r
        return [np.cos(th[0])**2/r + q*np.sin(th[0])**2]
    s = solve_ivp(f, (a, b), [0.0], rtol=1e-11, atol=1e-12, max_step=0.01)
    return s.y[0, -1]

def bn_from_theta(th, n, k, b=3.0):
    x = k*b
    num = x*jvp(n, x)*np.sin(th) - jv(n, x)*np.cos(th)
    den = x*h1vp(n, x)*np.sin(th) - hankel1(n, x)*np.cos(th)
    return -num/den

k = np.pi/2
for n in range(4):
    th1 = theta_b(lambda r: 1.0, n, k)
    th6 = theta_b(lambda r: 6.0, n, k)
    # target: b_n = 0  <=> cot th = x J'/J
    x = k*3.0
    tstar = np.arctan2(jv(n, x), x*jvp(n, x)) % np.pi
    # bare check vs cloak2d
    nn, bb = cloak2d.coeffs([], [1.0], k, core='pec')
    bare = bb[nn == n][0]
    print(f"n={n}: theta(eps=1)={th1:.4f}  theta(eps=6)={th6:.4f}  range={th6-th1:.3f} rad  target mod pi={tstar:.4f}  "
          f"|b_n| bare={abs(bare):.4f} via theta={abs(bn_from_theta(th1,n,k)):.4f}")
    # zeros inside the range?
    zs = [tstar + m*np.pi for m in range(-2, 12) if th1 <= tstar + m*np.pi <= th6]
    print("    cancellation angles inside range:", np.round(zs, 3), " forced travel to first zero:", (zs[0]-th1) if zs else None)

# check the L16 optimum against the Prufer route
d = __import__('json').load(open('/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline/de_ext_B0.0_L16.json'))
radii, eps = np.array(d['radii']), np.array(d['eps'])
ef = lambda r: eps[min(np.searchsorted(radii, r, side='right')-1, len(eps)-1)]
tot = 0
for n in range(6):
    th = theta_b(ef, n, k)
    s = (4/k)*(1 if n == 0 else 2)*abs(bn_from_theta(th, n, k))**2
    tot += s
    print(f"L16 design n={n}: theta={th:.4f} sigma_n={s:.4f}")
print("L16 total via Prufer:", tot, " cloak2d:", cloak2d.widths(np.sqrt(eps), list(radii), k, core='pec')[1])
# monotonicity in k
for n in range(3):
    print("theta vs k (eps=L16):", n, [round(theta_b(ef, n, kk), 4) for kk in k*np.array([0.95, 1.0, 1.05])])
