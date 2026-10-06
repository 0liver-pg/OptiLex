# Exact per-channel attainable Prufer intervals [theta(eps=1), theta(eps=emax)] -> rigorous per-channel floor
# L_pc = sum_n min_{theta in I_n} sigma_n(theta) / sigma_bare (valid for all measurable radial eps in [1, emax]).
import numpy as np, sys
from scipy.special import jv, jvp, hankel1, h1vp
sys.path.insert(0, '/Users/oliverpascal/Local/GitHub/OptiLex/invisibility/experiments/cards_baseline')
import fastcyl
def theta_const(eps, n, k, a, b):
    # exact Prufer angle for a uniform shell: u = J_n(kmr) Y_n(kma) - Y_n(kmr) J_n(kma); cot(theta) = r u'/u; unwrap via counting zeros
    from scipy.special import yv, yvp
    m = np.sqrt(eps); rr = np.linspace(a, b, 4001)
    x0 = k*m*a
    u = jv(n, k*m*rr)*yv(n, x0) - yv(n, k*m*rr)*jv(n, x0)
    up = k*m*(jvp(n, k*m*rr)*yv(n, x0) - yvp(n, k*m*rr)*jv(n, x0))
    th = np.unwrap(np.arctan2(u, rr*up)*2)/2   # angle defined mod pi; theta(a)=0
    th = th - th[0]
    return th[-1]
def sig(th, n, k, b):
    x = k*b
    num = x*jvp(n, x)*np.sin(th) - jv(n, x)*np.cos(th)
    den = x*h1vp(n, x)*np.sin(th) - hankel1(n, x)*np.cos(th)
    return (4/k)*(1 if n == 0 else 2)*np.abs(num/den)**2
for ka in (0.5, np.pi/2, 3.0):
    for ba in (1.25, 1.5, 2.0, 3.0):
        for emax in (2.0, 4.0, 6.0):
            k = ka; a = 1.0; b = ba
            bare = fastcyl.widths_pec([], [1.0], k)[1]
            N = int(k*b*np.sqrt(emax)) + 6
            tot = 0.0
            for n in range(N + 1):
                t1, t2 = theta_const(1.0, n, k, a, b), theta_const(emax, n, k, a, b)
                ths = np.linspace(t1, t2, 4001)
                tot += sig(ths, n, k, b).min()
            print(f"ka={ka:.3f} b/a={ba} emax={emax}: per-channel floor R >= {tot/bare:.4f}")
